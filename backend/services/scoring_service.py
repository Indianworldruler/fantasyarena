"""
Scoring Service — Strategy Pattern

Each sport has its own scoring strategy.
The ScoringEngine selects the right strategy at runtime based on contest sport.

Cricket scoring rules (Dream11-style):
  Run:          0.5 pts
  Four bonus:   1 pt
  Six bonus:    2 pts
  Half-century: 8 pts (at 50 runs — handled via meta)
  Century:      16 pts
  Wicket:       25 pts
  Maiden over:  12 pts
  Catch:        8 pts
  Stumping:     12 pts
  Run out:      6 pts
  Captain multiplier:       2x
  Vice-captain multiplier:  1.5x
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.scoring import ScoringEvent, EventType, Match, MatchStatus
from models.team import Team, TeamPlayer
from models.contest import Contest


# ── Strategy interfaces ──────────────────────────────────────────────────────

class ScoringStrategy:
    def points_for(self, event_type: EventType, meta: dict | None) -> float:
        raise NotImplementedError


class CricketScoringStrategy(ScoringStrategy):
    POINTS = {
        EventType.RUN:         0.5,
        EventType.FOUR:        1.0,
        EventType.SIX:         2.0,
        EventType.WICKET:      25.0,
        EventType.MAIDEN_OVER: 12.0,
        EventType.CATCH:       8.0,
        EventType.STUMPING:    12.0,
        EventType.RUN_OUT:     6.0,
        EventType.BONUS:       5.0,
        EventType.PENALTY:     -5.0,
    }

    def points_for(self, event_type: EventType, meta: dict | None) -> float:
        base = self.POINTS.get(event_type, 0.0)
        if meta:
            if meta.get("milestone") == "fifty":
                base += 8.0
            elif meta.get("milestone") == "century":
                base += 16.0
        return base


class FootballScoringStrategy(ScoringStrategy):
    POINTS = {
        EventType.BONUS:   10.0,
        EventType.PENALTY: -2.0,
    }
    def points_for(self, event_type: EventType, meta: dict | None) -> float:
        return self.POINTS.get(event_type, 0.0)


class ScoringStrategyFactory:
    """Selects the correct strategy based on sport type."""
    _registry = {
        "cricket":    CricketScoringStrategy,
        "football":   FootballScoringStrategy,
        "basketball": FootballScoringStrategy,
    }

    @classmethod
    def get(cls, sport: str) -> ScoringStrategy:
        return cls._registry.get(sport, CricketScoringStrategy)()


# ── Scoring Engine ───────────────────────────────────────────────────────────

def process_event(db: Session, match_id: int, player_id: int, event_type: EventType, meta: dict | None) -> ScoringEvent:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if match.status != MatchStatus.LIVE:
        raise HTTPException(status_code=400, detail="Match is not live")

    contest = db.query(Contest).filter(Contest.id == match.contest_id).first()
    sport = contest.sport.value if contest else "cricket"
    strategy = ScoringStrategyFactory.get(sport)
    points = strategy.points_for(event_type, meta)

    event = ScoringEvent(
        match_id=match_id,
        player_id=player_id,
        event_type=event_type,
        points_awarded=points,
        meta=meta,
    )
    db.add(event)
    db.flush()

    _apply_points_to_teams(db, match.contest_id, player_id, points)
    db.commit()
    db.refresh(event)
    return event


def _apply_points_to_teams(db: Session, contest_id: int | None, player_id: int, base_points: float):
    """
    Find every TeamPlayer in this contest that has this player.
    Apply captain/vc multiplier and add to team total.
    """
    if not contest_id:
        return

    team_players = (
        db.query(TeamPlayer)
        .join(Team, Team.id == TeamPlayer.team_id)
        .filter(Team.contest_id == contest_id, TeamPlayer.player_id == player_id)
        .all()
    )

    for tp in team_players:
        multiplier = 2.0 if tp.is_captain else (1.5 if tp.is_vice_captain else 1.0)
        earned = base_points * multiplier
        tp.points_earned += earned

        team = db.query(Team).filter(Team.id == tp.team_id).first()
        if team:
            team.total_points += earned


def create_match(db: Session, name: str, contest_id: int | None, team_a: str, team_b: str) -> Match:
    match = Match(name=name, contest_id=contest_id, team_a=team_a, team_b=team_b)
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


def start_match(db: Session, match_id: int) -> Match:
    from datetime import datetime, timezone
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.status = MatchStatus.LIVE
    match.started_at = datetime.now(timezone.utc)

    if match.contest_id:
        contest = db.query(Contest).filter(Contest.id == match.contest_id).first()
        if contest:
            from models.contest import ContestStatus
            contest.status = ContestStatus.LIVE

    db.commit()
    db.refresh(match)
    return match


def get_matches(db: Session) -> list[Match]:
    return db.query(Match).order_by(Match.created_at.desc()).all()
