#!/usr/bin/env python3
"""Build harness155.lua from harness154.lua for round 156 (the magic missiles). Older harnesses are never edited.

Pin rebases (code lines only; a rule with a guard only touches lines holding the guard):
  entries 799 -> 810, keys 854 -> 865 (11 entries / 11 keys), full-table iterations 1598 -> 1620,
  multi-use charge-gate keys 246 -> 250 (+4), wind-up keys 235 -> 241 (+6), range_real fields 294 -> 305 (+11),
  target classes 26 -> 28 (Dead Eye and Focused Shot: "single");
  section 0zr (round 146): "Dead Eye and Focused Shot are absent" becomes "they are not on enemy_blob" (they now ride
  enemy_single_shot);
  the tooltip mirror gains the five new wordings.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_all_spot_harness154\harness154.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_magic_missiles_harness155\harness155.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h155_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 155 - ROUND 156: THE MAGIC MISSILES (11 entries, 5 new families:
--   enemy_large_shot, enemy_single_shot, enemy_infantry_shot,
--   enemy_melee_or_fast, enemy_melee_or_shooting).
--   Edited vs harness154: this banner, the pin rebases listed in
--   tools/make_harness155.py, the tooltip mirror, run_h155 and its call.
--   RED control: H155_LIVE / H155_ANN on docs/backups/round156/pre156_*.lua.
-- ============================================================================
"""
PIN_RULES = [
    (r"== 799\b", "== 810", None),
    (r"== 854\b", "== 865", None),
    (r"it == 1598\b", "it == 1620", None),
    (r"entries = 799, keys = 854", "entries = 810, keys = 865", None),
    (r"want 799\b", "want 810", None),
    (r"FULL 799-entry table", "FULL 810-entry table", None),
    (r"799 abilities per pass", "810 abilities per pass", None),
    (r"table of 799 after round 146", "table of 810 after round 156", None),
    (r"\(12 air-drop entries of 799\)", "(12 air-drop entries of 810)", None),
    (r"\(RED_MODE and 0 or 246\)", "(RED_MODE and 0 or 250)", None),
    (r"nkeys == 235\b", "nkeys == 241", None),
    (r"== 294\)", "== 305)", "range_real = \")"),
    (r"\(EXP\.sum and 294 or 96\)", "(EXP.sum and 305 or 96)", None),
    (r"== 26\)", "== 28)", "target_class = \")"),
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
    ('        and raw_find(s, "wh3_dlc26_character_abilities_dead_eye", 1, true) == nil\n'
     '        and raw_find(s, "wh2_dlc13_lord_abilities_kill_shot", 1, true) == nil\n',
     '        -- ROUND 156: Dead Eye and Focused Shot now ride enemy_single_shot; never enemy_blob\n'
     '        and raw_find(s, \'trigger = "enemy_blob",\\n\\t\\tbadge = "zz_auto_badge_dead_eye"\', 1, true) == nil\n'
     '        and raw_find(s, \'trigger = "enemy_blob",\\n\\t\\tbadge = "zz_auto_badge_focused_shot"\', 1, true) == nil\n'),
    ('    enemy_blob = "When armed and standing still, fires at the enemy infantry where the blast destroys the most value, '
     'when it hits enough soldiers and none of ours are near",\n',
     '    enemy_blob = "When armed and standing still, fires at the enemy infantry where the blast destroys the most value, '
     'when it hits enough soldiers and none of ours are near",\n'
     '    enemy_large_shot = "When armed, fires on the most valuable large enemy in range with none of yours near it, '
     'otherwise on the most armoured enemy infantry",\n'
     '    enemy_single_shot = "When armed and standing still, fires on the most valuable single-entity enemy in range '
     '(lord, hero or monster) with none of yours near it",\n'
     '    enemy_infantry_shot = "When armed and standing still, fires on the enemy infantry in range worth the most per '
     'soldier, with none of yours near it",\n'
     '    enemy_melee_or_fast = "When armed, fires on the closest enemy in range that is fighting in melee, otherwise on a '
     'fast enemy closing on your units",\n'
     '    enemy_melee_or_shooting = "When armed, fires on the closest enemy in range that is fighting in melee, otherwise on '
     'the closest enemy missile unit that is shooting",\n'),
]
for a, b in R:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h154()\n") == 1
src = src.replace("\nrun_h154()\n", "\nrun_h154()\nrun_h155()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
