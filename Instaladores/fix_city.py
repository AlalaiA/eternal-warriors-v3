from pathlib import Path

BASE = Path(r"E:\0000ew V2Claude\frontend")

# ── Arreglar fmt() en city.js ─────────────────────────────────────────────
path = BASE / "js/screens/city.js"
src = path.read_text(encoding="utf-8")

OLD = """function fmt(val) {
  if (val === undefined || val === null) return '—';
  const n = Number(val);
  if (n >= 1e12) return (n/1e12).toFixed(2) + 'B';
  if (n >= 1e9)  return (n/1e9).toFixed(2)  + 'MM';
  if (n >= 1e6)  return (n/1e6).toFixed(2)  + 'M';
  if (n >= 1e3)  return (n/1e3).toFixed(1)  + 'K';
  return n.toLocaleString('es');
}"""

NEW = """function fmt(val) {
  if (val === undefined || val === null) return '—';
  const n = Number(val);
  if (isNaN(n)) return '—';
  if (n >= 1e33) return (n/1e33).toFixed(1) + 'D';
  if (n >= 1e30) return (n/1e30).toFixed(1) + 'N';
  if (n >= 1e27) return (n/1e27).toFixed(1) + 'O';
  if (n >= 1e24) return (n/1e24).toFixed(1) + 'S';
  if (n >= 1e21) return (n/1e21).toFixed(1) + 'Z';
  if (n >= 1e18) return (n/1e18).toFixed(1) + 'E';
  if (n >= 1e15) return (n/1e15).toFixed(1) + 'P';
  if (n >= 1e12) return (n/1e12).toFixed(1) + 'T';
  if (n >= 1e9)  return (n/1e9).toFixed(1)  + 'B';
  if (n >= 1e6)  return (n/1e6).toFixed(1)  + 'M';
  if (n >= 1e3)  return (n/1e3).toFixed(1)  + 'K';
  return n.toLocaleString('es');
}"""

c = src.count(OLD)
if c != 1:
    print(f"ERROR fmt: ancla encontrada {c} veces"); exit(1)
src = src.replace(OLD, NEW)

# ── Arreglar drawCity: proporciones correctas ─────────────────────────────
OLD2 = """  const W = canvas.parentElement.clientWidth;
  const H = canvas.parentElement.clientHeight - 48;
  canvas.width  = W;
  canvas.height = H;"""

NEW2 = """  const wrap = canvas.parentElement;
  const W = wrap.clientWidth;
  const H = wrap.clientHeight;
  canvas.width  = W;
  canvas.height = H;
  canvas.style.width  = W + 'px';
  canvas.style.height = H + 'px';"""

c2 = src.count(OLD2)
if c2 != 1:
    print(f"ERROR canvas: ancla encontrada {c2} veces"); exit(1)
src = src.replace(OLD2, NEW2)

path.write_text(src, encoding="utf-8")
print("OK js/screens/city.js — fmt y canvas corregidos")

# ── Arreglar city.css: canvas ocupa todo el wrap ──────────────────────────
css_path = BASE / "css/city.css"
css = css_path.read_text(encoding="utf-8")

OLD3 = """#city-canvas {
  display: block;
  width: 100%;
  height: 100%;
}"""

NEW3 = """#city-canvas {
  display: block;
  position: absolute;
  top: 0; left: 0;
}"""

c3 = css.count(OLD3)
if c3 != 1:
    print(f"ERROR css: ancla encontrada {c3} veces"); exit(1)
css = css.replace(OLD3, NEW3)
css_path.write_text(css, encoding="utf-8")
print("OK css/city.css — canvas absolute")

print("\n✅ Listo. Recarga el navegador.")
