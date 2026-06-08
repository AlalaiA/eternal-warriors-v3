# ETERNAL WARRIORS v3.0 — DOCUMENTO MAESTRO v10.1
**Fecha:** Junio 2026 · **Stack:** Python FastAPI + HTML5 Canvas · **Plataforma:** Windows 10
**Repo:** `https://github.com/AlalaiA/eternal-warriors-v3.git`

---

## ⚠ LECCIONES CRÍTICAS DE CAMBIOS DE CHAT

En sesiones anteriores se perdió trabajo por estos errores. Claude DEBE evitarlos:

1. **Nunca asumir que un fix está instalado en disco.** Siempre verificar con `grep` antes de parchear.
2. **Pedir el archivo actual antes de cada fix.** El archivo en `/mnt/user-data/uploads/` puede diferir del que Claude tiene en contexto.
3. **`__INF__` es un string sentinel**, no float. Usar `safe_resource_float(v)` en lugar de `float(v)`.
4. **El orders_ticker silencia excepciones.** Con `traceback.print_exc()` en el `except` de `main.py` se ven los errores reales.
5. **Los CSV de edificios tienen header partido en 2 líneas** — `csv.reader` los lee como una sola entrada con `\n` embebido. La primera fila de datos es nivel 1.
6. **`unit_levels` tiene dos formatos:** `{NIVEL_DE_TROPAS: N}` (legacy) y `{EXPLORADOR: 40, ...}` (por tipo). Siempre usar `_nivel_tropas_player()`.
7. **`parseInt("1e+20")` devuelve 1** — usar `Math.floor(Number(val))` para cantidades grandes en JS.
8. **El panel derecho de ciudad necesita que `cr` esté definida dentro de `_updateRight`** — no en scope externo.
9. **Nunca reescribir un archivo completo** sin antes leer el archivo exacto en disco. Los anchors de str_replace deben tomarse del archivo actual, no del contexto anterior.

---

## 1. PRERROGATIVAS DE TRABAJO

### 1.1 Protocolo de comunicación
- Claude frena y espera respuesta si necesita un insumo. **Nunca pregunta y sigue produciendo.**
- Respuestas concisas. Sin verbosidad innecesaria.
- Correcciones directas: Jorge corrige supuestos erróneos y Claude los incorpora sin debate.
- **Nunca inventar mecánicas de juego ni valores de CSV.** Si falta info, parar y preguntar.
- **Los CSV son canónicos y no se modifican** salvo instrucción explícita de Jorge.

### 1.2 Protocolo de código
- Siempre: `grep` líneas → `view` rango → `str_replace` exacto. Nunca reescribir archivos completos.
- Validación de sintaxis obligatoria (`ast.parse`) después de cada cambio Python.
- **Audit antes de fix:** leer el archivo exacto del disco antes de parchear.
- **Un fix por problema.** Sin bundling de cambios no relacionados.

### 1.3 Protocolo de arranque de nueva sesión
1. Subir `EW_Maestro_v10.1.md` al nuevo chat.
2. Subir archivos modificados en la sesión anterior.
3. Claude lee el documento, confirma estado y pregunta qué se trabaja.

### 1.4 Archivos clave a subir según contexto

| Archivo | Ruta | Cuándo subir |
|---|---|---|
| `orders.py` | `backend/systems/` | Bugs de órdenes/combate/espionaje |
| `combat.py` | `backend/systems/` | Bugs de combate/sigilo/muralla |
| `espionage.py` | `backend/systems/` | Bugs de espionaje |
| `alliances.py` | `backend/systems/` | Bugs de alianzas/préstamo |
| `queues.py` | `backend/systems/` | Bugs de colas de producción |
| `buildings.py` | `backend/systems/` | Bugs de construcción |
| `production.py` | `backend/systems/` | Bugs de producción de recursos |
| `save_manager.py` | `backend/data/` | PermissionError o race conditions |
| `orders.py` | `backend/api/` | Bugs endpoint órdenes |
| `alliances.py` | `backend/api/` | Bugs endpoint alianzas |
| `city.py` | `backend/api/` | Bugs producción/tick |
| `map.py` | `backend/api/` | Bugs entidades del mapa |
| `leveling.py` | `backend/api/` | Bugs subida de nivel |
| `army.js` | `frontend/js/screens/` | Bugs MISIONES (órdenes) |
| `map.js` | `frontend/js/screens/` | Bugs mapa |
| `reports.js` | `frontend/js/screens/` | Bugs informes |
| `alliance.js` | `frontend/js/screens/` | Bugs pantalla alianzas |
| `city.js` | `frontend/js/screens/` | Bugs pantalla ciudad |
| `invocations.js` | `frontend/js/screens/` | Bugs pantalla EJÉRCITO (producción) |
| `game.html` | `frontend/` | Bugs navegación |
| `joticalindo.json` | `backend/db/players/` | Pérdida de tropas o estado |
| `jiarito.json` | `backend/db/players/` | Pérdida de tropas o estado |
| `orders.json` | `backend/db/global/` | Diagnóstico órdenes en tránsito |
| `alliances.json` | `backend/db/global/` | Diagnóstico alianzas |

---

## 2. STACK Y ARQUITECTURA

### 2.1 Stack tecnológico
| Componente | Tecnología | Versión |
|---|---|---|
| Backend | Python + FastAPI + Uvicorn | 3.12.10 |
| Frontend | HTML5 + Canvas 2D + JS ES Modules | Vanilla |
| Persistencia | JSON plano por jugador + world JSON | Custom |
| Concurrencia | threading.Lock() por archivo | stdlib |

### 2.2 Árbol del proyecto
```
E:\0000ew V2Claude\
├── run.bat                        — limpia __pycache__ antes y después de uvicorn
├── backend/
│   ├── main.py                    — FastAPI + ticker órdenes (5s) + traceback logging
│   ├── api/
│   │   ├── city.py               — producción/tick + XP/batallas/dioses al frontend
│   │   ├── orders.py             — endpoints órdenes + historial combinado
│   │   ├── map.py                — entidades + filtro dioses abatidos por jugador
│   │   ├── queues.py             — colas cuartel/templo
│   │   ├── alliances.py          — endpoints alianzas y préstamo
│   │   ├── leveling.py           — subida de nivel de tropas
│   │   ├── buildings.py
│   │   ├── escondite.py
│   │   └── auth.py
│   ├── systems/
│   │   ├── orders.py             — resolver órdenes (ataque, espionaje, etc.)
│   │   ├── combat.py             — combate, sigilo, muralla, XP entidades
│   │   ├── espionage.py          — espionaje ciudad y entidades
│   │   ├── alliances.py          — alianzas, préstamo, retorno de tropas
│   │   ├── queues.py             — colas de producción e invocación
│   │   ├── production.py         — producción recursos + aldeanos
│   │   ├── buildings.py          — construcción edificios
│   │   └── herreria.py
│   ├── data/
│   │   └── save_manager.py       — I/O JSON con lock + safe_resource_float()
│   └── db/
│       ├── players/              — joticalindo.json, jiarito.json, ginao.json, alalaia.json, admin.json
│       ├── world/                — dioses.json, cuevas.json (999 liberadas), inactivos.json
│       └── global/               — orders.json, alliances.json, accounts.json
├── frontend/
│   ├── game.html                 — nav: CIUDAD · MISIONES · EJÉRCITO · MAPA IMPERIAL
│   │                               INFORMES · ALIANZA · AJUSTES
│   └── js/screens/
│       ├── city.js               — canvas ciudad + panel obras (tick 1s) + leveling modal
│       ├── army.js               — MISIONES: tropas + prestadas + cuevas, MAX fix
│       ├── map.js                — 8 capas toggle, colores diferenciados, filtro dioses
│       ├── reports.js            — polling 5s, informes batalla + espionaje
│       ├── alliance.js           — pantalla alianzas (PENDIENTE completar)
│       ├── invocations.js        — EJÉRCITO: colas cuartel + templo (polling 5s)
│       └── settings.js           — VACÍO
└── csv/                          — CSVs canónicos (tiempos edificios rediseñados)
```

### 2.3 Comandos esenciales
```cmd
run.bat                           — arranca servidor con limpieza de caché
git add -A && git commit -m "msg" && git push
```

---

## 3. CSV CANÓNICOS

| CSV | Descripción | Columnas clave | Notas |
|---|---|---|---|
| `caracteristicas_unidades.csv` | Stats unidades básicas por nivel | col[6]=destreza, col[7]=velocidad, col[8]=sigilo | |
| `caracteristicas_invocaciones.csv` | Stats invocaciones | col[5]=sigilo, col[6]=velocidad, col[7]=nv_min_sacerdote, col[8]=tiempo_SEG, col[9]=costo_mana | Tiempos en SEGUNDOS |
| `tiempo_base_produccion_unidades_basicas.csv` | Tiempo entrenamiento | col[1]=segundos | Header dice minutos — MIENTE |
| `cuevas.csv` | 999 cuevas — 6 tipos | id,x,y,tipo,clase,hp,pa,ca,destreza,velocidad,experiencia,deteccion | Clases: Behemot, Chupacabras, Dragón, Leviatán, Patotas, Simurgh |
| `dioses.csv` | 400 dioses | hp,pa,ca,destreza,experiencia | Ordenados por CA asc. #1=menor CA, #400=mayor CA |
| `portales.csv` / `portales_condiciones.csv` | 10 portales | Condiciones de desbloqueo | PENDIENTE implementar |
| `karlaka.csv` | KarlakÁ en (500,500) | Entidad final | |
| `experiencia_requerida.csv` | XP acumulada para nivel N | nivel, experiencia_requerida | Niveles 2–40 |
| `edificio1..12.csv` | Edificios nv1–50 | costos + stat + tiempo_min | Tiempos NUEVOS (curva jugable 1.5 años TOP) |

### Curva de tiempos de edificios (rediseñada esta sesión)
Objetivo: jugador TOP (universidad nv45 = 99% red., 4 slots, 12 ciudades) tarde ~18 meses en llegar al máximo **con restricción de materiales**:
- Nv 1–2: 0 min (gratis) · Nv 3: 5 min · Nv 5: 30 min
- Nv 10: 1–3 días · Nv 20: 1–2 semanas · Nv 30: 1–2 meses
- Nv 40: 5–13 meses · Nv máx: 18–30 meses

---

## 4. SISTEMAS IMPLEMENTADOS

### 4.1 Save Manager (`backend/data/save_manager.py`)
- Lock por archivo (`_file_locks` + `_meta_lock`) — evita race conditions.
- `update_player(jugador, fn)`: load → fn(data) → save atómico bajo lock.
- `safe_resource_float(v)`: convierte `"__INF__"` → `1e300`. Usar en lugar de `float(v)`.
- `__INF__` = **string en disco y en memoria**. `_SafeEncoder` convierte `float("inf")` → `"__INF__"` al guardar.
- Escritura directa sin `.tmp` + reintento ×3 cada 50ms para `PermissionError` de Windows.

### 4.2 Sistema de Órdenes (`backend/systems/orders.py`)

#### Tipos de orden
| Tipo | Descripción |
|---|---|
| ATAQUE | A ciudad jugador/inactivo/dios/cueva |
| ESPIONAJE | A ciudad o entidad del mundo |
| DESPLAZAMIENTO | Mover tropas entre ciudades propias o aliadas |
| TRANSPORTE | Mover recursos entre ciudades propias |
| FUNDAR | Fundar nueva ciudad (solo con Exploradores, fuera de zona KarlakÁ) |

#### Mecánicas clave
- **Costo oro:** `10 × distancia_euclidiana × cantidad_unidades_básicas` (invocaciones gratis).
- **Tiempo viaje:** `distancia × (50 / velocidad_mínima)` segundos.
- **Velocidad mínima:** incluye tropas propias Y prestadas con su nivel correcto.
- **`_nivel_tropas_player(player, unidades)`:** soporta ambos formatos de `unit_levels`.
- **Retorno automático:** tropas regresan a `ciudad_origen` del despachador.
- **Tropas prestadas:** regresan a ciudad origen del dueño tras ATAQUE/ESPIONAJE/TRANSPORTE. Se quedan en destino tras DESPLAZAMIENTO.
- **`_guardar_informe()`:** llamado al **llegar** (no al regresar) en `_resolver_ataque`, `_resolver_ataque_entidad` y `_resolver_espionaje`.
- **XP distribuida:** igual entre todos los propietarios del bando atacante.
- **Zona prohibida KarlakÁ:** ±50 tiles de (500,500) — solo para FUNDAR.

#### Restricciones de ataque
- **Aliados:** bloqueado en `api/orders.py` antes de crear la orden.
- **Dioses/Cuevas con tropas prestadas:** rechazado — combate vs entidades es INDIVIDUAL.
- **Dios ya derrotado:** validación temprana en `crear_orden` + segunda barrera en `_resolver_ataque`.

#### `unidades_sobrevivientes` — formato actual
```python
# Formato por propietario — _ejecutar_retorno lo detecta automáticamente
orden["unidades_sobrevivientes"] = resultado["sobrevivientes_atk"]
# → {JOTICALINDO: {GUERRERO: N, ...}, JIARITO: {EXPLORADOR: N, ...}}
```

### 4.3 Combate (`backend/systems/combat.py`)

#### Mecánica
- **PA invariable** — nunca se agota. Grupos golpean en orden DESTREZA DESC.
- **Fórmula bajas:** `floor((PA_atk - CA_def) × cantidad_atk / HP_def)`. Si PA ≤ CA → sin daño.
- **Cascada:** si elimina un grupo, PA sobrante pasa al siguiente del mismo bloque DST.
- **Máximo 9 rondas.** Empate → mayor XP de kills gana; empate exacto → victoria del atacante.
- **ATK siempre recibe su turno** aunque DEF tenga mayor DST.

#### Muralla
- HP total por nivel (`edificio3_muralla.csv` col[6]). **Sin CA propia.**
- Pseudo-grupo defensor con `destreza=inf` — siempre al frente.
- Si atacante no la derriba y muere → "El atacante no consiguió traspasar la muralla y murió".
- Regeneración de muralla: **PENDIENTE** (materiales + tiempo por definir).

#### Sigilo — fórmula (v9)
```
sigilo_efectivo = sigilo_max_pelotón
  + por cada unidad adicional:
    si sigilo_unidad ≥ sigilo_max × 0.5 → +3.0
    si sigilo_unidad <  sigilo_max × 0.5 → −1.0
tope máximo: 200
```

**Exploradores nv40 (sigilo=98) vs Torre nv50 (det=101):**

| Exploradores | Sigilo efectivo | Resultado |
|---|---|---|
| 1 | 98 | DETECTADO |
| 2 | 101 | DETECTADO (empate = detectado) |
| 3 | 104 | Nv1 |
| 5 | 110 | Nv2 |
| 8 | 119 | Nv3 |
| 15 | 140 | Nv4 |
| 20 | 155 | **Nv5** ✅ |

#### XP en combate vs entidades
- **Victoria en combate** (HP=0): `xp_atk += ent_xp` durante el combate.
- **Victoria por valor** (9 rondas + ≥80% ald + ≥90% mil): `xp_atk += ent_xp` luego `× 2.0`.
- **Victoria por resistencia** (9 rondas sin cumplir valor): `xp_atk += ent_xp × 1`.
- ⚠ Bug conocido: `valor_cumplido: false` aparece en informes aunque el mensaje diga "Victoria por valor". Pendiente depurar `_verificar_valor`.

### 4.4 Espionaje (`backend/systems/espionage.py`)

#### Detección
```
detectado = sigilo_efectivo <= 0  OR  deteccion_torre >= sigilo_efectivo
```

#### Niveles de inteligencia
| Diferencia (sigilo_ef − det_torre) | Nivel | Información |
|---|---|---|
| ≤ 0 | COMBATE | Combate automático |
| 1–5 | Nv1 | Coords + nombre propietario |
| 6–15 | Nv2 | + Materiales |
| 16–30 | Nv3 | + Tipos unidades/invocaciones |
| 31–53 | Nv4 | + Niveles y cantidades |
| ≥ 54 | Nv5 | Todo: ejércitos con propietarios, escondite, edificios |

### 4.5 Sistema de Alianzas

#### Reglas de negocio
- Máximo **50 miembros** por alianza.
- **VITAMINIZADOS** (ALALAIA + ADMIN): alianza especial, no se pueden aliar con nadie externo.
- Un jugador pertenece a **una sola alianza** a la vez.
- Si un jugador sale o es expulsado → sus tropas prestadas regresan automáticamente.
- **No se puede atacar ni espiar a un aliado** — validado en `api/orders.py`.
- **Combate vs dioses/cuevas con tropas prestadas: PROHIBIDO** — solo individual.

#### Alianzas actuales en disco
| Alianza | Tipo | Líder | Miembros |
|---|---|---|---|
| AAA_KILLERS | normal | JOTICALINDO | JOTICALINDO, JIARITO, GINAO |
| VITAMINIZADOS | vitaminizado | ADMIN | ADMIN, ALALAIA |

#### Tropas prestadas — estructura en ciudad huésped
```json
"TROPAS_PRESTADAS": [
  {"jugador": "JIARITO", "unidad": "EXPLORADOR", "cantidad": 9780, "ciudad_origen": "Bogotá"}
]
```
- ATAQUE/ESPIONAJE/TRANSPORTE → regresan a `ciudad_origen` del dueño al terminar.
- DESPLAZAMIENTO → se quedan en destino.

#### Endpoints (`backend/api/alliances.py`)
```
GET    /api/alliances                          — listar alianzas
GET    /api/alliances/{jugador}                — alianza del jugador
POST   /api/alliances/crear                    — crear alianza
POST   /api/alliances/solicitar                — solicitar unirse
POST   /api/alliances/aceptar                  — aceptar solicitud (líder)
POST   /api/alliances/salir                    — salir o expulsar
POST   /api/alliances/prestar                  — prestar tropas a aliado
POST   /api/alliances/reclamar                 — reclamar tropas prestadas
GET    /api/alliances/{jugador}/tropas_prestadas
```

#### ⚠ PENDIENTE — UI de Alianzas (PRÓXIMA SESIÓN PRIORITARIO)
`alliance.js` existe pero el flujo completo **no está implementado ni probado**. Pendiente:
- Ver alianza actual, crear, solicitar, aceptar/rechazar, expulsar, salir
- Prestar y reclamar tropas desde la UI
- Definir si hay rangos además de líder/miembro
- ¿Descripción/lema de alianza?
- ¿Límite de tropas prestables simultáneamente?
- ¿Qué pasa si la alianza se disuelve con tropas prestadas?

### 4.6 Informes
- `_guardar_informe()` llamado al **llegar** (no al regresar).
- Historial = órdenes propias completadas + `player["informes"]`, deduplicados por ID.
- Polling **5 segundos** en `reports.js`.
- Muestra: ejército enviado (propias + prestadas con 🤝), bajas, XP ganada, sigilo.

### 4.7 Colas de Producción (`backend/systems/queues.py`)
- **2 slots simultáneos** por cuartel y por templo (hasta 3 templos = 6 slots invocación).
- **Tiempo cuartel:** `base_seg × (1 - red_cuartel/100 - red_universidad/100)`, cap 95%.
- **Tiempo templo:** `base_seg × (1 - reb_templo/100 - red_universidad/100)`, cap 95%.
- CSV unidades: tiempos en **SEGUNDOS** (el header dice minutos — miente).
- Pantalla **EJÉRCITO** (`invocations.js`): colas activas con barra de progreso (polling 5s).

### 4.8 Producción de Recursos (`backend/systems/production.py`)
- **Recursos:** `aldeanos × tasa_material_por_aldeano_por_hora[nivel_CC]` — cap por almacén.
- **Maná:** `sacerdotes × mana_por_sacerdote_por_hora[nivel_sacerdote]` — cap por santuario.
- **Aldeanos:** producidos por Centro de Ciudad a `aldeanos/hora[nivel_CC]` — cap por Casa.
- **Aldeanos NO se producen en cuartel** — el cuartel entrena tropas militares.
- Retroactividad máx: 3 días (`LAST_PROD` timestamp).
- Caché de módulo: `_CC_TASAS`, `_MATERIAL_TASAS`, etc. se cargan una vez al arrancar.

### 4.9 Sistema de Niveles de Tropas (`backend/api/leveling.py`)
- Solo tropas básicas del cuartel tienen nivel: ALDEANO, EXPLORADOR, SACERDOTE, GUERRERO, COMANDO, MERCENARIO, MARINE, CYBORG, MAGO, METAHUMANO.
- **Invocaciones NO tienen nivel. Criaturas de cueva NO tienen nivel.**
- El jugador decide **manualmente** a qué tropa asignar XP del pool global `player["experiencia"]`.
- Nivel máximo efectivo: `min(40, 20 + floor(len(dioses_abatidos) / 20))`.
- **Endpoint:** `GET /api/leveling/{jugador}` · `POST /api/leveling/{jugador}/subir {tipo}`.
- **UI:** botón "⬆ Subir nivel de tropas" en panel de Progreso → modal que actualiza in-place sin parpadeo.

#### XP requerida por nivel (`experiencia_requerida.csv`)
Nv2: 3.3M · Nv5: 13.6M · Nv10: 450M · Nv20: 950M · Nv30: 1.87T · Nv40: 1.95T

### 4.10 Mapa Imperial (`frontend/js/screens/map.js`)
- **8 capas toggle:** 👤 Humanos · 🤝 Alianza · 💊 Vitaminizados · 🏚 Inactivos · 🌩 Dioses · 🦎 Cuevas · 🌀 Portales · ☠ KarlakÁ
- **Colores:** propias=verde, aliadas=azul claro, vitaminizadas=magenta, rivales=dorado, inactivos=azul, dioses=morado, cuevas=naranja, portales=cian, karlakÁ=rojo.
- **Dioses abatidos** filtrados por jugador: `/api/map/entities?jugador=JOTICALINDO`.
- Solo muestra órdenes `EN_VIAJE` o `REGRESANDO`.
- Coordenadas en **enteros** (`Math.round`). Botón 🏠 navega a la primera ciudad propia.

### 4.11 Pantalla Ciudad (`frontend/js/screens/city.js`)
- **Canvas isométrico** con 12 edificios + muralla + torres de vigilancia.
- **Panel izquierdo:**
  - ▼ Recursos (∞ para __INF__)
  - ▼ Producción / Hora
  - ▼ Logística (niveles edificios clave)
  - ▼ Construcciones (N) — obras activas con barra de progreso actualizada cada **1 segundo**. Se ocultan automáticamente al completarse.
  - ▼ Progreso — XP, batallas, dioses, cuevas + botón "⬆ Subir nivel de tropas"
- **Panel derecho:**
  - ▼ Ejército (tropas básicas)
  - ▼ Invocaciones
  - ▼ Criaturas de Cueva (naranja, solo si hay capturadas)
  - ⚒ Herrería (bonus PA/CA/HP)
- **Sync:** tick de 1s para recursos + obras. Sync completo con backend cada **10 segundos**.

### 4.12 Pantalla MISIONES (`frontend/js/screens/army.js`)
- Tropas propias: básicas + invocaciones + criaturas de cueva (naranja).
- Tropas aliadas prestadas: agrupadas por propietario con 🤝.
- **MAX fix:** usa `Math.floor(Number(val))` — `parseInt("1e+20")` daba `1`.
- FUNDAR: solo Exploradores. Criaturas de cueva no pueden fundar.
- Formulario de orden persiste estado entre renders.

### 4.13 Pantalla EJÉRCITO (`frontend/js/screens/invocations.js`)
- Muestra colas activas de cuarteles y templos con barra de progreso.
- Formularios: Cuartel 1/2, Templo 1/2/3, tropa/invocación, cantidad.
- Polling 5s.

### 4.14 Construcción de Edificios (`backend/systems/buildings.py`)
- Máximo **4 obras simultáneas** por ciudad (formato nuevo con `inicio` y `duracion_seg`).
- Obras en formato viejo (`KEY/TIEMPO/TOTAL`) son datos legacy — no bloquean el límite.
- `_apply_univ_reduction(tiempo_seg, nivel_universidad)`: aplica reducción de universidad al tiempo base.
- Universidad reduce: colas (col[6]) y edificios (col[7]) — dos estadísticas distintas.

---

## 5. MECÁNICAS DE JUEGO

### 5.1 Combate JvJ (Jugador vs Jugador)
- Puede ser **conjunto**: varios jugadores de la misma alianza atacan juntos con tropas prestadas.
- XP dividida en partes **iguales** entre todos los propietarios del bando atacante.
- Tropas prestadas participan con sus stats de nivel correcto del dueño.
- El defensor **no sabe** del ataque hasta que la orden llega.
- El defensor **no ve el ataque en sus informes** (pendiente implementar).

### 5.2 Combate vs Dioses
- **INDIVIDUAL** — rechazado al despachar si hay tropas prestadas.
- **Un dios solo puede ser vencido una vez por jugador.** Bloqueado al despachar.
- El dios queda `_derrotado=True, HP=0` en `dioses.json` para todos los jugadores.
- El dios desaparece del mapa del jugador que lo venció.
- Victorias: en combate (HP=0), por valor (≥80% ald + ≥90% mil, XP×2), por resistencia (9 rondas).
- Sin botín de materiales. Solo XP.

### 5.3 Combate vs Cuevas
- **INDIVIDUAL** — rechazado al despachar si hay tropas prestadas.
- **Victoria:** criatura capturada → añadida en `ciudad_origen` del atacante.
  - Claves JSON: `BEHEMOT`, `CHUPACABRAS`, `DRAGON`, `LEVIATAN`, `PATOTAS`, `SIMURGH` (sin tildes).
  - ⚠ En disco puede existir `"DRAGÓN"` (con tilde) por capturas antiguas — es legacy.
- **Derrota:** la criatura vuelve al mapa (no muere).
- La cueva puede ser atacada de nuevo por el mismo jugador (sin restricción de una vez).
- Sin botín de materiales. Solo XP.

### 5.4 Criaturas de Cueva — Captura e Incorporación
1. Jugador ataca cueva en el mapa.
2. Victoria → `_capturar_criatura()` añade +1 al tipo en `ciudad_origen`.
3. La cueva queda `_derrotado=True` en `cuevas.json`, desaparece del mapa.
4. La criatura aparece en MISIONES y CIUDAD como unidad disponible (en naranja).
5. Disponible para todas las misiones **excepto FUNDAR**.
6. No tiene nivel propio. No se puede invocar desde templo.

### 5.5 Progresión de Tropas
- **Pool global** `player["experiencia"]` acumula XP de todos los combates.
- **Asignación manual** desde el modal de subida de nivel en CIUDAD.
- **Niveles 1–20:** por XP del pool.
- **Niveles 21–40:** cada nivel adicional requiere 20 dioses abatidos más.
  - `nivel_max = min(40, 20 + floor(len(dioses_abatidos) / 20))`
- **Solo tropas básicas tienen nivel.** Invocaciones y criaturas de cueva, no.

### 5.6 Producción de Aldeanos
- **Fuente:** Centro de Ciudad produce aldeanos a `aldeanos/hora[nivel_CC]`.
- **Cap:** capacidad máxima según nivel de Casa.
- Retroactividad máx: 3 días.
- **Los aldeanos NO se producen en cuartel.**

### 5.7 Máximo de Ciudades y Fundación
- Máximo por jugador definido en `player["cities"][0]["CIUDADES_MAXIMAS_POR_JUGADOR"]`.
- JOTICALINDO: 12 ciudades (jL01–jL12).
- Fundar requiere: Exploradores (solo ellos), coordenada libre, fuera de zona KarlakÁ.
- **Zona prohibida KarlakÁ:** ±50 tiles de (500,500) — **solo para FUNDAR**, no para ataques.

### 5.8 Cuentas Vitaminizadas (ALALAIA y ADMIN)
- Sus recursos son `"__INF__"` — string sentinel, nunca float.
- Reposición de tropas cuando son atacadas: **pendiente integrar** a `orders.py`.
- No pueden aliarse fuera de VITAMINIZADOS.
- ADMIN: 14 ciudades (Admin02–Admin15). ALALAIA: 14 ciudades (AlalaiA02–AlalaiA15).

### 5.9 Dioses
- 400 dioses ordenados por CA ascendente (CSV `dioses.csv`).
- Cada jugador solo puede vencer **una vez** cada dios.
- Los dioses vencidos desaparecen del mapa del jugador que los venció.
- XP del dios: campo `experiencia` del CSV.
- Cada 20 dioses vencidos → +1 nivel máximo de tropas (hasta nv40 = 400 dioses).
- `player["dioses_abatidos"]` = lista de IDs: `["Dios-001", "Dios-002", ...]`.

### 5.10 Portales
- 10 portales en el mapa (`portales.csv`).
- Condiciones de desbloqueo en `portales_condiciones.csv`:
  - nivel mínimo tropas, batallas ganadas, cuevas derrotadas, misiones espionaje, porcentaje resistencia KarlakÁ, top militar, cuentas hijo, nivel cuentas alianza.
- **Sistema de portales: PENDIENTE DE IMPLEMENTAR COMPLETAMENTE.**

### 5.11 KarlakÁ
- HP=5e17, PA=4.5e18, CA=5e18.
- Solo puede ser atacada con **1 Éon Supremo**.
- Si se ataca con más de 1 unidad o con non-ÉON SUPREMO → PA se multiplica ×100.000.
- Zona prohibida (solo para FUNDAR): ±50 tiles de (500,500).

### 5.12 Herrería
- Bonus global PA/CA/HP sumado de todas las herrerías de todas las ciudades del jugador.
- `calcular_bonus_herreria(player)` → `{pa_bonus, ca_bonus, hp_bonus, detalle}`.
- **NO afecta invocaciones** — solo tropas básicas.
- Se muestra en el panel derecho de CIUDAD.

### 5.13 NG+ (New Game Plus)
- Ciclo de reinicio tras derrotar a KarlakÁ.
- **PENDIENTE DE DISEÑAR E IMPLEMENTAR.**

---

## 6. JUGADORES Y MUNDO

### 6.1 Jugadores
| Jugador | Tipo | Ciudades | Capital | Notas |
|---|---|---|---|---|
| JOTICALINDO | Humano/test | 12 (jL01–jL12) | jL01 (242,522) | Cuenta principal de Jorge |
| JIARITO | Especial/aliado | 15 | Bogotá (666,666) | `unit_levels={EXPLORADOR:40,...}` por tipo |
| GINAO | Especial/aliado | Variable | — | Aliado AAA_KILLERS |
| ALALAIA | Vitaminizada | 14 | — | Recursos __INF__ |
| ADMIN | Vitaminizado | 14 | — | Recursos __INF__ |

### 6.2 Estado actual de JOTICALINDO (al cierre de esta sesión)
- `unit_levels`: todos en nivel **21** (por tipo: MAGO, SACERDOTE, ALDEANO, EXPLORADOR, GUERRERO, COMANDO, METAHUMANO, CYBORG, MARINE, MERCENARIO)
- `experiencia`: ~4.61×10¹⁷
- `dioses_abatidos`: **45** (Dios-001 a Dios-045) → nivel máx desbloqueado = **22**
- `batallas_ganadas`: 14, `batallas_perdidas`: 1
- `cuevas_derrotadas`: 2, `misiones_espionaje`: 29
- Criaturas capturadas en jL01: `DRAGON: 2` (legacy con tilde; nuevo formato: `DRAGON`)
- Ciudades jL01–jL12, todas en radio estrecho (242–245, 520–522)
- jL01 tiene OBRAS activas — universidad nv10, herrería nv6, cuartel1 nv9, cuartel2 nv6

### 6.3 Distribución del mundo (1000×1000 tiles)
- 300 ciudades inactivas · 72 ciudades IA · 400 dioses · 999 cuevas (liberadas) · 10 portales · KarlakÁ (500,500)

---

## 7. BUGS RESUELTOS (acumulado completo)

| Bug | Causa | Fix |
|---|---|---|
| Tropas desaparecen al regresar | Race condition | `update_player()` atómico con lock |
| PermissionError .tmp Windows | `os.replace()` falla | Escritura directa sin .tmp + reintento ×3 |
| `__INF__` crashea ticker | `float("__INF__")` en varios archivos | `safe_resource_float()` + parches en `espionage.py`, `orders.py` |
| Orden espionaje congelada | `unidades={}` → retorno fallaba | Fix `unidades_sobrevivientes` en espionaje exitoso |
| Informe no llega tras combate | `_guardar_informe` no llamado en `_resolver_ataque` ni `_resolver_ataque_entidad` | Añadido en ambas funciones |
| Informe tarda minutos | Se guardaba al regresar | `_guardar_informe` al llegar; historial incluye `player["informes"]` |
| Nivel tropas = 1 en orden | `api/orders.py` leía `NIVEL_DE_TROPAS` inexistente | Usar `_nivel_tropas_player()` |
| Dios atascado en ticker | `_verificar_valor` hacía `float(v)` sobre NOMBRE="jL01" | Skip campos no-numéricos |
| Dios ya derrotado atascaba ticker | Sin validación temprana | Validación en `crear_orden` + barrera en `_resolver_ataque` |
| Ciudades ADMIN no en mapa | `JUGADORES_ACTIVOS` sin ADMIN | Añadido + categoría `CIUDAD_VITAMINIZADA` |
| Mapa clusters tapaban ciudades | Umbral cluster `< 2` muy alto | Bajado a `< 0.3` |
| Panel derecho ciudad en blanco | `cr` usada antes de definirse | Definir `cr` dentro de `_updateRight` |
| Construcciones legacy no desaparecen | Obras formato viejo sin filtrar | Panel filtra obras con `pct >= 100` |
| Obras no se ocultan al completarse | Sin filtro de tiempo transcurrido | Filtrar `obrasData` donde `(now - inicio) >= duracion_seg` |
| Barras de obras estáticas | Solo se actualizaban en sync (30s) | Ticker de 1s con `data-obra-inicio`/`data-obra-dur` en DOM |
| Sync ciudad muy lento | Intervalo de 30 segundos | Bajado a 10 segundos |
| MAX toma entero < 9 con números grandes | `parseInt("1e+20")` devuelve `1` | `Math.floor(Number(val))` en `army.js` |
| Sigilo=8 explorador nv40 JIARITO | `NIVEL_DE_TROPAS` no existe en JIARITO | `_nivel_tropas_player()` soporta ambos formatos |
| XP no visible en ciudad | `api/city.py` no exponía `experiencia` | Añadidos campos jugador en respuesta |
| Informes solo muestran tropas propias | `reports.js` ignoraba `unidades_prestadas` | Mostrar prestadas con 🤝 + bajas prestadas |
| Tiempos producción 60× rápidos | CSV en segundos pero código ×60 | Eliminado ×60 en `queues.py` |
| Tropas prestadas regresan a ciudad incorrecta | `sobrev_prestados={}` | Si sin bajas → devolver cantidad original |
| Criaturas de cueva clave con tilde | `CLASE_A_UNIDAD` mapeaba a `DRAGÓN` | Normalizado a `DRAGON`, `LEVIATAN`, etc. sin tildes |
| Dioses bloqueados por conteo incorrecto | Migración int→lista incompleta | Lista reconstruida manualmente (45 dioses) |

---

## 8. PENDIENTES PRIORIZADOS

### 8.1 PRÓXIMA SESIÓN — Alianzas UI (PRIORITARIO #1)
`alliance.js` tiene la estructura pero el flujo completo no está implementado ni probado:
1. Ver alianza actual, crear, solicitar, aceptar/rechazar, expulsar, salir
2. Prestar y reclamar tropas desde la UI
3. Definir: ¿rangos? ¿descripción/lema? ¿límite de tropas prestables? ¿qué pasa al disolver?
4. Testar flujo completo: crear → invitar → aceptar → prestar → reclamar → expulsar

### 8.2 PRÓXIMA SESIÓN — Mensajería Interna (PRIORITARIO #2)
- Mensaje directo jugador→jugador
- Mensaje broadcast a alianza
- Notificaciones de eventos (ataque recibido, solicitud alianza, etc.)
- Almacenamiento: `player["mensajes"][]` o tabla separada
- ¿Polling (5s) o WebSocket?

### 8.3 Funcionales
- **Reposición vitaminizadas**: lógica existe en `experience.py`, no integrada a `orders.py`.
- **Regeneración de muralla**: materiales + tiempo (pendiente definir).
- **Sistema de portales**: condiciones de desbloqueo implementadas en CSV, no en código.
- **NG+**: ciclo de reinicio con KarlakÁ. Sin diseñar.
- **Ataques recibidos en informes**: el defensor no ve el ataque en sus informes.
- **WebSocket**: actualmente polling 5s. Mejora de UX futura.
- **Imágenes**: `alalaia_small.png` / `karlaka_small.png` dan 404.
- **Pantalla Ajustes** (`settings.js`): vacía.
- **Centrado del mapa** en ciudad propia al navegar.
- **Bug `valor_cumplido: false`**: mensaje "Victoria por valor" contradice el campo. Depurar `_verificar_valor`.

### 8.4 Técnicos
- Float precision para aldeano >1e15.
- `LAST_PROD` de JL2–JL12 muy antiguo → producción retroactiva exagerada al cargar.
- Campos legacy en ciudades: `JUGADOR`, `NIVEL_DE_TROPAS`, `TIPO_JUGADOR`, `NIVEL_DE_TROPA`.
- Clave `"DRAGÓN": 2` (con tilde) en jL01 — legacy, no rompe nada pero es inconsistente.

---

## 9. NOTAS DE DISEÑO — REGLAS QUE NUNCA CAMBIAN

- **JIARITO no es IA autónoma** — cuenta especial controlada por Jorge.
- **`unit_levels` de JIARITO:** `{EXPLORADOR: 40, GUERRERO: 40, ...}` (nivel por tipo).
- **`unit_levels` de JOTICALINDO:** `{MAGO: 21, ...}` (nivel por tipo, migrado).
- **Siempre `_nivel_tropas_player()`** para leer nivel de cualquier jugador.
- **La herrería NO afecta invocaciones** — solo tropas básicas.
- **Las invocaciones NO tienen nivel** — son las que son.
- **Las criaturas de cueva NO tienen nivel** — capturadas tal cual.
- **Aldeanos: producidos por CC, no por cuartel.**
- **Zona prohibida KarlakÁ: solo para FUNDAR**, no para ataques.
- **Dioses: un jugador, un dios, una vez.**
- **Combate vs dioses/cuevas: SIEMPRE individual** (sin tropas prestadas).
- **`__INF__`** es string en JSON y en memoria Python. Usar `safe_resource_float()` para aritmética.
- **Tiempos de edificios nuevos**: curva exponencial rediseñada — CSVs en `csv/` reemplazados.
- **Criaturas de cueva**: 6 tipos fijos (Behemot, Chupacabras, Dragón, Leviatán, Patotas, Simurgh). Claves JSON sin tildes: BEHEMOT, CHUPACABRAS, DRAGON, LEVIATAN, PATOTAS, SIMURGH.
- **Invocaciones**: 14 tipos (Demonio, Ánima, Espectro, Gólem, Centauro, Kraken, Alonardo, Madreselva, Coloso, Fénix, Dragón de Oro, Caballero de Luz, AlalaiA, Éon Supremo). Claves: DEMONIO, ANIMA, ESPECTRO, GOLEM, CENTAURO, KRAKEN, ALONARDO, MADRESELVA, COLOSO, FENIX, DRAGON_DE_ORO, CABALLERO_DE_LUZ, ALALAIA, EON_SUPREMO.
- **Tropas básicas**: 10 tipos (Aldeano, Explorador, Sacerdote, Guerrero, Comando, Mercenario, Marine, Cyborg, Mago, Metahumano).
- **Navtabs** (game.html): CIUDAD · MISIONES · EJÉRCITO · MAPA IMPERIAL · INFORMES · ALIANZA · AJUSTES. (MISIONES=army.js, EJÉRCITO=invocations.js).
