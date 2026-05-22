"""
fix_city_art2.py
Eternal Warriors v3.0 — Corrección: losas transparentes + escala edificios + caminos

PROBLEMA:
  1. Losas de la plazoleta tienen fill opaco (#1a1820) — tapan el terreno y los edificios
  2. sc base = 0.28 — edificios de nivel bajo son invisibles (3-4px)
  3. Caminos van de iso(-2,-2) a iso(2,2) — líneas demasiado largas y gruesas

FIXES:
  1. Losas: solo borde dorado semitransparente, sin fill opaco
  2. sc base: 0.28 → 0.42 (edificios siempre visibles)
  3. Caminos: de iso(-1,-1)/iso(1,1) y lineWidth reducido

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_city_art2.py
"""

from pathlib import Path
import sys

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
if not TARGET.exists():
    print(f"ERROR: No se encontró:\n  {TARGET}")
    sys.exit(1)

src = TARGET.read_text(encoding="utf-8")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 1 — Losas: quitar fill opaco, solo borde dorado
# ══════════════════════════════════════════════════════════════════════════════
OLD_LOSAS = """\
      // Losa de piedra oscura con borde dorado
      ctx.fillStyle=dc===0&&dr===0?'#1a1820':'#161418';
      ctx.beginPath();
      ctx.moveTo(x,y-TH/2); ctx.lineTo(x+TW/2,y);
      ctx.lineTo(x,y+TH/2); ctx.lineTo(x-TW/2,y);
      ctx.closePath(); ctx.fill();
      ctx.strokeStyle='rgba(180,150,60,0.25)'; ctx.lineWidth=0.8; ctx.stroke();"""

NEW_LOSAS = """\
      // Borde dorado sutil sobre el terreno existente (sin fill opaco)
      ctx.beginPath();
      ctx.moveTo(x,y-TH/2); ctx.lineTo(x+TW/2,y);
      ctx.lineTo(x,y+TH/2); ctx.lineTo(x-TW/2,y);
      ctx.closePath();
      ctx.strokeStyle= dc===0&&dr===0 ? 'rgba(200,170,60,0.35)' : 'rgba(160,130,50,0.18)';
      ctx.lineWidth=0.8; ctx.stroke();"""

c1 = src.count(OLD_LOSAS)
if c1 != 1:
    print(f"ERROR fix 1: ancla encontrada {c1} veces. Abortando.")
    sys.exit(1)
src = src.replace(OLD_LOSAS, NEW_LOSAS)
print("OK fix 1: losas sin fill opaco — solo borde dorado semitransparente")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 2 — sc base: 0.28 → 0.42
# ══════════════════════════════════════════════════════════════════════════════
OLD_SC = "  const sc = 0.28 + Math.min(lvl,scMax)*0.013;"
NEW_SC = "  const sc = 0.42 + Math.min(lvl,scMax)*0.013;"

c2 = src.count(OLD_SC)
if c2 != 1:
    print(f"ERROR fix 2: ancla encontrada {c2} veces. Abortando.")
    sys.exit(1)
src = src.replace(OLD_SC, NEW_SC)
print("OK fix 2: sc base 0.28 → 0.42 (edificios siempre visibles)")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 3 — Caminos: más cortos y más finos
# ══════════════════════════════════════════════════════════════════════════════
OLD_CAMINOS = """\
  ctx.save();
  ctx.strokeStyle='rgba(100,85,60,0.35)';
  ctx.lineWidth=5;
  // Camino NW-SE (de fondo-izquierda a frente-derecha)
  const nw=iso(-2,-2), se=iso(2,2);
  ctx.beginPath(); ctx.moveTo(nw.x,nw.y); ctx.lineTo(se.x,se.y); ctx.stroke();
  // Camino NE-SW (de fondo-derecha a frente-izquierda)
  const ne=iso(2,-2), sw=iso(-2,2);
  ctx.beginPath(); ctx.moveTo(ne.x,ne.y); ctx.lineTo(sw.x,sw.y); ctx.stroke();
  ctx.strokeStyle='rgba(130,110,75,0.15)';
  ctx.lineWidth=3;
  ctx.beginPath(); ctx.moveTo(nw.x,nw.y); ctx.lineTo(se.x,se.y); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(ne.x,ne.y); ctx.lineTo(sw.x,sw.y); ctx.stroke();
  ctx.restore();"""

NEW_CAMINOS = """\
  ctx.save();
  // Caminos entre plazoleta y edificios — cortos, sutiles
  ctx.strokeStyle='rgba(90,75,50,0.28)';
  ctx.lineWidth=3;
  const nw=iso(-1,-1), se=iso(1,1);
  const ne=iso(1,-1),  sw=iso(-1,1);
  const ct=iso(0,0);
  [[nw,ct],[se,ct],[ne,ct],[sw,ct]].forEach(([a,b])=>{
    ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
  });
  ctx.restore();"""

c3 = src.count(OLD_CAMINOS)
if c3 != 1:
    print(f"ERROR fix 3: ancla encontrada {c3} veces. Abortando.")
    sys.exit(1)
src = src.replace(OLD_CAMINOS, NEW_CAMINOS)
print("OK fix 3: caminos cortos desde esquinas de plazoleta al centro")

# ══════════════════════════════════════════════════════════════════════════════
# Guardar
# ══════════════════════════════════════════════════════════════════════════════
TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO — city.js actualizado.")
print()
print("Para verificar:")
print("  Recarga con Ctrl+Shift+R en http://127.0.0.1:8000/game")
print("  Los edificios deben ser visibles sobre el terreno verde.")
print("  La plazoleta central debe verse como borde dorado sutil, no caja negra.")
print("  Los caminos deben ser líneas finas entre el centro y las esquinas de la plaza.")
