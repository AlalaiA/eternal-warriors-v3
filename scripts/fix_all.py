from pathlib import Path

path = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = path.read_text(encoding="utf-8")

# 1. cy más arriba
OLD1 = "  const cx = W/2, cy = H*0.70;"
NEW1 = "  const cx = W/2, cy = H*0.63;"
c1 = src.count(OLD1)
if c1!=1: print(f"ERROR cy:{c1}"); exit(1)
src = src.replace(OLD1, NEW1)
print("Fix 1: cy=0.63")

# 2. Etiquetas más pequeñas y compactas
OLD2 = """  ctx.font = 'bold 9px Rajdhani, sans-serif';
  const label = lvl > 0 ? `${text}  Nv.${lvl}` : text;
  const tw = ctx.measureText(label).width + 14;
  ctx.fillStyle='rgba(5,5,15,0.88)';
  ctx.strokeStyle = lvl > 0 ? 'rgba(180,150,60,0.7)' : 'rgba(50,50,70,0.5)';
  ctx.lineWidth=0.8;
  rr(ctx, x-tw/2, y-9, tw, 16, 3); ctx.fill(); ctx.stroke();
  ctx.fillStyle = lvl > 0 ? '#d4ae5c' : '#505065';
  ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText(label, x, y);"""

NEW2 = """  ctx.font = '7px Rajdhani, sans-serif';
  const label = lvl > 0 ? `${text} ${lvl}` : text;
  const tw = ctx.measureText(label).width + 8;
  ctx.fillStyle='rgba(5,5,15,0.82)';
  ctx.strokeStyle = lvl > 0 ? 'rgba(160,130,50,0.6)' : 'rgba(40,40,60,0.5)';
  ctx.lineWidth=0.6;
  rr(ctx, x-tw/2, y-7, tw, 12, 2); ctx.fill(); ctx.stroke();
  ctx.fillStyle = lvl > 0 ? '#c4a050' : '#484860';
  ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText(label, x, y-1);"""

c2 = src.count(OLD2)
if c2!=1: print(f"ERROR label:{c2}"); exit(1)
src = src.replace(OLD2, NEW2)
print("Fix 2: etiquetas compactas")

# 3. Reducir escala general de edificios
OLD3 = "  const scMax = b.type==='sanctuary' ? 25 : (b.type==='cityhall' ? 40 : 50);\n  const sc = 0.45 + Math.min(lvl,scMax)*0.015;"
NEW3 = "  const scMax = b.type==='sanctuary' ? 20 : (b.type==='cityhall' ? 35 : b.type==='watchtower' ? 30 : 40);\n  const sc = 0.38 + Math.min(lvl,scMax)*0.013;"
c3 = src.count(OLD3)
if c3!=1: print(f"ERROR sc:{c3}"); exit(1)
src = src.replace(OLD3, NEW3)
print("Fix 3: escala reducida")

path.write_text(src, encoding="utf-8")
print("✅ Recarga el navegador.")
