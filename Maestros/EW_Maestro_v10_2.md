# ETERNAL WARRIORS v3.0 — DOCUMENTO MAESTRO v10.2
**Fecha:** Junio 2026 · **Stack:** Python FastAPI + HTML5 Canvas · **Plataforma:** Windows 10
**Repo:** `https://github.com/AlalaiA/eternal-warriors-v3.git`

---

## ⚠ LECCIONES CRÍTICAS DE CAMBIOS DE CHAT

1. **Nunca asumir que un fix está instalado en disco.** Siempre verificar con `grep` antes de parchear.
2. **Pedir el archivo actual antes de cada fix.** El archivo en `/mnt/user-data/uploads/` puede diferir del contexto.
3. **`__INF__` es un string sentinel**, no float. Usar `safe_resource_float(v)` en lugar de `float(v)`.
4. **El orders_ticker silencia excepciones.** Con `traceback.print_exc()` en el `except` de `main.py` se ven los errores reales.
5. **Los CSV de edificios tienen header partido en 2 líneas** — `csv.reader` los lee como una sola entrada con `\n` embebido.
6. **`unit_levels` tiene dos formatos:** `{NIVEL_DE_TROPAS: N}` (legacy) y `{EXPLORADOR: 40, ...}` (por tipo). Siempre usar `_nivel_tropas_player()`.
7. **`parseInt("1e+20")` devuelve 1** — usar `Math.floor(Number(val))` para cantidades grandes en JS.
8. **Nunca reescribir un archivo completo** sin antes leer el archivo exacto en disco.
9. **`safe_resource_float` debe importarse en TODOS los sistemas** que lean recursos de ciudad: `production.py`, `buildings.py`, `queues.py`, `espionage.py`, `orders.py`, `combat.py`.
10. **Claves de invocaciones con guión bajo** (`DRAGON_DE_ORO`) vs con espacio (`DRAGON DE ORO`) — normalizar siempre con `key.replace("_", " ")` al buscar en city dict.
11. **`_unidades_ciudad()`** debe probar ambas formas de clave (con `_` y con espacio).
12. **Tropas prestadas con clave compuesta** `"UNIDAD|ciudad_origen"` en el frontend para distinguir múltiples entradas del mismo jugador+unidad.
13. **`retornar_tropas_prestadas_post_orden`** debe devolver proporcionalmente a cada ciudad_origen, no todo a la primera.
14. **Nunca limpiar/borrar datos del jugador sin su consentimiento explícito.**

---

## 1. PRERROGATIVAS DE TRABAJO

### 1.1 Protocolo de comunicación
- Claude frena y espera respuesta si necesita un insumo. **Nunca pregunta y sigue produciendo.**
- Respuestas concisas. Sin verbosidad innecesaria.
- Correcciones directas: Jorge corrige supuestos erróneos y Claude los incorpora sin debate.
- **Nunca inventar mecánicas de juego ni valores de CSV.** Si falta info, parar y preguntar.
- **Los CSV son canónicos y no se modifican** salvo instrucción explícita de Jorge.
- **Nunca limpiar/borrar datos del jugador sin su consentimiento explícito.**

### 1.2 Protocolo de código
- Siempre: `grep` líneas → `view` rango → `str_replace` exacto. Nunca reescribir archivos completos.
- Validación de sintaxis obligatoria (`ast.parse`) después de cada cambio Python.
- **Audit antes de fix:** leer el archivo exacto del disco antes de parchear.
- **Un fix por problema.** Sin bundling de cambios no relacionados.

### 1.3 Protocolo de arranque de nueva sesión
1. Subir `EW_Maestro_v10_2.md` al nuevo chat.
2. Subir archivos modificados en la sesión anterior.
3. Claude lee el documento, confirma estado y pregunta qué se trabaja.

### 1.4 Archivos clave a subir según contexto

| Archivo | Ruta | Cuándo subir |
|---|---|---|
| `orders.py` | `backend/systems/` | Bugs órdenes/combate/espionaje/detección/NG+ |
| `combat.py` | `backend/systems/` | Bugs combate/sigilo/muralla/criaturas |
| `espionage.py` | `backend/systems/` | Bugs espionaje/inteligencia |
| `alliances.py` | `backend/systems/` | Bugs alianzas/préstamo/retorno |
| `queues.py` | `backend/systems/` | Bugs colas de producción |
| `buildings.py` | `backend/systems/` | Bugs construcción |
| `production.py` | `backend/systems/` | Bugs producción recursos |
| `detection.py` | `backend/systems/` | Bugs detección Torre |
| `ngplus.py` | `backend/systems/` | Bugs NG+ |
| `karlaka_event.py` | `backend/systems/` | Bugs evento KarlakÁ |
| `save_manager.py` | `backend/data/` | PermissionError o race conditions |
| `city.py` | `backend/api/` | Bugs producción/tick/obras |
| `orders.py` | `backend/api/` | Bugs endpoint órdenes |
| `alliances.py` | `backend/api/` | Bugs endpoint alianzas |
| `alerts.py` | `backend/api/` | Bugs alertas detección |
| `messages.py` | `backend/api/` | Bugs mensajería |
| `map.py` | `backend/api/` | Bugs mapa |
| `leveling.py` | `backend/api/` | Bugs subida de nivel |
| `army.js` | `frontend/js/screens/` | Bugs MISIONES |
| `map.js` | `frontend/js/screens/` | Bugs mapa |
| `reports.js` | `frontend/js/screens/` | Bugs informes |
| `alliance.js` | `frontend/js/screens/` | Bugs alianzas |
| `city.js` | `frontend/js/screens/` | Bugs ciudad |
| `invocations.js` | `frontend/js/screens/` | Bugs EJÉRCITO |
| `messages.js` | `frontend/js/screens/` | Bugs mensajería |
| `app.js` | `frontend/js/` | Bugs navegación/alertas overlay |
| `game.html` | `frontend/` | Bugs navegación tabs |

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
├── run.bat
├── backend/
│   ├── main.py
│   ├── api/
│   │   ├── city.py               — producción/tick + procesar_obras
│   │   ├── orders.py             — órdenes + historial
│   │   ├── map.py                — entidades + filtro dioses
│   │   ├── queues.py             — colas cuartel/templo
│   │   ├── alliances.py          — alianzas multi-líder
│   │   ├── alerts.py             — alertas Torre de Vigilancia
│   │   ├── messages.py           — mensajería interna
│   │   ├── leveling.py           — subida de nivel tropas
│   │   ├── buildings.py
│   │   ├── escondite.py
│   │   └── auth.py
│   ├── systems/
│   │   ├── orders.py             — resolver órdenes + detección + límite ataques
│   │   ├── combat.py             — combate + sigilo + muralla + criaturas
│   │   ├── espionage.py          — espionaje nv1-5
│   │   ├── detection.py          — detección Torre de Vigilancia
│   │   ├── alliances.py          — alianzas + retorno proporcional
│   │   ├── queues.py             — colas + cancelación por sacerdotes
│   │   ├── production.py         — producción + __INF__ en nv50
│   │   ├── buildings.py          — construcción + safe_resource_float
│   │   ├── ngplus.py             — NG+ (PENDIENTE)
│   │   ├── karlaka_event.py      — evento KarlakÁ cada 3 días (PENDIENTE)
│   │   └── herreria.py
│   ├── data/
│   │   └── save_manager.py
│   └── db/
│       ├── players/
│       ├── world/
│       └── global/               — orders.json, alliances.json, accounts.json,
│                                    messages.json, karlaka_event.json (PENDIENTE)
├── frontend/
│   ├── game.html                 — CIUDAD·MISIONES·EJÉRCITO·MAPA·INFORMES·ALIANZA·MENSAJES·AJUSTES
│   └── js/
│       ├── app.js                — orquestador + poller alertas (5s) + overlay
│       └── screens/
│           ├── city.js
│           ├── army.js           — clave compuesta prestadas + criaturas cueva
│           ├── map.js            — alianza dinámica por jugador
│           ├── reports.js        — polling 2s + perspectiva atacante/defensor
│           ├── alliance.js       — multi-líder: promover/degradar
│           ├── invocations.js    — colas + pausa ticker
│           ├── messages.js       — mensajería + badge
│           └── settings.js       — VACÍO
└── csv/
    └── caracteristicas_invocaciones.csv  — col[10]=cantidad_min sacerdotes
```

---

## 3. CSV CANÓNICOS

| CSV | Columnas clave | Notas |
|---|---|---|
| `caracteristicas_unidades.csv` | col[6]=destreza, col[7]=velocidad, col[8]=sigilo | |
| `caracteristicas_invocaciones.csv` | col[7]=nv_min_sacerdote, col[8]=tiempo_SEG, col[9]=costo_mana, col[10]=cantidad_min | Tiempos en SEGUNDOS |
| `tiempo_base_produccion_unidades_basicas.csv` | col[1]=segundos | Header dice minutos — MIENTE |
| `edificio4_torre_de_vigilancia.csv` | col[6]=deteccion, col[9]=radiocasillasvigilancia | Radio nv50=2000 tiles |
| `edificio7_almacen.csv` | col[6]=capacidad | nv50='infinito' → __INF__ |
| `edificio8_santuario_arcano.csv` | col[6]=capacidad | nv50='infinito' → __INF__ |
| `edificio3_muralla.csv` | col[6]=hp | HP finito. Destreza=∞, PA=0. No regenera. |
| `dioses.csv` | col[9]=experiencia | 400 dioses, CA asc |
| `cuevas.csv` | hp,pa,ca,destreza,experiencia | 999 cuevas liberadas |

---

## 4. SISTEMAS IMPLEMENTADOS

### 4.1 Save Manager
- `safe_resource_float(v)`: `"__INF__"` → `1e300`. **OBLIGATORIO** en toda aritmética sobre recursos.
- `_SafeEncoder`: `float("inf")` → `"__INF__"` al guardar. `1e300` se guarda como número.
- Lock por archivo, escritura directa, reintento ×3 cada 50ms.

### 4.2 Producción de Recursos
- Almacén nv50 / Santuario nv50: capacidad `'infinito'` en CSV → recursos se setean a `"__INF__"` directamente.
- Cualquier jugador que alcance nv50 en estos edificios tendrá recursos/maná infinitos.

### 4.3 Colas de Producción
- `cantidad_min` sacerdotes (col[10] CSV) — mínimo para mantener activa cola de templo.
- Si sacerdotes caen por debajo: cola cancelada automáticamente, maná devuelto.
- Valores: Demonio=5K · Ánima=7.5K · Espectro=12K · Gólem=18K · Centauro=20K · Kraken=25K · Alonardo=35K · Madreselva=45K · Coloso=125K · Fénix=250K · Dragón de Oro=350K · Caballero de Luz=1M · AlalaiA=2M · Éon Supremo=150M.

### 4.4 Construcción de Edificios
- `city.py` llama `procesar_obras(c)` en cada tick.
- `buildings.py` usa `safe_resource_float` para comparar y descontar recursos.

### 4.5 Muralla
- **Destreza = ∞** (siempre al frente, absorbe el primer ataque).
- **PA = 0** (no contraataca nunca).
- **HP finito** según nivel del CSV.
- **No se regenera** — lo destruido queda destruido.
- El mecanismo defensivo es el **límite de ataques por día** (ver 4.6).

### 4.6 Límite de Ataques Diarios — PENDIENTE IMPLEMENTAR
- Máximo **3 ataques por jugador atacante** a un mismo jugador humano cada 24h.
- Aplica solo a jugadores humanos. Inactivos e IA no tienen protección.
- Contador guardado en `player["ataques_recibidos"]`: `{jugador_atacante: [timestamps]}`.
- Al crear la orden: verificar cuántos ataques ha recibido ese defensor de ese atacante en las últimas 24h. Si ≥3, rechazar.
- Espionaje: se cuenta separado o junto (pendiente definir con Jorge).

### 4.7 Criaturas de Cueva — Comportamiento en Combate
- Si el **dueño pierde** el combate en el que participan criaturas capturadas:
  - Las criaturas se borran del JSON del jugador.
  - Regresan al mapa (`cuevas.json`): `_derrotado=False`, HP restaurado.
  - Pueden ser capturadas de nuevo por cualquier jugador.
- Si el dueño **gana**: las criaturas permanecen en su ciudad.
- Claves JSON sin tildes: BEHEMOT, CHUPACABRAS, DRAGON, LEVIATAN, PATOTAS, SIMURGH.

### 4.8 Sistema de Órdenes — Estado v10.2
- **`jugador_dest` inferido por coordenadas** cuando el frontend no lo manda.
- **Reposición vitaminizadas**: tras cada combate donde ALALAIA o ADMIN son defensores.
  - Aldeano: `1.5×10⁴⁰` · Básicas: 3M · Invocaciones: 3M · AlalaiA: 18 · Éon Supremo: 3.

### 4.9 Detección por Torre de Vigilancia
- **Mecánica**: `deteccion_torre` vs `sigilo_efectivo_atacante` (inversa del espionaje).
- `diferencia = deteccion_torre - sigilo_efectivo`

| Diferencia | Nivel | Información al defensor |
|---|---|---|
| ≤ 0 | No detectado | Silencio |
| 1–5 | Nv1 | Coordenadas origen |
| 6–15 | Nv2 | + Jugador atacante + coordenadas |
| 16–30 | Nv3 | + Tipo de orden (ATAQUE/ESPIONAJE) |
| 31–53 | Nv4 | + Tipos de unidades |
| ≥ 54 | Nv5 | Todo: cantidades, niveles por tipo, stats herrería, dueños |

- Torre nv50: detección=101, radio=2000 tiles (cubre todo el mapa).
- **Overlay**: aparece en cualquier pantalla en máximo 5s. `pendiente_desactivar=True` si no ha sido vista.

### 4.10 Espionaje — Inteligencia
- Nv5 revela: unidades con cantidades, `unit_levels` por tipo de tropa, bonus de herrería, tropas prestadas con dueños, criaturas de cueva capturadas.

### 4.11 Alianzas — Modelo Multi-Líder
- `"lideres": [str]` — múltiples líderes simultáneos.
- Retorno proporcional de tropas prestadas por ciudad_origen.
- Endpoints: `/promover`, `/degradar`, `/crear`, `/solicitar`, `/aceptar`, `/rechazar`, `/salir`, `/prestar`, `/reclamar`.

### 4.12 Mensajería Interna
- `backend/db/global/messages.json` (máx 500, FIFO).
- Tipos: DIRECTO y ALIANZA (broadcast).
- Badge no leídos en nav, polling 5s.

### 4.13 Informes de Batalla
- Campo `rol: "ATACANTE"/"DEFENSOR"` — perspectiva correcta para cada jugador.
- Polling 2s con fetches en paralelo.

---

## 5. MECÁNICAS DE JUEGO

### 5.1 Recursos Infinitos
- ALMACEN nv50 → todos los materiales = `"__INF__"`.
- SANTUARIO_ARCANO nv50 → MANÁ = `"__INF__"`.
- VITAMINIZADAS tienen `__INF__` por defecto en todos los recursos.

### 5.2 Cuentas Vitaminizadas (ALALAIA y ADMIN)
- Recursos `__INF__`, tropas repuestas automáticamente tras combate.
- Torre nv50 en todas las ciudades → detección Nv5 de cualquier movimiento.
- No pueden aliarse fuera de VITAMINIZADOS.

### 5.3 NG+ (New Game Plus) — DISEÑO COMPLETO

#### Condición de activación
Derrotar a KarlakÁ con exactamente 1 Éon Supremo.

#### Qué se preserva
- Herrerías, Universidad, Almacenes, Santuarios Arcanos (niveles actuales).
- 50% de la experiencia total acumulada.
- 50% del poder militar (tropas básicas e invocaciones).

#### Qué se reparte (antes del reinicio, a voluntad del jugador)
- El 50% de XP restante → a cualquier jugador que el jugador decida (aliados o no).
- Las tropas sobrantes (el otro 50% militar) → a cualquier jugador que decida.

#### Qué se reinicia
- Ciudades → nv1 en todos los edificios (excepto los preservados).
- Recursos → valores iniciales del CSV `iniciales.csv`.
- Tropas → 50% de las que tenía.
- El mundo completo: dioses resurgen, cuevas se repueblan, KarlakÁ permanece igual.

#### Bonus acumulativos por vuelta
- +1 ciudad máxima por cada vuelta completada.
- Cada 5 vueltas: +10 niveles adicionales de tropa desbloqueables.
- **Cuenta espejo**: activación manual por el jugador. Nombre = nombre del jugador + consecutivo (ej: JOTICALINDO2). Funciona como cuenta humana normal. Almacenes, Santuarios y Universidad a nivel máximo desde el inicio.

#### AlalaiAs propias
- Con cada reinicio de NG+, las invocaciones AlalaiA del jugador se potencian un 10% acumulativo en todos sus stats.

#### Portales adicionales
- Cada vuelta de NG+ genera 10 portales nuevos con condiciones más exigentes (por definir).

#### El Objetivo del Servidor (NG+6)
- Al completar el nivel 50 de tropas y terminar el reinicio 5 (entrando en NG+6):
  - El jugador pierde su alianza — se convierte en **entidad independiente**.
  - Se convierte en objetivo activo del servidor: todos los jugadores que lo derroten o le resistan ganan un **bonus enorme de experiencia**.
  - Sus cuentas espejo se independizan (lo abandonan).
  - Puede seguir atacando normalmente.
  - Sus futuros NG+ incluyen a otros jugadores de NG+ como **condición obligatoria de reinicio** (similar a un portal).
  - KarlakÁ sigue con el mismo poder — él es ahora parte del mundo, no solo un jugador.

#### Campos en el JSON del jugador
```json
{
  "ciclo_ng": 0,
  "ng_ciudades_bonus": 0,
  "ng_niveles_tropa_bonus": 0,
  "ng_cuentas_espejo": [],
  "es_objetivo_servidor": false,
  "alalaia_potenciacion": 1.0
}
```

### 5.4 Evento KarlakÁ (cada 3 días) — DISEÑO COMPLETO

#### Mecánica
- KarlakÁ ataca a todos los jugadores activos (excluidos: AlalaiA, ADMIN, JIARITO, GINAO).
- Empieza con el **0.1% de su poder total** (PA, CA, HP).
- Cada ronda del evento: si algún jugador resiste, KarlakÁ incrementa en 0.1%.
- Continúa hasta que **ningún jugador resiste**.

#### Recompensa por resistir
- Cada jugador que resiste un incremento de 0.1% recibe XP equivalente al **0.1% de matar 10 Éones Supremos**.
- Cuanto más lejos aguante (0.1%, 0.2%... hasta 100%), más XP acumula.

#### Continuidad entre eventos
- El siguiente evento (3 días después) arranca en el **nivel final del evento anterior − 0.1%**.
- Mínimo siempre: 0.1%.
- Si nadie resistió en el evento anterior, el siguiente arranca en 0.1% de nuevo.

#### Estado del evento
Almacenado en `backend/db/global/karlaka_event.json`:
```json
{
  "ultimo_evento": 1234567890,
  "proximo_evento": 1234827090,
  "nivel_actual_pct": 0.1,
  "nivel_maximo_alcanzado": 0.0,
  "activo": false,
  "resultados": {}
}
```

### 5.5 Portales
- 10 portales originales con condiciones en `portales_condiciones.csv`.
- Cada vuelta de NG+ genera 10 portales adicionales (condiciones por definir).
- **Sistema de portales: PENDIENTE DE IMPLEMENTAR COMPLETAMENTE.**

---

## 6. JUGADORES Y MUNDO

### 6.1 Estado actual
| Jugador | Tipo | Ciudades | Estado |
|---|---|---|---|
| JOTICALINDO | Humano/test | 12 (jL01–jL12) | nv27 · 261 dioses · nv_max=33 · NG+0 |
| JIARITO | Especial | 15 | unit_levels por tipo nv40 |
| GINAO | Especial | Variable | Aliado AAA_KILLERS |
| ALALAIA | Vitaminizada | 14 (AlalaiA02–15) | __INF__ · Aldeano=1.5×10⁴⁰ · Torre nv50 |
| ADMIN | Vitaminizado | 14 (Admin02–15) | __INF__ · Torre nv50 |

### 6.2 Alianzas activas
| Alianza | Líderes | Miembros |
|---|---|---|
| AAA_KILLERS | JOTICALINDO | JOTICALINDO, JIARITO, GINAO |
| VITAMINIZADOS | ADMIN | ADMIN, ALALAIA |

### 6.3 Contraseña de todos los jugadores
`3333`

---

## 7. BUGS RESUELTOS (v10.2)

| Bug | Causa | Fix |
|---|---|---|
| `float("__INF__")` crash generalizado | `float()` directo sin `_srf` | `safe_resource_float` importado en todos los sistemas |
| Criaturas cueva: 1 de 3 visible | Clave legacy `"DRAGÓN"` con tilde | Normalizado a `"DRAGON"` + army.js busca ambas |
| Inputs tropas prestadas resetean a 1000 | Misma clave `_seleccion` para múltiples entradas | Clave compuesta `"UNIDAD|ciudad_origen"` |
| Tropas prestadas no regresan a ciudad correcta | Retorno a primera ciudad_origen solamente | Retorno proporcional por cada entrada |
| Ataques no detectados por Torre | `jugador_dest=null` cuando no se rellena el campo | Backend infiere jugador_dest por coordenadas |
| Overlay alerta nunca aparece | `app.js` sin poller instalado | `app.js` con `startAlertPoller()` instalado |
| Alerta se desactiva antes de ser vista | `activa=False` inmediatamente al llegar orden | `pendiente_desactivar=True` hasta que usuario la cierra |
| AlalaiA sin tropas tras combate | `_reponer_vitaminizadas` no instalada | Instalada en `orders.py` |
| Obras no se aplican | `city.py` no llamaba `procesar_obras` | Añadido en `_procesar_ciudad` |
| Espionaje nv5 sin tropas prestadas ni criaturas | `_recopilar_inteligencia` incompleta | Añadidos `tropas_prestadas`, `criaturas_cueva`, `unit_levels`, herrería |
| Informes tardan varios minutos | Fetches secuenciales + polling 5s | `Promise.all` paralelo + polling 2s |
| Informe atacante = defensor | `reports.js` ignoraba campo `rol` | Perspectiva por `rol: "ATACANTE"/"DEFENSOR"` |
| Mapa con alianza hardcodeada | `ALIANZA_JOTICALINDO = Set([...])` fijo | Carga dinámica desde `/api/alliances/{jugador}` |
| `cantidad_min_sacerdote` no definida | Función no añadida al instalar `queues.py` | Función + `_srf` importado correctamente |
| `_srf` no definida en `buildings.py` | Import en posición incorrecta | Import en posición 977 del archivo |

---

## 8. PENDIENTES PRIORIZADOS

### 8.1 PRÓXIMA SESIÓN
1. **Límite de ataques por ciudad/día** (3 por atacante cada 24h, solo jugadores humanos)
2. **Criaturas de cueva regresan al mapa** cuando el dueño pierde el combate
3. **NG+ — sistema completo** (`backend/systems/ngplus.py`)
4. **Evento KarlakÁ** (`backend/systems/karlaka_event.py`)

### 8.2 Funcionales pendientes
- Sistema de portales (condiciones en CSV, lógica pendiente)
- Portales adicionales NG+ (condiciones por definir en sesión futura)
- Pantalla Ajustes (`settings.js`) vacía
- Imágenes `alalaia_small.png` / `karlaka_small.png` dan 404
- Centrado del mapa en ciudad propia al navegar
- Bug `valor_cumplido: false` en informes de victoria por valor
- `LAST_PROD` de JL2–JL12 muy antiguo → producción retroactiva exagerada

---

## 9. NOTAS DE DISEÑO — REGLAS QUE NUNCA CAMBIAN

- **JIARITO no es IA autónoma** — cuenta especial controlada por Jorge.
- **La herrería NO afecta invocaciones** — solo tropas básicas.
- **Las invocaciones NO tienen nivel** — son las que son.
- **Las criaturas de cueva NO tienen nivel** — capturadas tal cual.
- **Aldeanos: producidos por CC, no por cuartel.**
- **Zona prohibida KarlakÁ: solo para FUNDAR**, no para ataques.
- **Dioses: un jugador, un dios, una vez.**
- **Combate vs dioses/cuevas: SIEMPRE individual** (sin tropas prestadas).
- **Muralla: destreza=∞, PA=0, HP finito, NO se regenera.**
- **`__INF__`** es string en JSON. Usar `safe_resource_float()` para aritmética.
- **Excluidos del evento KarlakÁ**: AlalaiA, ADMIN, JIARITO, GINAO.
- **NG+6**: jugador pasa a ser objetivo del servidor, sin alianza.
- **KarlakÁ**: mismo poder en todos los ciclos NG+. No escala.
- **Invocaciones**: 14 tipos. Claves: DEMONIO, ANIMA, ESPECTRO, GOLEM, CENTAURO, KRAKEN, ALONARDO, MADRESELVA, COLOSO, FENIX, DRAGON_DE_ORO, CABALLERO_DE_LUZ, ALALAIA, EON_SUPREMO.
- **Tropas básicas**: 10 tipos. Niveles 1–40.
- **Navtabs**: CIUDAD · MISIONES · EJÉRCITO · MAPA IMPERIAL · INFORMES · ALIANZA · MENSAJES · AJUSTES.
