from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.team import Team, TeamPlayer
from models.player import Player
from models.contest import Contest, ContestStatus
from config import settings


def get_players(db: Session) -> list[Player]:
    return db.query(Player).filter(Player.is_active == True).all()


def create_team(db: Session, user_id: int, name: str, contest_id: int, players_input: list[dict]) -> Team:
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    if contest.status == ContestStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Contest is completed, cannot create team")

    existing = db.query(Team).filter(Team.user_id == user_id, Team.contest_id == contest_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="You already have a team for this contest")

    player_ids = [p["player_id"] for p in players_input]
    if len(set(player_ids)) != len(player_ids):
        raise HTTPException(status_code=400, detail="Duplicate players not allowed")

    db_players = db.query(Player).filter(Player.id.in_(player_ids), Player.is_active == True).all()
    if len(db_players) != len(player_ids):
        raise HTTPException(status_code=400, detail="One or more players not found or inactive")

    player_map = {p.id: p for p in db_players}
    total_credits = sum(p.credit_value for p in db_players)
    if total_credits > 100:
        raise HTTPException(status_code=400, detail=f"Total credits {total_credits:.1f} exceeds limit of 100")

    captains = [p for p in players_input if p.get("is_captain")]
    vcs      = [p for p in players_input if p.get("is_vice_captain")]
    if len(captains) != 1:
        raise HTTPException(status_code=400, detail="Exactly one captain required")
    if len(vcs) != 1:
        raise HTTPException(status_code=400, detail="Exactly one vice-captain required")
    if captains[0]["player_id"] == vcs[0]["player_id"]:
        raise HTTPException(status_code=400, detail="Captain and vice-captain must be different players")

    wk_count = sum(1 for p in db_players if p.role.value == "wicket_keeper")
    if wk_count < 1:
        raise HTTPException(status_code=400, detail="Team must have at least 1 wicket-keeper")

    team = Team(
        name=name,
        user_id=user_id,
        contest_id=contest_id,
        total_credits_used=total_credits,
        total_points=0.0,
    )
    db.add(team)
    db.flush()

    for pi in players_input:
        tp = TeamPlayer(
            team_id=team.id,
            player_id=pi["player_id"],
            is_captain=pi.get("is_captain", False),
            is_vice_captain=pi.get("is_vice_captain", False),
            points_earned=0.0,
        )
        db.add(tp)

    db.commit()
    db.refresh(team)
    return team


def get_team_with_players(db: Session, team_id: int, user_id: int) -> dict:
    team = db.query(Team).filter(Team.id == team_id, Team.user_id == user_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    team_players = db.query(TeamPlayer).filter(TeamPlayer.team_id == team_id).all()
    result = []
    for tp in team_players:
        player = db.query(Player).filter(Player.id == tp.player_id).first()
        result.append({
            "player_id":        tp.player_id,
            "player_name":      player.name,
            "team_name":        player.team_name,
            "role":             player.role.value,
            "credit_value":     player.credit_value,
            "is_captain":       tp.is_captain,
            "is_vice_captain":  tp.is_vice_captain,
            "points_earned":    tp.points_earned,
        })

    return {
        "id":                  team.id,
        "name":                team.name,
        "user_id":             team.user_id,
        "contest_id":          team.contest_id,
        "total_credits_used":  team.total_credits_used,
        "total_points":        team.total_points,
        "is_locked":           team.is_locked,
        "players":             result,
        "created_at":          team.created_at,
    }


def list_user_teams(db: Session, user_id: int) -> list:
    teams = db.query(Team).filter(Team.user_id == user_id).all()
    return [get_team_with_players(db, t.id, user_id) for t in teams]
