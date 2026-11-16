#!/usr/bin/env python3
"""Build harness161.lua from harness160.lua for round 162 (the wandering winds). Older harnesses are never edited.

Pin rebases (code lines only; a rule with a guard only touches lines holding the guard):
  entries 860 -> 892, keys 917 -> 949 (32 entries / 32 keys), full-table iterations 1720 -> 1784,
  multi-use charge-gate keys 271 -> 287 (+16), wind-up keys 258 -> 289 (+31), range_real fields 333 -> 365 (+32),
  target classes 33 -> 43 (+10 not_flying); the tooltip mirror gains the two new wordings.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_ally_buffs_armed_harness160\harness160.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_wandering_winds_harness161\harness161.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h161_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 161 - ROUND 162: THE WANDERING WINDS (32 entries, 2 new families:
--   enemy_wave, enemy_wander).
--   Edited vs harness160: this banner, the pin rebases listed in
--   tools/make_harness161.py, the tooltip mirror, run_h161 and its call.
--   RED control: H161_LIVE / H161_ANN on docs/backups/round162/pre162_*.lua.
-- ============================================================================
"""
PIN_RULES = [
    (r"== 860\b", "== 892", None),
    (r"== 917\b", "== 949", None),
    (r"it == 1720\b", "it == 1784", None),
    (r"entries = 860, keys = 917", "entries = 892, keys = 949", None),
    (r"want 860\b", "want 892", None),
    (r"FULL 860-entry table", "FULL 892-entry table", None),
    (r"860 abilities per pass", "892 abilities per pass", None),
    (r"table of 860 after round 159", "table of 892 after round 162", None),
    (r"\(12 air-drop entries of 860\)", "(12 air-drop entries of 892)", None),
    (r"\(RED_MODE and 0 or 271\)", "(RED_MODE and 0 or 287)", None),
    (r"nkeys == 258\b", "nkeys == 289", None),
    (r"== 333\)", "== 365)", "range_real = \")"),
    (r"\(EXP\.sum and 333 or 96\)", "(EXP.sum and 365 or 96)", None),
    (r"== 33\)", "== 43)", "target_class = \")"),
    # harness 118's deleted-symbol list searched the bare substring "dwell", which the game's own key
    # wh3_main_spell_bound_the_dwellers_below now carries. Narrowed to " dwell" (with the leading space): every form the
    # round-118 deletion removed (docs/backups/round118/pre118: " dwell_ok", " dwell_text", the word " dwell" in prose)
    # starts with a space, the game key does not ("_dwellers"); zz_ad_dwell_purge stays its own token. One token for
    # one token, so the suite's boundary counts do not move.
    (r'"FOURTH\.ad_event", "ad_fired", "dwell", "short crossing", "proj=",',
     '"FOURTH.ad_event", "ad_fired", " dwell", "short crossing", "proj=",', None),
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
TIP = ('    enemy_blob_vortex = "When armed and standing still, fires at the enemy infantry where the blast destroys the most '
       'value, when it hits enough soldiers and none of ours are near",\n')
NEW_TIP = TIP + (
    '    enemy_wave = "When armed and standing still, fires its wave at a standing enemy whose path holds the most enemy '
    'value and none of our units",\n'
    '    enemy_wander = "When armed and standing still, fires at a standing enemy blob worth the most, with none of our '
    'units within the blast\'s wandering reach",\n')
assert src.count(TIP) == 1, src.count(TIP)
src = src.replace(TIP, NEW_TIP)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h160()\n") == 1
src = src.replace("\nrun_h160()\n", "\nrun_h160()\nrun_h161()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
