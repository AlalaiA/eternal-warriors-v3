# ETERNAL WARRIORS v3.0 — DOCUMENTO MAESTRO v10.3
**Fecha:** Junio 2026 · **Stack:** Python FastAPI + HTML5 Canvas · **Plataforma:** Windows 10
**Repo:** `https://github.com/AlalaiA/eternal-warriors-v3.git`

---

## ⚠ LECCIONES CRÍTICAS DE CAMBIOS DE CHAT

1. **Nunca asumir que un fix está instalado en disco.** Siempre verificar con `grep` antes de parchear.
2. **Pedir el archivo actual antes de cada fix.** El archivo en `/mnt/user-data/uploads/` puede diferir del contexto.
3. **`__INF__` es un string sentinel**, no float. Usar `safe_resource_float(v)` en lugar de `float(v)`. Aplica también en `_calcular_saqueo` — los recursos `__INF__` se tratan como capacidad_carga completa disponible.
4. **El orders_ticker silencia excepciones.** Con `traceback.print_exc()` en el `except` de `main.py` se ven los errores reales.
5. **Los CSV de edificios tienen header partido en 2 líneas** — `csv.reader` los lee como una sola entrada con `\n` embebido.
6. **`unit_levels` tiene dos formatos:** `{NIVEL_DE_TROPAS: N}` (legacy) y `{EXPLORADOR: 40, ...}` (por tipo). Siempre usar `_nivel_tropas_player()`.
7. **`parseInt("1e+20")` devuelve 1** — usar `Math.floor(Number(val))` para cantidades grandes en JS.
8. **Nunca reescribir un archivo completo** sin antes leer el archivo exacto en disco.
9. **`safe_resource_float` debe importarse en TODOS los sistemas** que lean recursos de ciudad: `production.py`, `buildings.py`, `queues.py`, `espionage.py`, `orders.py`, `combat.py`.
10. **Claves de invocaciones con guión bajo** (`DRAGON_DE_ORO`) vs con espacio (`DRAGON DE ORO`) — normalizar siempre con `_norm()` al buscar. `_calcular_bajas` debe normalizar ambas claves antes de comparar.
11. **`_unidades_ciudad()`** debe probar ambas formas de clave (con `_` y con espacio).
12. **Tropas prestadas con clave compuesta** `"UNIDAD|ciudad_origen"` en el frontend para distinguir múltiples entradas del mismo jugador+unidad.
13. **`retornar_tropas_prestadas_post_orden`** debe devolver proporcionalmente a cada ciudad_origen, no todo a la primera.
14. **Nunca limpiar/borrar datos del jugador sin su consentimiento explícito.**
15. **Cuando dos archivos tienen el mismo nombre**, el sistema sobreescribe el anterior al subirlos. Renombrar temporalmente (ej: `systems_alliances.py`) antes de subir.
16. **`sigilos.extend([val] * cantidad_enorme)`** explota con cantidades astronómicas. La función `_calcular_sigilo_efectivo` recibe `[(sigilo, cantidad)]` y opera matemáticamente, nunca expande listas.
17. **`_resolver_espionaje_entidad`**: los sobrevivientes de `combate["sobrevivientes_atk"]` tienen claves normalizadas por `_norm()`. Reconvertir al formato original de `orden["unidades"]` antes de asignar a `unidades_sobrevivientes`.
18. **Espionaje a dioses/cuevas**: SIEMPRE desencadena combate — son entidades hostiles. No existe "espionaje exitoso" contra entidades del mundo.
19. **`_calcular_saqueo`**: el almacén/santuario nv50 NO protege contra saqueo — solo el escondite protege. El atacante se lleva lo que cabe en su capacidad de carga.
20. **Las invocaciones NO tienen capacidad de carga** — no saquean ni transportan recursos. Solo las tropas básicas (col[5] del CSV = CARGA DE MATERIALES).

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
1. Subir `EW_Maestro_v10_3.md` al nuevo chat.
2. Subir archivos modificados en la sesión anterior.
3. Claude lee el documento, confirma estado y pregunta qué se trabaja.

### 1.4 Archivos clave a subir según contexto

| Archivo | Ruta | Cuándo subir |
|---|---|---|
| `orders.py` | `backend/systems/` | Bugs órdenes/combate/espionaje/detección/NG+ |
| `combat.py` | `backend/systems/` | Bugs combate/sigilo/muralla/criaturas/saqueo |
| `espionage.py` | `backend/systems/` | Bugs espionaje/inteligencia |
| `alliances.py` | `backend/systems/` | Bugs alianzas/préstamo/retorno — subir como `alliances_systems.py` |
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
| `city.js` | `frontend/js/screens/` | Bugs ciudad/leveling modal |
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
│   │   ├── map.py                — entidades + _derrotado en respuesta
│   │   ├── queues.py             — colas cuartel/templo
│   │   ├── alliances.py          — alianzas multi-líder
│   │   ├── alerts.py             — alertas Torre de Vigilancia
│   │   ├── messages.py           — mensajería interna
│   │   ├── leveling.py           — subida de nivel tropas
│   │   ├── buildings.py
│   │   ├── escondite.py
│   │   └── auth.py
│   ├── systems/
│   │   ├── orders.py             — órdenes + límite ataques + saqueo espionaje
│   │   ├── combat.py             — combate + sigilo corregido + saqueo __INF__
│   │   ├── espionage.py          — espionaje nv1-5
│   │   ├── detection.py          — detección Torre de Vigilancia
│   │   ├── alliances.py          — multi-líder: rechazar/promover/degradar
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
│           ├── city.js           — leveling modal sin parpadeo (_refrescarLeveling)
│           ├── army.js           — clave compuesta prestadas + criaturas cueva
│           ├── map.js            — filtra _derrotado en _drawLayer y _hitTest
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
| `caracteristicas_unidades.csv` | col[3]=PA, col[5]=CARGA, col[6]=destreza, col[7]=velocidad, col[8]=sigilo | Aldeano nv1: PA=15, nv40: PA=440000 |
| `caracteristicas_invocaciones.csv` | col[2]=PA, col[7]=nv_min_sacerdote, col[8]=tiempo_SEG, col[9]=costo_mana, col[10]=cantidad_min | Sin carga — no saquean |
| `tiempo_base_produccion_unidades_basicas.csv` | col[1]=segundos | Header dice minutos — MIENTE |
| `edificio4_torre_de_vigilancia.csv` | col[6]=deteccion, col[9]=radiocasillasvigilancia | Radio nv50=2000 tiles |
| `edificio7_almacen.csv` | col[6]=capacidad | nv50='infinito' → __INF__ — NO protege contra saqueo |
| `edificio8_santuario_arcano.csv` | col[6]=capacidad | nv50='infinito' → __INF__ |
| `edificio3_muralla.csv` | col[6]=hp | HP finito. Destreza=∞, PA=0. No regenera. |
| `edificio6_escondite.csv` | col[6]=capacidad_ejercito, col[7]=cap_material | Único que protege recursos contra saqueo |
| `dioses.csv` | col[9]=experiencia | 400 dioses, CA asc |
| `cuevas.csv` | hp,pa,ca,destreza,experiencia | 999 cuevas liberadas |
| `portales_condiciones.csv` | 8 columnas de condiciones | Ver sección 5.5 |

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

### 4.6 Límite de Ataques Diarios — IMPLEMENTADO
- Máximo **3 ataques por jugador atacante** a un mismo jugador humano cada 24h.
- Solo aplica cuando el DEFENSOR es jugador humano real (excluidos: ALALAIA, ADMIN, JIARITO, GINAO).
- Contador en `player["ataques_recibidos"]`: `{jugador_atacante: [timestamps]}`.
- **Doble chequeo**: al crear la orden + al llegar (race condition). Si llega y el límite ya está lleno → orden anulada, tropas regresan intactas.
- **Espionaje detectado** (combate) → también cuenta como ataque.
- Espionaje silencioso → NO cuenta.

### 4.7 Criaturas de Cueva — Comportamiento en Combate
- Si el **dueño pierde**: criaturas se borran del JSON, regresan al mapa con HP restaurado.
- Si el dueño **gana**: permanecen.
- Claves JSON sin tildes: BEHEMOT, CHUPACABRAS, DRAGON, LEVIATAN, PATOTAS, SIMURGH.

### 4.8 Sistema de Órdenes
- **`jugador_dest` inferido por coordenadas** cuando el frontend no lo manda.
- **Reposición vitaminizadas**: tras cada combate donde ALALAIA o ADMIN son defensores.
- **Espionaje a entidades del mundo** (dioses/cuevas): SIEMPRE combate — no hay espionaje silencioso.
- **Saqueo en espionaje detectado**: si el atacante gana el combate, saquea igual que ATAQUE usando tropas básicas sobrevivientes. Las invocaciones no cargan.

### 4.9 Detección por Torre de Vigilancia
- **Mecánica**: `deteccion_torre` vs `sigilo_efectivo_atacante`.
- `diferencia = sigilo_efectivo - deteccion_torre`

| Diferencia | Nivel | Información al defensor |
|---|---|---|
| ≤ 0 | No detectado | Silencio |
| 1–5 | Nv1 | Coordenadas origen |
| 6–15 | Nv2 | + Jugador atacante + coordenadas |
| 16–30 | Nv3 | + Tipo de orden (ATAQUE/ESPIONAJE) |
| 31–53 | Nv4 | + Tipos de unidades |
| ≥ 54 | Nv5 | Todo: cantidades, niveles por tipo, stats herrería, dueños |

- Torre nv50: detección=101, radio=2000 tiles.
- **Overlay**: aparece en cualquier pantalla en máximo 5s.

### 4.10 Sigilo — Fórmula Canónica
```
sigilo_max  = máximo sigilo de cualquier unidad del pelotón
umbral      = max(sigilo_max × 0.5, 10)
efectivo    = sigilo_max
  + por cada unidad adicional:
      si sigilo_unidad >= umbral → +3.0
      si sigilo_unidad <  umbral → -1.0
resultado   = max(0.0, min(200.0, efectivo))
```
- **Referencia canónica**: 20 exploradores nv40 (sigilo=98) vs Torre nv50 (detección=101):
  - umbral=max(49,10)=49 · efectivo=98+19×3=155 · diff=54 → **Nv5** ✓
- Con millones de invocaciones (sigilo=1 < umbral=10) → todas restan → efectivo=0 → detectado ✓
- Con mezcla exploradores+invocaciones → invocaciones restan → detectado ✓
- **NUNCA** expandir listas por cantidad — operar matemáticamente.

### 4.11 Saqueo
- Solo tropas básicas saquean (col[5] CSV = CARGA DE MATERIALES).
- Invocaciones: carga=0, no saquean.
- Escondite: único edificio que protege recursos contra saqueo.
- Almacén/Santuario nv50: NO protegen contra saqueo.
- Recursos `__INF__`: el atacante se lleva su capacidad de carga completa de ese recurso.
- MANÁ: solo lo pueden transportar sacerdotes.

### 4.12 Espionaje — Inteligencia
- Nv5 revela: unidades con cantidades, `unit_levels` por tipo de tropa, bonus de herrería, tropas prestadas con dueños, criaturas de cueva capturadas.
- Espionaje a dioses/cuevas: **siempre combate**, sin intel.

### 4.13 Alianzas — Modelo Multi-Líder
- `"lideres": [str]` — múltiples líderes simultáneos.
- `_migrar_alianza()` + `_migrar_todas()`: migran formato viejo `{lider: str}` al nuevo.
- Funciones implementadas: `rechazar_solicitud`, `promover_lider`, `degradar_lider`.
- Retorno proporcional de tropas prestadas por ciudad_origen.

### 4.14 Mensajería Interna
- `backend/db/global/messages.json` (máx 500, FIFO).
- Tipos: DIRECTO y ALIANZA (broadcast).
- Badge no leídos en nav, polling 5s.

### 4.15 Informes de Batalla
- Campo `rol: "ATACANTE"/"DEFENSOR"` — perspectiva correcta para cada jugador.
- Polling 2s con fetches en paralelo.

### 4.16 Modal de Subir Nivel — Sin Parpadeo
- `_abrirLeveling()`: si el modal ya existe, llama `_refrescarLeveling()` en lugar de destruirlo.
- `_refrescarLeveling()`: actualiza solo `#leveling-xp` y `#leveling-filas` in-place.
- `_subirNivel()`: llama `_refrescarLeveling()` tras el fetch — cero parpadeo.

### 4.17 Mapa — Filtro de Derrotados
- `map.py` (backend): incluye `_derrotado: true/false` en cada entidad de la respuesta.
- `map.js` (frontend): `_drawLayer` y `_hitTest` filtran `e._derrotado` — no se dibujan ni se pueden clickear.

### 4.18 Ranking Militar
**Fórmula de valor por unidad:**
- Tropas básicas: `val(nv) = (PA_unidad_en_nv / PA_aldeano_en_nv) × nv`
  - Aldeano nv1 = 1 punto · Aldeano nv40 = 40 puntos
- Invocaciones: `val = PA_invocacion / PA_aldeano_nv1`
- Criaturas de cueva: `val = PA_criatura / PA_aldeano_nv1`
- Excluidos del ranking: ALALAIA, ADMIN.
- `minimum_military_top` en portales = puesto máximo permitido (ej: 10 → debe estar en top 10, es decir puesto ≤ 10).

---

## 5. MECÁNICAS DE JUEGO

### 5.1 Recursos Infinitos
- ALMACEN nv50 → todos los materiales = `"__INF__"`.
- SANTUARIO_ARCANO nv50 → MANÁ = `"__INF__"`.
- VITAMINIZADAS tienen `__INF__` por defecto en todos los recursos.
- `__INF__` no protege contra saqueo — solo el escondite protege.

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
- El 50% de XP restante → a cualquier jugador que el jugador decida.
- Las tropas sobrantes (el otro 50% militar) → a cualquier jugador que decida.

#### Qué se reinicia
- Ciudades → nv1 en todos los edificios (excepto los preservados).
- Recursos → valores iniciales del CSV `iniciales.csv`.
- Tropas → 50% de las que tenía.
- El mundo completo: dioses resurgen, cuevas se repueblan, KarlakÁ permanece igual.

#### Bonus acumulativos por vuelta
- +1 ciudad máxima por cada vuelta completada.
- Cada 5 vueltas: +10 niveles adicionales de tropa desbloqueables.
- **Cuenta espejo**: activación manual por el jugador. Nombre = nombre del jugador + consecutivo (ej: JOTICALINDO2). Almacenes, Santuarios y Universidad a nivel máximo desde el inicio.

#### AlalaiAs propias
- Con cada reinicio de NG+, las invocaciones AlalaiA del jugador se potencian un 10% acumulativo en todos sus stats.

#### Portales adicionales
- Cada vuelta de NG+ genera 10 portales nuevos con condiciones más exigentes (por definir).

#### El Objetivo del Servidor (NG+6)
- Al completar el nivel 50 de tropas y terminar el reinicio 5:
  - El jugador pierde su alianza — entidad independiente.
  - Objetivo activo del servidor: todos los que lo derroten o resistan ganan bonus enorme de XP.
  - Sus cuentas espejo se independizan.
  - Sus futuros NG+ incluyen a otros jugadores de NG+ como condición obligatoria.

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
- Cada ronda: si algún jugador resiste, KarlakÁ incrementa en 0.1%.
- Continúa hasta que ningún jugador resiste.

#### Recompensa por resistir
- Cada jugador que resiste un incremento de 0.1% recibe XP equivalente al 0.1% de matar 10 Éones Supremos.

#### Continuidad entre eventos
- El siguiente evento arranca en nivel_final_anterior − 0.1%. Mínimo: 0.1%.

#### Estado del evento
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

### 5.5 Portales — Condiciones
10 portales con condiciones escalonadas en `portales_condiciones.csv`. Columnas:

| Campo | Descripción |
|---|---|
| `minimun_level_all_troops` | Nivel mínimo de TODAS las tropas |
| `number_battles_win` | Batallas ganadas acumuladas |
| `caves_defeated` | Cuevas derrotadas |
| `espionage_missions` | Misiones de espionaje |
| `percentage_resistance_karlaka` | % máximo resistido al evento KarlakÁ |
| `minimum_military_top` | Puesto máximo en ranking militar (≤ este valor) |
| `minimun_child_accounts` | Número de cuentas aliadas/hijas con nivel mínimo |
| `minimun_level_child_or_alliance_accounts` | Nivel mínimo de dichas cuentas |

**Campos en JSON del jugador para verificación:**
```json
{
  "batallas_ganadas": 400000,
  "cuevas_derrotadas": 800,
  "misiones_espionaje": 105000,
  "resistencia_karlaka_pct": 60,
  "cuentas_aliadas_nv_min": 10,
  "nv_cuentas_aliadas": 38
}
```

**Lógica de verificación:**
- `minimum_military_top`: puesto_jugador ≤ valor_csv (ej: top=10 → puesto≤10)
- Resto de condiciones: valor_jugador ≥ valor_csv
- Excluidos del ranking: ALALAIA, ADMIN

---

## 6. JUGADORES Y MUNDO

### 6.1 Estado actual
| Jugador | Tipo | Ciudades | Estado |
|---|---|---|---|
| JOTICALINDO | Humano/test | 12 (jL01–jL12) | **nv40** · **400 dioses** · todos portales cumplidos · NG+0 · XP=1.08e+32 |
| JIARITO | Especial | 15 | unit_levels por tipo nv40 |
| GINAO | Especial | Variable | Aliado AAA_KILLERS |
| ALALAIA | Vitaminizada | 14 (AlalaiA02–15) | __INF__ · Aldeano=1.5×10⁴⁰ · Torre nv50 |
| ADMIN | Vitaminizado | 14 (Admin02–15) | __INF__ · Torre nv50 |

**JOTICALINDO — valores de referencia para reposición:**
```
VAL_REF = 7143499999999999999999999999999999999999999932513499
ANIMA   = 17400000000099990000115810338288741156477808850475895658946
ESPECTRO= 349999999999999900575599999999998437529221227758187114497
GOLEM   = 497526000000000099994875425079286170419241278563024065449139
CENTAURO= 4975259999999999999999992856563328735
Resto de invocaciones = VAL_REF (en las 12 ciudades)
Edificios: ALMACEN=50, SANTUARIO_ARCANO=50, UNIVERSIDAD=50, HERRERIA=50, CASA=50
Recursos: __INF__ en todos
```

**Contadores de progreso (portal 10 cumplido):**
```
batallas_ganadas=400000, cuevas_derrotadas=800, misiones_espionaje=105000
resistencia_karlaka_pct=60, cuentas_aliadas_nv_min=10, nv_cuentas_aliadas=38
```

### 6.2 Alianzas activas
| Alianza | Líderes | Miembros |
|---|---|---|
| AAA_KILLERS | JOTICALINDO | JOTICALINDO, JIARITO, GINAO |
| VITAMINIZADOS | ADMIN | ADMIN, ALALAIA |

### 6.3 Contraseña de todos los jugadores
`3333`

---

## 7. BUGS RESUELTOS

### v10.2 (sesión anterior)
| Bug | Causa | Fix |
|---|---|---|
| `float("__INF__")` crash generalizado | `float()` directo sin `_srf` | `safe_resource_float` importado en todos los sistemas |
| Criaturas cueva: 1 de 3 visible | Clave legacy `"DRAGÓN"` con tilde | Normalizado a `"DRAGON"` + army.js busca ambas |
| Inputs tropas prestadas resetean a 1000 | Misma clave `_seleccion` para múltiples entradas | Clave compuesta `"UNIDAD|ciudad_origen"` |
| Tropas prestadas no regresan a ciudad correcta | Retorno a primera ciudad_origen solamente | Retorno proporcional por cada entrada |
| Overlay alerta nunca aparece | `app.js` sin poller instalado | `app.js` con `startAlertPoller()` instalado |
| AlalaiA sin tropas tras combate | `_reponer_vitaminizadas` no instalada | Instalada en `orders.py` |
| Obras no se aplican | `city.py` no llamaba `procesar_obras` | Añadido en `_procesar_ciudad` |

### v10.3 (esta sesión)
| Bug | Causa | Fix |
|---|---|---|
| `ImportError: rechazar_solicitud` al arrancar | Faltaban 3 funciones en `systems/alliances.py` | Añadidas `rechazar_solicitud`, `promover_lider`, `degradar_lider` + `_migrar_alianza/_todas` |
| Dioses derrotados siguen en el mapa | 118 dioses sin `_derrotado=True` en `dioses.json` | Auditoría y corrección de `dioses.json` |
| Dioses derrotados visibles en frontend | `map.py` no enviaba `_derrotado`; `map.js` no filtraba | `map.py` incluye campo; `map.js` filtra en `_drawLayer` y `_hitTest` |
| Espionaje a dioses: exitoso sin combate | `_resolver_espionaje_entidad` solo combatía si sigilo≤0 | Entidades siempre detectan y combaten |
| Bajas incorrectas al enviar mezcla de invocaciones | `_calcular_bajas` no normalizaba claves (`EON_SUPREMO` vs `EON SUPREMO`) | Normalización con `_norm()` en ambos lados |
| `cannot fit 'int' into index-sized integer` | `sigilos.extend([val] * cantidad_enorme)` con cantidades astronómicas | `_calcular_sigilo_efectivo` opera matemáticamente sin expandir listas |
| Sigilo con millones de invocaciones = 200 (tope) | Fórmula premiaba más unidades | Umbral absoluto mínimo=10: invocaciones (sig=1) siempre restan |
| Tropas perdidas tras espionaje a entidad | Claves normalizadas de sobrevivientes no coincidían con ciudad | Reconversión `_norm→original` antes de asignar `unidades_sobrevivientes` |
| Modal subir nivel parpadea al subir nivel | `_subirNivel` destruía y recreaba el modal completo | `_refrescarLeveling` actualiza in-place sin destruir el modal |
| Límite de ataques diarios: no existía | No implementado | `_verificar_limite_ataques` + `_registrar_ataque` en `systems/orders.py` |
| Espionaje detectado: botín siempre vacío | `orden["botin"] = {}` hardcodeado | `_calcular_saqueo` aplicado cuando atacante gana el combate del espionaje |
| `float("__INF__")` en `_calcular_saqueo` | `float(defensor_city.get(recurso))` sin `_srf` | `_srf` importado; `__INF__` = capacidad_carga completa disponible |
| Almacén nv50 bloqueaba todo saqueo | `if almacen_inf: continue` en bucle de saqueo | Eliminada la condición — solo el escondite protege |

---

## 8. PENDIENTES PRIORIZADOS

### 8.1 PRÓXIMA SESIÓN
1. **Combate contra KarlakÁ** — mecánica especial: 1 Éon Supremo exacto activa NG+
2. **NG+ — sistema completo** (`backend/systems/ngplus.py`)
3. **Evento KarlakÁ** (`backend/systems/karlaka_event.py`)
4. **Ver contenido de misión en vuelo** — click sobre punto en movimiento o zona de informe → mostrar unidades, tipo, destino, opción de retornar (tropas prestadas regresan a ciudad origen)
5. **Sacerdotes requeridos bloqueados en misiones** — las cantidades mínimas de sacerdotes por invocación no deben estar disponibles para enviar en misiones

### 8.2 Funcionales pendientes
- Backend verificación de portales (endpoint que chequea condiciones y las muestra en UI)
- Sistema de portales completo (lógica de paso, efectos)
- Portales adicionales NG+ (condiciones por definir)
- Pantalla Ajustes (`settings.js`) vacía
- Imágenes `alalaia_small.png` / `karlaka_small.png` dan 404
- Centrado del mapa en ciudad propia al navegar
- Bug `valor_cumplido: false` en informes de victoria por valor
- `LAST_PROD` de JL2–JL12 muy antiguo → producción retroactiva exagerada
- Criaturas de cueva regresan al mapa cuando el dueño pierde el combate

---

## 9. NOTAS DE DISEÑO — REGLAS QUE NUNCA CAMBIAN

- **JIARITO no es IA autónoma** — cuenta especial controlada por Jorge.
- **La herrería NO afecta invocaciones** — solo tropas básicas.
- **Las invocaciones NO tienen nivel** — son las que son.
- **Las invocaciones NO tienen capacidad de carga** — no saquean ni transportan.
- **Las criaturas de cueva NO tienen nivel** — capturadas tal cual.
- **Aldeanos: producidos por CC, no por cuartel.**
- **Zona prohibida KarlakÁ: solo para FUNDAR**, no para ataques.
- **Dioses: un jugador, un dios, una vez.**
- **Combate vs dioses/cuevas: SIEMPRE individual** (sin tropas prestadas).
- **Espionaje vs dioses/cuevas: SIEMPRE combate** — no hay intel silenciosa.
- **Muralla: destreza=∞, PA=0, HP finito, NO se regenera.**
- **`__INF__`** es string en JSON. Usar `safe_resource_float()` para aritmética.
- **Almacén/Santuario nv50**: dan recursos infinitos al dueño pero NO protegen contra saqueo.
- **Solo el Escondite** protege recursos contra saqueo.
- **Excluidos del evento KarlakÁ**: AlalaiA, ADMIN, JIARITO, GINAO.
- **Excluidos del ranking militar**: ALALAIA, ADMIN.
- **NG+6**: jugador pasa a ser objetivo del servidor, sin alianza.
- **KarlakÁ**: mismo poder en todos los ciclos NG+. No escala.
- **Invocaciones**: 14 tipos. Claves: DEMONIO, ANIMA, ESPECTRO, GOLEM, CENTAURO, KRAKEN, ALONARDO, MADRESELVA, COLOSO, FENIX, DRAGON_DE_ORO, CABALLERO_DE_LUZ, ALALAIA, EON_SUPREMO.
- **Tropas básicas**: 10 tipos. Niveles 1–40.
- **Navtabs**: CIUDAD · MISIONES · EJÉRCITO · MAPA IMPERIAL · INFORMES · ALIANZA · MENSAJES · AJUSTES.
- **Portales 1–10**: todos cumplidos por JOTICALINDO. Verificación: puesto_militar ≤ minimum_military_top; resto ≥.
