"""
fix_08_city_layout.py
Corrige el layout de la ciudad en city.js:
1. Todos los templos (1,2,3) y cuarteles (1,2) posicionados y diferenciados visualmente
2. Edificios distribuidos en profundidad real (no amontonados)
3. Cuarteles: rojo/marcial — Templos: azul/dorado/púrpura según número
4. Labels más claros

Ejecutar desde: E:\\0000ew V2Claude\\
"""
import pathlib, sys, re

TARGET = pathlib.Path("frontend/js/screens/city.js")
if not TARGET.exists():
    sys.exit(f"ERROR: No se encuentra {TARGET}")

src = TARGET.read_text(encoding="utf-8")
original = src

# ─── Reemplazar getLayout completo ────────────────────────────────────────────
OLD_LAYOUT = r"function getLayout\(c, cx, cy, rx, ry\) \{.*?\n\}"

NEW_LAYOUT = r"""function getLayout(c, cx, cy, rx, ry) {
  const lv = k => Number(c[k] || 0);
  const pos = (ox, ov) => ({ x: cx + ox, y: cy + ov * 0.5 });
  const b = (ox, ov, key, label, type, extra = {}) => {
    const { x, y } = pos(ox, ov);
    return { key, label, lvl: lv(key), x, y, type, ...extra };
  };

  // Radio interior disponible (85% del rombo de la muralla)
  const ix = rx * 0.82;
  const iy = ry * 0.82;

  // ── Plano fondo (ov más negativo = más al fondo en isométrico) ─────────────
  // C.Ciudad: centro absoluto, fondo
  // Santuario: izquierda fondo
  // Universidad: derecha fondo

  // ── Plano medio ────────────────────────────────────────────────────────────
  // Templo 1 (azul): izquierda media
  // Templo 2 (dorado): centro-derecha media
  // Templo 3 (púrpura): derecha media — el que ya estaba

  // ── Plano medio-bajo ───────────────────────────────────────────────────────
  // Almacén: izquierda
  // C.Viajes: derecha
  // Herrería: centro-derecha

  // ── Primer plano ──────────────────────────────────────────────────────────
  // Casa: izquierda
  // Cuartel 1: centro-izquierda  (rojo marcial)
  // Cuartel 2: centro-derecha    (rojo marcial)
  // Escondite: derecha

  return [
    // ── Fondo ──────────────────────────────────────────────────────────────
    b(      0,    -iy*0.72, 'CENTRO_DE_CIUDAD',  'C.Ciudad',    'cityhall'),
    b( -ix*0.52,  -iy*0.42, 'SANTUARIO_ARCANO',  'Santuario',   'sanctuary'),
    b(  ix*0.52,  -iy*0.42, 'UNIVERSIDAD',        'Universidad', 'university'),

    // ── Plano medio: 3 templos diferenciados ─────────────────────────────
    b( -ix*0.75,  -iy*0.12, 'TEMPLO_1',  'Templo I',   'temple', { accentKey: 'blue'   }),
    b(      0,    -iy*0.18, 'TEMPLO_2',  'Templo II',  'temple', { accentKey: 'gold'   }),
    b(  ix*0.75,  -iy*0.12, 'TEMPLO_3',  'Templo III', 'temple', { accentKey: 'purple' }),

    // ── Plano medio-bajo ─────────────────────────────────────────────────
    b( -ix*0.75,   iy*0.20, 'ALMACEN',           'Almacén',     'warehouse'),
    b(  ix*0.40,   iy*0.14, 'HERRERIA',           'Herrería',    'forge'),
    b(  ix*0.75,   iy*0.20, 'CENTRO_DE_VIAJES',   'C.Viajes',    'travel'),

    // ── Primer plano: 2 cuarteles diferenciados ──────────────────────────
    b( -ix*0.55,   iy*0.55, 'CASA',      'Casa',        'house'),
    b( -ix*0.18,   iy*0.62, 'CUARTEL_1', 'Cuartel I',   'barracks', { accentKey: 'red1' }),
    b(  ix*0.18,   iy*0.62, 'CUARTEL_2', 'Cuartel II',  'barracks', { accentKey: 'red2' }),
    b(  ix*0.55,   iy*0.55, 'ESCONDITE', 'Escondite',   'hideout'),

    // ── Muralla (solo label, sin edificio visible) ────────────────────────
    // La muralla se dibuja aparte como contenedor
  ];
}"""

patched = re.sub(OLD_LAYOUT, NEW_LAYOUT, src, flags=re.DOTALL)
if patched == src:
    print("⚠️  getLayout no encontrado con regex — intentando búsqueda por ancla")
    # Búsqueda por ancla exacta
    anchor = "function getLayout(c, cx, cy, rx, ry) {"
    if anchor in src:
        start = src.index(anchor)
        # Buscar el cierre de la función contando llaves
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
        src = src[:start] + NEW_LAYOUT + src[end:]
        print("✅ getLayout reemplazado via búsqueda por ancla")
    else:
        print("ERROR: No se encontró getLayout en city.js")
        sys.exit(1)
else:
    src = patched
    print("✅ getLayout reemplazado via regex")

# ─── Actualizar drawBuilding para pasar accentKey ────────────────────────────
# Los templos ahora tienen accentKey en lugar de accent directo

OLD_DRAW = """  switch (b.type) {
    case 'cityhall':   artCityHall(ctx, b.x, b.y, lvl);   break;
    case 'sanctuary':  artSanctuary(ctx, b.x, b.y, lvl);  break;
    case 'temple':     artTemple(ctx, b.x, b.y, lvl);     break;
    case 'university': artUniversity(ctx, b.x, b.y, lvl); break;
    case 'warehouse':  artWarehouse(ctx, b.x, b.y, lvl);  break;
    case 'watchtower': artWatchtower(ctx, b.x, b.y, lvl); break;
    case 'travel':     artTravel(ctx, b.x, b.y, lvl);     break;
    case 'house':      artHouse(ctx, b.x, b.y, lvl);      break;
    case 'barracks':   artBarracks(ctx, b.x, b.y, lvl);   break;
    case 'forge':      artForge(ctx, b.x, b.y, lvl);      break;
    case 'hideout':    artHideout(ctx, b.x, b.y, lvl);    break;
  }"""

NEW_DRAW = """  // Paleta de acentos por clave
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
  }"""

if OLD_DRAW in src:
    src = src.replace(OLD_DRAW, NEW_DRAW)
    print("✅ drawBuilding — paleta de acentos añadida")
else:
    print("⚠️  drawBuilding switch no encontrado exactamente — verificar manualmente")

# ─── Actualizar artBarracks para usar accent ─────────────────────────────────
# artBarracks actualmente ignora accent — añadir parámetro y usarlo en la bandera

OLD_BARRACKS_SIG = "function artBarracks(ctx,x,y,lvl){"
NEW_BARRACKS_SIG = "function artBarracks(ctx,x,y,lvl,accent='rgb(200,50,30)'){"

if OLD_BARRACKS_SIG in src:
    # Cambiar la bandera de rojo fijo a usar accent
    src = src.replace(OLD_BARRACKS_SIG, NEW_BARRACKS_SIG)
    # Reemplazar el color fijo de la bandera roja con accent
    src = src.replace(
        "ctx.fillStyle='rgb(140,20,20)';ctx.beginPath();ctx.moveTo(x,y-H*1.32)",
        "ctx.fillStyle=accent;ctx.beginPath();ctx.moveTo(x,y-H*1.32)"
    )
    print("✅ artBarracks — acepta accent, bandera diferenciada por cuartel")
else:
    print("⚠️  artBarracks sig no encontrada exactamente")

# ─── Actualizar artTemple para aceptar accent como parámetro directo ─────────
# artTemple ya acepta accent pero hay que verificar la firma
OLD_TEMPLE_SIG = "function artTemple(ctx,x,y,lvl){"
NEW_TEMPLE_SIG = "function artTemple(ctx,x,y,lvl,accent='rgb(126,200,227)'){"
if OLD_TEMPLE_SIG in src:
    src = src.replace(OLD_TEMPLE_SIG, NEW_TEMPLE_SIG)
    print("✅ artTemple — firma actualizada con accent por defecto")
elif "function artTemple(ctx,x,y,lvl,accent" in src:
    print("ℹ️  artTemple ya tiene parámetro accent")
else:
    print("⚠️  artTemple sig no encontrada — verificar manualmente")

# ─── Guardar ─────────────────────────────────────────────────────────────────
if src != original:
    backup = TARGET.with_suffix(".js.bak")
    backup.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")
    print(f"\n✅ city.js guardado  (backup: {backup})")
else:
    print("\n⚠️  Sin cambios aplicados")

print("""
Ahora:
  run.bat
  Recargar el navegador (Ctrl+Shift+R para limpiar caché)

Deberías ver:
  - C.Ciudad al fondo centro
  - 3 Templos en plano medio: azul / dorado / púrpura
  - 2 Cuarteles en primer plano con banderas de distinto rojo
  - Edificios distribuidos sin amontonarse
""")
