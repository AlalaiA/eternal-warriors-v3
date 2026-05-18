from pathlib import Path

BASE = Path(r"E:\0000ew V2Claude\frontend")

city_js = r'''/* Pantalla CIUDAD — Vista completa con edificios SVG */
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
        ${stat('📦','Almacén',   c.ALMACEN)}
        ${stat('🔮','Santuario', c.SANTUARIO_ARCANO)}
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

  requestAnimationFrame(() => drawCity(c));
}

// ── Formato de números ────────────────────────────────────────────────────
function fmt(val) {
  if (val === undefined || val === null) return '—';
  const n = Number(val);
  if (isNaN(n)) return '—';
  if (n === 0)  return '0';
  const abs = Math.abs(n), s = n < 0 ? '-' : '';
  const tiers = [[1e15,'Q'],[1e12,'T'],[1e9,'B'],[1e6,'M'],[1e3,'K']];
  for (const [d, sfx] of tiers) {
    if (abs >= d) {
      const v = abs/d;
      return s + (v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(1) : v.toFixed(2)) + sfx;
    }
  }
  if (abs >= 1e18) {
    const e = Math.floor(Math.log10(abs));
    return s + (abs/Math.pow(10,e)).toFixed(1) + 'e' + e;
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

// ── Dibujado de ciudad ────────────────────────────────────────────────────
function drawCity(c) {
  const canvas = document.getElementById('city-canvas');
  const wrap   = document.getElementById('city-wrap');
  if (!canvas || !wrap) return;
  const W = wrap.clientWidth, H = wrap.clientHeight;
  if (W < 10 || H < 10) { setTimeout(()=>drawCity(c), 50); return; }
  canvas.width  = W; canvas.height = H;
  canvas.style.width = W+'px'; canvas.style.height = H+'px';

  const ctx = canvas.getContext('2d');

  // Fondo
  const bg = ctx.createRadialGradient(W/2,H*0.55,0,W/2,H*0.55,W*0.7);
  bg.addColorStop(0,'#141428'); bg.addColorStop(1,'#04040c');
  ctx.fillStyle = bg; ctx.fillRect(0,0,W,H);

  // Estrellas
  drawStars(ctx, W, H);

  // Suelo isométrico
  const cx = W/2, cy = H*0.58;
  drawGround(ctx, cx, cy, W);

  // Muralla exterior
  const mLvl = Number(c.MURALLA||0);
  if (mLvl > 0) drawWall(ctx, cx, cy, mLvl);

  // Edificios — posiciones relativas al centro isométrico
  const buildings = getBuildingLayout(c, cx, cy);
  // Ordenar por Y para pintado correcto (painter's algorithm)
  buildings.sort((a,b) => a.y - b.y);
  buildings.forEach(b => drawBuilding(ctx, b));

  // Luz ambiental central
  const glow = ctx.createRadialGradient(cx, cy-60, 5, cx, cy-60, 120);
  glow.addColorStop(0,'rgba(80,120,255,0.12)');
  glow.addColorStop(1,'rgba(80,120,255,0)');
  ctx.fillStyle = glow;
  ctx.beginPath(); ctx.arc(cx, cy-60, 120, 0, Math.PI*2); ctx.fill();
}

function drawStars(ctx, W, H) {
  ctx.fillStyle = 'rgba(255,255,255,0.6)';
  for (let i=0; i<80; i++) {
    const x = (Math.sin(i*137.5)*0.5+0.5)*W;
    const y = (Math.cos(i*97.3)*0.5+0.5)*H*0.5;
    const r = i%7===0 ? 1.2 : 0.5;
    ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
  }
}

function drawGround(ctx, cx, cy, W) {
  const tw=56, th=28, cols=16, rows=12;
  for (let r=0; r<rows; r++) {
    for (let col=0; col<cols; col++) {
      const x = cx + (col-cols/2)*tw/2 - (r-rows/2)*tw/2;
      const y = cy + (col-cols/2)*th/2 + (r-rows/2)*th/2;
      const base = (col+r)%2===0 ? 30 : 22;
      ctx.fillStyle = `rgb(${base},${base+8},${base})`;
      ctx.beginPath();
      ctx.moveTo(x, y-th/2); ctx.lineTo(x+tw/2, y);
      ctx.lineTo(x, y+th/2); ctx.lineTo(x-tw/2, y);
      ctx.closePath(); ctx.fill();
      ctx.strokeStyle='rgba(0,0,0,0.3)'; ctx.lineWidth=0.4; ctx.stroke();
    }
  }
}

function drawWall(ctx, cx, cy, lvl) {
  const r = 170 + lvl*0.5;
  const h = 12 + lvl*0.3;
  const pts = [
    [cx, cy - r*0.5],
    [cx + r*0.6, cy],
    [cx, cy + r*0.5],
    [cx - r*0.6, cy]
  ];
  // Sombra
  ctx.strokeStyle = `rgba(60,80,100,0.4)`;
  ctx.lineWidth = h*0.6;
  ctx.beginPath();
  pts.forEach((p,i) => i===0 ? ctx.moveTo(p[0],p[1]) : ctx.lineTo(p[0],p[1]));
  ctx.closePath(); ctx.stroke();
  // Muralla
  ctx.strokeStyle = `rgb(${50+lvl},${60+lvl},${80+lvl})`;
  ctx.lineWidth = h*0.4;
  ctx.stroke();
  // Almenas
  ctx.fillStyle = `rgb(${55+lvl},${65+lvl},${85+lvl})`;
  for (let i=0; i<24; i++) {
    const t = i/24;
    const idx = Math.floor(t*4);
    const frac = (t*4) % 1;
    const p0 = pts[idx], p1 = pts[(idx+1)%4];
    const bx = p0[0] + (p1[0]-p0[0])*frac;
    const by = p0[1] + (p1[1]-p0[1])*frac;
    ctx.fillRect(bx-3, by-h*0.5-4, 5, 4);
  }
}

function getBuildingLayout(c, cx, cy) {
  const lvl = k => Number(c[k]||0);
  return [
    // Centro de Ciudad — centro
    { key:'CENTRO_DE_CIUDAD', label:'Centro Ciudad', lvl:lvl('CENTRO_DE_CIUDAD'),
      x:cx, y:cy-20, type:'cityhall', color:['#3a5080','#253560','#4a68a8'] },
    // Casa — izquierda
    { key:'CASA', label:'Casa', lvl:lvl('CASA'),
      x:cx-120, y:cy-10, type:'house', color:['#4a3820','#2e2010','#6a5030'] },
    // Torre de Vigilancia — derecha arriba
    { key:'TORRE_DE_VIGILANCIA', label:'Torre Vig.', lvl:lvl('TORRE_DE_VIGILANCIA'),
      x:cx+130, y:cy-40, type:'tower', color:['#304050','#1e2e3a','#405870'] },
    // Centro de Viajes — izq arriba
    { key:'CENTRO_DE_VIAJES', label:'C. Viajes', lvl:lvl('CENTRO_DE_VIAJES'),
      x:cx-90, y:cy-60, type:'travel', color:['#303860','#1e2448','#4048a0'] },
    // Escondite — derecha abajo
    { key:'ESCONDITE', label:'Escondite', lvl:lvl('ESCONDITE'),
      x:cx+100, y:cy+30, type:'hideout', color:['#2a3020','#181e10','#3a4030'] },
    // Almacén — izq abajo
    { key:'ALMACEN', label:'Almacén', lvl:lvl('ALMACEN'),
      x:cx-110, y:cy+40, type:'warehouse', color:['#503010','#382008','#705020'] },
    // Santuario Arcano — arriba centro
    { key:'SANTUARIO_ARCANO', label:'Santuario', lvl:lvl('SANTUARIO_ARCANO'),
      x:cx+30, y:cy-90, type:'sanctuary', color:['#402060','#280e48','#6030a0'] },
    // Universidad — arr izq
    { key:'UNIVERSIDAD', label:'Universidad', lvl:lvl('UNIVERSIDAD'),
      x:cx-50, y:cy-80, type:'university', color:['#203850','#102438','#305878'] },
    // Herrería — abajo der
    { key:'HERRERIA', label:'Herrería', lvl:lvl('HERRERIA'),
      x:cx+60, y:cy+50, type:'forge', color:['#502010','#380e04','#803020'] },
    // Templo 1 — der centro
    { key:'TEMPLO_1', label:'Templo 1', lvl:lvl('TEMPLO_1'),
      x:cx+70, y:cy-60, type:'temple', color:['#403000','#2c2000','#806000'] },
    // Templo 2 — der centro+
    { key:'TEMPLO_2', label:'Templo 2', lvl:lvl('TEMPLO_2'),
      x:cx+90, y:cy-20, type:'temple', color:['#403800','#2c2800','#807000'] },
    // Templo 3 — der abajo
    { key:'TEMPLO_3', label:'Templo 3', lvl:lvl('TEMPLO_3'),
      x:cx+50, y:cy+10, type:'temple', color:['#3a2800','#281800','#705000'] },
    // Cuartel 1 — izq centro
    { key:'CUARTEL_1', label:'Cuartel 1', lvl:lvl('CUARTEL_1'),
      x:cx-60, y:cy+10, type:'barracks', color:['#302020','#201010','#503030'] },
    // Cuartel 2 — izq abajo
    { key:'CUARTEL_2', label:'Cuartel 2', lvl:lvl('CUARTEL_2'),
      x:cx-30, y:cy+50, type:'barracks', color:['#282020','#180e0e','#483030'] },
  ];
}

function drawBuilding(ctx, b) {
  const lvl   = b.lvl || 0;
  const scale = 0.4 + Math.min(lvl, 50) * 0.016; // escala 0.4 (nv0) → 1.2 (nv50)
  const w     = 36 * scale;
  const h     = (40 + lvl * 1.2) * scale;
  const x = b.x, y = b.y;
  const [tc, lc, rc] = b.color;

  // Sombra
  ctx.fillStyle = 'rgba(0,0,0,0.25)';
  ctx.beginPath();
  ctx.ellipse(x, y + h*0.3, w*0.9, w*0.3, 0, 0, Math.PI*2);
  ctx.fill();

  switch(b.type) {
    case 'cityhall':   drawTowerGroup(ctx, x, y, w, h, tc, lc, rc, 3, lvl); break;
    case 'temple':     drawTemple(ctx, x, y, w, h, tc, lc, rc, lvl); break;
    case 'sanctuary':  drawSanctuary(ctx, x, y, w, h, tc, lc, rc, lvl); break;
    case 'tower':      drawSingleTower(ctx, x, y, w*0.6, h*1.4, tc, lc, rc); break;
    case 'barracks':   drawBarracks(ctx, x, y, w, h, tc, lc, rc); break;
    case 'forge':      drawForge(ctx, x, y, w, h, tc, lc, rc, lvl); break;
    default:           drawBlock(ctx, x, y, w, h, tc, lc, rc); break;
  }

  // Etiqueta nivel
  drawLabel(ctx, x, y + h*0.35, b.label, lvl);
}

function isoBlock(ctx, x, y, w, h, tc, lc, rc) {
  const hw=w/2, qh=w/4;
  // Top
  ctx.fillStyle=tc;
  ctx.beginPath();
  ctx.moveTo(x,y-h); ctx.lineTo(x+hw,y-h+qh);
  ctx.lineTo(x,y-h+qh*2); ctx.lineTo(x-hw,y-h+qh);
  ctx.closePath(); ctx.fill();
  // Left
  ctx.fillStyle=lc;
  ctx.beginPath();
  ctx.moveTo(x-hw,y-h+qh); ctx.lineTo(x,y-h+qh*2);
  ctx.lineTo(x,y); ctx.lineTo(x-hw,y-qh);
  ctx.closePath(); ctx.fill();
  // Right
  ctx.fillStyle=rc;
  ctx.beginPath();
  ctx.moveTo(x,y-h+qh*2); ctx.lineTo(x+hw,y-h+qh);
  ctx.lineTo(x+hw,y-qh); ctx.lineTo(x,y);
  ctx.closePath(); ctx.fill();
  // Borde
  ctx.strokeStyle='rgba(0,0,0,0.4)'; ctx.lineWidth=0.5;
  ctx.beginPath();
  ctx.moveTo(x,y-h); ctx.lineTo(x+hw,y-h+qh); ctx.lineTo(x+hw,y-qh);
  ctx.lineTo(x,y); ctx.lineTo(x-hw,y-qh); ctx.lineTo(x-hw,y-h+qh); ctx.closePath();
  ctx.stroke();
}

function drawBlock(ctx, x, y, w, h, tc, lc, rc) { isoBlock(ctx,x,y,w,h,tc,lc,rc); }

function drawTowerGroup(ctx, x, y, w, h, tc, lc, rc, n, lvl) {
  // Torres laterales
  isoBlock(ctx, x-w*0.6, y+h*0.1, w*0.55, h*0.7, lc, shadeColor(lc,-20), shadeColor(rc,-10));
  isoBlock(ctx, x+w*0.6, y+h*0.1, w*0.55, h*0.7, rc, shadeColor(lc,-20), shadeColor(rc,-10));
  // Torre central
  isoBlock(ctx, x, y, w, h, tc, lc, rc);
  // Punta brillante
  if (lvl >= 10) {
    const glow = ctx.createRadialGradient(x, y-h, 2, x, y-h, 20);
    glow.addColorStop(0,'rgba(150,200,255,0.8)');
    glow.addColorStop(1,'rgba(150,200,255,0)');
    ctx.fillStyle = glow;
    ctx.beginPath(); ctx.arc(x, y-h, 20, 0, Math.PI*2); ctx.fill();
  }
}

function drawTemple(ctx, x, y, w, h, tc, lc, rc, lvl) {
  isoBlock(ctx, x, y, w, h*0.6, lc, shadeColor(lc,-30), shadeColor(rc,-10));
  // Aguja
  ctx.fillStyle = tc;
  ctx.beginPath();
  ctx.moveTo(x, y-h); ctx.lineTo(x+w*0.25, y-h*0.6); ctx.lineTo(x-w*0.25, y-h*0.6);
  ctx.closePath(); ctx.fill();
  if (lvl >= 5) {
    const g = ctx.createRadialGradient(x,y-h,1,x,y-h,15);
    g.addColorStop(0,'rgba(255,200,50,0.7)'); g.addColorStop(1,'rgba(255,200,50,0)');
    ctx.fillStyle=g; ctx.beginPath(); ctx.arc(x,y-h,15,0,Math.PI*2); ctx.fill();
  }
}

function drawSanctuary(ctx, x, y, w, h, tc, lc, rc, lvl) {
  isoBlock(ctx, x, y, w*0.8, h*0.5, lc, shadeColor(lc,-30), shadeColor(rc,-10));
  // Cúpula
  ctx.fillStyle = tc;
  ctx.beginPath(); ctx.ellipse(x, y-h*0.5, w*0.5, h*0.5, 0, Math.PI, 0); ctx.fill();
  ctx.fillStyle = shadeColor(rc, 20);
  ctx.beginPath(); ctx.ellipse(x, y-h*0.5, w*0.3, h*0.35, 0, Math.PI, 0); ctx.fill();
  if (lvl >= 10) {
    // Partículas de maná
    for (let i=0; i<5; i++) {
      const px = x + Math.sin(i*1.26)*w*0.4;
      const py = y - h*0.6 - i*4;
      ctx.fillStyle = `rgba(120,60,220,${0.6-i*0.1})`;
      ctx.beginPath(); ctx.arc(px,py,2,0,Math.PI*2); ctx.fill();
    }
  }
}

function drawSingleTower(ctx, x, y, w, h, tc, lc, rc) {
  isoBlock(ctx, x, y, w, h, tc, lc, rc);
  // Almenas
  ctx.fillStyle = shadeColor(tc, 20);
  for (let i=-1; i<=1; i++) {
    ctx.fillRect(x + i*w*0.3 - 3, y-h-6, 5, 6);
  }
}

function drawBarracks(ctx, x, y, w, h, tc, lc, rc) {
  isoBlock(ctx, x, y, w, h*0.7, tc, lc, rc);
  // Techo
  ctx.fillStyle = shadeColor(tc, -20);
  ctx.beginPath();
  ctx.moveTo(x-w*0.6, y-h*0.7+w*0.25);
  ctx.lineTo(x, y-h);
  ctx.lineTo(x+w*0.6, y-h*0.7+w*0.25);
  ctx.closePath(); ctx.fill();
}

function drawForge(ctx, x, y, w, h, tc, lc, rc, lvl) {
  isoBlock(ctx, x, y, w, h*0.6, tc, lc, rc);
  // Chimenea
  isoBlock(ctx, x+w*0.2, y-h*0.55, w*0.25, h*0.4, shadeColor(tc,10), shadeColor(lc,10), shadeColor(rc,10));
  if (lvl > 0) {
    // Brasas
    ctx.fillStyle = 'rgba(255,100,20,0.5)';
    ctx.beginPath(); ctx.arc(x+w*0.2, y-h*0.9, 5, 0, Math.PI*2); ctx.fill();
  }
}

function drawLabel(ctx, x, y, text, lvl) {
  const label = lvl > 0 ? `${text} Nv.${lvl}` : `${text} —`;
  ctx.save();
  const tw = ctx.measureText(label).width + 12;
  ctx.fillStyle = 'rgba(8,8,18,0.85)';
  ctx.strokeStyle = lvl > 0 ? 'rgba(180,150,60,0.6)' : 'rgba(60,60,80,0.5)';
  ctx.lineWidth = 0.8;
  roundRect(ctx, x-tw/2, y-9, tw, 16, 3);
  ctx.fill(); ctx.stroke();
  ctx.fillStyle = lvl > 0 ? '#c9a84c' : '#555570';
  ctx.font = '9px Rajdhani, sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(label, x, y);
  ctx.restore();
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x+r,y); ctx.lineTo(x+w-r,y);
  ctx.arcTo(x+w,y,x+w,y+r,r);
  ctx.lineTo(x+w,y+h-r); ctx.arcTo(x+w,y+h,x+w-r,y+h,r);
  ctx.lineTo(x+r,y+h); ctx.arcTo(x,y+h,x,y+h-r,r);
  ctx.lineTo(x,y+r); ctx.arcTo(x,y,x+r,y,r);
  ctx.closePath();
}

function shadeColor(hex, pct) {
  const n = parseInt(hex.replace('#',''),16);
  const r = Math.min(255,Math.max(0,((n>>16)&0xff)+pct));
  const g = Math.min(255,Math.max(0,((n>>8)&0xff)+pct));
  const b = Math.min(255,Math.max(0,(n&0xff)+pct));
  return `rgb(${r},${g},${b})`;
}
'''

p = BASE / "js/screens/city.js"
p.write_text(city_js, encoding="utf-8")
print("OK js/screens/city.js")
print("\n✅ Listo. Recarga el navegador.")
