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
    return sorted(k for k in keys if usa[k].get("wind_up_stance", "").strip())


def text(keys):
    return ";".join(keys)


if __name__ == "__main__":
    src = open(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua",
               encoding="utf-8").read()
    k = derive(src)
    print(len(k), "of", len(mod_keys(src)), "mod keys play a cast animation")
