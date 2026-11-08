--------------------------------------------------------------------------------
-- zz_probe_step.lua - THROWAWAY STEP-PROBE PACK (separate from the main mod)
--
-- QUESTION THIS ROUND SETTLES: WHY does the Witch Hunter WALK A LITTLE after /
-- while a SCRIPTED enemy-targeted cast (Accusation) auto-casts? Five candidate
-- explanations exist with no evidence for any of them, so this probe records the
-- reads and the engine command events needed to tell them apart from ONE log.
--
-- ALREADY KNOWN (do not re-establish):
--   * Working cast route: fetch caster + target FRESH each cast from the
--     script-unit enumerators and call
--         caster_su.uc:perform_special_ability(key, enemy_su.unit)
--     (proven live: target effect count 0 -> 1).
--   * unit:unit_distance(other) is EDGE-TO-EDGE (bounding-box aware,
--     battle_unit.lua:160) and position() is the CENTRE of the main squad, so a
--     raw unit_distance can read 0.0 without either unit having moved.
--   * The main mod's trigger is enemy:is_in_melee() OR enemy:is_under_missile_attack().
--   * target_intercept_range IS the cast range (Accusation 75 m).
--   * A cast may be REFUSED (engine cooldown) and the engine may or may not act
--     on a refused cast.
--
-- THE FIVE CANDIDATES (this probe's VERDICT line discriminates them):
--   1. The engine issues its own ATTACK order (ability ai_usage = hex_melee).
--      -> VERDICT order_after_attack=y
--   2. The engine MOVES the caster to get in range (move-into-range response,
--      possibly on a refusal). -> VERDICT order_after_move=y
--   3. The step is cast ANIMATION / the unit shuffling to face its target.
--      -> moved_total small, NO order, NOT refused
--   4. The unit ALREADY had a move/attack order before the mod cast.
--      -> VERDICT already_moving_before=y
--   5. COOLDOWN re-approach: the cast was refused and the engine re-approaches.
--      -> VERDICT refused=y (+ order_after_move=y if the engine drives it)
--
-- WHAT THE PROBE LOGS, PER CAST (up to 4 capped casts, all tick-stamped):
--   (a) BEFORE: caster position (x,y 1dp), edge-to-edge unit_distance(target)
--       (1dp), is_in_melee() for BOTH units, target is_under_missile_attack(),
--       and an EXHAUSTIVE movement/order/state member inventory of the caster's
--       battle_unit AND its script_unit (every read the API dump offers that
--       answers "is this unit already doing something").
--   (b) EVERY engine command event, from a callback registered for ALL 26
--       documented command event types (battle.lua:122-147), logged with name +
--       payload (bool1/string1/unit) + tick, so an engine-issued Attack/Move
--       order around the cast is visible AND distinguishable from our own
--       ability command.
--   (c) THE CAST: CAST-PLAN / TRY / accepted= / err=, plus ONE immediate
--       same-tick position re-read right after the call returns (POSTPOS).
--   (d) AFTER: sample the caster's position every poll for up to ~6 polls
--       (12 s at 2 s polling), each SAMPLE line carrying the tick, the delta in
--       metres from the pre-cast position, the point-to-point step delta, the
--       unit_distance and both melee flags. Sampling stops early once the
--       position has stopped growing (2 non-growing samples).
--   (e) A REFUSED cast is logged prominently (REFUSED ...) and sampling
--       continues - that is candidate-5 evidence.
--   (f) STEP RESULT + machine-checkable VERDICT per cast:
--       VERDICT cast=N moved_total=.. order_after_attack=.. order_after_move=..
--               already_moving_before=.. refused=..
--
-- SAFETY / HYGIENE:
--   * Conflict-phase gate only, mirroring the main mod (bm:is_conflict_phase()),
--     logging the phase NAME and the boolean on every poll.
--   * Hard caps: ~4 casts and a poll cap; every engine touch is pcall'd.
--   * ZERO state writes beyond the ability casts themselves; the forbidden-write
--     trip counter (P.trips) must stay 0, write-shaped members are presence-only
--     and never called.
--   * Ships as its OWN Movie pack (zz_probe_step.pack) holding this ONE file.
--     The MAIN MOD is not in this pack and is never touched (byte-identical).
--
-- REMOVAL: delete zz_probe_step.pack from the game's data/ folder (and the log
-- file zz_probe_step_log.txt next to Warhammer3.exe). One pack, one file, one log.
--------------------------------------------------------------------------------

-- The probe's whole state lives in ONE chunk local (P) so the file adds a single
-- local to the main chunk and can never trip Lua's 200-local ceiling.
local P = {}

P.TAG       = "[zz_probe_step] "
P.LOG_FILE  = "zz_probe_step_log.txt"
P.POLL_MS   = 2000
P.MAX_POLLS = 44
P.MAX_CASTS = 4
P.SAMPLE_POLLS = 6
P.NAME      = "zz_probe_step_poll"

-- a key is cast at most once per this window; 6 sample polls at 2 s = 12 s, so
-- the next cast becomes eligible exactly when the previous cast's sampling ends.
P.CAST_COOLDOWN_MS = 12000

-- the probe ARMS ITSELF (needs no main-mod badge): a local unit owning any of
-- these enemy-targeted ability keys is a valid caster.
P.ARMED_KEYS = {
	"wh_main_hero_abilities_accusation",
	"wh2_main_character_abilities_assassins_trophy",
	"wh3_dlc29_hero_active_amulet_of_pha_stah",
}
P.ARMED_SET = {}

-- every movement / order / state read the API dump offers that could answer
-- "is this unit already doing something". Names that do not exist are reported
-- ABSENT; names that exist but need args report their error signature.
P.MOVE_READS = {
	"position", "ordered_position", "ordered_bearing", "ordered_width", "bearing",
	"position_of_officer",
	"is_moving", "is_moving_fast", "is_idle", "is_attacking", "is_charging",
	"is_in_melee", "is_under_missile_attack",
	"slow_speed", "fast_speed", "speed", "velocity",
	"destination", "has_order", "current_order", "order_queue", "formation_position",
	"current_target", "unit_in_range", "unit_distance",
	"is_ai_controlled", "is_script_controlled", "is_player_controlled",
	"has_attribute", "is_behaviour_active",
}
-- the script_unit wrapper side (the dump's own extra movement reads)
P.SU_READS = {
	"has_moved", "get_cached_position", "get_cached_destination_position",
	"get_cached_destination_bearing", "get_cached_destination_width",
	"position_offset", "is_in_melee",
}

-- write-shaped member prefixes: a member whose name starts with one of these is
-- presence-only and is NEVER called, so no accidental write can occur.
P.WRITE_PREFIX = {
	"set", "reset", "clear", "goto", "teleport", "turn", "cache", "kill", "heal",
	"reduce", "respawn", "select", "highlight", "mark", "deploy", "attack",
	"melee", "fire", "withdraw", "halt", "step", "increment", "decrement",
	"change", "occupy", "rotate", "interact", "besiege", "disable", "enable",
	"play", "trigger", "add", "remove", "apply", "force",
}

-- the 26 documented command event types (battle.lua:122-147). Registering a
-- callback for EVERY one makes every engine-issued command visible in the log.
P.CMD_NAMES = {
	"Group Created", "Group Destroyed", "Repair Mode",
	"Move", "Move Orientation Width", "Move Rotation Angle", "Change Speed",
	"Attack Unit", "Change Skirmish", "Change Melee", "Change Formation",
	"Attack Building", "Climb/Dock Building", "Special Ability", "Shot Type",
	"Fire At Will", "Broadside Attack", "Naval Shot Type", "Ram", "Withdraw",
	"Halt", "Double Click", "Entity Hit", "Double Click Unit Card",
	"Unit Left Battlefield", "Battle Results",
}

-- run state
P.polls_done   = 0
P.elapsed_ms   = 0
P.casts_done   = 0
P.last_cast_ms = -1
P.fp_logged    = false
P.finished     = false
P.log_handle   = nil
P.logging_off  = false

-- gate bookkeeping (one-time transition lines)
P.gate_wait_logged  = false
P.gate_enter_logged = false

-- command-event log (name + tick + payload) and the per-cast window
P.cmd_events = {}
P.cmd_handlers_ok = 0

-- the active post-cast sampling record and the active command window
P.sample = nil
P.win    = nil

-- forbidden-write trip counter (must stay 0)
P.trips = 0

-- the ARRAY half of ARMED_KEYS + the SET half (a lone set has #==0; a lone array
-- cannot be keyed by name) - both are kept for the loop and the guard.
for i = 1, #P.ARMED_KEYS do P.ARMED_SET[P.ARMED_KEYS[i]] = true end


-- ============================================================================
-- 1. THE PROBE'S OWN LOG (append + flush per line, the established idiom)
-- ============================================================================

P.write = function(line)
	if P.logging_off then return end
	if P.log_handle == nil then
		local ok, h = pcall(io.open, P.LOG_FILE, "a")
		if not ok or h == nil then
			P.logging_off = true
			return
		end
		P.log_handle = h
		pcall(function()
			P.log_handle:write("\n======== zz_probe_step session ========\n")
			P.log_handle:flush()
		end)
	end
	pcall(function()
		P.log_handle:write(line .. "\n")
		P.log_handle:flush()
	end)
end

P.log = function(message)
	local line = P.TAG .. tostring(message)
	P.write(line)
	if ModLog ~= nil then pcall(ModLog, line) end
	pcall(out, line)
end


-- ============================================================================
-- 2. SAFE HELPERS (every engine touch is pcall'd; no error can escape)
-- ============================================================================

P.truncate = function(s, n)
	s = tostring(s)
	if #s > n then return string.sub(s, 1, n) .. "..." end
	return s
end

P.num = function(v)
	if type(v) ~= "number" then return tostring(v) end
	if v ~= v then return "nan" end
	if v == math.floor(v) and math.abs(v) < 1e15 then return tostring(math.floor(v)) end
	return string.format("%.1f", v)
end

P.fmt = function(v)
	if v == nil then return "nil" end
	if type(v) ~= "number" then return tostring(v) end
	if v ~= v then return "nan" end
	return string.format("%.2f", v)
end

-- One pcall'd read, rendered as a short string; an error becomes "<ERR: ...>".
P.read1 = function(fn)
	local ok, v = pcall(fn)
	if not ok then return "<ERR: " .. P.truncate(v, 50) .. ">" end
	if v == nil then return "nil" end
	if type(v) == "number" then return P.num(v) end
	if type(v) == "boolean" then return tostring(v) end
	local ok2, s = pcall(tostring, v)
	if ok2 and s ~= nil then return P.truncate(s, 40) end
	return "<opaque>"
end

-- position() of a battle_unit: returns (raw_vec, "x,y" 1dp, x, y)
P.read_pos = function(unit)
	if unit == nil then return nil, "nil", nil, nil end
	local ok, v = pcall(function() return unit:position() end)
	if not ok or v == nil then return nil, "<ERR: " .. P.truncate(ok and "nil" or v, 40) .. ">", nil, nil end
	local x, y
	local okx, vx = pcall(function() return v:get_x() end)
	if okx and type(vx) == "number" then x = vx end
	local oky, vy = pcall(function() return v:get_y() end)
	if oky and type(vy) == "number" then y = vy end
	if x ~= nil and y ~= nil then
		return v, string.format("%.1f,%.1f", x, y), x, y
	end
	return v, "<vec>", nil, nil
end

P.dist2 = function(x1, y1, x2, y2)
	if x1 == nil or y1 == nil or x2 == nil or y2 == nil then return nil end
	local dx, dy = x1 - x2, y1 - y2
	return math.sqrt(dx * dx + dy * dy)
end

P.is_write = function(name)
	local n = string.lower(tostring(name))
	for i = 1, #P.WRITE_PREFIX do
		local p = P.WRITE_PREFIX[i]
		if string.sub(n, 1, #p) == p then return true end
	end
	return false
end


-- ============================================================================
-- 3. COLLECTION / CASTER HELPERS
-- ============================================================================

P.owned_armed_key = function(unit)
	local set = {}
	local function absorb(ok, owned)
		if ok and type(owned) == "table" then
			for _, v in pairs(owned) do
				if type(v) == "string" then set[v] = true end
			end
		end
	end
	absorb(pcall(function() return unit:owned_special_abilities() end))
	absorb(pcall(function() return unit:owned_non_passive_special_abilities() end))
	for i = 1, #P.ARMED_KEYS do
		if set[P.ARMED_KEYS[i]] then return P.ARMED_KEYS[i] end
	end
	return nil
end

-- FRESH caster this instant: enumerate our army NOW and return the first
-- {su, unit, uc, key} whose unit owns an armed key. Never hold a controller.
P.fresh_caster = function()
	local ok, coll = pcall(function() return bm:get_scriptunits_for_local_players_army() end)
	if not ok or coll == nil then return nil end
	local n = 0
	pcall(function() n = coll:count() end)
	if type(n) ~= "number" then return nil end
	for i = 1, n do
		local ok2, su = pcall(function() return coll:item(i) end)
		if ok2 and su ~= nil then
			local unit, uc
			pcall(function() unit = su.unit end)
			pcall(function() uc = su.uc end)
			if unit ~= nil then
				local key = P.owned_armed_key(unit)
				if key ~= nil then return { su = su, unit = unit, uc = uc, key = key } end
			end
		end
	end
	return nil
end

-- up to 4 fresh enemy units (each keeps BOTH handles)
P.read_enemies = function()
	local list = {}
	local ok, coll = pcall(function() return bm:get_scriptunits_for_main_enemy_army_to_local_player() end)
	if not ok or coll == nil then return list end
	local n = 0
	pcall(function() n = coll:count() end)
	if type(n) ~= "number" then return list end
	local cap = n
	if cap > 4 then cap = 4 end
	for i = 1, cap do
		local ok2, su = pcall(function() return coll:item(i) end)
		if ok2 and su ~= nil then
			local unit
			pcall(function() unit = su.unit end)
			if unit ~= nil then
				local ui
				pcall(function() ui = unit:unique_ui_id() end)
				list[#list + 1] = {
					su = su, unit = unit, ui_id = ui,
					desc = P.read1(function() return unit:type() end),
				}
			end
		end
	end
	return list
end


-- ============================================================================
-- 4. THE MOVEMENT / ORDER / STATE READ INVENTORY  (item a)
--    A member that exists and is read-shaped is CALLED (pcall'd); a member that
--    exists and is write-shaped is reported presence-only and NEVER called.
-- ============================================================================

P.inventory = function(handle, hname, list, target_unit, pre_vec)
	if handle == nil then
		P.log("READ " .. hname .. " ABSENT: <no handle>")
		return
	end
	local absent = {}
	for i = 1, #list do
		local name = list[i]
		local ok, m = pcall(function() return handle[name] end)
		if not ok or m == nil then
			absent[#absent + 1] = name
		elseif type(m) ~= "function" then
			P.log("READ " .. hname .. "." .. name .. " => value(" .. type(m) .. ")="
				.. P.read1(function() return m end))
		elseif P.is_write(name) then
			P.log("READ " .. hname .. "." .. name .. " => EXISTS(fn) NOT CALLED (write-shaped)")
		else
			local val
			if name == "unit_distance" and target_unit ~= nil then
				val = P.read1(function() return handle:unit_distance(target_unit) end)
			elseif name == "unit_in_range" and target_unit ~= nil then
				val = P.read1(function() return handle:unit_in_range(target_unit) end)
			elseif name == "has_moved" and pre_vec ~= nil then
				val = P.read1(function() return handle:has_moved(pre_vec, 0.1) end)
			elseif name == "has_attribute" then
				val = P.read1(function() return handle:has_attribute("moving") end)
			elseif name == "is_behaviour_active" then
				val = P.read1(function() return handle:is_behaviour_active("fire_at_will") end)
			else
				val = P.read1(function() return handle[name]() end)
			end
			P.log("READ " .. hname .. "." .. name .. " => " .. val)
		end
	end
	if #absent > 0 then
		P.log("READ " .. hname .. " ABSENT (" .. #absent .. "): " .. table.concat(absent, ", "))
	end
end


-- ============================================================================
-- 5. ONE CAST  (pre-reads + inventory + TRY + immediate same-tick re-read)
-- ============================================================================

P.do_cast = function(cast_n)
	local caster = P.fresh_caster()
	if caster == nil then
		P.log("CAST-PLAN cast=" .. cast_n .. " skipped: no local unit owns an armed key")
		return false
	end
	local enemies = P.read_enemies()
	if #enemies == 0 then
		P.log("CAST-PLAN cast=" .. cast_n .. " skipped: no enemy unit available")
		return false
	end
	local pick = ((cast_n - 1) % #enemies) + 1
	local tgt = enemies[pick]

	local unit, uc, su, key = caster.unit, caster.uc, caster.su, caster.key
	if uc == nil then
		P.log("CAST-PLAN cast=" .. cast_n .. " skipped: the fresh script_unit has no controller")
		return false
	end

	-- ---- CAST-PLAN ----
	P.log("")
	P.log("CAST-PLAN cast=" .. cast_n .. " key=" .. tostring(key)
		.. " target#" .. tostring(pick) .. "/" .. tostring(#enemies)
		.. " target_type=" .. tgt.desc)

	-- ---- (a) BEFORE the cast: position, edge-to-edge distance, melee flags ----
	local cpos, ctxt, cx, cy = P.read_pos(unit)
	local tpos, ttxt, tx, ty = P.read_pos(tgt.unit)
	local dist = P.read1(function() return unit:unit_distance(tgt.unit) end)
	local c_melee = P.read1(function() return unit:is_in_melee() end)
	local t_melee = P.read1(function() return tgt.unit:is_in_melee() end)
	local t_missile = P.read1(function() return tgt.unit:is_under_missile_attack() end)

	local ok_mov, movv = pcall(function() return unit:is_moving() end)
	local ok_idle, idle = pcall(function() return unit:is_idle() end)
	local mov_before = (ok_mov and movv == true) or (ok_idle and idle == false)

	P.log("BEFORE cast=" .. cast_n
		.. " caster_pos=" .. ctxt .. " target_pos=" .. ttxt
		.. " unit_distance=" .. dist .. " (edge-to-edge, battle_unit.lua:160)"
		.. " caster_in_melee=" .. c_melee
		.. " target_in_melee=" .. t_melee
		.. " target_under_missile=" .. t_missile
		.. " caster_is_moving=" .. (ok_mov and tostring(movv == true) or "<ERR>")
		.. " caster_is_idle=" .. (ok_idle and tostring(idle == true) or "<ERR>"))

	-- ---- (a cont.) exhaustive movement/order/state member inventory ----
	P.inventory(unit, "unit", P.MOVE_READS, tgt.unit, cpos)
	P.inventory(su, "script_unit", P.SU_READS, tgt.unit, cpos)

	-- ---- open the command window BEFORE the cast ----
	P.win = { cast = cast_n, from_tick = P.polls_done, mov_before = mov_before, refused = false }

	local can = "?"
	local okc, cv = pcall(function() return unit:can_perform_special_ability(key) end)
	if okc then can = tostring(cv == true) end

	-- ---- (c) THE CAST ----
	P.log("TRY cast=" .. cast_n .. " key=" .. tostring(key)
		.. " target_type=" .. tgt.desc .. " can=" .. can
		.. " route=uc:perform_special_ability(key, enemy_su.unit)")
	local accepted, err = pcall(function() return uc:perform_special_ability(key, tgt.unit) end)
	if accepted ~= true then accepted = false end
	local err_txt = ""
	if not accepted then
		if err ~= nil and err ~= true and err ~= false then err_txt = P.truncate(tostring(err), 110) end
	end
	P.log("ACCEPTED cast=" .. cast_n .. " accepted=" .. tostring(accepted)
		.. " err=" .. (accepted and "-" or (err_txt ~= "" and err_txt or "<no error text>")))

	-- ---- (c cont.) ONE immediate same-tick position re-read (right after the
	-- call returned) - this separates an instantaneous animation/order from a
	-- later walk. ----
	local _, p2txt, p2x, p2y = P.read_pos(unit)
	local imm = P.dist2(cx, cy, p2x, p2y)
	P.log("POSTPOS cast=" .. cast_n .. " pos=" .. p2txt
		.. " delta=" .. P.fmt(imm) .. "m (same tick, immediately after the call returned)")

	if not accepted then
		P.win.refused = true
		P.log("REFUSED cast=" .. cast_n
			.. " <- the cast was REFUSED (engine cooldown); sampling continues -"
			.. " this is CANDIDATE-5 evidence (does the engine re-approach on its own?)")
	end

	P.casts_done = P.casts_done + 1
	P.last_cast_ms = P.elapsed_ms

	-- ---- (d) arm the post-cast sampler ----
	P.sample = {
		cast = cast_n, unit = unit, tgt = tgt.unit, key = key, desc = tgt.desc,
		pre_vec = cpos, pre_x = cx, pre_y = cy,
		prev_x = p2x, prev_y = p2y,
		n = 0, last_delta = (imm or 0), moved_total = (imm or 0), nogrow = 0,
	}
	P.log("SAMPLING cast=" .. cast_n .. " begins: up to " .. P.SAMPLE_POLLS
		.. " polls (" .. (P.SAMPLE_POLLS * P.POLL_MS / 1000) .. "s), stops early if the delta stops growing")
	return true
end


-- ============================================================================
-- 6. THE POST-CAST SAMPLER  (item d) + STEP RESULT / VERDICT  (item f)
-- ============================================================================

P.finish_sample = function()
	local s = P.sample
	if s == nil then return end
	local w = P.win
	local seen, atk, mov = {}, "n", "n"
	if w ~= nil then
		for i = 1, #P.cmd_events do
			local e = P.cmd_events[i]
			if e.tick >= w.from_tick and e.tick <= P.polls_done then
				seen[#seen + 1] = e.name .. "@" .. tostring(e.tick)
				if e.name == "Attack Unit" or e.name == "Attack Building" then atk = "y" end
				if e.name == "Move" or e.name == "Move Orientation Width"
					or e.name == "Move Rotation Angle" or e.name == "Change Speed" then mov = "y" end
			end
		end
	end
	local mt = s.moved_total or 0
	P.log("STEP RESULT cast=" .. s.cast
		.. " moved=" .. P.fmt(mt) .. "m during=" .. tostring(s.n) .. "polls"
		.. " orders_seen=" .. (#seen > 0 and table.concat(seen, ",") or "-")
		.. " key=" .. tostring(s.key))
	P.log("VERDICT cast=" .. s.cast
		.. " moved_total=" .. P.fmt(mt)
		.. " order_after_attack=" .. atk
		.. " order_after_move=" .. mov
		.. " already_moving_before=" .. ((w ~= nil and w.mov_before) and "y" or "n")
		.. " refused=" .. ((w ~= nil and w.refused) and "y" or "n"))
	P.sample = nil
	P.win = nil
end

P.do_sample = function()
	local s = P.sample
	if s == nil then return end
	local unit, tgt = s.unit, s.tgt
	local _, ptxt, px, py = P.read_pos(unit)
	local dpre = P.dist2(s.pre_x, s.pre_y, px, py)
	local dstep = P.dist2(s.prev_x, s.prev_y, px, py)
	s.n = s.n + 1
	if dpre ~= nil and (s.moved_total == nil or dpre > s.moved_total) then s.moved_total = dpre end

	local dist = P.read1(function() return unit:unit_distance(tgt) end)
	local cm = P.read1(function() return unit:is_in_melee() end)
	local tm = P.read1(function() return tgt:is_in_melee() end)

	P.log("SAMPLE cast=" .. s.cast .. " n=" .. tostring(s.n) .. "/" .. tostring(P.SAMPLE_POLLS)
		.. " tick=" .. tostring(P.polls_done) .. " pos=" .. ptxt
		.. " delta_from_pre=" .. P.fmt(dpre) .. "m"
		.. " step_delta=" .. P.fmt(dstep) .. "m"
		.. " unit_distance=" .. dist
		.. " caster_in_melee=" .. cm .. " target_in_melee=" .. tm)

	if dpre ~= nil and dpre > (s.last_delta or 0) + 0.05 then
		s.nogrow = 0
	else
		s.nogrow = s.nogrow + 1
	end
	if dpre ~= nil then s.last_delta = dpre end
	s.prev_x, s.prev_y = px, py

	if s.n >= P.SAMPLE_POLLS or s.nogrow >= 2 then
		P.finish_sample()
	end
end


-- ============================================================================
-- 7. ONE POLL  (conflict phase only; capped)
-- ============================================================================

P.run_poll = function(reason)
	if P.finished then return end
	if P.polls_done >= P.MAX_POLLS then
		P.finished = true
		P.log("probe finished (poll cap " .. tostring(P.MAX_POLLS) .. ")")
		return
	end

	-- THE GATE - mirrors the main mod exactly: act only in the conflict phase.
	local ok_phase, conflict = pcall(function() return bm:is_conflict_phase() end)
	local phase_name = "?"
	pcall(function() phase_name = bm:get_current_phase_name() end)

	if not ok_phase or conflict ~= true then
		if not P.gate_wait_logged then
			P.gate_wait_logged = true
			local ctxt = ok_phase and tostring(conflict) or ("<ERR: " .. P.truncate(conflict, 60) .. ">")
			P.log("GATE waiting for conflict: phase=" .. tostring(phase_name)
				.. " conflict=" .. ctxt
				.. " (no poll runs until bm:is_conflict_phase() is true - the main mod's own gate)")
		end
		return
	end

	if not P.gate_enter_logged then
		P.gate_enter_logged = true
		P.log("GATE conflict phase ENTERED: phase=" .. tostring(phase_name)
			.. " conflict=true - polls begin (the engine names the conflict phase \"Deployed\")")
	end

	P.polls_done = P.polls_done + 1
	P.elapsed_ms = (P.polls_done - 1) * P.POLL_MS

	P.log("")
	P.log("=== poll " .. tostring(P.polls_done) .. "/" .. tostring(P.MAX_POLLS)
		.. (reason and (" (" .. tostring(reason) .. ")") or "")
		.. " | phase=" .. tostring(phase_name)
		.. " | conflict=" .. tostring(conflict)
		.. " | t=" .. tostring(math.floor(P.elapsed_ms / 1000)) .. "s"
		.. " | casts=" .. tostring(P.casts_done) .. "/" .. tostring(P.MAX_CASTS) .. " ===")

	-- (1) if a cast is being sampled, this poll IS a sample - do not cast.
	if P.sample ~= nil then
		pcall(P.do_sample)
	elseif P.casts_done >= P.MAX_CASTS then
		P.log("CASTS capped (" .. tostring(P.MAX_CASTS) .. ") - sampling done, probe idle")
	elseif P.last_cast_ms >= 0 and (P.elapsed_ms - P.last_cast_ms) < P.CAST_COOLDOWN_MS then
		P.log("CASTS spacing: " .. tostring(math.ceil((P.CAST_COOLDOWN_MS - (P.elapsed_ms - P.last_cast_ms)) / 1000))
			.. "s until cast " .. tostring(P.casts_done + 1)
			.. " (>= " .. tostring(P.CAST_COOLDOWN_MS / 1000) .. "s between casts)")
	else
		pcall(P.do_cast, P.casts_done + 1)
	end

	-- (2) one-time first-non-player-army line (context)
	if not P.fp_logged then
		P.fp_logged = true
		local ok, army = pcall(function() return bm:get_first_non_player_army() end)
		if ok and army ~= nil then
			local units
			pcall(function() units = army:units() end)
			if units ~= nil then
				local cnt
				pcall(function() cnt = units:count() end)
				P.log("E first_non_player_army():units() count=" .. P.num(cnt))
			end
		end
	end

	if P.polls_done >= P.MAX_POLLS then
		P.finished = true
		P.log("probe finished (poll cap " .. tostring(P.MAX_POLLS) .. ")")
	end
end

P.tick = function()
	local ok, err = pcall(P.run_poll, nil)
	if not ok then
		P.log("POLL ERROR (swallowed - engine callbacks stay alive): " .. P.truncate(err, 160))
	end
end


-- ============================================================================
-- 8. THE COMMAND-EVENT INSTRUMENT  (item b)
--    Registered for ALL 26 documented command event types, so EVERY engine-issued
--    command is logged with its payload and tick.
-- ============================================================================

P.on_cmd = function(ctx)
	local name = P.read1(function() return ctx:get_name() end)
	local b1   = P.read1(function() return ctx:get_bool1() end)
	local s1   = P.read1(function() return ctx:get_string1() end)
	local unitv = "nil"
	local ok_u, u = pcall(function() return ctx:get_unit() end)
	if ok_u and u ~= nil then unitv = P.read1(function() return u:type() end) end
	local posv = "nil"
	local ok_p, pv = pcall(function() return ctx:get_position() end)
	if ok_p and pv ~= nil then
		local okx, vx = pcall(function() return pv:get_x() end)
		local oky, vy = pcall(function() return pv:get_y() end)
		if okx and oky and type(vx) == "number" and type(vy) == "number" then
			posv = string.format("%.1f,%.1f", vx, vy)
		else
			posv = "<vec>"
		end
	end
	P.cmd_events[#P.cmd_events + 1] = { name = name, tick = P.polls_done, b1 = b1, s1 = s1 }
	P.log("CMD tick=" .. tostring(P.polls_done) .. " name=" .. name
		.. " bool1=" .. b1 .. " str1=" .. s1 .. " unit=" .. unitv .. " pos=" .. posv)
end


-- ============================================================================
-- 9. CONSOLE HOOK + START UP
-- ============================================================================

function zz_probe_step_status()
	pcall(P.run_poll, "console")
	local summary = "zz_probe_step: polls=" .. tostring(P.polls_done) .. "/" .. tostring(P.MAX_POLLS)
		.. " casts=" .. tostring(P.casts_done) .. "/" .. tostring(P.MAX_CASTS)
		.. " sampling=" .. tostring(P.sample ~= nil)
		.. " cmds=" .. tostring(#P.cmd_events)
		.. " cmd_handlers=" .. tostring(P.cmd_handlers_ok)
		.. " trips=" .. tostring(P.trips) .. " log=" .. P.LOG_FILE
	P.log("STATUS (console): " .. summary)
	return summary
end

P.log("loaded from script/battle/mod/ (auto-load proof). Log file: " .. P.LOG_FILE
	.. " | STEP PROBE: up to " .. tostring(P.MAX_CASTS) .. " capped casts, "
	.. tostring(P.SAMPLE_POLLS) .. "-poll position sampling after each, "
	.. tostring(P.CAST_COOLDOWN_MS / 1000) .. "s between casts | poll every "
	.. tostring(P.POLL_MS / 1000) .. "s, max " .. tostring(P.MAX_POLLS)
	.. " polls | all " .. tostring(#P.CMD_NAMES) .. " command event types logged"
	.. " | console: zz_probe_step_status()")

-- register EVERY documented command event type before anything else can fire
do
	local names = P.CMD_NAMES
	for i = 1, #names do
		local nm = names[i]
		local ok, e = pcall(function()
			bm:register_command_handler_callback(nm, P.on_cmd, "zz_probe_step_cmd_" .. tostring(i))
		end)
		if ok then
			P.cmd_handlers_ok = P.cmd_handlers_ok + 1
		else
			P.log("command listener FAILED for '" .. tostring(nm) .. "': " .. P.truncate(e, 100))
		end
	end
	P.log("command listeners registered: " .. tostring(P.cmd_handlers_ok) .. "/" .. tostring(#names)
		.. " documented event types")
end

local ok_reg, err_reg = pcall(function()
	bm:repeat_callback(P.tick, P.POLL_MS, P.NAME)
end)
if ok_reg then
	P.log("timer registered: " .. P.NAME .. " every " .. tostring(P.POLL_MS) .. " ms")
else
	P.log("timer registration FAILED: " .. P.truncate(err_reg, 160)
		.. " - use the console: zz_probe_step_status()")
end
