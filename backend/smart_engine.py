# smart engine . py
import re
import asyncio
import httpx
from typing import List, Dict

# --- Context Intelligence Engine ---

def extract_keywords(text: str) -> List[str]:
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    important = {'ai', 'model', 'token', 'context', 'thought', 'brainstorm', 'memory', 'query', 'response', 'logic', 'plan', 'goal', 'system'}
    return [w for w in set(words) if w in important]

def detect_self_reference(text: str) -> bool:
    patterns = [
        r'as i.*mentioned',
        r'you.*asked',
        r'earlier',
        r'previously',
        r'in the.*conversation',
        r'we.*talked'
    ]
    return any(re.search(p, text.lower()) for p in patterns)

def build_smart_context(messages: List[Dict]) -> str:
    full_text = " ".join([m['content'] for m in messages])
    keywords = extract_keywords(full_text)
    topic_str = f"Topics: {', '.join(keywords)}" if keywords else "Topics: discussion"
    
    summary = f"Conversation with {len(messages)} messages. Roles: {', '.join(set(m['role'] for m in messages))}."
    
    return "\\n".join([
        "## SMART CONTEXT ENGINE",
        topic_str,
        summary,
        "## INSTRUCTIONS",
        "Respond with insight, not repetition.",
        "Use user's voice and goals.",
        "Be concise, logical, forward-thinking.",
        "## CONVERSATION HISTORY",
        "\\n".join([f"{m['role']}: {m['content']}" for m in messages])
    ])
