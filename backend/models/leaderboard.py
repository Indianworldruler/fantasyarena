from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, func, UniqueConstraint
from database import Base


class LeaderboardEntry(Base):
    __tablename__ = "leaderboard_entries"

    id = Column(Integer, primary_key=True, index=True)
    contest_id = Column(Integer, ForeignKey("contests.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    total_points = Column(Float, default=0.0, nullable=False)
    rank = Column(Integer, nullable=True)
    prize_won = Column(Float, default=0.0, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("contest_id", "user_id", name="uq_leaderboard_contest_user"),
    )
