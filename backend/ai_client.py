# backend/ai_client.py
import httpx
import os

HF_API_KEY = os.getenv("HF_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def call_huggingface(client: httpx.AsyncClient, prompt: str):
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