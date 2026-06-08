"""
backend/systems/buildings.py
Sistema de construcción/mejora de edificios.

Responsabilidades:
- Cargar costos y tiempos de cada edificio desde sus CSVs canónicos
- Validar si el jugador puede subir un edificio (recursos + nivel máx)
- Iniciar obra (descontar recursos, crear entrada en city['OBRAS'])
- Procesar obras terminadas (retroactividad igual que colas: max 3 días)
- Cancelar obra (devolver recursos)
- Retornar datos de edificio para la UI (nivel actual, siguiente nivel, costo, tiempo)

CSV pattern para edificios:
  Row 0 = header (puede tener \n embebido en último campo — csv.reader lo maneja)
  Row N = datos del nivel N (Row 1 = nivel 1, Row 2 = nivel 2, ...)
  Columnas fijas: [0]Nivel [1]costomadera [2]costopiedra [3]costohierro
                  [4]costooro [5]costocarbon [6]stat_especial [7]tiempo_min
  Excepciones documentadas en EDIFICIOS_META abajo.
"""

import csv
import pathlib
from typing import Optional
from backend.data.save_manager import safe_resource_float as _srf

CSV_DIR = pathlib.Path(__file__).parent.parent.parent / "csv"
MAX_RETROACTIVIDAD_SEG = 3 * 24 * 3600  # 3 días

# ── Metadatos de cada edificio ─────────────────────────────────────────────────
# csv_file      : nombre del CSV
# campo_json    : clave en el dict ciudad del JSON del jugador
# max_nivel     : filas de datos en el CSV (= niveles disponibles)
# stat_col      : índice de la columna de stat especial (-1 si no aplica)
# stat_nombre   : nombre descriptivo del stat especial
# tiempo_col    : índice de la columna de tiempo en minutos
EDIFICIOS_META = {
    "CENTRO_DE_CIUDAD":   {"csv": "edificio1_centro_de_ciudad.csv",  "campo": "CENTRO_DE_CIUDAD",   "max_nivel": 45, "stat_col": 6, "stat_nombre": "aldeanos_hora",        "tiempo_col": 7},
    "CASA":               {"csv": "edificio2_casa.csv",               "campo": "CASA",               "max_nivel": 50, "stat_col": 6, "stat_nombre": "capacidad",            "tiempo_col": 7},
    "MURALLA":            {"csv": "edificio3_muralla.csv",            "campo": "MURALLA",            "max_nivel": 50, "stat_col": 6, "stat_nombre": "hp",                   "tiempo_col": 7},
    "TORRE_DE_VIGILANCIA":{"csv": "edificio4_torre_de_vigilancia.csv","campo": "TORRE_DE_VIGILANCIA","max_nivel": 50, "stat_col": 6, "stat_nombre": "deteccion",            "tiempo_col": 8},
    "CENTRO_DE_VIAJES":   {"csv": "edificio5_centro_de_viajes.csv",   "campo": "CENTRO_DE_VIAJES",   "max_nivel": 40, "stat_col": 6, "stat_nombre": "cuadros_alcance",      "tiempo_col": 7},
    "ESCONDITE":          {"csv": "edificio6_escondite.csv",          "campo": "ESCONDITE",          "max_nivel": 40, "stat_col": 6, "stat_nombre": "capacidad_ejercito",   "tiempo_col": 8},
    "ALMACEN":            {"csv": "edificio7_almacen.csv",            "campo": "ALMACEN",            "max_nivel": 50, "stat_col": 6, "stat_nombre": "capacidad_material",   "tiempo_col": 7},
    "SANTUARIO_ARCANO":   {"csv": "edificio8_santuario_arcano.csv",   "campo": "SANTUARIO_ARCANO",   "max_nivel": 50, "stat_col": 6, "stat_nombre": "capacidad_mana",       "tiempo_col": 7},
    "UNIVERSIDAD":        {"csv": "edificio9_universidad.csv",        "campo": "UNIVERSIDAD",        "max_nivel": 45, "stat_col": 6, "stat_nombre": "reduccion_colas_pct",  "tiempo_col": 8},
    "HERRERIA":           {"csv": "edificio10_herreria.csv",          "campo": "HERRERIA",           "max_nivel": 40, "stat_col": 6, "stat_nombre": "bonus_arma",           "tiempo_col": 9},
    "TEMPLO_1":           {"csv": "edificio11_templo.csv",            "campo": "TEMPLO_1",           "max_nivel": 50, "stat_col": 6, "stat_nombre": "rebaja_invocacion_pct","tiempo_col": 7},
    "TEMPLO_2":           {"csv": "edificio11_templo.csv",            "campo": "TEMPLO_2",           "max_nivel": 50, "stat_col": 6, "stat_nombre": "rebaja_invocacion_pct","tiempo_col": 7},
    "TEMPLO_3":           {"csv": "edificio11_templo.csv",            "campo": "TEMPLO_3",           "max_nivel": 50, "stat_col": 6, "stat_nombre": "rebaja_invocacion_pct","tiempo_col": 7},
    "CUARTEL_1":          {"csv": "edificio12_cuartel.csv",           "campo": "CUARTEL_1",          "max_nivel": 50, "stat_col": 6, "stat_nombre": "reduccion_tiempo_pct", "tiempo_col": 7},
    "CUARTEL_2":          {"csv": "edificio12_cuartel.csv",           "campo": "CUARTEL_2",          "max_nivel": 50, "stat_col": 6, "stat_nombre": "reduccion_tiempo_pct", "tiempo_col": 7},
    "CUARTEL_3":          {"csv": "edificio12_cuartel.csv",           "campo": "CUARTEL_3",          "max_nivel": 50, "stat_col": 6, "stat_nombre": "reduccion_tiempo_pct", "tiempo_col": 7},
}

# ── Cache en memoria ───────────────────────────────────────────────────────────
_csv_cache: dict = {}


def _load_edificio_csv(csv_name: str) -> list[dict]:
    """
    Carga CSV de edificio. Retorna lista indexada por nivel (índice 0 vacío,
    índice 1 = nivel 1, etc.).
    Cada elemento: {nivel, madera, piedra, hierro, oro, carbon, stat, tiempo_min}
    """
    if csv_name in _csv_cache:
        return _csv_cache[csv_name]

    path = CSV_DIR / csv_name
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        rows = list(reader)

    # Row 0 siempre es header (con posible \n embebido en último campo)
    data = [None]  # índice 0 = vacío; nivel 1 en índice 1
    for row in rows[1:]:
        if len(row) < 6:
            continue
        try:
            nivel = int(row[0].strip())
            stat_val = row[6].strip().rstrip("%") if len(row) > 6 else "0"
            tiempo_str = row[7].strip().rstrip("%") if len(row) > 7 else "0"
            # Para edificios con más columnas (tiempo en índice diferente),
            # buildings_info() pasa el índice correcto desde EDIFICIOS_META
            def _f(v): return float(v.strip().replace(",","").replace("%","")) if v.strip().replace(",","").replace("%","") else 0.0
            data.append({
                "nivel":      nivel,
                "madera":     _f(row[1]),
                "piedra":     _f(row[2]),
                "hierro":     _f(row[3]),
                "oro":        _f(row[4]),
                "carbon":     _f(row[5]),
                "stat":       float(stat_val.replace(",", ".")) if stat_val else 0.0,
                "tiempo_min": float(tiempo_str.replace(",", ".")) if tiempo_str else 0.0,
                "_row":       row,   # fila completa para índices especiales
            })
        except (ValueError, IndexError):
            continue

    _csv_cache[csv_name] = data
    return data


def _get_nivel_data(csv_name: str, nivel: int, tiempo_col: int) -> Optional[dict]:
    """Retorna los datos del nivel solicitado con tiempo_col correcto."""
    data = _load_edificio_csv(csv_name)
    if nivel < 1 or nivel >= len(data) or data[nivel] is None:
        return None
    entry = data[nivel].copy()
    row = entry["_row"]
    if len(row) > tiempo_col:
        try:
            entry["tiempo_min"] = float(row[tiempo_col].strip().replace(",", "."))
        except ValueError:
            pass
    return entry


# ── API pública ────────────────────────────────────────────────────────────────


def _load_universidad_reduccion() -> dict:
    """
    Carga % de reducción de la Universidad por nivel.
    col[6] = % reducción colas (cuartel/templo/herrería/CC)
    col[7] = % reducción tiempo de construcción de edificios
    Retorna: {nivel: {"colas_pct": float, "edificios_pct": float}}
    """
    import csv as _csv
    result = {}
    csv_path = CSV_DIR / "edificio9_universidad.csv"
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = _csv.reader(f, delimiter=";")
        rows = list(reader)
    for row in rows[1:]:
        if len(row) < 8:
            continue
        try:
            nivel = int(row[0].strip())
            colas   = float(row[6].strip().rstrip("%").replace(",","."))
            edifs   = float(row[7].strip().rstrip("%").replace(",","."))
            result[nivel] = {"colas_pct": colas, "edificios_pct": edifs}
        except (ValueError, IndexError):
            continue
    return result

_UNIV_CACHE: dict = {}

def get_universidad_reduccion(nivel_universidad: int) -> dict:
    """Retorna {colas_pct, edificios_pct} para el nivel dado."""
    global _UNIV_CACHE
    if not _UNIV_CACHE:
        _UNIV_CACHE = _load_universidad_reduccion()
    if nivel_universidad <= 0:
        return {"colas_pct": 0.0, "edificios_pct": 0.0}
    # Usar el nivel exacto o el más cercano hacia abajo
    nv = max(k for k in _UNIV_CACHE if k <= nivel_universidad) if any(k <= nivel_universidad for k in _UNIV_CACHE) else 1
    return _UNIV_CACHE.get(nv, {"colas_pct": 0.0, "edificios_pct": 0.0})


def _apply_univ_reduction(tiempo_seg: int, nivel_universidad: int) -> int:
    """Aplica el % de reducción de la Universidad al tiempo de construcción."""
    if nivel_universidad <= 0 or tiempo_seg <= 0:
        return tiempo_seg
    reduccion = get_universidad_reduccion(nivel_universidad)
    pct = reduccion.get("edificios_pct", 0.0)
    return max(1, int(tiempo_seg * (1 - pct / 100)))

def buildings_info(city: dict, edificio: str) -> dict:
    """
    Retorna info para la UI de subida de edificio.
    {
      nivel_actual, nivel_siguiente, max_nivel,
      costo: {madera,piedra,hierro,oro,carbon},
      tiempo_seg: int,
      stat_nombre: str, stat_actual: float, stat_siguiente: float,
      puede_subir: bool,   # False si ya en nivel máx o hay obra activa
      en_construccion: bool,
      tiempo_restante_seg: float | None
    }
    """
    import time
    meta = EDIFICIOS_META.get(edificio)
    if not meta:
        return {"error": f"Edificio {edificio} no registrado"}

    nivel_actual = int(city.get(meta["campo"], 0) or 0)
    max_nivel = meta["max_nivel"]

    # ¿Hay obra activa para este edificio? Solo obras v3 (tienen "inicio" y "duracion_seg")
    obras = city.get("OBRAS", [])
    obra_activa = next((o for o in obras 
                        if o.get("edificio") == edificio 
                        and "inicio" in o and "duracion_seg" in o), None)
    en_construccion = obra_activa is not None
    tiempo_restante = None
    if obra_activa:
        fin = obra_activa["inicio"] + obra_activa["duracion_seg"]
        tiempo_restante = max(0.0, fin - time.time())

    nivel_sig = nivel_actual + 1
    puede_subir = (not en_construccion) and (nivel_sig <= max_nivel)

    siguiente = _get_nivel_data(meta["csv"], nivel_sig, meta["tiempo_col"]) if puede_subir else None
    actual_data = _get_nivel_data(meta["csv"], nivel_actual, meta["tiempo_col"])

    return {
        "edificio":         edificio,
        "nivel_actual":     nivel_actual,
        "nivel_siguiente":  nivel_sig,
        "max_nivel":        max_nivel,
        "stat_nombre":      meta["stat_nombre"],
        "stat_actual":      actual_data["stat"] if actual_data else 0,
        "stat_siguiente":   siguiente["stat"] if siguiente else None,
        "costo":            {k: int(siguiente[k]) for k in ("madera","piedra","hierro","oro","carbon")} if siguiente else None,
        "tiempo_seg":       _apply_univ_reduction(
                                int(siguiente["tiempo_min"] * 60),
                                city.get("UNIVERSIDAD", 0)
                            ) if siguiente else None,
        "puede_subir":      puede_subir,
        "reduccion_universidad_pct": get_universidad_reduccion(city.get("UNIVERSIDAD",0)).get("edificios_pct",0),
        "en_construccion":  en_construccion,
        "tiempo_restante_seg": tiempo_restante,
    }


def iniciar_obra(player: dict, city: dict, edificio: str) -> dict:
    """
    Inicia construcción del siguiente nivel.
    Valida recursos, descuenta, agrega entrada en city['OBRAS'].
    Retorna {"ok": True} o {"error": str}
    """
    import time
    # Validar límite de obras simultáneas (máx 4)
    obras_v3 = [o for o in city.get("OBRAS", []) if "inicio" in o and "duracion_seg" in o]
    if len(obras_v3) >= 4:
        return {"error": f"Límite de 4 obras simultáneas alcanzado. "
                          f"Tienes {len(obras_v3)} en progreso."}

    info = buildings_info(city, edificio)
    if "error" in info:
        return info
    if not info["puede_subir"]:
        if info["en_construccion"]:
            return {"error": f"{edificio} ya tiene una obra en progreso"}
        return {"error": f"{edificio} ya está en nivel máximo ({info['max_nivel']})"}

    costo = info["costo"]
    # Verificar recursos
    faltantes = []
    for mat in ("MADERA", "PIEDRA", "HIERRO", "ORO", "CARBON"):
        disponible = _srf(city.get(mat, 0))
        necesario  = costo[mat.lower()]
        if disponible < 1e50 and disponible < necesario:
            faltantes.append(f"{mat}: necesita {necesario:,}, tiene {int(disponible):,}")
    if faltantes:
        return {"error": "Recursos insuficientes: " + "; ".join(faltantes)}

    # Descontar recursos solo si no son __INF__
    for mat in ("MADERA", "PIEDRA", "HIERRO", "ORO", "CARBON"):
        actual = _srf(city.get(mat, 0))
        if actual < 1e50:
            city[mat] = actual - costo[mat.lower()]

    # Registrar obra
    now = time.time()
    obra = {
        "edificio":    edificio,
        "nivel_dest":  info["nivel_siguiente"],
        "inicio":      now,
        "duracion_seg": info["tiempo_seg"],
    }
    if "OBRAS" not in city:
        city["OBRAS"] = []
    city["OBRAS"].append(obra)

    return {
        "ok":           True,
        "edificio":     edificio,
        "nivel_dest":   info["nivel_siguiente"],
        "fin":          now + info["tiempo_seg"],
        "duracion_seg": info["tiempo_seg"],
    }


def procesar_obras(city: dict) -> list[str]:
    """
    Procesa obras terminadas. Llama al cargar ciudad y al hacer tick.
    Retorna lista de edificios que subieron de nivel en esta pasada.
    """
    import time
    obras = city.get("OBRAS", [])
    if not obras:
        return []

    now = time.time()
    terminadas = []
    pendientes = []

    for obra in obras:
        # Ignorar obras con formato v2 o incompleto (sin claves v3)
        if "inicio" not in obra or "duracion_seg" not in obra:
            pendientes.append(obra)  # conservar sin tocar
            continue
        fin = obra["inicio"] + obra["duracion_seg"]
        if now >= fin:
            terminadas.append(obra)
        else:
            pendientes.append(obra)

    subidos = []
    for obra in terminadas:
        edificio = obra["edificio"]
        nivel_dest = obra["nivel_dest"]
        meta = EDIFICIOS_META.get(edificio)
        if not meta:
            continue
        # Actualizar nivel en city
        nivel_actual = city.get(meta["campo"], 0)
        if nivel_dest == nivel_actual + 1:  # sanidad: solo subir 1 nivel a la vez
            city[meta["campo"]] = nivel_dest
            subidos.append(edificio)

    city["OBRAS"] = pendientes
    return subidos


def cancelar_obra(city: dict, edificio: str) -> dict:
    """
    Cancela obra activa. Devuelve el 50% de los recursos (costo de cancelación).
    """
    obras = city.get("OBRAS", [])
    obra = next((o for o in obras if o.get("edificio") == edificio), None)
    if not obra:
        return {"error": f"No hay obra activa para {edificio}"}

    meta = EDIFICIOS_META.get(edificio)
    if not meta:
        return {"error": f"Edificio {edificio} no registrado"}

    nivel_dest = obra["nivel_dest"]
    data = _get_nivel_data(meta["csv"], nivel_dest, meta["tiempo_col"])
    devuelto = {}
    if data:
        for mat in ("madera", "piedra", "hierro", "oro", "carbon"):
            # Devolver 50%
            reembolso = int(data[mat] * 0.5)
            city[mat.upper()] = city.get(mat.upper(), 0) + reembolso
            devuelto[mat] = reembolso

    city["OBRAS"] = [o for o in obras if o.get("edificio") != edificio]

    return {"ok": True, "edificio": edificio, "devuelto": devuelto}
