#!/usr/bin/env python3
"""Build harness208.lua from harness207.lua for round 210 (the user's second replies to the afternoon code review).
Older harnesses are never edited. Edits: the banner, run_h208 and its call, and the rebased pins listed in PINS (each
is documented in the round document).
With DEV=<path> it writes a development copy that runs ONLY run_h208 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_replies_harness207\harness207.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_replies2_harness208\harness208.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h208_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 208 - ROUND 210: THE SECOND REPLIES (the Loons' own trigger, the caster-front breaths as cones from the
--   caster, the run-up of slow units, a transformed unit's new abilities).
--   Edited vs harness207: this banner, run_h208 and its call, the rebased pins (see the round document).
--   RED control: H208_LIVE / H208_ANN on docs/backups/round210/pre210_*.lua.
-- ============================================================================
"""
# the pins rebased in this round: (old text, new text, how many times it occurs)
PINS = [
    # the Loons left enemy_ground_melee (74 -> 72) for enemy_wave_charge (0 -> 2)
    ('''cp(s, 'trigger = "enemy_ground_area"') == 2 and cp(s, 'trigger = "enemy_ground_melee"') == 74)''',
     '''cp(s, 'trigger = "enemy_ground_area"') == 2 and cp(s, 'trigger = "enemy_ground_melee"') == 72)   -- HARNESS 208''', 1),
    ('''      and cp97(s, 'trigger = "enemy_ground_melee"') == 74)''',
     '''      and cp97(s, 'trigger = "enemy_ground_melee"') == 72)   -- HARNESS 208''', 1),
    ('''        and cp101(s, 'trigger = "enemy_ground_melee"') == (RED_MODE and 1 or 74))''',
     '''        and cp101(s, 'trigger = "enemy_ground_melee"') == (RED_MODE and 1 or 72))   -- HARNESS 208''', 1),
    ('''      cp102(s, 'trigger = "enemy_ground_melee"') == (EXP.sum and 74 or 1))''',
     '''      cp102(s, 'trigger = "enemy_ground_melee"') == (EXP.sum and 72 or 1))   -- HARNESS 208''', 1),
    ('''        and cp(s, 'trigger = "enemy_wave_charge"') == 0 and cp(s, 'trigger = "enemy_cone"') == 5''',
     '''        and cp(s, 'trigger = "enemy_wave_charge"') == 2 and cp(s, 'trigger = "enemy_cone"') == 5''', 1),
    ("waves == 33 and charge == 0 and steps == 1 and order == 1", "waves == 33 and charge == 2 and steps == 1 and order == 1", 1),
    ('''        and raw_find(s, '{ marker = "spinning_loons", name = "Spinning Loons", trigger = "enemy_ground_melee",', 1, true) ~= nil''',
     '''        and raw_find(s, '{ marker = "spinning_loons", name = "Spinning Loons", trigger = "enemy_wave_charge",', 1, true) ~= nil''', 1),
    ('''        and raw_find(s, '{ marker = "loons_of_eight_peaks", name = "The Loons of Eight Peaks", trigger = "enemy_ground_melee",', 1, true) ~= nil''',
     '''        and raw_find(s, '{ marker = "loons_of_eight_peaks", name = "The Loons of Eight Peaks", trigger = "enemy_wave_charge",', 1, true) ~= nil''', 1),
    # harness 142's LO1 and LE1 (an enemy in melee 10 m away -> a cast): the Loons no longer fire at an enemy in melee
    ('''      function(b) return one(b, LO, 10) end, "spinning_loons", LO, 1, 0, false, "ground" },''',
     '''      function(b) return one(b, LO, 10) end, "spinning_loons", LO, 0, 0, false, nil },   -- HARNESS 208: superseded''', 1),
    ('''      function(b) return one(b, LE, 10) end, "loons_of_eight_peaks", LE, 1, nil, false, "ground" },''',
     '''      function(b) return one(b, LE, 10) end, "loons_of_eight_peaks", LE, 0, nil, false, nil },   -- HARNESS 208: superseded''', 1),
    # harness 207: the ring left the two entries, and its LN2 world (a clear ring -> a cast) is superseded
    ("ring == 2 and ringtab == 1 and waves == 33", "ring == 0 and ringtab == 0 and waves == 33", 1),
    ('''      20710, LO, "spinning_loons", 150, 1, 1)''', '''      20710, LO, "spinning_loons", 150, 0, 1)   -- HARNESS 208: superseded''', 1),
    # the owned list is read again 2 s after a cast (round 210): one more scan per casting unit in these two worlds
    ("W.scans[1001] == 1 and W.scans[3001] == 1)", "W.scans[1001] == 2 and W.scans[3001] == 2)   -- HARNESS 208", 1),
    ("    d = ((W.scans[5001] or 0) == 2)\n", "    d = ((W.scans[5001] or 0) == 4)   -- HARNESS 208\n", 1),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h207()\n") == 1
    src = src.replace("\nrun_h207()\n", "\nrun_h207()\nrun_h208()\n")
    for old, new, n in PINS:
        assert src.count(old) == n, (old, src.count(old))
        src = src.replace(old, new)
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!208)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
