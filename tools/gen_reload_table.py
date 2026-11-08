#!/usr/bin/env python3
"""Generate FOURTH.RELOAD_S - every ranged unit's reload time in seconds - from the
game's own tables in gamedata\\wh3 (user ruling 2026-11-03: a baked stat is allowed
when the engine offers no live read; the battle API has no reload read).

Chain, per main unit (battle_unit:type() answers the main_units key):
  main_units.unit -> main_units.land_unit -> land_units.primary_missile_weapon
  (artillery: land_units.engine -> battlefield_engines.missile_weapon)
  -> missile_weapons.default_projectile -> projectiles.base_reload_time
  reload = base_reload_time x (1 - land_units.reload / 100)
The reload-skill term can only make the value SMALLER (cast earlier), which is the
safe direction for "cast before the second shot". Units with no missile weapon are
not listed. Never hand-edit the generated block: re-run this script.

    python gen_reload_table.py            # print the Lua block to stdout
    python gen_reload_table.py --check F  # exit 1 unless F contains exactly this block
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gamedata_paths import GAMEDATA  # noqa: E402

BEGIN = "-- BEGIN GENERATED RELOAD TABLE (tools/gen_reload_table.py; do not edit by hand)\n"
END = "-- END GENERATED RELOAD TABLE\n"


def table(name):
    with open(os.path.join(GAMEDATA, name), encoding="utf-8") as f:
        rows = [r for r in csv.reader(f, delimiter="\t") if r]
    return {r[0]: dict(zip(rows[0], r)) for r in rows[2:]}


def build():
    mu, lu = table("main_units.tsv"), table("land_units.tsv")
    mw, pj, be = table("missile_weapons.tsv"), table("projectiles.tsv"), table("battlefield_engines.tsv")
    out = {}
    for unit, m in mu.items():
        L = lu.get(m.get("land_unit", ""))
        if L is None:
            continue
        w = L.get("primary_missile_weapon", "") or be.get(L.get("engine", ""), {}).get("missile_weapon", "")
        if not w or w not in mw:
            continue
        p = pj.get(mw[w]["default_projectile"])
        if p is None:
            continue
        base = float(p["base_reload_time"])
        skill = float(L.get("reload") or 0)
        r = round(base * (1.0 - skill / 100.0), 2)
        if r > 0:
            out[unit] = r
    return out


def block():
    t = build()
    lines = [BEGIN, "-- %d ranged units: seconds between shots (base_reload_time x (1 - reload skill / 100))\n" % len(t),
             "FOURTH.RELOAD_S = {\n"]
    for k in sorted(t):
        lines.append('\t["%s"] = %s,\n' % (k, ("%g" % t[k])))
    lines += ["}\n", END]
    return "".join(lines)


if __name__ == "__main__":
    b = block()
    if len(sys.argv) > 2 and sys.argv[1] == "--check":
        s = open(sys.argv[2], encoding="utf-8").read()
        ok = s.count(b) == 1
        print("RELOAD TABLE %s in %s" % ("MATCHES the game data" if ok else "DIFFERS from the game data", sys.argv[2]))
        sys.exit(0 if ok else 1)
    sys.stdout.write(b)
