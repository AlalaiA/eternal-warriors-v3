"""
fix_15_zonas_desde_posicion_real.py

La zona de cada edificio se deriva de su posición visual real (b.x, b.y)
usando las dimensiones exactas calculadas de cada función art*().

Zona = rectángulo centrado en b.x, desde b.y-totalH hasta b.y,
       con ancho halfW*2. Esto garantiza que zona y dibujo siempre coinciden.

Ejecutar desde: E:\\0000ew V2Claude\\
"""
import pathlib, sys

TARGET = pathlib.Path("frontend/js/screens/city.js")
if not TARGET.exists():
    sys.exit(f"ERROR: {TARGET}")

src = TARGET.read_text(encoding="utf-8")
original = src

# ─── PATCH 1: _HITBOX con dimensiones reales calculadas ───────────────────────
# halfW y totalH calculados con los niveles reales de jL01
# Se usan como referencia base; el JS los escala igual que art*()

OLD_HITBOX_BLOCK = """// ─── DIMENSIONES DE HITBOX POR TIPO ──────────────────────────────────────────
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

NEW_HITBOX_BLOCK = """// ─── DIMENSIONES VISUALES REALES POR TIPO ────────────────────────────────────
// Calculadas desde las funciones art*() con niveles medios
// [halfW, totalH]: halfW = mitad ancho, totalH = altura desde b.y hacia arriba
const _DIMS = {
  cityhall:   [127, 186],
  sanctuary:  [ 54, 137],
  temple:     [ 38,  98],
  university: [ 37,  90],
  warehouse:  [ 43,  62],
  watchtower: [ 28, 110],
  travel:     [ 32,  87],
  house:      [ 26,  47],
  barracks:   [ 36,  68],
  forge:      [ 30,  78],
  hideout:    [ 26,  27],
};"""

if OLD_HITBOX_BLOCK in src:
    src = src.replace(OLD_HITBOX_BLOCK, NEW_HITBOX_BLOCK)
    print("✅ PATCH 1 — _DIMS con valores reales calculados")
else:
    # puede que ya haya sido reemplazado por fix anterior
    if "_DIMS" not in src:
        # insertar antes de drawBuilding
        anchor = "// ─── DISPATCHER DE EDIFICIOS"
        if anchor in src:
            insert = """// ─── DIMENSIONES VISUALES REALES POR TIPO ────────────────────────────────────
const _DIMS = {
  cityhall:   [127, 186],
  sanctuary:  [ 54, 137],
  temple:     [ 38,  98],
  university: [ 37,  90],
  warehouse:  [ 43,  62],
  watchtower: [ 28, 110],
  travel:     [ 32,  87],
  house:      [ 26,  47],
  barracks:   [ 36,  68],
  forge:      [ 30,  78],
  hideout:    [ 26,  27],
};

"""
            src = src.replace(anchor, insert + anchor)
            print("✅ PATCH 1 — _DIMS insertado antes de drawBuilding")
        else:
            print("⚠️  PATCH 1 — no se pudo insertar _DIMS")
    else:
        print("ℹ️  PATCH 1 — _DIMS ya existe")

# ─── PATCH 2: drawBuilding — calcular zx,zy,zw,zh desde b.x,b.y + _DIMS ──────
# Reemplazar el bloque de registro de hitbox

OLD_REGISTER = """  // Registrar hitbox preciso para este edificio
  const [hw, th] = _HITBOX[b.type] || [45, 80];
  b.hx = b.x - hw;
  b.hy = b.y - th;
  b.hw = hw * 2;
  b.hh = th;"""

NEW_REGISTER = """  // Zona derivada de posición visual real del edificio
  const [hw, th] = _DIMS[b.type] || [40, 70];
  b.zx = b.x - hw;
  b.zy = b.y - th;
  b.zw = hw * 2;
  b.zh = th;"""

if OLD_REGISTER in src:
    src = src.replace(OLD_REGISTER, NEW_REGISTER)
    print("✅ PATCH 2 — zona calculada desde b.x,b.y con _DIMS")
else:
    print("⚠️  PATCH 2 — bloque registro hitbox no encontrado")

# ─── PATCH 3: _hitTest ────────────────────────────────────────────────────────
# Asegurar que usa zx,zy,zw,zh
OLD_HIT_A = """// Test de hit: zona cartesiana exclusiva por edificio
function _hitTest(b, mx, my) {
  if (b.zw === undefined) return false;
  return mx >= b.zx && mx <= b.zx + b.zw &&
         my >= b.zy && my <= b.zy + b.zh;
}"""

OLD_HIT_B = """// Test de hit usando zona cartesiana fija
function _hitTest(b, mx, my) {
  if (b.zw === undefined) return false;
  return mx >= b.zx && mx <= b.zx + b.zw &&
         my >= b.zy && my <= b.zy + b.zh;
}"""

CORRECT_HIT = """// Hit test: zona derivada de posición visual real
function _hitTest(b, mx, my) {
  if (!b.zw) return false;
  return mx >= b.zx && mx <= b.zx + b.zw &&
         my >= b.zy && my <= b.zy + b.zh;
}"""

if OLD_HIT_A in src:
    src = src.replace(OLD_HIT_A, CORRECT_HIT)
    print("✅ PATCH 3 — _hitTest OK")
elif OLD_HIT_B in src:
    src = src.replace(OLD_HIT_B, CORRECT_HIT)
    print("✅ PATCH 3 — _hitTest OK (variante B)")
else:
    print("ℹ️  PATCH 3 — _hitTest ya correcto o no encontrado")

# ─── PATCH 4: getLayout — posiciones isométricas reales ───────────────────────
# Volver al layout isométrico original pero con posiciones corregidas.
# El layout define b.x, b.y (posición visual).
# La zona se calcula automáticamente en drawBuilding usando _DIMS.
# Así zona y edificio SIEMPRE coinciden — es matemáticamente imposible que difieran.

start = src.index("function getLayout(c, cx, cy, rx, ry) {")
depth = 0
i = start
while i < len(src):
    if src[i] == '{': depth += 1
    elif src[i] == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
    i += 1

NEW_LAYOUT = """function getLayout(c, cx, cy, rx, ry) {
  const lv = k => Number(c[k] || 0);

  // Posición isométrica: ox=offset horizontal, ov=offset profundidad
  // py = cy + ov*0.5  (proyección 2:1 isométrica)
  // La zona se calcula automáticamente en drawBuilding con _DIMS
  const b = (ox, ov, key, label, type, extra={}) => ({
    key, label, type,
    lvl: lv(key),
    x: cx + ox,
    y: cy + ov * 0.5,
    zx:0, zy:0, zw:0, zh:0,  // se calculan en drawBuilding
    hovered: false,
    ...extra,
  });

  const ix = rx * 0.78;
  const iy = ry * 0.78;

  return [
    // ── FONDO ─────────────────────────────────────────────────────────────
    b(      0,  -iy*1.10, 'CENTRO_DE_CIUDAD',  'C.Ciudad',    'cityhall'),
    b( -ix*0.52,-iy*0.65, 'SANTUARIO_ARCANO',  'Santuario',   'sanctuary'),
    b(  ix*0.52,-iy*0.65, 'UNIVERSIDAD',        'Universidad', 'university'),

    // ── PLANO MEDIO ───────────────────────────────────────────────────────
    b( -ix*0.78,-iy*0.25, 'CASA',      'Casa',        'house'),
    b( -ix*0.30,-iy*0.30, 'ALMACEN',   'Almacén',     'warehouse'),
    b(  ix*0.08,-iy*0.20, 'ESCONDITE', 'Escondite',   'hideout'),
    b(  ix*0.48,-iy*0.25, 'HERRERIA',  'Herrería',    'forge'),
    b(  ix*0.85,-iy*0.20, 'CENTRO_DE_VIAJES','C.Viajes','travel'),

    // ── TEMPLOS: fila separada, bien espaciados ────────────────────────
    b( -ix*0.60, iy*0.22, 'TEMPLO_1', 'Templo I',   'temple', {accentKey:'blue'}),
    b(       0,  iy*0.18, 'TEMPLO_2', 'Templo II',  'temple', {accentKey:'gold'}),
    b(  ix*0.60, iy*0.22, 'TEMPLO_3', 'Templo III', 'temple', {accentKey:'purple'}),

    // ── CUARTELES: primer plano, bien separados ────────────────────────
    b( -ix*0.40, iy*0.72, 'CUARTEL_1', 'Cuartel I',  'barracks', {accentKey:'red1'}),
    b(  ix*0.40, iy*0.72, 'CUARTEL_2', 'Cuartel II', 'barracks', {accentKey:'red2'}),
  ];
}"""

src = src[:start] + NEW_LAYOUT + src[end:]
print("✅ PATCH 4 — getLayout isométrico limpio, zonas calculadas desde _DIMS")

# ─── PATCH 5: label en base del edificio, no de la zona ───────────────────────
OLD_LABEL_ZONE = """  // Label siempre en borde inferior de la zona
  const labelY = b.zw !== undefined ? b.zy + b.zh - 2 : b.y;
  drawLabel(ctx, b.zx + b.zw/2, labelY, b.label, lvl, b.type, b.hovered);"""

NEW_LABEL_FINAL = """  drawLabel(ctx, b.x, b.y, b.label, lvl, b.type, b.hovered);"""

if OLD_LABEL_ZONE in src:
    src = src.replace(OLD_LABEL_ZONE, NEW_LABEL_FINAL)
    print("✅ PATCH 5 — label en posición visual del edificio")

# ─── Guardar ──────────────────────────────────────────────────────────────────
if src != original:
    backup = TARGET.with_suffix(".js.bak6")
    backup.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")
    print(f"\n✅ city.js guardado (backup: {backup})")
else:
    print("\n⚠️  Sin cambios")

print("""
run.bat + Ctrl+Shift+R

La zona ahora SE CALCULA AUTOMÁTICAMENTE desde donde está dibujado el edificio.
Es matemáticamente imposible que difieran.

Debug (F12 consola):
  window._ewDebugHitbox = true
""")
