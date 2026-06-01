/**
 * ETERNAL WARRIORS v3.0 — reports.js
 * Pantalla de Informes: Batalla y Espionaje
 */
'use strict';

let _jugador = '', _ciudad = '';
let _ordenes  = [];
let _tab      = 'batalla';  // 'batalla' | 'espionaje'
let _syncTimer = null;

// ── Formato ───────────────────────────────────────────────────────────────────

function _fmt(n) {
  if (n == null) return '—';
  n = Number(n);
  if (!isFinite(n) || isNaN(n)) return '∞';
  const a = Math.abs(n), s = n < 0 ? '-' : '';
  if (a >= 1e18) return s + (a/1e18).toFixed(1) + 'Qn';
  if (a >= 1e15) return s + (a/1e15).toFixed(1) + 'Pd';
  if (a >= 1e12) return s + (a/1e12).toFixed(1) + 'T';
  if (a >= 1e9)  return s + (a/1e9).toFixed(1)  + 'B';
  if (a >= 1e6)  return s + (a/1e6).toFixed(1)  + 'M';
  if (a >= 1e3)  return s + (a/1e3).toFixed(1)  + 'K';
  if (a >= 1)    return s + Math.round(a).toLocaleString('es');
  if (a > 0)     return s + a.toFixed(2);  // fracciones menores a 1
  return '0';
}

function _fmtFecha(ts) {
  if (!ts) return '?';
  const d = new Date(ts * 1000);
  return d.toLocaleDateString('es', {day:'2-digit',month:'2-digit',year:'2-digit'}) +
         ' ' + d.toLocaleTimeString('es', {hour:'2-digit',minute:'2-digit'});
}

// ── Estilos ───────────────────────────────────────────────────────────────────

const CSS = {
  panel:  `background:rgba(8,10,20,0.85);border:1px solid rgba(201,168,76,0.2);border-radius:8px;padding:16px;margin-bottom:10px;`,
  title:  `color:#c9a84c;font-family:'Cinzel',serif;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;border-bottom:1px solid rgba(201,168,76,0.15);padding-bottom:6px;`,
  row:    `display:flex;justify-content:space-between;align-items:center;padding:3px 0;font-size:11px;font-family:'Cinzel',serif;border-bottom:1px solid rgba(255,255,255,0.04);`,
  badge:  (col, bg) => `background:${bg};color:${col};padding:2px 10px;border-radius:10px;font-size:10px;font-family:'Cinzel',serif;letter-spacing:1px;`,
  tab:    (activo) => `flex:1;padding:10px;background:${activo?'rgba(201,168,76,0.12)':'transparent'};
    border:none;border-bottom:${activo?'2px solid #c9a84c':'2px solid transparent'};
    color:${activo?'#c9a84c':'#666'};font-family:'Cinzel',serif;font-size:11px;
    letter-spacing:2px;cursor:pointer;transition:all 0.2s;`,
};

const NIVEL_ESP_LABEL = ['☠ Detectado','● Mínimo','●● Recursos','●●● Ejército','●●●● Completo','●●●●● Escondite'];
const NIVEL_ESP_COLOR = ['#e05050','#888','#c9a84c','#6ba3e0','#9b6ad6','#50d0c0'];

// ── Render principal ──────────────────────────────────────────────────────────

export async function render(container, jugador, ciudad) {
  _jugador = jugador;
  _ciudad  = ciudad;

  container.innerHTML = `
    <div style="display:flex;flex-direction:column;height:calc(100vh - 120px);padding:12px;box-sizing:border-box;gap:10px;">
      <!-- Tabs -->
      <div style="display:flex;border-bottom:1px solid rgba(201,168,76,0.2);">
        <button id="tab-batalla"  onclick="window._repTab('batalla')"  style="${CSS.tab(true)}">⚔ BATALLA</button>
        <button id="tab-espionaje" onclick="window._repTab('espionaje')" style="${CSS.tab(false)}">🕵 ESPIONAJE</button>
      </div>
      <!-- Contenido -->
      <div id="rep-content" style="flex:1;overflow-y:auto;"></div>
    </div>`;

  window._repTab = (tab) => {
    _tab = tab;
    document.getElementById('tab-batalla').style.cssText  = CSS.tab(tab === 'batalla');
    document.getElementById('tab-espionaje').style.cssText = CSS.tab(tab === 'espionaje');
    _renderContent();
  };

  await _cargar();
  _renderContent();
  _syncTimer = setInterval(_cargar, 15000);
}

async function _cargar() {
  try {
    // Cargar activas
    const r1 = await fetch(`/api/orders/${_jugador}`);
    const d1 = await r1.json();
    let todas = d1.ordenes || [];

    // Cargar historial (completadas con resultado)
    try {
      const r2 = await fetch(`/api/orders/historial/${_jugador}`);
      if (r2.ok) {
        const d2 = await r2.json();
        const ids = new Set(todas.map(o => o.id));
        (d2.ordenes || []).forEach(o => { if (!ids.has(o.id)) todas.push(o); });
      }
    } catch (_) {}

    _ordenes = todas;
  } catch (e) {
    console.error('reports._cargar:', e);
  }
  _renderContent();
}

function _renderContent() {
  const el = document.getElementById('rep-content');
  if (!el) return;
  if (_tab === 'batalla') _renderBatalla(el);
  else _renderEspionaje(el);
}

// ── BATALLA ───────────────────────────────────────────────────────────────────

function _renderBatalla(el) {
  // Incluir ataques Y espionajes detectados (que desencadenaron combate)
  const ataques = _ordenes
    .filter(o => o.resultado && (
      o.tipo === 'ATAQUE' ||
      (o.tipo === 'ESPIONAJE' && o.resultado.detectado)
    ))
    .sort((a, b) => (b.inicio || 0) - (a.inicio || 0));

  if (!ataques.length) {
    el.innerHTML = `<div style="color:#555;font-family:'Cinzel',serif;font-size:12px;text-align:center;padding:40px;">Sin informes de batalla</div>`;
    return;
  }

  el.innerHTML = ataques.map(o => _cardBatalla(o)).join('');
}

function _cardBatalla(o) {
  const r = o.resultado;

  // Para espionajes detectados, usar el combate_completo
  const combate = r.combate_completo || r;
  const victoria = combate.victoria_atacante ?? r.victoria ?? false;
  const victoriaPor = r.victoria_por || (victoria ? 'combate' : 'derrota');
  const col   = victoria ? '#4caf50' : '#e05050';
  const bg    = victoria ? 'rgba(76,175,80,0.08)' : 'rgba(224,80,80,0.08)';

  const ICONO_MAP = {
    'combate':     '⚔ VICTORIA EN COMBATE',
    'resistencia': '🛡 VICTORIA POR RESISTENCIA',
    'valor':       '✦ VICTORIA POR VALOR',
    'derrota':     '💀 DERROTA',
  };
  const icono = ICONO_MAP[victoriaPor] || (victoria ? '⚔ VICTORIA' : '💀 DERROTA');
  const esEspio = o.tipo === 'ESPIONAJE';

  // Bajas propias
  const bajas_atk = combate.bajas_atk?.[_jugador.toUpperCase()] || {};

  // Bajas enemigas — aplanar todos los jugadores defensores
  const bajas_def = Object.values(combate.bajas_def || {}).reduce((acc, b) => {
    if (typeof b === 'object') Object.entries(b).forEach(([k,v]) => acc[k] = (acc[k]||0) + v);
    return acc;
  }, {});

  // Saqueo
  const saqueo   = combate.saqueo || r.saqueo || o.botin || {};
  const haySaqueo = Object.values(saqueo).some(v => v >= 1);

  // Muralla
  const muralla_resistio      = combate.muralla_atravesada === false;
  const muralla_atravesada_ok = combate.muralla_atravesada === true;

  // XP
  const xp = combate.xp_por_jugador_atk?.[_jugador.toUpperCase()] ||
             r.xp?.[_jugador.toUpperCase()] || 0;

  // Rondas
  const rondas = combate.rondas ?? r.rondas ?? 0;

  // Mensaje
  const mensaje = combate.mensaje || r.mensaje || '';

  return `
    <div style="${CSS.panel} border-left:3px solid ${col};">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
        <div>
          <div style="color:${col};font-family:'Cinzel',serif;font-size:13px;font-weight:600;">
            ${esEspio ? '🕵 ' : ''}${icono}
          </div>
          <div style="color:#888;font-size:10px;margin-top:2px;font-family:'Cinzel',serif;">
            ${_fmtFecha(o.inicio)} &nbsp;·&nbsp; ${o.ciudad_origen||'?'} → ${o.ciudad_dest || `(${Math.round(o.x_dest||0)}, ${Math.round(o.y_dest||0)})`}
          </div>
          <div style="color:#666;font-size:10px;font-family:'Cinzel',serif;">
            📍 (${Math.round(o.x_orig||0)}, ${Math.round(o.y_orig||0)}) → (${Math.round(o.x_dest||0)}, ${Math.round(o.y_dest||0)})
          </div>
          ${esEspio ? `<div style="color:#e07050;font-size:10px;font-family:'Cinzel',serif;">⚠ Espionaje detectado — combate automático</div>` : ''}
          ${r.victoria_por === 'valor' ? `<div style="color:#c9a84c;font-size:10px;font-family:'Cinzel',serif;">✦ ${r.valor_razon||''}</div>` : ''}
          ${r.victoria_por === 'resistencia' ? `<div style="color:#6ba3e0;font-size:10px;font-family:'Cinzel',serif;">🛡 Sobrevivió las 9 rondas</div>` : ''}
          ${mensaje ? `<div style="color:#888;font-size:10px;margin-top:2px;font-family:'Cinzel',serif;">${mensaje}</div>` : ''}
        </div>
        <div style="text-align:right;">
          <span style="${CSS.badge(col, bg)}">${icono}</span>
          ${rondas > 0 ? `<div style="color:#666;font-size:10px;margin-top:4px;">${rondas} ronda${rondas>1?'s':''}</div>` : ''}
        </div>
      </div>

      ${muralla_resistio ? `
        <div style="color:#e07050;font-family:'Cinzel',serif;font-size:11px;padding:6px;
          background:rgba(200,100,50,0.08);border-radius:4px;margin-bottom:8px;">
          🛡 La muralla resistió el ataque
        </div>` : ''}
      ${muralla_atravesada_ok ? `
        <div style="color:#4caf50;font-family:'Cinzel',serif;font-size:11px;padding:6px;
          background:rgba(76,175,80,0.06);border-radius:4px;margin-bottom:8px;">
          🛡 Muralla atravesada
        </div>` : ''}

      <div style="${CSS.title}">Ejército enviado</div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;">
        ${Object.entries(o.unidades||{}).map(([k,v]) =>
          `<span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
            padding:2px 8px;border-radius:4px;font-size:10px;font-family:'Cinzel',serif;color:#b0a080;">
            ${k}: ${_fmt(v)}</span>`
        ).join('') || '<span style="color:#555;font-size:10px;">—</span>'}
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
        <div>
          <div style="${CSS.title}">Bajas propias</div>
          ${Object.keys(bajas_atk).length === 0
            ? '<div style="color:#4caf50;font-size:10px;">Sin bajas</div>'
            : Object.entries(bajas_atk).filter(([,v])=>v>0).map(([k,v])=>
                `<div style="${CSS.row}"><span style="color:#e08080">${k}</span><span style="color:#e8e0d0">-${_fmt(v)}</span></div>`
              ).join('')}
        </div>
        <div>
          <div style="${CSS.title}">Bajas enemigas</div>
          ${Object.keys(bajas_def).length === 0
            ? '<div style="color:#666;font-size:10px;">—</div>'
            : Object.entries(bajas_def).filter(([,v])=>v>0).map(([k,v])=>
                `<div style="${CSS.row}"><span style="color:#80c080">${k}</span><span style="color:#e8e0d0">-${_fmt(v)}</span></div>`
              ).join('')}
        </div>
      </div>

      ${haySaqueo ? `
        <div style="${CSS.title}">Botín saqueado</div>
        <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px;">
          ${Object.entries(saqueo).filter(([,v])=>v>=1).map(([k,v])=>
            `<span style="background:rgba(201,168,76,0.1);border:1px solid rgba(201,168,76,0.3);
              padding:2px 10px;border-radius:4px;font-size:10px;font-family:'Cinzel',serif;color:#c9a84c;">
              +${_fmt(v)} ${k}</span>`
          ).join('')}
        </div>` : ''}

      ${xp > 0 ? `
        <div style="color:#9b6ad6;font-size:10px;font-family:'Cinzel',serif;text-align:right;">
          ✦ +${_fmt(xp)} XP
        </div>` : ''}
    </div>`;
}

// ── ESPIONAJE ─────────────────────────────────────────────────────────────────

function _renderEspionaje(el) {
  const misiones = _ordenes
    .filter(o => o.tipo === 'ESPIONAJE' && o.resultado)
    .sort((a, b) => (b.inicio || 0) - (a.inicio || 0));

  if (!misiones.length) {
    el.innerHTML = `<div style="color:#555;font-family:'Cinzel',serif;font-size:12px;text-align:center;padding:40px;">Sin informes de espionaje</div>`;
    return;
  }

  el.innerHTML = misiones.map(o => _cardEspionaje(o)).join('');
}

function _cardEspionaje(o) {
  const r          = o.resultado;
  const detectado  = r.detectado;
  const nivel      = r.nivel_espionaje || 0;
  const col        = detectado ? '#e05050' : NIVEL_ESP_COLOR[nivel] || '#c9a84c';
  const bg         = detectado ? 'rgba(224,80,80,0.08)' : 'rgba(201,168,76,0.05)';
  const nivelLabel = detectado ? NIVEL_ESP_LABEL[0] : (NIVEL_ESP_LABEL[nivel] || '?');
  const intel      = r.inteligencia || {};

  return `
    <div style="${CSS.panel} border-left:3px solid ${col};">
      <!-- Cabecera -->
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
        <div>
          <div style="color:${col};font-family:'Cinzel',serif;font-size:13px;font-weight:600;">
            ${detectado ? '⚠ DETECTADO' : '🕵 EXITOSO'}
          </div>
          <div style="color:#888;font-size:10px;margin-top:2px;font-family:'Cinzel',serif;">
            ${_fmtFecha(o.inicio)} &nbsp;·&nbsp; ${o.ciudad_origen||'?'} → ${o.ciudad_dest ? o.ciudad_dest : `(${Math.round(o.x_dest||0)}, ${Math.round(o.y_dest||0)})`}
          </div>
          ${o.ciudad_dest ? `<div style="color:#a09070;font-size:10px;font-family:'Cinzel',serif;">${o.ciudad_dest}</div>` : ''}
        </div>
        <span style="${CSS.badge(col, bg)}">${nivelLabel}</span>
      </div>

      <!-- Sigilo -->
      <div style="color:#666;font-size:10px;font-family:'Cinzel',serif;margin-bottom:8px;">
        Sigilo efectivo: <b style="color:#e8e0d0">${r.sigilo?.toFixed(0) ?? '?'}</b>
      </div>

      ${detectado ? `
        <div style="color:#e07050;font-family:'Cinzel',serif;font-size:11px;padding:6px;
          background:rgba(200,80,50,0.08);border-radius:4px;margin-bottom:8px;">
          ⚠ Detectado — ${r.combate || 'combate automático'}
        </div>` : ''}

      ${!detectado && nivel >= 1 ? `
        <!-- Ciudad/Entidad -->
        <div style="${CSS.title}">
          ${intel.tipo && !intel.muralla && intel.muralla !== 0 ? intel.tipo : 'Ciudad'}
        </div>
        <div style="${CSS.row}">
          <span style="color:#b0a080">Nombre</span>
          <span style="color:#e8e0d0">${intel.nombre || '?'}</span>
        </div>
        ${intel.muralla !== undefined ? `
        <div style="${CSS.row}">
          <span style="color:#b0a080">Muralla</span>
          <span style="color:#e8e0d0">Nv. ${intel.muralla ?? '?'}</span>
        </div>` : ''}
        ${intel.hp ? `
        <div style="${CSS.row}"><span style="color:#b0a080">❤ HP</span><span style="color:#e8e0d0">${_fmt(intel.hp)}</span></div>
        <div style="${CSS.row}"><span style="color:#b0a080">⚔ PA</span><span style="color:#e8e0d0">${_fmt(intel.pa)}</span></div>
        <div style="${CSS.row}"><span style="color:#b0a080">🛡 CA</span><span style="color:#e8e0d0">${_fmt(intel.ca)}</span></div>
        <div style="${CSS.row}"><span style="color:#b0a080">⚡ Destreza</span><span style="color:#e8e0d0">${_fmt(intel.destreza)}</span></div>
        ` : ''}` : ''}

      ${!detectado && nivel >= 2 && intel.recursos ? `
        <!-- Recursos -->
        <div style="${CSS.title} margin-top:10px;">Recursos</div>
        <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px;">
          ${Object.entries(intel.recursos).map(([k,v]) =>
            `<span style="background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);
              padding:2px 8px;border-radius:4px;font-size:10px;font-family:'Cinzel',serif;color:#c9a84c;">
              ${k}: ${_fmt(v)}</span>`
          ).join('')}
        </div>` : ''}

      ${!detectado && nivel >= 3 && intel.ejercito ? `
        <!-- Ejército -->
        <div style="${CSS.title} margin-top:10px;">Ejército</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:2px;">
          ${Object.entries(intel.ejercito).filter(([,v])=>v>0).map(([k,v])=>
            `<div style="${CSS.row}"><span style="color:#b0a080">${k}</span><span style="color:#e8e0d0">${_fmt(v)}</span></div>`
          ).join('') || '<div style="color:#555;font-size:10px;">Sin tropas visibles</div>'}
        </div>` : ''}

      ${!detectado && nivel >= 4 && intel.invocaciones ? `
        <!-- Invocaciones -->
        <div style="${CSS.title} margin-top:10px;">Invocaciones</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:2px;">
          ${Object.entries(intel.invocaciones).filter(([,v])=>v>0).map(([k,v])=>
            `<div style="${CSS.row}"><span style="color:#a080c0">${k}</span><span style="color:#e8e0d0">${_fmt(v)}</span></div>`
          ).join('') || '<div style="color:#555;font-size:10px;">Sin invocaciones</div>'}
        </div>
        <!-- Edificios -->
        <div style="${CSS.title} margin-top:10px;">Edificios</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:2px;">
          ${Object.entries(intel.edificios||{}).filter(([,v])=>v>0).map(([k,v])=>
            `<div style="${CSS.row}"><span style="color:#8080b0">${k.replace(/_/g,' ')}</span><span style="color:#e8e0d0">Nv.${v}</span></div>`
          ).join('')}
        </div>` : ''}

      ${!detectado && nivel >= 5 && intel.escondite ? `
        <!-- Escondite -->
        <div style="${CSS.title} margin-top:10px;">🔒 Escondite</div>
        <div style="${CSS.row}"><span style="color:#b0a080">Materiales</span></div>
        ${Object.entries(intel.escondite.materiales||{}).filter(([,v])=>v>0).map(([k,v])=>
          `<div style="${CSS.row} padding-left:10px;"><span style="color:#888">${k}</span><span style="color:#c9a84c">${_fmt(v)}</span></div>`
        ).join('') || '<div style="color:#555;font-size:10px;padding-left:10px;">Vacío</div>'}
        <div style="${CSS.row}"><span style="color:#b0a080">Tropas</span></div>
        ${Object.entries(intel.escondite.tropas||{}).filter(([,v])=>v>0).map(([k,v])=>
          `<div style="${CSS.row} padding-left:10px;"><span style="color:#888">${k}</span><span style="color:#e8e0d0">${_fmt(v)}</span></div>`
        ).join('') || '<div style="color:#555;font-size:10px;padding-left:10px;">Vacío</div>'}` : ''}

      <!-- Botín -->
      ${r.botin && Object.values(r.botin).some(v=>v>0) ? `
        <div style="${CSS.title} margin-top:10px;">Botín</div>
        ${Object.entries(r.botin).filter(([,v])=>v>0).map(([k,v])=>
          `<div style="${CSS.row}"><span style="color:#b0a080">${k}</span><span style="color:#c9a84c">+${_fmt(v)}</span></div>`
        ).join('')}` : ''}
    </div>`;
}

// ── Cleanup ───────────────────────────────────────────────────────────────────

export function cleanup() {
  if (_syncTimer) { clearInterval(_syncTimer); _syncTimer = null; }
  _ordenes = [];
  delete window._repTab;
}
