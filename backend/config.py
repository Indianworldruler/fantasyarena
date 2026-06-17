import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

class Settings:
    APP_NAME: str = "FantasyArena"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # SQLite
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/fantasyarena_faculty.db"
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "fantasyarena-super-secret-key-change-in-prod")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24

    # Neo4j
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")

    # Graph service
    GRAPH_SERVICE_URL: str = os.getenv("GRAPH_SERVICE_URL", "http://localhost:4000")

    # CORS origins
    CORS_ORIGINS: list = ["*"]

    # Wallet
    INITIAL_WALLET_BALANCE: float = 1000.0
    MIN_CONTEST_ENTRY: float = 10.0
    MAX_TEAM_PLAYERS: int = 11
    MIN_TEAM_PLAYERS: int = 11

settings = Settings()
