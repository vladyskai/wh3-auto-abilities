#!/usr/bin/env python3
"""Round 206 (tuning, 2026-11-22, from the user's Sunfang battle: "why it casts so far away from the main blob?" and
"Fought until a second cast, and that one was perfect. So still a bit inconsistent"), both copies.

The log: at the first order one Grave Guard unit stood (in melee) and two were still WALKING in. The path's value
counted all three where they were at that moment (108 + 108 soldiers under the cone). The fire arrived about 5 s later:
the walking unit had moved 8 m on and only 48 of its soldiers were still under it. At the second cast all three stood,
and it was perfect.

An exact wave's value now counts only enemies that STAND STILL (is_moving() exactly false, read once per unit per map).
This is option A of the user's 2026-11-22 ruling (standing targets only) applied to the value too, not only to the
enemy the path is anchored on.
Backups: docs/backups/round206/pre206_{live,ann}.lua."""
import os
import shutil

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round206"

OLD = """			-- ROUND 205 (user 2026-11-22): an enemy single entity is not counted, the damage to it is negligible
			if o.men > 1 then
				local c = FOURTH.wave_cover(o, sx, sz, ex, ez, row.r)
				if c > 0 then val = val + (o.value or 1) * c end
			end
"""
NEW = """			-- ROUND 206: an enemy that is still WALKING is not counted either: the fire arrives seconds after the
			-- order and it will have moved on (is_moving() exactly false counts, read once per unit per map)
			if o.still == nil then o.still = FOURTH.ww_target_still(o) end
			-- ROUND 205 (user 2026-11-22): an enemy single entity is not counted, the damage to it is negligible
			if o.men > 1 then
				local c = FOURTH.wave_cover(o, sx, sz, ex, ez, row.r)
				if c > 0 and o.still then val = val + (o.value or 1) * c end
			end
"""


def patch(path):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 206: an enemy that is still WALKING" not in s, "already patched: " + path
    assert s.count(OLD) == 1, (path, s.count(OLD))
    open(path, "w", encoding="utf-8", newline="").write(s.replace(OLD, NEW))
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre206_live.lua"), (ANN, "pre206_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    patch(LIVE)
    patch(ANN)


if __name__ == "__main__":
    main()
