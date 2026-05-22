"""
backend/systems/herreria.py
Calcula el bonus acumulativo de todas las herrerías del jugador.

Reglas:
- Cada ciudad del jugador puede tener una herrería de nivel 0-40
- El bonus total = SUMA de bonus(nivel_herreria_ciudad) de todas las ciudades
- El bonus es inmediato al subir de nivel
- Aplica a todas las unidades del jugador independientemente de dónde estén
"""
import csv
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent.parent / "csv" / "edificio10_herreria.csv"

_HERRERIA_DATA: dict | None = None


def _load_herreria() -> dict:
    data = {}
    if not CSV_PATH.exists():
        return data
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        for row in reader:
            if not row or not row[0].strip().isdigit():
                continue
            nivel = int(row[0].strip())
            try:
                data[nivel] = {
                    "pa": float(row[6].strip().replace(",", "") or 0),
                    "ca": float(row[7].strip().replace(",", "") or 0),
                    "hp": float(row[8].strip().replace(",", "") or 0),
                }
            except (ValueError, IndexError):
                pass
    return data


def get_herreria_data() -> dict:
    global _HERRERIA_DATA
    if _HERRERIA_DATA is None:
        _HERRERIA_DATA = _load_herreria()
    return _HERRERIA_DATA


def calcular_bonus_herreria(player: dict) -> dict:
    """
    Calcula el bonus acumulativo de todas las herrerías del jugador.
    
    Retorna:
        {
            "pa_bonus": float,   # bonus total de poder de ataque
            "ca_bonus": float,   # bonus total de clase de armadura
            "hp_bonus": float,   # bonus total de puntos de vida
            "detalle": [         # detalle por ciudad
                {"ciudad": str, "nivel": int, "pa": float, "ca": float, "hp": float}
            ]
        }
    """
    data = get_herreria_data()
    total_pa = 0.0
    total_ca = 0.0
    total_hp = 0.0
    detalle = []

    for city in player.get("cities", []):
        nivel = int(city.get("HERRERIA", 0) or 0)
        if nivel <= 0:
            continue
        bonus = data.get(nivel, data.get(max(data.keys()), {"pa":0,"ca":0,"hp":0}))
        total_pa += bonus["pa"]
        total_ca += bonus["ca"]
        total_hp += bonus["hp"]
        detalle.append({
            "ciudad": city.get("NOMBRE", "?"),
            "nivel":  nivel,
            "pa":     bonus["pa"],
            "ca":     bonus["ca"],
            "hp":     bonus["hp"],
        })

    return {
        "pa_bonus": total_pa,
        "ca_bonus": total_ca,
        "hp_bonus": total_hp,
        "detalle":  detalle,
    }
