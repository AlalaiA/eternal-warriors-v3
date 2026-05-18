"""
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
