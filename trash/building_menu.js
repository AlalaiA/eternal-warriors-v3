/* building_menu.js — Menú de edificio con colas de entrenamiento/invocación */

const UNIDADES_BASICAS = [
  'EXPLORADOR','GUERRERO','SACERDOTE','COMANDO',
  'MERCENARIO','MARINE','CYBORG','MAGO','METAHUMANO'
];

const INVOCACIONES = [
  'DEMONIO','ANIMA','ESPECTRO','GOLEM','CENTAURO',
  'KRAKEN','ALONARDO','MADRESELVA','COLOSO','FENIX',
  'DRAGON_DE_ORO','CABALLERO_DE_LUZ','ALALAIA','EON_SUPREMO'
];

const NOMBRE_DISPLAY = {
  EXPLORADOR:'Explorador', GUERRERO:'Guerrero', SACERDOTE:'Sacerdote',
  COMANDO:'Comando', MERCENARIO:'Mercenario', MARINE:'Marine',
  CYBORG:'Cyborg', MAGO:'Mago', METAHUMANO:'Metahumano',
  DEMONIO:'Demonio', ANIMA:'Ánima', ESPECTRO:'Espectro',
  GOLEM:'Gólem', CENTAURO:'Centauro', KRAKEN:'Kraken',
  ALONARDO:'Alonardo', MADRESELVA:'Madreselva', COLOSO:'Coloso',
  FENIX:'Fénix', DRAGON_DE_ORO:'Dragón de Oro',
  CABALLERO_DE_LUZ:'Caballero de Luz', ALALAIA:'AlalaiA',
  EON_SUPREMO:'Éon Supremo',
};

function fmtTime(seg) {
  seg = Math.max(0, Math.round(seg));
  const d = Math.floor(seg / 86400);
  const h = Math.floor((seg % 86400) / 3600);
  const m = Math.floor((seg % 3600) / 60);
  const s = seg % 60;
  if (d > 0) return `${d}d ${h}h ${m}m`;
  if (h > 0) return `${h}h ${m}m ${s}s`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

function fmtNum(n) {
  if (!n && n !== 0) return '—';
  n = Number(n);
  const tiers = [[1e12,'T'],[1e9,'B'],[1e6,'M'],[1e3,'K']];
  for (const [d,s] of tiers) if (Math.abs(n) >= d) return (n/d).toFixed(1)+s;
  return Math.round(n).toLocaleString('es');
}

export function openBuildingMenu(building, jugador, ciudad, cityData, tasas) {
  // Cerrar menú existente
  const existing = document.getElementById('building-menu-overlay');
  if (existing) existing.remove();

  const tipo = building.type;
  const label = building.label;
  const nivel = building.lvl || 0;

  // Solo cuarteles y templos tienen colas
  const esCuartel = tipo === 'barracks';
  const esTemplo  = tipo === 'temple';
  const tieneMenu = esCuartel || esTemplo || nivel > 0;

  if (!tieneMenu) return;

  const overlay = document.createElement('div');
  overlay.id = 'building-menu-overlay';
  overlay.style.cssText = `
    position:fixed;inset:0;background:rgba(0,0,0,0.75);z-index:2000;
    display:flex;align-items:center;justify-content:center;
  `;
  overlay.onclick = e => { if(e.target===overlay) overlay.remove(); };

  const panel = document.createElement('div');
  panel.style.cssText = `
    background:rgba(8,10,20,0.98);border:1px solid rgba(201,168,76,0.35);
    border-radius:10px;padding:0;width:520px;max-height:80vh;
    overflow:hidden;display:flex;flex-direction:column;
    box-shadow:0 16px 64px rgba(0,0,0,0.8);font-family:'Rajdhani',sans-serif;
  `;

  // Header
  const header = document.createElement('div');
  header.style.cssText = `
    padding:16px 20px;border-bottom:1px solid rgba(201,168,76,0.2);
    display:flex;justify-content:space-between;align-items:center;
    background:linear-gradient(90deg,rgba(201,168,76,0.06),transparent);
  `;
  header.innerHTML = `
    <div>
      <div style="font-family:'Cinzel',serif;font-size:14px;color:#c9a84c;letter-spacing:1px">
        ${label}
      </div>
      <div style="font-size:10px;color:#7a6e5e;margin-top:2px">Nivel ${nivel}</div>
    </div>
    <button onclick="document.getElementById('building-menu-overlay').remove()"
      style="background:none;border:1px solid rgba(201,168,76,0.3);color:#c9a84c;
      width:28px;height:28px;border-radius:4px;cursor:pointer;font-size:14px">✕</button>
  `;

  // Body scrollable
  const body = document.createElement('div');
  body.style.cssText = 'padding:16px 20px;overflow-y:auto;flex:1;';

  // Estado de colas
  const colaSection = document.createElement('div');
  colaSection.id = 'cola-status';
  colaSection.innerHTML = '<div style="color:#5a5a78;font-size:11px">Cargando colas...</div>';
  body.appendChild(colaSection);

  // Formulario según tipo
  if (esCuartel || esTemplo) {
    const form = buildQueueForm(tipo, building, jugador, ciudad, cityData, tasas, colaSection);
    body.appendChild(form);
  }

  panel.appendChild(header);
  panel.appendChild(body);
  overlay.appendChild(panel);
  document.body.appendChild(overlay);

  // Cargar estado de colas
  loadColaStatus(jugador, ciudad, building, colaSection);

  // Refrescar colas cada 5 segundos mientras el menú está abierto
  const refreshInterval = setInterval(() => {
    if (!document.getElementById('building-menu-overlay')) {
      clearInterval(refreshInterval);
      return;
    }
    loadColaStatus(jugador, ciudad, building, colaSection);
  }, 5000);
}

async function loadColaStatus(jugador, ciudad, building, container) {
  try {
    const res  = await fetch(`/api/queues/${jugador}/${ciudad}`);
    const data = await res.json();
    if (!data.ok) { container.innerHTML = ''; return; }

    const tipo = building.type === 'barracks' ? 'CUARTEL' : 'TEMPLO';
    const misColas = data.colas.filter(c => c.tipo && c.tipo.startsWith(tipo));

    if (misColas.length === 0) {
      container.innerHTML = `
        <div style="color:#5a5a78;font-size:11px;padding:8px 0">
          No hay colas activas en este edificio.
        </div>`;
      return;
    }

    container.innerHTML = misColas.map(c => `
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
        border-radius:6px;padding:10px 12px;margin-bottom:8px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
          <span style="color:#c9a84c;font-family:'Cinzel',serif;font-size:11px">
            ${c.tipo} — ${NOMBRE_DISPLAY[c.unidad] || c.unidad}
          </span>
          <button onclick="cancelarCola('${jugador}','${ciudad}','${c.tipo}')"
            style="background:rgba(140,30,30,0.4);border:1px solid rgba(200,50,50,0.4);
            color:#e08080;font-size:9px;padding:2px 8px;border-radius:3px;cursor:pointer">
            Cancelar
          </button>
        </div>
        <div style="background:rgba(201,168,76,0.08);border-radius:3px;height:6px;overflow:hidden;margin-bottom:6px">
          <div style="height:100%;width:${c.porcentaje}%;background:linear-gradient(90deg,#8a6020,#c9a84c);
            border-radius:3px;transition:width 0.5s"></div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:10px;color:#7a6e5e">
          <span>${fmtNum(c.completadas)} / ${fmtNum(c.cantidad_total)} unidades</span>
          <span>⏱ ${fmtTime(c.tiempo_total_restante_seg)} restante</span>
        </div>
      </div>
    `).join('');

  } catch(e) {
    container.innerHTML = '';
  }
}

function buildQueueForm(tipo, building, jugador, ciudad, cityData, tasas, colaStatus) {
  const esCuartel = tipo === 'barracks';
  const lista = esCuartel ? UNIDADES_BASICAS : INVOCACIONES;

  // Determinar qué cuarteles/templos tiene disponibles
  const slots = [];
  if (esCuartel) {
    ['CUARTEL_1','CUARTEL_2','CUARTEL_3'].forEach(k => {
      if (cityData[k] && cityData[k] > 0) slots.push(k);
    });
  } else {
    ['TEMPLO_1','TEMPLO_2','TEMPLO_3'].forEach(k => {
      if (cityData[k] && cityData[k] > 0) slots.push(k);
    });
  }

  const wrap = document.createElement('div');
  wrap.style.marginTop = '12px';

  wrap.innerHTML = `
    <div style="font-family:'Cinzel',serif;font-size:11px;color:#c9a84c;
      letter-spacing:1px;margin-bottom:10px;border-top:1px solid rgba(201,168,76,0.15);padding-top:12px">
      ${esCuartel ? '⚔ ENTRENAR UNIDADES' : '✨ INVOCAR'}
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px">
      <div>
        <label style="font-size:9px;color:#7a6e5e;letter-spacing:1px;display:block;margin-bottom:4px">
          ${esCuartel ? 'CUARTEL' : 'TEMPLO'}
        </label>
        <select id="bm-slot" style="width:100%;background:rgba(10,12,22,0.9);
          border:1px solid rgba(201,168,76,0.25);color:#e8dcc8;padding:6px 8px;
          border-radius:4px;font-family:'Rajdhani',sans-serif;font-size:12px">
          ${slots.map(s => `<option value="${s}">${s.replace('_',' ')} (Nv.${cityData[s]})</option>`).join('')}
        </select>
      </div>
      <div>
        <label style="font-size:9px;color:#7a6e5e;letter-spacing:1px;display:block;margin-bottom:4px">
          ${esCuartel ? 'UNIDAD' : 'INVOCACIÓN'}
        </label>
        <select id="bm-unidad" style="width:100%;background:rgba(10,12,22,0.9);
          border:1px solid rgba(201,168,76,0.25);color:#e8dcc8;padding:6px 8px;
          border-radius:4px;font-family:'Rajdhani',sans-serif;font-size:12px">
          ${lista.map(u => `<option value="${u}">${NOMBRE_DISPLAY[u]||u}</option>`).join('')}
        </select>
      </div>
    </div>

    <div style="margin-bottom:10px">
      <label style="font-size:9px;color:#7a6e5e;letter-spacing:1px;display:block;margin-bottom:4px">
        CANTIDAD
      </label>
      <input id="bm-cantidad" type="number" min="1" value="100"
        style="width:100%;background:rgba(10,12,22,0.9);border:1px solid rgba(201,168,76,0.25);
        color:#e8dcc8;padding:6px 8px;border-radius:4px;font-family:'Rajdhani',sans-serif;
        font-size:12px;box-sizing:border-box">
    </div>

    <div id="bm-info" style="font-size:10px;color:#7a6e5e;margin-bottom:10px;min-height:16px"></div>

    <button id="bm-submit"
      style="width:100%;padding:10px;background:linear-gradient(135deg,rgba(201,168,76,0.15),rgba(201,168,76,0.08));
      border:1px solid rgba(201,168,76,0.4);color:#c9a84c;font-family:'Cinzel',serif;
      font-size:12px;letter-spacing:1px;border-radius:5px;cursor:pointer;transition:all 0.2s">
      ${esCuartel ? '⚔ INICIAR ENTRENAMIENTO' : '✨ INICIAR INVOCACIÓN'}
    </button>

    <div id="bm-msg" style="margin-top:8px;font-size:11px;text-align:center;min-height:16px"></div>
  `;

  // Actualizar info al cambiar selección
  const updateInfo = () => {
    const slot    = wrap.querySelector('#bm-slot')?.value;
    const unidad  = wrap.querySelector('#bm-unidad')?.value;
    const cantidad = parseInt(wrap.querySelector('#bm-cantidad')?.value) || 1;
    const infoEl  = wrap.querySelector('#bm-info');
    if (!slot || !unidad || !infoEl) return;

    if (esCuartel) {
      infoEl.textContent = `Tiempo estimado calculado por el servidor según nivel del cuartel.`;
    } else {
      infoEl.textContent = `Se descontará el maná requerido al confirmar la cola.`;
    }
  };

  setTimeout(() => {
    wrap.querySelector('#bm-slot')?.addEventListener('change', updateInfo);
    wrap.querySelector('#bm-unidad')?.addEventListener('change', updateInfo);
    wrap.querySelector('#bm-cantidad')?.addEventListener('input', updateInfo);

    wrap.querySelector('#bm-submit')?.addEventListener('click', async () => {
      const slot     = wrap.querySelector('#bm-slot')?.value;
      const unidad   = wrap.querySelector('#bm-unidad')?.value;
      const cantidad = parseInt(wrap.querySelector('#bm-cantidad')?.value) || 1;
      const msgEl    = wrap.querySelector('#bm-msg');
      const btn      = wrap.querySelector('#bm-submit');

      if (!slot || !unidad || cantidad < 1) return;

      btn.disabled = true;
      btn.style.opacity = '0.6';
      msgEl.style.color = '#7a6e5e';
      msgEl.textContent = 'Procesando...';

      try {
        const endpoint = esCuartel ? 'cuartel' : 'templo';
        const body = esCuartel
          ? { cuartel: slot, unidad, cantidad }
          : { templo: slot, invocacion: unidad, cantidad };

        const res  = await fetch(`/api/queues/${jugador}/${ciudad}/${endpoint}`, {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify(body),
        });
        const data = await res.json();

        if (data.ok) {
          msgEl.style.color = '#60a840';
          msgEl.textContent = data.msg;
          // Refrescar estado de colas
          setTimeout(() => loadColaStatus(jugador, ciudad, building, colaStatus), 500);
        } else {
          msgEl.style.color = '#e06060';
          msgEl.textContent = data.msg;
        }
      } catch(e) {
        msgEl.style.color = '#e06060';
        msgEl.textContent = 'Error de conexión';
      } finally {
        btn.disabled = false;
        btn.style.opacity = '1';
      }
    });

    updateInfo();
  }, 50);

  return wrap;
}

window.cancelarCola = async function(jugador, ciudad, tipo) {
  if (!confirm(`¿Cancelar cola de ${tipo}?`)) return;
  try {
    const res  = await fetch(`/api/queues/${jugador}/${ciudad}/${tipo}`, {method:'DELETE'});
    const data = await res.json();
    if (data.ok) {
      const overlay = document.getElementById('building-menu-overlay');
      if (overlay) overlay.remove();
    }
  } catch(e) {}
};
