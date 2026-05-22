"""
Gestión de lectura/escritura de JSONs de la nueva estructura v3
"""
import json
import math
from pathlib import Path

DB = Path(__file__).parent.parent / "db"

PLAYER_PATHS = {
    "JIARITO":     DB / "players" / "jiarito.json",
    "GINAO":       DB / "players" / "ginao.json",
    "JOTICALINDO": DB / "players" / "joticalindo.json",
    "ALALAIA":     DB / "players" / "alalaia.json",
    "ADMIN":       DB / "players" / "admin.json",
}

class _SafeEncoder(json.JSONEncoder):
    """Convierte valores problemáticos a JSON válido."""
    def default(self, obj):
        return super().default(obj)
    def iterencode(self, o, _one_shot=False):
        return super().iterencode(self._sanitize(o), _one_shot)
    def _sanitize(self, obj):
        if isinstance(obj, float):
            if math.isnan(obj): return 0.0
            if math.isinf(obj): return 1e300  # infinito como número grande válido
            return obj
        if isinstance(obj, dict):
            return {k: self._sanitize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._sanitize(v) for v in obj]
        return obj

def load_json(path: Path) -> dict | list:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    # Parsear solo el primer objeto JSON válido (ignora basura al final)
    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(text.strip())
    return obj

def save_json(path: Path, data):
    text = json.dumps(data, cls=_SafeEncoder, ensure_ascii=True, indent=2)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

class SaveManager:
    def load_player(self, jugador: str) -> dict:
        jugador = jugador.upper()
        path = PLAYER_PATHS.get(jugador)
        if not path:
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
