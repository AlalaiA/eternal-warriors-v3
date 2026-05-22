"""
fix_05_buildings_api_savemanager.py
Corrige buildings.py API para usar SaveManager() en lugar de load_player/save_player sueltos.
Ejecutar desde: E:\0000ew V2Claude\
"""
import pathlib, sys

TARGET = pathlib.Path("backend/api/buildings.py")
if not TARGET.exists():
    sys.exit(f"ERROR: No se encuentra {TARGET}")

NEW_CONTENT = '''"""
backend/api/buildings.py
Endpoints REST para info y gestión de edificios.
"""
from fastapi import APIRouter, HTTPException
from backend.data.save_manager import SaveManager
from backend.systems.buildings import buildings_info, iniciar_obra, cancelar_obra, procesar_obras

router = APIRouter(prefix="/api/buildings", tags=["buildings"])
_sm = SaveManager()


def _get_city(jugador: str, ciudad: str):
    player = _sm.load_player(jugador)
    if not player:
        raise HTTPException(404, f"Jugador {jugador} no encontrado")
    city = next((c for c in player.get("cities", []) if c["NOMBRE"] == ciudad), None)
    if not city:
        raise HTTPException(404, f"Ciudad {ciudad} no encontrada")
    return player, city


@router.get("/{jugador}/{ciudad}/{edificio}")
def get_building_info(jugador: str, ciudad: str, edificio: str):
    player, city = _get_city(jugador, ciudad)
    subidos = procesar_obras(city)
    if subidos:
        _sm.save_player(jugador, player)
    info = buildings_info(city, edificio.upper())
    if "error" in info:
        raise HTTPException(400, info["error"])
    return info


@router.post("/{jugador}/{ciudad}/{edificio}/upgrade")
def post_upgrade(jugador: str, ciudad: str, edificio: str):
    player, city = _get_city(jugador, ciudad)
    procesar_obras(city)
    result = iniciar_obra(player, city, edificio.upper())
    if "error" in result:
        raise HTTPException(400, result["error"])
    _sm.save_player(jugador, player)
    return result


@router.delete("/{jugador}/{ciudad}/{edificio}/upgrade")
def delete_upgrade(jugador: str, ciudad: str, edificio: str):
    player, city = _get_city(jugador, ciudad)
    result = cancelar_obra(city, edificio.upper())
    if "error" in result:
        raise HTTPException(400, result["error"])
    _sm.save_player(jugador, player)
    return result
'''

TARGET.write_text(NEW_CONTENT, encoding="utf-8")
print(f"✅ Corregido: {TARGET}")
print("   SaveManager() instanciado, métodos load_player/save_player correctos.")
print("\nArrancar servidor:")
print("  run.bat")
