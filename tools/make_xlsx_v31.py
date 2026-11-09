#!/usr/bin/env python3
"""Build WH3_abilities_master_v31_2026-11-09.xlsx from v30 - round 139: Stand Your Ground on the NEW
melee_or_wavering_aura (QA battle 1). melee_low_morale leaves the table (no entry), so the family count stays 59
and no Numbers row moves. v1-v30 are never opened for writing.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v30_2026-11-09.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v31_2026-11-09.xlsx"
OLD, NEW = "melee_low_morale", "melee_or_wavering_aura"
KEYS = ["wh_main_character_abilities_stand_your_ground", "wh3_dlc24_character_abilities_tacticians_stand_your_ground"]
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
TEXT = (NEW + ": not routing; the caster's is_in_melee() true, or its is_wavering() exactly true, fires at once; "
        "otherwise the CLOSEST tracked ally (alive, not the owner, not routing) that is in melee or wavering within "
        "the aura bound by unit_distance; bound: 24 m (70% of the ability's 35 m effect_range); user ruling "
        "2026-11-09 after QA battle 1: \"The general or any friendly unit within 24m is in melee or wavering.\"; cast "
        "target: self (the aura is centred on the caster; the DLC24 key uses the ground form at the caster's own "
        "position); " + SHARED_TAIL)

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
n_rows = 0
for r in range(2, ws.max_row + 1):
    if any(k in KEYS for k in keys_of(r)):
        assert str(ws.cell(row=r, column=21).value) == OLD, r
        old = str(ws.cell(row=r, column=22).value or "")
        gates = (" GATES" + old.split(" GATES", 1)[1]) if " GATES" in old else ""
        ws.cell(row=r, column=21).value = NEW
        ws.cell(row=r, column=22).value = TEXT + gates
        n_rows += 1
assert n_rows == 2, n_rows

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
assert len(trig) == 59 and trig[NEW] == 1 and trig[OLD] == 0, (len(trig), trig[NEW], trig[OLD])

n = wb["Numbers"]
assert n.cell(row=105, column=1).value == "Bombardment set (COMPLETE - round 108)"
n.cell(row=7, column=1).value = (
    "Date: 2026-11-09     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v31 - ROUND 139: Stand Your Ground on the NEW melee_or_wavering_aura after QA battle 1; melee_low_morale has no "
    "entry left. Implemented 750 rows / 750 keys and 373 not implemented, unchanged. The mod: 698 entries / 750 keys / "
    "59 trigger families.)")
n.cell(row=42, column=1).value = (
    "Trigger families after round 139 - re-counted from the mod's own ABILITIES table: 59 families / 698 entries / "
    "750 keys (metallurgy_melee and melee_low_morale keep 0 entries). Round 139: the NEW melee_or_wavering_aura (1).")
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
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v30")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v31 (2026-11-09)"
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("28. ROUND 139 - STAND YOUR GROUND AFTER QA BATTLE 1 (v31)", None),
    ("THE FINDING", "In QA battle 1 Stand Your Ground fired once, at 232 s, when the General himself was in melee and "
     "wavering (melee_low_morale); the Spearmen around him had wavered from 177 s."),
    ("THE RULING (2026-11-09)", "\"The general or any friendly unit within 24m is in melee or wavering.\""),
    ("THE NEW FAMILY: melee_or_wavering_aura", "evaluate_melee_or_wavering_aura | the caster in melee or wavering, or "
     "a friendly unit inside the 70% aura bound (24 m) in melee or wavering | cast target: self | 1 entry / 2 keys"),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-09"
ch.cell(row=r, column=2).value = "v31"
ch.cell(row=r, column=3).value = (
    "ROUND 139. QA battle 1: Stand Your Ground on the NEW melee_or_wavering_aura (the General or a friendly unit "
    "within 24 m in melee or wavering). Counts unchanged; 59 families. SHIPPED: installed pack md5 %s; harness 138 "
    "full suite 6,018 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user ruling 2026-11-09 (QA battle 1); xlsx v31 supersedes v30; v1-v30 byte-unchanged."
wb.save(DST)
print("wrote", DST)
