#!/usr/bin/env python3
"""Build harness169.lua from harness168.lua for round 170 (Potion of Foolhardiness moves from melee_unwavering to
charge_or_wavering). Older harnesses are never edited.

Rebases (the entry moved family, user ruling 2026-11-17 "Charge or wavering"; labels keep their historical numbers, as
in earlier rounds):
  * every pin of the melee_unwavering entry count: 299 -> 298 (18 checks; the EXP tables of harness 100/101 too);
  * every pin of the charge_or_wavering entry count: 1 -> 2 (3 checks).
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_sensor_visibility_harness168\harness168.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_foolhardiness_harness169\harness169.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h169_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 169 - ROUND 170: POTION OF FOOLHARDINESS ON charge_or_wavering.
--   Edited vs harness168: this banner, the count rebases listed in
--   tools/make_harness169.py (melee_unwavering 299 -> 298, charge_or_wavering 1 -> 2),
--   run_h169 and its call.
--   RED control: H169_LIVE / H169_ANN on docs/backups/round170/pre170_*.lua.
-- ============================================================================
"""
R = [
    ("""'trigger = "melee_unwavering"') == 299""", """'trigger = "melee_unwavering"') == 298""", 14),
    ("      mu == 299)\n", "      mu == 298)   -- HARNESS 169: Foolhardiness moved out\n", 1),
    ("mu = 299,", "mu = 298,", 2),
    ("""cp(s, 'trigger = "charge_or_wavering"') == 1""", """cp(s, 'trigger = "charge_or_wavering"') == 2""", 3),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h168()\n") == 1
src = src.replace("\nrun_h168()\n", "\nrun_h168()\nrun_h169()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
