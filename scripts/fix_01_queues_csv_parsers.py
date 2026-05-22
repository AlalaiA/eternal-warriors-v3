"""
fix_01_queues_csv_parsers.py
Corrige BUG 1 (MAGO no reconocida) y BUG 2 (nivel sacerdote 3000) en queues.py
Ejecutar desde: E:\0000ew V2Claude\
"""
import re, sys, pathlib

TARGET = pathlib.Path("backend/systems/queues.py")

if not TARGET.exists():
    sys.exit(f"ERROR: No se encuentra {TARGET}. Ejecutar desde la raíz del proyecto.")

src = TARGET.read_text(encoding="utf-8")
original = src

# ─── PATCH 1: _load_tiempo_unidades ───────────────────────────────────────────
# El CSV tiene BOM (utf-8-sig) + separador ';' + header en Row 0.
# El csv.reader con utf-8-sig ya elimina BOM. Row 0 es el header, Row 1+ son datos.
# Problema probable: se usa open() sin utf-8-sig o se salta la fila incorrecta.
# Reemplazamos toda la función con implementación auditada.

OLD_LOAD_TIEMPO = r'def _load_tiempo_unidades\(\).*?(?=\ndef |\nclass |\Z)'
NEW_LOAD_TIEMPO = '''def _load_tiempo_unidades():
    """Carga tiempo base (minutos) por unidad. CSV: utf-8-sig, sep=';', Row0=header, Row1+=datos."""
    import csv as _csv
    result = {}
    csv_path = pathlib.Path(__file__).parent.parent.parent / "csv" / "tiempo_base_produccion_unidades_basicas.csv"
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = _csv.reader(f, delimiter=";")
        rows = list(reader)
    # Row 0 es header; datos comienzan en Row 1
    for row in rows[1:]:
        if len(row) < 2:
            continue
        nombre = row[0].strip().upper()   # normalizar a MAYÚSCULAS
        try:
            minutos = float(row[1].strip().replace(",", "."))
            result[nombre] = minutos
        except ValueError:
            pass
    return result

'''

# ─── PATCH 2: _load_invocaciones ──────────────────────────────────────────────
# Columnas confirmadas por auditoría:
# [0]Invocación [1]HP [2]PA [3]CA [4]DESTREZA [5]SIGILO [6]VELOCIDAD
# [7]NIVEL_MIN_SACERDOTE [8]TIEMPO_BASE_MIN [9]COSTO_MANA
# El bug era usar índice 6 (VELOCIDAD=3000) en lugar de 7.

OLD_LOAD_INVOC = r'def _load_invocaciones\(\).*?(?=\ndef |\nclass |\Z)'
NEW_LOAD_INVOC = '''def _load_invocaciones():
    """
    Carga características de invocaciones. CSV: utf-8-sig, sep=';', Row0=header.
    Columnas: [0]Invocación [1]HP [2]PA [3]CA [4]DESTREZA [5]SIGILO [6]VELOCIDAD
              [7]NIVEL_MIN_SACERDOTE [8]TIEMPO_BASE_MIN [9]COSTO_MANA
    """
    import csv as _csv
    result = {}
    csv_path = pathlib.Path(__file__).parent.parent.parent / "csv" / "caracteristicas_invocaciones.csv"
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = _csv.reader(f, delimiter=";")
        rows = list(reader)
    for row in rows[1:]:  # Row 0 = header
        if len(row) < 10:
            continue
        nombre = row[0].strip().upper()
        try:
            result[nombre] = {
                "hp":                  float(row[1].strip()),
                "pa":                  float(row[2].strip()),
                "ca":                  float(row[3].strip()),
                "destreza":            float(row[4].strip()),
                "sigilo":              float(row[5].strip()),
                "velocidad":           float(row[6].strip()),
                "nivel_min_sacerdote": int(row[7].strip()),    # índice 7 ← CORRECTO
                "tiempo_base_min":     float(row[8].strip()),  # índice 8
                "costo_mana":          float(row[9].strip()),  # índice 9
            }
        except (ValueError, IndexError):
            pass
    return result

'''

# Aplicar patches con regex DOTALL
patched1 = re.sub(OLD_LOAD_TIEMPO, NEW_LOAD_TIEMPO.rstrip(), src, flags=re.DOTALL)
if patched1 == src:
    print("AVISO: No se encontró _load_tiempo_unidades() — puede que el nombre difiera.")
    print("Busca manualmente y reemplaza el bloque de carga del CSV de tiempo.")
else:
    print("✅ PATCH 1 aplicado: _load_tiempo_unidades()")
    src = patched1

patched2 = re.sub(OLD_LOAD_INVOC, NEW_LOAD_INVOC.rstrip(), src, flags=re.DOTALL)
if patched2 == src:
    print("AVISO: No se encontró _load_invocaciones() — puede que el nombre difiera.")
    print("Busca manualmente y corrige el índice de NIVEL_MIN_SACERDOTE a [7].")
else:
    print("✅ PATCH 2 aplicado: _load_invocaciones() — índice NIVEL_MIN_SACERDOTE corregido a [7]")
    src = patched2

# ─── Escribir ─────────────────────────────────────────────────────────────────
if src != original:
    backup = TARGET.with_suffix(".py.bak")
    backup.write_text(original, encoding="utf-8")
    TARGET.write_text(src, encoding="utf-8")
    print(f"\n✅ Guardado en {TARGET}  (backup: {backup})")
else:
    print("\n⚠️  No se aplicó ningún cambio. El archivo puede tener nombres de función distintos.")
    print("Ejecuta esto para ver las funciones de carga actuales:")
    print("  grep -n 'def _load' backend/systems/queues.py")

print("\nVerifica con:")
print("  python -c \"import sys; sys.path.insert(0,'backend'); from systems.queues import _load_tiempo_unidades, _load_invocaciones; t=_load_tiempo_unidades(); i=_load_invocaciones(); print('MAGO' in t, 'DEMONIO' in i, i.get('DEMONIO',{}).get('nivel_min_sacerdote'))\"")
