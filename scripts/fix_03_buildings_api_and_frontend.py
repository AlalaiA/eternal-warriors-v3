"""
fix_03_buildings_api_and_frontend.py

1. Agrega endpoints de buildings a backend/api/buildings.py (nuevo archivo)
2. Registra el router en backend/main.py
3. Crea/actualiza frontend/js/screens/building_menu.js con soporte de subida de edificios

Ejecutar desde: E:\0000ew V2Claude\
"""
import pathlib, sys, re

ROOT = pathlib.Path(".")

if not (ROOT / "backend" / "main.py").exists():
    sys.exit("ERROR: Ejecutar desde la raíz E:\\0000ew V2Claude\\")

# ═══════════════════════════════════════════════════════════════════════════════
# 1. backend/api/buildings.py  — Router FastAPI
# ═══════════════════════════════════════════════════════════════════════════════

BUILDINGS_API = '''"""
backend/api/buildings.py
Endpoints REST para info y gestión de edificios.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.data.save_manager import load_player, save_player
from backend.systems.buildings import buildings_info, iniciar_obra, cancelar_obra, procesar_obras

router = APIRouter(prefix="/api/buildings", tags=["buildings"])


@router.get("/{jugador}/{ciudad}/{edificio}")
def get_building_info(jugador: str, ciudad: str, edificio: str):
    """Retorna info del edificio: nivel actual, costo siguiente nivel, tiempo, stat."""
    player = load_player(jugador)
    if not player:
        raise HTTPException(404, f"Jugador {jugador} no encontrado")
    city = next((c for c in player["cities"] if c["NOMBRE"] == ciudad), None)
    if not city:
        raise HTTPException(404, f"Ciudad {ciudad} no encontrada")
    # Procesar obras que puedan haber terminado
    subidos = procesar_obras(city)
    if subidos:
        save_player(player)
    info = buildings_info(city, edificio.upper())
    if "error" in info:
        raise HTTPException(400, info["error"])
    return info


@router.post("/{jugador}/{ciudad}/{edificio}/upgrade")
def post_upgrade(jugador: str, ciudad: str, edificio: str):
    """Inicia la construcción del siguiente nivel del edificio."""
    player = load_player(jugador)
    if not player:
        raise HTTPException(404, f"Jugador {jugador} no encontrado")
    city = next((c for c in player["cities"] if c["NOMBRE"] == ciudad), None)
    if not city:
        raise HTTPException(404, f"Ciudad {ciudad} no encontrada")
    procesar_obras(city)
    result = iniciar_obra(player, city, edificio.upper())
    if "error" in result:
        raise HTTPException(400, result["error"])
    save_player(player)
    return result


@router.delete("/{jugador}/{ciudad}/{edificio}/upgrade")
def delete_upgrade(jugador: str, ciudad: str, edificio: str):
    """Cancela obra activa, devuelve 50% de recursos."""
    player = load_player(jugador)
    if not player:
        raise HTTPException(404, f"Jugador {jugador} no encontrado")
    city = next((c for c in player["cities"] if c["NOMBRE"] == ciudad), None)
    if not city:
        raise HTTPException(404, f"Ciudad {ciudad} no encontrada")
    result = cancelar_obra(city, edificio.upper())
    if "error" in result:
        raise HTTPException(400, result["error"])
    save_player(player)
    return result
'''

api_path = ROOT / "backend" / "api" / "buildings.py"
api_path.write_text(BUILDINGS_API, encoding="utf-8")
print(f"✅ Creado: {api_path}")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Registrar router en main.py
# ═══════════════════════════════════════════════════════════════════════════════

MAIN = ROOT / "backend" / "main.py"
main_src = MAIN.read_text(encoding="utf-8")

if "buildings" not in main_src:
    # Buscar el último import de router y añadir tras él
    import_line = "from backend.api.buildings import router as buildings_router"
    include_line = 'app.include_router(buildings_router)'

    # Añadir import junto a los otros
    if "from backend.api.queues import" in main_src:
        main_src = main_src.replace(
            "from backend.api.queues import",
            f"{import_line}\nfrom backend.api.queues import"
        )
    else:
        # Fallback: añadir al principio de los imports del proyecto
        main_src = import_line + "\n" + main_src

    # Añadir include_router
    if "include_router" in main_src:
        # Insertar tras el último include_router existente
        last = main_src.rfind("app.include_router(")
        end_of_line = main_src.index("\n", last)
        main_src = main_src[:end_of_line+1] + include_line + "\n" + main_src[end_of_line+1:]
    else:
        main_src += f"\n{include_line}\n"

    MAIN.write_text(main_src, encoding="utf-8")
    print(f"✅ Router buildings registrado en main.py")
else:
    print("ℹ️  buildings ya registrado en main.py — sin cambios")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. frontend/js/screens/building_menu.js — actualizado con subida de edificios
# ═══════════════════════════════════════════════════════════════════════════════

BUILDING_MENU_JS = r'''/**
 * building_menu.js
 * Menú de edificio: colas (cuartel/templo) + subida de nivel
 * 
 * API pública:
 *   openBuildingMenu(edificio, cityData) — abre el panel
 *   closeBuildingMenu()                  — cierra
 */

const _MENU = (() => {
  const JUGADOR = () => sessionStorage.getItem('jugador');
  const CIUDAD  = () => sessionStorage.getItem('ciudad_actual');

  let _panel = null;
  let _ticker = null;

  // ── Crear panel DOM ────────────────────────────────────────────────────────
  function _ensurePanel() {
    if (_panel) return _panel;
    _panel = document.createElement('div');
    _panel.id = 'building-menu';
    _panel.style.cssText = `
      position:fixed; top:50%; left:50%; transform:translate(-50%,-50%);
      background:var(--bg-panel,#1a1a2e); border:2px solid var(--color-gold,#c9a84c);
      border-radius:12px; padding:24px; min-width:360px; max-width:480px;
      color:var(--text-main,#e8e0d0); z-index:1000; box-shadow:0 8px 32px #000a;
      font-family:var(--font-main,'Cinzel',serif);
    `;
    document.body.appendChild(_panel);
    return _panel;
  }

  function _closePanel() {
    if (_ticker) { clearInterval(_ticker); _ticker = null; }
    if (_panel)  { _panel.style.display = 'none'; }
  }

  // ── Formateo ───────────────────────────────────────────────────────────────
  function _fmt(n) { return Number(n).toLocaleString('es-CO'); }
  function _fmtTime(s) {
    s = Math.floor(s);
    if (s <= 0) return '✅ Listo';
    const h = Math.floor(s/3600), m = Math.floor((s%3600)/60), sec = s%60;
    if (h > 0) return `${h}h ${m}m ${sec}s`;
    if (m > 0) return `${m}m ${sec}s`;
    return `${sec}s`;
  }

  // ── Panel principal de edificio ────────────────────────────────────────────
  async function _showBuildingPanel(edificio, cityData) {
    const p = _ensurePanel();
    p.style.display = 'block';
    p.innerHTML = `<div style="text-align:center;color:var(--color-gold,#c9a84c)">⏳ Cargando ${edificio}...</div>`;

    let info;
    try {
      const r = await fetch(`/api/buildings/${JUGADOR()}/${CIUDAD()}/${edificio}`);
      info = await r.json();
    } catch (e) {
      p.innerHTML = `<p style="color:#f66">Error de red</p><button onclick="_MENU_close()">Cerrar</button>`;
      return;
    }

    _renderBuildingInfo(info, edificio, cityData);
  }

  function _renderBuildingInfo(info, edificio, cityData) {
    const p = _ensurePanel();
    const nombre = edificio.replace(/_/g,' ');
    const nivelActual = info.nivel_actual;
    const nivelSig = info.nivel_siguiente;
    const maxNivel = info.max_nivel;

    let costoHTML = '';
    if (info.costo) {
      const iconos = {madera:'🪵',piedra:'🪨',hierro:'⚙️',oro:'🪙',carbon:'🔥'};
      costoHTML = Object.entries(info.costo).filter(([_,v])=>v>0).map(([mat,val])=>
        `<span style="margin-right:8px">${iconos[mat]||''}${_fmt(val)}</span>`
      ).join('');
    }

    let statHTML = '';
    if (info.stat_nombre) {
      statHTML = `
        <tr><td style="color:#aaa">${info.stat_nombre.replace(/_/g,' ')}</td>
            <td>${_fmt(info.stat_actual)}</td>
            <td>${info.stat_siguiente != null ? '→ ' + _fmt(info.stat_siguiente) : '—'}</td></tr>`;
    }

    let accionHTML = '';
    if (info.en_construccion) {
      const tr = info.tiempo_restante_seg ?? 0;
      accionHTML = `
        <div id="bm-obra" style="margin-top:16px;padding:12px;background:#0a0a1a;border-radius:8px">
          <div>🔨 Construyendo nivel ${nivelSig}…</div>
          <div id="bm-obra-time" style="font-size:1.2em;color:var(--color-gold,#c9a84c);margin:8px 0">${_fmtTime(tr)}</div>
          <div style="background:#333;border-radius:4px;height:8px;margin:6px 0">
            <div id="bm-obra-bar" style="background:var(--color-gold,#c9a84c);height:8px;border-radius:4px;width:0%"></div>
          </div>
          <button onclick="_MENU_cancelObra('${edificio}')" style="${_btnStyle('#8b1a1a')}">❌ Cancelar obra (recuperar 50%)</button>
        </div>`;
      // Arrancar ticker
      let dur = (info.tiempo_seg || 3600);
      let restante = tr;
      if (_ticker) clearInterval(_ticker);
      _ticker = setInterval(() => {
        restante = Math.max(0, restante - 1);
        const el = document.getElementById('bm-obra-time');
        const bar = document.getElementById('bm-obra-bar');
        if (el) el.textContent = _fmtTime(restante);
        if (bar) bar.style.width = `${Math.min(100, ((dur-restante)/dur)*100).toFixed(1)}%`;
        if (restante <= 0) {
          clearInterval(_ticker); _ticker = null;
          _showBuildingPanel(edificio, cityData); // recargar
        }
      }, 1000);
    } else if (info.puede_subir && info.costo) {
      accionHTML = `
        <div style="margin-top:16px">
          <div style="color:#aaa;font-size:.85em;margin-bottom:6px">Costo nivel ${nivelSig}:</div>
          <div style="margin-bottom:10px">${costoHTML}</div>
          <div style="color:#aaa;font-size:.85em">Tiempo: ${_fmtTime(info.tiempo_seg)}</div>
          <button onclick="_MENU_iniciarObra('${edificio}')" style="${_btnStyle('#1a4a1a')};margin-top:10px">⬆️ Subir a nivel ${nivelSig}</button>
        </div>`;
    } else if (nivelActual >= maxNivel) {
      accionHTML = `<div style="margin-top:16px;color:#aaa">🏆 Nivel máximo alcanzado</div>`;
    }

    // ¿Es cuartel o templo? Agregar sección de colas
    let colaHTML = '';
    if (/CUARTEL/.test(edificio) || /TEMPLO/.test(edificio)) {
      colaHTML = `<div style="margin-top:16px;border-top:1px solid #333;padding-top:12px">
        <button onclick="_MENU_openCola('${edificio}')" style="${_btnStyle('#1a2a4a')}">
          ⚔️ ${/CUARTEL/.test(edificio) ? 'Entrenar tropas' : 'Invocar criaturas'}
        </button>
      </div>`;
    }

    p.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
        <h2 style="margin:0;color:var(--color-gold,#c9a84c);font-size:1.1em">${nombre}</h2>
        <button onclick="_MENU_close()" style="background:none;border:none;color:#888;font-size:1.3em;cursor:pointer">✕</button>
      </div>
      <table style="width:100%;border-collapse:collapse;font-size:.9em">
        <thead><tr style="color:#888"><th style="text-align:left">Stat</th><th>Actual</th><th>Siguiente</th></tr></thead>
        <tbody>
          <tr><td style="color:#aaa">Nivel</td><td>${nivelActual}</td><td>${nivelSig <= maxNivel ? nivelSig : '—'}</td></tr>
          ${statHTML}
        </tbody>
      </table>
      ${accionHTML}
      ${colaHTML}
    `;
  }

  function _btnStyle(bg) {
    return `background:${bg};border:1px solid #444;color:#e8e0d0;padding:8px 16px;
            border-radius:6px;cursor:pointer;width:100%;font-size:.9em;`;
  }

  // ── Acciones ───────────────────────────────────────────────────────────────
  async function _iniciarObra(edificio) {
    const r = await fetch(`/api/buildings/${JUGADOR()}/${CIUDAD()}/${edificio}/upgrade`, {method:'POST'});
    const data = await r.json();
    if (data.error) { alert('Error: ' + data.error); return; }
    _showBuildingPanel(edificio, null);
  }

  async function _cancelarObra(edificio) {
    if (!confirm('¿Cancelar obra? Solo recuperarás el 50% de los recursos.')) return;
    const r = await fetch(`/api/buildings/${JUGADOR()}/${CIUDAD()}/${edificio}/upgrade`, {method:'DELETE'});
    const data = await r.json();
    if (data.error) { alert('Error: ' + data.error); return; }
    _showBuildingPanel(edificio, null);
  }

  function _openCola(edificio) {
    // Delega al sistema de colas existente
    if (typeof openColaMenu === 'function') {
      openColaMenu(edificio);
    } else {
      alert('Sistema de colas no disponible en este contexto.');
    }
  }

  // ── Exposición global ──────────────────────────────────────────────────────
  window._MENU_close       = _closePanel;
  window._MENU_iniciarObra = _iniciarObra;
  window._MENU_cancelObra  = _cancelarObra;
  window._MENU_openCola    = _openCola;

  return {
    open:  _showBuildingPanel,
    close: _closePanel,
  };
})();

/** API pública */
function openBuildingMenu(edificio, cityData) { _MENU.open(edificio, cityData); }
function closeBuildingMenu()                   { _MENU.close(); }
'''

menu_path = ROOT / "frontend" / "js" / "screens" / "building_menu.js"
menu_path.parent.mkdir(parents=True, exist_ok=True)
menu_path.write_text(BUILDING_MENU_JS, encoding="utf-8")
print(f"✅ Actualizado: {menu_path}")


print("""
═════════════════════════════════════════════════════════════
ENDPOINTS NUEVOS (registrar en main.py si no lo hizo auto):

  GET    /api/buildings/{jugador}/{ciudad}/{edificio}
  POST   /api/buildings/{jugador}/{ciudad}/{edificio}/upgrade
  DELETE /api/buildings/{jugador}/{ciudad}/{edificio}/upgrade

INTEGRACIÓN en city.js:
  En el handler de click sobre un edificio en el canvas, reemplaza o extiende
  la llamada existente para incluir:

    openBuildingMenu(nombreEdificio, cityData);

  donde nombreEdificio es la clave exacta del JSON del jugador, ej:
    'CENTRO_DE_CIUDAD', 'CUARTEL_1', 'TEMPLO_2', 'MURALLA', etc.
═════════════════════════════════════════════════════════════
""")
