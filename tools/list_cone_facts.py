#!/usr/bin/env python3
"""Round 209 (read-only): the game's table values for the caster-front breaths, Lamprey's Bite and the Loons."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ww_tables as G  # noqa: E402
import gen_vortex_tables as GV  # noqa: E402

MOD = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
EXTRA = ["wh3_dlc24_unit_abilities_lampreys_bite", "wh_main_unit_abilities_spinning_loons",
         "wh_dlc06_unit_abilities_the_loons_of_eight_peaks", "wh2_dlc15_lord_abilities_da_boss_loons"]
F = ["launch_source", "launch_source_offset", "start_radius", "goal_radius", "expansion_speed", "movement_speed",
     "duration", "change_max_angle", "move_change_freq", "affects_allies", "num_vortexes", "delay", "launch_vfx"]


def main():
    src = open(MOD, encoding="utf-8").read()
    kf = G.keys_in(src)
    keys = [k for k, f in sorted(kf.items()) if f == "enemy_cone"] + EXTRA
    usa = {r["key"]: r for r in G.tsv("unit_spec_abil.tsv")}
    vx = {r["vortex_key"]: r for r in G.tsv("battle_vortexs.tsv")}
    ww = dict(x.split("=", 1) for x in re.search(r'FOURTH\.WW_TEXT = "([^"]*)"', src).group(1).split(";") if "=" in x)
    for k in keys:
        u = usa[k]
        print("==", k, "| family", kf.get(k), "| WW", ww.get(k))
        print("   range", u["target_intercept_range"], "enemies", u["target_enemies"], "ground", u["target_ground"],
              "self", u.get("target_self"), "wind_up", u.get("wind_up_time"), "uses", u.get("num_uses"))
        for v in GV.chain(vx, u["vortex"]):
            print("   vortex", v["vortex_key"], {f: v.get(f) for f in F if f in v})


if __name__ == "__main__":
    main()
