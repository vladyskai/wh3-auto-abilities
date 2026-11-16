#!/usr/bin/env python3
"""Round 162: the WW table for the wandering-wind families (user rulings 2026-11-16), GENERATED from the game data
(CLAUDE.md rule 4: never hand-typed). One row per key:

  key=<kind>,<radius>,<path>,<offset>,<buffer>,<hits_allies>
    kind        1 = a WAVE (launch_source target_near_edge: starts <offset> m before the target, rolls <path> m along the
                caster-to-target heading); 2 = a WANDERER / static area (starts on the target centre)
    radius      the largest start_radius / goal_radius along the vortex chain (metres)
    path        movement_speed x duration of the first vortex (metres)
    offset      launch_source_offset (metres)
    buffer      the SIMULATED 95% drift (user ruling 2026-11-16: "Simulated 95%"), rounded UP to a whole metre:
                for a wave the sideways drift from its straight line, for a wanderer the distance from its start point;
                4,000 paths per reading, the wider of the two readings of change_max_angle (+-angle and +-angle/2,
                the field's meaning is not documented), a fixed per-key seed so the build can re-derive it exactly
    hits_allies 1 when any vortex of the chain has affects_allies = true

The path model: every move_change_freq seconds the heading turns by a uniform random angle; the vortex moves in a
straight line between turns, so the farthest point of each leg is one of its two ends (exact, no time step).
keys_in(script_txt) reads the keys of the script's entries on the two families; lua_block(rows) is the embedded text.
"""
import math
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamedata_paths as GP  # noqa: E402
import gen_vortex_tables as GV  # noqa: E402

FAMILIES = ("enemy_wave", "enemy_wander")
RUNS = 4000


def tsv(name):
    with open(os.path.join(GP.GAMEDATA, name), encoding="utf-8-sig") as f:
        h = f.readline().rstrip("\n").split("\t")
        f.readline()
        for line in f:
            yield dict(zip(h, line.rstrip("\n").split("\t")))


def keys_in(script_txt):
    out = {}
    for m in re.finditer(r'trigger = "(%s)",\n\t\tbadge = "[^"]+",\n\t\tkeys = \{ "([^"]+)" \}' % "|".join(FAMILIES),
                         script_txt):
        out[m.group(2)] = m.group(1)
    return out


def drift95(v, key, wave):
    """the 95% drift of one vortex row: sideways (wave) or from the start (wanderer), the wider of two readings"""
    spd, dur = float(v["movement_speed"] or 0), float(v["duration"] or 0)
    ang, freq = float(v["change_max_angle"] or 0), float(v["move_change_freq"] or 0)
    if spd <= 0 or dur <= 0:
        return 0.0
    if freq <= 0 or ang <= 0:
        # no turn: a wave stays on its line; a wanderer goes straight out (heading unknown) for its whole path
        return 0.0 if wave else spd * dur
    best = 0.0
    for lim in (ang, ang / 2.0):
        rng = random.Random("%s/%g" % (key, lim))
        vals = []
        for _ in range(RUNS):
            x = z = h = t = 0.0
            mx = 0.0
            while t < dur - 1e-9:
                leg = min(freq, dur - t)
                x += spd * leg * math.cos(h)
                z += spd * leg * math.sin(h)
                t += leg
                mx = max(mx, abs(z) if wave else math.hypot(x, z))
                if lim >= 360:
                    h = rng.uniform(0.0, 2.0 * math.pi)
                else:
                    h += math.radians(rng.uniform(-lim, lim))
            vals.append(mx)
        vals.sort()
        best = max(best, vals[int(0.95 * RUNS)])
    return best


def derive(key_fams):
    usa = {r["key"]: r for r in tsv("unit_spec_abil.tsv")}
    vx = {r["vortex_key"]: r for r in tsv("battle_vortexs.tsv")}
    out = {}
    for k, fam in sorted(key_fams.items()):
        rows = GV.chain(vx, usa[k]["vortex"])
        assert rows, "%s has no vortex" % k
        v = rows[0]
        wave = (fam == "enemy_wave")
        # a wave must launch from the target's near edge; a wanderer may too (The Ruination of Cities: three spokes from
        # the near edge, offset 0, no turn, so its buffer is its whole path)
        assert (not wave) or v["launch_source"] == "target_near_edge", "%s: wave launched from %s" % (k, v["launch_source"])
        r = max(max(float(x["start_radius"] or 0), float(x["goal_radius"] or 0)) for x in rows)
        path = float(v["movement_speed"] or 0) * float(v["duration"] or 0)
        off = float(v["launch_source_offset"] or 0)
        buf = int(math.ceil(drift95(v, k, wave) - 1e-9))
        allies = 1 if any(x["affects_allies"] == "true" for x in rows) else 0
        kind = 1 if wave else (3 if v["launch_source"] == "target_near_edge" else 2)
        ground = 1 if (usa[k]["target_enemies"] != "true" and usa[k]["target_ground"] == "true") else 0
        out[k] = (kind, r, path, off, buf, allies, ground)
    return out


def fmt(v):
    return ("%.3f" % v).rstrip("0").rstrip(".")


def lua_block(rows):
    t = ";".join("%s=%d,%s,%s,%s,%d,%d,%d" % (k, a, fmt(r), fmt(p), fmt(o), b, h, g)
                 for k, (a, r, p, o, b, h, g) in sorted(rows.items()))
    return ("-- GENERATED by tools/gen_ww_tables.py from unit_spec_abil and battle_vortexs (the simulated 95%% drift; the\n"
            "-- build refuses a pack whose table differs from the game data). Do not hand-edit.\n"
            "-- key=kind,radius,path,offset,buffer,hits_allies,ground_only; kind 1 wave, 2 wanderer from the target centre,\n"
            "-- 3 wanderer from the target's near edge\n"
            "FOURTH.WW_TEXT = \"%s\"\n"
            "FOURTH.WW = {}\n"
            "function FOURTH.load_ww_table()   -- a function, so the loop adds no main-chunk locals\n"
            "\tfor k, a, r, p, o, b, h, g in string.gmatch(FOURTH.WW_TEXT,\n"
            "\t\t\"([^;=]+)=(%%d),([%%d%%.]+),([%%d%%.]+),([%%d%%.]+),(%%d+),(%%d),(%%d)\") do\n"
            "\t\tFOURTH.WW[k] = { kind = tonumber(a), r = tonumber(r), path = tonumber(p), off = tonumber(o), buf = tonumber(b),\n"
            "\t\t\tallies = (h == \"1\"), ground = (g == \"1\") }\n"
            "\tend\n"
            "end\n"
            "FOURTH.load_ww_table()\n" % t)


if __name__ == "__main__":
    src = open(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua",
               encoding="utf-8").read()
    kf = keys_in(src)
    print(len(kf), "keys on the families")
    for k, v in sorted(derive(kf).items()):
        print(k, v)
