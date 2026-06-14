"""
Event Handlers — Observer Pattern

Pipeline:
  match.event
    → handle_match_event
        → leaderboard.updated  (sync scores + re-rank)
        → notification.send    (score update notify to all affected users)

  leaderboard.updated
    → handle_leaderboard_updated
        → WebSocket broadcast to leaderboard room

  notification.send
    → handle_notification_send
        → persist notification + WebSocket push to user

All handlers are async and registered on app startup.
"""

import logging
from database import SessionLocal
from event_bus import bus
from routers.websocket import manager

logger = logging.getLogger("event_handlers")


async def handle_match_event(payload: dict):
    """
    Triggered by: match.event
    Syncs scores to leaderboard then fans out further events.
    """
    contest_id = payload.get("contest_id")
    if not contest_id:
        return

    db = SessionLocal()
    try:
        from services.leaderboard_service import sync_scores_to_leaderboard
        sync_scores_to_leaderboard(db, contest_id)

        from models.leaderboard import LeaderboardEntry
        from models.user import User
        from models.team import Team

        entries = (
            db.query(LeaderboardEntry)
            .filter(LeaderboardEntry.contest_id == contest_id)
            .order_by(LeaderboardEntry.total_points.desc())
            .all()
        )

        leaderboard_snapshot = []
        for entry in entries:
            user = db.query(User).filter(User.id == entry.user_id).first()
            team = db.query(Team).filter(Team.id == entry.team_id).first()
            leaderboard_snapshot.append({
                "rank":         entry.rank,
                "username":     user.username if user else "—",
                "team_name":    team.name if team else "—",
                "total_points": entry.total_points,
            })

        await bus.publish("leaderboard.updated", {
            "contest_id":  contest_id,
            "leaderboard": leaderboard_snapshot,
            "trigger":     payload,
        })

        # Notify all participants of score change
        player_id = payload.get("player_id")
        event_type = payload.get("event_type", "event")
        points = payload.get("points", 0)

        for entry in entries:
            from models.team import TeamPlayer
            has_player = db.query(TeamPlayer).filter(
                TeamPlayer.team_id == entry.team_id,
                TeamPlayer.player_id == player_id,
            ).first()
            if has_player:
                await bus.publish("notification.send", {
                    "user_id":  entry.user_id,
                    "title":    "Score Update",
                    "message":  f"Player event: {event_type} (+{points:.1f} pts)",
                    "type":     "score_update",
                })
    except Exception as e:
        logger.error(f"handle_match_event failed: {e}")
    finally:
        db.close()


async def handle_leaderboard_updated(payload: dict):
    """
    Triggered by: leaderboard.updated
    Broadcasts current leaderboard to all WebSocket clients watching that contest.
    """
    contest_id = payload.get("contest_id")
    if not contest_id:
        return

    room = f"leaderboard_{contest_id}"
    await manager.broadcast(room, {
        "type":        "leaderboard_update",
        "contest_id":  contest_id,
        "leaderboard": payload.get("leaderboard", []),
        "trigger":     payload.get("trigger"),
    })

    match_id = payload.get("trigger", {}).get("match_id")
    if match_id:
        match_room = f"match_{match_id}"
        await manager.broadcast(match_room, {
            "type":       "match_event",
            "event_type": payload.get("trigger", {}).get("event_type"),
            "player_id":  payload.get("trigger", {}).get("player_id"),
            "points":     payload.get("trigger", {}).get("points"),
        })

    logger.info(f"Leaderboard broadcast sent to room '{room}' ({len(payload.get('leaderboard',[]))} entries)")


async def handle_notification_send(payload: dict):
    """
    Triggered by: notification.send
    Persists notification and pushes to user's WebSocket if connected.
    """
    db = SessionLocal()
    try:
        from models.notification import NotificationType
        from services.notification_service import create_notification

        ntype_map = {
            "score_update":       NotificationType.SCORE_UPDATE,
            "leaderboard_update": NotificationType.LEADERBOARD_UPDATE,
            "prize_awarded":      NotificationType.PRIZE_AWARDED,
            "wallet":             NotificationType.WALLET,
        }
        ntype = ntype_map.get(payload.get("type", ""), NotificationType.SYSTEM)
        notif = create_notification(
            db,
            payload["user_id"],
            ntype,
            payload.get("title", "Notification"),
            payload.get("message", ""),
        )
        db.commit()

        user_room = f"user_{payload['user_id']}"
        await manager.broadcast(user_room, {
            "type":    "notification",
            "id":      notif.id,
            "title":   notif.title,
            "message": notif.message,
        })
    except Exception as e:
        logger.error(f"handle_notification_send failed: {e}")
        db.rollback()
    finally:
        db.close()


def register_handlers():
    bus.subscribe("match.event",         handle_match_event)
    bus.subscribe("leaderboard.updated", handle_leaderboard_updated)
    bus.subscribe("notification.send",   handle_notification_send)
    logger.info("All event handlers registered")
