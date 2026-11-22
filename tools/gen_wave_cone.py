#!/usr/bin/env python3
"""Round 205: the CONE table of the straight waves, GENERATED from the game data (CLAUDE.md rule 4: never hand-typed).

A wave whose vortex starts narrower than it ends grows as it rolls: battle_vortexs.start_radius -> goal_radius at
expansion_speed metres per second, while it moves at movement_speed metres per second. Its radius d metres from its
start is  min(goal_radius, start_radius + (expansion_speed / movement_speed) x d).

  FOURTH.WW_CONE_TEXT "key=start_radius,growth_per_metre;..."   for every enemy_wave key whose vortex grows

  derive(script_txt) -> {key: (r0, growth per metre)}
  text(rows)         -> the string embedded in the mod

    python tools/gen_wave_cone.py            # print the text and the rows
"""
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamedata_paths as GP  # noqa: E402

MOD = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"


def _table(name):
    with open(os.path.join(GP.GAMEDATA, name), encoding="utf-8-sig") as f:
        rows = list(csv.reader(f, delimiter="\t"))
    return {r[0]: dict(zip(rows[0], r)) for r in rows[2:] if r}


def derive(script_txt):
    usa, vx = _table("unit_spec_abil.tsv"), _table("battle_vortexs.tsv")
    ww = dict(x.split("=", 1) for x in re.search(r'FOURTH\.WW_TEXT = "([^"]*)"', script_txt).group(1).split(";") if "=" in x)
    out = {}
    # ROUND 210 (user test 2026-11-22: Skabscrath "always starts at the caster"): the breaths from the caster's front
    # (enemy_cone) grow the same way, from the caster on
    for m in re.finditer(r'\{ marker = "([^"]+)", name = "[^"]*", trigger = "enemy_(?:wave|cone)",(.*?)ox = 0', script_txt, re.S):
        for k in re.findall(r'"(wh[^"]*)"', m.group(2).split("keys = {")[1].split("}")[0]):
            v = vx[usa[k]["vortex"]]
            r0, r1 = float(v["start_radius"]), float(v["goal_radius"])
            exp, spd, dur = float(v["expansion_speed"]), float(v["movement_speed"]), float(v["duration"])
            # only a wave whose table radius IS the vortex's goal radius (Hell Hammer's 14.1 m is its bombardment's)
            wwr = float(ww[k].split(",")[1])
            if r0 < r1 and exp > 0 and spd > 0 and abs(wwr - r1) < 0.01:
                g = exp / spd
                # the cone must reach (about) its goal radius by the end of its path, or the table is misread
                assert abs(min(r1, r0 + g * spd * dur) - r1) <= 0.5, (k, r0, r1, exp, spd, dur)
                out[k] = (r0, g)
            elif r0 < r1 and exp > 0 and spd > 0 and abs(wwr - (r0 + exp * dur)) < 0.01:
                # ROUND 209: a wave that stops growing before its goal radius (Lamprey's Bite): the WW table carries
                # the radius it reaches, the cone grows to exactly that
                out[k] = (r0, exp / spd)
    return out


def _num(x):
    s = "%.4f" % x
    return s.rstrip("0").rstrip(".") if "." in s else s


def text(rows):
    return ";".join("%s=%s,%s" % (k, _num(rows[k][0]), _num(rows[k][1])) for k in sorted(rows))


if __name__ == "__main__":
    rows = derive(open(MOD, encoding="utf-8").read())
    print(text(rows))
    print(len(rows), "growing waves")
