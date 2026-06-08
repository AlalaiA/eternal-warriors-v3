"""
experience.py — Sistema de XP para Eternal Warriors v3.0
=========================================================
Responsabilidades:
  - Tablas de XP por muerte de unidades básicas (por tipo y nivel)
  - Tablas de XP por muerte de invocaciones (por tipo)
  - XP de entidades del mapa: dioses y cuevas (campo 'experiencia' del CSV)
  - XP por criaturas de cueva en combate JvJ (regresan al mapa pero dan XP)
  - Distribución proporcional entre ejércitos participantes (por número de bandos)
  - Reposición instantánea de cuentas vitaminizadas (ALALAIA, ADMIN)

Regla de distribución:
  XP_total se divide en partes IGUALES entre todos los propietarios
  del bando atacante que participaron (sin importar cuántas tropas aportó cada uno).
  Ejemplo: JOTICALINDO + JIARITO atacan juntos → cada uno recibe XP_total / 2.
"""

import math
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Jugadores vitaminizados — sus ciudades se reponen instantáneamente
# ---------------------------------------------------------------------------
VITAMINIZADOS = {"ALALAIA", "ADMIN"}

# Snapshot de valores canónicos por ciudad vitaminizada.
# Clave: (jugador, nombre_ciudad) → dict con cantidades originales.
# Se puebla la primera vez que se lee el save de cada vitaminizado.
_vitaminizado_snapshot: Dict[tuple, dict] = {}

UNIDADES_VITAMINIZADAS = [
    "ALDEANO","EXPLORADOR","SACERDOTE","GUERRERO","COMANDO","MERCENARIO",
    "MARINE","CYBORG","MAGO","METAHUMANO","DEMONIO","ANIMA","ESPECTRO",
    "GOLEM","CENTAURO","KRAKEN","ALONARDO","MADRESELVA","COLOSO","FENIX",
    "DRAGON_DE_ORO","CABALLERO_DE_LUZ","ALALAIA","EON_SUPREMO",
]

def registrar_snapshot_vitaminizado(jugador: str, ciudad: dict) -> None:
    """
    Llama esto justo después de cargar el JSON de un vitaminizado,
    para guardar las cantidades originales de cada ciudad.
    Solo registra si aún no existe el snapshot de esa ciudad.
    """
    if jugador not in VITAMINIZADOS:
        return
    key = (jugador, ciudad.get("NOMBRE", ""))
    if key not in _vitaminizado_snapshot:
        snap = {u: ciudad.get(u, 0) for u in UNIDADES_VITAMINIZADAS}
        _vitaminizado_snapshot[key] = snap

def reponer_ciudad_vitaminizada(jugador: str, ciudad: dict) -> bool:
    """
    Si el jugador es vitaminizado, restaura todas las unidades de la ciudad
    a sus valores de snapshot. Retorna True si se aplicó reposición.
    """
    if jugador not in VITAMINIZADOS:
        return False
    key = (jugador, ciudad.get("NOMBRE", ""))
    snap = _vitaminizado_snapshot.get(key)
    if snap is None:
        # No hay snapshot aún — registrar el estado actual como canónico
        registrar_snapshot_vitaminizado(jugador, ciudad)
        return False
    for u, v in snap.items():
        ciudad[u] = v
    return True

def necesita_reposicion(jugador: str, ciudad: dict) -> bool:
    """
    Retorna True si alguna unidad de la ciudad vitaminizada bajó respecto
    al snapshot (es decir, fue atacada).
    """
    if jugador not in VITAMINIZADOS:
        return False
    key = (jugador, ciudad.get("NOMBRE", ""))
    snap = _vitaminizado_snapshot.get(key)
    if snap is None:
        return False
    for u, v in snap.items():
        if ciudad.get(u, 0) < v:
            return True
    return False

# ---------------------------------------------------------------------------
# Tablas de XP — construidas una sola vez al importar el módulo
# ---------------------------------------------------------------------------

# XP por muerte de unidad básica: _XP_UNIDAD[(tipo_upper, nivel)] = xp
_XP_UNIDAD: Dict[tuple, int] = {}

# XP por muerte de invocación: _XP_INVOCACION[tipo_upper] = xp
_XP_INVOCACION: Dict[str, int] = {}

def _safe_int(v) -> int:
    try:
        return int(float(str(v).replace(",", ".")))
    except Exception:
        return 0

def _cargar_tablas() -> None:
    import csv, os
    base = os.path.dirname(os.path.abspath(__file__))

    # Intentar rutas relativas al módulo y luego rutas canónicas del proyecto
    csv_dirs = [
        os.path.join(base, "..", "csv"),
        os.path.join(base, "..", "..", "csv"),
        os.path.join(base),
    ]

    def _find_csv(nombre: str) -> Optional[str]:
        for d in csv_dirs:
            p = os.path.join(d, nombre)
            if os.path.exists(p):
                return p
        return None

    # --- Unidades básicas ---
    ruta_u = _find_csv("experiencia_dada_por_unidades_basicas_por_nivel.csv")
    if ruta_u:
        with open(ruta_u, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                tipo = row.get("tipo", "").strip().upper()
                nivel = _safe_int(row.get("nivel", 0))
                xp = _safe_int(row.get("exp", 0))
                if tipo and nivel and xp:
                    _XP_UNIDAD[(tipo, nivel)] = xp

    # --- Invocaciones ---
    ruta_i = _find_csv("experiencia_por_invocaciones.csv")
    if ruta_i:
        with open(ruta_i, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                tipo = row.get("tipo", "").strip().upper()
                xp = _safe_int(row.get("exp", 0))
                if tipo and xp:
                    _XP_INVOCACION[tipo] = xp

_cargar_tablas()

# ---------------------------------------------------------------------------
# API pública de consulta de XP
# ---------------------------------------------------------------------------

# Nombres internos (claves JSON) → nombres canónicos de CSV
_ALIAS_UNIDAD = {
    "ALDEANO": "ALDEANO", "EXPLORADOR": "EXPLORADOR", "SACERDOTE": "SACERDOTE",
    "GUERRERO": "GUERRERO", "COMANDO": "COMANDO", "MERCENARIO": "MERCENARIO",
    "MARINE": "MARINE", "CYBORG": "CYBORG", "MAGO": "MAGO",
    "METAHUMANO": "METAHUMANO",
}
_ALIAS_INVOCACION = {
    "DEMONIO": "DEMONIO", "ANIMA": "ÁNIMA", "ESPECTRO": "ESPECTRO",
    "GOLEM": "GÓLEM", "CENTAURO": "CENTAURO", "KRAKEN": "KRAKEN",
    "ALONARDO": "ALONARDO", "MADRESELVA": "MADRESELVA", "COLOSO": "COLOSO",
    "FENIX": "FÉNIX", "DRAGON_DE_ORO": "DRAGÓN DE ORO",
    "CABALLERO_DE_LUZ": "CABALLERO DE LUZ", "ALALAIA": "ALALAIA",
    "EON_SUPREMO": "ÉON SUPREMO",
}

def xp_por_muerte_unidad(tipo_key: str, nivel: int) -> int:
    """
    Retorna el XP que da matar 1 unidad básica del tipo y nivel dados.
    tipo_key: clave interna JSON (ej. 'GUERRERO', 'EXPLORADOR').
    """
    canon = _ALIAS_UNIDAD.get(tipo_key.upper(), tipo_key.upper())
    return _XP_UNIDAD.get((canon, nivel), 0)

def xp_por_muerte_invocacion(tipo_key: str) -> int:
    """
    Retorna el XP que da matar/capturar 1 invocación del tipo dado.
    tipo_key: clave interna JSON (ej. 'ALALAIA', 'EON_SUPREMO').
    """
    canon = _ALIAS_INVOCACION.get(tipo_key.upper(), tipo_key.upper())
    return _XP_INVOCACION.get(canon, 0)

def xp_por_bajas_grupo(tipo_key: str, nivel_o_none, cantidad_bajas: int) -> int:
    """
    XP total generado por `cantidad_bajas` muertes de un grupo.
    Si el tipo es invocación, nivel_o_none se ignora.
    """
    if tipo_key.upper() in _ALIAS_INVOCACION:
        return xp_por_muerte_invocacion(tipo_key) * cantidad_bajas
    else:
        return xp_por_muerte_unidad(tipo_key, nivel_o_none or 1) * cantidad_bajas

# ---------------------------------------------------------------------------
# Cálculo de XP total de un combate
# ---------------------------------------------------------------------------

def calcular_xp_total_combate(
    bajas_atacante: Dict[str, Dict],
    bajas_defensor: Dict[str, Dict],
    nivel_tropas_atacante: int,
    nivel_tropas_defensor: int,
) -> Dict[str, int]:
    """
    Calcula el XP bruto que genera un combate:
      - ATK gana XP por las bajas que causó al defensor
      - DEF gana XP por las bajas que causó al atacante

    Parámetros
    ----------
    bajas_atacante : dict
        Bajas SUFRIDAS por el atacante. Formato:
        {'GUERRERO': {'cantidad': N, 'nivel': L}, 'ALALAIA': {'cantidad': N}, ...}
    bajas_defensor : dict
        Bajas SUFRIDAS por el defensor (misma estructura).
    nivel_tropas_atacante : int
        Nivel global del atacante (para unidades sin nivel explícito).
    nivel_tropas_defensor : int
        Nivel global del defensor.

    Retorna
    -------
    {'xp_atacante': int, 'xp_defensor': int}
    """
    xp_atk = 0  # XP que gana el atacante (por matar al defensor)
    xp_def = 0  # XP que gana el defensor (por matar al atacante)

    for tipo_key, info in bajas_defensor.items():
        cant = int(info.get("cantidad", 0))
        if cant <= 0:
            continue
        nivel = info.get("nivel", nivel_tropas_defensor) or nivel_tropas_defensor
        xp_atk += xp_por_bajas_grupo(tipo_key, nivel, cant)

    for tipo_key, info in bajas_atacante.items():
        cant = int(info.get("cantidad", 0))
        if cant <= 0:
            continue
        nivel = info.get("nivel", nivel_tropas_atacante) or nivel_tropas_atacante
        xp_def += xp_por_bajas_grupo(tipo_key, nivel, cant)

    return {"xp_atacante": xp_atk, "xp_defensor": xp_def}

# ---------------------------------------------------------------------------
# Distribución proporcional entre propietarios
# ---------------------------------------------------------------------------

def distribuir_xp_entre_propietarios(
    xp_total: int,
    propietarios: List[str],
) -> Dict[str, int]:
    """
    Divide xp_total en partes IGUALES entre todos los propietarios del bando.
    El residuo se asigna al primero de la lista (jugador principal / despachador).

    Parámetros
    ----------
    xp_total : int
        XP total a repartir.
    propietarios : list[str]
        Lista de jugadores que participaron en el bando (sin duplicados).
        Ej: ['JOTICALINDO', 'JIARITO']

    Retorna
    -------
    {'JOTICALINDO': xp_parcial, 'JIARITO': xp_parcial, ...}
    """
    if not propietarios or xp_total <= 0:
        return {p: 0 for p in propietarios}

    n = len(propietarios)
    base = xp_total // n
    residuo = xp_total - base * n

    resultado = {p: base for p in propietarios}
    resultado[propietarios[0]] += residuo
    return resultado

# ---------------------------------------------------------------------------
# XP de entidades del mapa (dioses / cuevas)
# ---------------------------------------------------------------------------

def xp_entidad_mapa(entidad: dict) -> int:
    """
    Retorna el XP del campo 'experiencia' de un dios o cueva del CSV.
    """
    return _safe_int(entidad.get("experiencia", 0))

# ---------------------------------------------------------------------------
# XP por criatura de cueva en combate JvJ
# ---------------------------------------------------------------------------
# En combate JvJ las criaturas de cueva no mueren: regresan al mapa.
# Pero SÍ generan XP para quien las "mata" (el bando que las elimina del campo).
# Usamos el mismo campo 'experiencia' del CSV de cuevas como valor de XP.

def xp_por_criatura_cueva_jvj(entidad_cueva: dict, cantidad: int = 1) -> int:
    """
    XP que da eliminar `cantidad` criaturas de cueva en combate JvJ.
    La criatura regresa al mapa pero el matador recibe este XP.
    """
    return xp_entidad_mapa(entidad_cueva) * cantidad
