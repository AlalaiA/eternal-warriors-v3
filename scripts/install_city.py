"""
install_city.py
Eternal Warriors v3.0 — Instala city.js reescrito desde cero

Corre desde: E:\\0000ew V2Claude\\
Comando:     python install_city.py
"""
import shutil, sys
from pathlib import Path

SRC  = Path(__file__).parent / 'city_new.js'
DEST = Path(r'E:\0000ew V2Claude\frontend\js\screens\city.js')
BAK  = DEST.with_suffix('.js.bak')

if not SRC.exists():
    print(f"ERROR: No se encontró city_new.js junto a este script.")
    sys.exit(1)

if not DEST.exists():
    print(f"ERROR: No se encontró el destino:\n  {DEST}")
    sys.exit(1)

# Backup
shutil.copy2(DEST, BAK)
print(f"Backup guardado en: {BAK}")

# Instalar
shutil.copy2(SRC, DEST)
print(f"Instalado en:       {DEST}")
print()
print("HECHO.")
print()
print("Para verificar:")
print("  Reinicia el servidor: Ctrl+C → run.bat")
print("  Abre en pestaña nueva incógnito: http://127.0.0.1:8000/game")
print("  Si algo falla, restaura el backup:")
print(f"    copy \"{BAK}\" \"{DEST}\"")
