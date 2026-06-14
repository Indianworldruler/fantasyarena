const express = require("express");
const { runQuery } = require("../neo4j");

const router = express.Router();

/**
 * POST /graph/relationships
 * Write a typed relationship into the graph.
 *
 * Body: { type, fromId, fromLabel, toId, toLabel, props }
 *
 * Supported types: JOINED, OWNS, HAS_PLAYER, ENTERED, FEATURES
 *
 * Uses MERGE so duplicate calls are idempotent.
 */
router.post("/", async (req, res) => {
  const { type, fromId, fromLabel, toId, toLabel, props = {} } = req.body;
  if (!type || !fromId || !fromLabel || !toId || !toLabel) {
    return res.status(400).json({ error: "type, fromId, fromLabel, toId, toLabel required" });
  }

  const cypher = `
    MERGE (a:${fromLabel} {id: $fromId})
    MERGE (b:${toLabel} {id: $toId})
    MERGE (a)-[r:${type}]->(b)
    SET r += $props
    RETURN type(r) AS rel, a.id AS from, b.id AS to
  `;

  try {
    const records = await runQuery(cypher, {
      fromId: parseInt(fromId),
      toId: parseInt(toId),
      props,
    });
    const rec = records[0];
    res.json({
      relationship: rec.get("rel"),
      from: rec.get("from").toNumber(),
      to: rec.get("to").toNumber(),
    });
  } catch (err) {
    console.error("Relationship write failed:", err.message);
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /graph/relationships/contest/:contestId/participants
 *
 * Cypher: Find all users who joined a contest.
 * (:User)-[:JOINED]->(:Contest {id})
 */
router.get("/contest/:contestId/participants", async (req, res) => {
  const contestId = parseInt(req.params.contestId);
  const cypher = `
    MATCH (u:User)-[:JOINED]->(c:Contest {id: $contestId})
    RETURN u.id AS userId
    ORDER BY u.id
  `;
  try {
    const records = await runQuery(cypher, { contestId });
    res.json({ contest_id: contestId, participants: records.map(r => r.get("userId").toNumber()) });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /graph/relationships/player/:playerId/teams
 *
 * Cypher: All teams that selected a given player.
 * (:Team)-[:HAS_PLAYER]->(:Player {id})
 */
router.get("/player/:playerId/teams", async (req, res) => {
  const playerId = parseInt(req.params.playerId);
  const cypher = `
    MATCH (t:Team)-[:HAS_PLAYER]->(p:Player {id: $playerId})
    RETURN t.id AS teamId
    ORDER BY t.id
  `;
  try {
    const records = await runQuery(cypher, { playerId });
    res.json({ player_id: playerId, teams: records.map(r => r.get("teamId").toNumber()) });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
