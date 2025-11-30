const BASE_URL = "http://localhost:8000";

export async function fetchRosRankings(position) {
  const url = position
    ? `${BASE_URL}/rankings/ros?position=${encodeURIComponent(position)}`
    : `${BASE_URL}/rankings/ros`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch rankings");
  return res.json();
}

export async function analyzeTrade(teamAIds, teamBIds) {
  const res = await fetch(`${BASE_URL}/trade/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ team_a: teamAIds, team_b: teamBIds }),
  });
  if (!res.ok) throw new Error("Failed to analyze trade");
  return res.json();
}

export async function fetchPlayers(position) {
  const url = position
    ? `${BASE_URL}/players?position=${encodeURIComponent(position)}`
    : `${BASE_URL}/players`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch players");
  return res.json();
}
