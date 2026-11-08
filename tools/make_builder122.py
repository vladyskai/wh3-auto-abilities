#!/usr/bin/env python3
"""Build the round-122 build script from tools/build_and_install121.py (the one
that built the installed round-121 pack).

Round 122 added ten self-cast melee buffs, all on the existing shared
melee_unwavering evaluator, so the builder's count pins follow the table:
687 -> 697 entries, melee_unwavering 360 -> 370. Nothing else changes: the
round-121 army-bar gate, the five-file identity checks and the probe refusal
are carried over untouched.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_and_install121.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261027_melee_buffs_harness121\build_and_install122.py"

src = open(SRC, encoding="utf-8").read()

REPS = [
    ('assert script_txt.count("\\t{ marker = ") == 687, "the abilities table is not 687 entries"',
     'assert script_txt.count("\\t{ marker = ") == 697, "the abilities table is not 697 entries"'),
    ("assert script_txt.count('trigger = \"melee_unwavering\"') == 360",
     "assert script_txt.count('trigger = \"melee_unwavering\"') == 370"),
]
for a, b in REPS:
    n = src.count(a)
    assert n >= 1, ("missing", a[:70])
    src = src.replace(a, b)
    print("  x%-3d %s" % (n, a[:90]))

src = src.replace('"melee_unwavering moved"', '"melee_unwavering moved (370 after round 122)"')
src = src.replace("the melee_unwavering entry count is not 360", "the melee_unwavering entry count is not 370")
src = src.replace("the melee_unwavering count is not 360", "the melee_unwavering count is not 370")

src = src.replace("ROUND 121: the ABILITIES table is 687 entries / 738 keys",
                  "ROUND 122: ten self-cast melee buffs added on melee_unwavering; the table is\n"
                  "697 entries / 748 keys, melee_unwavering 370.\n"
                  "ROUND 121: the ABILITIES table is 687 entries / 738 keys", 1)

open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
