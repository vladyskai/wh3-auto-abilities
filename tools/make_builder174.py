#!/usr/bin/env python3
"""Build the round-174 build script from the round-173 one (the score 1-2 review, rows 24-50).

Gate rebases (counts the round changes on purpose):
  * enemy_melee 35 -> 34 (Transfix); enemy_engaged_or_shot 46 -> 37; enemy_ground_area 9 -> 6; target_class 56 -> 58;
    enemy_blob 77 -> 71; enemy_single_drain 10 -> 12; enemy_commander_value 3 -> 5; ally_melee_buff 14 -> 11;
    ally_overseer / ally_beast / ally_broken 1 -> 0, ally_missile 3 -> 0; the shot families carry 36 -> 53 keys;
    start_armed entries 8 -> 9 (Helping Hand).
ROUND 174 GATE:
  * the SPELLCASTER table REGENERATED from the game data (tools/gen_spellcaster_keys.py) and equal to the shipped text;
  * the 13 new families wired and ridden, the 27 entries on their families, the spellcaster class in the class gate;
  * the ally picker keeps routing allies only for the routing family; the not-missile filter."""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_close_two_harness172\build_and_install173.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_review_rows_harness173\build_and_install174.py"
R = [
    ("""script_txt.count('trigger = "enemy_melee"') == 35""", """script_txt.count('trigger = "enemy_melee"') == 34""", 2),
    ("""script_txt.count('trigger = "enemy_engaged_or_shot"') == 46""", """script_txt.count('trigger = "enemy_engaged_or_shot"') == 37""", 4),
    ("""script_txt.count('trigger = "enemy_ground_area"') == 9""", """script_txt.count('trigger = "enemy_ground_area"') == 6""", 1),
    ('script_txt.count("\\t\\ttarget_class = ") == 56', 'script_txt.count("\\t\\ttarget_class = ") == 58', 1),
    ("""script_txt.count('trigger = "enemy_blob"') == 77""", """script_txt.count('trigger = "enemy_blob"') == 71""", 1),
    ("""script_txt.count('trigger = "enemy_single_drain"') == 10""", """script_txt.count('trigger = "enemy_single_drain"') == 12""", 1),
    ("""script_txt.count('trigger = "enemy_commander_value"') == 3""", """script_txt.count('trigger = "enemy_commander_value"') == 5""", 1),
    ("""script_txt.count('trigger = "ally_melee_buff"') == 14""", """script_txt.count('trigger = "ally_melee_buff"') == 11""", 2),
    ("""script_txt.count('trigger = "ally_overseer"') == 1 and script_txt.count('trigger = "ally_beast"') == 1""",
     """script_txt.count('trigger = "ally_overseer"') == 0 and script_txt.count('trigger = "ally_beast"') == 0""", 1),
    ("""script_txt.count('trigger = "ally_broken"') == 1 and script_txt.count('trigger = "ally_missile"') == 3""",
     """script_txt.count('trigger = "ally_broken"') == 0 and script_txt.count('trigger = "ally_missile"') == 0""", 1),
    ('for _f, _n in (("enemy_large_shot", 5), ("enemy_single_shot", 2),',
     'for _f, _n in (("enemy_large_shot", 7), ("enemy_single_shot", 2),', 1),
    ("assert len(_k156) == 36,", "assert len(_k156) == 53,", 1),
    ("assert len(_k157) == 36,", "assert len(_k157) == 53,", 1),
    ("assert len(_k158) == 36,", "assert len(_k158) == 53,", 1),
]
ANCHOR = 'print("ROUND 173 GATE OK: Null Stone and Rock Eye are closed")\n'
ADD = ANCHOR + r'''# ROUND 174: the score 1-2 review, rows 24-50 (user, 2026-11-18: "You may implement items 24 to 50").
import gen_spellcaster_keys as _gs174
assert ('FOURTH.SPELLCASTER_TEXT = "%s"\n' % _gs174.text(_gs174.derive())) in script_txt, \
    "BUILD REFUSED (round 174): the SPELLCASTER table differs from the game data"
for _f174 in ("enemy_large_value_shot", "enemy_spellcaster", "enemy_ground_spellcasters", "enemy_missile_value",
              "enemy_ground_shooters", "enemy_commander_wavering", "ally_charge_melee", "ally_wavering_melee",
              "ally_lord_melee", "ally_missile_shooting", "ally_melee_risk", "ally_beast_charge", "ally_routing"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f174, _f174)) in script_txt, "BUILD REFUSED (round 174): %s not wired" % _f174
    assert ('trigger = "%s"' % _f174) in script_txt, "BUILD REFUSED (round 174): no entry rides %s" % _f174
_mv174 = {"weapon_abilities_amber_bow": "enemy_large_shot", "spell_bound_gaze_of_nagash": "enemy_large_shot",
          "spell_bound_hand_of_gods": "enemy_large_value_shot", "spell_light_shems_burning_gaze_bound": "enemy_large_value_shot",
          "character_abilities_goggly_glare": "enemy_large_value_shot", "spell_bound_vindictive_glare": "enemy_large_value_shot",
          "dont_even_try_it": "enemy_single_drain", "muster_of_malevolents": "enemy_single_drain",
          "cube_of_darkness": "enemy_spellcaster", "scroll_of_leeching": "enemy_spellcaster",
          "the_vortex_shard": "enemy_spellcaster", "the_black_tongue": "enemy_spellcaster",
          "the_tricksters_pendant": "enemy_ground_spellcasters", "tricksters_shard": "enemy_ground_spellcasters",
          "silence_the_prey": "enemy_commander_value", "power_siphon": "enemy_commander_value",
          "pageant_of_shrikes": "enemy_missile_value", "chalice_of_dark_rain": "enemy_ground_shooters",
          "transfix_hex": "enemy_commander_wavering", "fury_of_khaine": "ally_charge_melee",
          "verminous_fury": "ally_wavering_melee", "helping_hand": "ally_lord_melee",
          "inspired_marksmanship_i": "ally_missile_shooting", "inspired_marksmanship_ii": "ally_missile_shooting",
          "inspired_marksmanship_iii": "ally_missile_shooting", "overseer_of_the_unseen": "ally_melee_risk",
          "whiplash": "ally_beast_charge", "iron_hand_captain": "ally_routing"}
for _m174, _t174 in _mv174.items():
    assert re.search(r'\{ marker = "%s", name = "[^"]+", trigger = "%s",' % (re.escape(_m174), _t174), script_txt), \
        "BUILD REFUSED (round 174): %s is not on %s" % (_m174, _t174)
assert 'if cls == "spellcaster" then return FOURTH.class_keys.spellcaster[t] == true end' in script_txt, \
    "BUILD REFUSED (round 174): the spellcaster class is not in the class gate"
assert 'and (family == "routing" or not unit_is_routing(other))' in script_txt, \
    "BUILD REFUSED (round 174): the ally picker does not keep routing allies for Iron-Handed Captain"
assert 'if f == "not_missile" then return not FOURTH.class_member(unit, "missile") end' in script_txt, \
    "BUILD REFUSED (round 174): the not-missile ally filter is missing"
assert "FOURTH.CLUSTER_M = math.floor(FOURTH.CLUSTER_REAL_M * 0.70)" in script_txt, \
    "BUILD REFUSED (round 174): the 70% rule is broken for the cluster radius"
print("ROUND 174 GATE OK: SPELLCASTER (%d land units) matches the game; 13 families wired; 27 entries moved"
      % len(_gs174.derive()))
# ROUND 174 COMPILE GATE (a round-174 table regeneration once left a syntax error that every text gate passed): the
# shipped script must COMPILE. Run this builder with 'uv run --with websockets --with lupa'.
try:
    import lupa as _lupa174
except ImportError:
    raise AssertionError("BUILD REFUSED (round 174): lupa is missing - run with 'uv run --with websockets --with lupa'")
_c174 = _lupa174.LuaRuntime().eval("function(s) local f, e = load(s, '=zz_test_deadly_onslaught.lua'); return tostring(e) end")
_e174 = _c174(script_txt)
assert _e174 == "nil", "BUILD REFUSED (round 174): the script does not compile: " + _e174
print("ROUND 174 COMPILE GATE OK: the script compiles")
'''
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
if "\nimport re\n" not in src and "\nimport re " not in src:
    src = src.replace(ADD, "import re\n" + ADD, 1)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
