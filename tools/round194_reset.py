#!/usr/bin/env python3
"""Round 194, part 2, both copies: the hook the optional MCT page calls when the player resets the remembered M/A
choices DURING a battle. The page empties the file itself. Without this hook the battle script would write its
in-memory choices back at the next click. A global function, so the MCT script (same Lua state in battle) can find it.
It forgets the remembered table only: the switches already clicked in this battle stay."""
LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
ANCHOR = "FOURTH.load_remembered()\n\nlocal function set_auto_for_unit(ui_id, marker, value)\n"
HOOK = """FOURTH.load_remembered()

-- the optional MCT page's reset, in battle: forget the remembered table and keep the file empty
function smart_ability_autocast_reset_remembered()
	for _, a in ipairs(ABILITIES) do a.remembered = nil end
	FOURTH.save_remembered()
end

local function set_auto_for_unit(ui_id, marker, value)
"""
for p in (LIVE, ANN):
    s = open(p, encoding="utf-8", newline="").read()
    assert "function smart_ability_autocast_reset_remembered()" not in s, p
    assert s.count(ANCHOR) == 1, p
    s = s.replace(ANCHOR, HOOK)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("patched", p)
