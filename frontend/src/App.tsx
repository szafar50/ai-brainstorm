import { useState } from 'react';
import { supabase } from './lib/supabase';

function App() {
  const [input, setInput] = useState<string>('');

const handleSubmit = async () => {
  if (!input.trim()) return;

  // 1. Save to Supabase immediately
  const { error: saveError } = await supabase
    .from('messages')
    .insert([{ content: input, role: 'user' }]);

  if (saveError) {
    alert('Failed to save to cloud');
    return;
  }

  // 2. Then call AI (next step)
  try {
    const response = await fetch(import.meta.env.VITE_API_URL + '/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: input }),
    });
    const data = await response.json();
    alert(`Saved: ${data.thought}`);
    setInput('');
  } catch (err) {
    alert('Failed to connect to backend');
  }
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