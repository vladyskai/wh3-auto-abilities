#!/usr/bin/env python3
"""Read-only peek at workbook v78: the rows round 201 touches and the Numbers sheet's fixed rows."""
import openpyxl

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v78_2026-11-22.xlsx"
wb = openpyxl.load_workbook(SRC, read_only=True)
for r, row in enumerate(wb["Abilities"].iter_rows(values_only=True, min_row=2), start=2):
    k = str(row[2])
    if "whirlwind_of_death" in k or "master_rune_of_" in k or "rune_abilities_rune_of_speed" in k:
        print(r, row[0], row[1], "|", k, "|", row[17], "|", str(row[18])[:150], "|", row[19], "|", row[20], "|",
              str(row[21])[:260], "|", row[22])
nm = wb["Numbers"]
for r, row in enumerate(nm.iter_rows(values_only=True, min_row=1, max_row=44), start=1):
    if any(v is not None for v in row):
        print("N", r, [str(v)[:170] if v is not None else None for v in row[:5]])
for r, row in enumerate(nm.iter_rows(values_only=True, min_row=183, max_row=190), start=183):
    print("N", r, [str(v)[:120] if v is not None else None for v in row[:5]])
print("sheets", wb.sheetnames, "cards rows", wb["Cards"].max_row, "defs rows", wb["Definitions"].max_row)
d = wb["Definitions"]
last = [r for r in d.iter_rows(values_only=True) if r[0]]
print("last def:", str(last[-3][0])[:100], "|", str(last[-1][0])[:60])
