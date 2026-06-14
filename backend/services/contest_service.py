from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.contest import Contest, ContestStatus
from models.leaderboard import LeaderboardEntry
from models.user import User
from services.payment_service import deduct_entry_fee
from services.notification_service import create_notification
from models.notification import NotificationType


class ContestFactory:
    """
    Design Pattern: Factory
    Encapsulates all validation and setup logic for contest creation.
    Ensures every contest is born in a consistent, valid state.
    """

    @staticmethod
    def create(db: Session, data: dict, created_by: int) -> Contest:
        if data["entry_fee"] < 0:
            raise HTTPException(status_code=400, detail="Entry fee cannot be negative")
        if data["prize_pool"] < data["entry_fee"]:
            raise HTTPException(status_code=400, detail="Prize pool must be >= entry fee")
        if data["max_teams"] < 2:
            raise HTTPException(status_code=400, detail="Contest needs at least 2 teams")

        contest = Contest(
            name=data["name"],
            description=data.get("description"),
            sport=data["sport"],
            match_name=data["match_name"],
            entry_fee=data["entry_fee"],
            prize_pool=data["prize_pool"],
            max_teams=data["max_teams"],
            status=ContestStatus.UPCOMING,
            starts_at=data["starts_at"],
            created_by=created_by,
        )
        db.add(contest)
        db.commit()
        db.refresh(contest)
        return contest


def list_contests(db: Session, status_filter: str | None = None) -> list[Contest]:
    q = db.query(Contest)
    if status_filter:
        q = q.filter(Contest.status == status_filter)
    return q.order_by(Contest.starts_at.desc()).all()


def get_contest(db: Session, contest_id: int) -> Contest:
    c = db.query(Contest).filter(Contest.id == contest_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contest not found")
    return c


def join_contest(db: Session, contest_id: int, team_id: int, user: User) -> dict:
    contest = get_contest(db, contest_id)

    if contest.status == ContestStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Contest is already completed")
    if contest.status == ContestStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Contest is cancelled")
    if contest.current_teams >= contest.max_teams:
        raise HTTPException(status_code=400, detail="Contest is full")

    existing = db.query(LeaderboardEntry).filter(
        LeaderboardEntry.contest_id == contest_id,
        LeaderboardEntry.user_id == user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Already joined this contest")

    from models.team import Team
    team = db.query(Team).filter(Team.id == team_id, Team.user_id == user.id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found or doesn't belong to you")
    if team.contest_id != contest_id:
        raise HTTPException(status_code=400, detail="Team was not built for this contest")

    wallet = deduct_entry_fee(db, user.id, contest.entry_fee, contest_id)

    entry = LeaderboardEntry(
        contest_id=contest_id,
        user_id=user.id,
        team_id=team_id,
        total_points=0.0,
        rank=None,
    )
    db.add(entry)
    contest.current_teams += 1
    team.is_locked = True
    db.commit()
    db.refresh(wallet)

    db.commit()
    create_notification(
        db, user.id, NotificationType.CONTEST_JOINED,
        "Contest Joined!",
        f"You joined '{contest.name}'. Entry fee ₹{contest.entry_fee} deducted.",
    )
    db.commit()

    return {
        "message": "Successfully joined contest",
        "contest_id": contest_id,
        "team_id": team_id,
        "entry_fee_deducted": contest.entry_fee,
        "wallet_balance_remaining": wallet.balance,
    }
