#!/usr/bin/env python3
"""Build harness168.lua from harness167.lua for round 169 (every enemy read skips hidden enemies). Older harnesses are
never edited. No pin needed a rebase (harness 167 stays green on the round-169 source)."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_anim_visibility_harness167\harness167.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_sensor_visibility_harness168\harness168.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h168_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 168 - ROUND 169: EVERY ENEMY READ SKIPS HIDDEN ENEMIES (the air drop,
--   the Farsight / Mist 'just beyond range' read, the contact set).
--   Edited vs harness167: this banner, run_h168 and its call (no rebase).
--   RED control: H168_LIVE / H168_ANN on docs/backups/round169/pre169_*.lua.
-- ============================================================================
"""
src = open(SRC, encoding="utf-8").read()
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h167()\n") == 1
src = src.replace("\nrun_h167()\n", "\nrun_h167()\nrun_h168()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
