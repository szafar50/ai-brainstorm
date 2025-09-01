from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import httpx
from typing import List
import os
from error_handler import global_exception_handler
from smart_engine import build_smart_context

# -----------------------------------------------------
# FASTAPI APP INITIALIZATION
# -----------------------------------------------------
app = FastAPI(title="AI Brainstorm Backend")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
# -----------------------------------------------------
# SUPABASE CONNECTION
# - Pulls messages history from Supabase REST API
# - Uses environment variables for security
# -----------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

async def fetch_context_from_supabase():
    """Fetch conversation messages from Supabase (ordered by created_at)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/messages",
            headers={"apikey": SUPABASE_ANON_KEY},
            params={"order": "created_at"}
        )
        return response.json()

# -----------------------------------------------------
# CORS MIDDLEWARE
# - Allows your frontend (Vercel/localhost) to call backend
# -----------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-brainstorm-2.vercel.app",
        "https://ai-brainstorm-2-pqxrk2b8a-shahid-zafars-projects.vercel.app",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------
# EXTERNAL API KEYS
# -----------------------------------------------------
HF_API_KEY = os.getenv("HF_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# -----------------------------------------------------
# GLOBAL ERROR HANDLER
# -----------------------------------------------------
app.add_exception_handler(Exception, global_exception_handler)

# -----------------------------------------------------
# REQUEST MODELS
# -----------------------------------------------------
class Message(BaseModel):
    content: str
    role: str

class AIRequest(BaseModel):
    messages: List[Message]

# -----------------------------------------------------
# CALLING HUGGING FACE (free AI models)
# -----------------------------------------------------
async def call_huggingface(client: httpx.AsyncClient, prompt: str):
    try:
        resp = await client.post(
            "https://api-inference.huggingface.co/models/google/flan-t5-small",
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": prompt, "max_new_tokens": 100}
        )
        if resp.status_code != 200:
            return f"Hugging Face: HTTP {resp.status_code} - {resp.text}"
        return "Hugging Face: " + resp.json()[0]['generated_text']
    except Exception as e:
        return f"Hugging Face: Failed - {str(e)}"
# -----------------------------------------------------
# CALLING GROQ (LLaMA3 model)
# -----------------------------------------------------
async def call_groq(client: httpx.AsyncClient, prompt: str):
    try:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",  # ✅ Latest production model
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150
            }
        )
        if resp.status_code != 200:
            return f"Groq: HTTP {resp.status_code} - {resp.text}"
        
        data = resp.json()
        if "choices" not in data or len(data["choices"]) == 0:
            return "Groq: No 'choices' in response"
        
        content = data["choices"][0]["message"]["content"]
        return f"Groq: {content}"
    except Exception as e:
        return f"Groq: Failed - {str(e)}"
    

async def call_qwen(client: httpx.AsyncClient, prompt: str):
    try:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "qwen-qwq-32b",  # ✅ Reasoning-focused
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150
            }
        )
        if resp.status_code != 200:
            return f"Qwen-QWQ: HTTP {resp.status_code} - {resp.text}"
        
        data = resp.json()
        if "choices" not in data or len(data["choices"]) == 0:
            return "Qwen-QWQ: No 'choices' in response"
        
        content = data["choices"][0]["message"]["content"]
        return f"Qwen-QWQ: {content}"
    except Exception as e:
        return f"Qwen-QWQ: Failed - {str(e)}"

# -----------------------------------------------------
# MAIN ENDPOINT: /ai
# - Fetches history from Supabase
# - Builds smart context (smart_engine.py)
# - Calls HuggingFace + Groq in parallel
# -----------------------------------------------------
@app.post("/ai")
async def get_ai_response():
    try:
        # 1. Fetch messages from Supabase
        raw_messages = await fetch_context_from_supabase()

        # 2. Format messages
        messages = [{"role": m["role"], "content": m["content"]} for m in raw_messages]

        # 3. Build smart context
        smart_context = build_smart_context(messages)

        # 4. Call AI models in parallel
        async with httpx.AsyncClient(timeout=30.0) as client:
            tasks = [
                call_groq(client, smart_context),
                call_qwen(client, smart_context),
                call_huggingface(client, smart_context)  # fallback
            ]
            results = await asyncio.gather(*tasks)

        # 5. Return structured response
        return {
            "status": "success",
            "responses": results,
            "context": smart_context
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
