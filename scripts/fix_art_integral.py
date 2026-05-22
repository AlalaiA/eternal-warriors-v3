"""
fix_art_integral.py
Eternal Warriors v3.0 — Fix artístico integral

Cambios:
  1. drawLabel: fuente 9px → 7px, altura 13→10, padding reducido
  2. drawWall: caras con volumen real (NW más clara, SE/SW más oscura)
  3. drawTerrain: terreno con calidez — lado izq verde/marrón, lado der rojo/lava
  4. drawFloor: plazoleta con grietas de lava (lado der) y musgo/luz (lado izq)
  5. renderFrame: añadir drawDuality() — niebla AlalaiA izq + brasa KarlakÁ der
  6. drawMist: niebla más cálida

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_art_integral.py
"""

from pathlib import Path
import sys

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
if not TARGET.exists():
    print(f"ERROR: No se encontró:\n  {TARGET}")
    sys.exit(1)

src = TARGET.read_text(encoding="utf-8")
ok = []

# ══════════════════════════════════════════════════════════════════════════════
# FIX 1 — Etiquetas más pequeñas
# ══════════════════════════════════════════════════════════════════════════════
OLD = """function drawLabel(ctx, x, y, text, lvl, type) {
  ctx.save();
  ctx.font = '600 9px Rajdhani, sans-serif';
  const label = lvl > 0 ? `${text} ${lvl}` : text;
  const tw = ctx.measureText(label).width + 10;
  ctx.fillStyle = 'rgba(4,4,12,0.85)';
  ctx.strokeStyle = lvl > 0 ? 'rgba(180,145,50,0.7)' : 'rgba(50,50,80,0.6)';
  ctx.lineWidth = 0.7;
  rr(ctx, x - tw / 2, y + 4, tw, 13, 3); ctx.fill(); ctx.stroke();
  ctx.fillStyle = lvl > 0 ? '#d4a840' : '#5a5a78';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(label, x, y + 11);
  ctx.restore();
}"""
NEW = """function drawLabel(ctx, x, y, text, lvl, type) {
  ctx.save();
  ctx.font = '500 7px Rajdhani, sans-serif';
  const label = lvl > 0 ? `${text} ${lvl}` : text;
  const tw = ctx.measureText(label).width + 7;
  ctx.fillStyle = 'rgba(3,3,10,0.88)';
  ctx.strokeStyle = lvl > 0 ? 'rgba(160,128,44,0.65)' : 'rgba(40,40,65,0.55)';
  ctx.lineWidth = 0.6;
  rr(ctx, x - tw / 2, y + 3, tw, 10, 2); ctx.fill(); ctx.stroke();
  ctx.fillStyle = lvl > 0 ? '#c89830' : '#505070';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(label, x, y + 8);
  ctx.restore();
}"""
c = src.count(OLD)
if c != 1: print(f"ERROR fix 1: {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD, NEW); ok.append("fix 1: etiquetas 7px")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 2 — drawWall: volumen real con caras diferenciadas
# ══════════════════════════════════════════════════════════════════════════════
OLD = """  // Cara inferior de la muralla (sombra/volumen)
  ctx.beginPath();
  pts.forEach(([px, py], i) => i === 0 ? ctx.moveTo(px, py + wallH) : ctx.lineTo(px, py + wallH));
  ctx.closePath();
  ctx.fillStyle = 'rgba(0,0,0,0.25)'; ctx.fill();

  // Cara frontal SW (izquierda-frente) — más oscura
  ctx.beginPath();
  ctx.moveTo(S[0], S[1]); ctx.lineTo(W[0], W[1]);
  ctx.lineTo(W[0], W[1] + wallH); ctx.lineTo(S[0], S[1] + wallH);
  ctx.closePath();
  ctx.fillStyle = wallD; ctx.fill();

  // Cara frontal SE (derecha-frente) — más oscura
  ctx.beginPath();
  ctx.moveTo(S[0], S[1]); ctx.lineTo(E[0], E[1]);
  ctx.lineTo(E[0], E[1] + wallH); ctx.lineTo(S[0], S[1] + wallH);
  ctx.closePath();
  ctx.fillStyle = wallD; ctx.fill();

  // Cara superior NW — más clara
  ctx.beginPath();
  ctx.moveTo(N[0], N[1]); ctx.lineTo(W[0], W[1]); ctx.lineTo(S[0], S[1]); ctx.lineTo(cx, cy);
  // Simplificado: solo el borde top
  ctx.restore && ctx.restore();

  // Línea superior del muro (corona)
  ctx.beginPath();
  pts.forEach(([px, py], i) => i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py));
  ctx.closePath();
  ctx.strokeStyle = wallC; ctx.lineWidth = wallH * 0.55; ctx.stroke();

  // Borde dorado fino en la corona
  ctx.strokeStyle = 'rgba(180,150,60,0.3)'; ctx.lineWidth = 1;
  ctx.beginPath();
  pts.forEach(([px, py], i) => i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py));
  ctx.closePath(); ctx.stroke();"""

NEW = """  // ── Caras de la muralla con volumen isométrico real ───────────────────────
  // Cara SW visible (frente-izquierda): luz AlalaiA, tono frío
  ctx.beginPath();
  ctx.moveTo(W[0], W[1]); ctx.lineTo(S[0], S[1]);
  ctx.lineTo(S[0], S[1] + wallH); ctx.lineTo(W[0], W[1] + wallH);
  ctx.closePath();
  ctx.fillStyle = `rgb(${42+lvl},${48+lvl},${62+lvl})`; ctx.fill();

  // Cara SE visible (frente-derecha): influencia KarlakÁ, tono más cálido
  ctx.beginPath();
  ctx.moveTo(E[0], E[1]); ctx.lineTo(S[0], S[1]);
  ctx.lineTo(S[0], S[1] + wallH); ctx.lineTo(E[0], E[1] + wallH);
  ctx.closePath();
  ctx.fillStyle = `rgb(${48+lvl},${44+lvl},${58+lvl})`; ctx.fill();

  // Corona superior — la cara más clara (iluminada desde arriba)
  ctx.beginPath();
  pts.forEach(([px, py], i) => i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py));
  ctx.closePath();
  ctx.strokeStyle = `rgb(${58+lvl},${65+lvl},${82+lvl})`; ctx.lineWidth = wallH * 0.6; ctx.stroke();

  // Filo superior dorado (ornamento)
  ctx.strokeStyle = 'rgba(190,158,65,0.35)'; ctx.lineWidth = 1.2;
  ctx.beginPath();
  pts.forEach(([px, py], i) => i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py));
  ctx.closePath(); ctx.stroke();

  // Contorno exterior oscuro para definición
  ctx.strokeStyle = 'rgba(0,0,0,0.5)'; ctx.lineWidth = 0.8;
  ctx.beginPath();
  ctx.moveTo(W[0], W[1] + wallH); ctx.lineTo(S[0], S[1] + wallH); ctx.lineTo(E[0], E[1] + wallH);
  ctx.stroke();"""

c = src.count(OLD)
if c != 1: print(f"ERROR fix 2: {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD, NEW); ok.append("fix 2: muralla con volumen")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 3 — drawTerrain: calidez por zona (izq=verde/musgo, der=rojo/tierra)
# ══════════════════════════════════════════════════════════════════════════════
OLD = """      const even = (col + r) % 2 === 0;
      ctx.fillStyle = even ? '#1c2418' : '#182014';
      ctx.beginPath();
      ctx.moveTo(px,           py - th * 0.25);
      ctx.lineTo(px + tw * 0.5, py);
      ctx.lineTo(px,           py + th * 0.25);
      ctx.lineTo(px - tw * 0.5, py);
      ctx.closePath(); ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,0.4)'; ctx.lineWidth = 0.5; ctx.stroke();"""
NEW = """      const even = (col + r) % 2 === 0;
      // Dualidad: izq (u<0) = verde/AlalaiA, der (u>0) = rojo/KarlakÁ
      const blend = Math.max(0, Math.min(1, u / rx + 0.5));
      const gr = Math.round(24 - blend * 8);
      const rr2 = Math.round(18 + blend * 14);
      const gb = Math.round(20 - blend * 6);
      ctx.fillStyle = even
        ? `rgb(${rr2},${gr+4},${gb})`
        : `rgb(${rr2-4},${gr},${gb-2})`;
      ctx.beginPath();
      ctx.moveTo(px,            py - th * 0.25);
      ctx.lineTo(px + tw * 0.5, py);
      ctx.lineTo(px,            py + th * 0.25);
      ctx.lineTo(px - tw * 0.5, py);
      ctx.closePath(); ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,0.38)'; ctx.lineWidth = 0.5; ctx.stroke();"""
c = src.count(OLD)
if c != 1: print(f"ERROR fix 3: {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD, NEW); ok.append("fix 3: terreno cálido por zona")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 4 — drawFloor: plazoleta con grietas de lava der y musgo izq
# ══════════════════════════════════════════════════════════════════════════════
OLD = """      const even = (col + r) % 2 === 0;
      ctx.fillStyle = even ? '#1a1a24' : '#161620';
      ctx.beginPath();
      ctx.moveTo(px,            py - th * 0.25);
      ctx.lineTo(px + tw * 0.5, py);
      ctx.lineTo(px,            py + th * 0.25);
      ctx.lineTo(px - tw * 0.5, py);
      ctx.closePath(); ctx.fill();
      ctx.strokeStyle = 'rgba(180,150,60,0.12)'; ctx.lineWidth = 0.5; ctx.stroke();"""
NEW = """      const even = (col + r) % 2 === 0;
      const blend2 = Math.max(0, Math.min(1, u / irx + 0.5));
      // Izq: piedra con tono azul/musgo (AlalaiA). Der: piedra con tono rojizo (KarlakÁ)
      const baseR = even ? Math.round(22 + blend2 * 10) : Math.round(18 + blend2 * 8);
      const baseG = even ? Math.round(22 - blend2 * 4)  : Math.round(18 - blend2 * 3);
      const baseB = even ? Math.round(30 - blend2 * 10) : Math.round(26 - blend2 * 8);
      ctx.fillStyle = `rgb(${baseR},${baseG},${baseB})`;
      ctx.beginPath();
      ctx.moveTo(px,            py - th * 0.25);
      ctx.lineTo(px + tw * 0.5, py);
      ctx.lineTo(px,            py + th * 0.25);
      ctx.lineTo(px - tw * 0.5, py);
      ctx.closePath(); ctx.fill();
      // Grieta de lava en lado derecho
      if (blend2 > 0.65 && (col * 3 + r * 7) % 11 === 0) {
        const la = 0.08 + 0.06 * Math.sin(tick * 0.04 + col + r);
        ctx.strokeStyle = `rgba(220,80,20,${la})`; ctx.lineWidth = 0.8;
        ctx.beginPath(); ctx.moveTo(px - tw*0.2, py - th*0.1); ctx.lineTo(px + tw*0.2, py + th*0.1); ctx.stroke();
      }
      // Musgo/luz en lado izquierdo
      if (blend2 < 0.35 && (col * 5 + r * 3) % 13 === 0) {
        ctx.strokeStyle = 'rgba(60,160,120,0.12)'; ctx.lineWidth = 0.6;
        ctx.beginPath(); ctx.moveTo(px - tw*0.15, py); ctx.lineTo(px + tw*0.15, py); ctx.stroke();
      }
      ctx.strokeStyle = 'rgba(160,130,50,0.10)'; ctx.lineWidth = 0.5; ctx.stroke();"""
c = src.count(OLD)
if c != 1: print(f"ERROR fix 4: {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD, NEW); ok.append("fix 4: plazoleta con lava/musgo por zona")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 5 — renderFrame: añadir drawDuality() después de drawFloor
# ══════════════════════════════════════════════════════════════════════════════
OLD = """  // Edificios — ordenados por Y (painter's algorithm)
  const layout = getLayout(c, cx, cy, rx, ry);"""
NEW = """  // Dualidad AlalaiA / KarlakÁ — niebla y brasas
  drawDuality(ctx, cx, cy, rx, ry);

  // Edificios — ordenados por Y (painter's algorithm)
  const layout = getLayout(c, cx, cy, rx, ry);"""
c = src.count(OLD)
if c != 1: print(f"ERROR fix 5: {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD, NEW); ok.append("fix 5: drawDuality() en renderFrame")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 6 — Insertar drawDuality() antes de drawStars
# ══════════════════════════════════════════════════════════════════════════════
DUALITY_FUNC = """\
// ─── DUALIDAD ALALAIA / KARLAKÃ ──────────────────────────────────────────────
function drawDuality(ctx, cx, cy, rx, ry) {
  // Lado AlalaiA (izquierda): niebla etérea azul-blanca
  const aG = ctx.createRadialGradient(cx - rx*0.45, cy - ry*0.15, 5, cx - rx*0.45, cy - ry*0.15, rx*0.55);
  aG.addColorStop(0, `rgba(80,140,220,${0.06+0.03*Math.sin(tick*0.03)})`);
  aG.addColorStop(0.5, `rgba(60,100,180,${0.03+0.02*Math.sin(tick*0.025)})`);
  aG.addColorStop(1, 'rgba(40,70,140,0)');
  ctx.fillStyle = aG; ctx.fillRect(0, 0, cx, cy + ry);

  // Partículas de luz AlalaiA
  for (let i = 0; i < 8; i++) {
    const t = (tick * 0.012 + i * 0.78) % 1;
    const px = cx - rx*0.7 + Math.sin(i*1.4)*rx*0.35;
    const py = (cy + ry*0.4) - t * ry * 1.2;
    const alpha = t < 0.2 ? t*5*0.3 : t > 0.8 ? (1-t)*5*0.3 : 0.30;
    ctx.fillStyle = `rgba(160,210,255,${alpha})`;
    ctx.beginPath(); ctx.arc(px, py, 1.5+Math.sin(i)*0.8, 0, Math.PI*2); ctx.fill();
  }

  // Lado KarlakÁ (derecha): brasa naranja-roja
  const kG = ctx.createRadialGradient(cx + rx*0.45, cy - ry*0.10, 5, cx + rx*0.45, cy - ry*0.10, rx*0.55);
  kG.addColorStop(0, `rgba(180,60,20,${0.07+0.04*Math.sin(tick*0.04)})`);
  kG.addColorStop(0.5, `rgba(140,40,10,${0.04+0.02*Math.sin(tick*0.035)})`);
  kG.addColorStop(1, 'rgba(100,20,5,0)');
  ctx.fillStyle = kG; ctx.fillRect(cx, 0, cx, cy + ry);

  // Brasas flotantes KarlakÁ
  for (let i = 0; i < 10; i++) {
    const t = (tick * 0.018 + i * 0.63) % 1;
    const px = cx + rx*0.18 + Math.sin(i*2.1)*rx*0.52;
    const py = (cy + ry*0.5) - t * ry * 1.4;
    const alpha = t < 0.15 ? t/0.15*0.5 : t > 0.75 ? (1-t)/0.25*0.5 : 0.5;
    const r2 = Math.round(220 + Math.sin(tick*0.1+i)*20);
    const g2 = Math.round(60 + Math.sin(tick*0.08+i)*20);
    ctx.fillStyle = `rgba(${r2},${g2},10,${alpha})`;
    ctx.beginPath(); ctx.arc(px, py, 1.2+Math.sin(i*1.3)*0.6, 0, Math.PI*2); ctx.fill();
  }

  // Grietas de lava animadas en el suelo derecho
  ctx.save();
  for (let i = 0; i < 5; i++) {
    const lx = cx + rx*0.12 + i*rx*0.12;
    const ly = cy + ry*0.15 + Math.sin(i*1.7)*ry*0.20;
    const la = 0.12 + 0.08*Math.sin(tick*0.06+i);
    const lg = ctx.createLinearGradient(lx, ly, lx + rx*0.08, ly + ry*0.04);
    lg.addColorStop(0, `rgba(255,80,0,0)`);
    lg.addColorStop(0.5, `rgba(255,100,10,${la})`);
    lg.addColorStop(1, `rgba(255,80,0,0)`);
    ctx.strokeStyle = lg; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(lx, ly); ctx.lineTo(lx + rx*0.08 + Math.sin(i)*4, ly + ry*0.04); ctx.stroke();
  }
  ctx.restore();
}

"""

OLD_STARS = "// ═══════════════════════════════════════════════════════════════════════════════\n// AMBIENTE"
c = src.count(OLD_STARS)
if c != 1: print(f"ERROR fix 6: ancla AMBIENTE encontrada {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD_STARS, DUALITY_FUNC + OLD_STARS)
ok.append("fix 6: drawDuality() insertada")

# ══════════════════════════════════════════════════════════════════════════════
# Guardar
# ══════════════════════════════════════════════════════════════════════════════
TARGET.write_text(src, encoding="utf-8")
print()
for msg in ok:
    print(f"OK — {msg}")
print()
print("HECHO — city.js actualizado.")
print()
print("Para verificar:")
print("  Ctrl+C → run.bat → Ctrl+Shift+R en http://127.0.0.1:8000/game")
print("  Izquierda: niebla azul/verde AlalaiA con partículas de luz")
print("  Derecha: brasas rojas KarlakÁ con grietas de lava en el suelo")
print("  Etiquetas más pequeñas y discretas")
print("  Muralla con caras visibles y volumen")
