#!/usr/bin/env python3
"""Build harness163.lua from harness162.lua for round 164 (the friendly-fire breaths). Older harnesses are never edited.

Pin rebases (code lines only; a rule with a guard only touches lines holding the guard):
  entries 918 -> 946, keys 975 -> 1003 (28 entries / 28 keys), full-table iterations 1836 -> 1892,
  multi-use charge-gate keys 304 -> 328 (+24), wind-up keys 310 -> 334 (+24), range_real fields 389 -> 417 (+28),
  target classes 47 -> 56 (+9 not_flying); enemy_wave 12 -> 30 (harness 161), enemy_wander 42 -> 43 (harnesses 161,
  162); the tooltip mirror gains the three new wordings. Further rebases only where a full run proves them.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_placed_areas_harness162\harness162.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_breaths_harness163\harness163.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h163_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 163 - ROUND 164: THE FRIENDLY-FIRE BREATHS (28 entries, 3 new
--   families: enemy_wave_charge, enemy_cone, enemy_sweep; a caster's own wave
--   no longer blocks it; the game's no-melee rule joins the WW caster gate).
--   Edited vs harness162: this banner, the pin rebases listed in
--   tools/make_harness163.py, the tooltip mirror, run_h163 and its call.
--   RED control: H163_LIVE / H163_ANN on docs/backups/round164/pre164_*.lua.
-- ============================================================================
"""
PIN_RULES = [
    (r"== 918\b", "== 946", None),
    (r"== 975\b", "== 1003", None),
    (r"it == 1836\b", "it == 1892", None),
    (r"entries = 918, keys = 975", "entries = 946, keys = 1003", None),
    (r"want 918\b", "want 946", None),
    (r"FULL 918-entry table", "FULL 946-entry table", None),
    (r"918 abilities per pass", "946 abilities per pass", None),
    (r"table of 918 after round 163", "table of 946 after round 164", None),
    (r"\(12 air-drop entries of 918\)", "(12 air-drop entries of 946)", None),
    (r"\(RED_MODE and 0 or 304\)", "(RED_MODE and 0 or 328)", None),
    (r"nkeys == 310\b", "nkeys == 334", None),
    (r"== 389\)", "== 417)", "range_real = \")"),
    (r"\(EXP\.sum and 389 or 96\)", "(EXP.sum and 417 or 96)", None),
    (r"== 47\)", "== 56)", "target_class = \")"),
    (r"(trigger = \"enemy_wave\"'\)) == 12\b", r"\1 == 30", None),
    (r"(trigger = \"enemy_wander\"'\)) == 42\b", r"\1 == 43", None),
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
TIP = '    ally_blast = "When armed, fires on the friendly unit (or itself) with the most enemy value around it",\n'
NEW_TIP = TIP + (
    '    enemy_wave_charge = "When armed and standing still, fires its wave at a charging enemy whose path holds none of our '
    'units",\n'
    '    enemy_cone = "When armed and standing still, breathes at a standing enemy when the cone holds the most enemy value '
    'and none of our other units",\n'
    '    enemy_sweep = "When armed, sweeps the closest enemy in melee when none of our other units are within its reach",\n')
assert src.count(TIP) == 1, src.count(TIP)
src = src.replace(TIP, NEW_TIP)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h162()\n") == 1
src = src.replace("\nrun_h162()\n", "\nrun_h162()\nrun_h163()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
