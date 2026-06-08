"""
backend/api/alliances.py
Eternal Warriors v3.0 — Endpoints de alianzas (modelo multi-líder)

Endpoints:
  GET    /api/alliances
  GET    /api/alliances/{jugador}
  GET    /api/alliances/{jugador}/tropas_prestadas
  GET    /api/alliances/{jugador}/mis_tropas_prestadas
  POST   /api/alliances/crear
  POST   /api/alliances/solicitar
  POST   /api/alliances/aceptar
  POST   /api/alliances/rechazar
  POST   /api/alliances/salir
  POST   /api/alliances/promover
  POST   /api/alliances/degradar
  POST   /api/alliances/prestar
  POST   /api/alliances/reclamar
"""

from fastapi import APIRouter
from pydantic import BaseModel
from backend.data.save_manager import SaveManager
from backend.systems.alliances import (
    crear_alianza, solicitar_union, aceptar_solicitud, rechazar_solicitud,
    promover_lider, degradar_lider, expulsar_o_salir,
    prestar_tropas, reclamar_tropas,
    _alianza_de, _son_aliados, _migrar_todas,
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
    ejecutor:    str
    alianza:     str
    solicitante: str

class RechazarRequest(BaseModel):
    ejecutor:    str
    alianza:     str
    solicitante: str

class SalirRequest(BaseModel):
    jugador:  str
    ejecutor: str
    alianza:  str

class PromoverRequest(BaseModel):
    ejecutor: str
    alianza:  str
    miembro:  str

class DegradarRequest(BaseModel):
    ejecutor:       str
    alianza:        str
    lider_objetivo: str

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
    alianzas = sm.load_alliances()
    _migrar_todas(alianzas)
    return {"ok": True, "alianzas": alianzas}


@router.get("/{jugador}/tropas_prestadas")
def get_tropas_prestadas(jugador: str):
    jugador = jugador.upper()
    player  = sm.load_player(jugador)
    result  = {}
    for city in player.get("cities", []):
        prestadas = city.get("TROPAS_PRESTADAS", [])
        if prestadas:
            result[city["NOMBRE"]] = prestadas
    return {"ok": True, "tropas_prestadas_en_mis_ciudades": result}


@router.get("/{jugador}/mis_tropas_prestadas")
def get_mis_tropas_prestadas(jugador: str):
    jugador  = jugador.upper()
    alianzas = sm.load_alliances()
    _migrar_todas(alianzas)
    nombre = _alianza_de(jugador, alianzas)
    if not nombre:
        return {"ok": True, "mis_tropas_en_otros": {}}

    aliados = [m for m in alianzas[nombre]["miembros"] if m != jugador]
    resultado = {}
    for aliado in aliados:
        try:
            player_aliado = sm.load_player(aliado)
        except Exception:
            continue
        for city in player_aliado.get("cities", []):
            mias = [p for p in city.get("TROPAS_PRESTADAS", []) if p["jugador"] == jugador]
            if mias:
                resultado.setdefault(aliado, {})[city["NOMBRE"]] = mias
    return {"ok": True, "mis_tropas_en_otros": resultado}


@router.get("/{jugador}")
def get_alliance_jugador(jugador: str):
    jugador  = jugador.upper()
    alianzas = sm.load_alliances()
    _migrar_todas(alianzas)
    nombre = _alianza_de(jugador, alianzas)
    if not nombre:
        return {"ok": True, "alianza": None, "miembros": [], "solicitudes": []}
    a = alianzas[nombre]
    return {
        "ok":          True,
        "alianza":     nombre,
        "lideres":     a["lideres"],
        "miembros":    a["miembros"],
        "solicitudes": a.get("solicitudes", []),
        "es_lider":    jugador in a["lideres"],
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
    result   = aceptar_solicitud(req.alianza, req.solicitante, req.ejecutor, alianzas)
    if result["ok"]:
        sm.save_alliances(alianzas)
    return result


@router.post("/rechazar")
def post_rechazar(req: RechazarRequest):
    alianzas = sm.load_alliances()
    result   = rechazar_solicitud(req.alianza, req.solicitante, req.ejecutor, alianzas)
    if result["ok"]:
        sm.save_alliances(alianzas)
    return result


@router.post("/promover")
def post_promover(req: PromoverRequest):
    """Un líder promueve a un miembro como co-líder."""
    alianzas = sm.load_alliances()
    result   = promover_lider(req.alianza, req.ejecutor, req.miembro, alianzas)
    if result["ok"]:
        sm.save_alliances(alianzas)
    return result


@router.post("/degradar")
def post_degradar(req: DegradarRequest):
    """Un líder degrada a otro líder (o a sí mismo) a miembro."""
    alianzas = sm.load_alliances()
    result   = degradar_lider(req.alianza, req.ejecutor, req.lider_objetivo, alianzas)
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
    _migrar_todas(alianzas)
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
