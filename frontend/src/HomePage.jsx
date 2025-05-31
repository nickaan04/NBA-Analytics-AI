import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

//backend expects lowercase props; we will display them uppercased in the dropdown
const PROP_OPTIONS = ['pts', 'reb', 'ast', 'stl', 'blk', 'to', 'fg3', 'fg', 'ft'];
const MIN_LEGS = 2;
const MAX_LEGS = 6;

function HomePage() {
  const navigate = useNavigate();

  // Each leg has: player (name), playerId, prop (lowercase), value (string), overUnder
  const [legs, setLegs] = useState(
    Array.from({ length: MIN_LEGS }, () => ({
      player: '',
      playerId: '',
      prop: '',
      value: '',
      overUnder: '',
    }))
  );
  const [players, setPlayers] = useState([]); // Array of { name, id } objects from backend
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch from /api/players
  useEffect(() => {
    fetch('/api/players/')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        // data.players is an array of { name, id }
        setPlayers(data.players || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch players:', err);
        setError('Failed to load player list.');
        setLoading(false);
      });
  }, []);

  // Add a new empty leg
  const addLeg = () => {
    if (legs.length < MAX_LEGS) {
      setLegs([
        ...legs,
        { player: '', playerId: '', prop: '', value: '', overUnder: '' },
      ]);
    }
  };

  // Remove last leg
  const removeLeg = () => {
    if (legs.length > MIN_LEGS) {
      setLegs(legs.slice(0, -1));
    }
  };

  // Update a field in a specific leg
  const updateLeg = (index, field, value) => {
    const updated = [...legs];
    if (field === 'player') {
      // Find matching player ID if the user typed exactly a known name
      const match = players.find((p) => p.name === value);
      updated[index].player = value;
      updated[index].playerId = match ? match.id : '';
    } else {
      updated[index][field] = value;
    }
    setLegs(updated);
  };

  // Validate that the line is >= 0.5, step .5, and not a whole number
  const isValidLine = (val) => {
    if (val === '' || isNaN(val)) return false;
    const num = parseFloat(val);
    if (num < 0.5) return false;
    return (num * 10) % 10 === 5;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate each leg
    for (let i = 0; i < legs.length; i++) {
      const leg = legs[i];
      if (!leg.playerId) {
        setError(`Leg ${i + 1}: Player "${leg.player}" is invalid.`);
        return;
      }
      if (!leg.prop) {
        setError(`Leg ${i + 1}: Please choose a prop.`);
        return;
      }
      if (!isValidLine(leg.value)) {
        setError(
          `Leg ${i + 1}: Line must be ≥ 0.5 and end in .5 (e.g. “2.5”, not “2.0”).`
        );
        return;
      }
      if (leg.overUnder !== 'over' && leg.overUnder !== 'under') {
        setError(`Leg ${i + 1}: Please choose Over or Under.`);
        return;
      }
    }

    // Build payload
    const payload = {
      parlayLegs: legs.map((l) => ({
        player: l.player,
        prop: l.prop, // lowercase
        value: parseFloat(l.value),
        overUnder: l.overUnder,
      })),
    };

    try {
      const res = await fetch('/api/parlay/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || `HTTP ${res.status}`);
      }
      const data = await res.json();
      navigate('/results', {
        state: {
          ...data,
          playerMap: players.reduce((acc, p) => {
            acc[p.name] = p.id;
            return acc;
          }, {}),
        },
      });
    } catch (err) {
      console.error('Parlay evaluation failed:', err);
      setError('Failed to evaluate parlay. Please try again.');
    }
  };

  return (
    <div className="homepage">
      <h1 className="title">ParlAI</h1>
      {loading && <p>Loading player list…</p>}
      {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}
      {!loading && (
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
                required
              >
                <option value="">Select Prop</option>
                {PROP_OPTIONS.map((p) => (
                  <option key={p} value={p}>
                    {p.toUpperCase()}
                  </option>
                ))}
              </select>

              <input
                type="number"
                step="0.5"
                min="0.5"
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
                    name={`overUnder-${idx}`}
                    checked={leg.overUnder === 'over'}
                    onChange={() => updateLeg(idx, 'overUnder', 'over')}
                  />{' '}
                  Over
                </label>
                <label style={{ marginLeft: '1rem' }}>
                  <input
                    type="radio"
                    name={`overUnder-${idx}`}
                    checked={leg.overUnder === 'under'}
                    onChange={() => updateLeg(idx, 'overUnder', 'under')}
                  />{' '}
                  Under
                </label>
              </div>
            </div>
          ))}

          <datalist id="player-list">
            {players.map((p) => (
              <option key={p.id} value={p.name} />
            ))}
          </datalist>

          <div className="leg-controls">
            <button
              type="button"
              onClick={removeLeg}
              disabled={legs.length <= MIN_LEGS}
            >
              −
            </button>
            <button
              type="button"
              onClick={addLeg}
              disabled={legs.length >= MAX_LEGS}
            >
              ＋
            </button>
          </div>

          <div className="submit-container">
            <button type="submit" className="submit-button">
              EVALUATE
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

export default HomePage;
