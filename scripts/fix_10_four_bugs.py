"""
fix_10_four_bugs.py

BUG A — api/queues.py: frontend envía {tipo, unidad/invocacion, cantidad}
         pero el modelo espera {cuartel/templo, unidad/invocacion, cantidad}
         → Aceptar ambas variantes en el modelo

BUG B — systems/queues.py línea 162: inv.get("tiempo_min") → debería ser "tiempo_base_min"

BUG C — systems/queues.py líneas 95 y 115: _load_reduccion_cuartel y _load_rebaja_templo
         leen col[5] (costocarbon) en lugar de col[6] (%reducción)

BUG D — systems/buildings.py: límite de 4 obras simultáneas no validado

Ejecutar desde: E:\\0000ew V2Claude\\
"""
import pathlib, sys

ROOT = pathlib.Path(".")

# ═══════════════════════════════════════════════════════════════════════════════
# BUG A — api/queues.py: modelos flexibles
# ═══════════════════════════════════════════════════════════════════════════════
QUEUES_API = ROOT / "backend/api/queues.py"
src = QUEUES_API.read_text(encoding="utf-8")
orig = src

OLD_MODELS = """class ColaCuartelRequest(BaseModel):
    cuartel: str    # CUARTEL_1, CUARTEL_2, CUARTEL_3
    unidad:  str    # GUERRERO, MAGO, etc.
    cantidad: int


class ColaTemploRequest(BaseModel):
    templo:     str  # TEMPLO_1, TEMPLO_2, TEMPLO_3
    invocacion: str  # DEMONIO, ANIMA, etc.
    cantidad:   int"""

NEW_MODELS = """class ColaCuartelRequest(BaseModel):
    # Acepta 'cuartel' o 'tipo' (compatibilidad frontend)
    cuartel:  str = ""
    tipo:     str = ""
    unidad:   str
    cantidad: int

    @property
    def cuartel_key(self) -> str:
        return (self.cuartel or self.tipo).upper()


class ColaTemploRequest(BaseModel):
    # Acepta 'templo' o 'tipo' (compatibilidad frontend)
    templo:     str = ""
    tipo:       str = ""
    invocacion: str = ""
    unidad:     str = ""   # alias de invocacion
    cantidad:   int

    @property
    def templo_key(self) -> str:
        return (self.templo or self.tipo).upper()

    @property
    def invocacion_key(self) -> str:
        return (self.invocacion or self.unidad).upper()"""

if OLD_MODELS in src:
    src = src.replace(OLD_MODELS, NEW_MODELS)
    print("✅ BUG A — modelos ColaCuartelRequest / ColaTemploRequest flexibles")
else:
    print("⚠️  BUG A — modelos no encontrados exactamente")

# Actualizar uso de req.cuartel → req.cuartel_key
src = src.replace(
    "result = iniciar_cola_cuartel(city, req.cuartel, req.unidad, req.cantidad, unit_levels)",
    "result = iniciar_cola_cuartel(city, req.cuartel_key, req.unidad, req.cantidad, unit_levels)"
)
src = src.replace(
    "result = iniciar_cola_templo(city, req.templo, req.invocacion, req.cantidad, unit_levels)",
    "result = iniciar_cola_templo(city, req.templo_key, req.invocacion_key, req.cantidad, unit_levels)"
)

if src != orig:
    QUEUES_API.write_text(src, encoding="utf-8")
    print("✅ BUG A — api/queues.py guardado")
else:
    print("⚠️  BUG A — sin cambios en api/queues.py")

# ═══════════════════════════════════════════════════════════════════════════════
# BUG B + BUG C — systems/queues.py
# ═══════════════════════════════════════════════════════════════════════════════
QUEUES_SYS = ROOT / "backend/systems/queues.py"
src = QUEUES_SYS.read_text(encoding="utf-8")
orig = src

# BUG B: "tiempo_min" → "tiempo_base_min"
OLD_B = '    base_min = inv.get("tiempo_min", 9000)'
NEW_B = '    base_min = inv.get("tiempo_base_min", 9000)'
if OLD_B in src:
    src = src.replace(OLD_B, NEW_B)
    print("✅ BUG B — tiempo_invocacion_seg usa 'tiempo_base_min' correctamente")
else:
    print("⚠️  BUG B — ancla no encontrada, verificar línea 162 de systems/queues.py")

# BUG C: _load_reduccion_cuartel lee col[5] en lugar de col[6]
OLD_C1 = """                red = row[5].strip().replace("%", "")
                result[nivel] = float(red)
            except (ValueError, IndexError):
                result[nivel] = 0.0
    return result

def _load_rebaja_templo"""

NEW_C1 = """                red = row[6].strip().replace("%", "")  # col[6] = %reducción
                result[nivel] = float(red)
            except (ValueError, IndexError):
                result[nivel] = 0.0
    return result

def _load_rebaja_templo"""

if OLD_C1 in src:
    src = src.replace(OLD_C1, NEW_C1)
    print("✅ BUG C — _load_reduccion_cuartel corregida a col[6]")
else:
    print("⚠️  BUG C parte 1 — ancla no encontrada, verificar _load_reduccion_cuartel")

# BUG C: _load_rebaja_templo lee col[5] en lugar de col[6]
OLD_C2 = """                reb = row[5].strip().replace("%", "")
                result[nivel] = float(reb)"""
NEW_C2 = """                reb = row[6].strip().replace("%", "")  # col[6] = %rebaja
                result[nivel] = float(reb)"""

if OLD_C2 in src:
    src = src.replace(OLD_C2, NEW_C2)
    print("✅ BUG C — _load_rebaja_templo corregida a col[6]")
else:
    print("⚠️  BUG C parte 2 — ancla no encontrada, verificar _load_rebaja_templo")

if src != orig:
    QUEUES_SYS.write_text(src, encoding="utf-8")
    print("✅ BUG B+C — systems/queues.py guardado")

# ═══════════════════════════════════════════════════════════════════════════════
# BUG D — systems/buildings.py: límite de 4 obras simultáneas
# ═══════════════════════════════════════════════════════════════════════════════
BUILDINGS_SYS = ROOT / "backend/systems/buildings.py"
src = BUILDINGS_SYS.read_text(encoding="utf-8")
orig = src

MAX_OBRAS = 4

OLD_D = """    info = buildings_info(city, edificio)
    if "error" in info:
        return info
    if not info["puede_subir"]:"""

NEW_D = f"""    # Validar límite de obras simultáneas (máx {MAX_OBRAS})
    obras_v3 = [o for o in city.get("OBRAS", []) if "inicio" in o and "duracion_seg" in o]
    if len(obras_v3) >= {MAX_OBRAS}:
        return {{"error": f"Límite de {MAX_OBRAS} obras simultáneas alcanzado. "
                          f"Tienes {{len(obras_v3)}} en progreso."}}

    info = buildings_info(city, edificio)
    if "error" in info:
        return info
    if not info["puede_subir"]:"""

if OLD_D in src:
    src = src.replace(OLD_D, NEW_D)
    print(f"✅ BUG D — límite de {MAX_OBRAS} obras simultáneas validado en iniciar_obra()")
else:
    print("⚠️  BUG D — ancla no encontrada en iniciar_obra()")

if src != orig:
    BUILDINGS_SYS.write_text(src, encoding="utf-8")
    print("✅ BUG D — systems/buildings.py guardado")

# ═══════════════════════════════════════════════════════════════════════════════
# Verificación rápida
# ═══════════════════════════════════════════════════════════════════════════════
print("""
─────────────────────────────────────────────────────────────
Verificar antes de arrancar:

  python -c "
import sys; sys.path.insert(0,'backend')
from systems.queues import get_reduccion_cuartel, get_rebaja_templo, tiempo_invocacion_seg
rc = get_reduccion_cuartel()
rt = get_rebaja_templo()
print('Cuartel nv6:', rc.get(6), '← debe ser 6.0')
print('Templo  nv3:', rt.get(3), '← debe ser 3.0')
print('Demonio nv1 seg:', tiempo_invocacion_seg('DEMONIO', 1), '← debe ser ~3564')
  "

Luego:
  run.bat  +  Ctrl+Shift+R
─────────────────────────────────────────────────────────────
""")
