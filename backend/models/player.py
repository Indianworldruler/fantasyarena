from sqlalchemy import Column, Integer, String, Float, Boolean, Enum, DateTime, func
from database import Base
import enum


class PlayerRole(str, enum.Enum):
    BATSMAN = "batsman"
    BOWLER = "bowler"
    ALL_ROUNDER = "all_rounder"
    WICKET_KEEPER = "wicket_keeper"


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    team_name = Column(String(100), nullable=False)
    role = Column(Enum(PlayerRole), nullable=False)
    credit_value = Column(Float, default=8.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    country = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
