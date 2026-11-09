#!/usr/bin/env python3
"""Build WH3_abilities_master_v28_2026-11-09.xlsx from v27 - round 136: audit batch 5, the melee hexes.

(1) 20 entries move from enemy_engaged_or_shot to enemy_melee (the missile arm removed from their text).
(2) Gaze of Fate, Sadistic Snare, Spearfisher's Net move to enemy_fast_near_ally; Spearfisher's Net gains the
    not-flying target class.
(3) Counts unchanged (750 / 373), 57 families (no Numbers row moves). Definitions: title v28, section 25.
    Changelog: a v28 row. v1-v27 are never opened for writing.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import collections
import os
import re
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v27_2026-11-09.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v28_2026-11-09.xlsx"
ES, EM, FA = "enemy_engaged_or_shot", "enemy_melee", "enemy_fast_near_ally"
TO_MELEE = ["assassins_trophy", "lord_of_dragons", "beguile", "oath_of_vengeance", "ottos_scythe",
            "averland_runefang", "the_dark_master", "enfeebling_foe", "the_hammer_of_karak_drazh", "torment_blade",
            "trophy_heads", "willing_prey", "whip_of_agony", "fermented_fungi",
            "blight_swarm", "virulent_contagion", "virulent_contagion_upgraded", "dispatch_the_swarm_attack",
            "dispatch_the_swarm_attack_upgraded", "pestilent_potions"]
TO_FAST = ["gaze_of_fate", "sadistic_snare", "spearfishers_net"]
NOFLY = ("not flying (the game's flying_currently flag): is_currently_flying() read live, only an exact false "
         "passes; true, nil or a raising read = not offered")
MISSILE_ARM = "arm = is_in_melee() -> melee, else is_under_missile_attack() -> missile (unreadable = false); "
MELEE_ONLY = ("is_in_melee() must be true - the under-missile-fire arm is OFF (user ruling round 136, audit batch 5: "
              "a melee-stat hex is wasted on an enemy that is only being shot); ")

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
row_of = {}
for r in range(2, ws.max_row + 1):
    for k in keys_of(r):
        row_of.setdefault(k, []).append(r)
entries, _, _ = bd.mod_entries()
by_marker = {e["marker"]: e for e in entries}


def rows_for(marker):
    out = []
    for k in by_marker[marker]["keys"]:
        for r in row_of.get(k, []):
            if r not in out:
                out.append(r)
    assert out, marker
    return out


n_m = n_f = 0
for m in TO_MELEE:
    for r in rows_for(m):
        t = str(ws.cell(row=r, column=22).value)
        assert str(ws.cell(row=r, column=21).value) == ES and t.startswith(ES + ":") and MISSILE_ARM in t, (m, r)
        t = EM + t[len(ES):]
        t = t.replace(MISSILE_ARM, MELEE_ONLY).replace("prefer a melee arm, then the closest", "the closest wins")
        t = t.replace("still in melee or under missile fire", "still in melee")
        ws.cell(row=r, column=21).value = EM
        ws.cell(row=r, column=22).value = t
        n_m += 1
for m in TO_FAST:
    for r in rows_for(m):
        t = str(ws.cell(row=r, column=22).value)
        assert str(ws.cell(row=r, column=21).value) == ES, m
        bound = re.search(r"bound: \d+ m \(70% of the ability's \d+ m target_intercept_range\)", t).group(0)
        tail = "shared gate:" + t.split("shared gate:", 1)[1]
        cls = ("target class: " + NOFLY + "; ") if m == "spearfishers_net" else ""
        t = (FA + ": not routing; enumerate the main enemy army list; per enemy: number_of_men_alive() > 0; "
             "is_valid_target() (fallback is_valid()) must not be false - unreadable passes; is_moving() exactly true; "
             "fast_speed() (the live run speed, m/s) >= FOURTH.FAST_ENEMY_MPS = 5 (user setting); one of our units, the "
             "caster counting, within FOURTH.FAST_ENEMY_NEAR_M = 40 m of it by unit_distance (user setting; an "
             "unreadable or negative distance does not count); unit_distance from the caster <= the entry's bound; the "
             "enemy closest to our units wins; " + cls + bound + "; no charge detection (user ruling round 136: "
             "'cannot move' roots the threat before contact); cast target: that enemy unit; pre-cast re-check: the "
             "enemy must still " + ("be on the ground, " if cls else "") + "be alive, still moving at 5 m/s or more "
             "within 40 m of our units and still within the bound, else the cast is skipped; " + tail)
        ws.cell(row=r, column=21).value = FA
        ws.cell(row=r, column=22).value = t
        n_f += 1
print("rows: %d to enemy_melee, %d to enemy_fast_near_ally" % (n_m, n_f))
assert n_f == 3 and n_m >= 20, (n_m, n_f)

rows = [(r, keys_of(r), str(ws.cell(row=r, column=20).value), str(ws.cell(row=r, column=21).value))
        for r in range(2, ws.max_row + 1)]
impl = [x for x in rows if x[2] == "IMPLEMENTED"]
assert len(impl) == 750
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
assert not [x[1][0] for x in impl if x[3] != fam_by_key.get(x[1][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 57 and (trig[ES], trig[EM], trig[FA]) == (47, 34, 7), (trig[ES], trig[EM], trig[FA])

n = wb["Numbers"]
assert n.cell(row=103, column=1).value == "Bombardment set (COMPLETE - round 108)"
n.cell(row=7, column=1).value = (
    "Date: 2026-11-09     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v28 - ROUND 136: audit batch 5. 20 melee hexes move from enemy_engaged_or_shot to enemy_melee; Gaze of Fate, "
    "Sadistic Snare and Spearfisher's Net on enemy_fast_near_ally; Spearfisher's Net filtered to enemies on the ground. "
    "Implemented 750 rows / 750 keys and 373 not implemented, unchanged. The mod: 698 entries / 750 keys / 57 trigger "
    "families.)")
n.cell(row=42, column=1).value = (
    "Trigger families after round 136 - re-counted from the mod's own ABILITIES table: 57 families / 698 entries / "
    "750 keys (metallurgy_melee keeps 0 entries). Round 136: enemy_engaged_or_shot 70 -> 47, enemy_melee 14 -> 34, "
    "enemy_fast_near_ally 4 -> 7.")
for r in range(44, 102):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t]
assert 44 + len(fam_sorted) == 101
n.cell(row=101, column=2).value = "TOTAL (57 families)"
n.cell(row=101, column=3).value = sum(trig.values())
n.cell(row=101, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v27")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v28 (2026-11-09)"
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("25. ROUND 136 - AUDIT BATCH 5: THE MELEE HEXES (v28)", None),
    ("THE RULINGS (2026-11-09)", "All as recommended. The pure melee hexes (14) and the spreading melee-defence hexes "
     "(6): \"Enemy in melee\". The immobilisers (Gaze of Fate, Sadistic Snare, Spearfisher's Net): \"Fast enemy near "
     "us\". Spearfisher's Net's not-flying filter: \"Yes, add it now\"."),
    ("THE NEW TARGET CLASS", "not_flying: is_currently_flying() read live; only an exact false passes."),
    ("THE ARITHMETIC", "Implemented 750 rows / keys and 373 not implemented, unchanged. Mod 698 entries / 750 keys / "
     "57 families; enemy_engaged_or_shot 70 -> 47, enemy_melee 14 -> 34, enemy_fast_near_ally 4 -> 7."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-09"
ch.cell(row=r, column=2).value = "v28"
ch.cell(row=r, column=3).value = (
    "ROUND 136. Audit batch 5: 20 melee hexes to enemy_melee; Gaze of Fate, Sadistic Snare, Spearfisher's Net on "
    "enemy_fast_near_ally; Spearfisher's Net filtered to enemies on the ground. Counts unchanged; 57 families. "
    "SHIPPED: installed pack md5 %s; harness 135 full suite 5,901 checks / 0 failures."
    % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-09 (audit batch 5); xlsx v28 supersedes v27; v1-v27 byte-unchanged."
wb.save(DST)
print("wrote", DST)
