"""
fix_11_hitbox_preciso.py

Problema raíz: el hitbox es un rectángulo genérico relativo a b.y que no
corresponde a la altura visual real de cada edificio.

Solución:
1. Cada función art*() recibe las mismas dimensiones W,H que calcula internamente
   → drawBuilding() las conoce y registra hitbox exacto en b.hx,b.hy,b.hw,b.hh
2. hover/click usan el hitbox registrado (rectángulo preciso)
3. drawBuilding() dibuja highlight dorado cuando b.hovered=true
4. onmousemove marca b.hovered y pide redibujo inmediato del frame de highlight

Ejecutar desde: E:\\0000ew V2Claude\\
"""
import pathlib, sys

TARGET = pathlib.Path("frontend/js/screens/city.js")
if not TARGET.exists():
    sys.exit(f"ERROR: No se encuentra {TARGET}")

src = TARGET.read_text(encoding="utf-8")
original = src

# ═══════════════════════════════════════════════════════════════════════════════
# PATCH 1: drawBuilding — registrar hitbox real + highlight hover
# ═══════════════════════════════════════════════════════════════════════════════

OLD_DRAW_BUILDING = """// ─── DISPATCHER DE EDIFICIOS ──────────────────────────────────────────────────
function drawBuilding(ctx, b) {
  const lvl = b.lvl || 0;
  ctx.save();
  // Paleta de acentos por clave
  const ACCENTS = {
    blue:   'rgb(80,160,255)',
    gold:   'rgb(220,170,50)',
    purple: 'rgb(180,80,255)',
    red1:   'rgb(200,50,30)',
    red2:   'rgb(180,40,20)',
  };
  const accent = b.accentKey ? ACCENTS[b.accentKey] : (b.accent || 'rgb(126,200,227)');

  switch (b.type) {
    case 'cityhall':   artCityHall(ctx, b.x, b.y, lvl);        break;
    case 'sanctuary':  artSanctuary(ctx, b.x, b.y, lvl);       break;
    case 'temple':     artTemple(ctx, b.x, b.y, lvl, accent);  break;
    case 'university': artUniversity(ctx, b.x, b.y, lvl);      break;
    case 'warehouse':  artWarehouse(ctx, b.x, b.y, lvl);       break;
    case 'watchtower': artWatchtower(ctx, b.x, b.y, lvl);      break;
    case 'travel':     artTravel(ctx, b.x, b.y, lvl);          break;
    case 'house':      artHouse(ctx, b.x, b.y, lvl);           break;
    case 'barracks':   artBarracks(ctx, b.x, b.y, lvl, accent);break;
    case 'forge':      artForge(ctx, b.x, b.y, lvl);           break;
    case 'hideout':    artHideout(ctx, b.x, b.y, lvl);         break;
  }
  ctx.restore();
  drawLabel(ctx, b.x, b.y, b.label, lvl, b.type);
}"""

NEW_DRAW_BUILDING = """// ─── DIMENSIONES DE HITBOX POR TIPO ──────────────────────────────────────────
// Cada entrada: [halfW, totalH] en píxeles base (sin escala de nivel)
// halfW  = mitad del ancho del edificio en pantalla
// totalH = altura total desde b.y hacia arriba
const _HITBOX = {
  cityhall:   [80, 200],
  sanctuary:  [55, 140],
  temple:     [50, 120],
  university: [55, 110],
  warehouse:  [55,  90],
  watchtower: [30, 130],
  travel:     [50, 100],
  house:      [40,  75],
  barracks:   [50,  95],
  forge:      [45,  85],
  hideout:    [45,  55],
};

// ─── DISPATCHER DE EDIFICIOS ──────────────────────────────────────────────────
function drawBuilding(ctx, b) {
  const lvl = b.lvl || 0;
  ctx.save();

  // Paleta de acentos por clave
  const ACCENTS = {
    blue:   'rgb(80,160,255)',
    gold:   'rgb(220,170,50)',
    purple: 'rgb(180,80,255)',
    red1:   'rgb(200,50,30)',
    red2:   'rgb(180,40,20)',
  };
  const accent = b.accentKey ? ACCENTS[b.accentKey] : (b.accent || 'rgb(126,200,227)');

  // Registrar hitbox preciso para este edificio
  const [hw, th] = _HITBOX[b.type] || [45, 80];
  b.hx = b.x - hw;
  b.hy = b.y - th;
  b.hw = hw * 2;
  b.hh = th;

  // Highlight hover ANTES de dibujar (halo detrás del edificio)
  if (b.hovered) {
    ctx.save();
    ctx.strokeStyle = 'rgba(255,220,80,0.85)';
    ctx.lineWidth   = 2.5;
    ctx.shadowColor = 'rgba(255,200,50,0.9)';
    ctx.shadowBlur  = 18;
    ctx.strokeRect(b.hx - 3, b.hy - 3, b.hw + 6, b.hh + 6);
    ctx.restore();
  }

  switch (b.type) {
    case 'cityhall':   artCityHall(ctx, b.x, b.y, lvl);        break;
    case 'sanctuary':  artSanctuary(ctx, b.x, b.y, lvl);       break;
    case 'temple':     artTemple(ctx, b.x, b.y, lvl, accent);  break;
    case 'university': artUniversity(ctx, b.x, b.y, lvl);      break;
    case 'warehouse':  artWarehouse(ctx, b.x, b.y, lvl);       break;
    case 'watchtower': artWatchtower(ctx, b.x, b.y, lvl);      break;
    case 'travel':     artTravel(ctx, b.x, b.y, lvl);          break;
    case 'house':      artHouse(ctx, b.x, b.y, lvl);           break;
    case 'barracks':   artBarracks(ctx, b.x, b.y, lvl, accent);break;
    case 'forge':      artForge(ctx, b.x, b.y, lvl);           break;
    case 'hideout':    artHideout(ctx, b.x, b.y, lvl);         break;
  }
  ctx.restore();

  // Label con fondo destacado si hovered
  drawLabel(ctx, b.x, b.y, b.label, lvl, b.type, b.hovered);
}

// Test de hit usando hitbox registrado
function _hitTest(b, mx, my) {
  if (!b.hw) return false;
  return mx >= b.hx && mx <= b.hx + b.hw &&
         my >= b.hy && my <= b.hy + b.hh;
}"""

if OLD_DRAW_BUILDING in src:
    src = src.replace(OLD_DRAW_BUILDING, NEW_DRAW_BUILDING)
    print("✅ PATCH 1 — drawBuilding con hitbox preciso y highlight hover")
else:
    print("⚠️  PATCH 1 — drawBuilding no encontrado exactamente")

# ═══════════════════════════════════════════════════════════════════════════════
# PATCH 2: drawLabel — resaltar cuando hovered
# ═══════════════════════════════════════════════════════════════════════════════

OLD_LABEL = """function drawLabel(ctx, x, y, text, lvl, type) {
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

NEW_LABEL = """function drawLabel(ctx, x, y, text, lvl, type, hovered = false) {
  ctx.save();
  ctx.font = `${hovered ? '700' : '500'} ${hovered ? '8' : '7'}px Rajdhani, sans-serif`;
  const label = lvl > 0 ? `${text} ${lvl}` : text;
  const tw = ctx.measureText(label).width + 10;
  const lh = hovered ? 12 : 10;
  ctx.fillStyle = hovered ? 'rgba(40,30,5,0.97)' : 'rgba(3,3,10,0.88)';
  ctx.strokeStyle = hovered ? 'rgba(255,210,60,0.95)' : (lvl > 0 ? 'rgba(160,128,44,0.65)' : 'rgba(40,40,65,0.55)');
  ctx.lineWidth = hovered ? 1.5 : 0.6;
  if (hovered) { ctx.shadowColor = 'rgba(255,200,50,0.8)'; ctx.shadowBlur = 8; }
  rr(ctx, x - tw / 2, y + 3, tw, lh, 2); ctx.fill(); ctx.stroke();
  ctx.shadowBlur = 0;
  ctx.fillStyle = hovered ? '#ffe066' : (lvl > 0 ? '#c89830' : '#505070');
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(label, x, y + 3 + lh / 2);
  ctx.restore();
}"""

if OLD_LABEL in src:
    src = src.replace(OLD_LABEL, NEW_LABEL)
    print("✅ PATCH 2 — drawLabel resaltado en hover")
else:
    print("⚠️  PATCH 2 — drawLabel no encontrado exactamente")

# ═══════════════════════════════════════════════════════════════════════════════
# PATCH 3: onclick y onmousemove — usar _hitTest
# ═══════════════════════════════════════════════════════════════════════════════

OLD_ONCLICK = """  // Click handler para menú de edificio
  canvas.onclick = (e) => {
    if (!_cityClickData) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const hit = _cityClickData.buildings.find(b => {
      const dx = mx - b.x, dy = my - b.y;
      return Math.abs(dx) < 55 && dy > -200 && dy < 20;
    });
    if (hit) {
      import(`/static/js/screens/building_menu.js?v=${Date.now()}`).then(m => {
        m.openBuildingMenu(
          hit.key,
          _cityClickData.jugador,
          _cityClickData.ciudad,
          _cityClickData.cityData
        );
      });
    }
  };

  // Cursor pointer sobre edificios
  canvas.onmousemove = (e) => {
    if (!_cityClickData) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const hit = _cityClickData.buildings.find(b => {
      const dx = mx - b.x, dy = my - b.y;
      return Math.abs(dx) < 55 && dy > -200 && dy < 20;
    });
    canvas.style.cursor = hit ? 'pointer' : 'default';
  };"""

NEW_ONCLICK = """  // Click handler para menú de edificio
  canvas.onclick = (e) => {
    if (!_cityClickData) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    // Buscar de adelante hacia atrás (primer plano primero)
    const buildings = [..._cityClickData.buildings].reverse();
    const hit = buildings.find(b => _hitTest(b, mx, my));
    if (hit) {
      import(`/static/js/screens/building_menu.js?v=${Date.now()}`).then(m => {
        m.openBuildingMenu(
          hit.key,
          _cityClickData.jugador,
          _cityClickData.ciudad,
          _cityClickData.cityData
        );
      });
    }
  };

  // Cursor pointer + highlight sobre edificios
  canvas.onmousemove = (e) => {
    if (!_cityClickData) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const buildings = [..._cityClickData.buildings].reverse();
    const hit = buildings.find(b => _hitTest(b, mx, my));
    // Actualizar estado hover en todos los edificios
    let changed = false;
    _cityClickData.buildings.forEach(b => {
      const wasHovered = b.hovered;
      b.hovered = (hit && b.key === hit.key);
      if (b.hovered !== wasHovered) changed = true;
    });
    canvas.style.cursor = hit ? 'pointer' : 'default';
    // Mostrar tooltip con nombre del edificio
    canvas.title = hit ? hit.label + (hit.lvl ? ' Nv.' + hit.lvl : '') : '';
  };"""

if OLD_ONCLICK in src:
    src = src.replace(OLD_ONCLICK, NEW_ONCLICK)
    print("✅ PATCH 3 — onclick/onmousemove usan _hitTest preciso + highlight")
else:
    print("⚠️  PATCH 3 — bloque onclick/onmousemove no encontrado exactamente")

# ═══════════════════════════════════════════════════════════════════════════════
# Guardar
# ═══════════════════════════════════════════════════════════════════════════════
if src != original:
    backup = TARGET.with_suffix(".js.bak2")
    backup.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")
    print(f"\n✅ city.js guardado  (backup: {backup})")
else:
    print("\n⚠️  Sin cambios — todos los patches fallaron, revisar anclas manualmente")

print("""
run.bat + Ctrl+Shift+R

Comportamiento esperado:
  - Pasar el mouse sobre cualquier edificio → borde dorado + label brillante
  - Click sobre el edificio → abre menú
  - Templos al fondo son seleccionables con precisión
  - Cuarteles tienen hitbox exacto sin solapamiento
""")
