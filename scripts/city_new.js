/* Pantalla CIUDAD — Eternal Warriors v3.0 */
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
    [1e48,'Qd'],[1e45,'Td'],[1e42,'Dd'],[1e39,'Nd'],
    [1e36,'Ud'],[1e33,'Dc'],[1e30,'No'],[1e27,'Oc'],
    [1e24,'Sp'],[1e21,'Sx'],[1e18,'Qi'],[1e15,'Q'],
    [1e12,'T'],[1e9,'B'],[1e6,'M'],[1e3,'K']
  ];
  for (const [d, sfx] of tiers) {
    if (abs >= d) {
      const v = abs/d;
      return s + (v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(1) : v.toFixed(2)) + sfx;
    }
  }
  if (abs >= 1e51) {
    const e = Math.floor(Math.log10(abs));
    return s + (abs / Math.pow(10, e)).toFixed(1) + 'e' + e;
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

// ═══════════════════════════════════════════════════════════════════════════════
// SISTEMA DE COORDENADAS
// ─────────────────────────────────────────────────────────────────────────────
// La muralla define el espacio jugable. Sus 4 vértices en pantalla:
//   N = (cx,    cy-RY)   — esquina superior (fondo)
//   E = (cx+RX, cy)      — esquina derecha
//   S = (cx,    cy+RY)   — esquina inferior (frente)
//   W = (cx-RX, cy)      — esquina izquierda
//
// Conversión isométrica: un punto (u,v) en espacio "mundo" donde
//   u = eje derecha-izquierda, v = eje frente-fondo
// se proyecta como:
//   px = cx + u
//   py = cy + v * 0.5    (aplastamiento isométrico 2:1)
//
// TODOS los sistemas (muralla, terreno, edificios) usan esta misma función.
// ═══════════════════════════════════════════════════════════════════════════════

let animFrame = null;
let tick = 0;

// RX y RY son el radio del rombo de la muralla en pantalla
// A nivel 40: RX=160, RY=80 (ratio 2:1 isométrico perfecto)
function wallRadius(lvl) {
  const s = 1 + Math.min(lvl, 50) * 0.006;
  return { rx: 160 * s, ry: 80 * s };
}

function drawCity(c) {
  const canvas = document.getElementById('city-canvas');
  const wrap   = document.getElementById('city-wrap');
  if (!canvas || !wrap) return;
  const W = wrap.clientWidth, H = wrap.clientHeight;
  if (W < 10 || H < 10) { setTimeout(() => drawCity(c), 50); return; }
  canvas.width = W; canvas.height = H;
  canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
  if (animFrame) cancelAnimationFrame(animFrame);
  function loop() { tick++; renderFrame(canvas, W, H, c); animFrame = requestAnimationFrame(loop); }
  loop();
}

function renderFrame(canvas, W, H, c) {
  const ctx = canvas.getContext('2d');
  // cy más bajo = más espacio para la torre del C.Ciudad que sube hacia arriba
  const cx = W * 0.5, cy = H * 0.64;
  const mLvl = Number(c.MURALLA || 0);
  const { rx, ry } = wallRadius(mLvl);

  // Cielo
  const sky = ctx.createLinearGradient(0, 0, 0, H);
  sky.addColorStop(0, '#010106'); sky.addColorStop(0.6, '#06060f'); sky.addColorStop(1, '#0a0a1a');
  ctx.fillStyle = sky; ctx.fillRect(0, 0, W, H);

  drawStars(ctx, W, H);
  drawMoon(ctx, W * 0.84, H * 0.10);
  drawMist(ctx, W, H, cx, cy);
  drawTerrain(ctx, cx, cy, rx, ry);
  if (mLvl > 0) drawWall(ctx, cx, cy, rx, ry, mLvl);
  drawFloor(ctx, cx, cy, rx, ry);

  // Edificios — ordenados por Y (painter's algorithm)
  const layout = getLayout(c, cx, cy, rx, ry);
  layout.sort((a, b) => a.y - b.y);
  layout.forEach(b => drawBuilding(ctx, b));

  drawParticles(ctx, cx, cy, c);
}

// ─── TERRENO ─────────────────────────────────────────────────────────────────
function drawTerrain(ctx, cx, cy, rx, ry) {
  // Dibuja tiles dentro del rombo definido por rx, ry
  const cols = 12, rows = 12;
  const tw = (rx * 2) / cols, th = (ry * 2) / rows;
  for (let r = 0; r < rows; r++) {
    for (let col = 0; col < cols; col++) {
      // Centro de la celda en coordenadas isométricas
      const u = (col - cols / 2 + 0.5) * tw;
      const v = (r  - rows / 2 + 0.5) * th;
      // Filtro rombo: |u/rx| + |v/ry| <= 1
      if (Math.abs(u / rx) + Math.abs(v / ry) > 0.96) continue;
      const px = cx + u;
      const py = cy + v * 0.5;
      const even = (col + r) % 2 === 0;
      ctx.fillStyle = even ? '#1c2418' : '#182014';
      ctx.beginPath();
      ctx.moveTo(px,           py - th * 0.25);
      ctx.lineTo(px + tw * 0.5, py);
      ctx.lineTo(px,           py + th * 0.25);
      ctx.lineTo(px - tw * 0.5, py);
      ctx.closePath(); ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,0.4)'; ctx.lineWidth = 0.5; ctx.stroke();
    }
  }
}

// ─── SUELO INTERIOR (plazoleta empedrada) ────────────────────────────────────
function drawFloor(ctx, cx, cy, rx, ry) {
  // Radio interior: 60% del rombo
  const irx = rx * 0.62, iry = ry * 0.62;
  const cols = 8, rows = 8;
  const tw = (irx * 2) / cols, th = (iry * 2) / rows;
  for (let r = 0; r < rows; r++) {
    for (let col = 0; col < cols; col++) {
      const u = (col - cols / 2 + 0.5) * tw;
      const v = (r  - rows / 2 + 0.5) * th;
      if (Math.abs(u / irx) + Math.abs(v / iry) > 0.92) continue;
      const px = cx + u;
      const py = cy + v * 0.5;
      const even = (col + r) % 2 === 0;
      ctx.fillStyle = even ? '#1a1a24' : '#161620';
      ctx.beginPath();
      ctx.moveTo(px,            py - th * 0.25);
      ctx.lineTo(px + tw * 0.5, py);
      ctx.lineTo(px,            py + th * 0.25);
      ctx.lineTo(px - tw * 0.5, py);
      ctx.closePath(); ctx.fill();
      ctx.strokeStyle = 'rgba(180,150,60,0.12)'; ctx.lineWidth = 0.5; ctx.stroke();
    }
  }

  // Caminos diagonales desde el centro a las esquinas
  ctx.save();
  const paths = [
    [cx, cy, cx - irx * 0.7, cy],
    [cx, cy, cx + irx * 0.7, cy],
    [cx, cy, cx, cy - iry * 0.6],
    [cx, cy, cx, cy + iry * 0.6],
  ];
  paths.forEach(([x1, y1, x2, y2]) => {
    const g = ctx.createLinearGradient(x1, y1, x2, y2);
    g.addColorStop(0, 'rgba(120,100,60,0.4)');
    g.addColorStop(1, 'rgba(80,65,40,0.1)');
    ctx.strokeStyle = g; ctx.lineWidth = 6;
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
    ctx.strokeStyle = 'rgba(160,130,70,0.15)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
  });
  ctx.restore();
}

// ─── MURALLA ─────────────────────────────────────────────────────────────────
function drawWall(ctx, cx, cy, rx, ry, lvl) {
  // Los 4 vértices del rombo en pantalla
  const N = [cx,      cy - ry];
  const E = [cx + rx, cy     ];
  const S = [cx,      cy + ry];
  const W = [cx - rx, cy     ];
  const pts = [N, E, S, W];
  const wallH = 18 + lvl * 0.25;
  const wallC = `rgb(${52 + lvl}, ${58 + lvl}, ${74 + lvl})`;
  const wallD = `rgb(${35 + lvl}, ${40 + lvl}, ${52 + lvl})`;

  // Cara inferior de la muralla (sombra/volumen)
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
  ctx.closePath(); ctx.stroke();

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
  }

  // Torres en los 4 vértices
  pts.forEach(([px, py]) => drawWallTower(ctx, px, py, wallH, lvl));
}

function drawWallTower(ctx, x, y, wallH, lvl) {
  const tw = 14 + lvl * 0.15, th = 26 + lvl * 0.28;
  const tc = `rgb(${58 + lvl}, ${64 + lvl}, ${82 + lvl})`;
  // Base
  ctx.fillStyle = tc;
  ctx.beginPath();
  ctx.moveTo(x, y - th); ctx.lineTo(x + tw * 0.5, y - th + tw * 0.25);
  ctx.lineTo(x + tw * 0.5, y + tw * 0.25); ctx.lineTo(x, y + tw * 0.5);
  ctx.lineTo(x - tw * 0.5, y + tw * 0.25); ctx.lineTo(x - tw * 0.5, y - th + tw * 0.25);
  ctx.closePath(); ctx.fill();
  ctx.strokeStyle = 'rgba(0,0,0,0.4)'; ctx.lineWidth = 0.8; ctx.stroke();
  // Techo cónico
  ctx.fillStyle = `rgb(${70 + lvl}, ${76 + lvl}, ${96 + lvl})`;
  ctx.beginPath();
  ctx.moveTo(x, y - th - 10); ctx.lineTo(x + tw * 0.5, y - th + tw * 0.25);
  ctx.lineTo(x - tw * 0.5, y - th + tw * 0.25); ctx.closePath(); ctx.fill();
  // Ventana con luz
  const wAlpha = 0.3 + 0.2 * Math.sin(tick * 0.05 + x);
  ctx.fillStyle = `rgba(255,200,80,${wAlpha})`;
  ctx.fillRect(x - 3, y - th * 0.55, 6, 5);
}

// ─── LAYOUT DE EDIFICIOS ──────────────────────────────────────────────────────
// Todos los edificios se posicionan con coordenadas (ox, ov) donde:
//   ox = offset horizontal en pantalla desde cx
//   ov = offset isométrico vertical (se convierte: py = cy + ov * 0.5)
// Esto garantiza que todos siguen la misma proyección 2:1.
function getLayout(c, cx, cy, rx, ry) {
  const lv = k => Number(c[k] || 0);

  // iso(ox, ov): offset horizontal + offset profundidad isométrica
  const pos = (ox, ov) => ({ x: cx + ox, y: cy + ov * 0.5 });

  const b = (ox, ov, key, label, type, extra = {}) => {
    const { x, y } = pos(ox, ov);
    return { key, label, lvl: lv(key), x, y, type, ...extra };
  };

  // Espaciado basado en rx/ry reales de la muralla
  // rx≈160, ry≈80 a nivel 40. Edificios dentro del 85% de ese espacio.
  const ix = rx * 0.82;  // radio interior X disponible
  const iy = ry * 0.82;  // radio interior Y disponible (en coord. mundo, *2 para pantalla)

  return [
    // ── C.Ciudad: cuadrante superior, edificio focal ──────────────────────────
    b(      0,  -iy*0.65, 'CENTRO_DE_CIUDAD', 'C.Ciudad',      'cityhall'),

    // ── Segundo plano: santuario y templos de la dualidad ────────────────────
    b( -ix*0.38, -iy*0.30, 'SANTUARIO_ARCANO', 'Santuario',     'sanctuary'),
    b( +ix*0.38, -iy*0.30, 'TEMPLO_3',         'Templo Luz',    'temple',   { accent: '#7ec8e3' }),

    // ── Plano medio: universidad, torre, templos ──────────────────────────────
    b( -ix*0.72,  -iy*0.05, 'UNIVERSIDAD',      'Universidad',   'university'),
    b( -ix*0.25,  +iy*0.05, 'TEMPLO_1',         'Templo Tierra', 'temple',   { accent: '#8a9040' }),
    b( +ix*0.25,  +iy*0.05, 'TORRE_DE_VIGILANCIA','Torre',        'watchtower'),
    b( +ix*0.72,  -iy*0.05, 'TEMPLO_2',         'Templo Guerra', 'temple',   { accent: '#c0452a' }),

    // ── Plano medio-bajo: almacén y viajes ────────────────────────────────────
    b( -ix*0.72,  +iy*0.30, 'ALMACEN',          'Almacén',       'warehouse'),
    b( +ix*0.72,  +iy*0.30, 'CENTRO_DE_VIAJES', 'C.Viajes',      'travel'),

    // ── Primer plano ──────────────────────────────────────────────────────────
    b( -ix*0.60,  +iy*0.65, 'CASA',             'Casa',          'house'),
    b( -ix*0.22,  +iy*0.65, 'CUARTEL_1',        'Cuartel 1',     'barracks'),
    b( +ix*0.22,  +iy*0.65, 'HERRERIA',         'Herrería',      'forge'),
    b( +ix*0.60,  +iy*0.65, 'CUARTEL_2',        'Cuartel 2',     'barracks'),

    // ── Frente ────────────────────────────────────────────────────────────────
    b(      0,   +iy*0.90, 'ESCONDITE',        'Escondite',     'hideout'),
  ];
}

// ─── DISPATCHER DE EDIFICIOS ──────────────────────────────────────────────────
function drawBuilding(ctx, b) {
  const lvl = b.lvl || 0;
  // Escala fija por tipo — independiente del nivel para coherencia visual
  const SC = {
    cityhall: 1.10, sanctuary: 0.72, temple: 0.68,
    university: 0.70, warehouse: 0.64, watchtower: 0.58,
    travel: 0.62, barracks: 0.60, forge: 0.58,
    house: 0.56, hideout: 0.50
  };
  const sc = SC[b.type] || 0.58;
  ctx.save();
  switch (b.type) {
    case 'cityhall':    drawCityHall(ctx, b.x, b.y, sc, lvl);            break;
    case 'house':       drawHouse(ctx, b.x, b.y, sc, lvl);               break;
    case 'watchtower':  drawWatchtower(ctx, b.x, b.y, sc, lvl);          break;
    case 'travel':      drawTravelCenter(ctx, b.x, b.y, sc, lvl);        break;
    case 'hideout':     drawHideout(ctx, b.x, b.y, sc, lvl);             break;
    case 'warehouse':   drawWarehouse(ctx, b.x, b.y, sc, lvl);           break;
    case 'sanctuary':   drawSanctuary(ctx, b.x, b.y, sc, lvl);           break;
    case 'university':  drawUniversity(ctx, b.x, b.y, sc, lvl);          break;
    case 'forge':       drawForge(ctx, b.x, b.y, sc, lvl);               break;
    case 'temple':      drawTemple(ctx, b.x, b.y, sc, lvl, b.accent || '#c8a000'); break;
    case 'barracks':    drawBarracks(ctx, b.x, b.y, sc, lvl);            break;
  }
  ctx.restore();
  drawLabel(ctx, b.x, b.y, b.label, lvl, b.type);
}

// ═══════════════════════════════════════════════════════════════════════════════
// HELPERS ISOMÉTRICOS
// ═══════════════════════════════════════════════════════════════════════════════

// isoBox: caja isométrica con 3 caras visibles (top, left, right)
// x,y = punto base inferior centro; w = ancho; h = altura
function isoBox(ctx, x, y, w, h, cTop, cLeft, cRight) {
  const hw = w / 2, qh = w / 4;
  // Cara superior
  ctx.fillStyle = cTop;
  ctx.beginPath();
  ctx.moveTo(x, y - h);
  ctx.lineTo(x + hw, y - h + qh);
  ctx.lineTo(x, y - h + qh * 2);
  ctx.lineTo(x - hw, y - h + qh);
  ctx.closePath(); ctx.fill();
  // Cara izquierda
  ctx.fillStyle = cLeft;
  ctx.beginPath();
  ctx.moveTo(x - hw, y - h + qh);
  ctx.lineTo(x, y - h + qh * 2);
  ctx.lineTo(x, y);
  ctx.lineTo(x - hw, y - qh);
  ctx.closePath(); ctx.fill();
  // Cara derecha
  ctx.fillStyle = cRight;
  ctx.beginPath();
  ctx.moveTo(x, y - h + qh * 2);
  ctx.lineTo(x + hw, y - h + qh);
  ctx.lineTo(x + hw, y - qh);
  ctx.lineTo(x, y);
  ctx.closePath(); ctx.fill();
  // Contorno
  ctx.strokeStyle = 'rgba(0,0,0,0.55)'; ctx.lineWidth = 0.7;
  ctx.beginPath();
  ctx.moveTo(x, y - h);
  ctx.lineTo(x + hw, y - h + qh); ctx.lineTo(x + hw, y - qh);
  ctx.lineTo(x, y); ctx.lineTo(x - hw, y - qh); ctx.lineTo(x - hw, y - h + qh);
  ctx.closePath(); ctx.stroke();
}

function glow(ctx, x, y, r, hexColor) {
  // hexColor debe ser '#rrggbb' o 'rgb(r,g,b)'
  let r2, g2, b2;
  if (hexColor.startsWith('#')) {
    const v = parseInt(hexColor.slice(1), 16);
    r2 = (v >> 16) & 255; g2 = (v >> 8) & 255; b2 = v & 255;
  } else {
    const m = hexColor.match(/\d+/g);
    r2 = +m[0]; g2 = +m[1]; b2 = +m[2];
  }
  const gr = ctx.createRadialGradient(x, y, 1, x, y, r);
  gr.addColorStop(0, `rgba(${r2},${g2},${b2},0.55)`);
  gr.addColorStop(1, `rgba(${r2},${g2},${b2},0)`);
  ctx.fillStyle = gr;
  ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
}

function drawLabel(ctx, x, y, text, lvl, type) {
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
}

function rr(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y); ctx.lineTo(x + w - r, y); ctx.arcTo(x + w, y, x + w, y + r, r);
  ctx.lineTo(x + w, y + h - r); ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
  ctx.lineTo(x + r, y + h); ctx.arcTo(x, y + h, x, y + h - r, r);
  ctx.lineTo(x, y + r); ctx.arcTo(x, y, x + r, y, r); ctx.closePath();
}

// ═══════════════════════════════════════════════════════════════════════════════
// AMBIENTE
// ═══════════════════════════════════════════════════════════════════════════════
function drawStars(ctx, W, H) {
  for (let i = 0; i < 130; i++) {
    const x = (Math.sin(i * 137.508) * 0.5 + 0.5) * W;
    const y = (Math.cos(i * 97.3) * 0.5 + 0.5) * H * 0.48;
    const br = 0.3 + 0.7 * Math.abs(Math.sin(tick * 0.01 + i));
    const r = i % 11 === 0 ? 1.6 : 0.7;
    ctx.fillStyle = `rgba(255,255,240,${br * 0.75})`;
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
  }
}

function drawMoon(ctx, x, y) {
  const g = ctx.createRadialGradient(x, y, 2, x, y, 38);
  g.addColorStop(0, 'rgba(220,210,180,0.92)');
  g.addColorStop(0.6, 'rgba(180,170,140,0.4)');
  g.addColorStop(1, 'rgba(180,170,140,0)');
  ctx.fillStyle = g;
  ctx.beginPath(); ctx.arc(x, y, 38, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = 'rgba(200,190,160,0.65)';
  ctx.beginPath(); ctx.arc(x, y, 20, 0, Math.PI * 2); ctx.fill();
}

function drawMist(ctx, W, H, cx, cy) {
  for (let i = 0; i < 3; i++) {
    const g = ctx.createRadialGradient(cx, cy + i * 22, 10, cx, cy + i * 22, W * 0.5);
    g.addColorStop(0, `rgba(${18 + i * 4},${22 + i * 4},${44 + i * 8},0.14)`);
    g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }
}

function drawParticles(ctx, cx, cy, c) {
  const mana = Number(c.MANA || 0);
  if (mana < 1000) return;
  const count = Math.min(22, Math.floor(Math.log10(mana) * 3));
  for (let i = 0; i < count; i++) {
    const angle = (i / count) * Math.PI * 2 + tick * 0.008;
    const r = 55 + 22 * Math.sin(tick * 0.02 + i);
    const px = cx + Math.cos(angle) * r;
    const py = cy - 15 + Math.sin(angle) * r * 0.4;
    const alpha = 0.18 + 0.18 * Math.abs(Math.sin(tick * 0.04 + i));
    ctx.fillStyle = `rgba(140,70,255,${alpha})`;
    ctx.beginPath(); ctx.arc(px, py, 2, 0, Math.PI * 2); ctx.fill();
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EDIFICIOS
// ═══════════════════════════════════════════════════════════════════════════════

function drawCityHall(ctx, x, y, sc, lvl) {
  const w = 72 * sc, h = 110 * sc;
  // Plataforma escalonada
  isoBox(ctx, x, y, w * 1.3, h * 0.08, '#1a2440', '#101828', '#223058');
  isoBox(ctx, x, y - h * 0.06, w * 1.1, h * 0.10, '#1e2a4a', '#14203a', '#283868');
  // Alas laterales simétricas
  isoBox(ctx, x - w * 0.52, y - h * 0.12, w * 0.44, h * 0.58, '#223268', '#16224e', '#2c3e80');
  isoBox(ctx, x + w * 0.52, y - h * 0.12, w * 0.44, h * 0.58, '#223268', '#16224e', '#2c3e80');
  // Torre central — la más alta y dominante
  isoBox(ctx, x, y - h * 0.10, w * 0.52, h * 0.88, '#2e4888', '#1e3068', '#3a58a8');
  // Ventanas alas — luz azul fría
  for (let i = 0; i < 4; i++) {
    const wy = y - h * (0.22 + i * 0.13);
    const wc = `rgba(120,190,255,${0.4 + 0.18 * Math.sin(tick * 0.04 + i)})`;
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.fillRect(x - w * 0.68, wy, 8 * sc, 6 * sc);
    ctx.fillRect(x + w * 0.36, wy, 8 * sc, 6 * sc);
    ctx.fillStyle = wc;
    ctx.fillRect(x - w * 0.67, wy + 0.5, 6 * sc, 5 * sc);
    ctx.fillRect(x + w * 0.37, wy + 0.5, 6 * sc, 5 * sc);
  }
  // Ventanas arco torre central
  for (let i = 0; i < 5; i++) {
    const wy = y - h * (0.28 + i * 0.14);
    const wc = `rgba(160,220,255,${0.55 + 0.2 * Math.sin(tick * 0.05 + i)})`;
    ctx.fillStyle = 'rgba(0,0,0,0.55)';
    ctx.fillRect(x - 5 * sc, wy - 8 * sc, 10 * sc, 12 * sc);
    ctx.fillStyle = wc;
    ctx.fillRect(x - 4 * sc, wy - 7 * sc, 8 * sc, 10 * sc);
    ctx.fillStyle = wc;
    ctx.beginPath(); ctx.arc(x, wy - 7 * sc, 4 * sc, Math.PI, 0); ctx.fill();
  }
  // Pináculos alas
  [-w * 0.52, w * 0.52].forEach(ox => {
    isoBox(ctx, x + ox, y - h * 0.68, w * 0.14, h * 0.18, '#364e98', '#263878', '#4060b8');
    ctx.fillStyle = '#4468c8';
    ctx.beginPath();
    ctx.moveTo(x + ox, y - h * 0.92);
    ctx.lineTo(x + ox + 4 * sc, y - h * 0.86);
    ctx.lineTo(x + ox - 4 * sc, y - h * 0.86);
    ctx.closePath(); ctx.fill();
    glow(ctx, x + ox, y - h * 0.92, 10 * sc, '#4060c0');
  });
  // Torre central — aguja y orbe
  isoBox(ctx, x, y - h * 0.86, w * 0.20, h * 0.22, '#3a60a8', '#2a4888', '#4a70c0');
  ctx.fillStyle = '#5078d0';
  ctx.beginPath();
  ctx.moveTo(x, y - h * 1.18);
  ctx.lineTo(x + 7 * sc, y - h * 1.02);
  ctx.lineTo(x - 7 * sc, y - h * 1.02);
  ctx.closePath(); ctx.fill();
  // Haz de luz dorado — emblema de la capital
  const beam = ctx.createLinearGradient(x, y - h * 1.15, x, y - h * 2.4);
  beam.addColorStop(0, `rgba(180,210,255,${0.06 + 0.04 * Math.sin(tick * 0.05)})`);
  beam.addColorStop(1, 'rgba(180,210,255,0)');
  ctx.fillStyle = beam; ctx.fillRect(x - 8 * sc, y - h * 2.4, 16 * sc, h * 1.25);
  // Orbe cima
  glow(ctx, x, y - h * 1.19, 24 * sc, '#80b0ff');
  const op = 0.85 + 0.15 * Math.sin(tick * 0.07);
  ctx.fillStyle = `rgba(180,220,255,${op})`;
  ctx.beginPath(); ctx.arc(x, y - h * 1.19, 5 * sc, 0, Math.PI * 2); ctx.fill();
  // Bandera
  ctx.strokeStyle = '#5070a0'; ctx.lineWidth = 1.2;
  ctx.beginPath(); ctx.moveTo(x - w * 0.52, y - h * 0.66); ctx.lineTo(x - w * 0.52, y - h * 0.84); ctx.stroke();
  const fw = Math.sin(tick * 0.06) * 3 * sc;
  ctx.fillStyle = '#3a5898';
  ctx.beginPath();
  ctx.moveTo(x - w * 0.52, y - h * 0.84);
  ctx.lineTo(x - w * 0.52 + 14 * sc + fw, y - h * 0.79);
  ctx.lineTo(x - w * 0.52 + 12 * sc + fw * 0.7, y - h * 0.76);
  ctx.lineTo(x - w * 0.52, y - h * 0.76);
  ctx.closePath(); ctx.fill();
}

function drawSanctuary(ctx, x, y, sc, lvl) {
  const w = 50 * sc, h = 70 * sc;
  isoBox(ctx, x, y, w * 1.1, h * 0.14, '#300e50', '#200838', '#401868');
  for (let i = -1; i <= 1; i++) {
    isoBox(ctx, x + i * w * 0.36, y - h * 0.10, w * 0.14, h * 0.42, '#3c1060', '#280848', '#4c1878');
  }
  isoBox(ctx, x, y - h * 0.32, w * 0.76, h * 0.56, '#481278', '#300c58', '#582090');
  const dY = y - h * 0.88;
  ctx.fillStyle = '#5820a0';
  ctx.beginPath(); ctx.ellipse(x, dY, w * 0.40, h * 0.36, 0, Math.PI, 0); ctx.fill();
  ctx.fillStyle = '#7030c0';
  ctx.beginPath(); ctx.ellipse(x, dY, w * 0.26, h * 0.24, 0, Math.PI, 0); ctx.fill();
  ctx.strokeStyle = 'rgba(180,80,255,0.25)'; ctx.lineWidth = 0.8;
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI;
    ctx.beginPath(); ctx.moveTo(x, dY); ctx.lineTo(x + Math.cos(a) * w * 0.40, dY - Math.sin(a) * h * 0.18); ctx.stroke();
  }
  glow(ctx, x, dY - h * 0.12, 16 * sc, '#b050ff');
  ctx.fillStyle = `rgba(200,100,255,${0.7 + 0.25 * Math.sin(tick * 0.08)})`;
  ctx.beginPath(); ctx.arc(x, dY - h * 0.12, 5 * sc, 0, Math.PI * 2); ctx.fill();
  const orbN = Math.min(8, Math.floor(3 + lvl * 0.1));
  for (let i = 0; i < orbN; i++) {
    const a = (i / orbN) * Math.PI * 2 + tick * 0.025;
    const px = x + Math.cos(a) * w * 0.42, py = dY + Math.sin(a) * h * 0.14;
    glow(ctx, px, py, 5 * sc, '#a040f0');
    ctx.fillStyle = `rgba(190,110,255,${0.55 + 0.3 * Math.sin(tick * 0.06 + i)})`;
    ctx.beginPath(); ctx.arc(px, py, 2.5 * sc, 0, Math.PI * 2); ctx.fill();
  }
  ctx.fillStyle = '#8040d0';
  ctx.beginPath(); ctx.moveTo(x, dY - h * 0.52); ctx.lineTo(x + 5 * sc, dY - h * 0.38); ctx.lineTo(x - 5 * sc, dY - h * 0.38); ctx.closePath(); ctx.fill();
  glow(ctx, x, dY - h * 0.52, 16 * sc, '#c060ff');
}

function drawTemple(ctx, x, y, sc, lvl, accent) {
  const w = 46 * sc, h = 68 * sc;
  let r2, g2, b2;
  if (accent.startsWith('#')) {
    const v = parseInt(accent.slice(1), 16);
    r2 = (v >> 16) & 255; g2 = (v >> 8) & 255; b2 = v & 255;
  } else { const m = accent.match(/\d+/g); r2=+m[0]; g2=+m[1]; b2=+m[2]; }
  isoBox(ctx, x, y, w * 1.1, h * 0.10, `rgb(${r2*0.28},${g2*0.28},${b2*0.22})`, `rgb(${r2*0.18},${g2*0.18},${b2*0.14})`, `rgb(${r2*0.34},${g2*0.34},${b2*0.28})`);
  isoBox(ctx, x, y - h * 0.08, w, h * 0.18, `rgb(${r2*0.32},${g2*0.32},${b2*0.26})`, `rgb(${r2*0.22},${g2*0.22},${b2*0.16})`, `rgb(${r2*0.38},${g2*0.38},${b2*0.32})`);
  isoBox(ctx, x, y - h * 0.22, w * 0.80, h * 0.52, `rgb(${r2*0.42},${g2*0.38},${b2*0.28})`, `rgb(${r2*0.28},${g2*0.26},${b2*0.18})`, `rgb(${r2*0.52},${g2*0.46},${b2*0.36})`);
  // Columnas
  for (let i = -1; i <= 1; i++) {
    ctx.fillStyle = `rgba(${r2*0.5},${g2*0.5},${b2*0.3},0.8)`;
    ctx.fillRect(x + i * w * 0.26 - 3 * sc, y - h * 0.22, 5 * sc, h * 0.48);
    ctx.fillStyle = accent;
    ctx.fillRect(x + i * w * 0.26 - 5 * sc, y - h * 0.22, 9 * sc, 3 * sc);
  }
  // Aguja y orbe
  ctx.fillStyle = `rgb(${r2*0.55},${g2*0.5},${b2*0.36})`;
  ctx.beginPath(); ctx.moveTo(x, y - h * 1.02); ctx.lineTo(x + 7 * sc, y - h * 0.62); ctx.lineTo(x - 7 * sc, y - h * 0.62); ctx.closePath(); ctx.fill();
  ctx.strokeStyle = accent; ctx.lineWidth = 0.8; ctx.stroke();
  [-w * 0.28, w * 0.28].forEach(ox => {
    ctx.fillStyle = `rgb(${r2*0.46},${g2*0.42},${b2*0.28})`;
    ctx.beginPath(); ctx.moveTo(x+ox, y-h*0.76); ctx.lineTo(x+ox+4*sc, y-h*0.60); ctx.lineTo(x+ox-4*sc, y-h*0.60); ctx.closePath(); ctx.fill();
    glow(ctx, x+ox, y-h*0.77, 7*sc, accent);
    ctx.fillStyle = accent; ctx.beginPath(); ctx.arc(x+ox, y-h*0.77, 2.5*sc, 0, Math.PI*2); ctx.fill();
  });
  glow(ctx, x, y - h * 1.03, 16 * sc, accent);
  ctx.fillStyle = `rgba(${r2},${g2},${b2},${0.85 + 0.15*Math.sin(tick*0.08)})`;
  ctx.beginPath(); ctx.arc(x, y - h * 1.03, 4*sc, 0, Math.PI*2); ctx.fill();
}

function drawHouse(ctx, x, y, sc, lvl) {
  const w = 50 * sc, h = 36 * sc, rH = 20 * sc;
  isoBox(ctx, x, y, w, h, '#5a4428', '#3c2c18', '#726038');
  ctx.fillStyle = '#4a3420';
  ctx.beginPath(); ctx.moveTo(x, y-h-rH); ctx.lineTo(x+w*0.58, y-h+w*0.14); ctx.lineTo(x-w*0.58, y-h+w*0.14); ctx.closePath(); ctx.fill();
  ctx.strokeStyle = '#2e1e10'; ctx.lineWidth = 0.8; ctx.stroke();
  ctx.strokeStyle = 'rgba(0,0,0,0.22)'; ctx.lineWidth = 0.6;
  for (let i=1;i<5;i++){const t=i/5;ctx.beginPath();ctx.moveTo(x-w*0.58*t,y-h+w*0.14*(1-t));ctx.lineTo(x+w*0.58*t,y-h+w*0.14*(1-t));ctx.stroke();}
  const wc = `rgba(255,190,80,${0.48+0.15*Math.sin(tick*0.05)})`;
  const ws = 8*sc;
  ctx.fillStyle='rgba(0,0,0,0.6)'; ctx.fillRect(x-w*0.28,y-h*0.58,ws,ws*1.1);
  ctx.fillStyle=wc; ctx.fillRect(x-w*0.27,y-h*0.57,ws-2,ws);
  ctx.fillStyle='rgba(0,0,0,0.6)'; ctx.fillRect(x+w*0.10,y-h*0.58,ws,ws*1.1);
  ctx.fillStyle=wc; ctx.fillRect(x+w*0.11,y-h*0.57,ws-2,ws);
  ctx.fillStyle='#1a0e04';
  ctx.beginPath(); ctx.arc(x,y-h*0.22,6*sc,Math.PI,0); ctx.rect(x-6*sc,y-h*0.22,12*sc,h*0.24); ctx.fill();
  if (lvl >= 3) glow(ctx, x, y-h*0.06, 12*sc, '#ff9020');
  isoBox(ctx, x+w*0.28, y-h*0.80, w*0.14, h*0.42, '#4a3820','#342a18','#5a4828');
  for (let i=0;i<3;i++){ctx.fillStyle=`rgba(180,160,140,${0.14-i*0.04})`;ctx.beginPath();ctx.arc(x+w*0.28+i*2*sc,y-h*0.98-i*8*sc,4*sc+i*2*sc,0,Math.PI*2);ctx.fill();}
}

function drawWatchtower(ctx, x, y, sc, lvl) {
  const w = 30 * sc, h = 80 * sc;
  isoBox(ctx, x, y, w*1.5, h*0.18, '#283040','#1a2030','#384050');
  isoBox(ctx, x, y-h*0.15, w, h*0.80, '#2e3848','#1e2838','#3e4858');
  ctx.fillStyle='#3a4858'; ctx.fillRect(x-w*0.7,y-h*0.74,w*1.4,h*0.04);
  isoBox(ctx, x, y-h*0.78, w*1.2, h*0.18, '#344050','#223040','#445060');
  for (let i=-2;i<=2;i++){ctx.fillStyle='#405060';ctx.fillRect(x+i*5*sc-2*sc,y-h*0.98,3.5*sc,6*sc);ctx.fillStyle='rgba(0,0,0,0.4)';ctx.fillRect(x+i*5*sc-1*sc,y-h*0.97,1.5*sc,3*sc);}
  for (let yy=0.25;yy<0.82;yy+=0.28){
    const wc=`rgba(200,230,255,${0.28+0.15*Math.sin(tick*0.04+yy*10)})`;
    ctx.fillStyle='rgba(0,0,0,0.5)'; ctx.fillRect(x-4*sc,y-h*yy-3*sc,7*sc,8*sc);
    ctx.fillStyle=wc; ctx.fillRect(x-3*sc,y-h*yy-2*sc,5*sc,6*sc);
  }
  if (lvl >= 8) {
    const a = tick*0.04, reach=48*sc;
    const lx=x+Math.cos(a)*reach, ly=y-h+Math.sin(a)*8*sc;
    const lg=ctx.createLinearGradient(x,y-h,lx,ly);
    lg.addColorStop(0,'rgba(220,240,255,0.5)'); lg.addColorStop(1,'rgba(220,240,255,0)');
    ctx.fillStyle=lg; ctx.beginPath(); ctx.moveTo(x,y-h); ctx.lineTo(lx-4,ly-2); ctx.lineTo(lx+4,ly+2); ctx.closePath(); ctx.fill();
    glow(ctx,x,y-h,10*sc,'#c0e0ff');
  }
  ctx.strokeStyle='#5a6878'; ctx.lineWidth=1.2;
  ctx.beginPath(); ctx.moveTo(x,y-h*0.98); ctx.lineTo(x,y-h*0.98-14*sc); ctx.stroke();
  ctx.fillStyle='#405870'; ctx.fillRect(x,y-h*0.98-14*sc,9*sc,6*sc);
}

function drawTravelCenter(ctx, x, y, sc, lvl) {
  const w=56*sc, h=50*sc;
  isoBox(ctx,x,y,w*1.1,h*0.18,'#1e2448','#141830','#283060');
  isoBox(ctx,x,y-h*0.14,w,h*0.32,'#243060','#182048','#304080');
  isoBox(ctx,x,y-h*0.40,w*0.85,h*0.68,'#2c3870','#1e2858','#3c4888');
  const aW=16*sc, aH=22*sc;
  ctx.fillStyle='rgba(0,0,0,0.72)';
  ctx.beginPath(); ctx.arc(x,y-h*0.50,aW*0.5,Math.PI,0); ctx.rect(x-aW*0.5,y-h*0.50,aW,aH*0.5); ctx.fill();
  const pA=0.42+0.28*Math.sin(tick*0.08);
  const pg=ctx.createRadialGradient(x,y-h*0.50,2,x,y-h*0.50,aW*0.5);
  pg.addColorStop(0,`rgba(80,140,255,${pA})`); pg.addColorStop(1,`rgba(60,100,220,0)`);
  ctx.fillStyle=pg; ctx.beginPath(); ctx.arc(x,y-h*0.50,aW*0.5,Math.PI,0); ctx.fill();
  ctx.strokeStyle=`rgba(120,180,255,${0.7+0.3*Math.sin(tick*0.09)})`; ctx.lineWidth=2*sc;
  ctx.beginPath(); ctx.arc(x,y-h*0.50,aW*0.55,Math.PI,0); ctx.stroke();
  ctx.fillStyle=`rgba(100,160,255,${0.3+0.15*Math.sin(tick*0.06)})`;
  for(let i=0;i<4;i++){ctx.fillRect(x-w*0.36+i*w*0.24,y-h*0.70,4*sc,4*sc);ctx.fillRect(x-w*0.33+i*w*0.24,y-h*0.55,3*sc,3*sc);}
  [-w*0.44,w*0.44].forEach(ox=>{
    ctx.fillStyle=`rgba(100,160,255,${0.5+0.2*Math.sin(tick*0.07+ox)})`;
    ctx.beginPath(); ctx.moveTo(x+ox,y-h*0.84); ctx.lineTo(x+ox+4*sc,y-h*0.70); ctx.lineTo(x+ox-4*sc,y-h*0.70); ctx.closePath(); ctx.fill();
    glow(ctx,x+ox,y-h*0.84,8*sc,'#5090ff');
  });
}

function drawHideout(ctx, x, y, sc, lvl) {
  const w=50*sc, h=22*sc;
  isoBox(ctx,x,y,w,h,'#262e1e','#181e10','#32382a');
  ctx.fillStyle='#1e2818';
  ctx.beginPath(); ctx.moveTo(x,y-h-6*sc); ctx.lineTo(x+w*0.55,y-h+w*0.10); ctx.lineTo(x-w*0.55,y-h+w*0.10); ctx.closePath(); ctx.fill();
  for(let i=0;i<8;i++){const gx=x-w*0.40+i*w*0.11,gy=y-h-3*sc;ctx.fillStyle=`rgba(${28+i*3},${42+i*5},12,0.6)`;ctx.beginPath();ctx.arc(gx,gy,4*sc+Math.sin(i)*2*sc,0,Math.PI*2);ctx.fill();}
  ctx.fillStyle='rgba(0,0,0,0.5)'; ctx.beginPath(); ctx.ellipse(x,y-h*0.18,8*sc,4*sc,0,0,Math.PI*2); ctx.fill();
  ctx.strokeStyle='#3a3a20'; ctx.lineWidth=1; ctx.stroke();
  ctx.fillStyle='#505030'; ctx.fillRect(x-7*sc,y-h*0.21,3*sc,2*sc); ctx.fillRect(x+4*sc,y-h*0.21,3*sc,2*sc);
  if (lvl >= 10) { ctx.fillStyle=`rgba(180,160,60,${0.1+0.05*Math.sin(tick*0.08)})`; ctx.beginPath(); ctx.arc(x,y-h*0.18,3*sc,0,Math.PI*2); ctx.fill(); }
}

function drawWarehouse(ctx, x, y, sc, lvl) {
  const w=68*sc, h=42*sc;
  isoBox(ctx,x,y,w*1.06,h*0.16,'#3a2010','#281408','#503020');
  isoBox(ctx,x,y-h*0.10,w,h,'#503818','#382808','#6a4828');
  ctx.fillStyle='#3a2810';
  ctx.beginPath(); ctx.moveTo(x,y-h-12*sc); ctx.lineTo(x+w*0.58,y-h+w*0.12); ctx.lineTo(x-w*0.58,y-h+w*0.12); ctx.closePath(); ctx.fill();
  ctx.strokeStyle='rgba(0,0,0,0.38)'; ctx.lineWidth=0.8; ctx.stroke();
  ctx.strokeStyle='rgba(0,0,0,0.22)'; ctx.lineWidth=0.7;
  for(let i=1;i<5;i++){const t=i/5;ctx.beginPath();ctx.moveTo(x-w*0.55*t,y-h+w*0.10*(1-t));ctx.lineTo(x+w*0.55*t,y-h+w*0.10*(1-t));ctx.stroke();}
  ctx.fillStyle='#1a0e06'; ctx.fillRect(x-14*sc,y-h*0.44,12*sc,h*0.44); ctx.fillRect(x+2*sc,y-h*0.44,12*sc,h*0.44);
  ctx.strokeStyle='#4a3018'; ctx.lineWidth=1; ctx.strokeRect(x-14*sc,y-h*0.44,12*sc,h*0.44); ctx.strokeRect(x+2*sc,y-h*0.44,12*sc,h*0.44);
  ctx.fillStyle='#606040'; ctx.fillRect(x-13*sc,y-h*0.38,2*sc,2*sc); ctx.fillRect(x+3*sc,y-h*0.38,2*sc,2*sc);
  for(let i=0;i<2;i++){const wx=x-w*0.36+i*w*0.66;ctx.fillStyle='rgba(0,0,0,0.5)';ctx.fillRect(wx,y-h*0.72,10*sc,7*sc);ctx.fillStyle=`rgba(200,160,80,${0.22+0.10*Math.sin(tick*0.04+i)})`;ctx.fillRect(wx+1,y-h*0.71,8*sc,5*sc);}
  if (lvl >= 10) glow(ctx,x,y-h*0.22,20*sc,'#b87828');
}

function drawUniversity(ctx, x, y, sc, lvl) {
  const w=60*sc, h=58*sc;
  isoBox(ctx,x,y,w*1.1,h*0.12,'#162838','#0e1c28','#203848');
  isoBox(ctx,x,y-h*0.10,w,h*0.26,'#1a3048','#0e2030','#284060');
  isoBox(ctx,x,y-h*0.33,w*0.88,h*0.62,'#1e3858','#122840','#2c4870');
  isoBox(ctx,x-w*0.36,y-h*0.18,w*0.30,h*0.90,'#162e48','#0e1e30','#243e60');
  for(let i=0;i<4;i++){
    const ay=y-h*(0.28+i*0.18);
    ctx.strokeStyle=`rgba(120,180,220,${0.3+0.10*Math.sin(tick*0.04+i)})`; ctx.lineWidth=1.5*sc;
    ctx.beginPath(); ctx.arc(x-w*0.36,ay,5*sc,Math.PI,0); ctx.stroke();
    ctx.fillStyle=`rgba(255,210,120,${0.3+0.12*Math.sin(tick*0.04+i*0.8)})`; ctx.fillRect(x-w*0.36-3*sc,ay-4*sc,6*sc,6*sc);
  }
  ctx.fillStyle='#182840';
  for(let i=0;i<3;i++){ctx.fillRect(x+w*0.10+i*w*0.14,y-h*(0.28+i*0.05),5*sc,h*(0.28+i*0.05));}
  for(let i=0;i<3;i++){
    const wx=x-w*0.18+i*w*0.20;
    ctx.fillStyle='rgba(0,0,0,0.5)'; ctx.fillRect(wx-5*sc,y-h*0.56,9*sc,11*sc);
    ctx.fillStyle=`rgba(255,200,100,${0.3+0.10*Math.sin(tick*0.03+i)})`; ctx.fillRect(wx-4*sc,y-h*0.55,7*sc,9*sc);
  }
  ctx.strokeStyle='#5a7a9a'; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(x-w*0.36,y-h*1.02); ctx.lineTo(x-w*0.36,y-h*1.02-12*sc); ctx.stroke();
  const vA=tick*0.05;
  ctx.fillStyle='#4a6a8a';
  ctx.beginPath(); ctx.moveTo(x-w*0.36+Math.cos(vA)*8*sc,y-h*1.02-6*sc+Math.sin(vA)*2*sc); ctx.lineTo(x-w*0.36+Math.cos(vA+Math.PI)*8*sc,y-h*1.02-6*sc+Math.sin(vA+Math.PI)*2*sc); ctx.lineTo(x-w*0.36,y-h*1.02-6*sc); ctx.closePath(); ctx.fill();
}

function drawForge(ctx, x, y, sc, lvl) {
  const w=54*sc, h=40*sc;
  isoBox(ctx,x,y,w*1.08,h*0.18,'#381408','#280e04','#502010');
  isoBox(ctx,x,y-h*0.14,w,h,'#502010','#380e06','#703020');
  isoBox(ctx,x+w*0.28,y-h*0.62,w*0.22,h*0.62,'#401808','#2c1004','#602018');
  isoBox(ctx,x+w*0.08,y-h*0.52,w*0.14,h*0.42,'#381408','#280e04','#502010');
  [[x+w*0.28,y-h*1.22],[x+w*0.08,y-h*0.92]].forEach(([sx,sy],ci)=>{
    for(let i=0;i<5;i++){const d=Math.sin(tick*0.04+i+ci)*4*sc;ctx.fillStyle=`rgba(160,140,120,${0.18-i*0.03})`;ctx.beginPath();ctx.arc(sx+d,sy-i*7*sc,5*sc+i*2*sc,0,Math.PI*2);ctx.fill();}
  });
  ctx.fillStyle='#0a0402';
  ctx.beginPath(); ctx.arc(x-w*0.15,y-h*0.26,9*sc,Math.PI,0); ctx.rect(x-w*0.15-9*sc,y-h*0.26,18*sc,10*sc); ctx.fill();
  glow(ctx,x-w*0.15,y-h*0.22,16*sc,'#ff7800');
  const fi=0.6+0.4*Math.sin(tick*0.12);
  for(let i=0;i<5;i++){
    const fx=x-w*0.15+(i-2)*3*sc,fh=6*sc+Math.sin(tick*0.10+i)*3*sc;
    const fg=ctx.createLinearGradient(fx,y-h*0.16,fx,y-h*0.16-fh);
    fg.addColorStop(0,`rgba(255,${60+i*20},0,${fi})`); fg.addColorStop(1,'rgba(255,200,0,0)');
    ctx.fillStyle=fg; ctx.beginPath(); ctx.ellipse(fx,y-h*0.16-fh/2,2*sc,fh/2,0,0,Math.PI*2); ctx.fill();
  }
  ctx.fillStyle='#303030';
  ctx.beginPath(); ctx.moveTo(x+w*0.10,y-h*0.04); ctx.lineTo(x+w*0.30,y-h*0.04); ctx.lineTo(x+w*0.28,y-h*0.10); ctx.lineTo(x+w*0.12,y-h*0.10); ctx.closePath(); ctx.fill();
  ctx.fillRect(x+w*0.16,y-h*0.10,w*0.08,h*0.08);
}

function drawBarracks(ctx, x, y, sc, lvl) {
  const w=56*sc, h=40*sc;
  isoBox(ctx,x,y,w*1.06,h*0.16,'#201414','#140c0c','#301c1c');
  isoBox(ctx,x,y-h*0.10,w,h,'#2e1c1c','#1e1010','#402828');
  ctx.fillStyle='#1c1010';
  ctx.beginPath(); ctx.moveTo(x,y-h-10*sc); ctx.lineTo(x+w*0.58,y-h+w*0.12); ctx.lineTo(x-w*0.58,y-h+w*0.12); ctx.closePath(); ctx.fill();
  ctx.strokeStyle='rgba(0,0,0,0.5)'; ctx.lineWidth=0.8; ctx.stroke();
  ctx.strokeStyle='rgba(0,0,0,0.2)'; ctx.lineWidth=0.6;
  for(let i=1;i<5;i++){const t=i/5;ctx.beginPath();ctx.moveTo(x-w*0.55*t,y-h+w*0.10*(1-t));ctx.lineTo(x+w*0.55*t,y-h+w*0.10*(1-t));ctx.stroke();}
  ctx.strokeStyle='#504040'; ctx.lineWidth=1.5;
  ctx.beginPath(); ctx.moveTo(x+w*0.22,y-h-10*sc); ctx.lineTo(x+w*0.22,y-h-10*sc-18*sc); ctx.stroke();
  const wv=Math.sin(tick*0.06)*3*sc;
  ctx.fillStyle='#8a2020';
  ctx.beginPath(); ctx.moveTo(x+w*0.22,y-h-26*sc); ctx.lineTo(x+w*0.22+12*sc+wv,y-h-22*sc); ctx.lineTo(x+w*0.22+10*sc+wv*0.7,y-h-19*sc); ctx.lineTo(x+w*0.22,y-h-19*sc); ctx.closePath(); ctx.fill();
  for(let i=0;i<4;i++){
    const wx=x-w*0.28+i*w*0.20;
    ctx.fillStyle='rgba(0,0,0,0.7)'; ctx.fillRect(wx-3*sc,y-h*0.52,5*sc,9*sc);
    ctx.fillStyle=`rgba(160,100,100,${0.22+0.08*Math.sin(tick*0.04+i)})`; ctx.fillRect(wx-2*sc,y-h*0.51,3*sc,7*sc);
  }
  ctx.strokeStyle='rgba(150,130,100,0.5)'; ctx.lineWidth=1;
  for(let i=0;i<4;i++){
    const lx=x-w*0.14+i*7*sc;
    ctx.beginPath(); ctx.moveTo(lx,y-h*0.04); ctx.lineTo(lx-2*sc,y-h*0.52); ctx.stroke();
    ctx.fillStyle='rgba(180,160,80,0.6)'; ctx.beginPath(); ctx.moveTo(lx-2*sc,y-h*0.52); ctx.lineTo(lx,y-h*0.57); ctx.lineTo(lx-4*sc,y-h*0.52); ctx.closePath(); ctx.fill();
  }
}
