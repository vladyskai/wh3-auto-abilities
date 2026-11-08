#!/usr/bin/env python3
"""Independent verification of v16, read back from disk (not from the build run)."""
import hashlib
import os
import openpyxl

D = r"C:\Users\vlady\Desktop\WH3_mod\docs"
V16 = os.path.join(D, "WH3_abilities_master_v16_2026-10-18.xlsx")
V15 = os.path.join(D, "WH3_abilities_master_v15_2026-10-18.xlsx")

wb = openpyxl.load_workbook(V16)
a = wb["Abilities"]

print("sheets          :", wb.sheetnames)
print("Abilities rows  :", a.max_row, "(v15: 1800)")

rows = []
for r in range(2, a.max_row + 1):
    if a.cell(row=r, column=21).value == "air_drop_on_infantry":
        rows.append(r)
print("air-drop rows   :", len(rows), rows)

need_sum = ["AIR_DROP_DWELL_S = 1.0 s", "AIR_DROP_MIN_CONTACT_S = 0.3 s",
            "short-crossing fallback", "CONTINUOUSLY for"]
need_trig = ["AIR_DROP_DWELL_S = 1.0 s", "AIR_DROP_MIN_CONTACT_S = 0.3 s",
             "SHORT-CROSSING FALLBACK", "dwell satisfied after", "dwell cancelled: separated after",
             "dwell started: under at gap", "poll's own tick", "RE-VERIFIES the dwell",
             "first evaluation of a contact can NEVER fire"]
bad_sum = [r for r in rows if not all(t in (a.cell(row=r, column=19).value or "") for t in need_sum)]
bad_trig = [r for r in rows if not all(t in (a.cell(row=r, column=22).value or "") for t in need_trig)]
print("col 19 dwell clause on all 19 :", not bad_sum, ("missing on " + str(bad_sum)) if bad_sum else "")
print("col 22 dwell + fallback on 19 :", not bad_trig, ("missing on " + str(bad_trig)) if bad_trig else "")
print("col 19 no stale 'round 114'   :",
      sum(1 for r in rows if "round 114 - THE SIMPLE EDGE-GAP RULE" in (a.cell(row=r, column=19).value or "")) == 0)

d = wb["Definitions"]
dtxt = "\n".join(str(c.value) for row in d.iter_rows() for c in row if c.value is not None)
for tok in ("13. THE DWELL (round 115)", "FOURTH.AIR_DROP_DWELL_S", "1.0 (s)",
            "FOURTH.AIR_DROP_MIN_CONTACT_S", "0.3 (s)", "SHORT-CROSSING",
            "dwell satisfied after", "dwell cancelled: separated after",
            "short crossing: under for", "tick_count", "PURGE", "TUNING GUIDE (round 115)"):
    assert tok in dtxt, "Definitions is missing: " + tok
print("Definitions     : both constants + the dwell semantics + the five lines + the tuning guide  OK")

n = wb["Numbers"]
vals = {n.cell(row=5, column=1).value: n.cell(row=5, column=3).value}
row4 = [n.cell(row=5, column=c).value for c in range(1, 6)]
num = "\n".join(str(c.value) for row in n.iter_rows() for c in row if c.value is not None)
assert "742" in num and "689" in num and "12 entries / 19 keys" in num
print("Numbers         : 742 implemented / 689 entries / 12-19 air-drop, round-115 note present  OK")

ch = wb["Changelog"]
last = [ch.cell(row=ch.max_row, column=c).value for c in range(1, 5)]
print("Changelog last  :", last[0], last[1], "|", last[2][:70], "...")
assert last[1] == "v16" and "ROUND 115" in last[2]

# v1-v15 must be untouched: v15 is the immediate predecessor and must still be
# the OLD text (no dwell clause) with its original size.
w15 = openpyxl.load_workbook(V15)
a15 = w15["Abilities"]
n15 = sum(1 for r in range(2, a15.max_row + 1)
          if a15.cell(row=r, column=21).value == "air_drop_on_infantry")
t15 = a15.cell(row=rows[0], column=22).value
print("v15             : %d air-drop rows, dwell absent: %s" % (n15, "AIR_DROP_DWELL_S" not in t15))
assert n15 == 19 and "AIR_DROP_DWELL_S" not in t15
print("v15 md5         :", hashlib.md5(open(V15, "rb").read()).hexdigest())
print("v16 md5         :", hashlib.md5(open(V16, "rb").read()).hexdigest())
print("V16 OK")
