"""
fix_city_selector.py
Eternal Warriors v3.0 — Selector de ciudades en el header

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_city_selector.py
"""

from pathlib import Path
import sys, shutil

APP_JS   = Path(r"E:\0000ew V2Claude\frontend\js\app.js")
GAME_HTML = Path(r"E:\0000ew V2Claude\frontend\game.html")

# ── FIX 1: app.js — añadir selector de ciudades ──────────────────────────────
src = APP_JS.read_text(encoding="utf-8")

OLD = """\
/* ETERNAL WARRIORS v3.0 — Orquestador frontend */

const JUGADOR = sessionStorage.getItem('jugador') || '';
const CAPITAL = sessionStorage.getItem('capital') || '';

if (!JUGADOR) window.location.href = '/';

// Header
document.getElementById('hdr-ciudad').textContent = CAPITAL || 'SIN CIUDAD';

// Cargar pantalla por defecto
window.addEventListener('DOMContentLoaded', () => {
  loadScreen('city');
  startTimer();
});"""

NEW = """\
/* ETERNAL WARRIORS v3.0 — Orquestador frontend */

const JUGADOR = sessionStorage.getItem('jugador') || '';
const CAPITAL = sessionStorage.getItem('capital') || '';

if (!JUGADOR) window.location.href = '/';

// Ciudad activa — empieza en la capital
let CIUDAD_ACTUAL = sessionStorage.getItem('ciudad_actual') || CAPITAL;

// Header
document.getElementById('hdr-ciudad').textContent = CIUDAD_ACTUAL || 'SIN CIUDAD';

// Cargar pantalla por defecto
window.addEventListener('DOMContentLoaded', async () => {
  await initCitySelector();
  loadScreen('city');
  startTimer();
});

// ── Selector de ciudades ────────────────────────────────────────────────────
async function initCitySelector() {
  try {
    const res  = await fetch(`/api/city/${JUGADOR}`);
    const data = await res.json();
    const ciudades = data.cities || [];

    const hdrCiudad = document.getElementById('hdr-ciudad');
    hdrCiudad.style.cursor = 'pointer';
    hdrCiudad.title = 'Click para cambiar de ciudad';

    // Crear dropdown
    const wrap = document.createElement('div');
    wrap.id = 'city-selector-wrap';
    wrap.style.cssText = 'position:relative;display:inline-block;';

    const btn = document.createElement('div');
    btn.id = 'hdr-ciudad-btn';
    btn.className = 'hdr-ciudad';
    btn.style.cssText = 'cursor:pointer;display:flex;align-items:center;gap:6px;';
    btn.innerHTML = `<span id="hdr-ciudad-name">${CIUDAD_ACTUAL}</span><span style="font-size:10px;opacity:0.6">▼</span>`;

    const dropdown = document.createElement('div');
    dropdown.id = 'city-dropdown';
    dropdown.style.cssText = `
      display:none;position:absolute;top:100%;left:0;
      background:rgba(8,10,20,0.97);border:1px solid rgba(201,168,76,0.3);
      border-radius:6px;min-width:180px;z-index:1000;
      box-shadow:0 8px 32px rgba(0,0,0,0.6);overflow:hidden;
    `;

    ciudades.forEach((nombre, i) => {
      const item = document.createElement('div');
      item.style.cssText = `
        padding:8px 14px;cursor:pointer;font-family:'Cinzel',serif;
        font-size:11px;letter-spacing:1px;color:#c9a84c;
        border-bottom:1px solid rgba(255,255,255,0.05);
        transition:background 0.15s;
      `;
      item.textContent = nombre;
      if (nombre === CIUDAD_ACTUAL) {
        item.style.background = 'rgba(201,168,76,0.12)';
        item.style.color = '#e8d080';
      }
      item.onmouseenter = () => item.style.background = 'rgba(201,168,76,0.08)';
      item.onmouseleave = () => {
        item.style.background = nombre === CIUDAD_ACTUAL ? 'rgba(201,168,76,0.12)' : '';
      };
      item.onclick = () => cambiarCiudad(nombre, dropdown, btn);
      dropdown.appendChild(item);
    });

    btn.onclick = (e) => {
      e.stopPropagation();
      dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
    };
    document.addEventListener('click', () => dropdown.style.display = 'none');

    wrap.appendChild(btn);
    wrap.appendChild(dropdown);

    // Reemplazar el hdr-ciudad original
    hdrCiudad.replaceWith(wrap);

  } catch(e) {
    console.error('Error cargando ciudades:', e);
  }
}

function cambiarCiudad(nombre, dropdown, btn) {
  CIUDAD_ACTUAL = nombre;
  sessionStorage.setItem('ciudad_actual', nombre);
  document.getElementById('hdr-ciudad-name').textContent = nombre;
  dropdown.style.display = 'none';
  // Actualizar highlight
  dropdown.querySelectorAll('div').forEach(item => {
    item.style.background = item.textContent === nombre ? 'rgba(201,168,76,0.12)' : '';
    item.style.color = item.textContent === nombre ? '#e8d080' : '#c9a84c';
  });
  // Recargar pantalla ciudad con la nueva ciudad
  loadScreen('city');
}"""

c = src.count(OLD)
if c != 1:
    print(f"ERROR app.js: ancla {c}x. Abortando.")
    sys.exit(1)
src = src.replace(OLD, NEW)

# También actualizar loadScreen para usar CIUDAD_ACTUAL
OLD2 = "    await mod.render(main, JUGADOR, CAPITAL);"
NEW2 = "    await mod.render(main, JUGADOR, CIUDAD_ACTUAL);"
c = src.count(OLD2)
if c != 1:
    print(f"ERROR app.js fix 2: {c}x. Abortando.")
    sys.exit(1)
src = src.replace(OLD2, NEW2)

APP_JS.write_text(src, encoding="utf-8")
print("OK fix 1: selector de ciudades en app.js")

# ── FIX 2: game.html — añadir Cinzel font para el dropdown ───────────────────
html = GAME_HTML.read_text(encoding="utf-8")
OLD_H = "<link rel=\"stylesheet\" href=\"/static/css/theme.css\">"
NEW_H = """\
<link rel="stylesheet" href="/static/css/theme.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Rajdhani:wght@400;500;600&display=swap" rel="stylesheet">"""
if OLD_H in html and 'fonts.googleapis' not in html:
    html = html.replace(OLD_H, NEW_H)
    GAME_HTML.write_text(html, encoding="utf-8")
    print("OK fix 2: fuentes Cinzel en game.html")
else:
    print("SKIP fix 2: fuentes ya presentes")

print()
print("HECHO.")
print()
print("  Ctrl+C → run.bat → Ctrl+Shift+R")
print()
print("El header mostrará el nombre de la ciudad activa.")
print("Click sobre el nombre despliega el selector con las 12 ciudades.")
print("Al seleccionar, la UI se recarga con la información de esa ciudad.")
