#!/usr/bin/env python3
"""Build harness211.lua from harness210.lua for round 213 (tuning: the cost of a selection). Older harnesses are never
edited. Edits: the banner, run_h211 and its call, and the rebased pins listed in PINS (documented in the round's
tracker section).
With DEV=<path> it writes a development copy that runs ONLY run_h211 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_transform_harness210\harness210.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_selectcost_harness211\harness211.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h211_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 211 - ROUND 213 (tuning): THE COST OF A SELECTION (the HUD walk's retries are spaced out).
--   Edited vs harness210: this banner, run_h211 and its call, the rebased pins.
--   RED control: H211_LIVE / H211_ANN on docs/backups/round213/pre213_*.lua.
-- ============================================================================
"""
# the pins rebased in this round: (old text, new text, how many times it occurs)
PINS = [
    # harness 79 B2c: the LATER selection of a unit whose button never came in a whole window. Round 213 remembers
    # that unit: the fresh window gives one walk on the event and ONE retry 4 ticks later, not a retry every 4th tick
    ("    local c = (one == 1) and (W.hud_walks == 1 + brisk2)\n",
     "    local c = (one == 1) and (W.hud_walks == 2)   -- HARNESS 211: the event walk and one retry (was 1 + brisk2)\n", 1),
    ('      .. "(one=" .. one .. ", total=" .. W.hud_walks .. ", want " .. (1 + brisk2) .. ") - anti-regression", c)\n',
     '      .. "(one=" .. one .. ", total=" .. W.hud_walks .. ", want 2 since round 213) - anti-regression", c)\n', 1),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h210()\n") == 1
    src = src.replace("\nrun_h210()\n", "\nrun_h210()\nrun_h211()\n")
    for old, new, n in PINS:
        assert src.count(old) == n, (old, src.count(old))
        src = src.replace(old, new)
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!211)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
