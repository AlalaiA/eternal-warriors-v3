"""
install_png.py
Eternal Warriors v3.0 — Actualiza city.js para usar PNGs + torres en muralla

Cambios:
  1. _SPRITE_MAP: .svg → .png
  2. drawWall: añade drawWallTowerSprite() en las 4 esquinas usando torre_vigilancia.png
  3. getLayout: elimina TORRE_DE_VIGILANCIA del interior
  4. Alturas de sprites ajustadas a las proporciones reales de los PNGs

Corre desde: E:\\0000ew V2Claude\\
Comando:     python install_png.py
"""

from pathlib import Path
import sys, shutil

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
if not TARGET.exists():
    print(f"ERROR: {TARGET}"); sys.exit(1)

bak = TARGET.with_suffix(".js.png.bak")
shutil.copy2(TARGET, bak)
print(f"Backup: {bak.name}")

src = TARGET.read_text(encoding="utf-8")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 1 — _SPRITE_MAP: .svg → .png
# ══════════════════════════════════════════════════════════════════════════════
OLD_MAP = """\
const _SPRITE_MAP = {
  cityhall:   'centro_ciudad.svg',
  sanctuary:  'santuario.svg',
  temple:     'templo.svg',
  university: 'universidad.svg',
  warehouse:  'almacen.svg',
  watchtower: 'torre_vigilancia.svg',
  travel:     'centro_viajes.svg',
  house:      'casa.svg',
  barracks:   'cuartel.svg',
  forge:      'herreria.svg',
  hideout:    'escondite.svg',
};"""

NEW_MAP = """\
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
};"""

c = src.count(OLD_MAP)
if c != 1: print(f"ERROR fix 1: {c} veces"); sys.exit(1)
src = src.replace(OLD_MAP, NEW_MAP)
print("OK fix 1: _SPRITE_MAP → .png")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 2 — drawBuilding: alturas ajustadas a proporciones reales de los PNGs
# ══════════════════════════════════════════════════════════════════════════════
OLD_H = """\
  const H = {
    cityhall: 130, sanctuary: 90, temple: 110,
    university: 95, warehouse: 80, watchtower: 110,
    travel: 85, barracks: 88, forge: 80,
    house: 72, hideout: 58
  };"""

NEW_H = """\
  // Alturas calibradas para los PNGs de Gemini (relación ~3:4)
  const H = {
    cityhall:   148,
    sanctuary:  100,
    temple:     118,
    university: 108,
    warehouse:   96,
    watchtower: 120,
    travel:      96,
    house:        82,
    barracks:   102,
    forge:        88,
    hideout:      64,
  };"""

c = src.count(OLD_H)
if c != 1: print(f"ERROR fix 2: {c} veces"); sys.exit(1)
src = src.replace(OLD_H, NEW_H)
print("OK fix 2: alturas de sprites ajustadas")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 3 — drawWall: torres en las 4 esquinas usando el sprite PNG
# ══════════════════════════════════════════════════════════════════════════════
OLD_TOWERS = "  // Torres en los 4 vértices\n  pts.forEach(([px, py]) => drawWallTower(ctx, px, py, wallH, lvl));"
NEW_TOWERS = """\
  // Torres en las 4 esquinas — sprite PNG escalado
  const towerH = 52 + lvl * 0.5;
  pts.forEach(([px, py]) => drawSprite(ctx, 'watchtower', px, py - wallH * 0.3, towerH));"""

c = src.count(OLD_TOWERS)
if c != 1: print(f"ERROR fix 3: {c} veces"); sys.exit(1)
src = src.replace(OLD_TOWERS, NEW_TOWERS)
print("OK fix 3: torres en esquinas de muralla con sprite PNG")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 4 — getLayout: eliminar TORRE_DE_VIGILANCIA del interior
# ══════════════════════════════════════════════════════════════════════════════
OLD_TOWER_LINE = "    b( +ix*0.25,  +iy*0.05, 'TORRE_DE_VIGILANCIA','Torre',        'watchtower'),\n\n"
NEW_TOWER_LINE = ""

c = src.count(OLD_TOWER_LINE)
if c != 1:
    # Intentar variante sin doble salto
    OLD_TOWER_LINE = "    b( +ix*0.25,  +iy*0.05, 'TORRE_DE_VIGILANCIA','Torre',        'watchtower'),\n"
    c = src.count(OLD_TOWER_LINE)
    if c != 1: print(f"ERROR fix 4: torre interior {c} veces. Abortando."); sys.exit(1)

src = src.replace(OLD_TOWER_LINE, NEW_TOWER_LINE)
print("OK fix 4: TORRE_DE_VIGILANCIA eliminada del interior")

# ══════════════════════════════════════════════════════════════════════════════
# Guardar
# ══════════════════════════════════════════════════════════════════════════════
TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO — city.js actualizado para PNGs.")
print()
print("Para verificar:")
print("  Ctrl+C → run.bat")
print("  Abre en pestaña nueva incógnito: http://127.0.0.1:8000/game")
print("  Los 11 edificios deben verse con los sprites de Gemini.")
print("  Las 4 esquinas de la muralla deben tener la torre escalada.")
print("  Si algún sprite no carga: F12 > Console muestra la ruta exacta.")
