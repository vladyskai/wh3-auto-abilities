#!/usr/bin/env python3
"""Build harness213.lua from harness212.lua for round 215 (tuning: the mod's own cost). Older harnesses are never
edited. Edits: the banner, run_h213 and its call, and the rebased pins listed in PINS.
With DEV=<path> it writes a development copy that runs ONLY run_h213 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_perfprobe_harness212\harness212.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_owncost_harness213\harness213.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h213_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 213 - ROUND 215 (tuning): THE MOD'S OWN COST (no walk storm before the first selection, the unit cards
--   read 5 times a second once the selection events arrive).
--   Edited vs harness212: this banner, run_h213 and its call, the rebased pins.
--   RED control: H213_LIVE / H213_ANN on docs/backups/round215/pre215_*.lua.
-- ============================================================================
"""
# the pins rebased in this round: (old text, new text, how many times it occurs)
PINS = [
    # harness 58 C5: a selection only the CARD reports, while the selection events are alive. The cards are read every
    # 4th UI tick then (round 215), so the reconciliation needs up to 4 ticks: the world waits 5, not 2
    ('    W.card_comps["1002"].state = "selected"\n    ui(W)\n    ui(W)\n    if TAG == "[live] " then\n'
     '      check(TAG .. "C5: the card-only selection',
     '    W.card_comps["1002"].state = "selected"\n    ui(W)\n    ui(W)\n    ui(W); ui(W); ui(W)   -- HARNESS 213\n'
     '    if TAG == "[live] " then\n      check(TAG .. "C5: the card-only selection', 1),
    ('    W.card_comps["1002"].state = "active"\n    ui(W)\n    ui(W)\n    if TAG == "[live] " then\n'
     '      check(TAG .. "C5b: the reconciled id was dropped again',
     '    W.card_comps["1002"].state = "active"\n    ui(W)\n    ui(W)\n    ui(W); ui(W); ui(W)   -- HARNESS 213\n'
     '    if TAG == "[live] " then\n      check(TAG .. "C5b: the reconciled id was dropped again', 1),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h212()\n") == 1
    src = src.replace("\nrun_h212()\n", "\nrun_h212()\nrun_h213()\n")
    for old, new, n in PINS:
        assert src.count(old) == n, (old, src.count(old))
        src = src.replace(old, new)
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!213)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
