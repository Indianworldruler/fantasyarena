from pydantic import BaseModel
from datetime import datetime
from models.contest import ContestStatus, SportType


class ContestCreate(BaseModel):
    name: str
    description: str | None = None
    sport: SportType = SportType.CRICKET
    match_name: str
    entry_fee: float
    prize_pool: float
    max_teams: int
    starts_at: datetime


class ContestOut(BaseModel):
    id: int
    name: str
    description: str | None
    sport: str
    match_name: str
    entry_fee: float
    prize_pool: float
    max_teams: int
    current_teams: int
    status: str
    starts_at: datetime
    ends_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ContestJoinRequest(BaseModel):
    team_id: int


class ContestJoinResponse(BaseModel):
    message: str
    contest_id: int
    team_id: int
    entry_fee_deducted: float
    wallet_balance_remaining: float
