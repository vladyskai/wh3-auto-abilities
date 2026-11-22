#!/usr/bin/env python3
"""Build harness207.lua from harness206.lua for round 209 (the user's replies to the afternoon code review). Older
harnesses are never edited. Edits: the banner, run_h207 and its call, and the rebased pins listed in PINS (each is
documented in the round document).
With DEV=<path> it writes a development copy that runs ONLY run_h207 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_searchcost_harness206\harness206.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_replies_harness207\harness207.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h207_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 207 - ROUND 209: THE REVIEW REPLIES (the Loons' friendly-fire ring, Lamprey's Bite as a wave, the player's
--   own cast protected, one bad unit no longer ends the poll).
--   Edited vs harness206: this banner, run_h207 and its call, the rebased pins (see the round document).
--   RED control: H207_LIVE / H207_ANN on docs/backups/round209/pre209_*.lua.
-- ============================================================================
"""
# the pins rebased in this round: (old text, new text, how many times it occurs)
PINS = [
    # harness 114's "the per-ability walk still BREAKS on 'gone'": the step now runs in a guard, so it RETURNS "gone"
    # and the caller's break follows the guard
    ('      inner_break = raw_find(string.sub(s, at, at + 80), "break", 1, true) ~= nil\n',
     '      inner_break = raw_find(string.sub(s, at, at + 80), \'return "gone"\', 1, true) ~= nil   -- HARNESS 207\n'
     '        and raw_find(s, \'elseif res_ab == "gone" then break end\', 1, true) ~= nil\n', 1),
    # Lamprey's Bite moved from enemy_wander to enemy_wave: 32 -> 33 waves, 42 -> 41 wanderers (four count pins)
    ('''        and cp(s, 'trigger = "enemy_wave"') == 32 and cp(s, 'trigger = "enemy_wander"') == 42\n''',
     '''        and cp(s, 'trigger = "enemy_wave"') == 33 and cp(s, 'trigger = "enemy_wander"') == 41   -- HARNESS 207\n''', 1),
    ('''        cp(s, "\\t{ marker = ") == 982 and cp(s, 'trigger = "enemy_wander"') == 42\n''',
     '''        cp(s, "\\t{ marker = ") == 982 and cp(s, 'trigger = "enemy_wander"') == 41   -- HARNESS 207\n''', 1),
    ('''        cp(s, "\\t{ marker = ") == 982 and cp(s, 'trigger = "enemy_wave"') == 32\n''',
     '''        cp(s, "\\t{ marker = ") == 982 and cp(s, 'trigger = "enemy_wave"') == 33   -- HARNESS 207\n''', 1),
    ('''        and cp(s, 'trigger = "enemy_sweep"') == 2 and cp(s, 'trigger = "enemy_wander"') == 42''',
     '''        and cp(s, 'trigger = "enemy_sweep"') == 2 and cp(s, 'trigger = "enemy_wander"') == 41''', 1),
    ("own == 1 and fns == 3 and single == 1 and shifts == 1 and waves == 32 and charge == 0 and steps == 1 and order == 1",
     "own == 1 and fns == 3 and single == 1 and shifts == 1 and waves == 33 and charge == 0 and steps == 1 and order == 1", 1),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h206()\n") == 1
    src = src.replace("\nrun_h206()\n", "\nrun_h206()\nrun_h207()\n")
    for old, new, n in PINS:
        assert src.count(old) == n, (old, src.count(old))
        src = src.replace(old, new)
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!207)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
