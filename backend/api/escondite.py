"""
backend/api/escondite.py
Endpoints REST para el sistema de Escondite.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from backend.data.save_manager import SaveManager
from backend.systems.escondite import (
    get_estado, meter_material, sacar_material,
    meter_tropas, sacar_tropas
)

router = APIRouter(prefix="/api/escondite", tags=["escondite"])
sm = SaveManager()


def _get_city(jugador: str, ciudad: str):
    player = sm.load_player(jugador.upper())
    city = next((c for c in player.get("cities", []) if c["NOMBRE"] == ciudad), None)
    return player, city


class MaterialRequest(BaseModel):
    material: str
    cantidad: float

class TropaRequest(BaseModel):
    tropa: str
    cantidad: int


@router.get("/{jugador}/{ciudad}")
def get_escondite(jugador: str, ciudad: str):
    player, city = _get_city(jugador, ciudad)
    if not city:
        return {"ok": False, "msg": "Ciudad no encontrada"}
    return {"ok": True, "estado": get_estado(city)}


@router.post("/{jugador}/{ciudad}/meter_material")
def post_meter_material(jugador: str, ciudad: str, req: MaterialRequest):
    player, city = _get_city(jugador, ciudad)
    if not city:
        return {"ok": False, "msg": "Ciudad no encontrada"}
    result = meter_material(city, req.material, req.cantidad)
    if result["ok"]:
        sm.save_player(jugador.upper(), player)
    return result


@router.post("/{jugador}/{ciudad}/sacar_material")
def post_sacar_material(jugador: str, ciudad: str, req: MaterialRequest):
    player, city = _get_city(jugador, ciudad)
    if not city:
        return {"ok": False, "msg": "Ciudad no encontrada"}
    result = sacar_material(city, req.material, req.cantidad)
    if result["ok"]:
        sm.save_player(jugador.upper(), player)
    return result


@router.post("/{jugador}/{ciudad}/meter_tropas")
def post_meter_tropas(jugador: str, ciudad: str, req: TropaRequest):
    player, city = _get_city(jugador, ciudad)
    if not city:
        return {"ok": False, "msg": "Ciudad no encontrada"}
    result = meter_tropas(city, req.tropa, req.cantidad)
    if result["ok"]:
        sm.save_player(jugador.upper(), player)
    return result


@router.post("/{jugador}/{ciudad}/sacar_tropas")
def post_sacar_tropas(jugador: str, ciudad: str, req: TropaRequest):
    player, city = _get_city(jugador, ciudad)
    if not city:
        return {"ok": False, "msg": "Ciudad no encontrada"}
    result = sacar_tropas(city, req.tropa, req.cantidad)
    if result["ok"]:
        sm.save_player(jugador.upper(), player)
    return result
