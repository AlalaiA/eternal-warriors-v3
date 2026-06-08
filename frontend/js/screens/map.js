/**
 * ETERNAL WARRIORS v3.0 — map.js
 * Mapa Imperial: canvas 2D con zoom/pan, todas las entidades del mundo,
 * selección de coordenadas para órdenes, trayectorias de misiones activas.
 */
'use strict';

// ── Estado ────────────────────────────────────────────────────────────────────

let _canvas, _ctx, _container;
let _jugador = '', _ciudad = '';

// Datos del mundo
let _entities   = null;   // {inactivos, dioses, cuevas, portales, karlaka}
let _ciudades   = [];     // ciudades de jugadores activos
let _ordenes    = [];     // trayectorias activas

// Viewport
let _scale    = 0.85;     // zoom actual (tiles → px)
let _offsetX  = 0;        // pan X en px
let _offsetY  = 0;        // pan Y en px
const MAPA_W  = 1000;
const MAPA_H  = 1000;
const MIN_SCALE = 0.15;
const MAX_SCALE = 12;

// Interacción
let _drag = false, _dragX = 0, _dragY = 0;
let _hovered = null;
let _selected = null;     // entidad seleccionada
let _coordCallback = null; // callback cuando se selecciona coordenada para orden

// Timers
let _syncTimer = null, _animTimer = null;
let _animFrame = 0;

// Colores por categoría
const CAT_COLOR = {
  CIUDAD_JUGADOR:      '#c9a84c',
  CIUDAD_PROPIA:       '#4caf50',
  CIUDAD_ALIADA:       '#5bbfff',
  CIUDAD_VITAMINIZADA: '#ff80ff',
  INACTIVOS:           '#6ba3e0',
  INACTIVOS_REN:       '#a0c8f0',
  DIOSES:              '#9b6ad6',
  CUEVAS:              '#e07050',
  PORTALES:            '#50d0d0',
  KARLAKA:             '#e03030',
};

const CAT_LABEL = {
  CIUDAD_JUGADOR:      'Ciudad rival',
  CIUDAD_PROPIA:       'Mi ciudad',
  CIUDAD_ALIADA:       'Ciudad aliada',
  CIUDAD_VITAMINIZADA: 'Vitaminizada',
  INACTIVOS:           'Ciudad inactiva',
  INACTIVOS_REN:       'Inactivo (ren.)',
  DIOSES:              'Dios',
  CUEVAS:              'Cueva',
  PORTALES:            'Portal',
  KARLAKA:             'KarlakÁ',
};

// Alianza de Joticalindo y vitaminizados
let _alianzaSet = new Set(); // cargado dinámicamente desde /api/alliances/{jugador}
const VITAMINIZADOS_SET    = new Set(['ALALAIA','ADMIN']);

// Estado de capas visibles
let _capas = {
  humanos:       true,
  alianza:       true,
  vitaminizados: true,
  inactivos:     true,
  inactivos_ren: false,
  dioses:        true,
  cuevas:        true,
  portales:      true,
  karlaka:       true,
};

// ── Coordenadas ───────────────────────────────────────────────────────────────

function _worldToScreen(wx, wy) {
  return {
    sx: wx * _scale + _offsetX,
    sy: (MAPA_H - wy) * _scale + _offsetY,  // Y invertido: 0 = abajo
  };
}

function _screenToWorld(sx, sy) {
  return {
    wx: (sx - _offsetX) / _scale,
    wy: MAPA_H - (sy - _offsetY) / _scale,  // Y invertido
  };
}

function _canvasXY(e) {
  const r = _canvas.getBoundingClientRect();
  return [e.clientX - r.left, e.clientY - r.top];
}

// ── Render ────────────────────────────────────────────────────────────────────

function _render() {
  if (!_ctx || !_canvas) return;
  const W = _canvas.width, H = _canvas.height;
  _ctx.clearRect(0, 0, W, H);

  // Fondo
  const bg = _ctx.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, '#010308');
  bg.addColorStop(1, '#060c14');
  _ctx.fillStyle = bg;
  _ctx.fillRect(0, 0, W, H);

  // Grid (solo en zoom suficiente)
  if (_scale >= 1.5) _drawGrid();

  // Zona prohibida KarlakÁ
  _drawZonaKarlaka();

  // Trayectorias de órdenes
  _drawOrdenes();

  // Entidades filtradas por capa
  if (_entities) {
    if (_capas.inactivos)    _drawLayer(_entities.inactivos || [], 2.5, CAT_COLOR.INACTIVOS,  false);
    if (_capas.dioses)       _drawLayer(_entities.dioses    || [], 4,   CAT_COLOR.DIOSES,     true);
    if (_capas.cuevas)       _drawLayer(_entities.cuevas    || [], 3,   CAT_COLOR.CUEVAS,     true);
    if (_capas.portales)     _drawLayer(_entities.portales  || [], 5,   CAT_COLOR.PORTALES,   true);
    if (_capas.karlaka && _entities.karlaka) _drawKarlaka();
  }

  // Ciudades de jugadores
  _drawCiudades();

  // Tooltip
  if (_hovered) _drawTooltip(_hovered);

  // Coordenadas del cursor
  _drawCoordsHUD();

  // Leyenda
  _drawLeyenda();

  // Marca de selección
  if (_selected) _drawSeleccionada(_selected);
}

function _drawGrid() {
  _ctx.strokeStyle = 'rgba(255,255,255,0.04)';
  _ctx.lineWidth   = 0.5;
  const step = 50;
  for (let x = 0; x <= MAPA_W; x += step) {
    const {sx, sy}   = _worldToScreen(x, 0);
    const {sx: sx2, sy: sy2} = _worldToScreen(x, MAPA_H);
    _ctx.beginPath(); _ctx.moveTo(sx, sy); _ctx.lineTo(sx2, sy2); _ctx.stroke();
  }
  for (let y = 0; y <= MAPA_H; y += step) {
    const {sx, sy}   = _worldToScreen(0, y);
    const {sx: sx2, sy: sy2} = _worldToScreen(MAPA_W, y);
    _ctx.beginPath(); _ctx.moveTo(sx, sy); _ctx.lineTo(sx2, sy2); _ctx.stroke();
  }
  // Labels de grid en zoom alto
  if (_scale >= 3) {
    _ctx.fillStyle = 'rgba(255,255,255,0.15)';
    _ctx.font = `${Math.min(11, _scale * 3)}px monospace`;
    for (let x = 0; x <= MAPA_W; x += step) {
      for (let y = 0; y <= MAPA_H; y += step) {
        const {sx, sy} = _worldToScreen(x, y);
        _ctx.fillText(`${x},${y}`, sx + 2, sy + 10);
      }
    }
  }
}

function _drawZonaKarlaka() {
  // Radio cuadrado 50 tiles alrededor de (500,500)
  const {sx: x1, sy: y1} = _worldToScreen(450, 450);
  const {sx: x2, sy: y2} = _worldToScreen(550, 550);
  _ctx.fillStyle   = 'rgba(200,30,30,0.06)';
  _ctx.strokeStyle = 'rgba(200,30,30,0.2)';
  _ctx.lineWidth   = 1;
  _ctx.fillRect(x1, y1, x2 - x1, y2 - y1);
  _ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
}

function _drawOrdenes() {
  if (!_ordenes.length) return;
  const now = Date.now() / 1000;

  _ordenes.forEach(o => {
    const regresando = o.estado === 'REGRESANDO';

    // En regreso: línea va de destino a origen
    const {sx: x1, sy: y1} = _worldToScreen(o.x_orig, o.y_orig);
    const {sx: x2, sy: y2} = _worldToScreen(o.x_dest, o.y_dest);

    const colMap = {
      ATAQUE:         '#e05050',
      ESPIONAJE:      '#c9a84c',
      DESPLAZAMIENTO: '#6ba3e0',
      TRANSPORTE:     '#80c080',
      FUNDAR:         '#d0a060',
    };
    const colIda    = colMap[o.tipo] || '#888';
    const colVuelta = '#88aaff';  // azul claro para regreso

    // Línea de trayectoria
    _ctx.save();
    _ctx.setLineDash([4 * _scale, 4 * _scale]);
    _ctx.strokeStyle = (regresando ? colVuelta : colIda) + '88';
    _ctx.lineWidth   = 1.5;
    _ctx.beginPath();
    _ctx.moveTo(x1, y1);
    _ctx.lineTo(x2, y2);
    _ctx.stroke();
    _ctx.restore();

    // Punto animado
    let t = 0;
    if (regresando) {
      // Va de x_dest → x_orig
      const durReg = Math.max(1, (o.t_retorno || 0) - (o.t_llegada || 0));
      const elapsed = now - (o.t_llegada || now);
      t = Math.min(1, elapsed / durReg);
      // Interpolar dest→orig
      const px = x2 + (x1 - x2) * t;
      const py = y2 + (y1 - y2) * t;
      _dibujarPunto(px, py, colVuelta);
    } else {
      // Va de x_orig → x_dest
      const dur = Math.max(1, (o.t_llegada || 0) - (o.inicio || 0));
      t = Math.min(1, (now - (o.inicio || now)) / dur);
      const px = x1 + (x2 - x1) * t;
      const py = y1 + (y2 - y1) * t;
      _dibujarPunto(px, py, colIda);
    }
  });
}

function _dibujarPunto(px, py, col) {
  _ctx.beginPath();
  _ctx.arc(px, py, Math.max(3, _scale * 0.8), 0, Math.PI * 2);
  _ctx.fillStyle   = col;
  _ctx.fill();
  _ctx.strokeStyle = '#fff6';
  _ctx.lineWidth   = 1;
  _ctx.stroke();
}

function _dot(x, y, r, fill, stroke) {
  _ctx.beginPath();
  _ctx.arc(x, y, r, 0, Math.PI * 2);
  _ctx.fillStyle = fill;
  _ctx.fill();
  if (stroke) {
    _ctx.strokeStyle = stroke;
    _ctx.lineWidth   = 0.8;
    _ctx.stroke();
  }
}

function _drawLayer(arr, baseR, color, glow) {
  const r = Math.max(1.2, baseR * Math.min(1, _scale * 0.5));
  const W = _canvas.width, H = _canvas.height;

  arr.forEach(e => {
    const {sx, sy} = _worldToScreen(e.x, e.y);
    if (sx < -r || sx > W + r || sy < -r || sy > H + r) return;

    const isHov = _hovered && _hovered.id === e.id;
    const isSel = _selected && _selected.id === e.id;

    if (glow && (isHov || isSel)) {
      _ctx.save();
      _ctx.shadowColor = isSel ? '#fff' : color;
      _ctx.shadowBlur  = isSel ? 14 : 8;
    }
    _dot(sx, sy, isSel ? r * 1.8 : isHov ? r * 1.4 : r, color, isHov ? '#fff8' : color + '88');
    if (glow && (isHov || isSel)) _ctx.restore();

    // Label en zoom alto
    if (_scale >= 4 && e.nombre) {
      _ctx.font      = `${Math.min(10, _scale)}px 'Cinzel',serif`;
      _ctx.fillStyle = color;
      _ctx.textAlign = 'center';
      _ctx.fillText(e.nombre, sx, sy - r - 3);
    }
  });
}

function _drawKarlaka() {
  const k = _entities.karlaka;
  if (!k) return;
  const {sx, sy} = _worldToScreen(k.x, k.y);
  const r = Math.max(6, 10 * Math.min(2, _scale));
  const pulse = 0.6 + 0.4 * Math.sin(_animFrame * 0.08);

  _ctx.save();
  _ctx.shadowColor = '#e03030';
  _ctx.shadowBlur  = 20 * pulse;

  // Anillos pulsantes
  [r * 2.5, r * 1.8, r].forEach((ri, i) => {
    _ctx.beginPath();
    _ctx.arc(sx, sy, ri, 0, Math.PI * 2);
    _ctx.strokeStyle = `rgba(220,40,40,${(0.15 - i * 0.04) * pulse})`;
    _ctx.lineWidth   = 1.5;
    _ctx.stroke();
  });

  _dot(sx, sy, r, '#c02020', '#ff4444');
  // Símbolo ☠ en zoom suficiente
  if (_scale >= 1) {
    _ctx.font      = `${Math.max(10, r * 1.2)}px serif`;
    _ctx.fillStyle = '#ff6666';
    _ctx.textAlign = 'center';
    _ctx.textBaseline = 'middle';
    _ctx.fillText('☠', sx, sy);
    _ctx.textBaseline = 'alphabetic';
  }
  _ctx.restore();

  if (_scale >= 0.5) {
    _ctx.font      = `bold ${Math.min(12, _scale * 4)}px 'Cinzel',serif`;
    _ctx.fillStyle = '#e03030';
    _ctx.textAlign = 'center';
    _ctx.fillText('KarlakÁ', sx, sy - r - 5);
  }
}

function _drawCiudades() {
  const W = _canvas.width, H = _canvas.height;

  // En zoom muy bajo (< 2), agrupar ciudades cercanas en clusters
  if (_scale < 0.3) {
    // Agrupar por jugador — mostrar un solo indicador por jugador
    const porJugador = {};
    _ciudades.forEach(c => {
      if (!porJugador[c.jugador]) porJugador[c.jugador] = [];
      porJugador[c.jugador].push(c);
    });
    Object.entries(porJugador).forEach(([jug, ciudades]) => {
      const esPropia  = jug === _jugador.toUpperCase();
      const esVitam   = VITAMINIZADOS_SET.has(jug);
      const esAliada  = !esPropia && _alianzaSet.has(jug);
      const esRival   = !esPropia && !esVitam && !esAliada;
      if (esVitam  && !_capas.vitaminizados) return;
      if (esAliada && !_capas.alianza)       return;
      if (esRival  && !_capas.humanos)       return;
      const col = esPropia  ? CAT_COLOR.CIUDAD_PROPIA
                : esVitam   ? CAT_COLOR.CIUDAD_VITAMINIZADA
                : esAliada  ? CAT_COLOR.CIUDAD_ALIADA
                :             CAT_COLOR.CIUDAD_JUGADOR;
      // Centroide
      const cx = ciudades.reduce((s, c) => s + c.x, 0) / ciudades.length;
      const cy = ciudades.reduce((s, c) => s + c.y, 0) / ciudades.length;
      const {sx, sy} = _worldToScreen(cx, cy);
      if (sx < -20 || sx > W + 20 || sy < -20 || sy > H + 20) return;

      const r = Math.max(4, Math.min(10, _scale * 3));
      _ctx.save();
      _ctx.shadowColor = col;
      _ctx.shadowBlur  = 6;
      _dot(sx, sy, r, col, '#fff6');
      _ctx.restore();

      // Contador
      _ctx.font      = `bold ${Math.max(8, r)}px 'Cinzel',serif`;
      _ctx.fillStyle = col;
      _ctx.textAlign = 'center';
      _ctx.fillText(ciudades.length > 1 ? `×${ciudades.length}` : jug, sx, sy - r - 3);
    });
    return;
  }

  // Zoom suficiente: un cuadrito igual por ciudad
  const LADO = Math.max(3, Math.min(7, _scale * 0.8)); // tamaño fijo, no depende de nivel_cc

  _ciudades.forEach(c => {
    const {sx, sy} = _worldToScreen(c.x, c.y);
    if (sx < -20 || sx > W + 20 || sy < -20 || sy > H + 20) return;

    const esPropia  = c.jugador === _jugador.toUpperCase();
    const esVitam   = VITAMINIZADOS_SET.has(c.jugador);
    const esAliada  = !esPropia && _alianzaSet.has(c.jugador);
    const esRival   = !esPropia && !esVitam && !esAliada;
    if (esVitam  && !_capas.vitaminizados) return;
    if (esAliada && !_capas.alianza)       return;
    if (esRival  && !_capas.humanos)       return;
    const col = esPropia  ? CAT_COLOR.CIUDAD_PROPIA
              : esVitam   ? CAT_COLOR.CIUDAD_VITAMINIZADA
              : esAliada  ? CAT_COLOR.CIUDAD_ALIADA
              :             CAT_COLOR.CIUDAD_JUGADOR;
    const isHov    = _hovered && _hovered.id === `ciudad-${c.jugador}-${c.nombre}`;
    const isSel    = _selected && _selected.id === `ciudad-${c.jugador}-${c.nombre}`;
    const lado     = isSel ? LADO * 1.6 : isHov ? LADO * 1.3 : LADO;

    if (isHov || isSel) {
      _ctx.save();
      _ctx.shadowColor = col;
      _ctx.shadowBlur  = isSel ? 12 : 6;
    }

    // Cuadrito centrado — todas iguales
    _ctx.fillStyle   = col;
    _ctx.strokeStyle = '#fff5';
    _ctx.lineWidth   = 0.5;
    _ctx.fillRect(sx - lado / 2, sy - lado / 2, lado, lado);
    _ctx.strokeRect(sx - lado / 2, sy - lado / 2, lado, lado);

    if (isHov || isSel) _ctx.restore();

    // Label solo en zoom alto
    if (_scale >= 4) {
      _ctx.font      = `${Math.min(9, _scale)}px 'Cinzel',serif`;
      _ctx.fillStyle = col;
      _ctx.textAlign = 'center';
      _ctx.fillText(c.nombre, sx, sy - lado / 2 - 3);
    }
  });
}

function _drawTooltip(e) {
  const {sx, sy} = _worldToScreen(e.x, e.y);
  const W = _canvas.width;
  const lines = _tooltipLines(e);
  const lh    = 16, pad = 10;
  const tw    = Math.max(...lines.map(l => l.length)) * 6.5 + pad * 2;
  const th    = lines.length * lh + pad * 2;
  let tx = sx + 14, ty = sy - th / 2;
  if (tx + tw > W - 10) tx = sx - tw - 14;
  ty = Math.max(10, Math.min(_canvas.height - th - 10, ty));

  _ctx.fillStyle   = 'rgba(6,8,18,0.95)';
  _ctx.strokeStyle = '#c9a84c88';
  _ctx.lineWidth   = 1;
  _ctx.beginPath();
  _ctx.roundRect(tx, ty, tw, th, 4);
  _ctx.fill();
  _ctx.stroke();

  _ctx.font      = "11px 'Cinzel',serif";
  _ctx.textAlign = 'left';
  lines.forEach((l, i) => {
    _ctx.fillStyle = i === 0 ? '#c9a84c' : '#a09880';
    _ctx.fillText(l, tx + pad, ty + pad + lh * i + 11);
  });
}

function _tooltipLines(e) {
  const lines = [];
  const lbl   = e.nombre || e.clase || e.cat || '?';
  lines.push(`${CAT_LABEL[e.cat] || e.cat}: ${lbl}`);
  lines.push(`📍 (${Math.round(e.x)}, ${Math.round(e.y)})`);
  if (e.jugador)  lines.push(`👤 ${e.jugador}`);
  if (e.muralla)  lines.push(`🛡 Muralla Nv.${e.muralla}`);
  if (e.nivel_cc) lines.push(`🏙 CC Nv.${e.nivel_cc}`);
  if (e.hp)       lines.push(`❤ HP: ${_fmtN(e.hp)}`);
  if (e.pa)       lines.push(`⚔ PA: ${_fmtN(e.pa)}`);
  if (e.capturada_por) lines.push(`🔒 Capturada por ${e.capturada_por}`);
  return lines;
}

function _drawCoordsHUD() {
  if (!_lastMX) return;
  const {wx, wy} = _screenToWorld(_lastMX, _lastMY);
  const txt = `(${Math.round(wx)}, ${Math.round(wy)})  ×${_scale.toFixed(2)}`;
  _ctx.font      = "10px 'Cinzel',serif";
  _ctx.fillStyle = 'rgba(201,168,76,0.5)';
  _ctx.textAlign = 'right';
  _ctx.fillText(txt, _canvas.width - 10, _canvas.height - 8);
}

function _drawLeyenda() {
  const items = [
    ['■', CAT_COLOR.CIUDAD_PROPIA,       'Mi ciudad'],
    ['◆', CAT_COLOR.CIUDAD_ALIADA,       'Aliado'],
    ['◆', CAT_COLOR.CIUDAD_JUGADOR,      'Rival'],
    ['◆', CAT_COLOR.CIUDAD_VITAMINIZADA, 'Vitaminizado'],
    ['●', CAT_COLOR.INACTIVOS,           'Inactivo'],
    ['●', CAT_COLOR.DIOSES,              'Dios'],
    ['●', CAT_COLOR.CUEVAS,              'Cueva'],
    ['●', CAT_COLOR.PORTALES,            'Portal'],
    ['☠', CAT_COLOR.KARLAKA,             'KarlakÁ'],
  ];
  const x = 10, y0 = _canvas.height - items.length * 16 - 10;
  _ctx.font = "10px 'Cinzel',serif";
  items.forEach(([sym, col, lbl], i) => {
    const y = y0 + i * 16;
    _ctx.fillStyle = col;
    _ctx.textAlign = 'left';
    _ctx.fillText(`${sym} ${lbl}`, x, y);
  });
}

function _drawSeleccionada(e) {
  const {sx, sy} = _worldToScreen(e.x, e.y);
  const r = 14;
  _ctx.save();
  _ctx.strokeStyle = '#fff';
  _ctx.lineWidth   = 1.5;
  _ctx.setLineDash([4, 4]);
  _ctx.beginPath();
  _ctx.arc(sx, sy, r, 0, Math.PI * 2);
  _ctx.stroke();
  _ctx.restore();
}

function _fmtN(n) {
  if (!n) return '?';
  n = Number(n);
  if (n >= 1e18) return (n / 1e18).toFixed(1) + 'Qn';
  if (n >= 1e15) return (n / 1e15).toFixed(1) + 'Pd';
  if (n >= 1e12) return (n / 1e12).toFixed(1) + 'T';
  if (n >= 1e9)  return (n / 1e9).toFixed(1)  + 'B';
  if (n >= 1e6)  return (n / 1e6).toFixed(1)  + 'M';
  if (n >= 1e3)  return (n / 1e3).toFixed(1)  + 'K';
  return Math.round(n).toLocaleString('es');
}

// ── Hit testing ───────────────────────────────────────────────────────────────

let _lastMX = 0, _lastMY = 0;

function _hitTest(sx, sy) {
  const threshold = Math.max(6, 8 / _scale);
  const {wx, wy}  = _screenToWorld(sx, sy);
  let best = null, bestD = threshold;

  const check = (arr, getCat) => {
    arr.forEach(e => {
      const dx = e.x - wx, dy = e.y - wy;
      const d  = Math.sqrt(dx * dx + dy * dy);
      if (d < bestD) { bestD = d; best = { ...e, cat: getCat(e) }; }
    });
  };

  if (_entities) {
    if (_capas.inactivos) check(_entities.inactivos || [], () => 'INACTIVOS');
    if (_capas.dioses)    check(_entities.dioses    || [], () => 'DIOSES');
    if (_capas.cuevas)    check(_entities.cuevas    || [], () => 'CUEVAS');
    if (_capas.portales)  check(_entities.portales  || [], () => 'PORTALES');
    if (_capas.karlaka && _entities.karlaka) {
      const k = _entities.karlaka;
      const dx = k.x - wx, dy = k.y - wy;
      const d  = Math.sqrt(dx * dx + dy * dy);
      if (d < bestD) { bestD = d; best = { ...k, cat: 'KARLAKA' }; }
    }
  }

  _ciudades.forEach(c => {
    // Respetar filtros de capa
    const esP  = c.jugador === _jugador.toUpperCase();
    const esV  = VITAMINIZADOS_SET.has(c.jugador);
    const esA  = !esP && _alianzaSet.has(c.jugador);
    const esR  = !esP && !esV && !esA;
    if (esV && !_capas.vitaminizados) return;
    if (esA && !_capas.alianza)       return;
    if (esR && !_capas.humanos)       return;

    const dx = c.x - wx, dy = c.y - wy;
    const d  = Math.sqrt(dx * dx + dy * dy);
    if (d < bestD) {
      bestD = d;
      // Asignar cat correcto para que _renderInfoPanel detecte esPropia
      const cat = esP ? 'CIUDAD_PROPIA'
                : esV ? 'CIUDAD_VITAMINIZADA'
                : esA ? 'CIUDAD_ALIADA'
                :       'CIUDAD_JUGADOR';
      best = { ...c, id: `ciudad-${c.jugador}-${c.nombre}`, cat };
    }
  });

  return best;
}

// ── Panel lateral de info ─────────────────────────────────────────────────────

function _renderInfoPanel(e) {
  const panel = document.getElementById('map-info-panel');
  if (!panel) return;
  if (!e) { panel.innerHTML = _panelVacio(); return; }

  const col     = CAT_COLOR[e.cat] || '#888';
  const nombre  = e.nombre || e.clase || `(${Math.round(e.x)}, ${Math.round(e.y)})`;
  // Sobrescribir cat label para tipos derivados
  const catLabel = e.cat === 'CIUDAD_PROPIA'       ? 'Mi ciudad'
                 : e.cat === 'CIUDAD_ALIADA'        ? 'Ciudad aliada'
                 : e.cat === 'CIUDAD_VITAMINIZADA'  ? 'Vitaminizada'
                 : CAT_LABEL[e.cat] || e.cat;
  const esCiudad  = ['CIUDAD_JUGADOR','CIUDAD_VITAMINIZADA','CIUDAD_ALIADA','CIUDAD_PROPIA'].includes(e.cat);
  const esPropia  = e.cat === 'CIUDAD_PROPIA' || (esCiudad && e.jugador === _jugador.toUpperCase());
  const esAliado  = e.cat === 'CIUDAD_ALIADA' && !esPropia;
  const esEnemigo = esCiudad && !esPropia && !esAliado;
  const esInactivo = e.cat === 'INACTIVOS';
  const esCueva   = e.cat === 'CUEVAS';
  const esDios    = e.cat === 'DIOSES';
  const esPortal  = e.cat === 'PORTALES';

  // Botones de acción según tipo
  let acciones = '';
  const coords = `${Math.round(e.x)},${Math.round(e.y)}`;
  const jugDest = e.jugador || '';

  if (esEnemigo || esInactivo) {
    acciones = `
      <button onclick="window._mapOrden('ATAQUE','${coords}','${jugDest}','${e.nombre||''}')"
        style="${_btnStyle('#2a0a0a','#e05050')}">⚔ Atacar</button>
      <button onclick="window._mapOrden('ESPIONAJE','${coords}','${jugDest}','${e.nombre||''}')"
        style="${_btnStyle('#1a1a0a','#c9a84c')}">🕵 Espiar</button>`;
  }
  if (esAliado) {
    acciones = `
      <button onclick="window._mapOrden('ESPIONAJE','${coords}','${jugDest}','${e.nombre||''}')"
        style="${_btnStyle('#1a1a0a','#5bbfff')}">🕵 Espiar (aliado)</button>
      <button onclick="window._mapOrden('DESPLAZAMIENTO','${coords}','${jugDest}','${e.nombre||''}')"
        style="${_btnStyle('#0a1a2a','#6ba3e0')}">🚶 Desplazar tropas</button>`;
  }
  if (esCueva || esDios) {
    acciones = `
      <button onclick="window._mapOrden('ATAQUE','${coords}','','${e.id||e.nombre||''}')"
        style="${_btnStyle('#2a1a0a','#e07050')}">⚔ Atacar</button>
      <button onclick="window._mapOrden('ESPIONAJE','${coords}','','${e.id||e.nombre||''}')"
        style="${_btnStyle('#1a1a0a','#c9a84c')}">🕵 Espiar</button>`;
  }
  if (esPortal) {
    acciones = `<div style="color:#50d0d0;font-size:10px;margin-top:4px">Portal — requiere condiciones especiales</div>`;
  }
  if (esPropia) {
    acciones = `
      <button onclick="window._mapOrden('DESPLAZAMIENTO','${coords}','${jugDest}','${e.nombre||''}')"
        style="${_btnStyle('#0a1a2a','#6ba3e0')}">🚶 Desplazar tropas aquí</button>
      <button onclick="window._mapOrden('TRANSPORTE','${coords}','${jugDest}','${e.nombre||''}')"
        style="${_btnStyle('#0a1a0a','#80c080')}">📦 Transportar recursos</button>`;
  }

  panel.innerHTML = `
    <div style="border-bottom:1px solid ${col}44;padding-bottom:8px;margin-bottom:10px;">
      <div style="color:${col};font-family:'Cinzel',serif;font-size:12px;letter-spacing:1px;">
        ${catLabel}
      </div>
      <div style="color:#e8e0d0;font-size:14px;font-family:'Cinzel',serif;margin-top:2px;font-weight:600;">
        ${nombre}
      </div>
    </div>

    <div style="font-size:11px;font-family:'Cinzel',serif;color:#888;margin-bottom:10px;">
      📍 (${Math.round(e.x)}, ${Math.round(e.y)})
    </div>

    ${e.jugador ? `<div style="font-size:11px;color:#b0a080;margin-bottom:4px;">👤 ${e.jugador}</div>` : ''}
    ${e.muralla  ? `<div style="font-size:11px;color:#888;margin-bottom:2px;">🛡 Muralla Nv.${e.muralla}</div>` : ''}
    ${e.nivel_cc ? `<div style="font-size:11px;color:#888;margin-bottom:2px;">🏙 C.Ciudad Nv.${e.nivel_cc}</div>` : ''}
    ${e.hp       ? `<div style="font-size:11px;color:#888;margin-bottom:2px;">❤ HP: ${_fmtN(e.hp)}</div>` : ''}
    ${e.pa       ? `<div style="font-size:11px;color:#888;margin-bottom:2px;">⚔ PA: ${_fmtN(e.pa)}</div>` : ''}
    ${e.ca       ? `<div style="font-size:11px;color:#888;margin-bottom:2px;">🛡 CA: ${_fmtN(e.ca)}</div>` : ''}
    ${e.capturada_por ? `<div style="font-size:11px;color:#e07050;margin-bottom:4px;">🔒 Capturada</div>` : ''}

    <div style="margin-top:12px;display:flex;flex-direction:column;gap:6px;">
      ${acciones}
      <button onclick="window._mapUsarCoordsEnOrden(${Math.round(e.x)},${Math.round(e.y)})"
        style="${_btnStyle('#0a0a1a','#6ba3e0')}">
        📌 Usar coordenadas en Ejército
      </button>
    </div>`;
}

function _panelVacio() {
  return `
    <div style="color:#444;font-size:11px;font-family:'Cinzel',serif;text-align:center;padding:20px 0;">
      Haz clic en una entidad<br>para ver sus datos<br>y opciones de acción
    </div>`;
}

function _btnStyle(bg, col) {
  return `background:${bg};border:1px solid ${col}66;color:${col};
    padding:6px 10px;border-radius:4px;cursor:pointer;
    font-family:'Cinzel',serif;font-size:10px;letter-spacing:1px;
    width:100%;text-align:left;transition:background 0.15s;`;
}

// ── Controles de zoom/pan ─────────────────────────────────────────────────────

function _zoom(factor, cx, cy) {
  const newScale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, _scale * factor));
  const ratio    = newScale / _scale;
  _offsetX = cx - ratio * (cx - _offsetX);
  _offsetY = cy - ratio * (cy - _offsetY);
  _scale   = newScale;
  _render();
}

function _centerOn(wx, wy) {
  const W = _canvas.width, H = _canvas.height;
  _offsetX = W / 2 - wx * _scale;
  _offsetY = H / 2 - wy * _scale;
  _render();
}

function _fitAll() {
  const W = _canvas.width, H = _canvas.height;
  _scale   = Math.min(W / MAPA_W, H / MAPA_H) * 0.85;
  _offsetX = (W - MAPA_W * _scale) / 2;
  _offsetY = (H - MAPA_H * _scale) / 2;
  _render();
}

// ── Handlers ──────────────────────────────────────────────────────────────────

function _onWheel(e) {
  e.preventDefault();
  const [cx, cy] = _canvasXY(e);
  _zoom(e.deltaY < 0 ? 1.15 : 0.87, cx, cy);
}

function _onMouseDown(e) {
  _drag  = true;
  _dragX = e.clientX - _offsetX;
  _dragY = e.clientY - _offsetY;
  _canvas.style.cursor = 'grabbing';
}

function _onMouseMove(e) {
  const [sx, sy] = _canvasXY(e);
  _lastMX = sx; _lastMY = sy;

  if (_drag) {
    _offsetX = e.clientX - _dragX;
    _offsetY = e.clientY - _dragY;
    _render();
    return;
  }

  const hit = _hitTest(sx, sy);
  if (hit?.id !== _hovered?.id) {
    _hovered = hit;
    _canvas.style.cursor = hit ? 'pointer' : 'crosshair';
    _render();
  } else {
    // Solo redibujar HUD de coordenadas
    _render();
  }
}

function _onMouseUp() {
  _drag = false;
  _canvas.style.cursor = _hovered ? 'pointer' : 'crosshair';
}

function _onClick(e) {
  if (_drag) return;
  const [sx, sy] = _canvasXY(e);
  const hit = _hitTest(sx, sy);

  if (hit) {
    _selected = hit;
    _renderInfoPanel(hit);
  } else {
    // Click en vacío — seleccionar coordenadas del mapa
    const {wx, wy} = _screenToWorld(sx, sy);
    const coord = { x: Math.round(wx), y: Math.round(wy), cat: 'COORD' };
    _selected = { ...coord, id: 'coord', nombre: `(${coord.x}, ${coord.y})` };
    _renderInfoPanel({ ...coord, cat: 'COORD', nombre: `(${coord.x}, ${coord.y})` });
    window._mapUsarCoordsEnOrden(coord.x, coord.y);
  }
  _render();
}

// ── Handlers globales para botones del panel ──────────────────────────────────

function _setupGlobals() {
  window._mapOrden = (tipo, coords, jugDest, ciudadDest) => {
    const [x, y] = coords.split(',').map(Number);
    // Navegar a la pantalla de ejército con datos prellenados
    sessionStorage.setItem('map_orden_tipo',    tipo);
    sessionStorage.setItem('map_orden_x',       x);
    sessionStorage.setItem('map_orden_y',       y);
    sessionStorage.setItem('map_orden_jug_dest', jugDest);
    sessionStorage.setItem('map_orden_ciudad_dest', ciudadDest);

    // Disparar evento para que app.js cargue la pantalla de ejército
    window.dispatchEvent(new CustomEvent('ew:irAEjercito', {
      detail: { tipo, x, y, jugDest, ciudadDest }
    }));
  };

  window._mapUsarCoordsEnOrden = (x, y) => {
    sessionStorage.setItem('map_orden_x', x);
    sessionStorage.setItem('map_orden_y', y);
    // Notificar si army.js está escuchando
    window.dispatchEvent(new CustomEvent('ew:coordsSeleccionadas', { detail: { x, y } }));
    _showCoordFeedback(x, y);
  };
}

function _showCoordFeedback(x, y) {
  const fb = document.getElementById('map-coord-feedback');
  if (!fb) return;
  fb.textContent = `📌 Coordenadas seleccionadas: (${x}, ${y}) — ve a Ejército para despachar`;
  fb.style.opacity = '1';
  setTimeout(() => { fb.style.opacity = '0'; }, 3000);
}

// ── Controles de teclado ──────────────────────────────────────────────────────

function _onKeyDown(e) {
  const step = 50 / _scale;
  if (e.key === 'ArrowLeft')  { _offsetX += step; _render(); }
  if (e.key === 'ArrowRight') { _offsetX -= step; _render(); }
  if (e.key === 'ArrowUp')    { _offsetY += step; _render(); }
  if (e.key === 'ArrowDown')  { _offsetY -= step; _render(); }
  if (e.key === '+' || e.key === '=') _zoom(1.2, _canvas.width/2, _canvas.height/2);
  if (e.key === '-')           _zoom(0.83, _canvas.width/2, _canvas.height/2);
  if (e.key === 'f' || e.key === 'F') _fitAll();
}

// ── Carga de datos ────────────────────────────────────────────────────────────

async function _loadData() {
  try {
    const [r1, r2, r3] = await Promise.all([
      fetch(`/api/map/entities?jugador=${_jugador}`),
      fetch('/api/map/players'),
      fetch(`/api/map/orders/${_jugador}`),
    ]);
    const d1 = await r1.json();
    const d2 = await r2.json();
    const d3 = await r3.json();

    _entities = d1;
    _ciudades = d2.ciudades || [];
    _ordenes  = (d3.ordenes || []).filter(o => o.estado === 'EN_VIAJE' || o.estado === 'REGRESANDO');
  } catch (e) {
    console.error('map.js _loadData:', e);
  }
}

// ── Botones de control ────────────────────────────────────────────────────────

function _renderControls() {
  return `
    <div style="position:absolute;top:10px;left:10px;display:flex;gap:6px;z-index:10;">
      <button onclick="window._mapFit()" title="Ver todo el mapa" style="${_ctrlBtn()}">⊡</button>
      <button onclick="window._mapZoomIn()" title="Zoom +" style="${_ctrlBtn()}">+</button>
      <button onclick="window._mapZoomOut()" title="Zoom -" style="${_ctrlBtn()}">−</button>
      <button onclick="window._mapGoHome()" title="Ir a mi ciudad" style="${_ctrlBtn('#2a1a08','#c9a84c')}">🏠</button>
      <button onclick="window._mapGoKarlaka()" title="Ver KarlakÁ" style="${_ctrlBtn('#2a0808','#e05050')}">☠</button>
    </div>
    <div style="position:absolute;top:52px;left:10px;display:flex;flex-wrap:wrap;gap:4px;z-index:10;max-width:500px;">
      ${_renderCapas()}
    </div>
    <div id="map-coord-feedback" style="
      position:absolute;bottom:12px;left:50%;transform:translateX(-50%);
      background:rgba(6,8,18,0.9);border:1px solid #c9a84c44;
      color:#c9a84c;font-family:'Cinzel',serif;font-size:11px;
      padding:6px 16px;border-radius:20px;pointer-events:none;
      opacity:0;transition:opacity 0.3s;z-index:20;
    "></div>`;
}

function _ctrlBtn(bg = '#0d0d1a', col = '#c9a84c') {
  return `background:${bg};border:1px solid ${col}44;color:${col};
    width:32px;height:32px;border-radius:6px;cursor:pointer;
    font-size:16px;font-family:monospace;`;
}

window._toggleCapa = function(capa) {
  _capas[capa] = !_capas[capa];
  const btn = document.getElementById('capa-btn-' + capa);
  if (btn) btn.style.opacity = _capas[capa] ? '1' : '0.3';
  _render();
};

function _renderCapas() {
  const defs = [
    ['humanos',       '👤','Humanos',      CAT_COLOR.CIUDAD_JUGADOR],
    ['alianza',       '🤝','Alianza',       CAT_COLOR.CIUDAD_ALIADA],
    ['vitaminizados', '💊','Vitaminizados', CAT_COLOR.CIUDAD_VITAMINIZADA],
    ['inactivos',     '🏚','Inactivos',     CAT_COLOR.INACTIVOS],
    ['dioses',        '🌩','Dioses',        CAT_COLOR.DIOSES],
    ['cuevas',        '🦎','Cuevas',        CAT_COLOR.CUEVAS],
    ['portales',      '🌀','Portales',      CAT_COLOR.PORTALES],
    ['karlaka',       '☠','KarlakÁ',       CAT_COLOR.KARLAKA],
  ];
  return defs.map(([k,ico,lbl,col]) => {
    const on = _capas[k];
    return `<button id="capa-btn-${k}" onclick="window._toggleCapa('${k}')" title="${lbl}"
      style="background:#0d0d1a;border:1px solid ${col}99;color:${col};
        padding:2px 8px;border-radius:4px;cursor:pointer;font-size:10px;
        font-family:'Cinzel',serif;white-space:nowrap;opacity:${on?'1':'0.3'};"
    >${ico} ${lbl}</button>`;
  }).join('');
}

// ── Render principal ──────────────────────────────────────────────────────────

export async function render(container, jugador, ciudad) {
  _jugador = jugador;
  _ciudad  = ciudad;

  // Cargar alianza dinámica del jugador actual
  _alianzaSet = new Set([jugador.toUpperCase()]);
  try {
    const ra = await fetch(`/api/alliances/${jugador}`).then(r => r.json());
    if (ra.alianza && ra.miembros) {
      _alianzaSet = new Set(ra.miembros.map(m => m.toUpperCase()));
    }
  } catch {}
  _selected = null;
  _hovered  = null;

  container.innerHTML = `
    <div style="display:flex;height:100%;position:relative;">
      <div style="flex:1;position:relative;overflow:hidden;">
        <canvas id="map-canvas" style="position:absolute;top:0;left:0;width:100%;height:100%;cursor:crosshair;display:block;"></canvas>
        ${_renderControls()}
      </div>
      <div id="map-info-panel" style="
        flex:0 0 280px;overflow-y:auto;
        background:rgba(6,8,18,0.95);
        border-left:1px solid rgba(201,168,76,0.2);
        padding:16px;font-size:12px;
      ">${_panelVacio()}</div>
    </div>`;

  _canvas = document.getElementById('map-canvas');
  _ctx    = _canvas.getContext('2d');
  _container = container;

  // Tamaño
  function _resize() {
    const wrap = _canvas.parentElement;
    _canvas.width  = wrap.clientWidth;
    _canvas.height = wrap.clientHeight;
    _render();
  }

  // Cargar datos
  await _loadData();

  // Vista inicial: centrar en ciudades del jugador con zoom adaptativo
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      _resize();
      const misCiudades = _ciudades.filter(c => c.jugador === jugador.toUpperCase());
      if (misCiudades.length > 0) {
        const xs = misCiudades.map(c => c.x);
        const ys = misCiudades.map(c => c.y);
        const minX = Math.min(...xs), maxX = Math.max(...xs);
        const minY = Math.min(...ys), maxY = Math.max(...ys);
        const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
        const spanX = maxX - minX, spanY = maxY - minY;
        // Si están muy juntas (span < 10 tiles), usar zoom fijo alto
        if (spanX < 10 && spanY < 10) {
          _scale = 30;
        } else {
          const W = _canvas.width, H = _canvas.height;
          _scale = Math.min(W / (spanX + 20), H / (spanY + 20), MAX_SCALE);
        }
        _centerOn(cx, cy);
      } else {
        _fitAll();
      }
      _render();
    });
  });

  // Eventos canvas
  _canvas.addEventListener('wheel',      _onWheel,     { passive: false });
  _canvas.addEventListener('mousedown',  _onMouseDown);
  _canvas.addEventListener('mousemove',  _onMouseMove);
  _canvas.addEventListener('mouseup',    _onMouseUp);
  _canvas.addEventListener('mouseleave', _onMouseUp);
  _canvas.addEventListener('click',      _onClick);
  window.addEventListener('keydown',     _onKeyDown);
  window.addEventListener('resize',      _resize);

  // Globals de controles
  _setupGlobals();
  window._mapFit      = _fitAll;
  window._mapZoomIn   = () => _zoom(1.3, _canvas.width/2, _canvas.height/2);
  window._mapZoomOut  = () => _zoom(0.77, _canvas.width/2, _canvas.height/2);
  window._mapGoHome   = () => {
    // Centrar en la primera ciudad propia (capital)
    const c = _ciudades.find(c => c.jugador === jugador.toUpperCase());
    if (c) { _scale = 6; _centerOn(c.x, c.y); _render(); }
  };
  window._mapGoKarlaka = () => { _scale = 2; _centerOn(500, 500); };

  // Animación continua (para KarlakÁ pulsante y trayectorias)
  _animTimer = setInterval(() => {
    _animFrame++;
    _render();
  }, 50);  // 20 fps para animaciones

  // Sync de órdenes cada 2s (necesario para ver el punto en movimiento)
  // Sync de entidades cada 15s (cambian poco)
  _syncTimer = setInterval(async () => {
    try {
      const r = await fetch(`/api/map/orders/${_jugador}`);
      const d = await r.json();
      _ordenes = (d.ordenes || []).filter(o => o.estado === 'EN_VIAJE' || o.estado === 'REGRESANDO');
    } catch (_) {}
  }, 2000);

  // Sync completo cada 15s
  setInterval(async () => {
    try {
      const [r1, r2] = await Promise.all([
        fetch(`/api/map/entities?jugador=${_jugador}`),
        fetch('/api/map/players'),
      ]);
      const d1 = await r1.json();
      const d2 = await r2.json();
      _entities = d1;
      _ciudades = d2.ciudades || [];
    } catch (_) {}
  }, 15000);
}

// ── Cleanup ───────────────────────────────────────────────────────────────────

export function cleanup() {
  if (_syncTimer) { clearInterval(_syncTimer); _syncTimer = null; }
  if (_animTimer) { clearInterval(_animTimer); _animTimer = null; }

  if (_canvas) {
    _canvas.removeEventListener('wheel',      _onWheel);
    _canvas.removeEventListener('mousedown',  _onMouseDown);
    _canvas.removeEventListener('mousemove',  _onMouseMove);
    _canvas.removeEventListener('mouseup',    _onMouseUp);
    _canvas.removeEventListener('mouseleave', _onMouseUp);
    _canvas.removeEventListener('click',      _onClick);
  }
  window.removeEventListener('keydown', _onKeyDown);

  // Limpiar globals
  ['_mapFit','_mapZoomIn','_mapZoomOut','_mapGoHome','_mapGoKarlaka',
   '_mapOrden','_mapUsarCoordsEnOrden'].forEach(k => delete window[k]);

  _canvas = null; _ctx = null;
  _entities = null; _ciudades = []; _ordenes = [];
  _selected = null; _hovered = null;
}
