import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Select from "react-select";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import './HomePage.css';

//backend expects lowercase props; we will display them uppercased in the dropdown
const PROP_OPTIONS = [
  { value: "pts", label: "PTS" },
  { value: "reb", label: "REB" },
  { value: "ast", label: "AST" },
  { value: "stl", label: "STL" },
  { value: "blk", label: "BLK" },
  { value: "tov", label: "TOV" },
  { value: "fg3", label: "FG3" },
  { value: "fg", label: "FG" },
  { value: "ft", label: "FT" },
];
const MIN_LEGS = 2;
const MAX_LEGS = 6;

function HomePage() {
  const navigate = useNavigate();

  // Each leg has: player (name), playerId, prop (lowercase), value (string), overUnder
  const [legs, setLegs] = useState(
    Array.from({ length: MIN_LEGS }, () => ({
      player: null,
      playerId: '',
      prop: null,
      value: '',
      overUnder: '',
    }))
  );
  const [players, setPlayers] = useState([]); // Array of { name, id } objects from backend
  const [loading, setLoading] = useState(true);
  const [statsByLeg, setStatsByLeg] = useState({});

  // Fetch from /api/players
  useEffect(() => {
    fetch('/api/players/')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        // data.players is an array of { name, id }
        const opts = data.players.map((p) => ({
          value: p.name,
          label: p.name,
          id: p.id,
        }));
        setPlayers(opts);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch players:", err);
        toast.error("Failed to load player list.");
        setLoading(false);
      });
  }, []);

  //Whenever a leg’s playerId changes, fetch that player’s stats
  useEffect(() => {
    legs.forEach((leg, idx) => {
      if (!leg.playerId) return;
      const existing = statsByLeg[idx];
      if (existing && existing.playerId === leg.playerId) return;

      fetch(`/api/player_stats/${leg.playerId}`)
        .then((res) => {
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          return res.json();
        })
        .then((data) => {
          setStatsByLeg((prev) => ({
            ...prev,
            [idx]: {
              playerId: leg.playerId,
              career: data.career,
              recent: data.recent,
            },
          }));
        })
        .catch((err) => {
          console.error(`Failed to fetch stats for ${leg.playerId}:`, err);
          toast.error("Unable to fetch player stats.");
        });
    });
  }, [legs, statsByLeg]);

  // Add a new empty leg
  const addLeg = () => {
    if (legs.length < MAX_LEGS) {
      setLegs([
        ...legs,
        { player: null, playerId: '', prop: null, value: '', overUnder: '' },
      ]);
    }
  };

  // Remove last leg
  const removeLeg = () => {
    if (legs.length > MIN_LEGS) {
      const newLegs = legs.slice(0, -1);
      setLegs(newLegs);

      // Also remove that leg’s stats if present
      setStatsByLeg((prev) => {
        const copy = { ...prev };
        delete copy[newLegs.length]; // drop the old index
        return copy;
      });
    }
  };

  // Update a field in a specific leg
  const updateLeg = (index, field, value) => {
    const updated = [...legs];
    if (field === "player") {
      updated[index].player = value; // value is { value: name, label: name, id: id } or null
      updated[index].playerId = value ? value.id : "";
    } else if (field === "prop") {
      updated[index].prop = value;   // value is { value: "pts", label: "PTS" } or null
    } else {
      updated[index][field] = value; // for “value” or “overUnder”
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

  // Validate each leg
  const handleSubmit = async (e) => {
    e.preventDefault();

    for (let i = 0; i < legs.length; i++) {
      const leg = legs[i];
      if (!leg.playerId) {
        toast.error(`Leg ${i + 1}: Please select a valid player.`);
        return;
      }
      if (!leg.prop) {
        toast.error(`Leg ${i + 1}: Please select a prop.`);
        return;
      }
      if (!isValidLine(leg.value)) {
        toast.error(
          `Leg ${i + 1}: Line must be ≥ 0.5 and end in .5 (e.g. “2.5”).`
        );
        return;
      }
      if (leg.overUnder !== "over" && leg.overUnder !== "under") {
        toast.error(`Leg ${i + 1}: Please choose Over or Under.`);
        return;
      }
    }

    // Build payload
    const payload = {
      parlayLegs: legs.map((l) => ({
        player: l.player.value,        // the name string
        prop: l.prop.value,            // lowercase
        value: parseFloat(l.value),
        overUnder: l.overUnder,
      })),
    };

    try {
      const res = await fetch("/api/parlay/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || `HTTP ${res.status}`);
      }
      const data = await res.json();
      navigate("/results", {
        state: {
          ...data,
          playerMap: players.reduce((acc, p) => {
            acc[p.value] = p.id;
            return acc;
          }, {}),
        },
      });
    } catch (err) {
      console.error("Parlay evaluation failed:", err);
      toast.error("Failed to evaluate parlay. Please try again.");
    }
  };

  return (
    <div className="homepage">
      <h1 className="title">ParlAI</h1>
      {loading && <p>Loading player list…</p>}

      {!loading && (
        <>
        <ToastContainer
          position="top-center"
          autoClose={3000}
          hideProgressBar
          newestOnTop
          closeOnClick
          pauseOnFocusLoss={false}
          draggable
          pauseOnHover
        />

        <form className="parlay-form" onSubmit={handleSubmit}>
          {legs.map((leg, idx) => {
            // Grab stats if they exist
            const stats = statsByLeg[idx] || null;
            const career = stats ? stats.career : null;
            const recent = stats ? stats.recent : null;
            // Player image path
            const imgUrl = leg.playerId
              ? `/images/${leg.playerId}.png`
              : null;

            return (
              <div className="parlay-leg-row" key={idx}>
                {/* Player name input */}
                <Select
                    className="player-select"
                    classNamePrefix="react-select"
                    options={players}
                    placeholder="Player"
                    value={leg.player}
                    onChange={(opt) => updateLeg(idx, "player", opt)}
                    isClearable
                    styles={{
                      control: (provided) => ({
                        ...provided,
                        backgroundColor: "#1f1f1f",
                        borderColor: "#444",
                        color: "#fff",
                        minWidth: "200px",
                      }),
                      menu: (provided) => ({
                        ...provided,
                        backgroundColor: "#2a2a2a",
                      }),
                      singleValue: (provided) => ({
                        ...provided,
                        color: "#fff",
                      }),
                      placeholder: (provided) => ({
                        ...provided,
                        color: "#aaa",
                      }),
                      option: (provided, state) => ({
                        ...provided,
                        backgroundColor: state.isFocused
                          ? "#3a3a3a"
                          : "#2a2a2a",
                        color: "#fff",
                      }),
                    }}
                    theme={(theme) => ({
                      ...theme,
                      colors: {
                        ...theme.colors,
                        primary25: "#444",
                        primary: "#888",
                        neutral0: "#2a2a2a",
                        neutral80: "#fff",
                        neutral20: "#444",
                        neutral10: "#333",
                      },
                    })}
                  />

                {/* Prop dropdown (uppercase display, lowercase value) */}
                <Select
                    className="prop-select"
                    classNamePrefix="react-select"
                    options={PROP_OPTIONS}
                    placeholder="Prop"
                    value={leg.prop}
                    onChange={(opt) => updateLeg(idx, "prop", opt)}
                    isClearable
                    styles={{
                      control: (provided) => ({
                        ...provided,
                        backgroundColor: "#1f1f1f",
                        borderColor: "#444",
                        color: "#fff",
                        minWidth: "120px",
                      }),
                      menu: (provided) => ({
                        ...provided,
                        backgroundColor: "#2a2a2a",
                      }),
                      singleValue: (provided) => ({
                        ...provided,
                        color: "#fff",
                      }),
                      placeholder: (provided) => ({
                        ...provided,
                        color: "#aaa",
                      }),
                      option: (provided, state) => ({
                        ...provided,
                        backgroundColor: state.isFocused
                          ? "#3a3a3a"
                          : "#2a2a2a",
                        color: "#fff",
                      }),
                    }}
                    theme={(theme) => ({
                      ...theme,
                      colors: {
                        ...theme.colors,
                        primary25: "#444",
                        primary: "#888",
                        neutral0: "#2a2a2a",
                        neutral80: "#fff",
                        neutral20: "#444",
                        neutral10: "#333",
                      },
                    })}
                  />

                {/* Line input */}
                <input
                  type="number"
                  step="0.5"
                  min="0.5"
                  value={leg.value}
                  onChange={(e) => updateLeg(idx, "value", e.target.value)}
                  required
                  className="input slim-input"
                  placeholder="Line"
                />

                {/* Over/Under */}
                <div className="toggle-group">
                    <button
                      type="button"
                      className={`toggle-btn ${
                        leg.overUnder === "over" ? "active" : ""
                      }`}
                      onClick={() => updateLeg(idx, "overUnder", "over")}
                    >
                      OVER
                    </button>
                    <button
                      type="button"
                      className={`toggle-btn ${
                        leg.overUnder === "under" ? "active" : ""
                      }`}
                      onClick={() => updateLeg(idx, "overUnder", "under")}
                    >
                      UNDER
                    </button>
                </div>

                {leg.playerId && stats && (
                  <div className="player-info">
                    <img
                      src={imgUrl}
                      alt={leg.player.value}
                      className="player-photo"
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = "/images/placeholder.png";
                      }}
                    />
                    <div className="stats-table">
                      {/* Header row of stat names */}
                      <div className="stats-header">
                        <span className="stats-label"></span>
                        {PROP_OPTIONS.map((p) => (
                          <span key={`header-${p.value}`} className="stats-header-item">
                            {p.label}
                          </span>
                        ))}
                      </div>
                      <div className="stats-row">
                        <span className="stats-label">SINCE 2022</span>
                        {PROP_OPTIONS.map((p) => (
                          <span key={`career-${p.value}`} className="stat-value">
                            {career[p.value].toFixed(1)}
                          </span>
                        ))}
                      </div>
                      <div className="stats-row">
                        <span className="stats-label">LAST 5 GAMES</span>
                        {PROP_OPTIONS.map((p) => (
                          <span key={`recent-${p.value}`} className="stat-value">
                            {recent[p.value].toFixed(1)}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}

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
        </>
      )}
    </div>
  );
}

export default HomePage;
