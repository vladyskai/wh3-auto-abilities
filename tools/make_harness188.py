#!/usr/bin/env python3
"""Build harness188.lua from harness187.lua for round 189 (the line of fire: the 35 'Requires line of sight to the
target' entries cast only along a line clear of every other unit and of the ground; user ruling 2026-11-21).
Older harnesses are never edited.

Rebase (R): load_world sets the TEST-ONLY global ZZ_AUTO_TEST_NO_LOS for every world that does not set W.los_on. The
older worlds put most units at the same spot (0, 0, 0) and have no ground; the line of fire is only proved in the new
section, whose worlds place every unit on a ground (the same pattern as ZZ_AUTO_TEST_NO_DEFAULTS, round 151).
New: run_h188 (tools/h188_section.lua)."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_rangerule_harness187\harness187.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_lineoffire_harness188\harness188.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h188_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 188 - ROUND 189: THE LINE OF FIRE (user ruling 2026-11-21: "I would just do the check for terrain on
--   all 35 and units on all 35. Just let's be safe, and if it doesn't fire, that's okay.").
--   Edited vs harness187: this banner, load_world's ZZ_AUTO_TEST_NO_LOS line (tools/make_harness188.py),
--   run_h188 and its call.
--   RED control: H188_LIVE / H188_ANN on docs/backups/round189/pre189_*.lua.
-- ============================================================================
"""
R = [
    ("  ZZ_AUTO_TEST_NO_DEFAULTS = (W.defaults_on ~= true)\n",
     "  ZZ_AUTO_TEST_NO_DEFAULTS = (W.defaults_on ~= true)\n"
     "  -- ROUND 189: older worlds have no ground and stack units on one spot; they run without the line of fire. A world\n"
     "  -- that tests it sets W.los_on.\n"
     "  ZZ_AUTO_TEST_NO_LOS = (W.los_on ~= true)\n", 1),
    # 0zz16 (harness 167) counted two keys across the WHOLE file to pin the round-168 ANIM table's content (Volley of
    # High Arrows in it, the bound Fireball not). Round 189's LOS_TEXT names both keys, so the pin now reads the ANIM
    # table itself: same meaning, old counts 1 / 0 unchanged.
    ('        and cp(s, "wh2_main_character_abilities_volley_of_high_arrows;") == 1\n'
     '        and cp(s, "wh_main_spell_bound_fireball;") == 0)\n',
     '        and cp(s:match(\'FOURTH%.ANIM_TEXT = "[^"]*"\') or "", "wh2_main_character_abilities_volley_of_high_arrows;") == 1\n'
     '        and cp(s:match(\'FOURTH%.ANIM_TEXT = "[^"]*"\') or "", "wh_main_spell_bound_fireball;") == 0)   -- R189: the ANIM table only\n', 1),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h187()\n") == 1
src = src.replace("\nrun_h187()\n", "\nrun_h187()\nrun_h188()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
