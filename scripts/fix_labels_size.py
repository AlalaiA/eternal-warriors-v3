"""
fix_labels_size.py
Eternal Warriors v3.0 — Corrige etiquetas y reduce tamaño de sprites

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_labels_size.py
"""

from pathlib import Path
import sys, re

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = TARGET.read_text(encoding="utf-8")

# ── FIX 1: Reducir alturas de sprites (estaban demasiado grandes) ─────────────
OLD_SH = """\
  const SH = {cityhall:150,sanctuary:105,temple:120,university:110,
    warehouse:100,watchtower:115,travel:100,house:88,
    barracks:108,forge:92,hideout:68};"""

NEW_SH = """\
  const SH = {cityhall:105,sanctuary:78,temple:85,university:80,
    warehouse:72,watchtower:82,travel:72,house:62,
    barracks:78,forge:66,hideout:50};"""

c = src.count(OLD_SH)
if c != 1: print(f"ERROR fix 1: {c}x"); sys.exit(1)
src = src.replace(OLD_SH, NEW_SH)
print("OK fix 1: alturas reducidas")

# ── FIX 2: Corregir etiquetas en getLayout ────────────────────────────────────
fixes = [
    ("'Templo Luz'",    "'Templo'"),
    ("'Templo Tierra'", "'Templo'"),
    ("'Templo Guerra'", "'Templo'"),
    ("'Cuartel 1'",     "'Cuartel'"),
    ("'Cuartel 2'",     "'Cuartel'"),
    ("'Cuartel Luz'",   "'Cuartel'"),
    ("'Cuartel Fuego'", "'Cuartel'"),
]
for old, new in fixes:
    if old in src:
        src = src.replace(old, new)
        print(f"OK fix 2: {old} → {new}")

TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO.")
print("  Ctrl+C → run.bat → Ctrl+Shift+R en http://127.0.0.1:8000/game")
