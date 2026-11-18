#!/usr/bin/env python3
"""Build the round-177 build script from the round-176 one (the score-3 review, rows 1-22).

Gate rebases: melee_unwavering 280 -> 265; plain start_armed lines 9 -> 21; ally_range_real fields 59 -> 62.
ROUND 177 GATE: the SQUIG table REGENERATED from the game data and equal to the shipped text; the 9 new families wired
and ridden; the 15 entries on their families; Daemonshield unchanged (the user's word)."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_mists_armed_harness175\build_and_install176.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows_harness176\build_and_install177.py"
R = [
    ("""script_txt.count('trigger = "melee_unwavering"') == 280""", """script_txt.count('trigger = "melee_unwavering"') == 265""", 4),
    ('assert script_txt.count("\\t\\tstart_armed = true,\\n") == 9,', 'assert script_txt.count("\\t\\tstart_armed = true,\\n") == 21,', 1),
    ('script_txt.count("\\t\\tally_range_real = ") == 59', 'script_txt.count("\\t\\tally_range_real = ") == 62', 1),
    ("""and script_txt.count('trigger = "melee_or_under_fire"') == 4, \\""",
     """and script_txt.count('trigger = "melee_or_under_fire"') == 5, \\""", 1),   # round 177: Rune of Oath & Steel
]
ANCHOR = 'print("ROUND 176 GATE OK: Master of Mists starts armed")\n'
ADD = ANCHOR + r'''# ROUND 177: the score-3 review, rows 1-22 (user, 2026-11-18: "Implement all until item 22, except the number 3").
import gen_squig_keys as _gq177
assert ('FOURTH.SQUIG_TEXT = "%s"\n' % _gq177.text(_gq177.derive())) in script_txt, \
    "BUILD REFUSED (round 177): the SQUIG table differs from the game data"
for _f177 in ("slow_army", "melee_vs_large", "ally_squig_melee", "enemy_melee_near", "aura_charge_or_melee",
              "melee_health25", "guard_aura", "self_or_ally_fire_melee", "melee_healthy"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f177, _f177)) in script_txt, "BUILD REFUSED (round 177): %s not wired" % _f177
    assert ('trigger = "%s"' % _f177) in script_txt, "BUILD REFUSED (round 177): no entry rides %s" % _f177
import re as _re177
for _m177, _t177 in (("blood_omens", "slow_army"), ("creature_killer", "melee_vs_large"),
                     ("empowering_shrooms", "ally_squig_melee"), ("everyone_has_their_price", "enemy_melee_near"),
                     ("fury_of_the_land", "aura_charge_or_melee"), ("refuse_to_die", "melee_health25"),
                     ("rune_of_oath_and_steel", "melee_or_under_fire"), ("shield_of_aeons", "guard_aura"),
                     ("dispatch_the_swarm_protect", "self_or_ally_fire_melee"),
                     ("dispatch_the_swarm_protect_upgraded", "self_or_ally_fire_melee"),
                     ("slayer_for_chaos", "self_last_stand"), ("steppe_hunters_horn", "melee_vs_large"),
                     ("the_armour_of_morkar", "guard_aura"), ("the_blood_price", "melee_healthy"),
                     ("ostermark_runefang", "melee_vs_large"), ("daemonshield", "melee_unwavering")):
    assert _re177.search(r'\{ marker = "%s", name = "[^"]+", trigger = "%s",' % (_re177.escape(_m177), _t177), script_txt), \
        "BUILD REFUSED (round 177): %s is not on %s" % (_m177, _t177)
print("ROUND 177 GATE OK: SQUIG (%d land units) matches the game; 9 families wired; 15 entries moved; Daemonshield kept"
      % len(_gq177.derive()))
'''
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
