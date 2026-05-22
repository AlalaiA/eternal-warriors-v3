"""
install_production.py
Eternal Warriors v3.0 — Instala sistema de producción

Qué hace:
  1. Copia production.py a backend/systems/
  2. Copia city_api.py a backend/api/city.py (reemplaza el anterior)
  3. Añade LAST_PROD a todas las ciudades de todos los jugadores (retroactividad 3 días)
  4. Verifica que las rutas de los CSVs estén correctas

Corre desde: E:\\0000ew V2Claude\\
Comando:     python install_production.py
"""

import json, time, shutil
from pathlib import Path

BASE    = Path(r"E:\0000ew V2Claude")
SCRIPT  = Path(__file__).parent

# ── 1. Copiar archivos ────────────────────────────────────────────────────────
src_prod = SCRIPT / "production.py"
src_city = SCRIPT / "city_api.py"

dst_prod = BASE / "backend" / "systems" / "production.py"
dst_city = BASE / "backend" / "api" / "city.py"

shutil.copy2(src_prod, dst_prod)
print(f"OK: {dst_prod}")

shutil.copy2(src_city, dst_city)
print(f"OK: {dst_city}")

# ── 2. Fijar rutas CSV en production.py ──────────────────────────────────────
# Los CSVs están en E:\0000ew V2Claude\ (raíz del proyecto)
prod_src = dst_prod.read_text(encoding="utf-8")
OLD_CSV = 'CSV_DIR = Path(__file__).parent.parent.parent / "mnt" / "project"'
NEW_CSV = 'CSV_DIR = Path(__file__).parent.parent.parent  # raíz del proyecto'
if OLD_CSV in prod_src:
    prod_src = prod_src.replace(OLD_CSV, NEW_CSV)

# Actualizar también los paths de búsqueda de CSVs
OLD_PATHS = '''\
    for path in [
        Path(__file__).parent.parent.parent / "mnt" / "project" / "edificio1_centro_de_ciudad.csv",
        Path(__file__).parent.parent.parent / "edificio1_centro_de_ciudad.csv",
    ]:'''
NEW_PATHS = '''\
    for path in [
        Path(__file__).parent.parent.parent / "edificio1_centro_de_ciudad.csv",
        Path(__file__).parent.parent.parent / "mnt" / "project" / "edificio1_centro_de_ciudad.csv",
    ]:'''
if OLD_PATHS in prod_src:
    prod_src = prod_src.replace(OLD_PATHS, NEW_PATHS)

for csv_name in ["aldeanos_materiales.csv", "mana_sacerdotes.csv"]:
    old = f'Path(__file__).parent.parent.parent / "mnt" / "project" / "{csv_name}"'
    new = f'Path(__file__).parent.parent.parent / "{csv_name}"'
    prod_src = prod_src.replace(old, new)

dst_prod.write_text(prod_src, encoding="utf-8")
print("OK: rutas CSV actualizadas en production.py")

# ── 3. Añadir LAST_PROD a todos los jugadores ─────────────────────────────────
PLAYERS_DIR = BASE / "backend" / "db" / "players"
RETROACTIVO = 3 * 24 * 3600  # 3 días en segundos
ahora = time.time()
last_prod_val = ahora - RETROACTIVO  # hace 3 días

count_cities = 0
for json_path in PLAYERS_DIR.rglob("*.json"):
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        modified = False
        for city in data.get("cities", []):
            if "LAST_PROD" not in city:
                city["LAST_PROD"] = last_prod_val
                modified = True
                count_cities += 1
        if modified:
            json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  Updated: {json_path.name}")
    except Exception as e:
        print(f"  SKIP {json_path.name}: {e}")

print(f"OK: LAST_PROD añadido a {count_cities} ciudades (retroactividad 3 días)")

# ── 4. Verificar CSVs ─────────────────────────────────────────────────────────
csvs = ["edificio1_centro_de_ciudad.csv", "aldeanos_materiales.csv", "mana_sacerdotes.csv"]
for csv in csvs:
    path = BASE / csv
    if path.exists():
        print(f"OK CSV: {csv}")
    else:
        print(f"ERROR CSV no encontrado: {path}")
        print(f"  Cópialo manualmente a {BASE}")

print()
print("HECHO.")
print()
print("Reinicia el servidor:")
print("  Ctrl+C → run.bat")
print()
print("Verifica en el navegador que los materiales ya tienen valores actualizados.")
print("Los recursos se actualizarán en tiempo real desde el frontend cada segundo.")
