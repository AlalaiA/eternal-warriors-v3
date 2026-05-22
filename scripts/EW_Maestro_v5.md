# ETERNAL WARRIORS v3.0 — DOCUMENTO MAESTRO DE SESIÓN v5
**Fecha:** Mayo 2026 | **Ruta proyecto:** `E:\0000ew V2Claude\`

---

## ARQUITECTURA DEL PROYECTO

### Stack tecnológico
| Capa | Tecnología | Rol |
|---|---|---|
| **Backend** | Python 3.12 + FastAPI | Lógica del juego, CSV, combate, savegame |
| **Comunicación** | WebSocket (FastAPI) | Tiempo real — órdenes, tick, eventos |
| **Frontend** | HTML5 + Canvas 2D | Renderer isométrico, UI, animaciones |
| **Estilos** | CSS3 + variables | Tema épico oscuro |
| **DB** | JSON por jugador | Savegames separados por entidad |

### Árbol del proyecto
```
E:\0000ew V2Claude\
├── backend\
│   ├── main.py              # FastAPI — servidor principal
│   ├── ws_handler.py        # WebSocket tiempo real
│   ├── __init__.py
│   ├── engine\
│   │   ├── game_engine.py   # Motor del juego
│   │   └── __init__.py
│   ├── data\
│   │   ├── save_manager.py  # Lectura/escritura JSONs
│   │   └── __init__.py
│   ├── api\
│   │   ├── auth.py          # Login/autenticación
│   │   ├── city.py          # Endpoints ciudad
│   │   ├── map.py           # Endpoints mapa
│   │   └── __init__.py
│   ├── systems\
│   │   ├── combat.py        # Sistema de combate
│   │   ├── espionage.py     # Sistema de espionaje
│   │   ├── production.py    # Producción recursos
│   │   ├── buildings.py     # Edificios y niveles
│   │   ├── orders.py        # Órdenes en tránsito
│   │   ├── alliances.py     # Alianzas
│   │   ├── experience.py    # Experiencia y niveles
│   │   ├── fog_of_war.py    # Niebla de guerra
│   │   └── __init__.py
│   └── db\
│       ├── players\
│       │   ├── jiarito.json
│       │   ├── ginao.json
│       │   ├── joticalindo.json
│       │   ├── alalaia.json
│       │   ├── admin.json
│       │   ├── humanos\        # Un json por jugador humano nuevo
│       │   └── ia\             # Un json por jugador IA
│       ├── world\
│       │   ├── inactivos.json
│       │   ├── dioses.json
│       │   ├── cuevas.json
│       │   ├── portales.json
│       │   └── karlaka.json
│       └── global\
│           ├── core.json       # Alianzas, dioses muertos, config global
│           ├── orders.json     # Órdenes activas en tránsito
│           └── accounts.json   # Credenciales hasheadas
├── frontend\
│   ├── index.html             # Login con AlalaiA y KarlakÁ
│   ├── game.html              # Pantalla principal del juego
│   ├── css\
│   │   ├── theme.css          # Variables globales, fuentes Cinzel/Rajdhani
│   │   ├── login.css          # Pantalla login
│   │   ├── game.css           # Layout juego
│   │   └── city.css           # Vista ciudad
│   ├── js\
│   │   ├── app.js             # Orquestador — carga pantallas
│   │   └── screens\
│   │       ├── city.js        # Vista ciudad isométrica (canvas 2D animado)
│   │       ├── map.js         # Mapa imperial (pendiente)
│   │       ├── army.js        # Ejército (pendiente)
│   │       ├── invocations.js # Invocaciones (pendiente)
│   │       ├── reports.js     # Informes (pendiente)
│   │       └── settings.js    # Ajustes (pendiente)
│   └── assets\
│       ├── ui\
│       │   ├── alalaia_portrait.jpg   # Imagen AlalaiA
│       │   └── karlaka_portrait.png   # Imagen KarlakÁ
│       ├── buildings\         # PNGs edificios (pendiente)
│       ├── tiles\             # Tiles isométricos (pendiente)
│       └── entities\          # Sprites entidades mapa (pendiente)
├── scripts\                   # Scripts de utilidad
├── run.bat                    # Arranca: python -m uvicorn backend.main:app --reload --port 8000
└── .gitignore
```

### GitHub
- Repo: `https://github.com/AlalaiA/eternal-warriors-v3`
- Branch: `main`
- Commits aplicados: base inicial + .gitignore

---

## CÓMO ARRANCAR EL PROYECTO

```
cd E:\0000ew V2Claude
run.bat
```
Abre `http://127.0.0.1:8000` en el navegador.
Swagger disponible en `http://127.0.0.1:8000/docs`.

---

## ESTRUCTURA DE SAVEGAMES v3

### Formato jugador (ej. joticalindo.json)
```json
{
  "player": "JOTICALINDO",
  "unit_levels": {"MAGO": 2, "SACERDOTE": 5},
  "experiencia": 0,
  "ng_plus": 0,
  "dioses_abatidos": [],
  "batallas_ganadas": 0,
  "batallas_perdidas": 0,
  "cuevas_derrotadas": 0,
  "misiones_espionaje": 0,
  "cities": [...]
}
```

### Niveles de tropas preservados
| Jugador | Niveles |
|---|---|
| JIARITO | Todos Nv.40 |
| GINAO | Todos Nv.40 |
| JOTICALINDO | MAGO Nv.2, SACERDOTE Nv.5, resto Nv.1 |

---

## ESTADO ACTUAL DE LA UI

### Login (index.html) ✅
- AlalaiA (izq) y KarlakÁ (der) con sus imágenes reales
- Fuentes Cinzel Decorative / Rajdhani
- Autenticación via `/api/auth/login`

### Ciudad (city.js) ✅ — En progreso
- Canvas 2D animado a 60fps
- 14 edificios isométricos artísticos con animaciones
- Muralla perimetral con torres en esquinas
- Luna, estrellas parpadeantes, partículas de maná
- Formato de números hasta 1e51 (K/M/B/T/Q/Qi/Sx/Sp/Oc/No/Dc...)
- **Pendiente:** ajuste fino del layout compacto (cy en ajuste)
- **Pendiente:** sprites PNG para edificios

### Pendientes de UI
- Mapa Imperial con niebla de guerra
- Pantalla Ejército
- Pantalla Invocaciones
- Informes de combate/espionaje
- Bandeja de entrada

---

## CSV CANÓNICOS (sin cambios)
Los mismos del v2 — están en `/mnt/project/` como referencia.
El backend v3 los lee via `csv_loader.py` (pendiente de implementar).

---

## JUGADORES Y ALIANZAS

| Jugador | Tipo | Archivo JSON |
|---|---|---|
| JIARITO | JIARITO | `players/jiarito.json` — 12+3 ciudades Nv.40 |
| GINAO | HUMANO | `players/ginao.json` — 12 ciudades Nv.40 |
| JOTICALINDO | HUMANO | `players/joticalindo.json` — 12 ciudades |
| ALALAIA | VITAMINIZADA | `players/alalaia.json` |
| ADMIN | ADMIN | `players/admin.json` |
| IA001-IA006 | JUGADORESIA | `players/ia/ia00X.json` |
| REN1-REN10 + Inactivos | INACTIVOS | `world/inactivos.json` |

**Alianzas activas:** JIARITO ↔ GINAO únicamente.

---

## SISTEMAS DEL JUEGO (pendientes de implementar en v3)

Cada sistema va en su propio archivo en `backend/systems/`:

| Sistema | Archivo | Estado |
|---|---|---|
| Combate | `combat.py` | Pendiente — migrar de data_manager.py v2 |
| Espionaje | `espionage.py` | Pendiente |
| Producción recursos | `production.py` | Pendiente |
| Edificios/construcción | `buildings.py` | Pendiente |
| Órdenes (ATAQUE/ESPIONAJE/etc) | `orders.py` | Pendiente |
| Alianzas | `alliances.py` | Pendiente |
| Experiencia | `experience.py` | Pendiente |
| Niebla de guerra | `fog_of_war.py` | Pendiente |

---

## REGLAS DE TRABAJO

1. **Un problema a la vez** — diagnosticar completamente, luego un solo fix.
2. **Auditar ancla exacta** antes de escribir cualquier fix — nunca asumir.
3. **Los CSV son canónicos** — no inventar valores.
4. **No especular** — si falta información, parar y pedirla.
5. **Fixes van en scripts `.py`** descargables y ejecutables.
6. **Git commit** después de cada bloque de cambios importantes.
7. **Pedir archivos actuales** antes de tocar código — el disco puede diferir.

---

## PENDIENTES PRIORITARIOS

1. **Ajuste fino layout ciudad** — cy actual ~0.63, santuario sale por arriba
2. **Sprites PNG edificios** — para reemplazar canvas 2D por imágenes artísticas
3. **Implementar sistemas backend** — combat.py, espionage.py, etc.
4. **Mapa Imperial** — renderer isométrico con niebla de guerra
5. **Tick del juego** — producción de recursos, órdenes en tránsito
6. **WebSocket** — comunicación tiempo real frontend ↔ backend

---

## GLOSARIO (sin cambios respecto a v4)
Ver versión anterior para glosario completo de tipos de ciudad, unidades, combate, espionaje y recursos.
