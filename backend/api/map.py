"""
Endpoints de mapa
"""
from fastapi import APIRouter
from backend.data.save_manager import SaveManager

router = APIRouter()
sm = SaveManager()

@router.get("/entities")
def get_entities():
    """Retorna todas las entidades del mundo para el mapa."""
    inactivos = sm.load_world("inactivos").get("cities", [])
    dioses    = sm.load_world("dioses").get("entities", [])
    cuevas    = sm.load_world("cuevas").get("entities", [])
    portales  = sm.load_world("portales").get("entities", [])
    karlaka   = sm.load_world("karlaka").get("entity", {})
    return {
        "ok": True,
        "inactivos": [{"id": c.get("ID"), "x": c.get("X"), "y": c.get("Y"), "nombre": c.get("NOMBRE")} for c in inactivos],
        "dioses":    [{"id": d.get("ID"), "x": d.get("X"), "y": d.get("Y"), "nombre": d.get("NOMBRE")} for d in dioses],
        "cuevas":    [{"id": c.get("ID"), "x": c.get("X"), "y": c.get("Y"), "nombre": c.get("NOMBRE")} for c in cuevas],
        "portales":  [{"id": p.get("ID"), "x": p.get("X"), "y": p.get("Y"), "nombre": p.get("NOMBRE")} for p in portales],
        "karlaka":   {"x": karlaka.get("X"), "y": karlaka.get("Y")},
    }
