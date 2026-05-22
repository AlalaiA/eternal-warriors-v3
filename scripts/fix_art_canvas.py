"""
fix_art_canvas.py
Eternal Warriors v3.0 — Reescritura artística de edificios Canvas 2D

Reemplaza drawBuilding para usar funciones artísticas canvas en lugar de sprites PNG.
Cada edificio tiene:
  - 3 caras isométricas con gradientes diferenciados (top/left/right)
  - Textura de piedra procedural con juntas irregulares
  - Ventanas con luz interna animada
  - Efectos de luz volumétrica y partículas

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_art_canvas.py
"""

from pathlib import Path
import sys, shutil

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
bak = TARGET.with_suffix(".js.art.bak")
shutil.copy2(TARGET, bak)
src = TARGET.read_text(encoding="utf-8")

# ── FIX 1: drawBuilding vuelve a usar funciones canvas artísticas ─────────────
OLD_BLD = """\
// ─── DISPATCHER DE EDIFICIOS ──────────────────────────────────────────────────
function drawBuilding(ctx, b) {
  const lvl = b.lvl || 0;
  // Altura en px del sprite según tipo
  const SH = {cityhall:210,sanctuary:88,temple:95,university:88,
    warehouse:80,watchtower:90,travel:80,house:68,
    barracks:85,forge:72,hideout:55};
  const h = SH[b.type] || 90;
  drawSprite(ctx, b.type, b.x, b.y, h);
  drawLabel(ctx, b.x, b.y, b.label, b.lvl, b.type);
}"""

NEW_BLD = """\
// ─── DISPATCHER DE EDIFICIOS ──────────────────────────────────────────────────
function drawBuilding(ctx, b) {
  const lvl = b.lvl || 0;
  ctx.save();
  switch (b.type) {
    case 'cityhall':   artCityHall(ctx, b.x, b.y, lvl);   break;
    case 'sanctuary':  artSanctuary(ctx, b.x, b.y, lvl);  break;
    case 'temple':     artTemple(ctx, b.x, b.y, lvl);     break;
    case 'university': artUniversity(ctx, b.x, b.y, lvl); break;
    case 'warehouse':  artWarehouse(ctx, b.x, b.y, lvl);  break;
    case 'watchtower': artWatchtower(ctx, b.x, b.y, lvl); break;
    case 'travel':     artTravel(ctx, b.x, b.y, lvl);     break;
    case 'house':      artHouse(ctx, b.x, b.y, lvl);      break;
    case 'barracks':   artBarracks(ctx, b.x, b.y, lvl);   break;
    case 'forge':      artForge(ctx, b.x, b.y, lvl);      break;
    case 'hideout':    artHideout(ctx, b.x, b.y, lvl);    break;
  }
  ctx.restore();
  drawLabel(ctx, b.x, b.y, b.label, lvl, b.type);
}

// ═══════════════════════════════════════════════════════════════════════════════
// HELPERS ARTÍSTICOS
// ═══════════════════════════════════════════════════════════════════════════════

// Caja isométrica artística con 3 caras, gradientes y borde de piedra
function isoArt(ctx, x, y, w, h, cTop, cLeft, cRight, opts={}) {
  const hw = w/2, qh = w/4;
  const bevel = opts.bevel || 0.5;

  // Cara superior
  const gTop = ctx.createLinearGradient(x-hw, y-h, x+hw, y-h+qh*2);
  gTop.addColorStop(0, lighten(cTop, 0.15));
  gTop.addColorStop(0.5, cTop);
  gTop.addColorStop(1, darken(cTop, 0.1));
  ctx.fillStyle = gTop;
  ctx.beginPath();
  ctx.moveTo(x, y-h);
  ctx.lineTo(x+hw, y-h+qh);
  ctx.lineTo(x, y-h+qh*2);
  ctx.lineTo(x-hw, y-h+qh);
  ctx.closePath(); ctx.fill();

  // Cara izquierda
  const gLeft = ctx.createLinearGradient(x-hw, y-h+qh, x, y);
  gLeft.addColorStop(0, cLeft);
  gLeft.addColorStop(1, darken(cLeft, 0.25));
  ctx.fillStyle = gLeft;
  ctx.beginPath();
  ctx.moveTo(x-hw, y-h+qh);
  ctx.lineTo(x, y-h+qh*2);
  ctx.lineTo(x, y);
  ctx.lineTo(x-hw, y-qh);
  ctx.closePath(); ctx.fill();

  // Cara derecha
  const gRight = ctx.createLinearGradient(x, y-h+qh*2, x+hw, y-qh);
  gRight.addColorStop(0, cRight);
  gRight.addColorStop(1, darken(cRight, 0.3));
  ctx.fillStyle = gRight;
  ctx.beginPath();
  ctx.moveTo(x, y-h+qh*2);
  ctx.lineTo(x+hw, y-h+qh);
  ctx.lineTo(x+hw, y-qh);
  ctx.lineTo(x, y);
  ctx.closePath(); ctx.fill();

  // Textura de piedra en caras (juntas de mampostería)
  if (opts.stone !== false) {
    drawStoneTexture(ctx, x, y, w, h);
  }

  // Contorno
  ctx.strokeStyle = 'rgba(0,0,0,0.7)';
  ctx.lineWidth = 0.8;
  ctx.beginPath();
  ctx.moveTo(x, y-h); ctx.lineTo(x+hw, y-h+qh); ctx.lineTo(x+hw, y-qh);
  ctx.lineTo(x, y); ctx.lineTo(x-hw, y-qh); ctx.lineTo(x-hw, y-h+qh);
  ctx.closePath(); ctx.stroke();

  // Filo superior dorado
  if (opts.gold) {
    ctx.strokeStyle = `rgba(200,160,50,${opts.gold})`;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x-hw, y-h+qh); ctx.lineTo(x, y-h); ctx.lineTo(x+hw, y-h+qh);
    ctx.stroke();
  }
}

// Textura de juntas de piedra sobre una caja isométrica
function drawStoneTexture(ctx, x, y, w, h) {
  const hw = w/2, qh = w/4;
  ctx.save();
  ctx.strokeStyle = 'rgba(0,0,0,0.18)';
  ctx.lineWidth = 0.6;
  // Juntas horizontales cara izq
  const rows = Math.max(2, Math.floor(h/12));
  for (let i = 1; i < rows; i++) {
    const t = i/rows;
    const yy = y - h + h*t;
    const xOff = hw * (1-t*0.5);
    ctx.beginPath();
    ctx.moveTo(x-hw, yy-qh*(1-t)); ctx.lineTo(x, yy);
    ctx.stroke();
    // Juntas verticales alternadas
    if (i%2===0) {
      ctx.beginPath();
      ctx.moveTo(x-hw*0.5, yy-qh*0.5*(1-t)); ctx.lineTo(x-hw*0.5, yy-qh*0.5*(1-t)-8);
      ctx.stroke();
    }
  }
  // Juntas horizontales cara der
  for (let i = 1; i < rows; i++) {
    const t = i/rows;
    const yy = y - h + h*t;
    ctx.beginPath();
    ctx.moveTo(x, yy); ctx.lineTo(x+hw, yy-qh*(1-t));
    ctx.stroke();
    if (i%2!==0) {
      ctx.beginPath();
      ctx.moveTo(x+hw*0.5, yy-qh*0.5*(1-t)); ctx.lineTo(x+hw*0.5, yy-qh*0.5*(1-t)-8);
      ctx.stroke();
    }
  }
  ctx.restore();
}

// Ventana isométrica con luz interna
function isoWindow(ctx, x, y, w, h, color, alpha) {
  ctx.fillStyle = 'rgba(0,0,0,0.7)';
  ctx.fillRect(x-w/2-1, y-h-1, w+2, h+2);
  const wg = ctx.createLinearGradient(x-w/2, y-h, x+w/2, y);
  wg.addColorStop(0, color.replace(')', `,${alpha+0.2})`).replace('rgb','rgba'));
  wg.addColorStop(1, color.replace(')', `,${alpha})`).replace('rgb','rgba'));
  ctx.fillStyle = wg;
  ctx.fillRect(x-w/2, y-h, w, h);
  // Reflejo
  ctx.fillStyle = `rgba(255,255,255,0.08)`;
  ctx.fillRect(x-w/2, y-h, w*0.4, h*0.45);
}

// Aguja/espiga artística
function drawSpire(ctx, x, y, h, w, color) {
  const g = ctx.createLinearGradient(x, y-h, x+w/2, y);
  g.addColorStop(0, lighten(color, 0.4));
  g.addColorStop(1, darken(color, 0.2));
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.moveTo(x, y-h);
  ctx.lineTo(x+w/2, y);
  ctx.lineTo(x-w/2, y);
  ctx.closePath(); ctx.fill();
  // Cara oscura
  ctx.fillStyle = darken(color, 0.3);
  ctx.beginPath();
  ctx.moveTo(x, y-h);
  ctx.lineTo(x, y);
  ctx.lineTo(x-w/2, y);
  ctx.closePath(); ctx.fill();
  ctx.strokeStyle = 'rgba(0,0,0,0.6)'; ctx.lineWidth = 0.7;
  ctx.beginPath(); ctx.moveTo(x,y-h); ctx.lineTo(x+w/2,y); ctx.lineTo(x-w/2,y); ctx.closePath(); ctx.stroke();
}

// Orbe mágico con glow
function drawOrb(ctx, x, y, r, color) {
  const glow = ctx.createRadialGradient(x,y,1,x,y,r*3.5);
  glow.addColorStop(0, color.replace('rgb','rgba').replace(')',',0.4)'));
  glow.addColorStop(1, color.replace('rgb','rgba').replace(')',',0)'));
  ctx.fillStyle = glow;
  ctx.beginPath(); ctx.arc(x,y,r*3.5,0,Math.PI*2); ctx.fill();
  const orb = ctx.createRadialGradient(x-r*0.3,y-r*0.3,r*0.1,x,y,r);
  orb.addColorStop(0,'rgba(255,255,255,0.9)');
  orb.addColorStop(0.3, lighten(color,0.4));
  orb.addColorStop(1, darken(color,0.2));
  ctx.fillStyle = orb;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
}

// Haz de luz vertical
function drawBeam(ctx, x, y, h, color) {
  const g = ctx.createLinearGradient(x,y,x,y-h);
  g.addColorStop(0, color.replace('rgb','rgba').replace(')',',0.3)'));
  g.addColorStop(0.5, color.replace('rgb','rgba').replace(')',',0.08)'));
  g.addColorStop(1, color.replace('rgb','rgba').replace(')',',0)'));
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.moveTo(x-6,y); ctx.lineTo(x+6,y); ctx.lineTo(x+2,y-h); ctx.lineTo(x-2,y-h);
  ctx.closePath(); ctx.fill();
}

// Domo/cúpula artística
function drawDome(ctx, x, y, rx, ry, color) {
  // Cara oscura izq
  const gL = ctx.createRadialGradient(x-rx*0.3, y-ry*0.2, 2, x, y, rx);
  gL.addColorStop(0, lighten(color,0.2));
  gL.addColorStop(0.5, color);
  gL.addColorStop(1, darken(color,0.4));
  ctx.fillStyle = gL;
  ctx.beginPath(); ctx.ellipse(x, y, rx, ry, 0, Math.PI, 0); ctx.fill();
  // Reflejo especular
  ctx.fillStyle = 'rgba(255,255,255,0.06)';
  ctx.beginPath(); ctx.ellipse(x-rx*0.2, y-ry*0.3, rx*0.4, ry*0.3, -0.3, Math.PI, 0); ctx.fill();
  // Nervios
  ctx.strokeStyle = darken(color, 0.25); ctx.lineWidth = 0.8;
  for (let i=-2; i<=2; i++) {
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.quadraticCurveTo(x + i*rx*0.4, y-ry*0.6, x+i*rx*0.5, y);
    ctx.stroke();
  }
  // Borde base
  ctx.strokeStyle = darken(color,0.3); ctx.lineWidth = 1.2;
  ctx.beginPath(); ctx.ellipse(x,y,rx,ry*0.25,0,0,Math.PI*2); ctx.stroke();
}

// Utilidades de color
function lighten(hex, amount) {
  const [r,g,b] = parseRGB(hex);
  return `rgb(${Math.min(255,Math.round(r+(255-r)*amount))},${Math.min(255,Math.round(g+(255-g)*amount))},${Math.min(255,Math.round(b+(255-b)*amount))})`;
}
function darken(hex, amount) {
  const [r,g,b] = parseRGB(hex);
  return `rgb(${Math.round(r*(1-amount))},${Math.round(g*(1-amount))},${Math.round(b*(1-amount))})`;
}
function parseRGB(c) {
  const m = c.match(/\d+/g);
  return m ? [+m[0],+m[1],+m[2]] : [128,128,128];
}

// ═══════════════════════════════════════════════════════════════════════════════
// EDIFICIOS ARTÍSTICOS
// ═══════════════════════════════════════════════════════════════════════════════

function artCityHall(ctx, x, y, lvl) {
  const sc = 0.7 + Math.min(lvl,40)*0.008;
  const W=90*sc, H=130*sc;

  // Plataforma base
  isoArt(ctx,x,y,W*1.4,H*0.08,'rgb(22,28,42)','rgb(14,18,28)','rgb(18,24,36)',{stone:false,gold:0.2});
  isoArt(ctx,x,y-H*0.06,W*1.15,H*0.1,'rgb(25,32,50)','rgb(16,20,32)','rgb(20,28,44)',{stone:true,gold:0.25});

  // Alas laterales
  isoArt(ctx,x-W*0.55,y-H*0.1,W*0.45,H*0.55,'rgb(28,38,70)','rgb(18,24,48)','rgb(22,32,58)',{stone:true,gold:0.15});
  isoArt(ctx,x+W*0.55,y-H*0.1,W*0.45,H*0.55,'rgb(24,34,64)','rgb(15,20,42)','rgb(20,30,54)',{stone:true,gold:0.12});

  // Pináculos alas
  drawSpire(ctx, x-W*0.55, y-H*0.63, H*0.22, W*0.12, 'rgb(45,65,120)');
  drawOrb(ctx, x-W*0.55, y-H*0.63-H*0.22, 4*sc, 'rgb(100,160,255)');
  drawSpire(ctx, x+W*0.55, y-H*0.63, H*0.22, W*0.12, 'rgb(40,58,108)');
  drawOrb(ctx, x+W*0.55, y-H*0.63-H*0.22, 4*sc, 'rgb(100,160,255)');

  // Torre central — la más alta
  isoArt(ctx,x,y-H*0.12,W*0.55,H*0.9,'rgb(32,45,88)','rgb(20,28,60)','rgb(26,38,75)',{stone:true,gold:0.3});

  // Ventanas torre (arco)
  const wA = 0.45 + 0.2*Math.sin(tick*0.04);
  for(let i=0;i<5;i++){
    const wy=y-H*(0.22+i*0.13);
    isoWindow(ctx,x-W*0.12,wy,W*0.14,H*0.1,'rgb(100,180,255)',wA-i*0.05);
    isoWindow(ctx,x+W*0.08,wy,W*0.14,H*0.1,'rgb(100,180,255)',wA-i*0.06);
  }
  // Ventanas alas
  for(let i=0;i<3;i++){
    isoWindow(ctx,x-W*0.66,y-H*(0.2+i*0.13),W*0.13,H*0.09,'rgb(80,150,230)',0.35-i*0.05);
    isoWindow(ctx,x+W*0.43,y-H*(0.2+i*0.13),W*0.13,H*0.09,'rgb(80,150,230)',0.32-i*0.05);
  }

  // Sub-torre y aguja
  isoArt(ctx,x,y-H*0.98,W*0.28,H*0.14,'rgb(38,55,105)','rgb(24,34,72)','rgb(32,46,90)',{stone:false});
  drawSpire(ctx, x, y-H*1.1, H*0.3, W*0.18, 'rgb(50,75,140)');

  // Haz de luz y orbe
  drawBeam(ctx, x, y-H*1.38, H*0.8, 'rgb(140,200,255)');
  drawOrb(ctx, x, y-H*1.38, 8*sc, 'rgb(160,220,255)');

  // Bandera animada
  ctx.strokeStyle='rgb(55,80,130)'; ctx.lineWidth=1.5;
  ctx.beginPath(); ctx.moveTo(x-W*0.55,y-H*0.85); ctx.lineTo(x-W*0.55,y-H*1.0); ctx.stroke();
  const fw=Math.sin(tick*0.06)*4*sc;
  ctx.fillStyle='rgb(40,60,120)';
  ctx.beginPath(); ctx.moveTo(x-W*0.55,y-H*1.0); ctx.lineTo(x-W*0.55+16*sc+fw,y-H*0.96); ctx.lineTo(x-W*0.55+14*sc+fw*0.7,y-H*0.93); ctx.lineTo(x-W*0.55,y-H*0.93); ctx.closePath(); ctx.fill();
}

function artSanctuary(ctx, x, y, lvl) {
  const sc = 0.65 + Math.min(lvl,44)*0.007;
  const W=70*sc, H=95*sc;

  // Base octogonal
  isoArt(ctx,x,y,W*1.1,H*0.12,'rgb(20,8,38)','rgb(12,4,24)','rgb(16,6,32)',{stone:true,gold:0.2});
  // Columnas
  for(let i=-1;i<=1;i++){
    isoArt(ctx,x+i*W*0.38,y-H*0.08,W*0.14,H*0.5,'rgb(30,10,55)','rgb(18,6,36)','rgb(24,8,46)',{stone:true});
  }
  // Cuerpo bajo cúpula
  isoArt(ctx,x,y-H*0.45,W*0.8,H*0.52,'rgb(35,12,65)','rgb(22,7,42)','rgb(28,10,54)',{stone:true,gold:0.15});

  // Cúpula
  drawDome(ctx,x,y-H*0.94,W*0.48,H*0.36,'rgb(70,18,130)');
  // Ventana circular cúpula
  const ca=0.4+0.25*Math.sin(tick*0.07);
  ctx.strokeStyle=`rgba(200,80,255,${ca})`; ctx.lineWidth=2;
  ctx.beginPath(); ctx.arc(x,y-H*0.94,W*0.16,0,Math.PI*2); ctx.stroke();
  ctx.fillStyle=`rgba(180,60,240,${ca*0.4})`;
  ctx.beginPath(); ctx.arc(x,y-H*0.94,W*0.12,0,Math.PI*2); ctx.fill();

  // Esferas orbitando
  for(let i=0;i<6;i++){
    const a=(i/6)*Math.PI*2+tick*0.022;
    const ox=Math.cos(a)*W*0.42, oy=Math.sin(a)*W*0.16;
    drawOrb(ctx,x+ox,y-H*0.94+oy,4*sc,'rgb(180,60,255)');
  }

  // Aguja y orbe cima
  drawSpire(ctx,x,y-H*1.28,H*0.22,W*0.12,'rgb(80,20,150)');
  drawBeam(ctx,x,y-H*1.48,H*0.5,'rgb(200,80,255)');
  drawOrb(ctx,x,y-H*1.48,7*sc,'rgb(210,100,255)');
}

function artTemple(ctx, x, y, lvl) {
  const sc = 0.62 + Math.min(lvl,3)*0.06;
  const W=65*sc, H=90*sc;

  // Base escalonada
  isoArt(ctx,x,y,W*1.2,H*0.1,'rgb(14,20,38)','rgb(8,12,24)','rgb(12,18,32)',{stone:false,gold:0.15});
  isoArt(ctx,x,y-H*0.08,W,H*0.14,'rgb(18,26,50)','rgb(10,16,32)','rgb(15,22,42)',{stone:true,gold:0.18});

  // Columnas frontales con capiteles
  for(let i=-1;i<=1;i++){
    isoArt(ctx,x+i*W*0.32,y-H*0.18,W*0.13,H*0.46,'rgb(22,34,65)','rgb(14,20,40)','rgb(18,28,54)',{stone:true});
    // Capitel dorado
    isoArt(ctx,x+i*W*0.32,y-H*0.62,W*0.18,H*0.04,'rgb(160,130,40)','rgb(120,95,25)','rgb(140,112,30)',{stone:false});
  }

  // Cuerpo principal
  isoArt(ctx,x,y-H*0.60,W*0.75,H*0.54,'rgb(20,30,60)','rgb(12,18,38)','rgb(16,26,50)',{stone:true,gold:0.12});

  // Cristales de AlalaiA flanqueando
  const ca=0.7+0.2*Math.sin(tick*0.05);
  // Cristal central
  ctx.save();
  const cg=ctx.createLinearGradient(x,y-H*1.3,x,y-H*0.6);
  cg.addColorStop(0,`rgba(180,230,255,${ca})`);
  cg.addColorStop(0.5,'rgba(80,160,220,0.7)');
  cg.addColorStop(1,'rgba(30,80,160,0.4)');
  ctx.fillStyle=cg;
  ctx.beginPath(); ctx.moveTo(x,y-H*1.3); ctx.lineTo(x+W*0.1,y-H*0.62); ctx.lineTo(x-W*0.1,y-H*0.62); ctx.closePath(); ctx.fill();
  ctx.strokeStyle=`rgba(200,240,255,${ca*0.7})`; ctx.lineWidth=0.8;
  ctx.beginPath(); ctx.moveTo(x,y-H*1.3); ctx.lineTo(x+W*0.1,y-H*0.62); ctx.stroke();
  ctx.restore();

  // Cristales laterales
  for(const [dx,dh] of [[-W*0.42,-1.0],[W*0.42,-1.0],[-W*0.58,-0.78],[W*0.58,-0.78]]){
    const cga=ctx.createLinearGradient(x+dx,y+dh*H,x+dx,y-H*0.62);
    cga.addColorStop(0,`rgba(160,220,255,${ca*0.8})`);
    cga.addColorStop(1,'rgba(40,100,180,0.3)');
    ctx.fillStyle=cga;
    ctx.beginPath(); ctx.moveTo(x+dx,y+dh*H); ctx.lineTo(x+dx+W*0.07,y-H*0.62); ctx.lineTo(x+dx-W*0.07,y-H*0.62); ctx.closePath(); ctx.fill();
    drawOrb(ctx,x+dx,y+dh*H,4.5*sc,'rgb(140,210,255)');
  }
  drawOrb(ctx,x,y-H*1.3,6*sc,'rgb(200,240,255)');
  drawBeam(ctx,x,y-H*1.28,H*0.5,'rgb(160,220,255)');

  // Puerta con luz interior
  ctx.fillStyle='rgba(0,0,0,0.8)';
  ctx.beginPath(); ctx.arc(x,y-H*0.28,W*0.12,Math.PI,0); ctx.rect(x-W*0.12,y-H*0.28,W*0.24,H*0.2); ctx.fill();
  const pA=0.3+0.15*Math.sin(tick*0.06);
  ctx.fillStyle=`rgba(120,200,255,${pA})`;
  ctx.beginPath(); ctx.arc(x,y-H*0.28,W*0.08,Math.PI,0); ctx.rect(x-W*0.08,y-H*0.28,W*0.16,H*0.16); ctx.fill();
}

function artUniversity(ctx, x, y, lvl) {
  const sc = 0.6 + Math.min(lvl,9)*0.015;
  const W=72*sc, H=88*sc;

  // Base
  isoArt(ctx,x,y,W*1.1,H*0.1,'rgb(14,22,36)','rgb(8,14,22)','rgb(12,18,30)',{stone:true,gold:0.12});

  // Torre lateral izq — la más alta
  isoArt(ctx,x-W*0.42,y-H*0.08,W*0.28,H*0.95,'rgb(16,26,46)','rgb(10,16,28)','rgb(13,22,38)',{stone:true});
  // Techo cónico torre
  drawSpire(ctx,x-W*0.42,y-H*1.0,H*0.24,W*0.3,'rgb(22,35,58)');
  // Veleta
  ctx.strokeStyle='rgb(70,100,140)'; ctx.lineWidth=1.2;
  ctx.beginPath(); ctx.moveTo(x-W*0.42,y-H*1.22); ctx.lineTo(x-W*0.42,y-H*1.35); ctx.stroke();
  ctx.fillStyle='rgb(60,90,130)'; ctx.beginPath(); ctx.moveTo(x-W*0.42-6*sc,y-H*1.31); ctx.lineTo(x-W*0.42+6*sc,y-H*1.31); ctx.lineTo(x-W*0.42,y-H*1.35); ctx.closePath(); ctx.fill();

  // Cuerpo principal biblioteca
  isoArt(ctx,x+W*0.1,y-H*0.08,W*0.78,H*0.82,'rgb(18,28,48)','rgb(11,17,30)','rgb(15,24,40)',{stone:true,gold:0.1});

  // Contrafuertes
  for(const dy of [0.25,0.48,0.68]){
    isoArt(ctx,x+W*0.52,y-H*dy,W*0.14,H*0.12,'rgb(14,22,38)','rgb(8,13,22)','rgb(12,18,32)',{stone:false});
  }

  // Ventanas con arco y luz cálida
  const wA=0.38+0.15*Math.sin(tick*0.04);
  // Ventanas torre
  for(let i=0;i<4;i++){
    isoWindow(ctx,x-W*0.42,y-H*(0.2+i*0.17),W*0.15,H*0.1,'rgb(255,190,80)',wA-i*0.04);
  }
  // Ventanas góticas cuerpo
  for(let i=0;i<3;i++){
    const wx=x-W*0.06+i*W*0.22;
    ctx.fillStyle='rgba(0,0,0,0.8)';
    ctx.beginPath(); ctx.arc(wx,y-H*0.48,W*0.08,Math.PI,0); ctx.rect(wx-W*0.08,y-H*0.48,W*0.16,H*0.2); ctx.fill();
    ctx.fillStyle=`rgba(255,185,70,${wA-i*0.04})`;
    ctx.beginPath(); ctx.arc(wx,y-H*0.48,W*0.055,Math.PI,0); ctx.rect(wx-W*0.055,y-H*0.48,W*0.11,H*0.15); ctx.fill();
  }

  // Friso ornamental
  ctx.strokeStyle='rgba(160,130,40,0.3)'; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(x-W*0.14,y-H*0.72); ctx.lineTo(x+W*0.52,y-H*0.72); ctx.stroke();
}

function artWarehouse(ctx, x, y, lvl) {
  const sc = 0.6 + Math.min(lvl,44)*0.005;
  const W=80*sc, H=58*sc;

  // Base
  isoArt(ctx,x,y,W*1.05,H*0.14,'rgb(34,22,10)','rgb(22,14,5)','rgb(28,18,8)',{stone:false});
  // Cuerpo ancho
  isoArt(ctx,x,y-H*0.1,W,H,'rgb(52,36,16)','rgb(36,24,8)','rgb(44,30,12)',{stone:true,gold:0.08});
  // Techo a dos aguas
  ctx.fillStyle='rgb(28,18,7)';
  ctx.beginPath(); ctx.moveTo(x-W/2,y-H*1.05); ctx.lineTo(x,y-H*1.22); ctx.lineTo(x+W/2,y-H*1.05); ctx.closePath(); ctx.fill();
  ctx.fillStyle='rgb(22,14,5)';
  ctx.beginPath(); ctx.moveTo(x-W/2,y-H*1.05); ctx.lineTo(x,y-H*1.22); ctx.lineTo(x,y-H*1.05); ctx.closePath(); ctx.fill();
  // Vigas techo
  ctx.strokeStyle='rgba(0,0,0,0.25)'; ctx.lineWidth=1;
  for(let i=1;i<5;i++){ctx.beginPath();ctx.moveTo(x-W/2+i*W/5,y-H*1.05);ctx.lineTo(x,y-H*1.22);ctx.stroke();}

  // Puertas dobles con herrajes
  ctx.fillStyle='rgba(0,0,0,0.8)';
  ctx.fillRect(x-W*0.17,y-H*0.55,W*0.14,H*0.52);
  ctx.fillRect(x+W*0.03,y-H*0.55,W*0.14,H*0.52);
  ctx.strokeStyle='rgb(60,40,15)'; ctx.lineWidth=1.2;
  ctx.strokeRect(x-W*0.18,y-H*0.57,W*0.36,H*0.55);
  // Herrajes
  for(const [px,py] of [[x-W*0.1,y-H*0.35],[x-W*0.1,y-H*0.22],[x+W*0.1,y-H*0.35],[x+W*0.1,y-H*0.22]]){
    ctx.fillStyle='rgb(70,55,20)'; ctx.beginPath(); ctx.arc(px,py,2.5*sc,0,Math.PI*2); ctx.fill();
  }
  // Ventanas laterales con luz cálida
  const wA=0.3+0.12*Math.sin(tick*0.04);
  isoWindow(ctx,x-W*0.4,y-H*0.42,W*0.15,H*0.2,'rgb(255,180,60)',wA);
  isoWindow(ctx,x+W*0.28,y-H*0.42,W*0.15,H*0.2,'rgb(255,180,60)',wA*0.85);
}

function artWatchtower(ctx, x, y, lvl) {
  const sc = 0.58 + Math.min(lvl,13)*0.01;
  const W=42*sc, H=110*sc;

  // Base reforzada
  isoArt(ctx,x,y,W*1.8,H*0.14,'rgb(18,24,32)','rgb(10,14,20)','rgb(15,20,28)',{stone:true});
  isoArt(ctx,x,y-H*0.12,W*1.4,H*0.1,'rgb(20,27,38)','rgb(12,16,24)','rgb(16,22,32)',{stone:true});

  // Fuste principal
  isoArt(ctx,x,y-H*0.2,W,H*0.72,'rgb(24,32,44)','rgb(15,20,28)','rgb(20,27,38)',{stone:true,gold:0.08});

  // Balcón
  isoArt(ctx,x,y-H*0.9,W*1.4,H*0.06,'rgb(28,38,52)','rgb(18,24,34)','rgb(22,30,42)',{stone:false,gold:0.12});
  // Almenas
  isoArt(ctx,x,y-H*0.95,W*1.3,H*0.1,'rgb(26,35,48)','rgb(16,22,32)','rgb(22,30,42)',{stone:false});
  for(let i=-2;i<=2;i++){
    ctx.fillStyle='rgb(30,40,55)';
    ctx.fillRect(x+i*W*0.24-4*sc,y-H*1.04,7*sc,9*sc);
    ctx.fillStyle='rgba(0,0,0,0.5)';
    ctx.fillRect(x+i*W*0.24-1.5*sc,y-H*1.03,3*sc,5*sc);
  }

  // Ventanas de observación
  const wA=0.35+0.15*Math.sin(tick*0.04);
  for(const h of [0.35,0.52,0.68]){
    isoWindow(ctx,x,y-H*h,W*0.3,H*0.1,'rgb(180,220,255)',wA);
  }

  // Faro giratorio
  const fAngle = tick*0.04;
  const fLen = 60*sc;
  const fx = x+Math.cos(fAngle)*fLen, fy = y-H*0.97+Math.sin(fAngle)*12*sc;
  const fG=ctx.createLinearGradient(x,y-H*0.97,fx,fy);
  fG.addColorStop(0,'rgba(200,240,255,0.5)'); fG.addColorStop(1,'rgba(200,240,255,0)');
  ctx.fillStyle=fG;
  ctx.beginPath(); ctx.moveTo(x-4,y-H*0.97); ctx.lineTo(x+4,y-H*0.97); ctx.lineTo(fx+3,fy); ctx.lineTo(fx-3,fy); ctx.closePath(); ctx.fill();
  drawOrb(ctx,x,y-H*0.97,6*sc,'rgb(200,240,255)');

  // Bandera
  ctx.strokeStyle='rgb(60,80,110)'; ctx.lineWidth=1.2;
  ctx.beginPath(); ctx.moveTo(x,y-H*1.04); ctx.lineTo(x,y-H*1.2); ctx.stroke();
  ctx.fillStyle='rgb(40,55,90)';
  ctx.fillRect(x,y-H*1.2,14*sc,9*sc);
}

function artTravel(ctx, x, y, lvl) {
  const sc = 0.6 + Math.min(lvl,11)*0.012;
  const W=68*sc, H=80*sc;

  // Base
  isoArt(ctx,x,y,W*1.1,H*0.12,'rgb(18,22,52)','rgb(10,13,32)','rgb(14,18,42)',{stone:false,gold:0.15});
  isoArt(ctx,x,y-H*0.1,W,H*0.2,'rgb(22,28,65)','rgb(13,17,40)','rgb(18,24,54)',{stone:true,gold:0.18});
  // Cuerpo
  isoArt(ctx,x,y-H*0.28,W*0.88,H*0.7,'rgb(26,34,78)','rgb(16,20,48)','rgb(22,30,66)',{stone:true,gold:0.12});

  // Portal arcano central
  const pA=0.5+0.3*Math.sin(tick*0.08);
  const pGlow=ctx.createRadialGradient(x,y-H*0.5,2,x,y-H*0.5,W*0.26);
  pGlow.addColorStop(0,`rgba(80,120,255,${pA})`); pGlow.addColorStop(1,'rgba(40,80,220,0)');
  ctx.fillStyle=pGlow; ctx.beginPath(); ctx.ellipse(x,y-H*0.5,W*0.26,H*0.26,0,0,Math.PI*2); ctx.fill();
  // Arco portal
  ctx.strokeStyle=`rgba(120,180,255,${pA*0.8})`; ctx.lineWidth=3;
  ctx.beginPath(); ctx.ellipse(x,y-H*0.52,W*0.2,H*0.2,0,Math.PI,0); ctx.stroke();
  ctx.beginPath(); ctx.ellipse(x,y-H*0.52,W*0.14,H*0.14,0,Math.PI,0); ctx.stroke();
  // Interior portal
  ctx.fillStyle=`rgba(40,80,200,${pA*0.4})`;
  ctx.beginPath(); ctx.ellipse(x,y-H*0.5,W*0.14,H*0.14,0,0,Math.PI*2); ctx.fill();
  // Partículas portal
  for(let i=0;i<6;i++){
    const a=(i/6)*Math.PI*2+tick*0.05;
    const pr=W*0.22;
    ctx.fillStyle=`rgba(140,200,255,${0.4+0.2*Math.sin(tick*0.08+i)})`;
    ctx.beginPath(); ctx.arc(x+Math.cos(a)*pr,y-H*0.5+Math.sin(a)*pr*0.5,2*sc,0,Math.PI*2); ctx.fill();
  }

  // Obeliscos en esquinas
  drawSpire(ctx,x-W*0.45,y-H*0.95,H*0.5,W*0.1,'rgb(30,42,88)');
  drawOrb(ctx,x-W*0.45,y-H*1.43,5*sc,'rgb(100,160,255)');
  drawSpire(ctx,x+W*0.45,y-H*0.95,H*0.5,W*0.1,'rgb(26,38,80)');
  drawOrb(ctx,x+W*0.45,y-H*1.43,5*sc,'rgb(100,160,255)');
}

function artHouse(ctx, x, y, lvl) {
  const sc = 0.58 + Math.min(lvl,38)*0.004;
  const W=58*sc, H=50*sc;

  // Base
  isoArt(ctx,x,y,W*1.05,H*0.1,'rgb(30,20,10)','rgb(18,12,5)','rgb(24,16,8)',{stone:false});
  // Paredes
  isoArt(ctx,x,y-H*0.08,W,H,'rgb(58,42,22)','rgb(38,26,12)','rgb(48,34,18)',{stone:true,gold:0.06});
  // Techo
  ctx.fillStyle='rgb(38,26,12)';
  ctx.beginPath(); ctx.moveTo(x-W/2,y-H*1.05); ctx.lineTo(x,y-H*1.22); ctx.lineTo(x+W/2,y-H*1.05); ctx.closePath(); ctx.fill();
  ctx.fillStyle='rgb(28,18,8)';
  ctx.beginPath(); ctx.moveTo(x-W/2,y-H*1.05); ctx.lineTo(x,y-H*1.22); ctx.lineTo(x,y-H*1.05); ctx.closePath(); ctx.fill();
  // Tejas
  ctx.strokeStyle='rgba(0,0,0,0.2)'; ctx.lineWidth=0.8;
  for(let i=1;i<5;i++){ctx.beginPath();ctx.moveTo(x-W/2*((5-i)/5),y-H*1.05-(y-H*1.22-y+H*1.05)*i/5);ctx.lineTo(x-(-W/2*((5-i)/5)),y-H*1.05-(y-H*1.22-y+H*1.05)*i/5);ctx.stroke();}

  // Ventanas con luz cálida
  const wA=0.45+0.2*Math.sin(tick*0.05);
  isoWindow(ctx,x-W*0.28,y-H*0.52,W*0.18,H*0.2,'rgb(255,185,70)',wA);
  isoWindow(ctx,x+W*0.1,y-H*0.52,W*0.18,H*0.2,'rgb(255,185,70)',wA*0.9);
  // Glow ventanas en suelo
  ctx.fillStyle=`rgba(255,160,50,${wA*0.08})`;
  ctx.beginPath(); ctx.ellipse(x-W*0.18,y-H*0.06,14*sc,5*sc,0,0,Math.PI*2); ctx.fill();

  // Puerta arqueada
  ctx.fillStyle='rgba(0,0,0,0.85)';
  ctx.beginPath(); ctx.arc(x,y-H*0.2,W*0.1,Math.PI,0); ctx.rect(x-W*0.1,y-H*0.2,W*0.2,H*0.22); ctx.fill();

  // Chimenea
  isoArt(ctx,x+W*0.28,y-H*1.05,W*0.13,H*0.25,'rgb(40,28,14)','rgb(26,18,8)','rgb(34,22,10)',{stone:false});
  // Humo
  for(let i=0;i<4;i++){
    const hx=x+W*0.28+(Math.sin(tick*0.03+i*1.5)*4*sc);
    const hy=y-H*1.28-i*12*sc;
    ctx.fillStyle=`rgba(180,160,140,${0.16-i*0.03})`;
    ctx.beginPath(); ctx.arc(hx,hy,5*sc+i*3*sc,0,Math.PI*2); ctx.fill();
  }

  // Macetero con planta mágica
  ctx.fillStyle='rgb(35,22,8)'; ctx.beginPath(); ctx.ellipse(x-W*0.38,y-H*0.04,6*sc,3*sc,0,0,Math.PI*2); ctx.fill();
  ctx.strokeStyle=`rgba(60,180,140,0.7)`; ctx.lineWidth=1.5;
  for(let i=0;i<3;i++){ctx.beginPath();ctx.moveTo(x-W*0.38,y-H*0.04);ctx.quadraticCurveTo(x-W*0.38+(i-1)*6*sc,y-H*0.18,x-W*0.38+(i-1)*4*sc,y-H*0.25);ctx.stroke();}
}

function artBarracks(ctx, x, y, lvl) {
  const sc = 0.62 + Math.min(lvl,6)*0.015;
  const W=78*sc, H=68*sc;

  // Base
  isoArt(ctx,x,y,W*1.05,H*0.1,'rgb(16,10,10)','rgb(10,6,6)','rgb(14,8,8)',{stone:false});
  // Alas
  isoArt(ctx,x-W*0.42,y-H*0.08,W*0.35,H*0.7,'rgb(24,14,14)','rgb(14,8,8)','rgb(20,12,12)',{stone:true});
  isoArt(ctx,x+W*0.42,y-H*0.08,W*0.35,H*0.7,'rgb(22,13,13)','rgb(13,7,7)','rgb(18,11,11)',{stone:true});
  // Cuerpo central
  isoArt(ctx,x,y-H*0.08,W*0.55,H*0.85,'rgb(28,16,16)','rgb(17,9,9)','rgb(23,13,13)',{stone:true,gold:0.1});
  // Techo central
  ctx.fillStyle='rgb(18,10,10)';
  ctx.beginPath(); ctx.moveTo(x-W*0.28,y-H*0.92); ctx.lineTo(x,y-H*1.1); ctx.lineTo(x+W*0.28,y-H*0.92); ctx.closePath(); ctx.fill();
  ctx.fillStyle='rgb(13,7,7)';
  ctx.beginPath(); ctx.moveTo(x-W*0.28,y-H*0.92); ctx.lineTo(x,y-H*1.1); ctx.lineTo(x,y-H*0.92); ctx.closePath(); ctx.fill();

  // Mástil + bandera de guerra
  ctx.strokeStyle='rgb(50,35,35)'; ctx.lineWidth=1.5;
  ctx.beginPath(); ctx.moveTo(x,y-H*1.1); ctx.lineTo(x,y-H*1.32); ctx.stroke();
  const bw=Math.sin(tick*0.06)*4*sc;
  ctx.fillStyle='rgb(140,20,20)';
  ctx.beginPath(); ctx.moveTo(x,y-H*1.32); ctx.lineTo(x+18*sc+bw,y-H*1.26); ctx.lineTo(x+16*sc+bw*0.7,y-H*1.22); ctx.lineTo(x,y-H*1.22); ctx.closePath(); ctx.fill();
  // Cruz en bandera
  ctx.strokeStyle='rgba(255,180,180,0.6)'; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(x+8*sc,y-H*1.32); ctx.lineTo(x+8*sc,y-H*1.22); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x+4*sc,y-H*1.27); ctx.lineTo(x+13*sc,y-H*1.27); ctx.stroke();

  // Ventanas militares estrechas con brasa
  const wA=0.3+0.12*Math.sin(tick*0.05);
  for(const [wx,wy] of [[x-W*0.2,y-H*0.48],[x,y-H*0.48],[x+W*0.2,y-H*0.48]]){
    isoWindow(ctx,wx,wy,W*0.1,H*0.15,'rgb(220,90,30)',wA);
  }
  for(const [wx,wy] of [[x-W*0.56,y-H*0.32],[x-W*0.56,y-H*0.48],[x+W*0.35,y-H*0.32],[x+W*0.35,y-H*0.48]]){
    isoWindow(ctx,wx,wy,W*0.09,H*0.13,'rgb(200,70,20)',wA*0.8);
  }

  // Lanzas
  ctx.strokeStyle='rgba(160,140,80,0.6)'; ctx.lineWidth=1.2;
  for(const [lx,ly] of [[x-W*0.1,y],[x-W*0.02,y],[x+W*0.06,y],[x+W*0.14,y]]){
    ctx.beginPath(); ctx.moveTo(lx,ly); ctx.lineTo(lx-2*sc,ly-22*sc); ctx.stroke();
    ctx.fillStyle='rgba(200,180,60,0.7)'; ctx.beginPath(); ctx.moveTo(lx-2*sc,ly-22*sc); ctx.lineTo(lx,ly-27*sc); ctx.lineTo(lx+2*sc,ly-22*sc); ctx.closePath(); ctx.fill();
  }

  // Escudo en pared
  ctx.fillStyle='rgba(120,30,30,0.6)'; ctx.strokeStyle='rgba(180,80,80,0.4)'; ctx.lineWidth=0.8;
  ctx.beginPath(); ctx.arc(x,y-H*0.62,10*sc,0,Math.PI*2); ctx.fill(); ctx.stroke();
}

function artForge(ctx, x, y, lvl) {
  const sc = 0.62 + Math.min(lvl,4)*0.02;
  const W=70*sc, H=60*sc;

  // Glow de fuego general
  const fGlow=ctx.createRadialGradient(x-W*0.15,y-H*0.3,4,x-W*0.15,y-H*0.3,W*0.5);
  fGlow.addColorStop(0,`rgba(255,100,0,${0.18+0.08*Math.sin(tick*0.1)})`); fGlow.addColorStop(1,'rgba(255,60,0,0)');
  ctx.fillStyle=fGlow; ctx.fillRect(x-W,y-H*1.5,W*2,H*1.8);

  // Base + cuerpo
  isoArt(ctx,x,y,W*1.05,H*0.12,'rgb(32,14,6)','rgb(20,8,3)','rgb(26,10,4)',{stone:false});
  isoArt(ctx,x,y-H*0.1,W,H,'rgb(48,22,8)','rgb(30,12,4)','rgb(38,16,6)',{stone:true,gold:0.05});

  // Chimeneas con volumen
  isoArt(ctx,x+W*0.22,y-H*0.88,W*0.2,H*0.95,'rgb(36,14,4)','rgb(22,8,2)','rgb(30,10,3)',{stone:true});
  isoArt(ctx,x+W*0.06,y-H*0.76,W*0.15,H*0.72,'rgb(32,12,4)','rgb(20,7,2)','rgb(26,9,3)',{stone:true});

  // Fuego en chimeneas
  for(const [fx,fy,fh] of [[x+W*0.22,y-H*1.8,H*0.4],[x+W*0.06,y-H*1.46,H*0.35]]){
    for(let i=0;i<5;i++){
      const fa=0.6+0.4*Math.sin(tick*0.12+i);
      const ffl=fh*(0.5+0.4*Math.sin(tick*0.1+i));
      const ffg=ctx.createLinearGradient(fx+i*2*sc,fy,fx+i*2*sc,fy-ffl);
      ffg.addColorStop(0,`rgba(255,${80+i*20},0,${fa})`); ffg.addColorStop(1,'rgba(255,200,0,0)');
      ctx.fillStyle=ffg; ctx.beginPath(); ctx.ellipse(fx+(i-2)*2.5*sc,fy-ffl/2,2.5*sc,ffl/2,0,0,Math.PI*2); ctx.fill();
    }
    // Humo
    for(let i=0;i<4;i++){
      ctx.fillStyle=`rgba(160,130,110,${0.2-i*0.04})`;
      ctx.beginPath(); ctx.arc(fx+Math.sin(tick*0.02+i)*4*sc,fy-ffl-i*14*sc,6*sc+i*4*sc,0,Math.PI*2); ctx.fill();
    }
  }

  // Puerta forja con fuego interior
  ctx.fillStyle='rgba(0,0,0,0.88)';
  ctx.beginPath(); ctx.arc(x-W*0.14,y-H*0.35,W*0.15,Math.PI,0); ctx.rect(x-W*0.14-W*0.15,y-H*0.35,W*0.3,H*0.36); ctx.fill();
  // Lava interior
  const fA=0.7+0.25*Math.sin(tick*0.12);
  const fg=ctx.createRadialGradient(x-W*0.14,y-H*0.22,2,x-W*0.14,y-H*0.22,W*0.14);
  fg.addColorStop(0,`rgba(255,160,0,${fA})`); fg.addColorStop(0.5,`rgba(255,60,0,${fA*0.6})`); fg.addColorStop(1,'rgba(200,20,0,0)');
  ctx.fillStyle=fg; ctx.fillRect(x-W*0.28,y-H*0.35,W*0.28,H*0.36);

  // Yunque
  ctx.fillStyle='rgb(28,28,28)';
  ctx.beginPath(); ctx.moveTo(x+W*0.2,y-H*0.08); ctx.lineTo(x+W*0.36,y-H*0.08); ctx.lineTo(x+W*0.35,y-H*0.18); ctx.lineTo(x+W*0.21,y-H*0.18); ctx.closePath(); ctx.fill();
  ctx.fillStyle='rgb(35,35,35)';
  ctx.fillRect(x+W*0.25,y-H*0.18,W*0.07,H*0.12);

  // Chispas
  for(let i=0;i<8;i++){
    const sa=(tick*0.15+i*0.8)%(Math.PI*2);
    const sd=18*sc*((tick*0.1+i)%1);
    const sx=x-W*0.14+Math.cos(sa)*sd, sy=y-H*0.32-Math.sin(Math.abs(sa))*sd;
    ctx.fillStyle=`rgba(255,${150+Math.floor(i*10)},0,${1-(tick*0.1+i)%1})`;
    ctx.beginPath(); ctx.arc(sx,sy,1.2*sc,0,Math.PI*2); ctx.fill();
  }
}

function artHideout(ctx, x, y, lvl) {
  const sc = 0.6 + Math.min(lvl,1)*0.1;
  const W=62*sc, H=32*sc;

  // Tierra/suelo circundante
  ctx.fillStyle='rgba(18,22,12,0.8)';
  ctx.beginPath(); ctx.ellipse(x,y-H*0.1,W*0.72,H*0.45,0,0,Math.PI*2); ctx.fill();

  // Estructura semi-enterrada
  isoArt(ctx,x,y,W,H,'rgb(24,30,16)','rgb(14,18,8)','rgb(20,25,12)',{stone:true});

  // Techo cubierto de tierra y hierba
  ctx.fillStyle='rgb(20,26,14)';
  ctx.beginPath(); ctx.moveTo(x-W/2,y-H*0.98); ctx.lineTo(x,y-H*1.18); ctx.lineTo(x+W/2,y-H*0.98); ctx.closePath(); ctx.fill();
  ctx.fillStyle='rgb(15,20,10)';
  ctx.beginPath(); ctx.moveTo(x-W/2,y-H*0.98); ctx.lineTo(x,y-H*1.18); ctx.lineTo(x,y-H*0.98); ctx.closePath(); ctx.fill();

  // Hierba y musgo
  ctx.strokeStyle='rgba(50,120,40,0.7)'; ctx.lineWidth=1.5;
  const grassPos=[-W*0.38,-W*0.22,-W*0.06,W*0.1,W*0.26,W*0.4];
  grassPos.forEach((gx,i)=>{
    const h2=6*sc+Math.sin(i*1.3)*3*sc;
    ctx.beginPath(); ctx.moveTo(x+gx,y-H*1.0); ctx.quadraticCurveTo(x+gx+Math.sin(i)*3*sc,y-H*1.0-h2/2,x+gx+Math.sin(i*0.7)*2*sc,y-H*1.0-h2); ctx.stroke();
  });

  // Trampilla oxidada
  ctx.fillStyle='rgba(0,0,0,0.7)';
  ctx.beginPath(); ctx.ellipse(x,y-H*0.62,W*0.24,H*0.28,0,0,Math.PI*2); ctx.fill();
  // Plancha oxidada
  const tg=ctx.createLinearGradient(x-W*0.2,y-H*0.62,x+W*0.2,y-H*0.62);
  tg.addColorStop(0,'rgb(60,30,10)'); tg.addColorStop(0.5,'rgb(80,40,12)'); tg.addColorStop(1,'rgb(55,28,9)');
  ctx.fillStyle=tg;
  ctx.beginPath(); ctx.ellipse(x,y-H*0.64,W*0.2,H*0.22,0,0,Math.PI*2); ctx.fill();
  // Bisagras y cerradura oxidada
  ctx.fillStyle='rgb(45,25,8)';
  ctx.fillRect(x-W*0.16,y-H*0.67,W*0.08,H*0.05);
  ctx.fillRect(x+W*0.08,y-H*0.67,W*0.08,H*0.05);
  ctx.beginPath(); ctx.arc(x,y-H*0.64,3.5*sc,0,Math.PI*2); ctx.fill();

  // Luz bioluminiscente filtrándose
  const lA=0.15+0.08*Math.sin(tick*0.06);
  ctx.fillStyle=`rgba(50,180,80,${lA})`;
  ctx.beginPath(); ctx.ellipse(x,y-H*0.64,W*0.1,H*0.1,0,0,Math.PI*2); ctx.fill();

  // Raíces
  ctx.strokeStyle='rgba(40,28,10,0.5)'; ctx.lineWidth=1.5;
  ctx.beginPath(); ctx.moveTo(x-W*0.5,y-H*0.5); ctx.quadraticCurveTo(x-W*0.3,y,x-W*0.15,y); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x+W*0.5,y-H*0.5); ctx.quadraticCurveTo(x+W*0.3,y,x+W*0.15,y); ctx.stroke();
}"""

c = src.count(OLD_BLD)
if c != 1: print(f"ERROR: drawBuilding ancla encontrada {c} veces. Abortando."); sys.exit(1)
src = src.replace(OLD_BLD, NEW_BLD)
print("OK: funciones artísticas Canvas 2D instaladas")

TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO — city.js actualizado.")
print()
print("Para verificar:")
print("  Ctrl+C → run.bat → Ctrl+Shift+R en http://127.0.0.1:8000/game")
