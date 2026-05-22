"""
install_queues.py
Eternal Warriors v3.0 — Instala sistema de colas

Corre desde: E:\\0000ew V2Claude\\
Comando:     python install_queues.py
"""

import shutil
from pathlib import Path

BASE   = Path(r"E:\0000ew V2Claude")
SCRIPT = Path(__file__).parent

# ── 1. Copiar archivos backend ────────────────────────────────────────────────
shutil.copy2(SCRIPT / "queues.py",     BASE / "backend" / "systems" / "queues.py")
print("OK: backend/systems/queues.py")

shutil.copy2(SCRIPT / "queues_api.py", BASE / "backend" / "api" / "queues.py")
print("OK: backend/api/queues.py")

# ── 2. Registrar router en main.py ────────────────────────────────────────────
MAIN = BASE / "backend" / "main.py"
src  = MAIN.read_text(encoding="utf-8")

OLD = "from backend.api.map import router as map_router"
NEW = """\
from backend.api.map    import router as map_router
from backend.api.queues import router as queues_router"""

if OLD in src and "queues_router" not in src:
    src = src.replace(OLD, NEW)
    OLD2 = 'app.include_router(map_router,  prefix="/api/map")'
    NEW2 = '''\
app.include_router(map_router,    prefix="/api/map")
app.include_router(queues_router, prefix="/api/queues")'''
    src = src.replace(OLD2, NEW2)
    MAIN.write_text(src, encoding="utf-8")
    print("OK: queues_router registrado en main.py")
else:
    print("SKIP: queues_router ya registrado")

print()
print("HECHO.")
print()
print("Reinicia el servidor:")
print("  Ctrl+C → run.bat")
print()
print("Endpoints disponibles:")
print("  GET  /api/queues/{jugador}/{ciudad}           — estado colas")
print("  POST /api/queues/{jugador}/{ciudad}/cuartel   — iniciar entrenamiento")
print("  POST /api/queues/{jugador}/{ciudad}/templo    — iniciar invocación")
print("  DELETE /api/queues/{jugador}/{ciudad}/{tipo}  — cancelar cola")
