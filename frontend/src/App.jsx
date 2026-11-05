import React, { useState } from 'react';
import { useDataFetch } from './hooks/useDataFetch';
import { InteractivePlayer } from './components/InteractivePlayer';

function App() {
  const [topic, setTopic] = useState('');
  const { data, loading, error, fetchData } = useDataFetch();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (topic.trim() === '') return;

    // We pass metadata as the second parameter to useDataFetch
    fetchData(topic, { skip_upload: true });
  };

  return (
    <div style={{ maxWidth: '600px', margin: '50px auto', fontFamily: 'sans-serif' }}>
      <h1>Educational Video Pipeline</h1>

      <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter a topic (e.g. Heart)"
          style={{ width: '70%', padding: '10px', fontSize: '16px' }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{ padding: '10px 20px', fontSize: '16px', marginLeft: '10px' }}
        >
          {loading ? 'Generating...' : 'Generate Video'}
        </button>
      </form>

      {error && (
        <div style={{ color: 'red', padding: '10px', border: '1px solid red', marginBottom: '20px' }}>
          <strong>Error: </strong> {error}
        </div>
      )}

      {data && (
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
          <h3>Job Dispatched Successfully!</h3>
          <p><strong>Task ID:</strong> {data.task_id}</p>
          <p><strong>Topic:</strong> {data.topic}</p>
          <p><strong>Status:</strong> {data.status}</p>
          <p><em>Check the Celery worker logs to monitor background compilation progress.</em></p>

          {/* We stub the player using mock scenes just to demonstrate Phase 6 */}
          <InteractivePlayer scenes={[
             { sequence: 1, text: "Welcome to the educational interactive journey. Choose a path.", choices: [{label: "Learn about the Heart", target_sequence: 2}, {label: "Learn about the Brain", target_sequence: 3}] },
             { sequence: 2, text: "The heart pumps blood. Want to learn about veins or arteries?", choices: [{label: "Veins", target_sequence: 4}, {label: "Arteries", target_sequence: 5}] },
             { sequence: 3, text: "The brain is the control center." }
          ]} />
        </div>
      )}
    </div>
  );
}

export default App;
