from pathlib import Path

path = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = path.read_text(encoding="utf-8")

OLD = "  requestAnimationFrame(() => drawCity(c));"
NEW = """  // Esperar layout completo antes de dibujar
  setTimeout(() => drawCity(c), 100);
  window.addEventListener('resize', () => drawCity(c));"""

c = src.count(OLD)
if c != 1:
    print(f"ERROR: {c} veces"); exit(1)
src = src.replace(OLD, NEW)
path.write_text(src, encoding="utf-8")
print("OK — delay aumentado a 100ms + resize handler")
print("✅ Recarga el navegador.")
