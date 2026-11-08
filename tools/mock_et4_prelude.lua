-- Mock engine prelude for the zz_probe_enemy_target ROUND-4 smoke test.
-- Loaded into a lupa Lua runtime BEFORE the probe. It provides exactly the
-- globals the probe touches (bm, common, out, script_unit) and models:
--   * fresh enemy + caster enumeration with readable fields,
--   * a common.get_context_value ActiveEffectList(true).Size that CHANGES when a
--     simulated cast lands (so the SELF / EFF delta detection is exercised),
--   * the six route shapes' distinct engine entry points:
--       perform_special_ability        (bench_fresh, take_control, attack_then_cast,
--                                       in_range_cast)
--       perform_special_ability_q      (queued_q)
--       battle_army:use_special_ability(army_use)
--     with these OUTCOMES, assigned by call order (deterministic):
--       1st perform_special_ability  -> INERT            (bench_fresh)
--       perform_special_ability_q    -> LANDS on ENEMY    (queued_q)   + CMD event
--       use_special_ability          -> INERT             (army_use)
--       2nd perform_special_ability  -> LANDS on SELF     (take_control) + CMD event
--       3rd perform_special_ability  -> INERT             (attack_then_cast)
--       4th perform_special_ability  -> LANDS on ENEMY    (in_range_cast) + CMD event
--   * take_control / release_control / attack_unit as COUNTERS (they are the
--     routes' legitimate orders - not forbidden writes),
--   * forbidden writes (reset_ability_cooldown, select_in_ui, ...) as TRAPS that
--     record a trip and error if ever CALLED (the probe must never call them),
--   * the "Special Ability" command-event registration, so the mock can fire the
--     engine's own ability-command event when a cast lands,
--   * in-range probing that is FALSE on the first call and TRUE afterwards, so the
--     in_range_cast DEFER path is exercised once before it fires.

casts = {}                    -- one record per cast attempt
perf_calls = 0                -- perform_special_ability calls (4 routes use it)
q_calls = 0
army_calls = 0
take_control_calls = 0
release_control_calls = 0
attack_unit_calls = 0
ground_calls = 0
trips = {}                    -- forbidden writes that were CALLED (must stay empty)
range_calls = 0               -- in_ability_range probes seen
cmd_handler = nil
cmd_fires = 0
repeat_fn = nil

-- effect counts per ui id (the engine state we simulate). The caster is 999.
eff = { [999] = 0, [1003] = 1, [1004] = 0, [1005] = 0 }

local function make_write(name)
	return function()
		trips[#trips + 1] = name
		error("WRITE CALLED (probe must only cast): " .. name)
	end
end

common = {}
function common.get_context_value(typ, id, field)
	local key = tonumber(id)
	if key == nil or eff[key] == nil then
		error("mock: unknown ui id " .. tostring(id))
	end
	if field == "ActiveEffectList(true).Size" then
		return tostring(eff[key])
	elseif field == "ActiveEffectState(true)" then
		if eff[key] > 0 then return "positive" end
		return ""
	end
	error("mock: unknown field " .. tostring(field))
end

local vec_mt = {}
vec_mt.__index = vec_mt
vec_mt.__tostring = function() return "battle_vector (MOCK)" end
function vec_mt:get_x() return self.x end
function vec_mt:get_y() return self.y end
local function make_vec(x, y) return setmetatable({ x = x or 0, y = y or 0 }, vec_mt) end

-- in-range state: FALSE on the very first unit_in_range probe, TRUE after
local function range_ok() return range_calls >= 2 end

local function make_unit(ui, typ, men, hp)
	local u = {}
	u.type = function() return typ end
	u.unique_ui_id = function() return ui end
	u.number_of_men_alive = function() return men end
	u.unary_hitpoints = function() return hp end
	u.is_in_melee = function() return false end
	u.is_valid_target = function() return true end
	u.position = function() return make_vec(10 + ui, 20 + ui) end
	u.owned_special_abilities = function() return {} end
	u.owned_non_passive_special_abilities = function() return {} end
	u.can_perform_special_ability = function(k) return true end
	u.current_target = function() return nil end
	u.unit_in_range = function(t)
		range_calls = range_calls + 1
		return range_ok()
	end
	u.unit_distance = function(t)
		if range_ok() then return 25.3 end
		return 999.0
	end
	return u
end

-- --- the caster (our Witch Hunter, ui 999) ---
local caster_unit = make_unit(999, "wh_main_emp_cha_witch_hunter_0", 1, 1)
caster_unit.owned_special_abilities = function() return { "wh_main_hero_abilities_accusation" } end
caster_unit.owned_non_passive_special_abilities = function() return { "wh_main_hero_abilities_accusation" } end
-- cooldown inventory: ONE working getter, ONE raising getter, the rest ABSENT
caster_unit.ability_charges = function() return 2 end
caster_unit.special_ability_cooldown = function() error("mock: special_ability_cooldown unavailable") end
-- FORBIDDEN write traps (never to be called by the probe)
caster_unit.select_in_ui = make_write("select_in_ui")

-- --- the enemies ---
local enemy_units = {
	make_unit(1003, "wh_main_vmp_cha_master_necromancer_0", 1, 1),
	make_unit(1004, "wh_main_vmp_inf_zombie", 160, 1),
	make_unit(1005, "wh_main_vmp_inf_zombie", 160, 1),
}
local enemy_su = {}
for i = 1, 3 do enemy_su[i] = { unit = enemy_units[i], uc = {} } end

local su_lookup = {}
for i = 1, 3 do su_lookup[enemy_su[i]] = i end
-- also let a fresh script_unit:new wrapper (a plain table) be recognisable
local wrapped = {}

local function land_cmd(key)
	cmd_fires = cmd_fires + 1
	if cmd_handler ~= nil then
		cmd_handler({ get_string1 = function() return key end })
	end
end

-- --- the controller: the ONLY writers the probe may call are the casts + the
--     route orders (counted). Forbidden writes are traps. ---
local caster_uc = {}
caster_uc.reset_ability_cooldown = make_write("reset_ability_cooldown")
function caster_uc:take_control() take_control_calls = take_control_calls + 1; return true end
function caster_uc:release_control() release_control_calls = release_control_calls + 1; return true end
function caster_uc:attack_unit(t, a, b) attack_unit_calls = attack_unit_calls + 1; return true end
function caster_uc:perform_special_ability(key, target)
	perf_calls = perf_calls + 1
	casts[#casts + 1] = { shape = "perform", key = key, target = target }
	if perf_calls == 2 then
		eff[999] = 1                 -- take_control route: self-application
		land_cmd(key)
	elseif perf_calls == 4 then
		eff[1005] = 1                -- in_range_cast route: lands on an enemy
		land_cmd(key)
	end
	-- perf_calls 1 (bench_fresh) and 3 (attack_then_cast) are INERT
	return true
end
function caster_uc:perform_special_ability_q(key, target)
	q_calls = q_calls + 1
	casts[#casts + 1] = { shape = "queued", key = key, target = target }
	eff[1004] = 1                    -- queued_q route: lands on an enemy
	land_cmd(key)
	return true
end
function caster_uc:perform_special_ability_ground(key, pos, a, b)
	ground_calls = ground_calls + 1
	casts[#casts + 1] = { shape = "ground", key = key, target = pos }
	return true
end

-- --- the army (for the army-level route) ---
local caster_army = {}
function caster_army:use_special_ability(key, pos, bearing, width)
	army_calls = army_calls + 1
	casts[#casts + 1] = { shape = "army", key = key, target = pos }
	return true                    -- army_use route: INERT
end
caster_unit.army = function() return caster_army end

local caster_su = { unit = caster_unit, uc = caster_uc }

-- --- script_unit:new (fresh wrapper, mirroring the benchmark's new_by_reference) ---
script_unit = {}
function script_unit:new(unit, name)
	wrapped[#wrapped + 1] = name
	return { unit = unit, name = name }
end

-- --- collections ---
local enemy_coll = {}
function enemy_coll:count() return 3 end
function enemy_coll:item(i) return enemy_su[i] end

local our_coll = {}
function our_coll:count() return 1 end
function our_coll:item(i) return caster_su end

local fp_army = {}
function fp_army:units() return enemy_coll end

bm = {}
function bm:is_conflict_phase() return true end
function bm:get_current_phase_name() return "Deployed" end
function bm:get_scriptunits_for_main_enemy_army_to_local_player() return enemy_coll end
function bm:get_scriptunits_for_local_players_army() return our_coll end
function bm:get_first_non_player_army() return fp_army end
function bm:repeat_callback(fn, ms, name) repeat_fn = fn; return true end
function bm:register_command_handler_callback(cmd, cb, name) cmd_handler = cb; return true end

out = function(...) end
