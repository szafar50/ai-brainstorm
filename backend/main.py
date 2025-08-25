from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Brainstorm Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",   # Vite dev server
        "http://localhost:5173",   # fallback
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows: POST, GET, etc.
    allow_headers=["*"],  # Allows: Content-Type, etc.
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