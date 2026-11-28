#!/usr/bin/env python3
"""Build harness214.lua from harness213.lua for round 216 (tuning: the cost of the HUD walk). Older harnesses are never
edited. Edits: the banner, run_h214 and its call, and the rebased pins listed in PINS.
With DEV=<path> it writes a development copy that runs ONLY run_h214 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_owncost_harness213\harness213.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_walkscope_harness214\harness214.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h214_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 214 - ROUND 216 (tuning): THE COST OF THE HUD WALK (the walk starts at the ability dial, no walk while no
--   selected unit owns one of our abilities).
--   Edited vs harness213: this banner, run_h214 and its call, the rebased pins.
--   RED control: H214_LIVE / H214_ANN on docs/backups/round216/pre216_*.lua.
-- ============================================================================
"""
# the pins rebased in this round: (old text, new text, how many times it occurs)
PINS = [
    # harness 78 W3 (three selection events in one tick = ONE walk): the three selected units owned nothing of ours.
    # Since round 216 such a selection costs no walk at all, so the world would test nothing. One of the three now
    # owns the ability: the coalescing test stays (exactly one walk).
    ('    { name = "c", uid = 1003, owns = {} },\n    -- ITEM 1 (harness 78): a 4th tracked unit that DOES own one of ours',
     '    { name = "c", uid = 1003, owns = { FS_MAIN } },   -- HARNESS 214: a selected OWNER, else no walk is due\n'
     '    -- ITEM 1 (harness 78): a 4th tracked unit that DOES own one of ours', 1),
    # harness 78 W5 (a newly tracked unit = ONE walk): the selected unit owns nothing of ours and the newcomer is not
    # selected, so its buttons cannot be on the dial. Old value 1 walk, new value 0 (the 5 s safety net stays).
    ('    a = (W.hud_walks == 1)\n    check(TAG .. "W5a: a newly tracked unit costs EXACTLY ONE walk on the next tick (got "',
     '    a = (W.hud_walks == 0)   -- HARNESS 214: 1 -> 0, nothing of ours can be on the dial of the selected unit\n'
     '    check(TAG .. "W5a: a newly tracked unit costs EXACTLY ONE walk on the next tick [round 216: NO walk while the selected unit owns nothing] (got "', 1),
    ('    b = (W.hud_walks == 1 + want)\n    check(TAG .. "W5b: and nothing walks per tick afterwards (total " .. W.hud_walks .. ", want "\n'
     '      .. (1 + want) .. ")", b)',
     '    b = (W.hud_walks == 0 + want)   -- HARNESS 214\n    check(TAG .. "W5b: and nothing walks per tick afterwards (total " .. W.hud_walks .. ", want "\n'
     '      .. (0 + want) .. ")", b)', 1),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h213()\n") == 1
    src = src.replace("\nrun_h213()\n", "\nrun_h213()\nrun_h214()\n")
    for old, new, n in PINS:
        assert src.count(old) == n, (old, src.count(old))
        src = src.replace(old, new)
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!214)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
