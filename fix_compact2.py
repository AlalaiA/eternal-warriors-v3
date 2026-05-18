from pathlib import Path

path = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = path.read_text(encoding="utf-8")

# Terrain
OLD2 = "cols=18, rows=14;"
c2 = src.count(OLD2)
if c2!=1: print(f"ERROR terrain:{c2}"); exit(1)
src = src.replace(OLD2, "cols=14, rows=10;")
print("Fix terrain OK")

# Muralla
OLD3 = "  const rx = 135*scale, ry = 76*scale;"
if src.count(OLD3) == 0:
    OLD3 = "  const rx = 195*scale, ry = 110*scale;"
c3 = src.count(OLD3)
if c3!=1: print(f"ERROR wall:{c3}"); exit(1)
src = src.replace(OLD3, "  const rx = 135*scale, ry = 76*scale;")
print("Fix muralla OK")

# Layout — reemplazar función getLayout completa
idx_start = src.find("function getLayout(c, cx, cy) {")
idx_end   = src.find("\nfunction drawBuilding(")
if idx_start == -1: print("ERROR: getLayout no encontrado"); exit(1)
if idx_end   == -1: print("ERROR: drawBuilding no encontrado"); exit(1)

NEW_LAYOUT = """function getLayout(c, cx, cy) {
  const lv = k => Number(c[k]||0);
  return [
    // Fila 1 — fondo
    { key:'SANTUARIO_ARCANO',    label:'Santuario',   lvl:lv('SANTUARIO_ARCANO'),
      x:cx,     y:cy-58, iy:cy-58, type:'sanctuary' },
    { key:'TEMPLO_3',            label:'Templo 3',    lvl:lv('TEMPLO_3'),
      x:cx-48,  y:cy-48, iy:cy-48, type:'temple', accent:'#e0b040' },
    { key:'TEMPLO_2',            label:'Templo 2',    lvl:lv('TEMPLO_2'),
      x:cx+48,  y:cy-48, iy:cy-48, type:'temple', accent:'#d4a020' },
    // Fila 2
    { key:'UNIVERSIDAD',         label:'Universidad', lvl:lv('UNIVERSIDAD'),
      x:cx-85,  y:cy-28, iy:cy-28, type:'university' },
    { key:'CENTRO_DE_CIUDAD',    label:'C.Ciudad',    lvl:lv('CENTRO_DE_CIUDAD'),
      x:cx,     y:cy-22, iy:cy-22, type:'cityhall' },
    { key:'CENTRO_DE_VIAJES',    label:'C.Viajes',    lvl:lv('CENTRO_DE_VIAJES'),
      x:cx+85,  y:cy-28, iy:cy-28, type:'travel' },
    // Fila 3
    { key:'ALMACEN',             label:'Almacén',     lvl:lv('ALMACEN'),
      x:cx-105, y:cy+8,  iy:cy+8,  type:'warehouse' },
    { key:'TEMPLO_1',            label:'Templo 1',    lvl:lv('TEMPLO_1'),
      x:cx-32,  y:cy+5,  iy:cy+5,  type:'temple', accent:'#c8a000' },
    { key:'TORRE_DE_VIGILANCIA', label:'Torre',       lvl:lv('TORRE_DE_VIGILANCIA'),
      x:cx+32,  y:cy+5,  iy:cy+5,  type:'watchtower' },
    { key:'ESCONDITE',           label:'Escondite',   lvl:lv('ESCONDITE'),
      x:cx+105, y:cy+8,  iy:cy+8,  type:'hideout' },
    // Fila 4 — frente
    { key:'CASA',                label:'Casa',        lvl:lv('CASA'),
      x:cx-108, y:cy+42, iy:cy+42, type:'house' },
    { key:'CUARTEL_1',           label:'Cuartel 1',   lvl:lv('CUARTEL_1'),
      x:cx-36,  y:cy+40, iy:cy+40, type:'barracks' },
    { key:'HERRERIA',            label:'Herrería',    lvl:lv('HERRERIA'),
      x:cx+36,  y:cy+40, iy:cy+40, type:'forge' },
    { key:'CUARTEL_2',           label:'Cuartel 2',   lvl:lv('CUARTEL_2'),
      x:cx+108, y:cy+42, iy:cy+42, type:'barracks' },
  ];
}
"""

src = src[:idx_start] + NEW_LAYOUT + src[idx_end:]
print("Fix layout OK")

path.write_text(src, encoding="utf-8")
print("✅ Recarga el navegador.")
