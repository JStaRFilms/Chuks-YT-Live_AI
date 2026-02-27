import json
import logging
import os
from src.llm import chat_completion

logger = logging.getLogger(__name__)

# In-memory conversation history
conversation_history: list[dict] = []
MAX_HISTORY = 30

def load_persona() -> str:
    """Load the persona configuration and build the system prompt."""
    persona_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'persona.json')
    try:
        with open(persona_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        prompt = (
            f"Your name is {data.get('name', 'Chuks')}. "
            f"Personality: {data.get('personality', '')} "
            f"Speaking Style: {data.get('speaking_style', '')} "
            f"Context: {data.get('knowledge_context', '')} "
            f"Rules:\n"
        )
        for rule in data.get('rules', []):
            prompt += f"- {rule}\n"
            
        return prompt
    except Exception as e:
        logger.error(f"Failed to load persona: {e}")
        return "You are a helpful AI assistant."

def build_context(user_text: str) -> list[dict]:
    """Build the full context array (system prompt + history + new user message)."""
    system_prompt = load_persona()
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_text})
    return messages

async def process_text_input(text: str) -> str:
    """Process a single text input through the full pipeline."""
    global conversation_history
    
    # Build context
    messages = build_context(text)
    
    # Call LLM
    response_text = await chat_completion(messages)
    
    # Append to history if it's not an error response
    if not response_text.startswith("Error:"):
        conversation_history.append({"role": "user", "content": text})
        conversation_history.append({"role": "assistant", "content": response_text})
    
        # Prune history if it exceeds max size
        if len(conversation_history) > MAX_HISTORY * 2:  # *2 because each exchange is 2 messages
            conversation_history = conversation_history[-(MAX_HISTORY * 2):]
        
    return response_text
