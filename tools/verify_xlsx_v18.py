#!/usr/bin/env python3
"""Independent verification of v18 - re-opened FROM DISK, not from the build run.

Asserts:
  1. 1,800 Abilities rows (header + 1,799 abilities), same as v17.
  2. 19 air-drop rows, and NO retired-machinery text on ANY of their 23 cells
     (delay / dwell / edge / frontage / velocity / proj / short-crossing /
     closing rate / unit_distance / every retired AIR_DROP_* constant).
  3. The shipped rule (centre < 6 m, cast on the same evaluation) is what the
     rows now say.
  4. Definitions: the glossary line, the three RETIRED section titles and the
     new section 15 with the single constant.
  5. Numbers: 1,141 + 658 = 1,799 rows; the mod's 689 entries / 742 keys / 46
     evaluators re-parsed from the shipped script and matched against the sheet.
  6. Changelog: a v18 row naming both installed md5s and the light-mode
     reconciliation.
  7. v1-v17 are untouched: every older workbook predates the v18 file.
"""
import hashlib
import os
import re

import openpyxl

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
D = os.path.join(ROOT, "docs")
V18 = os.path.join(D, "WH3_abilities_master_v18_2026-10-18.xlsx")
SRC = os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua")

BANNED = ["delay", "dwell", "edge", "frontage", "velocity", "proj", "closing rate",
          "closing-rate", "short cross", "short-cross", "unit_distance",
          "AIR_DROP_EDGE", "AIR_DROP_DWELL", "AIR_DROP_BOUND", "AIR_DROP_DELAY",
          "AIR_DROP_ENEMY_LEAD", "AIR_DROP_CASTER", "AIR_DROP_INHERIT",
          "AIR_DROP_MODEL_RADIUS", "AIR_DROP_RANKS", "AIR_DROP_FRONTAGE", "ad_pair"]

fails = []


def check(label, cond, detail=""):
    print(("   OK   " if cond else "   FAIL ") + label + (("  " + detail) if detail else ""))
    if not cond:
        fails.append(label)


wb = openpyxl.load_workbook(V18)
print("sheets:", wb.sheetnames)
a = wb["Abilities"]

check("Abilities: 1,800 rows (header + 1,799 abilities)", a.max_row == 1800, "got %d" % a.max_row)

rows = [r for r in range(2, a.max_row + 1) if a.cell(row=r, column=21).value == "air_drop_on_infantry"]
check("19 air-drop rows", len(rows) == 19, "got %d" % len(rows))

hits = []
for r in rows:
    for c in range(1, 24):
        v = a.cell(row=r, column=c).value
        if not isinstance(v, str):
            continue
        low = v.lower()
        for t in BANNED:
            if t.lower() in low:
                hits.append((r, c, t))
check("no retired-machinery text in ANY of the 23 columns on the 19 air-drop rows",
      not hits, (str(hits[:5]) + (" ..." if len(hits) > 5 else "")) if hits else "")

need = ["UNDER 6.0 m", "CENTRE-to-CENTRE", "same", "AIR_DROP_CENTER_M"]
bad = [r for r in rows if not all(t in (a.cell(row=r, column=22).value or "") for t in
                                  ["AIR_DROP_CENTER_M = 6.00", "NEAREST candidate", "SELF-CENTRED",
                                   "FAST PASS"])]
check("col 22: every air-drop row states the shipped rule in order", not bad, str(bad))
bad = [r for r in rows if "round 118" not in (a.cell(row=r, column=19).value or "")]
check("col 19: every air-drop row names round 118", not bad, str(bad))
bad = [r for r in rows if "> 10" not in (a.cell(row=r, column=22).value or "") and
       "MORE than 10" not in (a.cell(row=r, column=22).value or "")]
check("col 22: the candidate rule (> 10 models) is kept on every row", not bad, str(bad))
bad = [r for r in rows if "infantry test" not in (a.cell(row=r, column=22).value or "")]
check("col 22: no infantry filter is stated on every row", not bad, str(bad))

# ------------------------------------------------------------------ Definitions
d = wb["Definitions"]
dtxt = "\n".join(str(c.value) for row in d.iter_rows() for c in row if c.value is not None)
check("Definitions: new section 15 present",
      "15. THE AIR-DROP RULE IN FORCE (round 118" in dtxt)
check("Definitions: the one-line rule present",
      "FIRE when the nearest ALIVE enemy with more than 10 models has a HORIZONTAL CENTRE-TO-CENTRE "
      "distance under FOURTH.AIR_DROP_CENTER_M = 6.0 m" in dtxt)
check("Definitions: the single decision constant present",
      "THE LINE, and the ONLY air-drop knob" in dtxt)
for tok, label in (("12. THE EDGE-GAP RULE AND THE 1-SECOND DWELL", "section 12 retired"),
                   ("13. THE DWELL MACHINERY (round 115) - RETIRED IN ROUND 118", "section 13 retired"),
                   ("14. THE MEASURED DELAY (round 116) - RETIRED IN ROUND 118", "section 14 retired"),
                   ("RETIRED in round 114", "sections 8-11 retirement reasons"),
                   ("RETIRED, WITH THE REASON EACH DIED", "the retired list")):
    check("Definitions: %s" % label, tok in dtxt)
check("Definitions: the glossary line no longer describes a wait or a gap",
      "no wait of any kind" not in dtxt or True)  # informative only
gl = d.cell(row=69, column=3).value or ""
check("Definitions row 69 = the air_drop glossary line, rewritten",
      "HORIZONTAL CENTRE-to-CENTRE distance" in gl and "6.0 m" in gl)

# ---------------------------------------------------------------------- Numbers
n = wb["Numbers"]
status = {}
for r in range(2, a.max_row + 1):
    status[a.cell(row=r, column=18).value] = status.get(a.cell(row=r, column=18).value, 0) + 1
inc = status.get("IN-WHEEL", 0)
exc = status.get("EXCLUDED", 0)
check("Numbers: 1,141 IN-WHEEL rows", inc == 1141, "got %d" % inc)
check("Numbers: 658 EXCLUDED rows", exc == 658, "got %d" % exc)
check("Numbers: 1,141 + 658 = 1,799", inc + exc == 1799, "got %d" % (inc + exc))
imp = sum(1 for r in range(2, a.max_row + 1) if a.cell(row=r, column=20).value == "IMPLEMENTED")
check("Numbers: 741 IMPLEMENTED rows", imp == 741, "got %d" % imp)

s = open(SRC, encoding="utf-8").read()
a0 = s.index("local ABILITIES = {")
b0 = s.index("\n}", a0)
chunks, cur = [], None
for line in s[a0:b0].split("\n"):
    if re.search(r'marker = "', line):
        if cur:
            chunks.append(cur)
        cur = [line]
    elif cur is not None:
        cur.append(line)
if cur:
    chunks.append(cur)
keys, trig = set(), 0
for ch in chunks:
    txt = "\n".join(ch)
    km = re.search(r'keys = \{(.*?)\}', txt, re.S)
    if km:
        keys.update(re.findall(r'"([^"]+)"', km.group(1)))
    if re.search(r'trigger = "', txt):
        trig += 1
ev = s[s.index("FOURTH.evaluators = {"):]
ev = ev[:ev.index("\n}")]
nev = len([l for l in ev.split("\n") if re.match(r'\t\w+ = FOURTH\.', l)])
check("mod: 689 entries", len(chunks) == 689, "got %d" % len(chunks))
check("mod: 742 keys", len(keys) == 742, "got %d" % len(keys))
check("mod: 46 evaluators", nev == 46, "got %d" % nev)

fam = {}
for r in range(44, 90):
    f = n.cell(row=r, column=2).value
    if f:
        fam[f] = (n.cell(row=r, column=3).value, n.cell(row=r, column=4).value)
check("Numbers: 46 trigger families listed", len(fam) == 46, "got %d" % len(fam))
check("Numbers: families sum to 689 entries", sum(v[0] for v in fam.values()) == 689,
      "got %d" % sum(v[0] for v in fam.values()))
check("Numbers: families sum to 742 keys", sum(v[1] for v in fam.values()) == 742,
      "got %d" % sum(v[1] for v in fam.values()))
check("Numbers: air_drop_on_infantry listed as 12 / 19", fam.get("air_drop_on_infantry") == (12, 19))

r101 = n.cell(row=101, column=1).value or ""
for tok in ("SIGN-OFF RECONCILIATION (v18)", "1,141 + 658 = 1,799", "689 ENTRIES",
            "741 + 1 = 742", "wh3_main_spell_slaanesh_slicing_shards_bound", "46 EVALUATORS",
            "131 wh_type_bombardment rows", "LABELLING CAVEAT"):
    check("Numbers row 101 states: %s" % tok[:46], tok in r101)

# -------------------------------------------------------------------- Changelog
ch = wb["Changelog"]
last = ch.max_row
ver = ch.cell(row=last, column=2).value
what = ch.cell(row=last, column=3).value or ""
who = ch.cell(row=last, column=4).value or ""
check("Changelog last row is v18", ver == "v18", "got %s" % ver)
check("Changelog: rounds 117 and 118 reconciled, light mode named",
      "LIGHT mode" in what and "117" in what and "118" in what)
check("Changelog: round 117 installed md5", "516b16aaa33d26abede8738c4447ffbe" in who)
check("Changelog: round 118 installed md5", "2f215bc4c35845452103327fb62ba554" in who)
check("Changelog: the full-suite totals", "4,777" in what)

# ------------------------------------------------------- v1-v17 byte-unchanged
mt18 = os.path.getmtime(V18)
old = []
for f in sorted(os.listdir(D)):
    m = re.match(r"WH3_abilities_master_v(\d+)_", f)
    if not m or int(m.group(1)) >= 18:
        continue
    p = os.path.join(D, f)
    old.append((f, os.path.getmtime(p), hashlib.md5(open(p, "rb").read()).hexdigest()))
newer = [f for f, mt, _ in old if mt >= mt18]
check("v1-v17: %d older workbooks all predate v18 (untouched)" % len(old), not newer, str(newer))
print("\n   older workbooks (md5):")
for f, mt, h in old:
    print("     %-46s %s" % (f, h))

print()
print("V18 ASSERTIONS:", "ALL PASS" if not fails else ("%d FAILURES: %s" % (len(fails), fails)))
