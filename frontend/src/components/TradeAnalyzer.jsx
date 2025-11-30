import { useEffect, useState } from "react";
import { analyzeTrade, fetchPlayers } from "../api";

const POSITIONS = ["ALL", "QB", "RB", "WR", "TE"];

export default function TradeAnalyzer() {
  const [players, setPlayers] = useState([]);
  const [positionFilter, setPositionFilter] = useState("ALL");
  const [selectedPlayerId, setSelectedPlayerId] = useState("");
  const [teamA, setTeamA] = useState([]); // array of player objects
  const [teamB, setTeamB] = useState([]); // array of player objects
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loadingPlayers, setLoadingPlayers] = useState(false);

  // Load players on mount and when positionFilter changes
  useEffect(() => {
    loadPlayers(positionFilter);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [positionFilter]);

  async function loadPlayers(filter) {
    try {
      setLoadingPlayers(true);
      setError("");

      let pos = null;
      if (filter && filter !== "ALL") {
        pos = filter;
      }

      const data = await fetchPlayers(pos);
      setPlayers(data);

      // Reset selection when list changes
      setSelectedPlayerId("");
    } catch (err) {
      setError(err.message || "Error loading players");
    } finally {
      setLoadingPlayers(false);
    }
  }

  function handleAddToTeam(teamSetter, team, playerId) {
    if (!playerId) return;

    const player = players.find((p) => p.id === playerId);
    if (!player) return;

    // avoid duplicates
    const alreadyInTeam = team.some((p) => p.id === player.id);
    if (alreadyInTeam) return;

    teamSetter([...team, player]);
  }

  function handleRemoveFromTeam(teamSetter, team, playerId) {
    teamSetter(team.filter((p) => p.id !== playerId));
  }

  async function handleAnalyze(e) {
    e.preventDefault();
    setError("");
    setResult(null);

    if (teamA.length === 0 || teamB.length === 0) {
      setError("Please add at least one player to both Team A and Team B.");
      return;
    }

    const teamAIds = teamA.map((p) => p.id);
    const teamBIds = teamB.map((p) => p.id);

    try {
      const analysis = await analyzeTrade(teamAIds, teamBIds);
      setResult(analysis);
    } catch (err) {
      setError(err.message || "Error analyzing trade");
    }
  }

  return (
    <section style={{ marginTop: "2rem" }}>
      <h2>Trade Analyzer</h2>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {/* Player selection & filter */}
      <div
        style={{
          border: "1px solid #ccc",
          padding: "1rem",
          borderRadius: "4px",
          marginBottom: "1rem",
        }}
      >
        <h3>Player Pool</h3>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "1rem",
            marginBottom: "0.75rem",
          }}
        >
          <label>
            Position filter:{" "}
            <select
              value={positionFilter}
              onChange={(e) => setPositionFilter(e.target.value)}
            >
              {POSITIONS.map((pos) => (
                <option key={pos} value={pos}>
                  {pos}
                </option>
              ))}
            </select>
          </label>

          {loadingPlayers && <span>Loading players...</span>}
        </div>

        <div style={{ display: "flex", gap: "1rem", alignItems: "flex-start" }}>
          <div style={{ flex: 1 }}>
            <label>
              Available players:{" "}
              <select
                size={8}
                style={{ width: "100%" }}
                value={selectedPlayerId}
                onChange={(e) => setSelectedPlayerId(e.target.value)}
              >
                <option value="" disabled>
                  -- select a player --
                </option>
                {players.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.team} {p.position})
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "0.5rem",
              marginTop: "0.5rem",
            }}
          >
            <button
              type="button"
              disabled={!selectedPlayerId}
              onClick={() =>
                handleAddToTeam(setTeamA, teamA, selectedPlayerId)
              }
            >
              Add to Team A
            </button>
            <button
              type="button"
              disabled={!selectedPlayerId}
              onClick={() =>
                handleAddToTeam(setTeamB, teamB, selectedPlayerId)
              }
            >
              Add to Team B
            </button>
          </div>
        </div>
      </div>

      {/* Team A / Team B rosters */}
      <form onSubmit={handleAnalyze}>
        <div style={{ display: "flex", gap: "1rem" }}>
          {/* Team A column */}
          <div style={{ flex: 1, border: "1px solid #ccc", padding: "1rem" }}>
            <h3>Team A gives</h3>
            {teamA.length === 0 ? (
              <p style={{ fontStyle: "italic" }}>No players added yet.</p>
            ) : (
              <ul style={{ listStyle: "none", paddingLeft: 0 }}>
                {teamA.map((p) => (
                  <li
                    key={p.id}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: "0.25rem",
                    }}
                  >
                    <span>
                      {p.name} ({p.team} {p.position})
                    </span>
                    <button
                      type="button"
                      onClick={() =>
                        handleRemoveFromTeam(setTeamA, teamA, p.id)
                      }
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Team B column */}
          <div style={{ flex: 1, border: "1px solid #ccc", padding: "1rem" }}>
            <h3>Team B gives</h3>
            {teamB.length === 0 ? (
              <p style={{ fontStyle: "italic" }}>No players added yet.</p>
            ) : (
              <ul style={{ listStyle: "none", paddingLeft: 0 }}>
                {teamB.map((p) => (
                  <li
                    key={p.id}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: "0.25rem",
                    }}
                  >
                    <span>
                      {p.name} ({p.team} {p.position})
                    </span>
                    <button
                      type="button"
                      onClick={() =>
                        handleRemoveFromTeam(setTeamB, teamB, p.id)
                      }
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <button type="submit" style={{ marginTop: "1rem" }}>
          Analyze Trade
        </button>
      </form>

      {result && (
        <div style={{ marginTop: "1rem" }}>
          <h3>Results</h3>
          <p>Team A total ROS: {result.team_a_total}</p>
          <p>Team B total ROS: {result.team_b_total}</p>
          <p>Delta (Team A perspective): {result.delta_a}</p>
          <p>
            Verdict: <strong>{result.verdict}</strong>
          </p>
        </div>
      )}
    </section>
  );
}
