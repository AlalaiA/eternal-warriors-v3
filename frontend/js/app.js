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
    const todasActivas = (r.alertas || []).filter(a => a.activa);
    const sinVer = todasActivas.filter(a => !a.vista);

    // Banner: persiste mientras haya alertas activas (aunque ya se hayan visto)
    if (todasActivas.length === 0) {
      _limpiarAmenazas();
    } else {
      const masReciente = todasActivas[todasActivas.length - 1];
      if (!document.getElementById('ew-threat-banner')) {
        _mostrarAmenazaPersistente(masReciente);
      }
    }

    // Overlay: solo para alertas no vistas
    for (const alerta of sinVer) {
      if (!_alertasMostradas.has(alerta.id)) {
        _alertasMostradas.add(alerta.id);
        _mostrarAmenazaPersistente(alerta);
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

// ── Texto parpadeante persistente de amenaza ─────────────────────────────────

function _mostrarAmenazaPersistente(alerta) {
  // Crear o actualizar el banner parpadeante en el header
  let banner = document.getElementById('ew-threat-banner');
  if (!banner) {
    banner = document.createElement('div');
    banner.id = 'ew-threat-banner';
    // Insertar en el body, fijo arriba
    document.body.appendChild(banner);
    // Añadir animación de parpadeo
    if (!document.getElementById('_threatStyle')) {
      const s = document.createElement('style');
      s.id = '_threatStyle';
      s.textContent = `
        @keyframes _threatBlink {
          0%,49% { opacity: 1; }
          50%,100% { opacity: 0.3; }
        }
        #ew-threat-banner {
          position: fixed;
          top: 40px; left: 0; right: 0;
          z-index: 9998;
          cursor: pointer;
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 12px;
          padding: 4px 16px;
          background: rgba(0,0,0,0.85);
          border-bottom: 1px solid rgba(200,50,50,0.5);
          font-family: 'Cinzel', serif;
          font-size: 11px;
          letter-spacing: 1px;
          animation: _threatBlink 1s ease-in-out infinite;
        }
      `;
      document.head.appendChild(s);
    }
  }

  const info     = alerta.info || {};
  const esAtaque = alerta.tipo_orden === 'ATAQUE';
  const color    = esAtaque ? '#ff6666' : '#ffaa44';
  const icono    = esAtaque ? '⚔' : '👁';
  const jugAtk   = info.jugador_atk || '???';

  // Calcular tiempo restante
  const _calcTiempo = () => {
    if (!alerta.t_llegada) return '';
    const s = Math.max(0, Math.floor(alerta.t_llegada - Date.now() / 1000));
    if (s <= 0) return '¡LLEGANDO!';
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sg = s % 60;
    return h > 0 ? `${h}h ${String(m).padStart(2,'0')}m`
         : m > 0 ? `${m}m ${String(sg).padStart(2,'0')}s`
         : `${sg}s`;
  };

  banner.innerHTML = `
    <span style="color:${color};">${icono}</span>
    <span style="color:${color};">${esAtaque ? 'ATAQUE' : 'ESPIONAJE'} DETECTADO</span>
    <span style="color:#aaa;">·</span>
    <span style="color:#e8d080;">${jugAtk}</span>
    ${info.x_orig != null ? `<span style="color:#aaa;">·</span><span style="color:#88aacc;">📍 (${info.x_orig}, ${info.y_orig})</span>` : ''}
    <span style="color:#aaa;">·</span>
    <span id="ew-threat-timer" style="color:${color};font-weight:bold;">${_calcTiempo()}</span>
    <span style="color:#555;font-size:10px;">[${alerta.ciudad}]</span>
    <span style="color:#666;font-size:9px;margin-left:8px;">▶ click para detalles</span>
  `;

  // Banner clickeable — abre el overlay de detalle
  banner.style.cursor = 'pointer';
  banner.style.pointerEvents = 'auto';
  banner.onclick = () => {
    if (!document.getElementById('ew-alert-overlay')) {
      _mostrarOverlay(alerta);
    }
  };

  // Actualizar timer cada segundo
  const existingIv = banner._timerIv;
  if (existingIv) clearInterval(existingIv);
  banner._timerIv = setInterval(() => {
    const el = document.getElementById('ew-threat-timer');
    if (!el) { clearInterval(banner._timerIv); return; }
    const t = _calcTiempo();
    el.textContent = t;
    if (t === '¡LLEGANDO!') el.style.color = '#ff4444';
  }, 1000);
}

function _limpiarAmenazas() {
  // Eliminar banner si no hay alertas activas
  const banner = document.getElementById('ew-threat-banner');
  if (banner) {
    if (banner._timerIv) clearInterval(banner._timerIv);
    banner.remove();
  }
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

  // Calcular tiempo restante
  let tiempoHtml = '';
  if (alerta.t_llegada) {
    const segsRest = Math.max(0, Math.floor(alerta.t_llegada - Date.now() / 1000));
    if (segsRest > 0) {
      const h = Math.floor(segsRest / 3600);
      const m = Math.floor((segsRest % 3600) / 60);
      const s = segsRest % 60;
      const tStr = h > 0
        ? `${h}h ${String(m).padStart(2,'0')}m`
        : m > 0 ? `${m}m ${String(s).padStart(2,'0')}s`
        : `${s}s`;
      tiempoHtml = `<div style="
        background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);
        border-radius:4px;padding:6px 12px;margin-bottom:12px;
        display:flex;justify-content:space-between;align-items:center;">
        <span style="font-size:11px;color:#a09060;">⏱ Llegada estimada</span>
        <span style="font-size:14px;color:#e8d080;font-family:'Cinzel',serif;" id="ew-alert-timer">${tStr}</span>
      </div>`;
    } else {
      tiempoHtml = `<div style="font-size:11px;color:#c05050;margin-bottom:8px;">⚠ Llegando ahora</div>`;
    }
  }
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

      <!-- Tiempo restante -->
      ${tiempoHtml}

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

  // Countdown en vivo
  if (alerta.t_llegada) {
    const timerEl = () => document.getElementById('ew-alert-timer');
    const iv = setInterval(() => {
      const el = timerEl();
      if (!el) { clearInterval(iv); return; }
      const segsRest = Math.max(0, Math.floor(alerta.t_llegada - Date.now() / 1000));
      if (segsRest <= 0) {
        el.textContent = '¡Llegando!';
        el.style.color = '#c05050';
        clearInterval(iv);
        return;
      }
      const h = Math.floor(segsRest / 3600);
      const m = Math.floor((segsRest % 3600) / 60);
      const s = segsRest % 60;
      el.textContent = h > 0
        ? `${h}h ${String(m).padStart(2,'0')}m`
        : m > 0 ? `${m}m ${String(s).padStart(2,'0')}s`
        : `${s}s`;
    }, 1000);
  }

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
