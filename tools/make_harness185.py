#!/usr/bin/env python3
"""Build harness185.lua from harness184.lua for round 186 (Warpstorm Scroll as a damage dealer). Older harnesses are
never edited.

Rebases: see R (each names the pin and why)."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_ruleshut3_harness184\harness184.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_warpstorm_harness185\harness185.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h185_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 185 - ROUND 186: WARPSTORM SCROLL AS A DAMAGE DEALER (NEW enemy_most_valuable: the
--   most valuable flying enemy, any number of models; no charge arm).
--   Edited vs harness184: this banner, the rebases listed in tools/make_harness185.py,
--   run_h185 and its call.
--   RED control: H185_LIVE / H185_ANN on docs/backups/round186/pre186_*.lua.
-- ============================================================================
"""
R = [
    # the TIP mirror: the new label
    ('    melee_or_self_shooting = "When armed, fires when this unit is in melee or shooting",\n',
     '    melee_or_self_shooting = "When armed, fires when this unit is in melee or shooting",\n'
     '    -- HARNESS 185: the round-186 label\n'
     '    enemy_most_valuable = "When armed, fires on the most valuable enemy in range that its target rule allows",\n', 1),
    # Warpstorm Scroll left enemy_single_drain (14 -> 13) for enemy_most_valuable
    ("""cp(s, 'trigger = "enemy_single_drain"') == 14""", """cp(s, 'trigger = "enemy_single_drain"') == 13""", 2),
    ('{ "warpstorm_scroll", "enemy_single_drain" }', '{ "warpstorm_scroll", "enemy_most_valuable" }', 1),
    # its card (harness 183, CA12)
    ('by.warpstorm_scroll == "Fires on the most valuable enemy monster or character; flying targets only"',
     'by.warpstorm_scroll == "Fires on the most valuable enemy; flying targets only"', 1),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h184()\n") == 1
src = src.replace("\nrun_h184()\n", "\nrun_h184()\nrun_h185()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
