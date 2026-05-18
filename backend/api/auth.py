"""
Autenticación de jugadores
"""
from fastapi import APIRouter
from pydantic import BaseModel
from backend.data.save_manager import SaveManager
import hashlib

router = APIRouter()
sm = SaveManager()

class LoginRequest(BaseModel):
    usuario: str
    password: str

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

@router.post("/login")
def login(req: LoginRequest):
    accounts = sm.load_accounts()
    usuario = req.usuario.upper()
    hashed = hash_pw(req.password)
    stored = accounts.get(usuario, accounts.get(req.usuario, ""))
    if stored and (stored == hashed or stored == req.password):
        player = sm.load_player(usuario)
        cities = player.get("cities", [])
        capital = cities[0].get("NOMBRE", "") if cities else ""
        return {"ok": True, "jugador": usuario, "capital": capital}
    return {"ok": False, "msg": "Usuario o contraseña incorrectos"}
