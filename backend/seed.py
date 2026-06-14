"""
Seed script: populates the player pool on first run.
Players represent a realistic cricket squad split across two teams.
"""
import logging
from database import SessionLocal
from models.player import Player, PlayerRole

logger = logging.getLogger("seed")

PLAYERS = [
    # Team India
    {"name": "Rohit Sharma",    "team_name": "India", "role": PlayerRole.BATSMAN,        "credit_value": 10.0, "country": "India"},
    {"name": "Virat Kohli",     "team_name": "India", "role": PlayerRole.BATSMAN,        "credit_value": 10.5, "country": "India"},
    {"name": "KL Rahul",        "team_name": "India", "role": PlayerRole.WICKET_KEEPER,  "credit_value": 9.5,  "country": "India"},
    {"name": "Hardik Pandya",   "team_name": "India", "role": PlayerRole.ALL_ROUNDER,    "credit_value": 9.0,  "country": "India"},
    {"name": "Ravindra Jadeja", "team_name": "India", "role": PlayerRole.ALL_ROUNDER,    "credit_value": 9.0,  "country": "India"},
    {"name": "Jasprit Bumrah",  "team_name": "India", "role": PlayerRole.BOWLER,         "credit_value": 10.0, "country": "India"},
    {"name": "Mohammed Shami",  "team_name": "India", "role": PlayerRole.BOWLER,         "credit_value": 8.5,  "country": "India"},
    {"name": "Shubman Gill",    "team_name": "India", "role": PlayerRole.BATSMAN,        "credit_value": 9.0,  "country": "India"},
    {"name": "Suryakumar Yadav","team_name": "India", "role": PlayerRole.BATSMAN,        "credit_value": 9.5,  "country": "India"},
    {"name": "Axar Patel",      "team_name": "India", "role": PlayerRole.ALL_ROUNDER,    "credit_value": 8.0,  "country": "India"},
    {"name": "Kuldeep Yadav",   "team_name": "India", "role": PlayerRole.BOWLER,         "credit_value": 8.0,  "country": "India"},
    # Australia
    {"name": "David Warner",    "team_name": "Australia", "role": PlayerRole.BATSMAN,        "credit_value": 10.0, "country": "Australia"},
    {"name": "Steve Smith",     "team_name": "Australia", "role": PlayerRole.BATSMAN,        "credit_value": 10.5, "country": "Australia"},
    {"name": "Pat Cummins",     "team_name": "Australia", "role": PlayerRole.BOWLER,         "credit_value": 10.0, "country": "Australia"},
    {"name": "Mitchell Starc",  "team_name": "Australia", "role": PlayerRole.BOWLER,         "credit_value": 9.5,  "country": "Australia"},
    {"name": "Glenn Maxwell",   "team_name": "Australia", "role": PlayerRole.ALL_ROUNDER,    "credit_value": 9.5,  "country": "Australia"},
    {"name": "Alex Carey",      "team_name": "Australia", "role": PlayerRole.WICKET_KEEPER,  "credit_value": 8.5,  "country": "Australia"},
    {"name": "Travis Head",     "team_name": "Australia", "role": PlayerRole.BATSMAN,        "credit_value": 9.0,  "country": "Australia"},
    {"name": "Josh Hazlewood",  "team_name": "Australia", "role": PlayerRole.BOWLER,         "credit_value": 8.5,  "country": "Australia"},
    {"name": "Cameron Green",   "team_name": "Australia", "role": PlayerRole.ALL_ROUNDER,    "credit_value": 8.5,  "country": "Australia"},
    {"name": "Marnus Labuschagne","team_name":"Australia", "role": PlayerRole.BATSMAN,       "credit_value": 9.0,  "country": "Australia"},
    {"name": "Adam Zampa",      "team_name": "Australia", "role": PlayerRole.BOWLER,         "credit_value": 8.0,  "country": "Australia"},
]


def seed_players():
    db = SessionLocal()
    try:
        existing = db.query(Player).count()
        if existing > 0:
            return
        for p in PLAYERS:
            db.add(Player(**p))
        db.commit()
        logger.info(f"Seeded {len(PLAYERS)} players")
    except Exception as e:
        db.rollback()
        logger.error(f"Seed failed: {e}")
    finally:
        db.close()
