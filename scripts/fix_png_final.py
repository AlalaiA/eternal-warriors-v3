"""
fix_png_final.py
Eternal Warriors v3.0 — Instala sprites PNG limpiamente

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_png_final.py
"""

from pathlib import Path
import sys, re

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = TARGET.read_text(encoding="utf-8")

# ── FIX 1: Insertar sistema de sprites ───────────────────────────────────────
OLD1 = "let animFrame = null;\nlet tick = 0;"
NEW1 = """\
let animFrame = null;
let tick = 0;

const _sprites = {};
const _SPRITE_MAP = {
  cityhall:'centro_ciudad.png', sanctuary:'santuario.png',
  temple:'templo.png', university:'universidad.png',
  warehouse:'almacen.png', watchtower:'torre_vigilancia.png',
  travel:'centro_viajes.png', house:'casa.png',
  barracks:'cuartel.png', forge:'herreria.png', hideout:'escondite.png',
};
const _BASE = '/static/assets/buildings/';
function _load(t){if(_sprites[t])return _sprites[t];const i=new Image();i.src=_BASE+(_SPRITE_MAP[t]||t+'.png');_sprites[t]=i;return i;}
Object.keys(_SPRITE_MAP).forEach(_load);
function drawSprite(ctx,type,x,y,h){const i=_load(type);if(!i.complete||!i.naturalWidth)return;const w=h*(i.naturalWidth/i.naturalHeight);ctx.drawImage(i,x-w/2,y-h,w,h);}"""

c = src.count(OLD1)
if c != 1: print(f"ERROR fix 1: {c}x"); sys.exit(1)
src = src.replace(OLD1, NEW1)
print("OK fix 1: sistema sprites")

# ── FIX 2: drawBuilding usa drawSprite ───────────────────────────────────────
OLD2 = """\
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
  }
  ctx.restore();
  drawLabel(ctx, b.x, b.y, b.label, lvl, b.type);
}"""

NEW2 = """\
  const SH = {cityhall:150,sanctuary:105,temple:120,university:110,
    warehouse:100,watchtower:115,travel:100,house:88,
    barracks:108,forge:92,hideout:68};
  drawSprite(ctx, b.type, b.x, b.y, SH[b.type]||90);
  drawLabel(ctx, b.x, b.y, b.label, lvl, b.type);
}"""

c = src.count(OLD2)
if c != 1: print(f"ERROR fix 2: {c}x"); sys.exit(1)
src = src.replace(OLD2, NEW2)
print("OK fix 2: drawBuilding → sprites")

# ── FIX 3: Torres en muralla con sprite ──────────────────────────────────────
OLD3 = "  // Torres en los 4 vértices\n  pts.forEach(([px, py]) => drawWallTower(ctx, px, py, wallH, lvl));"
NEW3 = """\
  // Torres en las 4 esquinas con sprite PNG
  const tH = 55 + lvl * 0.6;
  pts.forEach(([px, py]) => drawSprite(ctx, 'watchtower', px, py - wallH * 0.2, tH));"""

c = src.count(OLD3)
if c != 1: print(f"ERROR fix 3: {c}x"); sys.exit(1)
src = src.replace(OLD3, NEW3)
print("OK fix 3: torres en muralla con sprite")

# ── FIX 4: Eliminar TORRE_DE_VIGILANCIA del interior ─────────────────────────
for variant in [
    "    b( +ix*0.25,  +iy*0.05, 'TORRE_DE_VIGILANCIA','Torre',        'watchtower'),\n\n",
    "    b( +ix*0.25,  +iy*0.05, 'TORRE_DE_VIGILANCIA','Torre',        'watchtower'),\n",
]:
    if src.count(variant) == 1:
        src = src.replace(variant, "")
        print("OK fix 4: torre interior eliminada")
        break
else:
    print("SKIP fix 4: torre interior no encontrada")

# ── Guardar ───────────────────────────────────────────────────────────────────
TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO.")
print()
print("Para verificar:")
print("  Ctrl+C → run.bat")
print("  Abre en incógnito: http://127.0.0.1:8000/game")
