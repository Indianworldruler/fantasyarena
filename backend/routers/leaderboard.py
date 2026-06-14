from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from middleware.auth_middleware import get_current_user
from models.user import User
from services import leaderboard_service

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("/{contest_id}")
def get_leaderboard(contest_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return leaderboard_service.get_leaderboard(db, contest_id)
