#!/usr/bin/env python3
"""Build harness151.lua from harness150.lua for round 152. Older harnesses are never edited.

Pin rebases (documented in docs/WH3_round152_no_hold.md):
  * section 150 world LG2 tested the whole-map HOLD (no cast); the hold is gone, so LG2 now expects ONE cast at the
    Grave Guard (the user's ruling 2026-11-15);
  * section 150's token check named blob_large_hold; it now names blob_not_flying (the hold function is removed).
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_large_defaults_harness150\harness150.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_no_hold_harness151\harness151.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h151_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 151 - ROUND 152: NO WHOLE-MAP HOLD, LARGE FIRST SKIPS FLIERS, 90
--   DEGREES FOR EVERY PREFER-CENTRAL ATTACK, 'TIRED' ARMED BY DEFAULT, THE ALL
--   BADGE ON SCREEN.
--   Edited vs harness150: this banner, the LG2 / 0zw rebases in
--   tools/make_harness151.py, run_h151 and its call.
--   RED control: H151_LIVE / H151_ANN on docs/backups/round152/pre152_*.lua.
-- ============================================================================
"""
src = open(SRC, encoding="utf-8").read()
R = [
    ('    { "LG2. Soporific: the dragon is 200 m away, Grave Guard in range -> no cast (the hold)",\n',
     '    { "LG2. Soporific: the dragon is 200 m away, Grave Guard in range -> ONE cast at the Grave Guard (round 152: no hold)",\n'),
    ('      "unit_abilities_soporific_breath", SO, 0, 1, nil, 5 },\n    { "LG3.',
     '      "unit_abilities_soporific_breath", SO, 1, 1, 5, 5 },   -- ROUND 152: was 0 (the hold)\n    { "LG3.'),
    ('        and raw_find(s, "function FOURTH.blob_large_hold(m, key, inf_value)", 1, true) ~= nil\n',
     '        and raw_find(s, "function FOURTH.blob_not_flying(u)", 1, true) ~= nil   -- ROUND 152: the hold is gone\n'),
]
for a, b in R:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h150()\n") == 1
src = src.replace("\nrun_h150()\n", "\nrun_h150()\nrun_h151()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
