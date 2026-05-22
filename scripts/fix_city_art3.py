"""
fix_city_art3.py
Eternal Warriors v3.0 — Fix: glow() en drawCityDecor usa rgba en lugar de rgb

ERROR: 'rgbaa(255,200,80,...)' — la función glow() agrega 'a' al string de color,
       pero ya se le estaba pasando 'rgba(...)' en lugar de 'rgb(...)'.

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_city_art3.py
"""

from pathlib import Path
import sys

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
if not TARGET.exists():
    print(f"ERROR: No se encontró:\n  {TARGET}")
    sys.exit(1)

src = TARGET.read_text(encoding="utf-8")

fixes = [
    # Fuente de maná
    (
        "glow(ctx,fx,fy-4,14,'rgb(120,60,220)');",
        "glow(ctx,fx,fy-4,14,'rgb(120,60,220)');"
    ),
    # Farolas — la línea usa template literal con rgba
    (
        "    glow(ctx,x+5,y-25,10,`rgba(255,200,80,${la})`);",
        "    glow(ctx,x+5,y-25,10,'rgb(255,200,80)');"
    ),
    # Arco de entrada
    (
        "  glow(ctx, gate.x, gate.y+2, 16, `rgba(80,130,255,${archGlow})`);",
        "  glow(ctx, gate.x, gate.y+2, 16, 'rgb(80,130,255)');"
    ),
]

for old, new in fixes:
    c = src.count(old)
    if c == 0:
        print(f"SKIP (no encontrada): {old[:60]}")
        continue
    if c > 1:
        print(f"ERROR: ancla encontrada {c} veces: {old[:60]}. Abortando.")
        sys.exit(1)
    src = src.replace(old, new)
    print(f"OK: {old[:60]}")

TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO — city.js actualizado.")
print()
print("Para verificar:")
print("  Recarga con Ctrl+Shift+R en http://127.0.0.1:8000/game")
print("  La consola del navegador (F12) no debe mostrar errores de color.")
print("  Los edificios deben verse sobre el terreno.")
