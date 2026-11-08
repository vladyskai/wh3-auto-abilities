-- Mock engine prelude for the zz_probe_step smoke test.
-- Provides exactly the globals the step probe touches (bm, out, io is real) and
-- models the caster's movement/order/state reads + the command-event instrument.
--
-- Control globals (set by the smoke driver):
--   caster_move      m added to caster_pos.x on each advance() (per-poll drift)
--   caster_is_moving the value unit:is_moving() answers
--   cast_accept      per-cast accepted result (index = perf_calls)
--   cast_move        per-cast caster_move (index = perf_calls)
--
-- fire_cmd(name, b1, s1) invokes the probe's registered callback for that name.

caster_pos = { x = 0.0, y = 0.0 }
caster_move = 0.0
caster_is_moving = false
perf_calls = 0
trips = {}
cast_accept = { true, false, true, true }
cast_move = { 0.3, 0.5, 0.0, 0.0 }
cmd_cbs = {}
repeat_fn = nil

function advance() caster_pos.x = caster_pos.x + caster_move end

function fire_cmd(name, b1, s1)
	local cb = cmd_cbs[name]
	if cb == nil then error("mock: no handler for command '" .. tostring(name) .. "'") end
	cb({
		get_name = function() return name end,
		get_bool1 = function() return b1 end,
		get_string1 = function() return s1 end,
		get_unit = function() return nil end,
		get_position = function() return nil end,
	})
end

local function make_write(name)
	return function()
		trips[#trips + 1] = name
		error("WRITE CALLED (probe must only cast): " .. name)
	end
end

local vec_mt = {}
vec_mt.__index = vec_mt
vec_mt.__tostring = function() return "battle_vector (MOCK)" end
function vec_mt:get_x() return self.x end
function vec_mt:get_y() return self.y end
local function make_vec(x, y) return setmetatable({ x = x or 0, y = y or 0 }, vec_mt) end

-- the caster's battle_unit: every movement/order/state read the dump offers
local function make_caster()
	local u = {}
	u.type = function() return "wh_main_emp_cha_witch_hunter_0" end
	u.unique_ui_id = function() return 999 end
	u.position = function() return make_vec(caster_pos.x, caster_pos.y) end
	u.ordered_position = function() return make_vec(caster_pos.x + 5, caster_pos.y) end
	u.ordered_bearing = function() return 90.0 end
	u.ordered_width = function() return 1.4 end
	u.bearing = function() return 88.0 end
	u.position_of_officer = function() return make_vec(caster_pos.x, caster_pos.y) end
	u.is_moving = function() return caster_is_moving end
	u.is_moving_fast = function() return false end
	u.is_idle = function() return not caster_is_moving end
	u.slow_speed = function() return 1.4 end
	u.fast_speed = function() return 3.6 end
	u.current_target = function() return nil end
	u.unit_in_range = function(t) return true end
	u.unit_distance = function(t) return 5.0 end
	u.is_in_melee = function() return false end
	u.is_under_missile_attack = function() return false end
	u.is_ai_controlled = function() return false end
	u.is_script_controlled = function() return false end
	u.is_player_controlled = function() return true end
	u.has_attribute = function(k) return false end
	u.is_behaviour_active = function(k) return false end
	u.owned_special_abilities = function() return { "wh_main_hero_abilities_accusation" } end
	u.owned_non_passive_special_abilities = function() return { "wh_main_hero_abilities_accusation" } end
	u.can_perform_special_ability = function(k) return true end
	-- forbidden write traps (must never be called)
	u.select_in_ui = make_write("select_in_ui")
	u.kill_number_of_men = make_write("kill_number_of_men")
	return u
end

local caster_unit = make_caster()
-- the script_unit wrapper: only has_moved + is_in_melee exist;
-- get_cached_* / position_offset are deliberately ABSENT.
local caster_su = { unit = caster_unit }
function caster_su:has_moved(p, thr) return caster_move > 0 end
function caster_su:is_in_melee() return false end

local caster_uc = {}
caster_uc.reset_ability_cooldown = make_write("reset_ability_cooldown")
function caster_uc:perform_special_ability(key, target)
	perf_calls = perf_calls + 1
	caster_move = cast_move[perf_calls] or 0.0
	if cast_accept[perf_calls] == false then
		-- the engine delivers a refusal (cooldown) as a Lua error
		error("unit '999' does not support this special ability")
	end
	return true
end
caster_su.uc = caster_uc

local function make_enemy(ui, typ)
	local u = {}
	u.type = function() return typ end
	u.unique_ui_id = function() return ui end
	u.position = function() return make_vec(200 + ui, 300) end
	u.is_in_melee = function() return true end
	u.is_under_missile_attack = function() return false end
	u.unit_distance = function(t) return 5.0 end
	return u
end
local e1 = { unit = make_enemy(1003, "wh_main_vmp_cha_master_necromancer_0"), uc = {} }
local e2 = { unit = make_enemy(1004, "wh_main_vmp_inf_zombie"), uc = {} }

local enemy_coll = {}
function enemy_coll:count() return 2 end
function enemy_coll:item(i) return ({ e1, e2 })[i] end

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
function bm:register_command_handler_callback(cmd, cb, name) cmd_cbs[cmd] = cb; return true end

out = function(...) end
