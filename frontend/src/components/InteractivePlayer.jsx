import React, { useState } from 'react';

/**
 * InteractivePlayer component for Phase 6.
 * Currently serves as a stub for the branching narrative UI playback.
 */
export const InteractivePlayer = ({ scenes }) => {
  const [currentSequenceId, setCurrentSequenceId] = useState(1);

  if (!scenes || scenes.length === 0) {
    return <div>No interactive scenes available.</div>;
  }

  // Find the scene matching the current sequence
  const currentScene = scenes.find((s) => s.sequence === currentSequenceId) || scenes[0];

  const handleChoiceClick = (targetSequence) => {
    setCurrentSequenceId(targetSequence);
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px', marginTop: '20px' }}>
      <h3>Interactive Web Player (Phase 6 Stub)</h3>
      <div style={{ backgroundColor: '#000', color: '#fff', padding: '40px', textAlign: 'center', marginBottom: '15px' }}>
        <p><em>(Video Player Simulation)</em></p>
        <p><strong>Playing Scene {currentScene.sequence}</strong></p>
        <p>"{currentScene.text}"</p>
      </div>

      {currentScene.choices && currentScene.choices.length > 0 ? (
        <div>
          <h4>What do you want to learn next?</h4>
          <div style={{ display: 'flex', gap: '10px' }}>
            {currentScene.choices.map((choice, idx) => (
              <button
                key={idx}
                onClick={() => handleChoiceClick(choice.target_sequence)}
                style={{ padding: '10px 15px', cursor: 'pointer' }}
              >
                {choice.label}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <p>End of narrative branch.</p>
      )}
    </div>
  );
};
