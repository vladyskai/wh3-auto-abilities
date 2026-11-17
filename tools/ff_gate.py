#!/usr/bin/env python3
"""Round 166: the friendly-fire gate (user ruling 2026-11-17: "Vortex with affects_allies=false should have no
friendly-fire check").

Every mod entry whose family runs a friendly-fire check must have a blast the GAME says can hit our units:
  * a vortex (unit_spec_abil.vortex and its subsequent_vortex chain) with affects_allies = true, or
  * a projectile (activated_projectile) with can_damage_allies = true or an explosion with affects_allies = true, or
  * a bombardment whose projectile or explosion can hit allies.
The WW families (wave, wander, strike, cone, sweep) read the flag per entry from the GENERATED WW table (row.allies):
they are listed apart and only reported. ally_blast casts on our own unit and has no check.

  violations(script_txt) -> [(marker, family, key, why)]   (empty = the gate passes)
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_vortex_tables as GV  # noqa: E402

# the families whose evaluator refuses a cast near our units, with no per-entry flag
CHECKED = ("enemy_blob", "enemy_blob_vortex", "enemy_large_shot", "enemy_single_shot", "enemy_infantry_shot",
           "melee_clear", "fly_dive", "last_stand_clear")


def can_hit_allies(usa_row, vx, prj, exp, bomb):
    rows = GV.chain(vx, usa_row.get("vortex", ""))
    if any(r["affects_allies"] == "true" for r in rows):
        return True
    p = prj.get(usa_row.get("activated_projectile", ""), {})
    if p.get("can_damage_allies") == "true" or exp.get(p.get("explosion_type", ""), {}).get("affects_allies") == "true":
        return True
    b = bomb.get(usa_row.get("bombardment", ""), {})
    bp = prj.get(b.get("projectile_type", ""), {})
    if bp.get("can_damage_allies") == "true" or exp.get(bp.get("explosion_type", ""), {}).get("affects_allies") == "true":
        return True
    return False


def entries(script_txt):
    body = script_txt.split("\nlocal ABILITIES = {", 1)[1].split("\n}\n", 1)[0]
    out = []
    for chunk in body.split("\n\t{ marker = ")[1:]:
        m = re.match(r'"([^"]+)",.*?trigger = "([a-z_0-9]+)",', chunk, re.S)
        keys = re.findall(r'"([^"]+)"', re.search(r"keys = \{([^}]*)\}", chunk).group(1))
        tc = re.search(r'target_class = "([a-z_]+)"', chunk)
        out.append((m.group(1), m.group(2), keys, tc.group(1) if tc else None))
    assert len(out) == script_txt.count("\t{ marker = "), (len(out), script_txt.count("\t{ marker = "))
    return out


def violations(script_txt):
    usa = {r["key"]: r for r in GV.tsv("unit_spec_abil.tsv")}
    vx = {r["vortex_key"]: r for r in GV.tsv("battle_vortexs.tsv")}
    prj = {r["key"]: r for r in GV.tsv("projectiles.tsv")}
    exp = {r["key"]: r for r in GV.tsv("projectiles_explosions.tsv")}
    bomb = {r["bombardment_key"]: r for r in GV.tsv("projectile_bombardments.tsv")}
    bad, n = [], 0
    for marker, fam, keys, tc in entries(script_txt):
        if fam in CHECKED or tc == "commander_ground":
            for k in keys:
                n += 1
                if not can_hit_allies(usa.get(k, {}), vx, prj, exp, bomb):
                    bad.append((marker, fam, k, "the game says its blast cannot hit our units"))
    return bad, n


if __name__ == "__main__":
    src = open(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua",
               encoding="utf-8").read()
    bad, n = violations(src)
    print("checked keys:", n, "violations:", len(bad))
    for b in bad:
        print("  ", b)
