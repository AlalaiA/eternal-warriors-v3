"""
backend/systems/orders.py
Eternal Warriors v3.0 — Sistema de órdenes

Tipos de orden:
  ATAQUE       — ejército atacante viaja a ciudad enemiga, combate al llegar
  ESPIONAJE    — pelotón espía viaja a ciudad enemiga, sigilo o combate al llegar
  DESPLAZAMIENTO — tropas se mueven de una ciudad propia a otra
  TRANSPORTE   — recursos se mueven de una ciudad propia a otra
  FUNDAR       — exploradores fundan una nueva ciudad en coordenadas vacías

Reglas generales:
  - Costo: 10 oro por tile (distancia euclidiana) por orden, cobrado al despachar
  - Sin oro suficiente → orden rechazada
  - Tiempo de viaje: distancia_euclidiana × (50 / velocidad_más_lenta) segundos
  - Velocidad más lenta = min(velocidad) de todas las unidades del grupo
  - Tras ATAQUE/ESPIONAJE exitoso: tropas regresan automáticamente con botín
  - Zona prohibida KarlakÁ: radio cuadrado 50 tiles centrado en (500, 500)
  - Mapa: 1000×1000 tiles

Fundar Ciudad:
  - Solo Exploradores
  - Tiempo base: 100 horas
  - Reducción multiplicativa: (1 - nivel/100) por nivel de explorador
    luego (1 - nivel/100) adicional por cada 10.000 exploradores enviados
"""

import math
import time
from backend.data.save_manager import safe_resource_float as _srf
import uuid
from pathlib import Path

# ── Constantes ────────────────────────────────────────────────────────────────

MAPA_SIZE        = 1000
KARLAKA_X        = 500
KARLAKA_Y        = 500
KARLAKA_RADIO    = 50          # radio cuadrado (±50 en X e Y)
COSTO_ORO_TILE   = 10.0        # oro por tile euclidiano
SEG_POR_TILE_BASE = 5.0        # segundos por tile para velocidad base 10
VELOCIDAD_BASE   = 10.0        # velocidad del aldeano Nv1
FUNDAR_HORAS_BASE = 100.0      # horas base para fundar ciudad

TIPOS_VALIDOS = {"ATAQUE", "ESPIONAJE", "DESPLAZAMIENTO", "TRANSPORTE", "FUNDAR"}

# ── Fórmulas base ─────────────────────────────────────────────────────────────

def distancia_euclidiana(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def _nivel_tropas_player(player: dict, unidades: dict = None) -> int:
    """
    Lee el nivel de tropas de un jugador.
    Soporta ambos formatos:
      - {NIVEL_DE_TROPAS: 20} (formato joticalindo)
      - {EXPLORADOR: 40, GUERRERO: 40, ...} (formato jiarito)
    Si se pasan unidades, usa el nivel más alto de esas unidades específicas.
    """
    ul = player.get("unit_levels", {})
    if "NIVEL_DE_TROPAS" in ul:
        return int(ul["NIVEL_DE_TROPAS"] or 1)
    if unidades:
        niveles = [int(ul.get(u.upper(), 1) or 1) for u in unidades if int((unidades or {}).get(u, 0) or 0) > 0]
        return max(niveles) if niveles else 1
    valores = [int(v or 1) for v in ul.values() if isinstance(v, (int, float))]
    return max(valores) if valores else 1


def segundos_por_tile(velocidad: float) -> float:
    """50 / velocidad — unidad más lenta marca el ritmo."""
    return 50.0 / max(velocidad, 0.001)


def tiempo_viaje_seg(distancia: float, velocidad_min: float) -> float:
    return distancia * segundos_por_tile(velocidad_min)


def costo_oro(distancia: float, cantidad_basicas: int = 1) -> float:
    """10 oro × distancia × unidades básicas enviadas."""
    return math.ceil(distancia * COSTO_ORO_TILE * max(1, cantidad_basicas))


def _zona_karlaka(x: float, y: float) -> bool:
    """True si (x, y) está dentro del radio cuadrado de KarlakÁ."""
    return (abs(x - KARLAKA_X) <= KARLAKA_RADIO and
            abs(y - KARLAKA_Y) <= KARLAKA_RADIO)


def _coordenadas_validas(x: float, y: float) -> bool:
    return (0 <= x <= MAPA_SIZE and
            0 <= y <= MAPA_SIZE and
            not _zona_karlaka(x, y))


# ── Velocidad mínima de un pelotón ────────────────────────────────────────────

def velocidad_minima(unidades_dict: dict, nivel_tropas: int,
                     grupos_extra: list = None) -> float:
    """
    Retorna la velocidad mínima del pelotón.
    grupos_extra: [{"unidades": dict, "nivel_tropas": int}] para tropas prestadas.
    """
    from backend.systems.combat import (
        get_stats_unidad, get_stats_invocacion, _norm, INVOCACIONES
    )
    vel_min = float("inf")

    def _vel_unidad(nombre_raw, nivel):
        nombre = _norm(nombre_raw)
        if nombre in INVOCACIONES or nombre == "KARLAKA":
            st = get_stats_invocacion(nombre)
        else:
            st = get_stats_unidad(nombre, nivel)
        return st.get("velocidad", VELOCIDAD_BASE)

    for nombre_raw, cantidad in unidades_dict.items():
        if int(cantidad or 0) <= 0:
            continue
        vel_min = min(vel_min, _vel_unidad(nombre_raw, nivel_tropas))
    for grupo in (grupos_extra or []):
        nivel = grupo.get("nivel_tropas", 1)
        for nombre_raw, cantidad in grupo.get("unidades", {}).items():
            if int(cantidad or 0) <= 0:
                continue
            vel_min = min(vel_min, _vel_unidad(nombre_raw, nivel))
    return vel_min if vel_min != float("inf") else VELOCIDAD_BASE


# ── Tiempo de fundación ───────────────────────────────────────────────────────

def tiempo_fundar_seg(nivel_exploradores: int, cantidad_exploradores: int) -> float:
    """
    Tiempo base: 100 horas.
    Reducción multiplicativa:
      - 1 vez: (1 - nivel/100) por el nivel del explorador
      - luego (1 - nivel/100) adicional por cada 10.000 exploradores
    Resultado en segundos.
    """
    base_seg  = FUNDAR_HORAS_BASE * 3600.0
    pct       = nivel_exploradores / 100.0          # fracción de reducción
    factor    = 1.0 - pct                           # ej. nivel 40 → factor 0.60

    # Reducción por nivel (1 vez)
    tiempo = base_seg * factor

    # Reducción adicional por cada 10.000 exploradores
    bloques = cantidad_exploradores // 10_000
    for _ in range(bloques):
        tiempo *= factor

    return max(tiempo, 1.0)   # mínimo 1 segundo


# ── Crear orden ───────────────────────────────────────────────────────────────

def crear_orden(
    tipo: str,
    jugador: str,
    ciudad_origen: dict,
    x_dest: float,
    y_dest: float,
    unidades: dict = None,
    recursos: dict = None,
    nivel_tropas: int = 1,
    jugador_dest: str = None,
    ciudad_dest_nombre: str = None,
    unidades_prestadas: dict = None,   # {jugador_dueño: {unidad: cantidad}}
    sm = None,                         # SaveManager para leer stats de propietarios
) -> dict:
    """
    Valida y crea una orden lista para encolar.

    Retorna:
        {"ok": True, "orden": {...}}
        {"ok": False, "msg": str}
    """
    tipo = tipo.upper()
    if tipo not in TIPOS_VALIDOS:
        return {"ok": False, "msg": f"Tipo de orden inválido: {tipo}"}

    unidades           = unidades  or {}
    recursos           = recursos  or {}
    unidades_prestadas = unidades_prestadas or {}
    x_orig    = float(ciudad_origen.get("X", 0))
    y_orig    = float(ciudad_origen.get("Y", 0))
    x_dest    = float(x_dest)
    y_dest    = float(y_dest)

    # ── Validar destino ───────────────────────────────────────────────────────
    if not (0 <= x_dest <= MAPA_SIZE and 0 <= y_dest <= MAPA_SIZE):
        return {"ok": False, "msg": "Coordenadas fuera del mapa (0-1000)"}

    if tipo == "FUNDAR" and _zona_karlaka(x_dest, y_dest):
        return {"ok": False, "msg": "No se puede fundar en la zona de KarlakÁ (radio 50 alrededor de 500,500)"}

    # ── Distancia y tiempos ───────────────────────────────────────────────────
    distancia = distancia_euclidiana(x_orig, y_orig, x_dest, y_dest)
    if distancia == 0 and tipo not in {"FUNDAR"}:
        return {"ok": False, "msg": "El origen y el destino son la misma casilla"}

    # ── Costo de oro — solo si hay unidades básicas ───────────────────────────
    INV_KEYS = {
        "DEMONIO","ANIMA","ESPECTRO","GOLEM","CENTAURO","KRAKEN",
        "ALONARDO","MADRESELVA","COLOSO","FENIX","DRAGON DE ORO",
        "CABALLERO DE LUZ","ALALAIA","EON SUPREMO",
    }
    from backend.systems.combat import _norm as _cnorm
    cantidad_basicas = sum(
        int(v or 0) for k, v in unidades.items()
        if _cnorm(k) not in INV_KEYS and int(v or 0) > 0
    )
    oro_costo = costo_oro(distancia, cantidad_basicas) if cantidad_basicas > 0 else 0.0
    oro_actual = _srf(ciudad_origen.get("ORO", 0))
    if oro_actual < oro_costo:
        return {"ok": False, "msg": f"Oro insuficiente: necesitas {oro_costo:,.0f}, tienes {oro_actual:,.0f}"}

    # ── Validaciones específicas por tipo ─────────────────────────────────────
    if tipo in {"ATAQUE", "ESPIONAJE", "DESPLAZAMIENTO"}:
        total_u = sum(int(v or 0) for v in unidades.values())
        total_p = sum(
            int(v or 0)
            for unids in unidades_prestadas.values()
            for v in unids.values()
        )
        if total_u + total_p <= 0:
            return {"ok": False, "msg": "Debes enviar al menos una unidad"}

    # ── Validar ataque a dios ya derrotado (temprano, antes del viaje) ──────────
    if tipo == "ATAQUE" and not jugador_dest and sm:
        try:
            mundo_dioses = sm.load_world("dioses")
            for e in mundo_dioses.get("entities", []):
                ex, ey = float(e.get("X", -1)), float(e.get("Y", -1))
                if abs(ex - x_dest) <= 1.0 and abs(ey - y_dest) <= 1.0:
                    # Es un dios — verificar si ya fue derrotado por este jugador
                    if e.get("_derrotado") or int(e.get("HP", 1)) <= 0:
                        return {"ok": False, "msg": f"{e.get('NOMBRE','Este dios')} ya fue derrotado y no puede ser atacado de nuevo"}
                    # Verificar si este jugador específicamente ya lo venció
                    jugador_data = sm.load_player(jugador)
                    da = jugador_data.get("dioses_abatidos", [])
                    if isinstance(da, int): da = []
                    eid = str(e.get("ID", ""))
                    if eid and eid in da:
                        return {"ok": False, "msg": f"Ya derrotaste a {e.get('NOMBRE','este dios')} — un dios solo puede ser vencido una vez por jugador"}
                    break
        except Exception:
            pass  # Si falla la consulta, no bloquear

    if tipo == "TRANSPORTE":
        if not any(_srf(v) > 0 for v in recursos.values()):
            return {"ok": False, "msg": "Debes enviar al menos un recurso"}
        # Verificar que la ciudad tiene esos recursos
        for rec, cant in recursos.items():
            disponible = _srf(ciudad_origen.get(rec, 0))
            if disponible < float(cant or 0):
                return {"ok": False, "msg": f"No tienes suficiente {rec}: necesitas {cant:,.0f}, tienes {disponible:,.0f}"}

    if tipo == "FUNDAR":
        exploradores = int(unidades.get("EXPLORADOR", 0) or 0)
        if exploradores <= 0:
            return {"ok": False, "msg": "Fundar ciudad requiere al menos 1 Explorador"}
        if len([u for u, v in unidades.items() if int(v or 0) > 0 and u != "EXPLORADOR"]) > 0:
            return {"ok": False, "msg": "Solo Exploradores pueden fundar ciudades"}

    # ── Calcular velocidad mínima y tiempo de viaje ───────────────────────────
    if tipo == "TRANSPORTE":
        # Transportes usan aldeanos/exploradores implícitamente — sin unidades → vel base
        vel_min = VELOCIDAD_BASE
    elif tipo == "FUNDAR":
        vel_min = velocidad_minima({"EXPLORADOR": unidades.get("EXPLORADOR", 1)}, nivel_tropas)
    else:
        _grupos_prest = []
        for dueño, unids in (unidades_prestadas or {}).items():
            if any(int(v or 0) > 0 for v in unids.values()):
                try:
                    from backend.data.save_manager import SaveManager as _SM
                    _sm_local = sm if sm is not None else _SM()
                    _player_d = _sm_local.load_player(dueño)
                    _ul = _player_d.get("unit_levels", {})
                    # unit_levels puede ser {UNIDAD: nivel} o tener NIVEL_DE_TROPAS global
                    if "NIVEL_DE_TROPAS" in _ul:
                        _nivel_d = int(_ul["NIVEL_DE_TROPAS"] or 1)
                    else:
                        # Usar el nivel más alto de las unidades prestadas
                        niveles = [int(_ul.get(u.upper(), 1) or 1) for u in unids]
                        _nivel_d = max(niveles) if niveles else 1
                except Exception:
                    _nivel_d = 1
                _grupos_prest.append({"unidades": unids, "nivel_tropas": _nivel_d})
        vel_min = velocidad_minima(unidades, nivel_tropas, _grupos_prest)

    t_viaje   = tiempo_viaje_seg(distancia, vel_min)
    t_regreso = t_viaje  # mismo tiempo de vuelta

    # Tiempo extra para FUNDAR
    t_fundar = 0.0
    if tipo == "FUNDAR":
        t_fundar = tiempo_fundar_seg(nivel_tropas, int(unidades.get("EXPLORADOR", 1)))

    ahora     = time.time()
    t_llegada = ahora + t_viaje
    t_retorno = t_llegada + t_fundar + (t_regreso if tipo in {"ATAQUE","ESPIONAJE"} else 0)

    # ── Descontar oro y recursos de la ciudad ─────────────────────────────────
    ciudad_origen["ORO"] = oro_actual - oro_costo

    if tipo == "TRANSPORTE":
        for rec, cant in recursos.items():
            ciudad_origen[rec] = float(ciudad_origen.get(rec, 0) or 0) - float(cant or 0)

    if tipo in {"ATAQUE","ESPIONAJE","DESPLAZAMIENTO","FUNDAR"}:
        for nombre, cant in unidades.items():
            cant = int(cant or 0)
            if cant > 0:
                ciudad_origen[nombre] = max(0, int(ciudad_origen.get(nombre, 0) or 0) - cant)
        # Validar que ataque a entidad del mundo no tenga tropas prestadas
    if tipo == "ATAQUE" and unidades_prestadas:
        # Comprobar si el destino es dios o cueva
        _es_entidad = False
        for _wk in ["dioses", "cuevas"]:
            try:
                _mundo = sm.load_world(_wk)
                for _e in _mundo.get("entities", []):
                    if (abs(float(_e.get("X", -999)) - x_dest) <= 1.0 and
                            abs(float(_e.get("Y", -999)) - y_dest) <= 1.0):
                        _es_entidad = True
                        break
            except Exception:
                pass
            if _es_entidad:
                break
        if _es_entidad:
            return {"ok": False, "msg": "El combate contra dioses y cuevas debe ser individual — retira las tropas prestadas"}

    # Descontar tropas prestadas de TROPAS_PRESTADAS
        prestadas = ciudad_origen.setdefault("TROPAS_PRESTADAS", [])
        for dueño, unids in unidades_prestadas.items():
            for unidad, cant in unids.items():
                cant = int(cant or 0)
                if cant <= 0:
                    continue
                entrada = next(
                    (p for p in prestadas if p["jugador"] == dueño and p["unidad"].upper() == unidad.upper()),
                    None
                )
                if entrada:
                    entrada["cantidad"] = max(0, entrada["cantidad"] - cant)
                    if entrada["cantidad"] == 0:
                        prestadas.remove(entrada)

    # ── Construir orden ───────────────────────────────────────────────────────
    orden = {
        "id":                  str(uuid.uuid4()),
        "tipo":                tipo,
        "jugador":             jugador,
        "ciudad_origen":       ciudad_origen.get("NOMBRE", "?"),
        "x_orig":              x_orig,
        "y_orig":              y_orig,
        "x_dest":              x_dest,
        "y_dest":              y_dest,
        "jugador_dest":        jugador_dest,
        "ciudad_dest":         ciudad_dest_nombre,
        "unidades":            {k: int(v) for k, v in unidades.items() if int(v or 0) > 0},
        "unidades_prestadas":  {
            dueño: {k: int(v) for k, v in unids.items() if int(v or 0) > 0}
            for dueño, unids in unidades_prestadas.items()
            if any(int(v or 0) > 0 for v in unids.values())
        },
        "recursos":            {k: _srf(v) for k, v in recursos.items() if _srf(v) > 0},
        "nivel_tropas":        nivel_tropas,
        "distancia":           round(distancia, 2),
        "oro_costo":           oro_costo,
        "velocidad_min":       vel_min,
        "inicio":              ahora,
        "t_llegada":           t_llegada,
        "t_fundar":            t_fundar,
        "t_retorno":           t_retorno,
        "estado":              "EN_VIAJE",   # EN_VIAJE | LLEGADA | REGRESANDO | COMPLETADA
        "resultado":           None,
        "botin":               {},
    }

    return {"ok": True, "orden": orden}


# ── Procesar órdenes activas ──────────────────────────────────────────────────

def _evaluar_y_registrar_deteccion(orden: dict, sm, ahora: float) -> None:
    """
    Si la orden está dentro del radio de la torre defensora y es detectable,
    escribe o actualiza la alerta en player["alertas"] del defensor.
    Solo se dispara una vez por orden (si ya existe la alerta, no la duplica).
    Nota: si el radio >= distancia total, se detecta desde el primer tick.
    """
    jugador_def = orden.get("jugador_dest")
    ciudad_dest = orden.get("ciudad_dest")
    x_d = orden.get("x_dest", -1)
    y_d = orden.get("y_dest", -1)

    # Si no hay jugador_dest, buscar qué jugador tiene una ciudad en las coords destino
    if not jugador_def:
        try:
            from backend.data.save_manager import PLAYER_PATHS
            for jug in PLAYER_PATHS:
                try:
                    p_tmp = sm.load_player(jug)
                    for c in p_tmp.get("cities", []):
                        cx = float(c.get("X", c.get("x", -999)))
                        cy = float(c.get("Y", c.get("y", -999)))
                        if abs(cx - x_d) <= 1.0 and abs(cy - y_d) <= 1.0:
                            jugador_def = jug
                            ciudad_dest = c.get("NOMBRE")
                            orden["jugador_dest"] = jugador_def
                            orden["ciudad_dest"]  = ciudad_dest
                            break
                except Exception:
                    continue
                if jugador_def:
                    break
        except Exception:
            pass

    if not jugador_def:
        return  # destino no es ciudad de jugador conocido

    # Si tenemos jugador pero no ciudad, buscar por coords
    if not ciudad_dest:
        try:
            player_def_tmp = sm.load_player(jugador_def)
            for c in player_def_tmp.get("cities", []):
                cx = float(c.get("X", c.get("x", -999)))
                cy = float(c.get("Y", c.get("y", -999)))
                if abs(cx - x_d) <= 1.0 and abs(cy - y_d) <= 1.0:
                    ciudad_dest = c.get("NOMBRE")
                    orden["ciudad_dest"] = ciudad_dest
                    break
        except Exception:
            pass

    if not ciudad_dest:
        return

    try:
        from backend.systems.detection import evaluar_deteccion
        player_def = sm.load_player(jugador_def)
        city_def   = next(
            (c for c in player_def.get("cities", []) if c.get("NOMBRE") == ciudad_dest),
            None
        )
        if not city_def:
            return

        resultado = evaluar_deteccion(orden, city_def, ahora)
        if not resultado:
            return

        alerta_id = f"alerta_{orden['id']}"
        alertas   = player_def.setdefault("alertas", [])

        # No duplicar — si ya existe esta alerta, actualizar nivel si subió
        existente = next((a for a in alertas if a["id"] == alerta_id), None)
        if existente:
            if resultado["nivel"] > existente.get("nivel", 0):
                existente["nivel"] = resultado["nivel"]
                existente["info"]  = resultado["info"]
                sm.save_player(jugador_def, player_def)
            return

        # Nueva alerta
        import time as _time
        alertas.append({
            "id":         alerta_id,
            "orden_id":   orden["id"],
            "ciudad":     ciudad_dest,
            "nivel":      resultado["nivel"],
            "tipo_orden": resultado["tipo_orden"],
            "info":       resultado["info"],
            "ts":         _time.time(),
            "activa":     True,
            "vista":      False,
        })
        sm.save_player(jugador_def, player_def)

    except Exception as e:
        import traceback
        print(f"[deteccion] Error evaluando orden {orden.get('id','?')[:8]}: {e}")
        traceback.print_exc()


def _desactivar_alerta(orden: dict, sm) -> None:
    """
    Marca la alerta como inactiva al llegar al destino.
    Si aún no fue vista por el frontend (vista=False), espera a que sea vista
    marcándola como pendiente — el endpoint /api/alerts la desactiva al hacer dismiss.
    """
    jugador_def = orden.get("jugador_dest")
    if not jugador_def:
        return
    alerta_id = f"alerta_{orden['id']}"
    try:
        def _fn(player):
            for a in player.get("alertas", []):
                if a["id"] == alerta_id:
                    if a.get("vista", False):
                        a["activa"] = False
                    else:
                        # Aún no vista — dejar activa para que el frontend la vea
                        # Se desactivará al hacer dismiss desde el frontend
                        a["pendiente_desactivar"] = True
                    break
        sm.update_player(jugador_def, _fn)
    except Exception:
        pass


def procesar_ordenes(
    orders: list,
    save_manager,
) -> list:
    """
    Revisa todas las órdenes activas y ejecuta las que han llegado a su destino.
    Modifica orders in-place. Retorna lista de órdenes con eventos nuevos.

    Llama a los sistemas de combate/espionaje según corresponda.
    Guarda los JSONs afectados via save_manager.
    """
    ahora     = time.time()
    eventos   = []

    for orden in orders:
        if orden.get("estado", "COMPLETADA") == "COMPLETADA":
            continue

        if orden.get("estado") == "EN_VIAJE":
            # Evaluar detección por Torre de Vigilancia del defensor
            _evaluar_y_registrar_deteccion(orden, save_manager, ahora)

        if orden.get("estado") == "EN_VIAJE" and ahora >= orden.get("t_llegada", ahora + 1):
            evento = _ejecutar_llegada(orden, save_manager)
            eventos.append(evento)
            print(f"[orders] Llegada: {orden['id'][:8]} tipo={orden['tipo']} sobrev={orden.get('unidades_sobrevivientes',{})}")

        if orden.get("estado") == "REGRESANDO" and ahora >= orden.get("t_retorno", ahora + 1):
            evento = _ejecutar_retorno(orden, save_manager)
            eventos.append(evento)

    return eventos


def _ejecutar_llegada(orden: dict, sm) -> dict:
    """Ejecuta la lógica al llegar al destino."""
    # Marcar alerta como inactiva — la orden llegó, ya no hay amenaza en tránsito
    _desactivar_alerta(orden, sm)
    tipo = orden["tipo"]

    if tipo == "ATAQUE":
        return _resolver_ataque(orden, sm)
    elif tipo == "ESPIONAJE":
        return _resolver_espionaje(orden, sm)
    elif tipo == "DESPLAZAMIENTO":
        return _resolver_desplazamiento(orden, sm)
    elif tipo == "TRANSPORTE":
        return _resolver_transporte(orden, sm)
    elif tipo == "FUNDAR":
        return _resolver_fundar(orden, sm)
    else:
        orden["estado"] = "COMPLETADA"
        return {"orden_id": orden["id"], "tipo": tipo, "ok": False, "msg": "Tipo desconocido"}


def _resolver_ataque(orden: dict, sm) -> dict:
    from backend.systems.combat import resolver_combate, aplicar_resultado_combate
    from backend.systems.herreria import calcular_bonus_herreria

    jugador_atk = sm.load_player(orden["jugador"])
    jugador_def_nombre = orden.get("jugador_dest") or ""

    # ── Buscar ciudad defensora ───────────────────────────────────────────────
    # Puede ser: jugador activo, inactivo, o entidad del mundo
    ciudad_def      = None
    jugador_def     = {}
    es_inactivo     = False

    if jugador_def_nombre:
        jugador_def = sm.load_player(jugador_def_nombre)
        if jugador_def:
            ciudad_def = _buscar_ciudad(jugador_def, orden["x_dest"], orden["y_dest"])

    # Si no encontró ciudad (inactivo, entidad de mundo, etc.)
    if not ciudad_def:
        # Buscar en inactivos por coordenadas
        try:
            mundo = sm.load_world("inactivos")
            for c in mundo.get("cities", []):
                if (abs(float(c.get("X", -999)) - orden["x_dest"]) <= 1.0 and
                        abs(float(c.get("Y", -999)) - orden["y_dest"]) <= 1.0):
                    ciudad_def  = c
                    es_inactivo = True
                    jugador_def_nombre = jugador_def_nombre or c.get("ID", "INACTIVO")
                    break
        except Exception:
            pass

    # Buscar en dioses o cuevas si aún no encontró
    entidad_mundo = None
    if not ciudad_def:
        for world_key in ["dioses", "cuevas"]:
            try:
                mundo    = sm.load_world(world_key)
                entities = mundo.get("entities", [])
                # Ordenar por CA para asignar número de dificultad
                ordenados = sorted(entities, key=lambda e: float(e.get("CA", 0) or 0))
                num_map   = {e.get("ID"): i+1 for i, e in enumerate(ordenados)}
                for e in entities:
                    if (abs(float(e.get("X", -999)) - orden["x_dest"]) <= 1.0 and
                            abs(float(e.get("Y", -999)) - orden["y_dest"]) <= 1.0):
                        entidad_mundo = dict(e)
                        entidad_mundo["_num_dificultad"] = num_map.get(e.get("ID"), 1)
                        break
            except Exception:
                pass
            if entidad_mundo:
                break

    # Si es entidad del mundo (dios/cueva) → combate INDIVIDUAL — sin tropas prestadas
    if entidad_mundo:
        if orden.get("unidades_prestadas"):
            nombre_ent = entidad_mundo.get("NOMBRE", "la entidad")
            return {
                "orden_id": orden["id"], "tipo": "ATAQUE", "ok": False,
                "msg": f"El combate contra {nombre_ent} debe ser individual — retira las tropas prestadas",
            }
        # Verificar que no sea un dios ya derrotado por este jugador
        es_dios_check = "DIOS" in str(entidad_mundo.get("CAT_KEY", entidad_mundo.get("TIPO",""))).upper()
        if es_dios_check:
            eid = str(entidad_mundo.get("ID", ""))
            da = jugador_atk.get("dioses_abatidos", [])
            if isinstance(da, int): da = []
            if eid and eid in da:
                nombre_ent = entidad_mundo.get("NOMBRE", "este dios")
                return {
                    "orden_id": orden["id"], "tipo": "ATAQUE", "ok": False,
                    "msg": f"Ya derrotaste a {nombre_ent} — un dios solo puede ser vencido una vez por jugador",
                }
        return _resolver_ataque_entidad(orden, sm, jugador_atk, entidad_mundo)

    if not ciudad_def:
        # No hay defensor — victoria automática, tropas regresan
        orden["unidades_sobrevivientes"] = orden["unidades"].copy()
        orden["botin"]   = {}
        orden["resultado"] = {"victoria": True, "mensaje": "Sin defensor — victoria automática", "rondas": 0}
        orden["estado"]   = "REGRESANDO"
        orden["t_retorno"] = time.time() + (orden["t_llegada"] - orden["inicio"])
        sm.save_player(orden["jugador"], jugador_atk)
        return {"orden_id": orden["id"], "tipo": "ATAQUE", "ok": True,
                "victoria": True, "msg": "Sin defensor"}

    # Ciudad origen del atacante
    ciudad_orig = _buscar_ciudad_nombre(jugador_atk, orden["ciudad_origen"])
    bonus_atk   = calcular_bonus_herreria(jugador_atk)

    nivel_def = (_nivel_tropas_player(jugador_def)
                 if jugador_def else 1)

    atacantes = [{
        "jugador":        orden["jugador"],
        "unidades":       orden["unidades"],
        "nivel_tropas":   orden["nivel_tropas"],
        "bonus_herreria": bonus_atk,
    }]
    # Añadir dueños de tropas prestadas como atacantes separados (XP individual)
    for dueño, unids_prest in orden.get("unidades_prestadas", {}).items():
        if not any(int(v or 0) > 0 for v in unids_prest.values()):
            continue
        player_dueño = sm.load_player(dueño)
        nivel_dueño  = _nivel_tropas_player(player_dueño, unids_prest)
        bonus_dueño  = calcular_bonus_herreria(player_dueño)
        atacantes.append({
            "jugador":        dueño,
            "unidades":       {k: int(v) for k, v in unids_prest.items() if int(v or 0) > 0},
            "nivel_tropas":   nivel_dueño,
            "bonus_herreria": bonus_dueño,
        })
    defensores = [{
        "jugador":      jugador_def_nombre,
        "unidades":     _unidades_ciudad(ciudad_def),
        "nivel_tropas": nivel_def,
    }]
    nivel_muralla = int(ciudad_def.get("MURALLA", 0) or 0)

    resultado = resolver_combate(atacantes, defensores, ciudad_def, nivel_muralla)

    # Aplicar bajas al defensor
    aplicar_resultado_combate(
        resultado,
        ciudades_atk = {orden["jugador"]: ciudad_orig} if ciudad_orig else {},
        ciudades_def = {jugador_def_nombre: ciudad_def},
        jugadores_atk = {orden["jugador"]: jugador_atk},
        jugadores_def = {jugador_def_nombre: jugador_def} if jugador_def else {},
    )

    # Reposición automática de tropas para cuentas vitaminizadas
    _reponer_vitaminizadas(jugador_def_nombre, ciudad_def, sm)

    # Persistir defensor — si es inactivo, guardar en world
    if es_inactivo:
        try:
            from backend.data.save_manager import save_json, DB
            mundo_path = DB / "world" / "inactivos.json"
            mundo2 = sm.load_world("inactivos")
            for i, c in enumerate(mundo2.get("cities", [])):
                if c.get("ID") == ciudad_def.get("ID"):
                    mundo2["cities"][i] = ciudad_def
                    break
            save_json(mundo_path, mundo2)
        except Exception as e:
            print(f"[orders] Error guardando inactivo: {e}")
    elif jugador_def:
        sm.save_player(jugador_def_nombre, jugador_def)

    orden["resultado"] = {
        "victoria":           resultado["victoria_atacante"],
        "victoria_por":       resultado.get("tipo_victoria", "combate" if resultado["victoria_atacante"] else None),
        "muralla_atravesada": resultado.get("muralla_atravesada", False),
        "mensaje":            resultado["mensaje"],
        "rondas":             resultado["rondas"],
        "bajas_atk":          resultado["bajas_atk"],
        "bajas_def":          resultado["bajas_def"],
        "saqueo":             resultado["saqueo"],
        "xp":                 resultado["xp_por_jugador_atk"],
        "victoria_atacante":  resultado["victoria_atacante"],
        "xp_por_jugador_atk": resultado["xp_por_jugador_atk"],
    }
    orden["botin"]                   = resultado["saqueo"]
    orden["unidades_sobrevivientes"] = resultado["sobrevivientes_atk"]  # todos los propietarios
    orden["estado"]                  = "REGRESANDO"
    orden["t_retorno"]               = time.time() + (orden["t_llegada"] - orden["inicio"])

    # Guardar atacante atómicamente — aplicar bajas + XP
    xp_ganada = resultado["xp_por_jugador_atk"].get(orden["jugador"], 0)


    def _aplicar_combate_atk(player):
        player["experiencia"] = float(player.get("experiencia", 0) or 0) + xp_ganada
        player["batallas_ganadas" if resultado["victoria_atacante"] else "batallas_perdidas"] = \
            int(player.get("batallas_ganadas" if resultado["victoria_atacante"] else "batallas_perdidas", 0) or 0) + 1

    sm.update_player(orden["jugador"], _aplicar_combate_atk)

    # Guardar informe inmediatamente al llegar — no esperar al retorno
    propietarios_extra = list(orden.get("unidades_prestadas", {}).keys())
    _guardar_informe(orden, sm, propietarios_extra)

    # Si t_retorno ya pasó, ejecutar retorno inmediatamente
    if time.time() >= orden["t_retorno"]:
        _ejecutar_retorno(orden, sm)

    return {"orden_id": orden["id"], "tipo": "ATAQUE", "ok": True,
            "victoria": resultado["victoria_atacante"], "msg": resultado["mensaje"]}


def _verificar_valor(orden: dict, jugador: dict, entidad: dict) -> dict:
    """
    Verifica si el jugador cumple las condiciones de victoria por valor.
    Requiere:
    - ≥ 90% de aldeanos, militares e invocaciones del jugador total
    - Mínimos absolutos basados en el número del dios/cueva ordenado por dificultad

    Retorna dict con 'cumple' bool y 'razon' string.
    """
    BASICAS  = {"ALDEANO","EXPLORADOR","SACERDOTE","GUERRERO","COMANDO",
                "MERCENARIO","MARINE","CYBORG","MAGO","METAHUMANO"}
    INVOCS   = {"DEMONIO","ANIMA","ESPECTRO","GOLEM","CENTAURO","KRAKEN",
                "ALONARDO","MADRESELVA","COLOSO","FENIX","DRAGON_DE_ORO",
                "CABALLERO_DE_LUZ","ALALAIA","EON_SUPREMO"}
    MIL      = BASICAS - {"ALDEANO"}

    # Sumar tropas en todas las ciudades del jugador
    total_ald = total_mil = total_inv = 0
    for city in jugador.get("cities", []):
        for k, v in city.items():
            ku = k.upper()
            if ku not in BASICAS and ku not in INVOCS:
                continue  # ignorar campos no numéricos (NOMBRE, STATUS, etc.)
            try:
                v = int(float(v or 0))
            except (TypeError, ValueError):
                continue
            if ku == "ALDEANO":       total_ald += v
            elif ku in MIL:           total_mil += v
            elif ku in INVOCS:        total_inv += v

    # Tropas enviadas
    env_ald = int(orden["unidades"].get("ALDEANO", 0) or 0)
    env_mil = sum(int(v or 0) for k, v in orden["unidades"].items()
                  if k.upper() in MIL)
    env_inv = sum(int(v or 0) for k, v in orden["unidades"].items()
                  if k.upper() in INVOCS)

    # Número de orden de la entidad (posición relativa por dificultad)
    tipo_ent = entidad.get("CAT_KEY", entidad.get("TIPO","")).upper()
    num_entidad = int(entidad.get("_num_dificultad", 1))

    # Mínimos absolutos
    if "DIOS" in tipo_ent:
        min_ald = num_entidad * 2_000
        min_mil = num_entidad * 25
        min_inv = num_entidad * 25
    else:  # CUEVAS — por tipo de criatura
        clase   = entidad.get("CLASE", "").lower()
        MINS_CUEVA = {
            "behemot":     (10_000,   100,   100),
            "simurgh":     (50_000,   500,   500),
            "leviatan":    (50_000,   500,   500),
            "leviatán":    (50_000,   500,   500),
            "patotas":     (200_000, 2_000, 2_000),
            "dragon":      (500_000, 5_000, 5_000),
            "dragón":      (500_000, 5_000, 5_000),
            "chupacabras": (500_000, 5_000, 5_000),
        }
        min_ald, min_mil, min_inv = MINS_CUEVA.get(clase, (10_000, 100, 100))

    # Verificar 90%
    pct_ald = (env_ald / total_ald * 100) if total_ald > 0 else 0
    pct_mil = (env_mil / total_mil * 100) if total_mil > 0 else 0
    pct_inv = (env_inv / total_inv * 100) if total_inv > 0 else 0

    fallos = []
    if pct_ald < 80:
        fallos.append(f"aldeanos {pct_ald:.0f}% < 80%")
    if pct_mil < 90:
        fallos.append(f"militares {pct_mil:.0f}% < 90%")
    if pct_inv < 90:
        fallos.append(f"invocaciones {pct_inv:.0f}% < 90%")
    if env_ald < min_ald:
        fallos.append(f"aldeanos {env_ald:,} < mínimo {min_ald:,}")
    if env_mil < min_mil:
        fallos.append(f"militares {env_mil:,} < mínimo {min_mil:,}")
    if env_inv < min_inv:
        fallos.append(f"invocaciones {env_inv:,} < mínimo {min_inv:,}")

    if fallos:
        return {"cumple": False, "razon": " | ".join(fallos)}
    return {"cumple": True, "razon": "Victoria por valor — ejército completo desplegado"}


def _resolver_ataque_entidad(orden: dict, sm, jugador_atk: dict, entidad: dict) -> dict:
    """Resuelve combate contra entidad del mundo (Dios, Cueva) con mecánica de valor."""
    from backend.systems.combat import resolver_combate_entidad
    from backend.systems.herreria import calcular_bonus_herreria
    from backend.data.save_manager import save_json, DB

    tipo_ent  = (entidad.get("CAT_KEY") or entidad.get("TIPO") or "").upper()
    es_dios   = "DIOS" in tipo_ent
    world_key = "dioses" if es_dios else "cuevas"
    nombre_ent = entidad.get("NOMBRE", entidad.get("ID", "?"))

    bonus_atk = calcular_bonus_herreria(jugador_atk)
    atacante  = {
        "jugador":        orden["jugador"],
        "unidades":       orden["unidades"],
        "nivel_tropas":   orden["nivel_tropas"],
        "bonus_herreria": bonus_atk,
    }

    resultado = resolver_combate_entidad(atacante, {
        "nombre":      nombre_ent,
        "tipo":        tipo_ent,
        "hp":          float(entidad.get("HP", 1)),
        "pa":          float(entidad.get("PA", 1)),
        "ca":          float(entidad.get("CA", 1)),
        "destreza":    float(entidad.get("DESTREZA", 1)),
        "experiencia": float(entidad.get("EXPERIENCIA", 0)),
    })

    # ── Verificar victoria por valor ──────────────────────────────────────────
    valor = _verificar_valor(orden, jugador_atk, entidad)

    # Victoria si: combate ganado, O sobrevivió 9 rondas, O cumple condiciones de valor
    sobrevivio_9 = resultado["rondas"] >= 9 and not resultado["victoria_atacante"]
    victoria_final = (resultado["victoria_atacante"]
                      or sobrevivio_9
                      or valor["cumple"])

    if victoria_final:
        mensaje = resultado["mensaje"]
        if not resultado["victoria_atacante"]:
            if sobrevivio_9:
                mensaje = f"Victoria por resistencia — 9 rondas superadas contra {nombre_ent}"
            elif valor["cumple"]:
                mensaje = f"Victoria por valor — {nombre_ent} honra el coraje del ejército"
        try:
            mundo = sm.load_world(world_key)
            clase_criatura = None
            for i, e in enumerate(mundo.get("entities", [])):
                if e.get("ID") == entidad.get("ID"):
                    mundo["entities"][i]["_derrotado"] = True
                    mundo["entities"][i]["HP"] = 0
                    if not es_dios:
                        # Guardar clase para capturar la criatura
                        clase_criatura = e.get("CLASE", e.get("NOMBRE", "")).upper()
                    break
            save_json(DB / "world" / f"{world_key}.json", mundo)

            # Capturar criatura de cueva → añadir al ejército del atacante
            if not es_dios and clase_criatura:
                # Mapeo de clase de cueva → clave de invocación en el JSON del jugador
                # 6 tipos de criaturas de cueva (del CSV cuevas.csv)
                CLASE_A_UNIDAD = {
                    "BEHEMOT":    "BEHEMOT",
                    "CHUPACABRAS":"CHUPACABRAS",
                    "DRAGÓN":     "DRAGON",
                    "DRAGON":     "DRAGON",
                    "LEVIATÁN":   "LEVIATAN",
                    "LEVIATAN":   "LEVIATAN",
                    "PATOTAS":    "PATOTAS",
                    "SIMURGH":    "SIMURGH",
                }
                unidad_key = CLASE_A_UNIDAD.get(clase_criatura.replace(" ", "_"), clase_criatura)
                ciudad_origen_nombre = orden.get("ciudad_origen")

                def _capturar_criatura(player):
                    for city in player.get("cities", []):
                        if city.get("NOMBRE") == ciudad_origen_nombre:
                            city[unidad_key] = int(city.get(unidad_key, 0) or 0) + 1
                            break
                sm.update_player(orden["jugador"], _capturar_criatura)
                orden["resultado"]["criatura_capturada"] = unidad_key

        except Exception as e:
            print(f"[orders] Error actualizando entidad: {e}")
    else:
        mensaje = resultado["mensaje"]

    xp_ganada = resultado["xp_por_jugador_atk"].get(orden["jugador"], 0)

    orden["resultado"] = {
        "victoria":          victoria_final,
        "victoria_combate":  resultado["victoria_atacante"],
        "victoria_por":      ("combate" if resultado["victoria_atacante"]
                              else "resistencia" if sobrevivio_9
                              else "valor" if valor["cumple"]
                              else "derrota"),
        "mensaje":           mensaje,
        "rondas":            resultado["rondas"],
        "bajas_atk":         resultado["bajas_atk"],
        "bajas_def":         resultado["bajas_def"],
        "saqueo":            {},
        "xp":                resultado["xp_por_jugador_atk"],
        "valor_cumplido":    valor["cumple"],
        "valor_razon":       valor["razon"],
    }
    orden["botin"]                   = {}
    orden["unidades_sobrevivientes"] = resultado["sobrevivientes_atk"]  # todos los propietarios
    orden["estado"]                  = "REGRESANDO"
    orden["t_retorno"]               = time.time() + (orden["t_llegada"] - orden["inicio"])

    entidad_id = str(entidad.get("ID", ""))

    def _aplicar_xp(player):
        player["experiencia"] = float(player.get("experiencia", 0) or 0) + xp_ganada
        if victoria_final:
            if es_dios:
                # Guardar ID del dios derrotado (lista de IDs)
                da = player.get("dioses_abatidos", [])
                if isinstance(da, int):
                    # Migrar formato viejo (int) a lista
                    da = []
                if entidad_id and entidad_id not in da:
                    da.append(entidad_id)
                player["dioses_abatidos"] = da
            else:
                player["cuevas_derrotadas"] = int(player.get("cuevas_derrotadas", 0) or 0) + 1

    sm.update_player(orden["jugador"], _aplicar_xp)

    # Guardar informe inmediatamente al llegar — no esperar al retorno
    propietarios_extra = list(orden.get("unidades_prestadas", {}).keys())
    _guardar_informe(orden, sm, propietarios_extra)

    if time.time() >= orden["t_retorno"]:
        _ejecutar_retorno(orden, sm)

    return {"orden_id": orden["id"], "tipo": "ATAQUE", "ok": True,
            "victoria": victoria_final, "msg": mensaje}


def _resolver_espionaje(orden: dict, sm) -> dict:
    from backend.systems.espionage import resolver_espionaje, aplicar_resultado_espionaje
    from backend.systems.combat import calcular_sigilo_grupo
    from backend.systems.herreria import calcular_bonus_herreria

    jugador_atk        = sm.load_player(orden["jugador"])
    jugador_def_nombre = orden.get("jugador_dest") or ""
    jugador_def        = {}
    ciudad_def         = None
    es_inactivo        = False

    if jugador_def_nombre:
        jugador_def = sm.load_player(jugador_def_nombre)
        if jugador_def:
            ciudad_def = _buscar_ciudad(jugador_def, orden["x_dest"], orden["y_dest"])

    if not ciudad_def:
        try:
            mundo = sm.load_world("inactivos")
            for c in mundo.get("cities", []):
                if (abs(float(c.get("X", -999)) - orden["x_dest"]) <= 1.0 and
                        abs(float(c.get("Y", -999)) - orden["y_dest"]) <= 1.0):
                    ciudad_def  = c
                    es_inactivo = True
                    jugador_def_nombre = jugador_def_nombre or c.get("ID", "INACTIVO")
                    break
        except Exception:
            pass

    # Buscar en dioses/cuevas si sigue sin encontrar
    if not ciudad_def:
        for world_key in ["dioses", "cuevas"]:
            try:
                mundo = sm.load_world(world_key)
                for e in mundo.get("entities", []):
                    if (abs(float(e.get("X", -999)) - orden["x_dest"]) <= 1.0 and
                            abs(float(e.get("Y", -999)) - orden["y_dest"]) <= 1.0):
                        return _resolver_espionaje_entidad(orden, sm, jugador_atk, e)
            except Exception:
                pass

    if not ciudad_def:
        # Sin destino — tropas regresan sin resultado
        orden["unidades_sobrevivientes"] = orden["unidades"].copy()
        orden["botin"]     = {}
        orden["resultado"] = {"detectado": False, "sigilo": 0, "nivel_espionaje": 0,
                               "inteligencia": None, "botin": {}, "combate": None}
        orden["estado"]    = "REGRESANDO"
        orden["t_retorno"] = time.time() + (orden["t_llegada"] - orden["inicio"])
        sm.save_player(orden["jugador"], jugador_atk)
        if time.time() >= orden["t_retorno"]:
            _ejecutar_retorno(orden, sm, jugador_atk)
        return {"orden_id": orden["id"], "ok": False, "msg": "Ciudad destino no encontrada"}

    ciudad_orig = _buscar_ciudad_nombre(jugador_atk, orden["ciudad_origen"])
    bonus_atk   = calcular_bonus_herreria(jugador_atk)
    nivel_def   = (_nivel_tropas_player(jugador_def)
                   if jugador_def else 1)

    # Construir grupos por propietario para sigilo correcto
    grupos_sigilo = [{"unidades": orden["unidades"], "nivel_tropas": orden["nivel_tropas"]}]
    for dueño, unids in orden.get("unidades_prestadas", {}).items():
        if any(int(v or 0) > 0 for v in unids.values()):
            player_dueño = sm.load_player(dueño)
            nivel_dueño  = _nivel_tropas_player(player_dueño, unids)
            grupos_sigilo.append({"unidades": unids, "nivel_tropas": nivel_dueño})

    # sigilo_efectivo calculado con el nivel correcto de cada propietario
    sigilo_efectivo = calcular_sigilo_grupo(grupos_sigilo)

    # Combinar unidades para el combate (si es detectado)
    unidades_esp = dict(orden["unidades"])
    for dueño, unids in orden.get("unidades_prestadas", {}).items():
        for k, v in unids.items():
            unidades_esp[k] = int(unidades_esp.get(k, 0)) + int(v or 0)

    resultado = resolver_espionaje(
        jugador_atk        = orden["jugador"],
        unidades_atk       = unidades_esp,
        nivel_tropas_atk   = orden["nivel_tropas"],
        bonus_herreria_atk = bonus_atk,
        jugador_def        = jugador_def_nombre,
        unidades_def       = _unidades_ciudad(ciudad_def) if ciudad_def else {},
        nivel_tropas_def   = nivel_def,
        objetivo_city      = ciudad_def or {},
        sigilo_precalculado = sigilo_efectivo,
    )

    aplicar_resultado_espionaje(
        resultado,
        atacante_city    = ciudad_orig or {},
        objetivo_city    = ciudad_def  or {},
        jugador_atacante = jugador_atk,
        jugador_defensor = jugador_def,
    )

    orden["resultado"] = {
        "detectado":       resultado["detectado"],
        "sigilo":          resultado["sigilo_efectivo"],
        "nivel_espionaje": resultado.get("nivel_espionaje", 0),
        "inteligencia":    resultado.get("inteligencia"),
        "combate":         resultado["combate"]["mensaje"] if resultado["combate"] else None,
        "combate_completo": resultado["combate"] if resultado["detectado"] and resultado["combate"] else None,
    }
    orden["botin"]  = {}
    if resultado["detectado"] and resultado["combate"]:
        orden["unidades_sobrevivientes"] = resultado["combate"]["sobrevivientes_atk"]  # todos los propietarios
    else:
        # Exitoso: tropas propias regresan intactas; prestadas las maneja retornar_tropas_prestadas_post_orden
        orden["unidades_sobrevivientes"] = {k: int(v or 0) for k, v in orden["unidades"].items() if int(v or 0) > 0}
    orden["estado"]    = "REGRESANDO"
    orden["t_retorno"] = time.time() + (orden["t_llegada"] - orden["inicio"])

    # Guardar contador de misiones atómicamente (sin tocar tropas)
    if not resultado["detectado"]:
        def _cnt(player):
            player["misiones_espionaje"] = int(player.get("misiones_espionaje", 0) or 0) + 1
        sm.update_player(orden["jugador"], _cnt)

    if jugador_def_nombre and jugador_def:
        sm.save_player(jugador_def_nombre, jugador_def)

    # Guardar informe siempre — detectado O exitoso
    propietarios_extra = list(orden.get("unidades_prestadas", {}).keys())
    _guardar_informe(orden, sm, propietarios_extra)

    if time.time() >= orden["t_retorno"]:
        _ejecutar_retorno(orden, sm)

    return {"orden_id": orden["id"], "tipo": "ESPIONAJE", "ok": True,
            "detectado": resultado["detectado"]}


def _resolver_espionaje_entidad(orden: dict, sm, jugador_atk: dict, entidad: dict) -> dict:
    """
    Espionaje a entidad del mundo (Dios, Cueva).
    El explorador obtiene intel básica de la entidad — siempre sin detección
    (las entidades no tienen torre de vigilancia).
    Si detectado por sigilo=0 → combate contra la entidad.
    """
    from backend.systems.espionage import calcular_sigilo as _calc_sigilo
    from backend.systems.combat import resolver_combate_entidad
    from backend.systems.herreria import calcular_bonus_herreria

    nivel_tropas = orden["nivel_tropas"]
    unidades_atk = orden["unidades"]

    # Calcular sigilo
    sigilo = _calc_sigilo(unidades_atk, nivel_tropas)

    # Entidades no tienen torre — detección = 0, siempre exitoso si sigilo > 0
    detectado = sigilo <= 0

    nombre_ent = entidad.get("NOMBRE", entidad.get("ID", "?"))
    tipo_ent   = entidad.get("CAT_KEY", entidad.get("TIPO", "?"))

    if detectado:
        # Combate contra la entidad
        bonus_atk = calcular_bonus_herreria(jugador_atk)
        atacante  = {
            "jugador":        orden["jugador"],
            "unidades":       unidades_atk,
            "nivel_tropas":   nivel_tropas,
            "bonus_herreria": bonus_atk,
        }
        combate = resolver_combate_entidad(atacante, {
            "nombre":      nombre_ent,
            "tipo":        tipo_ent,
            "hp":          float(entidad.get("HP", 1)),
            "pa":          float(entidad.get("PA", 1)),
            "ca":          float(entidad.get("CA", 1)),
            "destreza":    float(entidad.get("DESTREZA", 1)),
            "experiencia": float(entidad.get("EXPERIENCIA", 0)),
        })
        sobrev = combate["sobrevivientes_atk"].get(orden["jugador"], {})
        xp     = combate["xp_por_jugador_atk"].get(orden["jugador"], 0)

        def _xp_fn(player):
            player["experiencia"] = float(player.get("experiencia", 0) or 0) + xp
        sm.update_player(orden["jugador"], _xp_fn)

        orden["resultado"] = {
            "detectado":       True,
            "sigilo":          sigilo,
            "nivel_espionaje": 0,
            "inteligencia":    None,
            "botin":           {},
            "combate":         combate["mensaje"],
            "combate_completo": combate,
        }
        orden["botin"]                   = {}
        orden["unidades_sobrevivientes"] = sobrev
    else:
        # Espionaje exitoso — intel básica de la entidad
        nivel_espio = 1  # entidades siempre dan nivel mínimo
        inteligencia = {
            "nivel":    nivel_espio,
            "nombre":   nombre_ent,
            "tipo":     tipo_ent,
            "x":        entidad.get("X"),
            "y":        entidad.get("Y"),
            "hp":       float(entidad.get("HP", 0)),
            "pa":       float(entidad.get("PA", 0)),
            "ca":       float(entidad.get("CA", 0)),
            "destreza": float(entidad.get("DESTREZA", 0)),
        }
        orden["resultado"] = {
            "detectado":       False,
            "sigilo":          sigilo,
            "nivel_espionaje": nivel_espio,
            "inteligencia":    inteligencia,
            "botin":           {},
            "combate":         None,
        }
        orden["botin"]                   = {}
        orden["unidades_sobrevivientes"] = unidades_atk.copy()

    orden["estado"]    = "REGRESANDO"
    orden["t_retorno"] = time.time() + (orden["t_llegada"] - orden["inicio"])

    if time.time() >= orden["t_retorno"]:
        _ejecutar_retorno(orden, sm)

    return {"orden_id": orden["id"], "tipo": "ESPIONAJE", "ok": True,
            "detectado": detectado}


def _resolver_desplazamiento(orden: dict, sm) -> dict:
    """Mueve tropas de ciudad origen a ciudad destino (ambas del mismo jugador).
    Tropas prestadas se quedan en ciudad destino como TROPAS_PRESTADAS.
    """
    jugador = sm.load_player(orden["jugador"])
    ciudad_dest = _buscar_ciudad(jugador, orden["x_dest"], orden["y_dest"])
    if not ciudad_dest:
        orden["estado"] = "COMPLETADA"
        return {"orden_id": orden["id"], "ok": False, "msg": "Ciudad destino no encontrada"}

    # Tropas propias
    for nombre, cant in orden["unidades"].items():
        ciudad_dest[nombre] = int(ciudad_dest.get(nombre, 0) or 0) + int(cant or 0)

    # Tropas prestadas — se mueven como TROPAS_PRESTADAS en ciudad destino
    prestadas_dest = ciudad_dest.setdefault("TROPAS_PRESTADAS", [])
    for dueño, unids in orden.get("unidades_prestadas", {}).items():
        for unidad, cant in unids.items():
            cant = int(cant or 0)
            if cant <= 0:
                continue
            entrada = next(
                (p for p in prestadas_dest
                 if p["jugador"] == dueño and p["unidad"] == unidad.upper()),
                None
            )
            if entrada:
                entrada["cantidad"] += cant
            else:
                prestadas_dest.append({
                    "jugador":       dueño,
                    "unidad":        unidad.upper(),
                    "cantidad":      cant,
                    "ciudad_origen": orden.get("ciudad_origen", "?"),
                })

    orden["estado"] = "COMPLETADA"
    sm.save_player(orden["jugador"], jugador)
    return {"orden_id": orden["id"], "tipo": "DESPLAZAMIENTO", "ok": True}


def _resolver_transporte(orden: dict, sm) -> dict:
    """Entrega recursos a la ciudad destino."""
    jugador_dest_nombre = orden.get("jugador_dest", orden["jugador"])
    jugador_dest = sm.load_player(jugador_dest_nombre)
    ciudad_dest  = _buscar_ciudad(jugador_dest, orden["x_dest"], orden["y_dest"])
    if not ciudad_dest:
        orden["estado"] = "COMPLETADA"
        return {"orden_id": orden["id"], "ok": False, "msg": "Ciudad destino no encontrada"}

    for rec, cant in orden["recursos"].items():
        ciudad_dest[rec] = float(ciudad_dest.get(rec, 0) or 0) + float(cant or 0)

    orden["estado"] = "COMPLETADA"
    sm.save_player(jugador_dest_nombre, jugador_dest)
    return {"orden_id": orden["id"], "tipo": "TRANSPORTE", "ok": True}


def _resolver_fundar(orden: dict, sm) -> dict:
    """Funda una nueva ciudad en las coordenadas destino."""
    from backend.data.save_manager import load_json, save_json
    from pathlib import Path
    import time as time_mod

    # Verificar zona KarlakÁ (doble check)
    if _zona_karlaka(orden["x_dest"], orden["y_dest"]):
        orden["estado"] = "COMPLETADA"
        return {"orden_id": orden["id"], "ok": False, "msg": "Zona prohibida KarlakÁ"}

    # Si aún está fundando (t_fundar > 0), esperar
    ahora = time_mod.time()
    if orden.get("_fundacion_inicio") is None:
        orden["_fundacion_inicio"] = ahora
    tiempo_fundando = ahora - orden["_fundacion_inicio"]
    if tiempo_fundando < orden.get("t_fundar", 0):
        return {"orden_id": orden["id"], "tipo": "FUNDAR", "ok": False, "msg": "Aún fundando"}

    jugador = sm.load_player(orden["jugador"])

    # Verificar que no hay ciudad en esas coordenadas
    for city in jugador.get("cities", []):
        if abs(float(city.get("X",0)) - orden["x_dest"]) < 1 and \
           abs(float(city.get("Y",0)) - orden["y_dest"]) < 1:
            orden["estado"] = "COMPLETADA"
            return {"orden_id": orden["id"], "ok": False, "msg": "Ya existe ciudad en esas coordenadas"}

    # Crear ciudad nueva con valores iniciales
    nueva_ciudad = _ciudad_inicial(
        jugador    = orden["jugador"],
        x          = orden["x_dest"],
        y          = orden["y_dest"],
        exploradores = orden["unidades"].get("EXPLORADOR", 0),
        nivel_tropas = orden["nivel_tropas"],
    )
    jugador["cities"].append(nueva_ciudad)

    orden["estado"]    = "COMPLETADA"
    orden["resultado"] = {"ciudad_fundada": nueva_ciudad["NOMBRE"]}

    sm.save_player(orden["jugador"], jugador)
    return {"orden_id": orden["id"], "tipo": "FUNDAR", "ok": True,
            "ciudad": nueva_ciudad["NOMBRE"]}



_VITAMINIZADOS = {"ALALAIA", "ADMIN"}

_TROPAS_REPO = [
    "ALDEANO","EXPLORADOR","SACERDOTE","GUERRERO","COMANDO",
    "MERCENARIO","MARINE","CYBORG","MAGO","METAHUMANO",
    "DEMONIO","ANIMA","ESPECTRO","GOLEM","CENTAURO","KRAKEN",
    "ALONARDO","MADRESELVA","COLOSO","FENIX","DRAGON_DE_ORO",
    "CABALLERO_DE_LUZ","ALALAIA","EON_SUPREMO",
]

_REPO_BASICAS  = 3_000_000
_REPO_INVOC    = 3_000_000
_REPO_ALALAIA  = 18
_REPO_EON      = 3

def _reponer_vitaminizadas(jugador: str, city: dict, sm) -> None:
    """
    Si el jugador es vitaminizado, repone sus tropas a los valores base
    después de un combate. Esto simula recursos infinitos.
    """
    if not jugador or jugador.upper() not in _VITAMINIZADOS:
        return

    _INVOC = {"DEMONIO","ANIMA","ESPECTRO","GOLEM","CENTAURO","KRAKEN",
              "ALONARDO","MADRESELVA","COLOSO","FENIX","DRAGON_DE_ORO",
              "CABALLERO_DE_LUZ","EON_SUPREMO"}
    _BASICAS = {"ALDEANO","EXPLORADOR","SACERDOTE","GUERRERO","COMANDO",
                "MERCENARIO","MARINE","CYBORG","MAGO","METAHUMANO"}

    for t in _TROPAS_REPO:
        if t == "ALALAIA":
            city[t] = _REPO_ALALAIA
        elif t == "EON_SUPREMO":
            city[t] = _REPO_EON
        elif t in _INVOC:
            city[t] = _REPO_INVOC
        else:
            city[t] = _REPO_BASICAS

    # Reponer aldeanos limpiamente (sin buffer fraccionario)
    city["ALDEANO"] = float(_REPO_BASICAS)

def _guardar_informe(orden: dict, sm, jugadores_extra: list = None) -> None:
    """
    Guarda copia del informe en el JSON de cada jugador participante.
    - El jugador que despachó la orden siempre recibe el informe.
    - jugadores_extra: dueños de tropas prestadas que también deben recibirlo.
    Máximo 200 informes por jugador (FIFO).
    """
    informe = {
        "id":            orden["id"],
        "tipo":          orden["tipo"],
        "jugador_atk":   orden.get("jugador"),
        "jugador_def":   orden.get("jugador_dest"),
        "ciudad_origen": orden.get("ciudad_origen"),
        "ciudad_dest":   orden.get("ciudad_dest"),
        "x_orig":        orden.get("x_orig"),
        "y_orig":        orden.get("y_orig"),
        "x_dest":        orden.get("x_dest"),
        "y_dest":        orden.get("y_dest"),
        "inicio":        orden.get("inicio"),
        "resultado":     orden.get("resultado"),
        "botin":         orden.get("botin", {}),
        "unidades":      orden.get("unidades", {}),
        "bajas_atk":     orden.get("resultado", {}).get("bajas_atacante", {}) if orden.get("resultado") else {},
        "bajas_def":     orden.get("resultado", {}).get("bajas_defensor", {}) if orden.get("resultado") else {},
    }
    jugador_atk = orden["jugador"]
    jugador_def = orden.get("jugador_dest")
    victoria_atk = (orden.get("resultado") or {}).get("victoria_atacante", True)

    destinatarios = [jugador_atk] + (jugadores_extra or [])
    if jugador_def and jugador_def not in destinatarios:
        destinatarios.append(jugador_def)
    destinatarios = list(dict.fromkeys(destinatarios))  # deduplicar

    for jug in destinatarios:
        # Perspectiva del informe según el rol del jugador
        es_def = (jug == jugador_def) and (jug != jugador_atk)
        if es_def:
            # El defensor ve: victoria = NOT victoria_atacante, mensaje adaptado
            res_def = dict(orden.get("resultado") or {})
            res_def["victoria_atacante"] = not victoria_atk
            res_def["mensaje"] = (
                "Defensa exitosa — repeliste el ataque"
                if not victoria_atk
                else "Tu ciudad fue atacada — el atacante venció"
            )
            inf_jug = dict(informe)
            inf_jug["resultado"] = res_def
            inf_jug["rol"] = "DEFENSOR"
        else:
            inf_jug = dict(informe)
            inf_jug["rol"] = "ATACANTE"

        def _fn(player, inf=inf_jug):
            informes = player.setdefault("informes", [])
            informes.insert(0, inf)
            if len(informes) > 200:
                player["informes"] = informes[:200]
        try:
            sm.update_player(jug, _fn)
        except Exception as e:
            print(f"[informes] Error guardando informe para {jug}: {e}")


def _ejecutar_retorno(orden: dict, sm, jugador_atk: dict = None) -> dict:
    """Acredita tropas y botín atómicamente usando update_player.
    Las tropas prestadas regresan a sus ciudades de origen.
    """
    _sobrev_raw = orden.get("unidades_sobrevivientes", {})
    _es_fmt_nuevo = bool(_sobrev_raw) and isinstance(next(iter(_sobrev_raw.values()), None), dict)
    sobrevivientes = _sobrev_raw.get(orden["jugador"], {}) if _es_fmt_nuevo else _sobrev_raw
    botin          = orden.get("botin", {})
    ciudad_nombre  = orden["ciudad_origen"]
    tipo_orden     = orden.get("tipo", "")

    print(f"[retorno] {orden['jugador']} ciudad={ciudad_nombre} sobrev={sobrevivientes}")

    # ── Devolver tropas prestadas a sus dueños ────────────────────────────────
    prestadas = orden.get("unidades_prestadas", {})
    if prestadas and tipo_orden != "DESPLAZAMIENTO":
        from backend.systems.alliances import retornar_tropas_prestadas_post_orden
        propietarios = list(prestadas.keys())
        # Para cada dueño: si tiene sobrevivientes registrados, usarlos
        # Si no (espionaje exitoso sin combate), devolver cantidad original completa
        sobrev_prestados = {}
        for dueño in propietarios:
            sobrev_dueño = _sobrev_raw.get(dueño, {}) if _es_fmt_nuevo else {}
            if not sobrev_dueño:
                # Sin registro de bajas → todas sobreviven (espionaje exitoso)
                sobrev_dueño = {k: int(v or 0) for k, v in prestadas[dueño].items()}
            sobrev_prestados[dueño] = sobrev_dueño
        retornar_tropas_prestadas_post_orden(
            jugador_huesped  = orden["jugador"],
            ciudad_huesped   = ciudad_nombre,
            unidades_usadas  = sobrev_prestados,
            propietarios_en_orden = propietarios,
            sm               = sm,
            desplazamiento   = False,
        )
    elif prestadas and tipo_orden == "DESPLAZAMIENTO":
        from backend.systems.alliances import retornar_tropas_prestadas_post_orden
        retornar_tropas_prestadas_post_orden(
            jugador_huesped  = orden["jugador"],
            ciudad_huesped   = ciudad_nombre,
            unidades_usadas  = {dueño: sobrevivientes.get(dueño, {}) for dueño in prestadas},
            propietarios_en_orden = list(prestadas.keys()),
            sm               = sm,
            desplazamiento   = True,
            ciudad_nueva     = orden.get("ciudad_dest"),
        )

    # ── XP distribuida por igual entre propietarios participantes ─────────────
    # El despachador ya recibió su parte al resolver la orden (en _resolver_ataque
    # / _resolver_ataque_entidad). Los prestadores reciben la misma fracción:
    # xp_por_jugador_atk ya viene dividida por número de jugadores desde combat.py.
    # Usamos la XP del despachador como referencia de "parte igual".
    resultado_orden = orden.get("resultado") or {}
    xp_dict = resultado_orden.get("xp") or resultado_orden.get("xp_por_jugador_atk") or {}
    xp_referencia = xp_dict.get(orden["jugador"], 0)

    # Acreditar la misma fracción de XP a cada dueño de tropas prestadas
    for dueño in prestadas:
        if xp_referencia > 0:
            def _fn_xp(player, xp=xp_referencia):
                player["experiencia"] = float(player.get("experiencia", 0) or 0) + xp
            sm.update_player(dueño, _fn_xp)

    def _fn(player):
        ciudad = _buscar_ciudad_nombre(player, ciudad_nombre)
        if not ciudad:
            ciudades = player.get("cities", [])
            if ciudades:
                ciudad = ciudades[0]
                print(f"[retorno] fallback a {ciudad.get('NOMBRE')}")
        if not ciudad:
            print(f"[retorno] ERROR: no se encontró ciudad {ciudad_nombre}")
            return

        for nombre_raw, cant in sobrevivientes.items():
            cant = int(cant or 0)
            if cant <= 0:
                continue
            kg = nombre_raw.replace(" ", "_")
            if nombre_raw in ciudad:
                ciudad[nombre_raw] = int(ciudad.get(nombre_raw, 0) or 0) + cant
            elif kg in ciudad:
                ciudad[kg] = int(ciudad.get(kg, 0) or 0) + cant
            else:
                ciudad[kg] = cant
            print(f"[retorno] +{cant:,} {nombre_raw}")

        for rec, cant in botin.items():
            cant = float(cant or 0)
            if cant > 0:
                ciudad[rec] = float(ciudad.get(rec, 0) or 0) + cant
                print(f"[retorno] botín +{cant:,.0f} {rec}")

    sm.update_player(orden["jugador"], _fn)
    orden["estado"] = "COMPLETADA"
    return {"orden_id": orden["id"], "tipo": orden["tipo"], "ok": True, "msg": "Regreso completado"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _buscar_ciudad(jugador: dict, x: float, y: float, tolerancia: float = 0.5) -> dict | None:
    for city in jugador.get("cities", []):
        if (abs(float(city.get("X", -999)) - x) <= tolerancia and
                abs(float(city.get("Y", -999)) - y) <= tolerancia):
            return city
    return None


def _buscar_ciudad_nombre(jugador: dict, nombre: str) -> dict | None:
    for city in jugador.get("cities", []):
        if city.get("NOMBRE") == nombre:
            return city
    return None


def _unidades_ciudad(city: dict) -> dict:
    """
    Extrae todas las unidades de una ciudad en un dict {NOMBRE: cantidad}.
    Soporta claves con espacios (DRAGON DE ORO) y con guiones bajos (DRAGON_DE_ORO).
    """
    TODAS = [
        "ALDEANO","EXPLORADOR","SACERDOTE","GUERRERO","COMANDO",
        "MERCENARIO","MARINE","CYBORG","MAGO","METAHUMANO",
        "DEMONIO","ANIMA","ESPECTRO","GOLEM","CENTAURO","KRAKEN",
        "ALONARDO","MADRESELVA","COLOSO","FENIX","DRAGON_DE_ORO",
        "CABALLERO_DE_LUZ","ALALAIA","EON_SUPREMO",
    ]
    resultado = {}
    for u in TODAS:
        # Intentar con guión bajo primero, luego con espacio
        val = city.get(u, city.get(u.replace("_", " "), 0))
        cant = int(float(val or 0))
        if cant > 0:
            resultado[u] = cant
    return resultado


def _ciudad_inicial(jugador: str, x: float, y: float,
                    exploradores: int = 0, nivel_tropas: int = 1) -> dict:
    """Crea un dict de ciudad nueva con valores mínimos."""
    import time as t
    nombre = f"{jugador[:2].upper()}_({int(x)},{int(y)})"
    return {
        "NOMBRE":           nombre,
        "JUGADOR":          jugador,
        "X":                x,
        "Y":                y,
        "CENTRO_DE_CIUDAD": 1,
        "CASA":             1,
        "MURALLA":          0,
        "TORRE_DE_VIGILANCIA": 0,
        "CENTRO_DE_VIAJES": 0,
        "ESCONDITE":        0,
        "ALMACEN":          1,
        "SANTUARIO_ARCANO": 0,
        "UNIVERSIDAD":      0,
        "HERRERIA":         0,
        "TEMPLO_1":         0,
        "TEMPLO_2":         0,
        "TEMPLO_3":         0,
        "CUARTEL_1":        0,
        "CUARTEL_2":        0,
        "ALDEANO":          exploradores,  # los exploradores se convierten en aldeanos fundadores
        "EXPLORADOR":       0,
        "SACERDOTE":        0, "GUERRERO":0, "COMANDO":0, "MERCENARIO":0,
        "MARINE":0, "CYBORG":0, "MAGO":0, "METAHUMANO":0,
        "MADERA":0, "PIEDRA":0, "HIERRO":0, "CARBON":0, "ORO":0, "MANA":0,
        "LAST_PROD":        t.time(),
        "COLAS":            [],
        "MIL_QUEUES":       {"C1":[],"C2":[]},
        "INV_QUEUES":       {"T1":[],"T2":[],"T3":[]},
        "OBRAS":            [],
        "ESCONDITE_DATA":   {"materiales":{"MADERA":0,"PIEDRA":0,"HIERRO":0,"CARBON":0,"ORO":0},
                             "tropas":{t:0 for t in ["ALDEANO","EXPLORADOR","SACERDOTE","GUERRERO",
                                       "COMANDO","MERCENARIO","MARINE","CYBORG","MAGO","METAHUMANO"]}},
    }


# ── Info pública ──────────────────────────────────────────────────────────────

def info_orden(orden: dict) -> dict:
    """Retorna estado resumido de una orden para mostrar en la UI."""
    ahora = time.time()
    return {
        "id":       orden["id"],
        "tipo":     orden["tipo"],
        "estado":   orden["estado"],
        "destino":  (orden["x_dest"], orden["y_dest"]),
        "seg_restantes": max(0, (
            orden["t_llegada"] if orden["estado"] == "EN_VIAJE"
            else orden["t_retorno"]
        ) - ahora),
        "resultado": orden.get("resultado"),
    }
