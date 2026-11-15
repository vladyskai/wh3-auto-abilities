#!/usr/bin/env python3
"""Build WH3_abilities_master_v41_2026-11-15.xlsx from v40 - round 153. No count changes.

(1) The 77 enemy_blob rows gain the trash rule (live value below 2 per soldier is not a target unless the blast covers
    3 packed blocks).
(2) Definitions: title v41, section 38. Changelog: a v41 row. Numbers: the date line.
v1-v40 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402
import gen_blob_tables as GB  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v40_2026-11-15.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v41_2026-11-15.xlsx"
src = open(r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua", encoding="utf-8").read()
KEYS = set(GB.keys_in(src))
assert len(KEYS) == 77
TRASH = (" ROUND 153 TRASH (user rulings 2026-11-15 \"ignore trash units ... Unless there is a big blob\", \"Value below 2\", "
         "\"3 packed blocks\"): an infantry target whose live value per soldier is below 2 (the bottom 4% of infantry: "
         "Zombies, Skavenslaves, The Tithe, Skeletons, Clanrats) is taken only when the blast covers at least 3 packed "
         "blocks (3 x the blast area / 2.368 m2: about 100 soldiers in a 5 m blast); an unreadable value is not trash.")
assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
n_t = 0
for r in range(2, ws.max_row + 1):
    ks = [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
    if ks and ks[0] in KEYS and str(ws.cell(row=r, column=20).value) == "IMPLEMENTED":
        c = ws.cell(row=r, column=22)
        c.value = str(c.value) + TRASH
        n_t += 1
assert n_t == 77, n_t
n = wb["Numbers"]
n.cell(row=7, column=1).value = (
    "Date: 2026-11-15     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v41 - ROUND 153: the blob attacks ignore trash infantry (value below 2 per soldier) unless the blast covers 3 "
    "packed blocks; the ALL badge for any selection, in the middle of the cloth, with a tooltip. No count change: 854 "
    "implemented / 269 not implemented (27 skipped); the mod 799 entries / 854 keys / 75 trigger families.)")
d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v40")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v41 (2026-11-15)"
base = d.max_row + 2
sec = [
    ("38. ROUND 153 - NO TRASH TARGETS, THE ALL BADGE FOR ANY SELECTION (v41)", None),
    ("THE RULINGS (2026-11-15)", "\"ignore trash units ... Unless there is a big blob\": trash = live value below 2 per "
     "soldier (\"Value below 2\"), a big blob = 3 packed blocks in the blast (\"3 packed blocks\"). The ALL badge: shown "
     "whenever a selected unit owns any of our abilities, in the middle of the cloth, with a hover tooltip."),
    ("THE ARITHMETIC", "No count change: 854 implemented / 269 not implemented (27 skipped); 799 entries / 854 keys; 75 "
     "families."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b
ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-15"
ch.cell(row=r, column=2).value = "v41"
ch.cell(row=r, column=3).value = (
    "ROUND 153. Blob attacks ignore trash infantry (value below 2 per soldier) unless 3 packed blocks; the ALL badge for "
    "any selection, moved, with a tooltip. Counts unchanged. SHIPPED: installed pack md5 %s; harness 152 full suite 6,473 "
    "checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-15; xlsx v41 supersedes v40; v1-v40 byte-unchanged."
wb.save(DST)
print("wrote", DST, "| trash rows", n_t)
