/**
 * frontend/js/screens/alliance.js
 * Eternal Warriors v3.0 — Pantalla de Alianzas
 */

const _API = (path) => `/api/alliances${path}`;

// ── Helpers ───────────────────────────────────────────────────────────────────

function _fmtNum(n) {
  if (!n) return '0';
  n = Number(n);
  if (n >= 1e15) return (n/1e15).toFixed(2)+'Qa';
  if (n >= 1e12) return (n/1e12).toFixed(2)+'T';
  if (n >= 1e9)  return (n/1e9).toFixed(2)+'G';
  if (n >= 1e6)  return (n/1e6).toFixed(2)+'M';
  if (n >= 1e3)  return (n/1e3).toFixed(1)+'K';
  return n.toLocaleString('es');
}

function _tag(color, text) {
  return `<span style="
    display:inline-block;padding:2px 8px;border-radius:3px;font-size:10px;
    letter-spacing:1px;font-family:'Cinzel',serif;
    background:${color}22;border:1px solid ${color}55;color:${color};
  ">${text}</span>`;
}

function _card(content, extra='') {
  return `<div style="
    background:rgba(12,15,28,0.85);border:1px solid rgba(201,168,76,0.2);
    border-radius:8px;padding:20px;margin-bottom:16px;${extra}
  ">${content}</div>`;
}

function _section(title, content) {
  return `
    <div style="margin-bottom:24px;">
      <div style="
        font-family:'Cinzel',serif;font-size:11px;letter-spacing:3px;
        color:#c9a84c;text-transform:uppercase;margin-bottom:12px;
        border-bottom:1px solid rgba(201,168,76,0.2);padding-bottom:8px;
      ">${title}</div>
      ${content}
    </div>`;
}

function _btn(label, onclick, color='#c9a84c', small=false) {
  return `<button onclick="${onclick}" style="
    background:transparent;border:1px solid ${color}55;color:${color};
    font-family:'Cinzel',serif;font-size:${small?'10':'11'}px;letter-spacing:1px;
    padding:${small?'5px 10px':'8px 16px'};border-radius:4px;cursor:pointer;
    transition:all 0.2s;margin:3px;
    " onmouseover="this.style.background='${color}22'" onmouseout="this.style.background='transparent'">
    ${label}
  </button>`;
}

function _input(id, placeholder, type='text') {
  return `<input id="${id}" type="${type}" placeholder="${placeholder}" style="
    background:rgba(255,255,255,0.04);border:1px solid rgba(201,168,76,0.25);
    color:#e8d5a3;font-family:'Rajdhani',sans-serif;font-size:13px;
    padding:8px 12px;border-radius:4px;width:100%;box-sizing:border-box;
    margin-bottom:8px;outline:none;
  ">`;
}

function _toast(el, msg, ok=true) {
  const t = document.createElement('div');
  t.style.cssText = `
    position:fixed;bottom:80px;left:50%;transform:translateX(-50%);
    background:${ok?'rgba(76,175,80,0.9)':'rgba(220,80,60,0.9)'};
    color:#fff;font-family:'Cinzel',serif;font-size:12px;letter-spacing:1px;
    padding:10px 24px;border-radius:6px;z-index:9999;
    animation:fadeIn 0.2s ease;
  `;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}


// ── Render principal ──────────────────────────────────────────────────────────

export async function render(container, jugador, ciudad) {
  container.innerHTML = `<div style="
    max-width:900px;margin:0 auto;padding:20px;
    font-family:'Rajdhani',sans-serif;color:#c8b88a;
  ">
    <div style="font-family:'Cinzel',serif;font-size:20px;color:#c9a84c;
      letter-spacing:3px;margin-bottom:24px;text-align:center;">
      🤝 ALIANZAS
    </div>
    <div id="ali-content">Cargando...</div>
  </div>`;

  await _loadAll(jugador, ciudad);
}

async function _loadAll(jugador, ciudad) {
  const el = document.getElementById('ali-content');
  if (!el) return;

  try {
    const [rMia, rAll, rPrest] = await Promise.all([
      fetch(_API(`/${jugador}`)).then(r=>r.json()),
      fetch(_API('')).then(r=>r.json()),
      fetch(_API(`/${jugador}/tropas_prestadas`)).then(r=>r.json()),
    ]);

    let html = '';

    // ── Mi alianza ────────────────────────────────────────────────────────────
    if (rMia.alianza) {
      const a = rMia;
      html += _section('MI ALIANZA', _card(`
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
          <span style="font-family:'Cinzel',serif;font-size:16px;color:#e8d080;">${a.alianza}</span>
          ${a.es_lider ? _tag('#c9a84c','LÍDER') : _tag('#8899aa','MIEMBRO')}
        </div>
        <div style="font-size:12px;color:#8899aa;margin-bottom:14px;">
          ${a.miembros.length} / 50 miembros
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px;">
          ${a.miembros.map(m => `
            <div style="
              background:rgba(201,168,76,0.06);border:1px solid rgba(201,168,76,0.2);
              border-radius:4px;padding:4px 10px;font-family:'Cinzel',serif;font-size:11px;
              color:${m===a.lider?'#c9a84c':'#8899aa'};
            ">
              ${m===a.lider?'👑 ':''}{${m}}
            </div>
          `).join('')}
        </div>
        ${a.es_lider && a.solicitudes.length > 0 ? `
          <div style="border-top:1px solid rgba(201,168,76,0.15);padding-top:12px;margin-top:4px;">
            <div style="font-family:'Cinzel',serif;font-size:10px;letter-spacing:2px;
              color:#c9a84c;margin-bottom:8px;">SOLICITUDES PENDIENTES</div>
            ${a.solicitudes.map(s => `
              <div style="display:flex;align-items:center;justify-content:space-between;
                padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
                <span style="font-size:13px;">${s}</span>
                <div>
                  ${_btn('✓ Aceptar', `_aceptarSolicitud('${a.alianza}','${s}','${jugador}')`, '#4caf50', true)}
                </div>
              </div>
            `).join('')}
          </div>
        ` : ''}
        <div style="margin-top:14px;">
          ${_btn('Salir de la alianza', `_salirAlianza('${a.alianza}','${jugador}','${jugador}')`, '#e07050', true)}
        </div>
      `));

    } else {
      // Sin alianza — crear o solicitar
      html += _section('MI ALIANZA', `
        <div style="color:#8899aa;font-size:13px;margin-bottom:16px;">
          No perteneces a ninguna alianza.
        </div>
        ${_card(`
          <div style="font-family:'Cinzel',serif;font-size:12px;color:#c9a84c;
            margin-bottom:10px;letter-spacing:2px;">CREAR NUEVA</div>
          ${_input('ali-nombre-nueva','Nombre de la alianza')}
          ${_btn('Crear alianza', `_crearAlianza('${jugador}')`, '#c9a84c')}
        `)}
        ${_card(`
          <div style="font-family:'Cinzel',serif;font-size:12px;color:#c9a84c;
            margin-bottom:10px;letter-spacing:2px;">UNIRSE A EXISTENTE</div>
          ${_input('ali-nombre-unirse','Nombre de la alianza')}
          ${_btn('Solicitar unión', `_solicitarUnion('${jugador}')`, '#7899cc')}
        `)}
      `);
    }

    // ── Tropas prestadas en mis ciudades ──────────────────────────────────────
    const prest = rPrest.tropas_prestadas_en_mis_ciudades || {};
    const ciudadesPrest = Object.entries(prest).filter(([,arr]) => arr.length > 0);

    if (ciudadesPrest.length > 0) {
      let pHtml = '';
      for (const [nomCiudad, entradas] of ciudadesPrest) {
        pHtml += `<div style="margin-bottom:12px;">
          <div style="font-size:11px;color:#8899aa;font-family:'Cinzel',serif;
            letter-spacing:1px;margin-bottom:6px;">${nomCiudad}</div>`;
        for (const p of entradas) {
          pHtml += `<div style="
            display:flex;align-items:center;justify-content:space-between;
            padding:6px 12px;background:rgba(201,168,76,0.04);
            border:1px solid rgba(201,168,76,0.12);border-radius:4px;margin-bottom:4px;
          ">
            <span style="font-size:13px;">
              <span style="color:#8899aa;font-size:11px;">${p.jugador} · </span>
              ${p.unidad} × ${_fmtNum(p.cantidad)}
            </span>
            <span style="font-size:10px;color:#666;">desde ${p.ciudad_origen}</span>
          </div>`;
        }
        pHtml += `</div>`;
      }
      html += _section('TROPAS ALIADAS EN MIS CIUDADES', _card(pHtml));
    }

    // ── Prestar tropas ────────────────────────────────────────────────────────
    if (rMia.alianza) {
      const aliados = rMia.miembros.filter(m => m !== jugador);
      if (aliados.length > 0) {
        // Obtener ciudades del jugador para el selector
        const rCity = await fetch(`/api/city/${jugador}`).then(r=>r.json());
        const misciudades = rCity.cities || [];

        html += _section('PRESTAR TROPAS', _card(`
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
            <div>
              <div style="font-size:11px;color:#8899aa;margin-bottom:4px;">Ciudad origen (mía)</div>
              <select id="prest-ciudad-orig" style="
                width:100%;background:rgba(255,255,255,0.04);
                border:1px solid rgba(201,168,76,0.25);color:#e8d5a3;
                font-family:'Rajdhani',sans-serif;font-size:13px;
                padding:8px;border-radius:4px;
              ">
                ${misciudades.map(c=>`<option value="${c}">${c}</option>`).join('')}
              </select>
            </div>
            <div>
              <div style="font-size:11px;color:#8899aa;margin-bottom:4px;">Aliado receptor</div>
              <select id="prest-aliado" style="
                width:100%;background:rgba(255,255,255,0.04);
                border:1px solid rgba(201,168,76,0.25);color:#e8d5a3;
                font-family:'Rajdhani',sans-serif;font-size:13px;
                padding:8px;border-radius:4px;
              " onchange="_cargarCiudadesAliado(this.value)">
                ${aliados.map(a=>`<option value="${a}">${a}</option>`).join('')}
              </select>
            </div>
          </div>
          <div style="margin-bottom:10px;">
            <div style="font-size:11px;color:#8899aa;margin-bottom:4px;">Ciudad destino (aliado)</div>
            <select id="prest-ciudad-dest" style="
              width:100%;background:rgba(255,255,255,0.04);
              border:1px solid rgba(201,168,76,0.25);color:#e8d5a3;
              font-family:'Rajdhani',sans-serif;font-size:13px;
              padding:8px;border-radius:4px;
            "><option>Cargando...</option></select>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px;">
            <div>
              <div style="font-size:11px;color:#8899aa;margin-bottom:4px;">Unidad</div>
              ${_input('prest-unidad','Ej: EXPLORADOR')}
            </div>
            <div>
              <div style="font-size:11px;color:#8899aa;margin-bottom:4px;">Cantidad</div>
              ${_input('prest-cantidad','Ej: 1000','number')}
            </div>
          </div>
          ${_btn('Prestar tropas', `_prestarTropas('${jugador}')`, '#7899cc')}
        `));
      }
    }

    // ── Alianzas existentes ───────────────────────────────────────────────────
    const todas = Object.values(rAll.alianzas || {});
    if (todas.length > 0 && !rMia.alianza) {
      html += _section('ALIANZAS EXISTENTES', todas.map(a => _card(`
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <span style="font-family:'Cinzel',serif;font-size:14px;color:#e8d080;">
              ${a.nombre}
            </span>
            <span style="font-size:11px;color:#8899aa;margin-left:10px;">
              ${a.miembros.length}/50 miembros
            </span>
          </div>
          <div>
            ${_tag(a.tipo==='vitaminizado'?'#aa66cc':'#4caf50', a.tipo.toUpperCase())}
          </div>
        </div>
        <div style="font-size:11px;color:#8899aa;margin-top:6px;">
          Líder: ${a.lider} · Miembros: ${a.miembros.join(', ')}
        </div>
      `)).join(''));
    }

    el.innerHTML = html;

    // Cargar ciudades del primer aliado si hay panel de préstamo
    if (rMia.alianza) {
      const primerAliado = rMia.miembros.find(m => m !== jugador);
      if (primerAliado) await _cargarCiudadesAliado(primerAliado);
    }

  } catch(e) {
    el.innerHTML = `<div style="color:#e07050;">Error cargando alianzas: ${e.message}</div>`;
  }
}


// ── Acciones ──────────────────────────────────────────────────────────────────

window._crearAlianza = async function(jugador) {
  const nombre = document.getElementById('ali-nombre-nueva')?.value?.trim();
  if (!nombre) return _toast(null, 'Escribe un nombre', false);
  const r = await fetch(_API('/crear'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({jugador, nombre})
  }).then(r=>r.json());
  _toast(null, r.msg, r.ok);
  if (r.ok) await _loadAll(jugador, null);
};

window._solicitarUnion = async function(jugador) {
  const alianza = document.getElementById('ali-nombre-unirse')?.value?.trim();
  if (!alianza) return _toast(null, 'Escribe el nombre de la alianza', false);
  const r = await fetch(_API('/solicitar'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({jugador, alianza})
  }).then(r=>r.json());
  _toast(null, r.msg, r.ok);
};

window._aceptarSolicitud = async function(alianza, solicitante, lider) {
  const r = await fetch(_API('/aceptar'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({alianza, solicitante, lider})
  }).then(r=>r.json());
  _toast(null, r.msg, r.ok);
  if (r.ok) await _loadAll(lider, null);
};

window._salirAlianza = async function(alianza, jugador, ejecutor) {
  if (!confirm(`¿Salir de la alianza ${alianza}?`)) return;
  const r = await fetch(_API('/salir'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({alianza, jugador, ejecutor})
  }).then(r=>r.json());
  _toast(null, r.msg, r.ok);
  if (r.ok) await _loadAll(jugador, null);
};

window._cargarCiudadesAliado = async function(aliado) {
  const sel = document.getElementById('prest-ciudad-dest');
  if (!sel) return;
  try {
    const r = await fetch(`/api/city/${aliado}`).then(r=>r.json());
    const ciudades = r.cities || [];
    sel.innerHTML = ciudades.map(c=>`<option value="${c}">${c}</option>`).join('');
  } catch {
    sel.innerHTML = '<option>Error</option>';
  }
};

window._prestarTropas = async function(jugador_dueño) {
  const ciudad_origen  = document.getElementById('prest-ciudad-orig')?.value;
  const jugador_huesped = document.getElementById('prest-aliado')?.value;
  const ciudad_destino = document.getElementById('prest-ciudad-dest')?.value;
  const unidad         = document.getElementById('prest-unidad')?.value?.trim().toUpperCase();
  const cantidad       = parseInt(document.getElementById('prest-cantidad')?.value || '0');

  if (!unidad || cantidad <= 0) return _toast(null, 'Completa todos los campos', false);

  const r = await fetch(_API('/prestar'), {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({
      jugador_dueño, ciudad_origen,
      jugador_huesped, ciudad_destino,
      unidades: {[unidad]: cantidad}
    })
  }).then(r=>r.json());
  _toast(null, r.msg, r.ok);
  if (r.ok) await _loadAll(jugador_dueño, null);
};

export function cleanup() {}
