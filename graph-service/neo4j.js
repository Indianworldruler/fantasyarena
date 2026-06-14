const neo4j = require("neo4j-driver");

const driver = neo4j.driver(
  process.env.NEO4J_URI || "bolt://localhost:7687",
  neo4j.auth.basic(
    process.env.NEO4J_USER || "neo4j",
    process.env.NEO4J_PASSWORD || "password"
  ),
  {
    maxConnectionPoolSize: 50,
    connectionAcquisitionTimeout: 5000,
  }
);

async function verifyConnection() {
  const session = driver.session();
  try {
    await session.run("RETURN 1");
    console.log("Neo4j connected");
  } catch (err) {
    console.warn("Neo4j unavailable — graph features disabled:", err.message);
  } finally {
    await session.close();
  }
}

async function runQuery(cypher, params = {}) {
  const session = driver.session();
  try {
    const result = await session.run(cypher, params);
    return result.records;
  } finally {
    await session.close();
  }
}

module.exports = { driver, verifyConnection, runQuery };
