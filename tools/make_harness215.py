#!/usr/bin/env python3
"""Build harness215.lua from harness214.lua for round 217 (tuning: the group walk, the card cadence). Older harnesses
are never edited. Edits: the banner, run_h215 and its call, and the rebased pins listed in PINS.
With DEV=<path> it writes a development copy that runs ONLY run_h215 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_walkscope_harness214\harness214.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_groupcards_harness215\harness215.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h215_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 215 - ROUND 217 (tuning): a group's wheel shows only shared abilities (no whole-HUD walk for the rest),
--   the unit cards are read 5 times a second as soon as the game accepted a selection callback.
--   Edited vs harness214: this banner, run_h215 and its call, the rebased pins.
--   RED control: H215_LIVE / H215_ANN on docs/backups/round217/pre217_*.lua.
-- ============================================================================
"""
# the pins rebased in this round: (old text, new text, how many times it occurs)
PINS = [
    # harness 76 DET and BL: ONE UI tick was one card sweep. The callbacks are registered in these worlds, so since
    # round 217 the cards are read every 4th UI tick: four ticks hold exactly one sweep.
    ('    reset_cards(W)\n    ui(W)\n    local swept = swept_ids(W)\n',
     '    reset_cards(W)\n    ui(W); ui(W); ui(W); ui(W)   -- HARNESS 215: one sweep in four ticks (was one tick)\n'
     '    local swept = swept_ids(W)\n', 2),
    # harness 76 BL2 / BL3: the re-sweep after a card turns 'selected' was one tick, now four
    ('    W.card_comps["6103"].state = "selected"\n    reset_cards(W)\n    ui(W)\n',
     '    W.card_comps["6103"].state = "selected"\n    reset_cards(W)\n    ui(W); ui(W); ui(W); ui(W)   -- HARNESS 215\n', 1),
    # harness 213 CD1a compared the reads BEFORE the first selection event with those after it (need at most 30%).
    # Since round 217 the reads before the event are already at the slow rate: both must be at most 30% of one read
    # per card and tick (3 cards x 40 ticks = 120). Harness 215 CR1 carries the RED control for the new rule.
    ('        local good = (before > 0 and share <= 0.30)\n',
     '        local good = (before > 0 and before <= 36 and after <= 36)   -- HARNESS 215: both at the slow rate\n', 1),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h214()\n") == 1
    src = src.replace("\nrun_h214()\n", "\nrun_h214()\nrun_h215()\n")
    for old, new, n in PINS:
        assert src.count(old) == n, (old, src.count(old))
        src = src.replace(old, new)
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!215)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
