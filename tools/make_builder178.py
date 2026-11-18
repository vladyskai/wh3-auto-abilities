#!/usr/bin/env python3
"""Build the round-178 build script from the round-177 one (the score-3 review, rows 23-55).

Gate rebases: the table 937 -> 938 entries (every '937': Trophy Heads split); enemy_engaged_or_shot 37 -> 22;
enemy_melee 34 -> 37; target_class 58 -> 54; enemy_blob 71 -> 69; enemy_commander_value 5 -> 4; enemy_area_drain
8 -> 11; enemy_ground_melee 75 -> 74; enemy_melee_or_shooting 1 -> 3; range_real 417 -> 418; the shot families carry
53 -> 60 keys; the round-158/159 gates now find Dweomer Leach Orb and Slann Gold on enemy_spellcaster without the
commander proxy class.
ROUND 178 GATE: the 2 new families wired and ridden; the 20 moves; the Trophy Heads split; Eye of Khorne ranks the
value first; the fire-first picker option."""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows_harness176\build_and_install177.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows2_harness177\build_and_install178.py"
R = [
    ("""script_txt.count('trigger = "enemy_melee"') == 34""", """script_txt.count('trigger = "enemy_melee"') == 35""", 2),
    # the 6 plain roots (rows 36-41, user: "Yes pls", no melee arm) joined the fast-enemy family
    ("""script_txt.count('trigger = "enemy_fast_near_ally"') == 9""", """script_txt.count('trigger = "enemy_fast_near_ally"') == 15""", 1),
    # the AREA caps serve the area drains AND enemy_most_models (Chain Lightning x2, The Soulstealer)
    ("""    r'trigger = "enemy_area_drain",\\n\\t\\tbadge = "[^"]+",\\n\\t\\tkeys = \\{ "([^"]+)" \\}', script_txt))""",
     """    r'trigger = "enemy_(?:area_drain|most_models)",\\n\\t\\tbadge = "[^"]+",\\n\\t\\tkeys = \\{ "([^"]+)" \\}', script_txt))""", 1),
    ("""script_txt.count('trigger = "enemy_engaged_or_shot"') == 37""", """script_txt.count('trigger = "enemy_engaged_or_shot"') == 22""", 4),
    ('script_txt.count("\\t\\ttarget_class = ") == 58', 'script_txt.count("\\t\\ttarget_class = ") == 54', 1),
    ("""script_txt.count('trigger = "enemy_blob"') == 71""", """script_txt.count('trigger = "enemy_blob"') == 69""", 1),
    ('("enemy_melee_or_fast", 4), ("enemy_melee_or_shooting", 1)', '("enemy_melee_or_fast", 4), ("enemy_melee_or_shooting", 3)', 1),
    ("assert len(_k156) == 53,", "assert len(_k156) == 60,", 1),
    ("assert len(_k157) == 53,", "assert len(_k157) == 60,", 1),
    ("assert len(_k158) == 53,", "assert len(_k158) == 60,", 1),
    ("""script_txt.count('trigger = "enemy_area_drain"') == 8 and script_txt.count('trigger = "enemy_commander_value"') == 5""",
     """script_txt.count('trigger = "enemy_area_drain"') == 8 and script_txt.count('trigger = "enemy_commander_value"') == 4""", 1),
    ("""("dweomer_leach_orb", "enemy_commander_value", '\\t\\ttarget_class = "commander",'),""",
     """("dweomer_leach_orb", "enemy_spellcaster", ""),   # ROUND 178: the spellcaster list""", 1),
    ("""("slann_gold", "enemy_commander_value", '\\t\\ttarget_class = "commander",'),""",
     """("slann_gold", "enemy_spellcaster", ""),   # ROUND 178: the spellcaster list""", 1),
    ("assert len(_a158) == 8 and", "assert len(_a158) == 11 and", 1),
    ('assert script_txt.count("\\t\\trange_real = ") == 417,', 'assert script_txt.count("\\t\\trange_real = ") == 418,', 2),
    ("""assert script_txt.count('trigger = "enemy_ground_melee"') == 75,""", """assert script_txt.count('trigger = "enemy_ground_melee"') == 74,""", 1),
    # Eye of Khorne's family label now says "most valuable" (the user's ruling)
    ("""assert 'enemy_low_health_noncommander = "When armed, fires on the lowest-health enemy' in script_txt""",
     """assert 'enemy_low_health_noncommander = "When armed, fires on the most valuable enemy' in script_txt   # ROUND 178""", 1),
]
ANCHOR = ('print("ROUND 177 GATE OK: SQUIG (%d land units) matches the game; 9 families wired; 15 entries moved; Daemonshield kept"\n'
          '      % len(_gq177.derive()))\n')
ADD = ANCHOR + r'''# ROUND 178: the score-3 review, rows 23-55 (user, 2026-11-18: "Approve rows 23-55. Row 56 stays the same").
for _f178 in ("enemy_fast_or_melee", "enemy_fast_fire_melee", "enemy_most_models"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f178, _f178)) in script_txt, "BUILD REFUSED (round 178): %s not wired" % _f178
    assert ('trigger = "%s"' % _f178) in script_txt, "BUILD REFUSED (round 178): no entry rides %s" % _f178
# the review doc's RULED texts (rows 23-24, 29: "a minimum of 16 units for both"; rows 36-41: no melee arm; rows 44-45:
# "makes sense to also add root")
for _m178, _t178 in (("spell_heavens_chain_lightning_bound", "enemy_most_models"),
                     ("spell_heavens_chain_lightning_bound_unit", "enemy_most_models"), ("the_soulstealer", "enemy_most_models"),
                     ("whip_of_misery", "enemy_melee_or_shooting"), ("word_of_pain", "enemy_melee_or_shooting"),
                     ("soulnetter", "enemy_fast_near_ally"), ("net_of_amyntok", "enemy_fast_near_ally"),
                     ("spider_web_attack", "enemy_fast_near_ally"), ("warp_gaze", "enemy_fast_near_ally"),
                     ("warpstiletto", "enemy_fast_near_ally"), ("pack_trap", "enemy_fast_near_ally"),
                     ("prey_of_anath_raema", "enemy_fast_fire_melee"), ("net_dem_up", "enemy_fast_fire_melee"),
                     ("glory_seeker", "enemy_fast_or_melee"), ("glory_seeker_upgraded", "enemy_fast_or_melee"),
                     ("prey_of_the_blood_god", "enemy_commander_value"), ("void_pendulum", "enemy_spellcaster"),
                     ("word_of_change", "enemy_spellcaster"), ("dweomer_leach_orb", "enemy_spellcaster"),
                     ("slann_gold", "enemy_spellcaster"), ("eye_of_khorne", "enemy_low_health_noncommander"),
                     ("trophy_heads", "enemy_melee"), ("trophy_heads_daemon_wings", "enemy_melee"),
                     ("oil_flask", "enemy_engaged_or_shot"), ("surprise_squig", "enemy_ground_melee")):
    assert _re177.search(r'\{ marker = "%s", name = "[^"]+", trigger = "%s",' % (_re177.escape(_m178), _t178), script_txt), \
        "BUILD REFUSED (round 178): %s is not on %s" % (_m178, _t178)
assert '\t\tkeys = { "wh3_main_daemon_wings_abilities_trophy_heads" },\n\t\trange_real = 150,\n\t\tox = 0, oy = 0 },' \
    in script_txt, "BUILD REFUSED (round 178): the Daemon Wings key is not on its own unclassed entry"
assert "local v, bv = FOURTH.unit_value(enemy), FOURTH.unit_value(best_enemy)" in script_txt, \
    "BUILD REFUSED (round 178): Eye of Khorne does not rank the value first"
assert '(arm == (FOURTH.eg_fire_first and "missile" or "melee")' in script_txt, \
    "BUILD REFUSED (round 178): the fire-first picker option is missing"
assert "\nFOURTH.MODELS_FLOOR = 16\n" in script_txt and 'elseif kind == "models" then' in script_txt, \
    "BUILD REFUSED (round 178): the user's 16-model floor is missing"
assert script_txt.count('trigger = "enemy_fast_or_melee"') == 2, "BUILD REFUSED (round 178): only Glory Seeker x2 ride enemy_fast_or_melee"
print("ROUND 178 GATE OK: 3 families wired; 20 entries moved; Trophy Heads split; Eye of Khorne value-first; fire-first; floor 16")
'''
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
n937 = len(re.findall(r"(?<!\d)937(?!\d)", src))
src = re.sub(r"(?<!\d)937(?!\d)", "938", src)
print("937 -> 938:", n937)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
