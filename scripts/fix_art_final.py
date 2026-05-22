"""
fix_art_final.py
Eternal Warriors v3.0 — Arte escénico: terreno mágico, muralla oscura, runas, dualidad

Cambios:
  1. drawTerrain: piedra oscura con brillo mágico sutil y más contraste
  2. drawFloor: suelo interior más rico — losas con venas de luz, runas grabadas
  3. drawWall: muralla oscura de piedra antigua, no gris claro
  4. drawDuality: más intensidad — niebla densa, brasas visibles, runas flotantes
  5. getLayout: un solo TEMPLO (quita TEMPLO_1 y TEMPLO_2 duplicados)
  6. cy: sube a H*0.62 para que C.Ciudad no se corte

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_art_final.py
"""

from pathlib import Path
import sys

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = TARGET.read_text(encoding="utf-8")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 1 — cy: bajar origen para que C.Ciudad no se corte
# ══════════════════════════════════════════════════════════════════════════════
OLD1 = "  const cx = W * 0.5, cy = H * 0.64;"
NEW1 = "  const cx = W * 0.5, cy = H * 0.62;"
c = src.count(OLD1)
if c != 1: print(f"ERROR fix 1: {c}x"); sys.exit(1)
src = src.replace(OLD1, NEW1)
print("OK fix 1: cy ajustado")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 2 — drawTerrain: piedra oscura con brillo mágico
# ══════════════════════════════════════════════════════════════════════════════
OLD2 = """\
      const even = (col + r) % 2 === 0;
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

NEW2 = """\
      const even = (col + r) % 2 === 0;
      // Dualidad visual: izq=azul/AlalaiA, der=rojo/KarlakÁ — piedra oscura ancestral
      const blend = Math.max(0, Math.min(1, u / rx + 0.5));
      // Base de piedra muy oscura con tinte de dualidad
      const baseR = even ? Math.round(12 + blend * 8)  : Math.round(10 + blend * 6);
      const baseG = even ? Math.round(14 - blend * 4)  : Math.round(11 - blend * 3);
      const baseB = even ? Math.round(18 - blend * 8)  : Math.round(15 - blend * 6);
      ctx.fillStyle = `rgb(${baseR},${baseG},${baseB})`;
      ctx.beginPath();
      ctx.moveTo(px,            py - th * 0.25);
      ctx.lineTo(px + tw * 0.5, py);
      ctx.lineTo(px,            py + th * 0.25);
      ctx.lineTo(px - tw * 0.5, py);
      ctx.closePath(); ctx.fill();
      // Venas de luz mágica en algunas celdas
      if ((col * 7 + r * 13) % 17 === 0) {
        const vAlpha = 0.06 + 0.04 * Math.sin(tick * 0.02 + col * 0.5 + r * 0.7);
        const vColor = blend < 0.5
          ? `rgba(60,120,220,${vAlpha})`   // AlalaiA: azul
          : `rgba(180,60,20,${vAlpha})`;   // KarlakÁ: rojo
        ctx.fillStyle = vColor;
        ctx.beginPath();
        ctx.moveTo(px, py - th * 0.25); ctx.lineTo(px + tw * 0.5, py);
        ctx.lineTo(px, py + th * 0.25); ctx.lineTo(px - tw * 0.5, py);
        ctx.closePath(); ctx.fill();
      }
      ctx.strokeStyle = 'rgba(0,0,0,0.55)'; ctx.lineWidth = 0.5; ctx.stroke();"""

c = src.count(OLD2)
if c != 1: print(f"ERROR fix 2: {c}x"); sys.exit(1)
src = src.replace(OLD2, NEW2)
print("OK fix 2: terreno oscuro mágico")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 3 — drawFloor: losas con runas y venas de luz
# ══════════════════════════════════════════════════════════════════════════════
OLD3 = """\
      const even = (col + r) % 2 === 0;
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

NEW3 = """\
      const even = (col + r) % 2 === 0;
      const blend2 = Math.max(0, Math.min(1, u / irx + 0.5));
      // Losas de piedra antigua — muy oscuras con ornamento dorado
      const base = even ? 16 : 13;
      ctx.fillStyle = `rgb(${base},${base},${Math.round(base*1.2)})`;
      ctx.beginPath();
      ctx.moveTo(px,            py - th * 0.25);
      ctx.lineTo(px + tw * 0.5, py);
      ctx.lineTo(px,            py + th * 0.25);
      ctx.lineTo(px - tw * 0.5, py);
      ctx.closePath(); ctx.fill();

      // Borde dorado sutil en todas las losas
      const borderAlpha = 0.12 + 0.05 * Math.sin(tick * 0.015 + col + r);
      ctx.strokeStyle = `rgba(180,145,40,${borderAlpha})`; ctx.lineWidth = 0.6; ctx.stroke();

      // Runas ancestrales grabadas — aparecen en celdas específicas
      if ((col * 11 + r * 7) % 19 === 0) {
        const runeAlpha = 0.18 + 0.10 * Math.sin(tick * 0.025 + col * 1.3 + r * 0.9);
        const runeColor = blend2 < 0.5
          ? `rgba(80,150,255,${runeAlpha})`   // AlalaiA: azul
          : `rgba(220,80,20,${runeAlpha})`;   // KarlakÁ: naranja
        ctx.fillStyle = runeColor;
        // Símbolo de runa simplificado (cruz de luz)
        ctx.fillRect(px - 1, py - th*0.18, 2, th*0.36);
        ctx.fillRect(px - tw*0.18, py - 1, tw*0.36, 2);
      }

      // Venas de lava (lado KarlakÁ)
      if (blend2 > 0.60 && (col * 3 + r * 7) % 11 === 0) {
        const la = 0.14 + 0.08 * Math.sin(tick * 0.04 + col + r);
        ctx.strokeStyle = `rgba(220,60,10,${la})`; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(px - tw*0.22, py - th*0.1); ctx.lineTo(px + tw*0.22, py + th*0.1); ctx.stroke();
        // Brillo de lava
        ctx.strokeStyle = `rgba(255,120,30,${la*0.5})`; ctx.lineWidth = 0.4;
        ctx.beginPath(); ctx.moveTo(px - tw*0.22, py - th*0.1); ctx.lineTo(px + tw*0.22, py + th*0.1); ctx.stroke();
      }

      // Musgo luminoso (lado AlalaiA)
      if (blend2 < 0.38 && (col * 5 + r * 3) % 13 === 0) {
        const ma = 0.12 + 0.07 * Math.sin(tick * 0.02 + col * 0.8 + r);
        ctx.strokeStyle = `rgba(40,180,140,${ma})`; ctx.lineWidth = 0.7;
        ctx.beginPath(); ctx.moveTo(px - tw*0.18, py); ctx.lineTo(px + tw*0.18, py); ctx.stroke();
      }"""

c = src.count(OLD3)
if c != 1: print(f"ERROR fix 3: {c}x"); sys.exit(1)
src = src.replace(OLD3, NEW3)
print("OK fix 3: suelo con runas y venas de lava")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 4 — drawWall: muralla oscura de piedra antigua (no gris claro)
# ══════════════════════════════════════════════════════════════════════════════
OLD4 = """\
  const wallH = 18 + lvl * 0.25;
  const wallC = `rgb(${52 + lvl}, ${58 + lvl}, ${74 + lvl})`;
  const wallD = `rgb(${35 + lvl}, ${40 + lvl}, ${52 + lvl})`;

  // ── Caras de la muralla con volumen isométrico real ───────────────────────
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
  ctx.stroke();

  // Almenas
  const merlons = Math.floor(24 + lvl * 0.4);
  ctx.fillStyle = wallC;
  for (let i = 0; i < merlons; i++) {
    const t = i / merlons;
    const seg = Math.floor(t * 4);
    const f = (t * 4) % 1;
    const [ax, ay] = pts[seg], [bx, by] = pts[(seg + 1) % 4];
    const mx = ax + (bx - ax) * f;
    const my = ay + (by - ay) * f;
    ctx.fillRect(mx - 2.5, my - wallH * 0.35 - 6, 5, 7);
  }"""

NEW4 = """\
  const wallH = 22 + lvl * 0.3;
  // Muralla de piedra oscura ancestral — no gris claro
  const wDark  = `rgb(${20+Math.floor(lvl*0.3)},${18+Math.floor(lvl*0.25)},${24+Math.floor(lvl*0.4)})`;
  const wMid   = `rgb(${28+Math.floor(lvl*0.35)},${24+Math.floor(lvl*0.3)},${34+Math.floor(lvl*0.45)})`;
  const wLight = `rgb(${36+Math.floor(lvl*0.4)},${32+Math.floor(lvl*0.35)},${44+Math.floor(lvl*0.5)})`;

  // Cara SW — tono frío AlalaiA
  ctx.beginPath();
  ctx.moveTo(W[0], W[1]); ctx.lineTo(S[0], S[1]);
  ctx.lineTo(S[0], S[1] + wallH); ctx.lineTo(W[0], W[1] + wallH);
  ctx.closePath();
  ctx.fillStyle = `rgb(${18+Math.floor(lvl*0.3)},${22+Math.floor(lvl*0.3)},${32+Math.floor(lvl*0.4)})`; ctx.fill();

  // Cara SE — tono cálido KarlakÁ
  ctx.beginPath();
  ctx.moveTo(E[0], E[1]); ctx.lineTo(S[0], S[1]);
  ctx.lineTo(S[0], S[1] + wallH); ctx.lineTo(E[0], E[1] + wallH);
  ctx.closePath();
  ctx.fillStyle = `rgb(${24+Math.floor(lvl*0.35)},${16+Math.floor(lvl*0.25)},${22+Math.floor(lvl*0.35)})`; ctx.fill();

  // Corona — piedra superior iluminada
  ctx.beginPath();
  pts.forEach(([px, py], i) => i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py));
  ctx.closePath();
  ctx.strokeStyle = wMid; ctx.lineWidth = wallH * 0.65; ctx.stroke();

  // Filo dorado ancestral
  ctx.strokeStyle = 'rgba(160,120,40,0.5)'; ctx.lineWidth = 1.5;
  ctx.beginPath();
  pts.forEach(([px, py], i) => i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py));
  ctx.closePath(); ctx.stroke();

  // Segundo filo más brillante
  ctx.strokeStyle = 'rgba(220,170,60,0.2)'; ctx.lineWidth = 0.6;
  ctx.beginPath();
  pts.forEach(([px, py], i) => i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py));
  ctx.closePath(); ctx.stroke();

  // Contorno base
  ctx.strokeStyle = 'rgba(0,0,0,0.7)'; ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(W[0], W[1]+wallH); ctx.lineTo(S[0], S[1]+wallH); ctx.lineTo(E[0], E[1]+wallH);
  ctx.stroke();

  // Almenas — misma piedra oscura
  const merlons = Math.floor(24 + lvl * 0.4);
  for (let i = 0; i < merlons; i++) {
    const t = i / merlons;
    const seg = Math.floor(t * 4);
    const f = (t * 4) % 1;
    const [ax, ay] = pts[seg], [bx, by] = pts[(seg + 1) % 4];
    const mx = ax + (bx - ax) * f;
    const my = ay + (by - ay) * f;
    ctx.fillStyle = wMid;
    ctx.fillRect(mx - 3, my - wallH * 0.35 - 7, 6, 8);
    // Borde de almena
    ctx.strokeStyle = 'rgba(160,120,40,0.3)'; ctx.lineWidth = 0.5;
    ctx.strokeRect(mx - 3, my - wallH * 0.35 - 7, 6, 8);
    // Ranura de la almena
    ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.fillRect(mx - 1, my - wallH * 0.35 - 6, 2, 4);
  }"""

c = src.count(OLD4)
if c != 1: print(f"ERROR fix 4: {c}x"); sys.exit(1)
src = src.replace(OLD4, NEW4)
print("OK fix 4: muralla oscura ancestral")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 5 — drawDuality: más intensidad + runas flotantes
# ══════════════════════════════════════════════════════════════════════════════
OLD5 = """\
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
  ctx.fillStyle = kG; ctx.fillRect(cx, 0, cx, cy + ry);"""

NEW5 = """\
// ─── DUALIDAD ALALAIA / KARLAKÃ ──────────────────────────────────────────────
function drawDuality(ctx, cx, cy, rx, ry) {
  // ── AlalaiA (izquierda): luz etérea azul-blanca más intensa ──────────────
  const aG = ctx.createRadialGradient(cx - rx*0.42, cy - ry*0.20, 5, cx - rx*0.42, cy - ry*0.20, rx*0.65);
  aG.addColorStop(0, `rgba(80,160,255,${0.14+0.06*Math.sin(tick*0.03)})`);
  aG.addColorStop(0.4, `rgba(50,110,200,${0.08+0.04*Math.sin(tick*0.025)})`);
  aG.addColorStop(1, 'rgba(30,60,140,0)');
  ctx.fillStyle = aG; ctx.fillRect(0, 0, cx + rx*0.1, cy + ry);

  // Partículas de luz AlalaiA — más numerosas y brillantes
  for (let i = 0; i < 14; i++) {
    const t = (tick * 0.010 + i * 0.52) % 1;
    const px = cx - rx*0.65 + Math.sin(i*1.4 + tick*0.008)*rx*0.42;
    const py = (cy + ry*0.5) - t * ry * 1.6;
    const alpha = t < 0.15 ? t/0.15*0.45 : t > 0.75 ? (1-t)/0.25*0.45 : 0.45;
    const size  = 1.2 + Math.sin(i*0.9)*0.8;
    ctx.fillStyle = `rgba(${160+Math.floor(i*4)},${200+Math.floor(i*2)},255,${alpha})`;
    ctx.beginPath(); ctx.arc(px, py, size, 0, Math.PI*2); ctx.fill();
  }

  // Runas de AlalaiA flotando
  const runeSymbols = ['✦','◆','✧','⋆'];
  ctx.font = '9px serif';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  for (let i = 0; i < 5; i++) {
    const t = (tick * 0.008 + i * 0.62) % 1;
    const rx2 = cx - rx*0.72 + Math.sin(i*2.1)*rx*0.38;
    const ry2 = (cy + ry*0.3) - t * ry * 1.4;
    const alpha = t < 0.2 ? t/0.2*0.35 : t > 0.7 ? (1-t)/0.3*0.35 : 0.35;
    ctx.fillStyle = `rgba(120,190,255,${alpha})`;
    ctx.fillText(runeSymbols[i % runeSymbols.length], rx2, ry2);
  }

  // ── KarlakÁ (derecha): brasa y fuego más visible ─────────────────────────
  const kG = ctx.createRadialGradient(cx + rx*0.42, cy - ry*0.15, 5, cx + rx*0.42, cy - ry*0.15, rx*0.65);
  kG.addColorStop(0, `rgba(200,60,10,${0.15+0.06*Math.sin(tick*0.04)})`);
  kG.addColorStop(0.4, `rgba(150,35,5,${0.09+0.04*Math.sin(tick*0.035)})`);
  kG.addColorStop(1, 'rgba(80,10,0,0)');
  ctx.fillStyle = kG; ctx.fillRect(cx - rx*0.1, 0, cx + rx*0.1, cy + ry);"""

c = src.count(OLD5)
if c != 1: print(f"ERROR fix 5: {c}x"); sys.exit(1)
src = src.replace(OLD5, NEW5)
print("OK fix 5: dualidad más intensa con runas")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 6 — getLayout: UN solo Templo, quitar duplicados TEMPLO_1 y TEMPLO_2
# ══════════════════════════════════════════════════════════════════════════════
OLD6 = """\
    // ── Plano medio: universidad, torre, templos ──────────────────────────────
    b( -ix*0.72,  -iy*0.05, 'UNIVERSIDAD',      'Universidad',   'university'),
    b( -ix*0.25,  +iy*0.05, 'TEMPLO_1',         'Templo', 'temple',   { accent: '#8a9040' }),
    b( +ix*0.72,  -iy*0.05, 'TEMPLO_2',         'Templo', 'temple',   { accent: '#c0452a' }),"""

NEW6 = """\
    // ── Plano medio: universidad ──────────────────────────────────────────────
    b( -ix*0.72,  -iy*0.05, 'UNIVERSIDAD',      'Universidad',   'university'),"""

c = src.count(OLD6)
if c != 1: print(f"ERROR fix 6: {c}x"); sys.exit(1)
src = src.replace(OLD6, NEW6)
print("OK fix 6: TEMPLO_1 y TEMPLO_2 eliminados del layout")

# ══════════════════════════════════════════════════════════════════════════════
# Guardar
# ══════════════════════════════════════════════════════════════════════════════
TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO — city.js actualizado.")
print()
print("Para verificar:")
print("  Ctrl+C → run.bat → Ctrl+Shift+R en http://127.0.0.1:8000/game")
