import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const PROP_OPTIONS = ['pts', 'reb', 'ast', 'stl', 'blk', 'to', 'fg3', 'fg', 'ft'];
const MIN_LEGS = 2;
const MAX_LEGS = 6;

function HomePage() {
  const navigate = useNavigate();
  const [players, setPlayers] = useState([]); //players will now be an array of objects: { name: string, id: string }
  const [legs, setLegs] = useState(
    Array.from({ length: MIN_LEGS }, () => ({ player: '', prop: '', value: '', overUnder: '' }))
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  //fetch the list of valid players from /api/players
  useEffect(() => {
    fetch('/api/players')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        //data.players is an array of { name, id }
        setPlayers(data.players || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch players:', err);
        setError("Failed to load player list.");
        setLoading(false);
      });
  }, []);

  //add or remove leg
  const addLeg = () => {
    if (legs.length < MAX_LEGS) {
      setLegs([...legs, { player: '', prop: '', value: '', overUnder: '' }]);
    }
  };
  const removeLeg = () => {
    if (legs.length > MIN_LEGS) {
      setLegs(legs.slice(0, legs.length - 1));
    }
  };

  //updates either playerName, prop, value, overUnder. If updating playerName,
  //also look up the corresponding playerId from our players array.
  const updateLeg = (index, field, value) => {
    const updated = [...legs];
    if (field === 'playerName') {
      // Find the object whose .name matches the typed value (if any)
      const match = players.find(p => p.name === value);
      updated[index].playerName = value;
      updated[index].playerId = match ? match.id : '';
    } else {
      updated[index][field] = value;
    }
    setLegs(updated);
  };

  //validate the line: must be >= 0.5 and must not be a whole integer (e.g. 2.0)
  const isValidLine = (val) => {
    if (val === '' || isNaN(val)) return false;
    const num = parseFloat(val);
    if (num < 0.5) return false;
    // Must end in .5, not .0
    // e.g. 2.5 → (2.5 * 10) % 10 = 5, okay
    //       2.0 → (2.0 * 10) % 10 = 0, fail
    return (num * 10) % 10 === 5;
  };

  //handle form submission: call POST /api/parlay, then navigate with actual data
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    //validate each leg
    for (let i = 0; i < legs.length; i++) {
      const leg = legs[i];
      if (!leg.playerId) {
        setError(`Leg ${i + 1}: Player "${leg.playerName}" is invalid.`);
        return;
      }
      if (!leg.prop) {
        setError(`Leg ${i + 1}: Please choose a prop.`);
        return;
      }
      if (!isValidLine(leg.value)) {
        setError(
          `Leg ${i + 1}: Line must be ≥ 0.5 and end in .5`
        );
        return;
      }
      if (leg.overUnder !== 'over' && leg.overUnder !== 'under') {
        setError(`Leg ${i + 1}: Please choose "Over" or "Under".`);
        return;
      }
    }

    // Build payload exactly as backend expects (props in lowercase)
    const payload = {
      parlayLegs: legs.map((l) => ({
        player: l.playerName,
        prop: l.prop, // already lowercase from the select value
        value: parseFloat(l.value),
        overUnder: l.overUnder,
      })),
    };

    try {
      const res = await fetch('/api/parlay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || `HTTP ${res.status}`);
      }
      const data = await res.json();
      // Pass the result to the results page, along with a local name→ID map
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
