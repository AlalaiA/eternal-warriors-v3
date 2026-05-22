"""
fix_mana_nivel.py
Eternal Warriors v3.0 — Corrige nivel de sacerdote para producción de maná

El nivel del sacerdote viene de player['unit_levels']['SACERDOTE'],
no de city['NIVEL_DE_TROPAS'].

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_mana_nivel.py
"""

from pathlib import Path
import sys

# ── FIX 1: production.py — calcular_tasas acepta nivel_sacerdote explícito ───
PROD = Path(r"E:\0000ew V2Claude\backend\systems\production.py")
src = PROD.read_text(encoding="utf-8")

OLD1 = """\
def calcular_tasas(city: dict) -> dict:
    \"\"\"
    Calcula las tasas de producción por segundo para una ciudad.
    Retorna dict con tasas/seg para cada recurso.
    \"\"\"
    nivel_cc  = int(city.get("CENTRO_DE_CIUDAD", 1) or 1)
    aldeanos  = float(city.get("ALDEANO", 0) or 0)
    sacerdotes = float(city.get("SACERDOTE", 0) or 0)
    nivel_sac = int(city.get("NIVEL_DE_TROPAS", 1) or 1)  # nivel sacerdote = nivel tropas por ahora"""

NEW1 = """\
def calcular_tasas(city: dict, unit_levels: dict = None) -> dict:
    \"\"\"
    Calcula las tasas de producción por segundo para una ciudad.
    unit_levels: dict con niveles por unidad del jugador (ej: {'SACERDOTE': 5})
    Retorna dict con tasas/seg para cada recurso.
    \"\"\"
    if unit_levels is None:
        unit_levels = {}
    nivel_cc   = int(city.get("CENTRO_DE_CIUDAD", 1) or 1)
    aldeanos   = float(city.get("ALDEANO", 0) or 0)
    sacerdotes = float(city.get("SACERDOTE", 0) or 0)
    # Nivel sacerdote viene de unit_levels del jugador, no de la ciudad
    nivel_sac  = int(unit_levels.get("SACERDOTE", city.get("NIVEL_DE_TROPAS", 1) or 1))"""

c = src.count(OLD1)
if c != 1: print(f"ERROR fix 1: {c}x"); sys.exit(1)
src = src.replace(OLD1, NEW1)
print("OK fix 1: calcular_tasas acepta unit_levels")

# ── FIX 2: aplicar_produccion también pasa unit_levels ───────────────────────
OLD2 = """\
def aplicar_produccion(city: dict, guardar: bool = True) -> dict:
    \"\"\"
    Aplica producción retroactiva desde LAST_PROD hasta ahora.
    Modifica city in-place y retorna las tasas calculadas.
    Retroactivo máximo: 3 días.
    \"\"\"
    ahora = time.time()
    last  = float(city.get("LAST_PROD", ahora - MAX_RETROACTIVO_SEG))

    # Máximo retroactivo: 3 días
    last = max(last, ahora - MAX_RETROACTIVO_SEG)
    segundos = max(0.0, ahora - last)

    tasas = calcular_tasas(city)"""

NEW2 = """\
def aplicar_produccion(city: dict, unit_levels: dict = None) -> dict:
    \"\"\"
    Aplica producción retroactiva desde LAST_PROD hasta ahora.
    Modifica city in-place y retorna las tasas calculadas.
    Retroactivo máximo: 3 días.
    \"\"\"
    if unit_levels is None:
        unit_levels = {}
    ahora = time.time()
    last  = float(city.get("LAST_PROD", ahora - MAX_RETROACTIVO_SEG))

    # Máximo retroactivo: 3 días
    last = max(last, ahora - MAX_RETROACTIVO_SEG)
    segundos = max(0.0, ahora - last)

    tasas = calcular_tasas(city, unit_levels)"""

c = src.count(OLD2)
if c != 1: print(f"ERROR fix 2: {c}x"); sys.exit(1)
src = src.replace(OLD2, NEW2)
PROD.write_text(src, encoding="utf-8")
print("OK fix 2: aplicar_produccion pasa unit_levels")

# ── FIX 3: city.py — pasar unit_levels a producción ─────────────────────────
CITY = Path(r"E:\0000ew V2Claude\backend\api\city.py")
src = CITY.read_text(encoding="utf-8")

OLD3 = """\
    for i, c in enumerate(cities):
        if c.get("NOMBRE") == city_name:
            # Inicializar LAST_PROD si no existe
            init_last_prod(c)
            # Aplicar producción retroactiva
            tasas = aplicar_produccion(c)
            # Guardar el estado actualizado
            player["cities"][i] = c
            sm.save_player(jugador.upper(), player)
            return {
                "ok":    True,
                "city":  c,
                "tasas": tasas,   # tasas/seg que el frontend usa para el ticker
            }"""

NEW3 = """\
    unit_levels = player.get("unit_levels", {})
    for i, c in enumerate(cities):
        if c.get("NOMBRE") == city_name:
            # Inicializar LAST_PROD si no existe
            init_last_prod(c)
            # Aplicar producción retroactiva con nivel real del sacerdote
            tasas = aplicar_produccion(c, unit_levels)
            # Guardar el estado actualizado
            player["cities"][i] = c
            sm.save_player(jugador.upper(), player)
            return {
                "ok":    True,
                "city":  c,
                "tasas": tasas,
            }"""

c = src.count(OLD3)
if c != 1: print(f"ERROR fix 3: {c}x"); sys.exit(1)
src = src.replace(OLD3, NEW3)

OLD4 = """\
    for c in player.get("cities", []):
        if c.get("NOMBRE") == city_name:
            tasas = calcular_tasas(c)
            return {"ok": True, "tasas": tasas}"""

NEW4 = """\
    unit_levels = player.get("unit_levels", {})
    for c in player.get("cities", []):
        if c.get("NOMBRE") == city_name:
            tasas = calcular_tasas(c, unit_levels)
            return {"ok": True, "tasas": tasas}"""

c = src.count(OLD4)
if c != 1: print(f"ERROR fix 4: {c}x"); sys.exit(1)
src = src.replace(OLD4, NEW4)

OLD5 = """\
    for i, c in enumerate(cities):
        if c.get("NOMBRE") == city_name:
            init_last_prod(c)
            tasas = aplicar_produccion(c)
            player["cities"][i] = c
            sm.save_player(jugador.upper(), player)
            return {
                "ok":   True,
                "city": c,
                "tasas": tasas,
            }"""

NEW5 = """\
    unit_levels = player.get("unit_levels", {})
    for i, c in enumerate(cities):
        if c.get("NOMBRE") == city_name:
            init_last_prod(c)
            tasas = aplicar_produccion(c, unit_levels)
            player["cities"][i] = c
            sm.save_player(jugador.upper(), player)
            return {
                "ok":   True,
                "city": c,
                "tasas": tasas,
            }"""

c = src.count(OLD5)
if c != 1: print(f"ERROR fix 5: {c}x"); sys.exit(1)
src = src.replace(OLD5, NEW5)
CITY.write_text(src, encoding="utf-8")
print("OK fix 3-5: city.py pasa unit_levels a producción")

print()
print("HECHO.")
print("  Ctrl+C → run.bat → Ctrl+Shift+R")
print("  JL6 con 1000 sacerdotes nivel 5 debe mostrar maná produciendo.")
