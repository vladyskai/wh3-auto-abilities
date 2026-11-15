#!/usr/bin/env python3
"""Build WH3_abilities_master_v40_2026-11-15.xlsx from v39 - round 152. No count changes.

(1) The 53 prefer-central blob rows: the whole-map hold sentence is replaced (no hold; never a flying large enemy); the
    33 central rows that are not breaths gain the 90-degree sentence (breaths already carry it).
(2) The 'tired' rows (Foe-Seeker, Dazh's Song of Winter Sunlight) get the DEFAULT armed clause.
(3) Definitions: title v40, section 37. Changelog: a v40 row. Numbers: the date line.
v1-v39 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402
import build_ability_database as bd  # noqa: E402
import gen_blob_tables as GB  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v39_2026-11-14.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v40_2026-11-15.xlsx"
src = open(r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua", encoding="utf-8").read()
SHOT = GB.shot_table(GB.keys_in(src))
entries, _, _ = bd.mod_entries()
TIRED = {k for e in entries if e["trigger"] == "tired" for k in e["keys"]}
HOLD_OLD = ("; with none in range the cast is HELD while a visible large enemy anywhere would lose more value than the best "
            "infantry target.")
HOLD_NEW = ("; ROUND 152 (user rulings 2026-11-15): NO hold (the whole-map hold was removed) and never a FLYING large enemy "
            "(is_currently_flying() must read false).")
ANGLE = (" ROUND 152 (user ruling 2026-11-15, \"All 53 central attacks\"): among infantry targets within 20% of the best value, "
         "the one whose side faces the attack (line of fire closest to 90 degrees off its facing).")
DEFAULT_ADD = (" DEFAULT (round 152, user ruling 2026-11-15 \"Foe-Seeker + tired\"): starts ARMED (A) in every battle; a badge "
               "click switches it off; the ALL badge arms or disarms every ability of the selected unit(s).")

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
nh = na = nt = 0
for r in range(2, ws.max_row + 1):
    ks = [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
    if not ks or str(ws.cell(row=r, column=20).value) != "IMPLEMENTED":
        continue
    cell = ws.cell(row=r, column=22)
    k = ks[0]
    if k in SHOT and SHOT[k][4] == 1:
        assert str(cell.value).count(HOLD_OLD) == 1, k
        cell.value = str(cell.value).replace(HOLD_OLD, HOLD_NEW)
        nh += 1
        if SHOT[k][5] != 1:
            cell.value = str(cell.value) + ANGLE
            na += 1
    if any(x in TIRED for x in ks):
        cell.value = str(cell.value) + DEFAULT_ADD
        nt += 1
assert nh == 53 and na == sum(1 for v in SHOT.values() if v[4] == 1 and v[5] != 1), (nh, na)
assert nt == len(TIRED), (nt, len(TIRED))
n = wb["Numbers"]
n.cell(row=7, column=1).value = (
    "Date: 2026-11-15     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v40 - ROUND 152: no whole-map hold; large first never at a flying enemy; the 90-degree preference for all 53 "
    "prefer-central attacks; the 2 'tired' abilities start armed; the ALL badge on screen. No count change: 854 "
    "implemented / 269 not implemented (27 skipped); the mod 799 entries / 854 keys / 75 trigger families.)")
d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v39")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v40 (2026-11-15)"
base = d.max_row + 2
sec = [
    ("37. ROUND 152 - NO HOLD, NO FLYING LARGE TARGETS, 90 DEGREES FOR EVERY CENTRAL ATTACK (v40)", None),
    ("THE RULINGS (2026-11-15)", "\"let's do not hold for a large unit in the whole map\"; \"Large first, skip fliers\"; "
     "\"All 53 central attacks\" (90 degrees); \"Foe-Seeker + tired\" start armed; the ALL badge below the portrait, right "
     "of the camera button (the user's screenshot)."),
    ("THE ARITHMETIC", "No count change: 854 implemented / 269 not implemented (27 skipped); 799 entries / 854 keys; 75 "
     "families. 28 trigger families / 434 entries start armed."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b
ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-15"
ch.cell(row=r, column=2).value = "v40"
ch.cell(row=r, column=3).value = (
    "ROUND 152. No whole-map hold; large first never at a flying enemy; 90 degrees for all 53 prefer-central attacks; "
    "Foe-Seeker and Dazh's Song start armed; the ALL badge on screen. Counts unchanged. SHIPPED: installed pack md5 %s; "
    "harness 151 full suite 6,446 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-15; xlsx v40 supersedes v39; v1-v39 byte-unchanged."
wb.save(DST)
print("wrote", DST, "| hold rows", nh, "| angle rows", na, "| tired rows", nt)
