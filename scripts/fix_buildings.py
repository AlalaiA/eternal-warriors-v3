from pathlib import Path

path = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = path.read_text(encoding="utf-8")

# Reemplazar todo el bloque de edificios desde drawCityHall hasta drawBarracks
OLD = """// ─── EDIFICIOS ───────────────────────────────────────────────────────────────

function drawCityHall(ctx, x, y, sc, lvl) {"""

# Buscar el final del bloque — después de drawBarracks
end_marker = """function drawParticles(ctx, cx, cy, c) {"""

idx_start = src.find(OLD)
idx_end   = src.find(end_marker)

if idx_start == -1:
    print("ERROR: no encontrado inicio bloque edificios"); exit(1)
if idx_end == -1:
    print("ERROR: no encontrado fin bloque edificios"); exit(1)

BUILDINGS = r"""
// ═══════════════════════════════════════════════════════════════
// EDIFICIOS — Arte isométrico detallado
// ═══════════════════════════════════════════════════════════════

function drawCityHall(ctx, x, y, sc, lvl) {
  const w=72*sc, h=(55+lvl*1.8)*sc;
  // Plataforma base
  isoBox(ctx,x,y,w*1.15,h*0.18,'#1e2d4a','#141e32','#283a5e');
  // Alas laterales
  isoBox(ctx,x-w*0.58,y-h*0.12,w*0.42,h*0.72,'#223060','#16204a','#2c3d78');
  isoBox(ctx,x+w*0.58,y-h*0.12,w*0.42,h*0.72,'#223060','#16204a','#2c3d78');
  // Cuerpo central
  isoBox(ctx,x,y-h*0.08,w*0.58,h*0.9,'#2e4278','#1e2d5c','#3e559a');
  // Ventanas alas
  for(let i=0;i<3;i++){
    const wy=y-h*(0.25+i*0.18);
    const wc=`rgba(120,180,255,${0.35+0.15*Math.sin(tick*0.04+i)})`;
    ctx.fillStyle=wc; ctx.fillRect(x-w*0.7,wy,7*sc,5*sc);
    ctx.fillStyle=wc; ctx.fillRect(x+w*0.4,wy,7*sc,5*sc);
  }
  // Ventanas arco central
  for(let i=0;i<4;i++){
    const wx=x-w*0.22+i*w*0.15, wy=y-h*0.5;
    const wc=`rgba(150,210,255,${0.5+0.2*Math.sin(tick*0.05+i)})`;
    ctx.fillStyle='rgba(0,0,0,0.5)'; ctx.fillRect(wx-4*sc,wy-8*sc,7*sc,10*sc);
    ctx.fillStyle=wc; ctx.fillRect(wx-3*sc,wy-7*sc,5*sc,8*sc);
    // Arco
    ctx.fillStyle=wc;
    ctx.beginPath(); ctx.arc(wx,wy-7*sc,2.5*sc,Math.PI,0); ctx.fill();
  }
  // Pináculos en alas
  [-w*0.58,w*0.58].forEach(ox=>{
    ctx.fillStyle='#3a5090';
    ctx.beginPath(); ctx.moveTo(x+ox,y-h*0.87); ctx.lineTo(x+ox+5*sc,y-h*0.72); ctx.lineTo(x+ox-5*sc,y-h*0.72); ctx.closePath(); ctx.fill();
    glow(ctx,x+ox,y-h*0.88,8*sc,'rgb(80,130,220)');
  });
  // Torre central con punta
  isoBox(ctx,x,y-h*0.85,w*0.22,h*0.3,'#3a5898','#263d7a','#4a68b0');
  ctx.fillStyle='#4a70c0';
  ctx.beginPath(); ctx.moveTo(x,y-h*1.22); ctx.lineTo(x+6*sc,y-h*1.0); ctx.lineTo(x-6*sc,y-h*1.0); ctx.closePath(); ctx.fill();
  // Orbe cima
  glow(ctx,x,y-h*1.23,20*sc,'rgb(100,160,255)');
  const orbPulse=0.85+0.15*Math.sin(tick*0.07);
  ctx.fillStyle=`rgba(180,220,255,${orbPulse})`;
  ctx.beginPath(); ctx.arc(x,y-h*1.23,4*sc,0,Math.PI*2); ctx.fill();
  // Haz de luz hacia arriba
  const beamAlpha=0.04+0.03*Math.sin(tick*0.05);
  const beam=ctx.createLinearGradient(x,y-h*1.2,x,y-h*2.2);
  beam.addColorStop(0,`rgba(150,200,255,${beamAlpha*3})`);
  beam.addColorStop(1,'rgba(150,200,255,0)');
  ctx.fillStyle=beam; ctx.fillRect(x-6*sc,y-h*2.2,12*sc,h);
  // Bandera
  ctx.strokeStyle='#5a7ab0'; ctx.lineWidth=1.2;
  ctx.beginPath(); ctx.moveTo(x-w*0.58,y-h*0.78); ctx.lineTo(x-w*0.58,y-h*0.78-16*sc); ctx.stroke();
  ctx.fillStyle='#3a5a90';
  ctx.fillRect(x-w*0.58,y-h*0.78-16*sc,11*sc,7*sc);
  ctx.fillStyle='rgba(200,220,255,0.5)';
  ctx.fillRect(x-w*0.58+1*sc,y-h*0.78-15*sc,4*sc,5*sc);
}

function drawHouse(ctx, x, y, sc, lvl) {
  const w=50*sc, h=(26+lvl*0.5)*sc;
  const roofH=18*sc;
  // Sombra base
  ctx.fillStyle='rgba(0,0,0,0.2)';
  ctx.beginPath(); ctx.ellipse(x,y+3,w*0.6,w*0.18,0,0,Math.PI*2); ctx.fill();
  // Paredes
  isoBox(ctx,x,y,w,h,'#5a4428','#3c2c18','#726038');
  // Techo a dos aguas con tejas
  ctx.fillStyle='#4a3420';
  ctx.beginPath(); ctx.moveTo(x,y-h-roofH); ctx.lineTo(x+w*0.58,y-h+w*0.14); ctx.lineTo(x-w*0.58,y-h+w*0.14); ctx.closePath(); ctx.fill();
  ctx.strokeStyle='#2e1e10'; ctx.lineWidth=0.8; ctx.stroke();
  // Líneas de tejas
  ctx.strokeStyle='rgba(0,0,0,0.25)'; ctx.lineWidth=0.6;
  for(let i=1;i<5;i++){
    const t=i/5;
    ctx.beginPath();
    ctx.moveTo(x-w*0.58*t,y-h+w*0.14*(1-t));
    ctx.lineTo(x+w*0.58*t,y-h+w*0.14*(1-t));
    ctx.stroke();
  }
  // Ventanas con luz cálida
  const wc=`rgba(255,190,80,${0.45+0.15*Math.sin(tick*0.05)})`;
  const ws=8*sc;
  // Ventana izq
  ctx.fillStyle='rgba(0,0,0,0.6)'; ctx.fillRect(x-w*0.28,y-h*0.58,ws,ws*1.1);
  ctx.fillStyle=wc; ctx.fillRect(x-w*0.27,y-h*0.57,ws-2,ws*1.0);
  ctx.strokeStyle='#3c2810'; ctx.lineWidth=0.8; ctx.strokeRect(x-w*0.28,y-h*0.58,ws,ws*1.1);
  // Ventana der
  ctx.fillStyle='rgba(0,0,0,0.6)'; ctx.fillRect(x+w*0.1,y-h*0.58,ws,ws*1.1);
  ctx.fillStyle=wc; ctx.fillRect(x+w*0.11,y-h*0.57,ws-2,ws*1.0);
  ctx.strokeStyle='#3c2810'; ctx.lineWidth=0.8; ctx.strokeRect(x+w*0.1,y-h*0.58,ws,ws*1.1);
  // Puerta arqueada
  ctx.fillStyle='#1a0e04';
  ctx.beginPath(); ctx.arc(x,y-h*0.2,6*sc,Math.PI,0); ctx.rect(x-6*sc,y-h*0.2,12*sc,h*0.22); ctx.fill();
  ctx.strokeStyle='#3c2010'; ctx.lineWidth=0.8; ctx.stroke();
  // Luz puerta
  if(lvl>=3){ glow(ctx,x,y-h*0.05,12*sc,'rgb(255,160,40)'); }
  // Chimenea con humo
  isoBox(ctx,x+w*0.3,y-h*0.85,w*0.14,h*0.45,'#4a3820','#342a18','#5a4828');
  if(lvl>=1){
    for(let i=0;i<3;i++){
      const smokeY=y-h*1.0-i*8*sc;
      const smokeAlpha=0.15-i*0.04;
      ctx.fillStyle=`rgba(180,160,140,${smokeAlpha})`;
      ctx.beginPath(); ctx.arc(x+w*0.3+i*2*sc,smokeY,4*sc+i*2*sc,0,Math.PI*2); ctx.fill();
    }
  }
}

function drawWatchtower(ctx, x, y, sc, lvl) {
  const w=30*sc, h=(65+lvl*2)*sc;
  // Base reforzada
  isoBox(ctx,x,y,w*1.5,h*0.22,'#283040','#1a2030','#384050');
  // Fuste de la torre
  isoBox(ctx,x,y-h*0.18,w,h*0.85,'#2e3848','#1e2838','#3e4858');
  // Ménsulas (soporte del balcón)
  ctx.fillStyle='#3a4858';
  ctx.fillRect(x-w*0.7,y-h*0.78,w*1.4,h*0.04);
  // Cuerpo superior (balcón)
  isoBox(ctx,x,y-h*0.82,w*1.2,h*0.2,'#344050','#223040','#445060');
  // Almenas detalladas
  for(let i=-2;i<=2;i++){
    ctx.fillStyle='#405060';
    ctx.fillRect(x+i*5*sc-2*sc,y-h-4*sc,3.5*sc,6*sc);
    // Ranuras
    ctx.fillStyle='rgba(0,0,0,0.4)';
    ctx.fillRect(x+i*5*sc-1*sc,y-h-3*sc,1.5*sc,3*sc);
  }
  // Ventanas de observación con luz
  for(let yy=0.25;yy<0.85;yy+=0.28){
    const wc=`rgba(200,230,255,${0.25+0.15*Math.sin(tick*0.04+yy*10)})`;
    ctx.fillStyle='rgba(0,0,0,0.5)'; ctx.fillRect(x-4*sc,y-h*yy-3*sc,7*sc,8*sc);
    ctx.fillStyle=wc; ctx.fillRect(x-3*sc,y-h*yy-2*sc,5*sc,6*sc);
  }
  // Luz de vigilancia giratoria
  if(lvl>=8){
    const angle=tick*0.04;
    const reach=45*sc;
    const lx=x+Math.cos(angle)*reach, ly=y-h+Math.sin(angle)*8*sc;
    const lg=ctx.createLinearGradient(x,y-h,lx,ly);
    lg.addColorStop(0,'rgba(220,240,255,0.5)');
    lg.addColorStop(0.7,'rgba(220,240,255,0.1)');
    lg.addColorStop(1,'rgba(220,240,255,0)');
    ctx.fillStyle=lg;
    ctx.beginPath(); ctx.moveTo(x,y-h); ctx.lineTo(lx-4,ly-2); ctx.lineTo(lx+4,ly+2); ctx.closePath(); ctx.fill();
    glow(ctx,x,y-h,10*sc,'rgb(200,230,255)');
  }
  // Bandera
  ctx.strokeStyle='#5a6878'; ctx.lineWidth=1.2;
  ctx.beginPath(); ctx.moveTo(x,y-h-2*sc); ctx.lineTo(x,y-h-2*sc-14*sc); ctx.stroke();
  ctx.fillStyle='#405870'; ctx.fillRect(x,y-h-14*sc,9*sc,6*sc);
}

function drawTravelCenter(ctx, x, y, sc, lvl) {
  const w=56*sc, h=(32+lvl*0.8)*sc;
  // Base con escalones
  isoBox(ctx,x,y,w*1.1,h*0.2,'#1e2448','#141830','#283060');
  isoBox(ctx,x,y-h*0.15,w,h*0.35,'#243060','#182048','#304080');
  // Cuerpo principal
  isoBox(ctx,x,y-h*0.4,w*0.85,h*0.7,'#2c3870','#1e2858','#3c4888');
  // Arco portal central
  const archW=16*sc, archH=22*sc;
  ctx.fillStyle='rgba(0,0,0,0.7)';
  ctx.beginPath(); ctx.arc(x,y-h*0.5,archW*0.5,Math.PI,0); ctx.rect(x-archW*0.5,y-h*0.5,archW,archH*0.5); ctx.fill();
  // Energía portal
  const portalAlpha=0.4+0.3*Math.sin(tick*0.08);
  const pg=ctx.createRadialGradient(x,y-h*0.5,2,x,y-h*0.5,archW*0.5);
  pg.addColorStop(0,`rgba(80,140,255,${portalAlpha})`);
  pg.addColorStop(0.6,`rgba(60,100,220,${portalAlpha*0.5})`);
  pg.addColorStop(1,'rgba(60,100,220,0)');
  ctx.fillStyle=pg;
  ctx.beginPath(); ctx.arc(x,y-h*0.5,archW*0.5,Math.PI,0); ctx.fill();
  // Anillo del portal
  ctx.strokeStyle=`rgba(120,180,255,${0.7+0.3*Math.sin(tick*0.09)})`;
  ctx.lineWidth=2*sc;
  ctx.beginPath(); ctx.arc(x,y-h*0.5,archW*0.55,Math.PI,0); ctx.stroke();
  // Runas en pilares
  ctx.fillStyle=`rgba(100,160,255,${0.3+0.15*Math.sin(tick*0.06)})`;
  for(let i=0;i<4;i++){
    ctx.fillRect(x-w*0.38+i*w*0.24,y-h*0.7,4*sc,4*sc);
    ctx.fillRect(x-w*0.35+i*w*0.24,y-h*0.55,3*sc,3*sc);
  }
  // Cristales en esquinas
  [-w*0.45,w*0.45].forEach(ox=>{
    ctx.fillStyle=`rgba(100,160,255,${0.5+0.2*Math.sin(tick*0.07+ox)})`;
    ctx.beginPath(); ctx.moveTo(x+ox,y-h*0.85); ctx.lineTo(x+ox+4*sc,y-h*0.7); ctx.lineTo(x+ox-4*sc,y-h*0.7); ctx.closePath(); ctx.fill();
    glow(ctx,x+ox,y-h*0.85,8*sc,'rgb(80,140,255)');
  });
}

function drawHideout(ctx, x, y, sc, lvl) {
  const w=50*sc, h=(16+lvl*0.4)*sc;
  // Estructura casi enterrada
  isoBox(ctx,x,y,w,h,'#262e1e','#181e10','#32382a');
  // Techo cubierto de tierra
  ctx.fillStyle='#1e2818';
  ctx.beginPath(); ctx.moveTo(x,y-h-6*sc); ctx.lineTo(x+w*0.55,y-h+w*0.1); ctx.lineTo(x-w*0.55,y-h+w*0.1); ctx.closePath(); ctx.fill();
  // Tierra y hierba encima
  for(let i=0;i<8;i++){
    const gx=x-w*0.4+i*w*0.11;
    const gy=y-h-3*sc;
    ctx.fillStyle=`rgba(${30+i*3},${45+i*5},${15},0.6)`;
    ctx.beginPath(); ctx.arc(gx,gy,4*sc+Math.sin(i)*2*sc,0,Math.PI*2); ctx.fill();
  }
  // Trampilla disimulada
  ctx.fillStyle='rgba(0,0,0,0.5)';
  ctx.beginPath(); ctx.ellipse(x,y-h*0.15,8*sc,4*sc,0,0,Math.PI*2); ctx.fill();
  ctx.strokeStyle='#3a3a20'; ctx.lineWidth=1; ctx.stroke();
  // Bisagras
  ctx.fillStyle='#505030';
  ctx.fillRect(x-7*sc,y-h*0.18,3*sc,2*sc);
  ctx.fillRect(x+4*sc,y-h*0.18,3*sc,2*sc);
  // Pequeña ventilación
  if(lvl>=5){
    ctx.fillStyle='rgba(100,120,80,0.4)';
    ctx.fillRect(x+w*0.25,y-h*0.6,5*sc,3*sc);
    ctx.strokeStyle='rgba(80,100,60,0.6)'; ctx.lineWidth=0.5; ctx.stroke();
  }
  // Luz de guardia (mínima, discreta)
  if(lvl>=10){
    ctx.fillStyle=`rgba(180,160,60,${0.1+0.05*Math.sin(tick*0.08)})`;
    ctx.beginPath(); ctx.arc(x,y-h*0.15,3*sc,0,Math.PI*2); ctx.fill();
  }
}

function drawWarehouse(ctx, x, y, sc, lvl) {
  const w=68*sc, h=(28+lvl*0.6)*sc;
  // Base
  isoBox(ctx,x,y,w*1.05,h*0.18,'#3a2010','#281408','#503020');
  // Estructura principal ancha
  isoBox(ctx,x,y-h*0.12,w,h,'#503818','#382808','#6a4828');
  // Techo a dos aguas amplio
  ctx.fillStyle='#3a2810';
  ctx.beginPath(); ctx.moveTo(x,y-h-12*sc); ctx.lineTo(x+w*0.58,y-h+w*0.12); ctx.lineTo(x-w*0.58,y-h+w*0.12); ctx.closePath(); ctx.fill();
  ctx.strokeStyle='rgba(0,0,0,0.4)'; ctx.lineWidth=0.8; ctx.stroke();
  // Vigas del techo
  ctx.strokeStyle='rgba(0,0,0,0.25)'; ctx.lineWidth=0.7;
  for(let i=1;i<5;i++){
    const t=i/5;
    ctx.beginPath(); ctx.moveTo(x-w*0.55*t,y-h+w*0.1*(1-t)); ctx.lineTo(x+w*0.55*t,y-h+w*0.1*(1-t)); ctx.stroke();
  }
  // Puertas dobles grandes
  ctx.fillStyle='#1a0e06';
  ctx.fillRect(x-14*sc,y-h*0.45,12*sc,h*0.45);
  ctx.fillRect(x+2*sc,y-h*0.45,12*sc,h*0.45);
  // Marco puerta
  ctx.strokeStyle='#4a3018'; ctx.lineWidth=1;
  ctx.strokeRect(x-14*sc,y-h*0.45,12*sc,h*0.45);
  ctx.strokeRect(x+2*sc,y-h*0.45,12*sc,h*0.45);
  // Bisagras y cerrojo
  ctx.fillStyle='#606040';
  ctx.fillRect(x-13*sc,y-h*0.4,2*sc,2*sc);
  ctx.fillRect(x-13*sc,y-h*0.28,2*sc,2*sc);
  ctx.fillRect(x+3*sc,y-h*0.4,2*sc,2*sc);
  ctx.fillRect(x+3*sc,y-h*0.28,2*sc,2*sc);
  // Ventanas de almacén
  for(let i=0;i<2;i++){
    const wx=x-w*0.38+i*w*0.7;
    ctx.fillStyle='rgba(0,0,0,0.5)'; ctx.fillRect(wx,y-h*0.75,10*sc,7*sc);
    ctx.fillStyle=`rgba(200,160,80,${0.2+0.1*Math.sin(tick*0.04+i)})`; ctx.fillRect(wx+1,y-h*0.74,8*sc,5*sc);
    ctx.strokeStyle='#4a3018'; ctx.lineWidth=0.6; ctx.strokeRect(wx,y-h*0.75,10*sc,7*sc);
  }
  if(lvl>=10){ glow(ctx,x,y-h*0.25,20*sc,'rgb(180,120,40)'); }
}

function drawSanctuary(ctx, x, y, sc, lvl) {
  const w=52*sc, h=(38+lvl*1.2)*sc;
  // Base octogonal
  isoBox(ctx,x,y,w*1.1,h*0.18,'#300e50','#200838','#401868');
  // Columnas base
  for(let i=-1;i<=1;i++){
    isoBox(ctx,x+i*w*0.38,y-h*0.12,w*0.12,h*0.45,'#401068','#280848','#501880');
  }
  // Cuerpo principal
  isoBox(ctx,x,y-h*0.35,w*0.78,h*0.6,'#481278','#300c58','#582090');
  // Cúpula principal
  const domeY=y-h*0.95;
  ctx.fillStyle='#5820a0';
  ctx.beginPath(); ctx.ellipse(x,domeY,w*0.42,h*0.45,0,Math.PI,0); ctx.fill();
  // Cúpula interior brillante
  ctx.fillStyle='#7030c0';
  ctx.beginPath(); ctx.ellipse(x,domeY,w*0.28,h*0.32,0,Math.PI,0); ctx.fill();
  // Nervios de la cúpula
  ctx.strokeStyle='rgba(180,80,255,0.3)'; ctx.lineWidth=1;
  for(let i=0;i<6;i++){
    const angle=(i/6)*Math.PI;
    ctx.beginPath(); ctx.moveTo(x,domeY); ctx.lineTo(x+Math.cos(angle)*w*0.42,domeY-Math.sin(angle)*h*0.45*0.5); ctx.stroke();
  }
  // Ventana circular
  const winAlpha=0.5+0.3*Math.sin(tick*0.07);
  glow(ctx,x,domeY-h*0.15,15*sc,'rgb(180,80,255)');
  ctx.fillStyle=`rgba(200,100,255,${winAlpha})`;
  ctx.beginPath(); ctx.arc(x,domeY-h*0.15,5*sc,0,Math.PI*2); ctx.fill();
  // Esferas de maná orbitando
  const orbCount=Math.min(8,Math.floor(2+lvl*0.15));
  for(let i=0;i<orbCount;i++){
    const angle=(i/orbCount)*Math.PI*2+tick*0.025;
    const rx=w*0.45, ry=h*0.2;
    const px=x+Math.cos(angle)*rx, py=domeY+Math.sin(angle)*ry;
    const alpha=0.5+0.3*Math.sin(tick*0.06+i*1.2);
    glow(ctx,px,py,6*sc,'rgb(160,60,255)');
    ctx.fillStyle=`rgba(200,120,255,${alpha})`;
    ctx.beginPath(); ctx.arc(px,py,2.5*sc,0,Math.PI*2); ctx.fill();
  }
  // Punta y cristal cima
  ctx.fillStyle='#8040d0';
  ctx.beginPath(); ctx.moveTo(x,domeY-h*0.55); ctx.lineTo(x+5*sc,domeY-h*0.4); ctx.lineTo(x-5*sc,domeY-h*0.4); ctx.closePath(); ctx.fill();
  glow(ctx,x,domeY-h*0.55,18*sc,'rgb(200,80,255)');
  ctx.fillStyle=`rgba(230,150,255,${0.8+0.2*Math.sin(tick*0.09)})`;
  ctx.beginPath(); ctx.arc(x,domeY-h*0.55,4*sc,0,Math.PI*2); ctx.fill();
}

function drawUniversity(ctx, x, y, sc, lvl) {
  const w=60*sc, h=(40+lvl)*sc;
  // Base con escalones
  isoBox(ctx,x,y,w*1.1,h*0.15,'#162838','#0e1c28','#203848');
  isoBox(ctx,x,y-h*0.12,w,h*0.28,'#1a3048','#0e2030','#284060');
  // Cuerpo principal (biblioteca)
  isoBox(ctx,x,y-h*0.35,w*0.9,h*0.65,'#1e3858','#122840','#2c4870');
  // Torre de estudio lateral
  isoBox(ctx,x-w*0.38,y-h*0.2,w*0.32,h*0.95,'#162e48','#0e1e30','#243e60');
  // Arcos góticos torre
  for(let i=0;i<4;i++){
    const ay=y-h*(0.3+i*0.18);
    ctx.strokeStyle=`rgba(120,180,220,${0.3+0.1*Math.sin(tick*0.04+i)})`;
    ctx.lineWidth=1.5*sc;
    ctx.beginPath(); ctx.arc(x-w*0.38,ay,5*sc,Math.PI,0); ctx.stroke();
    const wc=`rgba(255,210,120,${0.3+0.12*Math.sin(tick*0.04+i*0.8)})`;
    ctx.fillStyle=wc; ctx.fillRect(x-w*0.38-3*sc,ay-4*sc,6*sc,6*sc);
  }
  // Contrafuertes
  ctx.fillStyle='#182840';
  for(let i=0;i<3;i++){
    ctx.fillRect(x+w*0.1+i*w*0.15,y-h*(0.3+i*0.05),5*sc,h*(0.3+i*0.05));
  }
  // Ventanas aula principal
  for(let i=0;i<3;i++){
    const wx=x-w*0.2+i*w*0.22;
    ctx.fillStyle='rgba(0,0,0,0.5)'; ctx.fillRect(wx-5*sc,y-h*0.6,9*sc,11*sc);
    const wc=`rgba(255,200,100,${0.3+0.1*Math.sin(tick*0.03+i)})`;
    ctx.fillStyle=wc; ctx.fillRect(wx-4*sc,y-h*0.59,7*sc,9*sc);
    // Parteluz
    ctx.strokeStyle='rgba(0,0,0,0.4)'; ctx.lineWidth=0.5;
    ctx.beginPath(); ctx.moveTo(wx,y-h*0.59); ctx.lineTo(wx,y-h*0.59+9*sc); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(wx-4*sc,y-h*0.59+4*sc); ctx.lineTo(wx+3*sc,y-h*0.59+4*sc); ctx.stroke();
  }
  // Veleta
  ctx.strokeStyle='#5a7a9a'; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(x-w*0.38,y-h*1.05); ctx.lineTo(x-w*0.38,y-h*1.05-12*sc); ctx.stroke();
  const vAngle=tick*0.05;
  ctx.fillStyle='#4a6a8a';
  ctx.beginPath(); ctx.moveTo(x-w*0.38+Math.cos(vAngle)*8*sc,y-h*1.05-6*sc+Math.sin(vAngle)*2*sc);
  ctx.lineTo(x-w*0.38+Math.cos(vAngle+Math.PI)*8*sc,y-h*1.05-6*sc+Math.sin(vAngle+Math.PI)*2*sc);
  ctx.lineTo(x-w*0.38,y-h*1.05-6*sc); ctx.closePath(); ctx.fill();
}

function drawForge(ctx, x, y, sc, lvl) {
  const w=54*sc, h=(28+lvl*0.7)*sc;
  // Base
  isoBox(ctx,x,y,w*1.08,h*0.2,'#381408','#280e04','#502010');
  // Estructura principal
  isoBox(ctx,x,y-h*0.15,w,h,'#502010','#380e06','#703020');
  // Chimenea principal
  isoBox(ctx,x+w*0.28,y-h*0.65,w*0.22,h*0.65,'#401808','#2c1004','#602018');
  // Chimenea secundaria
  isoBox(ctx,x+w*0.08,y-h*0.55,w*0.14,h*0.45,'#381408','#280e04','#502010');
  // Humo animado chimeneas
  [[x+w*0.28,y-h*1.28],[x+w*0.08,y-h*0.98]].forEach(([cx,cy],ci)=>{
    for(let i=0;i<5;i++){
      const drift=Math.sin(tick*0.04+i+ci)*4*sc;
      const sy=cy-i*7*sc;
      const alpha=0.18-i*0.03;
      ctx.fillStyle=`rgba(160,140,120,${alpha})`;
      ctx.beginPath(); ctx.arc(cx+drift,sy,5*sc+i*2*sc,0,Math.PI*2); ctx.fill();
    }
  });
  // Puerta de la forja — fuego interior
  ctx.fillStyle='#0a0402';
  ctx.beginPath(); ctx.arc(x-w*0.15,y-h*0.28,9*sc,Math.PI,0); ctx.rect(x-w*0.15-9*sc,y-h*0.28,18*sc,10*sc); ctx.fill();
  // Llamas
  const fireIntensity=0.6+0.4*Math.sin(tick*0.12);
  glow(ctx,x-w*0.15,y-h*0.25,16*sc,'rgb(255,120,0)');
  for(let i=0;i<5;i++){
    const fx=x-w*0.15+(i-2)*3*sc;
    const fh=6*sc+Math.sin(tick*0.1+i)*3*sc;
    const fg=ctx.createLinearGradient(fx,y-h*0.18,fx,y-h*0.18-fh);
    fg.addColorStop(0,`rgba(255,${60+i*20},0,${fireIntensity})`);
    fg.addColorStop(0.5,`rgba(255,${100+i*15},0,${fireIntensity*0.7})`);
    fg.addColorStop(1,'rgba(255,200,0,0)');
    ctx.fillStyle=fg;
    ctx.beginPath(); ctx.ellipse(fx,y-h*0.18-fh/2,2*sc,fh/2,0,0,Math.PI*2); ctx.fill();
  }
  // Yunque
  ctx.fillStyle='#303030';
  ctx.beginPath();
  ctx.moveTo(x+w*0.1,y-h*0.05);
  ctx.lineTo(x+w*0.3,y-h*0.05);
  ctx.lineTo(x+w*0.28,y-h*0.1);
  ctx.lineTo(x+w*0.12,y-h*0.1);
  ctx.closePath(); ctx.fill();
  ctx.fillRect(x+w*0.16,y-h*0.1,w*0.08,h*0.08);
  // Chispas
  if(lvl>=3){
    for(let i=0;i<4;i++){
      if(Math.sin(tick*0.15+i*1.3)>0.6){
        const sx=x-w*0.1+(i-2)*8*sc;
        const sy=y-h*0.3-Math.random()*10*sc;
        ctx.fillStyle=`rgba(255,${150+Math.random()*100},0,0.8)`;
        ctx.beginPath(); ctx.arc(sx,sy,1.5*sc,0,Math.PI*2); ctx.fill();
      }
    }
  }
}

function drawTemple(ctx, x, y, sc, lvl, accent) {
  const w=46*sc, h=(48+lvl*1.4)*sc;
  const r=parseInt(accent.slice(1,3)||'c8',16);
  const g=parseInt(accent.slice(3,5)||'a0',16);
  const b=parseInt(accent.slice(5,7)||'00',16);
  // Base escalonada
  isoBox(ctx,x,y,w*1.1,h*0.12,`rgb(${r*0.3},${g*0.3},${b*0.2})`,`rgb(${r*0.2},${g*0.2},${b*0.1})`,`rgb(${r*0.35},${g*0.35},${b*0.25})`);
  isoBox(ctx,x,y-h*0.1,w,h*0.22,`rgb(${r*0.35},${g*0.35},${b*0.25})`,`rgb(${r*0.25},${g*0.25},${b*0.15})`,`rgb(${r*0.4},${g*0.4},${b*0.3})`);
  // Cuerpo
  isoBox(ctx,x,y-h*0.28,w*0.82,h*0.55,`rgb(${r*0.45},${g*0.4},${b*0.3})`,`rgb(${r*0.3},${g*0.28},${b*0.2})`,`rgb(${r*0.55},${g*0.48},${b*0.38})`);
  // Columnas frontales
  for(let i=-1;i<=1;i++){
    ctx.fillStyle=`rgba(${r*0.5},${g*0.5},${b*0.3},0.8)`;
    ctx.fillRect(x+i*w*0.28-3*sc,y-h*0.27,5*sc,h*0.5);
    // Capitel
    ctx.fillStyle=accent;
    ctx.fillRect(x+i*w*0.28-5*sc,y-h*0.27,9*sc,3*sc);
  }
  // Decoración friso
  ctx.fillStyle=`rgba(${r},${g},${b},0.3)`;
  ctx.fillRect(x-w*0.4,y-h*0.52,w*0.8,4*sc);
  // Aguja principal
  ctx.fillStyle=`rgb(${r*0.6},${g*0.55},${b*0.4})`;
  ctx.beginPath(); ctx.moveTo(x,y-h*1.05); ctx.lineTo(x+8*sc,y-h*0.65); ctx.lineTo(x-8*sc,y-h*0.65); ctx.closePath(); ctx.fill();
  ctx.strokeStyle=accent; ctx.lineWidth=0.8; ctx.stroke();
  // Agujas laterales
  [-w*0.3,w*0.3].forEach(ox=>{
    ctx.fillStyle=`rgb(${r*0.5},${g*0.45},${b*0.3})`;
    ctx.beginPath(); ctx.moveTo(x+ox,y-h*0.8); ctx.lineTo(x+ox+4*sc,y-h*0.62); ctx.lineTo(x+ox-4*sc,y-h*0.62); ctx.closePath(); ctx.fill();
    glow(ctx,x+ox,y-h*0.8,7*sc,accent);
    ctx.fillStyle=accent; ctx.beginPath(); ctx.arc(x+ox,y-h*0.8,2.5*sc,0,Math.PI*2); ctx.fill();
  });
  // Orbe cima
  glow(ctx,x,y-h*1.06,16*sc,accent);
  const orbA=0.85+0.15*Math.sin(tick*0.08);
  ctx.fillStyle=accent; ctx.fillStyle=`rgba(${r},${g},${b*0.5},${orbA})`;
  ctx.beginPath(); ctx.arc(x,y-h*1.06,4*sc,0,Math.PI*2); ctx.fill();
  // Rayos de luz divina
  if(lvl>=5){
    const rayAlpha=0.06+0.04*Math.sin(tick*0.06);
    for(let i=0;i<4;i++){
      const angle=(i/4)*Math.PI*2+tick*0.01;
      const ray=ctx.createLinearGradient(x,y-h*1.05,x+Math.cos(angle)*35*sc,y-h*1.05+Math.sin(angle)*12*sc);
      ray.addColorStop(0,`rgba(${r},${g},${b*0.5},${rayAlpha*3})`);
      ray.addColorStop(1,`rgba(${r},${g},${b*0.5},0)`);
      ctx.fillStyle=ray;
      ctx.fillRect(x+Math.cos(angle)*17*sc-1,y-h*1.05+Math.sin(angle)*6*sc-1,3,3);
    }
  }
}

function drawBarracks(ctx, x, y, sc, lvl) {
  const w=56*sc, h=(28+lvl*0.6)*sc;
  // Base
  isoBox(ctx,x,y,w*1.06,h*0.18,'#201414','#140c0c','#301c1c');
  // Cuerpo principal
  isoBox(ctx,x,y-h*0.12,w,h,'#2e1c1c','#1e1010','#402828');
  // Techo militar
  ctx.fillStyle='#1c1010';
  ctx.beginPath(); ctx.moveTo(x,y-h-10*sc); ctx.lineTo(x+w*0.58,y-h+w*0.12); ctx.lineTo(x-w*0.58,y-h+w*0.12); ctx.closePath(); ctx.fill();
  ctx.strokeStyle='rgba(0,0,0,0.5)'; ctx.lineWidth=0.8; ctx.stroke();
  // Líneas de listones techo
  ctx.strokeStyle='rgba(0,0,0,0.2)'; ctx.lineWidth=0.6;
  for(let i=1;i<5;i++){
    const t=i/5;
    ctx.beginPath(); ctx.moveTo(x-w*0.55*t,y-h+w*0.1*(1-t)); ctx.lineTo(x+w*0.55*t,y-h+w*0.1*(1-t)); ctx.stroke();
  }
  // Mástil con bandera
  ctx.strokeStyle='#504040'; ctx.lineWidth=1.5;
  ctx.beginPath(); ctx.moveTo(x+w*0.22,y-h-10*sc); ctx.lineTo(x+w*0.22,y-h-10*sc-18*sc); ctx.stroke();
  // Bandera animada
  const wave=Math.sin(tick*0.06)*3*sc;
  ctx.fillStyle='#8a2020';
  ctx.beginPath();
  ctx.moveTo(x+w*0.22,y-h-10*sc-18*sc);
  ctx.lineTo(x+w*0.22+12*sc+wave,y-h-10*sc-14*sc);
  ctx.lineTo(x+w*0.22+10*sc+wave*0.7,y-h-10*sc-11*sc);
  ctx.lineTo(x+w*0.22,y-h-10*sc-11*sc);
  ctx.closePath(); ctx.fill();
  // Cruz/emblema bandera
  ctx.fillStyle='rgba(255,200,200,0.5)';
  ctx.fillRect(x+w*0.22+4*sc,y-h-10*sc-16*sc,4*sc,1.5*sc);
  ctx.fillRect(x+w*0.22+5.5*sc,y-h-10*sc-17.5*sc,1.5*sc,4*sc);
  // Ventanas estrechas militares
  for(let i=0;i<4;i++){
    const wx=x-w*0.3+i*w*0.2;
    ctx.fillStyle='rgba(0,0,0,0.7)'; ctx.fillRect(wx-3*sc,y-h*0.55,5*sc,9*sc);
    ctx.fillStyle=`rgba(160,100,100,${0.2+0.08*Math.sin(tick*0.04+i)})`; ctx.fillRect(wx-2*sc,y-h*0.54,3*sc,7*sc);
    // Marco
    ctx.strokeStyle='rgba(80,40,40,0.6)'; ctx.lineWidth=0.5; ctx.strokeRect(wx-3*sc,y-h*0.55,5*sc,9*sc);
  }
  // Rack de lanzas
  ctx.strokeStyle='rgba(150,130,100,0.5)'; ctx.lineWidth=1;
  for(let i=0;i<4;i++){
    const lx=x-w*0.15+i*7*sc;
    ctx.beginPath(); ctx.moveTo(lx,y-h*0.05); ctx.lineTo(lx-2*sc,y-h*0.55); ctx.stroke();
    ctx.fillStyle='rgba(180,160,80,0.6)';
    ctx.beginPath(); ctx.moveTo(lx-2*sc,y-h*0.55); ctx.lineTo(lx,y-h*0.6); ctx.lineTo(lx-4*sc,y-h*0.55); ctx.closePath(); ctx.fill();
  }
  // Escudos en pared
  if(lvl>=5){
    [-w*0.38,w*0.38].forEach(ox=>{
      ctx.fillStyle='rgba(100,40,40,0.5)';
      ctx.beginPath(); ctx.arc(x+ox,y-h*0.35,6*sc,0,Math.PI*2); ctx.fill();
      ctx.strokeStyle='rgba(150,80,80,0.4)'; ctx.lineWidth=1; ctx.stroke();
    });
  }
}

"""

# Insertar el bloque nuevo
src = src[:idx_start] + BUILDINGS + src[idx_end:]

path.write_text(src, encoding="utf-8")
print("OK — edificios artísticos detallados aplicados")
print("✅ Recarga el navegador.")
