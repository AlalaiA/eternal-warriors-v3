"""
install_png_system.py
Eternal Warriors v3.0 — Instala sistema de sprites PNG en city.js

Cambios:
  1. Inserta cache de imágenes + drawSprite() después de 'let animFrame'
  2. Reemplaza drawBuilding() para usar drawSprite()
  3. Reemplaza torres en muralla para usar sprite PNG
  4. Elimina TORRE_DE_VIGILANCIA del layout interior
  5. Corrige nombres: TEMPLO_1/2/3 → TEMPLO, CUARTEL_1/2 → CUARTEL

Corre desde: E:\\0000ew V2Claude\\
Comando:     python install_png_system.py
"""

from pathlib import Path
import sys, shutil, re

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
if not TARGET.exists():
    print(f"ERROR: {TARGET}"); sys.exit(1)

bak = TARGET.with_suffix(".js.bak2")
shutil.copy2(TARGET, bak)
print(f"Backup: {bak.name}")

src = TARGET.read_text(encoding="utf-8")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 1 — Insertar sistema de sprites después de 'let animFrame = null;'
# ══════════════════════════════════════════════════════════════════════════════
OLD_ANIM = "let animFrame = null;\nlet tick = 0;"
NEW_ANIM = """\
let animFrame = null;
let tick = 0;

// ── Sistema de sprites PNG ────────────────────────────────────────────────────
const _sprites = {};
const _SPRITE_MAP = {
  cityhall:   'centro_ciudad.png',
  sanctuary:  'santuario.png',
  temple:     'templo.png',
  university: 'universidad.png',
  warehouse:  'almacen.png',
  watchtower: 'torre_vigilancia.png',
  travel:     'centro_viajes.png',
  house:      'casa.png',
  barracks:   'cuartel.png',
  forge:      'herreria.png',
  hideout:    'escondite.png',
};
const _BASE_PATH = '/static/assets/buildings/';

function _loadSprite(type) {
  if (_sprites[type]) return _sprites[type];
  const img = new Image();
  img.src = _BASE_PATH + (_SPRITE_MAP[type] || type + '.png');
  _sprites[type] = img;
  return img;
}
Object.keys(_SPRITE_MAP).forEach(_loadSprite);

function drawSprite(ctx, type, x, y, h) {
  const img = _loadSprite(type);
  if (!img.complete || img.naturalWidth === 0) return;
  const w = h * (img.naturalWidth / img.naturalHeight);
  ctx.drawImage(img, x - w / 2, y - h, w, h);
}"""

c = src.count(OLD_ANIM)
if c != 1: print(f"ERROR fix 1: {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD_ANIM, NEW_ANIM)
print("OK fix 1: sistema de sprites insertado")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 2 — drawBuilding: usar drawSprite en lugar de funciones canvas
# ══════════════════════════════════════════════════════════════════════════════
OLD_BLD = """\
// ─── DISPATCHER DE EDIFICIOS ──────────────────────────────────────────────────
function drawBuilding(ctx, b) {
  const lvl = b.lvl || 0;
  // Escala fija por tipo — independiente del nivel para coherencia visual
  const SC = {
    cityhall: 1.10, sanctuary: 0.72, temple: 0.68,
    university: 0.70, warehouse: 0.64, watchtower: 0.58,
    travel: 0.62, barracks: 0.60, forge: 0.58,
    house: 0.56, hideout: 0.50
  };
  const sc = SC[b.type] || 0.58;
  ctx.save();
  switch (b.type) {
    case 'cityhall':    drawCityHall(ctx, b.x, b.y, sc, lvl);            break;
    case 'house':       drawHouse(ctx, b.x, b.y, sc, lvl);               break;
    case 'watchtower':  drawWatchtower(ctx, b.x, b.y, sc, lvl);          break;
    case 'travel':      drawTravelCenter(ctx, b.x, b.y, sc, lvl);        break;
    case 'hideout':     drawHideout(ctx, b.x, b.y, sc, lvl);             break;
    case 'warehouse':   drawWarehouse(ctx, b.x, b.y, sc, lvl);           break;
    case 'sanctuary':   drawSanctuary(ctx, b.x, b.y, sc, lvl);           break;
    case 'university':  drawUniversity(ctx, b.x, b.y, sc, lvl);          break;
    case 'forge':       drawForge(ctx, b.x, b.y, sc, lvl);               break;
    case 'temple':      drawTemple(ctx, b.x, b.y, sc, lvl, b.accent || '#c8a000'); break;
    case 'barracks':    drawBarracks(ctx, b.x, b.y, sc, lvl);            break;
  }"""

NEW_BLD = """\
// ─── DISPATCHER DE EDIFICIOS ──────────────────────────────────────────────────
function drawBuilding(ctx, b) {
  const lvl = b.lvl || 0;
  // Altura en px del sprite según tipo
  const H = {
    cityhall: 150, sanctuary: 105, temple: 120,
    university: 110, warehouse: 100, watchtower: 115,
    travel: 100, house: 88, barracks: 108,
    forge: 92, hideout: 68,
  };
  const h = H[b.type] || 90;
  drawSprite(ctx, b.type, b.x, b.y, h);
  {"""

c = src.count(OLD_BLD)
if c != 1: print(f"ERROR fix 2: {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD_BLD, NEW_BLD)
print("OK fix 2: drawBuilding usa sprites PNG")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 3 — Torres en muralla: usar sprite PNG
# ══════════════════════════════════════════════════════════════════════════════
OLD_TOWERS = "  // Torres en los 4 vértices\n  pts.forEach(([px, py]) => drawWallTower(ctx, px, py, wallH, lvl));"
NEW_TOWERS = """\
  // Torres en los 4 esquinas — sprite PNG escalado por nivel de muralla
  const towerH = 55 + lvl * 0.6;
  pts.forEach(([px, py]) => drawSprite(ctx, 'watchtower', px, py - wallH * 0.2, towerH));"""

c = src.count(OLD_TOWERS)
if c != 1: print(f"ERROR fix 3: {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD_TOWERS, NEW_TOWERS)
print("OK fix 3: torres en esquinas usan sprite PNG")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 4 — getLayout: eliminar TORRE_DE_VIGILANCIA + corregir nombres
# ══════════════════════════════════════════════════════════════════════════════
# Eliminar torre interior
OLD_TOWER = "    b( +ix*0.25,  +iy*0.05, 'TORRE_DE_VIGILANCIA','Torre',        'watchtower'),\n"
c = src.count(OLD_TOWER)
if c == 1:
    src = src.replace(OLD_TOWER, "")
    print("OK fix 4a: TORRE_DE_VIGILANCIA eliminada del interior")
else:
    print(f"SKIP fix 4a: torre interior {c} veces")

# Corregir nombres de templos y cuarteles
fixes_names = [
    ("'TEMPLO_3',         'Templo Luz',    'temple'", "'TEMPLO',  'Templo', 'temple'"),
    ("'TEMPLO_1',         'Templo Tierra', 'temple'", "'TEMPLO',  'Templo', 'temple'"),
    ("'TEMPLO_2',         'Templo Guerra', 'temple'", "'TEMPLO',  'Templo', 'temple'"),
    ("'CUARTEL_1',        'Cuartel 1',     'barracks'", "'CUARTEL', 'Cuartel', 'barracks'"),
    ("'CUARTEL_2',        'Cuartel 2',     'barracks'", "'CUARTEL', 'Cuartel', 'barracks'"),
]
for old, new in fixes_names:
    if old in src:
        src = src.replace(old, new)
        print(f"OK fix 4b: {old[:30]}...")

# ══════════════════════════════════════════════════════════════════════════════
# Guardar
# ══════════════════════════════════════════════════════════════════════════════
TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO — city.js actualizado.")
print()
print("Para verificar:")
print("  Ctrl+C → run.bat")
print("  Abre en pestaña nueva incógnito: http://127.0.0.1:8000/game")
print("  Los edificios deben verse con los sprites de Gemini.")
print("  Las 4 esquinas de la muralla deben tener la torre PNG.")
print("  Si algún sprite no carga: F12 > Console muestra la ruta exacta.")
