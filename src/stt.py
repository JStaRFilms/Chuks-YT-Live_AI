import os
import io
import wave
import time
import logging
import threading
import asyncio
import numpy as np
import sounddevice as sd
from groq import Groq

logger = logging.getLogger(__name__)

# Config
MIC_DEVICE_INDEX = int(os.getenv("MIC_DEVICE_INDEX", 0))
SILENCE_THRESHOLD = float(os.getenv("SILENCE_THRESHOLD", 0.01))
SILENCE_DURATION = float(os.getenv("SILENCE_DURATION", 1.5))
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'int16'

WHISPER_MODELS = ["whisper-large-v3", "whisper-large-v3-turbo"]
model_index = 0

def get_next_model() -> str:
    global model_index
    model = WHISPER_MODELS[model_index % len(WHISPER_MODELS)]
    model_index += 1
    return model

def is_silent(audio_chunk: np.ndarray, threshold: float = SILENCE_THRESHOLD) -> bool:
    """Check if the given audio chunk is silent based on RMS."""
    if len(audio_chunk) == 0:
        return True
    
    # Convert int16 to float32 for RMS calculation to prevent overflow
    float_chunk = audio_chunk.astype(np.float32) / 32768.0
    rms = np.sqrt(np.mean(float_chunk ** 2))
    return rms < threshold

def encode_audio_to_wav(audio_data: np.ndarray, sample_rate: int) -> bytes:
    """Encode raw numpy array to WAV bytes."""
    byte_io = io.BytesIO()
    with wave.open(byte_io, 'wb') as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2) # 2 bytes for int16
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    return byte_io.getvalue()

def transcribe(audio_bytes: bytes) -> str:
    """Transcribe audio bytes using Groq Whisper API (Synchronous)."""
    try:
        client = Groq()
        model_to_use = get_next_model()
        logger.info(f"Transcribing with {model_to_use}...")
        
        result = client.audio.transcriptions.create(
            file=("audio.wav", audio_bytes),
            model=model_to_use,
            language="en",
        )
        return result.text.strip()
    except Exception as e:
        logger.error(f"Groq Whisper STT Error: {e}")
        return ""

class MicListener:
    def __init__(self):
        self._is_listening = False
        self._thread = None
        
        self.state = "WAITING_FOR_SPEECH"
        self.audio_buffer = []
        self.silence_start_time = 0
        
    def _audio_callback(self, indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags):
        """Callback invoked by sounddevice for each audio block."""
        if status:
            logger.warning(f"Audio status: {status}")
            
        is_chunk_silent = is_silent(indata)
        
        if self.state == "WAITING_FOR_SPEECH":
            if not is_chunk_silent:
                logger.info("Speech detected. Recording...")
                self.state = "RECORDING_SPEECH"
                self.audio_buffer.append(indata.copy())
                
        elif self.state == "RECORDING_SPEECH":
            self.audio_buffer.append(indata.copy())
            
            if is_chunk_silent:
                self.silence_start_time = time.time()
                self.state = "SPEECH_ENDED"
                
        elif self.state == "SPEECH_ENDED":
            self.audio_buffer.append(indata.copy())
            
            if not is_chunk_silent:
                # User started speaking again before silence duration
                self.state = "RECORDING_SPEECH"
            elif time.time() - self.silence_start_time > SILENCE_DURATION:
                # Silence duration exceeded, process the buffer
                audio_data = np.concatenate(self.audio_buffer, axis=0)
                self.audio_buffer = []
                self.state = "WAITING_FOR_SPEECH"
                
                # We need to process transcription in this thread to not block the callback 
                # but it's better to process the API call in a separated thread/queue
                # to not block sounddevice stream.
                threading.Thread(target=self._process_and_transcribe, args=(audio_data,)).start()

    def _process_and_transcribe(self, audio_data: np.ndarray):
        """Process the audio block and call Groq."""
        try:
            wav_bytes = encode_audio_to_wav(audio_data, SAMPLE_RATE)
            logger.info("Sending recorded audio to Groq Whisper...")
            
            transcript = transcribe(wav_bytes)
            
            if transcript:
                logger.info(f"Transcript: {transcript}")
                if self._callback and self._loop:
                    # Pass the text to orchestrator safely
                    asyncio.run_coroutine_threadsafe(self._callback(transcript), self._loop)
            else:
                logger.info("Empty transcript. Ignored.")
                
        except Exception as e:
            logger.error(f"Error processing audio block: {e}")

    def start_listening(self, callback: callable, loop: asyncio.AbstractEventLoop):
        """Start mic capture in a background thread."""
        if self._is_listening:
            return
            
        self._callback = callback
        self._loop = loop
        self._is_listening = True
        
        def run_stream():
            logger.info(f"Starting mic listener on device {MIC_DEVICE_INDEX}...")
            try:
                with sd.InputStream(
                    device=MIC_DEVICE_INDEX,
                    channels=CHANNELS,
                    samplerate=SAMPLE_RATE,
                    dtype=DTYPE,
                    callback=self._audio_callback,
                    blocksize=int(SAMPLE_RATE * 0.1) # 100ms blocks
                ):
                    while self._is_listening:
                        time.sleep(0.1)
            except Exception as e:
                logger.error(f"Microphone error: {e}")
                self._is_listening = False

        self._thread = threading.Thread(target=run_stream, daemon=True)
        self._thread.start()

    def stop_listening(self):
        """Stop mic capture gracefully."""
        self._is_listening = False
        if self._thread:
            self._thread.join(timeout=2.0)
            logger.info("Mic listener stopped.")
