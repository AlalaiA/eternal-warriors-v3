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
});

async function loadScreen(screen) {
  // Actualizar nav
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById('nav-' + (screen === 'city' ? 'city' :
              screen === 'army' ? 'army' : screen === 'invocations' ? 'inv' :
              screen === 'map' ? 'map' : screen === 'reports' ? 'rep' : 'set'));
  if (btn) btn.classList.add('active');

  const main = document.getElementById('main-content');
  main.innerHTML = '<div class="screen-loading"><span>Cargando...</span></div>';

  try {
    const mod = await import(`/static/js/screens/${screen}.js`);
    await mod.render(main, JUGADOR, CAPITAL);
  } catch(e) {
    main.innerHTML = `<div class="screen-loading"><span>Pantalla en construcción: ${screen}</span></div>`;
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
