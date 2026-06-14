"""
Admin Service
Provides internal views, match event triggering, leaderboard inspection,
system logs, and metrics. All routes require is_admin JWT claim.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from middleware.auth_middleware import get_admin_user, get_current_user
from models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger("admin")


class LogBuffer(logging.Handler):
    def __init__(self, capacity: int = 200):
        super().__init__()
        self.capacity = capacity
        self.records: list[dict] = []

    def emit(self, record: logging.LogRecord):
        import datetime
        entry = {
            "ts":      datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "level":   record.levelname,
            "service": record.name,
            "msg":     self.format(record),
        }
        self.records.append(entry)
        if len(self.records) > self.capacity:
            self.records.pop(0)


log_buffer = LogBuffer()
logging.getLogger().addHandler(log_buffer)


@router.get("/setup/status")
def setup_status(db: Session = Depends(get_db)):
    """Public endpoint — checks if any admin exists. Used by first-run UI."""
    from models.user import User as U
    admin_exists = db.query(U).filter(U.is_admin == True).first() is not None
    return {"admin_exists": admin_exists}


@router.post("/setup/first-admin")
def create_first_admin(body: dict, db: Session = Depends(get_db)):
    """
    Public endpoint — only works when NO admin exists yet.
    Registers and promotes the first admin account.
    This removes the need to run any terminal command.
    """
    from models.user import User as U
    from services.auth_service import hash_password, create_token
    from models.wallet import Wallet
    from config import settings

    existing_admin = db.query(U).filter(U.is_admin == True).first()
    if existing_admin:
        raise HTTPException(status_code=403, detail="An admin account already exists. Use the login page.")

    username = body.get("username", "").strip()
    email    = body.get("email", "").strip()
    password = body.get("password", "")

    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="Username, email and password are required")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    if db.query(U).filter(U.username == username).first():
        raise HTTPException(status_code=409, detail="Username already taken")
    if db.query(U).filter(U.email == email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = U(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        full_name=body.get("full_name", ""),
        is_admin=True,
    )
    db.add(user)
    db.flush()

    wallet = Wallet(user_id=user.id, balance=settings.INITIAL_WALLET_BALANCE)
    db.add(wallet)
    db.commit()
    db.refresh(user)

    token = create_token(user)
    logger.info(f"First admin account created: {username}")
    return {
        "message": "Admin account created successfully",
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "is_admin": True,
    }


@router.get("/users")
def admin_list_users(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    from models.user import User as U
    from models.wallet import Wallet
    users = db.query(U).all()
    result = []
    for u in users:
        w = db.query(Wallet).filter(Wallet.user_id == u.id).first()
        result.append({
            "id": u.id, "username": u.username, "email": u.email,
            "is_admin": u.is_admin, "is_active": u.is_active,
            "wallet_balance": w.balance if w else 0.0,
            "created_at": u.created_at,
        })
    return result


@router.get("/contests")
def admin_list_contests(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    from models.contest import Contest
    return db.query(Contest).order_by(Contest.created_at.desc()).all()


@router.post("/contests", status_code=201)
def admin_create_contest(body: dict, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    from services.contest_service import ContestFactory
    from datetime import datetime
    data = {
        "name":        body["name"],
        "description": body.get("description"),
        "sport":       body.get("sport", "cricket"),
        "match_name":  body["match_name"],
        "entry_fee":   float(body["entry_fee"]),
        "prize_pool":  float(body["prize_pool"]),
        "max_teams":   int(body["max_teams"]),
        "starts_at":   datetime.fromisoformat(body["starts_at"].replace("Z", "+00:00")),
    }
    return ContestFactory.create(db, data, admin.id)


@router.get("/teams")
def admin_list_teams(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    from models.team import Team
    teams = db.query(Team).all()
    return [{
        "id": t.id, "name": t.name, "user_id": t.user_id,
        "contest_id": t.contest_id, "total_points": t.total_points,
        "is_locked": t.is_locked, "total_credits_used": t.total_credits_used,
    } for t in teams]


@router.get("/transactions")
def admin_list_transactions(
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    from models.transaction import Transaction
    txs = db.query(Transaction).order_by(Transaction.created_at.desc()).limit(limit).all()
    return [{
        "id": t.id, "user_id": t.user_id, "amount": t.amount,
        "type": t.type, "status": t.status,
        "description": t.description, "created_at": t.created_at,
    } for t in txs]


@router.get("/matches")
def admin_list_matches(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    from models.scoring import Match
    return db.query(Match).order_by(Match.created_at.desc()).all()


@router.post("/matches", status_code=201)
def admin_create_match(
    body: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    from services.scoring_service import create_match
    return create_match(db, body["name"], body.get("contest_id"), body["team_a"], body["team_b"])


@router.post("/matches/{match_id}/start")
def admin_start_match(match_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    from services.scoring_service import start_match
    return start_match(db, match_id)


@router.post("/matches/{match_id}/complete")
def admin_complete_match(match_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    from models.scoring import Match, MatchStatus
    from models.contest import Contest, ContestStatus
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    from datetime import datetime, timezone
    match.status = MatchStatus.COMPLETED
    match.completed_at = datetime.now(timezone.utc)
    if match.contest_id:
        contest = db.query(Contest).filter(Contest.id == match.contest_id).first()
        if contest:
            contest.status = ContestStatus.COMPLETED
            _distribute_prizes(db, contest)
    db.commit()
    logger.info(f"Match {match_id} completed")
    return {"message": f"Match {match_id} completed", "match_id": match_id}


def _distribute_prizes(db: Session, contest):
    from models.leaderboard import LeaderboardEntry
    from services.payment_service import credit_winnings
    from services.notification_service import create_notification
    from models.notification import NotificationType

    entries = (
        db.query(LeaderboardEntry)
        .filter(LeaderboardEntry.contest_id == contest.id)
        .order_by(LeaderboardEntry.total_points.desc())
        .all()
    )
    if not entries:
        return

    pool = contest.prize_pool
    prize_map = {1: 0.50, 2: 0.25, 3: 0.15}
    winners_count = max(1, len(entries) // 5)

    for rank, entry in enumerate(entries, start=1):
        pct = prize_map.get(rank, 0)
        if rank > 3 and rank <= winners_count:
            pct = 0.10 / max(winners_count - 3, 1)
        if pct > 0:
            prize = round(pool * pct, 2)
            entry.prize_won = prize
            credit_winnings(db, entry.user_id, prize, contest.id)
            create_notification(
                db, entry.user_id, NotificationType.PRIZE_AWARDED,
                "You won a prize! 🏆",
                f"Rank #{rank} in '{contest.name}'. ₹{prize} credited to wallet.",
            )
    db.commit()
    logger.info(f"Prizes distributed for contest {contest.id}")


@router.post("/promote/{username}")
def promote_to_admin(username: str, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    from models.user import User as U
    user = db.query(U).filter(U.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = True
    db.commit()
    logger.info(f"User '{username}' promoted to admin by '{admin.username}'")
    return {"message": f"{username} is now an admin"}


@router.get("/leaderboard/{contest_id}")
def admin_get_leaderboard(contest_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    from services.leaderboard_service import get_leaderboard
    return get_leaderboard(db, contest_id)


@router.get("/logs")
def admin_get_logs(limit: int = 50, admin: User = Depends(get_admin_user)):
    return {"logs": log_buffer.records[-limit:]}


@router.get("/metrics")
def admin_metrics(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    from logger import metrics as m
    from models.user import User as U
    from models.contest import Contest
    from models.team import Team
    from models.transaction import Transaction
    from models.scoring import Match, MatchStatus
    from routers.websocket import manager

    snap = m.snapshot()
    snap.update({
        "db": {
            "users":        db.query(U).count(),
            "contests":     db.query(Contest).count(),
            "teams":        db.query(Team).count(),
            "transactions": db.query(Transaction).count(),
            "live_matches": db.query(Match).filter(Match.status == MatchStatus.LIVE).count(),
        },
        "websocket": {
            "active_rooms": manager.active_connections(),
        },
    })
    return snap
