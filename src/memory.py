import logging
from src.db import get_last_session_summary, get_pinned_memories, get_messages_for_session, set_session_summary
from src.llm import chat_completion

logger = logging.getLogger(__name__)

async def get_context_additions() -> str:
    """Gets pinned memories and the previous session summary to inject into the persona/system prompt."""
    pinned = await get_pinned_memories()
    summary = await get_last_session_summary()
    
    additions = []
    if pinned:
        additions.append("Pinned Memories (Important Facts):")
        for p in pinned:
            cat = p.get('category', 'general')
            additions.append(f"- [{cat}] {p['content']}")
            
    if summary:
        additions.append(f"Previous Session Summary:\n{summary}")
        
    return "\n\n".join(additions)

async def summarize_session(session_id: int):
    """Generate a summary of a session and save it."""
    try:
        messages = await get_messages_for_session(session_id)
        if not messages:
            logger.info(f"No messages in session {session_id}, skipping summary.")
            return
            
        # Format messages for the summarization prompt
        transcript = ""
        for m in messages:
            transcript += f"{m['role'].capitalize()}: {m['content']}\n"
            
        summary_prompt = [
            {"role": "system", "content": "You are a helpful assistant summarizing a conversation. Please summarize the following transcript in a concise paragraph. Focus on the main topics discussed, what was learned about the user, and key takeaways."},
            {"role": "user", "content": f"Transcript:\n{transcript}"}
        ]
        
        # Get purely text summary (not streaming for background task)
        logger.info(f"Generating summary for session {session_id}...")
        summary = await chat_completion(summary_prompt)
        
        if summary and not summary.startswith("Error:"):
            await set_session_summary(session_id, summary)
            logger.info(f"Successfully saved summary for session {session_id}")
        else:
            logger.error(f"Failed to generate valid summary: {summary}")
            
    except Exception as e:
        logger.error(f"Error summarizing session {session_id}: {e}")
