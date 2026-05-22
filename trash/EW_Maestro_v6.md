# ETERNAL WARRIORS v3.0 — DOCUMENTO MAESTRO DE SESIÓN v6
**Fecha:** Mayo 2026 | **Ruta proyecto:** `E:\0000ew V2Claude\`

---

## REGLAS DE TRABAJO — NO NEGOCIABLES

1. **Scripts descargables** — todo fix va en un script `.py` descargable, nunca inline.
2. **Instrucciones de consola formateadas** — cada comando en bloque de código separado.
3. **Nunca crear CSVs** — los CSVs son canónicos e inamovibles. Están en `E:\0000ew V2Claude\csv\`.
4. **Pedir archivos actuales** antes de tocar código — el disco puede diferir de lo subido.
5. **Auditar ancla exacta** antes de escribir OLD en cualquier fix.
6. **Un problema a la vez** — diagnosticar completamente, luego un solo fix verificado.
7. **No especular** — si falta información, parar y pedirla.
8. **No bucles de corrección** — si un fix falla dos veces, auditar el archivo real.
9. **Git commit** después de bloques importantes de cambios.
10. **Ahorro de tokens** — respuestas concisas, sin explicaciones largas innecesarias.

---

## STACK TECNOLÓGICO

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12 + FastAPI |
| Comunicación | REST + WebSocket (pendiente) |
| Frontend | HTML5 + Canvas 2D |
| Estilos | CSS3 + variables (tema épico oscuro) |
| DB | JSON por jugador en `backend/db/` |
| CSVs canónicos | `E:\0000ew V2Claude\csv\` |

---

## ÁRBOL DEL PROYECTO

```
E:\0000ew V2Claude\
├── run.bat                          # Arranca uvicorn
├── csv\                             # CSVs canónicos (NO TOCAR)
│   ├── edificio1_centro_de_ciudad.csv
│   ├── edificio2_casa.csv ... edificio12_cuartel.csv
│   ├── aldeanos_materiales.csv
│   ├── mana_sacerdotes.csv
│   ├── caracteristicas_unidades.csv
│   ├── caracteristicas_invocaciones.csv
│   ├── tiempo_base_produccion_unidades_basicas.csv
│   ├── experiencia_requerida.csv
│   ├── experiencia_por_invocaciones.csv
│   ├── experiencia_dada_por_unidades_basicas_por_nivel.csv
│   └── (portales, cuevas, dioses, inactivos, jugadoresia...)
├── backend\
│   ├── main.py                      # FastAPI — routers registrados
│   ├── ws_handler.py
│   ├── engine\game_engine.py
│   ├── data\save_manager.py
│   ├── api\
│   │   ├── auth.py
│   │   ├── city.py                  # GET ciudad, POST tick ✅
│   │   ├── map.py
│   │   └── queues.py                # Colas cuartel/templo ✅
│   └── systems\
│       ├── production.py            # Producción materiales + maná ✅
│       ├── queues.py                # Lógica de colas ✅
│       ├── combat.py                # PENDIENTE
│       ├── espionage.py             # PENDIENTE
│       ├── buildings.py             # PENDIENTE
│       ├── orders.py                # PENDIENTE
│       ├── alliances.py             # PENDIENTE
│       ├── experience.py            # PENDIENTE
│       └── fog_of_war.py            # PENDIENTE
├── frontend\
│   ├── index.html                   # Login
│   ├── game.html                    # Pantalla principal
│   ├── css\theme.css / game.css / city.css
│   ├── js\
│   │   ├── app.js                   # Orquestador + selector ciudades ✅
│   │   └── screens\
│   │       ├── city.js              # Vista ciudad canvas 2D ✅
│   │       ├── building_menu.js     # Menú edificio + colas ✅
│   │       ├── map.js               # PENDIENTE
│   │       ├── army.js              # PENDIENTE
│   │       ├── invocations.js       # PENDIENTE
│   │       ├── reports.js           # PENDIENTE
│   │       └── settings.js          # PENDIENTE
│   └── assets\
│       ├── ui\alalaia_small.png / karlaka_small.png
│       └── buildings\               # Sprites PNG de Gemini ✅
└── db\
    └── players\
        ├── jiarito.json / ginao.json / joticalindo.json
        ├── alalaia.json / admin.json / ia.json
        └── (humanos\ / ia\)
```

---

## ENDPOINTS BACKEND ACTIVOS

| Método | Ruta | Función |
|---|---|---|
| GET | `/api/city/{jugador}/{ciudad}` | Carga ciudad + producción retroactiva |
| GET | `/api/city/{jugador}/{ciudad}/tasas` | Solo tasas/seg |
| POST | `/api/city/{jugador}/{ciudad}/tick` | Sync producción cada 30s |
| GET | `/api/city/{jugador}` | Lista de ciudades del jugador |
| GET | `/api/queues/{jugador}/{ciudad}` | Estado colas activas |
| POST | `/api/queues/{jugador}/{ciudad}/cuartel` | Iniciar entrenamiento |
| POST | `/api/queues/{jugador}/{ciudad}/templo` | Iniciar invocación |
| DELETE | `/api/queues/{jugador}/{ciudad}/{tipo}` | Cancelar cola |

---

## SISTEMAS IMPLEMENTADOS ✅

### Producción (`backend/systems/production.py`)
- Materiales: `aldeanos × tasa_por_nivel_CC` — fuente: `aldeanos_materiales.csv`
- Maná: `sacerdotes × tasa_por_nivel_sacerdote` — fuente: `mana_sacerdotes.csv`
- Nivel sacerdote: `player['unit_levels']['SACERDOTE']` (NO `NIVEL_DE_TROPAS`)
- Retroactividad: 3 días máximo desde `LAST_PROD`
- Ticker frontend: 1 segundo local + sync backend cada 30s
- Tasa visible en UI: `+X/s` junto a cada recurso

### Colas (`backend/systems/queues.py`)
- **Cuarteles** (CUARTEL_1, CUARTEL_2, CUARTEL_3): unidades básicas
  - Tiempo = `TIEMPO_BASE_MIN × 60 × (1 - %reduccion_cuartel/100)`
  - Fuente: `tiempo_base_produccion_unidades_basicas.csv` + `edificio12_cuartel.csv`
- **Templos** (TEMPLO_1, TEMPLO_2, TEMPLO_3): invocaciones
  - Tiempo = `TIEMPO_BASE_MIN × 60 × (1 - %rebaja_templo/100)`
  - Costo maná descontado al iniciar
  - Requiere nivel mínimo sacerdote
  - Fuente: `caracteristicas_invocaciones.csv` + `edificio11_templo.csv`
- Retroactividad: 3 días desde `inicio` de la cola
- Cancelar templo: devuelve maná proporcional a pendientes

### Selector de ciudades (`frontend/js/app.js`)
- Click en nombre de ciudad en header → dropdown con las 12 ciudades
- Al seleccionar: recarga `city.js` con datos de la nueva ciudad
- `CIUDAD_ACTUAL` en `sessionStorage`

### Click en edificios (`frontend/js/screens/building_menu.js`)
- Click en canvas sobre Cuartel → menú entrenamiento
- Click en canvas sobre Templo → menú invocación
- Progreso en tiempo real con barra y countdown
- Botón cancelar

---

## BUGS CONOCIDOS A RESOLVER (próxima sesión)

### BUG 1 — "Unidad MAGO no reconocida" en cuartel
**Causa:** `tiempo_base_produccion_unidades_basicas.csv` tiene "Mago" con mayúscula inicial. El sistema hace `.upper()` y busca "MAGO", pero el CSV tiene el nombre con capitalización mixta ("Sacerdote", "Guerrero", etc.).
**Fix:** En `queues.py → _load_tiempo_unidades()`, normalizar la clave a uppercase al cargar:
```python
result[row[0].strip().upper()] = float(row[1].strip())
```
**Estado:** Está escrito así pero el match falla. Auditar el CSV real con:
```
python -c "open(r'csv/tiempo_base_produccion_unidades_basicas.csv').read()" 
```
y verificar encoding BOM y separador.

### BUG 2 — "Se requiere Sacerdote nivel 3000" en templo
**Causa:** `caracteristicas_invocaciones.csv` — el parser lee la columna de nivel mínimo sacerdote (índice 6) pero puede estar leyendo la columna equivocada. "Demonio" tiene nivel mínimo real ~7, no 3000.
**Fix:** Auditar estructura del CSV:
```
python -c "import csv; [print(i,r) for i,r in enumerate(csv.reader(open(r'csv/caracteristicas_invocaciones.csv',encoding='utf-8-sig'),delimiter=';')) if i<3]"
```
Luego ajustar el índice correcto en `_load_invocaciones()`.

### BUG 3 — city.js: C.Ciudad se ve como bloques azules rectangulares
**Causa:** `artCityHall()` usa `isoArt()` con colores azules planos. Necesita gradientes más ricos, texturas de piedra más visibles y mayor contraste entre caras.
**Pendiente:** Mejorar arte canvas 2D en próxima sesión de visuales.

---

## ESTRUCTURA JSON JUGADOR

```json
{
  "player": "JOTICALINDO",
  "unit_levels": {"MAGO": 2, "SACERDOTE": 5},
  "experiencia": 0.0,
  "ng_plus": 0,
  "cities": [
    {
      "NOMBRE": "jL01",
      "JUGADOR": "JOTICALINDO",
      "CENTRO_DE_CIUDAD": 38,
      "ALDEANO": 153011550064,
      "SACERDOTE": 1000,
      "MANA": 1990000000,
      "LAST_PROD": 1234567890.0,
      "COLAS": [
        {
          "tipo": "CUARTEL_1",
          "unidad": "GUERRERO",
          "cantidad_total": 1000,
          "cantidad_hecha": 234,
          "tiempo_por_unidad_seg": 22176,
          "inicio": 1234567890.0
        }
      ],
      "OBRAS": [...],
      "TEMPLO_1": 2, "TEMPLO_2": 3, "TEMPLO_3": 3,
      "CUARTEL_1": 6, "CUARTEL_2": 4
    }
  ]
}
```

---

## JUGADORES Y CIUDADES

| Jugador | Tipo | Ciudades | Notas |
|---|---|---|---|
| JIARITO | JIARITO | 12 | Capital: Bogotá. Nivel 40 todo. |
| GINAO | HUMANO | 12 | Aliado JIARITO. Nivel 40. |
| JOTICALINDO | HUMANO | 12 | Capital: jL01. Sacerdote Nv.5, Mago Nv.2 |
| ALALAIA | VITAMINIZADA | — | Especial |
| ADMIN | ADMIN | — | Especial |

**Alianzas activas:** JIARITO ↔ GINAO únicamente.

---

## CSV CANÓNICOS — MAPA DE USO

| CSV | Usado en |
|---|---|
| `edificio1_centro_de_ciudad.csv` | Tasas aldeanos/hora por nivel CC, costos subida |
| `aldeanos_materiales.csv` | Producción materiales por aldeano por nivel CC |
| `mana_sacerdotes.csv` | Producción maná por sacerdote por nivel |
| `tiempo_base_produccion_unidades_basicas.csv` | Tiempo entrenamiento cuartel |
| `edificio12_cuartel.csv` | % reducción tiempo por nivel cuartel |
| `edificio11_templo.csv` | % rebaja invocación por nivel templo |
| `caracteristicas_invocaciones.csv` | Tiempo, costo maná, nivel mín sacerdote por invocación |
| `caracteristicas_unidades.csv` | HP, PA, CA, Sigilo, Velocidad por unidad y nivel |
| `experiencia_requerida.csv` | XP necesaria por nivel de jugador |
| `experiencia_por_invocaciones.csv` | XP dada al invocar cada criatura |
| `experiencia_dada_por_unidades_basicas_por_nivel.csv` | XP por unidad y nivel |
| `edificio2_casa.csv` ... `edificio10_herreria.csv` | Costos y niveles de cada edificio |

---

## PENDIENTES POR ORDEN DE PRIORIDAD

### Prioridad ALTA
1. **BUG 1 y 2** — colas cuartel y templo no funcionan correctamente
2. **Subir nivel de edificio** — click en edificio → ver nivel actual, costo siguiente nivel, botón subir
3. **Pantalla Ejército** — ver y gestionar tropas por ciudad
4. **Pantalla Invocaciones** — ver invocaciones disponibles por ciudad

### Prioridad MEDIA
5. **Mapa Imperial** — renderer isométrico con entidades del mundo
6. **Sistema de órdenes** — TRANSPORTE, DESPLAZAMIENTO, ATAQUE, ESPIONAJE
7. **Pantalla Informes** — historial de batallas y espionajes
8. **WebSocket** — tiempo real para órdenes y eventos

### Prioridad BAJA
9. **Arte ciudad** — mejorar funciones canvas 2D de edificios
10. **Sistema de experiencia** — XP por batallas, invocaciones, dioses
11. **NG+ (New Game Plus)** — mecánica de reinicio con ventajas
12. **Portales y KarlakÁ** — sistema de desbloqueo y boss final

---

## FLUJO DE TRABAJO ESTÁNDAR

```
1. Usuario reporta bug o pide feature
2. IA pide archivo actual si lo necesita
3. IA diagnostica con grep/view — nunca asume
4. IA declara: "Voy a modificar X en Y porque Z. Ancla: [texto]"
5. IA genera script .py descargable
6. Usuario corre el script y reporta salida exacta
7. Git commit si cambios importantes
```

---

## CONVENCIONES DE NOMENCLATURA

| Concepto | Variable/campo |
|---|---|
| Jugador activo | `sessionStorage.jugador` |
| Ciudad activa | `sessionStorage.ciudad_actual` |
| Tasas producción | `window._prodTasas` |
| Estado ciudad local | `window._prodCity` |
| Ticker producción | `window._prodTicker` |
| Datos click edificio | `_cityClickData` |
| Nivel sacerdote | `player.unit_levels.SACERDOTE` |
| Producción retroactiva | `LAST_PROD` (timestamp unix en city JSON) |
| Cola activa | `city.COLAS[]` |

---

## NOTAS TÉCNICAS CRÍTICAS

1. **Nivel sacerdote** = `player['unit_levels']['SACERDOTE']`, NO `city['NIVEL_DE_TROPAS']`
2. **CSVs en** `csv\` — NO en la raíz del proyecto
3. **Sprites PNG** en `frontend/assets/buildings/` — generados con Gemini, fondo negro eliminado
4. **city.js** usa Canvas 2D con funciones `artCityHall`, `artSanctuary`, etc. — NO sprites PNG para edificios principales (el sistema de sprites quedó instalado pero no activo)
5. **Retroactividad** = 3 días máximo en producción Y en colas
6. **Colas** se procesan al cargar ciudad (GET) y al hacer tick (POST)
7. **`OBRAS`** = construcciones de edificios en progreso (sistema del v2, no migrado aún)

---

## HISTORIAL DE FIXES SESIÓN ACTUAL

| Fix | Archivo | Estado |
|---|---|---|
| Sistema de producción materiales/maná | `backend/systems/production.py` | ✅ |
| Nivel sacerdote real para maná | `production.py` + `city.py` | ✅ |
| Ticker 1s frontend + sync 30s | `city.js` | ✅ |
| Selector de ciudades dropdown | `app.js` | ✅ |
| Sistema de colas cuartel/templo | `backend/systems/queues.py` | ✅ parcial (bugs 1 y 2) |
| Menú edificio con click en canvas | `building_menu.js` + `city.js` | ✅ |
| Arte canvas 2D edificios | `city.js` funciones `art*` | ✅ (mejorable) |
| Sprites PNG Gemini integrados | `frontend/assets/buildings/` | ✅ |
| Layout muralla como contenedor | `city.js` | ✅ |
| Dualidad AlalaiA/KarlakÁ | `drawDuality()` en `city.js` | ✅ |
