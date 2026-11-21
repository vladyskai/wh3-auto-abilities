#!/usr/bin/env python3
"""Build harness191.lua from harness190.lua for round 192 (the closing check for fast enemies, Grombrindal Has No Fear,
the five spell-bar runes removed). Older harnesses are never edited.

Edits: the banner, load_world's ZZ_AUTO_TEST_NO_CLOSING line (older worlds keep the pre-192 fast rule), the rebases in
COUNTS / TRIG / R (each names the pin and why), run_h191 and its call."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_still1_harness190\harness190.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_closing_harness191\harness191.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h191_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 191 - ROUND 192: THE FAST ENEMY MUST BE RUNNING AND CLOSING (is_moving_fast + the gap to our nearest
--   unit shrinking 3 m/s over 1 s), GROMBRINDAL HAS NO FEAR (melee_or_wavering_aura), THE FIVE SPELL-BAR RUNES
--   REMOVED (Breaking, Negation, Slowness, Speed, Oath & Steel).
--   Edited vs harness190: this banner, load_world's ZZ_AUTO_TEST_NO_CLOSING line, the rebases listed in
--   tools/make_harness191.py, run_h191 and its call.
--   RED control: H191_LIVE / H191_ANN on docs/backups/round192/pre192_*.lua.
-- ============================================================================
"""
LOADW = ("  ZZ_AUTO_TEST_NO_LOS = (W.los_on ~= true)\n")
LOADW_NEW = ("  ZZ_AUTO_TEST_NO_LOS = (W.los_on ~= true)\n"
             "  -- ROUND 192: older worlds model a fast enemy as moving at a fixed gap; they run with the pre-192 rule\n"
             "  -- (moving, no closing check). A world that tests the closing rule sets W.closing_on.\n"
             "  ZZ_AUTO_TEST_NO_CLOSING = (W.closing_on ~= true)\n")
# entries 988 -> 984 (5 runes out, Grombrindal Has No Fear in), keys 1041 -> 1037, the badge-path walk 2 x 984;
# melee_unwavering 281 -> 279 (Rune of Breaking, Rune of Negation): every 281 in the file is that pin
COUNTS = [("988", "984", None), ("1041", "1037", None), ("1976", "1968", 1), ("281", "279", 17)]
# family pins written as cp(s, 'trigger = "<family>"') == N (any cp helper): Rune of Speed left charge_or_melee, Rune
# of Slowness left enemy_fast_near_ally, Rune of Oath & Steel left melee_or_under_fire, Grombrindal Has No Fear joined
# melee_or_wavering_aura
TRIG = [("charge_or_melee", "36", "35"), ("enemy_fast_near_ally", "20", "19"), ("melee_or_under_fire", "5", "4"),
        ("melee_or_wavering_aura", "2", "3")]
R = [
    ("(it == 1968)   -- HARNESS 184: 2 x 984", "(it == 1968)   -- HARNESS 184: 2 x 988; HARNESS 191: 2 x 984", 1),
    # harness 169's own charge_or_melee pin (written cm == 36): Rune of Speed left the mod
    ("      cm == 36)   -- HARNESS 179: Shield of Thorns moved",
     "      cm == 35)   -- HARNESS 179: Shield of Thorns moved; HARNESS 191: Rune of Speed removed", 1),
    # range_real fields 430 -> 429: Rune of Slowness (range_real 100) left the mod
    ('cp97(s, "\\t\\trange_real = ") == 430)', 'cp97(s, "\\t\\trange_real = ") == 429)', 1),
    ('cp(s, "\\t\\trange_real = ") == 430)', 'cp(s, "\\t\\trange_real = ") == 429)', 1),
    ("(EXP.sum and 430 or 96)", "(EXP.sum and 429 or 96)", 1),
    # the cast-gate wind-up table 353 -> 348: the five runes had a wind-up
    ("blk ~= nil and nkeys == 353)", "blk ~= nil and nkeys == 348)", 1),
    # harness 123 / 124 (the spell-bar rule) used Rune of Slowness as THE rune: it now uses the Master Rune of
    # Slowness (the same trigger, still in the mod), so the spell-bar and wheel cases keep testing the same code
    ('  local RUNE = "wh2_dlc17_rune_abilities_rune_of_slowness"\n',
     '  local RUNE = "wh2_dlc17_rune_abilities_master_rune_of_slowness"   -- HARNESS 191: the plain rune left the mod\n', 2),
    ('  local B_RUNE = "zz_auto_badge_rune_of_slowness"\n', '  local B_RUNE = "zz_auto_badge_master_rune_of_slowness"\n', 2),
    ('"claim: rune_of_slowness is a SPELL-BAR', '"claim: master_rune_of_slowness is a SPELL-BAR', 1),
    ('"SPELLBAR rune_of_slowness: button=', '"SPELLBAR master_rune_of_slowness: button=', 1),
    ('"badge rune_of_slowness: using fallback', '"badge master_rune_of_slowness: using fallback', 1),
    ('"scan: rune_of_slowness is on the right-hand SPELL bar', '"scan: master_rune_of_slowness is on the right-hand SPELL bar', 1),
    # harness 133 G3 (charge_or_melee on a charge): Rune of Speed -> Master Rune of Speed (the same trigger)
    ('  local RUN = "wh2_dlc17_rune_abilities_rune_of_speed"\n',
     '  local RUN = "wh2_dlc17_rune_abilities_master_rune_of_speed"   -- HARNESS 191: the plain rune left the mod\n', 1),
    ('{ "G3. Rune of Speed: charging -> ONE cast", charging, "rune_of_speed", RUN, 1, nil, nil },',
     '{ "G3. Master Rune of Speed: charging -> ONE cast", charging, "master_rune_of_speed", RUN, 1, nil, nil },', 1),
    # harness 98 AB-W1 and harness 99 CG15: Shock Collar / Remouldered now take only a Clan Moulder monster (the game's
    # rule, round 192); their qualifying ally becomes Rat Ogres (CG15's plain Rat Ogres also prove the monster list no
    # longer decides for Remouldered)
    ('      awavering = true, adist = 30, expect = "fire_ally" })',
     '      awavering = true, adist = 30, expect = "fire_ally", aname = "wh2_main_skv_mon_rat_ogres" })   -- HARNESS 191', 1),
    ('key = K.remo, marker = "remouldered", cuid = 9729, allies = { { name = MONST, uid = 9730,',
     'key = K.remo, marker = "remouldered", cuid = 9729, allies = { { name = "wh2_main_skv_mon_rat_ogres", uid = 9730,', 1),
    # harness 176 RO1 (melee_or_under_fire under missile fire): Rune of Oath & Steel -> Charmed Shield (the same trigger)
    ('RO = "wh_main_rune_abilities_rune_of_oath_and_steel",', 'RO = "wh_main_weapon_abilities_charmed_shield",', 1),
    ('{ "RO1. Rune of Oath & Steel: under missile fire, not in melee -> ONE cast",\n'
     '      function(b) return { caster(b, K.RO, { missile = true }) } end, "rune_of_oath_and_steel", K.RO, 1, 0 },',
     '{ "RO1. Charmed Shield (HARNESS 191: the rune left the mod): under missile fire, not in melee -> ONE cast",\n'
     '      function(b) return { caster(b, K.RO, { missile = true }) } end, "charmed_shield", K.RO, 1, 0 },', 1),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(LOADW) == 1
    src = src.replace(LOADW, LOADW_NEW)
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
    assert src.count("\nrun_h190()\n") == 1
    src = src.replace("\nrun_h190()\n", "\nrun_h190()\nrun_h191()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST, len(src), "bytes")


if __name__ == "__main__":
    main()
