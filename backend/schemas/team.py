from pydantic import BaseModel, field_validator
from datetime import datetime


class TeamPlayerInput(BaseModel):
    player_id: int
    is_captain: bool = False
    is_vice_captain: bool = False


class TeamCreate(BaseModel):
    name: str
    contest_id: int
    players: list[TeamPlayerInput]

    @field_validator("players")
    @classmethod
    def validate_players(cls, players):
        if len(players) != 11:
            raise ValueError("Team must have exactly 11 players")
        captains = [p for p in players if p.is_captain]
        vcs = [p for p in players if p.is_vice_captain]
        if len(captains) != 1:
            raise ValueError("Team must have exactly 1 captain")
        if len(vcs) != 1:
            raise ValueError("Team must have exactly 1 vice-captain")
        return players


class TeamPlayerOut(BaseModel):
    player_id: int
    player_name: str
    team_name: str
    role: str
    credit_value: float
    is_captain: bool
    is_vice_captain: bool
    points_earned: float

    model_config = {"from_attributes": True}


class TeamOut(BaseModel):
    id: int
    name: str
    user_id: int
    contest_id: int
    total_credits_used: float
    total_points: float
    is_locked: bool
    players: list[TeamPlayerOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class PlayerOut(BaseModel):
    id: int
    name: str
    team_name: str
    role: str
    credit_value: float
    is_active: bool
    country: str | None

    model_config = {"from_attributes": True}
