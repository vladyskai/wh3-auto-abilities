#!/usr/bin/env python3
"""Round 208 (tuning, 2026-11-22, the afternoon code review items C5 and D): the cost of the free-aim search. No cast
decision changes.

1. NO SEARCH WHILE THE ABILITY CANNOT BE CAST. The wave evaluator ran its 24 x 7 path search once per second for the
   whole battle, also during the ability's recharge. It now asks unit:can_perform_special_ability(key) first: an exact
   false skips the search (an unreadable answer still searches). The engine answers true for a multi-use ability with
   no use left (a known fact), so those still search.
2. THE SEARCHES OF SEVERAL CASTERS ARE SPREAD OUT. Every armed wave caster searched on the same poll. The poll on which
   a caster searches now depends on its unit id (tick + id is a multiple of FREE_AIM_EVERY), so four casters use four
   different polls. The table FOURTH.aim_next is no longer needed.
Backups: docs/backups/round208/pre208_{live,ann}.lua."""
import os
import shutil

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round208"

OLD = """	if free then
		-- ROUND 204: the search is heavy (24 headings x the shifts per enemy): once per FREE_AIM_EVERY polls
		local id = "?"
		pcall(function() id = tostring(unit:unique_ui_id()) end)
		local key = tostring(FOURTH.rc_self_keys and FOURTH.rc_self_keys[1])
		local per = FOURTH.aim_next[id]
		if per == nil then
			per = {}
			FOURTH.aim_next[id] = per
		end
		if (per[key] or 0) > tick_count then return %s end
		per[key] = tick_count + FOURTH.FREE_AIM_EVERY
	end
"""
NEW = """	if free then
		-- ROUND 204: the search is heavy (24 headings x the shifts per enemy): once per FREE_AIM_EVERY polls.
		-- ROUND 208: WHICH poll depends on the unit's id, so several wave casters do not all search on the same one
		local idn = 0
		pcall(function() idn = tonumber(unit:unique_ui_id()) or 0 end)
		if (tick_count + idn) %% FOURTH.FREE_AIM_EVERY ~= 0 then return %s end
		-- ROUND 208: no search while the ability cannot be cast (its recharge): only an exact false skips it
		local key = FOURTH.rc_self_keys and FOURTH.rc_self_keys[1]
		local ok_can, can = pcall(function() return unit:can_perform_special_ability(key) end)
		if ok_can and can == false then return %s end
	end
"""


def patch(path, live):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 208" not in s, "already patched: " + path
    miss = "nil" if live else "false"
    old = OLD % miss
    assert s.count(old) == 1, (path, s.count(old))
    s = s.replace(old, NEW % (miss, miss))
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre208_live.lua"), (ANN, "pre208_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    patch(LIVE, True)
    patch(ANN, False)


if __name__ == "__main__":
    main()
