import sounddevice as sd

if __name__ == "__main__":
    print("Audio Devices:")
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        device_type = "Output" if dev['max_output_channels'] > 0 else "Input"
        if dev['max_input_channels'] > 0 and dev['max_output_channels'] > 0:
            device_type = "In/Out"
        # highlight the default devices maybe, but simple print is fine
        print(f"[{i}] {dev['name']} ({device_type})")
