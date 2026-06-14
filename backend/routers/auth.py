from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from services.auth_service import register_user, authenticate_user, create_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=201, response_model=dict)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, req.username, req.email, req.password, req.full_name)
    return {"message": "Account created", "user_id": user.id, "username": user.username}


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user  = authenticate_user(db, req.username, req.password)
    token = create_token(user)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        is_admin=user.is_admin,
    )
