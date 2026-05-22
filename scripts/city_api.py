"""
backend/api/city.py
Endpoints de ciudad con sistema de producción integrado
"""
from fastapi import APIRouter
from backend.data.save_manager import SaveManager
from backend.systems.production import aplicar_produccion, calcular_tasas, init_last_prod

router = APIRouter()
sm = SaveManager()

@router.get("/{jugador}/{city_name}")
def get_city(jugador: str, city_name: str):
    player = sm.load_player(jugador.upper())
    cities = player.get("cities", [])
    for i, c in enumerate(cities):
        if c.get("NOMBRE") == city_name:
            # Inicializar LAST_PROD si no existe
            init_last_prod(c)
            # Aplicar producción retroactiva
            tasas = aplicar_produccion(c)
            # Guardar el estado actualizado
            player["cities"][i] = c
            sm.save_player(jugador.upper(), player)
            return {
                "ok":    True,
                "city":  c,
                "tasas": tasas,   # tasas/seg que el frontend usa para el ticker
            }
    return {"ok": False, "msg": "Ciudad no encontrada"}


@router.get("/{jugador}/{city_name}/tasas")
def get_tasas(jugador: str, city_name: str):
    """Devuelve solo las tasas de producción por segundo — para el ticker del frontend."""
    player = sm.load_player(jugador.upper())
    for c in player.get("cities", []):
        if c.get("NOMBRE") == city_name:
            tasas = calcular_tasas(c)
            return {"ok": True, "tasas": tasas}
    return {"ok": False, "msg": "Ciudad no encontrada"}


@router.post("/{jugador}/{city_name}/tick")
def tick_city(jugador: str, city_name: str):
    """
    Aplica producción desde LAST_PROD hasta ahora y guarda.
    El frontend llama este endpoint cada 30 segundos como checkpoint.
    """
    player = sm.load_player(jugador.upper())
    cities = player.get("cities", [])
    for i, c in enumerate(cities):
        if c.get("NOMBRE") == city_name:
            init_last_prod(c)
            tasas = aplicar_produccion(c)
            player["cities"][i] = c
            sm.save_player(jugador.upper(), player)
            return {
                "ok":   True,
                "city": c,
                "tasas": tasas,
            }
    return {"ok": False, "msg": "Ciudad no encontrada"}


@router.get("/{jugador}")
def get_all_cities(jugador: str):
    player = sm.load_player(jugador.upper())
    return {"ok": True, "cities": [c.get("NOMBRE") for c in player.get("cities", [])]}
