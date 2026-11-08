--------------------------------------------------------------------------------
-- zz_probe_unit_reads.lua - RUNTIME PROBE FOR UNIT READS (separate from the mod)
--
-- WHY THIS FILE EXISTS
--   The ability project needs to know which battle_unit reads ACTUALLY work at
--   runtime, not merely which names appear in the API dump. This file is a
--   throwaway probe: it runs in a real battle, calls each candidate read on a
--   local-player unit under pcall, and writes ONE capped block per pass to its
--   OWN log file. It never touches the main mod (zz_test_deadly_onslaught.lua)
--   and it is trivially removable: delete this one file and rebuild.
--
-- WHERE THIS FILE GOES
--   script/battle/mod/zz_probe_unit_reads.lua inside the .pack. The game's own
--   mod loader (script/_lib/lib_mod_loader.lua) runs core:load_mods on
--   "/script/battle/mod/" in every battle and EXECUTES every *.lua it finds, so
--   the top-level code below runs at load. This probe PROVES it ran by logging:
--   if the log file below never appears, the loading mechanism is the finding.
--
-- WHERE THE OUTPUT GOES
--   zz_probe_unit_reads_log.txt, in the game's install folder (next to
--   Warhammer3.exe) - a DIFFERENT file from the main mod's log, so the two can
--   never mix. Search it for "zz_probe_unit_reads".
--
-- WHAT IT TESTS (per sample unit, every pass):
--   * the DUMP-CONFIRMED reads        - is each actually callable and sane?
--   * the CLAIMED-BUT-ABSENT reads    - health / ammo / stat / effects names
--   * PLAUSIBLE VARIANTS             - shortened / alternate spellings, the
--                                      dump-declared health/ammo reads, and
--                                      ability active/buff state candidates
--   ROUND 2 adds, found by grepping the API dumps for the naming family the
--   round-1 wins revealed:
--   * NEW READS                      - unary_of_men_alive, is_under_missile_attack,
--                                      slow_speed, is_under_attack (script_unit),
--                                      unit_in_range (both argument shapes),
--                                      winds_of_magic_current /
--                                      winds_of_magic_remaining_recharge_rate /
--                                      winds_of_magic_reserve (on battle_army),
--                                      current_battle_speed (on battle), plus a
--                                      broad sweep of other zero-arg reads.
--   * PRESENCE-ONLY WRITES           - the setter/change/modify/refill/grant/
--                                      heal/reduce family. These are NEVER
--                                      CALLED: only whether the member EXISTS is
--                                      reported, so the experiment cannot change
--                                      battle state.
--   * DOUBLE-SAMPLE                  - the two live reads (unary_of_men_alive,
--                                      unary_hitpoints) are read twice ~10 s
--                                      apart in the same pass, to show whether
--                                      the value changes (live) or not (static).
--   Each read line is classified: WORKS / EXISTS-BUT-ERRORS / ABSENT.
--   PASS 1 also re-confirms the GROUND-TARGETED cast call
--   (battle_unitcontroller:perform_special_ability_ground with the caster's own
--   position) from this separate file.
--
-- PACE: one block every PROBE_MS (20 s), capped at PROBE_MAX_PASSES (6) so the
-- log stays small. A console rescue hook (zz_probe_now) can force one pass from
-- the Lua console (Modding Development Tools, shift+F3) if the timer never runs.
--------------------------------------------------------------------------------


-- ============================================================================
-- 1. THE PROBE'S OWN LOG (a file of its own - never the main mod's log)
-- ============================================================================

local PROBE_TAG  = "[zz_probe_unit_reads] "
local LOG_FILE   = "zz_probe_unit_reads_log.txt"
local PROBE_MS   = 20000          -- one pass every 20 s
local PROBE_MAX_PASSES = 6        -- capped: at most 6 blocks
local PROBE_NAME = "zz_probe_unit_reads_poll"
local SECOND_MS  = 10000          -- round 2: re-read the two live reads 10 s later

local log_handle = nil
local file_logging_off = false

local function write_to_file(line)
	if file_logging_off then return end

	if log_handle == nil then
		local ok, handle = pcall(io.open, LOG_FILE, "a")
		if not ok or handle == nil then
			file_logging_off = true
			return
		end
		log_handle = handle
		pcall(function()
			log_handle:write("\n======== zz_probe_unit_reads session ========\n")
			log_handle:flush()
		end)
	end

	pcall(function()
		log_handle:write(line .. "\n")
		log_handle:flush()
	end)
end

local function log(message)
	local line = PROBE_TAG .. tostring(message)
	write_to_file(line)
	if ModLog ~= nil then pcall(ModLog, line) end
	pcall(out, line)
end


-- ============================================================================
-- 2. SMALL SAFE HELPERS (every engine touch is pcall'd; no error can escape)
-- ============================================================================

-- Capture the Lua global type() so the classifier can tell an engine method
-- apart from a name that merely resolves to a Lua global (e.g. shadowing).
local lua_type = type

local function truncate(s, n)
	s = tostring(s)
	if #s > n then return string.sub(s, 1, n) .. "..." end
	return s
end

-- One compact rendering of a returned value (plain tables are counted, not
-- dumped; a value with its own tostring - e.g. a vector - shows its text).
local function fmt(v)
	local t = lua_type(v)
	if t == "table" then
		local n = 0
		pcall(function()
			for _ in pairs(v) do
				n = n + 1
				if n >= 50 then break end
			end
		end)
		local ok, s = pcall(tostring, v)
		if ok and s ~= nil and string.sub(s, 1, 5) ~= "table" then
			return truncate(s, 60) .. " #n=" .. tostring(n)
		end
		return "#table(" .. tostring(n) .. (n >= 50 and "+" or "") .. ")"
	end
	local ok, s = pcall(tostring, v)
	if ok and s ~= nil then return truncate(s, 60) end
	return "<no-tostring>"
end

-- The first owned special-ability key on this unit (for the one read that
-- takes an argument), or nil when nothing is owned / readable.
local function first_owned_key(unit)
	local ok, owned = pcall(function() return unit:owned_special_abilities() end)
	if ok and lua_type(owned) == "table" then
		for _, v in pairs(owned) do
			if lua_type(v) == "string" then return v end
		end
	end
	return nil
end

-- Which argument a named read needs, if any. Only two shapes occur here:
-- can_perform_special_ability wants a key; GetProperty wants a property name.
local function call_arg_for(unit, name)
	if name == "can_perform_special_ability" then
		return first_owned_key(unit) or "wh_main_character_abilities_deadly_onslaught"
	elseif name == "GetProperty" or name == "get_property" then
		return "armour"
	end
	return nil
end

-- THE CLASSIFIER. Reads the member, then calls it, and returns one verdict:
--   WORKS               - callable and returned a value (or an existing
--                         non-callable member answered)
--   EXISTS-BUT-ERRORS   - the member exists and calling it raised
--   ABSENT              - no such member (nil, or the member read itself raised)
local function probe_read(unit, name)
	local ok_get, m = pcall(function() return unit[name] end)
	if not ok_get then
		return "ABSENT | member read raised: " .. truncate(m, 80)
	end

	local mt = lua_type(m)
	if mt ~= "function" then
		if m == nil then
			return "ABSENT"
		end
		return "WORKS | (non-callable " .. mt .. ") value=" .. fmt(m)
	end

	if m == lua_type then
		return "ABSENT | name resolves to the Lua global type()"
	end

	local arg = call_arg_for(unit, name)
	local ok, v
	if arg ~= nil then
		ok, v = pcall(m, unit, arg)
	else
		ok, v = pcall(m, unit)
	end

	if ok then
		return "WORKS | value=" .. fmt(v)
	end
	return "EXISTS-BUT-ERRORS | err=" .. truncate(v, 120)
end

-- PRESENCE-ONLY classifier (round 2). Reads the member and reports whether it
-- EXISTS on the handle. It NEVER calls the member, so a setter can be
-- inventoried without the probe ever changing battle state.
local function probe_presence(handle, name)
	if handle == nil then return "NO HANDLE" end
	local ok_get, m = pcall(function() return handle[name] end)
	if not ok_get then
		return "ABSENT | member read raised: " .. truncate(m, 80)
	end
	if m == nil then return "ABSENT" end
	local mt = lua_type(m)
	if mt == "function" then return "EXISTS (function) - NOT CALLED" end
	return "EXISTS (non-callable " .. mt .. ") - NOT CALLED"
end


-- ============================================================================
-- 3. THE CANDIDATE READS
-- ============================================================================

-- (a) names the extracted API dump declares on battle_unit.
local DUMP_CONFIRMED = {
	"number_of_men_alive", "fatigue_state", "is_wavering", "is_routing",
	"is_shattered", "is_crumbling", "is_unstable", "fast_speed", "position",
	"bearing", "is_in_melee", "is_moving_fast", "is_idle", "is_valid_target",
	"owned_special_abilities", "can_perform_special_ability", "type",
	"current_target", "unique_ui_id",
}

-- (b) health / ammo / morale / stat / effects names believed ABSENT.
local CLAIMED_ABSENT = {
	"health_percent", "hit_points", "max_hit_points",
	"initial_number_of_men_alive", "ammunition_percent", "morale_percent",
	"armour", "armor", "melee_attack", "melee_defence", "weapon_damage",
	"ap_damage", "active_effects", "effects", "buffs", "modifiers",
	"has_effect", "is_under_effect",
}

-- (c) plausible variants - one call each. The last group also carries the
-- dump-declared health/ammo reads (unary_hitpoints, ammo_left, ...) and the
-- ability active/buff state candidates, so runtime decides instead of prose.
local VARIANTS = {
	"health", "health_remaining", "hp", "hitpoints", "hit_points_percent",
	"ammo", "ammunition", "melee_attack_value", "armour_value",
	"weapon_damage_value", "GetProperty", "get_property",
	"unary_hitpoints", "ammo_left", "starting_ammo", "initial_number_of_men",
	"number_of_enemies_killed", "missile_range",
	"active_abilities", "ability_active", "is_ability_active",
	"has_ability_active", "active_special_abilities", "passive_special_abilities",
}

-- Keys whose engine call is the POSITION form (for the ground-cast re-confirm).
local GROUND_KEYS = {
	["wh3_dlc24_character_abilities_tacticians_stand_your_ground"] = true,
}


-- ============================================================================
-- 3b. ROUND-2 CANDIDATES (found by grepping the API dumps for the naming
--     family the round-1 wins revealed)
--
--     DUMPS ARE REFERENCES, NOT PROOF. Round 1 already proved that: is_crumbling
--     and is_unstable are declared in battle_unit.lua yet ABSENT at runtime. So
--     every round-2 read is still decided by a live call under pcall, and every
--     write is only ever PRESENCE-checked, never called.
-- ============================================================================

-- (d) round-2 new UNIT reads. is_under_attack is declared on script_unit, not
--     battle_unit, so it is probed on the script_unit handle below.
local R2_UNIT_READS = {
	"unary_of_men_alive", "is_under_missile_attack", "slow_speed",
}

-- (d2) round-2 new reads on the script_unit handle (su).
local R2_SCRIPTUNIT_READS = {
	"is_under_attack",
}

-- (e) other zero-arg reads found in the dumps, family terms: unary_, *_left,
--     *_percent, *_current, starting_, missile_, and hitpoint/health/fatigue/
--     ammo/damage/armour/attack/defence/charge/bonus/speed/range/morale.
local R2_UNIT_EXTRA = {
	"is_moving", "is_leaving_battle", "is_valid_for_deployment",
	"is_invulnerable", "is_rampaging", "is_controllable", "is_deploying",
	"is_deployed", "is_currently_flying", "can_fly", "is_hidden",
	"is_currently_garrisoned", "strategic_value", "ordered_bearing",
	"ordered_width", "num_special_abilities",
	"owned_passive_special_abilities", "owned_non_passive_special_abilities",
	"can_use_magic", "unit_class", "is_commanding_unit", "alliance_index",
	"army_index", "is_ai_controlled", "is_script_controlled",
	"is_player_controlled", "is_left_flank_threatened",
	"is_right_flank_threatened", "is_rear_flank_threatened", "left_flank_threat",
	"right_flank_threat", "rear_threat", "is_on_top_of_platform",
}

-- (f) ARMY reads (army = unit:army()). Winds-of-magic lives on the army.
local R2_ARMY_READS = {
	"winds_of_magic_current", "winds_of_magic_remaining_recharge_rate",
	"winds_of_magic_reserve", "faction_key", "subculture_key", "is_rebel",
	"is_commander_alive", "is_commander_invincible", "is_player_controlled",
	"army_handicap", "unique_id", "num_reinforcement_units",
	"is_reinforcement_army", "flag_path",
}

-- (g) BATTLE reads (battle = bm.battle). current_battle_speed lives on battle.
local R2_BATTLE_READS = {
	"current_battle_speed",
}

-- (h) PRESENCE-ONLY writes. NEVER CALLED: an experiment must not change battle
--     state. For each, we report only whether the member EXISTS and is a
--     function. Grouped by the handle the dump declares it on.
local WRITE_UNIT = {
	"heal_hitpoints_unary", "reduce_hitpoints_unary", "set_current_ammo_unary",
	"kill_number_of_men", "respawn", "set_special_abilities_flags",
	"set_stat_attribute", "disable_special_ability",
	"disable_passive_special_abilities", "disable_non_passive_special_abilities",
	"mark_as_ally", "deploy_reinforcement", "highlight", "select_in_ui",
}
local WRITE_SCRIPTUNIT = {
	"modify_ammo", "refill_ammo", "grant_infinite_ammo", "set_enabled",
	"set_always_visible", "set_always_visible_no_hidden",
	"set_always_visible_no_leave_battle",
	"set_always_visible_no_hidden_no_leave_battle", "set_melee_mode",
	"set_stat_attribute", "set_invisible_to_all", "change_behaviour_active",
	"take_control", "release_control", "refresh", "cache_ammo",
	"restore_cached_ammo", "cache_health", "withdraw", "halt",
}
local WRITE_ARMY = {
	"modify_winds_of_magic_current", "modify_winds_of_magic_reserve",
	"change_faction", "allow_use_toggleables", "enable_reinforcement",
	"enable_army_destruction_morale_effect", "reset_currency_amount",
	"enable_reinforcement_adc", "suppress_reinforcement_adc",
}
local WRITE_BATTLE = {
	"modify_battle_speed", "restore_battle_speed",
	"change_conflict_time_update_overridden", "change_victory_countdown_limit",
	"set_volume", "set_music_vm_variable", "set_banners_enabled",
	"set_stat_attribute", "set_special_abilities_flags",
}
local WRITE_UC = {
	"change_fatigue_amount", "change_move_speed", "change_current_walk_speed",
	"change_shot_type", "change_shot_type_q", "change_behaviour_active",
	"change_group_formation", "change_group_formation_q", "change_enabled",
	"set_invincible", "set_invisible_to_all", "set_always_visible_to_all",
	"set_contributes_to_army_strength", "set_matched_combat_chance",
}

-- (i) the two live reads re-sampled ~10 s later in the same pass, to show the
--     value CHANGE over time (proving the read is live, not a static constant).
local DOUBLE_SAMPLE = { "unary_of_men_alive", "unary_hitpoints" }


-- ============================================================================
-- 4. ONE PASS
-- ============================================================================

local passes_done = 0
local waiting_logged = false

-- Pick the key used for the ground-cast re-confirm: prefer a real ground key
-- the unit owns, else any owned key, else the known ground key (to exercise the
-- call shape even when unowned).
local function pick_ground_key(unit)
	local ok, owned = pcall(function() return unit:owned_special_abilities() end)
	local first = nil
	if ok and lua_type(owned) == "table" then
		for _, v in pairs(owned) do
			if lua_type(v) == "string" then
				if first == nil then first = v end
				if GROUND_KEYS[v] then return v, true end
			end
		end
	end
	if first ~= nil then return first, false end
	return "wh3_dlc24_character_abilities_tacticians_stand_your_ground", false
end

local function probe_ground(unit, uc)
	log("-- ground-targeted cast re-confirm (from this separate file) --")

	local api = "ABSENT"
	local ok_api, fn = pcall(function() return uc and uc.perform_special_ability_ground end)
	if ok_api and lua_type(fn) == "function" then
		api = "present (function)"
	end
	log("  uc.perform_special_ability_ground -> " .. api)

	local ok_pos, pos = pcall(function() return unit:position() end)
	if not ok_pos or pos == nil then
		log("  caster own position() -> FAILED (" .. truncate(pos, 100)
			.. ") - ground cast not attempted (fail-open)")
		return
	end
	log("  caster own position() -> ok value=" .. fmt(pos))

	if uc == nil then
		log("  ground cast: SKIPPED (no controller on the script unit)")
		return
	end

	local key, is_ground = pick_ground_key(unit)
	local ok_call, err_call = pcall(function()
		return uc:perform_special_ability_ground(key, pos, 0, 0)
	end)

	if ok_call then
		log("  uc:perform_special_ability_ground('" .. tostring(key)
			.. "', <own pos>, 0, 0) -> CLEAN pcall, engine accepted"
			.. (is_ground and " (owned ground key)" or " (exercised, not an owned ground key)"))
	else
		log("  uc:perform_special_ability_ground('" .. tostring(key)
			.. "', <own pos>, 0, 0) -> CLEAN pcall, engine replied: " .. truncate(err_call, 120))
	end
end

-- unit_in_range takes an argument. The dump signature is:
--   function battle_unit:unit_in_range(target_unit) end   [target_unit: battle_unit] -> boolean
-- We try BOTH shapes so the log records what the engine accepts:
--   (1) the unit's own battle_unit handle  (the documented argument shape),
--   (2) the unit's own position vector     (the shape guessed in the task text).
local function probe_unit_in_range(unit)
	log("  unit_in_range dump signature: function battle_unit:unit_in_range(target_unit)"
		.. " [target_unit: battle_unit] -> boolean")

	local ok_get, m = pcall(function() return unit.unit_in_range end)
	if not ok_get or lua_type(m) ~= "function" then
		log("  unit_in_range -> ABSENT (no callable member on battle_unit)")
		return
	end

	local ok1, v1 = pcall(m, unit, unit)
	if ok1 then
		log("  unit_in_range(own battle_unit) -> WORKS | value=" .. fmt(v1)
			.. "  [argument shape: battle_unit - the documented one]")
	else
		log("  unit_in_range(own battle_unit) -> EXISTS-BUT-ERRORS | err="
			.. truncate(v1, 120))
	end

	local pos = nil
	pcall(function() pos = unit:position() end)
	if pos ~= nil then
		local ok2, v2 = pcall(m, unit, pos)
		if ok2 then
			log("  unit_in_range(own position) -> WORKS | value=" .. fmt(v2)
				.. "  [argument shape: battle_vector - accepted]")
		else
			log("  unit_in_range(own position) -> EXISTS-BUT-ERRORS | err="
				.. truncate(v2, 120)
				.. "  [argument shape: battle_vector - engine wants a battle_unit]")
		end
	else
		log("  unit_in_range(own position) -> SKIPPED (position() unavailable)")
	end
end

local function run_pass(reason)
	if passes_done >= PROBE_MAX_PASSES then return end

	local ok_phase, conflict = pcall(function() return bm:is_conflict_phase() end)
	if not ok_phase or conflict ~= true then
		if not waiting_logged then
			waiting_logged = true
			log("waiting for the conflict phase (no pass run yet)")
		end
		return
	end

	local sunits
	local ok_su, res = pcall(function() return bm:get_scriptunits_for_local_players_army() end)
	if ok_su then sunits = res end
	if sunits == nil then
		if not waiting_logged then
			waiting_logged = true
			log("no local-army script units returned yet")
		end
		return
	end

	local total = 0
	local ok_cnt, cnt = pcall(function() return sunits:count() end)
	if ok_cnt and lua_type(cnt) == "number" then total = cnt end
	if total <= 0 then
		if not waiting_logged then
			waiting_logged = true
			log("local army empty so far")
		end
		return
	end

	passes_done = passes_done + 1
	local idx = ((passes_done - 1) % total) + 1

	local ok_item, su = pcall(function() return sunits:item(idx) end)
	if not ok_item then su = nil end

	local unit = su and su.unit or nil
	local uc = su and su.uc or nil

	local phase_name = "?"
	pcall(function() phase_name = bm:get_current_phase_name() end)

	log("")
	log("===== probe pass " .. tostring(passes_done) .. "/" .. tostring(PROBE_MAX_PASSES)
		.. (reason and (" (" .. tostring(reason) .. ")") or "")
		.. " | phase=" .. tostring(phase_name)
		.. " | local units=" .. tostring(total)
		.. " | sample=" .. tostring(idx) .. "/" .. tostring(total) .. " =====")

	if unit == nil then
		log("sample unit missing - no reads run")
		return
	end

	local u_type, u_id = "?", "?"
	pcall(function() u_type = unit:type() end)
	pcall(function() u_id = unit:unique_ui_id() end)
	log("unit: type=" .. tostring(u_type) .. " unique_ui_id=" .. tostring(u_id))

	log("-- (a) dump-confirmed reads --")
	for i = 1, #DUMP_CONFIRMED do
		local name = DUMP_CONFIRMED[i]
		log("  " .. name .. " -> " .. probe_read(unit, name))
	end

	log("-- (b) claimed-but-absent reads --")
	for i = 1, #CLAIMED_ABSENT do
		local name = CLAIMED_ABSENT[i]
		log("  " .. name .. " -> " .. probe_read(unit, name))
	end

	log("-- (c) plausible variants --")
	for i = 1, #VARIANTS do
		local name = VARIANTS[i]
		log("  " .. name .. " -> " .. probe_read(unit, name))
	end

	-- ---------- ROUND 2 ------------------------------------------------------
	local army = nil
	pcall(function() army = unit:army() end)
	local battle = nil
	pcall(function() battle = bm.battle end)

	log("-- (d) round-2 new unit reads --")
	for i = 1, #R2_UNIT_READS do
		local name = R2_UNIT_READS[i]
		log("  " .. name .. " -> " .. probe_read(unit, name))
	end

	log("-- (d2) round-2 new script_unit reads (handle su; battle_unit lacks these) --")
	for i = 1, #R2_SCRIPTUNIT_READS do
		local name = R2_SCRIPTUNIT_READS[i]
		log("  " .. name .. " -> " .. probe_read(su, name))
	end

	log("-- (d3) unit_in_range (takes an argument) --")
	pcall(probe_unit_in_range, unit)

	log("-- (e) other zero-arg reads found in the dumps --")
	for i = 1, #R2_UNIT_EXTRA do
		local name = R2_UNIT_EXTRA[i]
		log("  " .. name .. " -> " .. probe_read(unit, name))
	end

	log("-- (f) army reads (army = unit:army()) --")
	if army == nil then
		log("  army handle unavailable - army reads skipped")
	else
		for i = 1, #R2_ARMY_READS do
			local name = R2_ARMY_READS[i]
			log("  " .. name .. " -> " .. probe_read(army, name))
		end
	end

	log("-- (g) battle reads (battle = bm.battle) --")
	if battle == nil then
		log("  battle handle unavailable (bm.battle not set yet) - battle reads skipped")
	else
		for i = 1, #R2_BATTLE_READS do
			local name = R2_BATTLE_READS[i]
			log("  " .. name .. " -> " .. probe_read(battle, name))
		end
	end

	log("-- (h) PRESENCE-ONLY writes (NEVER CALLED - state must not change) --")
	local function presence_block(label, handle, list)
		log("  [" .. label .. "]")
		if handle == nil then
			log("    handle unavailable - presence not checkable")
			return
		end
		for i = 1, #list do
			local name = list[i]
			log("    " .. name .. " -> " .. probe_presence(handle, name))
		end
	end
	presence_block("battle_unit", unit, WRITE_UNIT)
	presence_block("script_unit", su, WRITE_SCRIPTUNIT)
	presence_block("battle_army", army, WRITE_ARMY)
	presence_block("battle", battle, WRITE_BATTLE)
	presence_block("battle_unitcontroller", uc, WRITE_UC)

	log("-- (i) double-sample: change over time (2nd read ~"
		.. tostring(SECOND_MS / 1000) .. " s later) --")
	for i = 1, #DOUBLE_SAMPLE do
		local name = DOUBLE_SAMPLE[i]
		log("  " .. name .. " #1 (t0): " .. probe_read(unit, name))
	end
	local idx_snapshot = idx
	local pass_snapshot = passes_done
	local cb_name = "zz_probe_second_" .. tostring(pass_snapshot)
	local ok_reg2, err_reg2 = pcall(function()
		bm:callback(function()
			local ok2, err2 = pcall(function()
				local s2 = bm:get_scriptunits_for_local_players_army()
				local u2 = nil
				if s2 ~= nil then
					pcall(function() u2 = s2:item(idx_snapshot).unit end)
				end
				if u2 == nil then u2 = unit end
				for j = 1, #DOUBLE_SAMPLE do
					local name = DOUBLE_SAMPLE[j]
					log("  " .. name .. " #2 (~" .. tostring(SECOND_MS / 1000)
						.. " s later): " .. probe_read(u2, name))
				end
			end)
			if not ok2 then
				log("  double-sample callback error: " .. truncate(err2, 140))
			end
		end, SECOND_MS, cb_name)
	end)
	if not ok_reg2 then
		log("  double-sample timer registration FAILED: " .. truncate(err_reg2, 140))
	end
	-- ---------- end ROUND 2 ------------------------------------------------

	-- PASS 1 ONLY: the ground-cast re-confirm (least disruptive cadence).
	if passes_done == 1 then
		pcall(probe_ground, unit, uc)
	end

	if passes_done >= PROBE_MAX_PASSES then
		log("probe complete: " .. tostring(PROBE_MAX_PASSES)
			.. " passes logged. Remove this file and rebuild to uninstall.")
	end
end


-- ============================================================================
-- 5. START IT UP (callback error wall + registration + console rescue)
-- ============================================================================

local function zz_probe_tick()
	local ok, err = pcall(run_pass, nil)
	if not ok then
		log("PROBE ERROR (swallowed - the engine's callbacks stay alive): " .. truncate(err, 160))
	end
end

-- Console rescue hooks (Lua console, shift+F3). Prefixed zz_probe_ so nothing
-- can clash with the main mod's globals.
function zz_probe_now()
	local ok, err = pcall(run_pass, "console")
	if ok then
		return "zz_probe_unit_reads: pass requested - see " .. LOG_FILE
	end
	return "zz_probe_unit_reads error: " .. tostring(err)
end

function zz_probe_status()
	return "zz_probe_unit_reads: passes=" .. tostring(passes_done) .. "/"
		.. tostring(PROBE_MAX_PASSES) .. " log=" .. LOG_FILE
end

log("loaded from script/battle/mod/ (auto-load proof). Log file: " .. LOG_FILE
	.. " | ROUND 2 (new reads + presence-only write inventory + double-sample)"
	.. " | one block every " .. tostring(PROBE_MS / 1000) .. " s, max "
	.. tostring(PROBE_MAX_PASSES) .. " passes | console: zz_probe_now()")

local ok_reg, err_reg = pcall(function()
	bm:repeat_callback(zz_probe_tick, PROBE_MS, PROBE_NAME)
end)
if ok_reg then
	log("timer registered: " .. PROBE_NAME .. " every " .. tostring(PROBE_MS) .. " ms")
else
	log("timer registration FAILED: " .. truncate(err_reg, 160)
		.. " - use the console: type zz_probe_now()")
end
