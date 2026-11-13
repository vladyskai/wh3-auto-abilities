#!/usr/bin/env python3
"""Round 145 (harness 144): THE BATTLEFIELD MAP PROBE - read-only (user request 2026-11-13: "see if we are able to have
an internal map of the units ... coordinates, entity numbers and size. Value of the units would also be useful ...
Especially to detect blobs of infantry"; the user chose "Yes, build the probe").

Every FOURTH.MAP_EVERY_S = 2 s of the conflict phase the LIVE build writes one MAP line per unit of both sides (our
units from the mod's own tracked list, the enemy from the main enemy army list) and one MAP_END line. Every read is
pcall'd and an unreadable value prints "?". It casts nothing, sets no state any trigger reads, and is called through
pcall at the very end of the poll body (after the drop walk), so an error in it can never cost a tick. The annotated
copy (log-free by rule) keeps the same reads into FOURTH.map_last instead of the log.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"


def sub(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a))
    return s.replace(a, b)


COMMON = r'''-- ============================================================================
-- ROUND 145 - THE BATTLEFIELD MAP PROBE (READ-ONLY; user request 2026-11-13).
--   Every FOURTH.MAP_EVERY_S seconds of the conflict phase: one MAP row per unit
--   of BOTH sides - our units from the mod's own tracked list, the enemy from
--   the main enemy army list. Per unit: the centre (position(), X/Z ground
--   plane), the officer's position, bearing(), ordered_width() (the frontage of
--   the formation it was ORDERED into, metres - not the live shape),
--   number_of_men_alive() / initial_number_of_men(), unary_hitpoints(),
--   strategic_value() (the engine's own "current strength" indicator - scale
--   unknown, first read in this round), is_infantry(), unit_class(),
--   is_visible_to_alliance(our alliance) (first read in this round), in melee,
--   moving, flying, routing. Every read is pcall'd; an unreadable value is "?".
--   It CASTS NOTHING and sets nothing any trigger reads. The depth of a block is
--   NOT readable: tools/analyze_map_log.py estimates it offline from the width,
--   the soldier count and the game's own spacing table.
-- ============================================================================
FOURTH.MAP_EVERY_S = 2
FOURTH.map_alliance = nil
FOURTH.map_last = nil

function FOURTH.map_num(f, fmt)
	local ok, v = pcall(f)
	if ok and type(v) == "number" then return string.format(fmt, v) end
	return "?"
end

function FOURTH.map_flag(f)
	local ok, v = pcall(f)
	if ok and v == true then return "1" end
	if ok and v == false then return "0" end
	return "?"
end

function FOURTH.map_xz(f)
	local x, z = "?", "?"
	pcall(function()
		local p = f()
		x = string.format("%.1f", p:get_x())
		z = string.format("%.1f", p:get_z())
	end)
	return x, z
end

-- OUR units' type: the identity watch's own cache when it has it, else ONE read
-- per unit per battle (kept here), so the map adds no repeated type() reads to
-- the units the poll loop already watches
FOURTH.map_type = {}
function FOURTH.map_own_type(u, id)
	local t = identity_by_unit[id] or FOURTH.map_type[id]
	if t ~= nil then return t end
	if FOURTH.map_type[id] == false then return "?" end
	local ok, v = pcall(function() return u:type() end)
	if ok and type(v) == "string" and v ~= "" then
		FOURTH.map_type[id] = v
		return v
	end
	FOURTH.map_type[id] = false
	return "?"
end

-- one unit's row: plain "key=value" pairs, one line, nothing but reads. For OUR
-- units the routing read is skipped (the player sees it, and the poll loop
-- already reads it every tick).
function FOURTH.map_row(u, side, t, alliance)
	local id, typ, cls = "?", "?", "?"
	pcall(function() id = tostring(u:unique_ui_id()) end)
	if side == "P" then
		typ = FOURTH.map_own_type(u, id)
	else
		pcall(function() typ = tostring(u:type()) end)
	end
	pcall(function() cls = tostring(u:unit_class()) end)
	local x, z = FOURTH.map_xz(function() return u:position() end)
	local ox, oz = FOURTH.map_xz(function() return u:position_of_officer() end)
	local vis = "?"
	if alliance ~= nil then vis = FOURTH.map_flag(function() return u:is_visible_to_alliance(alliance) end) end
	return "MAP t=" .. t .. " side=" .. side .. " id=" .. id .. " type=" .. typ
		.. " x=" .. x .. " z=" .. z .. " ox=" .. ox .. " oz=" .. oz
		.. " bearing=" .. FOURTH.map_num(function() return u:bearing() end, "%.0f")
		.. " width=" .. FOURTH.map_num(function() return u:ordered_width() end, "%.1f")
		.. " men=" .. FOURTH.map_num(function() return u:number_of_men_alive() end, "%d")
		.. "/" .. FOURTH.map_num(function() return u:initial_number_of_men() end, "%d")
		.. " hp=" .. FOURTH.map_num(function() return u:unary_hitpoints() end, "%.2f")
		.. " sv=" .. FOURTH.map_num(function() return u:strategic_value() end, "%.1f")
		.. " inf=" .. FOURTH.map_flag(function() return u:is_infantry() end)
		.. " class=" .. cls .. " vis=" .. vis
		.. " melee=" .. FOURTH.map_flag(function() return u:is_in_melee() end)
		.. " moving=" .. FOURTH.map_flag(function() return u:is_moving() end)
		.. " fly=" .. FOURTH.map_flag(function() return u:is_currently_flying() end)
		.. " routing=" .. ((side == "P") and "-" or FOURTH.map_flag(function() return u:is_routing() end))
end

-- every MAP_EVERY_S seconds: the rows of both sides, in a list
function FOURTH.map_rows(tick)
	local every = math.floor((FOURTH.MAP_EVERY_S * 1000) / POLL_MS)
	if every < 1 or (tick % every) ~= 0 then return nil end
	local t = string.format("%.1f", tick * POLL_MS / 1000)
	if FOURTH.map_alliance == nil then
		pcall(function() FOURTH.map_alliance = bm:get_player_alliance() end)
	end
	local alliance = FOURTH.map_alliance
	local rows, n_own, n_en = {}, 0, 0
	for i = 1, #(tracked_units or {}) do
		local u = tracked_units[i] and tracked_units[i].unit
		if u ~= nil then
			rows[#rows + 1] = FOURTH.map_row(u, "P", t, alliance)
			n_own = n_own + 1
		end
	end
	local ok_c, coll = pcall(function() return bm:get_scriptunits_for_main_enemy_army_to_local_player() end)
	if ok_c and coll ~= nil then
		local ok_n, n = pcall(function() return coll:count() end)
		if ok_n and type(n) == "number" then
			for i = 1, n do
				local e = nil
				pcall(function() e = coll:item(i).unit end)
				if e ~= nil then
					rows[#rows + 1] = FOURTH.map_row(e, "E", t, alliance)
					n_en = n_en + 1
				end
			end
		end
	end
	rows[#rows + 1] = "MAP_END t=" .. t .. " own=" .. n_own .. " enemy=" .. n_en
		.. " alliance=" .. ((alliance ~= nil) and "1" or "?")
	return rows
end

'''
LIVE_TICK = r'''-- the LIVE build writes the rows to the battle log
function FOURTH.map_tick(tick)
	local rows = FOURTH.map_rows(tick)
	if rows == nil then return end
	for i = 1, #rows do log(rows[i]) end
end

'''
ANN_TICK = r'''-- the reading copy keeps the rows instead of writing them (it is log-free by rule)
function FOURTH.map_tick(tick)
	local rows = FOURTH.map_rows(tick)
	if rows ~= nil then FOURTH.map_last = rows end
end

'''
HOOK_OLD = "\tfor g = 1, #gone_ids do\n\t\tdrop_unit_by_ui_id(gone_ids[g])\n\tend\n"
HOOK_NEW = HOOK_OLD + ("\n\t-- ROUND 145: the read-only battlefield map probe (casts nothing; pcall'd so it can never\n"
                       "\t-- cost a tick)\n\tpcall(FOURTH.map_tick, tick_count)\n")
ANCHOR = "FOURTH.evaluators = {\n"
for path, tick in ((SRC, LIVE_TICK), (ANN, ANN_TICK)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "FOURTH.map_tick" not in s
    s = sub(s, ANCHOR, COMMON + tick + ANCHOR)
    s = sub(s, HOOK_OLD, HOOK_NEW)
    assert "string.find" not in COMMON + tick
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)
