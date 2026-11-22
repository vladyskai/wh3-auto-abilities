#!/usr/bin/env python3
"""Build the round-201 build script from the round-199 one (round 200 was the release tool, no builder).
Drift from removing the five Master Runes (user 2026-11-22: "do it") and adding Endless Whirlwind of Death (2 keys):
the entry/key counts (985 -> 982, 1038 -> 1035), melee_unwavering 279 -> 278, charge_or_melee 35 -> 34,
enemy_fast_near_ally 19 -> 18, range_real 429 -> 428, ally_range_real 81 -> 80, the ally arm 10 -> 9 entries (8 -> 7),
the old BLOCK789 / AUTO327 lists drop the runes.
ROUND 201 GATE (PERMANENT, rule 12): no key the game marks source_type = rune is in the script, in any form; the two
Endless Whirlwind entries ride melee_unwavering and their vortexes do not hit allies."""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_reviewfixes2_harness198\build_and_install199.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_masterrunes_harness199\build_and_install201.py"

R = [
    ("AUTO327 = [x for x in AUTO327 if x[0] not in ('rune_of_breaking', 'rune_of_negation', 'rune_of_slowness')]   # ROUND 192: the spell-bar runes left the mod\n",
     "AUTO327 = [x for x in AUTO327 if x[0] not in ('rune_of_breaking', 'rune_of_negation', 'rune_of_slowness')]   # ROUND 192: the spell-bar runes left the mod\n"
     "AUTO327 = [x for x in AUTO327 if x[0] not in ('master_rune_of_breaking', 'master_rune_of_negation', 'master_rune_of_slowness')]   # ROUND 201: the Master Runes left too\n", 1),
    ("assert len(AUTO327) == 284,", "assert len(AUTO327) == 281,", 1),
    ("assert _nk327 == 299,", "assert _nk327 == 296,", 1),
    ("assert len(BLOCK789) == 60, ",
     "BLOCK789 = [x for x in BLOCK789 if x[0] not in ('master_rune_of_oath_and_steel', 'master_rune_of_speed')]   # ROUND 201: the Master Runes left the mod\n"
     "assert len(BLOCK789) == 58, ", 1),
    ("assert _nk789 == 64,", "assert _nk789 == 62,", 1),
    ('script_txt.count("\\t\\trange_real = ") == 429', 'script_txt.count("\\t\\trange_real = ") == 428', 2),
    ('assert script_txt.count("\\t\\tally_range_real = ") == 81, "the ally_range_real fields are not 81 (71 + the ten round-199 ally arms)"',
     'assert script_txt.count("\\t\\tally_range_real = ") == 80, "the ally_range_real fields are not 80 (81 - Master Rune of Oath & Steel, round 201)"', 1),
    ('assert len(_arm199) == 10 and script_txt.count("\\t\\tally_value_arm = true,") == 8 \\\n',
     'assert len(_arm199) == 9 and script_txt.count("\\t\\tally_value_arm = true,") == 7 \\\n', 1),
    ('"BUILD REFUSED (round 199): the ally arm rides %d entries, expected 10 (8 + 2 ally-only)" % len(_arm199)',
     '"BUILD REFUSED (round 199): the ally arm rides %d entries, expected 9 (7 + 2 ally-only; round 201)" % len(_arm199)', 1),
]
COUNTS = [("985", "982"), ("1038", "1035"), ("279", "278")]
ANCHOR_HEAD = 'print("ROUND 199 GATE OK: a capital key is claimed; the ally arm on 10 entries'
ADD = r'''# ROUND 201 (user rulings 2026-11-22, after the Dwarf battle on the release build). PERMANENT (rule 12, the left-hand
# wheel only): the game puts every source_type = rune ability on the right-hand bar. One of them (Master Rune of
# Slowness) fired by itself because its entry rode a default-armed family and a cast needs no badge.
import csv as _csv201
import gamedata_paths as _gp201
with open(_gp201.GAMEDATA + r"\unit_abilities.tsv", encoding="utf-8-sig") as _f201:
    _r201 = list(_csv201.reader(_f201, delimiter="\t"))
_h201 = _r201[0]
_runes201 = [r[0] for r in _r201[2:] if r and r[_h201.index("source_type")] == "rune"]
assert len(_runes201) == 12, "BUILD REFUSED (round 201): the game's rune list moved (%d)" % len(_runes201)
for _k201 in _runes201:
    assert ('"%s"' % _k201) not in script_txt and (_k201 + "=") not in script_txt and (_k201 + ";") not in script_txt, \
        "BUILD REFUSED (round 201 right-hand-bar gate): the rune %s is in the script" % _k201
for _m201 in ("master_rune_of_breaking", "master_rune_of_negation", "master_rune_of_slowness", "master_rune_of_speed",
              "master_rune_of_oath_and_steel"):
    assert ('marker = "%s"' % _m201) not in script_txt and ('"zz_auto_badge_%s"' % _m201) not in script_txt, \
        "BUILD REFUSED (round 201): %s is still in the script" % _m201
with open(_gp201.GAMEDATA + r"\unit_spec_abil.tsv", encoding="utf-8-sig") as _f201:
    _s201 = list(_csv201.reader(_f201, delimiter="\t"))
_sh201 = _s201[0]
with open(_gp201.GAMEDATA + r"\battle_vortexs.tsv", encoding="utf-8-sig") as _f201:
    _v201 = list(_csv201.reader(_f201, delimiter="\t"))
_vh201 = _v201[0]
for _m201, _n201, _k201 in (("whirlwind_of_death_ror", "Endless Whirlwind of Death", "wh3_dlc25_unit_abilities_whirlwind_of_death_ror"),
                            ("whirlwind_of_death_ror_upgraded", "Endless Whirlwind of Death Upgraded",
                             "wh3_dlc25_unit_abilities_whirlwind_of_death_ror_upgraded")):
    assert ('\t{ marker = "%s", name = "%s", trigger = "melee_unwavering",\n\t\tbadge = "zz_auto_badge_%s",\n'
            '\t\tkeys = { "%s" },\n\t\tox = 0, oy = 0 },\n' % (_m201, _n201, _m201, _k201)) in script_txt, \
        "BUILD REFUSED (round 201): %s is not on melee_unwavering" % _m201
    _row201 = next(r for r in _s201[2:] if r and r[0] == _k201)
    _vx201 = _row201[_sh201.index("vortex")]
    _vr201 = next(r for r in _v201[2:] if r and r[0] == _vx201)
    assert _vr201[_vh201.index("affects_allies")] == "false", \
        "BUILD REFUSED (round 201): the vortex of %s hits allies (it needs a clear-of-ours trigger)" % _k201
print("ROUND 201 GATE OK: none of the game's %d rune-type keys is in the script (the right-hand bar); "
      "Endless Whirlwind of Death x2 on melee_unwavering, vortexes that do not hit allies" % len(_runes201))
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
    for fam, old, new in (("charge_or_melee", "35", "34"), ("enemy_fast_near_ally", "19", "18")):
        pat = r"""(\.count\('trigger = "%s"'\) == )%s(?!\d)""" % (fam, old)
        got = len(re.findall(pat, src))
        src = re.sub(pat, r"\g<1>" + new, src)
        print(fam, old, "->", new, ":", got)
    i = src.index(ANCHOR_HEAD)
    j = src.index("\n", src.index("\n", i) + 1) + 1   # the print spans two lines
    assert src[i:j].rstrip().endswith(")"), src[i:j]
    src = src[:j] + ADD + src[j:]
    src = src.replace("20261122_reviewfixes2_harness198", "20261122_masterrunes_harness199")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
