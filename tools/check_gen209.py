#!/usr/bin/env python3
"""Round 209 (read-only): what the changed generators answer before and after Lamprey's Bite moves to enemy_wave."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ww_tables as G  # noqa: E402
import gen_wave_cone as GC  # noqa: E402

MOD = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
LAMP = "wh3_dlc24_unit_abilities_lampreys_bite"


def rows_of(block):
    return dict(x.split("=", 1) for x in re.search(r'FOURTH\.WW_TEXT = "([^"]*)"', block).group(1).split(";"))


def main():
    s = open(MOD, encoding="utf-8").read()
    kf = G.keys_in(s)
    print(len(kf), "keys; the table in the script equals the generator:", G.lua_block(G.derive(kf)) in s)
    old = rows_of(s)
    kf[LAMP] = "enemy_wave"
    new = rows_of(G.lua_block(G.derive(kf)))
    print("changed rows:", [(k, old.get(k), new[k]) for k in new if old.get(k) != new[k]])
    print("ring:", G.ring_rows(["wh_main_unit_abilities_spinning_loons", "wh_dlc06_unit_abilities_the_loons_of_eight_peaks"]))
    print("cones now:", len(GC.derive(s)))


if __name__ == "__main__":
    main()
