#!/usr/bin/env python3
"""Round 167: the RISKY set, GENERATED from the game data (CLAUDE.md rule 4: never hand-typed).

User ruling 2026-11-17 (the overnight audit's feature 8, "Safer defaults for Rampage and self-damage abilities"): an
ability that makes OUR unit rampage, or damages the caster itself, starts on M even when its family starts armed.

  RAMPAGE      a phase of the ability carries the attribute 'rampage' with attribute_type 'positive'
               (special_ability_phase_attribute_effects) and is applied to the caster or its allies
               (special_ability_to_phases junction: target_self or target_friends true).
  SELF-DAMAGE  a phase applied to the caster (target_self true) deals damage (phases.damage_amount > 0) and is not
               marked enemy-only (phases.affects_enemies true with affects_allies false is an enemy-only effect).

  derive(script_txt) -> {key: "R" | "D" | "RD"} for the mod's keys
  text(rows)         -> "key=R;key=D;..." (the one string embedded in the mod)
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
    g = GP.GAMEDATA
    ramp = {r["phase"] for r in tsv(os.path.join(g, "uieff", "phase_attribute_effects.tsv"))
            if r["attribute"] == "rampage" and r["attribute_type"] == "positive"}
    ph = {r["id"]: r for r in tsv(os.path.join(g, "phases.tsv"))}
    keys = mod_keys(script_txt)
    out = {}
    for r in tsv(os.path.join(g, "phase_junc.tsv")):
        k = r["special_ability"]
        if k not in keys:
            continue
        p = r["phase"]
        flag = out.get(k, "")
        if p in ramp and (r["target_self"] == "true" or r["target_friends"] == "true") and "R" not in flag:
            flag += "R"
        row = ph.get(p, {})
        try:
            dmg = float(row.get("damage_amount") or 0)
        except ValueError:
            dmg = 0
        enemy_only = row.get("affects_enemies") == "true" and row.get("affects_allies") != "true"
        if r["target_self"] == "true" and dmg > 0 and not enemy_only and "D" not in flag:
            flag += "D"
        if flag:
            out[k] = flag
    return out


def text(rows):
    return ";".join("%s=%s" % (k, rows[k]) for k in sorted(rows))


if __name__ == "__main__":
    src = open(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua",
               encoding="utf-8").read()
    rows = derive(src)
    print(len(rows), "risky keys")
    for k in sorted(rows):
        print("  ", rows[k], k)
