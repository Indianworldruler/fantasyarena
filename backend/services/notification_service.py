from sqlalchemy.orm import Session
from models.notification import Notification, NotificationType
from fastapi import HTTPException


def create_notification(db: Session, user_id: int, ntype: NotificationType, title: str, message: str) -> Notification:
    notif = Notification(user_id=user_id, type=ntype, title=title, message=message)
    db.add(notif)
    db.flush()
    return notif


def get_user_notifications(db: Session, user_id: int, unread_only: bool = False) -> list[Notification]:
    q = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        q = q.filter(Notification.is_read == False)
    return q.order_by(Notification.created_at.desc()).limit(50).all()


def mark_read(db: Session, notification_id: int, user_id: int) -> Notification:
    n = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    n.is_read = True
    db.commit()
    db.refresh(n)
    return n


def mark_all_read(db: Session, user_id: int):
    db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).update({"is_read": True})
    db.commit()
