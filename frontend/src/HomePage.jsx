import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const DUMMY_PLAYERS = [
  'Jalen Brunson',
  'Stephen Curry',
  'Anthony Davis',
  'Luka Doncic',
  'Ja Morant'
];

const PROP_OPTIONS = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TO', '3PTM', 'FGM', 'FTM'];
const MIN_LEGS = 2;
const MAX_LEGS = 6;

function HomePage() {
  const navigate = useNavigate();
  const [players] = useState(DUMMY_PLAYERS);
  const [legs, setLegs] = useState(
    Array.from({ length: MIN_LEGS }, () => ({ player: '', prop: 'PTS', value: '', overUnder: 'over' }))
  );

  const addLeg = () => {
    if (legs.length < MAX_LEGS) {
      setLegs([...legs, { player: '', prop: 'PTS', value: '', overUnder: 'over' }]);
    }
  };

  const removeLeg = () => {
    if (legs.length > MIN_LEGS) {
      setLegs(legs.slice(0, -1));
    }
  };

  const updateLeg = (index, field, value) => {
    const updated = [...legs];
    updated[index][field] = value;
    setLegs(updated);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    navigate('/results', { state: { parlayLegs: legs } });
  };

  return (
    <div className="homepage">
      <h1 className="title">ParlAI</h1>
      <form className="parlay-form" onSubmit={handleSubmit}>
        {legs.map((leg, idx) => (
          <div className="parlay-leg-row" key={idx}>
            <input
              type="text"
              list="player-list"
              value={leg.player}
              onChange={(e) => updateLeg(idx, 'player', e.target.value)}
              required
              className="input slim-input"
              placeholder="Player"
            />
            <select
              value={leg.prop}
              onChange={(e) => updateLeg(idx, 'prop', e.target.value)}
              className="select slim-input"
            >
              {PROP_OPTIONS.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
            <input
              type="number"
              step="0.5"
              value={leg.value}
              onChange={(e) => updateLeg(idx, 'value', e.target.value)}
              required
              className="input slim-input"
              placeholder="Line"
            />
            <div className="radio-group horizontal">
              <label>
                <input
                  type="radio"
                  checked={leg.overUnder === 'over'}
                  onChange={() => updateLeg(idx, 'overUnder', 'over')}
                /> Over
              </label>
              <label>
                <input
                  type="radio"
                  checked={leg.overUnder === 'under'}
                  onChange={() => updateLeg(idx, 'overUnder', 'under')}
                /> Under
              </label>
            </div>
          </div>
        ))}

        <datalist id="player-list">
          {players.map((p) => (
            <option key={p} value={p} />
          ))}
        </datalist>

        <div className="leg-controls">
          <button type="button" onClick={removeLeg} disabled={legs.length <= MIN_LEGS}>−</button>
          <button type="button" onClick={addLeg} disabled={legs.length >= MAX_LEGS}>+</button>
        </div>

        <div className="submit-container">
          <button type="submit" className="submit-button">EVALUATE</button>
        </div>
      </form>
    </div>
  );
}

export default HomePage;
