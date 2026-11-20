#!/usr/bin/env python3
"""Build harness180.lua from harness179.lua for round 181 (Land Mine "A", Surprise Squig! blob with clearance, the
range fixes). Older harnesses are never edited.

Rebases: see R; every '935' (entries) becomes 936 (the Lord of Undeath split), 1870 (2 x 935) becomes 1872."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows4_harness179\harness179.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_landmine_squig_harness180\harness180.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h180_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 180 - ROUND 181: LAND MINE (60 soldiers in the blast), SURPRISE SQUIG! (blob with
--   clearance), THE RANGE FIXES (Curse of Khsar, Ravaging Swarm x2, the Lord of Undeath split).
--   Edited vs harness179: this banner, the rebases listed in tools/make_harness180.py,
--   run_h180 and its call.
--   RED control: H180_LIVE / H180_ANN on docs/backups/round181/pre181_*.lua.
-- ============================================================================
"""
LABELS = (
    '    melee_clear_block = "When armed, fires in melee when none of our other units is inside its blast and at least 60 enemy soldiers are",\n'
    '    enemy_summon_blob = "When armed, places the summon under the standing enemy block worth the most inside its explosion, none of ours near",\n')
R = [
    # the TIP mirror: the 2 new labels
    ('    charge_or_tired = "When armed, fires when charging or tired",\n',
     '    charge_or_tired = "When armed, fires when charging or tired",\n'
     '    -- HARNESS 180: the round-181 labels\n' + LABELS, 1),
    # the counts
    ("""'trigger = "melee_clear"') == 5""", """'trigger = "melee_clear"') == 4""", 1),   # Land Mine
    ('range_real = ") == 417', 'range_real = ") == 418', 2),   # the Lord of Undeath split
    ("EXP.sum and 417 or 96))", "EXP.sum and 418 or 96))", 1),
    ("1870", "1872", 1),   # 2 x 936
    # h179 CA8: Land Mine's card names its 60-soldier line now (round 181)
    ('          local c_ok = by.land_mine == "Fires in melee unless wavering, clear of allies"\n',
     '          local c_ok = by.land_mine == "Fires in melee unless wavering, clear of allies, with 60+ enemies in the blast"   -- HARNESS 180\n', 1),
    # h179 0zz28: round 180 pinned "Land Mine NOT moved" (row 98 waited); the user ruled "A" (round 181)
    ("""cp(s, "melee_clear_block") == 0 and""", """cp(s, 'trigger = "melee_clear_block"') == 1 and   -- HARNESS 180: row 98 built (A)\n       """, 1),
    # h97 the r30 family: Ravaging Swarm's real range is 100 m (round 181)
    ('    { real = 30,  bound = 21,  marker = "dispatch_the_swarm_attack", key = "wh3_dlc29_hero_active_dispatch_the_swarm_attack", ground = false },\n',
     '    { real = 100, bound = 70,  marker = "dispatch_the_swarm_attack", key = "wh3_dlc29_hero_active_dispatch_the_swarm_attack", ground = false },   -- HARNESS 180: its real 100 m\n', 1),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
n935 = len(re.findall(r"(?<!\d)935(?!\d)", src))
src = re.sub(r"(?<!\d)935(?!\d)", "936", src)
print("935 -> 936:", n935)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h179()\n") == 1
src = src.replace("\nrun_h179()\n", "\nrun_h179()\nrun_h180()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
