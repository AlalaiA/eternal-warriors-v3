"""
fix_sprites_v3.py
Eternal Warriors v3.0 — Fix fondo blanco cuartel + torres canvas en muralla

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_sprites_v3.py
"""

from pathlib import Path
from PIL import Image
import numpy as np
import sys

DEST = Path(r"E:\0000ew V2Claude\frontend\assets\buildings")
TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 1 — Eliminar fondo blanco del cuartel
# ══════════════════════════════════════════════════════════════════════════════
def remove_light_bg(img, threshold=200, tolerance=22):
    img = img.convert("RGBA")
    arr = np.array(img, dtype=np.int32)
    r, g, b, a = arr[...,0], arr[...,1], arr[...,2], arr[...,3]
    brightness = (r + g + b) / 3
    is_light = brightness > threshold
    is_neutral = (np.abs(r-g) < tolerance) & (np.abs(r-b) < tolerance) & (np.abs(g-b) < tolerance)
    is_bg = is_light & is_neutral
    # Semitransparente para bordes
    semi = (brightness > threshold - 40) & (brightness <= threshold) & is_neutral
    result = arr.copy()
    result[..., 3] = np.where(is_bg, 0, np.where(semi, (arr[...,3] * 0.25).astype(int), arr[...,3]))
    return Image.fromarray(result.astype(np.uint8), "RGBA")

path = DEST / "cuartel.png"
if path.exists():
    img = Image.open(path)
    clean = remove_light_bg(img)
    clean.save(path, "PNG")
    print("OK fix 1: fondo blanco eliminado de cuartel.png")
else:
    print("ERROR fix 1: cuartel.png no encontrado")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# FIX 2 — Restaurar torres canvas en muralla (quitar sprite torre)
# ══════════════════════════════════════════════════════════════════════════════
src = TARGET.read_text(encoding="utf-8")

OLD_TOWER = """\
  // Torres en las 4 esquinas con sprite PNG
  const tH = 55 + lvl * 0.6;
  pts.forEach(([px, py]) => drawSprite(ctx, 'watchtower', px, py - wallH * 0.2, tH));"""

NEW_TOWER = "  // Torres en los 4 vértices\n  pts.forEach(([px, py]) => drawWallTower(ctx, px, py, wallH, lvl));"

c = src.count(OLD_TOWER)
if c != 1: print(f"ERROR fix 2: {c}x"); sys.exit(1)
src = src.replace(OLD_TOWER, NEW_TOWER)
print("OK fix 2: torres canvas restauradas en muralla")

TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO.")
print("  Ctrl+C → run.bat → Ctrl+Shift+R en http://127.0.0.1:8000/game")
