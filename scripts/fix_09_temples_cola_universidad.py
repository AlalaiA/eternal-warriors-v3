"""
fix_09_temples_cola_universidad.py

3 fixes en 1:
1. city.js  — hitbox ampliado para templos y todos los edificios al fondo
2. buildings.py — Universidad descuenta % del tiempo de construcción de edificios
3. building_menu.js — integra cola real (cuartel/templo) con datos del backend
4. buildings.py — cargar % reducción universidad desde CSV

Ejecutar desde: E:\\0000ew V2Claude\\
"""
import pathlib, sys, re

ROOT = pathlib.Path(".")

# ═══════════════════════════════════════════════════════════════════════════════
# 1. city.js — hitbox mejorado
# ═══════════════════════════════════════════════════════════════════════════════
CITY_JS = ROOT / "frontend/js/screens/city.js"
src_city = CITY_JS.read_text(encoding="utf-8")
orig_city = src_city

# El hitbox actual: Math.abs(dx) < 40 && dy > -120 && dy < 10
# Problema: edificios al fondo tienen y pequeña (arriba en pantalla),
# el cálculo dy = my - b.y funciona bien pero -120 es muy poco para edificios altos.
# Solución: ampliar a -200 y aumentar tolerancia X a 50

OLD_HIT = """    const hit = _cityClickData.buildings.find(b => {
      const dx = mx - b.x, dy = my - b.y;
      return Math.abs(dx) < 40 && dy > -120 && dy < 10;
    });"""

NEW_HIT = """    const hit = _cityClickData.buildings.find(b => {
      const dx = mx - b.x, dy = my - b.y;
      return Math.abs(dx) < 55 && dy > -200 && dy < 20;
    });"""

OLD_HIT2 = """    const hit = _cityClickData.buildings.find(b => {
      const dx = mx - b.x, dy = my - b.y;
      return Math.abs(dx) < 40 && dy > -120 && dy < 10;
    });
    canvas.style.cursor = hit ? 'pointer' : 'default';"""

NEW_HIT2 = """    const hit = _cityClickData.buildings.find(b => {
      const dx = mx - b.x, dy = my - b.y;
      return Math.abs(dx) < 55 && dy > -200 && dy < 20;
    });
    canvas.style.cursor = hit ? 'pointer' : 'default';"""

src_city = src_city.replace(OLD_HIT, NEW_HIT)
src_city = src_city.replace(OLD_HIT2, NEW_HIT2)

if src_city != orig_city:
    CITY_JS.write_text(src_city, encoding="utf-8")
    print("✅ city.js — hitbox ampliado a ±55px / -200px altura")
else:
    print("⚠️  city.js — hitbox no encontrado, buscar manualmente Math.abs(dx) < 40")

# ═══════════════════════════════════════════════════════════════════════════════
# 2. buildings.py — Universidad reduce tiempo de construcción de edificios
#    CSV universidad: col[6]=% reducción colas, col[7]=% reducción edificios
# ═══════════════════════════════════════════════════════════════════════════════
BUILDINGS_PY = ROOT / "backend/systems/buildings.py"
src_bld = BUILDINGS_PY.read_text(encoding="utf-8")
orig_bld = src_bld

# Añadir función _load_universidad_reduccion si no existe
if "_load_universidad" not in src_bld:
    UNIV_FUNC = '''
def _load_universidad_reduccion() -> dict:
    """
    Carga % de reducción de la Universidad por nivel.
    col[6] = % reducción colas (cuartel/templo/herrería/CC)
    col[7] = % reducción tiempo de construcción de edificios
    Retorna: {nivel: {"colas_pct": float, "edificios_pct": float}}
    """
    import csv as _csv
    result = {}
    csv_path = CSV_DIR / "edificio9_universidad.csv"
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = _csv.reader(f, delimiter=";")
        rows = list(reader)
    for row in rows[1:]:
        if len(row) < 8:
            continue
        try:
            nivel = int(row[0].strip())
            colas   = float(row[6].strip().rstrip("%").replace(",","."))
            edifs   = float(row[7].strip().rstrip("%").replace(",","."))
            result[nivel] = {"colas_pct": colas, "edificios_pct": edifs}
        except (ValueError, IndexError):
            continue
    return result

_UNIV_CACHE: dict = {}

def get_universidad_reduccion(nivel_universidad: int) -> dict:
    """Retorna {colas_pct, edificios_pct} para el nivel dado."""
    global _UNIV_CACHE
    if not _UNIV_CACHE:
        _UNIV_CACHE = _load_universidad_reduccion()
    if nivel_universidad <= 0:
        return {"colas_pct": 0.0, "edificios_pct": 0.0}
    # Usar el nivel exacto o el más cercano hacia abajo
    nv = max(k for k in _UNIV_CACHE if k <= nivel_universidad) if any(k <= nivel_universidad for k in _UNIV_CACHE) else 1
    return _UNIV_CACHE.get(nv, {"colas_pct": 0.0, "edificios_pct": 0.0})

'''
    # Insertar antes de buildings_info
    insert_anchor = "def buildings_info("
    if insert_anchor in src_bld:
        src_bld = src_bld.replace(insert_anchor, UNIV_FUNC + insert_anchor)
        print("✅ buildings.py — _load_universidad_reduccion() añadida")
    else:
        print("⚠️  buildings.py — no se encontró buildings_info para insertar antes")
else:
    print("ℹ️  buildings.py — _load_universidad ya existe")

# Modificar buildings_info para aplicar reducción de universidad al tiempo_seg
OLD_BINFO_TIME = '        "tiempo_seg":       int(siguiente["tiempo_min"] * 60) if siguiente else None,'
NEW_BINFO_TIME = '''        "tiempo_seg":       _apply_univ_reduction(
                                int(siguiente["tiempo_min"] * 60),
                                city.get("UNIVERSIDAD", 0)
                            ) if siguiente else None,'''

if OLD_BINFO_TIME in src_bld:
    # Añadir helper _apply_univ_reduction antes de buildings_info
    HELPER = '''
def _apply_univ_reduction(tiempo_seg: int, nivel_universidad: int) -> int:
    """Aplica el % de reducción de la Universidad al tiempo de construcción."""
    if nivel_universidad <= 0 or tiempo_seg <= 0:
        return tiempo_seg
    reduccion = get_universidad_reduccion(nivel_universidad)
    pct = reduccion.get("edificios_pct", 0.0)
    return max(1, int(tiempo_seg * (1 - pct / 100)))

'''
    if "_apply_univ_reduction" not in src_bld:
        src_bld = src_bld.replace(
            "def buildings_info(",
            HELPER + "def buildings_info("
        )
    src_bld = src_bld.replace(OLD_BINFO_TIME, NEW_BINFO_TIME)
    print("✅ buildings.py — tiempo_seg reducido por Universidad")
else:
    print("⚠️  buildings.py — ancla tiempo_seg no encontrada, verificar manualmente")

# También exponer get_universidad_reduccion en el info para que el frontend lo muestre
OLD_BINFO_RETURN = '        "puede_subir":      puede_subir,'
NEW_BINFO_RETURN = '''        "puede_subir":      puede_subir,
        "reduccion_universidad_pct": get_universidad_reduccion(city.get("UNIVERSIDAD",0)).get("edificios_pct",0),'''

if OLD_BINFO_RETURN in src_bld and "reduccion_universidad_pct" not in src_bld:
    src_bld = src_bld.replace(OLD_BINFO_RETURN, NEW_BINFO_RETURN)
    print("✅ buildings.py — reduccion_universidad_pct expuesta en buildings_info")

if src_bld != orig_bld:
    BUILDINGS_PY.write_text(src_bld, encoding="utf-8")
    print(f"✅ buildings.py guardado")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. building_menu.js — integrar cola real + mostrar reducción universidad
# ═══════════════════════════════════════════════════════════════════════════════
MENU_JS = ROOT / "frontend/js/screens/building_menu.js"
src_menu = MENU_JS.read_text(encoding="utf-8")

# Reemplazar el _render para mostrar reducción universidad y mejorar la cola
OLD_UNIV = "        <div style=\"color:#aaa;font-size:.82em\">⏱ Tiempo: ${_fmtTime(info.tiempo_seg)}</div>"
NEW_UNIV = """        <div style="color:#aaa;font-size:.82em">
          ⏱ Tiempo: ${_fmtTime(info.tiempo_seg)}
          ${info.reduccion_universidad_pct > 0
            ? `<span style="color:#4a9;margin-left:6px">🎓 -${info.reduccion_universidad_pct}% (Universidad)</span>`
            : ''}
        </div>"""

if OLD_UNIV in src_menu:
    src_menu = src_menu.replace(OLD_UNIV, NEW_UNIV)
    print("✅ building_menu.js — reducción Universidad visible en UI")

# Mejorar el botón de cola para abrir panel real con fetch de colas
OLD_COLA_BTN = """window._ewOpenCola = function(edificio, jugador, ciudad) {
  // Delegar al sistema de colas existente si está disponible
  if (typeof openColaMenu === 'function') {
    openColaMenu(edificio, jugador, ciudad);
  } else {
    alert(`Cola para ${edificio} — integrar con sistema de colas existente`);
  }
};"""

NEW_COLA_BTN = r"""window._ewOpenCola = async function(edificio, jugador, ciudad) {
  const p = document.getElementById('ew-building-menu');
  if (!p) return;

  // Cargar estado de colas del backend
  let colas = [];
  try {
    const r = await fetch(`/api/queues/${jugador}/${ciudad}`);
    const d = await r.json();
    colas = (d.colas || []).filter(c => c.tipo === edificio);
  } catch(e) { /* sin colas activas */ }

  const esCuartel = /CUARTEL/.test(edificio);
  const nombre = edificio.replace(/_/g,' ');

  // Cola activa
  let colaActivaHTML = '';
  if (colas.length > 0) {
    const cola = colas[0];
    const hechas = cola.cantidad_hecha || 0;
    const total  = cola.cantidad_total || 1;
    const tpu    = cola.tiempo_por_unidad_seg || 0;
    const restantes = total - hechas;
    const tiempoRestante = restantes * tpu - ((Date.now()/1000) - cola.inicio) % tpu;
    const pct = (hechas/total*100).toFixed(1);
    colaActivaHTML = `
      <div style="background:#0a0a18;border:1px solid #333;border-radius:6px;padding:10px;margin-bottom:10px">
        <div style="color:#c9a84c;margin-bottom:4px">📋 Cola activa: ${cola.unidad}</div>
        <div style="color:#aaa;font-size:.85em">${hechas.toLocaleString()} / ${total.toLocaleString()} unidades</div>
        <div style="background:#1a1a2a;border-radius:3px;height:5px;margin:6px 0">
          <div style="background:#c9a84c;height:5px;border-radius:3px;width:${pct}%"></div>
        </div>
        <div style="color:#aaa;font-size:.82em">⏱ ~${_fmtTime(tiempoRestante)} por unidad</div>
        <button onclick="window._ewCancelarCola('${edificio}','${jugador}','${ciudad}')"
                style="background:#5a1a1a;border:1px solid #444;color:#e8e0d0;padding:5px 10px;
                       border-radius:4px;cursor:pointer;width:100%;margin-top:6px;font-size:.82em">
          ❌ Cancelar cola
        </button>
      </div>`;
  }

  // Unidades disponibles para entrenar/invocar
  const endpoint = esCuartel ? 'cuartel' : 'templo';
  const unidades = esCuartel
    ? ['EXPLORADOR','GUERRERO','SACERDOTE','COMANDO','MERCENARIO','MARINE','CYBORG','MAGO','METAHUMANO']
    : ['DEMONIO','ANIMA','ESPECTRO','GOLEM','CENTAURO','KRAKEN','ALONARDO','MADRESELVA','COLOSO','FENIX','DRAGON_DE_ORO','CABALLERO_DE_LUZ','ALALAIA','EON_SUPREMO'];

  const unidadRows = unidades.map(u => `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:3px 0;border-bottom:1px solid #111">
      <span style="color:#ddd;font-size:.88em">${u.replace(/_/g,' ')}</span>
      <div style="display:flex;gap:4px;align-items:center">
        <input id="qty-${u}" type="number" min="1" value="1"
               style="width:52px;background:#111;border:1px solid #333;color:#e8e0d0;
                      border-radius:3px;padding:2px 4px;font-size:.82em">
        <button onclick="window._ewEncolarUnidad('${edificio}','${jugador}','${ciudad}','${u}',document.getElementById('qty-${u}').value,'${endpoint}')"
                style="background:#1a2a4a;border:1px solid #333;color:#c9a84c;padding:3px 8px;
                       border-radius:3px;cursor:pointer;font-size:.82em">▶</button>
      </div>
    </div>`).join('');

  // Inyectar en el panel existente
  const orig = p.innerHTML;
  p.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <span style="color:#c9a84c">${nombre} — ${esCuartel ? 'Entrenar' : 'Invocar'}</span>
      <button onclick="this.closest('#ew-building-menu').style.display='none'"
              style="background:none;border:none;color:#888;font-size:1.2em;cursor:pointer">✕</button>
    </div>
    ${colaActivaHTML}
    <div style="max-height:320px;overflow-y:auto">${unidadRows}</div>`;
};

window._ewEncolarUnidad = async function(edificio, jugador, ciudad, unidad, cantidad, endpoint) {
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

window._ewCancelarCola = async function(edificio, jugador, ciudad) {
  if (!confirm('¿Cancelar la cola activa?')) return;
  try {
    const r = await fetch(`/api/queues/${jugador}/${ciudad}/${edificio}`, {method:'DELETE'});
    const d = await r.json();
    if (!r.ok) { alert('Error: ' + (d.detail || JSON.stringify(d))); return; }
    window._ewOpenCola(edificio, jugador, ciudad);
  } catch(e) { alert('Error de red: ' + e.message); }
};"""

if OLD_COLA_BTN in src_menu:
    src_menu = src_menu.replace(OLD_COLA_BTN, NEW_COLA_BTN)
    MENU_JS.write_text(src_menu, encoding="utf-8")
    print("✅ building_menu.js — cola real integrada (fetch /api/queues)")
else:
    # Insertar antes del export
    if "window._ewOpenCola" in src_menu:
        # Reemplazar la función existente completa
        src_menu = re.sub(
            r'window\._ewOpenCola\s*=\s*function.*?(?=window\._ew|\nexport)',
            NEW_COLA_BTN + "\n\n",
            src_menu, flags=re.DOTALL
        )
        MENU_JS.write_text(src_menu, encoding="utf-8")
        print("✅ building_menu.js — _ewOpenCola reemplazada via regex")
    else:
        print("⚠️  building_menu.js — _ewOpenCola no encontrada, revisar manualmente")

print("""
═══════════════════════════════════════════════════════════════
run.bat  +  Ctrl+Shift+R en navegador

Cambios:
  ✅ Hitbox ampliado — templos al fondo ahora clickeables
  ✅ Universidad descuenta % del tiempo de construcción
  ✅ Cola integrada — click en Cuartel/Templo muestra:
       · Cola activa con barra de progreso
       · Lista de unidades/invocaciones con campo cantidad + botón ▶
       · Botón cancelar cola
═══════════════════════════════════════════════════════════════
""")
