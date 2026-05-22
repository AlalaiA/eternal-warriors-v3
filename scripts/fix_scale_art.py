"""
fix_scale_art.py
Eternal Warriors v3.0 — C.Ciudad dominante + terreno con contraste

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_scale_art.py
"""

from pathlib import Path
import sys

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = TARGET.read_text(encoding="utf-8")

# ── FIX 1: Alturas de sprites — C.Ciudad mucho más grande ────────────────────
OLD1 = """\
  const SH = {cityhall:105,sanctuary:78,temple:85,university:80,
    warehouse:72,watchtower:82,travel:72,house:62,
    barracks:78,forge:66,hideout:50};"""
NEW1 = """\
  const SH = {cityhall:210,sanctuary:88,temple:95,university:88,
    warehouse:80,watchtower:90,travel:80,house:68,
    barracks:85,forge:72,hideout:55};"""

c = src.count(OLD1)
if c != 1: print(f"ERROR fix 1: {c}x"); sys.exit(1)
src = src.replace(OLD1, NEW1)
print("OK fix 1: C.Ciudad h=210, resto proporcional")

# ── FIX 2: C.Ciudad más arriba para que domine sin cortarse ──────────────────
OLD2 = "    b(      0,  -iy*0.65, 'CENTRO_DE_CIUDAD', 'C.Ciudad',      'cityhall'),"
NEW2 = "    b(      0,  -iy*0.55, 'CENTRO_DE_CIUDAD', 'C.Ciudad',      'cityhall'),"

c = src.count(OLD2)
if c != 1: print(f"ERROR fix 2: {c}x"); sys.exit(1)
src = src.replace(OLD2, NEW2)
print("OK fix 2: C.Ciudad reposicionado al fondo central")

# ── FIX 3: Terreno — colores base más visibles con más contraste ──────────────
OLD3 = """\
      // Base de piedra muy oscura con tinte de dualidad
      const baseR = even ? Math.round(12 + blend * 8)  : Math.round(10 + blend * 6);
      const baseG = even ? Math.round(14 - blend * 4)  : Math.round(11 - blend * 3);
      const baseB = even ? Math.round(18 - blend * 8)  : Math.round(15 - blend * 6);
      ctx.fillStyle = `rgb(${baseR},${baseG},${baseB})`;"""
NEW3 = """\
      // Piedra oscura con contraste visible entre celdas
      const baseR = even ? Math.round(22 + blend * 14) : Math.round(14 + blend * 10);
      const baseG = even ? Math.round(20 - blend * 6)  : Math.round(13 - blend * 4);
      const baseB = even ? Math.round(28 - blend * 10) : Math.round(18 - blend * 7);
      ctx.fillStyle = `rgb(${baseR},${baseG},${baseB})`;"""

c = src.count(OLD3)
if c != 1: print(f"ERROR fix 3: {c}x"); sys.exit(1)
src = src.replace(OLD3, NEW3)
print("OK fix 3: terreno más contrastado")

# ── FIX 4: Venas de luz más visibles ─────────────────────────────────────────
OLD4 = """\
        const vAlpha = 0.06 + 0.04 * Math.sin(tick * 0.02 + col * 0.5 + r * 0.7);"""
NEW4 = """\
        const vAlpha = 0.18 + 0.10 * Math.sin(tick * 0.02 + col * 0.5 + r * 0.7);"""

c = src.count(OLD4)
if c != 1: print(f"ERROR fix 4: {c}x"); sys.exit(1)
src = src.replace(OLD4, NEW4)
print("OK fix 4: venas mágicas más brillantes")

# ── FIX 5: Suelo interior — losas más visibles ───────────────────────────────
OLD5 = """\
      const base = even ? 16 : 13;
      ctx.fillStyle = `rgb(${base},${base},${Math.round(base*1.2)})`;"""
NEW5 = """\
      const base = even ? 28 : 20;
      ctx.fillStyle = `rgb(${base},${Math.round(base*0.9)},${Math.round(base*1.3)})`;"""

c = src.count(OLD5)
if c != 1: print(f"ERROR fix 5: {c}x"); sys.exit(1)
src = src.replace(OLD5, NEW5)
print("OK fix 5: suelo interior más visible")

# ── FIX 6: Borde dorado losas más visible ────────────────────────────────────
OLD6 = """\
      const borderAlpha = 0.12 + 0.05 * Math.sin(tick * 0.015 + col + r);
      ctx.strokeStyle = `rgba(180,145,40,${borderAlpha})`; ctx.lineWidth = 0.6; ctx.stroke();"""
NEW6 = """\
      const borderAlpha = 0.28 + 0.10 * Math.sin(tick * 0.015 + col + r);
      ctx.strokeStyle = `rgba(200,160,50,${borderAlpha})`; ctx.lineWidth = 0.7; ctx.stroke();"""

c = src.count(OLD6)
if c != 1: print(f"ERROR fix 6: {c}x"); sys.exit(1)
src = src.replace(OLD6, NEW6)
print("OK fix 6: bordes dorados losas más brillantes")

TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO.")
print("  Ctrl+C → run.bat → Ctrl+Shift+R en http://127.0.0.1:8000/game")
