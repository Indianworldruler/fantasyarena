from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func, Enum, Text
from database import Base
import enum


class NotificationType(str, enum.Enum):
    CONTEST_JOINED = "contest_joined"
    SCORE_UPDATE = "score_update"
    LEADERBOARD_UPDATE = "leaderboard_update"
    PRIZE_AWARDED = "prize_awarded"
    MATCH_STARTED = "match_started"
    MATCH_COMPLETED = "match_completed"
    WALLET = "wallet"
    SYSTEM = "system"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
