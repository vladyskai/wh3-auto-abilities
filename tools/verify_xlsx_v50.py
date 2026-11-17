#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v50_2026-11-17.xlsx (round 166) from disk: the v38 verifier's structural checks
re-pointed at v50 (counts unchanged since round 164: 1,003 implemented, 36 skipped, 946 entries, 95 families; v1-v49
byte-unchanged, 94 files), then the round-166 checks: the Cards sheet holds 946 rows equal to the harness-165 CARD
lines, every card short and whole ('Fires ...', at most 160 characters, no token, bracket, name or em dash), the 22
round-165 notes are still there, and every round-166 wanderer key carries its note."""
import os
import runpy
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

T = os.path.dirname(os.path.abspath(__file__))
V38 = open(os.path.join(T, "verify_xlsx_v38.py"), encoding="utf-8").read()
V49 = open(os.path.join(T, "verify_xlsx_v49.py"), encoding="utf-8").read()
# the v49 verifier's patch list (v38 -> v49), its targets re-pointed at v50
R49 = eval(V49.split("\nR = ", 1)[1].split("\nfor a, b, n in R:", 1)[0])
SUB = [("v49_2026-11-17", "v50_2026-11-17"), ("v48_2026-11-16", "v49_2026-11-17"),
       ("round165\\pre_v49_workbook_md5", "round166\\pre_v50_workbook_md5"),
       ("df53a1b19192d4afecf132049cecb6e0", "5fdc60d3685f343e1efd2dc5869fd39e"),
       ("rows in v49, %d in v48", "rows in v50, %d in v49"), ("master v49", "master v50"),
       ("46. ROUND 165", "47. ROUND 166"), ("section 46", "section 47"), ('"v49" and', '"v50" and'),
       ("changelog v49", "changelog v50"), ("== 92 and", "== 94 and"), ("XLSX v49", "XLSX v50"), ("v1-v48", "v1-v49")]
R = []
for a, b, n in R49:
    for x, y in SUB:
        b = b.replace(x, y)
    R.append((a, b, n))
for a, b, n in R:
    assert V38.count(a) == n, (a[:70], V38.count(a))
    V38 = V38.replace(a, b)
head = V38
tmp = os.path.join(T, "_verify_v50_base.py")
open(tmp, "w", encoding="utf-8", newline="\n").write(head)
try:
    runpy.run_path(tmp, run_name="__main__")
except SystemExit as e:
    if e.code not in (None, 0):
        raise
finally:
    os.remove(tmp)

import make_xlsx_v49 as M49  # noqa: E402  (the round-165 notes; nothing is written on import)
import make_xlsx_v50 as M  # noqa: E402
RUN_CARDS = {}
for line in open(M.RUN, encoding="utf-8"):
    if line.startswith("CARD "):
        m, c = line[5:].rstrip("\n").split(": ", 1)
        RUN_CARDS[m] = c
wb = openpyxl.load_workbook(M.DST, read_only=True)
cs = wb["Cards"]
rows = list(cs.iter_rows(min_row=2, values_only=True))
same = sum(1 for r in rows if RUN_CARDS.get(r[0]) == r[4])
whole = sum(1 for r in rows if r[4] and r[4].startswith("Fires ") and r[4].endswith(".") and len(r[4]) <= 160
            and "{" not in r[4] and "[" not in r[4] and "\u2014" not in r[4] and " on A:" not in r[4])
ws = wb["Abilities"]
noted165, noted166 = set(), set()
wk = M.wander_keys()
for row in ws.iter_rows(min_row=2, values_only=True):
    for k in str(row[2]).split(";"):
        k = k.strip()
        if k in M49.NOTES and ("ROUND 165 (night audit): " + M49.NOTES[k] + ".") in str(row[21]):
            noted165.add(k)
        if k in wk and M.NOTE in str(row[21]):
            noted166.add(k)
print("Cards: %d rows, %d equal to the harness-165 run, %d short and whole; round-165 notes %d / %d; round-166 "
      "wanderer notes %d / %d" % (len(rows), same, whole, len(noted165), len(M49.NOTES), len(noted166), len(wk)))
good = (len(rows) == 946 and same == 946 and whole == 946 and noted165 == set(M49.NOTES) and noted166 == wk
        and len(wk) > 0)
print("XLSX v50 VERIFY OK" if good else "XLSX v50 VERIFY: round-166 checks FAILED")
sys.exit(0 if good else 1)
