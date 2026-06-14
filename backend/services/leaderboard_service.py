"""
Leaderboard Service

Ranking algorithm:
  1. Fetch all LeaderboardEntry rows for a contest
  2. Join with Team to get current total_points
  3. Sort descending by total_points (stable sort — earliest join wins tiebreak)
  4. Assign ranks 1..N
  5. Persist ranks back to DB
  6. Return ranked list with user/team detail

Caching note (system design):
  In production this would be a Redis sorted set (ZADD/ZRANGE).
  O(log N) insert, O(N) range query. Here we use in-memory sort which
  is fine for demo scale but would not survive 100k concurrent users.
"""

from sqlalchemy.orm import Session
from models.leaderboard import LeaderboardEntry
from models.team import Team
from models.user import User
from models.contest import Contest
from fastapi import HTTPException


def get_leaderboard(db: Session, contest_id: int) -> dict:
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    entries = (
        db.query(LeaderboardEntry)
        .filter(LeaderboardEntry.contest_id == contest_id)
        .order_by(LeaderboardEntry.total_points.desc())
        .all()
    )

    result = []
    for rank, entry in enumerate(entries, start=1):
        entry.rank = rank
        user  = db.query(User).filter(User.id == entry.user_id).first()
        team  = db.query(Team).filter(Team.id == entry.team_id).first()
        result.append({
            "rank":         rank,
            "user_id":      entry.user_id,
            "username":     user.username if user else "—",
            "team_id":      entry.team_id,
            "team_name":    team.name if team else "—",
            "total_points": entry.total_points,
            "prize_won":    entry.prize_won,
        })

    db.commit()
    return {"contest_id": contest_id, "contest_name": contest.name, "entries": result}


def sync_scores_to_leaderboard(db: Session, contest_id: int):
    """
    Pull latest team totals into leaderboard entries and re-rank.
    Called by the event bus after every scoring event.
    """
    entries = db.query(LeaderboardEntry).filter(LeaderboardEntry.contest_id == contest_id).all()
    for entry in entries:
        team = db.query(Team).filter(Team.id == entry.team_id).first()
        if team:
            entry.total_points = team.total_points

    entries.sort(key=lambda e: e.total_points, reverse=True)
    for rank, entry in enumerate(entries, start=1):
        entry.rank = rank

    db.commit()
