from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum, JSON
from database import Base
import enum


class MatchStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    COMPLETED = "completed"


class EventType(str, enum.Enum):
    # Cricket
    RUN = "run"
    FOUR = "four"
    SIX = "six"
    WICKET = "wicket"
    MAIDEN_OVER = "maiden_over"
    CATCH = "catch"
    STUMPING = "stumping"
    RUN_OUT = "run_out"
    # Generic
    BONUS = "bonus"
    PENALTY = "penalty"


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    contest_id = Column(Integer, ForeignKey("contests.id", ondelete="SET NULL"), nullable=True, index=True)
    team_a = Column(String(100), nullable=False)
    team_b = Column(String(100), nullable=False)
    status = Column(Enum(MatchStatus), default=MatchStatus.SCHEDULED, nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ScoringEvent(Base):
    __tablename__ = "scoring_events"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    event_type = Column(Enum(EventType), nullable=False)
    points_awarded = Column(Float, nullable=False)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
