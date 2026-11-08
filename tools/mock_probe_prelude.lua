-- Mock engine prelude for the zz_probe_unit_reads round-2 smoke test.
-- Loaded into a lupa Lua runtime BEFORE the probe. It provides exactly the
-- globals the probe touches (bm, out) and builds handle mocks that:
--   * return values for reads that must WORK,
--   * raise for reads that must be EXISTS-BUT-ERRORS,
--   * leave names undefined for reads that must be ABSENT,
--   * install a TRIP function for every write-family name the probe knows
--     (set_/change_/modify_/refill_/grant_/heal_/reduce_/kill_/respawn). If the
--     probe ever CALLS one, `trips` records it and the smoke test fails.

trips = {}
ground_calls = 0
second_fn = nil
repeat_fn = nil

local function make_write(name)
	return function(...)
		trips[#trips + 1] = name
		error("WRITE CALLED (probe must never call a setter): " .. name)
	end
end

local vec_mt = { __tostring = function() return "battle_vector (MOCK)" end }
local function make_vec() return setmetatable({}, vec_mt) end

local army, battle, uc, su, unit, coll

-- ------------------------------- battle_unit -------------------------------
unit = {}
unit.type = function() return "mock_unit" end
unit.unique_ui_id = function() return 101 end
unit.unary_of_men_alive = function() return 0.5 end
unit.unary_hitpoints = function() return 0.7 end
unit.number_of_men_alive = function() return 50 end
unit.initial_number_of_men = function() return 100 end
unit.number_of_enemies_killed = function() return 3 end
unit.is_under_missile_attack = function() return false end
unit.slow_speed = function() return 3.0 end
unit.fast_speed = function() return 10.0 end
unit.position = function() return make_vec() end
unit.owned_special_abilities = function() return { "k1", "k2" } end
unit.can_perform_special_ability = function(key) return true end
unit.current_target = function() return nil end
unit.num_special_abilities = function() return 2 end
unit.is_in_melee = function() return false end
unit.is_moving_fast = function() return true end
unit.is_moving = function() return true end
unit.army = function() return army end
unit.unit_in_range = function(self, target)
	if target == self then return true end
	error("mock: unit_in_range expects a battle_unit, got something else")
end
-- EXISTS-BUT-ERRORS reads:
unit.is_crumbling = function() error("mock: is_crumbling not available at runtime") end
unit.strategic_value = function() error("mock: strategic_value not available at runtime") end
-- ABSENT reads (health_percent, hit_points, buffs, is_unstable, ...) are simply
-- not defined: indexing them yields nil.
for _, n in ipairs({
	"heal_hitpoints_unary", "reduce_hitpoints_unary", "set_current_ammo_unary",
	"kill_number_of_men", "respawn", "set_special_abilities_flags",
	"set_stat_attribute", "disable_special_ability",
	"disable_passive_special_abilities", "disable_non_passive_special_abilities",
	"mark_as_ally", "deploy_reinforcement", "highlight", "select_in_ui",
}) do unit[n] = make_write(n) end

-- ------------------------------- battle_army -------------------------------
army = {}
army.winds_of_magic_current = function() return 30.0 end
army.winds_of_magic_remaining_recharge_rate = function() return 0.5 end
army.winds_of_magic_reserve = function() return 100.0 end
army.faction_key = function() return "wh_main_empire" end
army.unique_id = function() return 1 end
for _, n in ipairs({
	"modify_winds_of_magic_current", "modify_winds_of_magic_reserve",
	"change_faction", "allow_use_toggleables", "enable_reinforcement",
	"enable_army_destruction_morale_effect", "reset_currency_amount",
	"enable_reinforcement_adc", "suppress_reinforcement_adc",
}) do army[n] = make_write(n) end

-- --------------------------------- battle ----------------------------------
battle = {}
battle.current_battle_speed = function() return 1.0 end
for _, n in ipairs({
	"modify_battle_speed", "restore_battle_speed",
	"change_conflict_time_update_overridden", "change_victory_countdown_limit",
	"set_volume", "set_music_vm_variable", "set_banners_enabled",
	"set_stat_attribute", "set_special_abilities_flags",
}) do battle[n] = make_write(n) end

-- --------------------------- battle_unitcontroller -------------------------
uc = {}
uc.perform_special_ability_ground = function(...) ground_calls = ground_calls + 1 end
for _, n in ipairs({
	"change_fatigue_amount", "change_move_speed", "change_current_walk_speed",
	"change_shot_type", "change_shot_type_q", "change_behaviour_active",
	"change_group_formation", "change_group_formation_q", "change_enabled",
	"set_invincible", "set_invisible_to_all", "set_always_visible_to_all",
	"set_contributes_to_army_strength", "set_matched_combat_chance",
}) do uc[n] = make_write(n) end

-- -------------------------------- script_unit ------------------------------
su = {}
su.unit = unit
su.uc = uc
su.owned_special_abilities = function() return unit:owned_special_abilities() end
su.is_under_attack = function() error("mock: is_under_attack not available at runtime") end
for _, n in ipairs({
	"modify_ammo", "refill_ammo", "grant_infinite_ammo", "set_enabled",
	"set_always_visible", "set_always_visible_no_hidden",
	"set_always_visible_no_leave_battle",
	"set_always_visible_no_hidden_no_leave_battle", "set_melee_mode",
	"set_stat_attribute", "set_invisible_to_all", "change_behaviour_active",
	"take_control", "release_control", "refresh", "cache_ammo",
	"restore_cached_ammo", "cache_health", "withdraw", "halt",
}) do su[n] = make_write(n) end

-- ------------------------- script unit collection --------------------------
coll = {}
function coll:count() return 1 end
function coll:item(i) return su end

-- ------------------------------ battle_manager -----------------------------
bm = {}
bm.battle = battle
function bm:is_conflict_phase() return true end
function bm:get_current_phase_name() return "Deployed" end
function bm:get_scriptunits_for_local_players_army() return coll end
function bm:repeat_callback(fn, ms, name) repeat_fn = fn; return true end
function bm:callback(fn, ms, name) second_fn = fn; return true end

out = function(...) end
