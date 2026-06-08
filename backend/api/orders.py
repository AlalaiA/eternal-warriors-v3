"""
backend/api/orders.py
Eternal Warriors v3.0 — Endpoints de órdenes

Endpoints:
  GET  /api/orders/{jugador}                    — lista órdenes activas del jugador
  POST /api/orders/{jugador}/crear              — crear y despachar una orden
  GET  /api/orders/{jugador}/{orden_id}         — estado de una orden específica
  DELETE /api/orders/{jugador}/{orden_id}       — cancelar orden EN_VIAJE (devuelve tropas/recursos)
  POST /api/orders/tick                         — procesar todas las órdenes activas (llamado interno)
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.data.save_manager import SaveManager
from backend.systems.orders import (
    crear_orden,
    procesar_ordenes,
    info_orden,
    _buscar_ciudad_nombre,
    _unidades_ciudad,
    _nivel_tropas_player,
)
from backend.systems.herreria import calcular_bonus_herreria

router  = APIRouter()
sm      = SaveManager()


# ── Modelos de request ────────────────────────────────────────────────────────

class OrdenRequest(BaseModel):
    tipo:               str                        # ATAQUE|ESPIONAJE|DESPLAZAMIENTO|TRANSPORTE|FUNDAR
    ciudad_origen:      str                        # NOMBRE de la ciudad origen
    x_dest:             float
    y_dest:             float
    unidades:           Optional[dict] = {}        # {NOMBRE: cantidad} — propias
    unidades_prestadas: Optional[dict] = {}        # {jugador_dueño: {NOMBRE: cantidad}}
    recursos:           Optional[dict] = {}        # {RECURSO: cantidad}
    jugador_dest:       Optional[str]  = None      # jugador dueño del destino
    ciudad_dest_nombre: Optional[str]  = None      # nombre ciudad destino (info)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/historial/{jugador}")
def get_historial(jugador: str):
    """
    Retorna informes del jugador — combina:
    1. Órdenes COMPLETADAS despachadas por el jugador (orders.json)
    2. Informes guardados en su JSON personal (copias de órdenes ajenas donde participó)
    """
    jugador = jugador.upper()

    # Fuente 1: órdenes propias completadas
    orders = sm.load_orders()
    propias = [
        o for o in orders
        if o.get("jugador") == jugador
        and o.get("estado") == "COMPLETADA"
        and o.get("resultado") is not None
    ]

    # Fuente 2: informes en JSON personal (participó con tropas prestadas)
    player = sm.load_player(jugador)
    personales = player.get("informes", [])

    # Combinar y deduplicar por id
    ids_vistos = set()
    combinados = []
    for o in propias + personales:
        oid = o.get("id")
        if oid and oid not in ids_vistos:
            ids_vistos.add(oid)
            combinados.append(o)

    combinados.sort(key=lambda o: o.get("inicio", 0), reverse=True)
    return {"ok": True, "ordenes": combinados[:200]}


@router.get("/{jugador}")
def get_ordenes(jugador: str):
    """Lista todas las órdenes activas (no COMPLETADAS) del jugador."""
    jugador = jugador.upper()
    orders  = sm.load_orders()
    activas = [
        info_orden(o) for o in orders
        if o.get("jugador") == jugador and o.get("estado") != "COMPLETADA"
    ]
    return {"ok": True, "ordenes": activas, "total": len(activas)}


@router.get("/{jugador}/{orden_id}")
def get_orden(jugador: str, orden_id: str):
    """Estado detallado de una orden específica."""
    jugador = jugador.upper()
    orders  = sm.load_orders()
    for o in orders:
        if o.get("id") == orden_id and o.get("jugador") == jugador:
            return {"ok": True, "orden": info_orden(o), "detalle": o}
    return {"ok": False, "msg": "Orden no encontrada"}


@router.post("/{jugador}/crear")
def post_crear_orden(jugador: str, req: OrdenRequest):
    """
    Crea y despacha una orden.
    - Valida condiciones
    - Cobra oro y descuenta unidades/recursos de la ciudad origen
    - Encola en orders.json
    """
    jugador = jugador.upper()
    player  = sm.load_player(jugador)
    if not player:
        return {"ok": False, "msg": "Jugador no encontrado"}

    # Buscar ciudad origen
    ciudad_orig = _buscar_ciudad_nombre(player, req.ciudad_origen)
    if not ciudad_orig:
        return {"ok": False, "msg": f"Ciudad origen '{req.ciudad_origen}' no encontrada"}

    # Leer nivel de tropas respetando ambos formatos (global y por tipo)
    nivel_tropas = _nivel_tropas_player(player, req.unidades or {})

    # ── Validar que no se ataque ni espíe a un aliado ────────────────────────
    if req.tipo in ("ATAQUE", "ESPIONAJE") and req.jugador_dest:
        jugador_dest_up = req.jugador_dest.upper()
        if jugador_dest_up != jugador:  # no es ciudad propia
            try:
                alianzas = sm.load_alliances()
                # Buscar en qué alianza está el atacante
                mi_alianza = None
                for nombre_al, al in alianzas.items():
                    miembros = al.get("miembros", [])
                    if jugador in miembros:
                        mi_alianza = nombre_al
                        break
                if mi_alianza:
                    miembros_al = alianzas[mi_alianza].get("miembros", [])
                    if jugador_dest_up in miembros_al:
                        return {"ok": False, "msg": f"No puedes atacar ni espiar a {jugador_dest_up} — es tu aliado en {mi_alianza}"}
            except Exception:
                pass  # Si falla la carga de alianzas, no bloquear

    resultado = crear_orden(
        tipo                = req.tipo,
        jugador             = jugador,
        ciudad_origen       = ciudad_orig,
        x_dest              = req.x_dest,
        y_dest              = req.y_dest,
        unidades            = req.unidades or {},
        recursos            = req.recursos or {},
        nivel_tropas        = nivel_tropas,
        jugador_dest        = req.jugador_dest.upper() if req.jugador_dest else None,
        ciudad_dest_nombre  = req.ciudad_dest_nombre,
        unidades_prestadas  = req.unidades_prestadas or {},
        sm                  = sm,
    )

    if not resultado["ok"]:
        return resultado

    # Guardar jugador (ciudad_orig fue modificada in-place: oro descontado, unidades descontadas)
    sm.save_player(jugador, player)

    # Encolar orden
    orders = sm.load_orders()
    orders.append(resultado["orden"])
    sm.save_orders(orders)

    return {
        "ok":      True,
        "msg":     f"Orden {req.tipo} despachada",
        "orden":   info_orden(resultado["orden"]),
    }


@router.delete("/{jugador}/{orden_id}")
def delete_cancelar_orden(jugador: str, orden_id: str):
    """
    Cancela una orden EN_VIAJE.
    Devuelve tropas y recursos a la ciudad origen.
    No devuelve el oro gastado.
    """
    jugador = jugador.upper()
    orders  = sm.load_orders()
    player  = sm.load_player(jugador)

    for o in orders:
        if o.get("id") != orden_id or o.get("jugador") != jugador:
            continue
        if o["estado"] != "EN_VIAJE":
            return {"ok": False, "msg": f"Solo se pueden cancelar órdenes EN_VIAJE (estado actual: {o['estado']})"}

        # Devolver tropas a ciudad origen
        ciudad_orig = _buscar_ciudad_nombre(player, o["ciudad_origen"])
        if ciudad_orig:
            for nombre, cant in o.get("unidades", {}).items():
                if int(cant or 0) > 0:
                    ciudad_orig[nombre] = int(ciudad_orig.get(nombre, 0) or 0) + int(cant)
            for rec, cant in o.get("recursos", {}).items():
                if float(cant or 0) > 0:
                    ciudad_orig[rec] = float(ciudad_orig.get(rec, 0) or 0) + float(cant)

        o["estado"] = "COMPLETADA"
        sm.save_player(jugador, player)
        sm.save_orders(orders)
        return {"ok": True, "msg": "Orden cancelada — tropas devueltas a ciudad origen"}

    return {"ok": False, "msg": "Orden no encontrada"}


def debug_ordenes(jugador: str):
    """Diagnóstico: muestra todas las órdenes del jugador con detalle completo."""
    jugador = jugador.upper()
    orders  = sm.load_orders()
    player  = sm.load_player(jugador)
    mis_ordenes = [o for o in orders if o.get("jugador") == jugador]

    # Estado actual del jugador
    ciudad_caps = {}
    for city in player.get("cities", []):
        nombre = city.get("NOMBRE")
        ciudad_caps[nombre] = {k: v for k, v in city.items()
                                if k in ["MAGO","GUERRERO","ALDEANO","EXPLORADOR",
                                         "EON_SUPREMO","ALALAIA","CABALLERO_DE_LUZ"]}

    return {
        "ok": True,
        "ordenes": mis_ordenes,
        "ciudades_tropas": ciudad_caps,
        "total_ordenes": len(mis_ordenes),
    }


def tick_ordenes():
    """
    Procesa todas las órdenes activas.
    Llamar periódicamente desde el servidor (cada 5-10 segundos).
    """
    orders  = sm.load_orders()
    orders  = [o for o in orders if isinstance(o, dict) and "estado" in o]
    eventos = procesar_ordenes(orders, sm)
    activas     = [o for o in orders if o.get("estado") != "COMPLETADA"]
    completadas = sorted(
        [o for o in orders if o.get("estado") == "COMPLETADA"],
        key=lambda o: o.get("inicio", 0), reverse=True
    )[:200]
    sm.save_orders(activas + completadas)

    return {
        "ok":     True,
        "eventos": len(eventos),
        "detalle": eventos,
    }
