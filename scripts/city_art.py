from pathlib import Path

BASE = Path(r"E:\0000ew V2Claude\frontend")

city_js = r'''/* Pantalla CIUDAD — Arte isométrico v2 */
export async function render(container, jugador, capital) {
  const res  = await fetch(`/api/city/${jugador}/${capital}`);
  const data = await res.json();
  const c    = data.city || {};

  container.innerHTML = `
  <link rel="stylesheet" href="/static/css/city.css">
  <div class="city-screen">
    <div class="city-left">
      <div class="panel">
        <div class="panel-title">▼ Recursos</div>
        ${stat('🪵','Madera', c.MADERA)}
        ${stat('🪨','Piedra', c.PIEDRA)}
        ${stat('⚙', 'Hierro', c.HIERRO)}
        ${stat('🔥','Carbón', c.CARBON)}
        ${stat('💰','Oro',    c.ORO)}
        ${stat('✨','Maná',   c.MANA)}
      </div>
      <div class="panel">
        <div class="panel-title">▼ Producción / hora</div>
        ${stat('👤','Aldeanos', c.ALDEANO)}
        ${stat('✨','Maná',     c.MANA)}
        ${stat('💰','Oro',      c.ORO)}
      </div>
      <div class="panel">
        <div class="panel-title">▼ Logística</div>
        ${stat('📦','Almacén Nv.',   c.ALMACEN)}
        ${stat('🔮','Santuario Nv.', c.SANTUARIO_ARCANO)}
      </div>
    </div>
    <div class="city-center">
      <div class="city-canvas-wrap" id="city-wrap">
        <canvas id="city-canvas"></canvas>
        <div class="city-name-badge">${c.NOMBRE || capital}</div>
      </div>
      <div class="city-stats-bar">
        ${statBar('👥','Población', fmt(c.ALDEANO))}
        ${statBar('⚔', 'Ejércitos','—')}
        ${statBar('✨','Invoc.',    countInv(c) + ' / 14')}
        ${statBar('🏛', 'Edificios','12')}
        ${statBar('🛡', 'Muralla',  'Nv.' + (c.MURALLA||0))}
      </div>
    </div>
    <div class="city-right">
      <div class="panel">
        <div class="panel-title">▼ Ejército</div>
        ${stat('','Aldeano',    c.ALDEANO)}
        ${stat('','Explorador', c.EXPLORADOR)}
        ${stat('','Sacerdote',  c.SACERDOTE)}
        ${stat('','Guerrero',   c.GUERRERO)}
        ${stat('','Comando',    c.COMANDO)}
        ${stat('','Mercenario', c.MERCENARIO)}
        ${stat('','Marine',     c.MARINE)}
        ${stat('','Cyborg',     c.CYBORG)}
        ${stat('','Mago',       c.MAGO)}
        ${stat('','Metahumano', c.METAHUMANO)}
      </div>
      <div class="panel">
        <div class="panel-title">▼ Invocaciones</div>
        ${stat('','Demonio',     c.DEMONIO)}
        ${stat('','Ánima',       c.ANIMA)}
        ${stat('','Espectro',    c.ESPECTRO)}
        ${stat('','Gólem',       c.GOLEM)}
        ${stat('','Centauro',    c.CENTAURO)}
        ${stat('','Kraken',      c.KRAKEN)}
        ${stat('','Alonardo',    c.ALONARDO)}
        ${stat('','Madreselva',  c.MADRESELVA)}
        ${stat('','Coloso',      c.COLOSO)}
        ${stat('','Fénix',       c.FENIX)}
        ${stat('','Dragón Oro',  c.DRAGON_DE_ORO)}
        ${stat('','Cab. Luz',    c.CABALLERO_DE_LUZ)}
        ${stat('','AlalaiA',     c.ALALAIA)}
        ${stat('','Éon Supremo', c.EON_SUPREMO)}
      </div>
    </div>
  </div>`;

  setTimeout(() => drawCity(c), 120);
  window.addEventListener('resize', () => drawCity(c));
}

function fmt(val) {
  if (val === undefined || val === null) return '—';
  const n = Number(val);
  if (isNaN(n)) return '—';
  if (n === 0)  return '0';
  const abs = Math.abs(n), s = n < 0 ? '-' : '';
  const tiers = [
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
  return s + Math.round(abs).toLocaleString('es');
}

function stat(icon, label, val) {
  return `<div class="stat-row">
    <span class="stat-label">${icon ? icon+' ' : ''}${label}</span>
    <span class="stat-val">${fmt(val)}</span>
  </div>`;
}
function statBar(icon, label, val) {
  return `<div class="stat-bar-item">
    <span class="stat-bar-icon">${icon}</span>
    <span class="stat-bar-label">${label}</span>
    <span class="stat-bar-val">${val}</span>
  </div>`;
}
function countInv(c) {
  return ['DEMONIO','ANIMA','ESPECTRO','GOLEM','CENTAURO','KRAKEN',
    'ALONARDO','MADRESELVA','COLOSO','FENIX','DRAGON_DE_ORO',
    'CABALLERO_DE_LUZ','ALALAIA','EON_SUPREMO'].filter(k=>c[k]>0).length;
}

// ═══════════════════════════════════════════════════════════════
// RENDERIZADOR ISOMÉTRICO
// ═══════════════════════════════════════════════════════════════
let animFrame = null;
let tick = 0;

function drawCity(c) {
  const canvas = document.getElementById('city-canvas');
  const wrap   = document.getElementById('city-wrap');
  if (!canvas || !wrap) return;
  const W = wrap.clientWidth, H = wrap.clientHeight;
  if (W < 10 || H < 10) { setTimeout(()=>drawCity(c), 50); return; }
  canvas.width = W; canvas.height = H;
  canvas.style.width = W+'px'; canvas.style.height = H+'px';

  if (animFrame) cancelAnimationFrame(animFrame);
  function loop() {
    tick++;
    render(canvas, W, H, c);
    animFrame = requestAnimationFrame(loop);
  }
  loop();
}

function render(canvas, W, H, c) {
  const ctx = canvas.getContext('2d');
  const cx = W/2, cy = H*0.52;

  // Fondo cielo nocturno
  const sky = ctx.createLinearGradient(0,0,0,H*0.6);
  sky.addColorStop(0,'#020208');
  sky.addColorStop(0.5,'#080818');
  sky.addColorStop(1,'#0e0e28');
  ctx.fillStyle = sky; ctx.fillRect(0,0,W,H);

  // Estrellas animadas
  drawStars(ctx, W, H);

  // Luna
  drawMoon(ctx, W*0.82, H*0.12);

  // Niebla de fondo
  drawMist(ctx, W, H, cx, cy);

  // Suelo isométrico detallado
  drawTerrain(ctx, cx, cy, W, H);

  // Muralla perimetral
  const mLvl = Number(c.MURALLA||0);
  if (mLvl > 0) drawWallPerimeter(ctx, cx, cy, mLvl);

  // Edificios
  const buildings = getLayout(c, cx, cy);
  buildings.sort((a,b) => (a.iy||a.y) - (b.iy||b.y));
  buildings.forEach(b => drawBuilding(ctx, b, c));

  // Partículas mágicas flotantes
  drawParticles(ctx, cx, cy, c);
}

function drawStars(ctx, W, H) {
  for (let i=0; i<120; i++) {
    const x = ((Math.sin(i*137.508)*0.5+0.5)*W);
    const y = ((Math.cos(i*97.3)*0.5+0.5)*H*0.45);
    const br = 0.3 + 0.7*Math.abs(Math.sin(tick*0.01 + i));
    const r = i%11===0 ? 1.5 : 0.6;
    ctx.fillStyle = `rgba(255,255,240,${br*0.7})`;
    ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
  }
}

function drawMoon(ctx, x, y) {
  const g = ctx.createRadialGradient(x,y,2,x,y,35);
  g.addColorStop(0,'rgba(220,210,180,0.9)');
  g.addColorStop(0.6,'rgba(180,170,140,0.4)');
  g.addColorStop(1,'rgba(180,170,140,0)');
  ctx.fillStyle = g;
  ctx.beginPath(); ctx.arc(x,y,35,0,Math.PI*2); ctx.fill();
  ctx.fillStyle = 'rgba(200,190,160,0.6)';
  ctx.beginPath(); ctx.arc(x,y,18,0,Math.PI*2); ctx.fill();
}

function drawMist(ctx, W, H, cx, cy) {
  for (let i=0; i<3; i++) {
    const g = ctx.createRadialGradient(cx,cy+i*20,10,cx,cy+i*20,W*0.5);
    g.addColorStop(0,`rgba(${20+i*5},${25+i*5},${50+i*10},0.15)`);
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0,0,W,H);
  }
}

function drawTerrain(ctx, cx, cy, W, H) {
  const TW=64, TH=32;
  const cols=18, rows=14;
  for (let r=0; r<rows; r++) {
    for (let col=0; col<cols; col++) {
      const x = cx + (col-cols/2)*TW/2 - (r-rows/2)*TW/2;
      const y = cy + (col-cols/2)*TH/2 + (r-rows/2)*TH/2;
      const dist = Math.sqrt(Math.pow((col-cols/2)/(cols/2),2)+Math.pow((r-rows/2)/(rows/2),2));
      if (dist > 0.95) continue;
      const base = (col+r)%2===0;
      const g1 = base ? 28 : 22, g2 = base ? 38 : 30;
      // Tile de tierra
      ctx.fillStyle = `rgb(${g1},${g2+4},${g1})`;
      ctx.beginPath();
      ctx.moveTo(x, y-TH/2); ctx.lineTo(x+TW/2, y);
      ctx.lineTo(x, y+TH/2); ctx.lineTo(x-TW/2, y);
      ctx.closePath(); ctx.fill();
      // Borde
      ctx.strokeStyle='rgba(0,0,0,0.5)'; ctx.lineWidth=0.5; ctx.stroke();
      // Hierba ocasional
      if ((col*7+r*13)%17===0) {
        ctx.fillStyle='rgba(40,80,40,0.5)';
        ctx.beginPath();
        ctx.moveTo(x, y-TH/2); ctx.lineTo(x+TW/2, y);
        ctx.lineTo(x, y+TH/2); ctx.lineTo(x-TW/2, y);
        ctx.closePath(); ctx.fill();
      }
    }
  }
  // Caminos
  drawPath(ctx, cx, cy, TW, TH, cols, rows);
}

function drawPath(ctx, cx, cy, TW, TH, cols, rows) {
  ctx.strokeStyle='rgba(80,60,40,0.4)';
  ctx.lineWidth=8;
  ctx.setLineDash([]);
  // Camino central vertical (isométrico)
  ctx.beginPath();
  ctx.moveTo(cx, cy - TH*(rows/2)*0.6);
  ctx.lineTo(cx, cy + TH*(rows/2)*0.6);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(cx - TW*(cols/2)*0.4, cy);
  ctx.lineTo(cx + TW*(cols/2)*0.4, cy);
  ctx.stroke();
  ctx.lineWidth=1;
}

function drawWallPerimeter(ctx, cx, cy, lvl) {
  const scale = 1 + lvl*0.004;
  const rx = 195*scale, ry = 110*scale;
  const h = 14 + lvl*0.3;
  const pts = [
    [cx, cy - ry],
    [cx + rx, cy],
    [cx, cy + ry],
    [cx - rx, cy]
  ];

  // Sombra muro
  ctx.beginPath();
  pts.forEach((p,i) => i===0 ? ctx.moveTo(p[0],p[1]+h) : ctx.lineTo(p[0],p[1]+h));
  ctx.closePath();
  ctx.strokeStyle='rgba(0,0,0,0.3)'; ctx.lineWidth=h*0.8; ctx.stroke();

  // Muro exterior
  const wallColor = `rgb(${45+lvl},${50+lvl},${65+lvl})`;
  ctx.strokeStyle = wallColor;
  ctx.lineWidth = h*0.5;
  ctx.beginPath();
  pts.forEach((p,i) => i===0 ? ctx.moveTo(p[0],p[1]) : ctx.lineTo(p[0],p[1]));
  ctx.closePath(); ctx.stroke();

  // Almenas
  ctx.fillStyle = wallColor;
  const numMerlons = Math.floor(28 + lvl*0.5);
  for (let i=0; i<numMerlons; i++) {
    const t = i/numMerlons;
    const segIdx = Math.floor(t*4);
    const segFrac = (t*4)%1;
    const p0 = pts[segIdx], p1 = pts[(segIdx+1)%4];
    const bx = p0[0]+(p1[0]-p0[0])*segFrac;
    const by = p0[1]+(p1[1]-p0[1])*segFrac;
    ctx.fillRect(bx-3, by-h*0.4-5, 5, 6);
  }

  // Torres en esquinas
  pts.forEach(([px,py]) => {
    drawTowerCorner(ctx, px, py, h, lvl);
  });
}

function drawTowerCorner(ctx, x, y, h, lvl) {
  const tw = 10+lvl*0.2, th = 20+lvl*0.3;
  ctx.fillStyle = `rgb(${50+lvl},${55+lvl},${70+lvl})`;
  ctx.fillRect(x-tw/2, y-th, tw, th);
  // Techo
  ctx.fillStyle = `rgb(${60+lvl},${65+lvl},${85+lvl})`;
  ctx.beginPath();
  ctx.moveTo(x, y-th-8); ctx.lineTo(x+tw/2, y-th); ctx.lineTo(x-tw/2, y-th);
  ctx.closePath(); ctx.fill();
  // Ventana con luz
  if (lvl >= 5) {
    ctx.fillStyle = `rgba(255,200,80,${0.3+0.2*Math.sin(tick*0.05)})`;
    ctx.fillRect(x-3, y-th*0.6, 6, 5);
  }
}

function getLayout(c, cx, cy) {
  const lv = k => Number(c[k]||0);
  return [
    { key:'CENTRO_DE_CIUDAD', label:'Centro Ciudad', lvl:lv('CENTRO_DE_CIUDAD'),
      x:cx, y:cy-15, iy:cy-15, type:'cityhall' },
    { key:'CASA', label:'Casa', lvl:lv('CASA'),
      x:cx-130, y:cy-5, iy:cy+5, type:'house' },
    { key:'TORRE_DE_VIGILANCIA', label:'Torre Vig.', lvl:lv('TORRE_DE_VIGILANCIA'),
      x:cx+145, y:cy-35, iy:cy-25, type:'watchtower' },
    { key:'CENTRO_DE_VIAJES', label:'C.Viajes', lvl:lv('CENTRO_DE_VIAJES'),
      x:cx-85, y:cy-65, iy:cy-55, type:'travel' },
    { key:'ESCONDITE', label:'Escondite', lvl:lv('ESCONDITE'),
      x:cx+110, y:cy+28, iy:cy+38, type:'hideout' },
    { key:'ALMACEN', label:'Almacén', lvl:lv('ALMACEN'),
      x:cx-115, y:cy+38, iy:cy+48, type:'warehouse' },
    { key:'SANTUARIO_ARCANO', label:'Santuario', lvl:lv('SANTUARIO_ARCANO'),
      x:cx+25, y:cy-95, iy:cy-85, type:'sanctuary' },
    { key:'UNIVERSIDAD', label:'Universidad', lvl:lv('UNIVERSIDAD'),
      x:cx-45, y:cy-82, iy:cy-72, type:'university' },
    { key:'HERRERIA', label:'Herrería', lvl:lv('HERRERIA'),
      x:cx+65, y:cy+45, iy:cy+55, type:'forge' },
    { key:'TEMPLO_1', label:'Templo 1', lvl:lv('TEMPLO_1'),
      x:cx+80, y:cy-55, iy:cy-45, type:'temple', accent:'#c8a000' },
    { key:'TEMPLO_2', label:'Templo 2', lvl:lv('TEMPLO_2'),
      x:cx+100, y:cy-15, iy:cy-5, type:'temple', accent:'#d4a020' },
    { key:'TEMPLO_3', label:'Templo 3', lvl:lv('TEMPLO_3'),
      x:cx+55, y:cy+10, iy:cy+20, type:'temple', accent:'#e0b040' },
    { key:'CUARTEL_1', label:'Cuartel 1', lvl:lv('CUARTEL_1'),
      x:cx-55, y:cy+8, iy:cy+18, type:'barracks' },
    { key:'CUARTEL_2', label:'Cuartel 2', lvl:lv('CUARTEL_2'),
      x:cx-25, y:cy+48, iy:cy+58, type:'barracks' },
  ];
}

function drawBuilding(ctx, b, c) {
  const lvl = b.lvl || 0;
  const sc = 0.45 + Math.min(lvl,50)*0.015;
  const x = b.x, y = b.y;

  ctx.save();
  switch(b.type) {
    case 'cityhall':   drawCityHall(ctx, x, y, sc, lvl); break;
    case 'house':      drawHouse(ctx, x, y, sc, lvl); break;
    case 'watchtower': drawWatchtower(ctx, x, y, sc, lvl); break;
    case 'travel':     drawTravelCenter(ctx, x, y, sc, lvl); break;
    case 'hideout':    drawHideout(ctx, x, y, sc, lvl); break;
    case 'warehouse':  drawWarehouse(ctx, x, y, sc, lvl); break;
    case 'sanctuary':  drawSanctuary(ctx, x, y, sc, lvl); break;
    case 'university': drawUniversity(ctx, x, y, sc, lvl); break;
    case 'forge':      drawForge(ctx, x, y, sc, lvl); break;
    case 'temple':     drawTemple(ctx, x, y, sc, lvl, b.accent||'#c8a000'); break;
    case 'barracks':   drawBarracks(ctx, x, y, sc, lvl); break;
  }
  ctx.restore();

  drawLabel(ctx, x, y + (30 + lvl*0.8)*sc + 8, b.label, lvl);
}

// ─── HELPERS ────────────────────────────────────────────────────────────────

function isoBox(ctx, x, y, w, h, top, left, right, outline=true) {
  const hw=w/2, qh=w/4;
  ctx.fillStyle=top;
  ctx.beginPath();
  ctx.moveTo(x,y-h); ctx.lineTo(x+hw,y-h+qh); ctx.lineTo(x,y-h+qh*2); ctx.lineTo(x-hw,y-h+qh);
  ctx.closePath(); ctx.fill();
  ctx.fillStyle=left;
  ctx.beginPath();
  ctx.moveTo(x-hw,y-h+qh); ctx.lineTo(x,y-h+qh*2); ctx.lineTo(x,y); ctx.lineTo(x-hw,y-qh);
  ctx.closePath(); ctx.fill();
  ctx.fillStyle=right;
  ctx.beginPath();
  ctx.moveTo(x,y-h+qh*2); ctx.lineTo(x+hw,y-h+qh); ctx.lineTo(x+hw,y-qh); ctx.lineTo(x,y);
  ctx.closePath(); ctx.fill();
  if (outline) {
    ctx.strokeStyle='rgba(0,0,0,0.5)'; ctx.lineWidth=0.8;
    ctx.beginPath();
    ctx.moveTo(x,y-h); ctx.lineTo(x+hw,y-h+qh); ctx.lineTo(x+hw,y-qh);
    ctx.lineTo(x,y); ctx.lineTo(x-hw,y-qh); ctx.lineTo(x-hw,y-h+qh); ctx.closePath();
    ctx.stroke();
  }
}

function addWindows(ctx, x, y, w, h, count, color) {
  for (let i=0; i<count; i++) {
    const wx = x - w*0.3 + (i/(count-1||1))*w*0.6;
    const wy = y - h*0.5;
    ctx.fillStyle = color;
    ctx.fillRect(wx-3, wy-4, 5, 6);
    ctx.fillStyle = 'rgba(0,0,0,0.3)';
    ctx.fillRect(wx-3, wy-4, 5, 1);
  }
}

function glow(ctx, x, y, r, color) {
  const g = ctx.createRadialGradient(x,y,1,x,y,r);
  g.addColorStop(0, color.replace(')',',0.6)').replace('rgb','rgba'));
  g.addColorStop(1, color.replace(')',',0)').replace('rgb','rgba'));
  ctx.fillStyle = g;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
}

function shade(hex, n) {
  if (hex.startsWith('rgb')) {
    return hex.replace(/\d+/g, (m,i) => Math.min(255,Math.max(0,+m+n)));
  }
  const v = parseInt(hex.replace('#',''),16);
  const r=Math.min(255,Math.max(0,((v>>16)&255)+n));
  const g=Math.min(255,Math.max(0,((v>>8)&255)+n));
  const b=Math.min(255,Math.max(0,(v&255)+n));
  return `rgb(${r},${g},${b})`;
}

// ─── EDIFICIOS ───────────────────────────────────────────────────────────────

function drawCityHall(ctx, x, y, sc, lvl) {
  const w=70*sc, h=(60+lvl*1.5)*sc;
  // Base
  isoBox(ctx,x,y,w,h*0.4,'#2a3a5a','#1a2a4a','#3a4a6a');
  // Torre izq
  isoBox(ctx,x-w*0.55,y-h*0.1,w*0.45,h*0.75,'#253560','#152550','#354570');
  // Torre der
  isoBox(ctx,x+w*0.55,y-h*0.1,w*0.45,h*0.75,'#253560','#152550','#354570');
  // Torre central
  isoBox(ctx,x,y,w*0.55,h,'#3a5080','#2a4070','#4a6090');
  // Ventanas azules
  addWindows(ctx, x-w*0.55, y-h*0.3, w*0.3, h*0.6, 2, `rgba(100,160,255,${0.4+0.2*Math.sin(tick*0.04)})`);
  addWindows(ctx, x+w*0.55, y-h*0.3, w*0.3, h*0.6, 2, `rgba(100,160,255,${0.4+0.2*Math.sin(tick*0.04+1)})`);
  addWindows(ctx, x, y-h*0.4, w*0.4, h*0.7, 3, `rgba(150,200,255,${0.5+0.2*Math.sin(tick*0.03)})`);
  // Punta con orbe
  if (lvl >= 5) {
    ctx.fillStyle='#4a88cc';
    ctx.beginPath(); ctx.moveTo(x,y-h-12*sc); ctx.lineTo(x+5*sc,y-h); ctx.lineTo(x-5*sc,y-h); ctx.closePath(); ctx.fill();
    glow(ctx, x, y-h-8*sc, 18*sc, 'rgb(80,150,255)');
    ctx.fillStyle=`rgba(150,200,255,${0.8+0.2*Math.sin(tick*0.07)})`;
    ctx.beginPath(); ctx.arc(x,y-h-12*sc,4*sc,0,Math.PI*2); ctx.fill();
  }
  // Bandera
  ctx.strokeStyle='#6a8aaa'; ctx.lineWidth=1.5;
  ctx.beginPath(); ctx.moveTo(x-w*0.55,y-h*0.8); ctx.lineTo(x-w*0.55,y-h*0.8-15*sc); ctx.stroke();
  ctx.fillStyle='#4a70a0';
  ctx.fillRect(x-w*0.55, y-h*0.8-15*sc, 10*sc, 7*sc);
}

function drawHouse(ctx, x, y, sc, lvl) {
  const w=52*sc, h=(28+lvl*0.6)*sc;
  isoBox(ctx,x,y,w,h,'#4a3820','#2e2010','#6a5030');
  // Techo
  ctx.fillStyle='#5a4830';
  ctx.beginPath();
  ctx.moveTo(x,y-h-14*sc); ctx.lineTo(x+w*0.6,y-h+w*0.15); ctx.lineTo(x-w*0.6,y-h+w*0.15);
  ctx.closePath(); ctx.fill();
  ctx.strokeStyle='rgba(0,0,0,0.4)'; ctx.lineWidth=0.8; ctx.stroke();
  // Ventanas cálidas
  const wc = `rgba(255,180,60,${0.4+0.15*Math.sin(tick*0.05)})`;
  ctx.fillStyle=wc; ctx.fillRect(x-12*sc, y-h*0.55, 8*sc, 7*sc);
  ctx.fillStyle=wc; ctx.fillRect(x+4*sc, y-h*0.55, 8*sc, 7*sc);
  // Puerta
  ctx.fillStyle='#1e1008';
  ctx.beginPath(); ctx.arc(x,y-h*0.18,5*sc,Math.PI,0); ctx.rect(x-5*sc,y-h*0.18,10*sc,8*sc); ctx.fill();
  if (lvl >= 3) {
    ctx.fillStyle='rgba(255,150,40,0.2)';
    ctx.beginPath(); ctx.arc(x,y-h*0.05,15*sc,0,Math.PI*2); ctx.fill();
  }
}

function drawWatchtower(ctx, x, y, sc, lvl) {
  const w=32*sc, h=(70+lvl*2)*sc;
  // Base sólida
  isoBox(ctx,x,y,w*1.3,h*0.3,'#304050','#1e2e3a','#405870');
  // Torre
  isoBox(ctx,x,y-h*0.2,w,h,'#304050','#1e2e3a','#405870');
  // Almenas en cima
  for (let i=-2;i<=2;i++) {
    ctx.fillStyle='#405870';
    ctx.fillRect(x+i*4*sc-2*sc, y-h-4*sc, 3*sc, 5*sc);
  }
  // Ventanas de observación
  for (let yy=0.3;yy<0.9;yy+=0.3) {
    ctx.fillStyle=`rgba(200,230,255,${0.3+0.2*Math.sin(tick*0.04+yy)})`;
    ctx.fillRect(x-3*sc, y-h*yy, 6*sc, 5*sc);
  }
  // Luz giratoria en cima
  if (lvl >= 10) {
    const angle = tick*0.03;
    const lx = x + Math.cos(angle)*20*sc;
    const ly = y-h + Math.sin(angle)*5*sc;
    const lg = ctx.createLinearGradient(x,y-h,lx,ly);
    lg.addColorStop(0,'rgba(200,230,255,0.6)');
    lg.addColorStop(1,'rgba(200,230,255,0)');
    ctx.fillStyle=lg;
    ctx.beginPath(); ctx.moveTo(x,y-h); ctx.lineTo(lx-3,ly-3); ctx.lineTo(lx+3,ly+3); ctx.closePath(); ctx.fill();
  }
}

function drawTravelCenter(ctx, x, y, sc, lvl) {
  const w=55*sc, h=(35+lvl*0.8)*sc;
  isoBox(ctx,x,y,w,h,'#303860','#1e2448','#4048a0');
  // Arco portal
  ctx.strokeStyle=`rgba(100,150,255,${0.7+0.3*Math.sin(tick*0.06)})`;
  ctx.lineWidth=3*sc;
  ctx.beginPath(); ctx.arc(x, y-h*0.3, 12*sc, Math.PI, 0); ctx.stroke();
  // Energía del portal
  if (lvl >= 5) {
    const pg = ctx.createRadialGradient(x,y-h*0.3,2,x,y-h*0.3,12*sc);
    pg.addColorStop(0,`rgba(80,120,255,${0.4+0.2*Math.sin(tick*0.08)})`);
    pg.addColorStop(1,'rgba(80,120,255,0)');
    ctx.fillStyle=pg; ctx.beginPath(); ctx.arc(x,y-h*0.3,12*sc,Math.PI,0); ctx.fill();
  }
  // Runas en las paredes
  ctx.fillStyle=`rgba(100,150,255,${0.3+0.15*Math.sin(tick*0.05)})`;
  for (let i=0;i<4;i++) {
    ctx.fillRect(x-w*0.3+i*w*0.2, y-h*0.6, 4*sc, 4*sc);
  }
}

function drawHideout(ctx, x, y, sc, lvl) {
  const w=48*sc, h=(20+lvl*0.5)*sc;
  // Muy bajo — semienterrado
  isoBox(ctx,x,y,w,h,'#2a3020','#181e10','#3a4030');
  // Trampilla
  ctx.fillStyle='#1a1a10';
  ctx.beginPath();
  ctx.ellipse(x, y-h*0.1, w*0.2, h*0.3, 0, 0, Math.PI*2);
  ctx.fill();
  ctx.strokeStyle='#3a3a20'; ctx.lineWidth=1.5; ctx.stroke();
  // Vegetación encima
  for (let i=0;i<5;i++) {
    const vx = x+(i-2)*9*sc, vy=y-h-2*sc;
    ctx.fillStyle=`rgba(${30+i*5},${50+i*8},20,0.7)`;
    ctx.beginPath(); ctx.arc(vx,vy,5*sc,0,Math.PI*2); ctx.fill();
  }
}

function drawWarehouse(ctx, x, y, sc, lvl) {
  const w=65*sc, h=(30+lvl*0.7)*sc;
  isoBox(ctx,x,y,w,h,'#503010','#382008','#705020');
  // Techo a dos aguas
  ctx.fillStyle='#604020';
  ctx.beginPath();
  ctx.moveTo(x,y-h-10*sc); ctx.lineTo(x+w*0.55,y-h+w*0.14); ctx.lineTo(x-w*0.55,y-h+w*0.14);
  ctx.closePath(); ctx.fill();
  // Puertas grandes
  ctx.fillStyle='#201008';
  ctx.fillRect(x-10*sc, y-h*0.4, 18*sc, h*0.4);
  ctx.fillRect(x+2*sc, y-h*0.4, 18*sc, h*0.4);
  // Bisagras
  ctx.fillStyle='#604030'; ctx.fillRect(x-1*sc, y-h*0.35, 2*sc, 2*sc);
  if (lvl >= 10) {
    ctx.fillStyle='rgba(255,160,60,0.15)';
    ctx.beginPath(); ctx.arc(x,y-h*0.2,25*sc,0,Math.PI*2); ctx.fill();
  }
}

function drawSanctuary(ctx, x, y, sc, lvl) {
  const w=50*sc, h=(40+lvl*1.2)*sc;
  isoBox(ctx,x,y,w,h*0.5,'#402060','#280e48','#6030a0');
  // Cúpula
  ctx.fillStyle='#5030a0';
  ctx.beginPath(); ctx.ellipse(x,y-h*0.52,w*0.45,h*0.5,0,Math.PI,0); ctx.fill();
  ctx.fillStyle='#6040b0';
  ctx.beginPath(); ctx.ellipse(x,y-h*0.52,w*0.25,h*0.35,0,Math.PI,0); ctx.fill();
  // Ventana circular
  ctx.fillStyle=`rgba(180,100,255,${0.5+0.3*Math.sin(tick*0.06)})`;
  ctx.beginPath(); ctx.arc(x,y-h*0.6,5*sc,0,Math.PI*2); ctx.fill();
  // Columnas de maná
  if (lvl >= 5) {
    for (let i=0;i<6;i++) {
      const angle = (i/6)*Math.PI*2 + tick*0.02;
      const px=x+Math.cos(angle)*w*0.35, py=y-h*0.55+Math.sin(angle)*h*0.15;
      const alpha = 0.4+0.3*Math.sin(tick*0.05+i);
      ctx.fillStyle=`rgba(180,80,255,${alpha})`;
      ctx.beginPath(); ctx.arc(px,py,3*sc,0,Math.PI*2); ctx.fill();
    }
  }
  glow(ctx, x, y-h*0.7, 30*sc, 'rgb(140,60,220)');
}

function drawUniversity(ctx, x, y, sc, lvl) {
  const w=58*sc, h=(45+lvl)*sc;
  isoBox(ctx,x,y,w,h*0.6,'#203850','#102438','#305878');
  // Torre biblioteca
  isoBox(ctx,x-w*0.25,y-h*0.3,w*0.4,h,'#1a3048','#0e2030','#284060');
  // Arcos góticos
  for (let i=0;i<3;i++) {
    ctx.strokeStyle=`rgba(100,180,220,${0.3+0.1*Math.sin(tick*0.04+i)})`;
    ctx.lineWidth=1.5*sc;
    ctx.beginPath(); ctx.arc(x-w*0.25+(i-1)*8*sc, y-h*0.4, 5*sc, Math.PI, 0); ctx.stroke();
  }
  // Ventanas cálidas de estudio
  addWindows(ctx, x-w*0.25, y-h*0.6, w*0.3, h*0.8, 2, `rgba(255,200,100,${0.35+0.15*Math.sin(tick*0.03)})`);
  // Contrafuertes
  ctx.fillStyle='#1a2838';
  ctx.fillRect(x+w*0.1, y-h*0.45, 6*sc, h*0.45);
  ctx.fillRect(x+w*0.25, y-h*0.35, 6*sc, h*0.35);
}

function drawForge(ctx, x, y, sc, lvl) {
  const w=52*sc, h=(32+lvl*0.7)*sc;
  isoBox(ctx,x,y,w,h,'#502010','#380e04','#803020');
  // Chimenea
  isoBox(ctx,x+w*0.25,y-h*0.6,w*0.2,h*0.55,'#402010','#2e0e04','#602018');
  // Fuego en chimenea
  const fire = `rgba(255,${80+Math.floor(80*Math.sin(tick*0.12))},0,${0.6+0.3*Math.sin(tick*0.1)})`;
  ctx.fillStyle=fire;
  ctx.beginPath(); ctx.arc(x+w*0.25, y-h*1.1, 6*sc, 0, Math.PI*2); ctx.fill();
  glow(ctx, x+w*0.25, y-h*1.05, 14*sc, 'rgb(255,100,0)');
  // Puerta con brasas
  ctx.fillStyle='#0a0402';
  ctx.beginPath(); ctx.arc(x,y-h*0.25,8*sc,Math.PI,0); ctx.rect(x-8*sc,y-h*0.25,16*sc,10*sc); ctx.fill();
  ctx.fillStyle=`rgba(255,60,0,${0.3+0.2*Math.sin(tick*0.08)})`;
  ctx.beginPath(); ctx.arc(x,y-h*0.3,5*sc,0,Math.PI*2); ctx.fill();
  // Yunque
  ctx.fillStyle='#303030';
  ctx.fillRect(x-8*sc, y-h*0.08, 16*sc, 4*sc);
  ctx.fillRect(x-5*sc, y-h*0.08, 10*sc, -4*sc);
}

function drawTemple(ctx, x, y, sc, lvl, accent) {
  const w=44*sc, h=(50+lvl*1.3)*sc;
  isoBox(ctx,x,y,w,h*0.45,shade(accent,-60),shade(accent,-80),shade(accent,-50));
  // Aguja central
  ctx.fillStyle=shade(accent,-30);
  ctx.beginPath();
  ctx.moveTo(x,y-h); ctx.lineTo(x+w*0.22,y-h*0.47); ctx.lineTo(x-w*0.22,y-h*0.47);
  ctx.closePath(); ctx.fill();
  ctx.strokeStyle=accent; ctx.lineWidth=1; ctx.stroke();
  // Ornamento en punta
  glow(ctx, x, y-h, 12*sc, accent);
  ctx.fillStyle=accent;
  ctx.beginPath(); ctx.arc(x,y-h,3*sc,0,Math.PI*2); ctx.fill();
  // Decoración
  ctx.strokeStyle=`rgba(${parseInt(accent.slice(1,3),16)},${parseInt(accent.slice(3,5),16)},0,0.4)`;
  ctx.lineWidth=1.5*sc;
  for (let i=0;i<3;i++) {
    ctx.beginPath(); ctx.arc(x,y-h*0.6,w*0.12*(i+1),0,Math.PI*2); ctx.stroke();
  }
}

function drawBarracks(ctx, x, y, sc, lvl) {
  const w=55*sc, h=(30+lvl*0.6)*sc;
  isoBox(ctx,x,y,w,h,'#302020','#201010','#503030');
  // Techo militar
  ctx.fillStyle='#201818';
  ctx.beginPath();
  ctx.moveTo(x,y-h-8*sc); ctx.lineTo(x+w*0.6,y-h+w*0.12); ctx.lineTo(x-w*0.6,y-h+w*0.12);
  ctx.closePath(); ctx.fill();
  // Bandera militar
  ctx.strokeStyle='#604040'; ctx.lineWidth=1.5;
  ctx.beginPath(); ctx.moveTo(x+w*0.2,y-h-8*sc); ctx.lineTo(x+w*0.2,y-h-8*sc-14*sc); ctx.stroke();
  ctx.fillStyle='#802020'; ctx.fillRect(x+w*0.2,y-h-8*sc-14*sc,9*sc,6*sc);
  // Ventanas cuartelarias
  for (let i=0;i<3;i++) {
    ctx.fillStyle='rgba(40,40,40,0.8)';
    ctx.fillRect(x-w*0.25+i*w*0.22, y-h*0.5, 7*sc, 6*sc);
    ctx.strokeStyle='rgba(100,60,60,0.5)'; ctx.lineWidth=0.5; ctx.strokeRect(x-w*0.25+i*w*0.22, y-h*0.5, 7*sc, 6*sc);
  }
  // Rack de armas
  ctx.strokeStyle='rgba(150,120,80,0.4)'; ctx.lineWidth=1;
  for (let i=0;i<3;i++) {
    ctx.beginPath(); ctx.moveTo(x-10*sc+i*8*sc, y-h*0.1); ctx.lineTo(x-10*sc+i*8*sc, y-h*0.6); ctx.stroke();
  }
}

function drawParticles(ctx, cx, cy, c) {
  const mana = Number(c.MANA||0);
  if (mana < 1000) return;
  const count = Math.min(20, Math.floor(Math.log10(mana)*3));
  for (let i=0;i<count;i++) {
    const angle = (i/count)*Math.PI*2 + tick*0.008;
    const r = 80 + 30*Math.sin(tick*0.02+i);
    const px = cx + Math.cos(angle)*r;
    const py = cy - 20 + Math.sin(angle)*r*0.4;
    const alpha = 0.2+0.2*Math.abs(Math.sin(tick*0.04+i));
    ctx.fillStyle=`rgba(150,80,255,${alpha})`;
    ctx.beginPath(); ctx.arc(px,py,2,0,Math.PI*2); ctx.fill();
  }
}

function drawLabel(ctx, x, y, text, lvl) {
  ctx.save();
  ctx.font = 'bold 9px Rajdhani, sans-serif';
  const label = lvl > 0 ? `${text}  Nv.${lvl}` : text;
  const tw = ctx.measureText(label).width + 14;
  ctx.fillStyle='rgba(5,5,15,0.88)';
  ctx.strokeStyle = lvl > 0 ? 'rgba(180,150,60,0.7)' : 'rgba(50,50,70,0.5)';
  ctx.lineWidth=0.8;
  rr(ctx, x-tw/2, y-9, tw, 16, 3); ctx.fill(); ctx.stroke();
  ctx.fillStyle = lvl > 0 ? '#d4ae5c' : '#505065';
  ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText(label, x, y);
  ctx.restore();
}

function rr(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x+r,y); ctx.lineTo(x+w-r,y); ctx.arcTo(x+w,y,x+w,y+r,r);
  ctx.lineTo(x+w,y+h-r); ctx.arcTo(x+w,y+h,x+w-r,y+h,r);
  ctx.lineTo(x+r,y+h); ctx.arcTo(x,y+h,x,y+h-r,r);
  ctx.lineTo(x,y+r); ctx.arcTo(x,y,x+r,y,r); ctx.closePath();
}
'''

p = BASE / "js/screens/city.js"
p.write_text(city_js, encoding="utf-8")
print("OK js/screens/city.js — Arte isométrico completo")
print("✅ Recarga el navegador (Ctrl+Shift+R).")
