"""
backend/api/map.py
Eternal Warriors v3.0 — Endpoints del Mapa Imperial

Endpoints:
  GET /api/map/entities          — todas las entidades del mundo (sin cuevas ocultas)
  GET /api/map/players           — ciudades de todos los jugadores activos
  GET /api/map/orders/{jugador}  — órdenes activas del jugador para dibujar trayectorias
  GET /api/map/entity/{cat}/{id} — detalle de una entidad específica
"""

from fastapi import APIRouter
from backend.data.save_manager import SaveManager

router = APIRouter()
sm     = SaveManager()

# Jugadores conocidos — en producción vendría de accounts.json
JUGADORES_ACTIVOS = ["JIARITO", "GINAO", "JOTICALINDO", "ALALAIA"]


@router.get("/entities")
def get_entities():
    """
    Retorna todas las entidades del mundo visibles para el mapa.
    Cuevas ocultas (_oculta=True) no se exponen hasta ser descubiertas.
    """
    inactivos_raw = sm.load_world("inactivos").get("cities", [])
    dioses_raw    = sm.load_world("dioses").get("entities", [])
    cuevas_raw    = sm.load_world("cuevas").get("entities", [])
    portales_raw  = sm.load_world("portales").get("entities", [])
    karlaka_raw   = sm.load_world("karlaka").get("entity", {})

    inactivos = [
        {"id": c.get("ID"), "x": c.get("X"), "y": c.get("Y"),
         "nombre": c.get("NOMBRE"), "cat": "INACTIVOS"}
        for c in inactivos_raw
    ]

    dioses = [
        {"id": d.get("ID"), "x": d.get("X"), "y": d.get("Y"),
         "nombre": d.get("NOMBRE"), "hp": d.get("HP"),
         "pa": d.get("PA"), "ca": d.get("CA"),
         "destreza": d.get("DESTREZA"), "cat": "DIOSES"}
        for d in dioses_raw
        if not d.get("_oculta", False)
    ]

    # Cuevas: solo visibles (no ocultas), capturadas incluyen quién las capturó
    cuevas = [
        {"id": c.get("ID"), "x": c.get("X"), "y": c.get("Y"),
         "clase": c.get("CLASE"), "hp": c.get("HP"),
         "capturada_por": c.get("_capturada_por"),
         "cat": "CUEVAS"}
        for c in cuevas_raw
        if not c.get("_oculta", True)
    ]

    portales = [
        {"id": p.get("ID"), "x": p.get("X"), "y": p.get("Y"),
         "nombre": p.get("NOMBRE"), "cat": "PORTALES"}
        for p in portales_raw
    ]

    karlaka = {
        "id":   karlaka_raw.get("ID"),
        "x":    karlaka_raw.get("X"),
        "y":    karlaka_raw.get("Y"),
        "nombre": karlaka_raw.get("NOMBRE", "KarlakÁ"),
        "hp":   karlaka_raw.get("HP"),
        "cat":  "KARLAKA",
    } if karlaka_raw else None

    return {
        "ok":        True,
        "inactivos": inactivos,
        "dioses":    dioses,
        "cuevas":    cuevas,
        "portales":  portales,
        "karlaka":   karlaka,
    }


@router.get("/players")
def get_players():
    """
    Retorna ciudades de todos los jugadores activos con sus coordenadas,
    jugador, y datos básicos para colorear en el mapa.
    """
    resultado = []
    for nombre in JUGADORES_ACTIVOS:
        try:
            player = sm.load_player(nombre)
            if not player:
                continue
            for city in player.get("cities", []):
                resultado.append({
                    "jugador":  nombre,
                    "nombre":   city.get("NOMBRE"),
                    "x":        city.get("X"),
                    "y":        city.get("Y"),
                    "nivel_cc": city.get("CENTRO_DE_CIUDAD", 1),
                    "muralla":  city.get("MURALLA", 0),
                    "cat":      "CIUDAD_JUGADOR",
                })
        except Exception:
            continue
    return {"ok": True, "ciudades": resultado}


@router.get("/orders/{jugador}")
def get_orders_map(jugador: str):
    """
    Retorna órdenes activas del jugador para dibujar trayectorias en el mapa.
    Solo EN_VIAJE y REGRESANDO.
    """
    jugador = jugador.upper()
    orders  = sm.load_orders()
    activas = [
        {
            "id":      o["id"],
            "tipo":    o["tipo"],
            "estado":  o["estado"],
            "x_orig":  o["x_orig"],
            "y_orig":  o["y_orig"],
            "x_dest":  o["x_dest"],
            "y_dest":  o["y_dest"],
            "t_llegada": o["t_llegada"],
            "t_retorno": o.get("t_retorno"),
            "inicio":  o["inicio"],
        }
        for o in orders
        if o.get("jugador") == jugador
        and o.get("estado") in ("EN_VIAJE", "REGRESANDO")
    ]
    return {"ok": True, "ordenes": activas}


@router.get("/entity/{cat}/{entity_id}")
def get_entity_detail(cat: str, entity_id: str):
    """
    Retorna detalle completo de una entidad del mundo.
    cat: inactivos | dioses | cuevas | portales | karlaka
    """
    cat = cat.lower()
    if cat == "karlaka":
        data = sm.load_world("karlaka").get("entity", {})
        return {"ok": True, "entity": data}

    world_map = {
        "inactivos": ("inactivos", "cities"),
        "dioses":    ("dioses",    "entities"),
        "cuevas":    ("cuevas",    "entities"),
        "portales":  ("portales",  "entities"),
    }
    if cat not in world_map:
        return {"ok": False, "msg": f"Categoría desconocida: {cat}"}

    fname, key = world_map[cat]
    entities   = sm.load_world(fname).get(key, [])
    entity     = next((e for e in entities if str(e.get("ID")) == str(entity_id)), None)

    if not entity:
        return {"ok": False, "msg": "Entidad no encontrada"}

    # Para inactivos, devolver resumen de tropas (sin datos internos)
    if cat == "inactivos":
        return {"ok": True, "entity": {
            "ID":      entity.get("ID"),
            "NOMBRE":  entity.get("NOMBRE"),
            "X":       entity.get("X"),
            "Y":       entity.get("Y"),
            "MURALLA": entity.get("MURALLA", 0),
            "NIVEL_DE_TROPAS": entity.get("NIVEL_DE_TROPAS", 1),
        }}

    return {"ok": True, "entity": entity}
