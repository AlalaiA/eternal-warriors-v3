"""
fix_13_zonas_cartesianas.py

Sistema simple: cada edificio tiene una zona fija en porcentaje del canvas.
El mouse entra en la zona → hover. Click → menú.
Sin isométricas, sin hitboxes dinámicos, sin solapamiento.

Las zonas están definidas mirando la imagen con debug:
  Canvas aprox 1200x650px. Zonas en % de W y H.

Ejecutar desde: E:\\0000ew V2Claude\\
"""
import pathlib, sys

TARGET = pathlib.Path("frontend/js/screens/city.js")
if not TARGET.exists():
    sys.exit(f"ERROR: {TARGET} no encontrado")

src = TARGET.read_text(encoding="utf-8")
original = src

# ── PATCH 1: reemplazar getLayout con zonas cartesianas fijas ─────────────────
# Cada zona: [cx%, cy%, w%, h%] — centro x, centro y, ancho, alto (% del canvas)
# Derivadas de la imagen de debug, distribuidas sin solapamiento

OLD_GETLAYOUT_START = "function getLayout(c, cx, cy, rx, ry) {"

# Buscar fin de getLayout
start = src.index(OLD_GETLAYOUT_START)
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

NEW_GETLAYOUT = """function getLayout(c, cx, cy, rx, ry) {
  const lv = k => Number(c[k] || 0);
  const W = cx * 2;   // ancho total del canvas
  const H = cy / 0.58; // alto total del canvas

  // Zona: {key, label, type, accentKey?, zx, zy, zw, zh}
  // zx,zy = centro de la zona en píxeles
  // zw,zh = ancho y alto de la zona en píxeles
  // Posiciones derivadas del layout visual real — sin solapamiento

  const z = (key, label, type, pctX, pctY, pctW, pctH, extra={}) => ({
    key, label, type,
    lvl: lv(key),
    // punto base para drawBuilding (centro-inferior visual)
    x: W * pctX,
    y: H * pctY,
    // zona de interacción cartesiana
    zx: W * pctX - W * pctW / 2,
    zy: H * pctY - H * pctH,
    zw: W * pctW,
    zh: H * pctH,
    ...extra,
  });

  return [
    // ── Fondo centro ───────────────────────────────────────────────────────
    z('CENTRO_DE_CIUDAD', 'C.Ciudad',    'cityhall',   0.500, 0.55,  0.13, 0.38),

    // ── Fondo izquierda / derecha ──────────────────────────────────────────
    z('SANTUARIO_ARCANO', 'Santuario',   'sanctuary',  0.360, 0.58,  0.12, 0.32),
    z('UNIVERSIDAD',      'Universidad', 'university', 0.640, 0.52,  0.12, 0.28),

    // ── Templos: fila media, 3 columnas sin solapar ────────────────────────
    z('TEMPLO_1', 'Templo I',   'temple', 0.290, 0.62,  0.11, 0.24, {accentKey:'blue'}),
    z('TEMPLO_2', 'Templo II',  'temple', 0.500, 0.60,  0.11, 0.24, {accentKey:'gold'}),
    z('TEMPLO_3', 'Templo III', 'temple', 0.700, 0.56,  0.11, 0.24, {accentKey:'purple'}),

    // ── Plano medio-bajo ───────────────────────────────────────────────────
    z('ALMACEN',         'Almacén',   'warehouse', 0.340, 0.73,  0.11, 0.20),
    z('HERRERIA',        'Herrería',  'forge',     0.570, 0.68,  0.10, 0.20),
    z('CENTRO_DE_VIAJES','C.Viajes',  'travel',    0.720, 0.68,  0.11, 0.20),

    // ── Primer plano ───────────────────────────────────────────────────────
    z('CASA',      'Casa',       'house',    0.400, 0.80,  0.10, 0.18),
    z('CUARTEL_1', 'Cuartel I',  'barracks', 0.500, 0.82,  0.10, 0.18, {accentKey:'red1'}),
    z('CUARTEL_2', 'Cuartel II', 'barracks', 0.590, 0.80,  0.10, 0.18, {accentKey:'red2'}),
    z('ESCONDITE', 'Escondite',  'hideout',  0.670, 0.78,  0.10, 0.16),
  ];
}"""

src = src[:start] + NEW_GETLAYOUT + src[end:]
print("✅ getLayout — zonas cartesianas fijas")

# ── PATCH 2: reemplazar _hitTest para usar zona cartesiana ────────────────────
OLD_HITTEST = """// Test de hit usando hitbox registrado
function _hitTest(b, mx, my) {
  if (!b.hw) return false;
  return mx >= b.hx && mx <= b.hx + b.hw &&
         my >= b.hy && my <= b.hy + b.hh;
}"""

NEW_HITTEST = """// Test de hit usando zona cartesiana fija
function _hitTest(b, mx, my) {
  if (b.zw === undefined) return false;
  return mx >= b.zx && mx <= b.zx + b.zw &&
         my >= b.zy && my <= b.zy + b.zh;
}"""

if OLD_HITTEST in src:
    src = src.replace(OLD_HITTEST, NEW_HITTEST)
    print("✅ _hitTest — usa zona cartesiana zx,zy,zw,zh")
else:
    print("⚠️  _hitTest no encontrado — añadir manualmente")

# ── PATCH 3: debug muestra zona cartesiana ────────────────────────────────────
OLD_DEBUG = """  // Debug visual: mostrar hitbox si window._ewDebugHitbox = true
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
  }"""

NEW_DEBUG = """  // Debug visual: mostrar zona cartesiana si window._ewDebugHitbox = true
  if (window._ewDebugHitbox && b.zw !== undefined) {
    ctx.save();
    ctx.strokeStyle = b.hovered ? 'rgba(255,80,80,0.9)' : 'rgba(80,255,80,0.5)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 3]);
    ctx.strokeRect(b.zx, b.zy, b.zw, b.zh);
    ctx.setLineDash([]);
    ctx.fillStyle = b.hovered ? 'rgba(255,80,80,0.15)' : 'rgba(80,255,80,0.08)';
    ctx.fillRect(b.zx, b.zy, b.zw, b.zh);
    ctx.fillStyle = 'rgba(255,255,255,0.9)';
    ctx.font = 'bold 9px monospace';
    ctx.fillText(b.key, b.zx + 3, b.zy + 11);
    ctx.restore();
  }"""

if OLD_DEBUG in src:
    src = src.replace(OLD_DEBUG, NEW_DEBUG)
    print("✅ Debug — muestra zona cartesiana")
else:
    print("⚠️  Debug block no encontrado")

# ── PATCH 4: highlight hover usa zona cartesiana ──────────────────────────────
OLD_HOVER = """  // Highlight hover ANTES de dibujar (halo detrás del edificio)
  if (b.hovered) {
    ctx.save();
    ctx.strokeStyle = 'rgba(255,220,80,0.85)';
    ctx.lineWidth   = 2.5;
    ctx.shadowColor = 'rgba(255,200,50,0.9)';
    ctx.shadowBlur  = 18;
    ctx.strokeRect(b.hx - 3, b.hy - 3, b.hw + 6, b.hh + 6);
    ctx.restore();
  }"""

NEW_HOVER = """  // Highlight hover ANTES de dibujar (halo suave sobre la zona)
  if (b.hovered && b.zw !== undefined) {
    ctx.save();
    ctx.strokeStyle = 'rgba(255,220,80,0.7)';
    ctx.lineWidth   = 2;
    ctx.shadowColor = 'rgba(255,200,50,0.8)';
    ctx.shadowBlur  = 14;
    ctx.strokeRect(b.zx + 2, b.zy + 2, b.zw - 4, b.zh - 4);
    ctx.fillStyle = 'rgba(255,210,50,0.06)';
    ctx.fillRect(b.zx + 2, b.zy + 2, b.zw - 4, b.zh - 4);
    ctx.restore();
  }"""

if OLD_HOVER in src:
    src = src.replace(OLD_HOVER, NEW_HOVER)
    print("✅ Hover highlight — usa zona cartesiana")
else:
    print("⚠️  Hover highlight no encontrado")

# ── Guardar ───────────────────────────────────────────────────────────────────
if src != original:
    backup = TARGET.with_suffix(".js.bak4")
    backup.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")
    print(f"\n✅ city.js guardado (backup: {backup})")
else:
    print("\n⚠️  Sin cambios")

print("""
run.bat + Ctrl+Shift+R

Cada edificio tiene ahora su zona exclusiva en coordenadas de pantalla.
Hover sobre la zona → highlight dorado + label brillante.
Click → abre menú.

Para ver las zonas:  (en consola F12)
  window._ewDebugHitbox = true
""")
