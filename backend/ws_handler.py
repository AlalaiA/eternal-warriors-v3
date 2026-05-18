"""
WebSocket handler — comunicación tiempo real frontend ↔ backend
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.engine.game_engine import GameEngine
import json

router = APIRouter()
engine = GameEngine()

class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}  # jugador → ws

    async def connect(self, jugador: str, ws: WebSocket):
        await ws.accept()
        self.connections[jugador] = ws

    def disconnect(self, jugador: str):
        self.connections.pop(jugador, None)

    async def send(self, jugador: str, data: dict):
        ws = self.connections.get(jugador)
        if ws:
            await ws.send_json(data)

    async def broadcast(self, data: dict):
        for ws in self.connections.values():
            await ws.send_json(data)

manager = ConnectionManager()

@router.websocket("/ws/{jugador}")
async def websocket_endpoint(ws: WebSocket, jugador: str):
    await manager.connect(jugador, ws)
    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            action = msg.get("action", "")

            if action == "PING":
                await manager.send(jugador, {"event": "PONG"})

            elif action == "GET_CITY":
                city_name = msg.get("name")
                data = engine.get_city(jugador, city_name)
                await manager.send(jugador, {"event": "CITY_DATA", "data": data})

            elif action == "SEND_ORDER":
                result = engine.send_order(jugador, msg)
                await manager.send(jugador, {"event": "ORDER_RESULT", "data": result})

            elif action == "MOVE_MAP":
                tiles = engine.move_map(jugador, msg.get("direction"), msg.get("from"))
                await manager.send(jugador, {"event": "MAP_UPDATE", "tiles": tiles})

    except WebSocketDisconnect:
        manager.disconnect(jugador)
