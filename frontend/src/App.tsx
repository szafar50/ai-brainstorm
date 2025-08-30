import { useState } from 'react';
import { supabase } from './lib/supabase';

function App() {
  const [input, setInput] = useState<string>('');

  const extractTopics = async (contextString: string) => {
    try {
      const response = await fetch(
        "https://api-inference.huggingface.co/models/bigscience/bloom",
        {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${import.meta.env.VITE_HF_API_KEY}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            inputs: `
              Extract key topics from this conversation as a JSON list:
              ${contextString}
              Return only: ["topic1", "topic2", ...]
            `,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      try {
        const topics = JSON.parse(data[0]?.generated_text || '[]');
        console.log("Extracted topics:", topics);
        return topics;
      } catch (err) {
        console.error("Failed to parse topics:", err);
        return [];
      }
    } catch (error) {
      console.error("Error calling Hugging Face API:", error);
      return [];
    }
  };

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

  // Save to Supabase
  const { error: saveError } = await supabase
    .from('messages')
    .insert([{ content: input, role: 'user' }]);

  if (saveError) {
    alert('Failed to save');
    return;
  }

  // Fetch all messages
  const { data: messages } = await supabase
    .from('messages')
    .select('content, role')
    .order('created_at', { ascending: true });

  // Call backend AI
  const res = await fetch(import.meta.env.VITE_API_URL + '/ai', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages })
  });

  const data = await res.json();
  console.log("AI Responses:", data.responses);
  alert(data.responses.join("\\n\\n"));
};

      // Fetch context
        const contextRes = await fetch(import.meta.env.VITE_API_URL + '/context', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(context),
        });
        const { context: smartContext } = await contextRes.json();
        console.log("Smart Context:", smartContext);

      // Extract topics from the current conversation
      const messages = await fetchMessages();
      if (messages.length > 0) {
        const contextString = messages.map(m => `${m.role}: ${m.content}`).join('\n');
        const topics = await extractTopics(contextString);
        console.log('Current conversation topics:', topics);
      }

    } catch (err) {
      console.error('Error in handleSubmit:', err);
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