"""
backend/systems/combat.py
Eternal Warriors v3.0 — Sistema de combate

Mecánica de ronda:
  1. Se compara la mayor DST viva de cada bando
  2. El de mayor DST golpea primero en cascada sobre el ejército contrario
     (cada subgrupo de ese DST con su propio PA, independientemente)
  3. Empate DST → mayor cantidad total en ese DST; persiste → ATK tiene prioridad
  4. Luego el otro bando golpea si queda algo vivo
  5. Máximo 9 rondas

Cascada:
  - PA nunca se agota ni reduce
  - bajas = floor((PA_atacante - CA_objetivo) * cantidad_atacante / HP_objetivo)
  - Si PA <= CA → sin daño, salta al siguiente objetivo en DST
  - Si mata a todos → continúa con PA completo al siguiente objetivo (mayor DST del enemigo)
  - Si sobrevive alguno → cascada se detiene para ese subgrupo

Multi-jugador:
  - Cada bando puede tener unidades de varios jugadores
  - XP total del bando se divide en partes iguales entre jugadores del bando

Muralla:
  - PA total del bando ATK vs HP muralla
  - Si PA_total <= HP_muralla → derrota instantánea
  - Si PA_total > HP_muralla → atravesada, combate normal

KarlakÁ:
  - ×100.000 en HP/PA/CA si atacado por >1 unidad o non-EON_SUPREMO

Saqueo:
  - Solo si victoria ATK
  - Capacidad = suma CARGA de sobrevivientes ATK
  - Orden: ORO → HIERRO → CARBON → PIEDRA → MADERA → MANA
  - Escondite intocable; recursos infinitos (almacén Nv50) no saqueables
"""

import csv
from backend.data.save_manager import safe_resource_float as _srf
import math
import unicodedata
from pathlib import Path

CSV_DIR = Path(__file__).parent.parent.parent / "csv"

# ── Normalización ─────────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    """Normaliza tildes, mayúsculas y guiones bajos: Eón_Supremo → EON SUPREMO."""
    s = str(s).replace("_", " ")
    return "".join(
        c for c in unicodedata.normalize("NFD", s.upper())
        if unicodedata.category(c) != "Mn"
    )

def _safe_float(v: str) -> float:
    """Parser robusto: notación europea (coma decimal), typos como 5,,0167."""
    v = str(v).strip().replace(",,", ".").replace(",", ".")
    try:
        return float(v)
    except ValueError:
        return 0.0

# ── Sets de clasificación ─────────────────────────────────────────────────────

UNIDADES_BASICAS = {
    "ALDEANO", "EXPLORADOR", "SACERDOTE", "GUERRERO", "COMANDO",
    "MERCENARIO", "MARINE", "CYBORG", "MAGO", "METAHUMANO",
}

INVOCACIONES = {
    "DEMONIO", "ANIMA", "ESPECTRO", "GOLEM", "CENTAURO", "KRAKEN",
    "ALONARDO", "MADRESELVA", "COLOSO", "FENIX", "DRAGON DE ORO",
    "CABALLERO DE LUZ", "ALALAIA", "EON SUPREMO",
}

ORDEN_SAQUEO = ["ORO", "HIERRO", "CARBON", "PIEDRA", "MADERA", "MANA"]

# ── Loaders CSV (cache de módulo) ─────────────────────────────────────────────

_UNIDADES_STATS:  dict | None = None
_INVOC_STATS:     dict | None = None
_MURALLA_HP:      dict | None = None
_XP_UNIDADES:     dict | None = None
_XP_INVOCACIONES: dict | None = None
_ESCONDITE_CAPS:  dict | None = None


def _load_unidades_stats() -> dict:
    path = CSV_DIR / "caracteristicas_unidades.csv"
    result = {}
    if not path.exists():
        return result
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        for row in reader:
            if len(row) < 9:
                continue
            nombre = _norm(row[0])
            try:
                nivel = int(row[1].strip())
                if nombre not in result:
                    result[nombre] = {}
                result[nombre][nivel] = {
                    "hp":       _safe_float(row[2]),
                    "pa":       _safe_float(row[3]),
                    "ca":       _safe_float(row[4]),
                    "carga":    _safe_float(row[5]),
                    "destreza": _safe_float(row[6]),
                    "velocidad":_safe_float(row[7]),
                    "sigilo":   _safe_float(row[8]),
                }
            except (ValueError, IndexError):
                pass
    return result


def _load_invoc_stats() -> dict:
    path = CSV_DIR / "caracteristicas_invocaciones.csv"
    result = {}
    if not path.exists():
        return result
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        for row in reader:
            if len(row) < 7:
                continue
            nombre = _norm(row[0])
            result[nombre] = {
                "hp":       _safe_float(row[1]),
                "pa":       _safe_float(row[2]),
                "ca":       _safe_float(row[3]),
                "destreza": _safe_float(row[4]),
                "sigilo":   _safe_float(row[5]),
                "velocidad":_safe_float(row[6]),
                "carga":    0.0,
            }
    return result


def _load_muralla_hp() -> dict:
    path = CSV_DIR / "edificio3_muralla.csv"
    result = {}
    if not path.exists():
        return result
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        for row in reader:
            if not row or not row[0].strip().isdigit():
                continue
            nivel = int(row[0].strip())
            try:
                result[nivel] = _safe_float(row[6])
            except IndexError:
                pass
    return result


def _load_xp_unidades() -> dict:
    path = CSV_DIR / "experiencia_dada_por_unidades_basicas_por_nivel.csv"
    result = {}
    if not path.exists():
        return result
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        for row in reader:
            if len(row) < 3:
                continue
            nombre = _norm(row[0])
            try:
                nivel = int(row[1].strip())
                if nombre not in result:
                    result[nombre] = {}
                result[nombre][nivel] = _safe_float(row[2])
            except (ValueError, IndexError):
                pass
    return result


def _load_xp_invocaciones() -> dict:
    path = CSV_DIR / "experiencia_por_invocaciones.csv"
    result = {}
    if not path.exists():
        return result
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        for row in reader:
            if len(row) < 2:
                continue
            nombre = _norm(row[0])
            try:
                result[nombre] = _safe_float(row[1])
            except (ValueError, IndexError):
                pass
    return result


def _load_escondite_caps() -> dict:
    path = CSV_DIR / "edificio6_escondite.csv"
    result = {}
    if not path.exists():
        return result
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        for row in reader:
            if not row or not row[0].strip().isdigit():
                continue
            nivel = int(row[0].strip())
            try:
                result[nivel] = {
                    "cap_material": _safe_float(row[7].strip().replace(",", "")),
                }
            except IndexError:
                pass
    return result


def _get_unidades():
    global _UNIDADES_STATS
    if _UNIDADES_STATS is None:
        _UNIDADES_STATS = _load_unidades_stats()
    return _UNIDADES_STATS

def _get_invocs():
    global _INVOC_STATS
    if _INVOC_STATS is None:
        _INVOC_STATS = _load_invoc_stats()
    return _INVOC_STATS

def _get_muralla():
    global _MURALLA_HP
    if _MURALLA_HP is None:
        _MURALLA_HP = _load_muralla_hp()
    return _MURALLA_HP

def _get_xp_unidades():
    global _XP_UNIDADES
    if _XP_UNIDADES is None:
        _XP_UNIDADES = _load_xp_unidades()
    return _XP_UNIDADES

def _get_xp_invocs():
    global _XP_INVOCACIONES
    if _XP_INVOCACIONES is None:
        _XP_INVOCACIONES = _load_xp_invocaciones()
    return _XP_INVOCACIONES

def _get_escondite_caps():
    global _ESCONDITE_CAPS
    if _ESCONDITE_CAPS is None:
        _ESCONDITE_CAPS = _load_escondite_caps()
    return _ESCONDITE_CAPS

# ── Stats públicos ────────────────────────────────────────────────────────────

def get_stats_unidad(nombre: str, nivel: int) -> dict:
    db  = _get_unidades()
    key = _norm(nombre)
    niveles = db.get(key, {})
    max_nv  = max(niveles.keys()) if niveles else 1
    return niveles.get(nivel, niveles.get(max_nv,
           {"hp":1,"pa":1,"ca":1,"destreza":1,"sigilo":1,"carga":0,"velocidad":1}))

def get_stats_invocacion(nombre: str) -> dict:
    db  = _get_invocs()
    key = _norm(nombre)
    return db.get(key, {"hp":1,"pa":1,"ca":1,"destreza":1,"sigilo":1,"carga":0,"velocidad":1})

def get_xp_unidad(nombre: str, nivel: int) -> float:
    db  = _get_xp_unidades()
    key = _norm(nombre)
    niveles = db.get(key, {})
    max_nv  = max(niveles.keys()) if niveles else 1
    return niveles.get(nivel, niveles.get(max_nv, 0))

def get_xp_invocacion(nombre: str) -> float:
    return _get_xp_invocs().get(_norm(nombre), 0)

# ── Construcción de grupos ────────────────────────────────────────────────────

def _build_grupos(
    unidades_dict: dict,
    nivel_tropas: int,
    bonus_herreria: dict = None,
    jugador: str = None,
) -> list[dict]:
    """
    Construye lista de grupos desde un dict {NOMBRE: cantidad}.
    Cada grupo: {nombre, cantidad, hp_unit, pa_unit, ca_unit, destreza,
                 sigilo, carga, es_invocacion, jugador}
    bonus_herreria: {pa_bonus, ca_bonus, hp_bonus}
    """
    if not bonus_herreria:
        bonus_herreria = {"pa_bonus": 0, "ca_bonus": 0, "hp_bonus": 0}
    else:
        bonus_herreria = {
            "pa_bonus": bonus_herreria.get("pa_bonus", 0),
            "ca_bonus": bonus_herreria.get("ca_bonus", 0),
            "hp_bonus": bonus_herreria.get("hp_bonus", 0),
        }

    grupos = []
    for nombre_raw, cantidad in unidades_dict.items():
        cantidad = int(cantidad or 0)
        if cantidad <= 0:
            continue
        nombre = _norm(nombre_raw)
        es_inv = nombre in INVOCACIONES or nombre == "KARLAKA"

        if es_inv:
            st = get_stats_invocacion(nombre)
        else:
            st = get_stats_unidad(nombre, nivel_tropas)

        grupos.append({
            "nombre":        nombre,
            "cantidad":      cantidad,
            "hp_unit":       st["hp"]       + bonus_herreria["hp_bonus"],
            "pa_unit":       st["pa"]       + bonus_herreria["pa_bonus"],
            "ca_unit":       st["ca"]       + bonus_herreria["ca_bonus"],
            "destreza":      st["destreza"],
            "sigilo":        st.get("sigilo", 1),
            "carga":         st.get("carga", 0),
            "es_invocacion": es_inv,
            "jugador":       jugador or "?",
        })
    return grupos


def _aplicar_karlaka(grupos: list[dict], atacantes: dict) -> None:
    """
    Si KarlakÁ está en los grupos defensores, aplica ×100.000
    si el atacante tiene >1 unidad o alguna non-EON SUPREMO.
    Modifica in-place.
    """
    for g in grupos:
        if g["nombre"] != "KARLAKA":
            continue
        total_atk  = sum(int(v or 0) for v in atacantes.values())
        nombres_atk = {_norm(k) for k, v in atacantes.items() if int(v or 0) > 0}
        solo_eon   = nombres_atk <= {"EON SUPREMO"}
        if total_atk > 1 or not solo_eon:
            mult = 100_000
            g["hp_unit"] *= mult
            g["pa_unit"] *= mult
            g["ca_unit"] *= mult

# ── Núcleo de combate ─────────────────────────────────────────────────────────

def _mayor_dst_viva(grupos: list[dict]) -> float:
    """Retorna la mayor destreza entre grupos con cantidad > 0."""
    vivos = [g["destreza"] for g in grupos if g["cantidad"] > 0]
    return max(vivos) if vivos else -1


def _subgrupos_de_dst(grupos: list[dict], dst: float) -> list[dict]:
    """Retorna grupos vivos con exactamente esa destreza."""
    return [g for g in grupos if g["cantidad"] > 0 and g["destreza"] == dst]


def _cantidad_total_dst(grupos: list[dict], dst: float) -> int:
    """Cuenta unidades totales vivas de una destreza."""
    return sum(g["cantidad"] for g in grupos if g["destreza"] == dst and g["cantidad"] > 0)


def _cascada_grupo(atacante: dict, enemigos_ordenados: list[dict], nivel_tropas_def: int, log: list) -> float:
    """
    Un subgrupo atacante (un nombre/jugador) golpea en cascada al ejército enemigo.
    enemigos_ordenados: lista de grupos del bando contrario, ordenada DST DESC.
    Retorna XP generada.
    """
    pa_unit  = atacante["pa_unit"]
    cant_atk = atacante["cantidad"]
    xp       = 0.0

    for obj in enemigos_ordenados:
        if obj["cantidad"] <= 0:
            continue
        dano_neto = pa_unit - obj["ca_unit"]
        if dano_neto <= 0:
            # No puede dañar — salta al siguiente
            continue
        bajas = min(obj["cantidad"], math.floor(dano_neto * cant_atk / max(obj["hp_unit"], 1)))
        if bajas > 0:
            xp_unit = (get_xp_invocacion(obj["nombre"])
                       if obj["es_invocacion"]
                       else get_xp_unidad(obj["nombre"], nivel_tropas_def))
            xp += bajas * xp_unit
            obj["cantidad"] -= bajas
            log.append(
                f"    {atacante['nombre']}(jug={atacante['jugador']} "
                f"dst={atacante['destreza']:.0f} ×{cant_atk:,})"
                f" → -{bajas:,}×{obj['nombre']}(dst={obj['destreza']:.0f})"
                f" [PA={pa_unit:.3e} CA={obj['ca_unit']:.3e} HP={obj['hp_unit']:.3e}]"
            )
        if obj["cantidad"] > 0:
            # Sobrevive → cascada se detiene para este atacante
            break
        # Eliminado → sigue cascada con PA completo

    return xp


def _ejecutar_golpe_bloque(
    bloque: list[dict],
    enemigos: list[dict],
    nivel_tropas_def: int,
    log: list,
) -> float:
    """
    Ejecuta el golpe de todos los subgrupos del bloque (misma DST) sobre el ejército enemigo.
    Cada subgrupo hace su cascada independientemente con su propio PA.
    enemigos ya ordenados DST DESC.
    Retorna XP total generada.
    """
    # Ordenar subgrupos del bloque: mayor cantidad primero (desempate interno)
    bloque_ord = sorted(bloque, key=lambda g: -g["cantidad"])
    xp_total = 0.0
    for sub in bloque_ord:
        if not any(g["cantidad"] > 0 for g in enemigos):
            break
        xp_total += _cascada_grupo(sub, enemigos, nivel_tropas_def, log)
    return xp_total


def _resolver_ronda(
    atk_grupos: list[dict],
    def_grupos: list[dict],
    nivel_tropas_atk: int,
    nivel_tropas_def: int,
    ronda: int,
    log: list,
) -> tuple[float, float]:
    """
    Resuelve una ronda completa.
    Retorna (xp_generada_para_atk, xp_generada_para_def).
    """
    xp_atk = 0.0
    xp_def = 0.0

    log.append(f"  --- Ronda {ronda} ---")

    # Ordenar ambos ejércitos DST DESC al inicio de la ronda
    atk_grupos.sort(key=lambda g: (-g["destreza"], -g["cantidad"]))
    def_grupos.sort(key=lambda g: (-g["destreza"], -g["cantidad"]))

    # Alternar golpes hasta que ambos hayan actuado o un bando quede en cero
    atk_actuado = False
    def_actuado  = False

    while True:
        dst_atk = _mayor_dst_viva(atk_grupos)
        dst_def  = _mayor_dst_viva(def_grupos)

        if dst_atk < 0 or dst_def < 0:
            break
        if atk_actuado and def_actuado:
            break

        # Decidir quién actúa ahora
        if dst_atk > dst_def:
            if atk_actuado:
                break
            # ATK golpea
            bloque = _subgrupos_de_dst(atk_grupos, dst_atk)
            def_ord = sorted([g for g in def_grupos if g["cantidad"] > 0],
                             key=lambda g: (-g["destreza"], -g["cantidad"]))
            log.append(f"  ATK golpea (DST={dst_atk:.0f} × {_cantidad_total_dst(atk_grupos, dst_atk):,} unidades):")
            xp_atk += _ejecutar_golpe_bloque(bloque, def_ord, nivel_tropas_def, log)
            atk_actuado = True
            # Continuar para dar turno a DEF si aún no ha actuado

        elif dst_def > dst_atk:
            if def_actuado:
                # DEF ya actuó — ahora le toca a ATK si no ha actuado
                if not atk_actuado:
                    bloque = _subgrupos_de_dst(atk_grupos, dst_atk)
                    def_ord = sorted([g for g in def_grupos if g["cantidad"] > 0],
                                     key=lambda g: (-g["destreza"], -g["cantidad"]))
                    log.append(f"  ATK golpea (DST={dst_atk:.0f} × {_cantidad_total_dst(atk_grupos, dst_atk):,} unidades):")
                    xp_atk += _ejecutar_golpe_bloque(bloque, def_ord, nivel_tropas_def, log)
                    atk_actuado = True
                break
            # DEF golpea primero (mayor DST)
            bloque = _subgrupos_de_dst(def_grupos, dst_def)
            atk_ord = sorted([g for g in atk_grupos if g["cantidad"] > 0],
                             key=lambda g: (-g["destreza"], -g["cantidad"]))
            log.append(f"  DEF golpea (DST={dst_def:.0f} × {_cantidad_total_dst(def_grupos, dst_def):,} unidades):")
            xp_def += _ejecutar_golpe_bloque(bloque, atk_ord, nivel_tropas_atk, log)
            def_actuado = True

        else:
            # Empate de DST — comparar cantidad total
            cnt_atk = _cantidad_total_dst(atk_grupos, dst_atk)
            cnt_def  = _cantidad_total_dst(def_grupos, dst_def)

            # Quién golpea primero
            if cnt_atk >= cnt_def:
                primero, seg = "ATK", "DEF"
            else:
                primero, seg = "DEF", "ATK"

            for turno in [primero, seg]:
                if turno == "ATK" and not atk_actuado:
                    bloque = _subgrupos_de_dst(atk_grupos, dst_atk)
                    def_ord = sorted([g for g in def_grupos if g["cantidad"] > 0],
                                     key=lambda g: (-g["destreza"], -g["cantidad"]))
                    log.append(f"  ATK golpea (DST={dst_atk:.0f} × {cnt_atk:,} unidades) [empate→ATK prio]:")
                    xp_atk += _ejecutar_golpe_bloque(bloque, def_ord, nivel_tropas_def, log)
                    atk_actuado = True
                elif turno == "DEF" and not def_actuado:
                    bloque = _subgrupos_de_dst(def_grupos, dst_def)
                    atk_ord = sorted([g for g in atk_grupos if g["cantidad"] > 0],
                                     key=lambda g: (-g["destreza"], -g["cantidad"]))
                    log.append(f"  DEF golpea (DST={dst_def:.0f} × {cnt_def:,} unidades):")
                    xp_def += _ejecutar_golpe_bloque(bloque, atk_ord, nivel_tropas_atk, log)
                    def_actuado = True
            break

    return xp_atk, xp_def

# ── Saqueo ────────────────────────────────────────────────────────────────────

def _calcular_saqueo(atk_grupos_vivos: list[dict], defensor_city: dict) -> dict:
    capacidad = sum(g["carga"] * g["cantidad"] for g in atk_grupos_vivos if g["cantidad"] > 0)
    if capacidad <= 0:
        return {}

    # Solo sacerdotes pueden transportar maná
    hay_sacerdotes = any(
        g["nombre"] == "SACERDOTE" and g["cantidad"] > 0
        for g in atk_grupos_vivos
    )

    nivel_esc = int(defensor_city.get("ESCONDITE", 0) or 0)
    esc_caps  = _get_escondite_caps()
    max_esc   = max(esc_caps.keys()) if esc_caps else 1
    cap_prot  = esc_caps.get(nivel_esc, esc_caps.get(max_esc, {})).get("cap_material", 0)
    mat_esc   = defensor_city.get("ESCONDITE_DATA", {}).get("materiales", {})

    almacen_inf   = int(defensor_city.get("ALMACEN", 0) or 0) >= 50
    santuario_inf = int(defensor_city.get("SANTUARIO_ARCANO", 0) or 0) >= 50

    saqueo    = {}
    restante  = capacidad

    for recurso in ORDEN_SAQUEO:
        if restante <= 0:
            break
        if recurso == "MANA" and (santuario_inf or not hay_sacerdotes):
            continue
        if recurso != "MANA" and almacen_inf:
            continue
        total    = float(defensor_city.get(recurso, 0) or 0)
        prot     = float(mat_esc.get(recurso, 0))
        saqueble = max(0.0, total - prot)
        tomado   = min(saqueble, restante)
        if tomado > 0:
            saqueo[recurso] = tomado
            restante -= tomado

    return saqueo

# ── API pública principal ─────────────────────────────────────────────────────

def resolver_combate(
    atacantes: list[dict],
    defensores: list[dict],
    defensor_city: dict,
    nivel_muralla: int = 0,
) -> dict:
    """
    Resuelve un combate completo entre dos bandos multi-jugador.

    Parámetros:
        atacantes: lista de {
            "jugador": str,
            "unidades": {NOMBRE: cantidad},
            "nivel_tropas": int,
            "bonus_herreria": {pa_bonus, ca_bonus, hp_bonus},  # opcional
        }
        defensores: lista de {
            "jugador": str,
            "unidades": {NOMBRE: cantidad},
            "nivel_tropas": int,
            "bonus_herreria": {pa_bonus, ca_bonus, hp_bonus},  # opcional
        }
        defensor_city: dict ciudad del defensor (para muralla, saqueo, escondite)
        nivel_muralla: int nivel de la muralla defensora

    Retorna:
        {
            "victoria_atacante": bool,
            "mensaje": str,
            "rondas": int,
            "log": [str],
            "iniciales_atk": {jugador: {nombre: cantidad}},
            "iniciales_def": {jugador: {nombre: cantidad}},
            "sobrevivientes_atk": {jugador: {nombre: cantidad}},
            "sobrevivientes_def": {jugador: {nombre: cantidad}},
            "bajas_atk": {jugador: {nombre: cantidad}},
            "bajas_def": {jugador: {nombre: cantidad}},
            "xp_por_jugador_atk": {jugador: float},
            "xp_por_jugador_def": {jugador: float},
            "saqueo": {recurso: cantidad},
            "muralla_atravesada": bool,
        }
    """
    log = []

    # ── Guardar iniciales ─────────────────────────────────────────────────────
    iniciales_atk = {p["jugador"]: {k: int(v or 0) for k, v in p["unidades"].items() if int(v or 0) > 0}
                     for p in atacantes}
    iniciales_def = {p["jugador"]: {k: int(v or 0) for k, v in p["unidades"].items() if int(v or 0) > 0}
                     for p in defensores}

    # ── Construir grupos ──────────────────────────────────────────────────────
    atk_grupos = []
    for p in atacantes:
        atk_grupos += _build_grupos(
            p["unidades"], p["nivel_tropas"],
            p.get("bonus_herreria"), p["jugador"]
        )

    def_grupos = []
    for p in defensores:
        def_grupos += _build_grupos(
            p["unidades"], p["nivel_tropas"],
            p.get("bonus_herreria"), p["jugador"]
        )

    # KarlakÁ
    todas_unidades_atk = {}
    for p in atacantes:
        todas_unidades_atk.update(p["unidades"])
    _aplicar_karlaka(def_grupos, todas_unidades_atk)

    # ── Fase muralla ──────────────────────────────────────────────────────────
    # La muralla es un pseudo-grupo defensor con destreza infinita (siempre al frente).
    # PA=0, CA=0: no ataca ni absorbe. El sobrante de daño que la destruye
    # continúa en cascada hacia las tropas defensoras, igual que cualquier grupo.
    muralla_atravesada = False
    if nivel_muralla > 0:
        muralla_db = _get_muralla()
        max_nv     = max(muralla_db.keys()) if muralla_db else 1
        hp_muralla = muralla_db.get(nivel_muralla, muralla_db.get(max_nv, 0))
        if hp_muralla > 0:
            muralla_grupo = {
                "nombre":        "MURALLA",
                "cantidad":      1,
                "hp_unit":       float(hp_muralla),
                "pa_unit":       0.0,
                "ca_unit":       0.0,
                "destreza":      float("inf"),
                "sigilo":        0,
                "carga":         0,
                "es_invocacion": False,
                "jugador":       "DEFENSA",
            }
            def_grupos.insert(0, muralla_grupo)
            log.append(f"Muralla Nv{nivel_muralla} HP={hp_muralla:.4e} — insertada al frente del DEF")

    # ── Niveles de tropas por bando (para XP) ────────────────────────────────
    # Usamos el nivel del primer jugador de cada bando como referencia para calcular XP
    # (las bajas son del bando contrario, su nivel ya está en sus grupos)
    nivel_tropas_atk = atacantes[0]["nivel_tropas"] if atacantes else 1
    nivel_tropas_def = defensores[0]["nivel_tropas"] if defensores else 1

    # ── Rondas ────────────────────────────────────────────────────────────────
    xp_total_atk = 0.0
    xp_total_def = 0.0
    rondas = 0

    for r in range(1, 10):
        atk_vivos = any(g["cantidad"] > 0 for g in atk_grupos)
        def_vivos  = any(g["cantidad"] > 0 for g in def_grupos)
        if not atk_vivos or not def_vivos:
            break
        rondas = r
        xp_r_atk, xp_r_def = _resolver_ronda(
            atk_grupos, def_grupos,
            nivel_tropas_atk, nivel_tropas_def,
            r, log
        )
        xp_total_atk += xp_r_atk
        xp_total_def += xp_r_def

    # ── Muralla atravesada — verificar post-rondas ───────────────────────────
    muralla_grupo_ref = next((g for g in def_grupos if g["nombre"] == "MURALLA"), None)
    if muralla_grupo_ref is not None:
        muralla_atravesada = muralla_grupo_ref["cantidad"] <= 0
        if not muralla_atravesada:
            # Atacante no derribó la muralla — derrota garantizada
            atk_vivos_check = any(g["cantidad"] > 0 for g in atk_grupos)
            if not atk_vivos_check:
                log.append("El atacante no consiguió traspasar la muralla y murió")
            else:
                log.append("El atacante no consiguió traspasar la muralla y murió")
            return _resultado_derrota_muralla(iniciales_atk, iniciales_def, log)
        # Excluir la muralla del cómputo de def_vivos (ya está destruida)
        def_grupos = [g for g in def_grupos if g["nombre"] != "MURALLA"]

    # ── Victoria ──────────────────────────────────────────────────────────────
    atk_vivos = any(g["cantidad"] > 0 for g in atk_grupos)
    def_vivos  = any(g["cantidad"] > 0 for g in def_grupos)

    if atk_vivos and not def_vivos:
        victoria = True
        mensaje  = "Victoria del atacante"
    elif def_vivos and not atk_vivos:
        victoria = False
        mensaje  = "Victoria del defensor"
    else:
        # Ambos sobreviven 9 rondas → quien generó más XP gana
        if xp_total_atk >= xp_total_def:
            victoria = True
            mensaje  = f"Victoria por puntos (XP atk={xp_total_atk:.3e} vs def={xp_total_def:.3e})"
        else:
            victoria = False
            mensaje  = f"Derrota por puntos (XP atk={xp_total_atk:.3e} vs def={xp_total_def:.3e})"

    log.append(mensaje)

    # ── Sobrevivientes y bajas ────────────────────────────────────────────────
    sobrev_atk = _grupos_a_dict_por_jugador(atk_grupos)
    sobrev_def  = _grupos_a_dict_por_jugador(def_grupos)
    bajas_atk  = _calcular_bajas(iniciales_atk, sobrev_atk)
    bajas_def   = _calcular_bajas(iniciales_def, sobrev_def)

    # ── XP dividida en partes iguales por jugador ─────────────────────────────
    n_jug_atk = len(atacantes)
    n_jug_def = len(defensores)
    xp_jug_atk = {p["jugador"]: xp_total_atk / n_jug_atk for p in atacantes}
    xp_jug_def = {p["jugador"]: xp_total_def / n_jug_def for p in defensores}

    # ── Saqueo ────────────────────────────────────────────────────────────────
    saqueo = {}
    if victoria:
        saqueo = _calcular_saqueo([g for g in atk_grupos if g["cantidad"] > 0], defensor_city)

    return {
        "victoria_atacante":  victoria,
        "mensaje":            mensaje,
        "rondas":             rondas,
        "log":                log,
        "iniciales_atk":      iniciales_atk,
        "iniciales_def":      iniciales_def,
        "sobrevivientes_atk": sobrev_atk,
        "sobrevivientes_def": sobrev_def,
        "bajas_atk":          bajas_atk,
        "bajas_def":          bajas_def,
        "xp_por_jugador_atk": xp_jug_atk,
        "xp_por_jugador_def": xp_jug_def,
        "saqueo":             saqueo,
        "muralla_atravesada": muralla_atravesada,
        "tipo_victoria":      "combate" if victoria else None,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _resultado_derrota_muralla(iniciales_atk, iniciales_def, log) -> dict:
    return {
        "victoria_atacante":  False,
        "mensaje":            "El atacante no consiguió traspasar la muralla y murió",
        "rondas":             0,
        "log":                log,
        "iniciales_atk":      iniciales_atk,
        "iniciales_def":      iniciales_def,
        "sobrevivientes_atk": {},
        "sobrevivientes_def": iniciales_def,
        "bajas_atk":          iniciales_atk,
        "bajas_def":          {},
        "xp_por_jugador_atk": {j: 0.0 for j in iniciales_atk},
        "xp_por_jugador_def": {j: 0.0 for j in iniciales_def},
        "saqueo":             {},
        "muralla_atravesada": False,
    }


def _grupos_a_dict_por_jugador(grupos: list[dict]) -> dict:
    """Convierte lista de grupos a {jugador: {nombre: cantidad}}."""
    result = {}
    for g in grupos:
        if g["cantidad"] <= 0:
            continue
        jug = g["jugador"]
        if jug not in result:
            result[jug] = {}
        result[jug][g["nombre"]] = result[jug].get(g["nombre"], 0) + g["cantidad"]
    return result


def _calcular_bajas(iniciales: dict, sobrevivientes: dict) -> dict:
    """Calcula bajas = iniciales - sobrevivientes por jugador."""
    bajas = {}
    for jug, unidades in iniciales.items():
        bajas[jug] = {}
        sobrev = sobrevivientes.get(jug, {})
        for nombre, cnt in unidades.items():
            b = cnt - sobrev.get(nombre, 0)
            if b > 0:
                bajas[jug][nombre] = b
    return bajas


# ── Sigilo ────────────────────────────────────────────────────────────────────

_SIGILO_FACTOR_APORTE = 3.0   # cada unidad que aporta suma este valor al sigilo del grupo
_SIGILO_UMBRAL_PCT    = 0.5   # unidad aporta si su sigilo >= sigilo_max * este porcentaje
_SIGILO_TOPE          = 200.0 # tope máximo de sigilo efectivo


def _calcular_sigilo_efectivo(sigilos: list) -> float:
    """
    Nueva fórmula de sigilo de grupo:
      - Base: sigilo de la unidad con mayor sigilo (sigilo_max)
      - Por cada unidad adicional:
          si sigilo_unidad >= sigilo_max * 0.5 → +3.0 (aporta)
          si sigilo_unidad <  sigilo_max * 0.5 → -1.0 (resta)
      - Tope máximo: 200
    sigilos: lista de valores de sigilo, una entrada por unidad (repetida por cantidad)
    """
    if not sigilos:
        return 0.0
    sigilo_max = max(sigilos)
    umbral     = sigilo_max * _SIGILO_UMBRAL_PCT
    efectivo   = float(sigilo_max)
    for s in sigilos[1:]:   # primera ya es el base (sigilo_max)
        if s >= umbral:
            efectivo += _SIGILO_FACTOR_APORTE
        else:
            efectivo -= 1.0
    return max(0.0, min(_SIGILO_TOPE, efectivo))


def calcular_sigilo(unidades_dict: dict, nivel_tropas: int) -> float:
    """
    Calcula sigilo efectivo de un pelotón de un solo propietario.
    """
    sigilos = []
    for nombre_raw, cantidad in unidades_dict.items():
        cantidad = int(cantidad or 0)
        if cantidad <= 0:
            continue
        nombre = _norm(nombre_raw)
        if nombre in INVOCACIONES:
            st = get_stats_invocacion(nombre)
        else:
            st = get_stats_unidad(nombre, nivel_tropas)
        sigilos.extend([st["sigilo"]] * cantidad)
    return _calcular_sigilo_efectivo(sigilos)


def calcular_sigilo_grupo(grupos: list) -> float:
    """
    Calcula sigilo efectivo de un pelotón con múltiples propietarios.
    grupos: [{"unidades": {nombre: cant}, "nivel_tropas": int}, ...]
    Usa la nueva fórmula con factor de aporte por unidad.
    """
    sigilos = []
    for grupo in grupos:
        nivel = grupo.get("nivel_tropas", 1)
        for nombre_raw, cantidad in grupo.get("unidades", {}).items():
            cantidad = int(cantidad or 0)
            if cantidad <= 0:
                continue
            nombre = _norm(nombre_raw)
            if nombre in INVOCACIONES:
                st = get_stats_invocacion(nombre)
            else:
                st = get_stats_unidad(nombre, nivel)
            sigilos.extend([st["sigilo"]] * cantidad)
    return _calcular_sigilo_efectivo(sigilos)


# ── Combate vs entidad del mundo (Cueva / Dios / KarlakÁ) ────────────────────

def resolver_combate_entidad(
    atacante: dict,
    entidad: dict,
) -> dict:
    """
    Combate contra una entidad del mundo (Cueva, Dios, KarlakÁ).

    atacante: {
        "jugador": str,
        "unidades": {NOMBRE: cantidad},
        "nivel_tropas": int,
        "bonus_herreria": dict,
    }
    entidad: {nombre, tipo, hp, pa, ca, destreza, experiencia}

    Retorna mismo formato que resolver_combate (bando DEF = la entidad).
    """
    log = []
    nombre_ent = entidad.get("nombre", "Entidad")
    tipo_ent   = entidad.get("tipo", "")

    ent_hp  = float(entidad.get("hp",  1))
    ent_pa  = float(entidad.get("pa",  1))
    ent_ca  = float(entidad.get("ca",  1))
    ent_dst = float(entidad.get("destreza", 1))
    ent_xp  = float(entidad.get("experiencia", 0))

    # KarlakÁ
    if _norm(tipo_ent) == "KARLAKA" or _norm(nombre_ent) == "KARLAKA":
        todas = atacante["unidades"]
        total = sum(int(v or 0) for v in todas.values())
        nombres = {_norm(k) for k, v in todas.items() if int(v or 0) > 0}
        solo_eon = nombres <= {"EON SUPREMO"}
        if total > 1 or not solo_eon:
            mult = 100_000
            ent_hp *= mult; ent_pa *= mult; ent_ca *= mult
            log.append(f"[KarlakÁ] ×{mult:,} activado")

    atk_grupos = _build_grupos(
        atacante["unidades"], atacante["nivel_tropas"],
        atacante.get("bonus_herreria"), atacante["jugador"]
    )
    nivel_tropas = atacante["nivel_tropas"]
    iniciales_atk = {atacante["jugador"]: {k: int(v or 0) for k, v in atacante["unidades"].items() if int(v or 0) > 0}}

    # Entidad como pseudo-grupo
    ent_grupo = {
        "nombre": _norm(nombre_ent), "cantidad": 1,
        "hp_unit": ent_hp, "pa_unit": ent_pa, "ca_unit": ent_ca,
        "destreza": ent_dst, "sigilo": 1, "carga": 0,
        "es_invocacion": False, "jugador": "MUNDO",
    }

    xp_atk = 0.0
    xp_def = 0.0
    rondas = 0

    for r in range(1, 10):
        atk_vivos = any(g["cantidad"] > 0 for g in atk_grupos)
        if not atk_vivos or ent_grupo["cantidad"] <= 0:
            break
        rondas = r
        log.append(f"  --- Ronda {r} ---")

        # Determinar quién tiene mayor DST
        dst_atk = _mayor_dst_viva(atk_grupos)
        dst_ent = ent_dst

        def golpe_atk():
            nonlocal xp_atk
            bloque = _subgrupos_de_dst(atk_grupos, dst_atk)
            log.append(f"  ATK golpea a {nombre_ent} (DST={dst_atk:.0f}):")
            for sub in sorted(bloque, key=lambda g: -g["cantidad"]):
                dano = sub["pa_unit"] - ent_grupo["ca_unit"]
                if dano <= 0:
                    log.append(f"    {sub['nombre']}×{sub['cantidad']:,}: PA≤CA — sin daño")
                    continue
                # Entidad tiene HP acumulado (no es por unidad sino total)
                dano_total = dano * sub["cantidad"]
                if dano_total >= ent_grupo["hp_unit"]:
                    log.append(f"    {sub['nombre']}×{sub['cantidad']:,}: daño={dano_total:.3e} ≥ HP={ent_grupo['hp_unit']:.3e} → {nombre_ent} DERROTADO")
                    ent_grupo["cantidad"] = 0
                    xp_atk += ent_xp
                else:
                    ent_grupo["hp_unit"] -= dano_total
                    log.append(f"    {sub['nombre']}×{sub['cantidad']:,}: daño={dano_total:.3e} | HP restante={ent_grupo['hp_unit']:.3e}")

        def golpe_ent():
            nonlocal xp_def
            atk_ord = sorted([g for g in atk_grupos if g["cantidad"] > 0],
                             key=lambda g: (-g["destreza"], -g["cantidad"]))
            log.append(f"  {nombre_ent} golpea al ATK:")
            xp_def += _cascada_grupo(ent_grupo, atk_ord, nivel_tropas, log)
            atk_grupos[:] = [g for g in atk_grupos if g["cantidad"] > 0]

        if dst_atk > dst_ent:
            golpe_atk()
            if ent_grupo["cantidad"] > 0:
                golpe_ent()
        elif dst_ent > dst_atk:
            golpe_ent()
            if any(g["cantidad"] > 0 for g in atk_grupos):
                golpe_atk()
        else:
            # Empate DST
            cnt_atk = _cantidad_total_dst(atk_grupos, dst_atk)
            if cnt_atk >= 1:  # ATK tiene prioridad en empate total
                golpe_atk()
                if ent_grupo["cantidad"] > 0:
                    golpe_ent()
            else:
                golpe_ent()
                if any(g["cantidad"] > 0 for g in atk_grupos):
                    golpe_atk()

    # ── Determinar tipo de victoria ──────────────────────────────────────────
    atk_sobrev = any(g["cantidad"] > 0 for g in atk_grupos)
    ent_muerta = ent_grupo["cantidad"] <= 0

    if ent_muerta:
        tipo_victoria = "combate"
        victoria      = True
        mensaje       = f"Victoria en combate: {nombre_ent} derrotado"
    elif atk_sobrev and rondas >= 9:
        # Verificar victoria por valor: ≥80% aldeanos y ≥90% mil+invoc del total enviado
        total_ald_ini  = sum(v for k, v in iniciales_atk.get(atacante["jugador"], {}).items() if _norm(k) == "ALDEANO")
        total_mil_ini  = sum(v for k, v in iniciales_atk.get(atacante["jugador"], {}).items()
                            if _norm(k) not in {"ALDEANO"} and _norm(k) in UNIDADES_BASICAS | INVOCACIONES)
        sobrev_dict    = _grupos_a_dict_por_jugador(atk_grupos).get(atacante["jugador"], {})
        sobrev_ald     = sum(v for k, v in sobrev_dict.items() if _norm(k) == "ALDEANO")
        sobrev_mil     = sum(v for k, v in sobrev_dict.items()
                            if _norm(k) not in {"ALDEANO"} and _norm(k) in UNIDADES_BASICAS | INVOCACIONES)
        pct_ald = (sobrev_ald / total_ald_ini) if total_ald_ini > 0 else 1.0
        pct_mil = (sobrev_mil / total_mil_ini) if total_mil_ini > 0 else 1.0
        # Acreditar XP de la entidad en victorias por valor/resistencia (no hubo HP=0)
        xp_atk += ent_xp
        if pct_ald >= 0.80 and pct_mil >= 0.90:
            tipo_victoria = "valor"
            victoria      = True
            mensaje       = f"Victoria por valor contra {nombre_ent} ({pct_ald*100:.1f}% ald, {pct_mil*100:.1f}% mil)"
            xp_atk *= 2.0  # XP doble por valor
        else:
            tipo_victoria = "resistencia"
            victoria      = True
            mensaje       = f"Victoria por resistencia contra {nombre_ent} (sobrevivió 9 rondas)"
    else:
        tipo_victoria = None
        victoria      = False
        mensaje       = f"Derrota contra {nombre_ent}"

    log.append(mensaje)

    sobrev_atk = _grupos_a_dict_por_jugador(atk_grupos)
    bajas_atk  = _calcular_bajas(iniciales_atk, sobrev_atk)

    return {
        "victoria_atacante":  victoria,
        "tipo_victoria":      tipo_victoria,   # "combate" | "valor" | "resistencia" | None
        "mensaje":            mensaje,
        "rondas":             rondas,
        "log":                log,
        "iniciales_atk":      iniciales_atk,
        "iniciales_def":      {nombre_ent: 1},
        "sobrevivientes_atk": sobrev_atk,
        "sobrevivientes_def": {} if ent_muerta else {nombre_ent: 1},
        "bajas_atk":          bajas_atk,
        "bajas_def":          {nombre_ent: 0 if not victoria else 1},
        "xp_por_jugador_atk": {atacante["jugador"]: xp_atk},
        "xp_por_jugador_def": {"MUNDO": xp_def},
        "saqueo":             {},
        "muralla_atravesada": False,
    }


# ── Aplicar resultados a ciudades y jugadores ─────────────────────────────────

def aplicar_resultado_combate(
    resultado: dict,
    ciudades_atk: dict,
    ciudades_def: dict,
    jugadores_atk: dict,
    jugadores_def: dict,
) -> None:
    """
    Aplica in-place el resultado del combate.

    ciudades_atk: {jugador: city_dict} — ciudad origen de cada atacante
    ciudades_def: {jugador: city_dict} — ciudad de cada defensor
    jugadores_atk: {jugador: player_dict}
    jugadores_def: {jugador: player_dict}
    """
    # Bajas atacantes
    for jug, bajas in resultado["bajas_atk"].items():
        city = ciudades_atk.get(jug)
        if not city:
            continue
        for nombre, cnt in bajas.items():
            actual = _srf(city.get(nombre, 0))
            if actual >= 1e50:  # __INF__ — no modificar
                continue
            clave = nombre if nombre in city else nombre.replace("_", " ")
            city[clave] = max(0.0, actual - cnt)

    # Bajas defensores
    for jug, bajas in resultado["bajas_def"].items():
        city = ciudades_def.get(jug)
        if not city:
            continue
        for nombre, cnt in bajas.items():
            actual = _srf(city.get(nombre, 0))
            if actual >= 1e50:  # __INF__ — no modificar
                continue
            # Intentar con guión bajo y con espacio (normalización de claves)
            clave = nombre if nombre in city else nombre.replace("_", " ")
            city[clave] = max(0.0, actual - cnt)

    # Saqueo — va a la ciudad del primer atacante (o repartido)
    if resultado["saqueo"] and ciudades_atk:
        primer_jug = next(iter(ciudades_atk))
        city_atk   = ciudades_atk[primer_jug]
        city_def   = next(iter(ciudades_def.values())) if ciudades_def else None
        for recurso, cantidad in resultado["saqueo"].items():
            city_atk[recurso] = float(city_atk.get(recurso, 0) or 0) + cantidad
            if city_def:
                city_def[recurso] = max(0.0, float(city_def.get(recurso, 0) or 0) - cantidad)

    # XP atacantes
    for jug, xp in resultado["xp_por_jugador_atk"].items():
        player = jugadores_atk.get(jug)
        if player:
            player["experiencia"] = float(player.get("experiencia", 0) or 0) + xp

    # XP defensores
    for jug, xp in resultado["xp_por_jugador_def"].items():
        player = jugadores_def.get(jug)
        if player:
            player["experiencia"] = float(player.get("experiencia", 0) or 0) + xp

    # Estadísticas
    victoria = resultado["victoria_atacante"]
    for player in jugadores_atk.values():
        k = "batallas_ganadas" if victoria else "batallas_perdidas"
        player[k] = int(player.get(k, 0) or 0) + 1
    for player in jugadores_def.values():
        k = "batallas_perdidas" if victoria else "batallas_ganadas"
        player[k] = int(player.get(k, 0) or 0) + 1
