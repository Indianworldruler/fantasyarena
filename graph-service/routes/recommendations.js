const express = require("express");
const { runQuery } = require("../neo4j");

const router = express.Router();

/**
 * GET /graph/recommendations/:userId
 *
 * Contest recommendations via collaborative filtering.
 *
 * Cypher strategy:
 *   Find contests joined by peers (users who share at least one contest with me),
 *   that I haven't joined yet. Rank by peer count (popularity signal).
 *
 *   MATCH (me:User {id})-[:JOINED]->(shared:Contest)<-[:JOINED]-(peer:User)
 *   MATCH (peer)-[:JOINED]->(rec:Contest)
 *   WHERE NOT (me)-[:JOINED]->(rec)
 *   RETURN rec.id, COUNT(DISTINCT peer) AS score
 *   ORDER BY score DESC LIMIT 5
 */
router.get("/:userId", async (req, res) => {
  const userId = parseInt(req.params.userId);
  const cypher = `
    MATCH (me:User {id: $userId})-[:JOINED]->(shared:Contest)<-[:JOINED]-(peer:User)
    MATCH (peer)-[:JOINED]->(rec:Contest)
    WHERE NOT (me)-[:JOINED]->(rec) AND me <> peer
    RETURN rec.id AS contestId, COUNT(DISTINCT peer) AS score
    ORDER BY score DESC
    LIMIT 5
  `;
  try {
    const records = await runQuery(cypher, { userId });
    const recommendations = records.map(r => ({
      contest_id: r.get("contestId").toNumber(),
      peer_count: r.get("score").toNumber(),
    }));
    res.json({ user_id: userId, recommendations });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /graph/recommendations/:userId/players
 *
 * Player recommendations: popular picks among users with overlapping contest history.
 *
 *   MATCH (me:User {id})-[:OWNS]->(myTeam:Team)-[:HAS_PLAYER]->(p:Player)
 *   WITH me, COLLECT(DISTINCT p.id) AS myPlayers
 *   MATCH (me)-[:JOINED]->(:Contest)<-[:JOINED]-(peer:User)
 *   MATCH (peer)-[:OWNS]->(peerTeam:Team)-[:HAS_PLAYER]->(rec:Player)
 *   WHERE NOT rec.id IN myPlayers
 *   RETURN rec.id AS playerId, COUNT(DISTINCT peer) AS popularity
 *   ORDER BY popularity DESC LIMIT 5
 */
router.get("/:userId/players", async (req, res) => {
  const userId = parseInt(req.params.userId);
  const cypher = `
    MATCH (me:User {id: $userId})-[:OWNS]->(myTeam:Team)-[:HAS_PLAYER]->(p:Player)
    WITH me, COLLECT(DISTINCT p.id) AS myPlayers
    MATCH (me)-[:JOINED]->(:Contest)<-[:JOINED]-(peer:User)
    MATCH (peer)-[:OWNS]->(peerTeam:Team)-[:HAS_PLAYER]->(rec:Player)
    WHERE NOT rec.id IN myPlayers AND me <> peer
    RETURN rec.id AS playerId, COUNT(DISTINCT peer) AS popularity
    ORDER BY popularity DESC
    LIMIT 5
  `;
  try {
    const records = await runQuery(cypher, { userId });
    const recommendations = records.map(r => ({
      player_id:  r.get("playerId").toNumber(),
      popularity: r.get("popularity").toNumber(),
    }));
    res.json({ user_id: userId, recommended_players: recommendations });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
