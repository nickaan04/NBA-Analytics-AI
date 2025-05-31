import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './ResultPage.css';

/**
 * Given a probability between 0 and 1, return a color string that
 * goes from red (low) to green (high).
 */
function getProbabilityColor(prob) {
  if (prob < 0.2) return '#e74c3c'; //red
  if (prob < 0.4) return '#e67e22'; //orange
  if (prob < 0.6) return '#f1c40f'; //yellow
  if (prob < 0.8) return '#2ecc71'; //light green
  return '#27ae60'; //dark green
}

/**
 * Convert a player name to a “key” for image lookup inside /public/images/.
 * Adjust as needed to match your actual filenames.
 */
function getPlayerImageUrl(playerName) {
  const key = playerName.toLowerCase().replace(/\s+/g, '');
  return `/images/${key}.png`;
}

function ResultPage() {
  const { state } = useLocation();
  const navigate = useNavigate();

  //if state is missing or malformed, redirect back to home
  if (
    !state ||
    !state.parlayLegProbabilities ||
    !state.playerMap ||
    !state.overallProbability
  ) {
    return (
      <div className="result-page-container">
        <p>No results available. <button onClick={() => navigate('/')}>Go Back</button></p>
      </div>
    );
  }

  const {
    overallProbability,
    parlayLegProbabilities,
    playerMap  //this is { playerName: playerId, … }
  } = state;

  return (
    <div className="result-page-container">
      {/* Title */}
      <h1 className="title">ParlAI</h1>

      {/* Overall Probability */}
      <div className="overall-prob-container">
        <span className="overall-prob-value">
          {(overallProbability * 100).toFixed(1)}%
        </span>
        <span className="overall-prob-label">Overall Parlay Probability</span>
      </div>

      {/* Individual Legs */}
      <div className="legs-container">
        {parlayLegProbabilities.map((leg, idx) => {
          const prob = leg.probability;
          const bgColor = getProbabilityColor(prob);
          //lookup the playerId so we point to /images/<playerId>.png
          const playerId = playerMap[leg.player];
          const playerImageUrl = playerId
            ? `/images/${playerId}.png`
            : `/images/placeholder.png`;

          return (
            <div key={idx} className="leg-card">
              <div className="player-info">
                <img
                  className="player-image"
                  src={playerImageUrl}
                  alt={leg.player}
                  onError={(e) => {
                    // Fallback if custom image not found:
                    e.target.onerror = null;
                    e.target.src = '/images/placeholder.png';
                  }}
                />
                <div className="player-details">
                  <h3 className="player-name">{leg.player}</h3>
                  <span className="prop-detail">
                    {leg.prop.toUpperCase()} {leg.overUnder === 'over' ? '>' : '<'} {leg.value}
                  </span>
                </div>
              </div>
              <div
                className="leg-probability"
                style={{ backgroundColor: bgColor }}
              >
                {(prob * 100).toFixed(1)}%
              </div>
            </div>
          );
        })}
      </div>

      {/* New Parlay Button */}
      <div className="new-parlay-container">
        <button className="new-parlay-button" onClick={() => navigate('/')}>
          New Parlay
        </button>
      </div>
    </div>
  );
}

export default ResultPage;