#!/usr/bin/env python3
"""Round 171: remove the charge-gate hold row of the closed Watched by the Watcher (3 uses, so it had a row in
charge_gate.hold_s); a closed ability leaves no quoted key behind (the round-171 build gate)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
ROW = '\t\t["wh3_dlc24_character_abilities_watched_by_the_watcher"] = 120,\n'
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert s.count(ROW) == 1, (path, s.count(ROW))
    s = s.replace(ROW, "")
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "row removed")
