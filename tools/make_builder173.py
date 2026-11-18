#!/usr/bin/env python3
"""Build the round-173 build script from the round-172 one (Null Stone and Rock Eye closed by the user, 2026-11-18).

Gate rebases: the table 939 -> 937 entries (every '939'); the key count 994 -> 992 (the wind-up gate);
melee_unwavering 282 -> 280; the auto-accepted list (AUTO327) loses both markers (291 -> 289 entries, 306 -> 304 keys).
ROUND 173 GATE: neither marker, badge nor key in the source."""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_ruled_rows_harness171\build_and_install172.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_close_two_harness172\build_and_install173.py"
R = [
    ("assert len(_keys160) == 994 and", "assert len(_keys160) == 992 and", 1),
    ("""script_txt.count('trigger = "melee_unwavering"') == 282""", """script_txt.count('trigger = "melee_unwavering"') == 280""", 4),
    ("assert len(AUTO327) == 291,",
     "AUTO327 = [x for x in AUTO327 if x[0] not in ('null_stone', 'item_passive_rock_eye')]   # ROUND 173: closed by the user\n"
     "assert len(AUTO327) == 289,", 1),
    ("assert _nk327 == 306,", "assert _nk327 == 304,", 1),
]
ANCHOR = ('print("ROUND 172 GATE OK: Horn (every living unit in a smaller army), Waaagh! (army charge or army melee), "\n'
          '      "Ursun\'s Roar (one unit charging or wavering)")\n')
ADD = ANCHOR + r'''# ROUND 173: Null Stone and Rock Eye closed by the user (2026-11-18: "Close Null stone, Rock Eye.").
for _t173 in ("null_stone", "rock_eye"):
    assert _t173 not in script_txt, "BUILD REFUSED (round 173): a closed ability is back: " + _t173
print("ROUND 173 GATE OK: Null Stone and Rock Eye are closed")
'''
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:70], src.count(a))
    src = src.replace(a, b)
n939 = len(re.findall(r"(?<!\d)939(?!\d)", src))
src = re.sub(r"(?<!\d)939(?!\d)", "937", src)
print("939 -> 937:", n939)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
