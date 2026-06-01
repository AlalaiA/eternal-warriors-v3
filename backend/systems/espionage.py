import csv
"""
backend/systems/espionage.py
Eternal Warriors v3.0 — Sistema de espionaje y exploración

Reglas canónicas:
  - sigilo_efectivo = sigilo_max_pelotón - (total_unidades - 1)
  - Si sigilo_efectivo <= 0: detección garantizada → combate automático
  - Si detectado: combate igual que ATAQUE (usando nueva API multi-jugador)
  - Si no detectado: inteligencia completa de la ciudad + botín si Explorador Nv40
  - Exploración (Cuevas/Dioses/Portales): siempre combate via resolver_combate_entidad
  - Invincible Explorer: exactamente 1 Explorador + nivel 40 + ≥1 Éon Supremo → sigilo=102 forzado
"""

from pathlib import Path
from backend.systems.combat import (
    calcular_sigilo,
    resolver_combate,
    resolver_combate_entidad,
    aplicar_resultado_combate,
    get_stats_unidad,
    _norm,
    INVOCACIONES,
)

CSV_DIR = Path(__file__).parent.parent.parent / "csv"

CSV_DIR_ESP = Path(__file__).parent.parent.parent / "csv"
_TORRE_DETECCION: dict | None = None

def _get_torre_deteccion() -> dict:
    """Carga detección por nivel de torre de vigilancia."""
    global _TORRE_DETECCION
    if _TORRE_DETECCION is not None:
        return _TORRE_DETECCION
    path = CSV_DIR_ESP / "edificio4_torre_de_vigilancia.csv"
    result = {}
    if path.exists():
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter=";")
            next(reader)
            for row in reader:
                if row and row[0].strip().isdigit():
                    result[int(row[0])] = int(row[6])
    _TORRE_DETECCION = result
    return result


def _nivel_espionaje_por_diff(diff: float) -> int:
    """
    Nivel de inteligencia según diferencia (sigilo_efectivo - deteccion_torre).
    Umbrales calibrados para nueva fórmula de sigilo (f=3.0):
      Nv1:  1–5    Nv2:  6–15    Nv3: 16–30
      Nv4: 31–53   Nv5: ≥54
    Referencia: 20 exploradores nv40 vs Torre nv50 → diff=54 → Nv5
    """
    if diff <= 5:  return 1
    if diff <= 15: return 2
    if diff <= 30: return 3
    if diff <= 53: return 4
    return 5


def _nivel_espionaje(sigilo_efectivo: float, nivel_torre: int) -> int:
    if sigilo_efectivo <= 0:
        return 0
    torre_db  = _get_torre_deteccion()
    max_nv    = max(torre_db.keys()) if torre_db else 1
    deteccion = torre_db.get(nivel_torre, torre_db.get(max_nv, 6))
    diff      = sigilo_efectivo - deteccion
    if diff <= 0: return 0
    return _nivel_espionaje_por_diff(diff)


UNIDADES_BASICAS = {
    "ALDEANO", "EXPLORADOR", "SACERDOTE", "GUERRERO", "COMANDO",
    "MERCENARIO", "MARINE", "CYBORG", "MAGO", "METAHUMANO",
}


# ── Espionaje ciudad ──────────────────────────────────────────────────────────

def resolver_espionaje(
    jugador_atk: str,
    unidades_atk: dict,
    nivel_tropas_atk: int,
    bonus_herreria_atk: dict,
    jugador_def: str,
    unidades_def: dict,
    nivel_tropas_def: int,
    objetivo_city: dict,
    sigilo_precalculado: float = None,   # ← añadir esta línea
) -> dict:
    """
    Resuelve una misión de espionaje contra una ciudad.

    Parámetros:
        jugador_atk:        nombre del jugador atacante
        unidades_atk:       {NOMBRE: cantidad} del pelotón espía
        nivel_tropas_atk:   nivel de tropas del atacante
        bonus_herreria_atk: {pa_bonus, ca_bonus, hp_bonus}
        jugador_def:        nombre del jugador defensor
        unidades_def:       {NOMBRE: cantidad} de tropas defensoras de la ciudad
        nivel_tropas_def:   nivel de tropas del defensor
        objetivo_city:      dict de la ciudad objetivo

    Retorna:
        {
          "detectado": bool,
          "sigilo_efectivo": float,
          "combate": dict | None,
          "inteligencia": dict | None,
          "botin_espionaje": dict,
        }
    """
    # ── Calcular sigilo ───────────────────────────────────────────────────────
    # Si viene precalculado (multi-propietario con niveles distintos), usarlo directamente
    if sigilo_precalculado is not None:
        sigilo_efectivo = sigilo_precalculado
    else:
        sigilo_efectivo = calcular_sigilo(unidades_atk, nivel_tropas_atk)

    nivel_torre_det = int(objetivo_city.get("TORRE_DE_VIGILANCIA", 0) or 0)
    torre_db_det    = _get_torre_deteccion()
    max_nv_det      = max(torre_db_det.keys()) if torre_db_det else 1
    deteccion_torre = torre_db_det.get(nivel_torre_det, torre_db_det.get(max_nv_det, 0)) if nivel_torre_det > 0 else 0
    detectado       = sigilo_efectivo <= 0 or deteccion_torre >= sigilo_efectivo

    if detectado:
        atacantes = [{
            "jugador":       jugador_atk,
            "unidades":      unidades_atk,
            "nivel_tropas":  nivel_tropas_atk,
            "bonus_herreria": bonus_herreria_atk or {"pa_bonus":0,"ca_bonus":0,"hp_bonus":0},
        }]
        defensores = [{
            "jugador":      jugador_def,
            "unidades":     unidades_def,
            "nivel_tropas": nivel_tropas_def,
        }]
        nivel_muralla = int(objetivo_city.get("MURALLA", 0) or 0)
        combate = resolver_combate(atacantes, defensores, objetivo_city, nivel_muralla)
        combate["deteccion_garantizada"] = True
        return {
            "detectado":       True,
            "sigilo_efectivo": sigilo_efectivo,
            "combate":         combate,
            "inteligencia":    None,
        }

    # ── Espionaje exitoso ─────────────────────────────────────────────────────
    diff_intel  = sigilo_efectivo - deteccion_torre
    nivel_espio = _nivel_espionaje_por_diff(diff_intel) if diff_intel > 0 else 1
    inteligencia = _recopilar_inteligencia(objetivo_city, nivel_espio)

    return {
        "detectado":       False,
        "sigilo_efectivo": sigilo_efectivo,
        "nivel_espionaje": nivel_espio,
        "combate":         None,
        "inteligencia":    inteligencia,
    }


def _recopilar_inteligencia(city: dict, nivel: int) -> dict:
    """
    Extrae datos de la ciudad según el nivel de espionaje obtenido.
    Nivel 1: nombre + coords
    Nivel 2: + recursos
    Nivel 3: + ejército básico
    Nivel 4: + invocaciones + edificios
    Nivel 5: + escondite
    """
    info = {
        "nivel":   nivel,
        "nombre":  city.get("NOMBRE", "?"),
        "jugador": city.get("JUGADOR", city.get("_jugador", "?")),
        "x":       city.get("X"),
        "y":       city.get("Y"),
        "muralla": city.get("MURALLA", 0),
    }

    if nivel >= 2:
        REC = ["MADERA","PIEDRA","HIERRO","CARBON","ORO","MANA"]
        info["recursos"] = {r: float(city.get(r, 0) or 0) for r in REC}

    if nivel >= 3:
        UB = ["ALDEANO","EXPLORADOR","SACERDOTE","GUERRERO","COMANDO",
              "MERCENARIO","MARINE","CYBORG","MAGO","METAHUMANO"]
        info["ejercito"] = {u: int(city.get(u, 0) or 0) for u in UB}

    if nivel >= 4:
        INV = ["DEMONIO","ANIMA","ESPECTRO","GOLEM","CENTAURO","KRAKEN",
               "ALONARDO","MADRESELVA","COLOSO","FENIX","DRAGON DE ORO",
               "CABALLERO DE LUZ","ALALAIA","EON SUPREMO"]
        EDI = ["CENTRO_DE_CIUDAD","CASA","MURALLA","TORRE_DE_VIGILANCIA",
               "CENTRO_DE_VIAJES","ESCONDITE","ALMACEN","SANTUARIO_ARCANO",
               "UNIVERSIDAD","HERRERIA","TEMPLO_1","TEMPLO_2","TEMPLO_3",
               "CUARTEL_1","CUARTEL_2"]
        info["invocaciones"] = {i: int(city.get(i, 0) or 0) for i in INV}
        info["edificios"]    = {e: int(city.get(e, 0) or 0) for e in EDI}

    if nivel >= 5:
        info["escondite"] = city.get("ESCONDITE_DATA", {})

    return info



# ── Exploración (Cuevas / Dioses / Portales) ──────────────────────────────────

def resolver_exploracion(
    jugador_atk: str,
    unidades_atk: dict,
    nivel_tropas_atk: int,
    bonus_herreria_atk: dict,
    entidad: dict,
) -> dict:
    """
    Resuelve una exploración contra una entidad del mundo.
    Siempre es combate, sin sigilo.

    entidad: {nombre, tipo, hp, pa, ca, destreza, experiencia}

    Retorna:
        {
          "victoria": bool,
          "combate": dict,
          "entidad_derrotada": bool,
          "xp_obtenida": float,
        }
    """
    atacante = {
        "jugador":        jugador_atk,
        "unidades":       unidades_atk,
        "nivel_tropas":   nivel_tropas_atk,
        "bonus_herreria": bonus_herreria_atk,
    }
    combate = resolver_combate_entidad(atacante, entidad)
    xp = combate["xp_por_jugador_atk"].get(jugador_atk, 0.0)

    return {
        "victoria":          combate["victoria_atacante"],
        "combate":           combate,
        "entidad_derrotada": combate["victoria_atacante"],
        "xp_obtenida":       xp,
    }


# ── Aplicar resultados ────────────────────────────────────────────────────────

def aplicar_resultado_espionaje(
    resultado: dict,
    atacante_city: dict,
    objetivo_city: dict,
    jugador_atacante: dict,
    jugador_defensor: dict,
) -> None:
    """
    Aplica in-place el resultado del espionaje.
    Si detectado → aplica combate completo.
    Si exitoso → transfiere botín + incrementa contador.
    """
    if resultado["detectado"] and resultado["combate"]:
        aplicar_resultado_combate(
            resultado["combate"],
            ciudades_atk={jugador_atacante.get("player", "?"): atacante_city},
            ciudades_def={jugador_defensor.get("player", "?"): objetivo_city},
            jugadores_atk={jugador_atacante.get("player", "?"): jugador_atacante},
            jugadores_def={jugador_defensor.get("player", "?"): jugador_defensor},
        )
    else:
        jugador_atacante["misiones_espionaje"] = (
            int(jugador_atacante.get("misiones_espionaje", 0) or 0) + 1
        )


def aplicar_resultado_exploracion(
    resultado: dict,
    atacante_city: dict,
    jugador_atacante: dict,
    tipo_entidad: str = "",
) -> None:
    """
    Aplica in-place el resultado de una exploración:
    bajas, XP y contadores.
    """
    jugador_key = jugador_atacante.get("player", "?")
    combate     = resultado.get("combate", {})

    # Bajas
    bajas = combate.get("bajas_atk", {}).get(jugador_key, {})
    for nombre, cnt in bajas.items():
        if cnt > 0:
            atacante_city[nombre] = max(0.0, float(atacante_city.get(nombre, 0) or 0) - cnt)

    # XP
    xp = resultado.get("xp_obtenida", 0.0)
    jugador_atacante["experiencia"] = float(jugador_atacante.get("experiencia", 0) or 0) + xp

    # Contadores
    if resultado["victoria"]:
        tipo = tipo_entidad.lower()
        if "cueva" in tipo:
            jugador_atacante["cuevas_derrotadas"] = int(jugador_atacante.get("cuevas_derrotadas", 0) or 0) + 1
        elif "dios" in tipo:
            jugador_atacante["dioses_abatidos"] = int(jugador_atacante.get("dioses_abatidos", 0) or 0) + 1
