import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

function ResultPage() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const data = state || { parlayLegs: [] };

  return (
    <div>
      <h1>Parlay Results</h1>
      <p><strong>Overall Probability:</strong> TBD</p>
      <table>
        <thead>
          <tr><th>Player</th><th>Prop</th><th>Line</th><th>Type</th></tr>
        </thead>
        <tbody>
          {data.parlayLegs.map((leg, idx) => (
            <tr key={idx}>
              <td>{leg.player}</td>
              <td>{leg.prop}</td>
              <td>{leg.value}</td>
              <td>{leg.overUnder}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <button onClick={() => navigate('/')}>New Parlay</button>
    </div>
  );
}

export default ResultPage;