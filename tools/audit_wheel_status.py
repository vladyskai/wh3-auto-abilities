#!/usr/bin/env python3
"""THE WHEEL-STATUS GATE - run this on every new workbook version.

THE RULE THIS ENFORCES IS THE USER'S, STATED IN ROUND 121, VERBATIM:

    "The triggers will not work if the ability is not in the ability wheel on
     the lower left corner of the battle screen, meaning 'you'd lose working
     triggers' makes no sense. Therefore, ALL ARMY ABILITIES PLEASE EXCLUDE."

An army-bar ability (a row in `army_special_abilities_tables`, i.e. a key in the
`army_spec` junction) is not on the battle ability wheel. `perform_special_ability`
can therefore never be called for it, so it can never fire and it can never be
IN-WHEEL. There is NO exceptions list and NO documented remainder: the earlier
BASELINE of 17 "unresolved" rows was the defect, not the fix, and was removed in
round 121 when the same ruling was applied to those 17 rows.

Why it exists at all (round 120): two rows read IN-WHEEL while their own reason
column said 'skipped (round 106: army-bar ability (army_spec junction) - out of
wheel scope)'. The Status column was computed from `unit_abilities.source_type`
ONLY, and the IN-WHEEL rule named the army-bar family only as `source_type =
army`, so the `army_spec` junction was never consulted. Round 106 wrote skips
through a loop that writes columns 19-22 and NEVER column 18.

Usage:
    python audit_wheel_status.py [path.xlsx]      # default: v20

GATES
  G1  FAIL if any row reads IN-WHEEL while its reason / implementation /
      trigger text names an army-bar, army_spec, army-ability or campaign-side
      junction exclusion.
  G2  FAIL if an IN-WHEEL row's reason does not start with 'carrier family:' or
      'skipped ' (the two legitimate forms), or if an EXCLUDED row names a
      trigger family.
  G3  FAIL if ANY row marked IN-WHEEL carries a key in the `army_spec` set -
      the DATA test, not the text test. No baseline, no exceptions list: one
      such row is a failure. (This is the gate the user's ruling requires.)
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import sys

import openpyxl

ARMY_SPEC = GP.ARMY_SPEC
DEFAULT = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v20_2026-10-20.xlsx"

ARMY_TOKENS = ("army_spec", "army-bar", "army bar", "army ability", "campaign-side junction")
FAMILY_PREFIXES = ("carrier family:", "skipped ")

TRIGGER_PREFIXES = ("enemy_", "ally_", "melee", "charge", "wavering", "health", "air_drop",
                    "ushoran", "glorious", "tired", "blood", "eat_da", "verminking", "barrier",
                    "metallurgy", "self_")

path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT

army = set()
with open(ARMY_SPEC, encoding="utf-8", errors="replace") as f:
    f.readline()
    for line in f:
        if line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        if c and c[0].strip():
            army.add(c[0].strip())

wb = openpyxl.load_workbook(path, data_only=True)
ws = wb["Abilities"]
rows = [(ws.cell(row=r, column=1).value, str(ws.cell(row=r, column=2).value),
         [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()],
         str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=19).value or ""),
         str(ws.cell(row=r, column=20).value or ""))
        for r in range(2, ws.max_row + 1)]

fails = []

# ------------------------------------------------------------------ G1
g1 = [r for r in rows if r[3] == "IN-WHEEL"
      and any(t in (r[4] + " " + r[5]).lower() for t in ARMY_TOKENS)]
if g1:
    fails.append("G1: %d row(s) read IN-WHEEL while their own text says army-bar/army_spec: %s"
                 % (len(g1), [(r[0], r[1], r[2][0] if r[2] else "") for r in g1]))

# ------------------------------------------------------------------ G2
for r in rows:
    if r[3] == "IN-WHEEL":
        if not r[4].startswith(FAMILY_PREFIXES):
            fails.append("G2: IN-WHEEL row %s (%s) has an unexplained reason: %s"
                         % (r[0], r[1], r[4][:80]))
    elif r[3] == "EXCLUDED":
        if r[5].lower().startswith(TRIGGER_PREFIXES):
            fails.append("G2: EXCLUDED row %s (%s) names a trigger family (%s)"
                         % (r[0], r[1], r[5]))

# ------------------------------------------------------------------ G3
# The DATA gate, with NO exceptions: any IN-WHEEL row whose key set intersects
# the army_spec junction is a failure, full stop.
g3 = [r for r in rows if r[3] == "IN-WHEEL" and any(k in army for k in r[2])]
g3_keys = sorted(set(k for r in g3 for k in r[2] if k in army))
if g3:
    fails.append("G3: %d row(s) read IN-WHEEL but carry an army_spec (army-bar) key - these can "
                 "never be cast (no wheel button) and must be EXCLUDED: %s"
                 % (len(g3), [(r[0], r[1], [k for k in r[2] if k in army]) for r in g3]))

# ------------------------------------------------------------------ report
print("WHEEL-STATUS AUDIT - %s" % path)
print("  the rule: army-bar (army_spec junction) = NOT in the battle ability wheel = EXCLUDED "
      "(user ruling, round 121)")
print("  rows: %d (%s)" % (len(rows), ", ".join("%s %d" % (s, sum(1 for r in rows if r[3] == s))
                                               for s in ("IN-WHEEL", "EXCLUDED"))))
print("  army_spec keys in the junction: %d" % len(army))
print("  G1 army-bar rows reading IN-WHEEL by their own text: %d (must be 0)" % len(g1))
print("  G3 army-bar rows reading IN-WHEEL by their KEYS:      %d (must be 0, no exceptions)"
      % len(g3))
if g3_keys:
    for k in g3_keys:
        print("     - %s" % k)
print("  EXCLUDED rows that carry an army_spec key: %d"
      % sum(1 for r in rows if r[3] == "EXCLUDED" and any(k in army for k in r[2])))

if fails:
    print("\nWHEEL-STATUS AUDIT: %d FAILURE(S)" % len(fails))
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("\nWHEEL-STATUS AUDIT OK")
