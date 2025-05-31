import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './ResultPage.css';

/**
 * Given a probability between 0 and 1, return a color string that
 * goes from red (low) to green (high).
 */
function getProbabilityColor(prob) {
  if (prob < 0.2) return '#e74c3c';   // red
  if (prob < 0.4) return '#e67e22';   // orange
  if (prob < 0.6) return '#f1c40f';   // yellow
  if (prob < 0.8) return '#2ecc71';   // light green
  return '#27ae60';                   // dark green
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

  // Hard-coded fallback data (only used if no state was passed)
  const fallbackData = {
    overallProbability: 0.78,
    parlayLegProbabilities: [
      {
        player: 'Jalen Brunson',
        prop: 'pts',
        value: 28.5,
        overUnder: 'over',
        probability: 0.82
      },
      {
        player: 'Anthony Davis',
        prop: 'reb',
        value: 11.5,
        overUnder: 'under',
        probability: 0.43
      },
      {
        player: 'Luka Doncic',
        prop: 'ast',
        value: 9.5,
        overUnder: 'over',
        probability: 0.65
      }
    ]
  };

  // If no state was passed from navigation, use fallbackData
  const data = state ?? fallbackData;

  return (
    <div className="result-page-container">
      {/* Title */}
      <h1 className="title">ParlAI</h1>

      {/* Overall Probability */}
      <div className="overall-prob-container">
        <span className="overall-prob-value">
          {(data.overallProbability * 100).toFixed(1)}%
        </span>
        <span className="overall-prob-label">Overall Parlay Probability</span>
      </div>

      {/* Individual Legs */}
      <div className="legs-container">
        {data.parlayLegProbabilities.map((leg, idx) => {
          const prob = leg.probability;
          const bgColor = getProbabilityColor(prob);
          const playerImageUrl = getPlayerImageUrl(leg.player);

          return (
            <div key={idx} className="leg-card">
              <div className="player-info">
                <img
                  className="player-image"
                  src={playerImageUrl}
                  alt={leg.player}
                  onError={(e) => {
                    // Fallback if image not found:
                    e.target.onerror = null;
                    e.target.src = '/images/dortlu01.png';
                  }}
                />
                <div className="player-details">
                  <h3 className="player-name">{leg.player}</h3>
                  <span className="prop-detail">
                    {leg.prop.toUpperCase()}{' '}
                    {leg.overUnder === 'over' ? '>' : '<'} {leg.value}
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