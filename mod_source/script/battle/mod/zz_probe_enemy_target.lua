--------------------------------------------------------------------------------
-- zz_probe_enemy_target.lua - THROWAWAY PROBE PACK (separate from the main mod)
--
-- ROUND 4 - EXHAUSTIVE ROUTE SWEEP: WHICH CALL MAKES AN ENEMY-TARGETED ABILITY
--           LAND? (each candidate is its own LABELLED route with paired
--           caster/target effect-count deltas and a RESULT landed=yes|no)
--
-- WHAT ROUNDS 1-3 ESTABLISHED (live battles, do not re-establish)
--   * Enemy units ENUMERATE (`E count=<n>`) and read cleanly (type/men/hp/pos/id).
--   * `uc:perform_special_ability(key, enemy_battle_unit)` -> `accepted=true err=-`
--     every time, yet the TARGET's active-effect count NEVER moves and
--     `can_perform_special_ability` stays TRUE after the cast (no cooldown was
--     consumed): the call is accepted but INERT.
--   * Passing a `script_unit` or `nil` as the target is a Lua TYPE ERROR
--     ('bad argument #1 to perform_special_ability (battle_unit expected)').
--   * `perform_special_ability_ground(key, enemy_pos, 0, 0)` is likewise inert.
--   * The caster's OWN active-effect count (SELF line) never moves either.
--   * NO cooldown read exists on the unit or the controller (getter inventory:
--     every getter ABSENT; only the write-shaped reset_ability_cooldown exists).
--   * The user's MANUAL cast of the same ability on an enemy visibly works.
--
-- WHY THIS ROUND: the prior round concluded "not possible", but the documented
-- API forms were never all tried and the ENGINE/AI demonstrably casts hexes. So
-- every surviving candidate becomes its OWN route, and each is proven the same
-- way (a paired before/after active-effect count on BOTH the caster and the
-- target) so "landed" is a measurement, never an assertion.
--
-- THE SIX ROUTES (one cast each, >=15 s apart, conflict phase only)
--   R1 bench_fresh        - MIRROR THE VANILLA BENCHMARK EXACTLY: re-fetch the
--                           caster FRESH from bm:get_scriptunits_for_local_players_
--                           army() this instant (not a handle held from an earlier
--                           poll - a stale controller is a prime suspect), use ITS
--                           .uc/.unit, wrap the enemy battle_unit in a fresh
--                           script_unit:new(...) and pass ITS .unit as the target
--                           (the benchmark passes sunit_ogr_04.unit, a script_unit's
--                           unit). Action: perform_special_ability(key, tgt.unit).
--   R2 queued_q          - the QUEUED form, perform_special_ability_q(key, enemy).
--   R3 army_use          - the ARMY-LEVEL form, battle_army:use_special_ability(key,
--                           enemy_position, 0, 0) on the caster's own army.
--   R4 take_control      - the main mod's OWN PROVEN working shape: uc:take_control()
--                           -> perform_special_ability(key, enemy) -> release_control().
--   R5 attack_then_cast  - LEGITIMISATION BY ATTACK ORDER: uc:attack_unit(enemy,true,
--                           true) FIRST, then perform_special_ability(key, enemy).
--                           Accusation is ai_usage=hex_melee; maybe the engine only
--                           fires a melee-classed hex for a unit already ordered in.
--   R6 in_range_cast     - gated on the ability's OWN reach: only fire once
--                           unit:unit_in_range(enemy) / unit_distance<=75 / in melee,
--                           i.e. when the target is inside Accusation's 75 m
--                           intercept range (round 3 fired at long range). No write.
--
-- EACH ROUTE PROVES ITS OUTCOME THE SAME WAY (per cast):
--   TRY   route=<l> kind=<k> key=<key> target=<desc> can=<b> accepted=<b> err=<..>
--   ORDER route=<l> issued=<take_control|attack_unit> ok=<b> err=<..>   (R4/R5 only)
--   CANPOST route=<l> can_after=<b>   (false => the cast took the cooldown)
--   SELF  route=<l> before=<n> after=<n> delta=<n> state=".."
--   EFF   route=<l> key=.. target=.. before=<n> after=<n> delta=<n> effstate=hp=men=
--   RESULT route=<l> landed=<yes|no> self_delta=<n> target_delta=<n> can_after=<b>
--
-- THE COMMAND-EVENT INSTRUMENT: battle_manager:register_command_handler_callback
-- ("Special Ability", cb, name) fires whenever the player OR script issues an
-- ability command (battle.lua:135 - event:get_string1() = the ability name). Any
-- cast that is genuinely accepted by the engine should raise it; the user's MANUAL
-- cast will raise it too. `CMD event=SpecialAbility key=...` lines are ground truth.
--
-- THE EFFECT SIGNAL: a unit's active-effect COUNT, read through
--   common.get_context_value("CcoBattleUnit", <bare ui id>, "ActiveEffectList(true).Size")
--   (proven live: returns a number), plus "ActiveEffectState(true)".
--   Read for BOTH the target enemy AND the caster on every cast.
--
-- ZERO STATE WRITES beyond the ability casts and the two ORDER calls that ARE the
-- variable under test (R4 take_control, R5 attack_unit). NO forbidden write is
-- ever made: no reset_ability_cooldown, no select_in_ui, no SetContextObject, no
-- kill/heal/teleport. The forbidden-write trip counter must stay at 0.
--
-- SHIPPED AS its OWN Movie .pack (zz_probe_enemy_target.pack) holding this ONE
-- file under script/battle/mod/. The MAIN MOD is not in this pack and is never
-- touched. Own log: zz_probe_enemy_target_log.txt next to Warhammer3.exe, flushed
-- per line. Console hook: zz_probe_enemy_target_status().
--
-- REMOVAL: delete zz_probe_enemy_target.pack from the game's data/ folder (and the
-- log file). One pack, one file, one log. No trace in the main mod.
--------------------------------------------------------------------------------

-- The probe's whole state lives in ONE chunk local (P) so the file adds a single
-- local to the main chunk and can never trip Lua's 200-local ceiling.
local P = {}

P.TAG       = "[zz_probe_enemy_target] "
P.LOG_FILE  = "zz_probe_enemy_target_log.txt"
P.POLL_MS   = 2000
P.MAX_POLLS = 65
P.MAX_CASTS = 6
P.NAME      = "zz_probe_enemy_target_poll"

-- a key is cast at most once per this window (routes are spaced by it too)
P.CAST_COOLDOWN_MS = 15000

-- how many polls to keep re-reading the caster's + target's effect count while
-- the deltas are still zero (a slow effect). One SELF/EFF line pair per poll.
P.EFFECT_SETTLE_POLLS = 3

-- Accusation's own reach, from unit_spec_abil.tsv (target_intercept_range = 75).
P.ABILITY_INTERCEPT_M = 75

-- Known ENEMY-targeted ability keys (from the project audit). kind:
--   "unit"   -> the engine wants an enemy battle_unit  (perform_special_ability)
--   "ground" -> the engine wants an enemy-ground point (perform_special_ability_ground)
P.ENEMY_KEYS = {
	["wh_main_hero_abilities_accusation"]             = "unit",
	["wh2_main_character_abilities_assassins_trophy"] = "unit",
	["wh3_dlc29_hero_active_amulet_of_pha_stah"]      = "unit",
	["wh2_dlc09_item_abilities_amulet_of_phastah"]    = "ground",
	["wh2_dlc09_character_abilities_curse_of_djaf"]   = "ground",
	["wh3_main_spell_tempest_hailstorm"]              = "ground",
}

-- deterministic scan order (pairs() over a string-keyed table is not stable)
P.KEY_ORDER = {
	"wh_main_hero_abilities_accusation",
	"wh2_main_character_abilities_assassins_trophy",
	"wh3_dlc29_hero_active_amulet_of_pha_stah",
	"wh2_dlc09_item_abilities_amulet_of_phastah",
	"wh2_dlc09_character_abilities_curse_of_djaf",
	"wh3_main_spell_tempest_hailstorm",
}

-- THE ROUTE TABLE. Each entry is ONE cast: a distinct call SHAPE and a varying
-- enemy. `at_ms` is the earliest elapsed conflict time; the driver ALSO enforces
-- P.CAST_COOLDOWN_MS since the previous cast, so spacing can only grow.
--   kind: how the cast is made (see the header).
--   pick: 1-based enemy index from the poll's enemy list (nil kind-independent).
--   defer_ms: (in_range routes) how long past at_ms to keep waiting for the target
--             to enter the ability's own range before firing anyway (labelled).
P.ROUTES = {
	{ label = "bench_fresh",      kind = "unit",       pick = 1, at_ms = 0,     defer_ms = 0,     why = "vanilla-benchmark mirror: fresh caster .uc/.unit + fresh script_unit:new(enemy).unit" },
	{ label = "queued_q",         kind = "q",          pick = 2, at_ms = 15000, defer_ms = 0,     why = "perform_special_ability_q(key, enemy_battle_unit)" },
	{ label = "army_use",         kind = "army",       pick = 3, at_ms = 30000, defer_ms = 0,     why = "battle_army:use_special_ability(key, enemy_pos, 0, 0)" },
	{ label = "take_control",     kind = "takecast",   pick = 1, at_ms = 45000, defer_ms = 0,     why = "the main mod's working shape: take_control -> cast -> release_control" },
	{ label = "attack_then_cast", kind = "attackcast", pick = 2, at_ms = 60000, defer_ms = 0,     why = "legitimise: uc:attack_unit(enemy) THEN perform_special_ability(key, enemy)" },
	{ label = "in_range_cast",    kind = "incast",     pick = 3, at_ms = 75000, defer_ms = 40000, why = "fire only while the enemy is inside the ability's own intercept range" },
}

-- COOLDOWN accessor inventory (kept from round 3: the "no cooldown read exists"
-- evidence). Getter-shaped names are CALLED (pcall'd); write-shaped names are
-- reported presence-only and NEVER called.
P.COOLDOWN_READ_UNIT = {
	"active_abilities", "ability_active", "is_ability_active", "has_ability_active",
	"active_special_abilities", "passive_special_abilities",
	"ability_cooldown", "special_ability_cooldown", "get_ability_cooldown",
	"cooldown_remaining", "ability_cooldown_remaining",
	"ability_charges", "ability_uses_remaining", "special_ability_charges",
}
P.COOLDOWN_READ_CTRL = {
	"ability_cooldown", "special_ability_cooldown", "get_ability_cooldown",
	"cooldown_remaining", "ability_charges", "ability_uses_remaining",
}
P.COOLDOWN_WRITE_LIST = { "reset_ability_cooldown" }
P.COOLDOWN_WRITE = { ["reset_ability_cooldown"] = true }

P.polls_done   = 0
P.elapsed_ms   = 0
P.casts_done   = 0
P.route_index  = 1
P.last_cast_ms = -1
P.fp_logged    = false
P.finished     = false
P.log_handle   = nil
P.logging_off  = false

-- order bookkeeping (R4/R5): labelled, counted, always logged. These are NOT the
-- forbidden write family - they are the legitimate orders the route is testing.
P.orders_issued = 0

-- forbidden-write trip counter (must stay 0)
P.trips = 0

-- gate bookkeeping (one-time transition lines)
P.gate_wait_logged  = false
P.gate_enter_logged = false

-- the pending paired follow-up (set by a cast, read at the next poll)
P.pending = nil
P.cooldown_probed = false

-- command-event counter (the engine's own "an ability command was issued" event)
P.cmd_events = 0
P.cmd_listener_ok = false


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
			P.log_handle:write("\n======== zz_probe_enemy_target session ========\n")
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

local lua_type = type

local function truncate(s, n)
	s = tostring(s)
	if #s > n then return string.sub(s, 1, n) .. "..." end
	return s
end

local function num(v)
	if lua_type(v) ~= "number" then return tostring(v) end
	if v ~= v then return "nan" end
	if v == math.floor(v) and math.abs(v) < 1e15 then return tostring(math.floor(v)) end
	return string.format("%.1f", v)
end

local function num_or_nil(v)
	if v == nil then return "nil" end
	if lua_type(v) ~= "number" then return tostring(v) end
	return num(v)
end

-- One pcall'd read, rendered as a short string; an error becomes "<ERR: ...>".
local function read1(fn)
	local ok, v = pcall(fn)
	if not ok then return "<ERR: " .. truncate(v, 50) .. ">" end
	if v == nil then return "nil" end
	if lua_type(v) == "number" then return num(v) end
	if lua_type(v) == "boolean" then return tostring(v) end
	local ok2, s = pcall(tostring, v)
	if ok2 and s ~= nil then return truncate(s, 40) end
	return "<opaque>"
end

local function read_position(unit)
	local ok, v = pcall(function() return unit:position() end)
	if not ok or v == nil then
		return nil, "<ERR: " .. truncate(ok and "nil" or v, 50) .. ">"
	end
	local x, y
	local okx, vx = pcall(function() return v:get_x() end)
	if okx and lua_type(vx) == "number" then x = vx end
	local oky, vy = pcall(function() return v:get_y() end)
	if oky and lua_type(vy) == "number" then y = vy end
	if x ~= nil and y ~= nil then
		return v, string.format("%.1f,%.1f", x, y)
	end
	return v, "<vec>"
end

-- ONE common.get_context_value read, pcall'd. Returns (value, err_or_nil).
P.gcv = function(obj_type, obj_id, field)
	local ok, v = pcall(function() return common.get_context_value(obj_type, obj_id, field) end)
	if not ok then return nil, v end
	return v, nil
end


-- ============================================================================
-- 3. ENEMY COLLECTION COUNTS
-- ============================================================================

P.log_enemy_count = function()
	local ok, coll = pcall(function()
		return bm:get_scriptunits_for_main_enemy_army_to_local_player()
	end)
	if not ok then
		P.log("E count=<ERR: " .. truncate(coll, 70) .. ">")
		return nil
	end
	if coll == nil then
		P.log("E count=<nil collection>")
		return nil
	end
	local okc, cnt = pcall(function() return coll:count() end)
	if not okc then
		P.log("E count=<ERR count(): " .. truncate(cnt, 70) .. ">")
		return coll
	end
	P.log("E count=" .. num(cnt))
	return coll
end

P.log_fp_count = function()
	local ok, army = pcall(function() return bm:get_first_non_player_army() end)
	if not ok then P.log("E fp count=<ERR army: " .. truncate(army, 70) .. ">"); return end
	if army == nil then P.log("E fp count=<nil army>"); return end
	local ok2, units = pcall(function() return army:units() end)
	if not ok2 then P.log("E fp count=<ERR units(): " .. truncate(units, 70) .. ">"); return end
	if units == nil then P.log("E fp count=<nil units>"); return end
	local ok3, cnt = pcall(function() return units:count() end)
	if not ok3 then P.log("E fp count=<ERR count(): " .. truncate(cnt, 70) .. ">"); return end
	P.log("E fp count=" .. num(cnt) .. " (get_first_non_player_army():units())")
end


-- ============================================================================
-- 4. THE EFFECT SIGNAL  (read the active-effect count + health of a unit)
-- ============================================================================

P.read_effect_block = function(unit, ui_id)
	local b = {
		id = ui_id, count = nil, state = nil,
		health = nil, men = nil, signal = "none", note = "",
	}
	if unit ~= nil then
		local okh, hv = pcall(function() return unit:unary_hitpoints() end)
		if okh and lua_type(hv) == "number" then b.health = hv end
		local okm, mv = pcall(function() return unit:number_of_men_alive() end)
		if okm and lua_type(mv) == "number" then b.men = mv end
	end
	if ui_id ~= nil then
		local raw, err = P.gcv("CcoBattleUnit", tostring(ui_id), "ActiveEffectList(true).Size")
		if raw ~= nil then
			local n = tonumber(raw)
			if n ~= nil then
				b.count = n
				b.signal = "effect_count"
			else
				b.note = "effect count field returned a non-number (" .. truncate(tostring(raw), 30) .. ")"
			end
		else
			b.note = "effect count read ERR: " .. truncate(tostring(err), 60)
		end
		local st = P.gcv("CcoBattleUnit", tostring(ui_id), "ActiveEffectState(true)")
		if st ~= nil then b.state = tostring(st) end
	end
	if b.signal == "none" then
		if b.health ~= nil or b.men ~= nil then b.signal = "health" end
	end
	return b
end


-- ============================================================================
-- 5. READ UP TO 3 ENEMY UNITS  (each entry keeps BOTH handles so a route can
--    hand the engine a battle_unit, a script_unit, or a position)
-- ============================================================================

P.read_enemy_units = function(coll)
	if coll == nil then return {} end
	local n = 0
	pcall(function() n = coll:count() end)
	if lua_type(n) ~= "number" then return {} end
	local cap = n
	if cap > 3 then cap = 3 end
	local list = {}
	for i = 1, cap do
		local ok, su = pcall(function() return coll:item(i) end)
		if ok and su ~= nil then
			local unit = nil
			pcall(function() unit = su.unit end)
			if unit ~= nil then
				local ui_id = nil
				pcall(function() ui_id = unit:unique_ui_id() end)
				local pos, pos_txt = read_position(unit)
				local desc = read1(function() return unit:type() end)
				list[#list + 1] = { su = su, unit = unit, ui_id = ui_id, desc = desc, pos = pos }
				P.log("E" .. i
					.. " type=" .. desc
					.. " men=" .. read1(function() return unit:number_of_men_alive() end)
					.. " hp=" .. read1(function() return unit:unary_hitpoints() end)
					.. " in_melee=" .. read1(function() return unit:is_in_melee() end)
					.. " valid=" .. read1(function() return unit:is_valid_target() end)
					.. " id=" .. (ui_id ~= nil and tostring(ui_id) or "nil")
					.. " pos=" .. pos_txt)
			else
				P.log("E" .. i .. " <no battle_unit on the script_unit>")
			end
		else
			P.log("E" .. i .. " <ERR item(" .. i .. "): " .. truncate(ok and "nil" or su, 50) .. ">")
		end
	end
	return list
end

P.find_in_list = function(list, ui_id)
	if ui_id == nil or list == nil then return nil end
	for i = 1, #list do
		if list[i].ui_id ~= nil and tostring(list[i].ui_id) == tostring(ui_id) then
			return list[i].unit
		end
	end
	return nil
end


-- ============================================================================
-- 6. OUR UNITS  (fresh fetch + which own an enemy key)
-- ============================================================================

P.owned_keys_set = function(unit)
	local set = {}
	local function absorb(ok, owned)
		if ok and lua_type(owned) == "table" then
			for _, v in pairs(owned) do
				if lua_type(v) == "string" then set[v] = true end
			end
		end
	end
	absorb(pcall(function() return unit:owned_special_abilities() end))
	absorb(pcall(function() return unit:owned_non_passive_special_abilities() end))
	return set
end

P.first_enemy_key = function(unit)
	local set = P.owned_keys_set(unit)
	for i = 1, #P.KEY_ORDER do
		local k = P.KEY_ORDER[i]
		if set[k] then return k, P.ENEMY_KEYS[k] end
	end
	return nil, nil
end

-- FRESH caster this instant: enumerate our army NOW and return the first
-- {su, unit, uc, key, kind} whose unit owns a listed enemy key. This is the
-- round-4 core: never hold a controller across polls.
P.fresh_caster = function()
	local ok, coll = pcall(function() return bm:get_scriptunits_for_local_players_army() end)
	if not ok or coll == nil then return nil end
	local n = 0
	pcall(function() n = coll:count() end)
	if lua_type(n) ~= "number" then return nil end
	for i = 1, n do
		local ok2, su = pcall(function() return coll:item(i) end)
		if ok2 and su ~= nil then
			local unit, uc
			pcall(function() unit = su.unit end)
			pcall(function() uc = su.uc end)
			if unit ~= nil then
				local k, kind = P.first_enemy_key(unit)
				if k ~= nil then
					return { su = su, unit = unit, uc = uc, key = k, kind = kind }
				end
			end
		end
	end
	return nil
end


-- ============================================================================
-- 7. THE ABILITY'S OWN REACH (for R6). No write - a pure read.
-- ============================================================================

P.in_ability_range = function(caster_unit, enemy_unit)
	local okr, inr = pcall(function() return caster_unit:unit_in_range(enemy_unit) end)
	if okr and inr == true then return true, "unit_in_range" end
	local okd, d = pcall(function() return caster_unit:unit_distance(enemy_unit) end)
	if okd and lua_type(d) == "number" and d <= P.ABILITY_INTERCEPT_M then
		return true, "dist=" .. num(d) .. "<=" .. tostring(P.ABILITY_INTERCEPT_M)
	end
	local okm, m = pcall(function() return caster_unit:is_in_melee() end)
	if okm and m == true then return true, "in_melee" end
	if okd and lua_type(d) == "number" then return false, "dist=" .. num(d) end
	return false, "range_unreadable"
end


-- ============================================================================
-- 8. ONE CAST (one route): TRY + ORDER + CANPOST, then the paired follow-up
-- ============================================================================

P.perform_cast = function(route, caster, enemy_entry)
	local unit = caster.unit
	local uc   = caster.uc
	local key  = caster.key
	local kind = route.kind
	local label = route.label

	-- caster self id + the "before" self effect read
	local self_ui = nil
	pcall(function() self_ui = unit:unique_ui_id() end)
	local self_pre = P.read_effect_block(unit, self_ui)

	local can = "?"
	local okc, cv = pcall(function() return unit:can_perform_special_ability(key) end)
	if okc then can = tostring(cv == true) end

	-- target descriptor + the "before" target effect read
	local tgt_desc = "none"
	local tgt_ui, tgt_unit, tgt_pos, pre = nil, nil, nil, nil
	if enemy_entry ~= nil then
		tgt_desc = enemy_entry.desc
		tgt_ui   = enemy_entry.ui_id
		tgt_unit = enemy_entry.unit
		tgt_pos  = enemy_entry.pos
		pre = P.read_effect_block(tgt_unit, tgt_ui)
	end
	local pre_txt = (pre ~= nil and pre.count ~= nil) and tostring(pre.count) or "nil"
	local sig_txt = (pre ~= nil) and pre.signal or "none"
	local self_pre_txt = (self_pre ~= nil and self_pre.count ~= nil) and tostring(self_pre.count) or "nil"

	local accepted = false
	local err = ""

	-- one labelled ORDER, when the route is a legitimisation route
	local function issue_order(what, fn)
		local ok_o, e_o = pcall(fn)
		P.orders_issued = P.orders_issued + 1
		P.log("ORDER route=" .. label .. " issued=" .. what
			.. " ok=" .. tostring(ok_o == true)
			.. (ok_o and "" or (" err=" .. truncate(tostring(e_o), 90))))
		return ok_o == true
	end

	-- ---- the cast itself (the route's distinct call shape) ----
	if uc == nil and kind ~= "army" then
		err = "<no controller on the fresh script_unit>"
	elseif tgt_unit == nil then
		err = "<no enemy target>"
	elseif kind == "unit" then
		-- R1: the vanilla-benchmark mirror. Fresh caster .uc + a fresh
		-- script_unit wrapper around the enemy battle_unit; pass ITS .unit.
		local tgt = tgt_unit
		pcall(function()
			local wrap = script_unit:new(tgt_unit, "zz_probe_et_enemy")
			if wrap ~= nil then
				local wu
				local okw = pcall(function() wu = wrap.unit end)
				if okw and wu ~= nil then tgt = wu end
			end
		end)
		accepted, err = pcall(function() return uc:perform_special_ability(key, tgt) end)
	elseif kind == "q" then
		accepted, err = pcall(function() return uc:perform_special_ability_q(key, tgt_unit) end)
	elseif kind == "army" then
		local ok_army, army = pcall(function() return unit:army() end)
		if not ok_army or army == nil or tgt_pos == nil then
			err = "<no army or no enemy position for the army-targeted form>"
		else
			accepted, err = pcall(function() return army:use_special_ability(key, tgt_pos, 0, 0) end)
		end
	elseif kind == "takecast" then
		-- R4: the main mod's own working shape.
		issue_order("take_control", function() uc:take_control() end)
		accepted, err = pcall(function() return uc:perform_special_ability(key, tgt_unit) end)
		issue_order("release_control", function() uc:release_control() end)
	elseif kind == "attackcast" then
		-- R5: legitimise with an attack order first.
		issue_order("attack_unit", function() uc:attack_unit(tgt_unit, true, true) end)
		accepted, err = pcall(function() return uc:perform_special_ability(key, tgt_unit) end)
	elseif kind == "incast" then
		-- R6: fire at the enemy while it is inside the ability's own reach.
		accepted, err = pcall(function() return uc:perform_special_ability(key, tgt_unit) end)
	else
		err = "<unknown route kind>"
	end

	if accepted ~= true then accepted = false end
	local err_txt = (err ~= true and err ~= false and err ~= nil and err ~= "") and tostring(err) or ""
	if accepted then err_txt = "" end

	P.log("TRY route=" .. label .. " kind=" .. kind .. " key=" .. tostring(key)
		.. " target=" .. tgt_desc
		.. " can=" .. can .. " accepted=" .. tostring(accepted)
		.. " err=" .. (accepted and "-" or truncate(err_txt, 110)))

	-- CANPOST: can_perform_special_ability read IMMEDIATELY after the cast.
	-- FALSE right after an accepted cast => the cast consumed the cooldown.
	local can_after = "?"
	local okc2, cv2 = pcall(function() return unit:can_perform_special_ability(key) end)
	if okc2 then can_after = tostring(cv2 == true) end
	P.log("CANPOST route=" .. label .. " can_after=" .. can_after
		.. " (false => the cast took the cooldown)")

	P.casts_done = P.casts_done + 1
	P.last_cast_ms = P.elapsed_ms

	-- queue the paired follow-up (SELF + EFF + RESULT) for the next polls
	P.pending = {
		route = label, kind = kind, key = key, target_desc = tgt_desc,
		self_unit = unit, self_ui = self_ui,
		pre_self_eff = (self_pre ~= nil and self_pre.count),
		target_unit = tgt_unit, target_ui = tgt_ui,
		pre_eff = (pre ~= nil and pre.count),
		pre_hp  = (pre ~= nil and pre.health),
		pre_men = (pre ~= nil and pre.men),
		post_can = can_after,
		settle = P.EFFECT_SETTLE_POLLS,
	}

	P.log("CAST route=" .. label .. " " .. tostring(P.casts_done) .. "/" .. tostring(P.MAX_CASTS)
		.. " key=" .. tostring(key) .. " kind=" .. kind
		.. " target=" .. tgt_desc .. " self_pre_eff=" .. self_pre_txt
		.. " tgt_pre_eff=" .. pre_txt .. " signal=" .. sig_txt
		.. " (>= " .. tostring(P.CAST_COOLDOWN_MS / 1000) .. "s to the next cast)"
		.. " | why: " .. route.why)
end


-- ============================================================================
-- 9. THE PAIRED FOLLOW-UP  (SELF + EFF + RESULT, one pair per poll while settling)
-- ============================================================================

P.settle_effects = function(enemy_list)
	local p = P.pending
	if p == nil then return end

	-- ---- SELF (the caster) ----
	local sb = P.read_effect_block(p.self_unit, p.self_ui)
	local s_after = sb.count
	local s_delta = "-"
	if p.pre_self_eff ~= nil and s_after ~= nil then s_delta = tostring(s_after - p.pre_self_eff) end
	P.log("SELF route=" .. p.route
		.. " before=" .. (p.pre_self_eff ~= nil and tostring(p.pre_self_eff) or "nil")
		.. " after=" .. (s_after ~= nil and tostring(s_after) or "nil")
		.. " delta=" .. s_delta
		.. " state=\"" .. (sb.state ~= nil and truncate(sb.state, 24) or "") .. "\""
		.. (sb.note ~= "" and (" note=\"" .. sb.note .. "\"") or ""))

	-- ---- TARGET (the enemy) ----
	local delta = "-"
	local after = nil
	if p.target_ui ~= nil then
		local tu = P.find_in_list(enemy_list, p.target_ui) or p.target_unit
		local tb = P.read_effect_block(tu, p.target_ui)
		after = tb.count
		if p.pre_eff ~= nil and after ~= nil then delta = tostring(after - p.pre_eff) end
		P.log("EFF route=" .. p.route
			.. " key=" .. tostring(p.key) .. " target=" .. p.target_desc
			.. " signal=" .. tb.signal
			.. " before=" .. (p.pre_eff ~= nil and tostring(p.pre_eff) or "nil")
			.. " after=" .. (after ~= nil and tostring(after) or "nil")
			.. " delta=" .. delta
			.. " effstate=" .. (tb.state ~= nil and ("\"" .. truncate(tb.state, 24) .. "\"") or "nil")
			.. " hp=" .. num_or_nil(p.pre_hp) .. "->" .. num_or_nil(tb.health)
			.. " men=" .. num_or_nil(p.pre_men) .. "->" .. num_or_nil(tb.men)
			.. (tb.note ~= "" and (" note=\"" .. tb.note .. "\"") or ""))
	else
		P.log("EFF route=" .. p.route .. " key=" .. tostring(p.key)
			.. " target=none (no enemy target for this route)")
	end

	-- ---- verdict ----
	local self_moved = (s_delta ~= "-" and s_delta ~= "0")
	local tgt_moved  = (delta ~= "-" and delta ~= "0")
	if self_moved or tgt_moved then
		local landed = (tgt_moved and "yes" or "no")
		P.log("RESULT route=" .. p.route .. " landed=" .. landed
			.. " self_delta=" .. s_delta .. " target_delta=" .. delta
			.. " can_after=" .. tostring(p.post_can)
			.. (tgt_moved and "  <- the ENEMY-targeted effect LANDED" or "")
			.. (self_moved and "  <- the CASTER's effect count moved (self-application)" or ""))
		P.pending = nil
		return
	end

	p.settle = p.settle - 1
	if p.settle <= 0 then
		P.log("RESULT route=" .. p.route .. " landed=no"
			.. " self_delta=" .. s_delta .. " target_delta=" .. delta
			.. " can_after=" .. tostring(p.post_can)
			.. " (no effect-count change within " .. tostring(P.EFFECT_SETTLE_POLLS)
			.. " poll(s) - accepted-but-inert OR cooldown-refused)")
		P.pending = nil
	end
end


-- ============================================================================
-- 10. THE COOLDOWN ACCESSOR INVENTORY  (kept from round 3, once, read-only)
-- ============================================================================

P.probe_cooldown = function(caster)
	if P.cooldown_probed then return end
	if caster == nil or caster.key == nil then return end
	P.cooldown_probed = true
	local key = caster.key
	P.log("COOLDOWN probe: key=" .. tostring(key)
		.. " (accessor inventory; getter-shaped members are CALLED, write-shaped are presence-only, all pcall'd)")

	local function one(handle_name, handle, name)
		if handle == nil then return end
		local ok_get, m = pcall(function() return handle[name] end)
		if not ok_get then
			P.log("COOLDOWN " .. handle_name .. "." .. name .. " => member read raised: " .. truncate(m, 60))
			return
		end
		if m == nil then
			P.log("COOLDOWN " .. handle_name .. "." .. name .. " => ABSENT")
			return
		end
		if lua_type(m) ~= "function" then
			P.log("COOLDOWN " .. handle_name .. "." .. name
				.. " => value (" .. lua_type(m) .. ")=" .. read1(function() return m end))
			return
		end
		local is_write = P.COOLDOWN_WRITE[name] == true
		if not is_write then
			local head = string.sub(name, 1, 3)
			if head == "set" or string.sub(name, 1, 5) == "reset" or string.sub(name, 1, 5) == "clear" then
				is_write = true
			end
		end
		if is_write then
			P.log("COOLDOWN " .. handle_name .. "." .. name
				.. " => EXISTS (function) - NOT CALLED (write-shaped)")
			return
		end
		local ok2, v = pcall(m, handle, key)
		if not ok2 then
			local ok3, v3 = pcall(m, handle)
			if ok3 then ok2, v = true, v3 end
		end
		if ok2 then
			P.log("COOLDOWN " .. handle_name .. "." .. name .. " => value=" .. read1(function() return v end))
		else
			P.log("COOLDOWN " .. handle_name .. "." .. name .. " => EXISTS-BUT-ERRORS err=" .. truncate(v, 80))
		end
	end

	for i = 1, #P.COOLDOWN_READ_UNIT do one("unit", caster.unit, P.COOLDOWN_READ_UNIT[i]) end
	for i = 1, #P.COOLDOWN_READ_CTRL do one("uc",   caster.uc,   P.COOLDOWN_READ_CTRL[i]) end
	for i = 1, #P.COOLDOWN_WRITE_LIST do one("uc", caster.uc, P.COOLDOWN_WRITE_LIST[i]) end

	P.log("COOLDOWN probe done: '=> value=' is a LIVE cooldown/readiness accessor;"
		.. " '=> ABSENT' on every getter means NO cooldown READ exists")
end


-- ============================================================================
-- 11. ONE POLL (conflict phase only; capped)
-- ============================================================================

P.run_poll = function(reason)
	if P.finished then return end
	if P.polls_done >= P.MAX_POLLS then
		P.finished = true
		P.log("probe finished (cap)")
		return
	end

	-- THE GATE - mirrors the main mod exactly: act only in the conflict phase.
	local ok_phase, conflict = pcall(function() return bm:is_conflict_phase() end)
	local phase_name = "?"
	pcall(function() phase_name = bm:get_current_phase_name() end)

	if not ok_phase or conflict ~= true then
		if not P.gate_wait_logged then
			P.gate_wait_logged = true
			local ctxt
			if not ok_phase then
				ctxt = "<ERR: " .. truncate(conflict, 60) .. ">"
			else
				ctxt = tostring(conflict)
			end
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
		.. " | casts=" .. tostring(P.casts_done) .. "/" .. tostring(P.MAX_CASTS)
		.. " | route=" .. tostring(P.route_index) .. "/" .. tostring(#P.ROUTES) .. " ===")

	-- (1) enemy collection counts
	local coll = P.log_enemy_count()
	if not P.fp_logged then
		P.fp_logged = true
		pcall(P.log_fp_count)
	end

	-- (2) enemy unit reads (up to 3); routes pick from this list
	local enemy_list = P.read_enemy_units(coll)

	-- (2b) the paired follow-up for the PREVIOUS cast (SELF + EFF + RESULT)
	pcall(P.settle_effects, enemy_list)

	-- (3) FRESH caster this poll (also drives the M read)
	local caster = P.fresh_caster()
	if caster == nil then
		P.log("M none: no local unit owns a listed enemy-targeted key (fresh fetch)")
	else
		local tgt, tgt_desc, dist = nil, "none", "-"
		pcall(function() tgt = caster.unit:current_target() end)
		if tgt ~= nil then
			tgt_desc = read1(function() return tgt:type() end)
			local okd, d = pcall(function() return caster.unit:unit_distance(tgt) end)
			if okd and lua_type(d) == "number" then dist = num(d) end
		end
		P.log("M fresh key=" .. tostring(caster.key)
			.. " valid=" .. read1(function() return caster.unit:is_valid_target() end)
			.. " current_target=" .. tgt_desc .. " dist=" .. dist)
	end

	-- (4) the once-per-session cooldown inventory (read-only)
	if caster ~= nil then pcall(P.probe_cooldown, caster) end

	-- (5) THE ROUTE DRIVER: one cast per route, >= CAST_COOLDOWN_MS apart
	if P.route_index > #P.ROUTES then
		P.log("ROUTES complete: " .. tostring(P.casts_done) .. " cast(s) attempted over "
			.. tostring(#P.ROUTES) .. " route(s)")
	elseif P.pending ~= nil then
		P.log("ROUTES holding (previous cast still settling)")
	elseif caster == nil then
		P.log("ROUTES waiting: no armed caster")
	else
		local r = P.ROUTES[P.route_index]
		local spaced = (P.last_cast_ms < 0) or (P.elapsed_ms - P.last_cast_ms >= P.CAST_COOLDOWN_MS)
		if P.casts_done >= P.MAX_CASTS then
			P.log("ROUTES capped (" .. tostring(P.MAX_CASTS) .. " casts)")
			P.route_index = #P.ROUTES + 1
		elseif P.elapsed_ms < r.at_ms then
			P.log("ROUTES waiting " .. tostring(math.ceil((r.at_ms - P.elapsed_ms) / 1000))
				.. "s for route=" .. r.label .. " (kind=" .. r.kind .. ")")
		elseif not spaced then
			P.log("ROUTES spacing: " .. tostring(math.ceil((P.CAST_COOLDOWN_MS - (P.elapsed_ms - P.last_cast_ms)) / 1000))
				.. "s until route=" .. r.label .. " (>= " .. tostring(P.CAST_COOLDOWN_MS / 1000) .. "s between casts)")
		else
			-- pick the enemy for this route
			local entry = nil
			if #enemy_list > 0 then
				local pick = r.pick
				if pick > #enemy_list then pick = #enemy_list end
				entry = enemy_list[pick]
			end

			-- R6: only fire inside the ability's own reach (defer up to defer_ms)
			local fire = true
			local range_note = ""
			if r.kind == "incast" and entry ~= nil then
				local inr, how = P.in_ability_range(caster.unit, entry.unit)
				if inr then
					range_note = " in_range=yes(" .. how .. ")"
				elseif P.elapsed_ms < r.at_ms + r.defer_ms then
					fire = false
					P.log("ROUTES route=" .. r.label .. " deferring: enemy out of the ability's reach ("
						.. how .. ") - waiting up to "
						.. tostring(math.ceil((r.at_ms + r.defer_ms - P.elapsed_ms) / 1000)) .. "s")
				else
					range_note = " in_range=NO(" .. how .. ", deadline passed)"
				end
			end

			if not fire then
				-- defer: leave route_index alone; next poll re-checks
			elseif entry == nil then
				P.log("ROUTES SKIP route=" .. r.label .. " (no enemy unit available to target)")
				P.route_index = P.route_index + 1
			else
				if range_note ~= "" then
					P.log("ROUTES route=" .. r.label .. range_note)
				end
				pcall(P.perform_cast, r, caster, entry)
				P.route_index = P.route_index + 1
			end
		end
	end

	if P.polls_done >= P.MAX_POLLS then
		P.finished = true
		P.log("probe finished (cap)")
	end
end

P.tick = function()
	local ok, err = pcall(P.run_poll, nil)
	if not ok then
		P.log("POLL ERROR (swallowed - engine callbacks stay alive): " .. truncate(err, 160))
	end
end


-- ============================================================================
-- 12. THE COMMAND-EVENT INSTRUMENT  (ground truth: did the ENGINE register an
--     ability command?)  battle.lua:135 - "Special Ability" command event.
-- ============================================================================

P.on_special_ability_cmd = function(ctx)
	P.cmd_events = P.cmd_events + 1
	local nm = "?"
	pcall(function() nm = ctx:get_string1() end)
	P.log("CMD event=SpecialAbility key=" .. tostring(nm)
		.. " (the engine issued an ability command - script OR player)")
end


-- ============================================================================
-- 13. CONSOLE HOOK  +  START UP
-- ============================================================================

function zz_probe_enemy_target_status()
	pcall(P.run_poll, "console")
	local summary = "zz_probe_enemy_target: polls=" .. tostring(P.polls_done) .. "/"
		.. tostring(P.MAX_POLLS) .. " casts=" .. tostring(P.casts_done) .. "/"
		.. tostring(P.MAX_CASTS) .. " route=" .. tostring(P.route_index) .. "/"
		.. tostring(#P.ROUTES) .. " orders=" .. tostring(P.orders_issued)
		.. " cmds=" .. tostring(P.cmd_events) .. " trips=" .. tostring(P.trips)
		.. " log=" .. P.LOG_FILE
	P.log("STATUS (console): " .. summary)
	return summary
end

P.log("loaded from script/battle/mod/ (auto-load proof). Log file: " .. P.LOG_FILE
	.. " | ENEMY-TARGET ROUND 4: 6-route sweep (bench_fresh, queued_q, army_use,"
	.. " take_control, attack_then_cast, in_range_cast), >= "
	.. tostring(P.CAST_COOLDOWN_MS / 1000) .. "s apart | poll every "
	.. tostring(P.POLL_MS / 1000) .. "s, max " .. tostring(P.MAX_POLLS) .. " polls / "
	.. tostring(P.MAX_CASTS) .. " casts | console: zz_probe_enemy_target_status()")

-- register the ability-command listener before anything else can fire
do
	local ok_cmd, e_cmd = pcall(function()
		bm:register_command_handler_callback("Special Ability", P.on_special_ability_cmd, "zz_probe_et_cmd")
	end)
	P.cmd_listener_ok = (ok_cmd == true)
	P.log("command listener 'Special Ability' registered=" .. tostring(P.cmd_listener_ok)
		.. (ok_cmd and "" or (" err=" .. truncate(e_cmd, 120))))
end

local ok_reg, err_reg = pcall(function()
	bm:repeat_callback(P.tick, P.POLL_MS, P.NAME)
end)
if ok_reg then
	P.log("timer registered: " .. P.NAME .. " every " .. tostring(P.POLL_MS) .. " ms")
else
	P.log("timer registration FAILED: " .. truncate(err_reg, 160)
		.. " - use the console: zz_probe_enemy_target_status()")
end
