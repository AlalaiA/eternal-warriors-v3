/**
 * frontend/js/screens/alliance.js
 * Eternal Warriors v3.0 — Pantalla de Alianzas (completa)
 *
 * Flujos implementados:
 *   - Ver alianza actual · Crear · Solicitar unión
 *   - Aceptar / Rechazar solicitudes (líder)
 *   - Expulsar miembro (líder) · Salir voluntariamente
 *   - Prestar tropas (selector de unidades disponibles)
 *   - Reclamar tropas propias prestadas a aliados
 *   - Ver tropas aliadas en mis ciudades
 *   - Ver mis tropas en ciudades ajenas
 *   - Polling 10s para actualización automática
 */

const _API = (path) => `/api/alliances${path}`;

// ── Helpers visuales ──────────────────────────────────────────────────────────

function _fmtNum(n) {
  if (n === '__INF__' || n === Infinity) return '∞';
  n = Number(n);
  if (!isFinite(n)) return '∞';
  if (n >= 1e15) return (n/1e15).toFixed(2)+'Qa';
  if (n >= 1e12) return (n/1e12).toFixed(2)+'T';
  if (n >= 1e9)  return (n/1e9).toFixed(2)+'G';
  if (n >= 1e6)  return (n/1e6).toFixed(2)+'M';
  if (n >= 1e3)  return (n/1e3).toFixed(1)+'K';
  return Math.floor(n).toLocaleString('es');
}

function _tag(color, text) {
  return `<span style="
    display:inline-block;padding:2px 9px;border-radius:2px;font-size:10px;
    letter-spacing:2px;font-family:'Cinzel',serif;text-transform:uppercase;
    background:${color}18;border:1px solid ${color}44;color:${color};
  ">${text}</span>`;
}

function _btn(label, onclick, color='#c9a84c', small=false, extra='') {
  return `<button onclick="${onclick}" style="
    background:transparent;border:1px solid ${color}55;color:${color};
    font-family:'Cinzel',serif;font-size:${small?'9':'11'}px;letter-spacing:1px;
    padding:${small?'4px 9px':'8px 18px'};border-radius:3px;cursor:pointer;
    transition:background 0.15s,border-color 0.15s;margin:3px;${extra}
    " onmouseover="this.style.background='${color}22';this.style.borderColor='${color}99'"
       onmouseout="this.style.background='transparent';this.style.borderColor='${color}55'">
    ${label}
  </button>`;
}

function _input(id, placeholder, type='text', val='') {
  return `<input id="${id}" type="${type}" placeholder="${placeholder}" value="${val}" style="
    background:rgba(255,255,255,0.04);border:1px solid rgba(201,168,76,0.25);
    color:#e8d5a3;font-family:'Rajdhani',sans-serif;font-size:13px;
    padding:8px 12px;border-radius:3px;width:100%;box-sizing:border-box;
    margin-bottom:8px;outline:none;
  " onfocus="this.style.borderColor='rgba(201,168,76,0.6)'"
     onblur="this.style.borderColor='rgba(201,168,76,0.25)'">`;
}

function _select(id, options, extra='') {
  return `<select id="${id}" style="
    width:100%;background:rgba(10,12,24,0.9);border:1px solid rgba(201,168,76,0.25);
    color:#e8d5a3;font-family:'Rajdhani',sans-serif;font-size:13px;
    padding:8px 10px;border-radius:3px;outline:none;${extra}
  ">${options}</select>`;
}

function _card(content, extra='') {
  return `<div style="
    background:rgba(8,11,22,0.88);border:1px solid rgba(201,168,76,0.18);
    border-radius:6px;padding:18px 20px;margin-bottom:14px;${extra}
  ">${content}</div>`;
}

function _section(icon, title, content) {
  return `<div style="margin-bottom:28px;">
    <div style="
      display:flex;align-items:center;gap:8px;
      font-family:'Cinzel',serif;font-size:10px;letter-spacing:3px;
      color:#c9a84c;text-transform:uppercase;margin-bottom:12px;
      border-bottom:1px solid rgba(201,168,76,0.15);padding-bottom:8px;
    ">${icon} ${title}</div>
    ${content}
  </div>`;
}

function _divider() {
  return `<div style="height:1px;background:rgba(201,168,76,0.1);margin:16px 0;"></div>`;
}

function _toast(msg, ok=true) {
  const t = document.createElement('div');
  t.style.cssText = `
    position:fixed;bottom:80px;left:50%;transform:translateX(-50%) translateY(10px);
    background:${ok?'rgba(60,140,80,0.95)':'rgba(190,60,50,0.95)'};
    color:#fff;font-family:'Cinzel',serif;font-size:11px;letter-spacing:2px;
    padding:10px 28px;border-radius:4px;z-index:9999;
    box-shadow:0 4px 20px rgba(0,0,0,0.5);
    animation:_toastIn 0.25s ease forwards;
  `;
  if (!document.getElementById('_toastStyle')) {
    const s = document.createElement('style');
    s.id = '_toastStyle';
    s.textContent = `@keyframes _toastIn{from{opacity:0;transform:translateX(-50%) translateY(14px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}`;
    document.head.appendChild(s);
  }
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => { t.style.opacity='0'; t.style.transition='opacity 0.3s'; setTimeout(()=>t.remove(),350); }, 3000);
}

function _labelSmall(text) {
  return `<div style="font-size:10px;color:#667788;letter-spacing:1px;margin-bottom:4px;font-family:'Cinzel',serif;">${text}</div>`;
}

// ── Estado global de sesión ───────────────────────────────────────────────────

let _jugador = null;
let _pollTimer = null;

// ── Render principal ──────────────────────────────────────────────────────────

export async function render(container, jugador, ciudad) {
  _jugador = jugador ? jugador.toUpperCase() : jugador;

  container.innerHTML = `
    <div style="
      max-width:920px;margin:0 auto;padding:24px 20px;
      font-family:'Rajdhani',sans-serif;color:#c8b88a;
    ">
      <div style="
        font-family:'Cinzel',serif;font-size:18px;color:#c9a84c;
        letter-spacing:4px;margin-bottom:6px;text-align:center;
      ">⚔ ALIANZAS</div>
      <div style="
        text-align:center;font-size:10px;color:#556;letter-spacing:2px;
        margin-bottom:28px;font-family:'Cinzel',serif;
      ">ETERNAL WARRIORS</div>
      <div id="ali-content" style="min-height:200px;">
        <div style="text-align:center;color:#556;padding:40px;">Cargando datos...</div>
      </div>
    </div>`;

  await _loadAll();
  _startPolling();
}

export function cleanup() {
  _stopPolling();
}

function _startPolling() {
  _stopPolling();
  _pollTimer = setInterval(_loadAll, 10000);
}

function _stopPolling() {
  if (_pollTimer) { clearInterval(_pollTimer); _pollTimer = null; }
}

// ── Carga y render de datos ───────────────────────────────────────────────────

async function _loadAll() {
  const el = document.getElementById('ali-content');
  if (!el) { _stopPolling(); return; }

  try {
    const [rMia, rAll, rPrest, rMisPrest] = await Promise.all([
      fetch(_API(`/${_jugador}`)).then(r=>r.json()),
      fetch(_API('')).then(r=>r.json()),
      fetch(_API(`/${_jugador}/tropas_prestadas`)).then(r=>r.json()),
      fetch(_API(`/${_jugador}/mis_tropas_prestadas`)).then(r=>r.json()),
    ]);

    let html = '';

    // ── BLOQUE: tiene alianza ─────────────────────────────────────────────────
    if (rMia.alianza) {
      html += _renderMiAlianza(rMia);
      html += await _renderPresentarTropas(rMia);
      html += _renderTropasAliadas(rPrest);
      html += _renderMisTropasEnOtros(rMisPrest);
    } else {
      // ── BLOQUE: sin alianza ───────────────────────────────────────────────
      html += _renderSinAlianza(rAll);
    }

    el.innerHTML = html;

    // Inicializar dropdowns post-render
    if (rMia.alianza) {
      await _initPrestDropdowns(rMia);
    }

  } catch(e) {
    if (el) el.innerHTML = `<div style="color:#c05050;text-align:center;padding:40px;font-family:'Cinzel',serif;font-size:11px;letter-spacing:2px;">ERROR · ${e.message}</div>`;
  }
}

// ── Sección: MI ALIANZA ───────────────────────────────────────────────────────

function _renderMiAlianza(rMia) {
  const a = rMia;
  const esLider = a.es_lider;
  const lideres = a.lideres || [];

  // Miembros
  const miembrosHtml = a.miembros.map(m => {
    const esEl  = m === _jugador;
    const esLid = lideres.includes(m);
    const puedeExpulsar = esLider && !esEl && !esLid;
    const puedePromover = esLider && !esEl && !esLid;
    const puedeDeg      = esLider && !esEl && esLid && lideres.length > 1;
    return `<div style="
      display:flex;align-items:center;justify-content:space-between;
      padding:7px 12px;margin-bottom:4px;border-radius:3px;
      background:${esEl?'rgba(201,168,76,0.08)':'rgba(255,255,255,0.02)'};
      border:1px solid ${esEl?'rgba(201,168,76,0.25)':'rgba(255,255,255,0.06)'};
    ">
      <div>
        <span style="font-family:'Cinzel',serif;font-size:12px;color:${esEl?'#c9a84c':'#aabbcc'};">
          ${esLid?'👑 ':''}${m}${esEl?' (tú)':''}
        </span>
      </div>
      <div style="display:flex;align-items:center;gap:4px;flex-wrap:wrap;justify-content:flex-end;">
        ${esLid ? _tag('#c9a84c','LÍDER') : _tag('#667788','MIEMBRO')}
        ${puedePromover ? _btn('⬆ Líder', `_promoverLider('${a.alianza}','${m}','${_jugador}')`, '#c9a84c', true) : ''}
        ${puedeDeg      ? _btn('⬇ Miembro', `_degradarLider('${a.alianza}','${m}','${_jugador}')`, '#778899', true) : ''}
        ${puedeExpulsar ? _btn('Expulsar', `_expulsarMiembro('${a.alianza}','${m}','${_jugador}')`, '#c05050', true) : ''}
      </div>
    </div>`;
  }).join('');

  // Solicitudes pendientes (solo líder)
  let solicitudesHtml = '';
  if (esLider && a.solicitudes && a.solicitudes.length > 0) {
    solicitudesHtml = _divider() + `
      <div style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:3px;color:#c9a84c;margin-bottom:10px;">
        SOLICITUDES PENDIENTES (${a.solicitudes.length})
      </div>
      ${a.solicitudes.map(s => `
        <div style="
          display:flex;align-items:center;justify-content:space-between;
          padding:8px 12px;background:rgba(201,168,76,0.05);
          border:1px solid rgba(201,168,76,0.15);border-radius:3px;margin-bottom:6px;
        ">
          <span style="font-family:'Cinzel',serif;font-size:12px;color:#e8d080;">${s}</span>
          <div>
            ${_btn('✓ Aceptar', `_aceptarSolicitud('${a.alianza}','${s}','${_jugador}')`, '#4caf50', true)}
            ${_btn('✗ Rechazar', `_rechazarSolicitud('${a.alianza}','${s}','${_jugador}')`, '#c05050', true)}
          </div>
        </div>
      `).join('')}`;
  }

  // El líder puede degradarse a sí mismo si hay otros líderes
  const puedeDegSelf = esLider && lideres.length > 1;
  const transferirHtml = puedeDegSelf ? `
    <div style="margin-top:10px;">
      ${_labelSmall('RENUNCIAR AL LIDERAZGO')}
      <div style="font-size:10px;color:#667;margin-bottom:6px;">
        Pasarás a ser miembro. Quedan ${lideres.length - 1} líder(es).
      </div>
      ${_btn('⬇ Renunciar al liderazgo', `_degradarLider('${a.alianza}','${_jugador}','${_jugador}')`, '#778899', true)}
    </div>` : '';

  const salirHtml = esLider && a.miembros.length > 1 && lideres.length <= 1
    ? `<div style="font-size:10px;color:#667;margin-top:8px;font-style:italic;">Eres el único líder — promueve a otro antes de salir.</div>`
    : _btn('⚑ Salir de la alianza', `_salirAlianza('${a.alianza}','${_jugador}','${_jugador}')`, '#c05050', true);

  return _section('⚔', 'MI ALIANZA', _card(`
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;">
      <div>
        <div style="font-family:'Cinzel',serif;font-size:20px;color:#e8d080;letter-spacing:2px;margin-bottom:4px;">
          ${a.alianza}
        </div>
        <div style="font-size:11px;color:#667788;">
          ${a.miembros.length} / 50 miembros · Líder${lideres.length>1?'es':''}: <span style="color:#c9a84c;">${lideres.join(', ')}</span>
        </div>
      </div>
      <div>
        ${esLider ? _tag('#c9a84c','LÍDER') : _tag('#667788','MIEMBRO')}
      </div>
    </div>

    <div style="margin-bottom:4px;font-family:'Cinzel',serif;font-size:9px;letter-spacing:3px;color:#667788;">MIEMBROS</div>
    ${miembrosHtml}

    ${solicitudesHtml}

    <div style="margin-top:14px;border-top:1px solid rgba(201,168,76,0.1);padding-top:12px;">
      ${transferirHtml}
      ${salirHtml}
    </div>
  `));
}

// ── Sección: PRESTAR TROPAS ───────────────────────────────────────────────────

async function _renderPresentarTropas(rMia) {
  const aliados = (rMia.miembros || []).filter(m => m !== _jugador);
  if (aliados.length === 0) return '';

  // Cargar ciudades propias para el selector origen
  let misCiudades = [];
  try {
    const rc = await fetch(`/api/city/${_jugador}`).then(r=>r.json());
    misCiudades = rc.cities || [];
  } catch {}

  const optsCiudadOrig = misCiudades.map(c=>`<option value="${c}">${c}</option>`).join('');
  const optsAliado     = aliados.map(a=>`<option value="${a}">${a}</option>`).join('');

  return _section('↗', 'PRESTAR TROPAS', _card(`
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;">
      <div>
        ${_labelSmall('Ciudad origen (mía)')}
        ${_select('prest-ciudad-orig', optsCiudadOrig, 'margin-bottom:0;')}
      </div>
      <div>
        ${_labelSmall('Aliado receptor')}
        ${_select('prest-aliado', optsAliado, 'margin-bottom:0;')}
      </div>
    </div>

    <div style="margin-bottom:12px;">
      ${_labelSmall('Ciudad destino (del aliado)')}
      ${_select('prest-ciudad-dest', '<option>Selecciona aliado primero</option>', 'margin-bottom:0;')}
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;">
      <div>
        ${_labelSmall('Unidad')}
        ${_select('prest-unidad', '<option value="">— tipo —</option>', 'margin-bottom:0;')}
      </div>
      <div>
        ${_labelSmall('Cantidad')}
        ${_input('prest-cantidad', 'Ej: 1000', 'number')}
      </div>
    </div>

    <div style="display:flex;align-items:center;gap:10px;">
      ${_btn('↗ Prestar tropas', `_prestarTropas()`, '#7899cc')}
      <span id="prest-disp" style="font-size:11px;color:#667788;"></span>
    </div>
  `));
}

async function _initPrestDropdowns(rMia) {
  const aliados = (rMia.miembros || []).filter(m => m !== _jugador);
  if (aliados.length === 0) return;

  // Listener: cambio de aliado → actualizar ciudades destino
  const selAliado = document.getElementById('prest-aliado');
  if (selAliado) {
    selAliado.addEventListener('change', () => _actualizarCiudadesAliado(selAliado.value));
    await _actualizarCiudadesAliado(aliados[0]);
  }

  // Listener: cambio de ciudad origen → actualizar unidades disponibles
  const selOrig = document.getElementById('prest-ciudad-orig');
  if (selOrig) {
    selOrig.addEventListener('change', () => _actualizarUnidadesOrigen(selOrig.value));
    if (selOrig.value) await _actualizarUnidadesOrigen(selOrig.value);
  }

  // Listener: cambio de unidad → mostrar disponible
  const selUnidad = document.getElementById('prest-unidad');
  if (selUnidad) {
    selUnidad.addEventListener('change', _actualizarDisponible);
  }
}

const _TROPAS_BASICAS = [
  'ALDEANO','EXPLORADOR','SACERDOTE','GUERRERO','COMANDO',
  'MERCENARIO','MARINE','CYBORG','MAGO','METAHUMANO'
];

let _ciudadOrigenData = null; // cache de la ciudad origen seleccionada

async function _actualizarUnidadesOrigen(nombreCiudad) {
  const selUnidad = document.getElementById('prest-unidad');
  if (!selUnidad) return;
  // Poblar con las 10 tropas básicas; el backend valida disponibilidad real
  const opts = _TROPAS_BASICAS
    .map(t => `<option value="${t}">${t}</option>`)
    .join('');
  selUnidad.innerHTML = opts;
  _ciudadOrigenData = null;
  _actualizarDisponible();
}

function _actualizarDisponible() {
  // Sin datos de ciudad en tiempo real — validación en backend
}

async function _actualizarCiudadesAliado(aliado) {
  const sel = document.getElementById('prest-ciudad-dest');
  if (!sel) return;
  try {
    const r = await fetch(`/api/city/${aliado}`).then(r=>r.json());
    const ciudades = r.cities || [];
    sel.innerHTML = ciudades.map(c=>`<option value="${c}">${c}</option>`).join('') || '<option>Sin ciudades</option>';
  } catch {
    sel.innerHTML = '<option>Error</option>';
  }
}

// ── Sección: TROPAS ALIADAS EN MIS CIUDADES ───────────────────────────────────

function _renderTropasAliadas(rPrest) {
  const prest = rPrest.tropas_prestadas_en_mis_ciudades || {};
  const entradas = Object.entries(prest).filter(([,arr]) => arr.length > 0);
  if (entradas.length === 0) return '';

  let inner = '';
  for (const [ciudad, arr] of entradas) {
    inner += `<div style="margin-bottom:14px;">
      <div style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:2px;color:#8899aa;margin-bottom:8px;">
        📍 ${ciudad}
      </div>`;
    for (const p of arr) {
      inner += `<div style="
        display:flex;align-items:center;justify-content:space-between;
        padding:7px 12px;background:rgba(100,150,200,0.06);
        border:1px solid rgba(100,150,200,0.15);border-radius:3px;margin-bottom:4px;
      ">
        <div>
          <span style="color:#7899cc;font-family:'Cinzel',serif;font-size:10px;">🤝 ${p.jugador}</span>
          <span style="color:#c8b88a;margin-left:10px;font-size:13px;">${p.unidad} × ${_fmtNum(p.cantidad)}</span>
        </div>
        <span style="font-size:10px;color:#556;">desde ${p.ciudad_origen}</span>
      </div>`;
    }
    inner += `</div>`;
  }

  return _section('🤝', 'TROPAS ALIADAS EN MIS CIUDADES', _card(inner));
}

// ── Sección: MIS TROPAS EN CIUDADES AJENAS ────────────────────────────────────

function _renderMisTropasEnOtros(rMisPrest) {
  const datos = rMisPrest.mis_tropas_en_otros || {};
  const aliados = Object.entries(datos);
  if (aliados.length === 0) return '';

  let inner = '';
  for (const [aliado, ciudades] of aliados) {
    for (const [ciudad, arr] of Object.entries(ciudades)) {
      inner += `<div style="margin-bottom:14px;">
        <div style="
          font-family:'Cinzel',serif;font-size:9px;letter-spacing:2px;
          color:#8899aa;margin-bottom:8px;
        ">↗ ${aliado} · ${ciudad}</div>`;
      for (const p of arr) {
        inner += `<div style="
          display:flex;align-items:center;justify-content:space-between;
          padding:7px 12px;background:rgba(201,168,76,0.05);
          border:1px solid rgba(201,168,76,0.15);border-radius:3px;margin-bottom:4px;
        ">
          <span style="color:#c8b88a;font-size:13px;">${p.unidad} × ${_fmtNum(p.cantidad)}</span>
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:10px;color:#556;">origen: ${p.ciudad_origen}</span>
            ${_btn('↙ Reclamar', `_reclamarTropas('${aliado}','${ciudad}','${p.unidad}',${p.cantidad})`, '#c9a84c', true)}
          </div>
        </div>`;
      }
      inner += `</div>`;
    }
  }

  return _section('↗', 'MIS TROPAS EN CIUDADES ALIADAS', _card(inner));
}

// ── Sección: SIN ALIANZA ──────────────────────────────────────────────────────

function _renderSinAlianza(rAll) {
  const todas = Object.values(rAll.alianzas || {})
    .filter(a => a.tipo !== 'vitaminizado');

  const listaHtml = todas.length > 0 ? todas.map(a => `
    <div style="
      display:flex;justify-content:space-between;align-items:center;
      padding:10px 14px;background:rgba(255,255,255,0.02);
      border:1px solid rgba(201,168,76,0.12);border-radius:3px;margin-bottom:6px;
    ">
      <div>
        <span style="font-family:'Cinzel',serif;font-size:13px;color:#e8d080;">${a.nombre}</span>
        <span style="font-size:11px;color:#667788;margin-left:10px;">${a.miembros.length}/50</span>
        <div style="font-size:10px;color:#556;margin-top:2px;">
          Líder: ${a.lider} · Miembros: ${a.miembros.join(', ')}
        </div>
      </div>
      <div>
        ${a.miembros.length < 50
          ? _btn('Solicitar', `_solicitarUnion_nombre('${a.nombre}')`, '#7899cc', true)
          : _tag('#556','LLENA')}
      </div>
    </div>
  `).join('') : `<div style="color:#556;font-size:12px;text-align:center;padding:20px;">
    No hay alianzas disponibles aún.
  </div>`;

  return `
    ${_section('⚑', 'CREAR ALIANZA', _card(`
      <div style="font-size:12px;color:#8899aa;margin-bottom:14px;">
        Funda tu propia alianza y recluta hasta 50 guerreros.
      </div>
      ${_labelSmall('Nombre de la alianza')}
      ${_input('ali-nombre-nueva','Ej: IRON_LEGION')}
      ${_btn('⚑ Fundar alianza', `_crearAlianza()`, '#c9a84c')}
    `))}
    ${_section('↙', 'UNIRSE A UNA ALIANZA', `
      <div style="margin-bottom:12px;">
        ${_card(`
          ${_labelSmall('Nombre exacto de la alianza')}
          ${_input('ali-nombre-unirse','Escribe el nombre')}
          ${_btn('↙ Solicitar unión', `_solicitarUnion()`, '#7899cc')}
        `)}
      </div>
      <div style="font-family:'Cinzel',serif;font-size:9px;letter-spacing:3px;color:#667788;margin-bottom:8px;">
        ALIANZAS EXISTENTES
      </div>
      ${listaHtml}
    `)}`;
}


// ── Acciones ──────────────────────────────────────────────────────────────────

window._crearAlianza = async function() {
  const nombre = document.getElementById('ali-nombre-nueva')?.value?.trim();
  if (!nombre) return _toast('Escribe un nombre para la alianza', false);
  const r = await fetch(_API('/crear'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({jugador: _jugador, nombre})
  }).then(r=>r.json());
  _toast(r.msg, r.ok);
  if (r.ok) await _loadAll();
};

window._solicitarUnion = async function() {
  const alianza = document.getElementById('ali-nombre-unirse')?.value?.trim().toUpperCase().replace(/ /g,'_');
  if (!alianza) return _toast('Escribe el nombre de la alianza', false);
  const r = await fetch(_API('/solicitar'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({jugador: _jugador, alianza})
  }).then(r=>r.json());
  _toast(r.msg, r.ok);
  if (r.ok) await _loadAll();
};

window._solicitarUnion_nombre = async function(alianza) {
  const r = await fetch(_API('/solicitar'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({jugador: _jugador, alianza})
  }).then(r=>r.json());
  _toast(r.msg, r.ok);
  if (r.ok) await _loadAll();
};

window._aceptarSolicitud = async function(alianza, solicitante, lider) {
  const r = await fetch(_API('/aceptar'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({alianza, solicitante, lider})
  }).then(r=>r.json());
  _toast(r.msg, r.ok);
  if (r.ok) await _loadAll();
};

window._rechazarSolicitud = async function(alianza, solicitante, lider) {
  const r = await fetch(_API('/rechazar'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({alianza, solicitante, lider})
  }).then(r=>r.json());
  _toast(r.msg, r.ok);
  if (r.ok) await _loadAll();
};

window._salirAlianza = async function(alianza, jugador, ejecutor) {
  if (!confirm(`¿Confirmas salir de la alianza ${alianza}?`)) return;
  const r = await fetch(_API('/salir'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({alianza, jugador, ejecutor})
  }).then(r=>r.json());
  _toast(r.msg, r.ok);
  if (r.ok) await _loadAll();
};

window._expulsarMiembro = async function(alianza, jugador, ejecutor) {
  if (!confirm(`¿Expulsar a ${jugador} de la alianza?`)) return;
  const r = await fetch(_API('/salir'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({alianza, jugador, ejecutor})
  }).then(r=>r.json());
  _toast(r.msg, r.ok);
  if (r.ok) await _loadAll();
};

window._prestarTropas = async function() {
  const ciudad_origen   = document.getElementById('prest-ciudad-orig')?.value;
  const jugador_huesped = document.getElementById('prest-aliado')?.value;
  const ciudad_destino  = document.getElementById('prest-ciudad-dest')?.value;
  const unidad          = document.getElementById('prest-unidad')?.value?.trim().toUpperCase();
  const cantidad        = Math.floor(Number(document.getElementById('prest-cantidad')?.value || '0'));

  if (!ciudad_origen || !jugador_huesped || !ciudad_destino)
    return _toast('Selecciona origen, aliado y destino', false);
  if (!unidad) return _toast('Selecciona una unidad', false);
  if (cantidad <= 0) return _toast('Cantidad debe ser mayor que 0', false);

  const r = await fetch(_API('/prestar'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({
      jugador_dueño: _jugador,
      ciudad_origen,
      jugador_huesped,
      ciudad_destino,
      unidades: {[unidad]: cantidad}
    })
  }).then(r=>r.json());
  _toast(r.msg, r.ok);
  if (r.ok) {
    document.getElementById('prest-cantidad').value = '';
    await _loadAll();
  }
};

window._promoverLider = async function(alianza, miembro, ejecutor) {
  if (!confirm(`¿Promover a ${miembro} como líder de ${alianza}?`)) return;
  const r = await fetch(_API('/promover'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({alianza, miembro, ejecutor})
  }).then(r=>r.json());
  _toast(r.msg, r.ok);
  if (r.ok) await _loadAll();
};

window._degradarLider = async function(alianza, lider_objetivo, ejecutor) {
  const msg = lider_objetivo === ejecutor
    ? `¿Renunciar a tu rol de líder en ${alianza}?`
    : `¿Degradar a ${lider_objetivo} a miembro en ${alianza}?`;
  if (!confirm(msg)) return;
  const r = await fetch(_API('/degradar'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({alianza, lider_objetivo, ejecutor})
  }).then(r=>r.json());
  _toast(r.msg, r.ok);
  if (r.ok) await _loadAll();
};

window._reclamarTropas = async function(jugador_huesped, ciudad_huesped, unidad, cantidad) {
  const cantInput = prompt(`¿Cuántos ${unidad} reclamar? (disponibles: ${_fmtNum(cantidad)})`, cantidad);
  if (cantInput === null) return;
  const cant = Math.floor(Number(cantInput));
  if (cant <= 0 || cant > cantidad) return _toast('Cantidad inválida', false);

  const r = await fetch(_API('/reclamar'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({
      jugador_dueño: _jugador,
      jugador_huesped,
      ciudad_huesped,
      unidades: {[unidad]: cant}
    })
  }).then(r=>r.json());
  _toast(r.msg, r.ok);
  if (r.ok) await _loadAll();
};
