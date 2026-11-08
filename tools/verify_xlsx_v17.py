#!/usr/bin/env python3
"""Independent verification of v17, read back from disk (not from the build run)."""
import hashlib
import os
import openpyxl

D = r"C:\Users\vlady\Desktop\WH3_mod\docs"
V17 = os.path.join(D, "WH3_abilities_master_v17_2026-10-18.xlsx")
V16 = os.path.join(D, "WH3_abilities_master_v16_2026-10-18.xlsx")

wb = openpyxl.load_workbook(V17)
a = wb["Abilities"]

print("sheets          :", wb.sheetnames)
print("Abilities rows  :", a.max_row, "(v16: 1800)")

rows = []
for r in range(2, a.max_row + 1):
    if a.cell(row=r, column=21).value == "air_drop_on_infantry":
        rows.append(r)
print("air-drop rows   :", len(rows), rows)

need_sum = ["round 116", "AIR_DROP_DWELL_MID_S - AIR_DROP_DWELL_SWING_S * proj",
            "0 s for an enemy running AT the caster, 1 s stationary or perpendicular, 2 s running AWAY",
            "measured ONCE per contact", "AIR_DROP_MIN_CONTACT_S = 0.3 s",
            "short-crossing fallback", "Every contact episode PRINTS the raw reads", "UNREADABLE"]
need_trig = ["AIR_DROP_DWELL_MID_S - (FOURTH.AIR_DROP_DWELL_SWING_S * proj)",
             "dot(v, axis) / (speed * |axis|)", "clamped to +-1",
             "0.0 s, proj 0 (stationary or perpendicular) -> 1.0 s, proj -1 (running straight AWAY) -> 2.0 s",
             "MEASURED ONCE PER CONTACT", "SHORT-CROSSING FALLBACK",
             "reads: moving=<b> is_moving_fast=<b>", "reads(hold):", "|h|=<n.n>",
             "delay=<n.nn>s (measured once for this contact)",
             "src=<src>", "measured once for this contact", "UNREADABLE",
             "dwell satisfied after", "dwell cancelled: separated after", "dwell started: under at gap",
             "POLL_MS = 250 ms steps", "VERIFIES THE WAIT", "the first evaluation of a contact stamps the PAIR"]
bad_sum = [r for r in rows if not all(t in (a.cell(row=r, column=19).value or "") for t in need_sum)]
bad_trig = [r for r in rows if not all(t in (a.cell(row=r, column=22).value or "") for t in need_trig)]
print("col 19 measured-delay clause on all 19 :", not bad_sum, ("missing on " + str(bad_sum)) if bad_sum else "")
print("col 22 formula + read log on all 19    :", not bad_trig, ("missing on " + str(bad_trig)) if bad_trig else "")
print("col 19 no stale 'round 115' rule line  :",
      sum(1 for r in rows if "round 115 - THE EDGE-GAP RULE" in (a.cell(row=r, column=19).value or "")) == 0)
print("col 22 no stale AIR_DROP_DWELL_S       :",
      sum(1 for r in rows if "AIR_DROP_DWELL_S =" in (a.cell(row=r, column=22).value or "")) == 0)

d = wb["Definitions"]
dtxt = "\n".join(str(c.value) for row in d.iter_rows() for c in row if c.value is not None)
for tok in ("14. THE MEASURED DELAY (round 116)",
            "FOURTH.AIR_DROP_DWELL_MID_S", "FOURTH.AIR_DROP_DWELL_SWING_S",
            "FOURTH.AIR_DROP_MIN_CONTACT_S",
            "axis = normalise(caster.position() - enemy.position())",
            "the COSINE, clamped to +-1",
            "proj +1 (running straight AT the caster) -> 0.00 s",
            "src=no-heading", "src=stationary", "src=moving-unreadable", "src=speed-unreadable",
            "src=speed-zero", "src=pos-unreadable", "src=axis-degenerate", "src=axis-unreadable",
            "reads: moving=true is_moving_fast=false", "reads(hold):",
            "UNREADABLE stands in for a read whose pcall failed",
            "MEASURED ONCE PER CONTACT", "TUNING GUIDE (round 116)"):
    print("  Definitions has %-52s : %s" % (tok[:52], tok in dtxt))
    assert tok in dtxt, "Definitions is missing: " + tok

n = wb["Numbers"]
print("Numbers 42 :", n.cell(row=42, column=1).value[:80])
print("Numbers 101:", n.cell(row=101, column=1).value[:80])
assert "round 116" in n.cell(row=42, column=1).value
assert "Round 116 reconciliation" in n.cell(row=101, column=1).value

ch = wb["Changelog"]
last = ch.max_row
print("Changelog last row:", ch.cell(row=last, column=2).value, "|", (ch.cell(row=last, column=3).value or "")[:70])
assert ch.cell(row=last, column=2).value == "v17"
assert "ROUND 116" in ch.cell(row=last, column=3).value
assert "0c489c2438cf9acc98730bff1b0df52b" in (ch.cell(row=last, column=4).value or "")

print()
print("file sizes / md5:")
for f in sorted(os.listdir(D)):
    if f.startswith("WH3_abilities_master_v1") and f.endswith(".xlsx"):
        p = os.path.join(D, f)
        print("  %-42s %8d  md5 %s" % (f, os.path.getsize(p), hashlib.md5(open(p, "rb").read()).hexdigest()))
print()
print("V17 ASSERTIONS: ALL PASS")
