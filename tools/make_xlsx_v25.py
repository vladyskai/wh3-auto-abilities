#!/usr/bin/env python3
"""Build WH3_abilities_master_v25_2026-11-08.xlsx from v24 - round 133: audit batch 2, protection
against shots fires when under fire.

(1) 7 rows move to under_fire (3) or melee_or_under_fire (4) with the evaluator's own checks; each
    keeps its GATES clause.
(2) Counts unchanged (752 implemented, 371 not implemented; 700 entries / 752 keys); 54 -> 56 families.
(3) Numbers: the trigger table grows to 56 rows (2 rows inserted above the bombardment block).
    Definitions: title v25, glossary counts, section 22. Changelog: a v25 row.
v1-v24 are never opened for writing.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v24_2026-11-08.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v25_2026-11-08.xlsx"
UF, MUF, MU = "under_fire", "melee_or_under_fire", "melee_unwavering"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")


def uf_text(aura):
    a = ("; otherwise the CLOSEST tracked ally alive, not the owner, not routing, under missile fire and within the "
         "aura bound by unit_distance; bound: %d m (70%% of the ability's %d m effect_range)" % aura) if aura else ""
    return ("under_fire: not routing; is_under_missile_attack() on the caster exactly true (unreadable or raising = "
            "false)" + a + "; cast target: self; " + SHARED_TAIL)


def muf_text(aura):
    a = ("; otherwise the CLOSEST tracked ally alive, not the owner, not routing, in melee or under missile fire and "
         "within the aura bound by unit_distance; bound: %d m (70%% of the ability's %d m effect_range)" % aura) if aura else ""
    return ("melee_or_under_fire: not routing; is_in_melee() with is_wavering() not true (fail-open morale) fires at "
            "once; otherwise is_under_missile_attack() on the caster exactly true" + a + "; cast target: self; " + SHARED_TAIL)


TEXT = {
    "wh2_dlc12_unit_abilities_shield_of_chaqua": (UF, uf_text((38, 55))),
    "wh3_dlc24_item_abilities_the_golden_eye_of_tzeentch": (UF, uf_text(None)),
    "wh_dlc07_lord_abilities_lions_shield": (UF, uf_text(None)),
    "wh3_dlc24_item_abilities_blessed_helm_of_the_oblast": (MUF, muf_text((24, 35))),
    "wh2_main_item_abilities_the_bane_shield": (MUF, muf_text((24, 35))),
    "wh_main_weapon_abilities_charmed_shield": (MUF, muf_text(None)),
    "wh3_twa08_unit_abilities_glacial_defence": (MUF, muf_text(None)),
}

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
row_of = {}
for r in range(2, ws.max_row + 1):
    for k in keys_of(r):
        row_of.setdefault(k, []).append(r)
for key, (fam, text) in TEXT.items():
    rs = row_of.get(key, [])
    assert len(rs) == 1 and keys_of(rs[0]) == [key], (key, rs)
    r = rs[0]
    assert str(ws.cell(row=r, column=20).value) == "IMPLEMENTED" and str(ws.cell(row=r, column=21).value) == MU, key
    old = str(ws.cell(row=r, column=22).value or "")
    gates = (" GATES" + old.split(" GATES", 1)[1]) if " GATES" in old else ""
    ws.cell(row=r, column=21).value = fam
    ws.cell(row=r, column=22).value = text + gates
print("rows retriggered:", len(TEXT))

rows = [(keys_of(r), str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=20).value),
         str(ws.cell(row=r, column=21).value)) for r in range(2, ws.max_row + 1)]
assert len(rows) == 1800
assert collections.Counter(x[1] for x in rows) == {"IN-WHEEL": 1123, "EXCLUDED": 677}
impl = [x for x in rows if x[2] == "IMPLEMENTED"]
assert len(impl) == 752 and len(set(k for x in impl for k in x[0])) == 752
entries, _, _ = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
assert (len(entries), len(fam_by_key)) == (700, 752)
assert not [x[0][0] for x in impl if x[3] != fam_by_key.get(x[0][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 56 and (trig[MU], trig[UF], trig[MUF]) == (342, 3, 4), (len(trig), trig[MU])

n = wb["Numbers"]
assert n.cell(row=100, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert all(int(str(m).split(":")[0][1:]) < 99 for m in n.merged_cells.ranges)
n.insert_rows(99, 2)
assert n.cell(row=102, column=1).value == "Bombardment set (COMPLETE - round 108)"
n.cell(row=7, column=1).value = (
    "Date: 2026-11-08     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v25 - ROUND 133: audit batch 2. Shield of Chaqua, The Golden Eye of Tzeentch and The Lion's Shield on the NEW "
    "under_fire; The Blessed Helm of the Oblast, The Bane Shield, Charmed Shield and Glacial Defence on the NEW "
    "melee_or_under_fire. Implemented 752 rows / 752 keys and 371 not implemented, unchanged. The mod: 700 entries / "
    "752 keys / 56 trigger families.)")
n.cell(row=42, column=1).value = (
    "Trigger families after round 133 - re-counted from the mod's own ABILITIES table: 56 families / 700 entries / "
    "752 keys (metallurgy_melee keeps 0 entries). Round 133: the NEW under_fire (3) and melee_or_under_fire (4); "
    "melee_unwavering 349 -> 342.")
for r in range(44, 101):
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
assert tot_row == 100, tot_row
n.cell(row=tot_row, column=2).value = "TOTAL (56 families)"
n.cell(row=tot_row, column=3).value = sum(trig.values())
n.cell(row=tot_row, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v24")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v25 (2026-11-08)"
g = d.cell(row=21, column=1)
g.value = str(g.value) + "; the two round-133 families (under_fire, melee_or_under_fire) in section 22"
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("22. ROUND 133 - AUDIT BATCH 2: PROTECTION AGAINST SHOTS (v25)", None),
    ("THE RULINGS (2026-11-08)", "Both as recommended: pure missile protection (Shield of Chaqua, The Golden Eye of "
     "Tzeentch, The Lion's Shield) \"When under fire\"; mixed protection (The Blessed Helm of the Oblast, The Bane "
     "Shield, Charmed Shield, Glacial Defence) \"In melee or under fire\"."),
    ("THE NEW FAMILY: under_fire", "evaluate_under_fire | the caster under missile fire; for an aura also any unit "
     "within the bound | cast target: self | 3 entries / 3 keys"),
    ("THE NEW FAMILY: melee_or_under_fire", "evaluate_melee_or_under_fire | the caster in melee (not wavering) or under "
     "fire; for an aura also any unit within the bound in melee or under fire | cast target: self | 4 entries / 4 keys"),
    ("THE READ", "battle_unit:is_under_missile_attack(), only an exact true counts. Never yet seen on the player's own "
     "units in a real battle: the QA battle is its first field proof."),
    ("THE ARITHMETIC", "Implemented 752 rows = 752 keys and 371 not implemented, unchanged. Mod 700 entries / 752 keys, "
     "54 -> 56 families, melee_unwavering 349 -> 342. Harness 132 full suite: 5,738 checks / 0 failures, run twice "
     "byte-identical."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-08"
ch.cell(row=r, column=2).value = "v25"
ch.cell(row=r, column=3).value = (
    "ROUND 133. Audit batch 2: Shield of Chaqua, The Golden Eye of Tzeentch, The Lion's Shield on the NEW under_fire; "
    "The Blessed Helm of the Oblast, The Bane Shield, Charmed Shield, Glacial Defence on the NEW melee_or_under_fire. "
    "Counts unchanged; 56 families. SHIPPED: installed pack md5 %s; harness 132 full suite 5,738 checks / 0 failures."
    % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-08 (audit batch 2); xlsx v25 supersedes v24; v1-v24 byte-unchanged."
wb.save(DST)
print("wrote", DST, "families", len(trig))
