#!/usr/bin/env python3
"""Round 155: bake the ALL button spot the user tuned in battle (2026-11-15; the last 'ALL POS -923,0' line, confirmed
by zz_all_where(), log archive\\logs\\battle_20261115_r154.txt). Live source and annotated copy, identically."""
import os
import shutil

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round155"
A = ("-- ROUND 154: the game's round button is 38 x 38 (the text badge was 36 x 24): the same centre, 7 lower. An ESTIMATE:\n"
     "-- the user tunes it in battle with the Lua Console hooks below and the tuned pair replaces this line.\n"
     "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -21\n")
B = ("-- ROUND 154: the game's round button is 38 x 38 (the text badge was 36 x 24).\n"
     "-- ROUND 155: the spot the user TUNED BY HAND in battle with zz_all_nudge (2026-11-15, the last 'ALL POS -923,0',\n"
     "-- confirmed by zz_all_where()). Re-tune the same way; the hooks below report the new pair.\n"
     "FOURTH.ALL_OX, FOURTH.ALL_OY = -923, 0\n")
os.makedirs(BK, exist_ok=True)
for path, tag in ((LIVE, "live"), (ANN, "ann")):
    bk = os.path.join(BK, "pre155_" + tag + ".lua")
    if not os.path.exists(bk):
        shutil.copy2(path, bk)
    s = open(bk, encoding="utf-8", newline="").read()
    assert s.count(A) == 1, (tag, s.count(A))
    s = s.replace(A, B)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(tag, "patched")
