from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

router = APIRouter(tags=["WebSocket"])
logger = logging.getLogger("websocket")


class ConnectionManager:
    """
    Manages active WebSocket connections per room (match_id or contest_id).
    In production: replaced by Redis Pub/Sub to support horizontal scaling
    across multiple server instances (stateless WebSocket workers).
    """

    def __init__(self):
        self.rooms: dict[str, list[WebSocket]] = {}

    async def connect(self, room: str, ws: WebSocket):
        await ws.accept()
        self.rooms.setdefault(room, []).append(ws)
        logger.info(f"WS connected to room '{room}'. Total: {len(self.rooms[room])}")

    def disconnect(self, room: str, ws: WebSocket):
        if room in self.rooms:
            self.rooms[room] = [w for w in self.rooms[room] if w != ws]

    async def broadcast(self, room: str, message: dict):
        dead = []
        for ws in self.rooms.get(room, []):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(room, ws)

    def active_connections(self) -> dict:
        return {room: len(conns) for room, conns in self.rooms.items() if conns}


manager = ConnectionManager()


@router.websocket("/ws/match/{match_id}")
async def match_websocket(websocket: WebSocket, match_id: int):
    room = f"match_{match_id}"
    await manager.connect(room, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(room, websocket)


@router.websocket("/ws/leaderboard/{contest_id}")
async def leaderboard_websocket(websocket: WebSocket, contest_id: int):
    room = f"leaderboard_{contest_id}"
    await manager.connect(room, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(room, websocket)
