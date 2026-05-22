"""
fix_drawbuilding.py
Eternal Warriors v3.0 — Cierra la llave huérfana en drawBuilding

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_drawbuilding.py
"""

from pathlib import Path
import sys

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = TARGET.read_text(encoding="utf-8")

OLD = """\
  const h = H[b.type] || 90;
  drawSprite(ctx, b.type, b.x, b.y, h);
  {"""

NEW = """\
  const h = H[b.type] || 90;
  drawSprite(ctx, b.type, b.x, b.y, h);
  drawLabel(ctx, b.x, b.y, b.label, b.lvl, b.type);
}"""

c = src.count(OLD)
if c != 1:
    print(f"ERROR: ancla encontrada {c} veces. Abortando.")
    sys.exit(1)

src = src.replace(OLD, NEW)

# Verificar que no hay código muerto del switch anterior
# Buscar y eliminar el bloque switch huérfano si quedó
import re
# El switch huérfano empieza con ctx.save(); switch y termina con ctx.restore();
pattern = r"\n  ctx\.save\(\);\n  switch \(b\.type\) \{.*?ctx\.restore\(\);\n\}"
match = re.search(pattern, src, re.DOTALL)
if match:
    src = src[:match.start()] + src[match.end():]
    print("OK: bloque switch huérfano eliminado")

TARGET.write_text(src, encoding="utf-8")
print("OK: drawBuilding corregido")
print()
print("Para verificar:")
print("  Ctrl+C → run.bat → Ctrl+Shift+R en http://127.0.0.1:8000/game")
