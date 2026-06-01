"""
backend/api/alliances.py
Eternal Warriors v3.0 — Endpoints de alianzas y tropas prestadas

Endpoints:
  GET    /api/alliances                                — listar todas las alianzas
  GET    /api/alliances/{jugador}                      — alianza del jugador
  POST   /api/alliances/crear                          — crear alianza
  POST   /api/alliances/solicitar                      — solicitar unirse
  POST   /api/alliances/aceptar                        — aceptar solicitud (líder)
  POST   /api/alliances/salir                          — salir o expulsar
  POST   /api/alliances/prestar                        — prestar tropas a aliado
  POST   /api/alliances/reclamar                       — reclamar tropas prestadas
  GET    /api/alliances/{jugador}/tropas_prestadas     — tropas prestadas en ciudades del jugador
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.data.save_manager import SaveManager
from backend.systems.alliances import (
    crear_alianza, solicitar_union, aceptar_solicitud,
    expulsar_o_salir, prestar_tropas, reclamar_tropas,
    _alianza_de, _son_aliados,
)

router = APIRouter()
sm     = SaveManager()


# ── Modelos ───────────────────────────────────────────────────────────────────

class CrearRequest(BaseModel):
    jugador: str
    nombre:  str

class SolicitarRequest(BaseModel):
    jugador: str
    alianza: str

class AceptarRequest(BaseModel):
    lider:      str
    alianza:    str
    solicitante: str

class SalirRequest(BaseModel):
    jugador:  str
    ejecutor: str
    alianza:  str

class PrestarRequest(BaseModel):
    jugador_dueño:   str
    ciudad_origen:   str
    jugador_huesped: str
    ciudad_destino:  str
    unidades:        dict

class ReclamarRequest(BaseModel):
    jugador_dueño:   str
    jugador_huesped: str
    ciudad_huesped:  str
    unidades:        dict


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("")
def get_all_alliances():
    """Lista todas las alianzas existentes."""
    alianzas = sm.load_alliances()
    return {"ok": True, "alianzas": alianzas}


@router.get("/{jugador}")
def get_alliance_jugador(jugador: str):
    """Devuelve la alianza del jugador y sus aliados."""
    jugador  = jugador.upper()
    alianzas = sm.load_alliances()
    nombre   = _alianza_de(jugador, alianzas)
    if not nombre:
        return {"ok": True, "alianza": None, "miembros": [], "solicitudes": []}
    a = alianzas[nombre]
    return {
        "ok":          True,
        "alianza":     nombre,
        "lider":       a["lider"],
        "miembros":    a["miembros"],
        "solicitudes": a.get("solicitudes", []),
        "es_lider":    a["lider"] == jugador,
    }


@router.post("/crear")
def post_crear(req: CrearRequest):
    alianzas = sm.load_alliances()
    result   = crear_alianza(req.nombre, req.jugador, alianzas)
    if result["ok"]:
        sm.save_alliances(alianzas)
    return result


@router.post("/solicitar")
def post_solicitar(req: SolicitarRequest):
    alianzas = sm.load_alliances()
    result   = solicitar_union(req.alianza, req.jugador, alianzas)
    if result["ok"]:
        sm.save_alliances(alianzas)
    return result


@router.post("/aceptar")
def post_aceptar(req: AceptarRequest):
    alianzas = sm.load_alliances()
    result   = aceptar_solicitud(req.alianza, req.solicitante, req.lider, alianzas)
    if result["ok"]:
        sm.save_alliances(alianzas)
    return result


@router.post("/salir")
def post_salir(req: SalirRequest):
    alianzas = sm.load_alliances()
    result   = expulsar_o_salir(req.alianza, req.jugador, req.ejecutor, alianzas, sm)
    if result["ok"]:
        sm.save_alliances(alianzas)
    return result


@router.post("/prestar")
def post_prestar(req: PrestarRequest):
    alianzas = sm.load_alliances()
    if not _son_aliados(req.jugador_dueño, req.jugador_huesped, alianzas):
        return {"ok": False, "msg": "Solo se pueden prestar tropas a aliados"}
    return prestar_tropas(
        req.jugador_dueño, req.ciudad_origen,
        req.jugador_huesped, req.ciudad_destino,
        req.unidades, sm,
    )


@router.post("/reclamar")
def post_reclamar(req: ReclamarRequest):
    return reclamar_tropas(
        req.jugador_dueño, req.jugador_huesped,
        req.ciudad_huesped, req.unidades, sm,
    )


@router.get("/{jugador}/tropas_prestadas")
def get_tropas_prestadas(jugador: str):
    """
    Devuelve todas las tropas prestadas presentes en ciudades del jugador
    (de otros aliados) y las propias tropas prestadas a otros.
    """
    jugador = jugador.upper()
    player  = sm.load_player(jugador)
    result  = {}

    for city in player.get("cities", []):
        prestadas = city.get("TROPAS_PRESTADAS", [])
        if prestadas:
            result[city["NOMBRE"]] = prestadas

    return {"ok": True, "tropas_prestadas_en_mis_ciudades": result}
