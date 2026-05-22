"""
fix_16_layout_desde_cero.py

Reescribe getLayout() siguiendo las imágenes de referencia:
- C.Ciudad: fondo centro (eje de simetría)
- Templos: diagonal izquierda, 3 en fila descendente
- Cuarteles: diagonal derecha, 2 en fila descendente  
- Santuario: centro-izquierda medio
- Almacén / Casa: izquierda medio-bajo
- Universidad / C.Viajes: derecha medio-bajo
- Herrería / Escondite: centro inferior

Todo en coordenadas relativas a cx,cy — el canvas NO se mueve.
Las zonas se calculan automáticamente desde b.x,b.y con _DIMS.

Ejecutar desde: E:\\0000ew V2Claude\\
"""
import pathlib, sys

TARGET = pathlib.Path("frontend/js/screens/city.js")
if not TARGET.exists():
    sys.exit(f"ERROR: {TARGET}")

src = TARGET.read_text(encoding="utf-8")
original = src

# Encontrar y reemplazar getLayout completo
start = src.index("function getLayout(c, cx, cy, rx, ry) {")
depth = 0
i = start
while i < len(src):
    if src[i] == '{': depth += 1
    elif src[i] == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
    i += 1

# Layout basado en las imágenes de referencia.
# cx,cy = centro del rombo de la muralla en pantalla.
# Proyección isométrica 2:1: mover 1 unidad en profundidad = 0.5 unidades en Y pantalla.
# rx≈160, ry≈80 a nivel 40.
# Posiciones expresadas como fracción de rx/ry para escalar con la muralla.

NEW_LAYOUT = """function getLayout(c, cx, cy, rx, ry) {
  const lv = k => Number(c[k] || 0);

  // Posición isométrica limpia.
  // ox = desplazamiento horizontal desde cx
  // oy = desplazamiento vertical final en pantalla (ya proyectado)
  // La zona de interacción se calcula en drawBuilding con _DIMS.
  const b = (ox, oy, key, label, type, extra={}) => ({
    key, label, type,
    lvl: lv(key),
    x: cx + ox,
    y: cy + oy,
    zx:0, zy:0, zw:0, zh:0,
    hovered: false,
    ...extra,
  });

  // Referencia visual (imágenes 3 y 4):
  // - C.Ciudad: fondo centro, más alto
  // - Templos: columna izquierda, escalonados hacia el jugador
  // - Cuarteles: columna derecha, escalonados hacia el jugador
  // - Santuario: centro, altura media
  // - Almacén, Casa: izquierda media-baja
  // - Herrería, C.Viajes: derecha media-baja
  // - Universidad, Escondite: frente centro

  // Escala base con la muralla
  const sx = rx / 160;  // factor escala horizontal
  const sy = ry / 80;   // factor escala vertical (ya es mitad del horizontal)

  return [
    // ── FONDO: C.Ciudad centrado ──────────────────────────────────────────
    b(      0,  -ry*1.00, 'CENTRO_DE_CIUDAD', 'C.Ciudad',   'cityhall'),

    // ── DIAGONAL IZQUIERDA: Templos (fondo→frente) ────────────────────────
    b( -rx*0.55, -ry*0.60, 'TEMPLO_1', 'Templo I',   'temple', {accentKey:'blue'}),
    b( -rx*0.70, -ry*0.20, 'TEMPLO_2', 'Templo II',  'temple', {accentKey:'gold'}),
    b( -rx*0.75,  ry*0.15, 'TEMPLO_3', 'Templo III', 'temple', {accentKey:'purple'}),

    // ── DIAGONAL DERECHA: Cuarteles ───────────────────────────────────────
    b(  rx*0.55, -ry*0.40, 'CUARTEL_1', 'Cuartel I',  'barracks', {accentKey:'red1'}),
    b(  rx*0.70,  ry*0.05, 'CUARTEL_2', 'Cuartel II', 'barracks', {accentKey:'red2'}),

    // ── CENTRO-IZQUIERDA: Santuario ───────────────────────────────────────
    b( -rx*0.25, -ry*0.30, 'SANTUARIO_ARCANO', 'Santuario',   'sanctuary'),

    // ── IZQUIERDA MEDIA: Casa y Almacén ───────────────────────────────────
    b( -rx*0.60,  ry*0.50, 'CASA',    'Casa',    'house'),
    b( -rx*0.30,  ry*0.35, 'ALMACEN', 'Almacén', 'warehouse'),

    // ── DERECHA MEDIA: Herrería y C.Viajes ────────────────────────────────
    b(  rx*0.30,  ry*0.35, 'HERRERIA',         'Herrería', 'forge'),
    b(  rx*0.65,  ry*0.50, 'CENTRO_DE_VIAJES', 'C.Viajes', 'travel'),

    // ── FRENTE CENTRO: Universidad y Escondite ────────────────────────────
    b( -rx*0.20,  ry*0.65, 'UNIVERSIDAD', 'Universidad', 'university'),
    b(  rx*0.20,  ry*0.65, 'ESCONDITE',   'Escondite',   'hideout'),
  ];
}"""

src = src[:start] + NEW_LAYOUT + src[end:]

# Guardar
if src != original:
    backup = TARGET.with_suffix(".js.bak7")
    backup.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")
    print(f"✅ getLayout reescrito desde cero")
    print(f"   Backup: {backup}")
else:
    print("⚠️  Sin cambios")

print("""
run.bat + Ctrl+Shift+R

Layout siguiendo referencias:
  Fondo:          C.Ciudad (centro)
  Diagonal izq:   Templo I → II → III (fondo a frente)
  Diagonal der:   Cuartel I → II (fondo a frente)
  Centro izq:     Santuario Arcano
  Izq media:      Casa + Almacén
  Der media:      Herrería + C.Viajes
  Frente centro:  Universidad + Escondite
""")
