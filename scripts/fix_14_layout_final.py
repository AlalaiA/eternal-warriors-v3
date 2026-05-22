"""
fix_14_layout_final.py

Layout aprobado con zonas cartesianas exclusivas.
Cuarteles frente, templos segunda fila, resto al fondo.
Hover ilumina toda la zona. Click abre menú.

Ejecutar desde: E:\\0000ew V2Claude\\
"""
import pathlib, sys

TARGET = pathlib.Path("frontend/js/screens/city.js")
if not TARGET.exists():
    sys.exit(f"ERROR: {TARGET} no encontrado")

src = TARGET.read_text(encoding="utf-8")
original = src

# ─── PATCH 1: getLayout con zonas cartesianas aprobadas ───────────────────────
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
  const W = cx * 2;
  const H = cy / 0.58;

  // z(): define edificio con zona cartesiana exclusiva
  // px,py = posición visual del edificio en pantalla (para art*)
  // zx,zy,zw,zh = zona de interacción (sin solapamiento entre edificios)
  // pctPX,pctPY = posición visual; pctZX,pctZY,pctZW,pctZH = zona interacción
  const z = (key, label, type, pctPX, pctPY, pctZX, pctZY, pctZW, pctZH, extra={}) => ({
    key, label, type,
    lvl: lv(key),
    x: W * pctPX,
    y: H * pctPY,
    zx: W * pctZX,
    zy: H * pctZY,
    zw: W * pctZW,
    zh: H * pctZH,
    hovered: false,
    ...extra,
  });

  // ── FILA FONDO ─────────────────────────────────────────────────────────────
  // Santuario izq | C.Ciudad centro | Universidad der
  // Zona Y: 0.08 → 0.38 del canvas

  // ── FILA MEDIA-ALTA ────────────────────────────────────────────────────────
  // Casa | Almacén | Escondite | Herrería | C.Viajes
  // Zona Y: 0.36 → 0.57

  // ── FILA TEMPLOS ──────────────────────────────────────────────────────────
  // Templo I | Templo II | Templo III  (3 zonas iguales)
  // Zona Y: 0.55 → 0.73

  // ── FILA CUARTELES ────────────────────────────────────────────────────────
  // Cuartel I (izq mitad) | Cuartel II (der mitad)
  // Zona Y: 0.72 → 0.90

  return [
    // FONDO
    z('SANTUARIO_ARCANO', 'Santuario',   'sanctuary',  0.25, 0.44,   0.08, 0.08, 0.24, 0.30),
    z('CENTRO_DE_CIUDAD', 'C.Ciudad',    'cityhall',   0.50, 0.38,   0.34, 0.08, 0.32, 0.30),
    z('UNIVERSIDAD',      'Universidad', 'university', 0.75, 0.42,   0.68, 0.08, 0.24, 0.30),

    // FILA MEDIA
    z('CASA',             'Casa',        'house',      0.14, 0.55,   0.08, 0.36, 0.14, 0.21),
    z('ALMACEN',          'Almacén',     'warehouse',  0.31, 0.53,   0.22, 0.36, 0.14, 0.21),
    z('ESCONDITE',        'Escondite',   'hideout',    0.50, 0.52,   0.38, 0.36, 0.12, 0.21),
    z('HERRERIA',         'Herrería',    'forge',      0.67, 0.53,   0.52, 0.36, 0.14, 0.21),
    z('CENTRO_DE_VIAJES', 'C.Viajes',    'travel',     0.84, 0.52,   0.68, 0.36, 0.24, 0.21),

    // TEMPLOS — 3 zonas iguales sin hueco
    z('TEMPLO_1', 'Templo I',   'temple', 0.17, 0.66,   0.08, 0.55, 0.28, 0.18, {accentKey:'blue'}),
    z('TEMPLO_2', 'Templo II',  'temple', 0.50, 0.66,   0.37, 0.55, 0.28, 0.18, {accentKey:'gold'}),
    z('TEMPLO_3', 'Templo III', 'temple', 0.82, 0.64,   0.66, 0.55, 0.28, 0.18, {accentKey:'purple'}),

    // CUARTELES — 2 zonas grandes primer plano
    z('CUARTEL_1', 'Cuartel I',  'barracks', 0.28, 0.80,   0.08, 0.72, 0.42, 0.18, {accentKey:'red1'}),
    z('CUARTEL_2', 'Cuartel II', 'barracks', 0.72, 0.80,   0.52, 0.72, 0.42, 0.18, {accentKey:'red2'}),
  ];
}"""

src = src[:start] + NEW_LAYOUT + src[end:]
print("✅ PATCH 1 — getLayout zonas aprobadas")

# ─── PATCH 2: drawBuilding — glow sobre toda la zona ──────────────────────────
OLD_HOVER = """  // Highlight hover ANTES de dibujar (halo suave sobre la zona)
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

NEW_HOVER = """  // Hover: iluminar TODA la zona del edificio
  if (b.hovered && b.zw !== undefined) {
    ctx.save();
    // Relleno suave dorado
    ctx.fillStyle = 'rgba(255,210,60,0.10)';
    ctx.fillRect(b.zx, b.zy, b.zw, b.zh);
    // Borde dorado brillante
    ctx.strokeStyle = 'rgba(255,220,80,0.90)';
    ctx.lineWidth = 2;
    ctx.strokeRect(b.zx, b.zy, b.zw, b.zh);
    // Esquinas reforzadas
    const cs = 10;
    ctx.strokeStyle = 'rgba(255,240,120,1.0)';
    ctx.lineWidth = 2.5;
    [[b.zx,b.zy],[b.zx+b.zw,b.zy],[b.zx,b.zy+b.zh],[b.zx+b.zw,b.zy+b.zh]].forEach(([cx2,cy2],i) => {
      const sx = i%2===0?1:-1, sy = i<2?1:-1;
      ctx.beginPath();
      ctx.moveTo(cx2+sx*cs, cy2); ctx.lineTo(cx2, cy2); ctx.lineTo(cx2, cy2+sy*cs);
      ctx.stroke();
    });
    ctx.restore();
  }"""

if OLD_HOVER in src:
    src = src.replace(OLD_HOVER, NEW_HOVER)
    print("✅ PATCH 2 — hover ilumina zona completa con esquinas")
else:
    print("⚠️  PATCH 2 — bloque hover no encontrado")

# ─── PATCH 3: debug usa zona cartesiana ───────────────────────────────────────
OLD_DEBUG = """  // Debug visual: mostrar zona cartesiana si window._ewDebugHitbox = true
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

NEW_DEBUG = """  // Debug: mostrar zonas si window._ewDebugHitbox = true
  if (window._ewDebugHitbox && b.zw !== undefined) {
    ctx.save();
    ctx.strokeStyle = b.hovered ? '#f55' : '#0f0';
    ctx.lineWidth = 1; ctx.setLineDash([3,2]);
    ctx.strokeRect(b.zx, b.zy, b.zw, b.zh);
    ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(255,255,255,0.8)';
    ctx.font = '8px monospace';
    ctx.fillText(b.key, b.zx+3, b.zy+10);
    ctx.restore();
  }"""

if OLD_DEBUG in src:
    src = src.replace(OLD_DEBUG, NEW_DEBUG)
    print("✅ PATCH 3 — debug simplificado")

# ─── PATCH 4: _hitTest usa zona cartesiana ────────────────────────────────────
OLD_HIT = """// Test de hit usando zona cartesiana fija
function _hitTest(b, mx, my) {
  if (b.zw === undefined) return false;
  return mx >= b.zx && mx <= b.zx + b.zw &&
         my >= b.zy && my <= b.zy + b.zh;
}"""

if OLD_HIT not in src:
    # puede estar como hitbox registrado
    OLD_HIT2 = """// Test de hit usando hitbox registrado
function _hitTest(b, mx, my) {
  if (!b.hw) return false;
  return mx >= b.hx && mx <= b.hx + b.hw &&
         my >= b.hy && my <= b.hy + b.hh;
}"""
    if OLD_HIT2 in src:
        src = src.replace(OLD_HIT2,
"""// Test de hit: zona cartesiana exclusiva por edificio
function _hitTest(b, mx, my) {
  if (b.zw === undefined) return false;
  return mx >= b.zx && mx <= b.zx + b.zw &&
         my >= b.zy && my <= b.zy + b.zh;
}""")
        print("✅ PATCH 4 — _hitTest zona cartesiana (reemplazo alternativo)")
    else:
        print("⚠️  PATCH 4 — _hitTest no encontrado")
else:
    print("ℹ️  PATCH 4 — _hitTest ya correcto")

# ─── PATCH 5: onclick/onmousemove — buscar de frente a fondo ─────────────────
# Cuarteles están al frente (último en el array) → reverse() correcto
# onmousemove: actualizar hovered + tooltip con nombre
OLD_MOVE = """    const buildings = [..._cityClickData.buildings].reverse();
    const hit = buildings.find(b => _hitTest(b, mx, my));
    // Actualizar estado hover en todos los edificios
    let changed = false;
    _cityClickData.buildings.forEach(b => {
      const wasHovered = b.hovered;
      b.hovered = (hit && b.key === hit.key);
      if (b.hovered !== wasHovered) changed = true;
    });
    canvas.style.cursor = hit ? 'pointer' : 'default';
    // Mostrar tooltip con nombre del edificio
    canvas.title = hit ? hit.label + (hit.lvl ? ' Nv.' + hit.lvl : '') : '';"""

NEW_MOVE = """    const buildings = [..._cityClickData.buildings].reverse();
    const hit = buildings.find(b => _hitTest(b, mx, my));
    _cityClickData.buildings.forEach(b => { b.hovered = !!(hit && b.key === hit.key); });
    canvas.style.cursor = hit ? 'pointer' : 'default';
    canvas.title = hit ? `${hit.label}${hit.lvl ? ' Nv.'+hit.lvl : ' (sin construir)'}` : '';"""

if OLD_MOVE in src:
    src = src.replace(OLD_MOVE, NEW_MOVE)
    print("✅ PATCH 5 — onmousemove simplificado + tooltip")
else:
    print("⚠️  PATCH 5 — onmousemove no encontrado exactamente")

# ─── PATCH 6: drawLabel — posición fija en borde inferior de la zona ──────────
# En vez de dibujar el label en b.y (posición visual del edificio),
# dibujarlo en el borde inferior de la zona (b.zy + b.zh - 4)
OLD_LABEL_CALL = "  drawLabel(ctx, b.x, b.y, b.label, lvl, b.type, b.hovered);"
NEW_LABEL_CALL = """  // Label siempre en borde inferior de la zona
  const labelY = b.zw !== undefined ? b.zy + b.zh - 2 : b.y;
  drawLabel(ctx, b.zx + b.zw/2, labelY, b.label, lvl, b.type, b.hovered);"""

if OLD_LABEL_CALL in src:
    src = src.replace(OLD_LABEL_CALL, NEW_LABEL_CALL)
    print("✅ PATCH 6 — label en borde inferior de zona")
else:
    print("⚠️  PATCH 6 — drawLabel call no encontrado")

# ─── Guardar ──────────────────────────────────────────────────────────────────
if src != original:
    backup = TARGET.with_suffix(".js.bak5")
    backup.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")
    print(f"\n✅ city.js guardado (backup: {backup})")
else:
    print("\n⚠️  Sin cambios — revisar anclas")

print("""
run.bat + Ctrl+Shift+R

Comportamiento:
  Hover sobre zona → toda el área se ilumina en dorado con esquinas marcadas
  Click → abre menú del edificio
  Tooltip nativo muestra nombre + nivel

Debug (consola F12):
  window._ewDebugHitbox = true   ← ver zonas verdes
""")
