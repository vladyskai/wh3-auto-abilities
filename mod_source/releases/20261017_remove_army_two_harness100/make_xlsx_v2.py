# -*- coding: utf-8 -*-
"""Create WH3_abilities_master_v2_2026-10-17.xlsx from v1 (v1 left untouched).

Changes:
  * Abilities: Meat Feast + Massacre -> Implementation "REMOVED (outside rule)"
    (new status value), Trigger family / Trigger (as implemented) -> "-",
    grey fill.
  * Definitions: new status-vocabulary row "REMOVED (outside rule)";
    OUTSIDE-RULE-IMPLEMENTED marked historical (0 rows); title -> v2.
  * Definitions trigger glossary: melee_unwavering 362/371, ushoran_health
    33/34, TOTAL 577/603.
  * Numbers: #6 -> 0, #7 -> 603, reconciliation sentence.
  * Changelog: v2 row.
"""
import os
import shutil
from copy import copy

import openpyxl
from openpyxl.styles import Font, PatternFill

DOCS = r"C:\Users\vlady\Desktop\WH3_mod\docs"
V1 = os.path.join(DOCS, "WH3_abilities_master_v1_2026-10-17.xlsx")
V2 = os.path.join(DOCS, "WH3_abilities_master_v2_2026-10-17.xlsx")
TODAY = "2026-10-17"

assert os.path.exists(V1)
wb = openpyxl.load_workbook(V1)

# ------------------------------------------------------------------ Abilities
ws = wb["Abilities"]
GREY = PatternFill("solid", fgColor="D9D9D9")
hits = []
for r in range(2, ws.max_row + 1):
    key = str(ws.cell(row=r, column=3).value or "")
    if "wh3_main_prisoners_butcher" in key or "wh3_main_prisoners_massacre" in key:
        hits.append(r)
        ws.cell(row=r, column=20, value="REMOVED (outside rule)")
        ws.cell(row=r, column=21, value="-")
        ws.cell(row=r, column=22, value="-")
        for ci in range(1, 24):
            ws.cell(row=r, column=ci).fill = GREY
assert len(hits) == 2, hits
print("Abilities rows updated:", hits)

# ------------------------------------------------------------------ Definitions
ds = wb["Definitions"]
ds.cell(row=1, column=1, value="DEFINITIONS - WH3 ability master v2 (%s)" % TODAY)

# locate the status vocabulary rows by their first-column text
row_out = None
for r in range(1, ds.max_row + 1):
    v = ds.cell(row=r, column=1).value
    if v == "OUTSIDE-RULE-IMPLEMENTED":
        row_out = r
        break
assert row_out, "OUTSIDE-RULE-IMPLEMENTED row not found"

# mark the old status as historical
ds.cell(row=row_out, column=2,
        value=("HISTORICAL (v1 only): the ability was in the mod but NOT in the wheel - the two Ogre army "
               "abilities Meat Feast (wh3_main_prisoners_butcher) and Massacre (wh3_main_prisoners_massacre). "
               "Both were REMOVED from the mod in v2 - see REMOVED (outside rule). (0 rows in v2)."))

# insert the new status row directly below it, copying the row's look
ds.insert_rows(row_out + 1)
for ci in range(1, 3):
    src = ds.cell(row=row_out, column=ci)
    dst = ds.cell(row=row_out + 1, column=ci)
    dst.font = copy(src.font)
    dst.fill = copy(src.fill)
    dst.border = copy(src.border)
    dst.alignment = copy(src.alignment)
ds.cell(row=row_out + 1, column=1, value="REMOVED (outside rule)")
ds.cell(row=row_out + 1, column=2,
        value=("The ability WAS implemented but sits OUTSIDE the in-wheel rule and has been REMOVED from the "
               "mod's ABILITIES table per the user's instruction of 2026-10-17. Meat Feast "
               "(wh3_main_prisoners_butcher) and Massacre (wh3_main_prisoners_massacre) - both army-bar - "
               "carry this value. (2 rows; v2)."))
print("Definitions: inserted REMOVED (outside rule) at row", row_out + 1)

# trigger glossary counts (find rows by trigger name in column A)
def set_counts(name, entries, keys):
    for r in range(1, ds.max_row + 1):
        if ds.cell(row=r, column=1).value == name and ds.cell(row=r, column=5).value is not None:
            ds.cell(row=r, column=5, value=str(entries))
            ds.cell(row=r, column=6, value=str(keys))
            return r
    raise AssertionError("glossary row not found: " + name)

print("glossary melee:", set_counts("melee_unwavering", 362, 371))
print("glossary ushoran:", set_counts("ushoran_health", 33, 34))
for r in range(1, ds.max_row + 1):
    if str(ds.cell(row=r, column=1).value or "").startswith("TOTAL (all 35 evaluators)"):
        ds.cell(row=r, column=5, value="577")
        ds.cell(row=r, column=6, value="603")
        print("glossary TOTAL:", r)
        break

# ------------------------------------------------------------------ Numbers
ns = wb["Numbers"]
for r in range(1, ns.max_row + 1):
    label = str(ns.cell(row=r, column=2).value or "")
    if label == "Implemented but OUTSIDE the rule (reported separately)":
        ns.cell(row=r, column=3, value="0")
        ns.cell(row=r, column=4, value="0")
        ns.cell(row=r, column=5, value="0")
    elif label == "All implemented in the mod (4 + 6)":
        ns.cell(row=r, column=3, value="603")
        ns.cell(row=r, column=4, value=603 / 1797)
        ns.cell(row=r, column=5, value=603 / 1158)
    elif str(ns.cell(row=r, column=1).value or "").startswith("Reconciliation:"):
        ns.cell(row=r, column=1,
                value=("Reconciliation: included 1158 + excluded 639 = 1797; implemented in 603 + implemented out 0 "
                       "= 603 (the whole mod); not implemented in wheel 555 + implemented in wheel 603 = 1158 included."))

# ------------------------------------------------------------------ Changelog
cs = wb["Changelog"]
row = cs.max_row + 1
cs.cell(row=row, column=1, value=TODAY)
cs.cell(row=row, column=2, value="v2")
cs.cell(row=row, column=3,
        value="removed Meat Feast and Massacre (implemented but outside the in-wheel rule) per user instruction")
cs.cell(row=row, column=4,
        value=("user instruction 2026-10-17; implemented by the mod build + tracker + spreadsheet update "
               "(harness 100). Supersedes v1; v1 is left unchanged."))
for ci in range(1, 5):
    cs.cell(row=row, column=ci).alignment = openpyxl.styles.Alignment(wrap_text=True, vertical="top")
    cs.cell(row=row, column=ci).border = openpyxl.styles.Border(
        left=openpyxl.styles.Side(style="thin"), right=openpyxl.styles.Side(style="thin"),
        top=openpyxl.styles.Side(style="thin"), bottom=openpyxl.styles.Side(style="thin"))
cs.row_dimensions[row].height = 45

wb.save(V2)
print("wrote", V2, os.path.getsize(V2), "bytes")
assert os.path.getsize(V1) == 349142, "v1 changed!"
print("v1 untouched:", os.path.getsize(V1), "bytes")
