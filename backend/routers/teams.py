from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from middleware.auth_middleware import get_current_user
from models.user import User
from schemas.team import TeamCreate, TeamOut, PlayerOut
from services import team_service

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/players/all", response_model=list[PlayerOut])
def list_players(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return team_service.get_players(db)


@router.get("", response_model=list[dict])
def list_teams(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return team_service.list_user_teams(db, current_user.id)


@router.post("", status_code=201, response_model=dict)
def create_team(req: TeamCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    players_input = [p.model_dump() for p in req.players]
    team = team_service.create_team(db, current_user.id, req.name, req.contest_id, players_input)
    return team_service.get_team_with_players(db, team.id, current_user.id)


@router.get("/{team_id}", response_model=dict)
def get_team(team_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return team_service.get_team_with_players(db, team_id, current_user.id)


@router.delete("/{team_id}", status_code=204)
def delete_team(team_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from models.team import Team
    from fastapi import HTTPException
    team = db.query(Team).filter(Team.id == team_id, Team.user_id == current_user.id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.is_locked:
        raise HTTPException(status_code=400, detail="Cannot delete a locked team (already joined a contest)")
    db.delete(team)
    db.commit()
