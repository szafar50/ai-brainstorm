// src/lib/api.ts
const API_URL = import.meta.env.VITE_API_URL;

export const aiApi = {
  async getResponse(messages: Array<{ role: string; content: string }>) {
    try {
      const res = await fetch(`${API_URL}/ai`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages }),
      });
      if (!res.ok) throw new Error('AI request failed');
      return await res.json();
    } catch (err) {
      console.error('AI API Error:', err);
      throw err;
    }
  },
};