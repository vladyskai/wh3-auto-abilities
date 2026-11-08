--------------------------------------------------------------------------------
-- zz_probe_dist.lua - THROWAWAY PASSIVE OBSERVER PACK (separate from the main mod)
--
-- QUESTION THIS PROBE SETTLES: when Accusation (wh_main_hero_abilities_accusation)
-- is ARMED and its owner is NOT MOVING while an enemy approaches, AT WHAT
-- DISTANCE does the engine's own unit_in_range() start reporting the enemy as in
-- range, and which of the mod's two candidate range tests (unit_distance <= 52,
-- the 0.7 x 75 m expectation, or unit_distance <= 75, the full intercept reach)
-- passes FIRST as the enemy closes in?
--
-- THE USER'S EXPECTATION: the Accusation cast should fire at 0.7 x 75 = 52 m,
-- NOT at 75 m. This probe measures the crossing distances so the two logs (this
-- one and the main mod's own fire log) can be correlated tick-by-tick.
--
-- IMPORTANT - THIS PROBE IS AN OBSERVER, NOT AN ACTOR:
--   * It performs ZERO writes and ZERO casts. It never calls
--     perform_special_ability / perform_special_ability_ground, never selects,
--     never sets context, never resets a cooldown. The MAIN MOD does the
--     casting; its own log records the fire. The probe only measures.
--   * This is deliberate: the previous step-probe's accepted far-target casts
--     walked the caster 18-23 m. This probe must NOT provoke that, so it must
--     never cast. A write trip counter (P.trips) counts any forbidden
--     write-shaped call and MUST stay 0; every write-shaped member is
--     presence-only and is NEVER invoked.
--
-- WHAT THE PROBE LOGS, PER 2 s POLL:
--   (0) ONCE: which local unit was chosen as the Accusation owner (via the
--       friendly script-unit enumerator + the key), with its type and ui id.
--   (a) OBS tick=<n> dist=<d>m caster_pos=<x>,<y>
--           caster_moved_since_last=<m> caster_is_moving=<t/f> caster_is_idle=<t/f>
--       `dist` is the edge-to-edge distance to the NEAREST candidate (min over
--       the CAND lines), "-" when no candidate exists. `caster_moved_since_last`
--       is how the user's precondition "the Witch Hunter is NOT moving" is
--       verified: it is the metres the CASTER travelled between the previous
--       poll and this one (n/a on the first observation).
--   (b) For EVERY enemy candidate (up to 6 nearest):
--       CAND tick=<n> idx=<i> type=<...> dist=<d>m in_melee=<t/f> under_fire=<t/f>
--            engine_unit_in_range=<t/f> our_52_test=<t/f> our_75_test=<t/f>
--       `engine_unit_in_range` is the engine's own unit_in_range(enemy) helper;
--       `our_52_test` is unit_distance(enemy) <= 52; `our_75_test` is
--       unit_distance(enemy) <= 75. ALL THREE side by side at every distance is
--       the whole point: it shows which test first passes and at what distance.
--   (c) CAND-FIRST tick=<n> idx=<i> type=<...> dist=<d>m
--            first_passing_test=<52|75|engine> mode=first
--       logged ONCE, the first time any candidate passes ANY of the three tests,
--       carrying the EXACT crossing distance. `first_passing_test` names the
--       tightest of our tests that passed (52 if that passed, else 75), or
--       "engine" when only the engine's own unit_in_range() passed. The line
--       also carries the raw engine/52/75 flags so the reading is unambiguous.
--   (d) CANPERF tick=<n> key=<...> can=<t/f>  - can_perform_special_ability for
--       the owner + the key, logged every poll for corroboration (a script that
--       notes "the ability is no longer performable" helps align the two logs).
--
-- SAFETY / HYGIENE:
--   * Conflict-phase gate only, mirroring the main mod (bm:is_conflict_phase()),
--     logging the phase NAME and the boolean on every gate evaluation.
--   * Hard poll cap (P.MAX_POLLS = 90 -> 3 minutes at 2 s) so it cannot run
--     forever; the cap is logged when it bites.
--   * Every engine touch is pcall'd; no error can escape the poll.
--   * Ships as its OWN Movie pack (zz_probe_dist.pack) holding this ONE file.
--     The MAIN MOD is not in this pack and is never touched (byte-identical).
--
-- REMOVAL: delete zz_probe_dist.pack from the game's data/ folder (and the log
-- file zz_probe_dist_log.txt next to Warhammer3.exe). One pack, one file, one log.
--------------------------------------------------------------------------------

-- The probe's whole state lives in ONE chunk local (P) so the file adds a single
-- local to the main chunk and can never trip Lua's 200-local ceiling.
local P = {}

P.TAG       = "[zz_probe_dist] "
P.LOG_FILE  = "zz_probe_dist_log.txt"
P.POLL_MS   = 2000
P.MAX_POLLS = 90
P.MAX_CANDS = 6
P.NAME      = "zz_probe_dist_poll"

-- the ability whose owner is observed (the FIRST / only key we look for)
P.KEY = "wh_main_hero_abilities_accusation"

-- write-shaped member prefixes: a member whose name starts with one of these is
-- presence-only and is NEVER called, so no accidental write can occur. A guard
-- read that is mistakenly pointed at one of these increments the trip counter.
P.WRITE_PREFIX = {
	"set", "reset", "clear", "goto", "teleport", "turn", "cache", "kill", "heal",
	"reduce", "respawn", "select", "highlight", "mark", "deploy", "attack",
	"melee", "fire", "withdraw", "halt", "step", "increment", "decrement",
	"change", "occupy", "rotate", "interact", "besiege", "disable", "enable",
	"play", "trigger", "add", "remove", "apply", "force", "perform",
}

-- run state
P.polls_done  = 0
P.elapsed_ms  = 0
P.finished    = false
P.log_handle  = nil
P.logging_off = false

-- gate bookkeeping (one-time transition lines)
P.gate_wait_logged  = false
P.gate_enter_logged = false

-- owner bookkeeping (log ONCE which unit was chosen)
P.owner        = nil        -- { su, unit, uc, key }
P.owner_logged = false
P.wait_logged  = false

-- previous caster position (for caster_moved_since_last) and the CAND-FIRST latch
P.prev_x    = nil
P.prev_y    = nil
P.first_hit = false

-- forbidden-write trip counter (must stay 0)
P.trips = 0


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
			P.log_handle:write("\n======== zz_probe_dist session ========\n")
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

-- one-decimal number (or the value verbatim when it is not a number)
P.num = function(v)
	if type(v) ~= "number" then return tostring(v) end
	if v ~= v then return "nan" end
	return string.format("%.1f", v)
end

-- true/false rendering for a boolean answer, "-" for anything unreadable
P.tf = function(v)
	if v == true then return "t" end
	if v == false then return "f" end
	return "-"
end

-- One pcall'd read of a member, rendered as a short string; an error becomes
-- "<ERR: ...>". WRITE-SHAPED members are refused (trips++) and never invoked.
P.read_member = function(obj, name, fn)
	if obj == nil then return "<no obj>" end
	if P.is_write(name) then
		P.trips = P.trips + 1
		return "<REFUSED write-shaped " .. tostring(name) .. ">"
	end
	local ok, v = pcall(fn)
	if not ok then return "<ERR: " .. P.truncate(v, 50) .. ">" end
	if v == nil then return "nil" end
	if type(v) == "number" then return P.num(v) end
	if type(v) == "boolean" then return tostring(v) end
	local ok2, s = pcall(tostring, v)
	if ok2 and s ~= nil then return P.truncate(s, 40) end
	return "<opaque>"
end

P.is_write = function(name)
	local n = string.lower(tostring(name))
	for i = 1, #P.WRITE_PREFIX do
		local p = P.WRITE_PREFIX[i]
		if string.sub(n, 1, #p) == p then return true end
	end
	return false
end

-- pcall'd boolean read of a no-arg member: returns true / false / nil
P.bool_read = function(fn)
	local ok, v = pcall(fn)
	if ok and v == true then return true end
	if ok and v == false then return false end
	return nil
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

-- the owner's edge-to-edge distance to an enemy (the ENGINE print, in metres);
-- nil when the read cannot be taken.
P.gap = function(unit, enemy)
	local ok, d = pcall(function() return unit:unit_distance(enemy) end)
	if ok and type(d) == "number" then return d end
	return nil
end


-- ============================================================================
-- 3. OWNER + CANDIDATE HELPERS
-- ============================================================================

-- TRUE when the unit owns the observed ability key.
P.owns_key = function(unit)
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
	return set[P.KEY] == true
end

-- FRESH owner this instant: enumerate our army and return the FIRST
-- {su, unit, uc, key} whose unit owns P.KEY. Never hold a controller.
P.find_owner = function()
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
			if unit ~= nil and P.owns_key(unit) then
				return { su = su, unit = unit, uc = uc, key = P.KEY }
			end
		end
	end
	return nil
end

-- up to P.MAX_CANDS enemies, nearest first, each with its edge-to-edge distance.
-- An unreadable distance sorts last (kept, logged with dist="?").
P.read_candidates = function(owner_unit)
	local list = {}
	local ok, coll = pcall(function() return bm:get_scriptunits_for_main_enemy_army_to_local_player() end)
	if not ok or coll == nil then return list end
	local n = 0
	pcall(function() n = coll:count() end)
	if type(n) ~= "number" then return list end
	for i = 1, n do
		local ok2, su = pcall(function() return coll:item(i) end)
		if ok2 and su ~= nil then
			local unit
			pcall(function() unit = su.unit end)
			if unit ~= nil then
				local ui
				pcall(function() ui = unit:unique_ui_id() end)
				local d = P.gap(owner_unit, unit)
				list[#list + 1] = {
					unit = unit, ui_id = ui, dist = d,
					desc = P.read_member(unit, "type", function() return unit:type() end),
				}
			end
		end
	end
	-- nearest first; nils last
	table.sort(list, function(a, b)
		if a.dist == nil and b.dist == nil then return false end
		if a.dist == nil then return false end
		if b.dist == nil then return true end
		return a.dist < b.dist
	end)
	local capped = {}
	for i = 1, #list do
		if i > P.MAX_CANDS then break end
		capped[#capped + 1] = list[i]
	end
	return capped
end


-- ============================================================================
-- 4. ONE POLL  (conflict phase only; capped)
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

	-- the phase name + boolean are LOGGED on every poll (the gate is visible)
	P.log("")
	P.log("=== poll " .. tostring(P.polls_done) .. "/" .. tostring(P.MAX_POLLS)
		.. (reason and (" (" .. tostring(reason) .. ")") or "")
		.. " | phase=" .. tostring(phase_name)
		.. " | conflict=" .. tostring(conflict)
		.. " | t=" .. tostring(math.floor(P.elapsed_ms / 1000)) .. "s ===)")

	-- (0) find the owner once
	if P.owner == nil then
		P.owner = P.find_owner()
		if P.owner ~= nil and not P.owner_logged then
			P.owner_logged = true
			local _, otxt = P.read_pos(P.owner.unit)
			P.log("OWNER chosen: type=" .. P.read_member(P.owner.unit, "type", function() return P.owner.unit:type() end)
				.. " ui_id=" .. P.read_member(P.owner.unit, "unique_ui_id", function() return P.owner.unit:unique_ui_id() end)
				.. " pos=" .. otxt .. " key=" .. tostring(P.KEY)
				.. " (the FIRST local unit owning the observed ability)")
		elseif P.owner == nil and not P.wait_logged then
			P.wait_logged = true
			P.log("OWNER not found yet: no local unit owns '" .. tostring(P.KEY)
				.. "' - re-searching every poll. Arm Accusation (A badge) on the Witch Hunter.")
		end
	end
	if P.owner == nil then
		return
	end

	local unit = P.owner.unit
	local key = P.owner.key

	-- caster position + movement since the previous poll (the "NOT moving"
	-- precondition, verified directly)
	local _, ctxt, cx, cy = P.read_pos(unit)
	local moved = "n/a"
	if P.prev_x ~= nil then
		local m = P.dist2(P.prev_x, P.prev_y, cx, cy)
		if m ~= nil then moved = P.num(m) end
	end
	P.prev_x, P.prev_y = cx, cy

	local t_mov  = P.bool_read(function() return unit:is_moving() end)
	local t_idle = P.bool_read(function() return unit:is_idle() end)

	-- candidates (nearest first, up to P.MAX_CANDS)
	local cands = P.read_candidates(unit)
	local nearest = "-"
	if #cands > 0 and cands[1].dist ~= nil then nearest = P.num(cands[1].dist) end

	-- (a) OBS
	P.log("OBS tick=" .. tostring(P.polls_done)
		.. " dist=" .. nearest .. "m"
		.. " caster_pos=" .. ctxt
		.. " caster_moved_since_last=" .. moved .. "m"
		.. " caster_is_moving=" .. P.tf(t_mov)
		.. " caster_is_idle=" .. P.tf(t_idle))

	-- (b) CAND per candidate + (c) CAND-FIRST latch
	local first_here = nil
	for i = 1, #cands do
		local c = cands[i]
		local enemy = c.unit
		local d = c.dist

		local eng  = P.bool_read(function() return unit:unit_in_range(enemy) end)
		local t52  = (d ~= nil) and (d <= 52) or false
		local t75  = (d ~= nil) and (d <= 75) or false

		P.log("CAND tick=" .. tostring(P.polls_done)
			.. " idx=" .. tostring(i)
			.. " type=" .. c.desc
			.. " dist=" .. (d ~= nil and P.num(d) or "?") .. "m"
			.. " in_melee=" .. P.tf(P.bool_read(function() return enemy:is_in_melee() end))
			.. " under_fire=" .. P.tf(P.bool_read(function() return enemy:is_under_missile_attack() end))
			.. " engine_unit_in_range=" .. P.tf(eng)
			.. " our_52_test=" .. (t52 and "t" or "f")
			.. " our_75_test=" .. (t75 and "t" or "f"))

		if first_here == nil and (eng == true or t52 or t75) then
			first_here = { idx = i, c = c, d = d, eng = eng, t52 = t52, t75 = t75 }
		end
	end

	if first_here ~= nil and not P.first_hit then
		P.first_hit = true
		local fc = first_here
		local which = "engine"
		if fc.t52 then
			which = "52"
		elseif fc.t75 then
			which = "75"
		end
		P.log("CAND-FIRST tick=" .. tostring(P.polls_done)
			.. " idx=" .. tostring(fc.idx)
			.. " type=" .. fc.c.desc
			.. " dist=" .. (fc.d ~= nil and P.num(fc.d) or "?") .. "m"
			.. " first_passing_test=" .. which
			.. " mode=first"
			.. " engine_unit_in_range=" .. P.tf(fc.eng)
			.. " our_52_test=" .. (fc.t52 and "t" or "f")
			.. " our_75_test=" .. (fc.t75 and "t" or "f")
			.. " (the exact crossing distance)")
	end

	-- (d) CANPERF - corroboration each poll
	local can = P.bool_read(function() return unit:can_perform_special_ability(key) end)
	P.log("CANPERF tick=" .. tostring(P.polls_done)
		.. " key=" .. tostring(key)
		.. " can=" .. P.tf(can))

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
-- 5. CONSOLE HOOK + START UP
-- ============================================================================

function zz_probe_dist_status()
	pcall(P.run_poll, "console")
	local summary = "zz_probe_dist: polls=" .. tostring(P.polls_done) .. "/" .. tostring(P.MAX_POLLS)
		.. " owner=" .. (P.owner ~= nil and "found" or "NOT found")
		.. " first_hit=" .. tostring(P.first_hit)
		.. " trips=" .. tostring(P.trips) .. " log=" .. P.LOG_FILE
	P.log("STATUS (console): " .. summary)
	return summary
end

P.log("loaded from script/battle/mod/ (auto-load proof). Log file: " .. P.LOG_FILE
	.. " | PASSIVE DISTANCE OBSERVER for '" .. tostring(P.KEY) .. "': NO casts, NO writes."
	.. " Poll every " .. tostring(P.POLL_MS / 1000) .. "s, max " .. tostring(P.MAX_POLLS)
	.. " polls (" .. tostring(P.MAX_POLLS * P.POLL_MS / 1000) .. "s)."
	.. " Per poll: OBS (caster pos/moved/is_moving/is_idle) + up to " .. tostring(P.MAX_CANDS)
	.. " CAND lines (dist + in_melee + under_fire + engine unit_in_range + our 52 m"
	.. " and 75 m tests) + CAND-FIRST (the first crossing) + CANPERF."
	.. " | console: zz_probe_dist_status()")

local ok_reg, err_reg = pcall(function()
	bm:repeat_callback(P.tick, P.POLL_MS, P.NAME)
end)
if ok_reg then
	P.log("timer registered: " .. P.NAME .. " every " .. tostring(P.POLL_MS) .. " ms")
else
	P.log("timer registration FAILED: " .. P.truncate(err_reg, 160)
		.. " - use the console: zz_probe_dist_status()")
end
