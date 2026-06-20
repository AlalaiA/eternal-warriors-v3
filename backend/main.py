"""
ETERNAL WARRIORS v3.0 — Servidor principal
Ejecutar: python -m uvicorn backend.main:app --reload --port 8000
"""
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from backend.ws_handler import router as ws_router
from backend.api.auth import router as auth_router
from backend.api.city import router as city_router
from backend.api.map import router as map_router
from backend.api.buildings import router as buildings_router
from backend.api.queues import router as queues_router
from backend.api.escondite import router as escondite_router
from backend.api.orders import router as orders_router
from backend.api.alliances import router as alliances_router
from backend.api.leveling import router as leveling_router
from backend.api.messages import router as messages_router
from backend.api.alerts  import router as alerts_router

# ── Ticker de órdenes ─────────────────────────────────────────────────────────

ORDERS_TICK_SEG = 5    # procesar órdenes cada 5 segundos
IA_TICK_SEG     = 120  # tick de jugadores IA cada 2 minutos

async def _ia_ticker():
    """Tarea de fondo: procesa el comportamiento autónomo de los jugadores IA."""
    from backend.data.save_manager import SaveManager
    from backend.systems.ia_behavior import procesar_tick_ia
    sm = SaveManager()
    while True:
        try:
            ordenes = sm.load_orders()
            nuevas  = procesar_tick_ia(sm, ordenes)
            if nuevas:
                ordenes_actuales = sm.load_orders()
                activas     = [o for o in ordenes_actuales if o.get("estado") != "COMPLETADA"]
                completadas = sorted(
                    [o for o in ordenes_actuales if o.get("estado") == "COMPLETADA"],
                    key=lambda o: o.get("inicio", 0), reverse=True
                )[:200]
                sm.save_orders(activas + completadas + nuevas)
                print(f"[ia_ticker] {len(nuevas)} nuevas órdenes IA encoladas")
        except Exception as e:
            import traceback
            print(f"[ia_ticker] Error: {e}")
            traceback.print_exc()
        await asyncio.sleep(IA_TICK_SEG)


async def _orders_ticker():
    """Tarea de fondo: procesa órdenes activas cada ORDERS_TICK_SEG segundos."""
    from backend.data.save_manager import SaveManager
    from backend.systems.orders import procesar_ordenes
    sm = SaveManager()
    while True:
        try:
            orders  = sm.load_orders()
            orders  = [o for o in orders if isinstance(o, dict) and "estado" in o]
            eventos = procesar_ordenes(orders, sm)
            # Siempre persistir — haya o no eventos
            activas     = [o for o in orders if o.get("estado") != "COMPLETADA"]
            completadas = sorted(
                [o for o in orders if o.get("estado") == "COMPLETADA"],
                key=lambda o: o.get("inicio", 0), reverse=True
            )[:200]
            sm.save_orders(activas + completadas)
        except Exception as e:
            import traceback
            print(f"[orders_ticker] Error: {e}")
            traceback.print_exc()
        await asyncio.sleep(ORDERS_TICK_SEG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Arrancar tareas de fondo al iniciar el servidor."""
    task_orders = asyncio.create_task(_orders_ticker())
    task_ia     = asyncio.create_task(_ia_ticker())
    yield
    task_orders.cancel()
    task_ia.cancel()
    try:
        await task_orders
    except asyncio.CancelledError:
        pass
    try:
        await task_ia
    except asyncio.CancelledError:
        pass


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="Eternal Warriors v3.0", lifespan=lifespan)

app.include_router(ws_router)
app.include_router(auth_router,    prefix="/api/auth")
app.include_router(city_router,    prefix="/api/city")
app.include_router(map_router,     prefix="/api/map")
app.include_router(queues_router,  prefix="/api/queues")
app.include_router(buildings_router)
app.include_router(escondite_router)
app.include_router(orders_router,   prefix="/api/orders")
app.include_router(alliances_router, prefix="/api/alliances")
app.include_router(leveling_router,  prefix="/api/leveling")
app.include_router(messages_router,  prefix="/api/messages")
app.include_router(alerts_router,    prefix="/api/alerts")

app.mount("/static", StaticFiles(directory="frontend", html=True), name="static")


@app.get("/favicon.ico")
def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)

@app.get("/")
def index():
    return FileResponse("frontend/index.html",
                        headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

@app.get("/game")
def game():
    return FileResponse("frontend/game.html",
                        headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

@app.middleware("http")
async def no_cache(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
