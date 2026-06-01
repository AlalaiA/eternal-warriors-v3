"""
recuperar_tropas.py — v2
Ejecutar UNA sola vez con el servidor APAGADO.
"""
import json, os
from pathlib import Path

BASE        = Path("E:/0000ew V2Claude")
PLAYER_PATH = BASE / "backend/db/players/joticalindo.json"

jot    = json.loads(PLAYER_PATH.read_text(encoding="utf-8"))
ciudad = next(c for c in jot["cities"] if c["NOMBRE"] == "jL01")

RECUPERAR = {
    "MAGO":       205_013_663,
    "MADRESELVA": 999_999_999_999,
    "ALONARDO":   53_188_769,
}

print("=== APLICANDO RECUPERACIÓN ===")
for k, v in RECUPERAR.items():
    actual = int(ciudad.get(k, 0) or 0)
    ciudad[k] = actual + v
    print(f"  {k:20s}: {actual:>20,} + {v:>20,} = {ciudad[k]:>20,}")

tmp = str(PLAYER_PATH) + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(json.dumps(jot, ensure_ascii=True, indent=2))
os.replace(tmp, PLAYER_PATH)
print("\n✅ Listo. Arranca el servidor.")
