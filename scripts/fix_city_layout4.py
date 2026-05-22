"""
fix_city_layout4.py
Eternal Warriors v3.0 — Layout definitivo: escala + posiciones corregidas

DIAGNÓSTICO FINAL:
  - Con nivel 44, sc = 0.38 + 44*0.013 = 0.952
  - drawWarehouse: w = 68 * 0.952 = 65px → se extiende 32px a cada lado del centro
  - En dc=-3: x = cx - 128. Borde izq del almacén = cx - 160 → sale del rombo visual
  - drawSanctuary/Temple/CityHall son aún más altos → se cortan por arriba del canvas

SOLUCIÓN:
  1. drawBuilding: reducir escala base y cap máximo — edificios más pequeños y uniformes
  2. getLayout: mover edificios grandes (warehouse, university) a dc=±2 en lugar de ±3
     y usar dr más conservador para los del fondo
  3. Santuario y temploss del fondo a dr=-2 (no -3) para no cortarse por arriba

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_city_layout4.py
"""

from pathlib import Path
import re, sys

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")

if not TARGET.exists():
    print(f"ERROR: No se encontró:\n  {TARGET}")
    sys.exit(1)

src = TARGET.read_text(encoding="utf-8")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 1 — drawBuilding: escala más pequeña y uniforme
# Ancla exacta (verificada en city.js):
# ══════════════════════════════════════════════════════════════════════════════
OLD_SC = (
    "function drawBuilding(ctx, b, c) {\n"
    "  const lvl = b.lvl || 0;\n"
    "  const scMax = b.type==='sanctuary' ? 20 : (b.type==='cityhall' ? 35 : b.type==='watchtower' ? 30 : 40);\n"
    "  const sc = 0.38 + Math.min(lvl,scMax)*0.013;"
)
NEW_SC = (
    "function drawBuilding(ctx, b, c) {\n"
    "  const lvl = b.lvl || 0;\n"
    "  // Escala máxima reducida: edificios caben dentro de una celda (32px)\n"
    "  const scMax = b.type==='cityhall' ? 18 : b.type==='sanctuary' ? 14 : 12;\n"
    "  const sc = 0.30 + Math.min(lvl,scMax)*0.012;"
)

c1 = src.count(OLD_SC)
if c1 != 1:
    print(f"ERROR fix 1 (escala): ancla encontrada {c1} veces. Abortando.")
    sys.exit(1)
src = src.replace(OLD_SC, NEW_SC)
print("OK fix 1: escala de edificios reducida (sc base 0.30, caps 12-18)")

# ══════════════════════════════════════════════════════════════════════════════
# FIX 2 — getLayout: posiciones compactas, todas dentro del rombo
# Reemplaza el bloque completo con regex (robusto ante versiones previas)
# ══════════════════════════════════════════════════════════════════════════════
pattern = r'function getLayout\(c, cx, cy\) \{.+?\n\}'
match = re.search(pattern, src, re.DOTALL)
if not match:
    print("ERROR fix 2: no se encontró getLayout. Abortando.")
    sys.exit(1)

OLD_LAYOUT = match.group(0)

NEW_LAYOUT = """\
function getLayout(c, cx, cy) {
  const lv = k => Number(c[k]||0);

  // iso(dc, dr): misma proyección que drawTerrain (TW=64, TH=32)
  // dc neg = izquierda/AlalaiA, dc pos = derecha/KarlakÁ
  // dr neg = fondo, dr pos = frente
  // Límite conservador: |dc|+|dr| <= 3 para edificios grandes, <= 4 para pequeños
  const TW = 64, TH = 32;
  const iso = (dc, dr) => ({
    x: cx + (dc - dr) * TW / 2,
    y: cy + (dc + dr) * TH / 2
  });
  const p = (dc, dr, key, label, type, extra={}) => {
    const {x, y} = iso(dc, dr);
    return { key, label, lvl:lv(key), x, y, iy:y, type, ...extra };
  };

  // Mapa de celdas — compacto, simétrico, dentro del rombo:
  //
  //               [-1,-2]Santuario  [+1,-2]TemploLuz
  //   [-2,-1]Univ   [0,-1]C.Ciudad   [+2,-1]TemploGuerra
  //   [-2, 0]Almacén  [-1,0]TplTierra  [+1,0]Torre  [+2,0]C.Viajes
  //   [-2,+1]Casa  [-1,+1]CuartelLuz  [+1,+1]Herrería  [+2,+1]CuartelFuego
  //                    [0,+2]Escondite
  //
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

    // ── Muy frente (centro) ──────────────────────────────────────────────────
    p( 0, +2, 'ESCONDITE',        'Escondite',     'hideout'),
  ];
}"""

if OLD_LAYOUT not in src:
    print("ERROR fix 2: bloque OLD no encontrado literalmente. Abortando.")
    sys.exit(1)

count = src.count(OLD_LAYOUT)
if count != 1:
    print(f"ERROR fix 2: ancla encontrada {count} veces. Abortando.")
    sys.exit(1)

src = src.replace(OLD_LAYOUT, NEW_LAYOUT)
print("OK fix 2: getLayout() v4 — 14 edificios, celdas |dc|+|dr|<=3")

# ══════════════════════════════════════════════════════════════════════════════
# Guardar
# ══════════════════════════════════════════════════════════════════════════════
TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO — city.js actualizado.")
print()
print("Para verificar:")
print("  Recarga con Ctrl+Shift+R en http://127.0.0.1:8000/game")
print("  Todos los edificios deben estar dentro del rombo.")
print("  Santuario y Templo Luz al fondo centro-izquierda/derecha.")
print("  C.Ciudad como edificio focal en el centro.")
print("  Cuarteles y Herrería al frente.")
