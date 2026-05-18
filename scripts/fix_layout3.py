from pathlib import Path

path = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = path.read_text(encoding="utf-8")

# Bajar cy
OLD1 = "  const cx = W/2, cy = H*0.62;"
NEW1 = "  const cx = W/2, cy = H*0.70;"
c1 = src.count(OLD1)
if c1!=1: print(f"ERROR cy: {c1}"); exit(1)
src = src.replace(OLD1, NEW1)

# Layout más compacto
OLD2 = """    // Layout compacto centrado — todo dentro del canvas
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

NEW2 = """    // Layout ajustado
    { key:'CENTRO_DE_CIUDAD', label:'Centro Ciudad', lvl:lv('CENTRO_DE_CIUDAD'),
      x:cx, y:cy+10, iy:cy+10, type:'cityhall' },
    { key:'CUARTEL_1',  label:'Cuartel 1',  lvl:lv('CUARTEL_1'),
      x:cx-80, y:cy+65, iy:cy+65, type:'barracks' },
    { key:'HERRERIA',   label:'Herrería',   lvl:lv('HERRERIA'),
      x:cx+10, y:cy+70, iy:cy+70, type:'forge' },
    { key:'CUARTEL_2',  label:'Cuartel 2',  lvl:lv('CUARTEL_2'),
      x:cx+80, y:cy+55, iy:cy+55, type:'barracks' },
    { key:'CASA',       label:'Casa',       lvl:lv('CASA'),
      x:cx-140, y:cy+20, iy:cy+20, type:'house' },
    { key:'ALMACEN',    label:'Almacén',    lvl:lv('ALMACEN'),
      x:cx-135, y:cy-25, iy:cy-25, type:'warehouse' },
    { key:'ESCONDITE',  label:'Escondite',  lvl:lv('ESCONDITE'),
      x:cx+130, y:cy+15, iy:cy+15, type:'hideout' },
    { key:'TEMPLO_1',   label:'Templo 1',   lvl:lv('TEMPLO_1'),
      x:cx+125, y:cy-25, iy:cy-25, type:'temple', accent:'#c8a000' },
    { key:'UNIVERSIDAD',      label:'Universidad',  lvl:lv('UNIVERSIDAD'),
      x:cx-85, y:cy-45, iy:cy-45, type:'university' },
    { key:'CENTRO_DE_VIAJES', label:'C.Viajes',     lvl:lv('CENTRO_DE_VIAJES'),
      x:cx+85, y:cy-45, iy:cy-45, type:'travel' },
    { key:'TORRE_DE_VIGILANCIA', label:'Torre Vig.', lvl:lv('TORRE_DE_VIGILANCIA'),
      x:cx+148, y:cy-8, iy:cy-8, type:'watchtower' },
    { key:'SANTUARIO_ARCANO', label:'Santuario',    lvl:lv('SANTUARIO_ARCANO'),
      x:cx,    y:cy-60, iy:cy-60, type:'sanctuary' },
    { key:'TEMPLO_2', label:'Templo 2', lvl:lv('TEMPLO_2'),
      x:cx+70, y:cy-75, iy:cy-75, type:'temple', accent:'#d4a020' },
    { key:'TEMPLO_3', label:'Templo 3', lvl:lv('TEMPLO_3'),
      x:cx-70, y:cy-75, iy:cy-75, type:'temple', accent:'#e0b040' },"""

c2 = src.count(OLD2)
if c2!=1: print(f"ERROR layout: {c2}"); exit(1)
src = src.replace(OLD2, NEW2)

# Reducir escala del santuario — limitar lvl
OLD3 = "  if (b.type === 'sanctuary') {"
# No existe aún — reducir escala global a 0.4 + min(lvl,30)*0.016
OLD3 = "  const sc = 0.45 + Math.min(lvl,50)*0.015;"
NEW3 = "  const scMax = b.type==='sanctuary' ? 25 : (b.type==='cityhall' ? 40 : 50);\n  const sc = 0.45 + Math.min(lvl,scMax)*0.015;"

c3 = src.count(OLD3)
if c3!=1: print(f"ERROR sc: {c3}"); exit(1)
src = src.replace(OLD3, NEW3)

path.write_text(src, encoding="utf-8")
print("OK — cy=0.70, layout ajustado, santuario limitado a scMax=25")
print("✅ Recarga el navegador.")
