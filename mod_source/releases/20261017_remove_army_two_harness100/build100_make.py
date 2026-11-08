# -*- coding: utf-8 -*-
"""Build build_and_install100.py from the shipped build_and_install99.py.

Round 100 removes Meat Feast (`wh3_main_prisoners_butcher`) and Massacre
(`wh3_main_prisoners_massacre`) from the mod. Both were implemented but sit
OUTSIDE the single in-wheel rule (source_type = army). Pins move DOWN:
579 -> 577 entries, 605 -> 603 keys, melee_unwavering 363 -> 362,
ushoran_health 34 -> 33; the two block-7-9 list rows are dropped (69 -> 67
entries / 73 -> 71 keys of that historical list), the Meat Feast presence
assert is replaced by ABSENCE asserts for both keys, and Grut's Sickle is
pinned as untouched.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC99 = os.path.join(HERE, "..", "20261015_classgated_harness99", "build_and_install99.py")
OUT = os.path.join(HERE, "build_and_install100.py")
NL = chr(10)

src = io.open(SRC99, encoding="utf-8", newline="").read()


def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied (%d)" % (label, count))


# ---------------------------------------------------------------- docstring
sub('\n"""\nimport hashlib',
    NL.join([
        '',
        'ROUND v100 (2026-10-17): REMOVAL. Meat Feast (wh3_main_prisoners_butcher)',
        'and Massacre (wh3_main_prisoners_massacre) were implemented but sit OUTSIDE',
        'the single in-wheel rule (both source_type = army). Per the user\'s decision',
        'of 2026-10-17 they are REMOVED from the ABILITIES table: 579 -> 577 entries,',
        '605 -> 603 keys, melee_unwavering 363 -> 362, ushoran_health 34 -> 33.',
        "Grut's Sickle and every other ability are untouched.",
        '"""',
        'import hashlib']),
    "docstring")

# ---------------------------------------------------------------- count pins
sub('assert script_txt.count("\\t{ marker = ") == 579, "the abilities table is not 579 entries"',
    'assert script_txt.count("\\t{ marker = ") == 577, "the abilities table is not 577 entries"',
    "entry count x3", count=3)
sub("assert script_txt.count('trigger = \"melee_unwavering\"') == 363, \\\n"
    '    "the melee_unwavering entry count is not 373 (10 Class-B entries moved to the ally families)"',
    "assert script_txt.count('trigger = \"melee_unwavering\"') == 362, \\\n"
    '    "the melee_unwavering entry count is not 362 (Massacre removed)"',
    "melee pin A")
sub("assert script_txt.count('trigger = \"melee_unwavering\"') == 363, \\\n"
    '    "the melee_unwavering count is not 373"',
    "assert script_txt.count('trigger = \"melee_unwavering\"') == 362, \\\n"
    '    "the melee_unwavering count is not 362 (Massacre removed)"',
    "melee pin B")
sub("assert script_txt.count('trigger = \"ushoran_health\"') == 34, \"the ushoran_health entry count is not 38 (3 Class-B heals moved to ally_heal)\"",
    "assert script_txt.count('trigger = \"ushoran_health\"') == 33, \"the ushoran_health entry count is not 33 (Meat Feast removed; Gulyas stays)\"",
    "ushoran pin")

# ---------------------------------------------------------------- BLOCK789
sub('    ("butcher", { "wh3_main_prisoners_butcher" }),\n', '', "block789 butcher")
sub('    ("massacre", { "wh3_main_prisoners_massacre" }),\n', '', "block789 massacre")
sub("assert len(BLOCK789) == 69, \"the block-7-9 entry list is not 69\"",
    "assert len(BLOCK789) == 67, \"the block-7-9 entry list is not 67 (Meat Feast + Massacre removed)\"",
    "block789 len")
sub('assert _nk789 == 73, "the block-7-9 key count is not 73 (got %d)" % _nk789',
    'assert _nk789 == 71, "the block-7-9 key count is not 71 (got %d)" % _nk789',
    "block789 keys")

# ---------------------------------------------------------------- presence -> absence
OLD = NL.join([
    "# the ARMY-BAR entry (Meat Feast, standing rule 10) is NOT given ally logic",
    "assert 'marker = \"butcher\", name = \"Meat Feast\", trigger = \"ushoran_health\"' in script_txt, \\",
    '    "the army-bar Meat Feast entry was changed"'])
NEW = NL.join([
    "# ROUND v100 (2026-10-17): the TWO ARMY-BAR ENTRIES ARE REMOVED. They were",
    "# implemented but sit OUTSIDE the single in-wheel rule; their keys, markers",
    "# and badge ids must be GONE. Grut's Sickle is a DIFFERENT, in-wheel item",
    "# ability (the max-HP ally pick rule) and must be untouched.",
    'assert "wh3_main_prisoners_butcher" not in script_txt, "the removed Meat Feast key is back"',
    'assert "wh3_main_prisoners_massacre" not in script_txt, "the removed Massacre key is back"',
    'assert \'marker = "butcher"\' not in script_txt, "the removed Meat Feast entry is back"',
    'assert \'marker = "massacre"\' not in script_txt, "the removed Massacre entry is back"',
    'assert "zz_auto_badge_butcher" not in script_txt and "zz_auto_badge_massacre" not in script_txt, \\',
    '    "a removed badge id is back"',
    'assert \'marker = "gruts_sickle"\' in script_txt and "wh3_main_item_abilities_gruts_sickle" in script_txt, \\',
    '    "Grut\'s Sickle was touched"',
    'assert "function FOURTH.evaluate_ally_winds(unit, routing)" in script_txt \\',
    '    and \'family == "winds"\' in script_txt, "the Grut\'s Sickle max-HP pick rule was touched"'])
sub(OLD, NEW, "presence -> absence")

io.open(OUT, "w", encoding="utf-8", newline="").write(src)
print("wrote", OUT, len(src), "bytes")
