// frontend/src/api.js

// Base URL for the backend.
// - In local dev (no env var): http://localhost:8000
// - In Docker / Render: set VITE_BACKEND_URL to your backend URL or service name.
const BACKEND_BASE_URL =
  import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

/**
 * Helper to build a full URL from a path.
 */
function buildUrl(path) {
  const trimmedBase = BACKEND_BASE_URL.replace(/\/+$/, "");
  const trimmedPath = path.replace(/^\/+/, "");
  return `${trimmedBase}/${trimmedPath}`;
}

/**
 * Get ROS rankings from the backend.
 * position: "ALL" | "QB" | "RB" | "WR" | "TE" | "K" | "D/ST"
 * Returns the full JSON object from /rankings/ros.
 */
export async function getRosRankings(position = "ALL") {
  try {
    const url = new URL(buildUrl("/rankings/ros"));

    if (position && position !== "ALL") {
      url.searchParams.set("position", position);
    }

    const res = await fetch(url.toString());
    if (!res.ok) {
      throw new Error(`Failed to fetch ROS rankings: ${res.status}`);
    }

    const data = await res.json();
    // Expected shape:
    // {
    //   position: string,
    //   generated_at: string,
    //   players: [
    //     {
    //       id: number,
    //       name: string,
    //       team: string,
    //       position: string,
    //       ros_score: number,
    //       tier_label: string,
    //       total_points: number | null,
    //       weekly_projection: number | null,
    //       matchup: string | null
    //     },
    //     ...
    //   ]
    // }
    return data;
  } catch (err) {
    console.error("Error in getRosRankings:", err);
    throw err;
  }
}

/**
 * Backwards-compatible alias for older components.
 * RosRankings.jsx currently imports { fetchRosRankings }.
 */
export const fetchRosRankings = getRosRankings;

/**
 * Fetch the player pool for the Trade Analyzer.
 * Returns an array of players.
 */
export async function fetchPlayers() {
  try {
    const res = await fetch(buildUrl("/players"));

    if (!res.ok) {
      throw new Error(`Failed to fetch players: ${res.status}`);
    }

    const data = await res.json();
    // Expected shape:
    // [
    //   {
    //     id: number,
    //     name: string,
    //     team: string,
    //     position: string,
    //     ros_score: number,
    //     total_points?: number,
    //     weekly_projection?: number,
    //     matchup?: string
    //   },
    //   ...
    // ]
    return data;
  } catch (err) {
    console.error("Error in fetchPlayers:", err);
    throw err;
  }
}

/**
 * Call the backend trade analysis endpoint.
 * teamAIds / teamBIds are arrays of player IDs.
 */
export async function analyzeTrade(teamAIds, teamBIds) {
  try {
    const res = await fetch(buildUrl("/trades/analyze"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        team_a_ids: teamAIds,
        team_b_ids: teamBIds,
      }),
    });

    if (!res.ok) {
      throw new Error(`Trade analysis failed: ${res.status}`);
    }

    const data = await res.json();
    // Expected shape:
    // {
    //   team_a_total: number,
    //   team_b_total: number,
    //   delta_a: number,
    //   verdict: string
    // }
    return data;
  } catch (err) {
    console.error("Error in analyzeTrade:", err);
    throw err;
  }
}
