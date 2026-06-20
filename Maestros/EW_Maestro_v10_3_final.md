# ETERNAL WARRIORS v3.0 — DOCUMENTO MAESTRO v10.3
**Fecha:** Junio 2026 · **Stack:** Python FastAPI + HTML5 Canvas · **Plataforma:** Windows 10
**Repo:** `https://github.com/AlalaiA/eternal-warriors-v3.git`

---

## ⚠ LECCIONES CRÍTICAS DE CAMBIOS DE CHAT

1. **Nunca asumir que un fix está instalado en disco.** Siempre verificar con `grep` antes de parchear.
2. **Pedir el archivo actual antes de cada fix.**
3. **`__INF__` es string sentinel** — usar `safe_resource_float(v)`. Aplica en `_calcular_saqueo`, `_ejecutar_retorno`, `aplicar_resultado_combate`.
4. **El orders_ticker silencia excepciones.** Con `traceback.print_exc()` se ven los errores reales.
5. **CSV de edificios tienen header partido en 2 líneas.**
6. **`unit_levels` dos formatos:** `{NIVEL_DE_TROPAS: N}` y `{EXPLORADOR: 40, ...}`. Usar `_nivel_tropas_player()`.
7. **`parseInt("1e+20")` devuelve 1** — usar `Math.floor(Number(val))`.
8. **Nunca reescribir un archivo completo** sin leer el exacto en disco.
9. **`safe_resource_float` en TODOS los sistemas** que lean recursos.
10. **Claves con guión bajo vs espacio** — normalizar con `_norm()`.
11. **`_calcular_bajas`** normaliza ambas claves con `_norm()`.
12. **Tropas prestadas con clave compuesta** `"UNIDAD|ciudad_origen"`.
13. **Retorno proporcional** de tropas prestadas a cada ciudad_origen.
14. **Nunca limpiar/borrar datos del jugador sin consentimiento explícito.**
15. **Archivos con mismo nombre**: renombrar temporalmente al subir (ej: `alliances_systems.py`).
16. **`sigilos.extend([val] * cantidad_enorme)`** explota — operar matemáticamente con `[(sigilo, cantidad)]`.
17. **Sobrevivientes normalizados**: reconvertir claves `_norm→original` antes de asignar a `unidades_sobrevivientes`.
18. **Espionaje a dioses/cuevas**: SIEMPRE combate.
19. **`_calcular_saqueo`**: Almacén nv50 NO protege. Solo escondite protege.
20. **Invocaciones NO tienen carga**. Sacerdotes transportan MANÁ (bolsa separada).
21. **Coma decimal europea en CSV** (`6,3E+021`) falla con `float()` — usar `_sf()` robusto.
22. **`_load_invocaciones`**: AlalaiA y Éon tienen coma europea — sin `_sf()` devuelven `nivel_min=99`.
23. **Orden de definición Python**: `cantidad_min_sacerdote` debe definirse ANTES de `sacerdotes_reservados_ciudad`.
24. **Banner de alerta**: `pointer-events:none` en CSS bloquea clics aunque se sobrescriba inline.
25. **Dismiss de alerta**: Banner filtra por `a.activa`; overlay filtra por `!a.vista`.
26. **`jugador_dest`**: usar `_formState.jugDest` como fallback si el campo de texto está vacío.

---

## 1. PRERROGATIVAS DE TRABAJO

### 1.1 Protocolo de comunicación
- Claude frena y espera si necesita un insumo. **Nunca pregunta y sigue produciendo.**
- Respuestas concisas. Sin verbosidad innecesaria.
- Correcciones directas: Jorge corrige supuestos erróneos y Claude los incorpora sin debate.
- **Nunca inventar mecánicas ni valores de CSV.** Si falta info, parar y preguntar.
- **Los CSV son canónicos y no se modifican** salvo instrucción explícita.
- **Nunca limpiar/borrar datos del jugador sin consentimiento explícito.**

### 1.2 Protocolo de código
- Siempre: `grep` → `view` → `str_replace` exacto. Nunca reescribir archivos completos.
- Validación obligatoria (`ast.parse`) después de cada cambio Python.
- **Un fix por problema.** Sin bundling de cambios no relacionados.

### 1.3 Protocolo de arranque de nueva sesión
1. Subir `EW_Maestro_v10_3.md` al nuevo chat.
2. Subir archivos modificados en la sesión anterior.
3. Claude lee el documento, confirma estado y pregunta qué se trabaja.

### 1.4 Archivos clave a subir según contexto

| Archivo | Ruta | Cuándo subir |
|---|---|---|
| `orders.py` | `backend/systems/` | Bugs órdenes/combate/espionaje/detección/saqueo |
| `combat.py` | `backend/systems/` | Bugs combate/sigilo/saqueo/__INF__ |
| `espionage.py` | `backend/systems/` | Bugs espionaje/inteligencia |
| `alliances.py` | `backend/systems/` | Subir como `alliances_systems.py` |
| `queues.py` | `backend/systems/` | Bugs colas/sacerdotes/invocaciones |
| `detection.py` | `backend/systems/` | Bugs detección Torre |
| `ngplus.py` | `backend/systems/` | NG+ (PENDIENTE) |
| `karlaka_event.py` | `backend/systems/` | KarlakÁ (PENDIENTE) |
| `city.py` | `backend/api/` | Bugs producción/tick/espacios |
| `orders.py` | `backend/api/` | Bugs endpoint órdenes/historial |
| `map.py` | `backend/api/` | Bugs mapa/detectadas |
| `alerts.py` | `backend/api/` | Bugs alertas |
| `army.js` | `frontend/js/screens/` | Bugs MISIONES/sacerdotes reservados |
| `map.js` | `frontend/js/screens/` | Bugs mapa/trayectorias detectadas |
| `reports.js` | `frontend/js/screens/` | Bugs informes |
| `city.js` | `frontend/js/screens/` | Bugs ciudad/leveling/espacios |
| `app.js` | `frontend/js/` | Bugs alertas/banner/overlay |

---

## 2. STACK Y ARQUITECTURA

```
E:\0000ew V2Claude\
├── backend/
│   ├── main.py
│   ├── api/
│   │   ├── city.py               — tick + espacios usados/max por ciudad
│   │   ├── orders.py             — historial incluye REGRESANDO
│   │   ├── map.py                — _derrotado + /detected/{jugador}
│   │   ├── queues.py, alliances.py, alerts.py, messages.py, leveling.py
│   ├── systems/
│   │   ├── orders.py             — límite ataques + saqueo + detección
│   │   ├── combat.py             — sigilo + saqueo 2 bolsas + _safe_float robusto
│   │   ├── queues.py             — _sf() robusto + sacerdotes_reservados_ciudad
│   │   ├── alliances.py          — multi-líder + _migrar_todas
│   │   ├── detection.py, espionage.py, production.py, buildings.py, herreria.py
│   │   ├── ngplus.py             — PENDIENTE
│   │   └── karlaka_event.py      — PENDIENTE
│   └── data/save_manager.py
├── frontend/
│   ├── game.html
│   └── js/
│       ├── app.js                — banner parpadeante clickeable + overlay detalle
│       └── screens/
│           ├── city.js           — leveling sin parpadeo + espacios usados/max
│           ├── army.js           — sacerdotes reservados + jugDest fallback
│           ├── map.js            — trayectorias detectadas enemigas
│           ├── reports.js        — r2 prioridad sobre r1
│           └── alliance.js, invocations.js, messages.js, settings.js (vacío)
└── csv/
```

---

## 3. CSV CANÓNICOS

| CSV | Columnas clave | Notas |
|---|---|---|
| `caracteristicas_unidades.csv` | col[3]=PA, col[5]=CARGA, col[6]=DST, col[7]=VEL, col[8]=SIGILO | Aldeano nv1: PA=15, nv40: PA=440.000 |
| `caracteristicas_invocaciones.csv` | col[2]=PA, col[7]=nv_min_sac, col[8]=tiempo_SEG, col[9]=costo_mana, col[10]=cantidad_min | Valores con coma europea — usar `_sf()` |
| `iniciales.csv` | col[2]=Espacios Máximos | HUMANO=400, ALALAIA/ADMIN/JIARITO=715 |
| `edificio4_torre_de_vigilancia.csv` | col[6]=deteccion, col[9]=radio | nv50: detección=101, radio=2000 |
| `edificio7_almacen.csv` | col[6]=capacidad | nv50=__INF__ — NO protege contra saqueo |
| `edificio6_escondite.csv` | cap_ejercito + cap_material | Único que protege contra saqueo |
| `edificio3_muralla.csv` | col[6]=hp | HP finito, destreza=∞, PA=0, no regenera |
| `portales_condiciones.csv` | 8 columnas | 10 portales — todos cumplidos por JOTICALINDO |
| `dioses.csv` | col[9]=experiencia | 400 dioses — todos derrotados por JOTICALINDO |

**Espacios por edificio (suma = 715):**
CC=45, Casa=50, Muralla=50, Torre=50, CViajes=40, Escondite=40, Almacén=50, Santuario=50, Universidad=50, Herrería=40, Templo1=50, Templo2=50, Templo3=50, Cuartel1=50, Cuartel2=50

---

## 4. SISTEMAS IMPLEMENTADOS

### 4.1 Sigilo — Fórmula Canónica
```
umbral      = max(sigilo_max × 0.5, 10)
efectivo    = sigilo_max + Σ(unidades_con_sigilo≥umbral × +3) + Σ(resto × -1)
resultado   = max(0, min(200, efectivo))
```
- 20 exploradores nv40 (sig=98): efectivo=155, diff=54 → **Nv5** ✓
- Invocaciones (sig=1 < umbral=10): siempre restan → detectado ✓

### 4.2 Saqueo — Dos Bolsas Separadas
- **Materiales**: carga de básicas EXCEPTO sacerdotes. `__INF__` reparte equitativamente.
- **Maná**: carga de sacerdotes EXCLUSIVAMENTE. Bolsa completamente independiente.
- Solo escondite protege. Almacén/Santuario nv50 NO protegen.

### 4.3 Detección por Torre
- Se evalúa en cada tick Y al crear la orden.
- Alerta guardada con `t_llegada`, `x_dest`, `y_dest`.
- No duplica alertas — actualiza nivel si sube.
- Niveles 1-5 según diferencia `detección_torre - sigilo_efectivo`.

### 4.4 Sistema de Alertas
- **Overlay**: una vez por alerta nueva (`!vista`). Countdown de llegada.
- **Banner parpadeante** (`top:40px`): persiste mientras `activa=True`. Clickeable → overlay.
- **Mapa**: trayectoria enemiga con línea punteada + punto animado.
- **Dismiss**: marca `vista=True` pero no elimina la alerta activa del banner.

### 4.5 Sacerdotes Reservados
- `sacerdotes_reservados_ciudad(city)`: suma `cantidad_min` de todas las colas de templo activas.
- army.js muestra disponibles = total − reservados (con 🔒).
- Si sacerdotes caen por debajo del mínimo: cola cancelada, maná devuelto.

### 4.6 Espacios por Ciudad
- Cada nivel de cada edificio = 1 espacio.
- Máximo: HUMANO=400, ALALAIA/ADMIN/JIARITO=715.
- Mostrado en barra inferior de ciudad: `285/400` (rojo si lleno).

### 4.7 Límite de Ataques Diarios
- Máx 3 ataques por atacante a un mismo jugador humano por 24h.
- Excluidos de protección: ALALAIA, ADMIN, JIARITO, GINAO.
- Espionaje detectado cuenta. Silencioso no cuenta.

### 4.8 Reposición Vitaminizadas
- Se repone al ser atacadas Y al retornar de un ataque propio.
- ALDEANO=1.5e+22, ALALAIA=18, EON=3, básicas=3M, invocaciones=3M.

### 4.9 Informes de Batalla
- Historial incluye COMPLETADAS + REGRESANDO (con resultado).
- `reports.js`: r2 (historial completo) sobreescribe r1 (resumen activas).
- Informe aparece al combatir, no al retornar.

---

## 5. JUGADORES Y MUNDO

### 5.1 Estado actual
| Jugador | Tipo | Estado |
|---|---|---|
| JOTICALINDO | Humano/test | nv40 · 400 dioses · portales 1-10 cumplidos · NG+0 · XP≈1.08e+32 · todas unidades=VAL_REF |
| JIARITO | Especial | unit_levels por tipo nv40 |
| GINAO | Especial | Aliado AAA_KILLERS |
| ALALAIA | Vitaminizada | __INF__ · Aldeano=1.5e+22 · Torre nv50 · 715 espacios |
| ADMIN | Vitaminizado | __INF__ · Torre nv50 · 715 espacios |

**VAL_REF JOTICALINDO (todas las unidades en las 12 ciudades):**
```
7143500000000000105764294366352530706695833247547392
```

**Contadores de progreso JOTICALINDO:**
```json
{
  "batallas_ganadas": 400000, "cuevas_derrotadas": 800,
  "misiones_espionaje": 105000, "resistencia_karlaka_pct": 60,
  "cuentas_aliadas_nv_min": 10, "nv_cuentas_aliadas": 38,
  "ciclo_ng": 0, "es_objetivo_servidor": false, "alalaia_potenciacion": 1.0
}
```

### 5.2 Alianzas
| Alianza | Líderes | Miembros |
|---|---|---|
| AAA_KILLERS | JOTICALINDO | JOTICALINDO, JIARITO, GINAO |
| VITAMINIZADOS | ADMIN | ADMIN, ALALAIA |

### 5.3 Contraseña todos los jugadores: `3333`

---

## 6. DISEÑO NG+ Y KARLAKÂ (PENDIENTE IMPLEMENTAR)

### NG+
- **Activación**: derrotar KarlakÁ con exactamente 1 Éon Supremo.
- **Preserva**: Herrerías, Universidad, Almacenes, Santuarios + 50% XP + 50% tropas.
- **Reinicia**: ciudades nv1 + recursos iniciales + mundo (dioses/cuevas resurgen).
- **Bonus**: +1 ciudad/vuelta; +10 niveles tropas cada 5 vueltas; NG+6 = Objetivo del Servidor.

### Evento KarlakÁ (cada 3 días)
- Ataca a todos excepto ALALAIA, ADMIN, JIARITO, GINAO.
- Empieza en 0.1% de poder, +0.1% por ronda resistida.
- XP por resistir cada 0.1% = 0.1% de matar 10 Éones Supremos.

---

## 7. PENDIENTES PRIORIZADOS

### 7.1 PRÓXIMA SESIÓN — Jugadores IA
1. **Sistema de jugadores IA** — comportamiento autónomo:
   - Atacan ciudades cercanas según sus stats
   - Defienden sus ciudades
   - Producen recursos y entrenan tropas
   - Interactúan con el evento KarlakÁ
2. **Comportamiento diferenciado**: IA agresiva, defensiva, expansionista

### 7.2 Sistemas grandes pendientes
3. **Combate contra KarlakÁ** — 1 Éon Supremo exacto activa NG+
4. **NG+ completo** (`backend/systems/ngplus.py`)
5. **Evento KarlakÁ** (`backend/systems/karlaka_event.py`)
6. **Ver contenido de misión en vuelo** — click sobre punto → unidades + opción retornar
7. **Portales** — backend verificación + UI

### 7.3 Pendientes menores
- Pantalla Ajustes (`settings.js`) vacía
- Imágenes `alalaia_small.png` / `karlaka_small.png` dan 404
- Centrado del mapa en ciudad propia al navegar
- Bug `valor_cumplido: false` en informes de victoria por valor
- `LAST_PROD` JL2–JL12 muy antiguo → producción retroactiva exagerada
- Criaturas de cueva regresan al mapa cuando el dueño pierde
- Timer del header hardcodeado — conectar al backend KarlakÁ

---

## 8. REGLAS QUE NUNCA CAMBIAN

- **JIARITO no es IA** — cuenta controlada por Jorge.
- **Herrería NO afecta invocaciones** — solo tropas básicas.
- **Invocaciones NO tienen nivel ni capacidad de carga**.
- **Sacerdotes transportan MANÁ exclusivamente** (bolsa separada).
- **Aldeanos**: producidos por CC, no cuartel.
- **Zona KarlakÁ**: prohibido fundar, sí atacar.
- **Dioses**: un jugador, un dios, una vez.
- **Combate/Espionaje vs dioses/cuevas**: SIEMPRE combate, sin intel silenciosa.
- **Muralla**: destreza=∞, PA=0, HP finito, no regenera.
- **`__INF__`**: string en JSON, `_srf()` para aritmética.
- **Almacén/Santuario nv50**: recursos ∞ pero NO protegen contra saqueo.
- **Solo Escondite** protege contra saqueo.
- **Excluidos KarlakÁ**: ALALAIA, ADMIN, JIARITO, GINAO.
- **Excluidos ranking militar**: ALALAIA, ADMIN.
- **NG+6**: jugador = Objetivo del Servidor, sin alianza.
- **Portales 1–10**: todos cumplidos por JOTICALINDO.
- **Universidad**: 1 por jugador (solo en ciudad capital).
