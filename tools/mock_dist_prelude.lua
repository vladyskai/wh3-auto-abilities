-- Mock engine prelude for the zz_probe_dist smoke test.
-- Provides the globals the distance probe touches (bm, out) and models the
-- caster's position/movement reads, the enemy candidates and the engine's own
-- unit_in_range helper. Control globals (set by the smoke driver):
--   conflict           bm:is_conflict_phase() answer
--   phase_name         bm:get_current_phase_name() answer
--   caster_x/caster_y  the caster's centre position (drives move-since-last)
--   caster_is_moving   unit:is_moving() answer
--   caster_is_idle     unit:is_idle() answer
--   can_perf           can_perform_special_ability() answer
--   engine_range_max   unit_in_range() is true when unit_distance <= this
--   enemy_dist         { [enemy_unit] = metres }  (read via unit_distance)

conflict = false
phase_name = "Deployment"
caster_x = 0.0
caster_y = 0.0
caster_is_moving = false
caster_is_idle = true
can_perf = true
engine_range_max = 60.0
perf_trap = 0
trips = {}
repeat_fn = nil

local vec_mt = {}
vec_mt.__index = vec_mt
vec_mt.__tostring = function() return "battle_vector (MOCK)" end
function vec_mt:get_x() return self.x end
function vec_mt:get_y() return self.y end
local function make_vec(x, y) return setmetatable({ x = x or 0, y = y or 0 }, vec_mt) end

local function make_write(name)
	return function()
		trips[#trips + 1] = name
		error("WRITE CALLED (probe must be read-only): " .. name)
	end
end

enemy_dist = {}

local caster_unit = {}
caster_unit.type = function() return "wh_main_emp_cha_witch_hunter_0" end
caster_unit.unique_ui_id = function() return 999 end
caster_unit.position = function() return make_vec(caster_x, caster_y) end
caster_unit.is_moving = function() return caster_is_moving end
caster_unit.is_idle = function() return caster_is_idle end
caster_unit.unit_distance = function(self, t) local d = enemy_dist[t]; if d == nil then error("no dist") end; return d end
caster_unit.unit_in_range = function(self, t) local d = enemy_dist[t]; if d == nil then error("no dist") end; return d <= engine_range_max end
caster_unit.is_in_melee = function() return false end
caster_unit.is_under_missile_attack = function() return false end
caster_unit.owned_special_abilities = function() return { "wh_main_hero_abilities_accusation" } end
caster_unit.owned_non_passive_special_abilities = function() return { "wh_main_hero_abilities_accusation" } end
caster_unit.can_perform_special_ability = function(k) return can_perf end
-- forbidden write traps (must never be called)
caster_unit.select_in_ui = make_write("select_in_ui")
caster_unit.reset_ability_cooldown = make_write("reset_ability_cooldown")
caster_unit.kill_number_of_men = make_write("kill_number_of_men")
caster_unit.heal_hitpoints_unary = make_write("heal_hitpoints_unary")

local caster_uc = {}
caster_uc.perform_special_ability = function() perf_trap = perf_trap + 1; error("CAST ATTEMPTED (observer must not cast)") end
caster_uc.perform_special_ability_ground = function() perf_trap = perf_trap + 1; error("GROUND CAST ATTEMPTED") end

local caster_su = { unit = caster_unit, uc = caster_uc }

local function make_enemy(ui, typ)
	local u = {}
	u.type = function() return typ end
	u.unique_ui_id = function() return ui end
	u.position = function() return make_vec(300, 300) end
	u.is_in_melee = function() return ui == 1001 end
	u.is_under_missile_attack = function() return ui == 1002 end
	return u
end
local e1 = { unit = make_enemy(1001, "wh_main_vmp_inf_zombie"), uc = {} }
local e2 = { unit = make_enemy(1002, "wh_main_vmp_cha_master_necromancer_0"), uc = {} }
local e3 = { unit = make_enemy(1003, "wh_main_vmp_inf_skeleton_warriors"), uc = {} }
enemy_dist[e1.unit] = 120.0
enemy_dist[e2.unit] = 200.0
enemy_dist[e3.unit] = 999.0

local enemy_coll = {}
function enemy_coll:count() return 3 end
function enemy_coll:item(i) return ({ e1, e2, e3 })[i] end

local our_coll = {}
function our_coll:count() return 1 end
function our_coll:item(i) return caster_su end

bm = {}
function bm:is_conflict_phase() return conflict end
function bm:get_current_phase_name() return phase_name end
function bm:get_scriptunits_for_main_enemy_army_to_local_player() return enemy_coll end
function bm:get_scriptunits_for_local_players_army() return our_coll end
function bm:repeat_callback(fn, ms, name) repeat_fn = fn; return true end
function bm:register_command_handler_callback() return true end

-- driver control helpers
function set_e1(d) enemy_dist[e1.unit] = d end

out = function(...) end
