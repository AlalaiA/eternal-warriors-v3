"""
backend/systems/alliances.py
Eternal Warriors v3.0 — Sistema de Alianzas

Reglas canónicas:
  - Máx 50 miembros por alianza
  - IA solo con IA, humanos solo con humanos
  - Un jugador pertenece a una sola alianza a la vez
  - Tropas prestadas: {jugador_dueño, unidad, cantidad, ciudad_origen}
    guardadas en city["TROPAS_PRESTADAS"] del huésped
  - PRESTAMO: tropas viajan de ciudad A a ciudad B — se añaden a TROPAS_PRESTADAS
  - RECLAMAR: dueño solicita retorno → orden de regreso automática
  - En ATAQUE/ESPIONAJE/TRANSPORTE: tropas prestadas regresan a ciudad_origen al terminar
  - En DESPLAZAMIENTO: tropas prestadas se quedan en ciudad destino (siguen prestadas)
  - XP: dividida en partes iguales entre todos los propietarios que participaron
"""

import time
from pathlib import Path

# Jugadores vitaminizados — solo pueden aliarse entre ellos
VITAMINIZADOS = {"ALALAIA", "ADMIN"}
MAX_MIEMBROS  = 50


def _es_vitaminizado(jugador: str) -> bool:
    return jugador.upper() in VITAMINIZADOS


def _migrar_alianza(alianza: dict) -> None:
    """Migra formato viejo {lider: str} al nuevo {lideres: [str]}."""
    if "lider" in alianza and "lideres" not in alianza:
        alianza["lideres"] = [alianza["lider"]]
    if "lideres" not in alianza:
        alianza["lideres"] = []
    if "solicitudes" not in alianza:
        alianza["solicitudes"] = []
    if "miembros" not in alianza:
        alianza["miembros"] = []


def _migrar_todas(alianzas: dict) -> None:
    """Migra todas las alianzas al formato multi-líder."""
    for alianza in alianzas.values():
        _migrar_alianza(alianza)


def _compatibles(j1: str, j2: str) -> bool:
    """
    True si dos jugadores pueden estar en la misma alianza.
    Vitaminizados solo con vitaminizados.
    Todos los demás (humanos, JIARITO, GINAO) pueden aliarse entre sí.
    """
    return _es_vitaminizado(j1) == _es_vitaminizado(j2)


# ── CRUD alianzas ─────────────────────────────────────────────────────────────

def crear_alianza(nombre: str, jugador: str, alianzas: dict) -> dict:
    """
    Crea una nueva alianza. El jugador se convierte en líder.
    Falla si ya pertenece a una alianza.
    """
    jugador = jugador.upper()
    nombre  = nombre.upper().replace(" ", "_")

    if _alianza_de(jugador, alianzas):
        return {"ok": False, "msg": f"{jugador} ya pertenece a una alianza"}
    if nombre in alianzas:
        return {"ok": False, "msg": f"Ya existe una alianza llamada {nombre}"}
    if len(nombre) < 3 or len(nombre) > 30:
        return {"ok": False, "msg": "Nombre de alianza debe tener entre 3 y 30 caracteres"}

    alianzas[nombre] = {
        "nombre":      nombre,
        "tipo":        "vitaminizado" if _es_vitaminizado(jugador) else "normal",
        "lideres":     [jugador],
        "miembros":    [jugador],
        "solicitudes": [],
        "creada":      int(time.time()),
    }
    return {"ok": True, "msg": f"Alianza {nombre} creada", "alianza": alianzas[nombre]}


def solicitar_union(nombre: str, jugador: str, alianzas: dict) -> dict:
    """Envía solicitud para unirse a una alianza existente."""
    jugador = jugador.upper()
    nombre  = nombre.upper().replace(" ", "_")

    if _alianza_de(jugador, alianzas):
        return {"ok": False, "msg": f"{jugador} ya pertenece a una alianza"}
    if nombre not in alianzas:
        return {"ok": False, "msg": f"Alianza {nombre} no existe"}

    alianza = alianzas[nombre]
    _migrar_alianza(alianza)
    if not _compatibles(jugador, alianza["lideres"][0] if alianza["lideres"] else jugador):
        return {"ok": False, "msg": "IA y humanos no pueden aliarse"}
    if len(alianza["miembros"]) >= MAX_MIEMBROS:
        return {"ok": False, "msg": "La alianza está llena (50 miembros)"}
    if jugador in alianza["solicitudes"]:
        return {"ok": False, "msg": "Ya tienes una solicitud pendiente"}

    alianza["solicitudes"].append(jugador)
    return {"ok": True, "msg": f"Solicitud enviada a {nombre}"}


def aceptar_solicitud(nombre: str, solicitante: str, lider: str, alianzas: dict) -> dict:
    """Un líder acepta una solicitud de unión (modelo multi-líder)."""
    lider       = lider.upper()
    solicitante = solicitante.upper()
    nombre      = nombre.upper().replace(" ", "_")

    if nombre not in alianzas:
        return {"ok": False, "msg": "Alianza no encontrada"}
    alianza = alianzas[nombre]
    _migrar_alianza(alianza)
    if lider not in alianza["lideres"]:
        return {"ok": False, "msg": "Solo un líder puede aceptar solicitudes"}
    if solicitante not in alianza.get("solicitudes", []):
        return {"ok": False, "msg": "Solicitud no encontrada"}
    if len(alianza["miembros"]) >= MAX_MIEMBROS:
        return {"ok": False, "msg": "La alianza está llena"}

    alianza["solicitudes"].remove(solicitante)
    if solicitante not in alianza["miembros"]:
        alianza["miembros"].append(solicitante)
    return {"ok": True, "msg": f"{solicitante} se unió a {nombre}"}


def rechazar_solicitud(nombre: str, solicitante: str, ejecutor: str, alianzas: dict) -> dict:
    """Un líder rechaza una solicitud de unión."""
    ejecutor    = ejecutor.upper()
    solicitante = solicitante.upper()
    nombre      = nombre.upper().replace(" ", "_")

    if nombre not in alianzas:
        return {"ok": False, "msg": "Alianza no encontrada"}
    alianza = alianzas[nombre]
    _migrar_alianza(alianza)
    if ejecutor not in alianza["lideres"]:
        return {"ok": False, "msg": "Solo un líder puede rechazar solicitudes"}
    if solicitante not in alianza.get("solicitudes", []):
        return {"ok": False, "msg": "Solicitud no encontrada"}

    alianza["solicitudes"].remove(solicitante)
    return {"ok": True, "msg": f"Solicitud de {solicitante} rechazada"}


def promover_lider(nombre: str, ejecutor: str, miembro: str, alianzas: dict) -> dict:
    """Un líder promueve a un miembro como co-líder."""
    ejecutor = ejecutor.upper()
    miembro  = miembro.upper()
    nombre   = nombre.upper().replace(" ", "_")

    if nombre not in alianzas:
        return {"ok": False, "msg": "Alianza no encontrada"}
    alianza = alianzas[nombre]
    _migrar_alianza(alianza)
    if ejecutor not in alianza["lideres"]:
        return {"ok": False, "msg": "Solo un líder puede promover miembros"}
    if miembro not in alianza["miembros"]:
        return {"ok": False, "msg": f"{miembro} no es miembro de la alianza"}
    if miembro in alianza["lideres"]:
        return {"ok": False, "msg": f"{miembro} ya es líder"}

    alianza["lideres"].append(miembro)
    return {"ok": True, "msg": f"{miembro} promovido a líder de {nombre}"}


def degradar_lider(nombre: str, ejecutor: str, lider_objetivo: str, alianzas: dict) -> dict:
    """Un líder degrada a otro líder (o a sí mismo) a miembro."""
    ejecutor       = ejecutor.upper()
    lider_objetivo = lider_objetivo.upper()
    nombre         = nombre.upper().replace(" ", "_")

    if nombre not in alianzas:
        return {"ok": False, "msg": "Alianza no encontrada"}
    alianza = alianzas[nombre]
    _migrar_alianza(alianza)
    if ejecutor not in alianza["lideres"]:
        return {"ok": False, "msg": "Solo un líder puede degradar a otros líderes"}
    if lider_objetivo not in alianza["lideres"]:
        return {"ok": False, "msg": f"{lider_objetivo} no es líder"}
    if len(alianza["lideres"]) <= 1:
        return {"ok": False, "msg": "La alianza debe tener al menos un líder"}

    alianza["lideres"].remove(lider_objetivo)
    return {"ok": True, "msg": f"{lider_objetivo} degradado a miembro en {nombre}"}


def transferir_liderazgo(nombre: str, lider_actual: str, nuevo_lider: str, alianzas: dict) -> dict:
    """El líder transfiere su rol a otro miembro de la alianza."""
    lider_actual = lider_actual.upper()
    nuevo_lider  = nuevo_lider.upper()
    nombre       = nombre.upper().replace(" ", "_")

    if nombre not in alianzas:
        return {"ok": False, "msg": "Alianza no encontrada"}
    alianza = alianzas[nombre]
    _migrar_alianza(alianza)
    if lider_actual not in alianza["lideres"]:
        return {"ok": False, "msg": "Solo el líder actual puede transferir el liderazgo"}
    if nuevo_lider not in alianza["miembros"]:
        return {"ok": False, "msg": f"{nuevo_lider} no es miembro de la alianza"}
    if nuevo_lider == lider_actual:
        return {"ok": False, "msg": "Ya eres el líder"}

    if lider_actual in alianza["lideres"]:
        alianza["lideres"].remove(lider_actual)
    if nuevo_lider not in alianza["lideres"]:
        alianza["lideres"].append(nuevo_lider)
    return {"ok": True, "msg": f"Liderazgo transferido a {nuevo_lider}"}


def expulsar_o_salir(nombre: str, jugador: str, ejecutor: str, alianzas: dict, sm) -> dict:
    """
    Expulsa a un miembro (solo el líder) o el jugador sale voluntariamente.
    Devuelve tropas prestadas automáticamente.
    """
    jugador  = jugador.upper()
    ejecutor = ejecutor.upper()
    nombre   = nombre.upper().replace(" ", "_")

    if nombre not in alianzas:
        return {"ok": False, "msg": "Alianza no encontrada"}
    alianza = alianzas[nombre]
    _migrar_alianza(alianza)

    es_lider_ejecutor = ejecutor in alianza["lideres"]
    if ejecutor != jugador and not es_lider_ejecutor:
        return {"ok": False, "msg": "Solo un líder puede expulsar miembros"}
    if jugador not in alianza["miembros"]:
        return {"ok": False, "msg": f"{jugador} no es miembro de {nombre}"}
    # Si el jugador es el único líder y hay más miembros, debe transferir primero
    if jugador in alianza["lideres"] and alianza["lideres"] == [jugador] and len(alianza["miembros"]) > 1:
        return {"ok": False, "msg": "Eres el único líder — transfiere el liderazgo antes de salir"}

    alianza["miembros"].remove(jugador)
    if jugador in alianza["lideres"]:
        alianza["lideres"].remove(jugador)

    # Si queda vacía, eliminar alianza
    if not alianza["miembros"]:
        del alianzas[nombre]
    elif not alianza["lideres"]:
        # Asignar el primer miembro como líder de emergencia
        alianza["lideres"] = [alianza["miembros"][0]]

    # Devolver tropas prestadas del jugador que sale
    _devolver_tropas_de(jugador, alianza["miembros"] if nombre in alianzas else [], sm)

    return {"ok": True, "msg": f"{jugador} salió de {nombre}"}


# ── Tropas prestadas ──────────────────────────────────────────────────────────

def prestar_tropas(
    jugador_dueño: str,
    ciudad_origen: str,
    jugador_huesped: str,
    ciudad_destino: str,
    unidades: dict,
    sm,
) -> dict:
    """
    Transfiere tropas de ciudad_origen (dueño) a ciudad_destino (huésped).
    Las tropas se añaden a city["TROPAS_PRESTADAS"] del huésped.
    Se descuentan de la ciudad del dueño.
    """
    jugador_dueño   = jugador_dueño.upper()
    jugador_huesped = jugador_huesped.upper()

    # Validar alianza
    alianzas = sm.load_alliances()
    if not _son_aliados(jugador_dueño, jugador_huesped, alianzas):
        return {"ok": False, "msg": "Solo se pueden prestar tropas a aliados"}
    if jugador_dueño == jugador_huesped:
        return {"ok": False, "msg": "No puedes prestarte tropas a ti mismo"}

    # Validar disponibilidad en ciudad origen
    player_dueño = sm.load_player(jugador_dueño)
    city_orig = _buscar_ciudad(player_dueño, ciudad_origen)
    if not city_orig:
        return {"ok": False, "msg": f"Ciudad {ciudad_origen} no encontrada"}

    for unidad, cant in unidades.items():
        cant = int(cant or 0)
        if cant <= 0:
            continue
        disponible = int(city_orig.get(unidad.upper(), 0) or 0)
        # No contar tropas ya prestadas a otros
        if disponible < cant:
            return {"ok": False, "msg": f"No hay suficientes {unidad} en {ciudad_origen}"}

    # Descontar de ciudad origen
    for unidad, cant in unidades.items():
        cant = int(cant or 0)
        if cant <= 0:
            continue
        u = unidad.upper()
        city_orig[u] = max(0, int(city_orig.get(u, 0) or 0) - cant)

    sm.save_player(jugador_dueño, player_dueño)

    # Añadir a TROPAS_PRESTADAS del huésped
    player_huesped = sm.load_player(jugador_huesped)
    city_dest = _buscar_ciudad(player_huesped, ciudad_destino)
    if not city_dest:
        return {"ok": False, "msg": f"Ciudad destino {ciudad_destino} no encontrada"}

    prestadas = city_dest.setdefault("TROPAS_PRESTADAS", [])
    for unidad, cant in unidades.items():
        cant = int(cant or 0)
        if cant <= 0:
            continue
        # Buscar entrada existente del mismo dueño + unidad + ciudad_origen
        entrada = next(
            (p for p in prestadas
             if p["jugador"] == jugador_dueño
             and p["unidad"].upper() == unidad.upper()
             and p["ciudad_origen"] == ciudad_origen),
            None
        )
        if entrada:
            entrada["cantidad"] += cant
        else:
            prestadas.append({
                "jugador":       jugador_dueño,
                "unidad":        unidad.upper(),
                "cantidad":      cant,
                "ciudad_origen": ciudad_origen,
            })

    sm.save_player(jugador_huesped, player_huesped)
    return {"ok": True, "msg": f"Tropas prestadas a {jugador_huesped} en {ciudad_destino}"}


def reclamar_tropas(
    jugador_dueño: str,
    jugador_huesped: str,
    ciudad_huesped: str,
    unidades: dict,
    sm,
) -> dict:
    """
    El dueño reclama sus tropas prestadas — regresan a su ciudad de origen.
    """
    jugador_dueño   = jugador_dueño.upper()
    jugador_huesped = jugador_huesped.upper()

    player_huesped = sm.load_player(jugador_huesped)
    city = _buscar_ciudad(player_huesped, ciudad_huesped)
    if not city:
        return {"ok": False, "msg": "Ciudad no encontrada"}

    prestadas = city.get("TROPAS_PRESTADAS", [])
    devueltas = {}

    for unidad, cant_reclamar in unidades.items():
        cant_reclamar = int(cant_reclamar or 0)
        if cant_reclamar <= 0:
            continue
        u = unidad.upper()
        entrada = next(
            (p for p in prestadas
             if p["jugador"] == jugador_dueño and p["unidad"] == u),
            None
        )
        if not entrada or entrada["cantidad"] < cant_reclamar:
            return {"ok": False, "msg": f"No hay suficientes {u} para reclamar"}

        entrada["cantidad"] -= cant_reclamar
        if entrada["cantidad"] <= 0:
            prestadas.remove(entrada)
        devueltas[u] = cant_reclamar

    if not devueltas:
        return {"ok": False, "msg": "Nada que reclamar"}

    # Devolver a ciudad de origen del dueño
    player_dueño = sm.load_player(jugador_dueño)
    # Buscar ciudad_origen de la primera entrada (todas deberían tener la misma)
    ciudad_origen = next(
        (p["ciudad_origen"] for p in city.get("TROPAS_PRESTADAS", [])
         if p["jugador"] == jugador_dueño),
        None
    )
    if not ciudad_origen:
        # Fallback: primera ciudad del dueño
        ciudades = player_dueño.get("cities", [])
        ciudad_origen = ciudades[0]["NOMBRE"] if ciudades else None

    if ciudad_origen:
        city_orig = _buscar_ciudad(player_dueño, ciudad_origen)
        if city_orig:
            for u, cant in devueltas.items():
                city_orig[u] = int(city_orig.get(u, 0) or 0) + cant

    sm.save_player(jugador_huesped, player_huesped)
    sm.save_player(jugador_dueño, player_dueño)
    return {"ok": True, "msg": "Tropas reclamadas", "devueltas": devueltas}


def retornar_tropas_prestadas_post_orden(
    jugador_huesped: str,
    ciudad_huesped: str,
    unidades_usadas: dict,
    propietarios_en_orden: list,
    sm,
    desplazamiento: bool = False,
    ciudad_nueva: str = None,
) -> None:
    """
    Llamado después de que se resuelve una orden que usó tropas prestadas.
    - ATAQUE/ESPIONAJE/TRANSPORTE: tropas sobrevivientes regresan a ciudad_origen del dueño
    - DESPLAZAMIENTO: tropas se mueven a ciudad_nueva (siguen prestadas ahí)
    """
    player_huesped = sm.load_player(jugador_huesped)
    city_orig_data = _buscar_ciudad(player_huesped, ciudad_huesped)
    if not city_orig_data:
        return

    prestadas = city_orig_data.get("TROPAS_PRESTADAS", [])

    for prop in propietarios_en_orden:
        if prop == jugador_huesped:
            continue  # tropas propias no se mueven

        # Tropas sobrevivientes de este propietario en la orden
        sobrev = {k: int(v or 0) for k, v in unidades_usadas.get(prop, {}).items() if int(v or 0) > 0}
        if not sobrev:
            continue

        if desplazamiento and ciudad_nueva:
            # Mover entrada a nueva ciudad (dentro del jugador huésped)
            player_new_city = sm.load_player(jugador_huesped)
            city_new = _buscar_ciudad(player_new_city, ciudad_nueva)
            if city_new:
                new_prestadas = city_new.setdefault("TROPAS_PRESTADAS", [])
                for unidad, cant in sobrev.items():
                    entrada = next(
                        (p for p in new_prestadas
                         if p["jugador"] == prop and p["unidad"] == unidad),
                        None
                    )
                    if entrada:
                        entrada["cantidad"] += cant
                    else:
                        # Mantener ciudad_origen original
                        orig = next(
                            (p["ciudad_origen"] for p in prestadas
                             if p["jugador"] == prop and p["unidad"] == unidad),
                            ciudad_huesped
                        )
                        new_prestadas.append({
                            "jugador": prop, "unidad": unidad,
                            "cantidad": cant, "ciudad_origen": orig,
                        })
                sm.save_player(jugador_huesped, player_new_city)
            # Quitar de ciudad actual
            for unidad, cant in sobrev.items():
                entrada = next(
                    (p for p in prestadas
                     if p["jugador"] == prop and p["unidad"] == unidad),
                    None
                )
                if entrada:
                    entrada["cantidad"] = max(0, entrada["cantidad"] - cant)
                    if entrada["cantidad"] <= 0:
                        prestadas.remove(entrada)
        else:
            # ATAQUE/ESPIONAJE/TRANSPORTE → regresar a ciudad_origen de cada entrada
            player_dueño = sm.load_player(prop)

            # Obtener todas las entradas de este dueño con sus ciudades origen
            entradas_prop = [p for p in prestadas if p["jugador"] == prop]

            # Calcular total prestado por unidad para distribuir proporcionalmente
            total_prestado = {}
            for ep in entradas_prop:
                u = ep["unidad"]
                total_prestado[u] = total_prestado.get(u, 0) + ep["cantidad"]

            # Devolver a cada ciudad_origen su proporción de sobrevivientes
            for ep in entradas_prop:
                u = ep["unidad"]
                cant_sobrev_total = sobrev.get(u, 0)
                if cant_sobrev_total <= 0 or total_prestado.get(u, 0) <= 0:
                    continue
                # Proporción: cuánto vuelve a esta ciudad_origen específica
                proporcion = ep["cantidad"] / total_prestado[u]
                cant_retorno = round(cant_sobrev_total * proporcion)
                if cant_retorno <= 0:
                    continue
                city_ret = _buscar_ciudad(player_dueño, ep["ciudad_origen"])
                if not city_ret:
                    # Fallback a primera ciudad
                    ciudades = player_dueño.get("cities", [])
                    city_ret = ciudades[0] if ciudades else None
                if city_ret:
                    city_ret[u] = int(city_ret.get(u, 0) or 0) + cant_retorno

            sm.save_player(prop, player_dueño)

            # Quitar de TROPAS_PRESTADAS del huésped
            for unidad, cant in sobrev.items():
                entrada = next(
                    (p for p in prestadas
                     if p["jugador"] == prop and p["unidad"] == unidad),
                    None
                )
                if entrada:
                    entrada["cantidad"] = max(0, entrada["cantidad"] - cant)
                    if entrada["cantidad"] <= 0:
                        prestadas.remove(entrada)

    sm.save_player(jugador_huesped, player_huesped)


def distribuir_xp_alianza(xp_total: float, propietarios: list) -> dict:
    """
    Divide XP en partes iguales entre todos los propietarios que participaron.
    propietarios: lista de jugadores que aportaron tropas (sin duplicados)
    """
    if not propietarios or xp_total <= 0:
        return {}
    parte = xp_total / len(propietarios)
    return {p: parte for p in propietarios}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _alianza_de(jugador: str, alianzas: dict) -> str | None:
    """Devuelve el nombre de la alianza del jugador, o None."""
    jugador = jugador.upper()
    for nombre, a in alianzas.items():
        if jugador in a.get("miembros", []):
            return nombre
    return None


def _son_aliados(j1: str, j2: str, alianzas: dict) -> bool:
    """True si ambos pertenecen a la misma alianza."""
    a1 = _alianza_de(j1.upper(), alianzas)
    a2 = _alianza_de(j2.upper(), alianzas)
    return a1 is not None and a1 == a2


def _buscar_ciudad(player: dict, nombre: str) -> dict | None:
    for c in player.get("cities", []):
        if c.get("NOMBRE") == nombre:
            return c
    return None


def _devolver_tropas_de(jugador: str, miembros_restantes: list, sm) -> None:
    """Devuelve todas las tropas prestadas de un jugador que ha salido de la alianza."""
    # Buscar en todas las ciudades de todos los miembros restantes
    for miembro in miembros_restantes:
        player = sm.load_player(miembro)
        modificado = False
        for city in player.get("cities", []):
            prestadas = city.get("TROPAS_PRESTADAS", [])
            a_devolver = [p for p in prestadas if p["jugador"] == jugador]
            if not a_devolver:
                continue
            # Devolver al dueño
            player_dueño = sm.load_player(jugador)
            for entrada in a_devolver:
                city_orig = _buscar_ciudad(player_dueño, entrada["ciudad_origen"])
                if city_orig:
                    u = entrada["unidad"]
                    city_orig[u] = int(city_orig.get(u, 0) or 0) + entrada["cantidad"]
            sm.save_player(jugador, player_dueño)
            # Limpiar del huésped
            city["TROPAS_PRESTADAS"] = [p for p in prestadas if p["jugador"] != jugador]
            modificado = True
        if modificado:
            sm.save_player(miembro, player)
