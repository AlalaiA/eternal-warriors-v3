/**
 * building_menu.js  — Eternal Warriors v3.0
 * 
 * API pública (exportada):
 *   openBuildingMenu(edificio, jugador, ciudad, cityData)
 *   closeBuildingMenu()
 */

// ── Panel singleton ────────────────────────────────────────────────────────────
let _panel = null;
let _ticker = null;

function _ensurePanel() {
  if (_panel) return _panel;
  _panel = document.createElement('div');
  _panel.id = 'ew-building-menu';
  _panel.style.cssText = `
    position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
    background:#0d0d1a;border:1px solid #c9a84c;border-radius:10px;
    padding:20px;min-width:340px;max-width:460px;max-height:80vh;overflow-y:auto;
    color:#e8e0d0;z-index:9999;box-shadow:0 8px 40px #000c;
    font-family:'Cinzel',serif;font-size:13px;
  `;
  // Click fuera cierra
  document.addEventListener('mousedown', (e) => {
    if (_panel && _panel.style.display !== 'none' && !_panel.contains(e.target)) {
      _closePanel();
    }
  });
  document.body.appendChild(_panel);
  return _panel;
}

function _closePanel() {
  if (_ticker) { clearInterval(_ticker); _ticker = null; }
  if (_panel)  _panel.style.display = 'none';
}

// ── Formateo ──────────────────────────────────────────────────────────────────
function _fmt(n) {
  if (n == null || n === undefined) return '—';
  n = Number(n); if (!isFinite(n) || isNaN(n)) return '—';
  const a = Math.abs(n), s = n < 0 ? '-' : '';
  if (a>=1e99) return s+(a/1e99).toFixed(1)+'Ct';
  if (a>=1e90) return s+(a/1e90).toFixed(1)+'No';
  if (a>=1e60) return s+(a/1e60).toFixed(1)+'Sx';
  if (a>=1e33) return s+(a/1e33).toFixed(1)+'Dc';
  if (a>=1e30) return s+(a/1e30).toFixed(1)+'No';
  if (a>=1e27) return s+(a/1e27).toFixed(1)+'Oc';
  if (a>=1e24) return s+(a/1e24).toFixed(1)+'Sp';
  if (a>=1e21) return s+(a/1e21).toFixed(1)+'Sx';
  if (a>=1e18) return s+(a/1e18).toFixed(1)+'Qn';
  if (a>=1e15) return s+(a/1e15).toFixed(1)+'Pd';
  if (a>=1e12) return s+(a/1e12).toFixed(1)+'T';
  if (a>=1e9)  return s+(a/1e9).toFixed(1)+'B';
  if (a>=1e6)  return s+(a/1e6).toFixed(1)+'M';
  if (a>=1e3)  return s+(a/1e3).toFixed(1)+'K';
  return s + Math.round(a).toLocaleString('es');
}

function _fmtTime(s) {
  s = Math.floor(s);
  if (s <= 0) return '✅ Listo';
  const h = Math.floor(s/3600), m = Math.floor((s%3600)/60), sec = s%60;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${sec}s`;
  return `${sec}s`;
}

function _btnStyle(bg, full=true) {
  return `background:${bg};border:1px solid #444;color:#e8e0d0;padding:7px 14px;
          border-radius:5px;cursor:pointer;${full?'width:100%;':''}font-size:12px;
          font-family:'Cinzel',serif;margin-top:6px;`;
}

// ── Render principal ──────────────────────────────────────────────────────────
async function _show(edificio, jugador, ciudad, cityData) {
  const p = _ensurePanel();
  p.style.display = 'block';
  p.innerHTML = `<div style="color:#c9a84c;text-align:center">⏳ Cargando ${edificio.replace(/_/g,' ')}…</div>`;

  let info;
  try {
    const r = await fetch(`/api/buildings/${jugador}/${ciudad}/${edificio}`);
    if (!r.ok) { const e = await r.json(); throw new Error(e.detail || r.status); }
    info = await r.json();
  } catch(e) {
    p.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="color:#c9a84c">${edificio.replace(/_/g,' ')}</span>
        <button onclick="document.getElementById('ew-building-menu').style.display='none'"
                style="background:none;border:none;color:#888;font-size:1.2em;cursor:pointer">✕</button>
      </div>
      <p style="color:#f66;margin-top:12px">Error: ${e.message}</p>`;
    return;
  }

  _render(info, edificio, jugador, ciudad, cityData);
}

function _render(info, edificio, jugador, ciudad, cityData) {
  if (_ticker) { clearInterval(_ticker); _ticker = null; }
  const p = _ensurePanel();
  const nombre = edificio.replace(/_/g,' ');
  const esCuartel = /CUARTEL/.test(edificio);
  const esTemplo  = /TEMPLO/.test(edificio);

  // Costo HTML
  const iconos = {madera:'🪵',piedra:'🪨',hierro:'⚙️',oro:'🪙',carbon:'🔥'};
  let costoRows = '';
  if (info.costo) {
    costoRows = Object.entries(info.costo)
      .filter(([,v]) => v > 0)
      .map(([mat, val]) => `
        <div style="display:flex;justify-content:space-between;padding:2px 0">
          <span style="color:#aaa">${iconos[mat]||''} ${mat}</span>
          <span>${_fmt(val)}</span>
        </div>`).join('');
  }

  // Stat HTML
  let statHTML = '';
  if (info.stat_nombre) {
    statHTML = `
      <div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid #222">
        <span style="color:#aaa">${info.stat_nombre.replace(/_/g,' ')}</span>
        <span>${_fmt(info.stat_actual)} ${info.stat_siguiente != null ? '→ <b style="color:#c9a84c">'+_fmt(info.stat_siguiente)+'</b>' : ''}</span>
      </div>`;
  }

  // Sección de acción (obra / subir / máx)
  let accionHTML = '';
  if (info.en_construccion) {
    const tr = info.tiempo_restante_seg ?? 0;
    const dur = info.tiempo_seg || 3600;
    accionHTML = `
      <div style="margin-top:14px;padding:10px;background:#0a0a18;border-radius:6px;border:1px solid #333">
        <div>🔨 Construyendo nivel ${info.nivel_siguiente}…</div>
        <div id="bm-t" style="font-size:1.15em;color:#c9a84c;margin:6px 0">${_fmtTime(tr)}</div>
        <div style="background:#1a1a2a;border-radius:3px;height:6px">
          <div id="bm-b" style="background:#c9a84c;height:6px;border-radius:3px;width:${Math.min(100,((dur-tr)/dur*100)).toFixed(1)}%"></div>
        </div>
        <button onclick="window._ewCancelObra('${edificio}','${jugador}','${ciudad}')"
                style="${_btnStyle('#5a1a1a')}">❌ Cancelar obra (50% devuelto)</button>
      </div>`;
    // Ticker cuenta regresiva
    let restante = tr;
    _ticker = setInterval(() => {
      restante = Math.max(0, restante - 1);
      const te = document.getElementById('bm-t');
      const be = document.getElementById('bm-b');
      if (te) te.textContent = _fmtTime(restante);
      if (be) be.style.width = Math.min(100, ((dur-restante)/dur*100)).toFixed(1) + '%';
      if (restante <= 0) { clearInterval(_ticker); _ticker = null; _show(edificio, jugador, ciudad, cityData); }
    }, 1000);

  } else if (info.puede_subir && info.costo) {
    accionHTML = `
      <div style="margin-top:14px">
        <div style="color:#aaa;font-size:.82em;margin-bottom:4px">Costo → Nivel ${info.nivel_siguiente}:</div>
        <div style="background:#0a0a18;padding:8px;border-radius:5px;margin-bottom:6px">${costoRows}</div>
        <div style="color:#aaa;font-size:.82em">
          ⏱ Tiempo: ${_fmtTime(info.tiempo_seg)}
          ${info.reduccion_universidad_pct > 0
            ? `<span style="color:#4a9;margin-left:6px">🎓 -${info.reduccion_universidad_pct}% (Universidad)</span>`
            : ''}
        </div>
        <button onclick="window._ewIniciarObra('${edificio}','${jugador}','${ciudad}')"
                style="${_btnStyle('#1a3a1a')}">⬆️ Construir nivel ${info.nivel_siguiente}</button>
      </div>`;
  } else if (info.nivel_actual >= info.max_nivel) {
    accionHTML = `<div style="margin-top:12px;color:#aaa;text-align:center">🏆 Nivel máximo</div>`;
  }

  // Cola (cuartel/templo)
  let colaHTML = '';
  if (esCuartel || esTemplo) {
    const colaLabel = esCuartel ? '⚔️ Entrenar tropas' : '🔮 Invocar criaturas';
    colaHTML = `
      <div style="margin-top:14px;padding-top:12px;border-top:1px solid #222">
        <button onclick="window._ewOpenCola('${edificio}','${jugador}','${ciudad}')"
                style="${_btnStyle('#1a1a3a')};">${colaLabel}</button>
      </div>`;
  }

  // Escondite UI
  if (edificio === 'ESCONDITE') {
    colaHTML = `
      <div style="margin-top:14px;padding-top:12px;border-top:1px solid #222">
        <button onclick="window._ewOpenEscondite('${jugador}','${ciudad}')"
                style="${_btnStyle('#1a2a1a')};">🕳️ Gestionar Escondite</button>
      </div>`;
  }

  p.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
      <span style="color:#c9a84c;font-size:1.05em">${nombre}</span>
      <button onclick="document.getElementById('ew-building-menu').style.display='none'"
              style="background:none;border:none;color:#888;font-size:1.3em;cursor:pointer">✕</button>
    </div>
    <div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid #222">
      <span style="color:#aaa">Nivel</span>
      <span><b>${info.nivel_actual}</b> / ${info.max_nivel}</span>
    </div>
    ${statHTML}
    ${accionHTML}
    ${colaHTML}`;
}

// ── Acciones globales (referenciadas desde onclick en HTML) ───────────────────
window._ewIniciarObra = async function(edificio, jugador, ciudad) {
  try {
    const r = await fetch(`/api/buildings/${jugador}/${ciudad}/${edificio}/upgrade`, {method:'POST'});
    const d = await r.json();
    if (!r.ok) { alert('Error: ' + (d.detail || JSON.stringify(d))); return; }
    _show(edificio, jugador, ciudad, null);
  } catch(e) { alert('Error de red: ' + e.message); }
};

window._ewCancelObra = async function(edificio, jugador, ciudad) {
  if (!confirm('¿Cancelar obra? Solo recuperarás el 50% de los recursos.')) return;
  try {
    const r = await fetch(`/api/buildings/${jugador}/${ciudad}/${edificio}/upgrade`, {method:'DELETE'});
    const d = await r.json();
    if (!r.ok) { alert('Error: ' + (d.detail || JSON.stringify(d))); return; }
    _show(edificio, jugador, ciudad, null);
  } catch(e) { alert('Error de red: ' + e.message); }
};

window._ewOpenCola = async function(edificio, jugador, ciudad) {
  const p = document.getElementById('ew-building-menu');
  if (!p) return;

  const esCuartel = /CUARTEL/.test(edificio);
  const nombre = edificio.replace(/_/g,' ');
  const endpoint = esCuartel ? 'cuartel' : 'templo';

  // Cargar colas activas y unit_levels en paralelo
  let todasColas = [], unitLevels = {};
  try {
    const [rq, rc] = await Promise.all([
      fetch(`/api/queues/${jugador}/${ciudad}`),
      fetch(`/api/city/${jugador}/${ciudad}`)
    ]);
    const dq = await rq.json();
    const dc = await rc.json();
    todasColas = (dq.colas || []).filter(c => c.tipo === edificio);
    unitLevels = dc.unit_levels || {};
  } catch(e) { /* sin datos */ }

  // Mostrar hasta 2 colas activas de este edificio
  let colaActivaHTML = todasColas.map((cola, idx) => {
    const completadas = cola.completadas || 0;
    const total       = cola.cantidad_total || 1;
    const pendientes  = cola.pendientes || 0;
    const pct         = (completadas/total*100).toFixed(1);
    const trSig       = cola.seg_para_siguiente || 0;
    const trTotal     = cola.tiempo_total_restante_seg || 0;
    return `
      <div style="background:#0a0a18;border:1px solid #3a3a20;border-radius:6px;padding:10px;margin-bottom:8px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
          <span style="color:#c9a84c;font-size:.9em">📋 Cola ${idx+1}: ${cola.unidad.replace(/_/g,' ')}</span>
          <span style="color:#aaa;font-size:.78em">⏱ ${_fmtTime(trSig)}/ud</span>
        </div>
        <div style="display:flex;justify-content:space-between;color:#aaa;font-size:.78em;margin-bottom:4px">
          <span>${_fmt(completadas)} / ${_fmt(total)}</span>
          <span>${_fmtTime(trTotal)} restante</span>
        </div>
        <div style="background:#1a1a2a;border-radius:3px;height:4px;margin:4px 0">
          <div style="background:#c9a84c;height:4px;border-radius:3px;width:${pct}%"></div>
        </div>
        <button onclick="window._ewCancelarCola('${edificio}','${jugador}','${ciudad}',${idx})"
                style="background:#5a1a1a;border:1px solid #444;color:#e8e0d0;padding:3px 8px;
                       border-radius:4px;cursor:pointer;width:100%;margin-top:5px;font-size:.78em">
          ❌ Cancelar cola ${idx+1}
        </button>
      </div>`;
  }).join('');

  // Unidades disponibles
  const CUARTEL_UNITS = ['EXPLORADOR','GUERRERO','SACERDOTE','COMANDO','MERCENARIO','MARINE','CYBORG','MAGO','METAHUMANO'];
  // Invocaciones con nivel mínimo de sacerdote requerido
  const TEMPLO_UNITS = [
    {key:'DEMONIO',         niv:7},  {key:'ANIMA',           niv:10},
    {key:'ESPECTRO',        niv:13}, {key:'GOLEM',           niv:18},
    {key:'CENTAURO',        niv:24}, {key:'KRAKEN',          niv:28},
    {key:'ALONARDO',        niv:30}, {key:'MADRESELVA',      niv:33},
    {key:'COLOSO',          niv:35}, {key:'FENIX',           niv:36},
    {key:'DRAGON_DE_ORO',   niv:37}, {key:'CABALLERO_DE_LUZ',niv:38},
    {key:'ALALAIA',         niv:39}, {key:'EON_SUPREMO',     niv:40},
  ];

  const nivelSac = unitLevels['SACERDOTE'] || unitLevels['sacerdote'] || 1;
  const numColasActivas = todasColas.length;
  const puedeEncolar = numColasActivas < 2;

  const unidadRows = esCuartel
    ? CUARTEL_UNITS.map(u => `
      <div style="display:flex;justify-content:space-between;align-items:center;
                  padding:3px 0;border-bottom:1px solid #111">
        <span style="color:#ddd;font-size:.85em">${u.replace(/_/g,' ')}</span>
        <div style="display:flex;gap:4px;align-items:center">
          <input id="qty-${u}" type="number" min="1" max="999999999" value="1"
                 style="width:52px;background:#111;border:1px solid #333;color:#e8e0d0;
                        border-radius:3px;padding:2px 4px;font-size:.82em"
                 ${puedeEncolar?'':'disabled'}>
          <button onclick="window._ewEncolarUnidad('${edificio}','${jugador}','${ciudad}','${u}',document.getElementById('qty-${u}').value,'${endpoint}')"
                  style="background:${puedeEncolar?'#1a2a4a':'#111'};border:1px solid #333;
                         color:${puedeEncolar?'#c9a84c':'#555'};padding:3px 8px;
                         border-radius:3px;cursor:${puedeEncolar?'pointer':'not-allowed'};font-size:.82em"
                  ${puedeEncolar?'':'disabled'}>▶</button>
        </div>
      </div>`).join('')
    : TEMPLO_UNITS.map(({key:u, niv}) => {
        const disponible = nivelSac >= niv && puedeEncolar;
        const bloqueado  = nivelSac < niv;
        return `
      <div style="display:flex;justify-content:space-between;align-items:center;
                  padding:3px 0;border-bottom:1px solid #111;
                  opacity:${bloqueado?'0.4':'1'}">
        <span style="color:${bloqueado?'#666':'#ddd'};font-size:.85em">
          ${u.replace(/_/g,' ')}
          <span style="color:#888;font-size:.75em"> Sac.${niv}</span>
        </span>
        <div style="display:flex;gap:4px;align-items:center">
          <input id="qty-${u}" type="number" min="1" max="999999999" value="1"
                 style="width:52px;background:#111;border:1px solid #333;color:#e8e0d0;
                        border-radius:3px;padding:2px 4px;font-size:.82em"
                 ${disponible?'':'disabled'}>
          <button onclick="window._ewEncolarUnidad('${edificio}','${jugador}','${ciudad}','${u}',document.getElementById('qty-${u}').value,'${endpoint}')"
                  style="background:${disponible?'#2a1a4a':'#111'};border:1px solid #333;
                         color:${disponible?'#c9a84c':'#555'};padding:3px 8px;
                         border-radius:3px;cursor:${disponible?'pointer':'not-allowed'};font-size:.82em"
                  ${disponible?'':'disabled'}>▶</button>
        </div>
      </div>`;}).join('');

  p.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <span style="color:#c9a84c">${nombre} — ${esCuartel ? 'Entrenar' : 'Invocar'}</span>
      <button onclick="document.getElementById('ew-building-menu').style.display='none'"
              style="background:none;border:none;color:#888;font-size:1.2em;cursor:pointer">✕</button>
    </div>
    <div id="ew-colas-wrap"></div>
    ${todasColas.length >= 2 ? '<div style="color:#888;font-size:.8em;margin-bottom:8px;text-align:center">2 colas activas — cancela una para encolar más</div>' : ''}
    <div style="max-height:300px;overflow-y:auto">${unidadRows}</div>`;

  // Ticker en tiempo real para las colas
  if (_ticker) { clearInterval(_ticker); _ticker = null; }
  let _colasSeg = todasColas.map(cola => ({
    ...cola,
    seg_para_siguiente: cola.seg_para_siguiente || 0,
    tiempo_total_restante_seg: cola.tiempo_total_restante_seg || 0,
  }));

  function _renderColas() {
    const wrap = document.getElementById('ew-colas-wrap');
    if (!wrap) return;
    wrap.innerHTML = _colasSeg.map((cola, idx) => {
      const completadas = cola.completadas || 0;
      const total       = cola.cantidad_total || 1;
      const pct         = Math.min(100, (completadas/total*100)).toFixed(1);
      const trSig       = Math.max(0, cola.seg_para_siguiente);
      const trTotal     = Math.max(0, cola.tiempo_total_restante_seg);
      return `
        <div style="background:#0a0a18;border:1px solid #3a3a20;border-radius:6px;padding:10px;margin-bottom:8px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
            <span style="color:#c9a84c;font-size:.9em">📋 Cola ${idx+1}: ${cola.unidad.replace(/_/g,' ')}</span>
            <span style="color:#aaa;font-size:.78em">⏱ ${_fmtTime(trSig)}/ud</span>
          </div>
          <div style="display:flex;justify-content:space-between;color:#aaa;font-size:.78em;margin-bottom:4px">
            <span>${_fmt(completadas)} / ${_fmt(total)}</span>
            <span>${_fmtTime(trTotal)} restante</span>
          </div>
          <div style="background:#1a1a2a;border-radius:3px;height:4px;margin:4px 0">
            <div style="background:#c9a84c;height:4px;border-radius:3px;width:${pct}%;transition:width 1s linear"></div>
          </div>
          <button onclick="window._ewCancelarCola('${edificio}','${jugador}','${ciudad}',${idx})"
                  style="background:#5a1a1a;border:1px solid #444;color:#e8e0d0;padding:3px 8px;
                         border-radius:4px;cursor:pointer;width:100%;margin-top:5px;font-size:.78em">
            ❌ Cancelar cola ${idx+1}
          </button>
        </div>`;
    }).join('');
  }

  _renderColas();

  if (_colasSeg.length > 0) {
    _ticker = setInterval(() => {
      _colasSeg = _colasSeg.map(cola => {
        let trSig = Math.max(0, (cola.seg_para_siguiente||0) - 1);
        let trTotal = Math.max(0, (cola.tiempo_total_restante_seg||0) - 1);
        let completadas = cola.completadas || 0;
        const tpu = cola.tiempo_por_unidad_seg || 1;
        // Cuando seg_para_siguiente llega a 0, completar una unidad
        if (trSig <= 0 && completadas < (cola.cantidad_total||1)) {
          completadas += 1;
          trSig = tpu; // resetear timer para siguiente unidad
        }
        return {...cola, seg_para_siguiente:trSig, tiempo_total_restante_seg:trTotal, completadas};
      });
      _renderColas();
    }, 1000);
  }
};

window._ewEncolarUnidad = async function(edificio, jugador, ciudad, unidad, cantidad, endpoint, nivelSac) {
  const qty = Math.max(1, parseInt(cantidad) || 1);
  try {
    const body = endpoint === 'cuartel'
      ? { tipo: edificio, unidad, cantidad: qty }
      : { tipo: edificio, invocacion: unidad, cantidad: qty };
    const r = await fetch(`/api/queues/${jugador}/${ciudad}/${endpoint}`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(body)
    });
    const d = await r.json();
    if (!r.ok) { alert('Error: ' + (d.detail || JSON.stringify(d))); return; }
    // Reabrir el panel de cola con estado actualizado
    window._ewOpenCola(edificio, jugador, ciudad);
  } catch(e) { alert('Error de red: ' + e.message); }
};

window._ewCancelarCola = async function(edificio, jugador, ciudad, idx=0) {
  if (!confirm(`¿Cancelar la cola ${idx+1}?`)) return;
  try {
    const r = await fetch(`/api/queues/${jugador}/${ciudad}/${edificio}?idx=${idx}`, {method:'DELETE'});
    const d = await r.json();
    if (!r.ok) { alert('Error: ' + (d.detail || JSON.stringify(d))); return; }
    window._ewOpenCola(edificio, jugador, ciudad);
  } catch(e) { alert('Error de red: ' + e.message); }
};

// ── Exports ───────────────────────────────────────────────────────────────────
export function openBuildingMenu(edificio, jugador, ciudad, cityData) {
  _show(edificio, jugador, ciudad, cityData);
}

export function closeBuildingMenu() {
  _closePanel();
}

// ── Escondite ─────────────────────────────────────────────────────────────────
window._ewOpenEscondite = async function(jugador, ciudad) {
  const p = document.getElementById('ew-building-menu');
  if (!p) return;

  p.innerHTML = `<div style="color:#c9a84c;text-align:center">⏳ Cargando escondite…</div>`;

  let estado;
  try {
    const r = await fetch(`/api/escondite/${jugador}/${ciudad}`);
    estado = (await r.json()).estado;
  } catch(e) { p.innerHTML = `<p style="color:#f66">Error: ${e.message}</p>`; return; }

  const { nivel, cap_ejercito, cap_material, escondido, tropas_usadas, tropas_libres } = estado;
  const MATS = ['MADERA','PIEDRA','HIERRO','CARBON','ORO'];
  const TROPAS = ['ALDEANO','EXPLORADOR','SACERDOTE','GUERRERO','COMANDO','MERCENARIO','MARINE','CYBORG','MAGO','METAHUMANO'];
  const ICO = {MADERA:'🪵',PIEDRA:'🪨',HIERRO:'⚙️',CARBON:'🔥',ORO:'🪙'};

  const matRows = MATS.map(m => {
    const esc = escondido.materiales[m]||0;
    const libre = Math.max(0, cap_material - esc);
    return `
      <div style="border-bottom:1px solid #111;padding:4px 0">
        <div style="display:flex;justify-content:space-between;font-size:.85em;margin-bottom:3px">
          <span>${ICO[m]||''} ${m}</span>
          <span style="color:#c9a84c">${_fmt(esc)} / ${_fmt(cap_material)}</span>
        </div>
        <div style="display:flex;gap:4px">
          <input id="esc-mat-${m}" type="number" min="1" max="999999999999" value="1"
                 style="flex:1;background:#111;border:1px solid #333;color:#e8e0d0;border-radius:3px;padding:2px 4px;font-size:.8em">
          <button onclick="window._ewEscMat('${jugador}','${ciudad}','${m}',document.getElementById('esc-mat-${m}').value,'meter')"
                  style="background:#1a3a1a;border:1px solid #333;color:#4a9;padding:2px 6px;border-radius:3px;cursor:pointer;font-size:.8em">▼</button>
          <button onclick="window._ewEscMat('${jugador}','${ciudad}','${m}',document.getElementById('esc-mat-${m}').value,'sacar')"
                  style="background:#3a1a1a;border:1px solid #333;color:#c44;padding:2px 6px;border-radius:3px;cursor:pointer;font-size:.8em">▲</button>
        </div>
      </div>`;
  }).join('');

  const tropRows = TROPAS.map(t => {
    const esc = escondido.tropas[t]||0;
    return `
      <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #111;padding:3px 0">
        <span style="font-size:.82em;flex:1">${t.replace(/_/g,' ')} <span style="color:#c9a84c">${_fmt(esc)}</span></span>
        <input id="esc-trop-${t}" type="number" min="1" max="999999999999" value="1"
               style="width:60px;background:#111;border:1px solid #333;color:#e8e0d0;border-radius:3px;padding:2px 4px;font-size:.78em">
        <button onclick="window._ewEscTrop('${jugador}','${ciudad}','${t}',document.getElementById('esc-trop-${t}').value,'meter')"
                style="background:#1a3a1a;border:1px solid #333;color:#4a9;padding:2px 5px;border-radius:3px;cursor:pointer;font-size:.78em;margin-left:2px">▼</button>
        <button onclick="window._ewEscTrop('${jugador}','${ciudad}','${t}',document.getElementById('esc-trop-${t}').value,'sacar')"
                style="background:#3a1a1a;border:1px solid #333;color:#c44;padding:2px 5px;border-radius:3px;cursor:pointer;font-size:.78em;margin-left:2px">▲</button>
      </div>`;
  }).join('');

  p.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <span style="color:#c9a84c">Escondite Nv.${nivel}</span>
      <button onclick="document.getElementById('ew-building-menu').style.display='none'"
              style="background:none;border:none;color:#888;font-size:1.2em;cursor:pointer">✕</button>
    </div>
    <div style="color:#aaa;font-size:.8em;margin-bottom:8px">
      🪖 Tropas: ${_fmt(tropas_usadas)} / ${_fmt(cap_ejercito)} · Libres: ${_fmt(tropas_libres)}
    </div>
    <div style="color:#888;font-size:.75em;margin-bottom:6px">▼ meter al escondite · ▲ sacar</div>
    <div style="font-size:.8em;color:#c9a84c;margin:6px 0 3px">MATERIALES</div>
    ${matRows}
    <div style="font-size:.8em;color:#c9a84c;margin:8px 0 3px">TROPAS</div>
    <div style="max-height:200px;overflow-y:auto">${tropRows}</div>`;
};

window._ewEscMat = async function(jugador, ciudad, material, cantidad, accion) {
  const qty = Math.max(1, parseFloat(cantidad) || 1);
  const endpoint = accion === 'meter' ? 'meter_material' : 'sacar_material';
  try {
    const r = await fetch(`/api/escondite/${jugador}/${ciudad}/${endpoint}`, {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({material, cantidad: qty})
    });
    const d = await r.json();
    if (!d.ok) { alert(d.msg); return; }
    window._ewOpenEscondite(jugador, ciudad);
  } catch(e) { alert('Error: ' + e.message); }
};

window._ewEscTrop = async function(jugador, ciudad, tropa, cantidad, accion) {
  const qty = Math.max(1, parseInt(cantidad) || 1);
  const endpoint = accion === 'meter' ? 'meter_tropas' : 'sacar_tropas';
  try {
    const r = await fetch(`/api/escondite/${jugador}/${ciudad}/${endpoint}`, {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({tropa, cantidad: qty})
    });
    const d = await r.json();
    if (!d.ok) { alert(d.msg); return; }
    window._ewOpenEscondite(jugador, ciudad);
  } catch(e) { alert('Error: ' + e.message); }
};
