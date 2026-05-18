from pathlib import Path

path = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = path.read_text(encoding="utf-8")

OLD = """    { key:'CENTRO_DE_CIUDAD', label:'Centro Ciudad', lvl:lv('CENTRO_DE_CIUDAD'),
      x:cx, y:cy-15, iy:cy-15, type:'cityhall' },
    { key:'CASA', label:'Casa', lvl:lv('CASA'),
      x:cx-130, y:cy-5, iy:cy+5, type:'house' },
    { key:'TORRE_DE_VIGILANCIA', label:'Torre Vig.', lvl:lv('TORRE_DE_VIGILANCIA'),
      x:cx+145, y:cy-35, iy:cy-25, type:'watchtower' },
    { key:'CENTRO_DE_VIAJES', label:'C.Viajes', lvl:lv('CENTRO_DE_VIAJES'),
      x:cx-85, y:cy-65, iy:cy-55, type:'travel' },
    { key:'ESCONDITE', label:'Escondite', lvl:lv('ESCONDITE'),
      x:cx+110, y:cy+28, iy:cy+38, type:'hideout' },
    { key:'ALMACEN', label:'Almacén', lvl:lv('ALMACEN'),
      x:cx-115, y:cy+38, iy:cy+48, type:'warehouse' },
    { key:'SANTUARIO_ARCANO', label:'Santuario', lvl:lv('SANTUARIO_ARCANO'),
      x:cx+25, y:cy-95, iy:cy-85, type:'sanctuary' },
    { key:'UNIVERSIDAD', label:'Universidad', lvl:lv('UNIVERSIDAD'),
      x:cx-45, y:cy-82, iy:cy-72, type:'university' },
    { key:'HERRERIA', label:'Herrería', lvl:lv('HERRERIA'),
      x:cx+65, y:cy+45, iy:cy+55, type:'forge' },
    { key:'TEMPLO_1', label:'Templo 1', lvl:lv('TEMPLO_1'),
      x:cx+80, y:cy-55, iy:cy-45, type:'temple', accent:'#c8a000' },
    { key:'TEMPLO_2', label:'Templo 2', lvl:lv('TEMPLO_2'),
      x:cx+100, y:cy-15, iy:cy-5, type:'temple', accent:'#d4a020' },
    { key:'TEMPLO_3', label:'Templo 3', lvl:lv('TEMPLO_3'),
      x:cx+55, y:cy+10, iy:cy+20, type:'temple', accent:'#e0b040' },
    { key:'CUARTEL_1', label:'Cuartel 1', lvl:lv('CUARTEL_1'),
      x:cx-55, y:cy+8, iy:cy+18, type:'barracks' },
    { key:'CUARTEL_2', label:'Cuartel 2', lvl:lv('CUARTEL_2'),
      x:cx-25, y:cy+48, iy:cy+58, type:'barracks' },"""

NEW = """    // Centro de Ciudad — centro exacto
    { key:'CENTRO_DE_CIUDAD', label:'Centro Ciudad', lvl:lv('CENTRO_DE_CIUDAD'),
      x:cx, y:cy+10, iy:cy+10, type:'cityhall' },
    // Fila delantera (sur)
    { key:'CUARTEL_1',  label:'Cuartel 1',  lvl:lv('CUARTEL_1'),
      x:cx-90,  y:cy+75, iy:cy+75, type:'barracks' },
    { key:'HERRERIA',   label:'Herrería',   lvl:lv('HERRERIA'),
      x:cx+10,  y:cy+80, iy:cy+80, type:'forge' },
    { key:'CUARTEL_2',  label:'Cuartel 2',  lvl:lv('CUARTEL_2'),
      x:cx+90,  y:cy+60, iy:cy+60, type:'barracks' },
    // Fila central izq
    { key:'CASA',       label:'Casa',       lvl:lv('CASA'),
      x:cx-155, y:cy+15, iy:cy+15, type:'house' },
    { key:'ALMACEN',    label:'Almacén',    lvl:lv('ALMACEN'),
      x:cx-155, y:cy-45, iy:cy-45, type:'warehouse' },
    // Fila central der
    { key:'ESCONDITE',  label:'Escondite',  lvl:lv('ESCONDITE'),
      x:cx+145, y:cy+10, iy:cy+10, type:'hideout' },
    { key:'TEMPLO_1',   label:'Templo 1',   lvl:lv('TEMPLO_1'),
      x:cx+145, y:cy-50, iy:cy-50, type:'temple', accent:'#c8a000' },
    // Fila trasera (norte)
    { key:'UNIVERSIDAD',    label:'Universidad', lvl:lv('UNIVERSIDAD'),
      x:cx-100, y:cy-80, iy:cy-80, type:'university' },
    { key:'SANTUARIO_ARCANO', label:'Santuario', lvl:lv('SANTUARIO_ARCANO'),
      x:cx,     y:cy-110, iy:cy-110, type:'sanctuary' },
    { key:'CENTRO_DE_VIAJES', label:'C.Viajes',  lvl:lv('CENTRO_DE_VIAJES'),
      x:cx+100, y:cy-80, iy:cy-80, type:'travel' },
    // Esquinas
    { key:'TORRE_DE_VIGILANCIA', label:'Torre Vig.', lvl:lv('TORRE_DE_VIGILANCIA'),
      x:cx+170, y:cy-20, iy:cy-20, type:'watchtower' },
    { key:'TEMPLO_2', label:'Templo 2', lvl:lv('TEMPLO_2'),
      x:cx+110, y:cy-130, iy:cy-130, type:'temple', accent:'#d4a020' },
    { key:'TEMPLO_3', label:'Templo 3', lvl:lv('TEMPLO_3'),
      x:cx-110, y:cy-130, iy:cy-130, type:'temple', accent:'#e0b040' },"""

c = src.count(OLD)
if c != 1:
    print(f"ERROR: {c} veces"); exit(1)
src = src.replace(OLD, NEW)
path.write_text(src, encoding="utf-8")
print("OK — layout reordenado con más espacio")
print("✅ Recarga el navegador.")
