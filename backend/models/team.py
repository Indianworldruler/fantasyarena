from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, func, UniqueConstraint
from database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    contest_id = Column(Integer, ForeignKey("contests.id", ondelete="CASCADE"), nullable=False, index=True)
    total_credits_used = Column(Float, default=0.0, nullable=False)
    total_points = Column(Float, default=0.0, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "contest_id", name="uq_user_contest_team"),
    )


class TeamPlayer(Base):
    __tablename__ = "team_players"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    is_captain = Column(Boolean, default=False, nullable=False)
    is_vice_captain = Column(Boolean, default=False, nullable=False)
    points_earned = Column(Float, default=0.0, nullable=False)

    __table_args__ = (
        UniqueConstraint("team_id", "player_id", name="uq_team_player"),
    )
