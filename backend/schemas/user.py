from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None


class WalletOut(BaseModel):
    user_id: int
    balance: float
    updated_at: datetime

    model_config = {"from_attributes": True}


class DepositRequest(BaseModel):
    amount: float

    def model_post_init(self, _):
        if self.amount <= 0:
            raise ValueError("Amount must be positive")


class WithdrawRequest(BaseModel):
    amount: float

    def model_post_init(self, _):
        if self.amount <= 0:
            raise ValueError("Amount must be positive")


class TransactionOut(BaseModel):
    id: int
    user_id: int
    amount: float
    type: str
    status: str
    reference_id: str | None
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
