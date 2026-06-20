/**
 * ETERNAL WARRIORS v3.0 — army.js
 * Pantalla de Ejército: ver tropas, lanzar órdenes, seguir misiones en curso.
 */
'use strict';

let _jugador = '', _ciudad = '', _cityData = null;
let _ordenes = [];
let _syncTimer = null, _ordTimer = null;

// ── Formato ───────────────────────────────────────────────────────────────────

function _fmt(n) {
  if (n == null) return '—';
  n = Number(n); if (!isFinite(n) || isNaN(n)) return n === Infinity ? '∞' : '—';
  const a = Math.abs(n), s = n < 0 ? '-' : '';
  if (a >= 1e18) return s + (a / 1e18).toFixed(1) + 'Qn';
  if (a >= 1e15) return s + (a / 1e15).toFixed(1) + 'Pd';
  if (a >= 1e12) return s + (a / 1e12).toFixed(1) + 'T';
  if (a >= 1e9)  return s + (a / 1e9).toFixed(1)  + 'B';
  if (a >= 1e6)  return s + (a / 1e6).toFixed(1)  + 'M';
  if (a >= 1e3)  return s + (a / 1e3).toFixed(1)  + 'K';
  return s + Math.round(a).toLocaleString('es');
}

function _fmtTime(seg) {
  seg = Math.max(0, Math.floor(seg));
  if (seg <= 0) return '✅ Llegando…';
  const d = Math.floor(seg / 86400), h = Math.floor((seg % 86400) / 3600),
        m = Math.floor((seg % 3600) / 60), s = seg % 60;
  if (d > 0) return `${d}d ${h}h ${m}m`;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

// ── Datos ─────────────────────────────────────────────────────────────────────

const ARMY = [
  ['Aldeano',      'ALDEANO'],
  ['Explorador',   'EXPLORADOR'],
  ['Sacerdote',    'SACERDOTE'],
  ['Guerrero',     'GUERRERO'],
  ['Comando',      'COMANDO'],
  ['Mercenario',   'MERCENARIO'],
  ['Marine',       'MARINE'],
  ['Cyborg',       'CYBORG'],
  ['Mago',         'MAGO'],
  ['Metahumano',   'METAHUMANO'],
];

const INV = [
  ['Demonio',          'DEMONIO'],
  ['Ánima',            'ANIMA'],
  ['Espectro',         'ESPECTRO'],
  ['Gólem',            'GOLEM'],
  ['Centauro',         'CENTAURO'],
  ['Kraken',           'KRAKEN'],
  ['Alonardo',         'ALONARDO'],
  ['Madreselva',       'MADRESELVA'],
  ['Coloso',           'COLOSO'],
  ['Fénix',            'FENIX'],
  ['Dragón de Oro',    'DRAGON_DE_ORO'],
  ['Cab. de Luz',      'CABALLERO_DE_LUZ'],
  ['AlalaiA',          'ALALAIA'],
  ['Éon Supremo',      'EON_SUPREMO'],
];

const CUEVAS = [
  ['Behemot',      'BEHEMOT'],
  ['Chupacabras',  'CHUPACABRAS'],
  ['Dragón (C)',   'DRAGON'],
  ['Leviatán',     'LEVIATAN'],
  ['Patotas',      'PATOTAS'],
  ['Simurgh',      'SIMURGH'],
];

const TIPO_ICONS = {
  ATAQUE:          '⚔️',
  ESPIONAJE:       '🕵️',
  DESPLAZAMIENTO:  '🚶',
  TRANSPORTE:      '📦',
  FUNDAR:          '🏗️',
};

const ESTADO_COLORS = {
  EN_VIAJE:    '#c9a84c',
  REGRESANDO:  '#6ba3e0',
  COMPLETADA:  '#4caf50',
};

// ── Estilos compartidos ───────────────────────────────────────────────────────

const CSS_PANEL = `
  background:rgba(8,10,20,0.85);border:1px solid rgba(201,168,76,0.25);
  border-radius:8px;padding:16px;margin-bottom:12px;
`;
const CSS_TITLE = `
  color:#c9a84c;font-family:'Cinzel',serif;font-size:12px;
  letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;
  border-bottom:1px solid rgba(201,168,76,0.2);padding-bottom:6px;
`;
const CSS_ROW = `
  display:flex;justify-content:space-between;align-items:center;
  padding:3px 0;font-size:12px;font-family:'Cinzel',serif;
  border-bottom:1px solid rgba(255,255,255,0.04);
`;
const CSS_INPUT = `
  background:#0d0d1a;border:1px solid rgba(201,168,76,0.4);
  color:#e8e0d0;padding:5px 8px;border-radius:4px;
  font-family:'Cinzel',serif;font-size:11px;width:100%;box-sizing:border-box;
`;
const CSS_BTN = (col='#1a2a58') => `
  background:${col};border:1px solid rgba(201,168,76,0.5);color:#e8e0d0;
  padding:7px 16px;border-radius:5px;cursor:pointer;font-family:'Cinzel',serif;
  font-size:11px;letter-spacing:1px;transition:background 0.2s;
`;
const CSS_BTN_DANGER = `
  background:#2a0a0a;border:1px solid rgba(200,50,50,0.5);color:#e88080;
  padding:4px 10px;border-radius:4px;cursor:pointer;font-family:'Cinzel',serif;
  font-size:10px;letter-spacing:1px;
`;

// ── Estado del selector de unidades ──────────────────────────────────────────

let _seleccion = {};   // {JUGADOR: {KEY: cantidad}} unidades seleccionadas para la orden

function _resetSeleccion() { _seleccion = {}; }

function _selGet(jug, key) { return (_seleccion[jug] || {})[key] || 0; }
function _selSet(jug, key, val, max) {
  if (!_seleccion[jug]) _seleccion[jug] = {};
  _seleccion[jug][key] = Math.max(0, Math.min(max, Math.floor(Number(val)) || 0));
  if (_seleccion[jug][key] === 0) delete _seleccion[jug][key];
  if (Object.keys(_seleccion[jug]).length === 0) delete _seleccion[jug];
}
function _selTotal() {
  return Object.values(_seleccion).reduce((s, d) =>
    s + Object.values(d).reduce((a, v) => a + (v||0), 0), 0);
}

// ── Listener de coordenadas desde el mapa ─────────────────────────────────────

let _coordListener = null;

function _setupMapListener() {
  _coordListener = (ev) => {
    const { x, y } = ev.detail;
    _formState.x = String(x);
    _formState.y = String(y);
    const xEl = document.getElementById('orden-x');
    const yEl = document.getElementById('orden-y');
    if (xEl) { xEl.value = x; xEl.style.borderColor = '#c9a84c'; setTimeout(() => { xEl.style.borderColor = ''; }, 1500); }
    if (yEl) { yEl.value = y; yEl.style.borderColor = '#c9a84c'; setTimeout(() => { yEl.style.borderColor = ''; }, 1500); }
    // Estimar solo si _cityData está disponible
    if (_cityData && window._armyEstimar) {
      window._armyEstimar();
    } else {
      // Reintentar cuando esté listo
      const retry = setInterval(() => {
        if (_cityData && window._armyEstimar) {
          window._armyEstimar();
          clearInterval(retry);
        }
      }, 100);
      setTimeout(() => clearInterval(retry), 3000);
    }
  };
  window.addEventListener('ew:coordsSeleccionadas', _coordListener);
}

// ── Render principal ──────────────────────────────────────────────────────────


// Parsear valor de recurso incluyendo __INF__
function _parseRecurso(v) {
  if (v === '__INF__' || v === Infinity) return Infinity;
  const n = parseFloat(v);
  return isNaN(n) ? 0 : n;
}

export async function render(container, jugador, ciudad) {
  _jugador = jugador;
  _ciudad  = ciudad;
  _resetSeleccion();

  container.innerHTML = `
    <div style="display:flex;gap:12px;height:100%;padding:12px;box-sizing:border-box;overflow:hidden;">
      <div id="army-left"  style="flex:0 0 380px;overflow-y:auto;"></div>
      <div id="army-center" style="flex:1;min-width:0;overflow-y:auto;"></div>
      <div id="army-right" style="flex:0 0 280px;overflow-y:auto;"></div>
    </div>`;

  // Guardar coords del mapa para aplicar después de cargar datos
  const _mapX  = sessionStorage.getItem('map_orden_x');
  const _mapY  = sessionStorage.getItem('map_orden_y');
  const _mapT  = sessionStorage.getItem('map_orden_tipo');
  const _mapJ  = sessionStorage.getItem('map_orden_jug_dest');
  const _mapC  = sessionStorage.getItem('map_orden_ciudad_dest');
  if (_mapX && _mapY) {
    ['map_orden_x','map_orden_y','map_orden_tipo','map_orden_jug_dest','map_orden_ciudad_dest']
      .forEach(k => sessionStorage.removeItem(k));
  }

  // Cargar datos primero, luego prellenar formulario
  await _loadAndRender();

  if (_mapX && _mapY) {
    // _cityData ya está listo — prellenar y estimar
    _formState.x       = _mapX;
    _formState.y       = _mapY;
    _formState.tipo    = _mapT || _formState.tipo;
    _formState.jugDest = _mapJ || '';
    _formState.ciudDest= _mapC || '';
    // El formulario ya existe (lo creó _loadAndRender) — restaurar y estimar
    _restaurarForm();
    setTimeout(() => window._armyEstimar?.(), 50);
  }

  _setupMapListener();

  // Sync cada 15s
  _syncTimer = setInterval(_loadAndRender, 15000);

  // Tick de contadores de tiempo cada segundo
  _ordTimer = setInterval(_tickOrdenes, 1000);
}

async function _loadAndRender() {
  try {
    const [r1, r2] = await Promise.all([
      fetch(`/api/city/${_jugador}/${_ciudad}`),
      fetch(`/api/orders/${_jugador}`),
    ]);
    const d1 = await r1.json();
    const d2 = await r2.json();
    _cityData = d1.city || d1;
    _ordenes  = (d2.ordenes || []).filter(o => o.estado !== 'COMPLETADA');
  } catch (e) {
    console.error('army.js _loadAndRender:', e);
    return;
  }
  _renderLeft();
  _renderCenter();
  _renderRight();
}

// ── Panel izquierdo: tropas disponibles ───────────────────────────────────────

function _renderLeft() {
  const el = document.getElementById('army-left');
  if (!el || !_cityData) return;

  // Grid fijo: nombre | cantidad | − | input | + | MAX
  const CSS_GRID_ROW = `
    display:grid;
    grid-template-columns:110px 64px 26px 72px 26px 36px;
    align-items:center;gap:4px;
    padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.04);
  `;
  const CSS_BTN_SM  = `background:#0d1528;border:1px solid rgba(201,168,76,0.3);color:#c9a84c;
    padding:0;width:26px;height:24px;border-radius:3px;cursor:pointer;
    font-size:14px;font-family:monospace;line-height:1;`;
  const CSS_BTN_MAX = `background:#0d2010;border:1px solid rgba(80,180,80,0.3);color:#80c080;
    padding:0 4px;height:24px;border-radius:3px;cursor:pointer;
    font-size:9px;font-family:'Cinzel',serif;letter-spacing:0.5px;`;
  const CSS_INP_SM  = `background:#080c18;border:1px solid rgba(201,168,76,0.25);
    color:#e8e0d0;padding:2px 4px;border-radius:3px;
    font-family:'Cinzel',serif;font-size:11px;width:100%;box-sizing:border-box;text-align:right;`;

  const makeRow = (lbl, key, color, cnt, jug) => {
    const sel = _selGet(jug, key);
    const idPfx = `sel-${jug}-${key}`;
    return `
      <div style="${CSS_GRID_ROW}">
        <span style="color:${color};font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${lbl}</span>
        <span style="color:#888;font-size:11px;text-align:right;padding-right:4px">${_fmt(cnt)}</span>
        <button onclick="window._armyAdj('${jug}','${key}',-1)" style="${CSS_BTN_SM}">−</button>
        <input id="${idPfx}" type="number" min="0" max="${cnt}" value="${sel}"
          style="${CSS_INP_SM}"
          onchange="window._armySet('${jug}','${key}',this.value,${cnt})">
        <button onclick="window._armyAdj('${jug}','${key}',1)" style="${CSS_BTN_SM}">+</button>
        <button onclick="window._armyAll('${jug}','${key}',${cnt})" style="${CSS_BTN_MAX}">MAX</button>
      </div>`;
  };

  // ── Sacerdotes reservados por colas de templo activas ────────────────────
  const _INV_CANT_MIN = {
    DEMONIO:5000, ANIMA:7500, ESPECTRO:12000, GOLEM:18000, CENTAURO:20000,
    KRAKEN:25000, ALONARDO:35000, MADRESELVA:45000, COLOSO:125000, FENIX:250000,
    DRAGON_DE_ORO:350000, CABALLERO_DE_LUZ:1000000, ALALAIA:2000000, EON_SUPREMO:150000000,
  };
  let _sacReservados = 0;
  for (const cola of (_cityData.COLAS || [])) {
    const tipo  = (cola.tipo || '').toUpperCase();
    const unid  = (cola.unidad || '').toUpperCase();
    const hecha = Number(cola.cantidad_hecha || 0);
    const total = Number(cola.cantidad_total || 0);
    if (tipo.startsWith('TEMPLO') && hecha < total) {
      _sacReservados += (_INV_CANT_MIN[unid] || 0);
    }
  }

  // ── Tropas propias ─────────────────────────────────────────────────────────
  const armyRows = ARMY.map(([lbl, key]) => {
    let cnt = Math.floor(_parseRecurso(_cityData[key]) || 0);
    let reservado = 0;
    if (key === 'SACERDOTE' && _sacReservados > 0) {
      reservado = Math.min(_sacReservados, cnt);
      cnt = Math.max(0, cnt - reservado);
    }
    if (cnt <= 0 && reservado <= 0) return '';
    const sel = _selGet(_jugador, key);
    const idPfx = `sel-${_jugador}-${key}`;
    const cntLabel = reservado > 0
      ? `<span style="color:#888;font-size:11px;text-align:right;padding-right:4px" title="${_fmt(reservado)} reservados para invocación">
           ${_fmt(cnt)} <span style="color:#e05050;font-size:9px">🔒</span>
         </span>`
      : `<span style="color:#888;font-size:11px;text-align:right;padding-right:4px">${_fmt(cnt)}</span>`;
    return `
      <div style="${CSS_GRID_ROW}">
        <span style="color:#b0a080;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${lbl}</span>
        ${cntLabel}
        <button onclick="window._armyAdj('${_jugador}','${key}',-1)" style="${CSS_BTN_SM}">−</button>
        <input id="${idPfx}" type="number" min="0" max="${cnt}" value="${sel}"
          style="${CSS_INP_SM}"
          onchange="window._armySet('${_jugador}','${key}',this.value,${cnt})">
        <button onclick="window._armyAdj('${_jugador}','${key}',1)" style="${CSS_BTN_SM}">+</button>
        <button onclick="window._armyAll('${_jugador}','${key}',${cnt})" style="${CSS_BTN_MAX}">MAX</button>
      </div>`;
  }).join('');

  const invRows = INV.map(([lbl, key]) => {
    const cnt = _cityData[key] || 0;
    if (cnt <= 0) return '';
    return makeRow(lbl, key, '#a080c0', cnt, _jugador);
  }).join('');

  // Criaturas de cueva capturadas
  const cuevaRows = CUEVAS.map(([lbl, key]) => {
    const cnt = Math.floor(_parseRecurso(_cityData[key]) || 0);
    if (cnt <= 0) return '';
    return makeRow(lbl, key, '#e08840', cnt, _jugador);
  }).join('');

  const hayArmy  = ARMY.some(([,k]) => (_cityData[k]||0) > 0);
  const hayInv   = INV.some(([,k])  => (_cityData[k]||0) > 0);
  const hayCueva = CUEVAS.some(([,k]) => Math.floor(_parseRecurso(_cityData[k])||0) > 0);

  // ── Tropas aliadas prestadas ───────────────────────────────────────────────
  const prestadas = _cityData.TROPAS_PRESTADAS || [];
  // Agrupar por jugador
  const porJugador = {};
  for (const p of prestadas) {
    if (!porJugador[p.jugador]) porJugador[p.jugador] = [];
    porJugador[p.jugador].push(p);
  }

  let aliadosHtml = '';
  for (const [jug, entradas] of Object.entries(porJugador)) {
    const rows = entradas.map(p => {
      // Clave compuesta para distinguir múltiples entradas del mismo jugador+unidad
      const compKey  = p.ciudad_origen ? `${p.unidad}|${p.ciudad_origen}` : p.unidad;
      const lblArmy  = ARMY.find(([,k]) => k === p.unidad);
      const lblInv   = INV.find(([,k])  => k === p.unidad);
      const lblCueva = CUEVAS.find(([,k]) => k === p.unidad);
      const lbl      = (lblArmy?.[0] || lblInv?.[0] || lblCueva?.[0] || p.unidad)
                     + (p.ciudad_origen ? ` (${p.ciudad_origen})` : '');
      const color    = lblCueva ? '#e08840' : lblInv ? '#a080c0' : '#7099bb';
      return makeRow(lbl, compKey, color, p.cantidad, jug);
    }).join('');

    aliadosHtml += `
      <div style="margin-top:12px;">
        <div style="${CSS_TITLE} color:#7099bb;">🤝 ${jug}</div>
        ${rows}
      </div>`;
  }

  const totalSel = _selTotal();

  el.innerHTML = `
    <div style="${CSS_PANEL}">
      <div style="${CSS_TITLE}">⚔ Ejército — ${_ciudad}</div>
      ${hayArmy ? armyRows : '<div style="color:#666;font-size:11px">Sin tropas básicas</div>'}
      ${hayInv   ? `<div style="${CSS_TITLE} margin-top:10px;">✨ Invocaciones</div>${invRows}` : ''}
      ${hayCueva ? `<div style="${CSS_TITLE} margin-top:10px;color:#e08840;">🦎 Criaturas de Cueva</div>${cuevaRows}` : ''}
      ${aliadosHtml}
      ${totalSel > 0 ? `
        <div style="margin-top:10px;display:flex;justify-content:space-between;align-items:center;">
          <span style="color:#c9a84c;font-size:11px">Seleccionadas: <b>${_fmt(totalSel)}</b></span>
          <button onclick="window._armyClear()" style="${CSS_BTN_DANGER}">Limpiar</button>
        </div>` : ''}
    </div>`;

  // Exponer handlers globales
  window._armyAdj = (jug, key, delta) => {
    const [unidad, origen] = key.includes('|') ? key.split('|') : [key, null];
    const max = jug === _jugador ? (_parseRecurso(_cityData[key]) || 0)
      : ((_cityData.TROPAS_PRESTADAS||[]).find(p =>
          p.jugador===jug && p.unidad===unidad && (!origen || p.ciudad_origen===origen)
        )?.cantidad || 0);
    _selSet(jug, key, (_selGet(jug, key) || 0) + delta, max);
    _renderLeft(); _renderCenter();
    if (window._armyEstimar) window._armyEstimar();
  };
  window._armySet = (jug, key, val, max) => {
    _selSet(jug, key, val, max);
    _renderLeft(); _renderCenter();
    if (window._armyEstimar) window._armyEstimar();
  };
  window._armyAll = (jug, key, max) => {
    _selSet(jug, key, max, max);
    _renderLeft(); _renderCenter();
    if (window._armyEstimar) window._armyEstimar();
  };
  window._armyClear = () => {
    _resetSeleccion();
    _renderLeft(); _renderCenter();
    if (window._armyEstimar) window._armyEstimar();
  };
}

// ── Estado del formulario (persiste entre renders del panel izquierdo) ─────────

let _formState = {
  tipo:      'ATAQUE',
  x:         '',
  y:         '',
  jugDest:   '',
  ciudDest:  '',
  recursos:  { MADERA:0, PIEDRA:0, HIERRO:0, CARBON:0, ORO:0 },
};

function _leerForm() {
  _formState.tipo     = document.getElementById('orden-tipo')?.value     || _formState.tipo;
  _formState.x        = document.getElementById('orden-x')?.value        || _formState.x;
  _formState.y        = document.getElementById('orden-y')?.value        || _formState.y;
  _formState.jugDest  = document.getElementById('orden-jugador-dest')?.value || _formState.jugDest;
  _formState.ciudDest = document.getElementById('orden-ciudad-dest')?.value  || _formState.ciudDest;
  ['MADERA','PIEDRA','HIERRO','CARBON','ORO'].forEach(r => {
    const v = parseFloat(document.getElementById(`res-${r}`)?.value || 0);
    _formState.recursos[r] = v;
  });
}

// ── Panel central: formulario de orden ───────────────────────────────────────

function _renderCenter() {
  const el = document.getElementById('army-center');
  if (!el) return;

  // Si el formulario ya existe, solo actualizar el resumen del pelotón
  if (document.getElementById('orden-tipo')) {
    _leerForm();       // guardar estado actual antes de tocar nada
    _updateResumen();  // actualizar solo el resumen
    return;
  }

  // Primera vez: construir todo
  el.innerHTML = `
    <div id="army-resumen" style="${CSS_PANEL}">
      <div style="${CSS_TITLE}">📋 Composición del pelotón</div>
      <div id="army-resumen-body">
        <div style="color:#555;font-size:11px;text-align:center;padding:8px 0">Selecciona unidades en el panel izquierdo</div>
      </div>
    </div>

    <div style="${CSS_PANEL}">
      <div style="${CSS_TITLE}">🗺 Despachar Orden</div>

      <div style="margin-bottom:8px">
        <label style="color:#c9a84c;font-size:10px;letter-spacing:1px">TIPO DE ORDEN</label>
        <select id="orden-tipo" style="${CSS_INPUT} margin-top:4px;" onchange="window._armyTipoChange(this.value)">
          <option value="ATAQUE">⚔️  ATAQUE</option>
          <option value="ESPIONAJE">🕵️  ESPIONAJE</option>
          <option value="DESPLAZAMIENTO">🚶  DESPLAZAMIENTO (ciudad propia)</option>
          <option value="TRANSPORTE">📦  TRANSPORTE</option>
          <option value="FUNDAR">🏗️  FUNDAR CIUDAD</option>
        </select>
      </div>

      <div id="orden-jugador-wrap" style="margin-bottom:8px">
        <label style="color:#c9a84c;font-size:10px;letter-spacing:1px">JUGADOR DESTINO</label>
        <input id="orden-jugador-dest" type="text" placeholder="Ej: JIARITO"
          style="${CSS_INPUT} margin-top:4px;" />
      </div>

      <div style="margin-bottom:8px">
        <label style="color:#c9a84c;font-size:10px;letter-spacing:1px">CIUDAD DESTINO (nombre, opcional)</label>
        <input id="orden-ciudad-dest" type="text" placeholder="Ej: Bogotá"
          style="${CSS_INPUT} margin-top:4px;" />
      </div>

      <div style="display:flex;gap:8px;margin-bottom:8px">
        <div style="flex:1">
          <label style="color:#c9a84c;font-size:10px;letter-spacing:1px">COORD X</label>
          <input id="orden-x" type="number" min="0" max="1000" placeholder="0–1000"
            style="${CSS_INPUT} margin-top:4px;" oninput="window._armyEstimar()">
        </div>
        <div style="flex:1">
          <label style="color:#c9a84c;font-size:10px;letter-spacing:1px">COORD Y</label>
          <input id="orden-y" type="number" min="0" max="1000" placeholder="0–1000"
            style="${CSS_INPUT} margin-top:4px;" oninput="window._armyEstimar()">
        </div>
      </div>

      <div id="orden-estimacion" style="
        background:rgba(201,168,76,0.06);border:1px solid rgba(201,168,76,0.15);
        border-radius:6px;padding:8px 12px;margin-bottom:10px;font-size:11px;
        font-family:'Cinzel',serif;min-height:36px;color:#a09060;
      ">Introduce coordenadas para estimar</div>

      <div id="orden-recursos-wrap" style="display:none;margin-bottom:8px">
        <div style="${CSS_TITLE} margin-bottom:6px;">📦 Recursos a transportar</div>
        ${['MADERA','PIEDRA','HIERRO','CARBON','ORO'].map(r => `
          <div style="${CSS_ROW}">
            <span style="color:#b0a080">${r}</span>
            <input id="res-${r}" type="number" min="0" max="${_cityData?.[r]||0}" value="0"
              style="${CSS_INPUT} width:100px;text-align:right;" />
          </div>`).join('')}
      </div>

      <button id="btn-despachar" onclick="window._armyDespachar()"
        style="${CSS_BTN('#1a2a0a')} width:100%;padding:10px;font-size:12px;letter-spacing:2px;margin-top:4px;">
        ▶ DESPACHAR
      </button>
      <div id="orden-msg" style="margin-top:8px;font-size:11px;text-align:center;min-height:18px;"></div>
    </div>`;

  // Restaurar estado del formulario
  _restaurarForm();
  _setupFormHandlers();
}

function _updateResumen() {
  const body = document.getElementById('army-resumen-body');
  if (!body) return;
  const total = _selTotal();
  if (total === 0) {
    body.innerHTML = '<div style="color:#555;font-size:11px;text-align:center;padding:8px 0">Selecciona unidades en el panel izquierdo</div>';
    return;
  }
  let html = '';
  for (const [jug, unids] of Object.entries(_seleccion)) {
    const entries = Object.entries(unids).filter(([,v])=>v>0);
    if (!entries.length) continue;
    const color = jug === _jugador ? '#b0a080' : '#7099bb';
    const jugLbl = jug === _jugador ? '⚔ Propias' : `🤝 ${jug}`;
    html += `<div style="color:${color};font-size:10px;letter-spacing:1px;
      font-family:'Cinzel',serif;margin-top:6px;margin-bottom:2px;">${jugLbl}</div>`;
    html += entries.map(([k, v]) => {
      const lbl = [...ARMY, ...INV].find(([,key]) => key === k)?.[0] || k;
      return `<div style="${CSS_ROW}"><span style="color:${color}">${lbl}</span>
        <span style="color:#e8e0d0">${_fmt(v)}</span></div>`;
    }).join('');
  }
  html += `<div style="margin-top:8px;display:flex;justify-content:space-between;align-items:center;">
    <span style="color:#c9a84c;font-size:11px">Total: <b>${_fmt(total)}</b></span>
    <button onclick="window._armyClear()" style="${CSS_BTN_DANGER}">Limpiar</button>
  </div>`;
  body.innerHTML = html;
}

function _restaurarForm() {
  const s = _formState;
  const tEl = document.getElementById('orden-tipo');
  const xEl = document.getElementById('orden-x');
  const yEl = document.getElementById('orden-y');
  const jEl = document.getElementById('orden-jugador-dest');
  const cEl = document.getElementById('orden-ciudad-dest');
  if (tEl && s.tipo)     { tEl.value = s.tipo; window._armyTipoChange?.(s.tipo); }
  if (xEl && s.x)        xEl.value = s.x;
  if (yEl && s.y)        yEl.value = s.y;
  if (jEl && s.jugDest)  jEl.value = s.jugDest;
  if (cEl && s.ciudDest) cEl.value = s.ciudDest;
  ['MADERA','PIEDRA','HIERRO','CARBON','ORO'].forEach(r => {
    const el = document.getElementById(`res-${r}`);
    if (el && s.recursos[r]) el.value = s.recursos[r];
  });
  if (s.x && s.y) setTimeout(() => window._armyEstimar?.(), 50);
}

function _setupFormHandlers() {
  window._armyTipoChange = (tipo) => {
    _formState.tipo = tipo;
    const jw = document.getElementById('orden-jugador-wrap');
    const rw = document.getElementById('orden-recursos-wrap');
    if (jw) jw.style.display = ['DESPLAZAMIENTO','FUNDAR'].includes(tipo) ? 'none' : '';
    if (rw) rw.style.display = tipo === 'TRANSPORTE' ? '' : 'none';
  };

  window._armyEstimar = () => {
    const x = parseFloat(document.getElementById('orden-x')?.value);
    const y = parseFloat(document.getElementById('orden-y')?.value);
    const el = document.getElementById('orden-estimacion');
    const btn = document.getElementById('btn-despachar');
    if (!el || !_cityData) return;
    if (isNaN(x) || isNaN(y)) {
      el.textContent = 'Introduce coordenadas para estimar';
      if (btn) btn.disabled = false;
      return;
    }

    const ox = _cityData.X || 0, oy = _cityData.Y || 0;
    const dist = Math.sqrt((x - ox) ** 2 + (y - oy) ** 2);

    const INV_KEYS = new Set(INV.map(([,k]) => k));
    let cantBasicas = 0;
    let velMin = Infinity;
    const VEL_APROX = {
      ALDEANO:10,EXPLORADOR:18,SACERDOTE:14,GUERRERO:15,COMANDO:25,
      MERCENARIO:30,MARINE:40,CYBORG:55,MAGO:50,METAHUMANO:80,
      DEMONIO:60,ANIMA:70,ESPECTRO:80,GOLEM:40,CENTAURO:120,KRAKEN:50,
      ALONARDO:150,MADRESELVA:100,COLOSO:200,FENIX:350,DRAGON_DE_ORO:500,
      CABALLERO_DE_LUZ:800,ALALAIA:5000000,EON_SUPREMO:1000000,
    };
    // Iterar sobre nueva estructura {jugador: {key: cant}}
    for (const unids of Object.values(_seleccion)) {
      for (const [k, v] of Object.entries(unids)) {
        if (v > 0) {
          if (!INV_KEYS.has(k)) cantBasicas += v;
          velMin = Math.min(velMin, VEL_APROX[k] || 10);
        }
      }
    }
    const oroC    = cantBasicas > 0 ? Math.ceil(dist * 10 * cantBasicas) : 0;
    const oroDisp = _parseRecurso(_cityData.ORO);
    const suficiente = oroC === 0 || oroDisp >= oroC;
    if (!isFinite(velMin)) velMin = 10;

    const segs = dist * (50 / velMin);

    // Bloquear botón si oro insuficiente
    if (btn) {
      btn.disabled = !suficiente;
      btn.style.opacity = suficiente ? '1' : '0.4';
      btn.style.cursor  = suficiente ? 'pointer' : 'not-allowed';
    }

    const costoStr = oroC === 0
      ? '<b style="color:#6ba3e0">Gratis</b> <span style="color:#666">(solo invocaciones)</span>'
      : `<b style="color:${suficiente ? '#c9a84c' : '#e05050'}">${_fmt(oroC)} oro</b>
         <span style="color:#666">/ disponible: <b style="color:${suficiente?'#c9a84c':'#e05050'}">${oroDisp === Infinity ? '∞' : _fmt(oroDisp)}</b></span>
         ${suficiente ? '✓' : ' ⚠ <b style="color:#e05050">ORO INSUFICIENTE</b>'}`;

    el.innerHTML = `
      <div style="display:flex;flex-wrap:wrap;gap:14px;align-items:center;">
        <span>📏 <b style="color:#e8e0d0">${dist.toFixed(1)} tiles</b></span>
        <span>⏱ <b style="color:#e8e0d0">${_fmtTime(segs)}</b></span>
        <span>🪙 ${costoStr}</span>
      </div>`;
  };

  window._armyDespachar = async () => {
    const msg  = document.getElementById('orden-msg');
    const tipo = document.getElementById('orden-tipo')?.value;
    const xStr = document.getElementById('orden-x')?.value;
    const yStr = document.getElementById('orden-y')?.value;
    const jugDest  = (document.getElementById('orden-jugador-dest')?.value?.trim().toUpperCase()) || _formState.jugDest?.toUpperCase() || '';
    console.log('[orden] jugDest:', jugDest, '| _formState.jugDest:', _formState.jugDest);
    const ciudDest = document.getElementById('orden-ciudad-dest')?.value?.trim();

    if (!xStr || !yStr) { msg.innerHTML = '<span style="color:#e05050">Introduce coordenadas</span>'; return; }

    const x = parseFloat(xStr), y = parseFloat(yStr);
    if (isNaN(x) || isNaN(y)) { msg.innerHTML = '<span style="color:#e05050">Coordenadas inválidas</span>'; return; }

    // Verificar oro antes de enviar
    if (_cityData) {
      const INV_KEYS = new Set(INV.map(([,k]) => k));
      let cantBasicas = 0;
      for (const unids of Object.values(_seleccion)) {
        for (const [k, v] of Object.entries(unids)) {
          if (v > 0 && !INV_KEYS.has(k)) cantBasicas += v;
        }
      }
      if (cantBasicas > 0) {
        const ox   = _cityData.X || 0, oy = _cityData.Y || 0;
        const dist = Math.sqrt((x - ox) ** 2 + (y - oy) ** 2);
        const oroC = Math.ceil(dist * 10 * cantBasicas);
        const oroDisp = _parseRecurso(_cityData.ORO);
        if (isFinite(oroDisp) && oroDisp < oroC) {
          msg.innerHTML = `<span style="color:#e05050">⚠ Oro insuficiente: necesitas ${_fmt(oroC)}, tienes ${_fmt(oroDisp)}</span>`;
          return;
        }
      }
    }

    // Aplanar selección: {jugador: {key: cant}} → {key: cant} para propias
    // y separar prestadas por propietario
    const propias = {};
    // Descomponer claves compuestas (UNIDAD|ciudad_origen) de vuelta a unidad real
    const prestadas_sel = {};  // {jugador: {unidad: cant}} — suma múltiples entradas
    for (const [jug, unids] of Object.entries(_seleccion)) {
      for (const [key, cnt] of Object.entries(unids)) {
        if (cnt <= 0) continue;
        if (jug === _jugador) propias[key] = (propias[key]||0) + cnt;
        else {
          if (!prestadas_sel[jug]) prestadas_sel[jug] = {};
          const unidadReal = key.includes('|') ? key.split('|')[0] : key;
          prestadas_sel[jug][unidadReal] = (prestadas_sel[jug][unidadReal] || 0) + cnt;
        }
      }
    }

    const totalUnidades = Object.values(propias).reduce((s,v)=>s+v,0)
      + Object.values(prestadas_sel).reduce((s,d)=>s+Object.values(d).reduce((a,v)=>a+v,0),0);

    if (totalUnidades === 0 && tipo !== 'TRANSPORTE') {
      msg.innerHTML = '<span style="color:#e05050">Selecciona al menos una unidad</span>'; return;
    }

    // Recursos para TRANSPORTE
    let recursos = {};
    if (tipo === 'TRANSPORTE') {
      ['MADERA','PIEDRA','HIERRO','CARBON','ORO'].forEach(r => {
        const v = parseFloat(document.getElementById(`res-${r}`)?.value || 0);
        if (v > 0) recursos[r] = v;
      });
    }

    msg.innerHTML = '<span style="color:#c9a84c">⏳ Despachando…</span>';

    try {
      const body = {
        tipo,
        ciudad_origen:      _ciudad,
        x_dest:             x,
        y_dest:             y,
        unidades:           propias,
        unidades_prestadas: prestadas_sel,
        recursos,
        jugador_dest:       jugDest || null,
        ciudad_dest_nombre: ciudDest || null,
      };
      const r = await fetch(`/api/orders/${_jugador}/crear`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(body),
      });
      const d = await r.json();
      if (d.ok) {
        msg.innerHTML = `<span style="color:#4caf50">✅ ${d.msg}</span>`;
        _resetSeleccion();
        await _loadAndRender();
      } else {
        msg.innerHTML = `<span style="color:#e05050">❌ ${d.msg}</span>`;
      }
    } catch (e) {
      msg.innerHTML = `<span style="color:#e05050">Error: ${e.message}</span>`;
    }
  };
}

// ── Panel derecho: órdenes en curso ──────────────────────────────────────────

function _renderRight() {
  const el = document.getElementById('army-right');
  if (!el) return;

  if (_ordenes.length === 0) {
    el.innerHTML = `
      <div style="${CSS_PANEL}">
        <div style="${CSS_TITLE}">🗺 Órdenes Activas</div>
        <div style="color:#555;font-size:11px;text-align:center;padding:12px 0">
          Sin órdenes activas
        </div>
      </div>`;
    return;
  }

  const cards = _ordenes.map(o => {
    const icon   = TIPO_ICONS[o.tipo] || '📋';
    const color  = ESTADO_COLORS[o.estado] || '#888';
    const segs   = Math.max(0, o.seg_restantes || 0);
    const destStr = o.destino ? `(${o.destino[0]}, ${o.destino[1]})` : '?';

    let resHTML = '';
    if (o.resultado) {
      const r = o.resultado;
      if (r.victoria !== undefined) {
        resHTML = `<div style="color:${r.victoria ? '#4caf50' : '#e05050'};font-size:10px;margin-top:4px">
          ${r.victoria ? '✅ Victoria' : '❌ Derrota'} — ${r.mensaje || ''}
        </div>`;
      }
      if (r.inteligencia) {
        resHTML = `<div style="color:#6ba3e0;font-size:10px;margin-top:4px">🔍 Inteligencia obtenida</div>`;
      }
      if (r.detectado === false) {
        resHTML += `<div style="color:#4caf50;font-size:10px">🕵️ No detectado</div>`;
      }
      if (r.detectado === true) {
        resHTML += `<div style="color:#e05050;font-size:10px">⚠️ Detectado — combate</div>`;
      }
    }

    return `
      <div style="
        background:rgba(8,10,20,0.9);border:1px solid ${color}44;
        border-left:3px solid ${color};border-radius:6px;
        padding:10px 12px;margin-bottom:8px;
      ">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="color:${color};font-size:12px;font-family:'Cinzel',serif;">
            ${icon} ${o.tipo}
          </span>
          <span style="color:${color};font-size:10px;background:${color}22;
            padding:2px 8px;border-radius:10px;">${o.estado}</span>
        </div>
        <div style="color:#888;font-size:10px;margin-top:4px">
          Destino: <span style="color:#b0a080">${destStr}</span>
        </div>
        <div style="color:#888;font-size:10px;margin-top:2px">
          ⏱ <span class="ord-timer" data-segs="${segs}" style="color:#e8e0d0">${_fmtTime(segs)}</span>
        </div>
        ${resHTML}
        ${o.estado === 'EN_VIAJE' ? `
          <button onclick="window._armyCancelar('${o.id}')"
            style="${CSS_BTN_DANGER} margin-top:6px;font-size:9px;">
            ✕ Cancelar
          </button>` : ''}
      </div>`;
  }).join('');

  el.innerHTML = `
    <div style="${CSS_PANEL}">
      <div style="${CSS_TITLE}">🗺 Órdenes Activas (${_ordenes.length})</div>
      ${cards}
    </div>`;

  window._armyCancelar = async (ordenId) => {
    try {
      const r = await fetch(`/api/orders/${_jugador}/${ordenId}`, { method: 'DELETE' });
      const d = await r.json();
      if (d.ok) await _loadAndRender();
      else alert(d.msg);
    } catch (e) {
      alert('Error: ' + e.message);
    }
  };
}

// ── Tick de timers en pantalla ────────────────────────────────────────────────

function _tickOrdenes() {
  document.querySelectorAll('.ord-timer').forEach(el => {
    let segs = parseFloat(el.dataset.segs || 0) - 1;
    if (segs < 0) segs = 0;
    el.dataset.segs = segs;
    el.textContent  = _fmtTime(segs);
  });
}

// ── Cleanup ───────────────────────────────────────────────────────────────────

export function cleanup() {
  if (_syncTimer) { clearInterval(_syncTimer); _syncTimer = null; }
  if (_ordTimer)  { clearInterval(_ordTimer);  _ordTimer  = null; }
  if (_coordListener) {
    window.removeEventListener('ew:coordsSeleccionadas', _coordListener);
    _coordListener = null;
  }
  _cityData = null;
  _ordenes  = [];
  _resetSeleccion();
  // Limpiar handlers globales
  delete window._armyAdj;
  delete window._armySet;
  delete window._armyAll;
  delete window._armyClear;
  delete window._armyTipoChange;
  delete window._armyEstimar;
  delete window._armyDespachar;
  delete window._armyCancelar;
}
