import React, { useEffect, useMemo, useState } from 'react';
import { fetchRosRankings, analyzeTrade } from '../api';

const POSITIONS = ['ALL', 'QB', 'RB', 'WR', 'TE'];

const TradeAnalyzer = () => {
  const [positionFilter, setPositionFilter] = useState('ALL');
  const [playerPool, setPlayerPool] = useState([]);
  const [teamA, setTeamA] = useState([]);
  const [teamB, setTeamB] = useState([]);
  const [loadingPlayers, setLoadingPlayers] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');

  // Load from ROS rankings so pool == "active relevant" players
  const loadPlayers = async () => {
    try {
      setLoadingPlayers(true);
      setError('');
      const data = await fetchRosRankings(); // same source as rankings page

      // Flatten ROSResult objects into simple player entries for the trade UI
      let flattened = (Array.isArray(data) ? data : []).map((row) => ({
        id: row.player.id,
        name: row.player.name,
        team: row.player.team,
        position: row.player.position,
        rosScore: row.ros_score ?? row.ros_points ?? 0,
      }));

      // 🔽 Sort highest ROS score → lowest
      flattened.sort((a, b) => b.rosScore - a.rosScore);

      setPlayerPool(flattened);
    } catch (err) {
      console.error(err);
      setError('Unable to load player pool.');
    } finally {
      setLoadingPlayers(false);
    }
  };

  useEffect(() => {
    loadPlayers();
  }, []);

  const filteredPool = useMemo(() => {
    if (positionFilter === 'ALL') return playerPool;
    return playerPool.filter((p) => p.position === positionFilter);
  }, [playerPool, positionFilter]);

  const addToTeam = (player, team) => {
    if (team === 'A') {
      if (teamA.find((p) => p.id === player.id)) return;
      setTeamA((list) => [...list, player]);
    } else {
      if (teamB.find((p) => p.id === player.id)) return;
      setTeamB((list) => [...list, player]);
    }
    setAnalysis(null);
  };

  const removeFromTeam = (id, team) => {
    if (team === 'A') {
      setTeamA((list) => list.filter((p) => p.id !== id));
    } else {
      setTeamB((list) => list.filter((p) => p.id !== id));
    }
    setAnalysis(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!teamA.length || !teamB.length) {
      setError('Add at least one player to each side before analyzing.');
      return;
    }
    try {
      setSubmitting(true);
      setError('');
      const res = await analyzeTrade(
        teamA.map((p) => p.id),
        teamB.map((p) => p.id)
      );
      setAnalysis(res);
    } catch (err) {
      console.error(err);
      setError('Trade analysis failed. Try again in a moment.');
    } finally {
      setSubmitting(false);
    }
  };

  const resetTrade = () => {
    setTeamA([]);
    setTeamB([]);
    setAnalysis(null);
    setError('');
  };

  return (
    <section className="panel">
      <div className="panel__header">
        <div>
          <h3 className="panel__title">Trade Analyzer</h3>
          <p className="panel__subtitle">
            Build each side of a trade from the live ROS-ranked player pool, then let
            FFTradeWizard compare rest-of-season value.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <select
            className="select"
            value={positionFilter}
            onChange={(e) => setPositionFilter(e.target.value)}
          >
            {POSITIONS.map((pos) => (
              <option key={pos} value={pos}>
                {pos === 'ALL' ? 'All Positions' : pos}
              </option>
            ))}
          </select>
          <button
            type="button"
            className="btn btn--ghost"
            onClick={loadPlayers}
            disabled={loadingPlayers}
          >
            ⟳ Refresh
          </button>
        </div>
      </div>

      {error && (
        <p
          style={{
            fontSize: '0.85rem',
            color: '#f97373',
            marginBottom: '0.75rem',
          }}
        >
          {error}
        </p>
      )}

      <div className="grid-two">
        {/* Left: Player pool */}
        <div>
          <p className="panel__subtitle" style={{ margin: '0 0 0.5rem' }}>
            Player pool · pulled from ROS rankings (highest ROS at top) · click to add to a side.
          </p>
          <div className="rankings-card__scroll" style={{ maxHeight: 320 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Player</th>
                  <th>Team</th>
                  <th>Pos</th>
                  <th>ROS</th>
                  <th style={{ width: 140 }}>Add to</th>
                </tr>
              </thead>
              <tbody>
                {loadingPlayers && (
                  <tr>
                    <td colSpan={5}>Loading players…</td>
                  </tr>
                )}
                {!loadingPlayers && filteredPool.length === 0 && (
                  <tr>
                    <td colSpan={5}>No players found for this filter.</td>
                  </tr>
                )}
                {!loadingPlayers &&
                  filteredPool.map((p) => (
                    <tr key={p.id}>
                      <td>{p.name}</td>
                      <td>{p.team}</td>
                      <td>{p.position}</td>
                      <td>{p.rosScore.toFixed(1)}</td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.35rem' }}>
                          <button
                            type="button"
                            className="btn"
                            onClick={() => addToTeam(p, 'A')}
                          >
                            Team A
                          </button>
                          <button
                            type="button"
                            className="btn btn--ghost"
                            onClick={() => addToTeam(p, 'B')}
                          >
                            Team B
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right: Team rosters & result */}
        <div>
          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '0.75rem' }}>
            <div className="trade-team">
              <h4 className="trade-team__title">Team A gives</h4>
              <p className="trade-team__subtitle">
                Total players: <strong>{teamA.length}</strong>
              </p>
              <ul className="trade-team__list">
                {teamA.map((p) => (
                  <li key={p.id}>
                    <div className="trade-team__player-main">
                      <span className="trade-team__player-name">{p.name}</span>
                      <span className="trade-team__player-meta">
                        {p.team} · {p.position}
                      </span>
                    </div>
                    <button
                      type="button"
                      className="btn btn--ghost"
                      onClick={() => removeFromTeam(p.id, 'A')}
                    >
                      ✕
                    </button>
                  </li>
                ))}
                {!teamA.length && (
                  <li>
                    <span className="trade-team__player-meta">
                      No players selected yet.
                    </span>
                  </li>
                )}
              </ul>
            </div>

            <div className="trade-team">
              <h4 className="trade-team__title">Team B gives</h4>
              <p className="trade-team__subtitle">
                Total players: <strong>{teamB.length}</strong>
              </p>
              <ul className="trade-team__list">
                {teamB.map((p) => (
                  <li key={p.id}>
                    <div className="trade-team__player-main">
                      <span className="trade-team__player-name">{p.name}</span>
                      <span className="trade-team__player-meta">
                        {p.team} · {p.position}
                      </span>
                    </div>
                    <button
                      type="button"
                      className="btn btn--ghost"
                      onClick={() => removeFromTeam(p.id, 'B')}
                    >
                      ✕
                    </button>
                  </li>
                ))}
                {!teamB.length && (
                  <li>
                    <span className="trade-team__player-meta">
                      No players selected yet.
                    </span>
                  </li>
                )}
              </ul>
            </div>
          </div>

          <form
            onSubmit={handleSubmit}
            style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.6rem' }}
          >
            <button
              type="submit"
              className="btn"
              disabled={submitting || !teamA.length || !teamB.length}
            >
              {submitting ? 'Analyzing…' : 'Analyze Trade'}
            </button>
            <button
              type="button"
              className="btn btn--ghost"
              onClick={resetTrade}
              disabled={submitting || (!teamA.length && !teamB.length)}
            >
              Clear
            </button>
          </form>

          {analysis && (
            <div style={{ marginTop: '0.3rem' }}>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <span className="badge">
                  Team A total ROS: {analysis.team_a_total.toFixed(1)}
                </span>
                <span className="badge">
                  Team B total ROS: {analysis.team_b_total.toFixed(1)}
                </span>
                <span className="badge">
                  Δ Team A: {analysis.delta_a > 0 ? '+' : ''}
                  {analysis.delta_a.toFixed(1)}
                </span>
              </div>
              <p style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>
                Verdict:{' '}
                <strong style={{ color: '#e5e7eb' }}>{analysis.verdict}</strong>
              </p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default TradeAnalyzer;
