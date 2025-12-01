import React, { useEffect, useState } from 'react';
import { fetchRosRankings } from '../api';

const POSITIONS = ['ALL', 'QB', 'RB', 'WR', 'TE'];

const RosRankings = () => {
  const [position, setPosition] = useState('ALL');
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadRankings = async (pos) => {
    try {
      setLoading(true);
      setError('');
      const data = await fetchRosRankings(pos === 'ALL' ? undefined : pos);
      setRankings(data || []);
    } catch (err) {
      console.error(err);
      setError('Unable to load rankings right now.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRankings(position);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [position]);

  return (
    <section className="panel rankings-card">
      <div className="panel__header">
        <div>
          <h3 className="panel__title">Rest-of-Season Player Rankings</h3>
          <p className="panel__subtitle">
            Sorted by projected ROS value · filter by position and scroll through
            the leaderboard.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <select
            className="select"
            value={position}
            onChange={(e) => setPosition(e.target.value)}
          >
            {POSITIONS.map((pos) => (
              <option key={pos} value={pos}>
                {pos === 'ALL' ? 'All Positions' : pos}
              </option>
            ))}
          </select>
          <span className="chip">
            {rankings.length ? `${rankings.length} players` : 'No players loaded'}
          </span>
        </div>
      </div>

      {loading && <p style={{ fontSize: '0.85rem' }}>Loading rankings…</p>}
      {error && (
        <p
          style={{
            fontSize: '0.85rem',
            color: '#f97373',
            marginTop: '0.25rem',
          }}
        >
          {error}
        </p>
      )}

      {!loading && !error && (
        <div className="rankings-card__scroll">
          <table className="table">
            <thead>
              <tr>
                <th>#</th>
                <th>Player</th>
                <th>Team</th>
                <th>Pos</th>
                <th>ROS Pts</th>
                <th>Tier</th>
              </tr>
            </thead>
            <tbody>
              {rankings.map((row, idx) => (
                <tr key={row.player.id}>
                  <td>{idx + 1}</td>
                  <td>{row.player.name}</td>
                  <td>{row.player.team}</td>
                  <td>{row.player.position}</td>
                  <td>{row.ros_points}</td>
                  <td>{row.tier}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
};

export default RosRankings;
