from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from middleware.auth_middleware import get_current_user
from models.user import User
from schemas.user import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(req: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if req.full_name is not None:
        current_user.full_name = req.full_name
    if req.email is not None:
        current_user.email = req.email
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/summary", response_model=dict)
def get_my_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Aggregate stats for the dashboard: contests joined, total winnings,
    teams created. Computed across all of the user's leaderboard entries.
    """
    from models.leaderboard import LeaderboardEntry
    from models.team import Team

    contests_joined = db.query(func.count(LeaderboardEntry.id)).filter(
        LeaderboardEntry.user_id == current_user.id
    ).scalar() or 0

    total_winnings = db.query(func.coalesce(func.sum(LeaderboardEntry.prize_won), 0.0)).filter(
        LeaderboardEntry.user_id == current_user.id
    ).scalar() or 0.0

    teams_created = db.query(func.count(Team.id)).filter(
        Team.user_id == current_user.id
    ).scalar() or 0

    return {
        "contests_joined": contests_joined,
        "total_winnings": round(total_winnings, 2),
        "teams_created": teams_created,
    }
