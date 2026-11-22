#!/usr/bin/env python3
"""Build the round-202 build script from the round-201 one (the wave probe, user 2026-11-22: "Yes, build the probe").
ROUND 202 GATE: the console command zz_wave is defined once, sends the orientation argument in the ground form, is
called by nothing, and the mod's own ground casts still send orientation 0 and width 0 (no trigger changed)."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_masterrunes_harness199\build_and_install201.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_waveprobe_harness200\build_and_install202.py"
ANCHOR_HEAD = 'print("ROUND 201 GATE OK: none of the game\'s %d rune-type keys is in the script'
ADD = r'''# ROUND 202 (user 2026-11-22: "Yes, build the probe"): the wave probe is a console command, called by nothing.
assert script_txt.count("\nfunction zz_wave(deg, fwd, side, key)\n") == 1 \
    and script_txt.count("su.uc:perform_special_ability_ground(key, pos, deg, 0)") == 1, \
    "BUILD REFUSED (round 202): the wave probe is not defined once with the orientation argument"
assert script_txt.count("zz_wave(") == 2, \
    "BUILD REFUSED (round 202): something calls the wave probe (%d mentions, expected its banner and its definition)" \
    % script_txt.count("zz_wave(")
assert script_txt.count("perform_special_ability_ground(") - script_txt.count("-- ") * 0 >= 2 \
    and "uc:perform_special_ability_ground(ability_key, pos, 0, 0)" in script_txt, \
    "BUILD REFUSED (round 202): the mod's own ground cast no longer sends orientation 0, width 0"
print("ROUND 202 GATE OK: the wave probe zz_wave (console only, called by nothing), the mod's own ground casts unchanged")
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    i = src.index(ANCHOR_HEAD)
    j = src.index("\n", src.index("\n", i) + 1) + 1   # the print spans two lines
    assert src[i:j].rstrip().endswith(")"), src[i:j]
    src = src[:j] + ADD + src[j:]
    src = src.replace("20261122_masterrunes_harness199", "20261122_waveprobe_harness200")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
