from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from middleware.auth_middleware import get_current_user, get_admin_user
from models.user import User
from schemas.contest import ContestCreate, ContestOut, ContestJoinRequest, ContestJoinResponse
from services import contest_service

router = APIRouter(prefix="/contests", tags=["Contests"])


@router.get("", response_model=list[ContestOut])
def list_contests(
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return contest_service.list_contests(db, status)


@router.post("", status_code=201, response_model=ContestOut)
def create_contest(
    req: ContestCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    return contest_service.ContestFactory.create(db, req.model_dump(), admin.id)


@router.get("/{contest_id}", response_model=ContestOut)
def get_contest(contest_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return contest_service.get_contest(db, contest_id)


@router.post("/{contest_id}/join", response_model=ContestJoinResponse)
def join_contest(
    contest_id: int,
    req: ContestJoinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return contest_service.join_contest(db, contest_id, req.team_id, current_user)
