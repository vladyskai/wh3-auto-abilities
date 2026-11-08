-- Mock engine prelude for the zz_probe_enemy_target ROUND-3 smoke test.
-- Loaded into a lupa Lua runtime BEFORE the probe. It provides exactly the
-- globals the probe touches (bm, common, out) and models:
--   * enemy enumeration (3 enemies + the caster) with readable fields,
--   * a common.get_context_value ActiveEffectList(true).Size that CHANGES when a
--     simulated cast lands (so the SELF / EFF delta detection is exercised),
--   * the four cast shapes' effect outcomes: battle_unit + ground are INERT
--     (round-2 reproduction), script_unit lands on the enemy, nil lands on SELF,
--   * a cooldown accessor inventory (one working getter, one raising getter,
--     everything else ABSENT, and the write-shaped reset_ability_cooldown present
--     but NEVER to be called - a call trips the mock).

casts = {}          -- one record per controller cast call
ground_calls = 0
trips = {}
repeat_fn = nil

local function make_write(name)
	return function()
		trips[#trips + 1] = name
		error("WRITE CALLED (probe must only cast): " .. name)
	end
end

-- effect counts per ui id (the engine state we simulate). The caster is 999.
eff = { [999] = 0, [1003] = 1, [1004] = 0, [1005] = 0 }

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
	u.unit_distance = function(t) return 25.3 end
	return u
end

-- --- the caster (our Witch Hunter, ui 999) ---
local caster_unit = make_unit(999, "wh_main_emp_cha_witch_hunter_0", 1, 1)
caster_unit.owned_special_abilities = function() return { "wh_main_hero_abilities_accusation" } end
caster_unit.owned_non_passive_special_abilities = function() return { "wh_main_hero_abilities_accusation" } end
-- cooldown inventory: ONE working getter, ONE raising getter, the rest ABSENT
caster_unit.ability_charges = function() return 2 end
caster_unit.special_ability_cooldown = function() error("mock: special_ability_cooldown unavailable") end

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

-- --- the controller: the ONLY writer the probe may call is a cast ---
local caster_uc = {}
caster_uc.reset_ability_cooldown = make_write("reset_ability_cooldown")
function caster_uc:perform_special_ability(key, target)
	local shape
	if target == nil then
		shape = "nil"
	elseif su_lookup[target] ~= nil then
		shape = "script_unit"
	else
		shape = "battle_unit"
	end
	casts[#casts + 1] = { shape = shape, key = key, target = target }
	-- simulate the engine outcome per shape
	if shape == "script_unit" then eff[1004] = 1 end -- lands on the SCRIPT_UNIT enemy
	if shape == "nil" then eff[999] = 1 end          -- self-application (H1)
	-- battle_unit: INERT (round-2 reproduction) - nothing changes
	return true
end
function caster_uc:perform_special_ability_ground(key, pos, a, b)
	ground_calls = ground_calls + 1
	casts[#casts + 1] = { shape = "ground", key = key, target = pos }
	return true
end

local caster_su = { unit = caster_unit, uc = caster_uc }

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

out = function(...) end
