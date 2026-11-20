#!/usr/bin/env python3
"""Build the round-181 build script from the round-180 one (Land Mine "A", Surprise Squig! blob with clearance, the
range fixes).

Gate rebases: see R; every '935' (entries) becomes 936 (the Lord of Undeath split).
ROUND 181 GATE: the 2 new families wired and ridden; the 60-soldier line; the GENERATED summon blast matches the game;
every entry's range_real / ally_range_real equals the game's target_intercept_range for EVERY key (the round-181 scan,
now a permanent gate); the Lord of Undeath split."""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows4_harness179\build_and_install180.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_landmine_squig_harness180\build_and_install181.py"
R = [
    ('("land_mine", "melee_clear", False)', '("land_mine", "melee_clear_block", False)', 1),   # row 98 built (A)
    ('for _k180 in ("heavens_gate", "snowflake_pendant", "stave_of_avelorn", "melee_clear_block"):',
     'for _k180 in ("heavens_gate", "snowflake_pendant", "stave_of_avelorn"):   # ROUND 181: melee_clear_block is back (row 98 "A")', 1),
    ('assert script_txt.count("\\t\\trange_real = ") == 417,', 'assert script_txt.count("\\t\\trange_real = ") == 418,', 2),
    ('for _f, _n in (("melee_clear", 5), ("fly_dive", 2),', 'for _f, _n in (("melee_clear", 4), ("fly_dive", 2),', 1),   # Land Mine moved
    ('("oil_flask", "enemy_engaged_or_shot"), ("surprise_squig", "enemy_ground_melee")):',
     '("oil_flask", "enemy_engaged_or_shot"), ("surprise_squig", "enemy_summon_blob")):   # ROUND 181: row 28 built', 1),
]
ANCHOR = ('print("ROUND 180 GATE OK: 4 families wired; 13 entries moved, defaults right; 3 closed; roots at 100 m; 80%% WW keys; "\n'
          '      "lizard (%d) / tiger (%d) sets match the game; Land Mine kept" % (len(_gr180.derive_lizard()), len(_gr180.derive_tiger())))\n')
ADD = ANCHOR + r'''# ROUND 181: Land Mine "A", Surprise Squig! blob with clearance, the range fixes (user, 2026-11-20).
for _f181 in ("melee_clear_block", "enemy_summon_blob"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f181, _f181)) in script_txt, "BUILD REFUSED (round 181): %s not wired" % _f181
    assert script_txt.count('trigger = "%s"' % _f181) == 1, "BUILD REFUSED (round 181): %s is not ridden once" % _f181
assert "\nFOURTH.LAND_MINE_MIN_MEN = 60" in script_txt, "BUILD REFUSED (round 181): the user's 60-soldier line moved"
import gen_summon_blast as _gs181
_ks181 = _gs181.keys_in(script_txt)
assert _ks181 == ["wh3_dlc25_character_abilities_surprise_squig"] and \
    _gs181.lua_block(_gs181.derive(_ks181)) in script_txt, "BUILD REFUSED (round 181): the summon blast differs from the game data"
import subprocess as _sp181, sys as _sy181
_scan181 = _sp181.run([_sy181.executable, r"C:\Users\vlady\Desktop\WH3_mod\tools\scan_range_real.py"], capture_output=True, text=True)
assert _scan181.stdout.strip().endswith("0 mismatches"), \
    "BUILD REFUSED (round 181): a range_real differs from the game's target_intercept_range:\n" + _scan181.stdout
assert '{ marker = "lord_of_undeath_4", name = "Lord of Undeath", trigger = "enemy_ground_melee",' in script_txt, \
    "BUILD REFUSED (round 181): the Lord of Undeath split is missing"
print("ROUND 181 GATE OK: 2 families wired; 60 soldiers; summon blast 21 m matches the game; 0 range mismatches; Lord of Undeath split")
'''
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
n935 = len(re.findall(r"(?<!\d)935(?!\d)", src))
src = re.sub(r"(?<!\d)935(?!\d)", "936", src)
print("935 -> 936:", n935)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
