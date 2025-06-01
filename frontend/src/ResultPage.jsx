// src/ResultPage.jsx

import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./ResultPage.css";

/**
 * Convert a probability (0 to 1) into a smooth HSL color from red (0°) to green (120°).
 * For example: prob=0 → "hsl(0, 75%, 50%)" (bright red)
 *              prob=0.5 → "hsl(60, 75%, 50%)" (yellowish)
 *              prob=1 → "hsl(120, 75%, 50%)" (bright green)
 */
function getProbabilityColor(prob) {
  const hue = Math.round(prob * 120);          // 0 → 120
  return `hsl(${hue}, 75%, 50%)`;
}

function ResultPage() {
  const { state } = useLocation();
  const navigate = useNavigate();

  // If state is missing or malformed, prompt to go back
  if (
    !state ||
    !state.parlayLegProbabilities ||
    !state.playerMap ||
    state.overallProbability == null
  ) {
    return (
      <div className="result-page-container">
        <p>
          No results available.{" "}
          <button className="new-parlay-button" onClick={() => navigate("/")}>
            Go Back
          </button>
        </p>
      </div>
    );
  }

  const { overallProbability, parlayLegProbabilities, playerMap } = state;

  // Compute overall color now via gradient
  const overallColor = getProbabilityColor(overallProbability);

  return (
    <div className="result-page-container">
      {/* Title */}
      <h1 className="title">ParlAI</h1>

      {/* Overall probability */}
      <div className="overall-prob-container">
        <span
          className="overall-prob-value"
          style={{ color: overallColor }}
        >
          {(overallProbability * 100).toFixed(1)}%
        </span>
        <span className="overall-prob-label">
          Overall Parlay Probability
        </span>
      </div>

      {/* Individual leg cards */}
      <div className="legs-container">
        {parlayLegProbabilities.map((leg, idx) => {
          const prob = leg.probability;
          const bgColor = getProbabilityColor(prob);

          const playerId = playerMap[leg.player];
          const playerImageUrl = playerId
            ? `/images/${playerId}.png`
            : `/images/placeholder.png`;

          return (
            <div key={idx} className="leg-card">
              {/* Player + Prop Info */}
              <div className="player-info">
                <img
                  className="player-photo"
                  src={playerImageUrl}
                  alt={leg.player}
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = "/images/placeholder.png";
                  }}
                />
                <div className="player-details">
                  <h2 className="player-name">{leg.player}</h2>
                  <span className="prop-detail">
                    {leg.overUnder.toUpperCase()} {leg.value}{" "}
                    {leg.prop.toUpperCase()}
                  </span>
                </div>
              </div>

              {/* Probability bar */}
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
        <button className="new-parlay-button" onClick={() => navigate("/")}>
          New Parlay
        </button>
      </div>
    </div>
  );
}

export default ResultPage;
