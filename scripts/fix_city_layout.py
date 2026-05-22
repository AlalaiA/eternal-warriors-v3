"""
fix_city_layout.py
Eternal Warriors v3.0 — Ajuste de layout de edificios en city.js

Qué cambia:
  1. cy: H*0.63 -> H*0.56  (sube el punto de origen, más espacio arriba para edificios del fondo)
  2. getLayout(): separa las filas verticalmente, amplía separaciones horizontales
     para que los edificios queden condensados pero legibles, como en la imagen guía.
     Dualidad luz (izquierda) / sombra (derecha) respetada en la distribución.
"""

from pathlib import Path
import sys

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")

if not TARGET.exists():
    print(f"ERROR: No se encontró el archivo en:\n  {TARGET}")
    sys.exit(1)

src = TARGET.read_text(encoding="utf-8")

# ── FIX 1: cy ────────────────────────────────────────────────────────────────
OLD_CY = "  const cx = W/2, cy = H*0.63;"
NEW_CY = "  const cx = W/2, cy = H*0.56;"

count = src.count(OLD_CY)
if count != 1:
    print(f"ERROR fix 1 (cy): ancla encontrada {count} veces (esperado 1). Abortando.")
    sys.exit(1)

src = src.replace(OLD_CY, NEW_CY)
print("OK fix 1: cy H*0.63 -> H*0.56")

# ── FIX 2: getLayout ─────────────────────────────────────────────────────────
OLD_LAYOUT = """function getLayout(c, cx, cy) {
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
}"""

NEW_LAYOUT = """function getLayout(c, cx, cy) {
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

count = src.count(OLD_LAYOUT)
if count != 1:
    print(f"ERROR fix 2 (getLayout): ancla encontrada {count} veces (esperado 1). Abortando.")
    sys.exit(1)

src = src.replace(OLD_LAYOUT, NEW_LAYOUT)
print("OK fix 2: getLayout() — 4 filas reposicionadas, separaciones ampliadas, dualidad luz/sombra")

# ── Guardar ──────────────────────────────────────────────────────────────────
TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO — city.js actualizado.")
print()
print("Para verificar:")
print("  Abre http://127.0.0.1:8000/game en el navegador.")
print("  Los edificios deben verse en 4 filas claras, sin solapamientos,")
print("  con los templos y santuario al fondo y los cuarteles al frente.")
print("  Santuario/Templo Luz a la izquierda (frio-azul), Templo Guerra a la derecha (rojo).")
