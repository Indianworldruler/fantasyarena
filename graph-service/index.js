require("dotenv").config();
const express = require("express");
const cors = require("cors");
const { verifyConnection } = require("./neo4j");

const relationshipsRouter = require("./routes/relationships");
const recommendationsRouter = require("./routes/recommendations");

const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors());
app.use(express.json());

app.use("/graph/relationships", relationshipsRouter);
app.use("/graph/recommendations", recommendationsRouter);

app.get("/health", (_, res) => {
  res.json({ status: "ok", service: "graph-service", port: PORT });
});

app.listen(PORT, async () => {
  console.log(`Graph service running on port ${PORT}`);
  await verifyConnection();
});
