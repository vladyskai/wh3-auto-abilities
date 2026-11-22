#!/usr/bin/env python3
"""Build harness199.lua from harness198.lua for round 201 (the five Master Runes removed, Endless Whirlwind of Death on
melee_unwavering). Older harnesses are never edited.

Edits: the banner, the rebases in COUNTS / TRIG / R (each names the pin and why), run_h199 and its call.
With DEV=<path> it writes a development copy that runs ONLY run_h199 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_reviewfixes2_harness198\harness198.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_masterrunes_harness199\harness199.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h199_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 199 - ROUND 201: THE FIVE MASTER RUNES REMOVED (Breaking, Negation, Slowness, Speed, Oath & Steel: the
--   right-hand bar, rule 12; one fired by itself in the user's Dwarf battle), ENDLESS WHIRLWIND OF DEATH on
--   melee_unwavering (two keys).
--   Edited vs harness198: this banner, the rebases listed in tools/make_harness199.py, run_h199 and its call.
--   RED control: H199_LIVE / H199_ANN on docs/backups/round201/pre201_*.lua.
-- ============================================================================
"""
# entries 985 -> 982 (5 runes out, 2 Endless Whirlwind in), keys 1038 -> 1035, the badge-path walk 2 x 982;
# melee_unwavering 279 -> 278 (Breaking, Negation, Oath & Steel out, the two Endless Whirlwind in)
COUNTS = [("985", "982", None), ("1038", "1035", None), ("1970", "1964", 1), ("279", "278", None)]
# family pins written as cp(s, 'trigger = "<family>"') == N: Master Rune of Speed left charge_or_melee, Master Rune of
# Slowness left enemy_fast_near_ally
TRIG = [("charge_or_melee", "35", "34"), ("enemy_fast_near_ally", "19", "18")]
R = [
    # harness 169's own charge_or_melee pin (written cm == 35): Master Rune of Speed left the mod
    ("      cm == 35)   -- HARNESS 179: Shield of Thorns moved; HARNESS 191: Rune of Speed removed",
     "      cm == 34)   -- HARNESS 179: Shield of Thorns moved; HARNESS 191: Rune of Speed removed; HARNESS 199: its Master Rune too", 1),
    # range_real fields 429 -> 428: Master Rune of Slowness (range_real 100) left the mod
    ('cp97(s, "\\t\\trange_real = ") == 429)', 'cp97(s, "\\t\\trange_real = ") == 428)', 1),
    ('cp(s, "\\t\\trange_real = ") == 429)', 'cp(s, "\\t\\trange_real = ") == 428)', 1),
    ("(EXP.sum and 429 or 96)", "(EXP.sum and 428 or 96)", 1),
    # ally_range_real fields 81 -> 80: Master Rune of Oath & Steel (the round-199 ally arm, 100 m) left the mod
    ('cp98(s, "\\t\\tally_range_real = ") == 81)', 'cp98(s, "\\t\\tally_range_real = ") == 80)', 1),
    ('and cp99(s, "\\t\\tally_range_real = ") == 81)', 'and cp99(s, "\\t\\tally_range_real = ") == 80)', 1),
    ('cp104(s, "\\t\\tally_range_real = ") == 81)', 'cp104(s, "\\t\\tally_range_real = ") == 80)', 1),
    # the cast-gate wind-up table 348 -> 343: the five Master Runes had a wind-up
    ("blk ~= nil and nkeys == 348)", "blk ~= nil and nkeys == 343)", 1),
    # harness 198's own token pin: the ally arm rides 7 + 2 entries (Master Rune of Oath & Steel left)
    ("cap == 1 and wrap == 1 and arms == 8 and only == 2 and inf == 1 and nxt >= 8)",
     "cap == 1 and wrap == 1 and arms == 7 and only == 2 and inf == 1 and nxt >= 8)   -- HARNESS 199: 8 -> 7", 1),
    # harness 123 / 124 (the spell-bar rule) used the Master Rune of Slowness as THE rune: it now uses Hunter's Trap
    # (the same trigger and the same 100 m range, still in the mod), so the spell-bar and wheel cases keep testing the
    # same code
    ('  local RUNE = "wh2_dlc17_rune_abilities_master_rune_of_slowness"   -- HARNESS 191: the plain rune left the mod\n',
     '  local RUNE = "wh2_dlc13_lord_abilities_hunters_trap"   -- HARNESS 199: the Master Rune left the mod too\n', 2),
    ('  local B_RUNE = "zz_auto_badge_master_rune_of_slowness"\n', '  local B_RUNE = "zz_auto_badge_hunters_trap"\n', 2),
    ('"claim: master_rune_of_slowness is a SPELL-BAR', '"claim: hunters_trap is a SPELL-BAR', 1),
    ('"SPELLBAR master_rune_of_slowness: button=', '"SPELLBAR hunters_trap: button=', 1),
    ('"badge master_rune_of_slowness: using fallback', '"badge hunters_trap: using fallback', 1),
    ('"scan: master_rune_of_slowness is on the right-hand SPELL bar', '"scan: hunters_trap is on the right-hand SPELL bar', 1),
    # harness 133 G3 (charge_or_melee on a charge): Master Rune of Speed -> Slippery (the same trigger)
    ('  local RUN = "wh2_dlc17_rune_abilities_master_rune_of_speed"   -- HARNESS 191: the plain rune left the mod\n',
     '  local RUN = "wh_main_hero_abilities_slippery"   -- HARNESS 199: the Master Rune left the mod too\n', 1),
    ('{ "G3. Master Rune of Speed: charging -> ONE cast", charging, "master_rune_of_speed", RUN, 1, nil, nil },',
     '{ "G3. Slippery (HARNESS 199: the rune left the mod): charging -> ONE cast", charging, "slippery", RUN, 1, nil, nil },', 1),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    for old, new, want in COUNTS:
        pat = r"(?<!\d)%s(?!\d)" % old
        got = len(re.findall(pat, src))
        assert want is None or got == want, (old, got)
        src = re.sub(pat, new, src)
        print(old, "->", new, ":", got)
    for fam, old, new in TRIG:
        pat = r"""(\w*\(s\w*, 'trigger = "%s"'\) == )%s(?!\d)""" % (fam, old)
        got = len(re.findall(pat, src))
        src = re.sub(pat, r"\g<1>" + new, src)
        print(fam, old, "->", new, ":", got)
    for a, b, n in R:
        assert src.count(a) == n, (a[:80], src.count(a))
        src = src.replace(a, b)
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h198()\n") == 1
    src = src.replace("\nrun_h198()\n", "\nrun_h198()\nrun_h199()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!199)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
