"""
fix_city_final.py
Eternal Warriors v3.0 — Rediseño definitivo del layout

Sistema nuevo:
  - La muralla define el espacio: rx=100*scale, ry=57*scale (nivel 40 → rx=116, ry=66)
  - Los edificios se posicionan con coordenadas absolutas relativas a (cx, cy)
  - C.Ciudad: cuadrante superior (entre vértice N y centro), ~25% del área total
  - Escala fija por tipo (no crece infinitamente con el nivel)
  - Painter's algorithm por Y

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_city_final.py
"""

from pathlib import Path
import sys, re

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
if not TARGET.exists():
    print(f"ERROR: No se encontró:\n  {TARGET}")
    sys.exit(1)

src = TARGET.read_text(encoding="utf-8")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 1 — drawBuilding: escala fija por tipo, no acumulativa con nivel
# ══════════════════════════════════════════════════════════════════════════════
OLD_BLD = """\
function drawBuilding(ctx, b, c) {
  const lvl = b.lvl || 0;
  // C.Ciudad domina: scMax alto. Santuario complementa: scMax bajo.
  const scMax = b.type==='cityhall' ? 28
              : b.type==='sanctuary' ? 10
              : b.type==='watchtower' ? 16
              : b.type==='temple' ? 12
              : 12;
  const sc = 0.42 + Math.min(lvl,scMax)*0.013;
  const x = b.x, y = b.y;"""

NEW_BLD = """\
function drawBuilding(ctx, b, c) {
  const lvl = b.lvl || 0;
  // Escala fija por tipo — tamaño visual consistente sin importar el nivel
  const sc = b.type==='cityhall'   ? 1.10
           : b.type==='sanctuary'  ? 0.72
           : b.type==='temple'     ? 0.68
           : b.type==='university' ? 0.72
           : b.type==='warehouse'  ? 0.65
           : b.type==='watchtower' ? 0.60
           : b.type==='travel'     ? 0.62
           : b.type==='barracks'   ? 0.62
           : b.type==='forge'      ? 0.60
           : b.type==='house'      ? 0.58
           : b.type==='hideout'    ? 0.55
           : 0.60;
  const x = b.x, y = b.y;"""

c = src.count(OLD_BLD)
if c != 1:
    print(f"ERROR fix 1: ancla encontrada {c} veces. Abortando.")
    sys.exit(1)
src = src.replace(OLD_BLD, NEW_BLD)
print("OK fix 1: drawBuilding — escala fija por tipo")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 2 — getLayout: coordenadas absolutas relativas a la muralla
#
# Muralla nivel 40: scale=1.16, rx=116, ry=66
# Vértices:
#   N = (cx,        cy-66)   ← arriba
#   E = (cx+116,    cy)      ← derecha
#   S = (cx,        cy+66)   ← abajo
#   W = (cx-116,    cy)      ← izquierda
#
# Cuadrantes (medios entre vértices):
#   NW_mid = (cx-58, cy-33)  ← mitad arista N→W
#   NE_mid = (cx+58, cy-33)  ← mitad arista N→E
#   SW_mid = (cx-58, cy+33)  ← mitad arista S→W
#   SE_mid = (cx+58, cy+33)  ← mitad arista S→E
#
# Layout:
#   C.Ciudad    → cuadrante N: (cx,    cy-44)   [25% del área]
#   Santuario   → (cx-55,  cy-22)
#   Templo Luz  → (cx+55,  cy-22)
#   Universidad → (cx-85,  cy-8)
#   Templo Tierra→ (cx-38, cy+5)
#   Torre       → (cx+38,  cy+5)
#   C.Viajes    → (cx+85,  cy-8)
#   Almacén     → (cx-85,  cy+20)
#   Templo Guerra→ (cx+85, cy+8)
#   Casa        → (cx-75,  cy+38)
#   Cuartel 1   → (cx-30,  cy+38)
#   Herrería    → (cx+30,  cy+38)
#   Cuartel 2   → (cx+75,  cy+38)
#   Escondite   → (cx,     cy+52)
# ══════════════════════════════════════════════════════════════════════════════
pattern = r'function getLayout\(c, cx, cy\) \{.+?\n\}'
match = re.search(pattern, src, re.DOTALL)
if not match:
    print("ERROR fix 2: no se encontró getLayout. Abortando.")
    sys.exit(1)

OLD_LAYOUT = match.group(0)

NEW_LAYOUT = """\
function getLayout(c, cx, cy) {
  const lv = k => Number(c[k]||0);

  // Coordenadas absolutas relativas a (cx, cy).
  // La muralla a nivel 40 ocupa rx≈116, ry≈66.
  // C.Ciudad en el cuadrante superior (N), ~25% del área total.
  // Painter's algorithm: ordenar por y (iy).
  const b = (ox, oy, key, label, type, extra={}) => ({
    key, label, lvl:lv(key),
    x: cx + ox, y: cy + oy, iy: cy + oy,
    type, ...extra
  });

  return [
    // ── Cuadrante N: C.Ciudad domina ─────────────────────────────────────────
    b(   0, -44, 'CENTRO_DE_CIUDAD', 'C.Ciudad',      'cityhall'),

    // ── Segundo plano: templos y santuario ───────────────────────────────────
    b( -55, -20, 'SANTUARIO_ARCANO', 'Santuario',     'sanctuary'),
    b( +55, -20, 'TEMPLO_3',         'Templo Luz',    'temple',   {accent:'#7ec8e3'}),

    // ── Plano medio: servicios ───────────────────────────────────────────────
    b( -88,  -5, 'UNIVERSIDAD',      'Universidad',   'university'),
    b( -38,  +5, 'TEMPLO_1',         'Templo Tierra', 'temple',   {accent:'#8a9040'}),
    b( +38,  +5, 'TORRE_DE_VIGILANCIA','Torre',        'watchtower'),
    b( +88,  -5, 'TEMPLO_2',         'Templo Guerra', 'temple',   {accent:'#c0452a'}),

    // ── Plano medio bajo ─────────────────────────────────────────────────────
    b( -88, +22, 'ALMACEN',          'Almacén',       'warehouse'),
    b( +88, +22, 'CENTRO_DE_VIAJES', 'C.Viajes',      'travel'),

    // ── Primer plano ─────────────────────────────────────────────────────────
    b( -75, +40, 'CASA',             'Casa',          'house'),
    b( -28, +40, 'CUARTEL_1',        'Cuartel 1',     'barracks'),
    b( +28, +40, 'HERRERIA',         'Herrería',      'forge'),
    b( +75, +40, 'CUARTEL_2',        'Cuartel 2',     'barracks'),

    // ── Frente ───────────────────────────────────────────────────────────────
    b(   0, +54, 'ESCONDITE',        'Escondite',     'hideout'),
  ];
}"""

if OLD_LAYOUT not in src:
    print("ERROR fix 2: ancla getLayout no encontrada. Abortando.")
    sys.exit(1)
src = src.replace(OLD_LAYOUT, NEW_LAYOUT)
print("OK fix 2: getLayout — coordenadas absolutas relativas a muralla")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 3 — cy: bajar origen para que C.Ciudad quepa arriba
# ══════════════════════════════════════════════════════════════════════════════
OLD_CY = "  const cx = W/2, cy = H*0.60;"
NEW_CY = "  const cx = W/2, cy = H*0.62;"
c = src.count(OLD_CY)
if c != 1:
    print(f"SKIP fix 3 (cy no encontrado: {c} veces) — continuando")
else:
    src = src.replace(OLD_CY, NEW_CY)
    print("OK fix 3: cy H*0.60 → H*0.62")

# ══════════════════════════════════════════════════════════════════════════════
# Guardar
# ══════════════════════════════════════════════════════════════════════════════
TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO — city.js actualizado.")
print()
print("Para verificar:")
print("  Recarga con Ctrl+Shift+R en http://127.0.0.1:8000/game")
print("  C.Ciudad debe estar en el cuadrante superior, bien centrado.")
print("  Todos los edificios dentro del rombo de la muralla.")
print("  Si alguno se sale, reporta cuál y hacia qué borde.")
