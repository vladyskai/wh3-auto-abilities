#!/usr/bin/env python3
"""Build harness160.lua from harness159.lua for round 161 (the ally melee buffs start armed). Older harnesses are never edited.

No roster change (860 entries / 917 keys). Pin rebases are added below only where a full run proves an earlier pin
encoded the ally melee buffs starting unarmed (each one documented in the round doc)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_beastmen_fixes_harness159\harness159.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_ally_buffs_armed_harness160\harness160.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h160_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 160 - ROUND 161: THE 14 ALLY MELEE BUFFS START ARMED (user
--   ruling 2026-11-16, "Whole family").
--   Edited vs harness159: this banner, the pin rebases listed in
--   tools/make_harness160.py, run_h160 and its call.
--   RED control: H160_LIVE / H160_ANN on docs/backups/round161/pre161_*.lua.
-- ============================================================================
"""
PIN_RULES = []
src = open(SRC, encoding="utf-8").read()
lines = src.split("\n")
hits = {a: 0 for a, _, _ in PIN_RULES}
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
    lines[i] = new
src = "\n".join(lines)
print("rules with no hit:", [a for a, v in hits.items() if v == 0])
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h159()\n") == 1
src = src.replace("\nrun_h159()\n", "\nrun_h159()\nrun_h160()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
