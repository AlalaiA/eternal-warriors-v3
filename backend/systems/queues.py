"""
backend/systems/queues.py
Eternal Warriors v3.0 — Sistema de colas de entrenamiento e invocación

Cuarteles (CUARTEL_1, CUARTEL_2, CUARTEL_3):
  - Entrenan unidades básicas (Explorador, Guerrero, Sacerdote, etc.)
  - Tiempo = TIEMPO_BASE_MINUTOS × 60 × (1 - reduccion_cuartel/100)
  - 3 colas independientes simultáneas

Templos (TEMPLO_1, TEMPLO_2, TEMPLO_3):
  - Invocan criaturas (Demonio, Ánima, etc.)
  - Tiempo = TIEMPO_INVOCACION_BASE_MINUTOS × 60 × (1 - rebaja_templo/100)
  - Costo en maná por unidad
  - Requiere nivel mínimo de sacerdote
  - 3 colas independientes simultáneas

Retroactividad:
  - Al procesar colas: calcular unidades completadas desde último tick
  - Máximo retroactivo: 3 días
"""

import csv, time
from pathlib import Path
import pathlib

CSV_DIR = Path(__file__).parent.parent.parent / "csv"
MAX_RETROACTIVO_SEG = 3 * 24 * 3600

# ── Loaders CSV ───────────────────────────────────────────────────────────────

def _load_tiempo_unidades():
    """Carga tiempo base (minutos) por unidad. CSV: utf-8-sig, sep=';', Row0=header, Row1+=datos."""
    import csv as _csv
    result = {}
    csv_path = pathlib.Path(__file__).parent.parent.parent / "csv" / "tiempo_base_produccion_unidades_basicas.csv"
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = _csv.reader(f, delimiter=";")
        rows = list(reader)
    # Row 0 es header; datos comienzan en Row 1
    for row in rows[1:]:
        if len(row) < 2:
            continue
        nombre = row[0].strip().upper()   # normalizar a MAYÚSCULAS
        try:
            minutos = float(row[1].strip().replace(",", "."))
            result[nombre] = minutos
        except ValueError:
            pass
    return result
def _load_invocaciones():
    """
    Carga características de invocaciones. CSV: utf-8-sig, sep=';', Row0=header.
    Columnas: [0]Invocación [1]HP [2]PA [3]CA [4]DESTREZA [5]SIGILO [6]VELOCIDAD
              [7]NIVEL_MIN_SACERDOTE [8]TIEMPO_BASE_MIN [9]COSTO_MANA
    """
    import csv as _csv
    result = {}
    csv_path = pathlib.Path(__file__).parent.parent.parent / "csv" / "caracteristicas_invocaciones.csv"
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = _csv.reader(f, delimiter=";")
        rows = list(reader)
    for row in rows[1:]:  # Row 0 = header
        if len(row) < 10:
            continue
        nombre = row[0].strip().upper()
        import unicodedata as _ud
        nombre = ''.join(ch for ch in _ud.normalize('NFD', nombre) if _ud.category(ch) != 'Mn')
        try:
            result[nombre] = {
                "hp":                  float(row[1].strip()),
                "pa":                  float(row[2].strip()),
                "ca":                  float(row[3].strip()),
                "destreza":            float(row[4].strip()),
                "sigilo":              float(row[5].strip()),
                "velocidad":           float(row[6].strip()),
                "nivel_min_sacerdote": int(row[7].strip()),    # índice 7 ← CORRECTO
                "tiempo_base_min":     float(row[8].strip()),  # índice 8
                "costo_mana":          float(row[9].strip()),  # índice 9
            }
        except (ValueError, IndexError):
            pass
    return result
def _load_reduccion_cuartel() -> dict:
    """% reducción tiempo por nivel de cuartel."""
    result = {}
    path = CSV_DIR / "edificio12_cuartel.csv"
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
                red = row[6].strip().replace("%", "")  # col[6] = %reducción
                result[nivel] = float(red)
            except (ValueError, IndexError):
                result[nivel] = 0.0
    return result

def _load_rebaja_templo() -> dict:
    """% rebaja tiempo invocación por nivel de templo."""
    result = {}
    path = CSV_DIR / "edificio11_templo.csv"
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
                reb = row[6].strip().replace("%", "")  # col[6] = %rebaja
                result[nivel] = float(reb)
            except (ValueError, IndexError):
                result[nivel] = 0.0
    return result

def _load_reduccion_universidad() -> dict:
    """% reducción tiempo en colas por nivel de universidad (aplica a cuartel y templo)."""
    result = {}
    path = CSV_DIR / "edificio9_universidad.csv"
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
                red = row[6].strip().replace("%","").replace(",",".")
                result[nivel] = float(red)
            except (ValueError, IndexError):
                result[nivel] = 0.0
    return result

def _load_costos_unidades() -> dict:
    """Carga costos de materiales por unidad y nivel desde caracteristicas_unidades.csv."""
    import csv as _csv
    result = {}  # {UNIDAD: {nivel: {madera,piedra,hierro,carbon,oro}}}
    path = CSV_DIR / "caracteristicas_unidades.csv"
    if not path.exists():
        return result
    with open(path, encoding="utf-8-sig") as f:
        reader = _csv.reader(f, delimiter=";")
        next(reader)  # header
        for row in reader:
            if len(row) < 14: continue
            unidad = row[0].strip().upper()
            try:
                nivel = int(row[1].strip())
                costos = {
                    'MADERA': float(row[9].strip()  or 0),
                    'PIEDRA': float(row[10].strip() or 0),
                    'HIERRO': float(row[11].strip() or 0),
                    'CARBON': float(row[12].strip() or 0),
                    'ORO':    float(row[13].strip() or 0),
                }
                if unidad not in result:
                    result[unidad] = {}
                result[unidad][nivel] = costos
            except (ValueError, IndexError):
                pass
    return result

# Cache de módulo
_TIEMPO_UNIDADES = None
_INVOCACIONES    = None
_RED_CUARTEL     = None
_REB_TEMPLO      = None
_RED_UNIVERSIDAD = None
_COSTOS_UNIDADES = None

def get_tiempo_unidades():
    global _TIEMPO_UNIDADES
    if _TIEMPO_UNIDADES is None: _TIEMPO_UNIDADES = _load_tiempo_unidades()
    return _TIEMPO_UNIDADES

def get_invocaciones():
    global _INVOCACIONES
    if _INVOCACIONES is None: _INVOCACIONES = _load_invocaciones()
    return _INVOCACIONES

def get_reduccion_cuartel():
    global _RED_CUARTEL
    if _RED_CUARTEL is None: _RED_CUARTEL = _load_reduccion_cuartel()
    return _RED_CUARTEL

def get_rebaja_templo():
    global _REB_TEMPLO
    if _REB_TEMPLO is None: _REB_TEMPLO = _load_rebaja_templo()
    return _REB_TEMPLO

def get_reduccion_universidad():
    global _RED_UNIVERSIDAD
    if _RED_UNIVERSIDAD is None: _RED_UNIVERSIDAD = _load_reduccion_universidad()
    return _RED_UNIVERSIDAD

def get_costos_unidades():
    global _COSTOS_UNIDADES
    if _COSTOS_UNIDADES is None: _COSTOS_UNIDADES = _load_costos_unidades()
    return _COSTOS_UNIDADES

# ── Cálculo de tiempos ────────────────────────────────────────────────────────

def tiempo_entrenamiento_seg(unidad: str, nivel_cuartel: int, nivel_universidad: int = 0) -> float:
    """Segundos por unidad básica entrenada. Aplica reducción de cuartel + universidad."""
    # Forzar recarga de cache para evitar datos obsoletos
    global _TIEMPO_UNIDADES, _RED_CUARTEL, _RED_UNIVERSIDAD
    _TIEMPO_UNIDADES = _load_tiempo_unidades()
    _RED_CUARTEL     = _load_reduccion_cuartel()
    _RED_UNIVERSIDAD = _load_reduccion_universidad()
    tiempos      = _TIEMPO_UNIDADES
    reducciones  = _RED_CUARTEL
    red_univ     = _RED_UNIVERSIDAD
    base_min     = tiempos.get(unidad.upper(), 300)
    red_c        = reducciones.get(nivel_cuartel, 0) / 100
    red_u        = red_univ.get(nivel_universidad, 0) / 100
    red_total    = min(red_c + red_u, 0.95)
    return base_min * (1 - red_total)

def tiempo_invocacion_seg(invocacion: str, nivel_templo: int, nivel_universidad: int = 0) -> float:
    """Segundos por unidad invocada. Aplica rebaja de templo + universidad."""
    invs     = get_invocaciones()
    rebajas  = get_rebaja_templo()
    red_univ = get_reduccion_universidad()
    inv      = invs.get(invocacion.upper(), {})
    base_seg = inv.get("tiempo_base_min", 9000)  # campo mal nombrado, son segundos
    reb_t    = rebajas.get(nivel_templo, 0) / 100
    red_u    = red_univ.get(nivel_universidad, 0) / 100
    red_total = min(reb_t + red_u, 0.95)
    return base_seg * (1 - red_total)

def costo_mana_invocacion(invocacion: str) -> float:
    """Maná por unidad invocada."""
    invs = get_invocaciones()
    return invs.get(invocacion.upper(), {}).get("costo_mana", 0)

def nivel_min_sacerdote(invocacion: str) -> int:
    """Nivel mínimo de sacerdote requerido."""
    invs = get_invocaciones()
    return invs.get(invocacion.upper(), {}).get("nivel_min_sacerdote", 99)

# ── Procesamiento de colas ────────────────────────────────────────────────────

def procesar_colas(city: dict, unit_levels: dict = None) -> dict:
    """
    Procesa todas las colas activas de una ciudad.
    - Completa unidades entrenadas/invocadas según tiempo transcurrido
    - Aplica retroactividad máxima de 3 días
    - Devuelve resumen de lo completado
    """
    if unit_levels is None:
        unit_levels = {}

    ahora = time.time()
    colas = city.get("COLAS", [])
    completadas = {}

    colas_activas = []
    for cola in colas:
        tipo       = cola.get("tipo", "")          # CUARTEL_1, TEMPLO_2, etc.
        unidad     = cola.get("unidad", "")
        cant_total = int(cola.get("cantidad_total", 0))
        cant_hecha = int(cola.get("cantidad_hecha", 0))
        inicio     = float(cola.get("inicio", ahora))
        t_por_unit = float(cola.get("tiempo_por_unidad_seg", 3600))

        if cant_hecha >= cant_total:
            continue  # cola ya terminada

        # Calcular cuántas unidades se han completado desde el inicio
        # con retroactividad máxima de 3 días
        inicio_efectivo = max(inicio, ahora - MAX_RETROACTIVO_SEG)
        seg_transcurridos = max(0.0, ahora - inicio_efectivo)
        completadas_desde_inicio = min(
            cant_total,
            int(seg_transcurridos / t_por_unit)
        )
        nuevas = max(0, completadas_desde_inicio - cant_hecha)

        if nuevas > 0:
            # Añadir unidades a la ciudad
            campo = unidad.upper()
            city[campo] = float(city.get(campo, 0) or 0) + nuevas
            cola["cantidad_hecha"] = completadas_desde_inicio
            completadas[f"{tipo}:{unidad}"] = nuevas

        # Mantener cola si no terminó
        if cola["cantidad_hecha"] < cant_total:
            colas_activas.append(cola)
        # Si terminó, no la añadimos → desaparece

    city["COLAS"] = colas_activas
    return completadas


def iniciar_cola_cuartel(city: dict, cuartel_key: str, unidad: str,
                          cantidad: int, unit_levels: dict = None) -> dict:
    """
    Inicia una cola de entrenamiento en un cuartel.
    cuartel_key: 'CUARTEL_1', 'CUARTEL_2', 'CUARTEL_3'
    unidad: nombre de la unidad básica (GUERRERO, MAGO, etc.)
    Retorna {"ok": bool, "msg": str, "tiempo_total_seg": float}
    """
    if unit_levels is None:
        unit_levels = {}

    # Verificar que el cuartel existe y tiene nivel > 0
    nivel_cuartel = int(city.get(cuartel_key, 0) or 0)
    if nivel_cuartel < 1:
        return {"ok": False, "msg": f"{cuartel_key} no existe o nivel 0"}

    # Verificar que no hay más de 2 colas activas en ese cuartel
    colas = city.get("COLAS", [])
    colas_activas_cuartel = [
        cola for cola in colas
        if cola.get("tipo") == cuartel_key
        and cola.get("cantidad_hecha", 0) < cola.get("cantidad_total", 0)
    ]
    if len(colas_activas_cuartel) >= 2:
        return {"ok": False, "msg": f"{cuartel_key} ya tiene 2 colas activas"}

    # Tiempo por unidad (con reducción de universidad)
    nivel_universidad = int(city.get("UNIVERSIDAD", 0) or 0)
    t_seg = tiempo_entrenamiento_seg(unidad, nivel_cuartel, nivel_universidad)
    if t_seg <= 0:
        return {"ok": False, "msg": f"Unidad {unidad} no reconocida"}

    # Verificar y descontar materiales
    nivel_tropa = int(unit_levels.get("NIVEL_DE_TROPAS", unit_levels.get(unidad.upper(), 1)) or 1)
    costos_db = get_costos_unidades()
    costos_unidad = costos_db.get(unidad.upper(), {})
    # Usar nivel de tropa, fallback a nivel 1
    costo_nivel = costos_unidad.get(nivel_tropa) or costos_unidad.get(1) or {}
    costo_total = {mat: val * cantidad for mat, val in costo_nivel.items()}

    # Verificar recursos suficientes
    for mat, val in costo_total.items():
        if val > 0:
            disponible = float(city.get(mat, 0) or 0)
            if disponible < val:
                return {
                    "ok": False,
                    "msg": f"Recursos insuficientes: necesitas {val:,.0f} {mat}, tienes {disponible:,.0f}"
                }

    # Descontar materiales
    for mat, val in costo_total.items():
        if val > 0:
            city[mat] = float(city.get(mat, 0) or 0) - val

    # Crear cola
    nueva_cola = {
        "tipo":               cuartel_key,
        "unidad":             unidad.upper(),
        "cantidad_total":     cantidad,
        "cantidad_hecha":     0,
        "tiempo_por_unidad_seg": t_seg,
        "inicio":             time.time(),
    }
    city.setdefault("COLAS", []).append(nueva_cola)

    return {
        "ok": True,
        "msg": f"Cola iniciada: {cantidad} {unidad} en {cuartel_key}",
        "tiempo_total_seg": t_seg * cantidad,
        "tiempo_por_unidad_seg": t_seg,
    }


def iniciar_cola_templo(city: dict, templo_key: str, invocacion: str,
                         cantidad: int, unit_levels: dict = None) -> dict:
    """
    Inicia una cola de invocación en un templo.
    templo_key: 'TEMPLO_1', 'TEMPLO_2', 'TEMPLO_3'
    invocacion: nombre de la invocación (DEMONIO, ANIMA, etc.)
    Retorna {"ok": bool, "msg": str}
    """
    if unit_levels is None:
        unit_levels = {}

    # Verificar templo
    nivel_templo = int(city.get(templo_key, 0) or 0)
    if nivel_templo < 1:
        return {"ok": False, "msg": f"{templo_key} no existe o nivel 0"}

    # Verificar nivel mínimo sacerdote
    nivel_sac = int(unit_levels.get("SACERDOTE", 1))
    nivel_min = nivel_min_sacerdote(invocacion)
    if nivel_sac < nivel_min:
        return {
            "ok": False,
            "msg": f"Se requiere Sacerdote nivel {nivel_min}. Tienes nivel {nivel_sac}."
        }

    # Verificar que no hay más de 2 colas activas en ese templo
    colas = city.get("COLAS", [])
    colas_activas_templo = [
        cola for cola in colas
        if cola.get("tipo") == templo_key
        and cola.get("cantidad_hecha", 0) < cola.get("cantidad_total", 0)
    ]
    if len(colas_activas_templo) >= 2:
        return {"ok": False, "msg": f"{templo_key} ya tiene 2 colas activas"}

    # Calcular costo maná total
    mana_por_unit = costo_mana_invocacion(invocacion)
    mana_total = mana_por_unit * cantidad
    mana_actual = float(city.get("MANA", 0) or 0)

    if mana_actual < mana_total:
        return {
            "ok": False,
            "msg": f"Maná insuficiente. Necesitas {mana_total:,.0f}, tienes {mana_actual:,.0f}"
        }

    # Descontar maná
    city["MANA"] = mana_actual - mana_total

    # Tiempo por unidad (con reducción de universidad)
    nivel_universidad = int(city.get("UNIVERSIDAD", 0) or 0)
    t_seg = tiempo_invocacion_seg(invocacion, nivel_templo, nivel_universidad)

    # Crear cola
    nueva_cola = {
        "tipo":               templo_key,
        "unidad":             invocacion.upper(),
        "cantidad_total":     cantidad,
        "cantidad_hecha":     0,
        "tiempo_por_unidad_seg": t_seg,
        "inicio":             time.time(),
        "mana_gastado":       mana_total,
    }
    city.setdefault("COLAS", []).append(nueva_cola)

    return {
        "ok": True,
        "msg": f"Cola iniciada: {cantidad} {invocacion} en {templo_key}",
        "tiempo_total_seg": t_seg * cantidad,
        "tiempo_por_unidad_seg": t_seg,
        "mana_gastado": mana_total,
    }


def cancelar_cola(city: dict, tipo: str, idx: int = 0) -> dict:
    """Cancela la cola idx (0 o 1) de un cuartel o templo. Devuelve maná si era templo."""
    colas = city.get("COLAS", [])
    colas_tipo = [i for i, c in enumerate(colas) if c.get("tipo") == tipo]
    if idx >= len(colas_tipo):
        return {"ok": False, "msg": f"No hay cola {idx+1} activa en {tipo}"}
    i = colas_tipo[idx]
    cola = colas[i]
    if tipo.startswith("TEMPLO"):
        pendientes = cola["cantidad_total"] - cola["cantidad_hecha"]
        mana_devuelto = pendientes * costo_mana_invocacion(cola["unidad"])
        city["MANA"] = float(city.get("MANA", 0) or 0) + mana_devuelto
    colas.pop(i)
    city["COLAS"] = colas
    return {"ok": True, "msg": f"Cola {idx+1} de {tipo} cancelada"}


def info_colas(city: dict) -> list:
    """
    Devuelve estado actual de todas las colas con progreso calculado.
    """
    ahora = time.time()
    resultado = []
    for cola in city.get("COLAS", []):
        cant_total = int(cola.get("cantidad_total", 0))
        cant_hecha = int(cola.get("cantidad_hecha", 0))
        t_por_unit = float(cola.get("tiempo_por_unidad_seg", 3600))
        inicio     = float(cola.get("inicio", ahora))

        seg_transcurridos = max(0.0, ahora - inicio)
        completadas_ahora = min(cant_total, int(seg_transcurridos / t_por_unit))
        pendientes = cant_total - completadas_ahora

        # Tiempo restante para siguiente unidad
        if pendientes > 0 and t_por_unit > 0:
            seg_en_unidad_actual = seg_transcurridos % t_por_unit
            seg_para_siguiente = t_por_unit - seg_en_unidad_actual
        else:
            seg_para_siguiente = 0

        resultado.append({
            "tipo":             cola.get("tipo"),
            "unidad":           cola.get("unidad"),
            "cantidad_total":   cant_total,
            "completadas":      completadas_ahora,
            "pendientes":       pendientes,
            "tiempo_por_unidad_seg": t_por_unit,
            "seg_para_siguiente": seg_para_siguiente,
            "tiempo_total_restante_seg": pendientes * t_por_unit - (t_por_unit - seg_para_siguiente),
            "porcentaje": round(completadas_ahora / cant_total * 100, 1) if cant_total > 0 else 100,
        })
    return resultado