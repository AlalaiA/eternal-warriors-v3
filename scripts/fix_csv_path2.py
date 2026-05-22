"""
fix_csv_path2.py
Eternal Warriors v3.0 — Actualiza rutas CSV a csv\ con regex

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_csv_path2.py
"""

from pathlib import Path
import re

TARGET = Path(r"E:\0000ew V2Claude\backend\systems\production.py")
src = TARGET.read_text(encoding="utf-8")

# Reemplazar todos los bloques "for path in [...]:" con la ruta correcta
# Para cada CSV específico
csvs = {
    "edificio1_centro_de_ciudad.csv": "_load_cc_tasas",
    "aldeanos_materiales.csv": "_load_material_tasas",
    "mana_sacerdotes.csv": "_load_mana_tasas",
}

for csv_name, func_name in csvs.items():
    # Buscar el bloque for path in [...] dentro de la función correcta
    pattern = r'(for path in \[)[^\]]+(\]:)'
    # Reemplazar el primero que aparezca después de la función
    new_block = f'for path in [\n        Path(__file__).parent.parent.parent / "csv" / "{csv_name}",\n    ]:'

    # Contar ocurrencias para diagnóstico
    matches = list(re.finditer(pattern, src, re.DOTALL))
    print(f"{csv_name}: {len(matches)} bloques 'for path in' encontrados en total")

# Reemplazar todos los bloques for path in con las 3 rutas correctas en orden
new_src = src

# Reemplazar cada bloque for path in [...]: con la versión correcta
replacements = [
    "csv/edificio1_centro_de_ciudad.csv",
    "csv/aldeanos_materiales.csv",
    "csv/mana_sacerdotes.csv",
]

pattern = r'for path in \[[^\]]+\]:'
matches = list(re.finditer(pattern, new_src, re.DOTALL))
print(f"\nTotal bloques encontrados: {len(matches)}")

if len(matches) != 3:
    print("ERROR: se esperaban 3 bloques. Abortando.")
    exit(1)

# Reemplazar de atrás hacia adelante para no desplazar índices
for match, csv_path in zip(reversed(matches), reversed(replacements)):
    csv_name = csv_path.split("/")[1]
    new_block = f'for path in [\n        Path(__file__).parent.parent.parent / "csv" / "{csv_name}",\n    ]:'
    new_src = new_src[:match.start()] + new_block + new_src[match.end():]
    print(f"OK: {csv_name}")

TARGET.write_text(new_src, encoding="utf-8")
print()
print("HECHO — rutas CSV actualizadas a csv/")
print()
print("Siguientes pasos:")
print("  python fix_production_ticker.py")
print("  Ctrl+C → run.bat")
