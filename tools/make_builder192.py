#!/usr/bin/env python3
"""Build the round-192 build script from the round-191 one.

Drift from removing the five spell-bar runes (user 2026-11-21: "They should not be in the mod"): the entry/key counts
(988 -> 984, 1041 -> 1037), melee_unwavering 281 -> 279, the old BLOCK789 / AUTO327 lists drop the runes (the same
filter pattern rounds 171-180 used for closed entries), round 177's moved-entry list drops Rune of Oath & Steel.

ROUND 192 GATE: the closing rule for fast enemies; the five runes gone (marker, badge, key); Grombrindal Has No Fear on
melee_or_wavering_aura with its real 55 m aura; Shock Collar and Remouldered carry the game's Moulder rule (code M) and
it is honoured; Remouldered's monster list yields to the rule."""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_still1_harness190\build_and_install191.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_closing_harness191\build_and_install192.py"

R = [
    ('AUTO327 = [x for x in AUTO327 if x[0] not in (\'snowflake_pendant\', \'stave_of_avelorn\')]   # ROUND 180: closed by the user\n',
     'AUTO327 = [x for x in AUTO327 if x[0] not in (\'snowflake_pendant\', \'stave_of_avelorn\')]   # ROUND 180: closed by the user\n'
     'AUTO327 = [x for x in AUTO327 if x[0] not in (\'rune_of_breaking\', \'rune_of_negation\', \'rune_of_slowness\')]   # ROUND 192: the spell-bar runes left the mod\n', 1),
    ("assert len(AUTO327) == 287,", "assert len(AUTO327) == 284,", 1),
    ("assert _nk327 == 302,", "assert _nk327 == 299,", 1),
    ('assert len(BLOCK789) == 62, ',
     'BLOCK789 = [x for x in BLOCK789 if x[0] not in (\'rune_of_oath_and_steel\', \'rune_of_speed\')]   # ROUND 192: the spell-bar runes left the mod\n'
     'assert len(BLOCK789) == 60, ', 1),
    ("assert _nk789 == 66,", "assert _nk789 == 64,", 1),
    ('                     ("rune_of_oath_and_steel", "melee_or_under_fire"), ("shield_of_aeons", "guard_aura"),\n',
     '                     ("shield_of_aeons", "guard_aura"),   # ROUND 192: Rune of Oath & Steel left the mod\n', 1),
]
R += [
    # range_real fields 430 -> 429: Rune of Slowness (range_real 100) left the mod
    ('script_txt.count("\\t\\trange_real = ") == 430', 'script_txt.count("\\t\\trange_real = ") == 429', 2),
    # the third 'FOURTH.ab_filter = nil' is Remouldered's: the game's Moulder rule replaces the monster list
    ('assert script_txt.count("FOURTH.ab_filter = nil") == 2, "the class-gate slot is not defined+cleared"',
     'assert script_txt.count("FOURTH.ab_filter = nil") == 3, "the class-gate slot is not defined+cleared"   # ROUND 192: + Remouldered', 1),
]
COUNTS = [("988", "984"), ("1041", "1037"), ("281", "279")]

ANCHOR = 'print("ROUND 191 GATE OK: the 8 group-1 triggers wait for an animated caster to stand still")\n'
ADD = ANCHOR + r'''# ROUND 192 (user rulings 2026-11-21): the fast enemy must be running and closing; Grombrindal Has No Fear; the five
# spell-bar runes removed; the Moulder rule for Shock Collar and Remouldered.
assert "\nFOURTH.FAST_CLOSING_MPS = 3     -- ROUND 192" in script_txt and "\nFOURTH.FAST_CLOSING_S = 1       -- ROUND 192" in script_txt, \
    "BUILD REFUSED (round 192): the closing constants moved"
assert script_txt.count("local ok_mf, mf = pcall(function() return enemy:is_moving_fast() end)   -- ROUND 192: really running") == 1 \
    and script_txt.count("local closing = old_rule or FOURTH.fast_closing(enemy, best)") == 1, \
    "BUILD REFUSED (round 192): fast_enemy_near does not ask running + closing"
for _m192, _k192 in (("rune_of_breaking", "wh2_dlc17_rune_abilities_rune_of_breaking"),
                     ("rune_of_negation", "wh_main_rune_abilities_rune_of_negation"),
                     ("rune_of_slowness", "wh2_dlc17_rune_abilities_rune_of_slowness"),
                     ("rune_of_speed", "wh2_dlc17_rune_abilities_rune_of_speed"),
                     ("rune_of_oath_and_steel", "wh_main_rune_abilities_rune_of_oath_and_steel")):
    assert ('marker = "%s"' % _m192) not in script_txt and ('"zz_auto_badge_%s"' % _m192) not in script_txt \
        and ('"%s"' % _k192) not in script_txt and (_k192 + "=") not in script_txt, \
        "BUILD REFUSED (round 192): %s is still in the script" % _m192
assert ('{ marker = "grombrindal_has_no_fear", name = "Grombrindal Has No Fear", trigger = "melee_or_wavering_aura",\n'
        '\t\tbadge = "zz_auto_badge_grombrindal_has_no_fear",\n'
        '\t\tkeys = { "wh_pro01_lord_passive_grombrindal_has_no_fear" },') in script_txt \
    and '"wh_pro01_lord_passive_grombrindal_has_no_fear" },   -- ROUND 192 (user: in range in melee or wavering)\n\t\taura_real = 55,' in script_txt, \
    "BUILD REFUSED (round 192): Grombrindal Has No Fear is not on melee_or_wavering_aura with its 55 m aura"
import gen_rule_sets as _gr192
assert len(_gr192.derive_moulder()) == 28, "BUILD REFUSED (round 192): the Moulder set moved (%d)" % len(_gr192.derive_moulder())
assert 'if a.M and not FOURTH.class_member(unit, "moulder") then return false end' in script_txt, \
    "BUILD REFUSED (round 192): the Moulder rule is not honoured"
for _k192 in ("wh2_dlc16_hero_abilities_shock_collar", "wh2_dlc16_lord_abilities_remouldered"):
    assert (_k192 + "=M;") in script_txt, "BUILD REFUSED (round 192): %s does not carry the Moulder rule" % _k192
assert "\tif FOURTH.ab_atarget ~= nil and FOURTH.ab_atarget.M == true then FOURTH.ab_filter = nil end" in script_txt, \
    "BUILD REFUSED (round 192): Remouldered's monster list still decides"
print("ROUND 192 GATE OK: running + closing; 5 runes gone; Grombrindal Has No Fear (55 m); Moulder rule (%d units)"
      % len(_gr192.derive_moulder()))
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    for a, b, n in R:
        assert src.count(a) == n, (a[:70], src.count(a))
        src = src.replace(a, b)
    for old, new in COUNTS:
        got = len(re.findall(r"(?<!\d)%s(?!\d)" % old, src))
        src = re.sub(r"(?<!\d)%s(?!\d)" % old, new, src)
        print(old, "->", new, ":", got)
    # family-count gates written as script_txt.count('trigger = "<family>"') == N
    for fam, old, new in (("charge_or_melee", "36", "35"), ("enemy_fast_near_ally", "20", "19"),
                          ("melee_or_under_fire", "5", "4"), ("melee_or_wavering_aura", "2", "3")):
        pat = r"""(\.count\('trigger = "%s"'\) == )%s(?!\d)""" % (fam, old)
        got = len(re.findall(pat, src))
        src = re.sub(pat, r"\g<1>" + new, src)
        print(fam, old, "->", new, ":", got)
    assert src.count(ANCHOR) == 1
    src = src.replace(ANCHOR, ADD)
    src = src.replace("20261121_still1_harness190", "20261121_closing_harness191")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
