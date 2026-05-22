"""
fix_csv_path.py
Eternal Warriors v3.0 — Actualiza ruta de CSVs a E:\\0000ew V2Claude\\csv\\

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_csv_path.py
"""

from pathlib import Path
import sys

TARGET = Path(r"E:\0000ew V2Claude\backend\systems\production.py")
src = TARGET.read_text(encoding="utf-8")

# Reemplazar todas las rutas de búsqueda de CSVs
OLD1 = """\
    for path in [
        Path(__file__).parent.parent.parent / "edificio1_centro_de_ciudad.csv",
        Path(__file__).parent.parent.parent / "mnt" / "project" / "edificio1_centro_de_ciudad.csv",
    ]:"""
NEW1 = """\
    for path in [
        Path(__file__).parent.parent.parent / "csv" / "edificio1_centro_de_ciudad.csv",
    ]:"""

OLD2 = """\
    for path in [
        Path(__file__).parent.parent.parent / "aldeanos_materiales.csv",
        Path(__file__).parent.parent.parent / "mnt" / "project" / "aldeanos_materiales.csv",
    ]:"""
NEW2 = """\
    for path in [
        Path(__file__).parent.parent.parent / "csv" / "aldeanos_materiales.csv",
    ]:"""

OLD3 = """\
    for path in [
        Path(__file__).parent.parent.parent / "mana_sacerdotes.csv",
        Path(__file__).parent.parent.parent / "mnt" / "project" / "mana_sacerdotes.csv",
    ]:"""
NEW3 = """\
    for path in [
        Path(__file__).parent.parent.parent / "csv" / "mana_sacerdotes.csv",
    ]:"""

fixes = [(OLD1,NEW1),(OLD2,NEW2),(OLD3,NEW3)]
for old, new in fixes:
    c = src.count(old)
    if c != 1:
        print(f"ERROR: ancla {c}x. Abortando.")
        sys.exit(1)
    src = src.replace(old, new)

TARGET.write_text(src, encoding="utf-8")
print("OK: rutas CSV actualizadas → csv/")
print()
print("Reinicia el servidor:")
print("  Ctrl+C → run.bat")
