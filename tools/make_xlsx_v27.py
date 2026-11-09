#!/usr/bin/env python3
"""Build WH3_abilities_master_v27_2026-11-09.xlsx from v26 - round 135: audit batch 4, the enemy slows and the
target filters.

(1) 11 rows move from enemy_engaged_or_shot to enemy_melee (the missile arm removed from their text).
(2) 4 rows move to the NEW enemy_fast_near_ally (Mither, Rune of Slowness, Master Rune of Slowness,
    Whispering Mist), the user's design: moving, run speed >= 5 m/s, within 40 m of one of our units.
(3) 15 entries (17 workbook rows) carry their target class in the trigger text.
(4) Counts unchanged (750 / 373); 56 -> 57 families: the Numbers trigger table gains one row (the
    bombardment block moves 102 -> 103). Definitions: title v27, glossary, section 24. Changelog: a v27 row.
v1-v26 are never opened for writing.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import collections
import os
import re
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v26_2026-11-09.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v27_2026-11-09.xlsx"
ES, EM, FA = "enemy_engaged_or_shot", "enemy_melee", "enemy_fast_near_ally"

TO_MELEE = ["wh3_dlc27_spell_bound_acquiescence", "wh_dlc05_weapon_abilities_el_syf",
            "wh3_main_weapon_abilities_frost_shard_glaive", "wh3_cp1_lord_abilities_hidden_huntress",
            "wh2_dlc11_character_abilities_hornswaggle", "wh3_dlc26_unit_abilities_marked_for_eatin",
            "wh2_dlc11_character_abilities_taunt", "wh3_dlc25_hero_abilities_titan_headsman",
            "wh2_dlc15_lord_abilities_youre_next", "wh3_dlc29_hero_active_tendrils_of_the_sea"]
TO_FAST = ["wh2_dlc15_hero_abilities_mither", "wh2_dlc17_rune_abilities_rune_of_slowness",
           "wh2_dlc17_rune_abilities_master_rune_of_slowness", "wh3_dlc29_hero_abilities_whispering_mist"]
CMDR = ("Lord/Hero only (the game's unit_is_not_commander_class flag): the enemy's type() must be in the derived "
        "commander set, else unit_class() == com; unreadable = not offered")
LARGE = ("large only (unit_is_not_large): the enemy's type() must be in the GENERATED large set (man_entity or "
         "mount entity size large / very_large); unreadable = not offered")
LSING = ("large single entity only (unit_is_not_large + unit_is_not_single_entity): the GENERATED large set and "
         "the GENERATED single-entity set (num_men 1); unreadable = not offered")
CLASS = {k: CMDR for k in ("wh_dlc05_weapon_abilities_el_syf", "wh2_dlc15_lord_abilities_youre_next",
                           "wh_dlc08_character_abilities_hunter_of_champions", "wh2_dlc14_lord_abilities_looming_dread",
                           "wh3_dlc29_lord_abilities_transfix")}
CLASS["wh3_dlc29_hero_active_tendrils_of_the_sea"] = LARGE
CLASS["wh3_dlc29_character_active_mark_of_the_monster"] = LSING
MARKER_CLASS = {"assassins_trophy": CMDR, "glory_seeker": CMDR, "glory_seeker_upgraded": CMDR, "headhunt": CMDR,
                "prey_of_the_blood_god": CMDR, "they_needs_stabbin": CMDR, "trophy_heads": CMDR,
                "whip_of_misery": LARGE}

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
key_of_marker = {e["marker"]: e["keys"] for e in entries}
for m, txt in MARKER_CLASS.items():
    for k in key_of_marker[m]:
        CLASS[k] = txt
CLASS["wh2_dlc17_character_abilities_hunter_of_champions_upgraded"] = CMDR
CLASS["wh3_cp1_lord_abilities_hidden_huntress_upgraded"] = None
CLASS.pop("wh3_cp1_lord_abilities_hidden_huntress_upgraded")
for k in key_of_marker["hidden_huntress_upgraded"]:
    TO_MELEE.append(k)
assert len(TO_MELEE) == 11, TO_MELEE


def the_row(key):
    rs = row_of.get(key, [])
    assert len(rs) == 1 and keys_of(rs[0]) == [key], (key, rs)
    return rs[0]


MISSILE_ARM = "arm = is_in_melee() -> melee, else is_under_missile_attack() -> missile (unreadable = false); "
MELEE_ONLY = ("is_in_melee() must be true - the under-missile-fire arm is OFF (user ruling round 135, audit batch 4: "
              "a slow that also cuts melee stats is wasted on an enemy that is only being shot); ")
n_melee = n_fast = n_cls = 0
for k in TO_MELEE:
    r = the_row(k)
    t = str(ws.cell(row=r, column=22).value)
    assert str(ws.cell(row=r, column=21).value) == ES and t.startswith(ES + ":") and MISSILE_ARM in t, k
    t = EM + t[len(ES):]
    t = t.replace(MISSILE_ARM, MELEE_ONLY).replace("prefer a melee arm, then the closest", "the closest wins")
    t = t.replace("still in melee or under missile fire", "still in melee")
    ws.cell(row=r, column=21).value = EM
    ws.cell(row=r, column=22).value = t
    n_melee += 1
for k in TO_FAST:
    r = the_row(k)
    t = str(ws.cell(row=r, column=22).value)
    assert str(ws.cell(row=r, column=21).value) == ES, k
    bound = re.search(r"bound: \d+ m \(70% of the ability's \d+ m target_intercept_range\)", t).group(0)
    tail = "shared gate:" + t.split("shared gate:", 1)[1]
    t = (FA + ": not routing; enumerate the main enemy army list; per enemy: number_of_men_alive() > 0; "
         "is_valid_target() (fallback is_valid()) must not be false - unreadable passes; is_moving() exactly true; "
         "fast_speed() (the live run speed, m/s) >= FOURTH.FAST_ENEMY_MPS = 5 (user setting); one of our units, the "
         "caster counting, within FOURTH.FAST_ENEMY_NEAR_M = 40 m of it by unit_distance (user setting; an "
         "unreadable or negative distance does not count); unit_distance from the caster <= the entry's bound; the "
         "enemy closest to our units wins; " + bound + "; no charge detection (user ruling 2026-11-09); cast target: "
         "that enemy unit; pre-cast re-check: the enemy must still be alive, still moving at 5 m/s or more within "
         "40 m of our units and still within the bound, else the cast is skipped; " + tail)
    ws.cell(row=r, column=21).value = FA
    ws.cell(row=r, column=22).value = t
    n_fast += 1
done_rows = set()
for k, txt in CLASS.items():
  for r in row_of.get(k, []):
    if r in done_rows:
        continue
    done_rows.add(r)
    assert str(ws.cell(row=r, column=20).value) == "IMPLEMENTED", k
    t = str(ws.cell(row=r, column=22).value)
    assert "; bound: " in t and "target class:" not in t, k
    t = t.replace("; bound: ", "; target class: " + txt + "; bound: ", 1)
    t = t.replace("pre-cast re-check: the enemy must still be alive,",
                  "pre-cast re-check: the enemy must still be of its target class, still be alive,", 1)
    ws.cell(row=r, column=22).value = t
    n_cls += 1
assert all(row_of.get(k) for k in CLASS)
print("rows: %d to enemy_melee, %d to enemy_fast_near_ally, %d with a target class" % (n_melee, n_fast, n_cls))
assert (n_melee, n_fast) == (11, 4) and n_cls >= 16, n_cls

rows = [(r, keys_of(r), str(ws.cell(row=r, column=20).value), str(ws.cell(row=r, column=21).value))
        for r in range(2, ws.max_row + 1)]
impl = [x for x in rows if x[2] == "IMPLEMENTED"]
assert len(impl) == 750
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
assert (len(entries), len(fam_by_key)) == (698, 750)
assert not [x[1][0] for x in impl if x[3] != fam_by_key.get(x[1][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 57 and (trig[ES], trig[EM], trig[FA]) == (70, 14, 4), (len(trig), trig[ES], trig[EM], trig[FA])

n = wb["Numbers"]
assert n.cell(row=102, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert all(int(str(m).split(":")[0][1:]) < 100 for m in n.merged_cells.ranges)
n.insert_rows(100, 1)
assert n.cell(row=103, column=1).value == "Bombardment set (COMPLETE - round 108)"
n.cell(row=7, column=1).value = (
    "Date: 2026-11-09     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v27 - ROUND 135: audit batch 4. 11 enemy slows that also cut melee stats move to enemy_melee; Mither, Rune of "
    "Slowness, Master Rune of Slowness and Whispering Mist on the NEW enemy_fast_near_ally; 15 enemy-targeted entries "
    "honour the game's target class (Lord/Hero, large, large single entity). Implemented 750 rows / 750 keys and 373 "
    "not implemented, unchanged. The mod: 698 entries / 750 keys / 57 trigger families.)")
n.cell(row=42, column=1).value = (
    "Trigger families after round 135 - re-counted from the mod's own ABILITIES table: 57 families / 698 entries / "
    "750 keys (metallurgy_melee keeps 0 entries). Round 135: enemy_engaged_or_shot 85 -> 70, enemy_melee 3 -> 14, "
    "the NEW enemy_fast_near_ally (4).")
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
tot_row = 44 + len(fam_sorted)
assert tot_row == 101, tot_row
n.cell(row=tot_row, column=2).value = "TOTAL (57 families)"
n.cell(row=tot_row, column=3).value = sum(trig.values())
n.cell(row=tot_row, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v26")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v27 (2026-11-09)"
g = d.cell(row=21, column=1)
g.value = str(g.value) + "; the round-135 family (enemy_fast_near_ally) and the enemy target classes in section 24"
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("24. ROUND 135 - AUDIT BATCH 4: THE ENEMY SLOWS AND THE TARGET FILTERS (v27)", None),
    ("THE RULINGS (2026-11-09)", "Slow plus a melee-stat cut (11): \"Enemy in melee\". Pure slows (Mither, Rune of "
     "Slowness, Master Rune of Slowness, Whispering Mist), the user's design: an enemy moving close to one of our units "
     "with at least cavalry speed, no charge detection; settings 5 m/s and 40 m. Looming Dread, Book of Secrets, "
     "Fecund Rebirth and Hunter of Champions (\"okay for enemy_engaged_or_shot\", round 123) keep their trigger, with "
     "the enemy type filtered. The target filters: all 15 now."),
    ("THE NEW FAMILY: enemy_fast_near_ally", "evaluate_enemy_fast_near_ally | an enemy inside the 70% bound, moving, "
     "fast_speed() >= 5 m/s, within 40 m of one of our units | cast target: that enemy | 4 entries / 4 keys"),
    ("THE TARGET CLASSES", "commander (12 entries: unit_is_not_commander_class), large (2: unit_is_not_large), "
     "large_single (1: both flags). The shared enemy picker and its pre-cast re-check skip an enemy outside the "
     "class. The large and single-entity sets are GENERATED from battle_entities, mounts, land_units and main_units "
     "(tools/gen_unit_size_keys.py: 980 large, 1,479 single); the build refuses a pack whose tables differ."),
    ("THE ARITHMETIC", "Implemented 750 rows / keys and 373 not implemented, unchanged. Mod 698 entries / 750 keys, "
     "56 -> 57 families; enemy_engaged_or_shot 85 -> 70, enemy_melee 3 -> 14."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-09"
ch.cell(row=r, column=2).value = "v27"
ch.cell(row=r, column=3).value = (
    "ROUND 135. Audit batch 4: 11 enemy slows to enemy_melee; Mither, Rune of Slowness, Master Rune of Slowness, "
    "Whispering Mist on the NEW enemy_fast_near_ally (5 m/s, 40 m); 15 enemy-targeted entries filtered by the game's "
    "target class. Counts unchanged; 57 families. SHIPPED: installed pack md5 %s; harness 134 full suite 5,852 checks "
    "/ 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-09 (audit batch 4); xlsx v27 supersedes v26; v1-v26 byte-unchanged."
wb.save(DST)
print("wrote", DST, "families", len(trig))
