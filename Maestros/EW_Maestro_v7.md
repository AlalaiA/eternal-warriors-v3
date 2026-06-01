# ETERNAL WARRIORS v3.0 — DOCUMENTO MAESTRO v7
**Fecha:** Mayo 2026 | **Repo:** `https://github.com/AlalaiA/eternal-warriors-v3.git`

---

## REGLAS DE TRABAJO — NO NEGOCIABLES

1. **Scripts de patch** — nunca generar archivos completos. Generar scripts Python que modifiquen el archivo en disco con `str.replace()` o `re.sub()`. Ejemplo: `patch_queues.py` que abre `queues.py`, reemplaza el ancla exacta y guarda.
2. **Auditar antes de escribir** — pedir archivo actual, leer ancla exacta.
3. **Un problema a la vez** — diagnosticar completamente, luego un solo fix.
4. **No especular** — si falta info, parar y pedirla.
5. **No bucles** — si un fix falla dos veces, auditar el archivo real.
6. **CSVs canónicos son inamovibles** — están en `csv\`, nunca se modifican.
7. **Git commit** después de bloques importantes.
8. **Respuestas concisas** — sin explicaciones largas innecesarias.
9. **JSON siempre con `save_manager.py` robusto** — nunca escribir JSON directamente.
10. **Verificar sintaxis** antes de entregar cualquier archivo Python o JS.

---

## STACK TECNOLÓGICO

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12 + FastAPI |
| Frontend | HTML5 + Canvas 2D isométrico |
| DB | JSON por jugador en `backend/db/players/` |
| CSVs | `csv\` (canónicos, NO TOCAR) |
| Servidor | `python -m uvicorn backend.main:app --reload --port 8000` |

---

## ÁRBOL DEL PROYECTO

```
E:\0000ew V2Claude\
├── run.bat
├── csv\                              # CSVs canónicos (NO TOCAR)
├── backend\
│   ├── main.py                       # Routers registrados: city, map, auth, buildings, queues, escondite
│   ├── data\save_manager.py          # _SafeEncoder — nunca produce JSON corrupto
│   ├── api\
│   │   ├── auth.py
│   │   ├── city.py                   # GET/POST ciudad, tasas, tick
│   │   ├── map.py
│   │   ├── buildings.py              # GET info, POST upgrade, DELETE upgrade
│   │   ├── queues.py                 # GET estado, POST cuartel/templo, DELETE cancelar
│   │   └── escondite.py              # GET estado, POST meter/sacar material/tropas
│   └── systems\
│       ├── production.py             # Materiales, maná, aldeanos con caps infinito nivel 50
│       ├── queues.py                 # Colas entrenamiento e invocación
│       ├── buildings.py              # Info edificios, iniciar_obra, procesar_obras
│       ├── herreria.py               # Bonus PA/CA/HP acumulativo todas las ciudades
│       ├── escondite.py              # Meter/sacar materiales y tropas básicas
│       ├── combat.py                 # PENDIENTE
│       ├── espionage.py              # PENDIENTE
│       ├── orders.py                 # PENDIENTE
│       ├── alliances.py              # PENDIENTE
│       └── experience.py             # PENDIENTE
└── frontend\
    ├── index.html / game.html
    ├── css\theme.css / game.css / city.css
    └── js\
        ├── app.js                    # Orquestador, cleanup() entre pantallas
        └── screens\
            ├── city.js               # Renderer isométrico + paneles + ticker
            ├── building_menu.js      # Menú edificios, colas, escondite
            ├── map.js                # PENDIENTE
            ├── army.js               # PENDIENTE
            ├── invocations.js        # PENDIENTE
            ├── reports.js            # PENDIENTE
            └── settings.js           # PENDIENTE
```

---

## SISTEMAS IMPLEMENTADOS ✅

### Producción (`production.py`)
- Materiales: aldeanos × tasa CC, cap almacén (∞ nivel 50)
- Maná: sacerdotes × tasa nivel sacerdote, cap santuario (∞ nivel 50)
- Aldeanos: CC produce X/hora, cap = capacidad Casa (∞ nivel 50)
- Retroactividad: 3 días máximo desde `LAST_PROD`
- Nivel 50 almacén/santuario/casa = `1e300` (sin cap real)
- Parser maná: comas = separadores de miles (`26,587` = 26587)

### Colas (`queues.py`)
- **2 colas simultáneas** por cuartel Y por templo
- Tiempo = base_seg × (1 - red_cuartel/100 - red_universidad/100), cap 95%
- CSV unidades: tiempos en **segundos** (no minutos, pese al header)
- Tildes normalizadas: ÁNIMA→ANIMA, GÓLEM→GOLEM, FÉNIX→FENIX, ÉON→EON
- Costo materiales descontado al iniciar (no si almacén nivel 50)
- Costo maná descontado al iniciar templo
- Verificación nivel mínimo sacerdote por invocación
- Cancelación por índice (cola 1 o cola 2)
- Entrega progresiva al hacer GET o tick

### Edificios (`buildings.py`)
- **4 obras simultáneas** máximo por ciudad
- Descuento universidad en tiempo de construcción (col[7])
- Parser robusto: comas = miles, % eliminado en stat y tiempo
- Universidad tiempo_col=8 (9 columnas)
- Obras v2 (`{"KEY":...}`) ignoradas, solo procesa obras v3 (`{"edificio":..., "inicio":..., "duracion_seg":...}`)
- Sin descuento de materiales si almacén nivel 50

### Herrería (`herreria.py`)
- Bonus acumulativo de TODAS las ciudades del jugador
- PA + CA + HP sumados de cada herrería activa
- Efecto inmediato al subir nivel
- Expuesto en GET ciudad como `bonus_herreria`

### Escondite (`escondite.py` + `api/escondite.py`)
- Manual: jugador decide qué y cuánto esconder
- Capacidades: cap_ejercito (tropas) y cap_material (por cada material)
- **NO guarda Maná**
- **SÍ guarda Invocaciones** — no ocupan espacio (capacidad ilimitada)
- Protege contra ataques normales
- **NO protege** contra nivel 40 + AlalaiA/Éon Supremo
- Reincorporación manual
- Endpoints: GET estado, POST meter/sacar material/tropas
- Campo `ESCONDITE_DATA` en JSON ciudad: `{materiales:{...}, tropas:{...}}`

### Frontend (`city.js`)
- Grid isométrico 9×9, edificios en celdas 2-8
- Edificios nivel 0 = ruinas (gris semitransparente)
- Muralla seleccionable en todo el perímetro (highlight en hover)
- Torres en 4 esquinas, todas clickeables
- Barras de progreso doradas sobre edificios en construcción (segundo pase)
- Panel izquierdo: Recursos (∞ si nivel 50), Producción/Hora, Logística
- Panel derecho: Ejército, Invocaciones, Herrería bonus
- Ticker local sin modificar cityData (offset visual), sync 30s
- Token de ciudad en ticker — se detiene solo si cambia ciudad
- cleanup() exportado y llamado por app.js al cambiar pantalla

### Save Manager (`save_manager.py`)
- `_SafeEncoder`: NaN→0, Inf→1e300, nunca produce JSON inválido
- `load_json`: parsea solo el primer objeto válido (ignora basura al final)
- `ensure_ascii=True` siempre

---

## ENDPOINTS BACKEND ACTIVOS

| Método | Ruta | Función |
|---|---|---|
| GET | `/api/city/{jugador}/{ciudad}` | Ciudad + producción retroactiva + bonus herrería |
| GET | `/api/city/{jugador}/{ciudad}/tasas` | Solo tasas/seg |
| POST | `/api/city/{jugador}/{ciudad}/tick` | Sync producción cada 30s |
| GET | `/api/city/{jugador}` | Lista ciudades del jugador |
| GET | `/api/queues/{jugador}/{ciudad}` | Estado colas activas |
| POST | `/api/queues/{jugador}/{ciudad}/cuartel` | Iniciar entrenamiento |
| POST | `/api/queues/{jugador}/{ciudad}/templo` | Iniciar invocación |
| DELETE | `/api/queues/{jugador}/{ciudad}/{tipo}?idx=0` | Cancelar cola por índice |
| GET | `/api/buildings/{jugador}/{ciudad}/{edificio}` | Info edificio |
| POST | `/api/buildings/{jugador}/{ciudad}/{edificio}/upgrade` | Iniciar obra |
| DELETE | `/api/buildings/{jugador}/{ciudad}/{edificio}/upgrade` | Cancelar obra |
| GET | `/api/escondite/{jugador}/{ciudad}` | Estado escondite |
| POST | `/api/escondite/{jugador}/{ciudad}/meter_material` | Esconder material |
| POST | `/api/escondite/{jugador}/{ciudad}/sacar_material` | Sacar material |
| POST | `/api/escondite/{jugador}/{ciudad}/meter_tropas` | Esconder tropas |
| POST | `/api/escondite/{jugador}/{ciudad}/sacar_tropas` | Sacar tropas |

---

## ESTRUCTURA JSON JUGADOR

```json
{
  "player": "JOTICALINDO",
  "unit_levels": {"MAGO": 2, "SACERDOTE": 10},
  "experiencia": 0.0,
  "ng_plus": 0,
  "cities": [
    {
      "NOMBRE": "jL01",
      "JUGADOR": "JOTICALINDO",
      "CENTRO_DE_CIUDAD": 38,
      "CASA": 50,
      "ALMACEN": 50,
      "SANTUARIO_ARCANO": 50,
      "UNIVERSIDAD": 9,
      "HERRERIA": 5,
      "MURALLA": 40,
      "TORRE_DE_VIGILANCIA": 13,
      "TEMPLO_1": 2, "TEMPLO_2": 3, "TEMPLO_3": 5,
      "CUARTEL_1": 7, "CUARTEL_2": 4,
      "ESCONDITE": 0,
      "ALDEANO": 153000000000,
      "MADERA": 5.58e+35,
      "MANA": 17000000000000,
      "LAST_PROD": 1779417811.0,
      "COLAS": [
        {
          "tipo": "CUARTEL_1",
          "unidad": "MAGO",
          "cantidad_total": 10,
          "cantidad_hecha": 0,
          "tiempo_por_unidad_seg": 1824.0,
          "inicio": 1779417219.0
        }
      ],
      "OBRAS": [
        {
          "edificio": "MURALLA",
          "nivel_dest": 41,
          "inicio": 1779417126.0,
          "duracion_seg": 28080000
        }
      ],
      "ESCONDITE_DATA": {
        "materiales": {"MADERA":0,"PIEDRA":0,"HIERRO":0,"CARBON":0,"ORO":0},
        "tropas": {"ALDEANO":0,"EXPLORADOR":0,"SACERDOTE":0,"GUERRERO":0,"COMANDO":0,"MERCENARIO":0,"MARINE":0,"CYBORG":0,"MAGO":0,"METAHUMANO":0}
      }
    }
  ]
}
```

---

## JUGADORES

| Jugador | Tipo | Ciudades | Notas |
|---|---|---|---|
| JIARITO | JIARITO | 12 | Capital: Bogotá. Nivel 40. |
| GINAO | HUMANO | 12 | Aliado JIARITO. Nivel 40. |
| JOTICALINDO | HUMANO | 12 | Capital: jL01. Sac.Nv.10, Mago Nv.2 |
| ALALAIA | VITAMINIZADA | — | Especial |

**Alianzas:** JIARITO ↔ GINAO únicamente.

---

## CSV CANÓNICOS — MAPA DE USO

| CSV | Notas importantes |
|---|---|
| `edificio1_centro_de_ciudad.csv` | col[6]=aldeanos/hora, col[7]=tiempo |
| `edificio2_casa.csv` | col[6]=capacidad aldeanos |
| `edificio6_escondite.csv` | col[6]=cap_ejercito, col[7]=cap_material, col[8]=tiempo |
| `edificio7_almacen.csv` | col[6]=cap_material (nivel 50=infinito) |
| `edificio8_santuario_arcano.csv` | col[6]=cap_mana (nivel 50=infinito, texto "infinito") |
| `edificio9_universidad.csv` | col[6]=red_colas%, col[7]=red_edificios%, col[8]=tiempo — 9 columnas total |
| `edificio10_herreria.csv` | col[6]=PA, col[7]=CA, col[8]=HP, col[9]=tiempo |
| `edificio11_templo.csv` | col[6]=rebaja_invocacion% |
| `edificio12_cuartel.csv` | col[6]=red_tiempo% |
| `aldeanos_materiales.csv` | Tasa producción materiales por aldeano/nivel CC |
| `mana_sacerdotes.csv` | Comas = miles (26,587 = 26587), col[0]=tasa, col[1]=nivel |
| `tiempo_base_produccion_unidades_basicas.csv` | Tiempos en **SEGUNDOS** (header dice minutos, miente) |
| `caracteristicas_invocaciones.csv` | col[7]=nivel_min_sacerdote, col[8]=tiempo_seg, col[9]=costo_mana — tildes en nombres |
| `caracteristicas_unidades.csv` | col[9]=madera...col[13]=oro — costo independiente del nivel |

---

## BUGS CONOCIDOS / PENDIENTES PRÓXIMA SESIÓN

### Pendientes Prioridad ALTA
1. **Escondite invocaciones** — implementar meter/sacar invocaciones (sin ocupar espacio de cap_ejercito ni cap_material)
2. **Escondite** — subir nivel desde 0 en jL01 para poder usarlo
2. **Pantalla Ejército** — ver y gestionar tropas por ciudad
3. **Pantalla Invocaciones** — ver invocaciones disponibles
4. **Sistema de órdenes** — TRANSPORTE, DESPLAZAMIENTO, ATAQUE, ESPIONAJE
5. **Sistema de combate** (`combat.py`) — aplica bonus herrería PA/CA/HP

### Pendientes Prioridad MEDIA
6. **Mapa Imperial** — renderer isométrico con entidades del mundo
7. **Sistema de experiencia** (`experience.py`)
8. **Pantalla Informes** — historial batallas y espionajes
9. **WebSocket** — tiempo real para órdenes y eventos
10. **Portales y KarlakÁ** — sistema desbloqueo y boss final

### Pendientes Prioridad BAJA
11. **Arte ciudad** — mejorar funciones canvas 2D
12. **NG+ (New Game Plus)** — reinicio con ventajas
13. **Imágenes `alalaia_small.png` / `karlaka_small.png`** — 404 en frontend

---

## PROBLEMAS RECURRENTES Y SOLUCIONES

### JSON corrupto
```bash
# Reparar JSON corrupto:
python fix_colas.py  # o cualquier script de reparación
# Siempre copiar save_manager.py ANTES de joticalindo.json
# Siempre parar el servidor ANTES de copiar JSONs
```

### Puerto 8000 ocupado
```bash
netstat -ano | findstr :8000
taskkill /F /PID [PID]
```

### Cache de módulos Python
```bash
# Si un fix no toma efecto, cerrar la ventana del servidor completamente
# No usar Ctrl+C, cerrar la ventana
```

### Materiales infinitos (nivel 50)
- `production.py` usa `cap >= 1e50` para decidir si aplicar cap
- `buildings.py` no descuenta materiales si `ALMACEN >= 50`
- `_fmt()` en JS muestra `∞` cuando valor es `Infinity` o `!isFinite()`

---

## CONVENCIONES DE NOMENCLATURA

| Concepto | Variable/campo |
|---|---|
| Ciudad activa | `sessionStorage.ciudad_actual` |
| Jugador activo | `sessionStorage.jugador` |
| Tasas producción | `window._prodTasas` |
| Estado ciudad local | `window._cityData` |
| Bonus herrería | `window._bonusHerreria` |
| Ticker producción | `ticker` (módulo city.js) |
| Sync servidor | `sync` (módulo city.js, cada 30s) |
| Nivel sacerdote | `player.unit_levels.SACERDOTE` |
| Cola activa | `city.COLAS[]` |
| Obra activa | `city.OBRAS[]` (formato v3 con `inicio` y `duracion_seg`) |
| Datos escondite | `city.ESCONDITE_DATA` |

---

## FLUJO DE TRABAJO ESTÁNDAR

```
1. Usuario reporta bug o pide feature
2. IA pide archivo actual si lo necesita
3. IA audita con grep/view — nunca asume
4. IA declara: "Voy a modificar X en Y porque Z"
5. IA genera archivo descargable
6. Usuario copia en orden: 1) parar servidor 2) copiar archivos 3) arrancar
7. Git commit si cambios importantes
```

---

## NOTAS TÉCNICAS CRÍTICAS

1. **Tiempos CSV unidades** = SEGUNDOS (no minutos, el header miente)
2. **Comas en CSVs** = separadores de miles, no decimales
3. **Nivel 50** almacén/santuario/casa = infinito real (sin cap)
4. **Universidad** tiene 9 columnas: tiempo en col[8], no col[7]
5. **Obras v2** `{"KEY":...}` deben ignorarse, solo procesar v3
6. **Tildes en invocaciones** se normalizan al cargar CSV (ÁNIMA→ANIMA)
7. **2 colas simultáneas** por cuartel Y por templo (independientes)
8. **4 obras simultáneas** máximo por ciudad (universidad 1 sola por jugador)
9. **Herrería acumulativa** de TODAS las ciudades del jugador
10. **Escondite NO guarda** Maná. Sí guarda Invocaciones (sin ocupar espacio). Pendiente: implementar invocaciones en escondite.
