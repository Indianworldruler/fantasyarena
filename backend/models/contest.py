from sqlalchemy import Column, Integer, String, Float, Boolean, Enum, DateTime, func, Text
from database import Base
import enum


class ContestStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SportType(str, enum.Enum):
    CRICKET = "cricket"
    FOOTBALL = "football"
    BASKETBALL = "basketball"


class Contest(Base):
    __tablename__ = "contests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    sport = Column(Enum(SportType), default=SportType.CRICKET, nullable=False)
    match_name = Column(String(200), nullable=False)
    entry_fee = Column(Float, nullable=False)
    prize_pool = Column(Float, nullable=False)
    max_teams = Column(Integer, nullable=False)
    current_teams = Column(Integer, default=0, nullable=False)
    status = Column(Enum(ContestStatus), default=ContestStatus.UPCOMING, nullable=False, index=True)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
