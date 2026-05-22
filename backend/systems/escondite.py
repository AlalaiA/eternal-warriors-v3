"""
backend/systems/escondite.py
Sistema de Escondite — protege materiales y tropas de ataques.

Reglas:
- El jugador decide qué y cuánto esconder (manual)
- Capacidades por nivel: cap_ejercito (tropas) y cap_material (por cada material)
- No guarda Maná ni Invocaciones
- Protege contra ataques normales
- NO protege contra nivel 40 + AlalaiA/Éon Supremo
- Reincorporación manual
"""
import csv
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent.parent / "csv" / "edificio6_escondite.csv"

_ESCONDITE_DATA: dict | None = None

MATERIALES = ["MADERA", "PIEDRA", "HIERRO", "CARBON", "ORO"]
TROPAS_BASICAS = ["ALDEANO", "EXPLORADOR", "SACERDOTE", "GUERRERO", "COMANDO",
                  "MERCENARIO", "MARINE", "CYBORG", "MAGO", "METAHUMANO"]


def _load_escondite() -> dict:
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
                    "cap_ejercito": float(row[6].strip().replace(",", "") or 0),
                    "cap_material": float(row[7].strip().replace(",", "") or 0),
                }
            except (ValueError, IndexError):
                pass
    return data


def get_escondite_data() -> dict:
    global _ESCONDITE_DATA
    if _ESCONDITE_DATA is None:
        _ESCONDITE_DATA = _load_escondite()
    return _ESCONDITE_DATA


def get_capacidades(nivel: int) -> dict:
    """Retorna las capacidades del escondite para un nivel dado."""
    data = get_escondite_data()
    if nivel <= 0:
        return {"cap_ejercito": 0, "cap_material": 0}
    max_nivel = max(data.keys()) if data else 1
    return data.get(nivel, data.get(max_nivel, {"cap_ejercito": 0, "cap_material": 0}))


def get_estado(city: dict) -> dict:
    """Retorna el estado actual del escondite de una ciudad."""
    nivel = int(city.get("ESCONDITE", 0) or 0)
    caps = get_capacidades(nivel)
    escondido = city.get("ESCONDITE_DATA", {
        "materiales": {m: 0 for m in MATERIALES},
        "tropas": {t: 0 for t in TROPAS_BASICAS},
    })
    # Calcular totales usados
    total_tropas = sum(escondido.get("tropas", {}).values())
    return {
        "nivel": nivel,
        "cap_ejercito": caps["cap_ejercito"],
        "cap_material": caps["cap_material"],
        "escondido": escondido,
        "tropas_usadas": total_tropas,
        "tropas_libres": max(0, caps["cap_ejercito"] - total_tropas),
    }


def meter_material(city: dict, material: str, cantidad: float) -> dict:
    """Mueve materiales de la ciudad al escondite."""
    material = material.upper()
    if material not in MATERIALES:
        return {"ok": False, "msg": f"{material} no es un material válido"}
    
    nivel = int(city.get("ESCONDITE", 0) or 0)
    if nivel <= 0:
        return {"ok": False, "msg": "No tienes Escondite construido"}
    
    caps = get_capacidades(nivel)
    _init_escondite_data(city)
    
    escondido_actual = city["ESCONDITE_DATA"]["materiales"].get(material, 0)
    espacio_libre = caps["cap_material"] - escondido_actual
    
    if espacio_libre <= 0:
        return {"ok": False, "msg": f"Escondite lleno para {material}"}
    
    cantidad = min(cantidad, espacio_libre, float(city.get(material, 0) or 0))
    if cantidad <= 0:
        return {"ok": False, "msg": "No hay suficiente material o espacio"}
    
    city[material] = float(city.get(material, 0) or 0) - cantidad
    city["ESCONDITE_DATA"]["materiales"][material] = escondido_actual + cantidad
    
    return {"ok": True, "msg": f"{cantidad:,.0f} {material} escondido",
            "escondido": city["ESCONDITE_DATA"]["materiales"][material]}


def sacar_material(city: dict, material: str, cantidad: float) -> dict:
    """Saca materiales del escondite a la ciudad."""
    material = material.upper()
    _init_escondite_data(city)
    
    escondido = city["ESCONDITE_DATA"]["materiales"].get(material, 0)
    cantidad = min(cantidad, escondido)
    
    if cantidad <= 0:
        return {"ok": False, "msg": f"No hay {material} escondido"}
    
    city["ESCONDITE_DATA"]["materiales"][material] = escondido - cantidad
    city[material] = float(city.get(material, 0) or 0) + cantidad
    
    return {"ok": True, "msg": f"{cantidad:,.0f} {material} reincorporado"}


def meter_tropas(city: dict, tropa: str, cantidad: int) -> dict:
    """Mueve tropas de la ciudad al escondite."""
    tropa = tropa.upper()
    if tropa not in TROPAS_BASICAS:
        return {"ok": False, "msg": f"{tropa} no es una tropa básica"}
    
    nivel = int(city.get("ESCONDITE", 0) or 0)
    if nivel <= 0:
        return {"ok": False, "msg": "No tienes Escondite construido"}
    
    caps = get_capacidades(nivel)
    _init_escondite_data(city)
    
    total_tropas = sum(city["ESCONDITE_DATA"]["tropas"].values())
    espacio_libre = caps["cap_ejercito"] - total_tropas
    
    if espacio_libre <= 0:
        return {"ok": False, "msg": "Escondite lleno para tropas"}
    
    disponible = int(city.get(tropa, 0) or 0)
    cantidad = min(cantidad, int(espacio_libre), disponible)
    
    if cantidad <= 0:
        return {"ok": False, "msg": "No hay tropas disponibles o espacio"}
    
    city[tropa] = disponible - cantidad
    city["ESCONDITE_DATA"]["tropas"][tropa] = city["ESCONDITE_DATA"]["tropas"].get(tropa, 0) + cantidad
    
    return {"ok": True, "msg": f"{cantidad:,} {tropa} escondido",
            "escondido": city["ESCONDITE_DATA"]["tropas"][tropa]}


def sacar_tropas(city: dict, tropa: str, cantidad: int) -> dict:
    """Saca tropas del escondite a la ciudad."""
    tropa = tropa.upper()
    _init_escondite_data(city)
    
    escondido = int(city["ESCONDITE_DATA"]["tropas"].get(tropa, 0))
    cantidad = min(cantidad, escondido)
    
    if cantidad <= 0:
        return {"ok": False, "msg": f"No hay {tropa} escondido"}
    
    city["ESCONDITE_DATA"]["tropas"][tropa] = escondido - cantidad
    city[tropa] = int(city.get(tropa, 0) or 0) + cantidad
    
    return {"ok": True, "msg": f"{cantidad:,} {tropa} reincorporado"}


def _init_escondite_data(city: dict):
    """Inicializa ESCONDITE_DATA si no existe."""
    if "ESCONDITE_DATA" not in city:
        city["ESCONDITE_DATA"] = {
            "materiales": {m: 0 for m in MATERIALES},
            "tropas": {t: 0 for t in TROPAS_BASICAS},
        }
    # Asegurar que todas las keys existen
    if "materiales" not in city["ESCONDITE_DATA"]:
        city["ESCONDITE_DATA"]["materiales"] = {m: 0 for m in MATERIALES}
    if "tropas" not in city["ESCONDITE_DATA"]:
        city["ESCONDITE_DATA"]["tropas"] = {t: 0 for t in TROPAS_BASICAS}
