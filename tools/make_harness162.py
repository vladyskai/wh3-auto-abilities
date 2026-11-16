#!/usr/bin/env python3
"""Build harness162.lua from harness161.lua for round 163 (the placed areas, the expendable units). Older harnesses are
never edited.

Pin rebases (code lines only; a rule with a guard only touches lines holding the guard):
  entries 892 -> 918, keys 949 -> 975 (26 entries / 26 keys), full-table iterations 1784 -> 1836,
  multi-use charge-gate keys 287 -> 304 (+17), wind-up keys 289 -> 310 (+21), range_real fields 365 -> 389 (+24),
  target classes 43 -> 47 (+4 not_flying); enemy_wander 20 -> 42 (harness 161's token check);
  the tooltip mirror gains the two new wordings. Further rebases are added only where a full run proves them.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_wandering_winds_harness161\harness161.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_placed_areas_harness162\harness162.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h162_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 162 - ROUND 163: THE PLACED AREAS AND THE EXPENDABLE UNITS (26
--   entries, 2 new families: enemy_strike, ally_blast; the friendly-fire
--   checks skip expendable and cheap units of ours).
--   Edited vs harness161: this banner, the pin rebases listed in
--   tools/make_harness162.py, the tooltip mirror, run_h162 and its call.
--   RED control: H162_LIVE / H162_ANN on docs/backups/round163/pre163_*.lua.
-- ============================================================================
"""
PIN_RULES = [
    (r"== 892\b", "== 918", None),
    (r"== 949\b", "== 975", None),
    (r"it == 1784\b", "it == 1836", None),
    (r"entries = 892, keys = 949", "entries = 918, keys = 975", None),
    (r"want 892\b", "want 918", None),
    (r"FULL 892-entry table", "FULL 918-entry table", None),
    (r"892 abilities per pass", "918 abilities per pass", None),
    (r"table of 892 after round 162", "table of 918 after round 163", None),
    (r"\(12 air-drop entries of 892\)", "(12 air-drop entries of 918)", None),
    (r"\(RED_MODE and 0 or 287\)", "(RED_MODE and 0 or 304)", None),
    (r"nkeys == 289\b", "nkeys == 310", None),
    (r"== 365\)", "== 389)", "range_real = \")"),
    (r"\(EXP\.sum and 365 or 96\)", "(EXP.sum and 389 or 96)", None),
    (r"== 43\)", "== 47)", "target_class = \")"),
    (r"(trigger = \"enemy_wander\"'\)) == 20\b", r"\1 == 42", None),
    # stale counts found by run 1: Arcane Vassal adds an ally_range_real field (57 -> 58, harnesses 98/99/104), Magma
    # Storm a second unbounded entry (1 -> 2, harness 102), Befuddlement joins enemy_fast_near_ally (8 -> 9, harnesses
    # 135/137) and Winged Staff joins enemy_area_drain (7 -> 8, harness 157)
    (r"(ally_range_real = \"\)) == 57\b", r"\1 == 58", None),
    (r"(unbounded = true,\"\)) == 1\b", r"\1 == 2", None),
    (r"(trigger = \"enemy_fast_near_ally\"'\)) == 8\b", r"\1 == 9", None),
    (r"(trigger = \"enemy_area_drain\"'\)) == 7\b", r"\1 == 8", None),
]
src = open(SRC, encoding="utf-8").read()
lines = src.split("\n")
changed, hits = [], {a: 0 for a, _, _ in PIN_RULES}
for i, ln in enumerate(lines):
    if ln.lstrip().startswith("--"):
        continue
    new = ln
    for a, b, guard in PIN_RULES:
        if guard is not None and guard not in new:
            continue
        new2, n = re.subn(a, b, new)
        if n:
            hits[a] += n
            new = new2
    if new != ln:
        changed.append(i + 1)
        lines[i] = new
src = "\n".join(lines)
print("count-pin lines rebased:", len(changed), "| rules with no hit:", [a for a, v in hits.items() if v == 0])
TIP = ('    enemy_wander = "When armed and standing still, fires at a standing enemy blob worth the most, with none of our '
       'units within the blast\'s wandering reach",\n')
NEW_TIP = TIP + (
    '    enemy_strike = "When armed and standing still, strikes the ground under the most valuable standing single enemy, '
    'with none of our units near",\n'
    '    ally_blast = "When armed, fires on the friendly unit (or itself) with the most enemy value around it",\n')
assert src.count(TIP) == 1, src.count(TIP)
src = src.replace(TIP, NEW_TIP)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h161()\n") == 1
src = src.replace("\nrun_h161()\n", "\nrun_h161()\nrun_h162()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
