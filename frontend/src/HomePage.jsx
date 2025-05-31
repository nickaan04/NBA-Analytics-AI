import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// Dummy list of players for prototype
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
  const [players, setPlayers] = useState(DUMMY_PLAYERS);
  const [legs, setLegs] = useState(
    Array.from({ length: MIN_LEGS }, () => ({ player: '', prop: 'PTS', value: '', overUnder: 'over' }))
  );

  // Handler to add a leg
  const addLeg = () => {
    if (legs.length < MAX_LEGS) {
      setLegs([...legs, { player: '', prop: 'PTS', value: '', overUnder: 'over' }]);
    }
  };
  // Handler to remove a leg
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
    // Pass legs to results page
    navigate('/results', { state: { parlayLegs: legs } });
  };

  return (
    <div>
      <h1 style={{ textAlign: 'center' }}>ParlAI</h1>
      <form onSubmit={handleSubmit}>
        {legs.map((leg, idx) => (
          <div key={idx} style={{ border: '1px solid #ccc', padding: '1rem', marginBottom: '1rem' }}>
            <h3>Leg {idx + 1}</h3>
            <label>
              Player:
              <input
                type="text"
                list="player-list"
                value={leg.player}
                onChange={(e) => updateLeg(idx, 'player', e.target.value)}
                required
                style={{ width: '100%' }}
              />
              <datalist id="player-list">
                {players.map((p) => (
                  <option key={p} value={p} />
                ))}
              </datalist>
            </label>
            <label>
              Prop:
              <select
                value={leg.prop}
                onChange={(e) => updateLeg(idx, 'prop', e.target.value)}
              >
                {PROP_OPTIONS.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </label>
            <label>
              Line:
              <input
                type="number"
                step="0.5"
                value={leg.value}
                onChange={(e) => updateLeg(idx, 'value', e.target.value)}
                required
              />
            </label>
            <fieldset>
              <legend>Type:</legend>
              <label>
                <input
                  type="radio"
                  checked={leg.overUnder === 'over'}
                  onChange={() => updateLeg(idx, 'overUnder', 'over')}
                />
                Over
              </label>
              <label>
                <input
                  type="radio"
                  checked={leg.overUnder === 'under'}
                  onChange={() => updateLeg(idx, 'overUnder', 'under')}
                />
                Under
              </label>
            </fieldset>
          </div>
        ))}

        <div style={{ textAlign: 'center' }}>
          <button type="button" onClick={removeLeg} disabled={legs.length <= MIN_LEGS}>-</button>
          <button type="button" onClick={addLeg} disabled={legs.length >= MAX_LEGS}>+</button>
        </div>

        <div style={{ textAlign: 'center', marginTop: '2rem' }}>
          <button type="submit" style={{ padding: '0.75rem 1.5rem' }}>Evaluate Parlay</button>
        </div>
      </form>
    </div>
  );
}

export default HomePage;