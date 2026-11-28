#!/usr/bin/env python3
"""Round 168: the ANIM set, GENERATED from the game data (CLAUDE.md rule 4: never hand-typed).

User ruling 2026-11-17 ("Option A, animation decides all"): a cast stops its moving caster only when the ability plays a
cast animation, unit_special_abilities.wind_up_stance not empty. Field evidence, 4 of 4: Volley of High Arrows and
Soporific Breath (cast_forward_short) stopped their casters; Book of Hoeth and Gaze of Malice (no stance) did not.
The mod's stand-still gate (FOURTH.blob_still) now applies only to an entry with a key in this set.

  derive(script_txt) -> sorted mod keys whose wind_up_stance is not empty
  text(keys)         -> "key;key;..." (the one string embedded in the mod)
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamedata_paths as GP  # noqa: E402


def tsv(path):
    with open(path, encoding="utf-8-sig") as f:
        h = f.readline().rstrip("\n").split("\t")
        f.readline()
        for line in f:
            yield dict(zip(h, line.rstrip("\n").split("\t")))


def mod_keys(script_txt):
    body = script_txt.split("\nlocal ABILITIES = {", 1)[1].split("\n}\n", 1)[0]
    out = set()
    for m in re.finditer(r"keys = \{([^}]*)\}", body):
        out.update(re.findall(r'"([^"]+)"', m.group(1)))
    return out


def derive(script_txt):
    keys = mod_keys(script_txt)
    usa = {r["key"]: r for r in tsv(os.path.join(GP.GAMEDATA, "unit_spec_abil.tsv"))}
    missing = sorted(k for k in keys if k not in usa)
    assert not missing, "mod keys missing from unit_special_abilities: %s" % missing[:5]
    return sorted(k for k in keys if usa[k].get("wind_up_stance", "").strip() and not placed(usa[k]))


def placed(row):
    """ROUND 220 (user ruling 2026-11-28, after his Brass Orb test: 'it didn't stop the unit when I cast', and 'Yes' to
    'all placed ones'): an effect PLACED at its target (a vortex, with no projectile shot by the caster and no
    bombardment) does not stop its caster, cast animation or not. Field: Brass Orb (cast_forward_medium, a vortex)
    did not stop a Warlock Master (archive/logs/battle_20261128_r219_perf.txt, t = 62 s), Amber Bow (the SAME stance,
    a projectile) stopped Markus Wulfhart, Gaze of Malice (a vortex) did not stop its caster."""
    return bool(row.get("vortex", "").strip()) and not row.get("activated_projectile", "").strip() \
        and not row.get("bombardment", "").strip()


def placed_keys(script_txt):
    """the mod keys round 220 took out of the ANIM set: a cast animation AND a placed effect"""
    keys = mod_keys(script_txt)
    usa = {r["key"]: r for r in tsv(os.path.join(GP.GAMEDATA, "unit_spec_abil.tsv"))}
    return sorted(k for k in keys if usa[k].get("wind_up_stance", "").strip() and placed(usa[k]))


def text(keys):
    return ";".join(keys)


if __name__ == "__main__":
    src = open(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua",
               encoding="utf-8").read()
    k = derive(src)
    print(len(k), "of", len(mod_keys(src)), "mod keys play a cast animation")
