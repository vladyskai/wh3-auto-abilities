#!/usr/bin/env python3
"""Build the round-124 build script from the round-123 one.

Round 124 (the spell-bar badge test) adds no ABILITIES entry, so no count pin
moves. Two changes only:
  * the army-bar gate reads army_spec.tsv from the project's gamedata\\wh3
    (Windows Temp gets cleaned; tools/gamedata_paths.py);
  * one content gate: the spell-bar test switch and its claim branch are in the
    shipped source.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261027_hex_batch_harness122\build_and_install123.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261101_spellbar_test_harness123\build_and_install124.py"

src = open(SRC, encoding="utf-8").read()
REPS = [
    ('ARMY_SPEC_TSV = r"C:/Users/vlady/AppData/Local/Temp/wh3/army_spec.tsv"',
     'ARMY_SPEC_TSV = r"C:/Users/vlady/Desktop/WH3_mod/gamedata/wh3/army_spec.tsv"  # was Temp until round 124'),
    ('print("ROUND 123 GATE OK: enemy_melee evaluator wired, 3 entries, no Daemonic Possession")\n',
     'print("ROUND 123 GATE OK: enemy_melee evaluator wired, 3 entries, no Daemonic Possession")\n'
     '# ROUND 124: the spell-bar badge test (switch + claim branch + offset branch).\n'
     'assert "FOURTH.SPELLBAR_BADGES = true" in script_txt, "the spell-bar test switch is missing"\n'
     'assert \'string.sub(id, 1, 12) == "button_spell"\' in script_txt, "the spell-bar claim branch is missing"\n'
     'assert \'return BADGE_X + (px - WHEEL_TOP_X), BADGE_Y + (py - WHEEL_TOP_Y), "spell", px, py\' in script_txt, \\\n'
     '    "the spell-bar offset branch is missing"\n'
     'print("ROUND 124 GATE OK: the spell-bar badge test is in the source")\n'),
    ("ROUND 123: the hex batch (4 melee_unwavering, 3 charge_or_melee, 3 on the new\n",
     "ROUND 124: the spell-bar badge test (no roster change; army_spec read from gamedata\\\\wh3).\n"
     "ROUND 123: the hex batch (4 melee_unwavering, 3 charge_or_melee, 3 on the new\n"),
]
for a, b in REPS:
    assert src.count(a) == 1, (a[:60], src.count(a))
    src = src.replace(a, b)
assert "AppData/Local/Temp" not in src, "a Temp path survived"
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
