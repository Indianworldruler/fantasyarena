import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.wallet import Wallet
from models.transaction import Transaction, TransactionType, TransactionStatus


def get_wallet(db: Session, user_id: int) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


def deposit(db: Session, user_id: int, amount: float) -> Wallet:
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    wallet = get_wallet(db, user_id)
    wallet.balance += amount
    tx = Transaction(
        user_id=user_id,
        amount=amount,
        type=TransactionType.DEPOSIT,
        status=TransactionStatus.SUCCESS,
        reference_id=str(uuid.uuid4())[:8].upper(),
        description=f"Wallet deposit of ₹{amount}",
    )
    db.add(tx)
    db.commit()
    db.refresh(wallet)
    return wallet


def withdraw(db: Session, user_id: int, amount: float) -> Wallet:
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    wallet = get_wallet(db, user_id)
    if wallet.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")
    wallet.balance -= amount
    tx = Transaction(
        user_id=user_id,
        amount=amount,
        type=TransactionType.WITHDRAWAL,
        status=TransactionStatus.SUCCESS,
        reference_id=str(uuid.uuid4())[:8].upper(),
        description=f"Wallet withdrawal of ₹{amount}",
    )
    db.add(tx)
    db.commit()
    db.refresh(wallet)
    return wallet


def deduct_entry_fee(db: Session, user_id: int, amount: float, contest_id: int) -> Wallet:
    """Called internally when user joins a contest. Fault-tolerant: rolls back on failure."""
    wallet = get_wallet(db, user_id)
    if wallet.balance < amount:
        raise HTTPException(status_code=400, detail=f"Insufficient balance. Need ₹{amount}, have ₹{wallet.balance:.2f}")
    try:
        wallet.balance -= amount
        tx = Transaction(
            user_id=user_id,
            amount=amount,
            type=TransactionType.CONTEST_ENTRY,
            status=TransactionStatus.SUCCESS,
            reference_id=f"CONTEST-{contest_id}",
            description=f"Entry fee for contest #{contest_id}",
        )
        db.add(tx)
        db.flush()
        return wallet
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Payment processing failed: {str(e)}")


def credit_winnings(db: Session, user_id: int, amount: float, contest_id: int) -> Wallet:
    wallet = get_wallet(db, user_id)
    wallet.balance += amount
    tx = Transaction(
        user_id=user_id,
        amount=amount,
        type=TransactionType.CONTEST_WINNINGS,
        status=TransactionStatus.SUCCESS,
        reference_id=f"WIN-CONTEST-{contest_id}",
        description=f"Winnings from contest #{contest_id}",
    )
    db.add(tx)
    db.flush()
    return wallet


def get_transactions(db: Session, user_id: int, limit: int = 50) -> list:
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .all()
    )
