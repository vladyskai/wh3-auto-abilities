#!/usr/bin/env python3
"""Build harness156.lua from harness155.lua for round 157 (the drains and the Executioner). Older harnesses are never
edited.

Pin rebases (code lines only; a rule with a guard only touches lines holding the guard):
  entries 810 -> 822, keys 865 -> 877 (12 entries / 12 keys), full-table iterations 1620 -> 1644,
  multi-use charge-gate keys 250 -> 258 (+8), wind-up keys 241 -> 249 (+8), range_real fields 305 -> 317 (+12),
  target classes 28 -> 29 (the base Executioner: commander);
  the tooltip mirror gains the two new wordings.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_magic_missiles_harness155\harness155.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_drains_harness156\harness156.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h156_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 156 - ROUND 157: THE DRAINS AND THE EXECUTIONER (12 entries, 2 new
--   families: enemy_single_drain, enemy_execute).
--   Edited vs harness155: this banner, the pin rebases listed in
--   tools/make_harness156.py, the tooltip mirror, run_h156 and its call.
--   RED control: H156_LIVE / H156_ANN on docs/backups/round157/pre157_*.lua.
-- ============================================================================
"""
PIN_RULES = [
    (r"== 810\b", "== 822", None),
    (r"== 865\b", "== 877", None),
    (r"it == 1620\b", "it == 1644", None),
    (r"entries = 810, keys = 865", "entries = 822, keys = 877", None),
    (r"want 810\b", "want 822", None),
    (r"FULL 810-entry table", "FULL 822-entry table", None),
    (r"810 abilities per pass", "822 abilities per pass", None),
    (r"table of 810 after round 156", "table of 822 after round 157", None),
    (r"\(12 air-drop entries of 810\)", "(12 air-drop entries of 822)", None),
    (r"\(RED_MODE and 0 or 250\)", "(RED_MODE and 0 or 258)", None),
    (r"nkeys == 241\b", "nkeys == 249", None),
    (r"== 305\)", "== 317)", "range_real = \")"),
    (r"\(EXP\.sum and 305 or 96\)", "(EXP.sum and 317 or 96)", None),
    (r"== 28\)", "== 29)", "target_class = \")"),
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
R = [
    ('    enemy_melee_or_shooting = "When armed, fires on the closest enemy in range that is fighting in melee, otherwise on '
     'the closest enemy missile unit that is shooting",\n',
     '    enemy_melee_or_shooting = "When armed, fires on the closest enemy in range that is fighting in melee, otherwise on '
     'the closest enemy missile unit that is shooting",\n'
     '    enemy_single_drain = "When armed and standing still, fires on the most valuable single-entity enemy in range '
     '(lord, hero or monster)",\n'
     '    enemy_execute = "When armed, fires on the most valuable enemy in range whose health is at or below the execute '
     'line",\n'),
]
for a, b in R:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h155()\n") == 1
src = src.replace("\nrun_h155()\n", "\nrun_h155()\nrun_h156()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
