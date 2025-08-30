from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import httpx
import os

from smart_engine import build_smart_context

app = FastAPI(title="AI Brainstorm Backend")

# CORS
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

# Models
HF_API_KEY = os.getenv("HF_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

class Message(BaseModel):
    content: str
    role: str

class AIRequest(BaseModel):
    messages: List[Message]

async def call_hf(client: httpx.AsyncClient, prompt: str):
    try:
        resp = await client.post(
            "https://api-inference.huggingface.co/models/gpt2",
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": prompt, "max_new_tokens": 150}
        )
        return "Hugging Face: " + resp.json()[0]['generated_text']
    except Exception as e:
        return f"Hugging Face: Error {str(e)}"

async def call_groq(client: httpx.AsyncClient, prompt: str):
    try:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}]}
        )
        return "Groq: " + resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Groq: Error {str(e)}"

@app.post("/ai")
async def get_ai_response(request: AIRequest):
    # 1. Build smart context
    smart_context = build_smart_context(request.messages)
    
    # 2. Call models in parallel
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [
            call_hf(client, smart_context),
            call_groq(client, smart_context)
        ]
        results = await asyncio.gather(*tasks)
    
    # 3. Return all responses
    return {
        "context": smart_context,
        "responses": results
    }

@app.get("/")
def home():
    return {"message": "Backend is alive 🚀"}
