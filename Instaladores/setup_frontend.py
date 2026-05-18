"""
Crea la estructura base del frontend v3.
Ejecutar desde E:\0000ew V2Claude\
"""
from pathlib import Path

BASE = Path(r"E:\0000ew V2Claude\frontend")

files = {}

# ── index.html — Login ────────────────────────────────────────────────────
files["index.html"] = '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Eternal Warriors v3.0</title>
<link rel="stylesheet" href="/static/css/theme.css">
<link rel="stylesheet" href="/static/css/login.css">
</head>
<body class="login-body">
  <div class="login-container">
    <div class="login-header">
      <div class="login-alalaia">
        <img src="/static/assets/ui/alalaia_portrait.png" alt="AlalaiA" onerror="this.style.display=\'none\'">
        <span class="login-title-sub">EQUILIBRIO · MEMORIA · LUZ</span>
      </div>
      <div class="login-title-center">
        <h1 class="login-title">ETERNAL WARRIORS</h1>
        <span class="login-version">v3.0 — Ciclo NG+</span>
      </div>
      <div class="login-karlaka">
        <img src="/static/assets/ui/karlaka_portrait.png" alt="KarlakÁ" onerror="this.style.display=\'none\'">
        <span class="login-title-sub">GUERRA · TIERRA · VOLUNTAD</span>
      </div>
    </div>
    <div class="login-box">
      <div class="login-field">
        <label>JUGADOR</label>
        <input type="text" id="usuario" placeholder="Tu nombre de jugador" autocomplete="off">
      </div>
      <div class="login-field">
        <label>CONTRASEÑA</label>
        <input type="password" id="password" placeholder="••••••••">
      </div>
      <div id="login-msg" class="login-msg"></div>
      <button class="btn-primary" onclick="doLogin()">ENTRAR AL MUNDO</button>
    </div>
    <div class="login-footer">
      <span>KarlakÁ observa. El ciclo continúa.</span>
    </div>
  </div>
<script>
async function doLogin() {
  const usuario  = document.getElementById('usuario').value.trim();
  const password = document.getElementById('password').value;
  const msg      = document.getElementById('login-msg');
  if (!usuario || !password) { msg.textContent = 'Completa todos los campos.'; return; }
  try {
    const res  = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({usuario, password})
    });
    const data = await res.json();
    if (data.ok) {
      sessionStorage.setItem('jugador', data.jugador);
      sessionStorage.setItem('capital', data.capital);
      window.location.href = '/game';
    } else {
      msg.textContent = data.msg || 'Error de autenticación.';
    }
  } catch(e) {
    msg.textContent = 'Error de conexión con el servidor.';
  }
}
document.addEventListener('keydown', e => { if (e.key === 'Enter') doLogin(); });
</script>
</body>
</html>
'''

# ── game.html — Pantalla principal ────────────────────────────────────────
files["game.html"] = '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Eternal Warriors v3.0</title>
<link rel="stylesheet" href="/static/css/theme.css">
<link rel="stylesheet" href="/static/css/game.css">
</head>
<body class="game-body">
  <!-- Header global -->
  <header class="game-header">
    <div class="header-left">
      <span id="hdr-ciudad" class="hdr-ciudad">CIUDAD</span>
      <span id="hdr-ciclo"  class="hdr-ciclo">Ciclo NG+0</span>
    </div>
    <div class="header-center">
      <img src="/static/assets/ui/alalaia_small.png" alt="" onerror="this.style.display=\'none\'">
      <div class="hdr-alalaia">
        <span>ALALAIA</span>
        <small>EQUILIBRIO · MEMORIA · LUZ</small>
      </div>
      <div class="hdr-sep">⚔</div>
      <div class="hdr-karlaka">
        <span>KARLAKᾹ OBSERVA</span>
        <small>GUERRA · TIERRA · VOLUNTAD</small>
      </div>
      <img src="/static/assets/ui/karlaka_small.png" alt="" onerror="this.style.display=\'none\'">
    </div>
    <div class="header-right">
      <span class="hdr-evento">PRÓXIMO EVENTO</span>
      <span id="hdr-timer" class="hdr-timer">--:--:--</span>
    </div>
  </header>

  <!-- Contenido principal -->
  <main id="main-content" class="main-content">
    <div id="screen-loading" class="screen-loading">
      <span>Cargando mundo...</span>
    </div>
  </main>

  <!-- Nav inferior -->
  <nav class="game-nav">
    <button class="nav-btn active" onclick="loadScreen('city')" id="nav-city">
      <span class="nav-icon">🏰</span><span>CIUDAD</span>
    </button>
    <button class="nav-btn" onclick="loadScreen('army')" id="nav-army">
      <span class="nav-icon">⚔</span><span>EJÉRCITO</span>
    </button>
    <button class="nav-btn" onclick="loadScreen('invocations')" id="nav-inv">
      <span class="nav-icon">✨</span><span>INVOCACIONES</span>
    </button>
    <button class="nav-btn" onclick="loadScreen('map')" id="nav-map">
      <span class="nav-icon">🗺</span><span>MAPA IMPERIAL</span>
    </button>
    <button class="nav-btn" onclick="loadScreen('reports')" id="nav-rep">
      <span class="nav-icon">📋</span><span>INFORMES</span>
    </button>
    <button class="nav-btn" onclick="loadScreen('settings')" id="nav-set">
      <span class="nav-icon">⚙</span><span>AJUSTES</span>
    </button>
  </nav>

<script src="/static/js/app.js"></script>
</body>
</html>
'''

# ── css/theme.css ─────────────────────────────────────────────────────────
files["css/theme.css"] = '''/* ETERNAL WARRIORS v3.0 — Tema global */
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Cinzel+Decorative:wght@400;700&family=Rajdhani:wght@400;500;600;700&display=swap');

:root {
  --color-bg:         #0a0a0f;
  --color-bg2:        #10101a;
  --color-panel:      #12121e;
  --color-border:     #2a2a45;
  --color-border2:    #3d3d6b;
  --color-gold:       #c9a84c;
  --color-gold2:      #e8c96d;
  --color-blue:       #4a7ab5;
  --color-blue2:      #6ba3e0;
  --color-red:        #8b1a1a;
  --color-red2:       #c44;
  --color-green:      #2d6a2d;
  --color-green2:     #4a9e4a;
  --color-purple:     #5a2d8a;
  --color-purple2:    #9b6ad6;
  --color-text:       #d4c9a8;
  --color-text2:      #9a8f6a;
  --color-white:      #f0e8d0;
  --font-title:       'Cinzel Decorative', serif;
  --font-ui:          'Cinzel', serif;
  --font-body:        'Rajdhani', sans-serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: 14px;
  overflow: hidden;
  height: 100vh;
  width: 100vw;
}

.btn-primary {
  background: linear-gradient(135deg, #1a1a3e, #2a2a5e);
  border: 1px solid var(--color-gold);
  color: var(--color-gold);
  font-family: var(--font-ui);
  font-size: 14px;
  letter-spacing: 2px;
  padding: 12px 32px;
  cursor: pointer;
  transition: all 0.2s;
  text-transform: uppercase;
}
.btn-primary:hover {
  background: linear-gradient(135deg, #2a2a5e, #3a3a7e);
  box-shadow: 0 0 20px rgba(201,168,76,0.3);
}

.panel {
  background: var(--color-panel);
  border: 1px solid var(--color-border);
  padding: 12px;
}

.panel-title {
  font-family: var(--font-ui);
  color: var(--color-gold);
  font-size: 11px;
  letter-spacing: 2px;
  text-transform: uppercase;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 6px;
  margin-bottom: 8px;
}
'''

# ── css/login.css ─────────────────────────────────────────────────────────
files["css/login.css"] = '''.login-body {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: radial-gradient(ellipse at center, #0d0d1a 0%, #050508 100%);
}

.login-container {
  width: 680px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.login-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.login-alalaia, .login-karlaka {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 140px;
}

.login-alalaia img, .login-karlaka img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 2px solid var(--color-gold);
  object-fit: cover;
}

.login-title-sub {
  font-family: var(--font-ui);
  font-size: 9px;
  letter-spacing: 1px;
  color: var(--color-text2);
  text-align: center;
}

.login-title-center {
  text-align: center;
  flex: 1;
}

.login-title {
  font-family: var(--font-title);
  font-size: 28px;
  color: var(--color-gold);
  text-shadow: 0 0 30px rgba(201,168,76,0.5);
  letter-spacing: 4px;
}

.login-version {
  font-family: var(--font-ui);
  font-size: 10px;
  color: var(--color-text2);
  letter-spacing: 2px;
}

.login-box {
  background: linear-gradient(135deg, #0e0e1e, #12121f);
  border: 1px solid var(--color-border2);
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  box-shadow: 0 0 60px rgba(0,0,0,0.8);
}

.login-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.login-field label {
  font-family: var(--font-ui);
  font-size: 10px;
  letter-spacing: 2px;
  color: var(--color-gold);
}

.login-field input {
  background: #08080f;
  border: 1px solid var(--color-border);
  color: var(--color-white);
  font-family: var(--font-body);
  font-size: 16px;
  padding: 10px 14px;
  outline: none;
  transition: border-color 0.2s;
}

.login-field input:focus {
  border-color: var(--color-gold);
}

.login-msg {
  color: var(--color-red2);
  font-size: 13px;
  min-height: 18px;
  text-align: center;
}

.login-box .btn-primary { width: 100%; }

.login-footer {
  text-align: center;
  font-family: var(--font-ui);
  font-size: 10px;
  color: var(--color-text2);
  letter-spacing: 2px;
}
'''

# ── css/game.css ──────────────────────────────────────────────────────────
files["css/game.css"] = '''.game-body {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.game-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(90deg, #0a0a1a, #0e0e20, #0a0a1a);
  border-bottom: 1px solid var(--color-border2);
  padding: 8px 20px;
  height: 56px;
  flex-shrink: 0;
}

.header-left { display: flex; flex-direction: column; }
.hdr-ciudad { font-family: var(--font-ui); color: var(--color-gold); font-size: 13px; letter-spacing: 2px; }
.hdr-ciclo  { font-size: 10px; color: var(--color-text2); }

.header-center {
  display: flex;
  align-items: center;
  gap: 16px;
}

.hdr-alalaia { text-align: right; }
.hdr-alalaia span { font-family: var(--font-ui); color: var(--color-blue2); font-size: 12px; }
.hdr-alalaia small { display: block; font-size: 9px; color: var(--color-text2); letter-spacing: 1px; }

.hdr-sep { color: var(--color-border2); font-size: 20px; }

.hdr-karlaka span { font-family: var(--font-ui); color: var(--color-red2); font-size: 12px; }
.hdr-karlaka small { display: block; font-size: 9px; color: var(--color-text2); letter-spacing: 1px; }

.header-right { text-align: right; }
.hdr-evento { display: block; font-size: 9px; color: var(--color-text2); letter-spacing: 1px; font-family: var(--font-ui); }
.hdr-timer  { font-family: var(--font-ui); color: var(--color-gold); font-size: 18px; }

.main-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.screen-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-family: var(--font-ui);
  color: var(--color-text2);
  letter-spacing: 3px;
}

.game-nav {
  display: flex;
  background: linear-gradient(90deg, #08080f, #0c0c18, #08080f);
  border-top: 1px solid var(--color-border2);
  height: 64px;
  flex-shrink: 0;
}

.nav-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  background: transparent;
  border: none;
  border-right: 1px solid var(--color-border);
  color: var(--color-text2);
  cursor: pointer;
  transition: all 0.2s;
  font-family: var(--font-ui);
  font-size: 9px;
  letter-spacing: 1px;
}

.nav-btn:hover, .nav-btn.active {
  background: linear-gradient(180deg, #1a1a3a, #0e0e20);
  color: var(--color-gold);
}

.nav-icon { font-size: 20px; }
'''

# ── js/app.js ─────────────────────────────────────────────────────────────
files["js/app.js"] = '''/* ETERNAL WARRIORS v3.0 — Orquestador frontend */

const JUGADOR = sessionStorage.getItem('jugador') || '';
const CAPITAL = sessionStorage.getItem('capital') || '';

if (!JUGADOR) window.location.href = '/';

// Header
document.getElementById('hdr-ciudad').textContent = CAPITAL || 'SIN CIUDAD';

// Cargar pantalla por defecto
window.addEventListener('DOMContentLoaded', () => {
  loadScreen('city');
  startTimer();
});

async function loadScreen(screen) {
  // Actualizar nav
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById('nav-' + (screen === 'city' ? 'city' :
              screen === 'army' ? 'army' : screen === 'invocations' ? 'inv' :
              screen === 'map' ? 'map' : screen === 'reports' ? 'rep' : 'set'));
  if (btn) btn.classList.add('active');

  const main = document.getElementById('main-content');
  main.innerHTML = '<div class="screen-loading"><span>Cargando...</span></div>';

  try {
    const mod = await import(`/static/js/screens/${screen}.js`);
    await mod.render(main, JUGADOR, CAPITAL);
  } catch(e) {
    main.innerHTML = `<div class="screen-loading"><span>Pantalla en construcción: ${screen}</span></div>`;
  }
}

function startTimer() {
  // Timer placeholder — se conectará al backend
  const el = document.getElementById('hdr-timer');
  let t = 2 * 24 * 3600 + 11 * 3600 + 47 * 60;
  setInterval(() => {
    t = Math.max(0, t - 1);
    const d = Math.floor(t / 86400);
    const h = Math.floor((t % 86400) / 3600);
    const m = Math.floor((t % 3600) / 60);
    el.textContent = `${d}d ${String(h).padStart(2,'0')}h ${String(m).padStart(2,'0')}m`;
  }, 1000);
}
'''

# ── js/screens/city.js ────────────────────────────────────────────────────
files["js/screens/city.js"] = '''/* Pantalla CIUDAD */
export async function render(container, jugador, capital) {
  const res  = await fetch(`/api/city/${jugador}/${capital}`);
  const data = await res.json();
  const c    = data.city || {};

  container.innerHTML = `
  <div class="city-screen">
    <div class="city-left">
      <div class="panel">
        <div class="panel-title">▼ Recursos</div>
        ${stat('🪵 Madera',  c.MADERA)}
        ${stat('🪨 Piedra',  c.PIEDRA)}
        ${stat('⚙ Hierro',  c.HIERRO)}
        ${stat('🔥 Carbón',  c.CARBON)}
        ${stat('💰 Oro',     c.ORO)}
        ${stat('✨ Maná',    c.MANA)}
      </div>
    </div>
    <div class="city-center">
      <div class="city-view-placeholder">
        <span>Vista isométrica — próximamente</span>
        <br><strong>${c.NOMBRE || capital}</strong>
      </div>
    </div>
    <div class="city-right">
      <div class="panel">
        <div class="panel-title">▼ Ejército</div>
        ${stat('Aldeano',    c.ALDEANO)}
        ${stat('Explorador', c.EXPLORADOR)}
        ${stat('Guerrero',   c.GUERRERO)}
        ${stat('Mago',       c.MAGO)}
      </div>
    </div>
  </div>
  `;
}

function stat(label, val) {
  const v = val !== undefined ? Number(val).toLocaleString('es') : '—';
  return `<div class="stat-row"><span class="stat-label">${label}</span><span class="stat-val">${v}</span></div>`;
}
'''

# ── js/screens/map.js, army.js, invocations.js, reports.js, settings.js ──
for screen in ['map','army','invocations','reports','settings']:
    files[f"js/screens/{screen}.js"] = f'''/* Pantalla {screen.upper()} — en construcción */
export async function render(container, jugador, capital) {{
  container.innerHTML = '<div class="screen-loading"><span>{screen.upper()} — próximamente</span></div>';
}}
'''

# ── css/city.css ──────────────────────────────────────────────────────────
files["css/city.css"] = '''.city-screen {
  display: grid;
  grid-template-columns: 220px 1fr 220px;
  height: 100%;
  gap: 0;
}

.city-left, .city-right {
  background: var(--color-panel);
  border-right: 1px solid var(--color-border);
  padding: 12px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.city-right { border-right: none; border-left: 1px solid var(--color-border); }

.city-center {
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, #0e0e20, #080810);
}

.city-view-placeholder {
  text-align: center;
  color: var(--color-text2);
  font-family: var(--font-ui);
  letter-spacing: 2px;
  font-size: 12px;
}

.city-view-placeholder strong {
  color: var(--color-gold);
  font-size: 18px;
  display: block;
  margin-top: 8px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px solid var(--color-border);
  font-size: 13px;
}

.stat-label { color: var(--color-text2); }
.stat-val   { color: var(--color-white); font-weight: 600; }
'''

# Placeholders de assets
files["assets/ui/.gitkeep"] = ""
files["assets/tiles/.gitkeep"] = ""

# Crear todos los archivos
for rel_path, content in files.items():
    full_path = BASE / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  OK {rel_path}")

print("\n✅ Frontend creado. Ejecuta run.bat.")
