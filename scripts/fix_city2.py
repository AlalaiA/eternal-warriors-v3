from pathlib import Path

path = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = path.read_text(encoding="utf-8")

OLD = """  drawCity(c);
}"""

NEW = """  // Esperar a que el canvas tenga dimensiones reales
  const canvas = document.getElementById('city-canvas');
  if (!canvas) return;
  const observer = new ResizeObserver(() => {
    drawCity(c);
  });
  observer.observe(canvas.parentElement);
  // También dibujar inmediatamente si ya tiene dimensiones
  if (canvas.parentElement.clientWidth > 0) drawCity(c);
}"""

OLD2 = """function drawCity(c) {
  const canvas = document.getElementById('city-canvas');
  if (!canvas) return;
  const wrap = canvas.parentElement;
  const W = wrap.clientWidth;
  const H = wrap.clientHeight;
  canvas.width  = W;
  canvas.height = H;
  canvas.style.width  = W + 'px';
  canvas.style.height = H + 'px';"""

NEW2 = """function drawCity(c) {
  const canvas = document.getElementById('city-canvas');
  if (!canvas) return;
  const wrap = canvas.parentElement;
  const W = wrap.clientWidth  || wrap.offsetWidth;
  const H = wrap.clientHeight || wrap.offsetHeight;
  if (W < 10 || H < 10) return;
  canvas.width  = W;
  canvas.height = H;
  canvas.style.width  = W + 'px';
  canvas.style.height = H + 'px';"""

for old, new, name in [(OLD, NEW, 'drawCity call'), (OLD2, NEW2, 'drawCity fn')]:
    c = src.count(old)
    if c != 1:
        print(f"ERROR {name}: {c} veces"); exit(1)
    src = src.replace(old, new)
    print(f"OK {name}")

path.write_text(src, encoding="utf-8")
print("\n✅ Listo. Recarga el navegador.")
