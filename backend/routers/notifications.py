from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from middleware.auth_middleware import get_current_user
from models.user import User
from schemas.scoring import NotificationOut
from services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationOut])
def get_notifications(
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return notification_service.get_user_notifications(db, current_user.id, unread_only)


@router.get("/unread-count", response_model=dict)
def get_unread_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    count = len(notification_service.get_user_notifications(db, current_user.id, unread_only=True))
    return {"unread_count": count}


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return notification_service.mark_read(db, notification_id, current_user.id)


@router.patch("/read-all", response_model=dict)
def mark_all_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notification_service.mark_all_read(db, current_user.id)
    return {"message": "All notifications marked as read"}
