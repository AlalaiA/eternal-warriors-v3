"""
backend/api/map.py
Eternal Warriors v3.0 — Endpoints del Mapa Imperial

Endpoints:
  GET /api/map/entities          — todas las entidades del mundo (sin cuevas ocultas)
  GET /api/map/players           — ciudades de todos los jugadores activos
  GET /api/map/orders/{jugador}  — órdenes activas del jugador para dibujar trayectorias
  GET /api/map/entity/{cat}/{id} — detalle de una entidad específica
"""

import math
from typing import Optional
from fastapi import APIRouter, Query
from backend.data.save_manager import SaveManager

router = APIRouter()
sm     = SaveManager()

# Jugadores conocidos — en producción vendría de accounts.json
JUGADORES_ACTIVOS = ["JIARITO", "GINAO", "JOTICALINDO", "ALALAIA", "ADMIN"]

# Radio de visión por ciudad (tiles). Un cuadrado de ±VISION_RADIO centrado en cada ciudad.
VISION_RADIO = 10


def _ciudades_jugador(jugador: str) -> list[dict]:
    """Devuelve lista de {x, y} de todas las ciudades activas del jugador."""
    if not jugador:
        return []
    try:
        player = sm.load_player(jugador.upper())
        return [{"x": float(c.get("X", 0)), "y": float(c.get("Y", 0))}
                for c in player.get("cities", [])]
    except Exception:
        return []


def _en_vision(x: float, y: float, ciudades: list[dict]) -> bool:
    """True si (x,y) cae dentro del radio de visión de al menos una ciudad."""
    if not ciudades:
        return True   # sin ciudades → visión total (no debería ocurrir)
    for c in ciudades:
        if abs(x - c["x"]) <= VISION_RADIO and abs(y - c["y"]) <= VISION_RADIO:
            return True
    return False


@router.get("/entities")
def get_entities(jugador: str = "", sin_vision: bool = False):
    """
    Retorna entidades del mundo visibles para el jugador.
    Si sin_vision=True se devuelve todo (uso interno / admin).
    En caso contrario, se filtra a radio VISION_RADIO tiles desde cada ciudad del jugador.
    """
    # Cargar dioses abatidos por el jugador
    dioses_abatidos_jugador = set()
    if jugador:
        try:
            player = sm.load_player(jugador.upper())
            da = player.get("dioses_abatidos", [])
            if isinstance(da, list):
                dioses_abatidos_jugador = set(str(x) for x in da)
        except Exception:
            pass

    ciudades_vis = [] if sin_vision else _ciudades_jugador(jugador)
    # Si no hay ciudades cargadas (jugador nuevo / sin contexto) → visión total
    usar_vision = bool(ciudades_vis)

    def visible(x, y):
        if not usar_vision:
            return True
        return _en_vision(float(x), float(y), ciudades_vis)
    inactivos_raw = sm.load_world("inactivos").get("cities", [])
    dioses_raw    = sm.load_world("dioses").get("entities", [])
    cuevas_raw    = sm.load_world("cuevas").get("entities", [])
    portales_raw  = sm.load_world("portales").get("entities", [])
    karlaka_raw   = sm.load_world("karlaka").get("entity", {})

    inactivos = [
        {"id": c.get("ID"), "x": c.get("X"), "y": c.get("Y"),
         "nombre": c.get("NOMBRE"), "cat": "INACTIVOS"}
        for c in inactivos_raw
        if visible(c.get("X", 0), c.get("Y", 0))
    ]

    dioses = [
        {"id": d.get("ID"), "x": d.get("X"), "y": d.get("Y"),
         "nombre": d.get("NOMBRE"), "hp": d.get("HP"),
         "pa": d.get("PA"), "ca": d.get("CA"),
         "destreza": d.get("DESTREZA"), "cat": "DIOSES"}
        for d in dioses_raw
        if not d.get("_oculta", False)
        and str(d.get("ID", "")) not in dioses_abatidos_jugador
        and visible(d.get("X", 0), d.get("Y", 0))
    ]

    cuevas = [
        {"id": c.get("ID"), "x": c.get("X"), "y": c.get("Y"),
         "clase": c.get("CLASE"), "hp": c.get("HP"),
         "capturada_por": c.get("_capturada_por"),
         "cat": "CUEVAS"}
        for c in cuevas_raw
        if not c.get("_oculta", True)
        and visible(c.get("X", 0), c.get("Y", 0))
    ]

    portales = [
        {"id": p.get("ID"), "x": p.get("X"), "y": p.get("Y"),
         "nombre": p.get("NOMBRE"), "cat": "PORTALES"}
        for p in portales_raw
        if visible(p.get("X", 0), p.get("Y", 0))
    ]

    # KarlakÁ: siempre visible (es un evento global, todos lo saben)
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
def get_players(jugador: str = "", sin_vision: bool = False):
    """
    Retorna ciudades de todos los jugadores activos.
    Aplica el mismo filtro de visión que /entities para el jugador consultante.
    Las ciudades propias SIEMPRE son visibles (están dentro del radio por definición).
    """
    ciudades_vis = [] if sin_vision else _ciudades_jugador(jugador)
    usar_vision  = bool(ciudades_vis)

    def visible(x, y):
        if not usar_vision:
            return True
        return _en_vision(float(x), float(y), ciudades_vis)

    resultado = []
    for nombre in JUGADORES_ACTIVOS:
        try:
            player = sm.load_player(nombre)
            if not player:
                continue
            es_propio       = nombre.upper() == jugador.upper()
            es_vitaminizado = nombre in ("ALALAIA", "ADMIN")
            for city in player.get("cities", []):
                cx, cy = city.get("X", 0), city.get("Y", 0)
                if not es_propio and not visible(cx, cy):
                    continue
                resultado.append({
                    "jugador":  nombre,
                    "nombre":   city.get("NOMBRE"),
                    "x":        cx,
                    "y":        cy,
                    "nivel_cc": city.get("CENTRO_DE_CIUDAD", 1),
                    "muralla":  city.get("MURALLA", 0),
                    "cat":      "CIUDAD_VITAMINIZADA" if es_vitaminizado else "CIUDAD_JUGADOR",
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


@router.get("/detected/{jugador}")
def get_detected(jugador: str):
    """
    Retorna órdenes enemigas detectadas por la Torre de Vigilancia del jugador.
    Se extraen de las alertas activas guardadas en player["alertas"].
    Solo incluye alertas con t_llegada (para poder dibujar la trayectoria).
    """
    jugador = jugador.upper()
    try:
        player  = sm.load_player(jugador)
        alertas = [a for a in player.get("alertas", []) if a.get("activa")]
        detectadas = []
        for a in alertas:
            if not a.get("t_llegada"):
                continue
            info = a.get("info", {})
            detectadas.append({
                "id":        a.get("orden_id"),
                "tipo":      a.get("tipo_orden", "ATAQUE"),
                "estado":    "EN_VIAJE",
                "x_orig":    info.get("x_orig"),
                "y_orig":    info.get("y_orig"),
                "x_dest":    a.get("x_dest"),
                "y_dest":    a.get("y_dest"),
                "inicio":    a.get("ts"),
                "t_llegada": a.get("t_llegada"),
                "t_retorno": None,
                "jugador_atk": info.get("jugador_atk"),
                "nivel":     a.get("nivel"),
            })
        return {"ok": True, "detectadas": detectadas}
    except Exception as e:
        return {"ok": False, "detectadas": [], "msg": str(e)}



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
