// frontend/src/api.js

// Use env var in production, fall back to localhost for dev
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// ROS rankings (used by rankings page + trade analyzer)
export async function fetchRosRankings(position) {
  const url = position
    ? `${BASE_URL}/rankings/ros?position=${encodeURIComponent(position)}`
    : `${BASE_URL}/rankings/ros`;

  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch rankings');
  return res.json();
}

// Optional alias (not required anymore, but harmless to keep)
export const getRosRankings = fetchRosRankings;

// Trade analysis
export async function analyzeTrade(teamAIds, teamBIds) {
  const res = await fetch(`${BASE_URL}/trade/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ team_a: teamAIds, team_b: teamBIds }),
  });

  if (!res.ok) throw new Error('Failed to analyze trade');
  return res.json();
}

// (Currently unused, but safe to keep if you want it later)
export async function fetchPlayers(position) {
  const url = position
    ? `${BASE_URL}/players?position=${encodeURIComponent(position)}`
    : `${BASE_URL}/players`;

  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch players');
  return res.json();
}
