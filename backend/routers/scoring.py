from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from middleware.auth_middleware import get_current_user, get_admin_user
from models.user import User
from schemas.scoring import MatchCreate, MatchOut, MatchEventRequest, MatchEventResponse
from services import scoring_service
from event_bus import bus

router = APIRouter(prefix="/scoring", tags=["Scoring & Matches"])


@router.get("/matches", response_model=list[MatchOut])
def list_matches(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return scoring_service.get_matches(db)


@router.post("/matches", status_code=201, response_model=MatchOut)
def create_match(req: MatchCreate, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    return scoring_service.create_match(db, req.name, req.contest_id, req.team_a, req.team_b)


@router.post("/matches/{match_id}/start", response_model=MatchOut)
def start_match(match_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    return scoring_service.start_match(db, match_id)


@router.post("/event", response_model=MatchEventResponse)
async def trigger_event(
    req: MatchEventRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """
    Observer Pattern entry point:
    match.event → scoring_service → event_bus → leaderboard + notification + WebSocket
    """
    event = scoring_service.process_event(db, req.match_id, req.player_id, req.event_type, req.meta)

    from models.scoring import Match
    match = db.query(Match).filter(Match.id == req.match_id).first()

    await bus.publish("match.event", {
        "match_id":      req.match_id,
        "contest_id":    match.contest_id if match else None,
        "player_id":     req.player_id,
        "event_type":    req.event_type.value,
        "points":        event.points_awarded,
    })

    return MatchEventResponse(
        event_id=event.id,
        player_id=req.player_id,
        event_type=req.event_type.value,
        points_awarded=event.points_awarded,
        message=f"Event processed. {event.points_awarded} pts awarded.",
    )


@router.get("/{contest_id}/{team_id}")
def get_team_score(contest_id: int, team_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from models.team import Team, TeamPlayer
    from models.player import Player
    team = db.query(Team).filter(Team.id == team_id, Team.contest_id == contest_id).first()
    if not team:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Team not found in this contest")
    tps = db.query(TeamPlayer).filter(TeamPlayer.team_id == team_id).all()
    breakdown = []
    for tp in tps:
        p = db.query(Player).filter(Player.id == tp.player_id).first()
        breakdown.append({
            "player_name":    p.name if p else "—",
            "is_captain":     tp.is_captain,
            "is_vice_captain":tp.is_vice_captain,
            "points_earned":  tp.points_earned,
        })
    return {"team_id": team_id, "team_name": team.name, "total_points": team.total_points, "breakdown": breakdown}
