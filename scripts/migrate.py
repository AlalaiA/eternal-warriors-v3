"""
ETERNAL WARRIORS v3.0 — Migrador de savegames v2 → v3
"""
import json
from pathlib import Path

V2          = Path(r"E:\0000ew V2Claude Versión 01\db")
V3          = Path(r"E:\0000ew V2Claude\backend\db")
PLAYERS_DIR = V3 / "players"
HUMANOS_DIR = PLAYERS_DIR / "humanos"
IA_DIR      = PLAYERS_DIR / "ia"
WORLD_DIR   = V3 / "world"
GLOBAL_DIR  = V3 / "global"

def mkdir():
    for d in [PLAYERS_DIR, HUMANOS_DIR, IA_DIR, WORLD_DIR, GLOBAL_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def save(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  OK {path.name}")

def load_cities(data):
    return data if isinstance(data, list) else data.get('cities', [])

def get_stat(val, jugador):
    if isinstance(val, dict): return val.get(jugador, 0)
    return val if jugador == 'JIARITO' else 0

def migrate():
    mkdir()

    required = ['savegame_core.json','savegame_jiarito.json','savegame_humano.json',
                'savegame_ia.json','savegame_vitaminizadas.json','savegame_inactivos.json',
                'savegame_cuevas.json','savegame_dioses.json','savegame_karlaka.json',
                'savegame_portales.json']
    for f in required:
        if not (V2 / f).exists():
            print(f"ERROR: no encontrado {V2 / f}"); return

    core    = load(V2 / "savegame_core.json")
    jiarito = load(V2 / "savegame_jiarito.json")
    humano  = load(V2 / "savegame_humano.json")
    ia      = load(V2 / "savegame_ia.json")
    vit     = load(V2 / "savegame_vitaminizadas.json")

    hul = core.get('human_unit_levels', {})
    hxp = core.get('human_xp', {})
    bg  = core.get('batallas_ganadas', 0)
    bp  = core.get('batallas_perdidas', 0)
    cd  = core.get('cuevas_derrotadas', 0)
    me  = core.get('misiones_espionaje', 0)
    da  = core.get('dioses_abatidos', {})

    print("\n── JUGADORES ──────────────────────────────────")

    # Separar ciudades de savegame_jiarito por jugador
    jia_all = load_cities(jiarito)
    # Contar por jugador para diagnóstico
    conteo = {}
    for c in jia_all:
        j = c.get('_jugador', '?')
        conteo[j] = conteo.get(j, 0) + 1
    print(f"  savegame_jiarito contiene: {conteo}")

    jia_cities   = [c for c in jia_all if c.get('_jugador', '?') in ('JIARITO', '?')]
    ginao_cities = [c for c in jia_all if c.get('_jugador', '') == 'GINAO']

    # JIARITO
    save(PLAYERS_DIR / "jiarito.json", {
        "player": "JIARITO",
        "unit_levels": core.get('unit_levels', {}),
        "experiencia": core.get('global_experience', 0),
        "ng_plus": core.get('ng_plus', 0),
        "dioses_abatidos": da.get('JIARITO', []) if isinstance(da, dict) else [],
        "batallas_ganadas": get_stat(bg, 'JIARITO'),
        "batallas_perdidas": get_stat(bp, 'JIARITO'),
        "cuevas_derrotadas": get_stat(cd, 'JIARITO'),
        "misiones_espionaje": get_stat(me, 'JIARITO'),
        "cities": jia_cities
    })

    # GINAO
    save(PLAYERS_DIR / "ginao.json", {
        "player": "GINAO",
        "unit_levels": hul.get('GINAO', {}),
        "experiencia": hxp.get('GINAO', 0),
        "ng_plus": core.get('human_ng_plus', {}).get('GINAO', 0),
        "dioses_abatidos": da.get('GINAO', []) if isinstance(da, dict) else [],
        "batallas_ganadas": get_stat(bg, 'GINAO'),
        "batallas_perdidas": get_stat(bp, 'GINAO'),
        "cuevas_derrotadas": get_stat(cd, 'GINAO'),
        "misiones_espionaje": get_stat(me, 'GINAO'),
        "cities": ginao_cities
    })

    # HUMANOS
    humano_cities = load_cities(humano)
    jugadores_humanos = {}
    for c in humano_cities:
        j = c.get('_jugador', 'DESCONOCIDO').upper()
        jugadores_humanos.setdefault(j, []).append(c)

    for jugador, cities in jugadores_humanos.items():
        dest = PLAYERS_DIR / f"{jugador.lower()}.json" if jugador == 'JOTICALINDO' else HUMANOS_DIR / f"{jugador.lower()}.json"
        save(dest, {
            "player": jugador,
            "unit_levels": hul.get(jugador, {}),
            "experiencia": hxp.get(jugador, 0),
            "ng_plus": core.get('human_ng_plus', {}).get(jugador, 0),
            "dioses_abatidos": da.get(jugador, []) if isinstance(da, dict) else [],
            "batallas_ganadas": get_stat(bg, jugador),
            "batallas_perdidas": get_stat(bp, jugador),
            "cuevas_derrotadas": get_stat(cd, jugador),
            "misiones_espionaje": get_stat(me, jugador),
            "cities": cities
        })

    # ALALAIA y ADMIN
    vit_cities = load_cities(vit)
    for jugador in ('ALALAIA', 'ADMIN'):
        cities = [c for c in vit_cities if c.get('_jugador','').upper() == jugador]
        save(PLAYERS_DIR / f"{jugador.lower()}.json", {
            "player": jugador,
            "unit_levels": hul.get(jugador, {}),
            "experiencia": hxp.get(jugador, 0),
            "cities": cities
        })

    # IA
    ia_cities = load_cities(ia)
    ia_groups = {}
    for c in ia_cities:
        j = c.get('_jugador', 'IA').upper()
        ia_groups.setdefault(j, []).append(c)
    for jugador, cities in ia_groups.items():
        save(IA_DIR / f"{jugador.lower()}.json", {
            "player": jugador,
            "unit_levels": core.get('ia_unit_levels', {}).get(jugador, {}),
            "experiencia": core.get('ia_xp', {}).get(jugador, 0),
            "cities": cities
        })

    print("\n── MUNDO ───────────────────────────────────────")

    save(WORLD_DIR / "inactivos.json", {"cities":   load_cities(load(V2 / "savegame_inactivos.json"))})
    save(WORLD_DIR / "cuevas.json",    {"entities": load_cities(load(V2 / "savegame_cuevas.json"))})
    save(WORLD_DIR / "dioses.json",    {"entities": load_cities(load(V2 / "savegame_dioses.json"))})

    kl = load_cities(load(V2 / "savegame_karlaka.json"))
    save(WORLD_DIR / "karlaka.json", {"entity": kl[0] if kl else {}})

    portales_list = load_cities(load(V2 / "savegame_portales.json"))
    portales_limpios = [p for p in portales_list if p.get('ID','').startswith('Portal-')]
    print(f"  Portales: {len(portales_limpios)} válidos de {len(portales_list)} totales")
    save(WORLD_DIR / "portales.json", {"entities": portales_limpios})

    print("\n── GLOBAL ──────────────────────────────────────")

    save(GLOBAL_DIR / "core.json", {
        "alianzas": core.get('alianzas', core.get('_alianzas', [])),
        "mensajes": core.get('mensajes', core.get('_mensajes', [])),
        "dioses_muertos": core.get('dioses_muertos', []),
        "order_speed": core.get('order_speed', 1.0),
        "ng_plus_global": core.get('ng_plus', 0),
        "save_timestamp": core.get('save_timestamp', 0),
    })
    save(GLOBAL_DIR / "orders.json",   {"orders": core.get('orders', [])})
    save(GLOBAL_DIR / "accounts.json", {"accounts": core.get('cuentas', {})})

    print("\n✅ Migración completa → " + str(V3))

if __name__ == "__main__":
    migrate()
