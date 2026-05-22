"""
backend/api/queues.py
Endpoints REST para colas de entrenamiento e invocación
"""
from fastapi import APIRouter
from pydantic import BaseModel
from backend.data.save_manager import SaveManager
from backend.systems.queues import (
    procesar_colas, iniciar_cola_cuartel, iniciar_cola_templo,
    cancelar_cola, info_colas
)

router = APIRouter()
sm = SaveManager()


class ColaCuartelRequest(BaseModel):
    cuartel: str    # CUARTEL_1, CUARTEL_2, CUARTEL_3
    unidad:  str    # GUERRERO, MAGO, etc.
    cantidad: int


class ColaTemploRequest(BaseModel):
    templo:     str  # TEMPLO_1, TEMPLO_2, TEMPLO_3
    invocacion: str  # DEMONIO, ANIMA, etc.
    cantidad:   int


def _get_city_and_player(jugador: str, city_name: str):
    player = sm.load_player(jugador.upper())
    cities = player.get("cities", [])
    for i, c in enumerate(cities):
        if c.get("NOMBRE") == city_name:
            return player, cities, i, c
    return player, cities, -1, None


@router.get("/{jugador}/{city_name}")
def get_colas(jugador: str, city_name: str):
    """Estado actual de todas las colas de una ciudad."""
    player, cities, idx, city = _get_city_and_player(jugador, city_name)
    if city is None:
        return {"ok": False, "msg": "Ciudad no encontrada"}

    unit_levels = player.get("unit_levels", {})

    # Procesar colas retroactivamente
    completadas = procesar_colas(city, unit_levels)
    if completadas:
        cities[idx] = city
        player["cities"] = cities
        sm.save_player(jugador.upper(), player)

    return {
        "ok": True,
        "colas": info_colas(city),
        "completadas": completadas,
        "mana": city.get("MANA", 0),
    }


@router.post("/{jugador}/{city_name}/cuartel")
def iniciar_cuartel(jugador: str, city_name: str, req: ColaCuartelRequest):
    """Inicia una cola de entrenamiento en un cuartel."""
    player, cities, idx, city = _get_city_and_player(jugador, city_name)
    if city is None:
        return {"ok": False, "msg": "Ciudad no encontrada"}

    unit_levels = player.get("unit_levels", {})

    # Procesar colas pendientes primero
    procesar_colas(city, unit_levels)

    result = iniciar_cola_cuartel(city, req.cuartel, req.unidad, req.cantidad, unit_levels)

    if result["ok"]:
        cities[idx] = city
        player["cities"] = cities
        sm.save_player(jugador.upper(), player)

    return result


@router.post("/{jugador}/{city_name}/templo")
def iniciar_templo(jugador: str, city_name: str, req: ColaTemploRequest):
    """Inicia una cola de invocación en un templo."""
    player, cities, idx, city = _get_city_and_player(jugador, city_name)
    if city is None:
        return {"ok": False, "msg": "Ciudad no encontrada"}

    unit_levels = player.get("unit_levels", {})

    # Procesar colas pendientes primero
    procesar_colas(city, unit_levels)

    result = iniciar_cola_templo(city, req.templo, req.invocacion, req.cantidad, unit_levels)

    if result["ok"]:
        cities[idx] = city
        player["cities"] = cities
        sm.save_player(jugador.upper(), player)

    return result


@router.delete("/{jugador}/{city_name}/{tipo}")
def cancelar(jugador: str, city_name: str, tipo: str):
    """Cancela la cola de un cuartel o templo específico."""
    player, cities, idx, city = _get_city_and_player(jugador, city_name)
    if city is None:
        return {"ok": False, "msg": "Ciudad no encontrada"}

    result = cancelar_cola(city, tipo.upper())

    if result["ok"]:
        cities[idx] = city
        player["cities"] = cities
        sm.save_player(jugador.upper(), player)

    return result
