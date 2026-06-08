# ETERNAL WARRIORS v3.0 — DOCUMENTO MAESTRO v9.0
**Fecha:** Junio 2026 · **Stack:** Python FastAPI + HTML5 Canvas · **Plataforma:** Windows 10

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
- Siempre: `grep` líneas → `view` rango → `str_replace` exacto. Nunca reescribir archivos completos salvo necesidad estricta.
- Validación de sintaxis obligatoria (`ast.parse`) después de cada cambio Python.
- Para archivos grandes: scripts Python/Node ejecutados en bash.
- **Audit antes de fix:** leer el archivo exacto del disco antes de parchear.
- **Un fix por problema.** Sin bundling de cambios no relacionados.

### 1.3 Protocolo de arranque de nueva sesión
1. Subir `EW_Maestro_v9.md` al nuevo chat.
2. Subir archivos modificados en la sesión anterior si hay cambios pendientes.
3. Claude lee el documento, confirma estado y pregunta qué se trabaja.

### 1.4 Archivos clave a subir según contexto

| Archivo | Ruta | Cuándo subir |
|---|---|---|
| `orders.py` | `backend/systems/` | Bugs de órdenes/combate/espionaje |
| `combat.py` | `backend/systems/` | Bugs de combate/sigilo/muralla |
| `espionage.py` | `backend/systems/` | Bugs de espionaje |
| `alliances.py` | `backend/systems/` | Bugs de alianzas/préstamo |
| `queues.py` | `backend/systems/` | Bugs de colas de producción |
| `save_manager.py` | `backend/data/` | PermissionError o race conditions |
| `orders.py` | `backend/api/` | Bugs endpoint órdenes |
| `alliances.py` | `backend/api/` | Bugs endpoint alianzas |
| `city.py` | `backend/api/` | Bugs producción/tick |
| `army.js` | `frontend/js/screens/` | Bugs formulario órdenes |
| `map.js` | `frontend/js/screens/` | Bugs mapa |
| `reports.js` | `frontend/js/screens/` | Bugs informes |
| `alliance.js` | `frontend/js/screens/` | Bugs pantalla alianzas |
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
├── backend/
│   ├── main.py                    — FastAPI app + ticker órdenes (5s)
│   ├── api/
│   │   ├── city.py               — producción/tick
│   │   ├── orders.py             — endpoints órdenes (historial combinado)
│   │   ├── map.py                — entidades y órdenes activas
│   │   ├── queues.py             — colas cuartel/templo
│   │   ├── alliances.py          — endpoints alianzas y préstamo de tropas
│   │   ├── buildings.py
│   │   ├── escondite.py
│   │   └── auth.py
│   ├── systems/
│   │   ├── orders.py             — resolver órdenes (ataque, espionaje, etc.)
│   │   ├── combat.py             — combate, sigilo, muralla
│   │   ├── espionage.py          — espionaje ciudad y entidades
│   │   ├── alliances.py          — alianzas, préstamo, retorno de tropas
│   │   ├── queues.py             — colas de producción e invocación
│   │   ├── production.py
│   │   ├── herreria.py
│   │   └── buildings.py
│   ├── data/
│   │   └── save_manager.py       — I/O JSON con lock por archivo
│   └── db/
│       ├── players/
│       │   ├── joticalindo.json
│       │   ├── jiarito.json
│       │   ├── ginao.json
│       │   ├── alalaia.json
│       │   └── admin.json
│       ├── world/                — inactivos, dioses, cuevas...
│       └── global/
│           ├── orders.json
│           ├── alliances.json    — AAA_KILLERS + VITAMINIZADOS
│           └── accounts.json
├── frontend/
│   ├── game.html                 — nav con: CIUDAD, EJÉRCITO, INVOCACIONES,
│   │                               MAPA IMPERIAL, INFORMES, ALIANZA, AJUSTES
│   ├── js/
│   │   ├── app.js               — orquestador + listener ew:irAEjercito
│   │   └── screens/
│   │       ├── city.js
│   │       ├── army.js          — selección tropas propias + prestadas
│   │       ├── map.js           — solo muestra EN_VIAJE y REGRESANDO
│   │       ├── reports.js       — informes batalla + espionaje con scroll
│   │       ├── alliance.js      — pantalla de alianzas y préstamo
│   │       ├── invocations.js
│   │       └── settings.js
│   └── css/
└── csv/                          — CSVs canónicos (NO MODIFICAR)
```

### 2.3 Comandos esenciales
```cmd
cd E:\0000ew V2Claude
python -m uvicorn backend.main:app --reload --port 8000
for /d /r "E:\0000ew V2Claude" %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
git add -A && git commit -m "mensaje" && git push
```

---

## 3. CSV CANÓNICOS

| CSV | Descripción | Columnas clave |
|---|---|---|
| `caracteristicas_unidades.csv` | Stats unidades básicas por nivel | col[6]=destreza, col[7]=velocidad, col[8]=sigilo |
| `caracteristicas_invocaciones.csv` | Stats invocaciones | col[5]=sigilo, col[6]=velocidad, col[7]=nv_min_sacerdote, col[8]=tiempo_SEG, col[9]=costo_mana |
| `tiempo_base_produccion_unidades_basicas.csv` | Tiempo entrenamiento | **SEGUNDOS** (header dice minutos — miente) |
| `edificio3_muralla.csv` | Muralla | col[6]=HP (sin CA propia) |
| `edificio4_torre_de_vigilancia.csv` | Torre | col[6]=deteccion, col[7]=sigilo_explorador_ref |
| `edificio9_universidad.csv` | Universidad | col[6]=red_colas%, col[7]=red_edificios% |
| `edificio11_templo.csv` | Templo | col[6]=rebaja_invocacion% |
| `edificio12_cuartel.csv` | Cuartel | col[6]=red_tiempo% |
| `dioses.csv` | 400 dioses | HP/PA/CA/DST/XP |
| `cuevas.csv` | 999 cuevas | 6 tipos |
| `portales.csv` / `portales_condiciones.csv` | 10 portales | Condiciones de desbloqueo |
| `karlaka.csv` | KarlakÁ en (500,500) | Entidad final |

---

## 4. SISTEMAS IMPLEMENTADOS

### 4.1 Save Manager (`backend/data/save_manager.py`)
- Lock por archivo (`_file_locks` dict + `_meta_lock`) — evita race conditions.
- `update_player(jugador, fn)`: load → fn(data) → save, todo bajo lock. Operación atómica.
- Escritura directa sin `.tmp` con reintento ×3 cada 50ms para `PermissionError` de Windows.
- `load_alliances()` / `save_alliances()`: lee/escribe `backend/db/global/alliances.json`.

### 4.2 Sistema de órdenes (`backend/systems/orders.py`)

#### Tipos de orden
| Tipo | Descripción | Resolución |
|---|---|---|
| ATAQUE | A ciudad jugador/inactivo/dios/cueva | `_resolver_ataque` → busca en todos los mundos |
| ESPIONAJE | A ciudad/entidad | `_resolver_espionaje` → sigilo_grupo por propietario |
| DESPLAZAMIENTO | Mover tropas ciudad propia→propia | `_resolver_desplazamiento` |
| TRANSPORTE | Mover recursos ciudad propia→propia | `_resolver_transporte` |
| FUNDAR | Fundar nueva ciudad | `_resolver_fundar` |

#### Mecánicas clave
- **Costo oro:** `10 × distancia_euclidiana × cantidad_unidades_básicas` (invocaciones gratis).
- **Tiempo viaje:** `distancia × (50 / velocidad_mínima)` segundos.
- **Velocidad mínima:** incluye tropas propias Y prestadas con su nivel correcto.
- **`_nivel_tropas_player(player, unidades)`:** lee nivel correcto soportando ambos formatos:
  - `{NIVEL_DE_TROPAS: 20}` (formato joticalindo)
  - `{EXPLORADOR: 40, GUERRERO: 40, ...}` (formato jiarito)
- **Retorno automático:** tropas sobrevivientes regresan a `ciudad_origen`.
- **Tropas prestadas:** regresan a ciudad de origen del dueño (Bogotá de JIARITO).
- **Informes:** `_guardar_informe()` guarda copia en `player["informes"]` de cada propietario participante.
- **XP:** dividida en partes iguales entre todos los propietarios que participaron.
- **Zona prohibida KarlakÁ:** radio cuadrado ±50 tiles centrado en (500,500).

### 4.3 Combate (`backend/systems/combat.py`)

#### Mecánica general
- **PA invariable** — nunca se agota. Cada grupo golpea en orden DESTREZA DESC.
- **Fórmula bajas:** `floor((PA_atk - CA_def) × cantidad_atk / HP_def)`. Si PA ≤ CA → sin daño.
- **Cascada:** si elimina a todo un grupo, PA completo pasa al siguiente (mismo bloque DST).
- **Máximo 9 rondas** para todos los combates.
- **Empate al fin de 9 rondas:** mayor XP de kills gana. Empate exacto → victoria del atacante.
- **Fix loop de rondas:** cuando DEF tiene mayor DST y actúa primero, ATK siempre recibe su turno en la misma ronda.

#### Muralla
- HP total por nivel (col[6] de `edificio3_muralla.csv`). **Sin CA propia.**
- Se inserta como pseudo-grupo defensor con `destreza=inf` (siempre al frente).
- El atacante la golpea primero; si la derriba, el sobrante de daño continúa en cascada a tropas.
- El defensor contraataca en paralelo según su DST, sin esperar a que caiga la muralla.
- Si el atacante no derriba la muralla y muere → `"El atacante no consiguió traspasar la muralla y murió"`.
- **Regeneración:** PENDIENTE (requiere materiales + tiempo por definir).

#### Sigilo — fórmula nueva (v9)
```
sigilo_efectivo = sigilo_max_grupo + Σ por cada unidad adicional:
    si sigilo_unidad ≥ sigilo_max × 0.5 → +3.0
    si sigilo_unidad <  sigilo_max × 0.5 → -1.0
tope máximo: 200
```

**Referencia exploradores nv40 (sigilo=98) vs Torre nv50 (det=101):**
| Exploradores | Sigilo efectivo | Resultado |
|---|---|---|
| 1 | 98 | DETECTADO |
| 2 | 101 | DETECTADO (empate = detectado) |
| 3 | 104 | Pasa — Intel Nv1 |
| 5 | 110 | Intel Nv2 |
| 8 | 119 | Intel Nv3 |
| 15 | 140 | Intel Nv4 |
| **20** | **155** | **Intel Nv5** ✅ |

**Otros niveles vs Torre nv50:**
| Nivel exp | Sigilo | Pasa torre con | Intel Nv5 con |
|---|---|---|---|
| 20 | 28 | 26 exploradores | 44 |
| 30 | 38 | 23 exploradores | 40 |
| 39 | 47 | 20 exploradores | 37 |
| 40 | 98 | 3 exploradores | 20 |

### 4.4 Espionaje (`backend/systems/espionage.py`)

#### Detección
```
detectado = sigilo_efectivo <= 0  OR  deteccion_torre >= sigilo_efectivo
```
- `calcular_sigilo_grupo(grupos)` — soporta múltiples propietarios con niveles distintos.
- Si detectado → combate automático (mismas reglas de combate normal).

#### Niveles de inteligencia
| Diferencia (sigilo_ef − det_torre) | Nivel | Información obtenida |
|---|---|---|
| ≤ 0 | COMBATE | Combate automático |
| 1–5 | Nv1 | Coordenadas + nombre propietario |
| 6–15 | Nv2 | + Materiales |
| 16–30 | Nv3 | + Tipos unidades/invocaciones/cuevas |
| 31–53 | Nv4 | + Niveles y cantidades (sin propietarios) |
| ≥ 54 | Nv5 | Todo: ejércitos con propietarios, escondite, edificios |

#### Espionaje encubierto de ataques
- Sigilo del grupo calculado con `calcular_sigilo_grupo` antes de la orden.
- Si sigilo_efectivo = 0 → siempre detectado aunque no haya torre.
- Defensor solo ve el ataque cuando ya llegó.

### 4.5 Sistema de Alianzas (`backend/systems/alliances.py`)

#### Reglas
- Máximo **50 miembros** por alianza.
- **VITAMINIZADOS** (ALALAIA + ADMIN): alianza especial, no pueden aliarse con nadie más.
- **Todos los demás** (JOTICALINDO, JIARITO, GINAO, humanos): pueden aliarse entre sí.
- Un jugador pertenece a **una sola alianza** a la vez.
- Si un jugador sale o es expulsado → sus tropas prestadas regresan automáticamente.

#### Alianzas actuales
| Alianza | Tipo | Líder | Miembros |
|---|---|---|---|
| AAA_KILLERS | normal | JOTICALINDO | JOTICALINDO, JIARITO, GINAO |
| VITAMINIZADOS | vitaminizado | ADMIN | ADMIN, ALALAIA |

#### Tropas prestadas
- Estructura en ciudad huésped: `city["TROPAS_PRESTADAS"] = [{jugador, unidad, cantidad, ciudad_origen}]`
- **ATAQUE/ESPIONAJE/TRANSPORTE:** tropas sobrevivientes regresan a `ciudad_origen` del dueño al terminar.
- **DESPLAZAMIENTO:** tropas se quedan en ciudad destino (siguen prestadas).
- **Reclamar:** botón en UI → tropas regresan inmediatamente a ciudad de origen.
- Velocidad del pelotón: usa el nivel correcto del dueño de las tropas prestadas.
- Sigilo del pelotón: usa `calcular_sigilo_grupo` con nivel correcto por propietario.

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
GET    /api/alliances/{jugador}/tropas_prestadas — tropas aliadas en ciudades
```

### 4.6 Informes (`backend/systems/orders.py` + `frontend/js/screens/reports.js`)
- `_guardar_informe(orden, sm, jugadores_extra)`: copia el informe en `player["informes"]` de cada participante.
- El historial (`/api/orders/historial/{jugador}`) combina órdenes propias completadas + informes personales, deduplicados por ID.
- Máximo 200 informes por jugador (FIFO).
- **Cada jugador ve solo informes de órdenes donde participó** (como despachador o como dueño de tropas prestadas).

### 4.7 Colas (`backend/systems/queues.py`)
- **2 colas simultáneas** por cuartel Y por templo.
- **Tiempo cuartel:** `base_seg × (1 - red_cuartel/100 - red_universidad/100)`, cap 95%.
- **Tiempo templo:** `base_seg × (1 - reb_templo/100 - red_universidad/100)`, cap 95%.
- CSV unidades y CSV invocaciones: tiempos en **SEGUNDOS**.
- Universidad: `col[6]` = reducción colas, `col[7]` = reducción edificios.

### 4.8 Mapa (`frontend/js/screens/map.js`)
- Solo muestra órdenes en estado `EN_VIAJE` o `REGRESANDO` (filtra COMPLETADAS).
- Botones ATACAR/ESPIAR desde panel lateral → navega a EJÉRCITO via evento `ew:irAEjercito`.

### 4.9 Pantalla Ejército (`frontend/js/screens/army.js`)
- **Sección 1:** Tropas propias del jugador activo.
- **Sección 2:** Tropas aliadas prestadas, agrupadas por propietario (🤝 JIARITO).
- `_seleccion = {jugador: {unidad: cantidad}}` — estructura por propietario.
- El body de la orden incluye `unidades` (propias) y `unidades_prestadas` (por dueño).

---

## 5. MECÁNICAS DE JUEGO

### 5.1 Combate vs Dioses y Cuevas

#### Tipos de victoria
| Tipo | Condición | Recompensa |
|---|---|---|
| **En combate** | HP entidad = 0 | XP + dios eliminado / criatura capturada |
| **Por valor** | Sobrevivir 9 rondas + ≥80% aldeanos + ≥90% militares/invoc | XP ×2 |
| **Por resistencia** | Sobrevivir 9 rondas sin cumplir valor | XP normal |

- **Criaturas de cuevas derrotadas:** se capturan y pasan al ejército del atacante.
- **Criaturas derrotadas por el defensor:** vuelven al mapa.
- **Sin botín de materiales** en ningún caso.

### 5.2 Progresión de tropas
- **Niveles 1–20:** por acumulación de XP de combate.
- **Niveles 21–40:** cada nivel requiere matar **20 dioses** adicionales (400 total para nv40).
- Los 400 dioses numerados por CA ascendente (#1 = menor CA, #400 = mayor CA).
- Cada 20 dioses vencidos (cualquier tipo) → desbloquea 1 nivel adicional.

### 5.3 KarlakÁ
- HP=5e17, PA=4.5e18, CA=5e18.
- Multiplicador ×100.000 en PA si es atacada por más de una unidad o por non-ÉON SUPREMO.
- Zona prohibida: radio cuadrado ±50 tiles centrado en (500,500).

### 5.4 Regeneración de muralla
- **PENDIENTE** — requiere materiales y tiempo ("altos") por definir.

---

## 6. JUGADORES Y MUNDO

### 6.1 Jugadores
| Jugador | Tipo | Ciudades | Capital | Notas |
|---|---|---|---|---|
| JOTICALINDO | Humano | 12 (jL01–jL12) | jL01 (242,522) | Jugador principal |
| JIARITO | Especial/aliado | 15 | Bogotá (666,666) | `unit_levels = {EXPLORADOR:40,...}` |
| GINAO | Especial/aliado | Variable | — | Aliado de JOTICALINDO |
| ALALAIA | Vitaminizada | 1 | — | Entidad especial |
| ADMIN | Vitaminizado | — | — | Alianza VITAMINIZADOS |

### 6.2 Distribución del mundo (1000×1000 tiles)
- 300 ciudades inactivas · 72 ciudades IA · 400 dioses · 999 cuevas · 10 portales · KarlakÁ (500,500).

---

## 7. BUGS RESUELTOS (historial acumulado)

| Bug | Causa | Fix |
|---|---|---|
| Tropas desaparecen al regresar | Race condition city.py | `update_player()` atómico con lock |
| PermissionError .tmp en Windows | `os.replace()` falla | Escritura directa sin .tmp + reintento ×3 |
| Tiempos entrenamiento/invocación 60× rápidos | CSV en segundos pero código ×60 | Eliminado ×60 en `queues.py` |
| ATK nunca golpea si DEF tiene mayor DST | Bug loop `_resolver_ronda` | ATK siempre recibe su turno en la misma ronda |
| Muralla destruía al atacante instantáneamente | Comparación PA total vs HP | Muralla como pseudo-grupo con DST=inf |
| Sigilo=8 con explorador nv40 de JIARITO | `NIVEL_DE_TROPAS` no existe en JIARITO | `_nivel_tropas_player()` soporta ambos formatos |
| Velocidad explorador nv40 = velocidad nv1 | `velocidad_minima()` ignoraba prestadas | `grupos_extra` en `velocidad_minima()` |
| Tropas prestadas regresan a jL01 | `sobrev_prestados={}` → no devolvía nada | Si no hay bajas registradas → devolver cantidad original |
| Estelas fantasma en mapa | Órdenes COMPLETADAS dibujadas | Filtro `EN_VIAJE OR REGRESANDO` en `map.js` |
| Informes no llegan a JIARITO | Solo guardaba en jugador despachador | `_guardar_informe()` copia a todos los propietarios |
| Historial retornaba 404 | Ruta `/historial/{jugador}` después de `/{jugador}` | Mover `get_historial` antes de `get_ordenes` |
| Sin scroll en informes | `height:100%` sin dimensión padre definida | `height:calc(100vh - 120px)` |
| Sigilo intel nivel máximo inalcanzable | Umbrales altos + fórmula lineal | Nueva fórmula f=3.0 + umbrales recalibrados |

---

## 8. PENDIENTES

### 8.1 Críticos — Próxima sesión
- **Línea de retorno fantasma en mapa:** JOTICALINDO ve retorno de tropas de JIARITO — solo debe ver retorno de tropas propias.
- **Pantalla de Alianzas UI:** funcional pero sin prueba completa del flujo crear→invitar→aceptar→prestar.
- **experience.py:** sistema de XP niveles 1–20 y progresión 21–40 por dioses.
- **invocations.js:** pantalla de invocaciones (colas, stats, producción en templos).

### 8.2 Funcionales
- Regeneración de muralla (materiales + tiempo, por definir).
- Sistema de portales — condiciones de desbloqueo (`portales_condiciones.csv`).
- NG+ (New Game Plus) — ciclo de reinicio con KarlakÁ.
- Ataques recibidos en informes (defensa).
- WebSocket tiempo real (actualmente polling cada 2–15s).
- Imágenes `alalaia_small.png` / `karlaka_small.png` (404 actual).
- Pantalla de ajustes (`settings.js`).
- Órdenes directas desde panel lateral del Mapa Imperial.
- Centrado del mapa en ciudad propia al navegar.

### 8.3 Técnicos
- Float precision para aldeano >1e15.
- Parseo notación europea en CSVs de invocaciones (`6,3E+021` → `safe_float`).
- Portal loading: skip archivos con `condiciones` en el nombre.
- Mapear todos los jugadores activos en `PLAYER_PATHS` de `save_manager.py`.
- Herrería global: bonus PA/CA/HP sumado de todas las ciudades — verificar estado en v3.0.

---

## 9. NOTAS DE DISEÑO IMPORTANTES

- **JIARITO no es IA autónoma** — es cuenta especial aliada controlada por Jorge.
- **`unit_levels` de JIARITO:** formato `{EXPLORADOR: 40, GUERRERO: 40, ...}` (sin `NIVEL_DE_TROPAS`).
- **`unit_levels` de JOTICALINDO:** formato `{NIVEL_DE_TROPAS: N}` (nivel global).
- **Siempre usar `_nivel_tropas_player(player, unidades)`** para leer nivel de tropas de cualquier jugador.
- **Tropas prestadas en espionaje:** el sigilo se calcula con `calcular_sigilo_grupo()` que respeta el nivel de cada propietario.
- **Los informes en mapa** muestran la línea de retorno hacia `ciudad_origen` (jL01) — esto es correcto aunque las tropas físicamente regresen a Bogotá. Es el trayecto de la orden, no el de las tropas prestadas.
