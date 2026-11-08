--------------------------------------------------------------------------------
-- TEMPLATE: auto-fire a battle ability under a chosen condition, in every battle.
--
-- Copy this file into a pack at  script/battle/mod/<unique_name>.lua  and edit the
-- SETTINGS block. Everything below it is the known-good shape:
--   settings -> bookkeeping -> tagged logger -> ability match -> charge measurement
--   -> watch list -> heartbeat -> wrapped poll -> registration
--
-- Keep the file NAME unique and make LOG_TAG match it. The folder path is
-- auto-loaded by the engine's own mod loader in campaign battles too, so no
-- vanilla file is touched.
--
-- Worked default: Deadly Onslaught, a self-buff (31 s duration, 90 s cooldown,
-- unlimited uses, no magic cost, not passive, and the engine's own AI treats it as
-- a charge augment). Swap ABILITY_KEYS and the condition for another target.
--
-- Before scripting an approximation of an engine state, check the data layer: a
-- condition the engine already tracks can often be expressed as a `passive`
-- ability plus one deactivate-flag row, evaluated by the engine itself instead of
-- estimated from queries. See references/wh3-mod-authoring.md.
--
-- NO UI WORK BELONGS IN THIS FILE. Creating or repainting a uicomponent from the
-- poll (or from a phase callback) does nothing or kills every timer in the battle.
-- For a control the player operates, follow references/wh3-battle-ui-and-input.md.
--
-- Each part below earned its place in a real run; the comments name the trap it
-- closes. Do not drop the heartbeat or the own-file logger to "simplify": a run
-- that fires nothing then produces a log that cannot distinguish "the timer never
-- ran" from "the trigger was never met".
--------------------------------------------------------------------------------


-- ============================================================================
-- 1. SETTINGS - the only things you normally touch
-- ============================================================================

-- The ability's database keys, from the game's ability table. Keep a LIST: the
-- same ability can exist under more than one key (a current one and a legacy
-- duplicate), and a unit may own the variant you did not guess.
--
-- Find innately-granted abilities in land_units_to_unit_abilites_junctions (note
-- the engine's spelling). That table is a unit's INNATE list, so it is what a
-- custom/skirmish battle will grant; campaign also grants skill-tree abilities.
-- Check it before promising which character can demonstrate the ability.
local ABILITY_KEYS = {
	"wh_main_character_abilities_deadly_onslaught",
}

-- Which situations count as "fire now". Ship ONLY the condition under test: an
-- extra trigger left on "so the run returns a positive result" fires when it
-- should not, and comes back reported as a defect rather than as a discovery.
local FIRE_ON_CHARGE = true
local FIRE_ON_MELEE  = false   -- switch on only to test the melee branch

-- "Charging" is not a query the scripting layer has: is_moving_fast() means
-- running OR charging, so a unit ordered to walk somewhere satisfies it. These
-- gate "a charge that will actually land": has a target, and impact is close.
-- The time is an estimate (distance / the unit's own max fast speed), so it reads
-- slightly optimistic while the unit is still accelerating.
local CHARGE_MIN_DISTANCE_M    = 12   -- a charge needs a run-up
local CHARGE_MAX_DISTANCE_M    = 60   -- ...but not the length of the map
local CHARGE_TIME_TO_CONTACT_S = 4    -- fire when impact is this close

-- How often, in milliseconds, we look at the battlefield. Raise it if a huge army
-- ever shows a frame cost; the shipped example mod polls at 50 ms.
local POLL_MS = 250

-- After an accepted activation, leave the unit alone for the ability's own
-- recharge_time, read from the game's table. Local rate guards are the ONLY
-- cooldown tracking: can_perform_special_ability() is a legality/ownership probe,
-- NOT a cooldown probe - it stays true right through an activation.
local ABILITY_RECHARGE_SECONDS = 90

-- Floor between attempts, so a rejected order cannot be retried every tick.
local MIN_SECONDS_BETWEEN_FIRES = 20

-- Re-scan units with no match yet, in polls. Ability instances may not all be
-- attached at the moment the watch list is built; without this, a late-attaching
-- ability reads as "the unit never had it".
local REDETECT_EVERY_N_POLLS = 16      -- 16 x 250 ms = every 4 s

-- Status-line cadence, in polls. This is the line that makes a silent run
-- diagnosable, so keep it well inside the length of a normal battle.
local HEARTBEAT_EVERY_N_POLLS = 20     -- 20 x 250 ms = every 5 s
local TICK_EVERY_N_POLLS      = 40     -- phase-agnostic proof of life, every 10 s

local MAX_ABILITIES_TO_LOG = 14

local LOG_TAG  = "[zz_test_deadly_onslaught] "
local LOG_FILE = "zz_test_deadly_onslaught_log.txt"   -- lands in the game install folder


-- ============================================================================
-- 2. BOOKKEEPING - state remembered between polls
-- ============================================================================

local tracked_units = nil              -- the watch list, built once contact starts
local target_key_by_unit = {}          -- ui id -> the ability key found on that unit
local last_fired_at_tick = {}          -- per unit id: the attempt floor
local activated_at_tick = {}           -- per unit id: set when the engine accepted one
local tick_count = 0                   -- our battle clock, in polls
local MIN_TICKS_BETWEEN_FIRES = (MIN_SECONDS_BETWEEN_FIRES * 1000) / POLL_MS
local ACTIVATION_BRAKE_TICKS  = (ABILITY_RECHARGE_SECONDS * 1000) / POLL_MS


-- ============================================================================
-- 3. LOGGING - tagged so one search finds every line
--    a) our own file  -> written with io.open, needs NO engine logging switch,
--       and is the file to read afterwards. Primary.
--    b) ModLog()      -> lua_mod_log.txt, provided by the mod loader. Also proves
--       the loader executed this file at all.
--    c) out()         -> engine script log; GATED OFF by default (needs an empty
--       script/enable_console_logging in the pack). Bonus channel only.
-- ============================================================================

local log_handle = nil
local file_logging_off = false

local function write_to_file(line)
	if file_logging_off then return end

	if log_handle == nil then
		local ok, handle = pcall(io.open, LOG_FILE, "a")   -- append: keep prior runs
		if not ok or handle == nil then
			file_logging_off = true
			return
		end
		log_handle = handle
		log_handle:write("\n======== new battle session ========\n")
	end

	pcall(function()      -- a diagnostic that throws is worse than no diagnostic
		log_handle:write(line .. "\n")
		log_handle:flush()
	end)
end

local function log(message)
	local line = LOG_TAG .. tostring(message)

	write_to_file(line)

	if ModLog ~= nil then
		pcall(ModLog, line)
	end

	out(line)
end


-- ============================================================================
-- 4. FINDING THE ABILITY ON A UNIT
-- ============================================================================

local function scan_unit_abilities(unit)
	local owned = unit:owned_special_abilities()
	local matching_key = nil
	local all_keys = {}

	if owned == nil then
		return nil, all_keys
	end

	for _, owned_key in pairs(owned) do
		all_keys[#all_keys + 1] = owned_key

		for _, wanted_key in ipairs(ABILITY_KEYS) do
			if owned_key == wanted_key then
				matching_key = owned_key
			end
		end
	end

	return matching_key, all_keys
end


-- ============================================================================
-- 5. MEASURING THE CONDITION
--    Return a table of measurements rather than a bare boolean, and log them:
--    a condition built on an inferred signal can only be tuned from real numbers.
--
--    Note what is NOT here. ordered_position() is documented as "the destination
--    while moving, the unit's current position while attacking", but in practice
--    it tracks distance travelled since the order was given - gating on it blocks
--    every genuine charge while looking correct. The real attack-versus-move
--    signal is simply "does the unit have a target at all".
-- ============================================================================

local function measure_charge(unit)
	local m = {
		fast = unit:is_moving_fast(),
		melee = unit:is_in_melee(),
		has_target = false,
		target_dist = -1,     -- metres to the target unit; -1 = unknown
		ttc = -1,             -- estimated seconds until contact; -1 = unknown
		charging = false,
	}

	local ok_target, target = pcall(function() return unit:current_target() end)
	if ok_target and target ~= nil then
		m.has_target = true
	end

	if m.has_target then
		local ok_dist, dist = pcall(function() return unit:unit_distance(target) end)
		if ok_dist and dist ~= nil then
			m.target_dist = dist
		end

		if m.target_dist >= 0 then
			local ok_speed, speed = pcall(function() return unit:fast_speed() end)
			if ok_speed and speed ~= nil and speed > 0 then
				m.ttc = m.target_dist / speed
			end
		end
	end

	if m.fast and not m.melee and m.has_target then
		local enough_run_up = true
		local close_enough  = true
		if m.target_dist >= 0 then
			enough_run_up = (m.target_dist >= CHARGE_MIN_DISTANCE_M)
			close_enough  = (m.target_dist <= CHARGE_MAX_DISTANCE_M)
		end

		local soon_enough = true
		if m.ttc >= 0 then
			soon_enough = (m.ttc <= CHARGE_TIME_TO_CONTACT_S)
		end

		m.charging = enough_run_up and close_enough and soon_enough
	end

	return m
end


-- ============================================================================
-- 6. WATCH LIST - and the diagnostic that says whether the ability exists at all
-- ============================================================================

local function rebuild_unit_list()
	tracked_units = {}

	local sunits = bm:get_scriptunits_for_local_players_army()
	if sunits == nil then
		log("no units returned yet (army not on the field?)")
		return
	end

	local total = sunits:count()
	log("watching " .. tostring(total) .. " unit(s) in the local player's army")

	local carriers = 0

	for i = 1, total do
		local script_unit = sunits:item(i)
		tracked_units[#tracked_units + 1] = script_unit

		local unit = script_unit.unit
		local ui_id = unit:unique_ui_id()
		local matching_key, all_keys = scan_unit_abilities(unit)

		target_key_by_unit[ui_id] = matching_key
		if matching_key ~= nil then carriers = carriers + 1 end

		-- This line is the whole point: a run that never fires still reports whether
		-- the unit had the ability at all, so the tester knows which half failed.
		log("  unit type '" .. tostring(unit:type()) .. "'"
			.. ", ui id " .. tostring(ui_id)
			.. ", has " .. tostring(#all_keys) .. " abilities"
			.. ", owns the target ability = " .. tostring(matching_key ~= nil)
			.. (matching_key and (" as '" .. matching_key .. "'") or ""))

		-- Dump the keys too: if the target is absent, this says what to retarget to
		-- without another test run.
		for j = 1, #all_keys do
			if j <= MAX_ABILITIES_TO_LOG then
				log("      ability: " .. tostring(all_keys[j]))
			end
		end
	end

	log("ability carriers found: " .. tostring(carriers))
end


-- ============================================================================
-- 7. HEARTBEAT - proof the timer is alive, and what every unit is doing
-- ============================================================================

local function log_heartbeat()
	-- Any call NOT yet observed running in the real game goes inside pcall.
	local phase_name = "?"
	local ok, value = pcall(function() return bm:get_current_phase_name() end)
	if ok then phase_name = value end

	local parts = {
		"hb t=" .. tostring(tick_count),
		"phase=" .. tostring(phase_name),
		"conflict=" .. tostring(bm:is_conflict_phase()),
	}

	if tracked_units ~= nil then
		for i = 1, #tracked_units do
			local script_unit = tracked_units[i]
			local unit = script_unit and script_unit.unit

			if unit ~= nil then
				local ui_id = unit:unique_ui_id()
				local m = measure_charge(unit)

				-- tostring() everything: Lua 5.1 string.format does not coerce
				-- booleans, and %d on a float is a risk.
				parts[#parts + 1] = string.format(
					"%s#%s alive=%s fast=%s melee=%s tgt=%s dist=%.1fm eta=%.1fs",
					tostring(unit:type()), tostring(ui_id),
					tostring(unit:number_of_men_alive()),
					tostring(m.fast), tostring(m.melee), tostring(m.has_target),
					m.target_dist, m.ttc)
			end
		end
	end

	log(table.concat(parts, " | "))
end


-- ============================================================================
-- 8. ACTIVATION
--    The call shape is the engine's own, taken from its shipped call sites:
--        sunit.uc:perform_special_ability("<ability key>", sunit.unit)
--    Ability key FIRST, target unit SECOND, and the target is REQUIRED - every
--    vendor call site passes one, and for a self-buff it is the unit itself.
--    Omitting it fails with "battle.unit expected, got no value"; swapping the
--    arguments fails with "bad self ... expecting special ability name (string)".
--
--    _q is the queued variant: it waits for the unit's current order to finish,
--    so for a "while charging" trigger it may never fire during the movement you
--    are watching. The ground-targeted variant is INVALID for a self-buff and
--    leaves the unit holding a targeting cursor.
-- ============================================================================

local function attempt_activation(script_unit, unit, ability_key, reason, ui_id)
	local uc = script_unit.uc
	if uc == nil then
		log("  no controller handle (.uc is nil) - cannot order the ability")
		return
	end

	-- Log the attempt BEFORE the call: a line written afterwards disappears
	-- exactly when the call fails, which is when it is worth the most.
	log("ATTEMPT " .. ability_key .. " on '" .. tostring(unit:type())
		.. "' ui id " .. tostring(ui_id) .. " | reason: " .. tostring(reason))

	local ok_call, err_call = pcall(function()
		uc:perform_special_ability(ability_key, unit)
	end)

	if ok_call then
		activated_at_tick[ui_id] = tick_count
		log("  perform_special_ability(key, unit) : ACCEPTED")
		log("  next attempt for this unit in "
			.. tostring(ABILITY_RECHARGE_SECONDS) .. " s")
	else
		local text = tostring(err_call)
		log("  perform_special_ability(key, unit) : REJECTED - " .. text)
		-- "does not support this special ability" is what the engine says while
		-- the ability is active or on cooldown, so treat it as evidence that an
		-- earlier activation worked rather than as a failure.
		if string.find(text, "does not support this special ability") ~= nil then
			activated_at_tick[ui_id] = tick_count
		end
	end

	-- Hand the unit back: an issued order implicitly takes control, which greys
	-- the unit card if it is never released.
	pcall(function() uc:release_control() end)
end


-- ============================================================================
-- 9. THE POLL BODY
-- ============================================================================

local function poll_body()
	tick_count = tick_count + 1

	-- Proof of life: if this line is in the log, the repeating timer works.
	if tick_count == 1 then
		log("poll is running (first tick)")
	end

	-- Phase-agnostic cadence: a run that dies early must still be provable as
	-- "the timer stopped" rather than "nothing ever happened".
	if (tick_count % TICK_EVERY_N_POLLS) == 0 then
		log("tick " .. tostring(tick_count)
			.. " | phase=" .. tostring(bm:get_current_phase_name())
			.. " | conflict=" .. tostring(bm:is_conflict_phase())
			.. " | tracked=" .. (tracked_units ~= nil and tostring(#tracked_units) or "nil"))
	end

	if (tick_count % HEARTBEAT_EVERY_N_POLLS) == 0 then
		log_heartbeat()
	end

	-- Nothing to do during deployment or after the battle is decided.
	if not bm:is_conflict_phase() then
		return
	end

	-- First poll after contact: build the list, then start work next time round.
	if tracked_units == nil then
		rebuild_unit_list()
		return
	end

	local do_redetect = (tick_count % REDETECT_EVERY_N_POLLS) == 0

	for i = 1, #tracked_units do
		local script_unit = tracked_units[i]
		local unit = script_unit and script_unit.unit

		if unit ~= nil and unit:number_of_men_alive() > 0 then
			local ui_id = unit:unique_ui_id()
			local ability_key = target_key_by_unit[ui_id]

			-- Not found yet: keep looking in case it attaches later than deployment.
			if ability_key == nil and do_redetect then
				local found = scan_unit_abilities(unit)
				if found ~= nil then
					target_key_by_unit[ui_id] = found
					ability_key = found
					log("late find: '" .. tostring(unit:type()) .. "' ui id "
						.. tostring(ui_id) .. " owns " .. tostring(found))
				end
			end

			-- Ask before acting: an illegal order raises a script error. This is a
			-- legality gate only - it does not reflect the cooldown.
			if ability_key ~= nil
				and unit:can_perform_special_ability(ability_key) then

				local m = measure_charge(unit)
				local reason = nil

				if FIRE_ON_CHARGE and m.charging then
					reason = string.format("charging (dist=%.1fm eta=%.1fs)",
						m.target_dist, m.ttc)
				elseif FIRE_ON_MELEE and m.melee then
					reason = "in melee"
				end

				if reason ~= nil then
					local last_attempt = last_fired_at_tick[ui_id] or -999999
					local last_success = activated_at_tick[ui_id] or -999999

					-- Two brakes: a floor between attempts, and the ability's own
					-- recharge time once the engine has accepted one.
					if (tick_count - last_attempt) >= MIN_TICKS_BETWEEN_FIRES
						and (tick_count - last_success) >= ACTIVATION_BRAKE_TICKS then

						last_fired_at_tick[ui_id] = tick_count
						attempt_activation(script_unit, unit, ability_key, reason, ui_id)
					end
				end
			end
		end
	end
end


-- ============================================================================
-- 10. THE POLL - wrapped, because one raising callback kills every timer
--     The battle's script timers all ride on a single engine timer whose driver
--     loops the pending callbacks and re-arms itself only after that loop
--     finishes. An error escaping THIS body therefore does not merely skip a
--     tick: every repeating callback in the battle goes silent for the rest of
--     the fight, which reads as "the trigger never fired". Wrap the whole body,
--     not just the individual engine calls inside it.
-- ============================================================================

local poll_errors = 0

local function poll()
	local ok, err = pcall(poll_body)
	if not ok then
		poll_errors = poll_errors + 1
		-- Counter-capped: a recurring fault stays visible without flooding the log.
		if poll_errors <= 3 or (poll_errors % 40) == 0 then
			log("POLL ERROR #" .. tostring(poll_errors) .. " (poll continues): "
				.. tostring(err))
		end
	end
end


-- ============================================================================
-- 11. REGISTRATION
--     The file BODY executes when the loader loads it, and bm already exists by
--     then, so registering here is correct. Do not wait for a global function
--     named after the file: that convention is the campaign-side loader's only.
--
--     Every phase callback is wrapped too: the phase dispatcher calls them in a
--     loop, so an error out of one starves every callback registered after it.
-- ============================================================================

bm:register_phase_change_callback("Deployed", function()
	local ok, err = pcall(function()
		log("combat phase started - building watch list")
		rebuild_unit_list()
	end)
	if not ok then log("deployed callback failed: " .. tostring(err)) end
end)

bm:repeat_callback(poll, POLL_MS, "zz_test_deadly_onslaught_poll")

-- Log-only phase watcher. The dispatcher emits this event unconditionally, so
-- its absence means phase changes are not reaching script at all - which is the
-- cleanest signal that something else in the file broke the engine's callbacks.
-- Keep it log-only: UI work here runs inside the phase dispatch.
core:add_listener(
	"zz_test_deadly_onslaught_phase_watch",
	"ScriptEventBattlePhaseChanged",
	function(context) return true end,
	function(context) log("phase change seen: " .. tostring(context.string)) end,
	true
)

log("loaded. Polling every " .. tostring(POLL_MS) .. " ms"
	.. " | fire on charge = " .. tostring(FIRE_ON_CHARGE)
	.. " | fire on melee = " .. tostring(FIRE_ON_MELEE))
for _, wanted_key in ipairs(ABILITY_KEYS) do
	log("  accepting ability: " .. wanted_key)
end
