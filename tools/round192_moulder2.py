#!/usr/bin/env python3
"""Round 192, part 3, both copies: Remouldered (the only ally_monster_heal entry) used the mod's own 'monster' list as a
stand-in for the game's rule. That list leaves out plain Rat Ogres, Wolf Rats and four Stormfiend kinds, which the game
lets Remouldered heal. When the entry carries the game's Moulder rule (code M, part 2), the rule replaces the list."""
LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
OLD = """function FOURTH.evaluate_ally_monster_heal(unit, routing)
	FOURTH.ab_filter = "monster"
	return FOURTH.ab_pick_ally(unit, routing, "heal")
end
"""
NEW = """function FOURTH.evaluate_ally_monster_heal(unit, routing)
	FOURTH.ab_filter = "monster"
	-- ROUND 192: the game's own Moulder rule (code M, the GENERATED moulder set) replaces the mod's monster list
	if FOURTH.ab_atarget ~= nil and FOURTH.ab_atarget.M == true then FOURTH.ab_filter = nil end
	return FOURTH.ab_pick_ally(unit, routing, "heal")
end
"""
for p in (LIVE, ANN):
    s = open(p, encoding="utf-8", newline="").read()
    assert s.count(OLD) == 1, p
    s = s.replace(OLD, NEW)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("patched", p)
