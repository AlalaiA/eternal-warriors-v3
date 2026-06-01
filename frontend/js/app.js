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

// ── Listener: ir a Ejército desde el mapa ───────────────────────────────────
window.addEventListener('ew:irAEjercito', () => {
  loadScreen('army');
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
}

let _currentMod = null;

async function loadScreen(screen) {
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  const navMap = {city:'city',army:'army',invocations:'inv',map:'map',reports:'rep',alliance:'ali',settings:'set'};
  const btn = document.getElementById('nav-' + (navMap[screen]||'city'));
  if (btn) btn.classList.add('active');

  // Limpiar módulo anterior antes de cargar el nuevo
  if (_currentMod && typeof _currentMod.cleanup === 'function') {
    try { _currentMod.cleanup(); } catch(_) {}
  }
  _currentMod = null;

  const main = document.getElementById('main-content');
  main.innerHTML = '<div class="screen-loading"><span>Cargando...</span></div>';

  try {
    // Cache-bust solo en city para forzar limpieza de estado
    const bust = screen === 'city' ? `?v=${Date.now()}` : '';
    const mod = await import(`/static/js/screens/${screen}.js${bust}`);
    _currentMod = mod;
    await mod.render(main, JUGADOR, CIUDAD_ACTUAL);
  } catch(e) {
    console.error('Error cargando pantalla:', screen, e);
    main.innerHTML = `<div class="screen-loading"><span>Error: ${e.message}</span></div>`;
  }
}

function startTimer() {
  // Timer placeholder — se conectará al backend
  const el = document.getElementById('hdr-timer');
  let t = 2 * 24 * 3600 + 11 * 3600 + 47 * 60;
  setInterval(() => {
    t = Math.max(0, t - 1);
    const d = Math.floor(t / 86400);
    const h = Math.floor((t % 86400) / 3600);
    const m = Math.floor((t % 3600) / 60);
    el.textContent = `${d}d ${String(h).padStart(2,'0')}h ${String(m).padStart(2,'0')}m`;
  }, 1000);
}
