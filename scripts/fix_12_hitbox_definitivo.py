"""
fix_12_hitbox_definitivo.py

El problema real: _cityClickData es local al módulo ES6, inaccesible desde consola.
Los hitboxes están mal calibrados porque nunca se pudieron verificar.

Solución en 3 partes:
1. Exponer window._cityClickData = _cityClickData al asignarlo
2. Agregar modo debug (window._ewDebugHitbox = true) que dibuja rectángulos de hitbox
3. Recalibrar hitboxes leyendo las dimensiones REALES de cada función art*()
   cityhall:  sc=0.7+lvl*0.008, W=90*sc*1.4≈126, H=130*sc≈91 → altura total ~1.38*H≈125
   sanctuary: sc=0.65+lvl*0.007, W=70*sc, H=95*sc → altura ~1.48*H
   temple:    sc=0.62+lvl*0.06(max3), W=65*sc, H=90*sc → altura ~1.3*H
   barracks:  sc=0.62+lvl*0.015(max6), W=78*sc, H=68*sc → altura ~1.32*H
   etc.

Ejecutar desde: E:\\0000ew V2Claude\\
"""
import pathlib, sys

TARGET = pathlib.Path("frontend/js/screens/city.js")
if not TARGET.exists():
    sys.exit(f"ERROR: No se encuentra {TARGET}")

src = TARGET.read_text(encoding="utf-8")
original = src

# ─── PATCH 1: exponer _cityClickData globalmente ──────────────────────────────
OLD_INIT = """  // Inicializar datos para click en edificios
  _cityClickData = {
    buildings: [],
    jugador:   jugador,
    ciudad:    capital,
    cityData:  data.city || {},
    tasas:     data.tasas || {},
  };"""

NEW_INIT = """  // Inicializar datos para click en edificios
  _cityClickData = {
    buildings: [],
    jugador:   jugador,
    ciudad:    capital,
    cityData:  data.city || {},
    tasas:     data.tasas || {},
  };
  window._cityClickData = _cityClickData;  // exponer para debug"""

if OLD_INIT in src:
    src = src.replace(OLD_INIT, NEW_INIT)
    print("✅ PATCH 1 — _cityClickData expuesto como window._cityClickData")
else:
    print("⚠️  PATCH 1 — ancla no encontrada")

# ─── PATCH 2: hitboxes calibrados con las dimensiones reales de art*() ────────
# Cada art*() calcula: sc = base + min(lvl, cap) * factor
# Para lvl promedio ~5, calculamos sc real y de ahí W,H en pantalla
# Hitbox: x centro del edificio, y punto base, extendiéndose hacia arriba
#
# cityhall:  sc≈0.74, W=90*sc*1.4≈93, altura total desde y hacia arriba ≈ H*1.4 = 130*0.74*1.4≈135
# sanctuary: sc≈0.685, W=70*sc≈48, H=95*sc≈65, altura total ≈ H*1.5 ≈ 98
# temple:    sc≈0.80 (lvl3), W=65*sc≈52, H=90*sc≈72, altura total ≈ H*1.3 ≈ 94
# university:sc≈0.675, W=72*sc≈49, H=88*sc≈59, altura total ≈ H*1.35 ≈ 80
# warehouse: sc≈0.62, W=80*sc≈50, H=58*sc≈36, altura total ≈ H*1.25 ≈ 45  (más el techo)
# watchtower:sc≈0.64, W=42*sc≈27, H=110*sc≈70, altura total ≈ H*1.04 ≈ 73
# travel:    sc≈0.67, W=68*sc≈46, H=80*sc≈54, altura total ≈ H*1.45 ≈ 78
# house:     sc≈0.60, W=58*sc≈35, H=50*sc≈30, altura total ≈ H*1.35 ≈ 41
# barracks:  sc≈0.71 (lvl6), W=78*sc≈55, H=68*sc≈48, altura total ≈ H*1.35 ≈ 65
# forge:     sc≈0.70 (lvl4), W=70*sc≈49, H=60*sc≈42, altura total ≈ H*1.55 ≈ 65
# hideout:   sc≈0.70 (lvl1), W=62*sc≈43, H=32*sc≈22, altura total ≈ H*1.2  ≈ 27

OLD_HITBOX = """// ─── DIMENSIONES DE HITBOX POR TIPO ──────────────────────────────────────────
// Cada entrada: [halfW, totalH] en píxeles base (sin escala de nivel)
// halfW  = mitad del ancho del edificio en pantalla
// totalH = altura total desde b.y hacia arriba
const _HITBOX = {
  cityhall:   [80, 200],
  sanctuary:  [55, 140],
  temple:     [50, 120],
  university: [55, 110],
  warehouse:  [55,  90],
  watchtower: [30, 130],
  travel:     [50, 100],
  house:      [40,  75],
  barracks:   [50,  95],
  forge:      [45,  85],
  hideout:    [45,  55],
};"""

NEW_HITBOX = """// ─── DIMENSIONES DE HITBOX POR TIPO ──────────────────────────────────────────
// [halfW, totalH] calibrados con las dimensiones reales de cada art*()
// halfW  = mitad del ancho visual real en pantalla
// totalH = altura total desde b.y hacia arriba (incluye aguja/orbe/chimenea)
const _HITBOX = {
  cityhall:   [70, 180],  // torre alta, orbe en cima
  sanctuary:  [52,  130],  // cúpula grande
  temple:     [48,  110],  // aguja central + orbes laterales
  university: [48,  105],
  warehouse:  [48,   70],
  watchtower: [28,  120],
  travel:     [46,   95],
  house:      [36,   68],
  barracks:   [46,   85],  // bandera sube ~30px extra
  forge:      [42,   90],  // chimeneas altas
  hideout:    [38,   50],
};"""

if OLD_HITBOX in src:
    src = src.replace(OLD_HITBOX, NEW_HITBOX)
    print("✅ PATCH 2 — hitboxes recalibrados con dimensiones reales")
else:
    print("⚠️  PATCH 2 — _HITBOX no encontrado")

# ─── PATCH 3: modo debug visual de hitboxes ───────────────────────────────────
# Insertar al final de drawBuilding, antes del label, un dibujado de hitbox en debug

OLD_AFTER_SWITCH = """  ctx.restore();

  // Label con fondo destacado si hovered
  drawLabel(ctx, b.x, b.y, b.label, lvl, b.type, b.hovered);
}

// Test de hit usando hitbox registrado
function _hitTest(b, mx, my) {
  if (!b.hw) return false;
  return mx >= b.hx && mx <= b.hx + b.hw &&
         my >= b.hy && my <= b.hy + b.hh;
}"""

NEW_AFTER_SWITCH = """  ctx.restore();

  // Debug visual: mostrar hitbox si window._ewDebugHitbox = true
  if (window._ewDebugHitbox && b.hw) {
    ctx.save();
    ctx.strokeStyle = b.hovered ? 'rgba(255,80,80,0.9)' : 'rgba(80,255,80,0.5)';
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 2]);
    ctx.strokeRect(b.hx, b.hy, b.hw, b.hh);
    ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(255,255,255,0.7)';
    ctx.font = '9px monospace';
    ctx.fillText(b.key.replace('_',' '), b.hx + 2, b.hy + 10);
    ctx.restore();
  }

  // Label con fondo destacado si hovered
  drawLabel(ctx, b.x, b.y, b.label, lvl, b.type, b.hovered);
}

// Test de hit usando hitbox registrado
function _hitTest(b, mx, my) {
  if (!b.hw) return false;
  return mx >= b.hx && mx <= b.hx + b.hw &&
         my >= b.hy && my <= b.hy + b.hh;
}"""

if OLD_AFTER_SWITCH in src:
    src = src.replace(OLD_AFTER_SWITCH, NEW_AFTER_SWITCH)
    print("✅ PATCH 3 — modo debug hitbox añadido (window._ewDebugHitbox = true)")
else:
    print("⚠️  PATCH 3 — ancla post-switch no encontrada")

# ─── PATCH 4: sincronizar _cityClickData.buildings después del sort ───────────
# El problema crítico: layout.sort() reordena pero _cityClickData.buildings
# se asigna DESPUÉS del draw, cuando los hitboxes ya están calculados.
# Hay que asegurar que window._cityClickData se actualiza en cada frame.

OLD_SYNC = """  // Guardar layout para detección de click
  if (_cityClickData) _cityClickData.buildings = layout;"""

NEW_SYNC = """  // Guardar layout para detección de click
  if (_cityClickData) {
    _cityClickData.buildings = layout;
    window._cityClickData = _cityClickData;  // mantener referencia global fresca
  }"""

if OLD_SYNC in src:
    src = src.replace(OLD_SYNC, NEW_SYNC)
    print("✅ PATCH 4 — window._cityClickData sincronizado en cada frame")
else:
    print("⚠️  PATCH 4 — ancla sync no encontrada")

# ─── Guardar ──────────────────────────────────────────────────────────────────
if src != original:
    backup = TARGET.with_suffix(".js.bak3")
    backup.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")
    print(f"\n✅ city.js guardado (backup: {backup})")
else:
    print("\n⚠️  Sin cambios — revisar anclas manualmente")

print("""
run.bat + Ctrl+Shift+R

PARA VERIFICAR HITBOXES EN CONSOLA (F12):
  window._ewDebugHitbox = true
  → Verás rectángulos verdes sobre cada edificio
  → Al hacer hover se ponen rojos
  → Ajustar _HITBOX en city.js si alguno no cubre el edificio

PARA VER COORDENADAS:
  window._cityClickData.buildings.map(b=>({k:b.key,hx:Math.round(b.hx),hy:Math.round(b.hy),hw:Math.round(b.hw),hh:Math.round(b.hh)}))
""")
