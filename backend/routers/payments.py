from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from middleware.auth_middleware import get_current_user
from models.user import User
from schemas.user import WalletOut, DepositRequest, WithdrawRequest, TransactionOut
from services import payment_service

router = APIRouter(prefix="/wallet", tags=["Wallet & Payments"])


@router.get("/balance", response_model=WalletOut)
def get_balance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return payment_service.get_wallet(db, current_user.id)


@router.post("/deposit", response_model=WalletOut)
def deposit(req: DepositRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return payment_service.deposit(db, current_user.id, req.amount)


@router.post("/withdraw", response_model=WalletOut)
def withdraw(req: WithdrawRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return payment_service.withdraw(db, current_user.id, req.amount)


@router.get("/transactions", response_model=list[TransactionOut])
def get_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return payment_service.get_transactions(db, current_user.id)
