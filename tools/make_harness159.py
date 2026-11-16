#!/usr/bin/env python3
"""Build harness159.lua from harness158.lua for round 160 (the Beastmen-battle fixes). Older harnesses are never edited.

No roster change (860 entries / 917 keys). Pin rebases are added below only where a full run proves an earlier pin
encoded the replaced 2.5 s instant hold (each one documented in the round doc)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_group_e_harness158\harness158.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_beastmen_fixes_harness159\harness159.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h159_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 159 - ROUND 160: THE BEASTMEN-BATTLE FIXES (when_ready skips a
--   routing unit; an instant ability holds its unit for one poll, not 2.5 s).
--   Edited vs harness158: this banner, the pin rebases listed in
--   tools/make_harness159.py, run_h159 and its call.
--   RED control: H159_LIVE / H159_ANN on docs/backups/round160/pre160_*.lua.
-- ============================================================================
"""
PIN_RULES = [
    # harness 81/107 B3b2: Deadly Onslaught and Foe-Seeker are both INSTANT (no wind_up_time), so the per-unit window
    # after the first is now one poll, not the 2.5 s (10-poll) minimum. B3b (never on the same poll) is unchanged.
    (r"the second no sooner than one full window \(10 polls\) after the first",
     "the second no sooner than one poll after the first (both instant, round 160)", None),
    (r"math\.abs\(first_at\[ONS\] - first_at\[FS_MAIN\]\) >= 10\)", "math.abs(first_at[ONS] - first_at[FS_MAIN]) >= 1)",
     None),
    # harness 140 S2 / P2: the instant helper (Strike of Tombs, Blessed Blade of Ptra) no longer holds the caster for
    # 2.5 s, so the ability under test fires at poll 2 / 3 instead of 11 / 12; the counting window is cut to end before
    # its 2 s repeat (the mock accepts every repeat): S2 16 -> 9 polls, P2 23 -> 10 polls.
    (r"\{ TOM, SOT \}, TOM, 16, 1, nil, 0 \}", "{ TOM, SOT }, TOM, 9, 1, nil, 0 }", None),
    (r"\{ SCR, SOT, BLD \}, SCR, 23, 1, nil, 0 \}", "{ SCR, SOT, BLD }, SCR, 10, 1, nil, 0 }", None),
]
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
assert src.count("\nrun_h158()\n") == 1
src = src.replace("\nrun_h158()\n", "\nrun_h158()\nrun_h159()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
