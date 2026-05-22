"""
fix_cy2.py
Eternal Warriors v3.0 — Ajusta cy y tamaño del canvas de ciudad

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_cy2.py
"""

from pathlib import Path
import sys

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = TARGET.read_text(encoding="utf-8")

# cy más abajo para que la ciudad quede centrada
OLD = "  const cx = W * 0.5, cy = H * 0.66;"
NEW = "  const cx = W * 0.5, cy = H * 0.58;"

c = src.count(OLD)
if c != 1: print(f"ERROR: {c}x"); sys.exit(1)
src = src.replace(OLD, NEW)
TARGET.write_text(src, encoding="utf-8")
print("OK: cy H*0.66 → H*0.58")
print()
print("  Ctrl+Shift+R en http://127.0.0.1:8000/game")
