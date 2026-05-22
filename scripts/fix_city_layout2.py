"""
fix_city_layout2.py
Eternal Warriors v3.0 — Layout isométrico correcto para city.js

PROBLEMA:
  Los edificios usaban offsets cartesianos (cx±N, cy±N) ignorando la
  proyección isométrica del terreno. El rombo de tierra tiene radio Y=80px,
  pero los edificios del fondo estaban a cy-110/cy-120 → fuera del rombo.

SOLUCIÓN:
  Función iso(col, row) que convierte coordenadas de celda del grid
  (mismo sistema que drawTerrain: TW=64, TH=32, cols=14, rows=10)
  a píxeles exactos. Cada edificio se asigna a una celda concreta.

  Grid de celdas (col, row) con origen en centro del rombo (7, 5):
    col va de 0 (izq) a 13 (der)  → X isométrico
    row va de 0 (fondo) a 9 (frente) → profundidad (Y)

  Distribución en el rombo (4 filas, dualidad luz/sombra):
    Fila 0 (row=1): Santuario, Templo Luz, Templo Guerra  — fondo
    Fila 1 (row=3): Universidad, C.Ciudad, C.Viajes       — segundo plano
    Fila 2 (row=5): Almacén, Templo Tierra, Torre, Escondite — medio
    Fila 3 (row=7): Casa, Cuartel Luz, Herrería, Cuartel Fuego — frente
"""

from pathlib import Path
import sys

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")

if not TARGET.exists():
    print(f"ERROR: No se encontró el archivo en:\n  {TARGET}")
    sys.exit(1)

src = TARGET.read_text(encoding="utf-8")

# ── Ancla OLD ────────────────────────────────────────────────────────────────
OLD = """function getLayout(c, cx, cy) {
  const lv = k => Number(c[k]||0);
  // Coordenadas isométricas: filas hacia el frente bajan en Y.
  // Dualidad: izquierda = luz (AlalaiA), derecha = sombra (KarlakÁ).
  // iy = valor de profundidad para ordenar el pintado (painter's algorithm).
  return [
    // ── Fila 0: fondo lejano (templos y santuario) ──────────────────────────
    { key:'SANTUARIO_ARCANO',    label:'Santuario',   lvl:lv('SANTUARIO_ARCANO'),
      x:cx-55,  y:cy-110, iy:cy-110, type:'sanctuary' },           // Luz — izquierda
    { key:'TEMPLO_3',            label:'Templo Luz',  lvl:lv('TEMPLO_3'),
      x:cx+10,  y:cy-120, iy:cy-120, type:'temple', accent:'#7ec8e3' }, // Luz — centro
    { key:'TEMPLO_2',            label:'Templo Guerra', lvl:lv('TEMPLO_2'),
      x:cx+85,  y:cy-105, iy:cy-105, type:'temple', accent:'#c0452a' }, // Sombra — derecha

    // ── Fila 1: segundo plano ────────────────────────────────────────────────
    { key:'UNIVERSIDAD',         label:'Universidad', lvl:lv('UNIVERSIDAD'),
      x:cx-115, y:cy-70,  iy:cy-70,  type:'university' },          // Luz
    { key:'CENTRO_DE_CIUDAD',    label:'C.Ciudad',    lvl:lv('CENTRO_DE_CIUDAD'),
      x:cx,     y:cy-65,  iy:cy-65,  type:'cityhall' },            // Centro — focal
    { key:'CENTRO_DE_VIAJES',    label:'C.Viajes',    lvl:lv('CENTRO_DE_VIAJES'),
      x:cx+115, y:cy-70,  iy:cy-70,  type:'travel' },              // Sombra

    // ── Fila 2: plano medio ──────────────────────────────────────────────────
    { key:'ALMACEN',             label:'Almacén',     lvl:lv('ALMACEN'),
      x:cx-120, y:cy-20,  iy:cy-20,  type:'warehouse' },           // Luz
    { key:'TEMPLO_1',            label:'Templo Tierra', lvl:lv('TEMPLO_1'),
      x:cx-40,  y:cy-18,  iy:cy-18,  type:'temple', accent:'#8a9040' }, // Luz-centro
    { key:'TORRE_DE_VIGILANCIA', label:'Torre',       lvl:lv('TORRE_DE_VIGILANCIA'),
      x:cx+40,  y:cy-18,  iy:cy-18,  type:'watchtower' },          // Sombra-centro
    { key:'ESCONDITE',           label:'Escondite',   lvl:lv('ESCONDITE'),
      x:cx+120, y:cy-20,  iy:cy-20,  type:'hideout' },             // Sombra

    // ── Fila 3: primer plano ─────────────────────────────────────────────────
    { key:'CASA',                label:'Casa',        lvl:lv('CASA'),
      x:cx-118, y:cy+40,  iy:cy+40,  type:'house' },               // Luz
    { key:'CUARTEL_1',           label:'Cuartel Luz', lvl:lv('CUARTEL_1'),
      x:cx-40,  y:cy+38,  iy:cy+38,  type:'barracks' },            // Luz-centro
    { key:'HERRERIA',            label:'Herrería',    lvl:lv('HERRERIA'),
      x:cx+40,  y:cy+38,  iy:cy+38,  type:'forge' },               // Sombra-centro
    { key:'CUARTEL_2',           label:'Cuartel Fuego', lvl:lv('CUARTEL_2'),
      x:cx+118, y:cy+40,  iy:cy+40,  type:'barracks' },            // Sombra
  ];
}"""

# ── Ancla NEW ────────────────────────────────────────────────────────────────
NEW = """function getLayout(c, cx, cy) {
  const lv = k => Number(c[k]||0);
  // iso(dc, dr): convierte desplazamiento de celda respecto al centro del grid
  // al mismo sistema de proyección que drawTerrain (TW=64, TH=32).
  // dc = columnas desde centro (negativo=izq/luz, positivo=der/sombra)
  // dr = filas desde centro    (negativo=fondo, positivo=frente)
  const TW = 64, TH = 32;
  const iso = (dc, dr) => ({
    x: cx + (dc - dr) * TW / 2,
    y: cy + (dc + dr) * TH / 2
  });

  const p = (dc, dr, key, label, type, extra={}) => {
    const {x, y} = iso(dc, dr);
    return { key, label, lvl:lv(key), x, y, iy:y, type, ...extra };
  };

  // Grid de 14×10 celdas. Centro = (0,0). Límite isométrico ~radio dc+dr≤5.
  // Dualidad: dc<0 = lado luz (AlalaiA), dc>0 = lado sombra (KarlakÁ).
  //
  //  dr=-4 ──── fondo más lejano
  //  dr=-2 ──── segundo plano
  //  dr= 0 ──── plano medio
  //  dr=+2 ──── primer plano
  //
  return [
    // ── Fila 0: fondo (dr=-4) ───────────────────────────────────────────────
    p(-2, -4, 'SANTUARIO_ARCANO', 'Santuario',    'sanctuary'),
    p( 0, -4, 'TEMPLO_3',         'Templo Luz',   'temple', {accent:'#7ec8e3'}),
    p(+2, -4, 'TEMPLO_2',         'Templo Guerra','temple', {accent:'#c0452a'}),

    // ── Fila 1: segundo plano (dr=-2) ───────────────────────────────────────
    p(-3, -2, 'UNIVERSIDAD',      'Universidad',  'university'),
    p( 0, -2, 'CENTRO_DE_CIUDAD', 'C.Ciudad',     'cityhall'),
    p(+3, -2, 'CENTRO_DE_VIAJES', 'C.Viajes',     'travel'),

    // ── Fila 2: plano medio (dr=0) ──────────────────────────────────────────
    p(-4,  0, 'ALMACEN',          'Almacén',      'warehouse'),
    p(-1,  0, 'TEMPLO_1',         'Templo Tierra','temple', {accent:'#8a9040'}),
    p(+1,  0, 'TORRE_DE_VIGILANCIA','Torre',      'watchtower'),
    p(+4,  0, 'ESCONDITE',        'Escondite',    'hideout'),

    // ── Fila 3: primer plano (dr=+2) ────────────────────────────────────────
    p(-4, +2, 'CASA',             'Casa',         'house'),
    p(-1, +2, 'CUARTEL_1',        'Cuartel Luz',  'barracks'),
    p(+1, +2, 'HERRERIA',         'Herrería',     'forge'),
    p(+4, +2, 'CUARTEL_2',        'Cuartel Fuego','barracks'),
  ];
}"""

count = src.count(OLD)
if count != 1:
    print(f"ERROR: ancla encontrada {count} veces (esperado 1). Abortando.")
    sys.exit(1)

src = src.replace(OLD, NEW)
TARGET.write_text(src, encoding="utf-8")

print("OK — getLayout() reescrito con proyección isométrica real.")
print()
print("Para verificar:")
print("  Abre http://127.0.0.1:8000/game en el navegador.")
print("  Todos los edificios deben estar dentro del rombo de tierra,")
print("  en 4 filas diagonales ordenadas de fondo a frente.")
print("  Si algún edificio sigue fuera del rombo, reporta cuál y en qué dirección.")
