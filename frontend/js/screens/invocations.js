/**
 * frontend/js/screens/invocations.js
 * Pantalla EJÉRCITO — colas de cuarteles e invocaciones de templos
 */

let _jugador = '', _ciudad = '', _ticker = null, _interacting = false;

// ── Formatters ────────────────────────────────────────────────────────────────
function _fmt(n) {
  if (n == null) return '—';
  n = Number(n);
  if (!isFinite(n)) return '∞';
  if (n >= 1e15) return (n/1e15).toFixed(1)+'Pd';
  if (n >= 1e12) return (n/1e12).toFixed(1)+'B';
  if (n >= 1e9)  return (n/1e9).toFixed(1)+'M';
  if (n >= 1e6)  return (n/1e6).toFixed(1)+'K';
  return Math.floor(n).toLocaleString('es-CO');
}

function _fmtT(seg) {
  if (!seg || seg <= 0) return '—';
  seg = Math.round(seg);
  const d = Math.floor(seg / 86400);
  const h = Math.floor((seg % 86400) / 3600);
  const m = Math.floor((seg % 3600) / 60);
  const s = seg % 60;
  if (d > 0) return `${d}d ${h}h ${m}m`;
  if (h > 0) return `${h}h ${m}m ${s}s`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

// ── Labels ────────────────────────────────────────────────────────────────────
const LABELS = {
  ALDEANO:'Aldeano', EXPLORADOR:'Explorador', SACERDOTE:'Sacerdote',
  GUERRERO:'Guerrero', COMANDO:'Comando', MERCENARIO:'Mercenario',
  MARINE:'Marine', CYBORG:'Cyborg', MAGO:'Mago', METAHUMANO:'Metahumano',
  DEMONIO:'Demonio', ANIMA:'Ánima', ESPECTRO:'Espectro', GOLEM:'Gólem',
  CENTAURO:'Centauro', KRAKEN:'Kraken', ALONARDO:'Alonardo',
  MADRESELVA:'Madreselva', COLOSO:'Coloso', FENIX:'Fénix',
  DRAGON_DE_ORO:'Dragón de Oro', CABALLERO_DE_LUZ:'Cab. de Luz',
  ALALAIA:'AlalaiA', EON_SUPREMO:'Éon Supremo',
};
const lbl = k => LABELS[k?.toUpperCase()] ?? k?.replace(/_/g,' ') ?? '—';

// Nivel mínimo sacerdote por invocación (espejo del CSV para feedback en UI)
const NV_MIN_SAC = {
  DEMONIO:7, ANIMA:10, ESPECTRO:13, GOLEM:18, CENTAURO:24, KRAKEN:28,
  ALONARDO:30, MADRESELVA:33, COLOSO:35, FENIX:36, DRAGON_DE_ORO:37,
  CABALLERO_DE_LUZ:38, ALALAIA:39, EON_SUPREMO:40,
};

const TROPAS_BASICAS = [
  'ALDEANO','EXPLORADOR','SACERDOTE','GUERRERO','COMANDO',
  'MERCENARIO','MARINE','CYBORG','MAGO','METAHUMANO'
];
const INVOCACIONES = [
  'DEMONIO','ANIMA','ESPECTRO','GOLEM','CENTAURO','KRAKEN',
  'ALONARDO','MADRESELVA','COLOSO','FENIX','DRAGON_DE_ORO',
  'CABALLERO_DE_LUZ','ALALAIA','EON_SUPREMO',
];

// ── Estilos ───────────────────────────────────────────────────────────────────
const SS = `
  background:#060810;border:1px solid #1a1a2e;color:#b0a080;
  padding:7px 9px;border-radius:4px;font-family:'Cinzel',serif;
  font-size:10px;width:100%;box-sizing:border-box;outline:none;
`;
const IS = `
  background:#060810;border:1px solid #1a1a2e;color:#e8e0d0;
  padding:7px 9px;border-radius:4px;font-size:11px;
  width:100%;box-sizing:border-box;outline:none;
`;

// ── Toast ─────────────────────────────────────────────────────────────────────
function _toast(msg, ok=true) {
  const t = document.createElement('div');
  t.style.cssText = `
    position:fixed;bottom:80px;left:50%;transform:translateX(-50%);
    background:${ok?'rgba(60,140,80,0.95)':'rgba(180,60,50,0.95)'};
    color:#fff;font-family:'Cinzel',serif;font-size:11px;letter-spacing:1px;
    padding:10px 24px;border-radius:4px;z-index:9999;
    box-shadow:0 4px 16px rgba(0,0,0,0.6);
    animation:_tin 0.2s ease;
  `;
  if (!document.getElementById('_tinstyle')) {
    const s = document.createElement('style');
    s.id = '_tinstyle';
    s.textContent = `@keyframes _tin{from{opacity:0;transform:translateX(-50%) translateY(8px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}`;
    document.head.appendChild(s);
  }
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(()=>{t.style.opacity='0';t.style.transition='opacity 0.3s';setTimeout(()=>t.remove(),350);},3500);
}

// ── Estado compartido para los forms (persiste entre re-renders del ticker) ───
const _STATE = {
  cuartel_tipo:   'CUARTEL_1',
  cuartel_unidad: 'EXPLORADOR',
  cuartel_cant:   '100',
  templo_tipo:    'TEMPLO_1',
  templo_unidad:  'DEMONIO',
  templo_cant:    '1',
};

function _saveState() {
  const g = id => document.getElementById(id)?.value;
  _STATE.cuartel_tipo   = g('prod-cuartel-tipo')   ?? _STATE.cuartel_tipo;
  _STATE.cuartel_unidad = g('prod-cuartel-unidad') ?? _STATE.cuartel_unidad;
  _STATE.cuartel_cant   = g('prod-cuartel-cant')   ?? _STATE.cuartel_cant;
  _STATE.templo_tipo    = g('prod-templo-tipo')     ?? _STATE.templo_tipo;
  _STATE.templo_unidad  = g('prod-templo-unidad')   ?? _STATE.templo_unidad;
  _STATE.templo_cant    = g('prod-templo-cant')     ?? _STATE.templo_cant;
}

// ── Render colas ──────────────────────────────────────────────────────────────
function _renderCola(c) {
  const pct       = c.porcentaje ?? 0;
  const esTemplo  = c.tipo?.toUpperCase().startsWith('TEMPLO');
  const color     = esTemplo ? '#9b6ad6' : '#c9a84c';
  const icono     = esTemplo ? '🌟' : '⚔';
  return `
    <div style="background:#0a0c14;border:1px solid ${color}33;border-radius:6px;padding:10px 14px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <div style="font-family:'Cinzel',serif;font-size:11px;color:${color};">
          ${icono} ${lbl(c.tipo)} — ${lbl(c.unidad)}
        </div>
        <div style="display:flex;gap:8px;align-items:center;">
          <span style="font-size:10px;color:#666;">${_fmt(c.completadas)}/${_fmt(c.cantidad_total)}</span>
          <button onclick="window._cancelarCola('${c.tipo}')"
            style="background:none;border:1px solid #2a2a3a;color:#555;
              border-radius:3px;padding:1px 7px;cursor:pointer;font-size:10px;
              transition:color 0.15s,border-color 0.15s;"
            onmouseover="this.style.color='#e07050';this.style.borderColor='#e0705066'"
            onmouseout="this.style.color='#555';this.style.borderColor='#2a2a3a'">✕</button>
        </div>
      </div>
      <div style="background:#111;border-radius:3px;height:5px;margin-bottom:6px;">
        <div style="background:${color};width:${Math.min(100,pct)}%;height:100%;
          border-radius:3px;transition:width 0.5s;"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:10px;color:#555;">
        <span>⏱ Siguiente: ${_fmtT(c.seg_para_siguiente)}</span>
        <span>Total restante: ${_fmtT(c.tiempo_total_restante_seg)}</span>
      </div>
    </div>`;
}

function _renderColas(colas) {
  if (!colas.length) return `
    <div style="text-align:center;color:#333;font-family:'Cinzel',serif;
      font-size:11px;padding:24px;border:1px solid #111;border-radius:6px;margin-bottom:16px;">
      No hay colas activas en ${_ciudad}
    </div>`;
  return `
    <div style="margin-bottom:20px;">
      <div style="font-family:'Cinzel',serif;font-size:10px;color:#666;
        letter-spacing:2px;margin-bottom:8px;">▼ COLAS ACTIVAS</div>
      <div style="display:flex;flex-direction:column;gap:8px;">
        ${colas.map(_renderCola).join('')}
      </div>
    </div>`;
}

// ── Formularios ───────────────────────────────────────────────────────────────
function _formCuartel() {
  const optsC = ['CUARTEL_1','CUARTEL_2']
    .map(k=>`<option value="${k}" ${_STATE.cuartel_tipo===k?'selected':''}>${lbl(k)}</option>`)
    .join('');
  const optsU = TROPAS_BASICAS
    .map(t=>`<option value="${t}" ${_STATE.cuartel_unidad===t?'selected':''}>${lbl(t)}</option>`)
    .join('');
  return `
    <div style="background:#0a0c14;border:1px solid #c9a84c33;border-radius:6px;padding:14px;">
      <div style="font-family:'Cinzel',serif;font-size:11px;color:#c9a84c;
        letter-spacing:1px;margin-bottom:12px;">⚔ CUARTEL</div>
      <div style="display:flex;flex-direction:column;gap:8px;">
        <select id="prod-cuartel-tipo" style="${SS}">${optsC}</select>
        <select id="prod-cuartel-unidad" style="${SS}">${optsU}</select>
        <input id="prod-cuartel-cant" type="number" min="1" value="${_STATE.cuartel_cant}"
          placeholder="Cantidad" style="${IS}">
        <button id="prod-cuartel-btn"
          style="background:rgba(201,168,76,0.1);border:1px solid #c9a84c66;
            color:#c9a84c;padding:8px;border-radius:4px;cursor:pointer;
            font-family:'Cinzel',serif;font-size:10px;width:100%;letter-spacing:1px;
            transition:background 0.15s;"
          onmouseover="this.style.background='rgba(201,168,76,0.2)'"
          onmouseout="this.style.background='rgba(201,168,76,0.1)'">
          + Encolar entrenamiento
        </button>
        <div id="prod-cuartel-msg" style="font-size:10px;color:#888;min-height:14px;text-align:center;"></div>
      </div>
    </div>`;
}

function _formTemplo(nivelSac) {
  const optsT = ['TEMPLO_1','TEMPLO_2','TEMPLO_3']
    .map(k=>`<option value="${k}" ${_STATE.templo_tipo===k?'selected':''}>${lbl(k)}</option>`)
    .join('');
  const optsI = INVOCACIONES.map(t => {
    const nmin = NV_MIN_SAC[t] ?? 0;
    const bloq = nmin > nivelSac;
    const sufx = bloq ? ` 🔒 nv${nmin}` : '';
    return `<option value="${t}" ${_STATE.templo_unidad===t?'selected':''}
      ${bloq?'style="color:#555"':''}>${lbl(t)}${sufx}</option>`;
  }).join('');

  return `
    <div style="background:#0a0c14;border:1px solid #9b6ad633;border-radius:6px;padding:14px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <div style="font-family:'Cinzel',serif;font-size:11px;color:#9b6ad6;letter-spacing:1px;">
          🌟 TEMPLO
        </div>
        <div style="font-size:10px;color:#9b6ad6aa;">
          Sacerdote nv${nivelSac}
        </div>
      </div>
      <div style="display:flex;flex-direction:column;gap:8px;">
        <select id="prod-templo-tipo" style="${SS}">${optsT}</select>
        <select id="prod-templo-unidad" style="${SS}">${optsI}</select>
        <input id="prod-templo-cant" type="number" min="1" value="${_STATE.templo_cant}"
          placeholder="Cantidad" style="${IS}">
        <button id="prod-templo-btn"
          style="background:rgba(155,106,214,0.1);border:1px solid #9b6ad666;
            color:#9b6ad6;padding:8px;border-radius:4px;cursor:pointer;
            font-family:'Cinzel',serif;font-size:10px;width:100%;letter-spacing:1px;
            transition:background 0.15s;"
          onmouseover="this.style.background='rgba(155,106,214,0.2)'"
          onmouseout="this.style.background='rgba(155,106,214,0.1)'">
          + Encolar invocación
        </button>
        <div id="prod-templo-msg" style="font-size:10px;color:#888;min-height:14px;text-align:center;"></div>
      </div>
    </div>`;
}

// ── Render principal ──────────────────────────────────────────────────────────
async function _render() {
  const wrap = document.getElementById('prod-wrap');
  if (!wrap) return;
  if (_interacting) return; // usuario interactuando con forms — no re-renderizar

  // Guardar estado actual del form antes de re-renderizar
  _saveState();

  let colas = [], mana = 0, nivelSac = 21; // fallback conservador; backend valida
  try {
    const r = await fetch(`/api/queues/${_jugador}/${encodeURIComponent(_ciudad)}`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const d = await r.json();
    colas    = d.colas || [];
    mana     = d.mana  || 0;
  } catch(e) {
    console.error('[EJÉRCITO] Error cargando colas:', e);
  }

  // nivel sacerdote — validado en backend; no se expone por /api/city

  wrap.innerHTML = `
    <div style="padding:16px;max-width:900px;margin:0 auto;">
      <!-- Header -->
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <div style="font-family:'Cinzel',serif;font-size:16px;color:#c9a84c;letter-spacing:2px;">
          ⚔ EJÉRCITO — ${_ciudad}
        </div>
        <div style="font-size:12px;color:#9b6ad6;font-family:'Cinzel',serif;">
          💜 Maná: ${_fmt(mana)}
        </div>
      </div>

      ${_renderColas(colas)}

      <!-- Formularios -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
        ${_formCuartel()}
        ${_formTemplo(nivelSac)}
      </div>
    </div>`;

  _bindForms();
}

// ── Bind de botones ───────────────────────────────────────────────────────────
function _bindForms() {
  // Pausar ticker mientras el usuario interactúa con los formularios
  const _markInteract = () => { _interacting = true; };
  const _unmarkInteract = () => { _interacting = false; };
  ['prod-cuartel-tipo','prod-cuartel-unidad','prod-cuartel-cant',
   'prod-templo-tipo','prod-templo-unidad','prod-templo-cant'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('focus',    _markInteract);
    el.addEventListener('mousedown',_markInteract);
    el.addEventListener('blur',     _unmarkInteract);
    el.addEventListener('change',   _unmarkInteract);
  });

  // ── Cuartel ──
  document.getElementById('prod-cuartel-btn')?.addEventListener('click', async () => {
    const tipo    = document.getElementById('prod-cuartel-tipo')?.value;
    const unidad  = document.getElementById('prod-cuartel-unidad')?.value;
    const cantRaw = document.getElementById('prod-cuartel-cant')?.value;
    const cantidad = Math.floor(Number(cantRaw));
    const msgEl   = document.getElementById('prod-cuartel-msg');

    if (!tipo || !unidad) return;
    if (cantidad <= 0) {
      if (msgEl) msgEl.style.color='#e07050', msgEl.textContent='Cantidad inválida';
      return;
    }
    if (msgEl) msgEl.style.color='#888', msgEl.textContent='Enviando…';

    try {
      const r = await fetch(`/api/queues/${_jugador}/${encodeURIComponent(_ciudad)}/cuartel`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({tipo, unidad, cantidad}),
      });
      const d = await r.json();
      if (d.ok) {
        _toast(`✓ ${cantidad} ${lbl(unidad)} encolados en ${lbl(tipo)}`);
        _render();
      } else {
        if (msgEl) msgEl.style.color='#e07050', msgEl.textContent=d.msg;
        _toast(d.msg, false);
      }
    } catch(e) {
      if (msgEl) msgEl.style.color='#e07050', msgEl.textContent='Error de red';
      _toast('Error de conexión', false);
    }
  });

  // ── Templo ──
  document.getElementById('prod-templo-btn')?.addEventListener('click', async () => {
    const tipo       = document.getElementById('prod-templo-tipo')?.value;
    const invocacion = document.getElementById('prod-templo-unidad')?.value;
    const cantRaw    = document.getElementById('prod-templo-cant')?.value;
    const cantidad   = Math.floor(Number(cantRaw));
    const msgEl      = document.getElementById('prod-templo-msg');

    if (!tipo || !invocacion) return;
    if (cantidad <= 0) {
      if (msgEl) msgEl.style.color='#e07050', msgEl.textContent='Cantidad inválida';
      return;
    }

    // Validación de nivel sacerdote delegada al backend

    if (msgEl) msgEl.style.color='#888', msgEl.textContent='Enviando…';

    try {
      const r = await fetch(`/api/queues/${_jugador}/${encodeURIComponent(_ciudad)}/templo`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({tipo, invocacion, cantidad}),
      });
      const d = await r.json();
      if (d.ok) {
        _toast(`✓ ${cantidad} ${lbl(invocacion)} encolados en ${lbl(tipo)}`);
        _render();
      } else {
        if (msgEl) msgEl.style.color='#e07050', msgEl.textContent=d.msg;
        _toast(d.msg, false);
      }
    } catch(e) {
      if (msgEl) msgEl.style.color='#e07050', msgEl.textContent='Error de red';
      _toast('Error de conexión', false);
    }
  });
}

// ── Cancelar cola ─────────────────────────────────────────────────────────────
window._cancelarCola = async function(tipo) {
  if (!confirm(`¿Cancelar la cola de ${lbl(tipo)}?`)) return;
  try {
    const r = await fetch(
      `/api/queues/${_jugador}/${encodeURIComponent(_ciudad)}/${tipo}`,
      {method:'DELETE'}
    );
    const d = await r.json();
    if (d.ok) { _toast(`Cola de ${lbl(tipo)} cancelada`); _render(); }
    else       { _toast(d.msg, false); }
  } catch { _toast('Error de conexión', false); }
};

// ── Export ────────────────────────────────────────────────────────────────────
export async function render(container, jugador, ciudad) {
  _jugador = jugador;
  _ciudad  = ciudad;

  container.innerHTML = `
    <div id="prod-wrap" style="
      height:calc(100vh - 60px);overflow-y:auto;
      background:#060810;color:#e8e0d0;
    "></div>`;

  await _render();

  if (_ticker) clearInterval(_ticker);
  _ticker = setInterval(_render, 5000);
}

export function cleanup() {
  if (_ticker) { clearInterval(_ticker); _ticker = null; }
}
