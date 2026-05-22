"""
fix_cy_ciudad.py
Eternal Warriors v3.0 — C.Ciudad no se corta + alpha semitransparente

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_cy_ciudad.py
"""

from pathlib import Path
from PIL import Image
import numpy as np
import sys

# ── FIX 1: Eliminar píxeles semitransparentes del centro_ciudad.png ──────────
# Los píxeles con alfa 1-80 son el "halo" del checkerboard de Gemini
path = Path(r"E:\0000ew V2Claude\frontend\assets\buildings\centro_ciudad.png")
img = Image.open(path).convert("RGBA")
arr = np.array(img, dtype=np.uint16)

# Umbralizar: alfa < 90 → 0, alfa > 180 → 255, intermedio → escalar
alpha = arr[..., 3].astype(float)
alpha = np.where(alpha < 90,  0,
        np.where(alpha > 180, 255,
                 ((alpha - 90) / 90 * 255).clip(0, 255)))
arr[..., 3] = alpha.astype(np.uint16)
Image.fromarray(arr.astype(np.uint8), "RGBA").save(path, "PNG")
print("OK fix 1: centro_ciudad.png — alfa semitransparente corregido")

# ── FIX 2: cy H*0.62 → H*0.66 para que C.Ciudad no se corte por arriba ──────
TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = TARGET.read_text(encoding="utf-8")

OLD = "  const cx = W * 0.5, cy = H * 0.62;"
NEW = "  const cx = W * 0.5, cy = H * 0.66;"

c = src.count(OLD)
if c != 1: print(f"ERROR fix 2: {c}x"); sys.exit(1)
src = src.replace(OLD, NEW)
TARGET.write_text(src, encoding="utf-8")
print("OK fix 2: cy H*0.62 → H*0.66")

print()
print("HECHO.")
print("  Ctrl+C → run.bat → Ctrl+Shift+R en http://127.0.0.1:8000/game")
