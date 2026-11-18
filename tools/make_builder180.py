#!/usr/bin/env python3
"""Build the round-180 build script from the round-179 one (the score-3 review, rows 87-114 and 128).

Gate rebases: see R; every '938' (entries) becomes 935 (three closed).
ROUND 180 GATE: the 4 new families wired and ridden; the moves with their defaults; the 3 closed (no quoted key left);
the roots on their real 100 m range; the 80% WW buffers (the generator's Q80); the lizard / tiger sets match the game;
the Z / T codes honoured; Land Mine NOT moved (row 98 waits)."""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows3_harness178\build_and_install179.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows4_harness179\build_and_install180.py"
R = [
    # Foe-Seeker left 'tired' for charge_or_tired (row 111: "include charge")
    ("""assert 'marker = "foe_seeker", name = "Foe-Seeker", trigger = "tired"' in script_txt,""",
     """assert 'marker = "foe_seeker", name = "Foe-Seeker", trigger = "charge_or_tired"' in script_txt,""", 1),
    ("""count('trigger = "charge_or_melee"') == 37""", """count('trigger = "charge_or_melee"') == 36""", 2),   # Shield of Thorns
    ("""count('trigger = "enemy_fast_near_ally"') == 15""", """count('trigger = "enemy_fast_near_ally"') == 19""", 1),   # the 4 roots
    ("""count('trigger = "enemy_ground_area"') == 6""", """count('trigger = "enemy_ground_area"') == 2""", 1),
    ("""count('trigger = "enemy_wander"') == 43""", """count('trigger = "enemy_wander"') == 42""", 1),   # Heaven's Gate
    ("""count('trigger = "melee_self_or_ally"') == 2""", """count('trigger = "melee_self_or_ally"') == 3""", 1),
    ("""count('trigger = "tired"') == 2""", """count('trigger = "tired"') == 1""", 1),   # Foe-Seeker
    ("""count('trigger = "ushoran_health"') == 18""", """count('trigger = "ushoran_health"') == 11""", 1),   # 7 heals
    ("""count('trigger = "when_ready"') == 22""", """count('trigger = "when_ready"') == 20""", 1),   # 2 closed
    ('assert script_txt.count("\\t\\trange_real = ") == 418,', 'assert script_txt.count("\\t\\trange_real = ") == 417,', 2),
    ('assert script_txt.count("\\t\\tally_range_real = ") == 63,', 'assert script_txt.count("\\t\\tally_range_real = ") == 68,', 1),
    ('assert script_txt.count("\\t\\tstart_armed = true,\\n") == 33,', 'assert script_txt.count("\\t\\tstart_armed = true,\\n") == 42,', 1),
    # the AUTO327 list: Snowflake Pendant and Stave of Avelorn closed (row 100-101), as round 173 did
    ("AUTO327 = [x for x in AUTO327 if x[0] not in ('null_stone', 'item_passive_rock_eye')]   # ROUND 173: closed by the user\n"
     "assert len(AUTO327) == 289,",
     "AUTO327 = [x for x in AUTO327 if x[0] not in ('null_stone', 'item_passive_rock_eye')]   # ROUND 173: closed by the user\n"
     "AUTO327 = [x for x in AUTO327 if x[0] not in ('snowflake_pendant', 'stave_of_avelorn')]   # ROUND 180: closed by the user\n"
     "assert len(AUTO327) == 287,", 1),
    ("assert _nk327 == 304, (", "assert _nk327 == 302, (", 1),
    # Eat da Runts! (row 114, "A: cheapest ally"): no self arm; the reason names the cheapest healthy ally
    ("""assert 'string.format("eat da runts: self health %d%% (<= 75%%), cast on self"' in script_txt, "the eat-da-runts self reason is missing\"""",
     """assert 'string.format("eat da runts: self health %d%% (<= 75%%), cast on the cheapest healthy ally"' in script_txt, "the eat-da-runts reason is missing (round 180)\"""", 1),
    ("assert len(_kf162) == 84 and", "assert len(_kf162) == 83 and", 1),   # Heaven's Gate
    ("assert len(_kf164) == 84 and", "assert len(_kf164) == 83 and", 1),
]
ANCHOR = ('print("ROUND 179 GATE OK: 6 families wired; 12 entries moved, defaults kept; 5 ranked modes; spot/deep re-checks; "\n'
          '      "the wavering pair; Grut\'s winds gate")\n')
ADD = ANCHOR + r'''# ROUND 180: the score-3 review, rows 87-114 and 128 (user, 2026-11-18).
for _f180 in ("health_aura_ally_rule", "self_heal_clear", "self_hurt_attacked", "charge_or_tired"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f180, _f180)) in script_txt, "BUILD REFUSED (round 180): %s not wired" % _f180
    assert ('trigger = "%s"' % _f180) in script_txt, "BUILD REFUSED (round 180): no entry rides %s" % _f180
for _m180, _t180, _armed180 in (("entangle", "enemy_fast_near_ally", False), ("get_em", "enemy_fast_near_ally", False),
                                ("hunters_snare", "enemy_fast_near_ally", False), ("hunters_trap", "enemy_fast_near_ally", False),
                                ("shield_of_thorns", "melee_self_or_ally", True),
                                ("blood_chalice_of_bathori", "health_aura_ally_rule", True),
                                ("undeath_morkharn_breath_of_darkness", "health_aura_ally_rule", True),
                                ("undeath_morkharn_breath_of_darkness_upgraded", "health_aura_ally_rule", True),
                                ("protection_prayer", "health_aura_ally_rule", True), ("bugmans_xxxxxx", "self_heal_clear", True),
                                ("potion_of_charoi", "self_hurt_attacked", True), ("skars_kraken_killer", "self_hurt_attacked", True),
                                ("foe_seeker", "charge_or_tired", True), ("rock_bottom", "self_out_of_ammo", False),
                                ("eat_da_runts", "eat_da_runts", False), ("cold_blooded", "wavering_ally_range", False),
                                ("land_mine", "melee_clear", False)):
    _i180 = script_txt.find('{ marker = "%s", ' % _m180)
    assert _i180 >= 0 and ('trigger = "%s",' % _t180) in script_txt[_i180:_i180 + 200], \
        "BUILD REFUSED (round 180): %s is not on %s" % (_m180, _t180)
    _j180 = script_txt.find("\t\tox = ", _i180)
    assert (("\t\tstart_armed = true,\n" in script_txt[_i180:_j180]) == _armed180), \
        "BUILD REFUSED (round 180): %s's default is wrong" % _m180
    if _t180 == "enemy_fast_near_ally":
        assert "\t\trange_real = 100,\n" in script_txt[_i180:_j180], "BUILD REFUSED (round 180): %s is not on its real 100 m" % _m180
for _k180 in ("heavens_gate", "snowflake_pendant", "stave_of_avelorn", "melee_clear_block"):
    assert _k180 not in script_txt, "BUILD REFUSED (round 180): %s is still in the script" % _k180
import gen_ww_tables as _gw180
assert len(_gw180.Q80) == 5, "BUILD REFUSED (round 180): the 80% keys moved"
import gen_rule_sets as _gr180
assert _gr180.lua_block() in script_txt, "BUILD REFUSED (round 180): the lizard / tiger sets differ from the game data"
assert 'if a.Z and not FOURTH.class_member(unit, "lizard") then return false end' in script_txt \
    and 'if a.T and not FOURTH.class_member(unit, "tiger") then return false end' in script_txt, \
    "BUILD REFUSED (round 180): the Z / T target rules are not honoured"
assert "and FOURTH.wavering(other) == true and FOURTH.ab_atarget_ok(other) then   -- ROUND 180" in script_txt, \
    "BUILD REFUSED (round 180): Cold-Blooded's picker ignores the game's target rule"
assert "\nFOURTH.BUGMAN_CLEAR_M = 38" in script_txt and 38 == int(55 * 0.70), "BUILD REFUSED (round 180): Bugman's bound"
assert "\nFOURTH.ROCK_BOTTOM_PCT = 50" in script_txt and "\nFOURTH.HURT_ATTACKED_PCT = 75" in script_txt, \
    "BUILD REFUSED (round 180): the ruled health lines moved"
print("ROUND 180 GATE OK: 4 families wired; 13 entries moved, defaults right; 3 closed; roots at 100 m; 80%% WW keys; "
      "lizard (%d) / tiger (%d) sets match the game; Land Mine kept" % (len(_gr180.derive_lizard()), len(_gr180.derive_tiger())))
'''
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
n938 = len(re.findall(r"(?<!\d)938(?!\d)", src))
src = re.sub(r"(?<!\d)938(?!\d)", "935", src)
print("938 -> 935:", n938)
n992 = len(re.findall(r"(?<!\d)992(?!\d)", src))
src = re.sub(r"(?<!\d)992(?!\d)", "989", src)
print("992 -> 989:", n992)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
