"""
ETERNAL WARRIORS v3.0 — Servidor principal
Ejecutar: python -m uvicorn backend.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.ws_handler import router as ws_router
from backend.api.auth import router as auth_router
from backend.api.city import router as city_router
from backend.api.map import router as map_router
import uvicorn

app = FastAPI(title="Eternal Warriors v3.0")

# WebSocket
app.include_router(ws_router)

# API REST
app.include_router(auth_router, prefix="/api/auth")
app.include_router(city_router, prefix="/api/city")
app.include_router(map_router,  prefix="/api/map")

# Frontend estático
app.mount("/static", StaticFiles(directory="frontend", html=True), name="static")

@app.get("/")
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
    return response

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
