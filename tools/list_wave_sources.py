#!/usr/bin/env python3
"""Round 203 research (user 2026-11-22: "Dragon breaths always come from a caster. Other abilities might also, check
individually to be sure."): for every key on enemy_wave / enemy_wave_charge / enemy_cone, print what the game's tables say
about WHERE the effect starts: the vortex's launch_source and launch_source_offset, or the projectile / bombardment the
ability uses instead, plus the mod's own WW row (kind, radius, path, offset, drift, allies, ground)."""
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamedata_paths as GP  # noqa: E402

MOD = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"


def table(name):
    with open(os.path.join(GP.GAMEDATA, name), encoding="utf-8-sig") as f:
        rows = list(csv.reader(f, delimiter="\t"))
    h = rows[0]
    return h, {r[0]: dict(zip(h, r)) for r in rows[2:] if r}


def main():
    s = open(MOD, encoding="utf-8").read()
    _, usa = table("unit_spec_abil.tsv")
    vh, vx = table("battle_vortexs.tsv")
    _, ua = table("unit_abilities.tsv")
    ww_txt = re.search(r'FOURTH\.WW_TEXT = "([^"]*)"', s)
    ww = dict(x.split("=", 1) for x in ww_txt.group(1).split(";") if "=" in x) if ww_txt else {}
    print("vortex columns:", [c for c in vh if "launch" in c or "source" in c])
    for fam in ("enemy_wave", "enemy_wave_charge", "enemy_cone"):
        print("==", fam)
        for m in re.finditer(r'\{ marker = "([^"]+)", name = "([^"]*)", trigger = "%s",(.*?)ox = 0' % fam, s, re.S):
            for k in re.findall(r'"(wh[^"]*)"', m.group(3).split("keys = {")[1].split("}")[0]):
                a = usa[k]
                v = vx.get(a.get("vortex", ""), None)
                src = "-"
                if v is not None:
                    src = "vortex %s off=%s speed=%s dur=%s r=%s->%s n=%s" % (
                        v.get("launch_source"), v.get("launch_source_offset"), v.get("movement_speed"), v.get("duration"),
                        v.get("start_radius"), v.get("goal_radius"), v.get("num_vortexes"))
                elif a.get("activated_projectile"):
                    src = "PROJECTILE " + a["activated_projectile"]
                elif a.get("bombardment"):
                    src = "BOMBARDMENT " + a["bombardment"]
                print("  %-30s %-58s %s | type=%s stance=%s | ww=%s" % (
                    m.group(2)[:30], k, src, ua.get(k, {}).get("type", "?"), a.get("wind_up_stance") or "-", ww.get(k, "?")))


if __name__ == "__main__":
    main()
