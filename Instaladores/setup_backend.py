"""
Crea la estructura de carpetas y archivos base del backend v3.
Ejecutar desde E:\0000ew V2Claude\
"""
import os
from pathlib import Path

BASE = Path(r"E:\0000ew V2Claude\backend")

files = {}

# ── main.py ───────────────────────────────────────────────────────────────
files["main.py"] = '''"""
ETERNAL WARRIORS v3.0 — Servidor principal
Ejecutar: python -m uvicorn backend.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.ws_handler import router as ws_router
from backend.api.auth import router as auth_router
from backend.api.city import router as city_router
from backend.api.map import router as map_router
import uvicorn

app = FastAPI(title="Eternal Warriors v3.0")

# WebSocket
app.include_router(ws_router)

# API REST
app.include_router(auth_router, prefix="/api/auth")
app.include_router(city_router, prefix="/api/city")
app.include_router(map_router,  prefix="/api/map")

# Frontend estático
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def index():
    return FileResponse("frontend/index.html")

@app.get("/game")
def game():
    return FileResponse("frontend/game.html")

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
'''

# ── __init__.py ───────────────────────────────────────────────────────────
files["__init__.py"] = '# Eternal Warriors v3.0 backend\n'

# ── ws_handler.py ─────────────────────────────────────────────────────────
files["ws_handler.py"] = '''"""
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
'''

# ── engine/game_engine.py ─────────────────────────────────────────────────
files["engine/__init__.py"] = ""
files["engine/game_engine.py"] = '''"""
Motor principal del juego — orquesta todos los sistemas
"""
from backend.data.save_manager import SaveManager

class GameEngine:
    def __init__(self):
        self.sm = SaveManager()

    def get_city(self, jugador: str, city_name: str) -> dict:
        player_data = self.sm.load_player(jugador)
        cities = player_data.get("cities", [])
        for c in cities:
            if c.get("NOMBRE") == city_name:
                return c
        return {}

    def send_order(self, jugador: str, msg: dict) -> dict:
        # TODO: delegar a systems/
        return {"ok": False, "msg": "No implementado aún"}

    def move_map(self, jugador: str, direction: str, from_pos: dict) -> list:
        # TODO: lógica de niebla de guerra
        return []
'''

# ── data/save_manager.py ──────────────────────────────────────────────────
files["data/__init__.py"] = ""
files["data/save_manager.py"] = '''"""
Gestión de lectura/escritura de JSONs de la nueva estructura v3
"""
import json
from pathlib import Path

DB = Path(__file__).parent.parent / "db"

PLAYER_PATHS = {
    "JIARITO":     DB / "players" / "jiarito.json",
    "GINAO":       DB / "players" / "ginao.json",
    "JOTICALINDO": DB / "players" / "joticalindo.json",
    "ALALAIA":     DB / "players" / "alalaia.json",
    "ADMIN":       DB / "players" / "admin.json",
}

def load_json(path: Path) -> dict | list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class SaveManager:
    def load_player(self, jugador: str) -> dict:
        jugador = jugador.upper()
        path = PLAYER_PATHS.get(jugador)
        if not path:
            # Buscar en humanos/
            path = DB / "players" / "humanos" / f"{jugador.lower()}.json"
        if path and path.exists():
            return load_json(path)
        return {}

    def save_player(self, jugador: str, data: dict):
        jugador = jugador.upper()
        path = PLAYER_PATHS.get(jugador)
        if not path:
            path = DB / "players" / "humanos" / f"{jugador.lower()}.json"
        save_json(path, data)

    def load_world(self, entity: str) -> dict | list:
        path = DB / "world" / f"{entity}.json"
        return load_json(path) if path.exists() else {}

    def load_core(self) -> dict:
        return load_json(DB / "global" / "core.json")

    def load_orders(self) -> list:
        data = load_json(DB / "global" / "orders.json")
        return data.get("orders", [])

    def save_orders(self, orders: list):
        save_json(DB / "global" / "orders.json", {"orders": orders})

    def load_accounts(self) -> dict:
        data = load_json(DB / "global" / "accounts.json")
        return data.get("accounts", {})
'''

# ── api/auth.py ───────────────────────────────────────────────────────────
files["api/__init__.py"] = ""
files["api/auth.py"] = '''"""
Autenticación de jugadores
"""
from fastapi import APIRouter
from pydantic import BaseModel
from backend.data.save_manager import SaveManager
import hashlib

router = APIRouter()
sm = SaveManager()

class LoginRequest(BaseModel):
    usuario: str
    password: str

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

@router.post("/login")
def login(req: LoginRequest):
    accounts = sm.load_accounts()
    usuario = req.usuario.upper()
    hashed = hash_pw(req.password)
    stored = accounts.get(usuario, accounts.get(req.usuario, ""))
    if stored and (stored == hashed or stored == req.password):
        player = sm.load_player(usuario)
        cities = player.get("cities", [])
        capital = cities[0].get("NOMBRE", "") if cities else ""
        return {"ok": True, "jugador": usuario, "capital": capital}
    return {"ok": False, "msg": "Usuario o contraseña incorrectos"}
'''

# ── api/city.py ───────────────────────────────────────────────────────────
files["api/city.py"] = '''"""
Endpoints de ciudad
"""
from fastapi import APIRouter
from backend.data.save_manager import SaveManager

router = APIRouter()
sm = SaveManager()

@router.get("/{jugador}/{city_name}")
def get_city(jugador: str, city_name: str):
    player = sm.load_player(jugador.upper())
    for c in player.get("cities", []):
        if c.get("NOMBRE") == city_name:
            return {"ok": True, "city": c}
    return {"ok": False, "msg": "Ciudad no encontrada"}

@router.get("/{jugador}")
def get_all_cities(jugador: str):
    player = sm.load_player(jugador.upper())
    return {"ok": True, "cities": [c.get("NOMBRE") for c in player.get("cities", [])]}
'''

# ── api/map.py ────────────────────────────────────────────────────────────
files["api/map.py"] = '''"""
Endpoints de mapa
"""
from fastapi import APIRouter
from backend.data.save_manager import SaveManager

router = APIRouter()
sm = SaveManager()

@router.get("/entities")
def get_entities():
    """Retorna todas las entidades del mundo para el mapa."""
    inactivos = sm.load_world("inactivos").get("cities", [])
    dioses    = sm.load_world("dioses").get("entities", [])
    cuevas    = sm.load_world("cuevas").get("entities", [])
    portales  = sm.load_world("portales").get("entities", [])
    karlaka   = sm.load_world("karlaka").get("entity", {})
    return {
        "ok": True,
        "inactivos": [{"id": c.get("ID"), "x": c.get("X"), "y": c.get("Y"), "nombre": c.get("NOMBRE")} for c in inactivos],
        "dioses":    [{"id": d.get("ID"), "x": d.get("X"), "y": d.get("Y"), "nombre": d.get("NOMBRE")} for d in dioses],
        "cuevas":    [{"id": c.get("ID"), "x": c.get("X"), "y": c.get("Y"), "nombre": c.get("NOMBRE")} for c in cuevas],
        "portales":  [{"id": p.get("ID"), "x": p.get("X"), "y": p.get("Y"), "nombre": p.get("NOMBRE")} for p in portales],
        "karlaka":   {"x": karlaka.get("X"), "y": karlaka.get("Y")},
    }
'''

# ── systems/ (placeholders) ───────────────────────────────────────────────
for sys in ["combat", "espionage", "production", "buildings", "orders", "alliances", "experience", "fog_of_war"]:
    files[f"systems/{sys}.py"] = f'"""\nSistema: {sys}\nPendiente de implementar.\n"""\n'
files["systems/__init__.py"] = ""

# ── run.bat ───────────────────────────────────────────────────────────────
run_bat = '@echo off\ncd /d E:\\0000ew V2Claude\npython -m uvicorn backend.main:app --reload --port 8000\npause\n'

# Crear archivos
for rel_path, content in files.items():
    full_path = BASE / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  OK {rel_path}")

# run.bat en raíz
run_path = Path(r"E:\0000ew V2Claude\run.bat")
with open(run_path, "w", encoding="utf-8") as f:
    f.write(run_bat)
print("  OK run.bat")

print("\n✅ Backend creado. Ejecuta run.bat para arrancar el servidor.")
