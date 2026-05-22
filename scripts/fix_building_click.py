"""
fix_building_click.py
Eternal Warriors v3.0 — Click en edificios abre menú de cola

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_building_click.py
"""

from pathlib import Path
import sys, shutil

BASE = Path(r"E:\0000ew V2Claude")

# ── 1. Copiar building_menu.js al frontend ────────────────────────────────────
src_menu = Path(__file__).parent / "building_menu.js"
dst_menu = BASE / "frontend" / "js" / "screens" / "building_menu.js"
shutil.copy2(src_menu, dst_menu)
print(f"OK: {dst_menu}")

# ── 2. Fix city.js — añadir click handler en el canvas ───────────────────────
CITY_JS = BASE / "frontend" / "js" / "screens" / "city.js"
src = CITY_JS.read_text(encoding="utf-8")

# Guardar jugador/ciudad/cityData/tasas como variables de módulo accesibles
OLD_DRAWCITY = """\
function drawCity(c) {
  const canvas = document.getElementById('city-canvas');
  const wrap   = document.getElementById('city-wrap');
  if (!canvas || !wrap) return;
  const W = wrap.clientWidth, H = wrap.clientHeight;
  if (W < 10 || H < 10) { setTimeout(() => drawCity(c), 50); return; }
  canvas.width = W; canvas.height = H;
  canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
  if (animFrame) cancelAnimationFrame(animFrame);
  function loop() { tick++; renderFrame(canvas, W, H, c); animFrame = requestAnimationFrame(loop); }
  loop();
}"""

NEW_DRAWCITY = """\
let _cityClickData = null;  // {buildings, jugador, ciudad, cityData, tasas}

function drawCity(c) {
  const canvas = document.getElementById('city-canvas');
  const wrap   = document.getElementById('city-wrap');
  if (!canvas || !wrap) return;
  const W = wrap.clientWidth, H = wrap.clientHeight;
  if (W < 10 || H < 10) { setTimeout(() => drawCity(c), 50); return; }
  canvas.width = W; canvas.height = H;
  canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
  if (animFrame) cancelAnimationFrame(animFrame);

  // Click handler para menú de edificio
  canvas.onclick = (e) => {
    if (!_cityClickData) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const hit = _cityClickData.buildings.find(b => {
      const dx = mx - b.x, dy = my - b.y;
      return Math.abs(dx) < 40 && dy > -120 && dy < 10;
    });
    if (hit) {
      import(`/static/js/screens/building_menu.js?v=1`).then(m => {
        m.openBuildingMenu(
          hit,
          _cityClickData.jugador,
          _cityClickData.ciudad,
          _cityClickData.cityData,
          _cityClickData.tasas
        );
      });
    }
  };

  // Cursor pointer sobre edificios
  canvas.onmousemove = (e) => {
    if (!_cityClickData) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const hit = _cityClickData.buildings.find(b => {
      const dx = mx - b.x, dy = my - b.y;
      return Math.abs(dx) < 40 && dy > -120 && dy < 10;
    });
    canvas.style.cursor = hit ? 'pointer' : 'default';
  };

  function loop() { tick++; renderFrame(canvas, W, H, c); animFrame = requestAnimationFrame(loop); }
  loop();
}"""

c = src.count(OLD_DRAWCITY)
if c != 1:
    print(f"ERROR drawCity: {c}x. Abortando.")
    sys.exit(1)
src = src.replace(OLD_DRAWCITY, NEW_DRAWCITY)
print("OK: click handler en canvas")

# Guardar buildings en _cityClickData cuando se calculan
OLD_LAYOUT = """\
  // Edificios — ordenados por Y (painter's algorithm)
  const layout = getLayout(c, cx, cy, rx, ry);
  layout.sort((a, b) => a.y - b.y);
  layout.forEach(b => drawBuilding(ctx, b));"""

NEW_LAYOUT = """\
  // Edificios — ordenados por Y (painter's algorithm)
  const layout = getLayout(c, cx, cy, rx, ry);
  layout.sort((a, b) => a.y - b.y);
  layout.forEach(b => drawBuilding(ctx, b));

  // Guardar layout para detección de click
  if (_cityClickData) _cityClickData.buildings = layout;"""

c = src.count(OLD_LAYOUT)
if c != 1:
    print(f"ERROR layout: {c}x. Abortando.")
    sys.exit(1)
src = src.replace(OLD_LAYOUT, NEW_LAYOUT)
print("OK: buildings guardados para click")

# Inicializar _cityClickData en render()
OLD_TICKER = """\
  // Ticker de producción — actualiza recursos por segundo en el DOM
  if (window._prodTicker) clearInterval(window._prodTicker);
  if (window._syncTicker) clearInterval(window._syncTicker);

  // Guardar tasas y estado actual
  window._prodTasas  = data.tasas  || {};
  window._prodCity   = data.city   || {};
  window._prodJugador = jugador;
  window._prodCapital = capital;"""

NEW_TICKER = """\
  // Ticker de producción — actualiza recursos por segundo en el DOM
  if (window._prodTicker) clearInterval(window._prodTicker);
  if (window._syncTicker) clearInterval(window._syncTicker);

  // Guardar tasas y estado actual
  window._prodTasas  = data.tasas  || {};
  window._prodCity   = data.city   || {};
  window._prodJugador = jugador;
  window._prodCapital = capital;

  // Inicializar datos para click en edificios
  _cityClickData = {
    buildings: [],
    jugador:   jugador,
    ciudad:    capital,
    cityData:  data.city || {},
    tasas:     data.tasas || {},
  };"""

c = src.count(OLD_TICKER)
if c != 1:
    print(f"ERROR ticker: {c}x. Abortando.")
    sys.exit(1)
src = src.replace(OLD_TICKER, NEW_TICKER)
print("OK: _cityClickData inicializado en render()")

CITY_JS.write_text(src, encoding="utf-8")
print()
print("HECHO.")
print()
print("  Ctrl+C → run.bat → Ctrl+Shift+R")
print("  Haz click en un Cuartel o Templo para abrir el menú de colas.")
