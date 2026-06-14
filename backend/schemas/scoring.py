from pydantic import BaseModel
from datetime import datetime
from models.scoring import EventType


class MatchCreate(BaseModel):
    name: str
    contest_id: int | None = None
    team_a: str
    team_b: str


class MatchOut(BaseModel):
    id: int
    name: str
    contest_id: int | None
    team_a: str
    team_b: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class MatchEventRequest(BaseModel):
    match_id: int
    player_id: int
    event_type: EventType
    meta: dict | None = None


class MatchEventResponse(BaseModel):
    event_id: int
    player_id: int
    event_type: str
    points_awarded: float
    message: str


class LeaderboardEntryOut(BaseModel):
    rank: int | None
    user_id: int
    username: str
    team_id: int
    team_name: str
    total_points: float
    prize_won: float

    model_config = {"from_attributes": True}


class LeaderboardOut(BaseModel):
    contest_id: int
    contest_name: str
    entries: list[LeaderboardEntryOut]


class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
