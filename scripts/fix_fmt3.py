from pathlib import Path

path = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = path.read_text(encoding="utf-8")

OLD = """  const tiers = [
    [1e33,'D'],[1e30,'N'],[1e27,'O'],[1e24,'Sp'],
    [1e21,'Sx'],[1e18,'Qi'],[1e15,'Q'],
    [1e12,'T'],[1e9,'B'],[1e6,'M'],[1e3,'K']
  ];
  for (const [d, sfx] of tiers) {
    if (abs >= d) {
      const v = abs/d;
      return s + (v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(1) : v.toFixed(2)) + sfx;
    }
  }
  return s + Math.round(abs).toLocaleString('es');"""

NEW = """  const tiers = [
    [1e48,'Qd'],[1e45,'Td'],[1e42,'Dd'],[1e39,'Nd'],
    [1e36,'Ud'],[1e33,'Dc'],[1e30,'No'],[1e27,'Oc'],
    [1e24,'Sp'],[1e21,'Sx'],[1e18,'Qi'],[1e15,'Q'],
    [1e12,'T'],[1e9,'B'],[1e6,'M'],[1e3,'K']
  ];
  for (const [d, sfx] of tiers) {
    if (abs >= d) {
      const v = abs/d;
      return s + (v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(1) : v.toFixed(2)) + sfx;
    }
  }
  if (abs >= 1e51) {
    const e = Math.floor(Math.log10(abs));
    return s + (abs / Math.pow(10, e)).toFixed(1) + 'e' + e;
  }
  return s + Math.round(abs).toLocaleString('es');"""

c = src.count(OLD)
if c != 1:
    print(f"ERROR: {c} veces"); exit(1)
src = src.replace(OLD, NEW)
path.write_text(src, encoding="utf-8")
print("OK — tiers extendidos hasta 1e51")
print("✅ Recarga el navegador.")
