"""
Actualiza city.js y city.css con layout completo basado en el prototipo.
Ejecutar desde E:\0000ew V2Claude\
"""
from pathlib import Path

BASE = Path(r"E:\0000ew V2Claude\frontend")

# ── js/screens/city.js ────────────────────────────────────────────────────
city_js = r'''/* Pantalla CIUDAD */
export async function render(container, jugador, capital) {
  const res  = await fetch(`/api/city/${jugador}/${capital}`);
  const data = await res.json();
  const c    = data.city || {};

  container.innerHTML = `
  <link rel="stylesheet" href="/static/css/city.css">
  <div class="city-screen">

    <!-- COLUMNA IZQUIERDA -->
    <div class="city-left">
      <div class="panel">
        <div class="panel-title">▼ Recursos</div>
        ${stat('🪵', 'Madera',  c.MADERA)}
        ${stat('🪨', 'Piedra',  c.PIEDRA)}
        ${stat('⚙',  'Hierro',  c.HIERRO)}
        ${stat('🔥', 'Carbón',  c.CARBON)}
        ${stat('💰', 'Oro',     c.ORO)}
        ${stat('✨', 'Maná',    c.MANA)}
      </div>
      <div class="panel">
        <div class="panel-title">▼ Producción / hora</div>
        ${stat('👤', 'Aldeanos', c.ALDEANO)}
        ${stat('✨', 'Maná',    c.MANA)}
        ${stat('💰', 'Oro',     c.ORO)}
      </div>
      <div class="panel">
        <div class="panel-title">▼ Logística</div>
        ${stat('📦', 'Almacén',   c.ALMACEN)}
        ${stat('🔮', 'Santuario', c.SANTUARIO_ARCANO)}
      </div>
    </div>

    <!-- COLUMNA CENTRAL: vista ciudad -->
    <div class="city-center">
      <div class="city-canvas-wrap">
        <canvas id="city-canvas"></canvas>
        <div class="city-name-badge">${c.NOMBRE || capital}</div>
        ${buildingBadge('CENTRO DE CIUDAD', 'Nv.' + (c.CENTRO_DE_CIUDAD||1), 50, 38)}
        ${buildingBadge('MURALLA',          'Nv.' + (c.MURALLA||0),          72, 58)}
        ${buildingBadge('ALMACÉN',          'Nv.' + (c.ALMACEN||0),          35, 58)}
        ${buildingBadge('CUARTEL',          'Nv.' + (c.CUARTEL_1||0),        50, 72)}
      </div>
      <!-- Stats inferiores -->
      <div class="city-stats-bar">
        ${statBar('👥', 'Población', fmt(c.ALDEANO))}
        ${statBar('⚔',  'Ejércitos', '—')}
        ${statBar('✨', 'Invoc.',    countInv(c))}
        ${statBar('🏛',  'Edificios', '—')}
        ${statBar('🛡',  'Muralla',   'Nv.' + (c.MURALLA||0))}
      </div>
    </div>

    <!-- COLUMNA DERECHA -->
    <div class="city-right">
      <div class="panel">
        <div class="panel-title">▼ Ejército</div>
        ${stat('',  'Aldeano',     c.ALDEANO)}
        ${stat('',  'Explorador',  c.EXPLORADOR)}
        ${stat('',  'Sacerdote',   c.SACERDOTE)}
        ${stat('',  'Guerrero',    c.GUERRERO)}
        ${stat('',  'Comando',     c.COMANDO)}
        ${stat('',  'Mercenario',  c.MERCENARIO)}
        ${stat('',  'Marine',      c.MARINE)}
        ${stat('',  'Cyborg',      c.CYBORG)}
        ${stat('',  'Mago',        c.MAGO)}
        ${stat('',  'Metahumano',  c.METAHUMANO)}
      </div>
      <div class="panel">
        <div class="panel-title">▼ Invocaciones</div>
        ${stat('', 'Demonio',    c.DEMONIO)}
        ${stat('', 'Ánima',      c.ANIMA)}
        ${stat('', 'Espectro',   c.ESPECTRO)}
        ${stat('', 'Gólem',      c.GOLEM)}
        ${stat('', 'Centauro',   c.CENTAURO)}
        ${stat('', 'Kraken',     c.KRAKEN)}
        ${stat('', 'Alonardo',   c.ALONARDO)}
        ${stat('', 'Madreselva', c.MADRESELVA)}
        ${stat('', 'Coloso',     c.COLOSO)}
        ${stat('', 'Fénix',      c.FENIX)}
        ${stat('', 'Dragón Oro', c.DRAGON_DE_ORO)}
        ${stat('', 'Cab. Luz',   c.CABALLERO_DE_LUZ)}
        ${stat('', 'AlalaiA',    c.ALALAIA)}
        ${stat('', 'Éon Supremo',c.EON_SUPREMO)}
      </div>
    </div>

  </div>
  `;

  drawCity(c);
}

function fmt(val) {
  if (val === undefined || val === null) return '—';
  const n = Number(val);
  if (n >= 1e12) return (n/1e12).toFixed(2) + 'B';
  if (n >= 1e9)  return (n/1e9).toFixed(2)  + 'MM';
  if (n >= 1e6)  return (n/1e6).toFixed(2)  + 'M';
  if (n >= 1e3)  return (n/1e3).toFixed(1)  + 'K';
  return n.toLocaleString('es');
}

function stat(icon, label, val) {
  return `<div class="stat-row">
    <span class="stat-label">${icon ? icon + ' ' : ''}${label}</span>
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

function buildingBadge(name, level, left, top) {
  return `<div class="building-badge" style="left:${left}%;top:${top}%">
    <span class="bb-name">${name}</span>
    <span class="bb-level">${level}</span>
  </div>`;
}

function countInv(c) {
  const keys = ['DEMONIO','ANIMA','ESPECTRO','GOLEM','CENTAURO','KRAKEN',
                'ALONARDO','MADRESELVA','COLOSO','FENIX','DRAGON_DE_ORO',
                'CABALLERO_DE_LUZ','ALALAIA','EON_SUPREMO'];
  return keys.filter(k => c[k] > 0).length + ' / 14';
}

function drawCity(c) {
  const canvas = document.getElementById('city-canvas');
  if (!canvas) return;
  const W = canvas.parentElement.clientWidth;
  const H = canvas.parentElement.clientHeight - 48;
  canvas.width  = W;
  canvas.height = H;
  const ctx = canvas.getContext('2d');

  // Fondo degradado
  const bg = ctx.createRadialGradient(W/2, H*0.6, 20, W/2, H*0.6, W*0.7);
  bg.addColorStop(0,   '#1a1a35');
  bg.addColorStop(0.5, '#0e0e20');
  bg.addColorStop(1,   '#05050f');
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, W, H);

  // Suelo isométrico
  drawIsoGround(ctx, W, H);

  // Ciudad central (representación geométrica hasta tener sprites)
  drawCityBlocks(ctx, W, H, c);
}

function drawIsoGround(ctx, W, H) {
  const cx = W / 2, cy = H * 0.62;
  const tw = 48, th = 24;
  const cols = 12, rows = 8;

  for (let r = 0; r < rows; r++) {
    for (let col = 0; col < cols; col++) {
      const x = cx + (col - cols/2) * tw/2 - (r - rows/2) * tw/2;
      const y = cy + (col - cols/2) * th/2 + (r - rows/2) * th/2;
      const light = (col + r) % 2 === 0 ? '#1e2a1e' : '#182218';
      ctx.fillStyle = light;
      ctx.beginPath();
      ctx.moveTo(x,      y - th/2);
      ctx.lineTo(x + tw/2, y);
      ctx.lineTo(x,      y + th/2);
      ctx.lineTo(x - tw/2, y);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = '#0a120a';
      ctx.lineWidth = 0.5;
      ctx.stroke();
    }
  }
}

function drawCityBlocks(ctx, W, H, c) {
  const cx = W / 2, cy = H * 0.52;
  const lvl = Number(c.CENTRO_DE_CIUDAD || 1);
  const scale = Math.min(1.5, 0.5 + lvl * 0.025);

  // Torre central
  drawIsoBlock(ctx, cx, cy, 60*scale, 80*scale, '#2a3560', '#1e2748', '#3d4d80');

  // Torres laterales
  drawIsoBlock(ctx, cx - 55*scale, cy + 10*scale, 35*scale, 50*scale, '#223355', '#162540', '#304870');
  drawIsoBlock(ctx, cx + 55*scale, cy + 10*scale, 35*scale, 50*scale, '#223355', '#162540', '#304870');

  // Muralla
  const mLvl = Number(c.MURALLA || 0);
  if (mLvl > 0) {
    const mH = 15 + mLvl * 0.5;
    ctx.strokeStyle = '#4a5a70';
    ctx.lineWidth = 3;
    ctx.strokeRect(cx - 100*scale, cy + 30*scale, 200*scale, mH);
  }

  // Luz mágica en la cima
  const glow = ctx.createRadialGradient(cx, cy - 40*scale, 2, cx, cy - 40*scale, 30*scale);
  glow.addColorStop(0, 'rgba(100,150,255,0.6)');
  glow.addColorStop(1, 'rgba(100,150,255,0)');
  ctx.fillStyle = glow;
  ctx.beginPath();
  ctx.arc(cx, cy - 40*scale, 30*scale, 0, Math.PI*2);
  ctx.fill();
}

function drawIsoBlock(ctx, x, y, w, h, topColor, leftColor, rightColor) {
  const hw = w/2, qw = w/4, qh = w/8;
  // Top face
  ctx.fillStyle = topColor;
  ctx.beginPath();
  ctx.moveTo(x, y - h);
  ctx.lineTo(x + hw, y - h + qh);
  ctx.lineTo(x, y - h + qh*2);
  ctx.lineTo(x - hw, y - h + qh);
  ctx.closePath();
  ctx.fill();
  // Left face
  ctx.fillStyle = leftColor;
  ctx.beginPath();
  ctx.moveTo(x - hw, y - h + qh);
  ctx.lineTo(x, y - h + qh*2);
  ctx.lineTo(x, y);
  ctx.lineTo(x - hw, y - qh);
  ctx.closePath();
  ctx.fill();
  // Right face
  ctx.fillStyle = rightColor;
  ctx.beginPath();
  ctx.moveTo(x, y - h + qh*2);
  ctx.lineTo(x + hw, y - h + qh);
  ctx.lineTo(x + hw, y - qh);
  ctx.lineTo(x, y);
  ctx.closePath();
  ctx.fill();
}
'''

# ── css/city.css ──────────────────────────────────────────────────────────
city_css = '''.city-screen {
  display: grid;
  grid-template-columns: 200px 1fr 200px;
  height: 100%;
  overflow: hidden;
}

.city-left, .city-right {
  background: var(--color-panel);
  border-right: 1px solid var(--color-border);
  padding: 8px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  scrollbar-width: thin;
  scrollbar-color: var(--color-border2) transparent;
}
.city-right { border-right: none; border-left: 1px solid var(--color-border); }

.city-center {
  display: flex;
  flex-direction: column;
  background: #05050f;
  position: relative;
  overflow: hidden;
}

.city-canvas-wrap {
  flex: 1;
  position: relative;
  overflow: hidden;
}

#city-canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.city-name-badge {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  font-family: var(--font-ui);
  font-size: 13px;
  color: var(--color-gold);
  letter-spacing: 3px;
  text-shadow: 0 0 20px rgba(201,168,76,0.8);
  pointer-events: none;
}

.building-badge {
  position: absolute;
  transform: translate(-50%, -50%);
  background: rgba(10,10,20,0.85);
  border: 1px solid var(--color-border2);
  padding: 3px 7px;
  pointer-events: none;
  text-align: center;
}
.bb-name  { display: block; font-family: var(--font-ui); font-size: 8px; color: var(--color-text2); letter-spacing: 1px; }
.bb-level { display: block; font-family: var(--font-ui); font-size: 10px; color: var(--color-gold); }

.city-stats-bar {
  display: flex;
  background: linear-gradient(90deg, #0a0a18, #0e0e20, #0a0a18);
  border-top: 1px solid var(--color-border);
  height: 48px;
  flex-shrink: 0;
}

.stat-bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-right: 1px solid var(--color-border);
  gap: 1px;
}
.stat-bar-item:last-child { border-right: none; }
.stat-bar-icon  { font-size: 14px; }
.stat-bar-label { font-size: 8px; color: var(--color-text2); font-family: var(--font-ui); letter-spacing: 1px; }
.stat-bar-val   { font-size: 11px; color: var(--color-gold); font-family: var(--font-ui); }

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 3px 2px;
  border-bottom: 1px solid var(--color-border);
  font-size: 12px;
  gap: 4px;
}
.stat-label { color: var(--color-text2); white-space: nowrap; }
.stat-val   { color: var(--color-white); font-weight: 600; text-align: right; }

.panel { margin-bottom: 0; }
'''

# Escribir archivos
(BASE / "js/screens/city.js").write_text(city_js, encoding="utf-8")
print("  OK js/screens/city.js")

(BASE / "css/city.css").write_text(city_css, encoding="utf-8")
print("  OK css/city.css")

print("\n✅ Vista de ciudad actualizada.")
