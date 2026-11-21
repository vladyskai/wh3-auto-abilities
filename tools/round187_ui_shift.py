#!/usr/bin/env python3
"""Round 187 (user, 2026-11-21: "we need to fix the UI scale ... when I change Resolution in the game, the A/M and the
arm all buttons are not aligned anymore").

THE CAUSE (the 2026-11-21 log, three battles): the M/A badges and the ALL button dock to hud_battle's BOTTOM-CENTRE with
offsets hand-tuned on a 1984 x 1116 UI space (2560 x 1440 at UI scale about 1.29), while the ability wheel hangs from
the BOTTOM-LEFT corner. At UI scale 1.6 (a 1600 x 900 UI space) the bottom centre moved (-192, -216) and the wheel
(0, -216), so every badge landed 192 px too far left (slot 1 at x = -65, the ALL button at -123: off screen).

THE FIX: a live correction, from position reads only (Position(), proven by the INVENTORY lines; no size read):
  ui_dx, ui_dy = (the wheel's shift) - (the bottom centre's shift) from the tuned frame, where
    the wheel   = ability_parent (tuned 42,893), else button_ability (96,845);
    the centre  = orders_parent (tuned 691,1055), else behaviour_parent (1021,1055), else button_parent (1072,1052).
  badge_offsets_for adds (ui_dx, ui_dy) to every ability badge's offset; the ALL button's dock offset is
  ALL_OX + ui_dx, ALL_OY + ui_dy. FOURTH.ui_shift_tick re-reads every 40 ui ticks (2 s), and when the correction changes it
  re-places every badge and the ALL button (a resolution change in battle follows within 2 s). On the tuned setting the
  correction is (0, 0): nothing moves. An unreadable reference keeps the last correction (0, 0 at start).
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

BLOCK = '''-- ============================================================================
-- ROUND 187 - THE BADGES FOLLOW THE WHEEL AT ANY RESOLUTION OR UI SCALE (user 2026-11-21: "we need to fix the UI
--   scale"). The badges and the ALL button dock to hud_battle's BOTTOM-CENTRE with offsets tuned on a 1984 x 1116 UI
--   space; the wheel hangs from the BOTTOM-LEFT. ui_dx / ui_dy = the wheel's shift minus the bottom centre's shift
--   from that tuned frame (Position() reads only), added to every badge offset and to the ALL button's; re-read every
--   UI_SHIFT_EVERY ui ticks (2 s); a change re-places every badge. (0, 0) on the tuned setting.
-- ============================================================================
FOURTH.ui_dx, FOURTH.ui_dy = 0, 0
FOURTH.UI_WHEEL_REFS = { { "ability_parent", 42, 893 }, { "button_ability", 96, 845 } }
FOURTH.UI_CENTRE_REFS = { { "orders_parent", 691, 1055 }, { "behaviour_parent", 1021, 1055 }, { "button_parent", 1072, 1052 } }
FOURTH.UI_SHIFT_EVERY = 40   -- ui ticks (the ui tick runs every 50 ms: 2 s)
FOURTH.ui_shift_n = 0

-- one component's screen position by id (the engine's recursive Find from the ui root, never find_uicomponent)
function FOURTH.ui_pos(id)
	local ok, x, y = pcall(function()
		local root = core:get_ui_root()
		if root == nil then return nil end
		local raw = root:Find(id, false)
		if raw == nil then return nil end
		return UIComponent(raw):Position()
	end)
	if ok and type(x) == "number" and type(y) == "number" then return x, y end
	return nil, nil
end

-- the shift of the first readable reference from its tuned position
function FOURTH.ui_ref_shift(refs)
	for i = 1, #refs do
		local r = refs[i]
		local x, y = FOURTH.ui_pos(r[1])
		if x ~= nil then return x - r[2], y - r[3], r[1] end
	end
	return nil, nil, nil
end

function FOURTH.ui_shift_tick()
	FOURTH.ui_shift_n = FOURTH.ui_shift_n + 1
	if FOURTH.ui_shift_n % FOURTH.UI_SHIFT_EVERY ~= 1 then return end
	local wx, wy, wid = FOURTH.ui_ref_shift(FOURTH.UI_WHEEL_REFS)
	local cx, cy, cid = FOURTH.ui_ref_shift(FOURTH.UI_CENTRE_REFS)
	if wx == nil or cx == nil then return end
	local dx, dy = wx - cx, wy - cy
	if dx == FOURTH.ui_dx and dy == FOURTH.ui_dy then return end
	FOURTH.ui_dx, FOURTH.ui_dy = dx, dy
	%LOG%
	if FOURTH.ui_replace ~= nil then pcall(FOURTH.ui_replace) end
	local st = FOURTH.all_state
	if st ~= nil and st.badge ~= nil then
		pcall(function() st.badge:SetDockOffset(FOURTH.ALL_OX + dx, FOURTH.ALL_OY + dy) end)
	end
end

'''
LOG = {True: ('log("UI SHIFT: the badges move by " .. tostring(dx) .. "," .. tostring(dy) .. " (wheel " .. tostring(wid) '
              '.. " " .. tostring(wx) .. "," .. tostring(wy) .. "; centre " .. tostring(cid) .. " " .. tostring(cx) .. "," '
              '.. tostring(cy) .. ")")'),
       False: "-- (the reading copy stays log-free)"}

COMMON = [
    ("\t\t\tst.badge:SetDockOffset(FOURTH.ALL_OX, FOURTH.ALL_OY)\n",
     "\t\t\tst.badge:SetDockOffset(FOURTH.ALL_OX + FOURTH.ui_dx, FOURTH.ALL_OY + FOURTH.ui_dy)   -- ROUND 187\n"),
    ("\tif st.badge ~= nil then pcall(function() st.badge:SetDockOffset(FOURTH.ALL_OX, FOURTH.ALL_OY) end) end\n",
     "\tif st.badge ~= nil then pcall(function() st.badge:SetDockOffset(FOURTH.ALL_OX + FOURTH.ui_dx, FOURTH.ALL_OY + FOURTH.ui_dy) end) end   -- ROUND 187\n"),
    ("\tpcall(FOURTH.all_badge_tick)\n",
     "\tpcall(FOURTH.ui_shift_tick)   -- ROUND 187: the badges follow the wheel at any resolution / UI scale\n"
     "\tpcall(FOURTH.all_badge_tick)\n"),
]
LIVE = [
    ("\t\t\treturn BADGE_X + (slot[1] - WHEEL_TOP_X), BADGE_Y + (slot[2] - WHEEL_TOP_Y),\n\t\t\t\tk, slot[1], slot[2]\n",
     "\t\t\treturn BADGE_X + (slot[1] - WHEEL_TOP_X) + FOURTH.ui_dx, BADGE_Y + (slot[2] - WHEEL_TOP_Y) + FOURTH.ui_dy,   -- ROUND 187\n"
     "\t\t\t\tk, slot[1], slot[2]\n"),
    ("\treturn BADGE_X + ability.ox, BADGE_Y + ability.oy, nil, nil, nil\n",
     "\treturn BADGE_X + ability.ox + FOURTH.ui_dx, BADGE_Y + ability.oy + FOURTH.ui_dy, nil, nil, nil   -- ROUND 187\n"),
    ("local function replace_all_badges()\n\tfor _, ability in ipairs(ABILITIES) do\n\t\tlocal state = ability_state[ability.marker]\n"
     "\t\tif state ~= nil then\n\t\t\tstate.placed = false\n\t\t\tpcall(place_badge, ability.marker)\n\t\tend\n\tend\nend\n",
     "local function replace_all_badges()\n\tfor _, ability in ipairs(ABILITIES) do\n\t\tlocal state = ability_state[ability.marker]\n"
     "\t\tif state ~= nil then\n\t\t\tstate.placed = false\n\t\t\tpcall(place_badge, ability.marker)\n\t\tend\n\tend\nend\n"
     "FOURTH.ui_replace = replace_all_badges   -- ROUND 187: the UI shift re-places every badge through it\n"),
]
ANN_ONLY = [
    ("\t\t\treturn BADGE_X + (slot[1] - WHEEL_TOP_X), BADGE_Y + (slot[2] - WHEEL_TOP_Y)\n",
     "\t\t\treturn BADGE_X + (slot[1] - WHEEL_TOP_X) + FOURTH.ui_dx, BADGE_Y + (slot[2] - WHEEL_TOP_Y) + FOURTH.ui_dy   -- ROUND 187\n"),
    ("\treturn BADGE_X + ability.ox, BADGE_Y + ability.oy\n",
     "\treturn BADGE_X + ability.ox + FOURTH.ui_dx, BADGE_Y + ability.oy + FOURTH.ui_dy   -- ROUND 187\n"),
]
ANCHOR = "function FOURTH.all_badge_tick()\n"


def sub(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a))
    return s.replace(a, b)


for path, live in ((SRC, True), (ANN, False)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "FOURTH.ui_shift_tick" not in s
    for a, b in COMMON + (LIVE if live else ANN_ONLY):
        s = sub(s, a, b)
    s = sub(s, ANCHOR, BLOCK.replace("%LOG%", LOG[live]) + ANCHOR)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "UI shift added")
