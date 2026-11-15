#!/usr/bin/env python3
"""Build harness157.lua from harness156.lua for round 158 (the last group B attacks). Older harnesses are never edited.

Pin rebases (code lines only; a rule with a guard only touches lines holding the guard):
  entries 822 -> 834, keys 877 -> 889 (12 entries / 12 keys), full-table iterations 1644 -> 1668,
  multi-use charge-gate keys 258 -> 263 (+5), wind-up keys 249 -> 253 (+4), range_real fields 317 -> 329 (+12),
  target classes 29 -> 31 (Storm of the Night: flying; Dweomer Leach Orb: commander);
  enemy_melee 34 -> 35 (Preyton Horns), enemy_melee_or_fast 2 -> 4 (Ethrac's Brazier, Storm of the Night);
  the tooltip mirror gains the two new wordings.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_drains_harness156\harness156.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_last_group_b_harness157\harness157.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h157_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 157 - ROUND 158: THE LAST GROUP B ATTACKS (12 entries, 2 new
--   families: enemy_area_drain, enemy_commander_value).
--   Edited vs harness156: this banner, the pin rebases listed in
--   tools/make_harness157.py, the tooltip mirror, run_h157 and its call.
--   RED control: H157_LIVE / H157_ANN on docs/backups/round158/pre158_*.lua.
-- ============================================================================
"""
PIN_RULES = [
    (r"== 822\b", "== 834", None),
    (r"== 877\b", "== 889", None),
    (r"it == 1644\b", "it == 1668", None),
    (r"entries = 822, keys = 877", "entries = 834, keys = 889", None),
    (r"want 822\b", "want 834", None),
    (r"FULL 822-entry table", "FULL 834-entry table", None),
    (r"822 abilities per pass", "834 abilities per pass", None),
    (r"table of 822 after round 157", "table of 834 after round 158", None),
    (r"\(12 air-drop entries of 822\)", "(12 air-drop entries of 834)", None),
    (r"\(RED_MODE and 0 or 258\)", "(RED_MODE and 0 or 263)", None),
    (r"nkeys == 249\b", "nkeys == 253", None),
    (r"== 317\)", "== 329)", "range_real = \")"),
    (r"\(EXP\.sum and 317 or 96\)", "(EXP.sum and 329 or 96)", None),
    (r"== 29\)", "== 31)", "target_class = \")"),
    # family counts: Preyton Horns joins enemy_melee (34 -> 35); Ethrac's Brazier and Storm of the Night join
    # enemy_melee_or_fast (2 -> 4)
    (r"cp\(s, 'trigger = \"enemy_melee\"'\) == 34", "cp(s, 'trigger = \"enemy_melee\"') == 35", None),
    (r"cp\(s, 'trigger = \"enemy_melee_or_fast\"'\) == 2", "cp(s, 'trigger = \"enemy_melee_or_fast\"') == 4", None),
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
    ('    enemy_execute = "When armed, fires on the most valuable enemy in range whose health is at or below the execute '
     'line",\n',
     '    enemy_execute = "When armed, fires on the most valuable enemy in range whose health is at or below the execute '
     'line",\n'
     '    enemy_area_drain = "When armed and standing still, fires on the enemy infantry in range worth the most per '
     'soldier, with enough soldiers for every strike",\n'
     '    enemy_commander_value = "When armed, fires on the most valuable enemy lord or hero in range",\n'),
]
for a, b in R:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h156()\n") == 1
src = src.replace("\nrun_h156()\n", "\nrun_h156()\nrun_h157()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
