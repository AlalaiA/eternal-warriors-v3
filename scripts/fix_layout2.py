from pathlib import Path

path = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = path.read_text(encoding="utf-8")

OLD = """    // Centro de Ciudad — centro exacto
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

NEW = """    // Layout compacto centrado — todo dentro del canvas
    { key:'CENTRO_DE_CIUDAD', label:'Centro Ciudad', lvl:lv('CENTRO_DE_CIUDAD'),
      x:cx, y:cy+40, iy:cy+40, type:'cityhall' },
    // Sur
    { key:'CUARTEL_1',  label:'Cuartel 1',  lvl:lv('CUARTEL_1'),
      x:cx-80, y:cy+95, iy:cy+95, type:'barracks' },
    { key:'HERRERIA',   label:'Herrería',   lvl:lv('HERRERIA'),
      x:cx+10, y:cy+100, iy:cy+100, type:'forge' },
    { key:'CUARTEL_2',  label:'Cuartel 2',  lvl:lv('CUARTEL_2'),
      x:cx+80, y:cy+80, iy:cy+80, type:'barracks' },
    // Centro izq/der
    { key:'CASA',     label:'Casa',     lvl:lv('CASA'),
      x:cx-140, y:cy+40, iy:cy+40, type:'house' },
    { key:'ALMACEN',  label:'Almacén',  lvl:lv('ALMACEN'),
      x:cx-130, y:cy-15, iy:cy-15, type:'warehouse' },
    { key:'ESCONDITE', label:'Escondite', lvl:lv('ESCONDITE'),
      x:cx+130, y:cy+30, iy:cy+30, type:'hideout' },
    { key:'TEMPLO_1',  label:'Templo 1',  lvl:lv('TEMPLO_1'),
      x:cx+125, y:cy-20, iy:cy-20, type:'temple', accent:'#c8a000' },
    // Norte
    { key:'UNIVERSIDAD',      label:'Universidad', lvl:lv('UNIVERSIDAD'),
      x:cx-90, y:cy-55, iy:cy-55, type:'university' },
    { key:'SANTUARIO_ARCANO', label:'Santuario',   lvl:lv('SANTUARIO_ARCANO'),
      x:cx,    y:cy-75, iy:cy-75, type:'sanctuary' },
    { key:'CENTRO_DE_VIAJES', label:'C.Viajes',    lvl:lv('CENTRO_DE_VIAJES'),
      x:cx+90, y:cy-55, iy:cy-55, type:'travel' },
    { key:'TORRE_DE_VIGILANCIA', label:'Torre Vig.', lvl:lv('TORRE_DE_VIGILANCIA'),
      x:cx+150, y:cy-5, iy:cy-5, type:'watchtower' },
    { key:'TEMPLO_2', label:'Templo 2', lvl:lv('TEMPLO_2'),
      x:cx+80,  y:cy-90, iy:cy-90, type:'temple', accent:'#d4a020' },
    { key:'TEMPLO_3', label:'Templo 3', lvl:lv('TEMPLO_3'),
      x:cx-80,  y:cy-90, iy:cy-90, type:'temple', accent:'#e0b040' },"""

c = src.count(OLD)
if c != 1:
    print(f"ERROR: {c} veces"); exit(1)
src = src.replace(OLD, NEW)

# También ajustar cy más abajo para que todo quepa
OLD2 = "  const cx = W/2, cy = H*0.52;"
NEW2 = "  const cx = W/2, cy = H*0.62;"

c2 = src.count(OLD2)
if c2 != 1:
    print(f"ERROR cy: {c2} veces"); exit(1)
src = src.replace(OLD2, NEW2)

path.write_text(src, encoding="utf-8")
print("OK — layout recentrado con cy=0.62")
print("✅ Recarga el navegador.")
