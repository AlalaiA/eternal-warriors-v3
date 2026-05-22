"""
fix_city_layout5.py
Eternal Warriors v3.0 — Sincronizar getLayout con TW=48 + separar edificios

PROBLEMA ACTUAL:
  - getLayout usa TW=64 pero drawTerrain usa TW=48 → edificios desalineados con el grid
  - Con sc=0.72 los edificios son ~52px de ancho pero las celdas TW=48 son de 24px → solapamiento
  - Solución: getLayout usa TW=48 Y los dc se espacian más (x1.5) para separar edificios

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_city_layout5.py
"""

from pathlib import Path
import sys, re

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
if not TARGET.exists():
    print(f"ERROR: No se encontró:\n  {TARGET}")
    sys.exit(1)

src = TARGET.read_text(encoding="utf-8")

# Reemplazar getLayout completo con regex (robusto)
pattern = r'function getLayout\(c, cx, cy\) \{.+?\n\}'
match = re.search(pattern, src, re.DOTALL)
if not match:
    print("ERROR: No se encontró getLayout. Abortando.")
    sys.exit(1)

OLD = match.group(0)

NEW = """\
function getLayout(c, cx, cy) {
  const lv = k => Number(c[k]||0);

  // TW/TH deben coincidir con drawTerrain
  // dc y dr multiplicados por 1.8 para separar edificios (evitar solapamiento a sc=0.72)
  const TW = 48, TH = 24;
  const iso = (dc, dr) => ({
    x: cx + (dc - dr) * TW / 2 * 1.8,
    y: cy + (dc + dr) * TH / 2 * 1.8
  });
  const p = (dc, dr, key, label, type, extra={}) => {
    const {x, y} = iso(dc, dr);
    return { key, label, lvl:lv(key), x, y, iy:y, type, ...extra };
  };

  return [
    // ── Fondo ────────────────────────────────────────────────────────────────
    p(-1, -2, 'SANTUARIO_ARCANO', 'Santuario',     'sanctuary'),
    p(+1, -2, 'TEMPLO_3',         'Templo Luz',    'temple',   {accent:'#7ec8e3'}),

    // ── Segundo plano ────────────────────────────────────────────────────────
    p(-2, -1, 'UNIVERSIDAD',      'Universidad',   'university'),
    p( 0, -1, 'CENTRO_DE_CIUDAD', 'C.Ciudad',      'cityhall'),
    p(+2, -1, 'TEMPLO_2',         'Templo Guerra', 'temple',   {accent:'#c0452a'}),

    // ── Plano medio ──────────────────────────────────────────────────────────
    p(-2,  0, 'ALMACEN',          'Almacén',       'warehouse'),
    p(-1,  0, 'TEMPLO_1',         'Templo Tierra', 'temple',   {accent:'#8a9040'}),
    p(+1,  0, 'TORRE_DE_VIGILANCIA','Torre',        'watchtower'),
    p(+2,  0, 'CENTRO_DE_VIAJES', 'C.Viajes',      'travel'),

    // ── Primer plano ─────────────────────────────────────────────────────────
    p(-2, +1, 'CASA',             'Casa',          'house'),
    p(-1, +1, 'CUARTEL_1',        'Cuartel 1',     'barracks'),
    p(+1, +1, 'HERRERIA',         'Herrería',      'forge'),
    p(+2, +1, 'CUARTEL_2',        'Cuartel 2',     'barracks'),

    // ── Frente centro ────────────────────────────────────────────────────────
    p( 0, +2, 'ESCONDITE',        'Escondite',     'hideout'),
  ];
}"""

if OLD not in src:
    print("ERROR: ancla getLayout no encontrada literalmente. Abortando.")
    sys.exit(1)

src = src.replace(OLD, NEW)
print("OK fix: getLayout — TW=48, separación ×1.8")

TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO — city.js actualizado.")
print()
print("Para verificar:")
print("  Recarga con Ctrl+Shift+R en http://127.0.0.1:8000/game")
print("  Los edificios deben estar bien separados entre sí.")
print("  Si siguen solapados, reporta cuáles y en qué dirección.")
