"""
backend/api/messages.py
Eternal Warriors v3.0 — Mensajería interna

Almacenamiento: backend/db/global/messages.json
{
  "mensajes": [
    {
      "id":        "msg_1234567890_abc",
      "tipo":      "DIRECTO" | "ALIANZA",
      "de":        "JOTICALINDO",
      "para":      "GINAO",           # solo DIRECTO
      "alianza":   "AAA_KILLERS",     # solo ALIANZA
      "asunto":    "str",
      "cuerpo":    "str",
      "ts":        1234567890,
      "leido_por": ["GINAO"]
    }
  ]
}
"""

import time, uuid
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from backend.data.save_manager import load_json, save_json, SaveManager
from backend.systems.alliances import _alianza_de, _migrar_todas

router = APIRouter()
sm     = SaveManager()

DB           = Path(__file__).parent.parent / "db"
MESSAGES_PATH = DB / "global" / "messages.json"
MAX_MENSAJES  = 500
MAX_CUERPO    = 1000


# ── Modelos ───────────────────────────────────────────────────────────────────

class EnviarRequest(BaseModel):
    de:      str
    para:    Optional[str] = None
    alianza: Optional[str] = None
    asunto:  str = ""
    cuerpo:  str

class LeerRequest(BaseModel):
    jugador: str
    msg_ids: list[str]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_msgs() -> list:
    if not MESSAGES_PATH.exists():
        return []
    try:
        return load_json(MESSAGES_PATH).get("mensajes", [])
    except Exception:
        return []

def _save_msgs(mensajes: list) -> None:
    mensajes = sorted(mensajes, key=lambda m: m.get("ts", 0), reverse=True)[:MAX_MENSAJES]
    save_json(MESSAGES_PATH, {"mensajes": mensajes})

def _nuevo_id() -> str:
    return f"msg_{int(time.time())}_{uuid.uuid4().hex[:6]}"

def _bandeja(jugador: str, mensajes: list, alianzas: dict) -> list:
    """Mensajes visibles para el jugador: directos + de su alianza."""
    jugador        = jugador.upper()
    nombre_alianza = _alianza_de(jugador, alianzas)
    resultado = []
    for m in mensajes:
        if m.get("tipo") == "DIRECTO":
            if m.get("de") == jugador or m.get("para") == jugador:
                resultado.append(m)
        elif m.get("tipo") == "ALIANZA":
            if nombre_alianza and m.get("alianza") == nombre_alianza:
                resultado.append(m)
    return sorted(resultado, key=lambda m: m.get("ts", 0), reverse=True)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/{jugador}/no_leidos")
def get_no_leidos(jugador: str):
    """Conteo rápido para badge en nav."""
    jugador  = jugador.upper()
    mensajes = _load_msgs()
    alianzas = sm.load_alliances()
    _migrar_todas(alianzas)
    bandeja  = _bandeja(jugador, mensajes, alianzas)
    count    = sum(
        1 for m in bandeja
        if jugador not in m.get("leido_por", [])
        and m.get("de") != jugador
    )
    return {"ok": True, "no_leidos": count}


@router.get("/{jugador}")
def get_bandeja(jugador: str):
    jugador  = jugador.upper()
    mensajes = _load_msgs()
    alianzas = sm.load_alliances()
    _migrar_todas(alianzas)
    return {"ok": True, "mensajes": _bandeja(jugador, mensajes, alianzas)}


@router.post("/enviar")
def post_enviar(req: EnviarRequest):
    de = req.de.upper()

    if not req.cuerpo.strip():
        return {"ok": False, "msg": "El mensaje no puede estar vacío"}
    if len(req.cuerpo) > MAX_CUERPO:
        return {"ok": False, "msg": f"Máximo {MAX_CUERPO} caracteres"}
    if not req.para and not req.alianza:
        return {"ok": False, "msg": "Especifica destinatario o alianza"}

    alianzas = sm.load_alliances()
    _migrar_todas(alianzas)

    if req.alianza:
        nombre_ali = req.alianza.upper().replace(" ", "_")
        if nombre_ali not in alianzas:
            return {"ok": False, "msg": "Alianza no encontrada"}
        if de not in alianzas[nombre_ali]["miembros"]:
            return {"ok": False, "msg": "No eres miembro de esa alianza"}
        msg = {
            "id":        _nuevo_id(),
            "tipo":      "ALIANZA",
            "de":        de,
            "alianza":   nombre_ali,
            "asunto":    req.asunto.strip()[:100],
            "cuerpo":    req.cuerpo.strip(),
            "ts":        int(time.time()),
            "leido_por": [de],
        }
    else:
        para = req.para.upper()
        if para == de:
            return {"ok": False, "msg": "No puedes enviarte mensajes a ti mismo"}
        msg = {
            "id":        _nuevo_id(),
            "tipo":      "DIRECTO",
            "de":        de,
            "para":      para,
            "asunto":    req.asunto.strip()[:100],
            "cuerpo":    req.cuerpo.strip(),
            "ts":        int(time.time()),
            "leido_por": [de],
        }

    mensajes = _load_msgs()
    mensajes.append(msg)
    _save_msgs(mensajes)
    return {"ok": True, "msg": "Mensaje enviado", "id": msg["id"]}


@router.post("/leer")
def post_leer(req: LeerRequest):
    jugador  = req.jugador.upper()
    mensajes = _load_msgs()
    marcados = 0
    for m in mensajes:
        if m["id"] in req.msg_ids and jugador not in m.get("leido_por", []):
            m.setdefault("leido_por", []).append(jugador)
            marcados += 1
    if marcados:
        _save_msgs(mensajes)
    return {"ok": True, "marcados": marcados}


@router.delete("/{msg_id}")
def delete_mensaje(msg_id: str, jugador: str):
    """Borra un mensaje. Solo el remitente puede borrarlo."""
    jugador  = jugador.upper()
    mensajes = _load_msgs()
    antes    = len(mensajes)
    mensajes = [m for m in mensajes
                if not (m["id"] == msg_id and m.get("de") == jugador)]
    if len(mensajes) == antes:
        return {"ok": False, "msg": "No encontrado o sin permiso"}
    _save_msgs(mensajes)
    return {"ok": True, "msg": "Eliminado"}
