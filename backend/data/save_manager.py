"""
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
