"""
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
