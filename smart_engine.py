import re
from typing import List, Dict
from collections import Counter

# Simple in-memory keyword extraction
def extract_keywords(text: str, min_len=4) -> List[str]:
    words = re.findall(r'\b[a-zA-Z]{%d,}\b' % min_len, text.lower())
    # Common AI/brainstorming terms
    important = {'ai', 'model', 'token', 'context', 'thought', 'brainstorm', 'memory', 'query', 'response', 'logic'}
    return [w for w in words if w in important]

# Detect if a response references earlier messages
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

# Build a smart context string with topics and summary
def build_smart_context(messages: List[Dict]) -> str:
    full_text = " ".join([m['content'] for m in messages])
    roles = {m['role'] for m in messages}
    
    # Extract keywords
    keywords = extract_keywords(full_text)
    topic_str = f"Topics: {', '.join(set(keywords))}" if keywords else "Topics: general discussion"
    
    # Simple summary
    summary = f"Conversation between {' and '.join(roles)}. Contains {len(messages)} messages."
    
    # Build context
    context_parts = [
        "## CONTEXT INTELLIGENCE ENGINE",
        topic_str,
        summary,
        "## INSTRUCTIONS",
        "Respond with insight, not repetition.",
        "If referencing past messages, keep it concise.",
        "Stay on topic. Use user's voice.",
        "## CONVERSATION HISTORY",
        "\\n".join([f"{m['role']}: {m['content']}" for m in messages])
    ]
    
    return "\\n".join(context_parts)
