#!/usr/bin/env python3
"""Build harness158.lua from harness157.lua for round 159 (group E). Older harnesses are never edited.

Pin rebases (code lines only; a rule with a guard only touches lines holding the guard):
  entries 834 -> 860, keys 889 -> 917 (26 entries / 28 keys), full-table iterations 1668 -> 1720,
  multi-use charge-gate keys 263 -> 271 (+8), wind-up keys 253 -> 258 (+5), range_real fields 329 -> 333 (+4),
  target classes 31 -> 33 (Slann Gold: commander; Deathmaster's Sigil: commander_ground);
  family counts: melee_unwavering 288 -> 299 (+11), charge_or_melee 36 -> 37 (Maneater Smoke Bomb), wavering_self
  3 -> 4 (Verminous Valour), enemy_ground_melee 74 -> 75 (Heaven's Flash), health_aura_ground 2 -> 3 (Slime Smoothie);
  the tooltip mirror gains the four new wordings.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_last_group_b_harness157\harness157.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_group_e_harness158\harness158.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h158_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 158 - ROUND 159: GROUP E (26 entries / 28 keys, 4 new families:
--   melee_clear, fly_dive, last_stand_clear, enemy_blob_vortex).
--   Edited vs harness157: this banner, the pin rebases listed in
--   tools/make_harness158.py, the tooltip mirror, run_h158 and its call.
--   RED control: H158_LIVE / H158_ANN on docs/backups/round159/pre159_*.lua.
-- ============================================================================
"""
PIN_RULES = [
    (r"== 834\b", "== 860", None),
    (r"== 889\b", "== 917", None),
    (r"it == 1668\b", "it == 1720", None),
    (r"entries = 834, keys = 889", "entries = 860, keys = 917", None),
    (r"want 834\b", "want 860", None),
    (r"FULL 834-entry table", "FULL 860-entry table", None),
    (r"834 abilities per pass", "860 abilities per pass", None),
    (r"table of 834 after round 158", "table of 860 after round 159", None),
    (r"\(12 air-drop entries of 834\)", "(12 air-drop entries of 860)", None),
    (r"\(RED_MODE and 0 or 263\)", "(RED_MODE and 0 or 271)", None),
    (r"nkeys == 253\b", "nkeys == 258", None),
    (r"== 329\)", "== 333)", "range_real = \")"),
    (r"\(EXP\.sum and 329 or 96\)", "(EXP.sum and 333 or 96)", None),
    (r"== 31\)", "== 33)", "target_class = \")"),
    # family counts
    (r"(trigger = \"melee_unwavering\"'\)) == 288", r"\1 == 299", None),
    (r"\bmu == 288\)", "mu == 299)", None),
    (r"mu = 288,", "mu = 299,", None),
    (r"(trigger = \"charge_or_melee\"'\)) == 36", r"\1 == 37", None),
    (r"(trigger = \"wavering_self\"'\)) == 3\b", r"\1 == 4", None),
    (r"(trigger = \"enemy_ground_melee\"'\)) == 74", r"\1 == 75", None),
    (r"\(RED_MODE and 1 or 74\)", "(RED_MODE and 1 or 75)", None),
    (r"(trigger = \"health_aura_ground\"'\)) == 2\b", r"\1 == 3", None),
    # stale mirrors found by run 1: harness 81's charge_or_melee count, harness 102's enemy_ground_melee sum, and
    # harness 157's enemy_commander_value (Slann Gold and Deathmaster's Sigil join the Leach Orb: 1 -> 3)
    (r"\bcm == 36\)", "cm == 37)", None),
    (r"\(EXP\.sum and 74 or 1\)", "(EXP.sum and 75 or 1)", None),
    (r"(trigger = \"enemy_commander_value\"'\)) == 1\b", r"\1 == 3", None),
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
TIP = '    enemy_commander_value = "When armed, fires on the most valuable enemy lord or hero in range",\n'
R = [
    (TIP, TIP +
     '    melee_clear = "When armed, fires when this unit is in melee and none of our other units are inside its blast",\n'
     '    fly_dive = "When armed, fires when this unit is flying over an enemy and none of our other units are inside its '
     'blast",\n'
     '    last_stand_clear = "When armed, fires when this unit is at 10% health or less in melee and none of our other '
     'units are inside its blast",\n'
     '    enemy_blob_vortex = "When armed and standing still, fires at the enemy infantry where the blast destroys the most '
     'value, when it hits enough soldiers and none of ours are near",\n'),
]
for a, b in R:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h157()\n") == 1
src = src.replace("\nrun_h157()\n", "\nrun_h157()\nrun_h158()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
