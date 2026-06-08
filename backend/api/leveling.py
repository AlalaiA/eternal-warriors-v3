"""
backend/api/leveling.py
Eternal Warriors v3.0 — Subida de nivel de tropas

El jugador decide manualmente a qué tipo de tropa asignar XP del pool global.
La XP se descuenta de player["experiencia"] y el nivel sube en player["unit_levels"][tipo].

Endpoints:
  GET  /api/leveling/{jugador}              — estado actual: niveles, XP pool, costos
  POST /api/leveling/{jugador}/subir        — subir nivel de un tipo de tropa
"""

import csv
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from backend.data.save_manager import SaveManager

router = APIRouter()
sm     = SaveManager()

CSV_PATH = Path(__file__).parent.parent.parent / "csv" / "experiencia_requerida.csv"

# ── Tabla XP acumulada por nivel ──────────────────────────────────────────────
_XP_TABLA: dict[int, float] = {}

def _cargar_tabla():
    global _XP_TABLA
    if _XP_TABLA:
        return
    if not CSV_PATH.exists():
        return
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            try:
                nivel = int(row["nivel"])
                xp    = float(str(row["experiencia_requerida"]).strip().replace(",", "."))
                _XP_TABLA[nivel] = xp
            except Exception:
                pass

_cargar_tabla()

MAX_NIVEL = 40

# Todas las tropas básicas e invocaciones que pueden subir de nivel
# Solo tropas básicas del cuartel tienen nivel propio.
# Invocaciones y criaturas de cueva NO tienen nivel.
TROPAS_BASICAS = [
    "ALDEANO", "EXPLORADOR", "SACERDOTE", "GUERRERO", "COMANDO",
    "MERCENARIO", "MARINE", "CYBORG", "MAGO", "METAHUMANO",
]
TODAS_LAS_TROPAS = TROPAS_BASICAS


def _xp_para_nivel(nivel_destino: int) -> float:
    """XP acumulada total necesaria para alcanzar nivel_destino."""
    return _XP_TABLA.get(nivel_destino, float("inf"))


def _xp_para_subir(nivel_actual: int) -> float:
    """XP que cuesta subir DEL nivel_actual AL siguiente."""
    if nivel_actual >= MAX_NIVEL:
        return float("inf")
    return _xp_para_nivel(nivel_actual + 1)


def _nivel_max_efectivo(player: dict) -> int:
    """
    Nivel máximo que puede alcanzar el jugador según dioses abatidos.
    Base: nivel 20. Cada 20 dioses abatidos desbloquea 1 nivel adicional (máx 40).
    """
    dioses = player.get("dioses_abatidos", 0)
    if isinstance(dioses, list):
        dioses = len(dioses)
    dioses = int(dioses or 0)
    return min(MAX_NIVEL, 20 + dioses // 20)


def _nivel_actual(player: dict, tipo: str) -> int:
    """Nivel actual de un tipo de tropa. Default 1 si no está en unit_levels."""
    ul = player.get("unit_levels", {})
    # Soporte formato global NIVEL_DE_TROPAS (legacy)
    if "NIVEL_DE_TROPAS" in ul and tipo not in ul:
        return int(ul["NIVEL_DE_TROPAS"] or 1)
    return int(ul.get(tipo, 1) or 1)


def _get_estado(jugador: str) -> dict:
    """Retorna el estado completo de niveles y costos del jugador."""
    player = sm.load_player(jugador.upper())
    if not player:
        return {"ok": False, "msg": "Jugador no encontrado"}

    xp_pool = float(player.get("experiencia", 0) or 0)
    ul       = player.get("unit_levels", {})

    nivel_max_ef = _nivel_max_efectivo(player)
    tropas = []
    for tipo in TODAS_LAS_TROPAS:
        nivel   = _nivel_actual(player, tipo)
        costo   = _xp_para_subir(nivel)
        puede   = nivel < nivel_max_ef and xp_pool >= costo
        tropas.append({
            "tipo":        tipo,
            "nivel":       nivel,
            "nivel_max":   nivel_max_ef,
            "xp_costo":    costo if nivel < nivel_max_ef else None,
            "puede_subir": puede,
        })

    return {
        "ok":      True,
        "jugador": jugador.upper(),
        "xp_pool": xp_pool,
        "tropas":  tropas,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/{jugador}")
def get_leveling(jugador: str):
    return _get_estado(jugador)


class SubirRequest(BaseModel):
    tipo: str   # nombre de la tropa, ej. "GUERRERO"


@router.post("/{jugador}/subir")
def post_subir_nivel(jugador: str, req: SubirRequest):
    jugador = jugador.upper()
    tipo    = req.tipo.upper()

    if tipo not in TODAS_LAS_TROPAS:
        return {"ok": False, "msg": f"Tipo de tropa desconocido: {tipo}"}

    resultado = {}

    def _fn(player):
        xp_pool = float(player.get("experiencia", 0) or 0)
        nivel   = _nivel_actual(player, tipo)

        nivel_max_ef = _nivel_max_efectivo(player)
        if nivel >= nivel_max_ef:
            msg = f"{tipo} ya está en nivel máximo ({nivel_max_ef})"
            if nivel_max_ef < MAX_NIVEL:
                dioses = player.get("dioses_abatidos", 0)
                if isinstance(dioses, list): dioses = len(dioses)
                faltan = 20 - (int(dioses or 0) % 20)
                msg += f" — mata {faltan} dioses más para desbloquear nivel {nivel_max_ef+1}"
            resultado.update({"ok": False, "msg": msg})
            return

        costo = _xp_para_subir(nivel)
        if xp_pool < costo:
            resultado.update({
                "ok":    False,
                "msg":   f"XP insuficiente. Necesitas {costo:,.0f}, tienes {xp_pool:,.0f}",
                "falta": costo - xp_pool,
            })
            return

        # Descontar XP y subir nivel
        player["experiencia"] = xp_pool - costo
        if "unit_levels" not in player:
            player["unit_levels"] = {}
        # Migrar formato global si existe
        if "NIVEL_DE_TROPAS" in player["unit_levels"] and tipo not in player["unit_levels"]:
            nv_global = int(player["unit_levels"]["NIVEL_DE_TROPAS"] or 1)
            player["unit_levels"][tipo] = nv_global
        player["unit_levels"][tipo] = nivel + 1

        resultado.update({
            "ok":          True,
            "tipo":        tipo,
            "nivel_antes": nivel,
            "nivel_nuevo": nivel + 1,
            "xp_gastada":  costo,
            "xp_restante": player["experiencia"],
        })

    sm.update_player(jugador, _fn)
    return resultado
