"""
backend/api/alerts.py
Eternal Warriors v3.0 — Alertas de detección por Torre de Vigilancia

Las alertas se escriben en player["alertas"] por el ticker de órdenes.
Estructura de cada alerta:
{
    "id":         "alerta_<orden_id>",
    "orden_id":   str,
    "ciudad":     str,       # ciudad defensora
    "nivel":      int,       # 1–5
    "tipo_orden": str,       # ATAQUE | ESPIONAJE
    "info":       dict,      # datos revelados según nivel
    "ts":         float,     # timestamp de primera detección
    "activa":     bool,      # False cuando la orden se resuelve
}
"""

import time
from fastapi import APIRouter
from pydantic import BaseModel
from backend.data.save_manager import SaveManager

router = APIRouter()
sm     = SaveManager()


class DismissRequest(BaseModel):
    jugador:  str
    alerta_id: str


@router.get("/{jugador}")
def get_alertas(jugador: str):
    """Devuelve alertas activas del jugador."""
    jugador = jugador.upper()
    player  = sm.load_player(jugador)
    alertas = [a for a in player.get("alertas", []) if a.get("activa", True)]
    return {"ok": True, "alertas": alertas}


@router.post("/dismiss")
def post_dismiss(req: DismissRequest):
    """Marca una alerta como vista (no la elimina — sigue activa hasta resolver)."""
    jugador = req.jugador.upper()

    def _fn(player):
        for a in player.get("alertas", []):
            if a["id"] == req.alerta_id:
                a["vista"] = True
                # Si la orden ya llegó y estaba pendiente de desactivar, desactivar ahora
                if a.get("pendiente_desactivar", False):
                    a["activa"] = False
                break

    sm.update_player(jugador, _fn)
    return {"ok": True}


@router.delete("/{jugador}/limpiar")
def delete_limpiar(jugador: str):
    """Elimina alertas inactivas (resueltas). Llamado desde el frontend."""
    jugador = jugador.upper()

    def _fn(player):
        player["alertas"] = [
            a for a in player.get("alertas", [])
            if a.get("activa", True)
        ]

    sm.update_player(jugador, _fn)
    return {"ok": True}
