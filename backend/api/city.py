"""
backend/api/city.py
Endpoints de ciudad con sistema de producción integrado.
Usa update_player atómico para evitar race conditions con el ticker de órdenes.
"""
from fastapi import APIRouter
from backend.data.save_manager import SaveManager
from backend.systems.production import aplicar_produccion, calcular_tasas, init_last_prod
from backend.systems.queues import procesar_colas
from backend.systems.buildings import procesar_obras
from backend.systems.herreria import calcular_bonus_herreria

router = APIRouter()
sm     = SaveManager()


def _procesar_ciudad(jugador: str, city_name: str):
    """
    Lee → modifica → guarda el jugador de forma atómica.
    Retorna (tasas, city_data, bonus_herreria) o None si no encuentra la ciudad.
    """
    resultado = {}

    def _fn(player):
        unit_levels = player.get("unit_levels", {})
        for i, c in enumerate(player.get("cities", [])):
            if c.get("NOMBRE") == city_name:
                init_last_prod(c)
                tasas = aplicar_produccion(c, unit_levels)
                procesar_colas(c, unit_levels)
                procesar_obras(c)
                player["cities"][i] = c
                resultado["tasas"]       = tasas
                resultado["city"]        = c
                resultado["unit_levels"] = unit_levels
                break

    player = sm.update_player(jugador.upper(), _fn)

    if not resultado:
        return None

    resultado["bonus_herreria"]    = calcular_bonus_herreria(player)
    resultado["experiencia"]        = float(player.get("experiencia", 0) or 0)
    resultado["batallas_ganadas"]   = int(player.get("batallas_ganadas", 0) or 0)
    resultado["batallas_perdidas"]  = int(player.get("batallas_perdidas", 0) or 0)
    _da = player.get("dioses_abatidos", [])
    resultado["dioses_abatidos"] = len(_da) if isinstance(_da, list) else int(_da or 0)
    resultado["cuevas_derrotadas"]  = int(player.get("cuevas_derrotadas", 0) or 0)
    resultado["misiones_espionaje"] = int(player.get("misiones_espionaje", 0) or 0)
    return resultado


@router.get("/{jugador}/{city_name}")
def get_city(jugador: str, city_name: str):
    r = _procesar_ciudad(jugador, city_name)
    if not r:
        return {"ok": False, "msg": "Ciudad no encontrada"}
    return {"ok": True, **r}


@router.get("/{jugador}/{city_name}/tasas")
def get_tasas(jugador: str, city_name: str):
    player = sm.load_player(jugador.upper())
    unit_levels = player.get("unit_levels", {})
    for c in player.get("cities", []):
        if c.get("NOMBRE") == city_name:
            return {"ok": True, "tasas": calcular_tasas(c, unit_levels)}
    return {"ok": False, "msg": "Ciudad no encontrada"}


@router.post("/{jugador}/{city_name}/tick")
def tick_city(jugador: str, city_name: str):
    r = _procesar_ciudad(jugador, city_name)
    if not r:
        return {"ok": False, "msg": "Ciudad no encontrada"}
    return {"ok": True, **r}


@router.get("/{jugador}")
def get_all_cities(jugador: str):
    player = sm.load_player(jugador.upper())
    return {"ok": True, "cities": [c.get("NOMBRE") for c in player.get("cities", [])]}
