"""
backend/systems/production.py
Eternal Warriors v3.0 — Sistema de producción de materiales y maná

Producción de materiales:
  - Fuente: aldeanos × tasa_material_por_aldeano_por_hora[nivel_CC]
  - CSV: edificio1_centro_de_ciudad.csv (columna "Aldeanos por hora" = multiplicador)
  - CSV: aldeanos_materiales.csv (tasa base por aldeano por nivel CC)

Producción de maná:
  - Fuente: sacerdotes × maná_por_sacerdote_por_hora[nivel_sacerdote]
  - CSV: mana_sacerdotes.csv

Retroactividad:
  - Campo LAST_PROD en la ciudad (timestamp unix)
  - Al cargar ciudad: calcular segundos transcurridos, aplicar tasa, cap por almacén
  - Máximo retroactivo: 3 días (259200 segundos)
"""

import csv, time
from pathlib import Path
from backend.data.save_manager import safe_resource_float

CSV_DIR = Path(__file__).parent.parent.parent  # raíz del proyecto
# En producción real apunta a los CSVs del proyecto
# Fallback: misma carpeta que el módulo
if not CSV_DIR.exists():
    CSV_DIR = Path(__file__).parent.parent.parent

def _load_cc_tasas() -> dict:
    """Carga tasa de aldeanos por hora por nivel de C.Ciudad desde CSV."""
    # Formato: Nivel;costomadera;...;Aldeanos por hora;Tiempos...
    tasas = {}
    for path in [
        Path(__file__).parent.parent.parent / "csv" / "edificio1_centro_de_ciudad.csv",
    ]:
        if path.exists():
            with open(path, encoding="utf-8-sig") as f:
                reader = csv.reader(f, delimiter=";")
                headers = next(reader)
                # Buscar columna "Aldeanos por hora"
                ald_idx = next((i for i,h in enumerate(headers) if "Aldeanos" in h), 6)
                for row in reader:
                    if not row or not row[0].strip().isdigit():
                        continue
                    nivel = int(row[0].strip())
                    try:
                        tasas[nivel] = float(row[ald_idx].strip().replace(",","."))
                    except (ValueError, IndexError):
                        pass
            break
    return tasas

def _load_material_tasas() -> dict:
    """Carga tasa de materiales por aldeano por hora por nivel CC desde CSV."""
    # Formato: NIVEL;MADERA;PIEDRA;HIERRO;ORO;CARBÓN
    tasas = {}
    for path in [
        Path(__file__).parent.parent.parent / "csv" / "aldeanos_materiales.csv",
    ]:
        if path.exists():
            with open(path, encoding="utf-8-sig") as f:
                reader = csv.reader(f, delimiter=";")
                next(reader)  # header
                for row in reader:
                    if not row or not row[0].strip().isdigit():
                        continue
                    nivel = int(row[0].strip())
                    def parse(v):
                        return float(v.strip().replace(",","").replace(".","").replace(" ","")) if v.strip() else 0
                    try:
                        tasas[nivel] = {
                            "MADERA":  parse(row[1]),
                            "PIEDRA":  parse(row[2]),
                            "HIERRO":  parse(row[3]),
                            "ORO":     parse(row[4]),
                            "CARBON":  parse(row[5]) if len(row) > 5 else 0,
                        }
                    except (ValueError, IndexError):
                        pass
            break
    return tasas

def _load_mana_tasas() -> dict:
    """Carga maná por sacerdote por hora por nivel de sacerdote desde CSV.
    Columnas: tasa;nivel — comas son separadores de miles (ej: 26,587 = 26587).
    """
    tasas = {}
    for path in [
        Path(__file__).parent.parent.parent / "csv" / "mana_sacerdotes.csv",
    ]:
        if path.exists():
            with open(path, encoding="utf-8-sig") as f:
                reader = csv.reader(f, delimiter=";")
                next(reader)  # header
                for row in reader:
                    if not row or len(row) < 2:
                        continue
                    try:
                        # Comas = separadores de miles, no decimales
                        tasa  = float(row[0].strip().replace(",","").replace(" ",""))
                        nivel = int(row[1].strip())
                        tasas[nivel] = tasa
                    except (ValueError, IndexError):
                        pass
            break
    return tasas

def _load_almacen_caps() -> dict:
    """Capacidad por material por nivel de almacén."""
    caps = {}
    path = Path(__file__).parent.parent.parent / "csv" / "edificio7_almacen.csv"
    if not path.exists(): return caps
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        for row in reader:
            if not row or not row[0].strip().isdigit(): continue
            nivel = int(row[0].strip())
            try:
                val = row[6].strip().replace(",","").lower()
                if val in ('infinito','inf','infinity','∞',''):
                    caps[nivel] = 1e300
                else:
                    caps[nivel] = float(val)
            except (ValueError, IndexError):
                caps[nivel] = 1e300
    return caps

def _load_santuario_caps() -> dict:
    """Capacidad de maná por nivel de santuario arcano."""
    caps = {}
    path = Path(__file__).parent.parent.parent / "csv" / "edificio8_santuario_arcano.csv"
    if not path.exists(): return caps
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        for row in reader:
            if not row or not row[0].strip().isdigit(): continue
            nivel = int(row[0].strip())
            try:
                val = row[6].strip().replace(",","").lower()
                if val in ('infinito','inf','infinity','∞',''):
                    caps[nivel] = 1e300
                else:
                    caps[nivel] = float(val)
            except (ValueError, IndexError):
                caps[nivel] = 1e300
    return caps

def _load_casa_caps() -> dict:
    """Capacidad de aldeanos por nivel de casa."""
    caps = {}
    path = Path(__file__).parent.parent.parent / "csv" / "edificio2_casa.csv"
    if not path.exists(): return caps
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        for row in reader:
            if not row or not row[0].strip().isdigit(): continue
            nivel = int(row[0].strip())
            try:
                val = row[6].strip().replace(",","")
                caps[nivel] = float(val)
            except (ValueError, IndexError):
                pass
    return caps

# Cache en módulo — se cargan una vez
_CC_TASAS        = None
_MATERIAL_TASAS  = None
_MANA_TASAS      = None
_ALMACEN_CAPS    = None
_SANTUARIO_CAPS  = None
_CASA_CAPS       = None

def get_cc_tasas():
    global _CC_TASAS
    if _CC_TASAS is None: _CC_TASAS = _load_cc_tasas()
    return _CC_TASAS

def get_material_tasas():
    global _MATERIAL_TASAS
    if _MATERIAL_TASAS is None: _MATERIAL_TASAS = _load_material_tasas()
    return _MATERIAL_TASAS

def get_mana_tasas():
    global _MANA_TASAS
    if _MANA_TASAS is None: _MANA_TASAS = _load_mana_tasas()
    return _MANA_TASAS

def get_almacen_caps():
    global _ALMACEN_CAPS
    if _ALMACEN_CAPS is None: _ALMACEN_CAPS = _load_almacen_caps()
    return _ALMACEN_CAPS

def get_santuario_caps():
    global _SANTUARIO_CAPS
    if _SANTUARIO_CAPS is None: _SANTUARIO_CAPS = _load_santuario_caps()
    return _SANTUARIO_CAPS

def get_casa_caps():
    global _CASA_CAPS
    if _CASA_CAPS is None: _CASA_CAPS = _load_casa_caps()
    return _CASA_CAPS

MAX_RETROACTIVO_SEG = 3 * 24 * 3600  # 3 días

def calcular_tasas(city: dict, unit_levels: dict = None) -> dict:
    """
    Calcula las tasas de producción por segundo para una ciudad.
    unit_levels: dict con niveles por unidad del jugador (ej: {'SACERDOTE': 5})
    Retorna dict con tasas/seg para cada recurso.
    """
    if unit_levels is None:
        unit_levels = {}
    nivel_cc   = int(city.get("CENTRO_DE_CIUDAD", 1) or 1)
    aldeanos   = float(city.get("ALDEANO", 0) or 0)
    sacerdotes = float(city.get("SACERDOTE", 0) or 0)
    # Nivel sacerdote viene de unit_levels del jugador, no de la ciudad
    nivel_sac  = int(unit_levels.get("SACERDOTE", city.get("NIVEL_DE_TROPAS", 1) or 1))

    cc_tasas       = get_cc_tasas()
    material_tasas = get_material_tasas()
    mana_tasas     = get_mana_tasas()

    # Tasa de aldeanos/hora que produce el CC (multiplicador poblacional)
    # En el CSV "Aldeanos por hora" = cuántos aldeanos produce el CC por hora
    # Para materiales: aldeanos_actuales × (material_por_aldeano_por_hora / 3600)
    mat = material_tasas.get(nivel_cc, material_tasas.get(max(material_tasas.keys()), {}))

    # Producción por segundo
    tasas = {
        "MADERA":  aldeanos * mat.get("MADERA", 0) / 3600,
        "PIEDRA":  aldeanos * mat.get("PIEDRA", 0) / 3600,
        "HIERRO":  aldeanos * mat.get("HIERRO", 0) / 3600,
        "ORO":     aldeanos * mat.get("ORO",    0) / 3600,
        "CARBON":  aldeanos * mat.get("CARBON", 0) / 3600,
    }

    # Maná por segundo (sacerdotes × tasa_por_nivel)
    mana_por_hora = mana_tasas.get(nivel_sac, mana_tasas.get(1, 1)) * sacerdotes
    tasas["MANA"] = mana_por_hora / 3600

    # Aldeanos por hora del CC
    tasas["ALDEANOS_POR_HORA"] = cc_tasas.get(nivel_cc, 1200)

    return tasas


def aplicar_produccion(city: dict, unit_levels: dict = None) -> dict:
    """
    Aplica producción retroactiva desde LAST_PROD hasta ahora.
    Modifica city in-place y retorna las tasas calculadas.
    Retroactivo máximo: 3 días.
    """
    if unit_levels is None:
        unit_levels = {}
    ahora = time.time()
    last  = float(city.get("LAST_PROD", ahora - MAX_RETROACTIVO_SEG))

    # Máximo retroactivo: 3 días
    last = max(last, ahora - MAX_RETROACTIVO_SEG)
    segundos = max(0.0, ahora - last)

    tasas = calcular_tasas(city, unit_levels)

    # Caps de almacén y santuario
    nivel_almacen   = int(city.get("ALMACEN", 1) or 1)
    nivel_santuario = int(city.get("SANTUARIO_ARCANO", 1) or 1)
    almacen_caps    = get_almacen_caps()
    santuario_caps  = get_santuario_caps()
    _max_alm = max(almacen_caps.keys()) if almacen_caps else 1
    _max_san = max(santuario_caps.keys()) if santuario_caps else 1
    cap_material = almacen_caps.get(nivel_almacen, almacen_caps.get(_max_alm, 1e300))
    cap_mana     = santuario_caps.get(nivel_santuario, santuario_caps.get(_max_san, 1e300))

    # Aplicar producción a cada recurso con cap de almacén
    for recurso in ["MADERA", "PIEDRA", "HIERRO", "ORO", "CARBON"]:
        if cap_material >= 1e50:
            # Almacén nv50 = infinito — recurso pasa a __INF__ directamente
            city[recurso] = "__INF__"
        else:
            ganado = tasas[recurso] * segundos
            actual = safe_resource_float(city.get(recurso, 0))
            if actual < 1e50:
                city[recurso] = min(actual + ganado, cap_material)

    # Maná con cap de santuario
    actual_mana = safe_resource_float(city.get("MANA", 0))
    ganado_mana = tasas["MANA"] * segundos
    if cap_mana >= 1e50:
        # Santuario nv50 = infinito — maná pasa a __INF__ directamente
        city["MANA"] = "__INF__"
    elif actual_mana < 1e50:
        city["MANA"] = min(actual_mana + ganado_mana, cap_mana)

    # Aldeanos — CC produce X aldeanos/hora, cap = capacidad de la Casa
    nivel_casa  = int(city.get("CASA", 1) or 1)
    casa_caps   = get_casa_caps()
    _max_casa   = max(casa_caps.keys()) if casa_caps else 1
    cap_casa    = casa_caps.get(nivel_casa, casa_caps.get(_max_casa, 1e300))
    aldeanos_actuales = float(city.get("ALDEANO", 0) or 0)
    aldeanos_por_hora = tasas.get("ALDEANOS_POR_HORA", 0)
    ganados = aldeanos_por_hora / 3600 * segundos
    if cap_casa >= 1e50:
        city["ALDEANO"] = aldeanos_actuales + ganados
    elif aldeanos_actuales < cap_casa:
        city["ALDEANO"] = min(aldeanos_actuales + ganados, cap_casa)

    # Actualizar timestamp
    city["LAST_PROD"] = ahora

    return tasas


def init_last_prod(city: dict):
    """
    Si la ciudad no tiene LAST_PROD, inicializa a hace 3 días
    para que en el primer tick se aplique la retroactividad completa.
    """
    if "LAST_PROD" not in city:
        city["LAST_PROD"] = time.time() - MAX_RETROACTIVO_SEG
