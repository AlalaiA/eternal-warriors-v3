"""
fix_04_queues_pathlib.py
Agrega 'import pathlib' al inicio de las dos funciones parcheadas en queues.py
que lo necesitan pero no lo tienen en scope local.

Ejecutar desde: E:\0000ew V2Claude\
"""
import pathlib, sys

TARGET = pathlib.Path("backend/systems/queues.py")
if not TARGET.exists():
    sys.exit(f"ERROR: No se encuentra {TARGET}")

src = TARGET.read_text(encoding="utf-8")
original = src

# Las funciones parcheadas usan pathlib.Path(__file__) pero no importan pathlib.
# El módulo puede o no tener 'import pathlib' a nivel de módulo.
# Solución limpia: asegurar 'import pathlib' a nivel de módulo (top-level).

lines = src.splitlines()

# ¿Ya tiene import pathlib a nivel de módulo?
has_pathlib = any(l.strip() == "import pathlib" for l in lines)

if not has_pathlib:
    # Insertar tras el último 'import' o 'from' del bloque de imports al inicio
    insert_at = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            insert_at = i + 1
        elif stripped and not stripped.startswith("#") and insert_at > 0:
            break  # salimos del bloque de imports
    lines.insert(insert_at, "import pathlib")
    src = "\n".join(lines)
    backup = TARGET.with_suffix(".py.bak2")
    backup.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")
    print(f"✅ 'import pathlib' añadido en línea {insert_at+1} de {TARGET}")
    print(f"   Backup: {backup}")
else:
    print("ℹ️  pathlib ya importado a nivel de módulo — sin cambios")

print("\nVerifica ahora:")
print("""  python -c "import sys; sys.path.insert(0,'backend'); from systems.queues import _load_tiempo_unidades, _load_invocaciones; t=_load_tiempo_unidades(); i=_load_invocaciones(); print('MAGO' in t, 'DEMONIO' in i, i.get('DEMONIO',{}).get('nivel_min_sacerdote'))" """)
