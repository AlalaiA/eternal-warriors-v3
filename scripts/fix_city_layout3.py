"""
fix_city_layout3.py
Eternal Warriors v3.0 — Layout isométrico v3: todas las celdas dentro del rombo

Corre desde: E:\0000ew V2Claude\
Comando:     python fix_city_layout3.py
"""

from pathlib import Path
import sys

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")

if not TARGET.exists():
    print(f"ERROR: No se encontró:\n  {TARGET}")
    sys.exit(1)

src = TARGET.read_text(encoding="utf-8")

# ── Ancla: funciona contra el layout actual (cualquier versión previa) ────────
# Buscamos el bloque completo de getLayout sin importar qué versión haya
import re

pattern = r'(function getLayout\(c, cx, cy\) \{)(.+?)(\n\})'
match = re.search(pattern, src, re.DOTALL)
if not match:
    print("ERROR: No se encontró la función getLayout. Abortando.")
    sys.exit(1)

OLD_BLOCK = match.group(0)

NEW_BLOCK = """function getLayout(c, cx, cy) {
  const lv = k => Number(c[k]||0);

  // iso(dc, dr): proyección isométrica idéntica a drawTerrain (TW=64, TH=32).
  // dc = columnas desde centro del rombo (neg=izq/AlalaiA, pos=der/KarlakÁ)
  // dr = filas desde centro              (neg=fondo, pos=frente)
  // Límite seguro: |dc| + |dr| <= 4  (rombo tiene radio 5 pero edificios ocupan espacio)
  const TW = 64, TH = 32;
  const iso = (dc, dr) => ({
    x: cx + (dc - dr) * TW / 2,
    y: cy + (dc + dr) * TH / 2
  });

  const p = (dc, dr, key, label, type, extra={}) => {
    const {x, y} = iso(dc, dr);
    return { key, label, lvl:lv(key), x, y, iy:y, type, ...extra };
  };

  //  Layout (dc, dr) — todas las celdas con |dc|+|dr| <= 4:
  //
  //          Santuario(-1,-3)  TemploLuz(+1,-3)
  //   Univ(-3,-1)   C.Ciudad(0,-1)   TemploGuerra(+3,-1)  C.Viajes(+2,+1)
  //   Almacén(-3,+1)  TemploTierra(-1,+1)  Torre(+1,+1)  Escondite(+3,+1)
  //     Casa(-2,+2)  CuartelLuz(-1,+3)  Herrería(+1,+3)  CuartelFuego(+2,+2)

  return [
    // ── Fila fondo (dr=-3) ───────────────────────────────────────────────────
    p(-1, -3, 'SANTUARIO_ARCANO', 'Santuario',     'sanctuary'),
    p(+1, -3, 'TEMPLO_3',         'Templo Luz',    'temple', {accent:'#7ec8e3'}),

    // ── Fila segundo plano (dr=-1) ───────────────────────────────────────────
    p(-3, -1, 'UNIVERSIDAD',      'Universidad',   'university'),
    p( 0, -1, 'CENTRO_DE_CIUDAD', 'C.Ciudad',      'cityhall'),
    p(+3, -1, 'TEMPLO_2',         'Templo Guerra', 'temple', {accent:'#c0452a'}),

    // ── Fila plano medio (dr=+1) ─────────────────────────────────────────────
    p(-3, +1, 'ALMACEN',          'Almacén',       'warehouse'),
    p(-1, +1, 'TEMPLO_1',         'Templo Tierra', 'temple', {accent:'#8a9040'}),
    p(+1, +1, 'TORRE_DE_VIGILANCIA','Torre',       'watchtower'),
    p(+3, +1, 'CENTRO_DE_VIAJES', 'C.Viajes',      'travel'),

    // ── Fila primer plano (dr=+2/+3) ────────────────────────────────────────
    p(-2, +2, 'CASA',             'Casa',          'house'),
    p(-1, +3, 'CUARTEL_1',        'Cuartel Luz',   'barracks'),
    p( 0, +3, 'HERRERIA',         'Herrería',      'forge'),
    p(+1, +3, 'ESCONDITE',        'Escondite',     'hideout'),
    p(+2, +2, 'CUARTEL_2',        'Cuartel Fuego', 'barracks'),
  ];
}"""

if OLD_BLOCK not in src:
    print("ERROR: ancla no encontrada literalmente. Abortando.")
    sys.exit(1)

count = src.count(OLD_BLOCK)
if count != 1:
    print(f"ERROR: ancla encontrada {count} veces (esperado 1). Abortando.")
    sys.exit(1)

src = src.replace(OLD_BLOCK, NEW_BLOCK)
TARGET.write_text(src, encoding="utf-8")

print("OK — getLayout() v3: 13 edificios, todas las celdas dentro del rombo.")
print()
print("Para verificar:")
print("  Abre http://127.0.0.1:8000/game y recarga con Ctrl+Shift+R.")
print("  Todos los edificios deben verse dentro del rombo de tierra.")
print("  Si alguno se sale, reporta cuál y hacia qué borde.")
