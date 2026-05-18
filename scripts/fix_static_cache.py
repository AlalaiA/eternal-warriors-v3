from pathlib import Path

path = Path(r"E:\0000ew V2Claude\backend\main.py")
src = path.read_text(encoding="utf-8")

OLD = 'app.mount("/static", StaticFiles(directory="frontend"), name="static")'
NEW = 'app.mount("/static", StaticFiles(directory="frontend", html=True), name="static")'

c = src.count(OLD)
if c != 1:
    print(f"ERROR: {c} veces"); exit(1)
src = src.replace(OLD, NEW)
path.write_text(src, encoding="utf-8")
print("OK main.py")

# Añadir headers no-cache al servidor
OLD2 = '''@app.get("/")
def index():
    return FileResponse("frontend/index.html")

@app.get("/game")
def game():
    return FileResponse("frontend/game.html")'''

NEW2 = '''@app.get("/")
def index():
    return FileResponse("frontend/index.html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

@app.get("/game")
def game():
    return FileResponse("frontend/game.html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

@app.middleware("http")
async def no_cache(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response'''

c2 = src.count(OLD2)
if c2 != 1:
    print(f"ERROR middleware: {c2} veces"); exit(1)
src = src.replace(OLD2, NEW2)
path.write_text(src, encoding="utf-8")
print("OK main.py — no-cache middleware añadido")
print("\n✅ Reinicia run.bat y recarga el navegador.")
