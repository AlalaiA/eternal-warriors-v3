from pathlib import Path
path = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = path.read_text(encoding="utf-8")
OLD = "  const cx = W/2, cy = H*0.60;"
NEW = "  const cx = W/2, cy = H*0.65;"
c = src.count(OLD)
if c!=1: print(f"ERROR:{c}"); exit(1)
src = src.replace(OLD, NEW)
path.write_text(src, encoding="utf-8")
print("OK — cy=0.65. Recarga.")
