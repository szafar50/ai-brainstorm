# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Brainstorm Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-brainstorm-2.vercel.app",   # ✅ No spaces
        "https://ai-brainstorm-2-pqxrk2b8a-shahid-zafars-projects.vercel.app",  # ✅ Optional: full subdomain
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Thought(BaseModel):
    content: str

@app.get("/")
def home():
    return {"message": "Backend is alive 🚀"}

@app.post("/save")
def save_thought(thought: Thought):
    # For now, just echo back
    return {"status": "saved", "thought": thought.content}