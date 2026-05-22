"""
fix_city_art.py
Eternal Warriors v3.0 — Arte ciudad: C.Ciudad dominante + decoración arquitectónica

Cambios:
  1. drawBuilding: scMax del C.Ciudad sube a 28 (domina visualmente).
                  Santuario baja a scMax=10 (complementa, no compite).
  2. drawSanctuary: altura reducida — la cúpula deja de ser el edificio más alto.
  3. renderFrame: se añade drawCityDecor() entre el terreno y los edificios.
     Pinta plazoleta central empedrada, caminos diagonales isométricos,
     fuentes de maná, farolas y muros bajos decorativos entre edificios.
  4. Nueva función drawCityDecor() insertada antes de drawStars.

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_city_art.py
"""

from pathlib import Path
import sys, re

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
if not TARGET.exists():
    print(f"ERROR: No se encontró:\n  {TARGET}")
    sys.exit(1)

src = TARGET.read_text(encoding="utf-8")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 1 — drawBuilding: scMax por tipo
# ══════════════════════════════════════════════════════════════════════════════
OLD_SC = (
    "  // Escala máxima reducida: edificios caben dentro de una celda (32px)\n"
    "  const scMax = b.type==='cityhall' ? 18 : b.type==='sanctuary' ? 14 : 12;\n"
    "  const sc = 0.30 + Math.min(lvl,scMax)*0.012;"
)
NEW_SC = (
    "  // C.Ciudad domina: scMax alto. Santuario complementa: scMax bajo.\n"
    "  const scMax = b.type==='cityhall' ? 28\n"
    "              : b.type==='sanctuary' ? 10\n"
    "              : b.type==='watchtower' ? 16\n"
    "              : b.type==='temple' ? 12\n"
    "              : 12;\n"
    "  const sc = 0.28 + Math.min(lvl,scMax)*0.013;"
)
c1 = src.count(OLD_SC)
if c1 != 1:
    print(f"ERROR fix 1: ancla encontrada {c1} veces. Abortando.")
    sys.exit(1)
src = src.replace(OLD_SC, NEW_SC)
print("OK fix 1: scMax — C.Ciudad=28, Santuario=10, Torre=16, Templo=12")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 2 — drawSanctuary: reducir altura de la cúpula
# ══════════════════════════════════════════════════════════════════════════════
OLD_SANCT = "function drawSanctuary(ctx, x, y, sc, lvl) {\n  const w=52*sc, h=(38+lvl*1.2)*sc;"
NEW_SANCT = "function drawSanctuary(ctx, x, y, sc, lvl) {\n  const w=44*sc, h=(28+lvl*0.5)*sc;"
c2 = src.count(OLD_SANCT)
if c2 != 1:
    print(f"ERROR fix 2: ancla encontrada {c2} veces. Abortando.")
    sys.exit(1)
src = src.replace(OLD_SANCT, NEW_SANCT)
print("OK fix 2: drawSanctuary — cúpula más compacta (h reducida)")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 3 — renderFrame: insertar drawCityDecor después del terreno
# ══════════════════════════════════════════════════════════════════════════════
OLD_RENDER = (
    "  // Muralla perimetral\n"
    "  const mLvl = Number(c.MURALLA||0);\n"
    "  if (mLvl > 0) drawWallPerimeter(ctx, cx, cy, mLvl);\n"
    "\n"
    "  // Edificios\n"
    "  const buildings = getLayout(c, cx, cy);"
)
NEW_RENDER = (
    "  // Muralla perimetral\n"
    "  const mLvl = Number(c.MURALLA||0);\n"
    "  if (mLvl > 0) drawWallPerimeter(ctx, cx, cy, mLvl);\n"
    "\n"
    "  // Decoración arquitectónica entre edificios\n"
    "  drawCityDecor(ctx, cx, cy, c);\n"
    "\n"
    "  // Edificios\n"
    "  const buildings = getLayout(c, cx, cy);"
)
c3 = src.count(OLD_RENDER)
if c3 != 1:
    print(f"ERROR fix 3: ancla encontrada {c3} veces. Abortando.")
    sys.exit(1)
src = src.replace(OLD_RENDER, NEW_RENDER)
print("OK fix 3: renderFrame — drawCityDecor() insertado antes de edificios")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 4 — Insertar drawCityDecor() antes de drawStars
# ══════════════════════════════════════════════════════════════════════════════
DECOR_FUNC = """\
function drawCityDecor(ctx, cx, cy, c) {
  const TW=64, TH=32;
  // iso helper local
  const iso=(dc,dr)=>({x:cx+(dc-dr)*TW/2, y:cy+(dc+dr)*TH/2});

  // ── Plazoleta central empedrada ────────────────────────────────────────────
  // Rombo de adoquines alrededor del centro
  ctx.save();
  for(let dc=-1;dc<=1;dc++){
    for(let dr=-1;dr<=1;dr++){
      if(Math.abs(dc)+Math.abs(dr)>1) continue;
      const {x,y}=iso(dc,dr);
      // Losa de piedra oscura con borde dorado
      ctx.fillStyle=dc===0&&dr===0?'#1a1820':'#161418';
      ctx.beginPath();
      ctx.moveTo(x,y-TH/2); ctx.lineTo(x+TW/2,y);
      ctx.lineTo(x,y+TH/2); ctx.lineTo(x-TW/2,y);
      ctx.closePath(); ctx.fill();
      ctx.strokeStyle='rgba(180,150,60,0.25)'; ctx.lineWidth=0.8; ctx.stroke();
    }
  }
  ctx.restore();

  // ── Fuente de maná central ────────────────────────────────────────────────
  const mana=Number(c.MANA||0);
  if(mana>0){
    const {x:fx,y:fy}=iso(0,0);
    // Base de piedra
    ctx.fillStyle='#2a2035';
    ctx.beginPath(); ctx.ellipse(fx,fy,18,8,0,0,Math.PI*2); ctx.fill();
    ctx.strokeStyle='rgba(140,100,200,0.4)'; ctx.lineWidth=1; ctx.stroke();
    // Agua de maná
    const wa=0.5+0.2*Math.sin(tick*0.06);
    ctx.fillStyle=`rgba(80,40,160,${wa})`;
    ctx.beginPath(); ctx.ellipse(fx,fy-3,12,5,0,0,Math.PI*2); ctx.fill();
    // Destello
    glow(ctx,fx,fy-4,14,'rgb(120,60,220)');
    ctx.fillStyle=`rgba(180,120,255,${0.7+0.3*Math.sin(tick*0.09)})`;
    ctx.beginPath(); ctx.arc(fx,fy-5,2.5,0,Math.PI*2); ctx.fill();
    // Partículas de maná subiendo
    for(let i=0;i<4;i++){
      const pa=(i/4)*Math.PI*2+tick*0.03;
      const pr=8+3*Math.sin(tick*0.05+i);
      const px=fx+Math.cos(pa)*pr*0.7;
      const py=fy-5+Math.sin(pa)*pr*0.3 - (tick*0.3+i*8)%20;
      const alpha=0.4+0.3*Math.sin(tick*0.06+i);
      ctx.fillStyle=`rgba(160,80,255,${alpha})`;
      ctx.beginPath(); ctx.arc(px,py,1.5,0,Math.PI*2); ctx.fill();
    }
  }

  // ── Caminos empedrados diagonales (proyección isométrica) ─────────────────
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
  ctx.restore();

  // ── Farolas isométricas en las esquinas de la plazoleta ───────────────────
  [[-1,-1],[+1,-1],[-1,+1],[+1,+1]].forEach(([dc,dr])=>{
    const {x,y}=iso(dc,dr);
    // Poste
    ctx.strokeStyle='#504850'; ctx.lineWidth=1.5;
    ctx.beginPath(); ctx.moveTo(x,y); ctx.lineTo(x,y-22); ctx.stroke();
    // Brazo
    ctx.beginPath(); ctx.moveTo(x,y-22); ctx.lineTo(x+5,y-24); ctx.stroke();
    // Luz
    const la=0.6+0.25*Math.sin(tick*0.07+dc+dr);
    glow(ctx,x+5,y-25,10,`rgba(255,200,80,${la})`);
    ctx.fillStyle=`rgba(255,220,120,${la+0.1})`;
    ctx.beginPath(); ctx.arc(x+5,y-25,2,0,Math.PI*2); ctx.fill();
    // Base del poste
    ctx.fillStyle='#3a3540';
    ctx.fillRect(x-2,y-3,4,4);
  });

  // ── Muros bajos entre edificios (separadores arquitectónicos) ─────────────
  // Muro izquierdo: de [-2,-1] a [-2,+1]
  [[-2,-1],[-2,0],[-2,+1]].forEach(([dc,dr],i,arr)=>{
    if(i===arr.length-1) return;
    const a=iso(dc,dr), b=iso(arr[i+1][0],arr[i+1][1]);
    ctx.strokeStyle='rgba(80,70,90,0.5)'; ctx.lineWidth=3;
    ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
    ctx.strokeStyle='rgba(120,100,130,0.2)'; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(a.x,a.y-4); ctx.lineTo(b.x,b.y-4); ctx.stroke();
  });
  // Muro derecho: de [+2,-1] a [+2,+1]
  [[+2,-1],[+2,0],[+2,+1]].forEach(([dc,dr],i,arr)=>{
    if(i===arr.length-1) return;
    const a=iso(dc,dr), b=iso(arr[i+1][0],arr[i+1][1]);
    ctx.strokeStyle='rgba(90,60,60,0.45)'; ctx.lineWidth=3;
    ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
    ctx.strokeStyle='rgba(140,80,70,0.2)'; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(a.x,a.y-4); ctx.lineTo(b.x,b.y-4); ctx.stroke();
  });

  // ── Arco de entrada (frente del C.Ciudad) ─────────────────────────────────
  const gate=iso(0,-1);
  ctx.fillStyle='rgba(40,50,80,0.7)';
  ctx.beginPath();
  ctx.arc(gate.x, gate.y+8, 10, Math.PI, 0);
  ctx.fill();
  ctx.strokeStyle='rgba(100,140,220,0.4)'; ctx.lineWidth=1.5;
  ctx.beginPath(); ctx.arc(gate.x, gate.y+8, 10, Math.PI, 0); ctx.stroke();
  const archGlow=0.3+0.15*Math.sin(tick*0.06);
  glow(ctx, gate.x, gate.y+2, 16, `rgba(80,130,255,${archGlow})`);
}

"""

OLD_STARS = "function drawStars(ctx, W, H) {"
c4 = src.count(OLD_STARS)
if c4 != 1:
    print(f"ERROR fix 4: ancla drawStars encontrada {c4} veces. Abortando.")
    sys.exit(1)
src = src.replace(OLD_STARS, DECOR_FUNC + OLD_STARS)
print("OK fix 4: drawCityDecor() — plazoleta, fuente de maná, farolas, caminos, muros")

# ══════════════════════════════════════════════════════════════════════════════
# Guardar
# ══════════════════════════════════════════════════════════════════════════════
TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO — city.js actualizado.")
print()
print("Para verificar:")
print("  Recarga con Ctrl+Shift+R en http://127.0.0.1:8000/game")
print("  El Centro de Ciudad debe ser el edificio más alto y prominente.")
print("  Plazoleta central empedrada con fuente de maná visible.")
print("  Farolas en las 4 esquinas de la plazoleta con luz cálida animada.")
print("  Caminos diagonales empedrados cruzando el rombo.")
