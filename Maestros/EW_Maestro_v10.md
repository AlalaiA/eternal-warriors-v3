# ETERNAL WARRIORS v3.0 — DOCUMENTO MAESTRO v10.0
**Fecha:** Junio 2026 · **Stack:** Python FastAPI + HTML5 Canvas · **Plataforma:** Windows 10

---

## ⚠ LECCIÓN CRÍTICA DE CAMBIOS DE CHAT

En sesiones anteriores se perdió trabajo por estos errores. Claude DEBE evitarlos:

1. **Nunca asumir que un fix está instalado en disco.** Siempre verificar con `grep` antes de parchear.
2. **Pedir el archivo actual antes de cada fix.** El archivo en `/mnt/user-data/uploads/` puede diferir del que Claude tiene en contexto de sesiones anteriores.
3. **`__INF__` es un string sentinel**, no float. `save_manager.py` lo preserva como string en memoria. Usar `safe_resource_float(v)` en lugar de `float(v)` para recursos.
4. **El orders_ticker silencia excepciones.** Añadir `traceback.print_exc()` al `except` de `main.py` cuando haya bugs misteriosos.
5. **Los CSV de edificios tienen header partido en 2 líneas** — `csv.reader` los lee correctamente como una sola entrada con `\n` embebido.
6. **`unit_levels` tiene dos formatos:** `{NIVEL_DE_TROPAS: N}` (legacy JOTICALINDO) y `{EXPLORADOR: 40, ...}` (JIARITO). Siempre usar `_nivel_tropas_player()`.

---

## 1. PRERROGATIVAS DE TRABAJO

### 1.1 Protocolo de comunicación
- Claude frena y espera respuesta antes de continuar si necesita un insumo.
- Nunca pregunta dentro de una acción y sigue produciendo — primero pregunta, luego actúa.
- Respuestas concisas. Sin verbosidad innecesaria.
- Correcciones directas: Jorge corrige supuestos erróneos y Claude los incorpora sin debate.
- **Nunca inventar mecánicas de juego ni valores de CSV.** Si falta info, parar y preguntar.
- **Los CSV son canónicos y no se modifican** salvo instrucción explícita de Jorge.

### 1.2 Protocolo de código
- Siempre: `grep` líneas → `view` rango → `str_replace` exacto. Nunca reescribir archivos completos.
- Validación de sintaxis obligatoria (`ast.parse`) después de cada cambio Python.
- Para archivos grandes: scripts Python ejecutados en bash.
- **Audit antes de fix:** leer el archivo exacto del disco antes de parchear.
- **Un fix por problema.** Sin bundling de cambios no relacionados.

### 1.3 Protocolo de arranque de nueva sesión
1. Subir `EW_Maestro_v10.md` al nuevo chat.
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
| `army.js` | `frontend/js/screens/` | Bugs formulario órdenes (ahora: MISIONES) |
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
├── run.bat                        — arranque con limpieza de caché automática
├── backend/
│   ├── main.py                    — FastAPI app + ticker órdenes (5s) + traceback logging
│   ├── api/
│   │   ├── city.py               — producción/tick + expone XP/batallas/dioses al frontend
│   │   ├── orders.py             — endpoints órdenes (historial combinado)
│   │   ├── map.py                — entidades con filtro de dioses abatidos por jugador
│   │   ├── queues.py             — colas cuartel/templo
│   │   ├── alliances.py          — endpoints alianzas y préstamo de tropas
│   │   ├── leveling.py           — subida de nivel de tropas (NUEVO)
│   │   ├── buildings.py
│   │   ├── escondite.py
│   │   └── auth.py
│   ├── systems/
│   │   ├── orders.py             — resolver órdenes
│   │   ├── combat.py             — combate, sigilo, muralla, XP entidades
│   │   ├── espionage.py          — espionaje ciudad y entidades
│   │   ├── alliances.py          — alianzas, préstamo, retorno de tropas
│   │   ├── queues.py             — colas de producción e invocación
│   │   ├── production.py         — producción recursos + aldeanos
│   │   ├── buildings.py          — construcción de edificios
│   │   ├── herreria.py
│   │   └── experience.py         — tablas XP unidades/invocaciones (módulo auxiliar)
│   ├── data/
│   │   └── save_manager.py       — I/O JSON con lock + safe_resource_float() para __INF__
│   └── db/
│       ├── players/
│       │   ├── joticalindo.json
│       │   ├── jiarito.json
│       │   ├── ginao.json
│       │   ├── alalaia.json
│       │   └── admin.json
│       ├── world/
│       │   ├── dioses.json
│       │   ├── cuevas.json       — 999 cuevas liberadas, stats restaurados del CSV
│       │   └── inactivos.json
│       └── global/
│           ├── orders.json
│           ├── alliances.json    — AAA_KILLERS + VITAMINIZADOS
│           └── accounts.json
├── frontend/
│   ├── game.html                 — nav: CIUDAD · MISIONES · EJÉRCITO · MAPA IMPERIAL
│   │                               INFORMES · ALIANZA · AJUSTES
│   ├── js/
│   │   ├── app.js
│   │   └── screens/
│   │       ├── city.js           — panel obras, progreso XP, criaturas cueva
│   │       ├── army.js           — MISIONES: tropas propias + prestadas + cuevas
│   │       ├── map.js            — capas toggle + colores diferenciados
│   │       ├── reports.js        — polling 5s, ejército enviado completo
│   │       ├── alliance.js       — pantalla alianzas
│   │       ├── invocations.js    — EJÉRCITO: colas cuartel + templo
│   │       └── settings.js
│   └── css/
└── csv/                          — CSVs canónicos (NO MODIFICAR salvo tiempos edificios)
```

### 2.3 Comandos esenciales
```cmd
cd E:\0000ew V2Claude
run.bat                           — lanza servidor limpiando caché automáticamente
git add -A && git commit -m "mensaje" && git push
```

---

## 3. CSV CANÓNICOS

| CSV | Descripción | Columnas clave | Notas |
|---|---|---|---|
| `caracteristicas_unidades.csv` | Stats unidades básicas por nivel | col[6]=destreza, col[7]=velocidad, col[8]=sigilo | |
| `caracteristicas_invocaciones.csv` | Stats invocaciones | col[5]=sigilo, col[6]=velocidad, col[7]=nv_min_sacerdote, col[8]=tiempo_SEG, col[9]=costo_mana | Tiempos en SEGUNDOS |
| `tiempo_base_produccion_unidades_basicas.csv` | Tiempo entrenamiento tropas | col[1]=segundos | Header dice minutos — MIENTE, son segundos |
| `cuevas.csv` | 999 cuevas — 6 tipos | id,x,y,tipo,clase,hp,pa,ca,destreza,velocidad,experiencia,deteccion | 6 clases: Behemot, Chupacabras, Dragón, Leviatán, Patotas, Simurgh |
| `dioses.csv` | 400 dioses ordenados por CA asc | hp,pa,ca,destreza,experiencia | #1=menor CA, #400=mayor CA |
| `portales.csv` / `portales_condiciones.csv` | 10 portales | Condiciones de desbloqueo | |
| `karlaka.csv` | KarlakÁ en (500,500) | Entidad final | |
| `experiencia_requerida.csv` | XP acumulada para nivel N | nivel, experiencia_requerida | Niveles 2–40 |
| `experiencia_dada_por_unidades_basicas_por_nivel.csv` | XP por matar 1 unidad básica | tipo, nivel, exp | |
| `experiencia_por_invocaciones.csv` | XP por matar 1 invocación | tipo, exp | |
| `edificio1_centro_de_ciudad.csv` | Centro de Ciudad (nv1–45) | col[6]=aldeanos/hora, col[7]=tiempo_min | Tiempos NUEVOS: curva jugable 1.5 años TOP |
| `edificio2_casa.csv` | Casa (nv1–50) | col[6]=capacidad | ↑ misma curva |
| `edificio3_muralla.csv` | Muralla (nv1–50) | col[6]=HP | ↑ |
| `edificio4_torre_de_vigilancia.csv` | Torre (nv1–50) | col[6]=detección, col[7]=sigilo_ref | ↑ |
| `edificio5_centro_de_viajes.csv` | C.Viajes (nv1–40) | col[6]=alcance_tiles | ↑ |
| `edificio6_escondite.csv` | Escondite (nv1–40) | col[6]=cap_ejercito, col[7]=cap_material | ↑ |
| `edificio7_almacen.csv` | Almacén (nv1–50) | col[6]=cap_material | ↑ |
| `edificio8_santuario_arcano.csv` | Santuario (nv1–50) | col[6]=cap_mana | ↑ |
| `edificio9_universidad.csv` | Universidad (nv1–45) | col[6]=red_colas%, col[7]=red_edificios%, col[8]=tiempo_min | ↑ |
| `edificio10_herreria.csv` | Herrería (nv1–40) | col[6]=bonus_pa, col[7]=bonus_ca, col[8]=bonus_hp, col[9]=tiempo_min | ↑ |
| `edificio11_templo.csv` | Templo (nv1–50) | col[6]=rebaja_invocación% | ↑ |
| `edificio12_cuartel.csv` | Cuartel (nv1–50) | col[6]=red_tiempo% | ↑ |

### Curva de tiempos de edificios (NUEVA — sesión actual)
Tiempos base rediseñados para que un jugador TOP (universidad nv45 = 99% reducción, 4 slots, 12 ciudades) tarde ~18 meses en llegar al máximo **con restricción de materiales**:
- Nv 1–2: 0 min (gratis)
- Nv 3: 5 min · Nv 4: 15 min · Nv 5: 30 min
- Nv 10: ~1–3 días · Nv 20: ~1–2 semanas
- Nv 30: ~1–2 meses · Nv 40: ~5–13 meses · Nv máx: ~18–30 meses

---

## 4. SISTEMAS IMPLEMENTADOS

### 4.1 Save Manager (`backend/data/save_manager.py`)
- Lock por archivo (`_file_locks` dict + `_meta_lock`) — evita race conditions.
- `update_player(jugador, fn)`: load → fn(data) → save atómico bajo lock.
- `safe_resource_float(v)`: convierte `"__INF__"` → `1e300` para aritmética. Usar en lugar de `float(v)`.
- `__INF__` permanece como **string en disco y en memoria** — JSON-safe. `_SafeEncoder` convierte `float("inf")` → `"__INF__"` al guardar.
- Escritura directa sin `.tmp` con reintento ×3 cada 50ms para `PermissionError` de Windows.

### 4.2 Sistema de órdenes (`backend/systems/orders.py`)

#### Tipos de orden
| Tipo | Descripción |
|---|---|
| ATAQUE | A ciudad jugador/inactivo/dios/cueva |
| ESPIONAJE | A ciudad o entidad |
| DESPLAZAMIENTO | Mover tropas entre ciudades propias/aliadas |
| TRANSPORTE | Mover recursos entre ciudades propias |
| FUNDAR | Fundar nueva ciudad (solo con Exploradores) |

#### Mecánicas clave
- **Costo oro:** `10 × distancia_euclidiana × cantidad_unidades_básicas` (invocaciones gratis).
- **Tiempo viaje:** `distancia × (50 / velocidad_mínima)` segundos.
- **Velocidad mínima:** incluye tropas propias Y prestadas con su nivel correcto.
- **`_nivel_tropas_player(player, unidades)`:** soporta formato `{NIVEL_DE_TROPAS: N}` y `{EXPLORADOR: 40, ...}`.
- **Retorno automático:** tropas sobrevivientes regresan a `ciudad_origen` del despachador.
- **Tropas prestadas:** regresan a ciudad origen del dueño tras ATAQUE/ESPIONAJE/TRANSPORTE.
- **Informes:** `_guardar_informe()` se llama en `_resolver_ataque`, `_resolver_ataque_entidad` y `_resolver_espionaje` — siempre al llegar, no al regresar.
- **XP distribuida:** igual entre todos los propietarios del bando atacante.
- **Zona prohibida KarlakÁ:** ±50 tiles centrado en (500,500) — solo para FUNDAR.

#### Restricciones de ataque
- **Aliados:** bloqueado en `api/orders.py` antes de crear la orden.
- **Dioses/Cuevas con tropas prestadas:** bloqueado — combate vs entidades es INDIVIDUAL.
- **Dios ya derrotado:** bloqueado en `crear_orden` (validación temprana) y en `_resolver_ataque` (segunda barrera). Mensaje inmediato en UI.

#### `unidades_sobrevivientes` — formato actual
```python
# Formato nuevo (todos los propietarios):
orden["unidades_sobrevivientes"] = resultado["sobrevivientes_atk"]
# → {JOTICALINDO: {GUERRERO: N}, JIARITO: {EXPLORADOR: N}}
# _ejecutar_retorno detecta el formato automáticamente
```

### 4.3 Combate (`backend/systems/combat.py`)

#### Mecánica general
- **PA invariable** — nunca se agota. Cada grupo golpea en orden DESTREZA DESC.
- **Fórmula bajas:** `floor((PA_atk - CA_def) × cantidad_atk / HP_def)`. Si PA ≤ CA → sin daño.
- **Cascada:** si elimina a todo un grupo, PA completo pasa al siguiente (mismo bloque DST).
- **Máximo 9 rondas.** Empate al fin → mayor XP de kills gana; empate exacto → victoria del atacante.
- **ATK siempre recibe su turno** aunque DEF tenga mayor DST.

#### Muralla
- HP total por nivel (col[6] de `edificio3_muralla.csv`). **Sin CA propia.**
- Pseudo-grupo defensor con `destreza=inf` — siempre al frente.
- Si atacante no la derriba y muere → `"El atacante no consiguió traspasar la muralla y murió"`.

#### Sigilo — fórmula (v9)
```
sigilo_efectivo = sigilo_max_pelotón
  + por cada unidad adicional:
    si sigilo_unidad ≥ sigilo_max × 0.5 → +3.0
    si sigilo_unidad <  sigilo_max × 0.5 → -1.0
tope máximo: 200
```

**Referencia exploradores nv40 (sigilo=98) vs Torre nv50 (det=101):**
| Exploradores | Sigilo efectivo | Resultado |
|---|---|---|
| 1 | 98 | DETECTADO |
| 2 | 101 | DETECTADO (empate = detectado) |
| 3 | 104 | Nv1 |
| 5 | 110 | Nv2 |
| 8 | 119 | Nv3 |
| 15 | 140 | Nv4 |
| 20 | 155 | **Nv5** ✅ |

#### XP en combate vs entidades (dioses/cuevas)
- **Victoria en combate** (HP=0): `xp_atk += ent_xp` durante el combate.
- **Victoria por valor** (9 rondas, ≥80% ald, ≥90% mil): `xp_atk += ent_xp` luego `× 2.0`.
- **Victoria por resistencia** (9 rondas sin cumplir valor): `xp_atk += ent_xp × 1`.
- La XP de la entidad proviene del campo `experiencia` del CSV de dioses/cuevas.

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

#### Reglas
- Máximo **50 miembros** por alianza.
- **VITAMINIZADOS** (ALALAIA + ADMIN): alianza especial, no pueden aliarse con nadie más.
- Un jugador pertenece a **una sola alianza** a la vez.
- Si un jugador sale o es expulsado → sus tropas prestadas regresan automáticamente.
- **No se puede atacar ni espiar a un aliado** — validación en `api/orders.py`.

#### Alianzas actuales
| Alianza | Tipo | Líder | Miembros |
|---|---|---|---|
| AAA_KILLERS | normal | JOTICALINDO | JOTICALINDO, JIARITO, GINAO |
| VITAMINIZADOS | vitaminizado | ADMIN | ADMIN, ALALAIA |

#### Tropas prestadas
- `city["TROPAS_PRESTADAS"] = [{jugador, unidad, cantidad, ciudad_origen}]`
- ATAQUE/ESPIONAJE/TRANSPORTE → regresan a `ciudad_origen` del dueño al terminar.
- DESPLAZAMIENTO → se quedan en destino.
- Combate vs dioses/cuevas → **prohibido con tropas prestadas** (combate individual).

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

#### ⚠ PENDIENTE — Sistema de Alianzas (próxima sesión)
La pantalla `alliance.js` existe pero el flujo completo **no ha sido probado ni pulido**. Pendiente definir y testear:
- Crear alianza desde la UI
- Invitar → solicitar → aceptar flujo completo
- Expulsar miembro (solo el líder puede)
- Atributos de alianza: nombre, líder, miembros, solicitudes pendientes, descripción (¿?)
- ¿Puede haber rango dentro de la alianza además de líder/miembro?
- ¿Hay límite de tropas prestables simultáneamente?
- ¿Qué pasa con las tropas prestadas si la alianza se disuelve?

### 4.6 Informes (`backend/systems/orders.py` + `frontend/js/screens/reports.js`)
- `_guardar_informe()` se llama **al llegar** en ataque, ataque-entidad y espionaje.
- Historial = órdenes propias completadas + informes personales, deduplicados.
- Polling cada **5 segundos** en `reports.js`.
- El informe muestra: ejército enviado (propias + prestadas con 🤝), bajas propias (incluye prestadas), bajas enemigas, sigilo efectivo, XP ganada.

### 4.7 Colas de Producción (`backend/systems/queues.py`)
- **2 slots simultáneos** por cuartel Y por templo (hasta 3 templos = 6 slots de invocación).
- **Tiempo cuartel:** `base_seg × (1 - red_cuartel/100 - red_universidad/100)`, cap 95%.
- **Tiempo templo:** `base_seg × (1 - reb_templo/100 - red_universidad/100)`, cap 95%.
- CSV unidades: tiempos en **SEGUNDOS** (el header dice minutos — miente).
- La pantalla **EJÉRCITO** (`invocations.js`) muestra todas las colas activas con barra de progreso.

### 4.8 Producción de Recursos (`backend/systems/production.py`)
- Recursos: `aldeanos × tasa_material_por_aldeano_por_hora[nivel_CC]` — cap por almacén.
- Maná: `sacerdotes × mana_por_sacerdote_por_hora[nivel_sacerdote]` — cap por santuario.
- **Aldeanos:** producidos por el Centro de Ciudad a tasa `aldeanos/hora[nivel_CC]` — cap por Casa.
- Retroactividad máx: 3 días (`LAST_PROD` timestamp).
- **Aldeanos no se producen en cuartel** — solo en Centro de Ciudad.

### 4.9 Sistema de Niveles de Tropas (`backend/api/leveling.py`)
- Solo tropas básicas del cuartel tienen nivel: ALDEANO, EXPLORADOR, SACERDOTE, GUERRERO, COMANDO, MERCENARIO, MARINE, CYBORG, MAGO, METAHUMANO.
- **Invocaciones NO tienen nivel.** Criaturas de cueva NO tienen nivel.
- El jugador decide **manualmente** a qué tropa asignar XP del pool global `player["experiencia"]`.
- Nivel máximo efectivo: `20 + floor(dioses_abatidos / 20)`, tope absoluto 40.
- **Endpoint:** `GET /api/leveling/{jugador}` · `POST /api/leveling/{jugador}/subir {tipo}`
- **UI:** botón "⬆ Subir nivel de tropas" en panel de Progreso de ciudad. Modal sin parpadeo (actualiza in-place).

#### XP requerida por nivel (de `experiencia_requerida.csv`)
- Nv2: 3.3M · Nv5: 13.6M · Nv10: 450M · Nv15: 700M
- Nv20: 950M · Nv30: 1.87T · Nv40: 1.95T · (acumulada total hasta nv40: ~455T)

### 4.10 Mapa Imperial (`frontend/js/screens/map.js`)
- **Capas toggle** (superior izquierda): 👤 Humanos · 🤝 Alianza · 💊 Vitaminizados · 🏚 Inactivos · 🌩 Dioses · 🦎 Cuevas · 🌀 Portales · ☠ KarlakÁ
- **Colores:** propias=verde, aliadas=azul claro, vitaminizadas=magenta, rivales=dorado, inactivos=azul, dioses=morado, cuevas=naranja, portales=cian, karlakÁ=rojo.
- **Dioses abatidos** filtrados por jugador — no aparecen en el mapa del que los mató.
- Coordenadas en **enteros** (`Math.round`).
- Botón 🏠 navega a la primera ciudad propia.
- Solo muestra órdenes `EN_VIAJE` o `REGRESANDO`.
- **`/api/map/entities?jugador=JOTICALINDO`** — filtra dioses abatidos.

### 4.11 Pantalla Ciudad (`frontend/js/screens/city.js`)
Panel izquierdo:
- **▼ Recursos** — con símbolo ∞ para `__INF__`
- **▼ Producción / Hora**
- **▼ Logística** — niveles edificios clave
- **▼ Construcciones (N)** — obras activas con barra de progreso en tiempo real. Se ocultan automáticamente al completarse.
- **▼ Progreso** — XP, batallas, dioses, cuevas + botón "⬆ Subir nivel de tropas"

Panel derecho:
- **▼ Ejército** — tropas básicas
- **▼ Invocaciones** — invocaciones
- **▼ Criaturas de Cueva** — solo si hay alguna capturada (naranja)
- **⚒ Herrería** — bonus PA/CA/HP global

### 4.12 Pantalla MISIONES (`frontend/js/screens/army.js`)
- Nombre anterior: EJÉRCITO. Ahora: **MISIONES**.
- Tropas propias: básicas + invocaciones + criaturas de cueva (naranja).
- Tropas aliadas prestadas: agrupadas por propietario con 🤝.
- FUNDAR: solo Exploradores. Criaturas de cueva no pueden fundar.

### 4.13 Pantalla EJÉRCITO (`frontend/js/screens/invocations.js`)
- Nombre anterior: INVOCACIONES. Ahora: **EJÉRCITO**.
- Muestra colas activas de cuarteles y templos con barra de progreso.
- Formularios para encolar: Cuartel 1/2, Templo 1/2/3, tropa/invocación, cantidad.
- Polling 5s.

---

## 5. MECÁNICAS DE JUEGO

### 5.1 Combate JvJ (Jugador vs Jugador)
- Puede ser **conjunto**: varios jugadores de la misma alianza atacan juntos.
- XP dividida en partes **iguales** entre todos los propietarios del bando atacante.
- Tropas prestadas participan con sus stats de nivel correcto (del dueño).
- El defensor **no sabe** que lo atacan hasta que la orden llega.

### 5.2 Combate vs Dioses
- **INDIVIDUAL** — sin tropas prestadas. Rechazado al despachar.
- **Un dios solo puede ser vencido una vez por jugador.** Rechazado al despachar si ya está en `dioses_abatidos`.
- El dios queda marcado `_derrotado=True, HP=0` en `backend/db/world/dioses.json` para todos.
- Victorias: en combate (HP=0), por valor (≥80% ald + ≥90% mil, XP×2), por resistencia (9 rondas).
- Sin botín de materiales.

### 5.3 Combate vs Cuevas
- **INDIVIDUAL** — sin tropas prestadas.
- **Victoria:** criatura capturada → pasa al ejército del atacante en su ciudad origen.
  - Claves JSON: `BEHEMOT`, `CHUPACABRAS`, `DRAGON`, `LEVIATAN`, `PATOTAS`, `SIMURGH`.
- **Derrota:** la criatura vuelve al mapa (no "muere").
- **En combate JvJ:** criaturas de cueva regresan al mapa al ser eliminadas, pero generan XP.
- La cueva puede ser atacada de nuevo por el mismo jugador (no hay restricción como con dioses).

### 5.4 Criaturas de Cueva — Captura e Incorporación
1. Jugador ataca cueva en el mapa (coordenadas del CSV).
2. Victoria → `_capturar_criatura()` añade +1 al tipo en `ciudad_origen` del jugador.
3. La criatura queda `_derrotado=True` en `cuevas.json` y desaparece del mapa.
4. La criatura capturada aparece en la pantalla MISIONES y CIUDAD como unidad disponible.
5. Puede participar en cualquier misión (ataque, espionaje, desplazamiento, transporte) **excepto fundar**.
6. No tiene nivel propio. No puede invocarse desde templo.
7. Claves de las 6 clases: `BEHEMOT`, `CHUPACABRAS`, `DRAGON`, `LEVIATAN`, `PATOTAS`, `SIMURGH`.

### 5.5 Progresión de Tropas (Niveles)
- **Pool global** `player["experiencia"]` acumula XP de todos los combates.
- **Asignación manual**: el jugador decide a qué tipo de tropa asignar XP desde el modal de subida.
- **Niveles 1–20**: por XP del pool (tabla `experiencia_requerida.csv`).
- **Niveles 21–40**: cada nivel adicional requiere haber matado 20 dioses más.
  - Fórmula: `nivel_max = min(40, 20 + floor(len(dioses_abatidos) / 20))`
- **Solo tropas básicas** tienen nivel: Aldeano, Explorador, Sacerdote, Guerrero, Comando, Mercenario, Marine, Cyborg, Mago, Metahumano.
- Invocaciones, criaturas de cueva y entidades del mapa NO tienen nivel.

### 5.6 Producción de Aldeanos
- **Fuente:** Centro de Ciudad produce aldeanos a tasa `aldeanos/hora[nivel_CC]`.
- **Cap:** capacidad máxima por nivel de Casa.
- Retroactividad máx: 3 días.
- **Aldeanos NO se producen en cuartel.** El cuartel entrena tropas militares.

### 5.7 Máximo de Ciudades
- Cada jugador tiene un máximo de ciudades (`CIUDADES_MAXIMAS_POR_JUGADOR` en su JSON).
- JOTICALINDO: 12 ciudades (jL01–jL12, todas en radio estrecho (242–245, 520–522)).
- JIARITO: 15 ciudades.
- Para fundar: requiere Exploradores, coordenada libre, fuera de zona KarlakÁ.
- Zona prohibida KarlakÁ: ±50 tiles de (500,500) = rango X:[450,550], Y:[450,550].

### 5.8 Cuentas Vitaminizadas (ALALAIA y ADMIN)
- Sus recursos son `"__INF__"` (sentinel string, no float).
- **Reposición instantánea**: cuando son atacadas, sus tropas se reponen. *(Implementado en `experience.py` como módulo, pendiente integrar al flujo de `orders.py`)*.
- No pueden aliarse con nadie fuera de VITAMINIZADOS.
- ADMIN tiene 14 ciudades (Admin02–Admin15). ALALAIA tiene 14 ciudades (AlalaiA02–AlalaiA15).

### 5.9 Dioses
- 400 dioses ordenados por CA ascendente (CSV `dioses.csv`).
- Cada jugador solo puede vencer **una vez** cada dios.
- Los dioses vencidos desaparecen del mapa del jugador que los venció.
- XP del dios va al campo `experiencia` del CSV.
- Cada 20 dioses vencidos → desbloquea 1 nivel adicional de tropa (hasta nv40).
- `player["dioses_abatidos"]` = lista de IDs (`["Dios-001", "Dios-002", ...]`).
- JOTICALINDO tiene actualmente 27 dioses abatidos (Dios-001 a 025, más 034 y 041).

### 5.10 Portales
- 10 portales en el mapa (`portales.csv`).
- Cada uno tiene condiciones de desbloqueo (`portales_condiciones.csv`):
  - nivel mínimo de tropas, batallas ganadas, cuevas derrotadas, misiones espionaje, etc.
- **Sistema de portales: PENDIENTE DE IMPLEMENTAR.**

### 5.11 KarlakÁ
- HP=5e17, PA=4.5e18, CA=5e18.
- Solo puede ser atacada con Éon Supremo (una unidad).
- Multiplicador ×100.000 en PA si atacada por más de una unidad o por non-ÉON SUPREMO.
- Zona prohibida solo para FUNDAR (±50 tiles), no para ataques.

### 5.12 Herrería
- Bonus global de PA, CA y HP sumado de todas las herrerías de todas las ciudades del jugador.
- `calcular_bonus_herreria(player)` → `{pa_bonus, ca_bonus, hp_bonus}`.
- **NO afecta invocaciones** — solo tropas básicas.

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

### 6.2 Estado actual de JOTICALINDO
- `unit_levels`: MAGO:21, SACERDOTE:21, ALDEANO:21, EXPLORADOR:21, GUERRERO:21, COMANDO:21, METAHUMANO:21, CYBORG:21, MARINE:21, MERCENARIO:21
- `experiencia`: ~4.61×10¹⁷
- `dioses_abatidos`: 27 (Dios-001..025, 034, 041)
- `batallas_ganadas`: 14, `batallas_perdidas`: 1
- `cuevas_derrotadas`: 2
- `misiones_espionaje`: 29
- Criaturas capturadas en jL01: `DRAGON: 2`

### 6.3 Distribución del mundo (1000×1000 tiles)
- 300 ciudades inactivas · 72 ciudades IA · 400 dioses · 999 cuevas · 10 portales · KarlakÁ (500,500)

---

## 7. BUGS RESUELTOS (sesiones anteriores + sesión actual)

| Bug | Causa | Fix |
|---|---|---|
| Tropas desaparecen al regresar | Race condition | `update_player()` atómico con lock |
| PermissionError .tmp Windows | `os.replace()` falla | Escritura directa sin .tmp + reintento ×3 |
| `__INF__` crashea ticker | `float("__INF__")` en varios archivos | `save_manager.safe_resource_float()` + parches en `espionage.py`, `orders.py` |
| FastAPI crashea con `float("inf")` | `_resolve_inf` convertía __INF__ a float | __INF__ permanece como string en memoria |
| Orden espionaje congelada | `unidades={}` → `sobrevivientes={}` → retorno fallaba | Fix `unidades_sobrevivientes` en espionaje exitoso |
| Informe no llega tras combate | `_guardar_informe` no llamado en `_resolver_ataque` ni `_resolver_ataque_entidad` | Añadido en ambas funciones |
| Informe tarda minutos | Se guardaba al regresar, no al llegar | `_guardar_informe` llamado al llegar; historial incluye `player["informes"]` |
| Nivel tropas = 1 en orden | `api/orders.py` leía `NIVEL_DE_TROPAS` que JOTICALINDO no tiene | Usar `_nivel_tropas_player()` |
| Dios atascado (loop infinito ticker) | `_verificar_valor` hacía `float(v)` sobre campo NOMBRE="jL01" | Skip campos no-numéricos |
| Dios ya derrotado atascaba ticker | No había validación temprana | Validación en `crear_orden` + segunda barrera en `_resolver_ataque` |
| Ciudades ADMIN no aparecen en mapa | `JUGADORES_ACTIVOS` no incluía ADMIN | Añadido + categoría `CIUDAD_VITAMINIZADA` |
| Mapa clusters tapabn ciudades | Umbral cluster `< 2` muy alto | Bajado a `< 0.3` |
| Panel derecho ciudad en blanco | `cr` usada antes de definirse en `_updateRight` | Definir `cr` dentro de `_updateRight` |
| Construcciones legacy en JSON | Obras en formato viejo (`KEY/TIEMPO/TOTAL`) | Limpiadas manualmente; panel filtra obras al 100% |
| Sigilo=8 explorador nv40 JIARITO | `NIVEL_DE_TROPAS` no existe en JIARITO | `_nivel_tropas_player()` soporta ambos formatos |
| XP no sube visible | `api/city.py` no exponía `experiencia` | Añadidos campos de jugador en respuesta de ciudad |
| Informes batallamuestra solo tropas propias | `reports.js` ignoraba `unidades_prestadas` | Mostrar prestadas con 🤝 + bajas prestadas |

---

## 8. PENDIENTES

### 8.1 PRÓXIMA SESIÓN — Alianzas (PRIORITARIO)
El flujo de alianzas en la UI está **incompleto y sin probar**. Tareas:

1. **Pantalla `alliance.js`**: revisar estado actual y completar:
   - Ver alianza actual del jugador
   - Crear alianza nueva
   - Solicitar unirse a alianza existente
   - Aceptar/rechazar solicitudes (solo líder)
   - Expulsar miembro (solo líder)
   - Salir de alianza
   - Ver miembros + sus stats básicos
   - Prestar tropas desde la UI (actualmente solo por API directo)
   - Reclamar tropas prestadas

2. **Definir atributos de alianza**:
   - ¿Hay rangos además de líder/miembro? (co-líder, oficial, etc.)
   - ¿Descripción/lema de alianza?
   - ¿Límite de tropas prestables simultáneamente?
   - ¿Qué pasa con tropas prestadas si alianza se disuelve?

3. **Testar flujo completo**: crear → invitar → aceptar → prestar → reclamar → expulsar.

### 8.2 PRÓXIMA SESIÓN — Mensajería Interna
Sistema de mensajes entre jugadores:
- Mensaje directo jugador→jugador
- Mensaje de alianza (broadcast a todos los miembros)
- Notificaciones de eventos (ataque recibido, solicitud de alianza, etc.)
- ¿Dónde se almacena? (JSON por jugador, campo `mensajes[]`)
- ¿Polling o WebSocket?

### 8.3 Funcionales pendientes
- **Reposición vitaminizadas**: módulo `experience.py` tiene la lógica pero no está integrada al flujo de `orders.py` post-combate.
- **Regeneración de muralla**: materiales + tiempo (pendiente definir).
- **Sistema de portales**: condiciones de desbloqueo (`portales_condiciones.csv`).
- **NG+** (New Game Plus): ciclo de reinicio con KarlakÁ.
- **Ataques recibidos en informes**: el defensor no ve registro del ataque en sus informes.
- **WebSocket**: actualmente polling cada 5s en informes y producción.
- **Imágenes**: `alalaia_small.png` / `karlaka_small.png` (404 actual).
- **Pantalla Ajustes** (`settings.js`): vacía.
- **Centrado del mapa** en ciudad propia al navegar.
- **`valor_cumplido: false`** con mensaje "Victoria por valor" — contradicción en el informe de combate vs dioses. Investigar bug en `_verificar_valor`.

### 8.4 Técnicos
- Float precision para aldeano >1e15.
- Parseo notación europea en CSVs de invocaciones (`6,3E+021` → `safe_float`).
- `LAST_PROD` de ciudades JL2–JL12 muy antiguo — producción retroactiva exagerada al cargar.
- Campos legacy en ciudades: `JUGADOR`, `NIVEL_DE_TROPAS`, `TIPO_JUGADOR`, `NIVEL_DE_TROPA` (distintos a los actuales). No rompen nada pero son ruido.

---

## 9. NOTAS DE DISEÑO IMPORTANTES

- **JIARITO no es IA autónoma** — cuenta especial controlada por Jorge.
- **`unit_levels` de JIARITO:** `{EXPLORADOR: 40, GUERRERO: 40, ...}` (nivel por tipo).
- **`unit_levels` de JOTICALINDO:** `{MAGO: 21, SACERDOTE: 21, ...}` (nivel por tipo, ya migrado).
- **Siempre `_nivel_tropas_player()`** para leer nivel de cualquier jugador.
- **La herrería NO afecta invocaciones** — solo tropas básicas.
- **Las invocaciones NO tienen nivel** — son las que son.
- **Las criaturas de cueva NO tienen nivel** — capturadas tal cual.
- **Aldeanos: producidos por CC, no por cuartel.**
- **Zona prohibida KarlakÁ: solo para FUNDAR**, no para ataques.
- **Dioses: un jugador, un dios, una vez.**
- **Combate vs dioses/cuevas: SIEMPRE individual** (sin tropas prestadas).
- **`__INF__`** es string en JSON y en memoria Python. Usar `safe_resource_float()` para aritmética.
- **Tiempos de edificios nuevos**: curva exponencial rediseñada — los CSVs en `csv/` fueron reemplazados en esta sesión.
