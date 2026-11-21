#!/usr/bin/env python3
"""Build harness189.lua from harness188.lua for round 190 (the animation decides in every shot trigger; user
2026-11-21: "Amber Bow canceled his movement, not good" -> "Fix the 8"). Older harnesses are never edited.
New: run_h189 (tools/h189_section.lua). Rebases: none planned (any found by the full run are listed here)."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_lineoffire_harness188\harness188.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_shotstill_harness189\harness189.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h189_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 189 - ROUND 190: THE ANIMATION DECIDES IN EVERY SHOT TRIGGER (user 2026-11-21: "Amber Bow canceled his
--   movement, not good" -> "Fix the 8").
--   Edited vs harness188: this banner, the rebases listed in tools/make_harness189.py, run_h189 and its call.
--   RED control: H189_LIVE / H189_ANN on docs/backups/round190/pre190_*.lua.
-- ============================================================================
"""
R = []
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h188()\n") == 1
src = src.replace("\nrun_h188()\n", "\nrun_h188()\nrun_h189()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
