#!/usr/bin/env python3
"""Build the round-179 build script from the round-178 one (the score-3 review, rows 115-134).

Gate rebases: ally_melee_buff 11 -> 1 (two gates); melee_self_or_ally 1 -> 2 (Favour of the Fay); health_aura_ground
3 -> 2 and health_aura_ally 9 -> 8; start_armed lines 21 -> 33 (the 12 moved entries keep their default); ally_range_real
62 -> 63 (Star of Avelorn's cast range); Star of Avelorn on heal_ground_best.
ROUND 179 GATE: the 6 new families wired and ridden; the 12 moves with start_armed; the 5 ranked ally modes; the heal
re-check modes "spot" and "deep"; the wavering pair without its melee condition; Grut's Sickle's winds gate."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows2_harness177\build_and_install178.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows3_harness178\build_and_install179.py"
R = [
    ("""assert script_txt.count('trigger = "ally_melee_buff"') == 11, "ally_melee_buff is not 14 entries\"""",
     """assert script_txt.count('trigger = "ally_melee_buff"') == 1, "ally_melee_buff is not 1 entry (round 179)\"""", 1),
    ("""assert script_txt.count('trigger = "ally_melee_buff"') == 11, "the ally_melee_buff count is not 11\"""",
     """assert script_txt.count('trigger = "ally_melee_buff"') == 1, "the ally_melee_buff count is not 1 (round 179)\"""", 1),
    ("""    and script_txt.count('trigger = "melee_self_or_ally"') == 1, \\""",
     """    and script_txt.count('trigger = "melee_self_or_ally"') == 2, \\""", 1),
    ("""assert script_txt.count('trigger = "health_aura_ground"') == 3,""",
     """assert script_txt.count('trigger = "health_aura_ground"') == 2,""", 1),
    ("""assert script_txt.count('trigger = "health_aura_ally"') == 9,""",
     """assert script_txt.count('trigger = "health_aura_ally"') == 8,""", 1),
    ('assert script_txt.count("\\t\\tstart_armed = true,\\n") == 21,', 'assert script_txt.count("\\t\\tstart_armed = true,\\n") == 33,', 1),
    ('assert script_txt.count("\\t\\tally_range_real = ") == 62,', 'assert script_txt.count("\\t\\tally_range_real = ") == 63,', 1),
    ("""assert 'marker = "star_of_avelorn", name = "Star of Avelorn", trigger = "health_aura_ground"' in script_txt,""",
     """assert 'marker = "star_of_avelorn", name = "Star of Avelorn", trigger = "heal_ground_best"' in script_txt,""", 1),
]
ANCHOR = 'print("ROUND 178 GATE OK: 3 families wired; 20 entries moved; Trophy Heads split; Eye of Khorne value-first; fire-first; floor 16")\n'
ADD = ANCHOR + r'''# ROUND 179: the score-3 review, rows 115-134 (user, 2026-11-18: "Items 115-134 approved").
for _f179 in ("ally_charge_or_melee", "ally_melee_wavering_first", "ally_value_melee", "ally_in_melee",
              "health_aura_ally_deep", "heal_ground_best"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f179, _f179)) in script_txt, "BUILD REFUSED (round 179): %s not wired" % _f179
    assert ('trigger = "%s"' % _f179) in script_txt, "BUILD REFUSED (round 179): no entry rides %s" % _f179
for _m179, _t179 in (("inspired_assault_i", "ally_charge_or_melee"), ("inspired_assault_ii", "ally_charge_or_melee"),
                     ("inspired_assault_iii", "ally_charge_or_melee"), ("inspired_defence_i", "ally_melee_wavering_first"),
                     ("inspired_defence_ii", "ally_melee_wavering_first"), ("inspired_defence_iii", "ally_melee_wavering_first"),
                     ("da_boss_as_a_plan", "ally_melee_wavering_first"), ("favour_of_the_fay", "melee_self_or_ally"),
                     ("orcs_are_da_best", "ally_value_melee"), ("hellish_vigour", "ally_in_melee"),
                     ("berry_wine", "health_aura_ally_deep"), ("star_of_avelorn", "heal_ground_best"),
                     ("gruts_sickle", "ally_winds"), ("commanding_presence", "wavering_self_or_ally"),
                     ("fury_of_ulric", "wavering_self_or_ally"), ("slezuzus_voice", "ally_melee_buff"),
                     ("horn_of_vaul", "melee_or_shooting_aura"), ("hunters_call", "melee_or_wavering_aura"),
                     ("cold_blooded", "wavering_ally_range"), ("captain_of_the_phoenix_guard", "ally_heal_melee")):
    _i179 = script_txt.find('{ marker = "%s", ' % _m179)
    assert _i179 >= 0 and ('trigger = "%s",' % _t179) in script_txt[_i179:_i179 + 200], \
        "BUILD REFUSED (round 179): %s is not on %s" % (_m179, _t179)
    if _m179 not in ("gruts_sickle", "commanding_presence", "fury_of_ulric", "slezuzus_voice", "horn_of_vaul",
                     "hunters_call", "cold_blooded", "captain_of_the_phoenix_guard"):
        _j179 = script_txt.find("\t\tox = 0, oy = 0 },", _i179)
        assert "\t\tstart_armed = true,\n" in script_txt[_i179:_j179], \
            "BUILD REFUSED (round 179): %s lost its default (its old family started armed)" % _m179
for _r179 in ("charge_contact_melee", "melee_wavering_first", "value_melee", "expendable_hp", "cheap_healthy"):
    assert script_txt.count('if family == "%s" then' % _r179) == 1, "BUILD REFUSED (round 179): ranked mode %s" % _r179
assert 'if FOURTH.ah_mode == "spot" then' in script_txt and 'if FOURTH.ah_mode == "deep" then' in script_txt, \
    "BUILD REFUSED (round 179): the heal re-check does not know the new rules"
assert "and not unit_is_routing(other)   -- ROUND 179: no melee condition" in script_txt, \
    "BUILD REFUSED (round 179): the wavering pair still asks for an ally in melee"
assert script_txt.count("if c == nil or c >= FOURTH.WINDS_LOW_POOL or r < FOURTH.WINDS_LOW_RESERVE then return nil end") == 2, \
    "BUILD REFUSED (round 179): Grut's Sickle does not wait for low winds"
assert "\nFOURTH.HEAL_DEEP_PCT = 55" in script_txt and "\nFOURTH.GRUT_HEALTHY_PCT = 75\n" in script_txt, \
    "BUILD REFUSED (round 179): the ruled health lines moved"
print("ROUND 179 GATE OK: 6 families wired; 12 entries moved, defaults kept; 5 ranked modes; spot/deep re-checks; "
      "the wavering pair; Grut's winds gate")
'''
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
