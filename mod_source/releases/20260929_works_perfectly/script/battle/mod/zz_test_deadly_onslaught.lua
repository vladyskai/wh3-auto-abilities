--------------------------------------------------------------------------------
-- Route 2 test case: automatically fire ONE ability, under a chosen condition.
--
-- Target ability : Deadly Onslaught
--                  database key = wh_main_character_abilities_deadly_onslaught
--                  (self-buff, 31 s duration, 90 s cooldown, unlimited uses,
--                   no magic cost, no usage restrictions of any kind,
--                   engine's own AI tag = augment_charge_self)
--
-- WHICH UNIT HAS IT
--   In skirmish/custom battles an ability comes from the unit's innate list
--   (db table: land_units_to_unit_abilites_junctions), not from a skill.
--   The Empire Captain does NOT have Deadly Onslaught there - which is why it
--   never showed up in skirmish. Boris Todbringer DOES, on all four of his
--   unit variants:
--       wh3_dlc29_emp_cha_boris_todbringer_toddy_0 ... _3
--   So this test works with Boris in skirmish, and needs no change of key.
--
-- WHAT THIS RUN IS FOR - it answers four questions in one battle:
--     1. Does a script in script/battle/mod/ run in this battle type?
--     2. Can we detect, per unit, whether it owns a given ability?
--     3. Can we make it fire that ability with no click from the player?
--     4. What happens to our control of that unit while it fires?
--
-- WHERE THIS FILE GOES
--   script/battle/mod/zz_test_deadly_onslaught.lua  inside the .pack file.
--   That folder is auto-loaded by the game's own mod loader
--   (script/_lib/lib_mod_loader.lua) in every battle. No vanilla file is edited.
--
-- WHERE THE OUTPUT GOES
--   zz_test_deadly_onslaught_log.txt, in the game's install folder (next to
--   Warhammer3.exe). Written directly by this script, so it does not depend on
--   any logging setting. Search it for "zz_test_deadly_onslaught".
--------------------------------------------------------------------------------


-- ============================================================================
-- 1. SETTINGS - the only things you normally touch
-- ============================================================================

-- Ability keys we will fire. The first is the one Boris Todbringer carries.
-- The second is a legacy duplicate definition that currently sits on no unit,
-- kept as harmless insurance in case a future patch assigns it.
local ABILITY_KEYS = {
	"wh_main_character_abilities_deadly_onslaught",
	"wh_dlc03_character_abilities_deadly_onslaught",
}

-- Which situations count as "fire now".
-- Round 5 ran with BOTH on (deliberately, to get a positive result). You saw it
-- fire while merely running and while already fighting, which is exactly what
-- that configuration asked for. Now it is tightened to charging only.
local FIRE_ON_CHARGE = true
local FIRE_ON_MELEE  = false   -- switch on only for testing

-- A charge is an ATTACK order on an enemy that is about to CONNECT - not simply
-- "moving fast", and not the instant the attack order is given. The engine
-- exposes no "is charging", so it is inferred from five signals:
--
--   1. is_moving_fast()      - the unit is running (necessary, not sufficient)
--   2. not is_in_melee()     - it has not made contact yet
--   3. current_target()      - it has an enemy unit as its target
--   4. ordered_position()    - the documentation: "if the unit is attacking, as
--                              opposed to moving, then this will return the
--                              current position of the unit". So position() and
--                              ordered_position() are near-equal while charging
--                              a unit and far apart while walking to a spot.
--                              This is what separates a charge from a run.
--   5. distance to the target, and the estimated time until contact - so the
--      ability is spent on the charge that is about to land, not on a charge
--      ordered from the far side of the battlefield.
--
-- ROUND 7 CORRECTION - signal 4 DOES NOT WORK.
-- The documentation claims that while the unit is ATTACKING, ordered_position()
-- returns its current position. The round-7 log disproves it: during a charge
-- the gap grew steadily from 17 m to 322 m, tracking how far the unit had
-- travelled since the order was given. So it measures "how long ago you
-- clicked", not "is this an attack". It blocked every genuine charge and passed
-- only orders given at close range - which is exactly what you saw. It is now
-- logged for diagnostics only and takes NO part in the decision. The real
-- attack-versus-move signal is simply "does the unit have a target at all".
local CHARGE_ORDER_TOLERANCE_M = 8      -- diagnostics only, NOT a gate
local CHARGE_MIN_DISTANCE_M    = 12     -- a charge needs a run-up
local CHARGE_MAX_DISTANCE_M    = 60     -- ...but not the length of the map
local CHARGE_TIME_TO_CONTACT_S = 4      -- fire when impact is this close

-- After an accepted activation, wait this long before trying again. This is the
-- ability's own recharge_time from the database - not a guess.
local ABILITY_RECHARGE_SECONDS = 90

-- How often, in milliseconds, we look at the battlefield. 250 ms = 4x a second.
local POLL_MS = 250

-- Safety brake: never fire the same unit twice within this many seconds.
-- The ability's own cooldown is 90 s; this only protects us if the game's
-- "can I use this?" check turns out not to include the cooldown.
local MIN_SECONDS_BETWEEN_FIRES = 20

-- How often to re-check a unit we have not yet found the ability on, in polls.
-- Cheap insurance: if abilities are not all attached at the moment we first
-- look, we pick them up a few seconds later instead of failing silently.
local REDETECT_EVERY_N_POLLS = 16    -- 16 x 250 ms = every 4 seconds

-- How often to write one compact status line, in polls. 20 x 250 ms = every 5 s.
-- This is what makes a silent run diagnosable: it proves the poll is alive and
-- records the battle phase plus what every watched unit is doing.
local HEARTBEAT_EVERY_N_POLLS = 20

-- Explicitly take control of the unit before ordering it.
-- OFF by default: the documentation says issuing an order takes control anyway,
-- and an explicit takeover is a candidate cause of the player's current order
-- being cancelled. Leave it off unless we find we need it.
local TAKE_CONTROL_FIRST = false

-- Hand the unit back to the player after the attempt.
-- ON by default so the unit's card does not stay greyed out afterwards.
local RELEASE_CONTROL_AFTER = true

-- How many of each unit's ability keys to write to the log.
local MAX_ABILITIES_TO_LOG = 14


-- ============================================================================
-- 2. BOOKKEEPING
-- ============================================================================

local tracked_units = nil                 -- units we watch
local target_key_by_unit = {}
local our_unit_ui_id = nil      -- the ui id of the unit whose ability we manage             -- ui id -> the ability key found on it
local last_fired_at_tick = {}             -- when we last fired, per unit
local pending_verify = nil                -- a deferred "did it take effect?" check
local tick_count = 0                      -- our battle clock
local MIN_TICKS_BETWEEN_FIRES = (MIN_SECONDS_BETWEEN_FIRES * 1000) / POLL_MS


-- ============================================================================
-- 3. LOGGING
--    a) our own file (primary - always works)
--    b) ModLog(), the mod loader's log, if it exists
--    c) out(), the game's own script log, if logging happens to be enabled
-- ============================================================================

local LOG_TAG  = "[zz_test_deadly_onslaught] "
local LOG_FILE = "zz_test_deadly_onslaught_log.txt"

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
		log_handle:write("\n======== new battle session ========\n")
	end

	pcall(function()
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
-- 4. FIND THE ABILITY ON A UNIT
--    Returns:
--      matching_key : the ability key this unit owns, or nil
--      all_keys     : every ability key the unit owns (for the log)
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
-- 5. IS IT ACTUALLY CHARGING?
--    A charge is an ATTACK order on an enemy that is about to connect.
--    Returns a table of measurements, which the log prints, so every decision
--    can be audited from real numbers.
--
--    charging = fast AND not melee AND has a target AND the order is an attack
--               (not a move) AND the target is close enough that impact is
--               within CHARGE_TIME_TO_CONTACT_S seconds.
-- ============================================================================

local function measure_charge(unit)
	local m = {
		fast = unit:is_moving_fast(),
		melee = unit:is_in_melee(),
		has_target = false,
		order_gap = -1,      -- position() vs ordered_position(); -1 = unmeasurable
		target_dist = -1,    -- metres to the target unit; -1 = unknown
		ttc = -1,            -- estimated seconds until contact; -1 = unknown
		charging = false,
	}

	local ok_target, target = pcall(function() return unit:current_target() end)
	if ok_target and target ~= nil then
		m.has_target = true
	end

	local ok_gap, gap = pcall(function()
		return unit:position():distance(unit:ordered_position())
	end)
	if ok_gap and gap ~= nil then
		m.order_gap = gap
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
		-- Having a target at all is the attack-versus-move signal: a move
		-- order sets none. (ordered_position() is NOT used here - round 7
		-- proved it tracks time-since-order, not attack-versus-move.)

		-- A real charge has a run-up: far enough that the unit actually
		-- builds speed, close enough that the impact is imminent.
		local enough_run_up = true
		if m.target_dist >= 0 then
			enough_run_up = (m.target_dist >= CHARGE_MIN_DISTANCE_M)
		end

		local close_enough = true
		if m.target_dist >= 0 then
			close_enough = (m.target_dist <= CHARGE_MAX_DISTANCE_M)
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
-- 6. BUILD THE WATCH LIST (and say out loud what we found)
--    bm:get_scriptunits_for_local_players_army() gives us "script units": each
--    wraps the unit itself (.unit) plus a controller that can give it orders
--    (.uc). The ability dump is what makes a failed run diagnosable: it shows
--    exactly which abilities each unit has, so we can retarget without guessing.
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
		if matching_key ~= nil then
			carriers = carriers + 1
		end
		if matching_key ~= nil and our_unit_ui_id == nil then
			our_unit_ui_id = ui_id
		end

		log("  unit '" .. tostring(unit:type()) .. "'"
			.. " ui id " .. tostring(ui_id)
			.. " | " .. tostring(#all_keys) .. " abilities"
			.. " | owns Deadly Onslaught = " .. tostring(matching_key ~= nil)
			.. (matching_key and (" as '" .. matching_key .. "'") or "")
			.. " | usable right now = "
			.. tostring(unit:can_perform_special_ability(ABILITY_KEYS[1])))

		for j = 1, #all_keys do
			if j <= MAX_ABILITIES_TO_LOG then
				log("      ability: " .. tostring(all_keys[j]))
			end
		end
	end

	-- Make the success case impossible to miss when reading the log.
	log("ability carriers found: " .. tostring(carriers))
end


-- ============================================================================
-- 5b. THE ON/OFF SWITCH AND ITS BUTTON
--     One boolean, flipped by a small button docked in the battle order bar.
--
--     WHERE THIS CODE MAY RUN - learned the hard way over rounds 9-15:
--       * creating the component from a model timer or from a phase callback has
--         twice killed the battle's model timer (and with it the poll that
--         watches for charges) - rounds 9, 10 and 13;
--       * painting it from a timer silently does nothing, so the button keeps the
--         template's placeholder icon - rounds 11 and 14;
--       * painting from a phase callback, or from a click handler, works - the
--         icon was correct in rounds 9 and 13, and clicks repainted it correctly.
--     So: create and paint in the phase callbacks and the click handler. The poll is
--     registered once at load and never touched again (see the note at rearm's old
--     place in section 9): removing and re-adding a model timer is what broke the
--     trigger in round 17.
-- ============================================================================

local AUTO_ENABLED = false         -- <- the switch itself: OFF, so the keyboard test shows the
                                   --    change (press the key -> armed -> the icon repaints)
                                   --    events the engine declares and the battle produced zero
                                   --    right-click and zero double-click events, so nothing can
                                   --    flip this from inside the game. - rounds 15-25 measured
                                   --    that no click in battle can flip it (right-clicks are never
                                   --    reported by the engine, left-clicks belong to the game's own
                                   --    actions). The double-click listener below can still flip it
                                   --    if the engine ever reports that gesture.

-- The switch itself. Everything that used to make a button for it - the template clone,
-- the docking, the two icon files, the bar-width fiddling and the click listener - has been
-- removed: the control is a right-click on the ability's own icon (section 8b).

-- The poll's name, used once, where it is registered.
local POLL_NAME = "zz_test_deadly_onslaught_poll"


-- ============================================================================
-- 6. HEARTBEAT
--    One compact line every few seconds: the battle phase, and for each watched
--    unit whether it is alive, running/charging, in melee, and able to use the
--    ability. If a run fires nothing, this is what explains why.
-- ============================================================================

local function log_heartbeat()
	-- The phase name is the one call here I have not yet seen run inside the
	-- real game, so it is guarded: a failure must not break the poll loop.
	local phase_name = "?"
	local ok, value = pcall(function() return bm:get_current_phase_name() end)
	if ok then
		phase_name = value
	end

	local parts = {
		"hb t=" .. tostring(tick_count),
		"phase=" .. tostring(phase_name),
		"conflict=" .. tostring(bm:is_conflict_phase()),
		"auto=" .. (AUTO_ENABLED and "ON" or "OFF"),
	}

	if tracked_units ~= nil then
		for i = 1, #tracked_units do
			local script_unit = tracked_units[i]
			local unit = script_unit and script_unit.unit

			if unit ~= nil then
				local ui_id = unit:unique_ui_id()
				local m = measure_charge(unit)

				parts[#parts + 1] = string.format(
					"%s#%s alive=%s fast=%s melee=%s tgt=%s gap=%.1fm dist=%.1fm eta=%.1fs",
					tostring(unit:type()),
					tostring(ui_id),
					tostring(unit:number_of_men_alive()),
					tostring(m.fast),
					tostring(m.melee),
					tostring(m.has_target),
					m.order_gap,
					m.target_dist,
					m.ttc)
			end
		end
	end

	log(table.concat(parts, " | "))
end


-- ============================================================================
-- 7. ACTIVATION
--    Resolved from the game's OWN script files, not from documentation:
--
--      script/battle/quest_battles/tamurkhan/kayzk/battle_script.lua
--        if sunit.unit:can_perform_special_ability("<key>") then
--            sunit.uc:perform_special_ability("<key>", sunit.unit)
--        end
--
--      script/benchmarks/battle_benchmark/battle_benchmark.lua
--        --- Khorne Lord Buffing Himself ---
--        sunit_kho_01.uc:perform_special_ability("<key>", sunit_kho_01.unit)
--
--    So: ability key FIRST, target unit SECOND, and the target is REQUIRED.
--    For a self-buff the target is the unit itself. Every one of the 26 vanilla
--    call sites passes a target; none omits it.
--
--    That explains the round 3 failure (we omitted the target) and the round 4
--    failures (we had the arguments the other way round, which the engine
--    reports as "bad self ... expecting special ability name (string)").
--
--    Round 3's ground-targeted variant is GONE - it is what left the unit
--    holding a targeting cursor with a crossed-out ability icon.
--
--    Success is still judged objectively: a real activation starts the cooldown,
--    so can_perform_special_ability must flip to false.
-- ============================================================================

-- How long after an accepted activation to leave the ability alone, in ticks.
local ACTIVATION_BRAKE_TICKS = (ABILITY_RECHARGE_SECONDS * 1000) / POLL_MS
local activated_at_tick = {}          -- ui id -> tick of the last accepted activation


-- ============================================================================
-- 7c. ACTIVATION
--     Resolved from the game's OWN script files, not from documentation:
--
--       script/battle/quest_battles/tamurkhan/kayzk/battle_script.lua
--         if sunit.unit:can_perform_special_ability("<key>") then
--             sunit.uc:perform_special_ability("<key>", sunit.unit)
--         end
--
--       script/benchmarks/battle_benchmark/battle_benchmark.lua
--         --- Khorne Lord Buffing Himself ---
--         sunit_kho_01.uc:perform_special_ability("<key>", sunit_kho_01.unit)
--
--     Ability key FIRST, target unit SECOND, target REQUIRED. All 26 vanilla
--     call sites pass a target; none omits it. For a self-buff the target is the
--     unit itself. This is the call that worked in round 5.
--
--     A NOTE ON DETECTING SUCCESS
--     can_perform_special_ability() does NOT report the cooldown. Round 5 proved
--     that: the call was accepted and the ability fired, yet this check still
--     returned true. What the engine does say, once the ability is active, is:
--
--        error: unit '1' does not support this special ability
--
--     So that error is treated here as evidence that the ability is currently
--     active - i.e. that an earlier activation worked.
-- ============================================================================

local function attempt_activation(script_unit, unit, ability_key, reason, ui_id)
	log("ATTEMPT " .. ability_key .. " on '" .. tostring(unit:type())
		.. "' ui id " .. tostring(ui_id) .. " | reason: " .. reason)

	local uc = script_unit.uc

	if uc == nil then
		log("  STOP: script_unit.uc is nil - there is no controller to order")
		return
	end

	if TAKE_CONTROL_FIRST then
		local ok_take, err_take = pcall(function() uc:take_control() end)
		log("  take_control            : ok=" .. tostring(ok_take)
			.. (ok_take and "" or ("  ERROR: " .. tostring(err_take))))
	end

	local _, can_before = pcall(function()
		return unit:can_perform_special_ability(ability_key)
	end)
	log("  can_perform before      : " .. tostring(can_before))

	-- The call the game itself uses.
	local ok_call, err_call = pcall(function()
		uc:perform_special_ability(ability_key, unit)
	end)

	if ok_call then
		activated_at_tick[ui_id] = tick_count
		log("  perform_special_ability(key, unit) : ACCEPTED")
		log("  next attempt for this unit in " .. tostring(ABILITY_RECHARGE_SECONDS) .. " s")
	else
		local err_text = tostring(err_call)
		log("  perform_special_ability(key, unit) : REJECTED - " .. err_text)

		if string.find(err_text, "does not support this special ability") ~= nil then
			log("  -> engine says the unit cannot use it right now, which is what it")
			log("     says while the ability is active/on cooldown. Treating that as")
			log("     evidence an earlier activation worked.")
			activated_at_tick[ui_id] = tick_count
		end
	end

	if RELEASE_CONTROL_AFTER then
		local ok_release, err_release = pcall(function() uc:release_control() end)
		log("  release_control         : ok=" .. tostring(ok_release)
			.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
	end
end


-- ============================================================================
-- 8. THE POLL - runs every POLL_MS milliseconds for the whole battle
-- ============================================================================

local function poll_body()
	tick_count = tick_count + 1

	-- Proof of life: if this line is in the log, the repeating timer works.
	if tick_count == 1 then
		log("poll is running (first tick)")
	end

	-- The switch is flipped by right-clicking the ability icon in battle - see the
	-- listener at the bottom of the file. No UI component is created anywhere in
	-- this mod: doing so from a timer or a phase callback is what broke the model
	-- timer in rounds 9-14.

	-- Say something every 10 s whatever the phase, so a silent run is provable
	-- and so we can see whether the timer is still being called at all.
	if (tick_count % 40) == 0 then
		log("tick " .. tostring(tick_count)
			.. " | phase=" .. tostring(bm:get_current_phase_name())
			.. " | conflict=" .. tostring(bm:is_conflict_phase())
			.. " | auto=" .. (AUTO_ENABLED and "ON" or "OFF")
			.. " | tracked=" .. (tracked_units ~= nil and tostring(#tracked_units) or "nil"))
	end

	if (tick_count % HEARTBEAT_EVERY_N_POLLS) == 0 then
		log_heartbeat()
	end

	-- Deferred "did it take effect?" check, for the case where a call was
	-- accepted but the ability did not go on cooldown immediately.
	if pending_verify ~= nil and tick_count >= pending_verify.at_tick then
		local pv = pending_verify
		pending_verify = nil

		if tracked_units ~= nil then
			for i = 1, #tracked_units do
				local u = tracked_units[i].unit
				if u ~= nil and u:unique_ui_id() == pv.ui_id then
					local _, still = pcall(function()
						return u:can_perform_special_ability(pv.key)
					end)
					log("  verify 1 s later        : can_perform = " .. tostring(still))
				end
			end
		end
	end

	-- Nothing to do during deployment or after the battle is decided.
	if not bm:is_conflict_phase() then return end

	-- First poll after contact: build the list.
	if tracked_units == nil then
		rebuild_unit_list()
		return
	end

	local do_redetect = (tick_count % REDETECT_EVERY_N_POLLS) == 0

	for i = 1, #tracked_units do
		local script_unit = tracked_units[i]
		local unit = script_unit and script_unit.unit

		-- Only look at units still alive on the field.
		if unit ~= nil and unit:number_of_men_alive() > 0 then
			local ui_id = unit:unique_ui_id()
			local ability_key = target_key_by_unit[ui_id]

			-- Not found on this unit yet: keep looking every few seconds in
			-- case the ability is granted slightly later than deployment.
			if ability_key == nil and do_redetect then
				local found = scan_unit_abilities(unit)
				if found ~= nil then
					target_key_by_unit[ui_id] = found
					ability_key = found
					log("late find: '" .. tostring(unit:type()) .. "' ui id "
						.. tostring(ui_id) .. " owns " .. tostring(found))
				end
			end

			-- The switch: when it is off, nothing is fired at all.
			if AUTO_ENABLED and ability_key ~= nil then
				-- The game's own gate, exactly as vanilla does it: only order
				-- an ability the unit can actually perform right now.
				if unit:can_perform_special_ability(ability_key) then

					local m = measure_charge(unit)

					local reason = nil

					if FIRE_ON_CHARGE and m.charging then
						reason = string.format(
							"charging (gap=%.1fm dist=%.1fm eta=%.1fs)",
							m.order_gap, m.target_dist, m.ttc)
					elseif FIRE_ON_MELEE and m.melee then
						reason = "in melee"
					end

					if reason ~= nil then
						local last_attempt = last_fired_at_tick[ui_id] or -999999
						local last_success = activated_at_tick[ui_id] or -999999

						-- Two brakes: a floor between attempts, and the ability's
						-- own recharge time once it has actually fired.
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
end


-- An error escaping a timer callback does not merely skip that tick: the battle
-- model's timer driver aborts before re-arming itself, which kills EVERY
-- repeating callback in the battle for the rest of the fight
-- (lib_timer_manager.lua, "timer_manager_battle_callback"). So the body is
-- wrapped, and the first few errors are logged rather than swallowing the battle.
local poll_errors = 0

local function poll()
	local ok, err = pcall(poll_body)
	if not ok then
		poll_errors = poll_errors + 1
		if poll_errors <= 3 or (poll_errors % 40) == 0 then
			log("POLL ERROR #" .. tostring(poll_errors) .. " (poll continues): "
				.. tostring(err))
		end
	end
end


-- ============================================================================
-- ============================================================================
-- 8b. THE ABILITY ICON ITSELF: THE RIGHT-CLICK TOGGLE, AND THE FEEDBACK
--
-- The control the player uses is a RIGHT-CLICK ON THE ABILITY'S OWN ICON, and it
-- needs two halves, because the engine only routes a mouse button to a component
-- whose layout declares it (no vanilla layout declares rclick - 0 of the 907 in
-- ui3.pack, which is why right-clicking an ability icon has never done anything):
--
--   * the layout half - shipped in this pack as ui/battle ui/hud_battle.twui.xml
--     and ui/common ui/land_unit_card.twui.xml - adds CA's own
--     ContextEventBroadcaster callback, whose documented trigger list includes
--     rclick, to every component that draws a unit ability icon;
--   * this half listens for whatever comes back and flips the switch.
--
-- The engine's own script says where those icons are: lib_battle_ui.lua's
-- highlight_unit_abilities() walks battle_orders -> orders_parent ->
-- behaviour_parent, takes child 0 of each slot, and calls
-- InterfaceFunction("AbilityKeyForScript") to learn which ability a button shows.
-- ============================================================================

-- Each layout insertion broadcasts its own event name, so the log says which
-- button the player actually pressed.
-- The property the layouts set on the ability button when it is right-clicked, and the last
-- value we saw (so a click fires once, even if clearing the property fails).
-- The switch is flipped by a double-click on the unit card - the engine's own
-- 'Double Click Unit Card' command, which it reports to script (round 22 proved the command
-- channel works; the layout-property channel is dead, every read echoes its own name).

local logged_no_parent = false

local our_buttons = {}          -- component id -> true, for the ability we manage
local our_button = nil          -- the component itself, for the feedback
local our_button_id = nil       -- its component id, for matching the script events
local watch_chain = {}          -- the ability button and its ancestors, all reporting events
local feedback_on = nil         -- last feedback state we applied

-- THE FEEDBACK: a plain image swap on the ability icon. Static - no pulse, no blink.
-- The icon slot is the one the vanilla layout marks with icon_index = 8 (round 21's layout read).
-- Both paths are read off / given by the game, so nothing has to resolve a guessed skin path.
local ICON_INDEX = 8
local ARMED_ICON = "ui\\battle ui\\ability_icons\\wh_main_spell_lil_waaagh_itchy_nuisance.png"
local original_icon = nil          -- whatever the button was showing before we touched it
local original_frame = nil         -- the button frame's own art path (image index 0)

local function read_frame()
	if our_button == nil then return nil end
	local ok, path = pcall(function() return our_button:GetImagePath(0) end)
	if ok then return tostring(path) end
	return nil
end

local function read_icon()
	if our_button == nil then return nil end
	local ok, path = pcall(function() return our_button:GetImagePath(ICON_INDEX) end)
	if ok then return tostring(path) end
	return nil
end

local ARMED_STATE = "inactive"       -- the button's own "greyed out" state
local original_state = nil

-- Round 31: writing to this button (SetState / SetImagePath) invalidates the reference we hold -
-- round 30's log shows every read AFTER the first setter returning function pointers and '0'.
-- So re-acquire it before and after touching it: walk the HUD again looking for our id.
local reacquire_visits = 0

local function reacquire_in(uic, depth)
	if uic == nil or depth > 6 or reacquire_visits > 4000 then return nil end
	reacquire_visits = reacquire_visits + 1
	local ok_i, id = pcall(function() return uic:Id() end)
	if ok_i and our_button_id ~= nil and tostring(id) == tostring(our_button_id) then return uic end
	local ok_n, n = pcall(function() return uic:ChildCount() end)
	if ok_n and type(n) == "number" then
		for i = 0, n - 1 do
			local ok_c, child = pcall(function() return uic:Find(i) end)
			if ok_c and child ~= nil then
				local got = reacquire_in(UIComponent(child), depth + 1)
				if got ~= nil then return got end
			end
		end
	end
	return nil
end

local function reacquire_button()
	if our_button_id == nil then return false end
	reacquire_visits = 0
	local ok, got = pcall(function()
		local hud = UIComponent(core:get_ui_root():Find("hud_battle"))
		if hud == nil then return nil end
		return reacquire_in(hud, 0)
	end)
	if ok and got ~= nil then
		our_button = got
		return true
	end
	return false
end

-- THE BADGE (option B, done right). Rounds 32-33 measured two things: an engine-owned ability
-- button does not draw children, and writing to it rebuilds it. So the badge is created on the
-- button's own ancestor (a plain container, the kind that demonstrably draws components we create),
-- and every UI tick it is MOVED to the ability button's top-right corner from the button's own
-- coordinates. Reading the button is safe; only writing to it is fatal.
local badge = nil
local badge_parent = nil
local BADGE_IMAGE = "ui/zz_auto/auto_badge.png"
local badge_logs = 0
local placed = false
local badge_visible_state = nil
local track = false          -- no computed tracking: the frames of reference do not match
                             -- (round 42). Position is the hand-tuned offset above.
local BADGE_X, BADGE_Y = -865, -209   -- the spot tuned by hand in-game (round 41), used as-is.
                                     -- MINUS is left/up, PLUS is right/down, from the bottom-centre
                                     -- dock of the badge's parent.
local ox, oy = nil, nil   -- the offset we converge on
local last_ex, last_ey = 1e9, 1e9
local badge_stuck = 0
local badge_dead = false

local function create_badge()
	if our_button == nil or badge ~= nil then return end
	-- parent it on hud_battle (the HUD root): a plain container with no LayoutEngine arranging its
	-- children, and its origin is the screen's, so the offset space equals the coordinates the button
	-- reports. Round 37's log showed the previous parent (battle_orders) ignoring SetDockOffset.
	local node = our_button
	for _ = 1, 8 do
		local ok_id, id = pcall(function() return node:Id() end)
		if ok_id and tostring(id) == "hud_battle" then break end
		local ok_p, parent = pcall(function() return node:Parent() end)
		if not ok_p or parent == nil then break end
		local ok_w, wrapped = pcall(function() return UIComponent(parent) end)
		if not ok_w or wrapped == nil then break end
		node = wrapped
	end
	badge_parent = node
	local ok, err = pcall(function()
		badge = UIComponent(badge_parent:CreateComponent("zz_auto_badge", "ui/templates/zz_auto_badge"))
	end)
	if not ok or badge == nil then
		log("badge: CreateComponent failed (" .. tostring(err) .. ")")
		badge = nil
		return
	end
	local ok_id, pid = pcall(function() return badge_parent:Id() end)
	log("badge: created on '" .. tostring(ok_id and pid or "?") .. "' (not on the ability button)")
	pcall(function() badge:SetDockingPoint(0) end)
	pcall(function() badge:Resize(24, 24) end)   -- room for the letter
	-- the bronze "A": our copy of a real vanilla text layout (colour changed in the file),
	-- the string supplied here - SetText exists, SetTextColour does not
	-- the letter carries the look now, so blank the template's own title-bar art underneath it
	for i = 0, 4 do
		pcall(function() badge:SetImagePath("ui/zz_auto/blank.png", i) end)
		local ok_r, rep = pcall(function() return badge:GetImagePath(i) end)
		log("   art slot " .. i .. " -> '" .. tostring(ok_r and rep or "?") .. "'")
	end
	local ok_p = pcall(function() badge:SetText("A") end)
	local ok_g, got = pcall(function() return badge:GetText() end)
	log("   set text ok=" .. tostring(ok_p) .. " engine reports='" .. tostring(ok_g and got or "?") .. "'")
end

local function button_xy()
	if our_button == nil then return nil, nil end
	local ok, a, b = pcall(function() return our_button:Position() end)
	if ok and type(a) == "number" and type(b) == "number" then return a, b end
	return nil, nil
end

local function place_badge()
	if badge == nil then return end

	-- TRACK MODE (round 40): the two numbers below stop being "where on the bar" and become the
	-- constant delta from the ability button's OWN position, recomputed every tick. Tune the delta
	-- once with the console while tracking, and the badge follows that icon - and, per ability, its
	-- own icon, since each badge is created for its own button.
	if track then
		local bx, by = button_xy()
		if bx ~= nil then
			pcall(function() badge:SetDockOffset(bx + BADGE_X, by + BADGE_Y) end)
		end
		return
	end

	if placed then return end
	-- AI General's proven configuration, and nothing cleverer than it: dock the created component to
	-- the BOTTOM-CENTRE of the bar and give it one offset. Round 38 proved the engine both reinterprets
	-- offsets and misreports the component's position, so there is nothing to steer by - one shot, and
	-- the numbers below are the only knobs left.
	pcall(function() badge:SetDockingPoint(8) end)                 -- 8 = bottom-centre
	local ok_o = pcall(function() badge:SetDockOffset(BADGE_X, BADGE_Y) end)
	pcall(function() badge_parent:Layout() end)
	placed = true
	log("badge: placed bottom-centre of '" .. tostring(badge_parent:Id()) .. "' (offset "
		.. tostring(BADGE_X) .. "," .. tostring(BADGE_Y) .. ") ok=" .. tostring(ok_o))
end
local function badge_visible(on)
	if badge == nil then return end
	badge_visible_state = on          -- keep the tick's idea of the state in step with the switch
	local ok = pcall(function() badge:SetVisible(on) end)
	log("   badge visible=" .. tostring(on) .. " ok=" .. tostring(ok))
end

-- ============================================================================
-- 11. THE TUNING HOOK - for the Lua console (Modding Development Tools, shift+F3)
--     Global functions so they can be typed in-game. They close over the badge's
--     position, which matters: nothing in script can read where a created component
--     really is (round 38: Position() reported a place the badge was not), so the
--     human eye is the measuring instrument. That is how the community's own
--     positioning tutorial does it - "test coordinates until the new UIC looks like
--     it's in the right place".
-- ============================================================================
function zz_badge_set(x, y)
	BADGE_X = tonumber(x) or BADGE_X
	BADGE_Y = tonumber(y) or BADGE_Y
	placed = false
	pcall(place_badge)
	local msg = "BADGE offset = " .. tostring(BADGE_X) .. "," .. tostring(BADGE_Y)
		.. " track=" .. tostring(track)
	log(msg)
	return msg
end


function zz_badge_track(on)
	local want = (on == true) or (tostring(on) == "true") or (tonumber(on) == 1)
	if want == track then
		local m = "BADGE already tracking=" .. tostring(track) .. " delta=" .. tostring(BADGE_X)
			.. "," .. tostring(BADGE_Y)
		log(m)
		return m
	end
	-- switching modes CONVERTS the numbers, so the badge stays exactly where it is:
	-- absolute -> delta = subtract the button position; delta -> absolute = add it back.
	local bx, by = button_xy()
	if bx == nil then
		local m = "BADGE mode switch failed: no button position"
		log(m)
		return m
	end
	if want then
		BADGE_X, BADGE_Y = BADGE_X - bx, BADGE_Y - by
	else
		BADGE_X, BADGE_Y = BADGE_X + bx, BADGE_Y + by
	end
	track = want
	placed = false
	pcall(place_badge)
	local m = "BADGE track=" .. tostring(track) .. " now " .. tostring(BADGE_X) .. "," .. tostring(BADGE_Y)
		.. " (button at " .. tostring(bx) .. "," .. tostring(by) .. ")"
	log(m)
	return m
end

function zz_badge_calibrate()
	return zz_badge_track(true)
end

function zz_badge_nudge(dx, dy)
	return zz_badge_set(BADGE_X + (tonumber(dx) or 0), BADGE_Y + (tonumber(dy) or 0))
end

function zz_badge_show()
	if badge == nil then return "badge not created yet" end
	pcall(function() badge:SetVisible(true) end)
	return "badge shown at " .. tostring(BADGE_X) .. "," .. tostring(BADGE_Y)
end

function zz_badge_hide()
	if badge == nil then return "badge not created yet" end
	pcall(function() badge:SetVisible(false) end)
	return "badge hidden"
end

function zz_badge_parent()
	if badge_parent == nil then return "no parent yet" end
	local ok, id = pcall(function() return badge_parent:Id() end)
	local ok2, w = pcall(function() return badge_parent:Width() end)
	local ok3, h = pcall(function() return badge_parent:Height() end)
	local bx, by = button_xy()
	local msg = "BADGE parent=" .. tostring(ok and id or "?") .. " size=" .. tostring(w)
		.. "x" .. tostring(h) .. " offset=" .. tostring(BADGE_X) .. "," .. tostring(BADGE_Y)
		.. " track=" .. tostring(track) .. " button=" .. tostring(bx) .. "," .. tostring(by)
	log(msg)
	return msg
end

local function set_armed_look(on)
	-- Availability is NEVER touched: the ability can always be used by hand.
	-- The state is shown by the badge instead.
	badge_visible(on)
end
local function apply_ability_feedback()
	if our_button == nil then return end
	if feedback_on == AUTO_ENABLED then return end      -- nothing to change

	set_armed_look(AUTO_ENABLED)
	feedback_on = AUTO_ENABLED
end

-- The one place the switch is flipped, whichever control did it.
local function set_auto(value, why)
	AUTO_ENABLED = value
	apply_ability_feedback()        -- the pulse on the ability icon - the only feedback now
	log("TOGGLE (" .. why .. ") - automatic activation is now "
		.. (AUTO_ENABLED and "ON" or "OFF"))
end

-- Find the ability icon. Round 18 showed the engine's own highlight path
-- (battle_orders/orders_parent/behaviour_parent) is the fire-at-will/skirmish row: for Boris
-- all three slots report an EMPTY ability key, so Deadly Onslaught is not there. So scan the
-- HUD instead, bounded, and ask every component the one question the engine documents for
-- identifying an ability button - InterfaceFunction("AbilityKeyForScript") - logging each hit
-- with its Address(). A scan that finds nothing still reports how far it got.
local walk_visits = 0

local function scan_component(uic, depth)
	if uic == nil or depth > 6 or walk_visits > 4000 or our_button ~= nil then return end
	walk_visits = walk_visits + 1

	local ok_key, key = pcall(function() return uic:InterfaceFunction("AbilityKeyForScript") end)
	if ok_key and type(key) == "string" and string.len(key) > 3 then
		local ok_addr, addr = pcall(function() return uic:Address() end)
		log("   ability button: key='" .. key .. "' id='" .. tostring(uic:Id())
			.. "' address=" .. tostring(addr))
		if string.find(string.lower(key), "onslaught") then
			our_button = uic
			local ok_i2, id2 = pcall(function() return uic:Id() end)
			if ok_i2 then our_button_id = tostring(id2) end
			log("   ^ that one is ours")

			-- ASK THE ENGINE TO REPORT ITS EVENTS. Without this the component only emits the
			-- default ones (ComponentLClickUp); with it, all of them - which is the documented
			-- way to hear the mouse events (wiki UI:Main Page, and vanilla's own use of it in
			-- _lib/lib_movie_overlay.lua: "set the panel to report all script events").
			-- ...and on every ancestor up to the HUD: a click may be attributed to a container
			-- (button_parent, SA_dial, ...) rather than to the button itself, and a component only
			-- reports what it has been asked to report.
			watch_chain = {}
			local node = uic
			for _ = 1, 7 do
				if node == nil then break end
				local ok_r, err_r = pcall(function() node:AddScriptEventReporter() end)
				local ok_a, addr = pcall(function() return node:Address() end)
				local ok_i, id = pcall(function() return node:Id() end)
				watch_chain[#watch_chain + 1] = { addr = (ok_a and addr or nil),
					id = (ok_i and tostring(id) or nil) }
				log("   event reporter on '" .. tostring(ok_i and id or "?") .. "' ok=" .. tostring(ok_r)
					.. (ok_r and "" or (" error=" .. tostring(err_r))))
				local ok_p, parent = pcall(function() return node:Parent() end)
				if not ok_p or parent == nil then break end
				local ok_w, wrapped = pcall(function() return UIComponent(parent) end)
				if not ok_w or wrapped == nil then break end
				node = wrapped
			end

			-- WHERE is it? Walk the parents so the log names the container chain. This is what
			-- settles whether the instance can be the component the layout defines at all.
			local path, node = {}, uic
			for _ = 1, 8 do
				local ok_id, id = pcall(function() return node:Id() end)
				table.insert(path, 1, tostring(ok_id and id or "?"))
				local ok_par, parent = pcall(function() return node:Parent() end)
				if not ok_par or parent == nil then break end
				local ok_w, wrapped = pcall(function() return UIComponent(parent) end)
				if not ok_w or wrapped == nil then break end
				node = wrapped
			end
			log("   its container chain: " .. table.concat(path, " < "))

			-- A short flash instead of a permanent pulse: it says "automatic mode is live" once
			-- and then gets out of the way. There is no toggle to keep it lit for.
			original_icon = read_icon()
			log("icon slot " .. tostring(ICON_INDEX) .. " currently shows: " .. tostring(original_icon))

			-- what states does this button have? That is the vocabulary the look can be changed with.
			local ok_cs, cs = pcall(function() return uic:CurrentState() end)
			original_state = ok_cs and tostring(cs) or nil
			local ok_fa, fa = pcall(function() return uic:GetImagePath(0) end)
			original_frame = ok_fa and tostring(fa) or nil
			log("current state: " .. tostring(original_state))
			local ok_ns, ns = pcall(function() return uic:NumStates() end)
			log("states available: " .. tostring(ok_ns and ns or "?"))
			if ok_ns and type(ns) == "number" then
				for i = 1, ns do
					local ok_s2, nm = pcall(function() return uic:GetStateByIndex(i - 1) end)
					if ok_s2 and nm ~= nil then log("      state [" .. tostring(i - 1) .. "] = " .. tostring(nm)) end
				end
			end
			apply_ability_feedback()

			-- (Round 22: the property reads that used to live here are gone - every read echoed the
			-- property's own name, including icon_index which vanilla declares with a value, so script
			-- cannot observe what a layout sets. The chain above is what identified the button.)
		end
	end

	local ok_n, n = pcall(function() return uic:ChildCount() end)
	if ok_n and type(n) == "number" then
		for i = 0, n - 1 do
			local ok_c, child = pcall(function() return uic:Find(i) end)
			if ok_c and child ~= nil then
				scan_component(UIComponent(child), depth + 1)
			end
		end
	end
end

local function find_ability_buttons()
	if our_button ~= nil then return end
	walk_visits = 0

	local ok, err = pcall(function()
		local hud = UIComponent(core:get_ui_root():Find("hud_battle"))
		if hud == nil then
			if not logged_no_parent then
				logged_no_parent = true
				log("ability icons: hud_battle is not on screen yet (will keep trying)")
			end
			return
		end

		log("ability icons: scanning the HUD for ability buttons")
		scan_component(hud, 0)
		log("   scan done: " .. tostring(walk_visits) .. " component(s) visited - "
			.. (our_button ~= nil and "OURS FOUND" or "ours not found"))
	end)

	if not ok then log("ability icon scan failed: " .. tostring(err)) end
end


-- (4) the engine's own report that an ability was *used* - the documented command channel
--     (battle.lua: "Special Ability - a command to use a special ability has been issued",
--     get_string1() = the ability name). Log only, but it is the control case for the whole
--     question: if a click on the icon reaches the game at all, this fires.
bm:register_command_handler_callback("Special Ability", function(context)
	local ability = "?"
	pcall(function() ability = context:get_string1() end)
	log("command: 'Special Ability' issued for '" .. tostring(ability) .. "'")
end, "zz_deadly_onslaught_ability_used")



-- Does this event belong to our chain? Returns the id of the matching component, or nil.
-- Compared by address first (what vanilla does) and by id second.
local function in_chain(context)
	for i = 1, #watch_chain do
		local e = watch_chain[i]
		if e.addr ~= nil and context.component ~= nil and context.component == e.addr then
			return e.id or "?"
		end
	end
	for i = 1, #watch_chain do
		local e = watch_chain[i]
		if e.id ~= nil and context.string == e.id then return e.id end
	end
	return nil
end

-- (1) THE EVENT THAT MATTERS: a right-click on the ability icon, now that the component
-- reports its events. script/events.lua declares ComponentRClickUp; this is the first time we are
-- actually asking for it. Matched by component id and by address, so whichever the context fills in
-- one of them will agree.
local rclick_other = 0
core:add_listener(
	"zz_deadly_onslaught_rclick",
	"ComponentRClickUp",
	function(context) return true end,          -- unfiltered ON PURPOSE: the log labels it
	function(context)
		local who = in_chain(context)
		if who ~= nil then
			log("RCLICK: right-click came in on '" .. tostring(context.string) .. "' - in our chain ("
				.. who .. ")")
			set_auto(not AUTO_ENABLED, "right-click on the ability icon")
		else
			if rclick_other < 15 then
				rclick_other = rclick_other + 1
				log("RCLICK: right-click on '" .. tostring(context.string) .. "' - not ours")
			end
		end
	end,
	true
)

-- (2) THE KEYBOARD. Round 26's firehose proved these two events fire in battle and carry the
-- shortcut's name (string=step_r, step_l, step_bck, step_fwd); no vanilla script uses either, so
-- nothing is being hijacked. The camera-step keys are ignored - they fire while the player pans and
-- would toggle the switch by accident. Any other shortcut flips it, and the log names it, so we can
-- pin the exact key afterwards.
local shortcut_seen = 0
local camera_names = 0
local last_name, last_tick = nil, -1

-- The camera keys fire while the player looks around, which is constant, and each press arrives
-- TWICE (round 27's log: every "cam_down" is doubled), so a naive toggle flips and immediately
-- flips back - which looks exactly like nothing happening. Both are handled here.
-- The one key that toggles. From round 28's log the number keys arrive as "usegroup0".."usegroup9";
-- pressing one whose control group is empty does nothing else in the battle, so it is a deliberate
-- switch rather than a hijacked action. Everything else is logged as ignored.
local TOGGLE_KEY = "usegroup8"

local function is_toggle_key(name)
	return name == TOGGLE_KEY
end

local function on_shortcut(event_name, context)
	local name = tostring(context.string)

	if not is_toggle_key(name) then
		if camera_names < 12 then
			camera_names = camera_names + 1
			log("KEY " .. event_name .. " -> '" .. name .. "' (ignored - toggle key is '"
				.. TOGGLE_KEY .. "')")
		end
		return
	end

	-- debounce: the same name twice inside one 250 ms poll tick is one physical press
	if name == last_name and tick_count <= last_tick + 1 then
		log("KEY " .. event_name .. " -> '" .. name .. "' (repeat of the same press - ignored)")
		return
	end
	last_name, last_tick = name, tick_count

	shortcut_seen = shortcut_seen + 1
	if shortcut_seen <= 60 then
		log("KEY " .. event_name .. " -> '" .. name .. "'  <<< TOGGLING ON THIS")
	end
	set_auto(not AUTO_ENABLED, "keyboard shortcut '" .. name .. "'")
end

core:add_listener("zz_deadly_onslaught_shortcut", "ShortcutTriggered",
	function(context) return true end,
	function(context) on_shortcut("ShortcutTriggered", context) end, true)

core:add_listener("zz_deadly_onslaught_shortcut_pressed", "ShortcutPressed",
	function(context) return true end,
	function(context) on_shortcut("ShortcutPressed", context) end, true)

-- (3) THE CONTROL: a left-click on the same icon, which happens whenever the ability is used -
-- so this one is seen without the player doing anything special. If this reports and the
-- right-click does not, the reporter works and the engine simply never raises the right-click.
local lclick_other = 0
core:add_listener(
	"zz_deadly_onslaught_lclick_control",
	"ComponentLClickUp",
	function(context) return true end,          -- unfiltered ON PURPOSE: the log labels it
	function(context)
		local who = in_chain(context)
		if who ~= nil then
			log("CONTROL: left-click came in on '" .. tostring(context.string) .. "' - in our chain ("
				.. who .. ") - component click events DO reach script in battle")
		else
			if lclick_other < 15 then
				lclick_other = lclick_other + 1
				log("CONTROL: left-click on '" .. tostring(context.string) .. "' - not ours")
			end
		end
	end,
	true
)

-- (3) THE LAST DOOR: the double-click COMPONENT event. The left-click family is reported in
-- battle (round 25's log is full of them, e.g. "left-click on 'button_ability'"), the right-click
-- family is not - so this is the one remaining mouse gesture the engine might report. It is a
-- left-double-click, which is also the gesture that uses the ability, so on the ability icon it
-- cannot be the control; on the unit card it is harmless (it centres the camera). Logged unfiltered
-- with the component's name, and it toggles when the click belongs to our chain or to the card.
local dblclick_other = 0
core:add_listener(
	"zz_deadly_onslaught_dblclick",
	"ComponentLDBLClickUp",
	function(context) return true end,
	function(context)
		local who = in_chain(context)
		local is_card = our_unit_ui_id ~= nil and tostring(context.string) == tostring(our_unit_ui_id)
		if who ~= nil or is_card then
			log("DBLCLICK: double-click came in on '" .. tostring(context.string) .. "'"
				.. (is_card and " - that is our unit's card" or (" - in our chain (" .. who .. ")")))
			set_auto(not AUTO_ENABLED, is_card and "double-click on the unit card"
				or "double-click on the ability icon")
		else
			if dblclick_other < 10 then
				dblclick_other = dblclick_other + 1
				log("DBLCLICK: double-click on '" .. tostring(context.string) .. "' - not ours")
			end
		end
	end,
	true
)

-- (4) THE SPARE: the engine's double-click *command*. It never fired in round 23, but it costs
-- nothing and would toggle the switch if some other situation ever raises it.
-- battle.lua's command list, verbatim: "Double Click Unit Card - A unit card has been
-- double-clicked upon - get_unit() returns the subject unit". This is the engine reporting a
-- mouse gesture to script, on the one channel that is proven to work (round 22's log showed
-- 'Special Ability' arriving the same way). No layout, no property, nothing drawn: the engine
-- tells us, we flip the switch - and the pulse on the ability icon is the feedback.
bm:register_command_handler_callback("Double Click Unit Card", function(context)
	local ok_u, unit = pcall(function() return context:get_unit() end)
	if not ok_u or unit == nil then
		log("double-click on a unit card: the engine sent no unit with it")
		return
	end

	local ok_id, ui_id = pcall(function() return unit:unique_ui_id() end)
	if not ok_id then ui_id = nil end

	if our_unit_ui_id == nil then
		log("double-click on a unit card (ui id " .. tostring(ui_id) .. ") - we have no ability "
			.. "carrier yet, so nothing to toggle")
		return
	end

	if tostring(ui_id) ~= tostring(our_unit_ui_id) then
		log("double-click on a unit card (ui id " .. tostring(ui_id) .. ") - not the carrier of "
			.. "Deadly Onslaught (ui id " .. tostring(our_unit_ui_id) .. "), nothing to toggle")
		return
	end

	set_auto(not AUTO_ENABLED, "double-click on the unit card")
end, "zz_deadly_onslaught_card_doubleclick")



-- ============================================================================
-- 9. START IT UP
--    The poll, the on/off button, and the watchdog that keeps the poll alive.
-- ============================================================================

-- The watchdog's bookkeeping. Round 16 declared these where round 19's deletion removed them,
-- which silently left them as globals - harmless until the stall branch ran, where the arithmetic
-- on a nil would throw and take the UI timer with it. Caught by the mock, not by a battle.
local last_seen_tick = -1
local stalled_checks = 0

local function phase_ui_refresh()
	find_ability_buttons()          -- the ability's own icon (section 8b)
	apply_ability_feedback()        -- keep the icon's pulse in step with the switch
	last_seen_tick = tick_count     -- so the watchdog does not read this as a stall
end

bm:register_phase_change_callback("Deployment", function()
	local ok, err = pcall(phase_ui_refresh)
	if not ok then log("phase_ui_refresh (Deployment) FAILED: " .. tostring(err)) end
end)
bm:register_phase_change_callback("Deployed", function()
	local ok, err = pcall(phase_ui_refresh)
	if not ok then log("phase_ui_refresh (Deployed) FAILED: " .. tostring(err)) end
end)
bm:register_phase_change_callback("Deployed", function()
	local ok, err = pcall(function()
		log("combat phase started - building watch list")
		rebuild_unit_list()
	end)
	if not ok then log("deployed callback failed: " .. tostring(err)) end
end)

-- Diagnostic: the phase dispatcher triggers this event unconditionally, so its
-- presence (or absence) tells us whether phase changes reach scripts at all.
core:add_listener(
	"zz_deadly_onslaught_phase_watch",
	"ScriptEventBattlePhaseChanged",
	function(context) return true end,
	function(context)
		-- Log only. Painting here is what broke round 12: the phase dispatcher
		-- runs this via core:trigger_event, and UI work inside it stopped the
		-- whole phase system after Startup.
		log("phase change seen: " .. tostring(context.string))
	end,
	true
)

bm:repeat_callback(poll, POLL_MS, POLL_NAME)

-- POLL WATCHDOG (real / UI timer, 500 ms)
-- The poll is the only thing watching for charges, and UI work in a phase
-- callback can kill the model timer that drives it (rounds 9, 10, 13). This runs
-- in the UI timer - the one context that has never died - and only checks whether
-- the poll's tick counter is still moving; if it is not, the poll is put back.
-- Nothing is created or painted from here.
-- ---------------------------------------------------------------------------
local ui_ticks = 0

local function ui_tick()
	ui_ticks = ui_ticks + 1
	if ui_ticks == 1 then
		log("ui timer is running (real callback, 500 ms) - watching the poll")
	end

	-- Watch the poll's tick counter and REPORT only: touching the timer registry from a UI
	-- context is what broke the trigger in round 17. While the ability icons are still
	-- unknown, keep trying to find them - the orders bar does not exist in the early
	-- phases, so the first attempts are expected to fail.
	if badge == nil and our_button ~= nil then pcall(create_badge) end

	-- Tied to the ability icon, properly: ask the button which ability it is showing. The dial is
	-- rebuilt for whichever unit is selected, so a visible button may be showing something else
	-- entirely (round 43: the dot stayed while another unit was selected). If the key is no longer
	-- ours, drop the reference - the scan then re-finds the button when our ability comes back.
	if our_button ~= nil then
		local ok_k, key = pcall(function() return our_button:InterfaceFunction("AbilityKeyForScript") end)
		local is_ours = ok_k and type(key) == "string" and string.len(key) > 3
			and string.find(string.lower(key), "onslaught") ~= nil
		if not is_ours then
			our_button = nil
			if badge ~= nil and badge_visible_state ~= false then
				badge_visible_state = false
				pcall(function() badge:SetVisible(false) end)
				log("badge: the dial is showing another ability now - badge hidden")
			end
		end
	end

	-- and while our ability IS on the dial, the badge follows the switch
	if badge ~= nil and our_button ~= nil then
		local want = AUTO_ENABLED
		if want ~= badge_visible_state then
			badge_visible_state = want
			pcall(function() badge:SetVisible(want) end)
		end
	end
	if badge ~= nil then pcall(place_badge) end

	if tick_count == last_seen_tick then
		stalled_checks = stalled_checks + 1
		-- 12 strikes = 6 seconds of real time with no model time passing. Long enough that the
		-- pause menu (which freezes model time) does not read as a dead timer - round 20's log
		-- flagged a "stall" that was almost certainly the player being paused.
		if stalled_checks == 12 then
			log("WATCHDOG: model time has not advanced for 6 s (tick " .. tostring(tick_count)
				.. ") - paused, or the poll is dead. NOT repairing it (the timer registry must not be touched from a UI context)")
		end
	else
		stalled_checks = 0
	end
	last_seen_tick = tick_count

	if our_button == nil and (ui_ticks % 2) == 0 then
		find_ability_buttons()
	end

end

bm:repeat_real_callback(ui_tick, 50, "zz_deadly_onslaught_ui")

-- ---------------------------------------------------------------------------
-- THE BUTTON ITSELF
-- A click handler is a UI context, and painting works from here (rounds 9-14:
-- both the state and the icon followed the clicks).
-- ---------------------------------------------------------------------------

log("loaded. polling every " .. tostring(POLL_MS) .. " ms"
	.. " | fire on charge = " .. tostring(FIRE_ON_CHARGE)
	.. " | fire on melee = " .. tostring(FIRE_ON_MELEE)
	.. " | automatic activation starts " .. (AUTO_ENABLED and "ON" or "OFF")
	.. " | press any shortcut key (not the arrow/step keys) to flip it")
for _, wanted_key in ipairs(ABILITY_KEYS) do
	log("  accepting ability: " .. wanted_key)
end

-- The tooltip override is a localisation file (text/db/zz_deadly_onslaught__.loc) that
-- re-writes the vanilla description of this ability with the right-click instruction
-- appended. This line proves whether it actually loaded: vanilla flavour text with no
-- "Right-click" line means the override lost, and only the tooltip is affected.
local TOOLTIP_KEY = "unit_abilities_tooltip_text_wh_main_character_abilities_deadly_onslaught"
local loc_ok, loc_text = pcall(function() return common.get_localised_string(TOOLTIP_KEY) end)
log("tooltip text in use (" .. (loc_ok and "ok" or "FAILED") .. "): " .. tostring(loc_text))
