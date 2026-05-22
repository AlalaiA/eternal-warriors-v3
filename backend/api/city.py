"""
backend/api/city.py
Endpoints de ciudad con sistema de producción integrado
"""
from fastapi import APIRouter
from backend.data.save_manager import SaveManager
from backend.systems.production import aplicar_produccion, calcular_tasas, init_last_prod
from backend.systems.queues import procesar_colas
from backend.systems.herreria import calcular_bonus_herreria

router = APIRouter()
sm = SaveManager()

@router.get("/{jugador}/{city_name}")
def get_city(jugador: str, city_name: str):
    player = sm.load_player(jugador.upper())
    cities = player.get("cities", [])
    unit_levels = player.get("unit_levels", {})
    for i, c in enumerate(cities):
        if c.get("NOMBRE") == city_name:
            init_last_prod(c)
            tasas = aplicar_produccion(c, unit_levels)
            procesar_colas(c, unit_levels)          # ← acreditar unidades completadas
            player["cities"][i] = c
            sm.save_player(jugador.upper(), player)
            bonus_herreria = calcular_bonus_herreria(player)
            return {
                "ok":           True,
                "city":         c,
                "tasas":        tasas,
                "unit_levels":  unit_levels,
                "bonus_herreria": bonus_herreria,
            }
    return {"ok": False, "msg": "Ciudad no encontrada"}


@router.get("/{jugador}/{city_name}/tasas")
def get_tasas(jugador: str, city_name: str):
    player = sm.load_player(jugador.upper())
    unit_levels = player.get("unit_levels", {})
    for c in player.get("cities", []):
        if c.get("NOMBRE") == city_name:
            tasas = calcular_tasas(c, unit_levels)
            return {"ok": True, "tasas": tasas}
    return {"ok": False, "msg": "Ciudad no encontrada"}


@router.post("/{jugador}/{city_name}/tick")
def tick_city(jugador: str, city_name: str):
    player = sm.load_player(jugador.upper())
    cities = player.get("cities", [])
    unit_levels = player.get("unit_levels", {})
    for i, c in enumerate(cities):
        if c.get("NOMBRE") == city_name:
            init_last_prod(c)
            tasas = aplicar_produccion(c, unit_levels)
            procesar_colas(c, unit_levels)          # ← acreditar unidades completadas
            player["cities"][i] = c
            sm.save_player(jugador.upper(), player)
            bonus_herreria = calcular_bonus_herreria(player)
            return {
                "ok":           True,
                "city":         c,
                "tasas":        tasas,
                "unit_levels":  unit_levels,
                "bonus_herreria": bonus_herreria,
            }
    return {"ok": False, "msg": "Ciudad no encontrada"}


@router.get("/{jugador}")
def get_all_cities(jugador: str):
    player = sm.load_player(jugador.upper())
    return {"ok": True, "cities": [c.get("NOMBRE") for c in player.get("cities", [])]}
