import { useState } from 'react';
import { supabase } from './lib/supabase';

function App() {
  const [input, setInput] = useState<string>('');

  const [output, setOutput] = useState<string[]>([]);

  const fetchMessages = async () => {
    const { data, error } = await supabase
      .from('messages')
      .select('content, role')
      .order('created_at', { ascending: true });

    if (error) {
      console.error('Error fetching messages:', error);
      return [];
    }

    return data || [];
  };

const handleSubmit = async () => {
  
  if (!input.trim()) return;

  
  // 1. Save user message to Supabase
  const { error: saveError } = await supabase
    .from('messages')
    .insert([{ content: input, role: 'user' }]);

  if (saveError) {
    alert('Failed to save to cloud');
    return;
  }

  // 2. Fetch full context AFTER save
  const context = await fetchMessages();
  const contextString = context.map(m => `${m.role}: ${m.content}`).join('\n');
  console.log('Full context:', contextString);

  // 3. NOW call AI with full context
  try {
    const aiRes = await fetch(import.meta.env.VITE_API_URL + '/ai', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: context }) // 👈 Send context
    });

    if (!aiRes.ok) {
      const text = await aiRes.text();
      console.error("AI request failed:", aiRes.status, text);
      throw new Error(`AI request failed: ${aiRes.status}`);
    }

    const data = await aiRes.json();
    console.log("AI Response:", data);
    
    setOutput([...data.responses]);

    // Save AI responses to Supabase
    for (const response of data.responses) {
      if (response.includes("Hugging Face:") || response.includes("Groq:")) {
        const content = response.split(": ").slice(1).join(": ");
        await supabase
          .from('messages')
          .insert([{ content, role: 'assistant' }]);
      }
    }


    alert(data.responses.join("\n\n"));
  } catch (err) {
    console.error("AI call failed:", err);
    alert("AI call failed. Check console.");
  }

  // 4. Clear input
  setInput('');
};
  return (
    <div style={styles.container}>
      <h1 style={styles.title}>AI Brainstorm 🌀</h1>
      <p style={styles.subtitle}>Your mind. Your model. Your tokens.</p>

      <input
        type="text"
        placeholder="Type a thought..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
        style={styles.input}
      />

      <button onClick={handleSubmit} style={styles.button}>
        Save Thought
      </button>
      <div style={styles.output}>
        {output.map((res, i) => (
          <p key={i} style={{ margin: '8px 0' }}>{res}</p>
        ))}
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    background: 'black',
    color: '#c084fc',
    fontFamily: 'monospace',
    padding: '40px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '20px',
  },
  title: {
    fontSize: '2rem',
    fontWeight: 'bold',
    margin: '0',
  },
  subtitle: {
    color: '#a855f7',
    fontSize: '1.1rem',
    margin: '0',
  },
  input: {
    padding: '12px 16px',
    width: '100%',
    maxWidth: '500px',
    backgroundColor: '#1a1a1a',
    border: '2px solid #c084fc',
    borderRadius: '8px',
    color: 'white',
    fontSize: '1rem',
    outline: 'none',
  },
  output: {
    marginTop: '20px',
    width: '100%',
    maxWidth: '600px',
    backgroundColor: '#1a1a1a',
    border: '2px solid #c084fc',
    borderRadius: '8px',
    padding: '16px',
    color: 'white',
    fontSize: '1rem',
    maxHeight: '300px',
    overflowY: 'auto',
  },
  button: {
    padding: '12px 24px',
    backgroundColor: '#c084fc',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: 'bold',
    fontSize: '1rem',
  },
};

export default App;