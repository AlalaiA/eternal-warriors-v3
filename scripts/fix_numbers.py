from pathlib import Path

path = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = path.read_text(encoding="utf-8")

OLD = """function fmt(val) {
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

NEW = """function fmt(val) {
  if (val === undefined || val === null) return '—';
  const n = Number(val);
  if (isNaN(n) || n === 0) return n === 0 ? '0' : '—';
  const abs = Math.abs(n);
  const sign = n < 0 ? '-' : '';
  const TIERS = [
    [1e15, 'Q'],   // Cuatrillón
    [1e12, 'T'],   // Billón
    [1e9,  'B'],   // Mil millones
    [1e6,  'M'],   // Millón
    [1e3,  'K'],   // Mil
  ];
  for (const [div, suffix] of TIERS) {
    if (abs >= div) {
      const v = abs / div;
      const str = v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(1) : v.toFixed(2);
      return sign + str + suffix;
    }
  }
  // Números muy grandes: notación compacta
  if (abs >= 1e18) {
    const exp = Math.floor(Math.log10(abs));
    const man = (abs / Math.pow(10, exp)).toFixed(1);
    return sign + man + 'e' + exp;
  }
  return sign + Math.round(abs).toLocaleString('es');
}"""

c = src.count(OLD)
if c != 1:
    print(f"ERROR: ancla fmt encontrada {c} veces"); exit(1)
src = src.replace(OLD, NEW)
path.write_text(src, encoding="utf-8")
print("OK city.js — fmt actualizado")

# Ampliar columna izquierda y derecha
css_path = Path(r"E:\0000ew V2Claude\frontend\css\city.css")
css = css_path.read_text(encoding="utf-8")

OLD2 = "  grid-template-columns: 200px 1fr 200px;"
NEW2 = "  grid-template-columns: 240px 1fr 240px;"

c2 = css.count(OLD2)
if c2 != 1:
    print(f"ERROR: ancla css encontrada {c2} veces"); exit(1)
css = css.replace(OLD2, NEW2)
css_path.write_text(css, encoding="utf-8")
print("OK city.css — columnas ampliadas a 240px")

print("\n✅ Listo. Recarga el navegador.")
