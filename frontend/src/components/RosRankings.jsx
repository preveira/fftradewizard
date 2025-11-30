import { useEffect, useState } from "react";
import { fetchRosRankings } from "../api";

const POSITIONS = ["ALL", "QB", "RB", "WR", "TE"];

export default function RosRankings() {
  const [position, setPosition] = useState("WR");
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadRankings(position === "ALL" ? null : position);
  }, [position]);

  async function loadRankings(pos) {
    setLoading(true);
    setError("");
    try {
      const data = await fetchRosRankings(pos);
      setRankings(data);
    } catch (err) {
      setError(err.message || "Error loading rankings");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <h2>Rest-of-Season Rankings</h2>

      <label>
        Position:{" "}
        <select
          value={position}
          onChange={(e) => setPosition(e.target.value)}
        >
          {POSITIONS.map((pos) => (
            <option key={pos} value={pos}>
              {pos}
            </option>
          ))}
        </select>
      </label>

      {loading && <p>Loading rankings...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!loading && !error && rankings.length > 0 && (
        <table
          style={{ width: "100%", marginTop: "1rem", borderCollapse: "collapse" }}
        >
          <thead>
            <tr>
              <th align="left">#</th>
              <th align="left">Player</th>
              <th align="left">Team</th>
              <th align="left">Pos</th>
              <th align="right">ROS Pts</th>
              <th align="left">Tier</th>
            </tr>
          </thead>
          <tbody>
            {rankings.map((row, idx) => (
              <tr key={row.player.id}>
                <td>{idx + 1}</td>
                <td>{row.player.name}</td>
                <td>{row.player.team}</td>
                <td>{row.player.position}</td>
                <td align="right">{row.ros_points}</td>
                <td>{row.tier}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
