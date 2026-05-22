# INSTRUCCIONES DE INICIO DE SESIÓN — ETERNAL WARRIORS v3.0

## PASO 1 — LEER EL DOCUMENTO MAESTRO

El primer mensaje contendrá `EW_Maestro_v5.md`. Léelo completamente antes de responder.

---

## PASO 2 — ENTENDER EL CONTEXTO

**Eternal Warriors v3.0** es un juego de estrategia con arquitectura web:
- **Backend:** Python 3.12 + FastAPI en `E:\0000ew V2Claude\backend\`
- **Frontend:** HTML5 + Canvas 2D en `E:\0000ew V2Claude\frontend\`
- **DB:** JSONs separados por jugador en `backend\db\`
- **Arranque:** `run.bat` → `http://127.0.0.1:8000`
- **GitHub:** `https://github.com/AlalaiA/eternal-warriors-v3`

**Lo más importante:**
- El proyecto NO usa pygame. Es web (FastAPI + HTML/JS/CSS).
- Los sistemas del juego (combate, espionaje, etc.) están en `backend/systems/` — pendientes de implementar.
- Los fixes van en scripts `.py` descargables, NO en fix.bat.
- Los CSV canónicos siguen siendo la fuente de verdad para datos del juego.

---

## PASO 3 — FLUJO DE TRABAJO

```
1. Usuario reporta bug o pide feature
2. IA pide el archivo actual si lo necesita
3. IA audita el ancla exacta antes de escribir fix
4. IA genera script .py descargable
5. Usuario lo corre y reporta resultado
6. Git commit tras cambios importantes
```

---

## PASO 4 — PENDIENTES PRIORITARIOS

### 1. Layout ciudad — cy ajuste fino
**Síntoma:** El Santuario Arcano sale por arriba del canvas.
**Estado:** cy=0.63, necesita subir a ~0.66-0.68.
**Archivo:** `frontend/js/screens/city.js` — constante `cy = H*0.63`
**Fix:** Cambiar `0.63` a `0.67` y verificar que todo quede dentro.

### 2. Sprites PNG edificios
**Estado:** Los edificios son canvas 2D geométrico. El usuario quiere arte visual como el prototipo.
**Plan:** Generar SVG artístico por edificio → exportar PNG → cargar con PixiJS.
**Carpeta destino:** `frontend/assets/buildings/`

### 3. Sistemas backend
**Estado:** Todos los archivos en `systems/` están vacíos (placeholder).
**Prioridad:** `production.py` primero (aldeanos producen recursos cada hora).
**Fuente:** Migrar lógica de `data_manager.py` del v2.

### 4. Mapa Imperial
**Estado:** `map.js` muestra "próximamente".
**Plan:** PixiJS + tiles isométricos + niebla de guerra + entidades del mundo.

### 5. Tick del juego
**Estado:** No hay tick activo. Los recursos no se producen en tiempo real.
**Plan:** Loop en `game_engine.py` que corre cada N segundos y actualiza producción.

---

## PASO 5 — CÓMO PEDIR ARCHIVOS

Cuando necesites un archivo del frontend:
> "Súbeme el `city.js` actual."

Cuando necesites un archivo del backend:
> "Súbeme el `game_engine.py` actual."

**Nunca usar los archivos del proyecto `/mnt/project/` — están obsoletos.**

---

## PASO 6 — REGLAS DE ESCRITURA DE FIXES

```python
from pathlib import Path

path = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = path.read_text(encoding="utf-8")

OLD = "ancla exacta del código"
NEW = "código reemplazado"

c = src.count(OLD)
if c != 1:
    print(f"ERROR: ancla encontrada {c} veces. Abortando.")
    exit(1)

src = src.replace(OLD, NEW)
path.write_text(src, encoding="utf-8")
print("OK — descripción del cambio")
```

**Reglas:**
- Ancla OLD debe ser única (verificar con `src.count(OLD) == 1`)
- Si falla, pedir el archivo actual antes de reintentar
- Un fix = un problema
- Para JS no hay `ast.parse` — verificar manualmente si hay duda

---

## PASO 7 — ENTORNO

| Item | Valor |
|---|---|
| Python | 3.12 |
| FastAPI | 0.136.1 |
| Uvicorn | 0.47.0 |
| Sistema | Windows 10 |
| Ruta proyecto | `E:\0000ew V2Claude\` |
| Arranque | `run.bat` |
| URL local | `http://127.0.0.1:8000` |
| GitHub | `https://github.com/AlalaiA/eternal-warriors-v3` |

---

## PASO 8 — CONFIRMACIÓN DE CONTEXTO AL INICIO

Al inicio de cada sesión, la IA envía:

---
**CONFIRMACIÓN DE CONTEXTO**

**Entiendo el proyecto como:** Eternal Warriors v3.0, juego de estrategia web (FastAPI + Canvas 2D). Backend Python, frontend HTML/JS/CSS. DB en JSONs separados por jugador.

**Pendientes que veo:**
1. [pendiente 1]
2. [pendiente 2]
...

**Empezaré por:** [pendiente específico] porque [razón]

**Necesito:** [archivos o info]

---

---

## PASO 9 — LECCIONES APRENDIDAS

- **Anclas en JS cambian** — siempre verificar con `check.py` antes de escribir el fix.
- **El archivo en disco puede diferir** del que se subió — pedir siempre el actual.
- **cy controla la posición vertical** de toda la ciudad — cambios pequeños (0.01) tienen gran impacto.
- **Los imports dinámicos en JS** necesitan cache-bust (`?v=Date.now()`) para refrescar.
- **No acumular fixes no solicitados** en el mismo script.
- **Git commit frecuente** — antes de cambios grandes.
