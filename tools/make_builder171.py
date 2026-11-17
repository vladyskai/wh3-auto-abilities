#!/usr/bin/env python3
"""Build the round-171 build script from the round-170 one (the score 1-2 review, rows 1-15 and 21).

Gate rebases (counts the round changes on purpose):
  * the table 946 -> 939 entries (every '946' in the script), the key count 1,003 -> 994 (the wind-up gate);
  * melee_unwavering 298 -> 282; ushoran_health 19 -> 18; when_ready 21 -> 22; ally_range_real fields 58 -> 59;
  * start_armed entries 1 -> 8 (the round-170 gate).
ROUND 171 GATE:
  * the CONTACT table REGENERATED from the game data (tools/gen_contact_keys.py) and equal to the shipped text;
  * the six families wired, the two split entries present, the nine closed markers and keys absent;
  * the fresh-contact tracker called once per poll."""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_foolhardiness_harness169\build_and_install170.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_review_rows_harness170\build_and_install171.py"
R = [
    ("""script_txt.count('trigger = "when_ready"') == 21""", """script_txt.count('trigger = "when_ready"') == 22""", 1),
    ("assert len(_keys160) == 1003 and", "assert len(_keys160) == 994 and", 1),
    ("""script_txt.count('trigger = "melee_unwavering"') == 298""", """script_txt.count('trigger = "melee_unwavering"') == 282""", 4),
    ("""script_txt.count('trigger = "ushoran_health"') == 19""", """script_txt.count('trigger = "ushoran_health"') == 18""", 1),
    ('script_txt.count("\\t\\tally_range_real = ") == 58', 'script_txt.count("\\t\\tally_range_real = ") == 59', 1),
    ('assert script_txt.count("\\t\\tstart_armed = true,\\n") == 1,', 'assert script_txt.count("\\t\\tstart_armed = true,\\n") == 8,', 1),
    # the auto-accepted list: the nine abilities the user closed in round 171 leave it (300 -> 291 entries, 315 -> 306 keys)
    ("assert len(AUTO327) == 300,",
     "AUTO327 = [x for x in AUTO327 if x[0] not in ('earthing_rod', 'hagtree_fetish', 'master_of_the_black_arts', "
     "'maw_shard', 'power_familiar', 'watched_by_the_watcher', 'sceptre_of_stability', 'locus_of_abjuration', "
     "'focus_instincts')]   # ROUND 171: closed by the user\nassert len(AUTO327) == 291,", 1),
    ("assert _nk327 == 315,", "assert _nk327 == 306,", 1),
]
ANCHOR = 'print("ROUND 170 GATE OK: Potion of Foolhardiness fires on its charge or when wavering, and still starts armed")\n'
ADD = ANCHOR + r'''# ROUND 171: the score 1-2 review, rows 1-15 and 21 (2026-11-17).
import gen_contact_keys as _gc171
assert ('FOURTH.CONTACT_TEXT = "%s"\n' % _gc171.text(_gc171.derive())) in script_txt, \
    "BUILD REFUSED (round 171): the CONTACT table differs from the game data"
for _f171 in ("army_charge", "aura_charge", "self_or_ally_charge", "slow_aura", "winds_low", "contact_melee"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f171, _f171)) in script_txt, "BUILD REFUSED (round 171): %s not wired" % _f171
    assert ('trigger = "%s"' % _f171) in script_txt, "BUILD REFUSED (round 171): no entry rides %s" % _f171
assert '{ marker = "ursuns_roar_charge"' in script_txt and '{ marker = "waaagh_army"' in script_txt, \
    "BUILD REFUSED (round 171): a split entry is missing"
for _m171, _k171 in (("earthing_rod", "wh_main_item_abilities_earthing_rod"),
                     ("hagtree_fetish", "wh_dlc03_item_abilities_hagtree_fetish"),
                     ("master_of_the_black_arts", "wh_main_lord_abilities_master_of_the_black_arts"),
                     ("maw_shard", "wh3_main_item_abilities_maw_shard"),
                     ("power_familiar", "wh3_dlc27_item_abilities_power_familiar"),
                     ("watched_by_the_watcher", "wh3_dlc24_character_abilities_watched_by_the_watcher"),
                     ("sceptre_of_stability", "wh_main_item_abilities_sceptre_of_stability"),
                     ("locus_of_abjuration", "wh3_main_character_abilities_locus_of_abjuration"),
                     ("focus_instincts", "wh2_dlc12_lord_abilities_focus_instincts")):
    assert ('marker = "%s"' % _m171) not in script_txt and ('"%s"' % _k171) not in script_txt, \
        "BUILD REFUSED (round 171): the closed ability is back: " + _m171
assert script_txt.count("\tpcall(FOURTH.track_melee)") == 1, "BUILD REFUSED (round 171): the melee tracker is not polled"
print("ROUND 171 GATE OK: CONTACT (%d land units) matches the game; six families wired; Ursun's Roar and Waaagh! split; "
      "nine abilities closed; the fresh-contact tracker polled" % len(_gc171.derive()))
'''
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:70], src.count(a))
    src = src.replace(a, b)
n946 = len(re.findall(r"(?<!\d)946(?!\d)", src))
src = re.sub(r"(?<!\d)946(?!\d)", "939", src)
print("946 -> 939:", n946)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
