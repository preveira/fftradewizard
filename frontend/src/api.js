// frontend/src/api.js

// Resolve backend base URL:
//
// Priority:
//   1. VITE_BACKEND_URL or VITE_API_BASE_URL (for flexibility)
//   2. If running on localhost -> http://localhost:8000
//   3. Otherwise -> Render backend: https://fftradewizard.onrender.com
//
const envBase =
  import.meta.env.VITE_BACKEND_URL || import.meta.env.VITE_API_BASE_URL;

const isBrowser = typeof window !== "undefined";
const isLocalhost =
  isBrowser &&
  (window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1");

const BACKEND_BASE_URL =
  envBase ||
  (isLocalhost
    ? "http://localhost:8000"
    : "https://fftradewizard.onrender.com");

/**
 * Helper to build a full URL from a path.
 */
function buildUrl(path) {
  const trimmedBase = BACKEND_BASE_URL.replace(/\/+$/, "");
  const trimmedPath = path.replace(/^\/+/, "");
  return `${trimmedBase}/${trimmedPath}`;
}

/**
 * Helper to handle JSON responses / errors.
 */
async function handleResponse(res) {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(
      `API error ${res.status}: ${text || res.statusText || "Unknown error"}`
    );
  }
  return res.json();
}

/**
 * Get ROS rankings from the backend.
 * position: "QB" | "RB" | "WR" | "TE" | "K" | "D/ST" | undefined
 * If omitted/undefined → all positions.
 *
 * Backend returns:
 *   [
 *     {
 *       player: { id, name, team, position, ... },
 *       ros_points,
 *       ros_score,
 *       season_points,
 *       week_projection,
 *       matchup,
 *       tier
 *     },
 *     ...
 *   ]
 */
export async function fetchRosRankings(position) {
  const url = new URL(buildUrl("/rankings/ros"));

  if (position) {
    url.searchParams.set("position", position);
  }

  const res = await fetch(url.toString(), {
    method: "GET",
  });

  return handleResponse(res);
}

// Backwards-compatible alias for any old imports
export const getRosRankings = fetchRosRankings;

/**
 * Fetch the player pool for the Trade Analyzer.
 * Optional position filter.
 *
 * Backend returns:
 *   [
 *     Player,
 *     ...
 *   ]
 */
export async function fetchPlayers(position) {
  const url = new URL(buildUrl("/players"));
  if (position) {
    url.searchParams.set("position", position);
  }

  const res = await fetch(url.toString(), {
    method: "GET",
  });

  return handleResponse(res);
}

/**
 * Call the backend trade analysis endpoint.
 * teamAIds / teamBIds are arrays of player IDs.
 *
 * Backend expects POST /trade/analyze
 * with JSON:
 *   { team_a_ids: string[], team_b_ids: string[] }
 */
export async function analyzeTrade(teamAIds, teamBIds) {
  const url = buildUrl("/trade/analyze"); // <-- FIXED PATH (no extra "s")

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      team_a_ids: teamAIds,
      team_b_ids: teamBIds,
    }),
  });

  return handleResponse(res);
}
