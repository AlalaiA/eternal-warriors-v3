"""
backend/systems/detection.py
Eternal Warriors v3.0 — Detección de ejércitos entrantes por Torre de Vigilancia

Mecánica (inversa del espionaje):
  deteccion_torre  vs  sigilo_efectivo_atacante
  diferencia = deteccion_torre - sigilo_efectivo

  ≤ 0      → No detectado (silencio)
  1–5      → Nv1: coordenadas de origen
  6–15     → Nv2: + jugador atacante
  16–30    → Nv3: + tipo de orden (ATAQUE / ESPIONAJE)
  31–53    → Nv4: + tipos de unidades (sin cantidades)
  ≥ 54     → Nv5: jugador, tipo, unidades con cantidades, niveles y dueños

El radio de vigilancia (radiocasillasvigilancia, col[9]) determina
cuántos tiles alrededor de la ciudad se monitorean.
La detección se evalúa cuando la orden está EN_VIAJE y la distancia
restante al destino es ≤ radio de la torre.
"""

import csv, math
from pathlib import Path
from functools import lru_cache

CSV_DIR = Path(__file__).parent.parent.parent / "csv"


# ── Carga CSV torre ───────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _load_torre_csv() -> dict:
    """
    Retorna dict {nivel: {deteccion, radio}}
    """
    result = {}
    path = CSV_DIR / "edificio4_torre_de_vigilancia.csv"
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        rows   = list(reader)
    for row in rows[1:]:
        if len(row) < 10:
            continue
        try:
            nivel     = int(row[0].strip())
            deteccion = float(row[6].strip())
            radio     = float(row[9].strip())
            result[nivel] = {"deteccion": deteccion, "radio": radio}
        except (ValueError, IndexError):
            pass
    return result


def _stats_torre(nivel: int) -> tuple[float, float]:
    """Devuelve (deteccion, radio) para el nivel de torre dado."""
    tabla = _load_torre_csv()
    if nivel <= 0:
        return 0.0, 0.0
    # Si el nivel exacto no existe, usar el más cercano por debajo
    nv = max((n for n in tabla if n <= nivel), default=None)
    if nv is None:
        return 0.0, 0.0
    e = tabla[nv]
    return e["deteccion"], e["radio"]


# ── Sigilo del atacante ───────────────────────────────────────────────────────

def _sigilo_orden(orden: dict) -> float:
    """
    Calcula el sigilo efectivo del grupo atacante usando la misma fórmula
    que calcular_sigilo_grupo en combat.py.
    Importa dinámicamente para evitar circular imports.
    """
    try:
        from backend.systems.combat import calcular_sigilo_grupo
        # Construir grupos: propias + prestadas
        grupos = []
        nivel_tropas = orden.get("nivel_tropas", 1)

        unidades = orden.get("unidades", {})
        if unidades:
            grupos.append({"unidades": unidades, "nivel_tropas": nivel_tropas})

        for dueño, unids in orden.get("unidades_prestadas", {}).items():
            if unids:
                # nivel_tropas del dueño no lo tenemos aquí — usar el de la orden como approx
                grupos.append({"unidades": unids, "nivel_tropas": nivel_tropas})

        if not grupos:
            return 0.0
        return calcular_sigilo_grupo(grupos)
    except Exception:
        return 0.0


# ── Evaluación principal ──────────────────────────────────────────────────────

def distancia_restante(orden: dict, ahora: float) -> float:
    """
    Estima la distancia restante en tiles basándose en el tiempo transcurrido.
    """
    t_inicio   = orden.get("inicio", ahora)
    t_llegada  = orden.get("t_llegada", ahora)
    distancia  = orden.get("distancia", 0.0)
    duracion   = t_llegada - t_inicio
    if duracion <= 0:
        return 0.0
    fraccion_restante = max(0.0, (t_llegada - ahora) / duracion)
    return distancia * fraccion_restante


def evaluar_deteccion(orden: dict, city_def: dict, ahora: float) -> dict | None:
    """
    Evalúa si la torre de la ciudad defensora detecta la orden entrante.

    Retorna None si no hay detección.
    Retorna dict con nivel y datos de la alerta si detecta.

    Solo aplica a órdenes EN_VIAJE de tipo ATAQUE o ESPIONAJE
    dirigidas a un jugador (no a entidades del mundo).
    """
    tipo = orden.get("tipo", "")
    if tipo not in ("ATAQUE", "ESPIONAJE"):
        return None
    if not orden.get("jugador_dest"):
        return None  # es contra entidad del mundo

    nivel_torre = int(city_def.get("TORRE_DE_VIGILANCIA", 0) or 0)
    if nivel_torre < 1:
        return None

    det, radio = _stats_torre(nivel_torre)
    if radio <= 0:
        return None

    dist_rest = distancia_restante(orden, ahora)

    # La orden debe estar dentro del radio para ser detectable
    if dist_rest > radio:
        return None

    sigilo = _sigilo_orden(orden)
    diferencia = det - sigilo

    if diferencia <= 0:
        return None  # No detectado

    nivel_det = _nivel_deteccion(diferencia)
    info      = _construir_info(orden, nivel_det)

    return {
        "orden_id":   orden["id"],
        "nivel":      nivel_det,
        "tipo_orden": tipo,
        "info":       info,
    }


def _nivel_deteccion(diferencia: float) -> int:
    if diferencia <= 0:  return 0
    if diferencia <= 5:  return 1
    if diferencia <= 15: return 2
    if diferencia <= 30: return 3
    if diferencia <= 53: return 4
    return 5


def _construir_info(orden: dict, nivel: int) -> dict:
    """
    Construye el dict de información revelada según el nivel de detección.
    Nv1: coords origen
    Nv2: + jugador atacante
    Nv3: + tipo de orden
    Nv4: + tipos de unidades (sin cantidades)
    Nv5: + cantidades, niveles y dueños
    """
    info = {
        "x_orig": orden.get("x_orig"),
        "y_orig": orden.get("y_orig"),
    }

    if nivel >= 2:
        info["jugador_atk"] = orden.get("jugador")
        info["x_orig"] = orden.get("x_orig")
        info["y_orig"] = orden.get("y_orig")

    if nivel >= 3:
        info["tipo_orden"] = orden.get("tipo")

    if nivel >= 4:
        # Tipos de unidades sin cantidades
        todas_unidades = set(orden.get("unidades", {}).keys())
        for unids in orden.get("unidades_prestadas", {}).values():
            todas_unidades.update(unids.keys())
        info["tipos_unidades"] = sorted(todas_unidades)

    if nivel >= 5:
        # Cantidades, nivel de tropas y dueños
        info["unidades"]          = orden.get("unidades", {})
        info["unidades_prestadas"] = orden.get("unidades_prestadas", {})
        info["nivel_tropas"]      = orden.get("nivel_tropas", 1)

    return info
