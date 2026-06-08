/**
 * frontend/js/screens/messages.js
 * Eternal Warriors v3.0 — Mensajería interna
 *
 * - Bandeja unificada: mensajes directos + mensajes de alianza
 * - Composición: directo (a jugador) o broadcast (a alianza)
 * - Polling 5s con badge de no leídos en el nav
 * - Marcar como leído al abrir; borrar propios
 */

const _MAPI = p => `/api/messages${p}`;

let _jugador   = null;
let _alianza   = null;
let _ticker    = null;
let _vistaActiva = 'bandeja'; // 'bandeja' | 'compose'
let _replyTo   = null; // {jugador, asunto} para responder

// ── Formatters ────────────────────────────────────────────────────────────────
function _fmtTs(ts) {
  if (!ts) return '';
  const d = new Date(ts * 1000);
  const ahora = new Date();
  const diffH = (ahora - d) / 3600000;
  if (diffH < 24) return d.toLocaleTimeString('es', {hour:'2-digit', minute:'2-digit'});
  return d.toLocaleDateString('es', {day:'2-digit', month:'2-digit', year:'2-digit'});
}

function _escHTML(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── Toast ─────────────────────────────────────────────────────────────────────
function _toast(msg, ok=true) {
  const t = document.createElement('div');
  t.style.cssText = `
    position:fixed;bottom:80px;left:50%;transform:translateX(-50%);
    background:${ok?'rgba(60,140,80,0.95)':'rgba(180,60,50,0.95)'};
    color:#fff;font-family:'Cinzel',serif;font-size:11px;letter-spacing:1px;
    padding:10px 24px;border-radius:4px;z-index:9999;
    box-shadow:0 4px 16px rgba(0,0,0,0.6);
  `;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(()=>{t.style.opacity='0';t.style.transition='opacity 0.3s';
    setTimeout(()=>t.remove(),350);}, 3000);
}

// ── Estilos compartidos ───────────────────────────────────────────────────────
const _IS = `background:rgba(255,255,255,0.04);border:1px solid rgba(201,168,76,0.25);
  color:#e8d5a3;font-family:'Rajdhani',sans-serif;font-size:13px;
  padding:8px 12px;border-radius:3px;width:100%;box-sizing:border-box;
  outline:none;margin-bottom:8px;`;

function _btn(label, onclick, color='#c9a84c', small=false) {
  return `<button onclick="${onclick}" style="
    background:transparent;border:1px solid ${color}55;color:${color};
    font-family:'Cinzel',serif;font-size:${small?'9':'11'}px;letter-spacing:1px;
    padding:${small?'4px 9px':'8px 18px'};border-radius:3px;cursor:pointer;
    transition:background 0.15s;margin:3px;"
    onmouseover="this.style.background='${color}22'"
    onmouseout="this.style.background='transparent'">${label}</button>`;
}

// ── Render principal ──────────────────────────────────────────────────────────
export async function render(container, jugador, ciudad) {
  _jugador = jugador?.toUpperCase() ?? jugador;

  // Obtener alianza del jugador
  try {
    const ra = await fetch(`/api/alliances/${_jugador}`).then(r=>r.json());
    _alianza = ra.alianza || null;
  } catch { _alianza = null; }

  container.innerHTML = `
    <div style="max-width:860px;margin:0 auto;padding:20px;
      font-family:'Rajdhani',sans-serif;color:#c8b88a;">
      <div style="font-family:'Cinzel',serif;font-size:18px;color:#c9a84c;
        letter-spacing:4px;margin-bottom:6px;text-align:center;">✉ MENSAJES</div>
      <div style="text-align:center;font-size:10px;color:#445;letter-spacing:2px;
        margin-bottom:24px;font-family:'Cinzel',serif;">ETERNAL WARRIORS</div>
      <div id="msg-wrap"></div>
    </div>`;

  await _loadAll();
  _startPolling();
}

export function cleanup() { _stopPolling(); }

function _startPolling() {
  _stopPolling();
  _ticker = setInterval(_refreshBadgeOnly, 5000);
}
function _stopPolling() {
  if (_ticker) { clearInterval(_ticker); _ticker = null; }
}

// Polling ligero: solo actualiza el badge sin re-renderizar toda la pantalla
async function _refreshBadgeOnly() {
  try {
    const r = await fetch(_MAPI(`/${_jugador}/no_leidos`)).then(r=>r.json());
    _updateNavBadge(r.no_leidos || 0);
  } catch {}
}

function _updateNavBadge(count) {
  // Actualizar badge en el botón de nav si existe
  const navBtn = document.getElementById('nav-msg');
  if (!navBtn) return;
  let badge = navBtn.querySelector('.nav-badge');
  if (count > 0) {
    if (!badge) {
      badge = document.createElement('span');
      badge.className = 'nav-badge';
      badge.style.cssText = `
        position:absolute;top:2px;right:2px;
        background:#c05050;color:#fff;
        font-size:9px;font-family:'Cinzel',serif;
        border-radius:8px;padding:1px 5px;min-width:14px;text-align:center;
        pointer-events:none;
      `;
      navBtn.style.position = 'relative';
      navBtn.appendChild(badge);
    }
    badge.textContent = count > 99 ? '99+' : count;
  } else if (badge) {
    badge.remove();
  }
}

// ── Carga completa ────────────────────────────────────────────────────────────
async function _loadAll() {
  const wrap = document.getElementById('msg-wrap');
  if (!wrap) return;

  try {
    const r = await fetch(_MAPI(`/${_jugador}`)).then(r=>r.json());
    const mensajes = r.mensajes || [];

    // Marcar automáticamente como leídos los que se muestran
    const noLeidos = mensajes
      .filter(m => m.de !== _jugador && !m.leido_por?.includes(_jugador))
      .map(m => m.id);
    if (noLeidos.length) {
      fetch(_MAPI('/leer'), {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({jugador: _jugador, msg_ids: noLeidos})
      });
      _updateNavBadge(0);
    }

    if (_vistaActiva === 'compose') {
      wrap.innerHTML = _renderCompose();
      _bindCompose();
    } else {
      wrap.innerHTML = _renderBandeja(mensajes);
    }

  } catch(e) {
    if (wrap) wrap.innerHTML = `<div style="color:#c05050;text-align:center;
      padding:40px;font-family:'Cinzel',serif;font-size:11px;">
      ERROR · ${_escHTML(e.message)}</div>`;
  }
}

// ── Bandeja ───────────────────────────────────────────────────────────────────
function _renderBandeja(mensajes) {
  const directos = mensajes.filter(m => m.tipo === 'DIRECTO');
  const alianza  = mensajes.filter(m => m.tipo === 'ALIANZA');

  return `
    <div style="display:flex;justify-content:flex-end;margin-bottom:16px;">
      ${_btn('✉ Nuevo mensaje', `_msgNuevo()`, '#c9a84c')}
    </div>

    ${_alianza ? `
      <div style="margin-bottom:28px;">
        <div style="font-family:'Cinzel',serif;font-size:10px;letter-spacing:3px;
          color:#9b6ad6;margin-bottom:10px;border-bottom:1px solid rgba(155,106,214,0.2);
          padding-bottom:6px;">🌐 ALIANZA · ${_escHTML(_alianza)}</div>
        ${alianza.length
          ? alianza.map(m => _renderMsg(m)).join('')
          : `<div style="color:#445;font-size:12px;padding:16px;text-align:center;
               font-family:'Cinzel',serif;">Sin mensajes de alianza</div>`}
        <div style="margin-top:10px;">
          ${_btn(`✉ Mensaje a ${_escHTML(_alianza)}`, `_msgAlianza()`, '#9b6ad6', true)}
        </div>
      </div>` : ''}

    <div>
      <div style="font-family:'Cinzel',serif;font-size:10px;letter-spacing:3px;
        color:#c9a84c;margin-bottom:10px;border-bottom:1px solid rgba(201,168,76,0.15);
        padding-bottom:6px;">✉ MENSAJES DIRECTOS</div>
      ${directos.length
        ? directos.map(m => _renderMsg(m)).join('')
        : `<div style="color:#445;font-size:12px;padding:16px;text-align:center;
             font-family:'Cinzel',serif;">Bandeja vacía</div>`}
    </div>`;
}

function _renderMsg(m) {
  const esPropio  = m.de === _jugador;
  const noLeido   = !esPropio && !m.leido_por?.includes(_jugador);
  const esAlianza = m.tipo === 'ALIANZA';
  const color     = esAlianza ? '#9b6ad6' : '#c9a84c';
  const contraparte = esPropio
    ? (esAlianza ? m.alianza : `→ ${m.para}`)
    : `← ${m.de}`;

  return `
    <div style="
      background:rgba(8,11,22,${noLeido?'0.95':'0.7'});
      border:1px solid ${noLeido?color+'55':'rgba(255,255,255,0.06)'};
      border-left:3px solid ${noLeido?color:'rgba(255,255,255,0.08)'};
      border-radius:4px;padding:12px 16px;margin-bottom:8px;
    ">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;
        margin-bottom:6px;">
        <div style="display:flex;align-items:center;gap:10px;">
          ${noLeido ? `<span style="width:6px;height:6px;border-radius:50%;
            background:${color};display:inline-block;flex-shrink:0;"></span>` : ''}
          <span style="font-family:'Cinzel',serif;font-size:11px;color:${color};">
            ${_escHTML(contraparte)}
          </span>
          ${m.asunto ? `<span style="font-size:12px;color:#aabbcc;font-weight:600;">
            ${_escHTML(m.asunto)}</span>` : ''}
        </div>
        <div style="display:flex;align-items:center;gap:6px;flex-shrink:0;">
          <span style="font-size:10px;color:#445;">${_fmtTs(m.ts)}</span>
          ${!esPropio
            ? _btn('↩', `_msgResponder('${_escHTML(m.de)}','${_escHTML(m.asunto||'')}')`,
                '#7899cc', true)
            : ''}
          ${esPropio
            ? _btn('✕', `_msgBorrar('${m.id}')`, '#c05050', true)
            : ''}
        </div>
      </div>
      <div style="font-size:13px;color:#c8b88a;line-height:1.5;white-space:pre-wrap;
        word-break:break-word;">${_escHTML(m.cuerpo)}</div>
    </div>`;
}

// ── Composición ───────────────────────────────────────────────────────────────
function _renderCompose() {
  const tieneAlianza = !!_alianza;
  const paraVal  = _replyTo?.jugador || '';
  const asuntoVal = _replyTo?.asunto
    ? (_replyTo.asunto.startsWith('Re:') ? _replyTo.asunto : `Re: ${_replyTo.asunto}`)
    : '';

  return `
    <div style="background:rgba(8,11,22,0.9);border:1px solid rgba(201,168,76,0.2);
      border-radius:6px;padding:20px;">
      <div style="font-family:'Cinzel',serif;font-size:11px;letter-spacing:3px;
        color:#c9a84c;margin-bottom:16px;">NUEVO MENSAJE</div>

      <!-- Tipo -->
      <div style="margin-bottom:12px;">
        <div style="font-size:10px;color:#667;letter-spacing:1px;
          font-family:'Cinzel',serif;margin-bottom:6px;">TIPO</div>
        <div style="display:flex;gap:8px;">
          <label style="display:flex;align-items:center;gap:6px;cursor:pointer;">
            <input type="radio" name="msg-tipo" value="DIRECTO" id="msg-tipo-dir"
              ${!tieneAlianza||paraVal?'checked':''} onchange="_msgTipoChange()"
              style="accent-color:#c9a84c;">
            <span style="font-size:12px;color:#c8b88a;">Directo</span>
          </label>
          ${tieneAlianza ? `
          <label style="display:flex;align-items:center;gap:6px;cursor:pointer;">
            <input type="radio" name="msg-tipo" value="ALIANZA" id="msg-tipo-ali"
              ${!paraVal&&tieneAlianza?'':''}  onchange="_msgTipoChange()"
              style="accent-color:#9b6ad6;">
            <span style="font-size:12px;color:#9b6ad6;">Alianza · ${_escHTML(_alianza)}</span>
          </label>` : ''}
        </div>
      </div>

      <!-- Para (solo directo) -->
      <div id="msg-para-wrap" style="margin-bottom:10px;">
        <div style="font-size:10px;color:#667;letter-spacing:1px;
          font-family:'Cinzel',serif;margin-bottom:4px;">PARA</div>
        <input id="msg-para" type="text" placeholder="Nombre del jugador"
          value="${_escHTML(paraVal)}"
          style="${_IS}text-transform:uppercase;">
      </div>

      <!-- Asunto -->
      <div style="margin-bottom:10px;">
        <div style="font-size:10px;color:#667;letter-spacing:1px;
          font-family:'Cinzel',serif;margin-bottom:4px;">ASUNTO (opcional)</div>
        <input id="msg-asunto" type="text" placeholder="Asunto..."
          value="${_escHTML(asuntoVal)}"
          style="${_IS}">
      </div>

      <!-- Cuerpo -->
      <div style="margin-bottom:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;
          margin-bottom:4px;">
          <div style="font-size:10px;color:#667;letter-spacing:1px;
            font-family:'Cinzel',serif;">MENSAJE</div>
          <span id="msg-chars" style="font-size:10px;color:#445;">0 / 1000</span>
        </div>
        <textarea id="msg-cuerpo" rows="6" placeholder="Escribe tu mensaje..."
          oninput="_msgCountChars()"
          style="${_IS}resize:vertical;font-family:'Rajdhani',sans-serif;
            font-size:13px;line-height:1.5;"></textarea>
      </div>

      <div style="display:flex;gap:8px;align-items:center;">
        ${_btn('✉ Enviar', `_msgEnviar()`, '#c9a84c')}
        ${_btn('← Volver', `_msgVolver()`, '#667788')}
        <span id="msg-send-status" style="font-size:11px;color:#667;"></span>
      </div>
    </div>`;
}

function _bindCompose() {
  // Contador de caracteres
  const ta = document.getElementById('msg-cuerpo');
  if (ta) ta.addEventListener('input', _msgCountChars);
  // Mostrar/ocultar campo "Para" según tipo
  _msgTipoChange();
}

// ── Acciones globales ─────────────────────────────────────────────────────────

window._msgNuevo = function() {
  _replyTo = null;
  _vistaActiva = 'compose';
  _loadAll();
};

window._msgAlianza = function() {
  _replyTo = null;
  _vistaActiva = 'compose';
  _loadAll().then(() => {
    const r = document.getElementById('msg-tipo-ali');
    if (r) { r.checked = true; _msgTipoChange(); }
  });
};

window._msgResponder = function(de, asunto) {
  _replyTo = {jugador: de, asunto};
  _vistaActiva = 'compose';
  _loadAll();
};

window._msgVolver = function() {
  _replyTo = null;
  _vistaActiva = 'bandeja';
  _loadAll();
};

window._msgTipoChange = function() {
  const tipo = document.querySelector('input[name="msg-tipo"]:checked')?.value;
  const wrap = document.getElementById('msg-para-wrap');
  if (wrap) wrap.style.display = tipo === 'DIRECTO' ? 'block' : 'none';
};

window._msgCountChars = function() {
  const ta  = document.getElementById('msg-cuerpo');
  const sp  = document.getElementById('msg-chars');
  if (!ta || !sp) return;
  const n = ta.value.length;
  sp.textContent = `${n} / 1000`;
  sp.style.color = n > 900 ? '#e07050' : '#445';
};

window._msgEnviar = async function() {
  const tipo     = document.querySelector('input[name="msg-tipo"]:checked')?.value || 'DIRECTO';
  const para     = document.getElementById('msg-para')?.value?.trim().toUpperCase();
  const asunto   = document.getElementById('msg-asunto')?.value?.trim();
  const cuerpo   = document.getElementById('msg-cuerpo')?.value?.trim();
  const statusEl = document.getElementById('msg-send-status');

  if (!cuerpo) {
    if (statusEl) statusEl.style.color='#e07050', statusEl.textContent='Escribe un mensaje';
    return;
  }
  if (tipo === 'DIRECTO' && !para) {
    if (statusEl) statusEl.style.color='#e07050', statusEl.textContent='Escribe el destinatario';
    return;
  }
  if (statusEl) statusEl.style.color='#888', statusEl.textContent='Enviando…';

  const body = {de: _jugador, asunto, cuerpo};
  if (tipo === 'ALIANZA') body.alianza = _alianza;
  else                    body.para    = para;

  try {
    const r = await fetch(_MAPI('/enviar'), {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify(body),
    }).then(r=>r.json());

    if (r.ok) {
      _toast('Mensaje enviado');
      _replyTo = null;
      _vistaActiva = 'bandeja';
      _loadAll();
    } else {
      if (statusEl) statusEl.style.color='#e07050', statusEl.textContent=r.msg;
      _toast(r.msg, false);
    }
  } catch {
    if (statusEl) statusEl.style.color='#e07050', statusEl.textContent='Error de conexión';
    _toast('Error de conexión', false);
  }
};

window._msgBorrar = async function(id) {
  if (!confirm('¿Eliminar este mensaje?')) return;
  const r = await fetch(`${_MAPI(`/${id}`)}?jugador=${_jugador}`, {method:'DELETE'})
    .then(r=>r.json());
  _toast(r.msg, r.ok);
  if (r.ok) _loadAll();
};
