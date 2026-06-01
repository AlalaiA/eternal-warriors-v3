"""
Gestión de lectura/escritura de JSONs de la nueva estructura v3
"""
import json
import math
import os
import time
import threading
from pathlib import Path

DB = Path(__file__).parent.parent / "db"

PLAYER_PATHS = {
    "JIARITO":     DB / "players" / "jiarito.json",
    "GINAO":       DB / "players" / "ginao.json",
    "JOTICALINDO": DB / "players" / "joticalindo.json",
    "ALALAIA":     DB / "players" / "alalaia.json",
    "ADMIN":       DB / "players" / "admin.json",
}

# Lock por archivo — evita que dos threads escriban el mismo archivo simultáneamente
_file_locks: dict = {}
_meta_lock = threading.Lock()

def _get_lock(path: Path) -> threading.Lock:
    key = str(path)
    with _meta_lock:
        if key not in _file_locks:
            _file_locks[key] = threading.Lock()
        return _file_locks[key]


class _SafeEncoder(json.JSONEncoder):
    def default(self, obj):
        return super().default(obj)
    def iterencode(self, o, _one_shot=False):
        return super().iterencode(self._sanitize(o), _one_shot)
    def _sanitize(self, obj):
        if isinstance(obj, float):
            if math.isnan(obj): return 0.0
            if math.isinf(obj): return 1e300
            return obj
        if isinstance(obj, dict):
            return {k: self._sanitize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._sanitize(v) for v in obj]
        return obj


def load_json(path: Path) -> dict | list:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(text.strip())
    return obj


def save_json(path: Path, data):
    """Escritura directa bajo lock por archivo."""
    text = json.dumps(data, cls=_SafeEncoder, ensure_ascii=True, indent=2)
    lock = _get_lock(path)
    with lock:
        # Reintento en Windows por si el archivo está temporalmente bloqueado
        for intento in range(3):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                break
            except PermissionError:
                if intento == 2:
                    raise
                time.sleep(0.05)


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

    def update_player(self, jugador: str, fn) -> dict:
        """
        Lee, aplica fn, guarda — todo bajo lock por archivo.
        Garantiza que ningún otro thread escriba el mismo JSON entre el read y el write.
        """
        jugador = jugador.upper()
        path = PLAYER_PATHS.get(jugador)
        if not path:
            path = DB / "players" / "humanos" / f"{jugador.lower()}.json"
        lock = _get_lock(path)
        with lock:
            data = load_json(path) if path.exists() else {}
            fn(data)
            text = json.dumps(data, cls=_SafeEncoder, ensure_ascii=True, indent=2)
            for intento in range(3):
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(text)
                    break
                except PermissionError:
                    if intento == 2:
                        raise
                    time.sleep(0.05)
        return data

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

    def load_alliances(self) -> dict:
        path = DB / "global" / "alliances.json"
        if not path.exists():
            return {}
        data = load_json(path)
        return data.get("alliances", {})

    def save_alliances(self, alianzas: dict):
        save_json(DB / "global" / "alliances.json", {"alliances": alianzas})
