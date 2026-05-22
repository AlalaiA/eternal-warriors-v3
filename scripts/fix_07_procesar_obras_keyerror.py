"""
fix_07_procesar_obras_keyerror.py
KeyError: 'inicio' en buildings.py línea 236.

Causa: city['OBRAS'] contiene entradas del sistema v2 con formato distinto,
o entradas vacías/corruptas. procesar_obras no valida las claves antes de usarlas.

Fix: saltar silenciosamente obras que no tengan las claves esperadas del sistema v3
     (inicio + duracion_seg). Las obras v2 se ignoran sin crashear.

Ejecutar desde: E:\\0000ew V2Claude\\
"""
import pathlib, sys

TARGET = pathlib.Path("backend/systems/buildings.py")
if not TARGET.exists():
    sys.exit(f"ERROR: No se encuentra {TARGET}")

src = TARGET.read_text(encoding="utf-8")
original = src

OLD = """    for obra in obras:
        fin = obra["inicio"] + obra["duracion_seg"]
        # Cap retroactividad: máx 3 días de retraso, pero igual se procesa si terminó
        if now >= fin:
            terminadas.append(obra)
        else:
            pendientes.append(obra)"""

NEW = """    for obra in obras:
        # Ignorar obras con formato v2 o incompleto (sin claves v3)
        if "inicio" not in obra or "duracion_seg" not in obra:
            pendientes.append(obra)  # conservar sin tocar
            continue
        fin = obra["inicio"] + obra["duracion_seg"]
        if now >= fin:
            terminadas.append(obra)
        else:
            pendientes.append(obra)"""

if OLD in src:
    src = src.replace(OLD, NEW)
    backup = TARGET.with_suffix(".py.bak3")
    backup.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")
    print(f"✅ Fix aplicado en {TARGET}")
    print(f"   Backup: {backup}")
else:
    print("⚠️  Bloque no encontrado exactamente. Aplicando búsqueda flexible...")
    import re
    pattern = r'for obra in obras:\s*\n\s*fin = obra\["inicio"\]'
    if re.search(pattern, src):
        # Reemplazar el bloque completo del for
        new_block = '''    for obra in obras:
        # Ignorar obras con formato v2 o incompleto (sin claves v3)
        if "inicio" not in obra or "duracion_seg" not in obra:
            pendientes.append(obra)
            continue
        fin = obra["inicio"] + obra["duracion_seg"]
        if now >= fin:
            terminadas.append(obra)
        else:
            pendientes.append(obra)'''
        src = re.sub(
            r'    for obra in obras:\s*\n.*?pendientes\.append\(obra\)',
            new_block,
            src, flags=re.DOTALL, count=1
        )
        TARGET.write_text(src, encoding="utf-8")
        print("✅ Fix aplicado via regex")
    else:
        print("ERROR: No se pudo localizar el bloque. Editar manualmente:")
        print("  En procesar_obras(), dentro del for loop sobre obras,")
        print("  añadir al inicio del loop:")
        print('    if "inicio" not in obra or "duracion_seg" not in obra:')
        print('        pendientes.append(obra)')
        print('        continue')
        sys.exit(1)

print("\nVerifica con:")
print('  python -c "import sys; sys.path.insert(0,\'backend\'); from systems.buildings import procesar_obras; city={\'OBRAS\':[{\'tipo\':\'CUARTEL_1\'}]}; print(procesar_obras(city), \'ok\')"')
print("\nArrancar servidor:")
print("  run.bat")
