@echo off
cd /d E:\0000ew V2Claude

echo [EW] Limpiando cache de Python...
for /d /r "E:\0000ew V2Claude" %%d in (__pycache__) do (
    if exist "%%d" (
        rd /s /q "%%d"
    )
)
for /r "E:\0000ew V2Claude" %%f in (*.pyc *.pyo) do (
    if exist "%%f" del /q "%%f"
)
echo [EW] Cache limpio.

echo [EW] Arrancando servidor...
python -m uvicorn backend.main:app --reload --port 8000

echo [EW] Servidor detenido. Limpiando cache residual...
for /d /r "E:\0000ew V2Claude" %%d in (__pycache__) do (
    if exist "%%d" rd /s /q "%%d"
)
echo [EW] Listo.
pause
