"""
fix_city_scale2.py
Eternal Warriors v3.0 — Escala parte 2: TW/TH con anclas específicas por función

Los fixes 1 y 2 del script anterior ya se aplicaron (cy y sc).
Este script completa los fixes 3-7 con anclas exactas por función.

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_city_scale2.py
"""

from pathlib import Path
import sys

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
if not TARGET.exists():
    print(f"ERROR: No se encontró:\n  {TARGET}")
    sys.exit(1)

src = TARGET.read_text(encoding="utf-8")

# ── FIX 3: drawCityDecor ─────────────────────────────────────────────────────
OLD = "function drawCityDecor(ctx, cx, cy, c) {\n  const TW=64, TH=32;"
NEW = "function drawCityDecor(ctx, cx, cy, c) {\n  const TW=48, TH=24;"
c = src.count(OLD)
if c != 1: print(f"ERROR fix 3 (drawCityDecor): {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD, NEW)
print("OK fix 3: drawCityDecor TW 64→48")

# ── FIX 4: drawTerrain ───────────────────────────────────────────────────────
OLD = "function drawTerrain(ctx, cx, cy, W, H) {\n  const TW=64, TH=32;"
NEW = "function drawTerrain(ctx, cx, cy, W, H) {\n  const TW=48, TH=24;"
c = src.count(OLD)
if c != 1: print(f"ERROR fix 4 (drawTerrain): {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD, NEW)
print("OK fix 4: drawTerrain TW 64→48")

# ── FIX 5: getLayout (comentario + declaración) ──────────────────────────────
OLD = "  // iso(dc, dr): misma proyección que drawTerrain (TW=64, TH=32)\n  // dc neg = izquierda/AlalaiA, dc pos = derecha/KarlakÁ\n  // dr neg = fondo, dr pos = frente\n  // Límite conservador: |dc|+|dr| <= 3 para edificios grandes, <= 4 para pequeños\n  const TW = 64, TH = 32;"
NEW = "  // iso(dc, dr): misma proyección que drawTerrain (TW=48, TH=24)\n  // dc neg = izquierda/AlalaiA, dc pos = derecha/KarlakÁ\n  // dr neg = fondo, dr pos = frente\n  // Límite conservador: |dc|+|dr| <= 3 para edificios grandes, <= 4 para pequeños\n  const TW = 48, TH = 24;"
c = src.count(OLD)
if c != 1: print(f"ERROR fix 5 (getLayout): {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD, NEW)
print("OK fix 5: getLayout TW 64→48")

# ── FIX 6: Muralla rx/ry ─────────────────────────────────────────────────────
OLD = "  const scale = 1 + lvl*0.004;\n  const rx = 135*scale, ry = 76*scale;"
NEW = "  const scale = 1 + lvl*0.004;\n  const rx = 100*scale, ry = 57*scale;"
c = src.count(OLD)
if c != 1: print(f"ERROR fix 6 (muralla): {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD, NEW)
print("OK fix 6: muralla rx 135→100, ry 76→57")

# ── FIX 7: drawPath lineWidth ────────────────────────────────────────────────
OLD = "  ctx.strokeStyle='rgba(80,60,40,0.4)';\n  ctx.lineWidth=8;"
NEW = "  ctx.strokeStyle='rgba(80,60,40,0.4)';\n  ctx.lineWidth=5;"
c = src.count(OLD)
if c != 1: print(f"ERROR fix 7 (drawPath): {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD, NEW)
print("OK fix 7: caminos lineWidth 8→5")

# ── Guardar ──────────────────────────────────────────────────────────────────
TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO — city.js actualizado.")
print()
print("Para verificar:")
print("  Recarga con Ctrl+Shift+R en http://127.0.0.1:8000/game")
print("  Los edificios deben verse notablemente más grandes.")
print("  El C.Ciudad debe ser el edificio más imponente.")
print("  Reporta captura o si hay errores en F12 > Console.")
