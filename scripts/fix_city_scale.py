"""
fix_city_scale.py
Eternal Warriors v3.0 — Escala visual definitiva

DIAGNÓSTICO REAL:
  Con sc=0.42 y w=72*sc=30px, un edificio de 30px de ancho no puede mostrar
  ventanas, arcos ni detalles — todo se ve como un bloque.
  La imagen guía muestra edificios que ocupan ~80-120px.
  
  Solución:
  1. sc base: 0.42 → 0.75. C.Ciudad con scMax=28 llega a sc=1.11 (≈80px de ancho).
  2. cy: H*0.56 → H*0.52 (más espacio vertical para edificios altos).
  3. TW/TH del grid de terreno: 64/32 → 48/24 (celdas más pequeñas = más terreno visible).
     Esto comprime el terreno y deja espacio para edificios más grandes.
  4. Muralla: rx/ry escalados acorde al nuevo TW.

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_city_scale.py
"""

from pathlib import Path
import sys

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
if not TARGET.exists():
    print(f"ERROR: No se encontró:\n  {TARGET}")
    sys.exit(1)

src = TARGET.read_text(encoding="utf-8")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 1 — cy: más espacio arriba para torres altas
# ══════════════════════════════════════════════════════════════════════════════
OLD_CY = "  const cx = W/2, cy = H*0.56;"
NEW_CY = "  const cx = W/2, cy = H*0.60;"
c = src.count(OLD_CY)
if c != 1: print(f"ERROR fix 1: {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD_CY, NEW_CY)
print("OK fix 1: cy H*0.56 → H*0.60")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 2 — sc base: 0.42 → 0.72
# ══════════════════════════════════════════════════════════════════════════════
OLD_SC = "  const sc = 0.42 + Math.min(lvl,scMax)*0.013;"
NEW_SC = "  const sc = 0.72 + Math.min(lvl,scMax)*0.014;"
c = src.count(OLD_SC)
if c != 1: print(f"ERROR fix 2: {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD_SC, NEW_SC)
print("OK fix 2: sc base 0.42 → 0.72")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 3 — Terreno: TW 64→48, TH 32→24 (celdas más pequeñas, rombo más compacto)
# ══════════════════════════════════════════════════════════════════════════════
OLD_TERRAIN = "  const TW=64, TH=32;"
NEW_TERRAIN = "  const TW=48, TH=24;"
c = src.count(OLD_TERRAIN)
if c != 1: print(f"ERROR fix 3: {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD_TERRAIN, NEW_TERRAIN)
print("OK fix 3: terreno TW 64→48, TH 32→24")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 4 — iso() en getLayout: TW 64→48, TH 32→24
# ══════════════════════════════════════════════════════════════════════════════
OLD_ISO = "  const TW = 64, TH = 32;\n  const iso = (dc, dr) => ({"
NEW_ISO = "  const TW = 48, TH = 24;\n  const iso = (dc, dr) => ({"
c = src.count(OLD_ISO)
if c != 1: print(f"ERROR fix 4: {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD_ISO, NEW_ISO)
print("OK fix 4: iso() en getLayout TW 64→48, TH 32→24")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 5 — iso() en drawCityDecor: TW 64→48, TH 32→24
# ══════════════════════════════════════════════════════════════════════════════
OLD_DECOR_ISO = "  const TW=64, TH=32;\n  // iso helper local\n  const iso=(dc,dr)=>({x:cx+(dc-dr)*TW/2, y:cy+(dc+dr)*TH/2});"
NEW_DECOR_ISO = "  const TW=48, TH=24;\n  // iso helper local\n  const iso=(dc,dr)=>({x:cx+(dc-dr)*TW/2, y:cy+(dc+dr)*TH/2});"
c = src.count(OLD_DECOR_ISO)
if c != 1: print(f"ERROR fix 5: {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD_DECOR_ISO, NEW_DECOR_ISO)
print("OK fix 5: iso() en drawCityDecor TW 64→48, TH 32→24")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 6 — Muralla: rx 135→100 acorde al nuevo TW
# ══════════════════════════════════════════════════════════════════════════════
OLD_WALL = "  const scale = 1 + lvl*0.004;\n  const rx = 135*scale, ry = 76*scale;"
NEW_WALL = "  const scale = 1 + lvl*0.004;\n  const rx = 100*scale, ry = 57*scale;"
c = src.count(OLD_WALL)
if c != 1: print(f"ERROR fix 6: {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD_WALL, NEW_WALL)
print("OK fix 6: muralla rx 135→100, ry 76→57")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 7 — drawPath: caminos acorde al nuevo TW/TH
# ══════════════════════════════════════════════════════════════════════════════
OLD_PATH = "function drawPath(ctx, cx, cy, TW, TH, cols, rows) {\n  ctx.strokeStyle='rgba(80,60,40,0.4)';\n  ctx.lineWidth=8;"
NEW_PATH = "function drawPath(ctx, cx, cy, TW, TH, cols, rows) {\n  ctx.strokeStyle='rgba(80,60,40,0.4)';\n  ctx.lineWidth=6;"
c = src.count(OLD_PATH)
if c != 1: print(f"ERROR fix 7: {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD_PATH, NEW_PATH)
print("OK fix 7: caminos lineWidth 8→6")

# ══════════════════════════════════════════════════════════════════════════════
# Guardar
# ══════════════════════════════════════════════════════════════════════════════
TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO — city.js actualizado.")
print()
print("Para verificar:")
print("  Recarga con Ctrl+Shift+R en http://127.0.0.1:8000/game")
print("  Los edificios deben verse mucho más grandes y con detalles visibles.")
print("  El C.Ciudad debe ser claramente el más imponente.")
print("  Si algún edificio se sale del rombo, reporta cuál.")
