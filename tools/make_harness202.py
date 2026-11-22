#!/usr/bin/env python3
"""Build harness202.lua from harness201.lua for round 204 (an exact wave drops the safety distance for a count of our
soldiers under it, sideways shifts, Tidecall and Wind Blast on enemy_wave). Older harnesses are never edited.

Edits: the banner, the rebases in R (each names the pin and why), run_h202 and its call. run_h201 STAYS IN THE FILE but
is no longer called: its six worlds pinned round 203's paths through the enemy's centre with the 16 m distance, which
the user's ruling replaced. run_h202 runs the same situations under the new rule.
With DEV=<path> it writes a development copy that runs ONLY run_h202 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_freeaim_harness201\harness201.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_exactwave_harness202\harness202.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h202_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 202 - ROUND 204: AN EXACT WAVE NEEDS NO SAFETY DISTANCE (at most 5 of our soldiers under it, our single
--   entities not counted), SIDEWAYS SHIFTS of the path, TIDECALL and WIND BLAST on enemy_wave.
--   Edited vs harness201: this banner, the rebases listed in tools/make_harness202.py, run_h202 and its call. run_h201
--   stays in the file and is no longer called (superseded by run_h202, see the maker's note).
--   RED control: H202_LIVE / H202_ANN on docs/backups/round204/pre204_*.lua.
-- ============================================================================
"""
R = [
    # the wave family 30 -> 32 entries, the charge family 2 -> 0: Tidecall and Wind Blast moved (user: "please implement
    # for tight call and wind blast. The slow effect is irrelevant in this case.")
    ("""cp(s, 'trigger = "enemy_wave"') == 30""", """cp(s, 'trigger = "enemy_wave"') == 32""", 2),
    ("""cp(s, 'trigger = "enemy_wave_charge"') == 2""", """cp(s, 'trigger = "enemy_wave_charge"') == 0""", 1),
    # harness 163 CH1 / CH2: Wind Blast was the charge wave (a fast enemy closing -> cast, a standing one -> none). On
    # enemy_wave it is the other way round (older worlds run the pre-203 rule: the caster's line, a standing target).
    ('    { "CH1. Wind Blast: a fast enemy 20 m from us, the path clear -> ONE cast at it",\n',
     '    { "CH1. Wind Blast (HARNESS 202: on enemy_wave now): a fast enemy on the move -> no cast",\n', 1),
    ('            unit_class = "com", dist = 20, moving = true, fast_speed = 8 } }, { [tostring(b + 5)] = 900 } end,\n'
     '      "wind_blast", WB, 1, 0, 5 },\n',
     '            unit_class = "com", dist = 20, moving = true, fast_speed = 8 } }, { [tostring(b + 5)] = 900 } end,\n'
     '      "wind_blast", WB, 0, nil, nil },\n', 1),
    ('    { "CH2. Wind Blast: the same enemy standing -> no cast",\n',
     '    { "CH2. Wind Blast (HARNESS 202: on enemy_wave now): the same enemy standing -> ONE cast at it",\n', 1),
    ('            unit_class = "com", dist = 20 } }, { [tostring(b + 5)] = 900 } end, "wind_blast", WB, 0, nil, nil },\n',
     '            unit_class = "com", dist = 20 } }, { [tostring(b + 5)] = 900 } end, "wind_blast", WB, 1, 0, 5 },\n', 1),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    for a, b, n in R:
        assert src.count(a) == n, (a[:80], src.count(a))
        src = src.replace(a, b)
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h201()\n") == 1
    src = src.replace("\nrun_h201()\n",
                      "\n-- HARNESS 202: run_h201 (round 203: paths through the enemy's centre, the 16 m distance) is superseded by\n"
                      "-- run_h202, which runs the same situations under the round-204 rule. It stays in the file, uncalled.\n"
                      "run_h202()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!202)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
