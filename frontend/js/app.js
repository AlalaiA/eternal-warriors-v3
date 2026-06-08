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


// ── Sistema de alertas de Torre de Vigilancia ─────────────────────────────────

const _LABELS_UNIDAD = {
  ALDEANO:'Aldeano', EXPLORADOR:'Explorador', SACERDOTE:'Sacerdote',
  GUERRERO:'Guerrero', COMANDO:'Comando', MERCENARIO:'Mercenario',
  MARINE:'Marine', CYBORG:'Cyborg', MAGO:'Mago', METAHUMANO:'Metahumano',
  DEMONIO:'Demonio', ANIMA:'Ánima', ESPECTRO:'Espectro', GOLEM:'Gólem',
  CENTAURO:'Centauro', KRAKEN:'Kraken', ALONARDO:'Alonardo',
  MADRESELVA:'Madreselva', COLOSO:'Coloso', FENIX:'Fénix',
  DRAGON_DE_ORO:'Dragón de Oro', CABALLERO_DE_LUZ:'Cab. de Luz',
  ALALAIA:'AlalaiA', EON_SUPREMO:'Éon Supremo',
};
const _lbl = k => _LABELS_UNIDAD[k?.toUpperCase()] ?? k ?? '?';

function _fmtNum(n) {
  n = Number(n);
  if (!isFinite(n)) return '∞';
  if (n >= 1e12) return (n/1e12).toFixed(1)+'T';
  if (n >= 1e9)  return (n/1e9).toFixed(1)+'G';
  if (n >= 1e6)  return (n/1e6).toFixed(1)+'M';
  if (n >= 1e3)  return (n/1e3).toFixed(1)+'K';
  return Math.floor(n).toLocaleString('es');
}

// Alertas ya mostradas en esta sesión para no re-mostrar el overlay
const _alertasMostradas = new Set();

// Poller de alertas — arranca con el juego
let _alertPoller = null;

function startAlertPoller() {
  if (_alertPoller) clearInterval(_alertPoller);
  _alertPoller = setInterval(_checkAlertas, 5000);
}

async function _checkAlertas() {
  if (!JUGADOR) return;
  try {
    const r = await fetch(`/api/alerts/${JUGADOR}`).then(r => r.json());
    const alertas = (r.alertas || []).filter(a => a.activa && !a.vista);
    for (const alerta of alertas) {
      if (!_alertasMostradas.has(alerta.id)) {
        _alertasMostradas.add(alerta.id);
        _mostrarOverlay(alerta);
        // Marcar como vista en backend para no repetir en próximos polls
        fetch('/api/alerts/dismiss', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({jugador: JUGADOR, alerta_id: alerta.id})
        });
      }
    }
  } catch {}
}

function _mostrarOverlay(alerta) {
  // Eliminar overlay previo si existe
  document.getElementById('ew-alert-overlay')?.remove();

  const info     = alerta.info || {};
  const nivel    = alerta.nivel || 1;
  const esAtaque = alerta.tipo_orden === 'ATAQUE';
  const color    = esAtaque ? '#c05050' : '#c9a84c';
  const icono    = esAtaque ? '⚔' : '👁';
  const titulo   = esAtaque ? 'EJÉRCITO ENEMIGO DETECTADO' : 'INCURSIÓN DETECTADA';

  // Construir detalle según nivel
  let detalleHtml = '';

  if (nivel >= 1 && info.x_orig != null) {
    detalleHtml += `<div style="margin-bottom:6px;font-size:12px;color:#aabbcc;">
      📍 Origen: (${info.x_orig}, ${info.y_orig})
    </div>`;
  }
  if (nivel >= 2 && info.jugador_atk) {
    detalleHtml += `<div style="margin-bottom:6px;font-size:13px;color:#e8d080;
      font-family:'Cinzel',serif;letter-spacing:1px;">
      ⚔ ${info.jugador_atk}
    </div>`;
  }
  if (nivel >= 3 && info.tipo_orden) {
    const tipoLabel = info.tipo_orden === 'ATAQUE' ? 'ATAQUE' : 'ESPIONAJE';
    detalleHtml += `<div style="margin-bottom:6px;font-size:11px;">
      Tipo: <span style="color:${color};font-family:'Cinzel',serif;">${tipoLabel}</span>
    </div>`;
  }
  if (nivel >= 4 && info.tipos_unidades?.length) {
    detalleHtml += `<div style="margin-bottom:6px;font-size:11px;color:#aabbcc;">
      Unidades: ${info.tipos_unidades.map(_lbl).join(', ')}
    </div>`;
  }
  if (nivel >= 5) {
    // Propias del atacante
    const propias = info.unidades || {};
    const prestadas = info.unidades_prestadas || {};
    const nv = info.nivel_tropas || 1;
    let unidadesHtml = '';

    const entradasPropias = Object.entries(propias).filter(([,n])=>Number(n)>0);
    if (entradasPropias.length) {
      unidadesHtml += `<div style="font-size:10px;color:#667;margin-bottom:3px;
        font-family:'Cinzel',serif;letter-spacing:1px;">
        ${info.jugador_atk || 'ATACANTE'} · nv${nv}
      </div>`;
      unidadesHtml += entradasPropias.map(([u,n]) =>
        `<div style="display:flex;justify-content:space-between;padding:2px 0;font-size:12px;">
          <span>${_lbl(u)}</span>
          <span style="color:#e8d080;">${_fmtNum(n)}</span>
        </div>`
      ).join('');
    }
    // Tropas prestadas con sus dueños
    for (const [dueño, unids] of Object.entries(prestadas)) {
      const entradasPrest = Object.entries(unids).filter(([,n])=>Number(n)>0);
      if (!entradasPrest.length) continue;
      unidadesHtml += `<div style="font-size:10px;color:#667;margin-top:6px;margin-bottom:3px;
        font-family:'Cinzel',serif;letter-spacing:1px;">🤝 ${dueño}</div>`;
      unidadesHtml += entradasPrest.map(([u,n]) =>
        `<div style="display:flex;justify-content:space-between;padding:2px 0;font-size:12px;">
          <span>${_lbl(u)}</span>
          <span style="color:#e8d080;">${_fmtNum(n)}</span>
        </div>`
      ).join('');
    }
    if (unidadesHtml) {
      detalleHtml += `<div style="
        background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.08);
        border-radius:4px;padding:10px 12px;margin-top:8px;
      ">${unidadesHtml}</div>`;
    }
  }

  const overlay = document.createElement('div');
  overlay.id = 'ew-alert-overlay';
  overlay.style.cssText = `
    position:fixed;top:0;left:0;width:100%;height:100%;
    background:rgba(0,0,0,0.72);z-index:99999;
    display:flex;align-items:center;justify-content:center;
    animation:_overlayIn 0.3s ease;
  `;
  if (!document.getElementById('_overlayStyle')) {
    const s = document.createElement('style');
    s.id = '_overlayStyle';
    s.textContent = `
      @keyframes _overlayIn {
        from { opacity:0; }
        to   { opacity:1; }
      }
      @keyframes _pulseAlert {
        0%,100% { box-shadow: 0 0 0 0 ${color}44; }
        50%      { box-shadow: 0 0 32px 8px ${color}33; }
      }
    `;
    document.head.appendChild(s);
  }

  overlay.innerHTML = `
    <div style="
      background:rgba(6,8,16,0.97);
      border:1px solid ${color}66;border-top:3px solid ${color};
      border-radius:8px;padding:28px 32px;max-width:420px;width:90%;
      animation:_pulseAlert 2s ease-in-out infinite;
      font-family:'Rajdhani',sans-serif;color:#c8b88a;
    ">
      <!-- Header -->
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
        <span style="font-size:28px;">${icono}</span>
        <div>
          <div style="font-family:'Cinzel',serif;font-size:13px;color:${color};
            letter-spacing:3px;">${titulo}</div>
          <div style="font-size:10px;color:#556;letter-spacing:1px;margin-top:2px;">
            Torre de Vigilancia · ${alerta.ciudad} · Nivel ${nivel}
          </div>
        </div>
      </div>

      <div style="height:1px;background:${color}33;margin:14px 0;"></div>

      <!-- Detalle -->
      <div style="margin-bottom:16px;">${detalleHtml || '<div style="color:#556;font-size:12px;">Señal detectada — información insuficiente</div>'}</div>

      <!-- Botones -->
      <div style="display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap;">
        <button onclick="_alertaVerInformes()" style="
          background:transparent;border:1px solid ${color}55;color:${color};
          font-family:'Cinzel',serif;font-size:10px;letter-spacing:1px;
          padding:7px 16px;border-radius:3px;cursor:pointer;transition:background 0.15s;"
          onmouseover="this.style.background='${color}22'"
          onmouseout="this.style.background='transparent'">
          📋 Ver informes
        </button>
        <button onclick="document.getElementById('ew-alert-overlay').remove()" style="
          background:transparent;border:1px solid #33445566;color:#667788;
          font-family:'Cinzel',serif;font-size:10px;letter-spacing:1px;
          padding:7px 16px;border-radius:3px;cursor:pointer;transition:background 0.15s;"
          onmouseover="this.style.background='rgba(255,255,255,0.04)'"
          onmouseout="this.style.background='transparent'">
          Cerrar
        </button>
      </div>
    </div>`;

  document.body.appendChild(overlay);

  // Click fuera cierra
  overlay.addEventListener('click', e => {
    if (e.target === overlay) overlay.remove();
  });
}

window._alertaVerInformes = function() {
  document.getElementById('ew-alert-overlay')?.remove();
  loadScreen('reports');
};

// Arrancar poller cuando carga el DOM
window.addEventListener('DOMContentLoaded', () => {
  startAlertPoller();
});
