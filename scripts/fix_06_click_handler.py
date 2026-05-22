"""
fix_06_click_handler.py
Corrige la firma del click handler en city.js y building_menu.js para que sean compatibles.

Problema:
  city.js línea 297-304 llama:
    m.openBuildingMenu(hit, jugador, ciudad, cityData, tasas)
  donde hit = objeto layout {key, label, lvl, x, y, type}

  building_menu.js espera:
    openBuildingMenu(edificio_string, cityData)

Fix:
  city.js → pasar hit.key como primer argumento
  building_menu.js → actualizar firma para recibir (edificio, jugador, ciudad, cityData)

Ejecutar desde: E:\\0000ew V2Claude\\
"""
import pathlib, sys

ROOT = pathlib.Path(".")

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Parchear city.js — corregir llamada openBuildingMenu
# ═══════════════════════════════════════════════════════════════════════════════

CITY_JS = ROOT / "frontend" / "js" / "screens" / "city.js"
if not CITY_JS.exists():
    sys.exit(f"ERROR: No se encuentra {CITY_JS}")

src = CITY_JS.read_text(encoding="utf-8")
original_city = src

OLD_CLICK = """      import(`/static/js/screens/building_menu.js?v=1`).then(m => {
        m.openBuildingMenu(
          hit,
          _cityClickData.jugador,
          _cityClickData.ciudad,
          _cityClickData.cityData,
          _cityClickData.tasas
        );
      });"""

NEW_CLICK = """      import(`/static/js/screens/building_menu.js?v=${Date.now()}`).then(m => {
        m.openBuildingMenu(
          hit.key,
          _cityClickData.jugador,
          _cityClickData.ciudad,
          _cityClickData.cityData
        );
      });"""

if OLD_CLICK in src:
    src = src.replace(OLD_CLICK, NEW_CLICK)
    CITY_JS.write_text(src, encoding="utf-8")
    print("✅ city.js — click handler corregido (hit.key, firma correcta)")
else:
    # Buscar variante con espacios/tabs distintos
    import re
    pattern = r"import\(`/static/js/screens/building_menu\.js[^`]*`\)\.then\(m\s*=>\s*\{[^}]+m\.openBuildingMenu\([^)]+\);\s*\}\);"
    match = re.search(pattern, src, re.DOTALL)
    if match:
        replacement = """import(`/static/js/screens/building_menu.js?v=${Date.now()}`).then(m => {
        m.openBuildingMenu(
          hit.key,
          _cityClickData.jugador,
          _cityClickData.ciudad,
          _cityClickData.cityData
        );
      });"""
        src = src[:match.start()] + replacement + src[match.end():]
        CITY_JS.write_text(src, encoding="utf-8")
        print("✅ city.js — click handler corregido via regex")
    else:
        print("⚠️  city.js — no se encontró el bloque openBuildingMenu. Editar manualmente:")
        print("   Busca la llamada a openBuildingMenu en el onclick del canvas y cámbiala a:")
        print("   m.openBuildingMenu(hit.key, _cityClickData.jugador, _cityClickData.ciudad, _cityClickData.cityData);")

# ═══════════════════════════════════════════════════════════════════════════════
# 2. Reescribir building_menu.js con firma correcta y funcionalidad completa
# ═══════════════════════════════════════════════════════════════════════════════

MENU_JS = ROOT / "frontend" / "js" / "screens" / "building_menu.js"

MENU_CONTENT = r"""/**
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
  if (n == null) return '—';
  n = Number(n);
  if (isNaN(n)) return '—';
  const abs = Math.abs(n), s = n < 0 ? '-' : '';
  const tiers = [[1e12,'T'],[1e9,'B'],[1e6,'M'],[1e3,'K']];
  for (const [d, x] of tiers) {
    if (abs >= d) return s + (abs/d).toFixed(abs/d >= 100 ? 0 : 1) + x;
  }
  return s + Math.round(abs).toLocaleString('es');
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
        <div style="color:#aaa;font-size:.82em">⏱ Tiempo: ${_fmtTime(info.tiempo_seg)}</div>
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

window._ewOpenCola = function(edificio, jugador, ciudad) {
  // Delegar al sistema de colas existente si está disponible
  if (typeof openColaMenu === 'function') {
    openColaMenu(edificio, jugador, ciudad);
  } else {
    alert(`Cola para ${edificio} — integrar con sistema de colas existente`);
  }
};

// ── Exports ───────────────────────────────────────────────────────────────────
export function openBuildingMenu(edificio, jugador, ciudad, cityData) {
  _show(edificio, jugador, ciudad, cityData);
}

export function closeBuildingMenu() {
  _closePanel();
}
"""

MENU_JS.write_text(MENU_CONTENT, encoding="utf-8")
print(f"✅ building_menu.js — reescrito con firma correcta")
print("   export openBuildingMenu(edificio, jugador, ciudad, cityData)")

print("""
═══════════════════════════════════════════════════════════════
Listo. Arrancar servidor y probar:
  run.bat

Click en cualquier edificio del canvas → debe abrir panel con:
  - Nombre y nivel actual
  - Costo del siguiente nivel
  - Botón ⬆️ Construir
  - Para cuartel/templo: botón de cola
═══════════════════════════════════════════════════════════════
""")
