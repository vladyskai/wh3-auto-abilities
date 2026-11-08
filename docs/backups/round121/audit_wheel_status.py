#!/usr/bin/env python3
"""THE WHEEL-STATUS GATE - run this on every new workbook version.

Why it exists (round 120): two rows (Thorsen's Thunderstorm, both keys) read
IN-WHEEL while their own reason column said 'skipped (round 106: army-bar
ability (army_spec junction) - out of wheel scope)'. An army-bar ability cannot
be in the wheel, so the two columns contradicted each other in the same row.

The pipeline cause: the Status column is computed from
`unit_abilities.source_type` ONLY (build_abilities_master_xlsx.py:590) - the
IN-WHEEL rule names the army-bar family only as `source_type = army`, so the
`army_spec` junction (the table that actually makes an ability an ARMY-BAR
button) was never consulted. A later round discovered the junction by hand and
wrote the skip through make_xlsx_v7.py's SKIP_KEYS loop, which writes columns
19-22 and NEVER writes or asserts column 18 - unlike set_impl(), which asserts
Status == IN-WHEEL before it writes.

Usage:
    python audit_wheel_status.py [path.xlsx]      # default: v19

GATES
  G1  FAIL if any row reads IN-WHEEL while its reason / implementation /
      trigger text names an army-bar, army_spec, army-ability or campaign-side
      junction exclusion.  (0 rows expected.)
  G2  FAIL if an IN-WHEEL row's reason does not start with 'carrier family:' or
      'skipped ' (the two legitimate forms), or if an EXCLUDED row names a
      trigger family.
  G3  FAIL if the set of IN-WHEEL rows that are `army_spec` junction entries
      differs from the DOCUMENTED BASELINE below - in either direction, so a
      new mislabel fails and a silent 'fix' also fails until the baseline is
      updated deliberately.  The list is printed on every run.
"""
import sys

import openpyxl

ARMY_SPEC = r"C:\Users\vlady\AppData\Local\Temp\wh3\army_spec.tsv"
DEFAULT = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v19_2026-10-20.xlsx"

ARMY_TOKENS = ("army_spec", "army-bar", "army bar", "army ability", "campaign-side junction")
FAMILY_PREFIXES = ("carrier family:", "skipped ")

# The documented, UNRESOLVED remainder: army_spec-junction abilities that still
# read IN-WHEEL. Round 120 corrected the two rows the user named and left these
# alone because 4 of them are IMPLEMENTED in the mod today - moving them is a
# roster decision, not a data correction. 17 rows / 17 keys.
BASELINE = {
    "wh2_dlc15_character_abilities_wardens_cage",
    "wh3_dlc20_cataclysm_bound_ashes_and_dust",
    "wh3_dlc20_cataclysm_bound_dance_of_despair",
    "wh3_dlc20_cataclysm_bound_gehennas_golden_globe",
    "wh3_dlc20_cataclysm_bound_magma_storm",
    "wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment",
    "wh3_dlc20_cataclysm_bound_storm_of_renewal",
    "wh3_dlc20_cataclysm_bound_time_amok",
    "wh3_dlc27_cataclysm_bound_ashes_and_dust",
    "wh3_dlc27_cataclysm_bound_dance_of_despair",
    "wh3_dlc27_cataclysm_bound_gehennas_golden_globe",
    "wh3_dlc27_cataclysm_bound_magma_storm",
    "wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment",
    "wh3_dlc27_cataclysm_bound_storm_of_renewal",
    "wh3_dlc27_cataclysm_bound_time_amok",
    "wh3_dlc29_army_abilities_pestilential_bombardment",
    "wh3_main_cataclysm_khorne_greater_gate_of_khorne",
}

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
resid = sorted(set(k for r in rows if r[3] == "IN-WHEEL" for k in r[2] if k in army))
new = sorted(set(resid) - BASELINE)
gone = sorted(BASELINE - set(resid))
if new:
    fails.append("G3: NEW army_spec rows reading IN-WHEEL (a fresh mislabel - correct them): %s" % new)
if gone:
    fails.append("G3: army_spec baseline keys no longer IN-WHEEL (update the baseline deliberately): %s"
                 % gone)

# ------------------------------------------------------------------ report
print("WHEEL-STATUS AUDIT - %s" % path)
print("  rows: %d (%s)" % (len(rows), ", ".join("%s %d" % (s, sum(1 for r in rows if r[3] == s))
                                               for s in ("IN-WHEEL", "EXCLUDED"))))
print("  G1 army-bar rows reading IN-WHEEL: %d (must be 0)" % len(g1))
print("  G3 army_spec-junction keys reading IN-WHEEL: %d - the documented, unresolved remainder:"
      % len(resid))
for k in resid:
    impl = sorted(set(r[5] for r in rows if k in r[2]))
    print("     - %s  [%s]" % (k, " / ".join(impl)))
print("     (moving these is a roster decision: %d of them are implemented today)"
      % sum(1 for r in rows if r[5] == "IMPLEMENTED" and any(k in army for k in r[2])))

if fails:
    print("\nWHEEL-STATUS AUDIT: %d FAILURE(S)" % len(fails))
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("\nWHEEL-STATUS AUDIT OK")
