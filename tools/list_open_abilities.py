#!/usr/bin/env python3
"""List the still-open in-wheel abilities (the progress page's rule) with their tracker status and workbook facts."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl
import make_progress_page as P
import build_ability_database as bd
ver, wbp = P.newest_workbook()
ws = openpyxl.load_workbook(wbp, read_only=True)["Abilities"]
trk = {r["key"]: r["status"] for r in bd.tracker_rows()}
out = []
for row in ws.iter_rows(min_row=2, values_only=True):
    if str(row[17]) != "IN-WHEEL" or str(row[19]) == "IMPLEMENTED":
        continue
    keys = [k.strip() for k in str(row[2]).split(";") if k.strip()]
    st = trk.get(keys[0], "")
    if P.group_of(st) != "open":
        continue
    out.append((P.open_kind(st, keys[0])[:1], row[1], keys, row[3], row[4], row[8], row[10], row[12], st, row[15]))
out.sort(key=lambda r: (r[0], str(r[1])))
for r in out:
    print("%s | %s | %s | %s | uses %s | radius %s | range %s | cd %s\n    STATUS: %s\n    OVERVIEW: %s" % (
        r[0], r[1], ";".join(r[2]), r[3], r[4], r[5], r[6], r[7], r[8][:300], str(r[9])[:260]))
print(len(out))
