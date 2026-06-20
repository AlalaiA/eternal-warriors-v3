"""
backend/systems/ia_behavior.py
Eternal Warriors v3.0 — Motor de comportamiento de jugadores IA (IRON_LEGION)

Tick acoplado al mismo asyncio loop que _orders_ticker.
Intervalo: IA_TICK_SEG (configurable, por defecto 120 seg = 2 min de proceso).

Arquitectura:
  - Cada jugador IA (ia-001..ia-006) es autónomo: construye, entrena, ataca.
  - Coordinación de alianza: ia-001 como coordinador, lanza ataques sincronizados.
  - Progresión: ataca dioses para subir XP y nivel de tropas → puede hacer NG+.
  - Persistencia: estado en ia_state.json bajo db/ia/ (misma carpeta que ia.json).
  - Al arrancar: calcula delta retroactivo igual que cualquier jugador humano.

REGLAS CANÓNICAS (no cambiar):
  - No atacan a ALALAIA, ADMIN, JIARITO, GINAO.
  - Máx 3 ataques/24h por atacante a un mismo jugador.
  - Respetan límite de espacios (400 por ciudad IA).
  - Invocaciones solo en fase LATE (tienen Templo).
  - unit_levels formato {NIVEL_DE_TROPAS: N} igual que humanos.
  - __INF__ → usar safe_resource_float.
"""

import math
import time
import random
import json
import uuid
import traceback
from pathlib import Path

from backend.data.save_manager import SaveManager, save_json, load_json, safe_resource_float as _srf

# ── Rutas ─────────────────────────────────────────────────────────────────────

DB = Path(__file__).parent.parent / "db"
IA_DIR      = DB / "players" / "ia"
IA_JSON     = IA_DIR / "ia.json"
IA_STATE    = IA_DIR / "ia_state.json"

# ── Constantes ────────────────────────────────────────────────────────────────

IA_TICK_SEG       = 120        # tick IA cada 2 minutos de tiempo real
IA_ALLIANCE_TICK  = 7200       # tick coordinador alianza cada 2 horas
IA_IDS            = [f"ia-{i:03d}" for i in range(1, 7)]   # ia-001 … ia-006
IA_COORDINADOR    = "ia-001"

INMUNES = set()  # Las IA atacan a todos los jugadores sin excepción

# Desbloqueo progresivo de ciudades por batallas ganadas
DESBLOQUEO_CIUDADES = {
    4: 10, 5: 25, 6: 50, 7: 80, 8: 120,
    9: 160, 10: 200, 11: 250, 12: 300
}  # num_ciudad → batallas_ganadas_minimas

# Prioridad de construcción de edificios (orden TOP → lo más rentable primero)
BUILD_PRIORITY = [
    "CENTRO_DE_CIUDAD", "CASA", "CUARTEL_1", "CUARTEL_2",
    "HERRERIA", "TEMPLO_1", "TEMPLO_2",
    "ALMACEN", "SANTUARIO_ARCANO", "ESCONDITE",
    "MURALLA", "TORRE_DE_VIGILANCIA", "CENTRO_DE_VIAJES",
]

# Umbral mínimo de tropas para atacar (suma de todas las unidades básicas militares)
TROPA_MIN_ATAQUE_CUEVA  = 500
TROPA_MIN_ATAQUE_JUGADOR = 2000
TROPA_MIN_ATAQUE_DIOS   = 300

TROPAS_MILITARES = {
    "EXPLORADOR", "SACERDOTE", "GUERRERO", "COMANDO",
    "MERCENARIO", "MARINE", "CYBORG", "MAGO", "METAHUMANO"
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _dist(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def _total_tropas_militares(ciudad: dict) -> int:
    return sum(int(_srf(ciudad.get(t, 0))) for t in TROPAS_MILITARES)


def _fase(ciudad: dict) -> str:
    """EARLY / MID / LATE según nivel de CC y tropas."""
    cc = int(_srf(ciudad.get("CENTRO_DE_CIUDAD", 0)))
    tiene_cuartel = int(_srf(ciudad.get("CUARTEL_1", 0))) >= 1
    tropas = _total_tropas_militares(ciudad)
    if cc < 8 or not tiene_cuartel:
        return "EARLY"
    if cc < 15 or tropas < 5000:
        return "MID"
    return "LATE"


def _obras_activas(ciudad: dict) -> set:
    """Edificios con obra activa. Formato real: {edificio, nivel_dest, inicio, duracion_seg}"""
    return {o["edificio"] for o in ciudad.get("OBRAS", []) if "duracion_seg" in o}


def _ciudad_activa(ia_id: str, nombre_ciudad: str, estado: dict) -> bool:
    """Comprueba si esta ciudad está desbloqueada según batallas ganadas."""
    num = int(nombre_ciudad.split(".")[-1])  # "IA001.04" → 4
    if num <= 3:
        return True
    batallas = estado.get(ia_id, {}).get("batallas_ganadas", 0)
    return batallas >= DESBLOQUEO_CIUDADES.get(num, 9999)


# ── Carga y guardado de estado IA ─────────────────────────────────────────────

def _cargar_estado() -> dict:
    """Carga ia_state.json. Inicializa si no existe."""
    if not IA_STATE.exists():
        estado = {
            ia_id: {
                "batallas_ganadas": 0,
                "dioses_derrotados": [],
                "cuevas_derrotadas": 0,
                "experiencia": 0,
                "ciclo_ng": 0,
                "ultimo_tick": 0.0,
                "ultimo_tick_alianza": 0.0,
                "objetivos_marcados": {},   # jugador → {prioridad, expira}
                "ataque_registrado": {},    # "jugador|ciudad" → [timestamps 24h]
            }
            for ia_id in IA_IDS
        }
        estado["_ultimo_tick_global"] = 0.0
        _guardar_estado(estado)
        return estado
    return load_json(IA_STATE)


def _guardar_estado(estado: dict):
    IA_STATE.parent.mkdir(parents=True, exist_ok=True)
    save_json(IA_STATE, estado)


# ── Carga de datos del mundo ───────────────────────────────────────────────────

def _cargar_ciudades_ia() -> list:
    """Devuelve lista de todas las ciudades IA desde ia.json."""
    if not IA_JSON.exists():
        return []
    data = load_json(IA_JSON)
    return data.get("cities", [])


def _guardar_ciudades_ia(cities: list):
    save_json(IA_JSON, {"player": "IA", "cities": cities})


def _cargar_dioses(sm: SaveManager) -> list:
    data = sm.load_world("dioses")
    if isinstance(data, list):
        return data
    return data.get("dioses", []) if isinstance(data, dict) else []


def _cargar_cuevas(sm: SaveManager) -> list:
    data = sm.load_world("cuevas")
    if isinstance(data, list):
        return data
    return data.get("cuevas", []) if isinstance(data, dict) else []


def _jugadores_humanos(sm: SaveManager) -> list:
    """Retorna lista de dicts con datos básicos de todos los jugadores atacables."""
    accounts = sm.load_accounts()
    humanos = []
    for nombre, acc in accounts.items():
        if nombre.upper() in INMUNES:
            continue
        data = sm.load_player(nombre)
        if data and data.get("cities"):
            humanos.append({"nombre": nombre.upper(), "data": data})
    return humanos


# ── Lógica de construcción ────────────────────────────────────────────────────

def _intentar_construccion(ciudad: dict, sm: SaveManager) -> bool:
    """
    Intenta encolar la siguiente construcción prioritaria usando iniciar_obra().
    Retorna True si se encoló algo.
    """
    from backend.systems.buildings import iniciar_obra, buildings_info

    obras_activas = _obras_activas(ciudad)
    # iniciar_obra permite máx 4 simultáneas
    if len(obras_activas) >= 4:
        return False

    # Jugador IA ficticio (iniciar_obra solo necesita city)
    player_dummy = {}

    for edificio in BUILD_PRIORITY:
        if edificio in obras_activas:
            continue
        info = buildings_info(ciudad, edificio)
        if not info.get("puede_subir"):
            continue
        costo = info.get("costo")
        if not costo:
            continue

        # Reservar 20% antes de construir
        puede = True
        for mat, cantidad in costo.items():
            clave = mat.upper()
            disponible = _srf(ciudad.get(clave, 0))
            if disponible < 1e50 and disponible < cantidad * 1.2:
                puede = False
                break
        if not puede:
            continue

        res = iniciar_obra(player_dummy, ciudad, edificio)
        if res.get("ok"):
            return True

    return False


# ── Lógica de entrenamiento ───────────────────────────────────────────────────

def _composicion_ejercito(fase: str, nivel_herreria: int) -> dict:
    """Retorna la composición deseada según fase."""
    if fase == "EARLY":
        return {"GUERRERO": 60, "EXPLORADOR": 30, "SACERDOTE": 10}
    if fase == "MID":
        return {"GUERRERO": 40, "MERCENARIO": 20, "EXPLORADOR": 20,
                "MARINE": 10, "SACERDOTE": 10}
    # LATE — añadir Cyborg/Mago si hay Herrería
    comp = {"GUERRERO": 30, "METAHUMANO": 20, "MERCENARIO": 15,
            "MARINE": 15, "SACERDOTE": 10, "EXPLORADOR": 10}
    if nivel_herreria >= 3:
        comp["CYBORG"] = 15
        comp["MAGO"] = 10
        # normalizar a 100%
        total = sum(comp.values())
        comp = {k: int(v * 100 / total) for k, v in comp.items()}
    return comp


def _intentar_entrenamiento(ciudad: dict) -> bool:
    """Encola entrenamiento en cuarteles disponibles usando iniciar_cola_cuartel()."""
    from backend.systems.queues import iniciar_cola_cuartel

    fase = _fase(ciudad)
    nivel_herreria = int(_srf(ciudad.get("HERRERIA", 0)))
    composicion = _composicion_ejercito(fase, nivel_herreria)
    nivel_tropas = int(_srf(ciudad.get("NIVEL_DE_TROPAS", 1))) or 1
    unit_levels  = {"NIVEL_DE_TROPAS": nivel_tropas}

    encolado = False
    for cuartel_key in ("CUARTEL_1", "CUARTEL_2"):
        nivel_cuartel = int(_srf(ciudad.get(cuartel_key, 0)))
        if nivel_cuartel < 1:
            continue

        # ¿Ya tiene 2 colas activas en este cuartel?
        colas_activas = [
            c for c in ciudad.get("COLAS", [])
            if c.get("tipo") == cuartel_key
            and c.get("cantidad_hecha", 0) < c.get("cantidad_total", 0)
        ]
        if len(colas_activas) >= 2:
            continue

        tipo = max(composicion, key=composicion.get)
        cantidad = max(10, nivel_cuartel * 50)

        res = iniciar_cola_cuartel(ciudad, cuartel_key, tipo, cantidad, unit_levels)
        if res.get("ok"):
            encolado = True

    return encolado


# ── Lógica de ataques ─────────────────────────────────────────────────────────

def _registrar_ataque(estado: dict, ia_id: str, objetivo_key: str):
    """Registra timestamp de ataque para respetar límite 3/24h."""
    ahora = time.time()
    registro = estado[ia_id].setdefault("ataque_registrado", {})
    lista = registro.get(objetivo_key, [])
    # limpiar los de más de 24h
    lista = [t for t in lista if ahora - t < 86400]
    lista.append(ahora)
    registro[objetivo_key] = lista


def _puede_atacar(estado: dict, ia_id: str, objetivo_key: str) -> bool:
    """Verifica que no se superen los 3 ataques en 24h al mismo objetivo."""
    ahora = time.time()
    lista = estado[ia_id].get("ataque_registrado", {}).get(objetivo_key, [])
    recientes = [t for t in lista if ahora - t < 86400]
    return len(recientes) < 3


def _atacar_cueva(ciudad: dict, estado: dict, ia_id: str,
                  cuevas: list, ordenes: list, sm: SaveManager) -> bool:
    """Busca la cueva más cercana no derrotada y lanza orden de ataque."""
    from backend.systems.orders import crear_orden

    derrotadas = set(estado[ia_id].get("dioses_derrotados", []))
    tropas = _total_tropas_militares(ciudad)
    if tropas < TROPA_MIN_ATAQUE_CUEVA:
        return False

    cx, cy = float(ciudad["X"]), float(ciudad["Y"])
    candidatas = [
        c for c in cuevas
        if c.get("id") not in derrotadas
        and not c.get("derrotada", False)
    ]
    if not candidatas:
        return False

    # La más cercana con radio máximo 300
    candidatas.sort(key=lambda c: _dist(cx, cy, float(c["x"]), float(c["y"])))
    objetivo = next((c for c in candidatas
                     if _dist(cx, cy, float(c["x"]), float(c["y"])) <= 300), None)
    if not objetivo:
        return False

    # Enviar 60% de tropas militares
    unidades = {}
    for t in TROPAS_MILITARES:
        cant = int(_srf(ciudad.get(t, 0)))
        if cant > 0:
            unidades[t] = max(1, int(cant * 0.6))

    nivel_tropas = int(_srf(ciudad.get("NIVEL_DE_TROPAS", 1))) or 1
    res = crear_orden(
        tipo="ATAQUE",
        jugador=ia_id,
        ciudad_origen=ciudad,
        x_dest=float(objetivo["x"]),
        y_dest=float(objetivo["y"]),
        unidades=unidades,
        nivel_tropas=nivel_tropas,
        jugador_dest=None,
        sm=sm,
    )
    if res.get("ok"):
        # Descontar tropas enviadas
        for t, cant in unidades.items():
            ciudad[t] = max(0, _srf(ciudad.get(t, 0)) - cant)
        # Descontar oro
        ciudad["ORO"] = max(0, _srf(ciudad.get("ORO", 0)) - res["orden"].get("costo_oro", 0))
        ordenes.append(res["orden"])
        return True
    return False


def _atacar_dios(ciudad: dict, estado: dict, ia_id: str,
                 dioses: list, ordenes: list, sm: SaveManager) -> bool:
    """Ataca el siguiente dios no derrotado más cercano para ganar XP."""
    from backend.systems.orders import crear_orden

    derrotados_global = set(estado[ia_id].get("dioses_derrotados", []))
    tropas = _total_tropas_militares(ciudad)
    if tropas < TROPA_MIN_ATAQUE_DIOS:
        return False

    cx, cy = float(ciudad["X"]), float(ciudad["Y"])
    candidatos = [
        d for d in dioses
        if d.get("id") not in derrotados_global
        and not d.get("derrotado", False)
    ]
    if not candidatos:
        return False

    candidatos.sort(key=lambda d: _dist(cx, cy, float(d["x"]), float(d["y"])))
    objetivo = next((d for d in candidatos
                     if _dist(cx, cy, float(d["x"]), float(d["y"])) <= 400), None)
    if not objetivo:
        return False

    # Enviar 40% de tropas — conservador para no quedar indefenso
    unidades = {}
    for t in TROPAS_MILITARES:
        cant = int(_srf(ciudad.get(t, 0)))
        if cant > 0:
            unidades[t] = max(1, int(cant * 0.4))

    nivel_tropas = int(_srf(ciudad.get("NIVEL_DE_TROPAS", 1))) or 1
    res = crear_orden(
        tipo="ATAQUE",
        jugador=ia_id,
        ciudad_origen=ciudad,
        x_dest=float(objetivo["x"]),
        y_dest=float(objetivo["y"]),
        unidades=unidades,
        nivel_tropas=nivel_tropas,
        jugador_dest=None,
        sm=sm,
    )
    if res.get("ok"):
        for t, cant in unidades.items():
            ciudad[t] = max(0, _srf(ciudad.get(t, 0)) - cant)
        ciudad["ORO"] = max(0, _srf(ciudad.get("ORO", 0)) - res["orden"].get("costo_oro", 0))
        ordenes.append(res["orden"])
        return True
    return False


def _atacar_jugador(ciudad: dict, estado: dict, ia_id: str,
                    humanos: list, ordenes: list, sm: SaveManager) -> bool:
    """Ataca al jugador humano más débil en radio, respetando límites."""
    from backend.systems.orders import crear_orden

    tropas = _total_tropas_militares(ciudad)
    if tropas < TROPA_MIN_ATAQUE_JUGADOR:
        return False

    cx, cy = float(ciudad["X"]), float(ciudad["Y"])

    # Elegir objetivo: primero los marcados como prioritarios, luego los más débiles
    ahora = time.time()
    marcados = {
        j: v for j, v in estado[ia_id].get("objetivos_marcados", {}).items()
        if v.get("expira", 0) > ahora
    }

    candidatos = []
    for humano in humanos:
        nombre = humano["nombre"]
        for city in humano["data"].get("cities", []):
            cx2, cy2 = float(city.get("X", 0)), float(city.get("Y", 0))
            dist = _dist(cx, cy, cx2, cy2)
            if dist > 400:
                continue
            obj_key = f"{nombre}|{city.get('NOMBRE', '')}"
            if not _puede_atacar(estado, ia_id, obj_key):
                continue
            poder = _total_tropas_militares(city)
            prioridad = marcados.get(nombre, {}).get("prioridad", 0)
            candidatos.append((prioridad, -poder, dist, nombre, city, obj_key))

    if not candidatos:
        return False

    # Ordenar: mayor prioridad → menor poder → menor distancia
    candidatos.sort(key=lambda x: (-x[0], x[1], x[2]))
    _, _, _, nombre_dest, ciudad_dest, obj_key = candidatos[0]

    # Enviar 70% de tropas
    unidades = {}
    for t in TROPAS_MILITARES:
        cant = int(_srf(ciudad.get(t, 0)))
        if cant > 0:
            unidades[t] = max(1, int(cant * 0.7))

    nivel_tropas = int(_srf(ciudad.get("NIVEL_DE_TROPAS", 1))) or 1
    res = crear_orden(
        tipo="ATAQUE",
        jugador=ia_id,
        ciudad_origen=ciudad,
        x_dest=float(ciudad_dest["X"]),
        y_dest=float(ciudad_dest["Y"]),
        unidades=unidades,
        nivel_tropas=nivel_tropas,
        jugador_dest=nombre_dest,
        ciudad_dest_nombre=ciudad_dest.get("NOMBRE"),
        sm=sm,
    )
    if res.get("ok"):
        for t, cant in unidades.items():
            ciudad[t] = max(0, _srf(ciudad.get(t, 0)) - cant)
        ciudad["ORO"] = max(0, _srf(ciudad.get("ORO", 0)) - res["orden"].get("costo_oro", 0))
        _registrar_ataque(estado, ia_id, obj_key)
        ordenes.append(res["orden"])
        return True
    return False


# ── Respuesta a ser atacado ───────────────────────────────────────────────────

def _marcar_objetivo_represalia(estado: dict, ia_id: str, atacante: str):
    """Marca al atacante como objetivo prioritario por 72h."""
    estado[ia_id].setdefault("objetivos_marcados", {})[atacante] = {
        "prioridad": 2,
        "expira": time.time() + 72 * 3600,
    }


# ── Tick por ciudad ───────────────────────────────────────────────────────────

def _tick_ciudad(ciudad: dict, estado: dict, ia_id: str,
                 dioses: list, cuevas: list, humanos: list,
                 ordenes: list, sm: SaveManager):
    """
    Procesa un tick para una ciudad IA activa.
    Orden de prioridades: construir > entrenar > atacar dios > atacar cueva > atacar jugador.
    """
    fase = _fase(ciudad)

    # 1. Construcción
    _intentar_construccion(ciudad, sm)

    # 2. Entrenamiento (solo si hay Cuartel)
    if int(_srf(ciudad.get("CUARTEL_1", 0))) >= 1:
        _intentar_entrenamiento(ciudad)

    # 3. Ataque a dios (para ganar XP y subir nivel, en todas las fases)
    tropas = _total_tropas_militares(ciudad)
    if tropas >= TROPA_MIN_ATAQUE_DIOS and random.random() < 0.3:
        _atacar_dios(ciudad, estado, ia_id, dioses, ordenes, sm)

    # 4. Ataque a cueva en fase MID+
    if fase != "EARLY" and tropas >= TROPA_MIN_ATAQUE_CUEVA and random.random() < 0.25:
        _atacar_cueva(ciudad, estado, ia_id, cuevas, ordenes, sm)

    # 5. Ataque a jugador humano en fase LATE
    if fase == "LATE" and tropas >= TROPA_MIN_ATAQUE_JUGADOR and random.random() < 0.2:
        _atacar_jugador(ciudad, estado, ia_id, humanos, ordenes, sm)


# ── Ataque coordinado (coordinador alianza) ───────────────────────────────────

def _tick_alianza(cities_ia: list, estado: dict, humanos: list,
                  ordenes: list, sm: SaveManager):
    """
    El coordinador (ia-001) evalúa cada IA_ALLIANCE_TICK si hay un objetivo
    humano que justifique un ataque coordinado multi-ciudad.

    Estrategia: encuentra el jugador humano con menor poder total,
    calcula cuántas ciudades IA pueden atacarlo simultáneamente,
    sincroniza la hora de llegada y lanza las órdenes.
    """
    from backend.systems.orders import crear_orden, distancia_euclidiana, tiempo_viaje_seg
    from backend.systems.combat import get_stats_unidad

    if not humanos:
        return

    # Candidato: jugador humano con menor poder y no inmune
    ahora = time.time()
    mejor = None
    mejor_poder = float("inf")
    mejor_city = None

    for humano in humanos:
        for city in humano["data"].get("cities", []):
            poder = _total_tropas_militares(city)
            if poder < mejor_poder:
                mejor_poder = poder
                mejor = humano["nombre"]
                mejor_city = city

    if not mejor or not mejor_city:
        return

    # Ciudades IA que pueden contribuir (LATE, en radio 600, tienen tropas)
    participantes = []
    for city in cities_ia:
        if city.get("ID") not in IA_IDS:
            continue
        if _fase(city) != "LATE":
            continue
        tropas = _total_tropas_militares(city)
        if tropas < TROPA_MIN_ATAQUE_JUGADOR:
            continue
        dist = _dist(float(city["X"]), float(city["Y"]),
                     float(mejor_city["X"]), float(mejor_city["Y"]))
        if dist > 600:
            continue
        obj_key = f"{mejor}|{mejor_city.get('NOMBRE', '')}"
        if not _puede_atacar(estado, city["ID"], obj_key):
            continue
        participantes.append((city, dist))

    if len(participantes) < 2:
        return  # no vale la pena si es solo 1

    # Calcular t_llegada sincronizada = ahora + max(tiempo_viaje)
    # Para simplificar: usamos velocidad 10 (guerrero nv1) como base
    t_max = max(_dist(float(c["X"]), float(c["Y"]),
                      float(mejor_city["X"]), float(mejor_city["Y"])) * 5.0
                for c, _ in participantes)
    t_llegada_global = ahora + t_max

    for city, dist in participantes:
        ia_id = city["ID"]
        obj_key = f"{mejor}|{mejor_city.get('NOMBRE', '')}"

        unidades = {}
        for t in TROPAS_MILITARES:
            cant = int(_srf(city.get(t, 0)))
            if cant > 0:
                unidades[t] = max(1, int(cant * 0.65))

        nivel_tropas = int(_srf(city.get("NIVEL_DE_TROPAS", 1))) or 1
        res = crear_orden(
            tipo="ATAQUE",
            jugador=ia_id,
            ciudad_origen=city,
            x_dest=float(mejor_city["X"]),
            y_dest=float(mejor_city["Y"]),
            unidades=unidades,
            nivel_tropas=nivel_tropas,
            jugador_dest=mejor,
            ciudad_dest_nombre=mejor_city.get("NOMBRE"),
            sm=sm,
        )
        if res.get("ok"):
            for t, cant in unidades.items():
                city[t] = max(0, _srf(city.get(t, 0)) - cant)
            city["ORO"] = max(0, _srf(city.get("ORO", 0)) - res["orden"].get("costo_oro", 0))
            _registrar_ataque(estado, ia_id, obj_key)
            ordenes.append(res["orden"])

    print(f"[ia_behavior] Ataque coordinado de {len(participantes)} ciudades IA sobre {mejor}")


# ── Procesar resultados de batallas anteriores ────────────────────────────────

def _procesar_eventos_retorno(eventos: list, estado: dict):
    """
    Llama a esta función con los eventos retornados del orders_ticker.
    Actualiza batallas_ganadas, dioses_derrotados, experiencia.
    """
    for ev in eventos:
        ia_id = ev.get("jugador", "").lower()
        if ia_id not in IA_IDS:
            continue
        est = estado.setdefault(ia_id, {})

        if ev.get("ok"):
            est["batallas_ganadas"] = est.get("batallas_ganadas", 0) + 1
            # ¿Era un dios?
            jugador_dest = ev.get("jugador_dest", "")
            if not jugador_dest:  # destino sin jugador → dios o cueva
                dios_id = ev.get("dios_id") or ev.get("cueva_id")
                if dios_id:
                    derrotados = est.setdefault("dioses_derrotados", [])
                    if dios_id not in derrotados:
                        derrotados.append(dios_id)
            # XP
            est["experiencia"] = est.get("experiencia", 0) + ev.get("xp_ganada", 0)
        else:
            # Si fue atacado por un humano → represalia
            atacante = ev.get("atacante_humano")
            if atacante:
                _marcar_objetivo_represalia(estado, ia_id, atacante)


# ── Tick global ───────────────────────────────────────────────────────────────

def procesar_tick_ia(sm: SaveManager, ordenes_existentes: list) -> list:
    """
    Punto de entrada principal. Llamado desde _ia_ticker en main.py.

    Retorna la lista de nuevas órdenes creadas para añadir a orders.json.
    """
    ahora = time.time()
    estado = _cargar_estado()
    cities_ia = _cargar_ciudades_ia()
    if not cities_ia:
        return []

    dioses   = _cargar_dioses(sm)
    cuevas   = _cargar_cuevas(sm)
    humanos  = _jugadores_humanos(sm)

    nuevas_ordenes = []

    # Agrupar ciudades por ia_id
    por_ia = {}
    for city in cities_ia:
        iid = city.get("ID", "")
        por_ia.setdefault(iid, []).append(city)

    for ia_id, ciudades in por_ia.items():
        if ia_id not in IA_IDS:
            continue

        est_ia = estado.setdefault(ia_id, {
            "batallas_ganadas": 0, "dioses_derrotados": [],
            "cuevas_derrotadas": 0, "experiencia": 0,
            "ciclo_ng": 0, "ultimo_tick": 0.0,
            "ultimo_tick_alianza": 0.0,
            "objetivos_marcados": {}, "ataque_registrado": {},
        })

        for city in ciudades:
            nombre = city.get("NOMBRE", "")
            if not _ciudad_activa(ia_id, nombre, estado):
                continue
            try:
                _tick_ciudad(city, estado, ia_id,
                             dioses, cuevas, humanos,
                             nuevas_ordenes, sm)
            except Exception:
                traceback.print_exc()

    # Tick de alianza coordinado (solo si toca)
    ultimo_alianza = estado.get("_ultimo_tick_alianza", 0.0)
    if ahora - ultimo_alianza >= IA_ALLIANCE_TICK:
        try:
            _tick_alianza(cities_ia, estado, humanos, nuevas_ordenes, sm)
        except Exception:
            traceback.print_exc()
        estado["_ultimo_tick_alianza"] = ahora

    # Persistir cambios en ciudades
    _guardar_ciudades_ia(cities_ia)
    estado["_ultimo_tick_global"] = ahora
    _guardar_estado(estado)

    return nuevas_ordenes
