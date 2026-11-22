#!/usr/bin/env python3
"""Round 207 (tuning, 2026-11-22, from the afternoon code review; the user: "do another check of the code, maybe there are
more bugs like the one we found"), both copies. Two defects of the SAME kind as rounds 203 and 206, inside the family
and the rulings that already exist (option A, standing targets only):

1. THE 5 DRIFTING WAVES (Wrath of Manann, Wind of Death, The Burning Head x2, Arnzipal's Black Horror) still counted
   WALKING enemies in a path's value (FOURTH.ww_path_value). Round 206 fixed only the exact waves. Their casts take 3 to
   5 s of wind-up and then roll at 7 to 20 m/s, so a walking unit is long gone. The slot FOURTH.ww_still_only (set by
   the wave evaluator, cleared in FOURTH.entry_reset) makes ww_path_value count standing enemies only. The cones
   (enemy_cone) share ww_path_value and are NOT changed: they have no ruling.
2. A GROUND-ONLY WAVE WITH NO AIM (Blue Fire of Chaos x2 when the caster's position is unreadable or the enemy stands on
   the caster) fell back to the old order: the enemy's centre with orientation 0, the round-165 bug. It now holds.
Backups: docs/backups/round207/pre207_{live,ann}.lua."""
import os
import shutil

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round207"

OLD_PATH = """	for i = 1, #m.all do
		local o = m.all[i]
		if FOURTH.ww_pt_seg(o.x, o.z, sx, sz, ex, ez) - o.half <= row.r
			and FOURTH.ww_seg_rect_gap(sx, sz, ex, ez, o) <= row.r then
			v = v + (o.value or 0)
		end
	end
	return v
"""
NEW_PATH = """	-- ROUND 207: for a wave (FOURTH.ww_still_only, set by the wave evaluator) a WALKING enemy is not counted: a
	-- drifting wave takes 3 to 5 s to cast and then rolls slowly, the unit will have moved on
	local still_only = (FOURTH.ww_still_only == true)
	for i = 1, #m.all do
		local o = m.all[i]
		if FOURTH.ww_pt_seg(o.x, o.z, sx, sz, ex, ez) - o.half <= row.r
			and FOURTH.ww_seg_rect_gap(sx, sz, ex, ez, o) <= row.r then
			if still_only and o.still == nil then o.still = FOURTH.ww_target_still(o) end
			if not still_only or o.still then v = v + (o.value or 0) end
		end
	end
	return v
"""
OLD_FREE = "	local free = (ZZ_AUTO_TEST_NO_FREE_AIM ~= true)   -- ROUND 203\n"
NEW_FREE = OLD_FREE + "	FOURTH.ww_still_only = free   -- ROUND 207: ww_path_value counts standing enemies only (cleared in entry_reset)\n"
OLD_TAKE = "	if best == nil then return %s end\n	FOURTH.ww_take(unit, best, row, aim)\n"
NEW_TAKE = ("	if best == nil then return %s end\n"
            "	-- ROUND 207: a ground-only wave has no unit form. Without an aim it would go out on the enemy's centre with\n"
            "	-- orientation 0 (always north, the round-165 bug): hold instead\n"
            "	if free and row.ground and aim == nil then return %s end\n"
            "	FOURTH.ww_take(unit, best, row, aim)\n")
OLD_RESET = "	FOURTH.ww_aim = nil   -- ROUND 203: the free aim of a wave\n"
NEW_RESET = OLD_RESET + "	FOURTH.ww_still_only = nil   -- ROUND 207: only the wave evaluator sets it\n"


def one(s, a, b, what):
    assert s.count(a) == 1, (what, s.count(a))
    return s.replace(a, b)


def patch(path, live):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 207" not in s, "already patched: " + path
    miss = "nil" if live else "false"
    s = one(s, OLD_PATH, NEW_PATH, "path")
    s = one(s, OLD_FREE, NEW_FREE, "free")
    i = s.index("\nfunction FOURTH.evaluate_enemy_wave(unit, routing)\n")
    j = s.index("\nfunction FOURTH.evaluate_enemy_wander(unit, routing)\n", i)
    body = one(s[i:j], OLD_TAKE % miss, NEW_TAKE % (miss, miss), "take")
    s = s[:i] + body + s[j:]
    s = one(s, OLD_RESET, NEW_RESET, "reset")
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre207_live.lua"), (ANN, "pre207_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    patch(LIVE, True)
    patch(ANN, False)


if __name__ == "__main__":
    main()
