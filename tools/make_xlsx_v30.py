#!/usr/bin/env python3
"""Build WH3_abilities_master_v30_2026-11-09.xlsx from v29 - round 138: the rarer target filters and Missile
Mirror's shooting trigger.

(1) Eternal Gaze, Entangle, Void Pendulum, Word of Change carry their target class in the trigger text.
(2) Missile Mirror moves to the NEW enemy_missile_shooting (missile class).
(3) Counts unchanged (750 / 373); 58 -> 59 families: the Numbers trigger table gains one row (bombardment block
    104 -> 105). Definitions: title v30, glossary, section 27. Changelog: a v30 row. v1-v29 never opened for writing.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import collections
import os
import re
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v29_2026-11-09.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v30_2026-11-09.xlsx"
ES, MS = "enemy_engaged_or_shot", "enemy_missile_shooting"
CLS = {
    "wh3_dlc29_lord_abilities_gaze_of_usirian": "not undead (the game's undead_unit flag): the enemy's type() must NOT be in "
        "the GENERATED undead set (unit attribute undead); unreadable = not offered",
    "wh2_dlc10_character_abilities_entangle": "not flying (flying_currently): is_currently_flying() read live, only an "
        "exact false passes",
    "wh3_main_item_abilities_void_pendulum": "Lord/Hero only, the closest approximation of the game's hasnt_casting_ability "
        "flag (no battle read or data list can tell a spellcaster; user ruling 2026-11-09)",
    "wh3_main_daemon_head_abilities_word_of_change": "Lord/Hero only, the closest approximation of the game's "
        "hasnt_casting_ability flag (no battle read or data list can tell a spellcaster; user ruling 2026-11-09)",
}
MIR = "wh3_dlc24_unit_bound_missile_mirror"

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
row_of = {}
for r in range(2, ws.max_row + 1):
    for k in keys_of(r):
        row_of.setdefault(k, []).append(r)
for k, txt in CLS.items():
    (r,) = row_of[k]
    t = str(ws.cell(row=r, column=22).value)
    assert "; bound: " in t and "target class:" not in t, k
    t = t.replace("; bound: ", "; target class: " + txt + "; bound: ", 1)
    t = t.replace("pre-cast re-check: the enemy must still be alive,",
                  "pre-cast re-check: the enemy must still be of its target class, still be alive,", 1)
    ws.cell(row=r, column=22).value = t
(r,) = row_of[MIR]
t = str(ws.cell(row=r, column=22).value)
assert str(ws.cell(row=r, column=21).value) == ES
bound = re.search(r"bound: \d+ m \(70% of the ability's \d+ m target_intercept_range\)", t).group(0)
tail = "shared gate:" + t.split("shared gate:", 1)[1]
ws.cell(row=r, column=21).value = MS
ws.cell(row=r, column=22).value = (
    MS + ": not routing; enumerate the main enemy army list; per enemy: number_of_men_alive() > 0; is_valid_target() "
    "(fallback is_valid()) must not be false - unreadable passes; target class: missile units only (the game's "
    "is_not_missile_unit flag; the generated missile set); SHOOTING = the enemy's ammo_left() dropped between two "
    "samples no more than ENEMY_AMMO_FRESH_S = 2 s apart, and the last drop lies within max(2 x its reload, 20 s) (the "
    "firing-flag window); an unreadable enemy ammunition never fires; not in melee; unit_distance <= the entry's bound; "
    "the closest wins; " + bound + "; cast target: that enemy unit; pre-cast re-check: the enemy must still be alive, "
    "still shooting, not in melee and within the bound, else the cast is skipped; " + tail)

entries, _, _ = bd.mod_entries()
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
assert len(trig) == 59 and (trig[ES], trig[MS]) == (46, 1), (len(trig), trig[ES], trig[MS])

n = wb["Numbers"]
assert n.cell(row=104, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert all(int(str(m).split(":")[0][1:]) < 102 for m in n.merged_cells.ranges)
n.insert_rows(102, 1)
assert n.cell(row=105, column=1).value == "Bombardment set (COMPLETE - round 108)"
n.cell(row=7, column=1).value = (
    "Date: 2026-11-09     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v30 - ROUND 138: the rarer target filters (Eternal Gaze not undead, Entangle not flying, Void Pendulum and Word "
    "of Change Lords/Heroes) and Missile Mirror on the NEW enemy_missile_shooting. Implemented 750 rows / 750 keys and "
    "373 not implemented, unchanged. The mod: 698 entries / 750 keys / 59 trigger families.)")
n.cell(row=42, column=1).value = (
    "Trigger families after round 138 - re-counted from the mod's own ABILITIES table: 59 families / 698 entries / "
    "750 keys (metallurgy_melee keeps 0 entries). Round 138: the NEW enemy_missile_shooting (1); enemy_engaged_or_shot "
    "47 -> 46.")
for r in range(44, 104):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t2, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t2
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t2]
assert 44 + len(fam_sorted) == 103
n.cell(row=103, column=2).value = "TOTAL (59 families)"
n.cell(row=103, column=3).value = sum(trig.values())
n.cell(row=103, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v29")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v30 (2026-11-09)"
g = d.cell(row=21, column=1)
g.value = str(g.value) + "; the round-138 family (enemy_missile_shooting) in section 27"
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("27. ROUND 138 - THE RARER TARGET FILTERS AND MISSILE MIRROR (v30)", None),
    ("THE RULINGS (2026-11-09)", "Void Pendulum and Word of Change: \"Lords/Heroes only\". Missile Mirror: \"Missile "
     "enemy shooting\". Entangle not flying, Eternal Gaze not undead, Missile Mirror missile units only: the game's own "
     "target rules."),
    ("THE NEW FAMILY: enemy_missile_shooting", "evaluate_enemy_missile_shooting | an enemy missile unit inside the "
     "70% bound, not in melee, whose ammunition dropped between two polls within the firing-flag window | cast target: "
     "that enemy | 1 entry / 1 key"),
    ("THE NEW CLASSES", "not_undead (GENERATED undead set: 355 unit types, tools/gen_undead_keys.py from the live "
     "unit_attributes_to_groups_junctions table) and missile (the generated missile set)."),
    ("THE ARITHMETIC", "Implemented 750 rows / keys and 373 not implemented, unchanged. Mod 698 entries / 750 keys, "
     "58 -> 59 families; enemy_engaged_or_shot 47 -> 46; target classes 16 -> 21."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-09"
ch.cell(row=r, column=2).value = "v30"
ch.cell(row=r, column=3).value = (
    "ROUND 138. The rarer target filters (Eternal Gaze not undead, Entangle not flying, Void Pendulum and Word of Change "
    "Lords/Heroes) and Missile Mirror on the NEW enemy_missile_shooting (missile units only). Counts unchanged; 59 "
    "families. SHIPPED: installed pack md5 %s; harness 137 full suite 5,995 checks / 0 failures."
    % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-09; xlsx v30 supersedes v29; v1-v29 byte-unchanged."
wb.save(DST)
print("wrote", DST)
