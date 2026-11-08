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

-- ============================================================================
-- 1a. THE CLAIM-TEST BISECT - the crash hunt, one engine operation per battle
-- ============================================================================
-- The claim test runs a fixed sequence of operations on the engine's own
-- ability-key value. The sequence is a LADDER: every step can be enabled on
-- its own, and a step that runs announces itself - `bisect: step <n> <name>
-- entering` immediately before its operation, `bisect: step <n> <name> ok`
-- immediately after it. THE STEP THAT KILLS THE GAME IS THE ONE WHOSE
-- `entering` LINE IS THE LOG'S LAST LINE, WITH NO `ok` AFTER IT.
--
-- WHAT THE LADDER FOUND: steps 1-6 all passed in battle (type, tostring,
-- concat copy, string.len, #, string.lower), and the log's last line was
-- `bisect: step 7 string.find plain entering` with no `ok` after it - the
-- FOUR-ARGUMENT PLAIN-MODE find is what killed the engine.
--
-- SO THE FIND IS GONE. Both find forms (plain and pattern) have been removed
-- from every claim/match path, and the match is now EXACT KEY EQUALITY: the
-- lowered copy of the key is compared against the ability's listed keys
-- (ABILITIES, section 1 - already lowercase). Steps 7-8 stay in the ladder
-- as REMOVED slots: they log `SKIPPED (equality match - find removed)` and
-- run nothing, so the record stays honest. Step 9 is the equality compare
-- and remains the verdict gate.
--
-- The nine steps, in the order they run:
--   1 type(v)                    - the value's Lua type
--   2 tostring(v)                - pcall'd text read (the copy's fallback)
--   3 v .. "" (concat copy)      - the fresh plain copy the claim works on
--   4 string.len on the copy     - the length read, pcall'd
--   5 # on the copy              - the language-level length fallback
--   6 string.lower on the copy   - the lowercased copy, pcall'd
--   7 string.find plain          - REMOVED (the killer the bisect named)
--   8 string.find pattern-form   - REMOVED (no find remains at all)
--   9 the equality compare       - lowered copy == each listed key (the gate)
--
-- HOW TO RAISE IT - ONE STEP PER BATTLE:
--   * This build ships CLAIM_BISECT = 9: the whole ladder on - steps 1-6 and
--     9 run, steps 7-8 log their removal. Expect the claim lines and the
--     deferred badges in the next battle log.
--   * Lower levels still gate: with step 9 off the verdict falls back to
--     'not ours' (no claim), so the switch keeps working.
--   * A disabled step logs `bisect: step <n> <name> SKIPPED (disabled)` and
--     its result does not contribute; steps 7-8 always log their removal.
--   * 0 = the whole claim test off; 9 = everything that still exists on.
local CLAIM_BISECT = 9

-- THE ABILITIES - one entry per ability, and this table drives everything:
-- the HUD scan (which dial buttons are ours), the firing loop (which trigger
-- and which keys to try) and the badges (one per ability, id and offset).
--   marker  - the ability's short name, for the log lines and the internal
--             lookups (NO LONGER a substring search: the engine's key is
--             matched by EXACT EQUALITY against the keys listed below)
--   name    - the ability's display name, for the badge log lines
--   trigger - "charge" : the existing charge conditions (section 5), verbatim
--             "running": fire whenever the engine says the unit is moving fast
--             "melee"  : fire whenever the engine says the unit is in melee
--   keys    - the database keys (lowercase) this ability answers to. A dial
--             button is CLAIMED when its key, lowercased, EQUALS one of
--             these, and the unit scan uses them as its search set (which
--             of them a unit actually carries - section 2). At fire time
--             the readiness check (can_perform_special_ability) asks about
--             the ONE key the scan found on the unit; this list is walked
--             only as the fallback when no usable key is cached yet. Add
--             new engine variants here: the scan probe prints every
--             key-bearing button we did not claim (ours=no), so an unknown
--             variant shows up in the log immediately.
--   badge   - the component id of the ability's own M/A badge (its click is
--             the only control)
--   ox, oy  - the badge's FALLBACK offset from the onslaught badge's own
--             BADGE_X / BADGE_Y (section 8b), used only when the claimed
--             button's bar position could not be determined at claim time:
--             onslaught BADGE_X+0/BADGE_Y+0, foe_seeker BADGE_X+70/BADGE_Y+30
--             (the measured +70,+30 from the top wheel slot to the 45-degree
--             slot), hammer_of_sigmar BADGE_X+98/BADGE_Y+102 (the measured
--             top-slot-to-right-slot step). When the bar position IS known,
--             the badge's offset is
--             that wheel slot's delta from the measured top slot (WHEEL_SLOT /
--             WHEEL_TOP_X/WHEEL_TOP_Y, section 8b) applied to BADGE_X/BADGE_Y,
--             so re-tuning the Deadly Onslaught badge (zz_badge_set) still
--             carries Foe-Seeker along.
local ABILITIES = {
	{ marker = "onslaught", name = "Deadly Onslaught", trigger = "charge",
		badge = "zz_auto_badge",
		keys = { "wh_main_character_abilities_deadly_onslaught" },
		ox = 0, oy = 0 },
	{ marker = "foe_seeker", name = "Foe-Seeker", trigger = "running",
		badge = "zz_auto_badge_fs",
		keys = { "wh_main_character_abilities_foe_seeker",
			"wh_dlc03_character_abilities_foe_seeker" },
		ox = 70, oy = 30 },
	{ marker = "hammer_of_sigmar", name = "Hammer of Sigmar", trigger = "melee",
		badge = "zz_auto_badge_hos",
		keys = { "wh_main_spell_bound_hammer_of_sigmar",
			"wh_dlc04_spell_bound_hammer_of_sigmar_upgraded" },
		ox = 98, oy = 102 },
}

-- Every key from the table above, for the ownership scan and the log.
local ALL_ABILITY_KEYS = {}
for _, ability in ipairs(ABILITIES) do
	for _, key in ipairs(ability.keys) do
		ALL_ABILITY_KEYS[#ALL_ABILITY_KEYS + 1] = key
	end
end

-- THE STATIC KEY -> MARKER MAP (item 1.3): every database key listed in the
-- table above, mapped to its ability's short marker, built once at load. It is
-- what turns a unit's cached owned keys (owned_keys_by_unit, section 2) into
-- the short list of abilities that unit can actually carry - the poll's
-- per-unit ability loop (section 8) iterates that list instead of the whole
-- table. Built from the SAME keys the scan matches on, so it can never drift.
local marker_by_key = {}
for _, ability in ipairs(ABILITIES) do
	for _, key in ipairs(ability.keys) do
		marker_by_key[key] = ability.marker
	end
end

-- THE STATIC MARKER -> ENTRY MAP (item 3.1): the ABILITIES entry behind each
-- marker, built once at load. It replaces ability_for's per-call walk of the
-- WHOLE table with ONE table read, so every badge / letter / active-set
-- lookup is O(1) instead of O(entries). INVARIANT: it is built AFTER the
-- ABILITIES table is fully populated (it is - the table above never changes),
-- and ability_by_marker[entry.marker] == entry for EVERY entry; the harness
-- asserts exactly that, because a mismatch would silently drop a badge.
local ability_by_marker = {}
for _, ability in ipairs(ABILITIES) do
	ability_by_marker[ability.marker] = ability
end

-- THE STATIC BADGE-ID -> ENTRY MAP (item 3.1, audit): the same idea for the
-- click router's badge lookup - a badge id is unique per entry, built at load
-- (after ABILITIES, same invariant), so ability_for_badge is one read too.
local ability_by_badge = {}
for _, ability in ipairs(ABILITIES) do
	ability_by_badge[ability.badge] = ability
end

-- THE STATIC KEY MEMBERSHIP SET (item 3.1): the SAME keys as ALL_ABILITY_KEYS
-- (above), but as a set, so "is this engine key one of ours?" is ONE table
-- read instead of a walk of the array. The ARRAY is kept for the ordered
-- iterations that need it (the log and the ordered fallback). INVARIANT:
-- built AFTER ABILITIES is fully populated; EVERY key of EVERY entry is in
-- this set - the harness asserts it, because a missing key would silently
-- miss an owned ability.
local ALL_ABILITY_KEYS_SET = {}
for _, ability in ipairs(ABILITIES) do
	for _, key in ipairs(ability.keys) do
		ALL_ABILITY_KEYS_SET[key] = true
	end
end

-- The ABILITIES entry behind a marker, and behind a badge id (the click
-- router works in badge ids).
local function ability_for(marker)
	-- item 3.1: O(1) - the load-time map, never a walk of the table.
	return ability_by_marker[marker]
end

local function ability_for_badge(badge_id)
	-- item 3.1 (audit): O(1) - the load-time badge-id map.
	return ability_by_badge[badge_id]
end

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

-- How often, in milliseconds, we look at the battlefield. 250 ms = 4x a second.
local POLL_MS = 250

-- THE SHORT GUARD - the short safety brake, in seconds, per (unit, ability):
-- no pair may attempt twice inside this window. The readiness gate (the
-- engine's own can_perform check, section 4) is the real brake now - there
-- are NO 60/90 s timers anywhere any more.
local GUARD_SECONDS = 2

-- How often, in polls, the cheap IDENTITY re-check runs for a unit we have
-- not yet found the ability on: 16 x 250 ms = every 4 seconds. The check
-- reads ONE cheap engine value (the identity watch below); the FULL scan it
-- used to run here now happens only when that value changes, plus the slow
-- fallback beneath this constant.
local REDETECT_EVERY_N_POLLS = 16    -- 16 x 250 ms = every 4 seconds

-- THE IDENTITY WATCH (this build, item 3.4). The 4 s re-check above no longer
-- re-runs the full scan: for a unit with nothing of ours, the poll reads ONE
-- cheap engine value - its identity, battle_unit:type() (battle_unit.lua:
-- "Returns the unit type of the unit, from the land_units table") - and
-- re-scans ONLY when that value CHANGES. That is what catches a
-- transformation or a mount: the unit's type key moves, so a loadout that
-- gained abilities mid-battle is picked up and its new abilities arm and
-- fire. The read costs almost nothing (a string the unit already carries),
-- so the per-4-s engine work of scanning every ability-less unit is gone.
--
-- THE SLOW SAFETY FALLBACK: every FALLBACK_RESCAN_EVERY_N_POLLS polls a full
-- scan still runs for a unit with nothing of ours, whatever its identity
-- says - so an unreadable or unchanging identity degrades to the old
-- behaviour, just far rarer (60 s instead of 4 s).
local FALLBACK_RESCAN_EVERY_N_POLLS = 240   -- 240 x 250 ms = every 60 seconds

-- How often to write one compact status line, in polls. 20 x 250 ms = every 5 s.
-- This is what makes a silent run diagnosable: it proves the poll is alive and
-- records the battle phase plus what every watched unit is doing.
local HEARTBEAT_EVERY_N_POLLS = 20

-- How often to re-list the player's units, in polls: a battle can GROW its
-- army after the first list was built - a summon, a Tzeentch split, a
-- transformation puts NEW units on the field mid-battle - and the watch list
-- must adopt them like any starting unit (tracked, scanned, selection
-- callback registered) without disturbing the units already on it. 40 x
-- 250 ms = every 10 seconds: low-frequency enough that the handful of engine
-- reads never shows, frequent enough that a fresh arrival is armed and
-- firing within seconds of appearing. The refresh speaks ONE line per
-- actual change, and is completely silent otherwise.
local RELIST_EVERY_N_POLLS = 40      -- 40 x 250 ms = every 10 seconds

-- Explicitly take control of the unit before ordering it.
-- OFF by default: the documentation says issuing an order takes control anyway,
-- and an explicit takeover is a candidate cause of the player's current order
-- being cancelled. Leave it off unless we find we need it.
local TAKE_CONTROL_FIRST = false

-- Hand the unit back to the player after the attempt - but ONLY a control we
-- actually took (took_control below). A release is never sent on its own:
-- the engine answers ok to releasing control we never had, and a needless
-- release may flush the unit's order queue. With TAKE_CONTROL_FIRST off
-- (today), this never runs at all.
local RELEASE_CONTROL_AFTER = true

-- How many of each unit's ability keys to write to the log.
local MAX_ABILITIES_TO_LOG = 14


-- ============================================================================
-- 2. BOOKKEEPING
-- ============================================================================

local tracked_units = nil                 -- units we watch
local units_by_ui_id = {}                 -- unique_ui_id (as string) -> unit (the unit-card click lookup)
local target_key_by_unit = {}             -- ui id -> the first of our keys found on the unit
local owned_keys_by_unit = {}             -- ui id (as text) -> EVERY one of our keys the scan
                                          -- found on that unit (ALL_ABILITY_KEYS filtered); the
                                          -- badge click's ownership test (section 10) and the
                                          -- per-unit primitive later items build on
local owned_abilities_by_unit = {}        -- ui id (as text) -> the ABILITIES entries that unit
                                          -- OWNS, in ABILITIES order, variants deduped (item 1.3).
                                          -- Computed once, when the scan fills the owned-key cache
                                          -- above; the poll's per-unit ability loop iterates THIS
                                          -- instead of the whole table. ABSENT (nil) = the unit's
                                          -- owned keys are UNKNOWN -> the loop falls back to the
                                          -- full ABILITIES table, exactly like today.
local identity_by_unit = {}               -- ui id (as text) -> the last-seen identity read of
                                          -- that unit (unit_identity -> battle_unit:type(), the
                                          -- land_units key). THE IDENTITY WATCH (item 3.4): the
                                          -- poll re-scans a unit with no key of ours only when
                                          -- this value CHANGES - which is what catches a
                                          -- transformation or a mount mid-battle
local selected_unit_id = nil              -- the single-choice tracker (string of unique_ui_id):
                                          -- a card click sets it, the card sweep (section 8e)
                                          -- keeps it on the engine's own 'selected' card; with
                                          -- several units selected it stays one of them while
                                          -- the badge click acts on selected_ui_ids below
local selected_ui_ids = {}                -- EVERY id the engine reports as SELECTED - the whole
                                          -- group, not just the tracker above. Maintained from
                                          -- the engine's own selection callback (section 3b)
                                          -- once it has delivered an event; until then (and
                                          -- whenever the callback has never fired) the shared
                                          -- card read (section 8e) keeps it, as it always did.
                                          -- Read by the badge click and the collective letter.

-- THE ENGINE SELECTION CALLBACK (this build). The battle manager's own
-- selection API - battle_manager:register_unit_selection_callback - takes one
-- registration per unit; the library registers the battle's single selection
-- handler once and dispatches every select/deselect event to each registered
-- unit's callback as (unit, selected:boolean). The card states do NOT carry a
-- group/box selection: measured in battle, box-selecting ten captains left
-- EVERY card reading 'active' - which is exactly why a badge click used to
-- toggle only one unit. The callback is the engine's own answer, so the
-- selected set is maintained from it; the card sweep stays as the fallback
-- and reconciliation whenever the API is unavailable or has never fired
-- (read_tracked_card_states, section 8e).
local selection_callbacks_by_ui_id = {}   -- ui id -> true: an accepted callback for that unit
local selection_callback_alive = false    -- true once the engine has DELIVERED an event
local selection_set_dirty = false         -- the set changed since the last convergence (section 8e)
local selection_set_sig = ""              -- the set at the last convergence ("1001,1002"; "" = empty)
local selection_callback_error_logged = false   -- one line for the first swallowed callback error
local reconciled_card_ids = {}            -- id -> true while the id sits in the set only because
                                          -- the cards still report it 'selected' (callback mode):
                                          -- the card read drops such an id again (section 8e)
-- THE REASONED WALK (this build). The old gate re-walked the whole HUD every
-- second UI tick for as long as ANY of our abilities was unclaimed - and a
-- selected unit that owns NONE of them (a Cathayan lord, a Tzeentch lord) has
-- no claim of ours to find, so the walk ran ~10x/s for the whole battle,
-- found nothing and filled the log. These two flags carry the whole reason
-- model: a selection CHANGE (the dial belongs to whoever is selected) and a
-- NEWLY TRACKED unit (a re-list arrival) each request exactly ONE walk - the
-- flag is a boolean, so however many events set it between two UI ticks, at
-- most one walk runs.
local walk_on_selection_change = false    -- set by the selection paths; consumed by the UI tick
local walk_on_new_unit = false            -- set by the re-list; consumed by the UI tick
local armed = {}                          -- ui_id -> (marker -> true/false); ABSENT means off
local last_attempt_at = {}                -- ui_id -> (marker -> tick of the last attempt)
-- THE KNOWN-GONE SET (this build): ui id (as text) -> true for a unit the
-- PRE-FIRE VALIDITY read or an engine rejection proved is no longer there.
-- It makes the drop FINAL: rebuild_unit_list consults it (section 6), so a
-- unit the engine has not yet taken off its army list cannot be re-adopted
-- and re-attempted by the next 10 s refresh - the removal notice is honoured
-- once, not every re-list.
local gone_units = {}
local pending_verify = nil                -- a deferred "did it take effect?" check
local tick_count = 0                      -- our battle clock
local GUARD_TICKS = (GUARD_SECONDS * 1000) / POLL_MS

-- The per-ability state, indexed by marker: the dial button the HUD scan found,
-- its event-reporting chain, the M/A badge component and its placement and
-- visibility bookkeeping. Nothing per-unit lives here.
local ability_state = {}
for _, ability in ipairs(ABILITIES) do
	ability_state[ability.marker] = { watch_chain = {} }
end

-- THE DEFERRED BADGE WORK (this build). A claim in the scan walk only records
-- the button and raises pending_badge[marker]; the ui tick builds the badge
-- from that flag, step by step and instrumented (section 8b). badge_attempts
-- counts the tick-creation attempts since the last claim, and badge_gave_up
-- latches once the budget is spent - until the dial rebuilds (a fresh claim
-- resets both).
local pending_badge = {}                  -- marker -> true while a claim waits for its badge
local badge_attempts = {}                 -- marker -> creation attempts since the last claim
local badge_gave_up = {}                  -- marker -> true once the attempt budget is spent

-- THE CLAIMED BUTTON'S BAR POSITION (this build): marker -> k, the 1-based
-- position of that ability's button among the KEY-BEARING children of its
-- parent bar ('button_parent' - the hidden bar the claimed buttons live in),
-- written by the claim walk (section 8b) and refreshed on every claim. Two
-- measured battles proved that position IS the wheel slot: k maps through
-- the static WHEEL_SLOT table (section 8b) to the measured wheel position,
-- and the badge's offset is BADGE_X/BADGE_Y (the hand-tuned top-slot pair)
-- shifted by that slot's delta from WHEEL_TOP_X/WHEEL_TOP_Y. nil / absent =
-- no usable position (never claimed, the bar unreadable, or more than six
-- key-bearing children): the badge then uses its fallback offset, logged at
-- placement. (The old live Position() read of the claimed button is GONE:
-- the claimed button lives in the hidden bar, so its Position() is a bar
-- coordinate like (1130,1052), NOT a wheel slot - that read is what put the
-- badges off-screen.)
local slot_index = {}

-- THE PER-UNIT SWITCH (this build): armed[ui_id][marker], ABSENT = off.
-- One entry per (unit, ability) pair, so two units carrying the same ability
-- arm and fire INDEPENDENTLY. A pair is flipped by: click the unit's card to
-- select it, then click the ability's M/A badge. This one helper is read by
-- BOTH the firing loop (does THIS unit fire THIS ability?) and the badge
-- display (which letter does the SELECTED unit's badge show?).
-- The arming tables are keyed by the unit's own ui id AS A NUMBER: the engine
-- reports it as a number (unit:unique_ui_id()), while the click paths carry
-- it as text (the card id IS that number). This maps the text form back to the
-- number so both paths always land on the SAME slot; a value that is already
-- the number (or a non-numeric id) passes through unchanged. tonumber never
-- allocates and no string is built, so the mapping is allocation-free.
local function unit_slot(ui_id)
	local n = tonumber(ui_id)
	if n ~= nil then return n end
	return ui_id
end

-- A READ NEVER CREATES: an unarmed (unit, marker) is a plain pass through
-- armed[ui_id] that MISSES (nil) - no inner table is ever built on a miss, so
-- reading a never-armed pair costs ONE table lookup and no allocation at all.
local function is_armed(unit, marker)
	if unit == nil then return false end
	local ok_id, raw_id = pcall(function() return unit:unique_ui_id() end)
	if not ok_id or raw_id == nil then return false end
	local ui_id = unit_slot(raw_id)
	local per = armed[ui_id]
	return per ~= nil and per[marker] == true
end

-- The unit behind the current selection, or nil while nothing is selected.
-- selected_unit_id follows the engine's own card state ('selected') through
-- the once-a-second card sweep (section 8e); a unit-card click is the
-- immediate fast-path when it lands first. A card's component id IS its
-- unit's unique_ui_id (the proven bridge - vanilla matches uic_card:Id() ==
-- unit:unique_ui_id() the same way), so selection is a plain table lookup:
-- no find of any kind.
local function selected_unit()
	if selected_unit_id == nil then return nil end
	return units_by_ui_id[tostring(selected_unit_id)]
end

-- One compact "how the per-unit switches stand" string, for the tick and
-- heartbeat logs: the selected unit and its own armed state per ability.
-- There is no global switch any more - each unit carries its own.
local function armed_states_string()
	local bits = { "selected=" .. tostring(selected_unit_id or "none") }
	local unit = selected_unit()
	for _, ability in ipairs(ABILITIES) do
		bits[#bits + 1] = ability.marker .. "=" .. (is_armed(unit, ability.marker) and "ON" or "OFF")
	end
	return table.concat(bits, ",")
end


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
-- 2b. THE ACTIVE ABILITY SET (item 1.4)
-- ============================================================================
-- The ui tick's badge build/show/hide work was the only place the WHOLE
-- ABILITIES table was walked every 50 ms. At three entries that is free; at
-- dozens it is per-tick waste. The set below is the subset that can matter in
-- THIS battle:
--
--   (a) every tracked unit's OWNED markers - our keys filtered out of the
--       per-unit cache (owned_keys_by_unit, section 2) the scan already
--       fills, so no engine read and no searching beyond the units we
--       already watch;
--   (b) every marker CURRENTLY CLAIMED on the dial - ability_state
--       [marker].button ~= nil. This is the SUPERSET SAFETY: the dial
--       belongs to whoever is selected, and a claim can name an ability no
--       tracked unit owns, so a badge that is on the dial is never lost;
--   (c) nothing else.
--
-- It is recomputed ONLY when an input changes - the re-list, a scan, a
-- claim, a drop - never per tick, so the ui tick reads a ready list. Until
-- ANY information exists (the bootstrap: no tracked unit has owned-keys data
-- yet) the set is nil and every reader falls back to the FULL ABILITIES
-- table, which keeps the bootstrap behaviour identical to today. One line is
-- logged, and ONLY when the membership actually changes.
--
-- This is item 1.4 only: the POLL's per-unit ability loop (item 1.3) is
-- deliberately untouched, and all_buttons_found() stays a full-table walk
-- (the walk gate is item 1.1's region, not this one).

local active_abilities = nil          -- list of ABILITIES entries; nil = unknown -> use ABILITIES
local active_abilities_note = nil     -- the last logged membership line (silence unless it moves)

-- The list the ui tick's badge paths iterate: the active set, or the whole
-- table while nothing is known yet.
local function active_abilities_list()
	return active_abilities or ABILITIES
end

-- Rebuild the set from the owned-key cache and the live claims, and log ONE
-- line only when the membership changed. Cheap by construction: it walks the
-- tracked units and their cached owned keys, never the engine.
local function refresh_active_abilities()
	local set = {}
	local known = false

	-- (a) every tracked unit's owned markers, read out of the owned-key cache.
	if tracked_units ~= nil then
		for i = 1, #tracked_units do
			local su = tracked_units[i]
			local unit = su and su.unit
			if unit ~= nil then
				local ok_id, ui_id = pcall(function() return unit:unique_ui_id() end)
				if ok_id and ui_id ~= nil then
					local owned = owned_keys_by_unit[tostring(ui_id)]
					if owned ~= nil then
						known = true
						for oi = 1, #owned do
							-- item 3.1: one read of the static key->marker map
							-- instead of walking ABILITIES and each entry's keys.
							local marker = marker_by_key[owned[oi]]
							if marker ~= nil then
								set[marker] = true
							end
						end
					end
				end
			end
		end
	end

	-- (b) every currently claimed marker - the superset safety.
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		if state ~= nil and state.button ~= nil then
			set[ability.marker] = true
		end
	end

	-- (c) bootstrap: no information at all -> the full table (identical to
	-- today; nothing is logged).
	if not known then
		active_abilities = nil
		return
	end

	local list = {}
	local names = {}
	for _, ability in ipairs(ABILITIES) do
		if set[ability.marker] then
			list[#list + 1] = ability
			names[#names + 1] = ability.marker
		end
	end
	active_abilities = list

	local note = table.concat(names, ", ")
	if note ~= active_abilities_note then
		active_abilities_note = note
		log("active abilities this battle: " .. (note ~= "" and note or "(none)"))
	end
end

-- ITEM 1.3 - THE PER-UNIT OWNED-ABILITY LIST. Turn a unit's cached owned DB
-- keys into the ABILITIES entries it can actually carry: each key maps through
-- the static marker_by_key table (built once, section 1), the markers are
-- DEDUPED (a unit carrying BOTH engine variants of one marker - e.g. the main
-- and DLC Foe-Seeker keys - yields that marker ONCE), and the list is emitted
-- in ABILITIES order so the firing order - and therefore every log line and
-- every firing decision - is exactly what the full-table walk produced. A unit
-- carrying none of ours yields an EMPTY list, and the poll then evaluates
-- nothing for it instead of the whole table.
local function owned_abilities_of(owned_keys)
	local mark_owned = {}
	for oi = 1, #owned_keys do
		local marker = marker_by_key[owned_keys[oi]]
		if marker ~= nil then
			mark_owned[marker] = true
		end
	end
	local list = {}
	for _, ability in ipairs(ABILITIES) do
		if mark_owned[ability.marker] then
			list[#list + 1] = ability
		end
	end
	return list
end


-- ============================================================================
-- 3b. THE ENGINE SELECTION CALLBACK (this build)
--     The battle manager's own selection API: one registration per unit
--     (battle_manager:register_unit_selection_callback(unit, callback)), and
--     the engine then delivers every selection change of that unit to the
--     callback as (unit, selected:boolean) - truthy on a selection, the
--     boolean false on a deselection. This is the ONLY mechanism that sees a
--     group / box selection: the unit cards do not report one. The callback
--     runs in the engine's event context, so it does NOTHING but maintain the
--     selected set and raise a flag - no UI writes, no log lines (the set
--     change is logged ONCE per change by the tick convergence, section 8e,
--     so a ten-unit box selection cannot spam ten lines). Everything in the
--     body runs inside the pcall wall of the registered wrapper below: a
--     callback that raises kills every callback registered for the battle,
--     and this one is never allowed to be that.
-- ============================================================================

local function engine_selection_has(id)
	for i = 1, #selected_ui_ids do
		if selected_ui_ids[i] == id then return true end
	end
	return false
end

-- The callback body. Only private state: add the id on a selection, remove it
-- on a deselection, and raise selection_set_dirty when the set really moved
-- (the tracker and the badge letters follow at the next convergence, section
-- 8e). A unit we do not track is ignored (its events are not ours to act on).
local function engine_selection_body(unit, selected)
	if unit == nil then return end
	local ok_id, ui_id = pcall(function() return unit:unique_ui_id() end)
	if not ok_id or ui_id == nil then return end
	local id = tostring(ui_id)
	if units_by_ui_id[id] == nil then return end

	selection_callback_alive = true

	if selected then
		if not engine_selection_has(id) then
			selected_ui_ids[#selected_ui_ids + 1] = id
			selection_set_dirty = true
			walk_on_selection_change = true   -- the dial now belongs to the new selection
		end
	else
		for i = #selected_ui_ids, 1, -1 do
			if selected_ui_ids[i] == id then
				table.remove(selected_ui_ids, i)
				selection_set_dirty = true
				walk_on_selection_change = true   -- the dial re-homes when a selection drops
			end
		end
	end
end

-- THE REGISTERED CALLBACK: the body behind the error wall. The first swallowed
-- error is logged once (it is also the proof the wall is doing its job); every
-- later one is swallowed the same silent way.
local function engine_selection_callback(unit, selected)
	local ok, err = pcall(engine_selection_body, unit, selected)
	if not ok and not selection_callback_error_logged then
		selection_callback_error_logged = true
		log("selection callback error (swallowed - the engine's callbacks stay alive): "
			.. tostring(err))
	end
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

		-- item 3.1: O(1) membership test against the static key set (the
		-- ALL_ABILITY_KEYS array stays for the ordered iterations).
		if ALL_ABILITY_KEYS_SET[owned_key] then
			matching_key = owned_key
		end
	end

	return matching_key, all_keys
end

-- THE CHEAP IDENTITY READ (this build, item 3.4): ONE engine call -
-- battle_unit:type(), the unit's land_units key (battle_unit.lua: "Returns
-- the unit type of the unit, from the land_units table"). It costs almost
-- nothing and it is the value a transformation or a mount moves, so it is
-- what the poll watches instead of re-running the full scan every 4 s. The
-- read is pcall-guarded and FAIL-OPEN: a missing method, a raising read or a
-- nil answer all come back as nil, and a nil identity never reports a change
-- (the 60 s fallback then carries the re-scan). Used by the poll's redetect
-- step only.
local function unit_identity(unit)
	local ok, value = pcall(function() return unit:type() end)
	if ok and value ~= nil then
		return tostring(value)
	end
	return nil
end

-- Which key of this ability (if any) did the unit list among its own? Used by
-- the watch-list log. owned_keys is the all_keys list scan_unit_abilities gave.
local function owned_key_in(ability, owned_keys)
	for _, wanted_key in ipairs(ability.keys) do
		for _, owned_key in ipairs(owned_keys) do
			if owned_key == wanted_key then return wanted_key end
		end
	end
	return nil
end

-- THE PER-UNIT OWNED-KEY CACHE (this build). The scan reports every ability a
-- unit carries (all_keys); this keeps only OUR keys from that list, per unit,
-- in owned_keys_by_unit (section 2). It answers one question without any
-- engine read or searching - "does this unit own this ability?" - for the
-- badge click's checkbox rule (section 10) and the collective badge letter.
local function our_keys_of(all_keys)
	local ours = {}
	for k = 1, #all_keys do
		-- item 3.1: O(1) membership test. The keys are unique, so an owned
		-- key was appended exactly once before too.
		if ALL_ABILITY_KEYS_SET[all_keys[k]] then
			ours[#ours + 1] = all_keys[k]
		end
	end
	return ours
end

-- Does this unit's cached owned-keys list carry one of this ability's keys?
-- (the same exact-equality match the scan and the ready gate use). Unknown
-- units and units the scan has not seen answer false.
local function unit_owns_marker(ui_id, marker)
	local ability = ability_for(marker)
	if ability == nil then return false end
	local owned = owned_keys_by_unit[tostring(ui_id)]
	if owned == nil then return false end
	return owned_key_in(ability, owned) ~= nil
end

-- WHY A WALK WOULD EVER BE NEEDED (this build). Two questions, both answered
-- from state the mod already holds - no engine read, no searching of any kind:
--   * is anything known yet about the SELECTED unit's own keys? (no selection,
--     or a selected id the scan has not cached: the BOOTSTRAP phase, which
--     keeps the old every-other-tick walk);
--   * does the selected unit OWN one of our keys whose dial claim is still
--     MISSING? (the dial-animation / lag case: retry briskly until claimed).
local function selection_walk_info_known()
	if selected_unit_id == nil then return false end
	if owned_keys_by_unit[tostring(selected_unit_id)] == nil then return false end
	return true
end

local function selected_unit_owns_unclaimed_key()
	if selected_unit_id == nil then return false end
	local owned = owned_keys_by_unit[tostring(selected_unit_id)]
	if owned == nil then return false end
	for _, ability in ipairs(ABILITIES) do
		if ability_state[ability.marker].button == nil
			and unit_owns_marker(selected_unit_id, ability.marker) then
			return true
		end
	end
	return false
end

-- THE COLLECTIVE SWITCH READ (this build) - the expected letter behind EVERY
-- badge write (the badge's first SetText, the cached writer, the per-tick
-- safety net and the click refresh all call it, so they can never disagree).
-- ONE selected unit: exactly the old read - that unit's own armed flag.
-- SEVERAL selected units: the vanilla "common ability" rule - on only when
-- EVERY selected unit that owns this ability has it armed, so the badge reads
-- A while the whole group is armed and flips to M the moment any member is
-- off. A group where no selected unit owns the ability reads off.
local function collective_armed(marker)
	local n = #selected_ui_ids
	if n <= 1 then
		return is_armed(selected_unit(), marker)
	end
	local owners = 0
	for i = 1, n do
		local id = selected_ui_ids[i]
		if unit_owns_marker(id, marker) then
			owners = owners + 1
			if not is_armed(units_by_ui_id[tostring(id)], marker) then
				return false
			end
		end
	end
	return owners > 0
end

-- THE READINESS GATE (the engine's own "can I use this?" check). The key it
-- asks about is the one the unit scan already found on this unit
-- (target_key_by_unit, section 2): a database variant the unit does NOT
-- carry can only ever answer false, so re-trying every variant at fire time
-- told us nothing new - one query, on the owned key, is the whole question.
-- The old walk over ability.keys stays ONLY as the fallback for a unit with
-- no usable cached key: not scanned yet, or the cached key belongs to a
-- DIFFERENT ability of ours (a unit can carry more than one - asking here
-- about that key could fire the wrong ability, so it is not used). No
-- fall-through when the owned key answers false: that means running/on
-- cooldown, and no other variant changes that. Returns the key or nil, plus
-- a text summary of every answer (logged on each evaluation, like the
-- earlier two-ability build).
local function check_readiness(unit, ability, cached_key)
	local ready_key = nil
	local parts = {}
	local suffix = " (fallback scan)"   -- no usable cached key: the old walk ran

	-- Which cached key may answer here: only one that belongs to THIS ability.
	local owned_key = nil
	if cached_key ~= nil then
		for _, wanted_key in ipairs(ability.keys) do
			if wanted_key == cached_key then owned_key = cached_key end
		end
	end

	if owned_key ~= nil then
		-- The one query: the key this unit was found to own.
		suffix = " (owned key)"
		local ok_c, can = pcall(function()
			return unit:can_perform_special_ability(owned_key)
		end)
		parts[#parts + 1] = owned_key .. "=" .. tostring(ok_c and tostring(can) or "ERROR")
		if ok_c and can == true then
			ready_key = owned_key
		end
	else
		-- No usable cached key yet: the original walk over the variants.
		for _, wanted_key in ipairs(ability.keys) do
			local ok_c, can = pcall(function()
				return unit:can_perform_special_ability(wanted_key)
			end)
			parts[#parts + 1] = wanted_key .. "=" .. tostring(ok_c and tostring(can) or "ERROR")
			if ok_c and can == true and ready_key == nil then
				ready_key = wanted_key
			end
		end
	end

	return ready_key, table.concat(parts, ", ") .. suffix
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
	-- THE ADDITIVE RE-LIST (this build). The old function wiped the watch
	-- list and rebuilt it from scratch - fine for its original single
	-- startup call, but the poll now re-runs it every RELIST_EVERY_N_POLLS
	-- polls (mid-battle arrivals: summons, Tzeentch splits, transformations),
	-- and a wipe would lose per-unit state. So this function now MERGES, by
	-- identity (ui id): every unit already on the list is left completely
	-- untouched; only units the list has never seen are appended, scanned
	-- and remembered; and a unit the engine no longer returns (died / left
	-- the field) is dropped, exactly what the old wholesale rebuild did
	-- with it.
	local first_build = (tracked_units == nil)
	if first_build then
		tracked_units = {}
	end

	local sunits = bm:get_scriptunits_for_local_players_army()
	if sunits == nil then
		log("no units returned yet (army not on the field?)")
		return
	end

	local total = sunits:count()
	if first_build then
		log("watching " .. tostring(total) .. " unit(s) in the local player's army")
	end

	local carriers = 0
	local fresh = {}            -- ui id (as text) -> true: the engine reported it this pass
	local new_count = 0
	local new_ids = {}

	for i = 1, total do
		local script_unit = sunits:item(i)
		local unit = script_unit.unit
		local ui_id = unit:unique_ui_id()
		local id_text = tostring(ui_id)

		if fresh[id_text] == nil then
			fresh[id_text] = true

			-- A UNIT THE LIST HAS NOT SEEN: track it, scan it, remember it. Only
			-- genuinely new arrivals run the scan below, so an existing unit's
			-- remembered key and owned keys can never be overwritten by a refresh.
			-- A unit in gone_units (this build) is NOT re-adopted: the pre-fire
			-- read or an engine rejection already proved it is gone, and the
			-- engine may still be listing it for a while.
			if units_by_ui_id[id_text] == nil and gone_units[id_text] == nil then
				tracked_units[#tracked_units + 1] = script_unit

				-- The card-click bridge: a unit card's component id IS this unit's
				-- unique_ui_id, so a click on the card finds the unit right here.
				units_by_ui_id[id_text] = unit

				local matching_key, all_keys = scan_unit_abilities(unit)

				target_key_by_unit[ui_id] = matching_key
				owned_keys_by_unit[id_text] = our_keys_of(all_keys)   -- the per-unit owned-key cache
				owned_abilities_by_unit[id_text] =                       -- item 1.3: the short list
					owned_abilities_of(owned_keys_by_unit[id_text])      -- this unit's poll walks
				if matching_key ~= nil then
					carriers = carriers + 1
				end

				new_count = new_count + 1
				new_ids[#new_ids + 1] = id_text
				walk_on_new_unit = true          -- a unit the list never saw: scan for its dial once

				-- THE OPENING CENSUS keeps its full per-unit log; a later refresh
				-- deliberately stays to its ONE change line below - a full census
				-- per refresh is exactly the log spam this build avoids.
				if first_build then
					local own_parts = {}
					for _, ability in ipairs(ABILITIES) do
						local owned_key = owned_key_in(ability, all_keys)
						own_parts[#own_parts + 1] = "owns " .. ability.name .. " = "
							.. tostring(owned_key ~= nil)
							.. (owned_key and (" as '" .. owned_key .. "'") or "")
					end

					log("  unit '" .. tostring(unit:type()) .. "'"
						.. " ui id " .. tostring(ui_id)
						.. " | " .. tostring(#all_keys) .. " abilities"
						.. " | " .. table.concat(own_parts, " | ")
						.. " | usable right now = "
						.. tostring(unit:can_perform_special_ability(ALL_ABILITY_KEYS[1])))

					for j = 1, #all_keys do
						if j <= MAX_ABILITIES_TO_LOG then
							log("      ability: " .. tostring(all_keys[j]))
						end
					end
				end
			end
		end
	end

	-- THE DROP: a unit the engine did not return this pass (it died or left
	-- the field) comes off the watch list, exactly as the old wholesale
	-- rebuild dropped it. The per-unit tables (armed states keyed by
	-- ui_id then marker, last attempts) are keyed by ui id and simply become
	-- unreachable, as they always did.
	local dropped_count = 0
	local dropped_ids = {}
	for i = #tracked_units, 1, -1 do
		local unit = tracked_units[i].unit
		local id_text = tostring(unit:unique_ui_id())
		if fresh[id_text] == nil then
			table.remove(tracked_units, i)
			units_by_ui_id[id_text] = nil
			dropped_count = dropped_count + 1
			dropped_ids[#dropped_ids + 1] = id_text
		end
	end

	-- Make the success case impossible to miss when reading the log (the
	-- opening census only).
	if first_build then
		log("ability carriers found: " .. tostring(carriers))
	end

	-- THE ONE REFRESH LINE: a re-list speaks exactly once, and ONLY when the
	-- watched set actually changed - silent while the army is steady, so the
	-- 10-second refreshes can never turn into per-poll log spam. (The
	-- opening census above is the initial build's voice; a refresh never
	-- repeats it.)
	if not first_build and (new_count > 0 or dropped_count > 0) then
		local parts = {}
		if new_count > 0 then
			parts[#parts + 1] = tostring(new_count) .. " new unit(s) now tracked ("
				.. table.concat(new_ids, ", ") .. ")"
		end
		if dropped_count > 0 then
			parts[#parts + 1] = tostring(dropped_count) .. " unit(s) dropped ("
				.. table.concat(dropped_ids, ", ") .. ")"
		end
		log("unit list refresh: " .. table.concat(parts, " | "))
	end

	-- THE ENGINE SELECTION CALLBACKS (this build): one registration per tracked
	-- unit with the engine's own selection API, so a GROUP / BOX selection
	-- reaches us per unit (the card states do not carry one - measured in
	-- battle). Everything is guarded twice: the API may not exist (or may not
	-- accept the unit) in some builds - the card sweep then stays in charge,
	-- unchanged - and a registration that raises is caught here (a callback
	-- that raises is caught again, inside, at every event). A unit already
	-- registered keeps its single registration across rebuilds, so a refresh
	-- registers for genuinely NEW units only - exactly once each.
	local registered_now = 0
	local ok_fn, is_fn = pcall(function()
		return type(bm.register_unit_selection_callback) == "function"
	end)
	if ok_fn and is_fn then
		for i = 1, #tracked_units do
			local su = tracked_units[i]
			local unit = su and su.unit
			if unit ~= nil then
				local ok_u, ui_id = pcall(function() return unit:unique_ui_id() end)
				if ok_u and ui_id ~= nil and selection_callbacks_by_ui_id[tostring(ui_id)] == nil then
					local ok_r, accepted = pcall(function()
						return bm:register_unit_selection_callback(unit, engine_selection_callback)
					end)
					if ok_r and accepted ~= false then
						selection_callbacks_by_ui_id[tostring(ui_id)] = true
						registered_now = registered_now + 1
					end
				end
			end
		end
		if first_build then
			log("engine selection API: " .. tostring(registered_now) .. " new callback(s) registered ("
				.. tostring(#selection_callbacks_by_ui_id) .. " unit(s) covered in total)")
		end
	else
		if first_build then
			log("engine selection API not available - the card-state sweep stays in charge (unchanged fallback)")
		end
	end

	-- ITEM 1.4 - the re-list / drop just changed the inputs: refresh the
	-- active set (silent unless the membership moved).
	refresh_active_abilities()
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

-- (The switch is PER UNIT AND PER ABILITY: armed[ui_id][marker], section 2
--  - absent means off (the badges show M) until the player clicks them. The
--  player selects a unit by clicking its card (the card id IS the unit's
--  unique_ui_id), then each badge click flips ONLY that unit's own ability.
--  The badge click is the ONLY control - the keyboard, right-click and
--  double-click routes have all been removed (rounds 15-25 measured that
--  nothing else reaches script in battle).)

-- The switch itself. Everything that used to make a button for it - the template clone,
-- the docking, the two icon files, the bar-width fiddling and the click listener - has been
-- removed: the control is a left-click on the M/A badge (section 8b).

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
		"auto=" .. armed_states_string(),
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

-- (The old fixed brakes - 90 s per unit after an accepted activation, and the
--  20 s floor between attempts - are gone. The readiness gate (section 4) and
--  the short guard (GUARD_SECONDS, section 1) are the whole brake now.)


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

-- A CONTAINS TEST WITH NO string.find IN IT. The bisect proved the engine
-- dies inside the four-argument plain-mode find, and this build has removed
-- every find call from the file. This small plain-Lua scan (string.sub
-- slices; it only ever sees our own tostring() error text, never an engine
-- value) is what checks for the engine's known "does not support this
-- special ability" message instead.
local function text_contains(haystack, needle)
	local h = tostring(haystack or "")
	local n = tostring(needle or "")
	local hlen = string.len(h)
	local nlen = string.len(n)
	if nlen == 0 or nlen > hlen then return false end
	for i = 1, hlen - nlen + 1 do
		if string.sub(h, i, i + nlen - 1) == n then return true end
	end
	return false
end

-- THE NON-EXISTENCE REFUSALS (this build). The engine wraps a refused fire as
-- "calling 'perform_special_ability' on bad self (error: ...)". When the unit
-- it names is GONE, the inner text says so in one of the forms below - and
-- those are what are matched here, exact substring only, through the same
-- find-free text_contains() the cooldown check uses. THE COOLDOWN/ACTIVE
-- REFUSAL THIS MOD HAS ALWAYS SEEN IS A DIFFERENT STRING ("does not support
-- this special ability"): none of the markers below is a substring of it, so
-- a LIVE unit that is merely on cooldown can never match and be dropped. The
-- live battle log proves that string is a hold, not a death: one unit (ui id
-- 1002) produced it dozens of times and ACCEPTED a fire minutes later.
local GONE_UNIT_ERRORS = {
	"does not exist",
	"no longer exists",
	"no such unit",
	"invalid unit",
	"unit is gone",
}

local function error_means_unit_gone(err_text)
	local text = tostring(err_text or "")
	for i = 1, #GONE_UNIT_ERRORS do
		if text_contains(text, GONE_UNIT_ERRORS[i]) then return true end
	end
	return false
end

-- THE PRE-FIRE VALIDITY READ (this build). Two cheap, pcall'd engine reads
-- immediately before the fire call, cutting the window between the poll's
-- alive check (which reads number_of_men_alive) and the call itself - a unit
-- that dies inside that window is exactly why this exists.
--
-- THE RULE is deliberately two-signal and fail-open, because an identity read
-- alone is NOT a death test: an unreadable identity (battle_unit:type()
-- answering nothing) is a state this mod already supports - the identity
-- watch keeps such a unit and the slow 60 s fallback still rescues it. So:
--   * if number_of_men_alive ANSWERS A NUMBER, that is the truth: > 0 alive,
--     <= 0 gone;
--   * only when it does NOT answer a number does the identity read decide,
--     and only a CLEAN nil (the unit answered nothing at all) counts as gone.
-- A READ THAT RAISES - either read - is a transient engine failure, exactly
-- the shape pcall catches, and is NEVER death. Two independent failures are
-- needed before a unit is called gone, so a single flaky read can never drop
-- a live unit. (unit_identity() is not reused here on purpose: it folds a
-- raising read and a nil answer into the same nil, which would make a
-- transient failure look like death.)
local function unit_is_gone(unit)
	if unit == nil then return true end
	local ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)
	if ok_alive and type(alive) == "number" then
		return alive <= 0                  -- the engine answered: THAT is the truth
	end
	local ok_id, id = pcall(function() return unit:type() end)
	return ok_id and id == nil             -- no answer from either read: gone
end

local function attempt_activation(script_unit, unit, ability_key, reason, ui_id, marker)
	-- PRE-FIRE VALIDITY (this build): re-verify the unit is still usable
	-- immediately before the call. A unit that is gone answers nothing, so it
	-- is dropped at once - ONE line, and the fire is never attempted (this
	-- check sits BEFORE the ATTEMPT line, so no attempt is ever logged for it).
	if unit_is_gone(unit) then
		log("unit " .. tostring(ui_id) .. " is gone (pre-fire check)"
			.. " - dropped from tracking")
		return "gone"
	end

	-- The armed-check outcome rides on the attempt line itself (once per
	-- attempt): by the time an attempt runs, this unit's pair is armed.
	log("ATTEMPT " .. tostring(marker) .. " '" .. ability_key .. "' on '" .. tostring(unit:type())
		.. "' ui id " .. tostring(ui_id) .. " | reason: " .. reason
		.. " | armed=" .. (is_armed(unit, marker) and "ON" or "OFF"))

	local uc = script_unit.uc

	if uc == nil then
		log("  STOP: script_unit.uc is nil - there is no controller to order")
		return
	end

	local took_control = false

	if TAKE_CONTROL_FIRST then
		local ok_take, err_take = pcall(function() uc:take_control() end)
		took_control = ok_take
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

	local outcome = "held"        -- what the caller gets back: held / fired / gone
	if ok_call then
		log("  perform_special_ability(key, unit) : ACCEPTED")
		log("  the readiness gate decides the next attempt (plus the "
			.. tostring(GUARD_SECONDS) .. " s guard)")
		outcome = "fired"
	else
		local err_text = tostring(err_call)
		log("  perform_special_ability(key, unit) : REJECTED - " .. err_text)

		-- AN ENGINE REJECTION THAT NAMES A NON-EXISTENT UNIT IS A REMOVAL
		-- NOTICE (this build): the unit it names is gone, so it is dropped at
		-- once. ONLY the non-existence text matches - the cooldown text below
		-- is a different string, so a live unit that is merely on cooldown
		-- never reaches this branch and keeps behaving exactly as before.
		if error_means_unit_gone(err_text) then
			log("unit " .. tostring(ui_id) .. " is gone (engine rejected the call)"
				.. " - dropped from tracking")
			outcome = "gone"
		elseif text_contains(err_text, "does not support this special ability") then
			log("  -> engine says the unit cannot use it right now, which is what it")
			log("     says while the ability is active/on cooldown. The readiness gate")
			log("     will hold the next attempt back until the engine says yes again.")
		end
	end

	if RELEASE_CONTROL_AFTER and took_control then
		local ok_release, err_release = pcall(function() uc:release_control() end)
		log("  release_control         : ok=" .. tostring(ok_release)
			.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
	end

	return outcome
end


-- ============================================================================
-- 7d. IS THE UNIT ROUTING? One shared engine read, per unit, per poll
--     battle_unit:is_routing() is the script-reachable accessor. The vanilla
--     scripts read exactly this call: lib_battle_misc.lua's is_routing_or_dead
--     runs obj:is_routing() on the unit, and a script_unit reaches its unit
--     through the .unit field - the very handle this poll already reads
--     is_moving_fast() and is_in_melee() from.
--
--     WHY: a routing unit is fleeing the field. Its flight trips the running
--     trigger (is_moving_fast) and can sit in melee geometry, so without this
--     guard an armed unit would burn active buffs while running away.
--
--     THE RULES:
--       * ONE read per unit per poll - the poll computes it once below and
--         every trigger reuses that value, however many are armed;
--       * guarded like every other engine read (pcall);
--       * FAIL-OPEN: only an exact true answer suppresses a trigger. A
--         missing method, a raising read or any other value counts as NOT
--         routing, so when the state cannot be read the mod behaves exactly
--         as it did before this condition existed.
-- ============================================================================

local function unit_is_routing(unit)
	local ok, routing = pcall(function() return unit:is_routing() end)
	if ok and routing == true then
		return true
	end
	return false
end


-- ============================================================================
-- 8. THE POLL - runs every POLL_MS milliseconds for the whole battle
-- ============================================================================

-- THE IMMEDIATE DROP (this build). The same bookkeeping as the re-list's own
-- drop path (section 6) - the unit leaves tracked_units and its
-- units_by_ui_id entry is cleared - but performed at once, the moment a
-- pre-fire validity read or an engine rejection proves the unit is gone. The
-- id is also put in gone_units, so the next 10 s re-list cannot re-adopt a
-- unit the engine has not yet taken off its army list. Called AFTER the
-- poll's tracking loop has stopped walking the list, so the table.remove here
-- can never disturb the iteration it came from; it is silent - the caller has
-- already written the one drop line.
local function drop_unit_by_ui_id(ui_id)
	local id_text = tostring(ui_id)
	gone_units[id_text] = true
	if tracked_units ~= nil then
		for i = #tracked_units, 1, -1 do
			local script_unit = tracked_units[i]
			local unit = script_unit and script_unit.unit
			local same = false
			if unit ~= nil then
				local ok_id, id = pcall(function() return unit:unique_ui_id() end)
				if ok_id and id ~= nil and tostring(id) == id_text then same = true end
			end
			if same then
				table.remove(tracked_units, i)
			end
		end
	end
	units_by_ui_id[id_text] = nil
end

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
			.. " | auto=" .. armed_states_string()
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

	-- THE PERIODIC RE-LIST (this build): mid-battle arrivals - summons,
	-- Tzeentch splits, transformations - must become watched, scanned and
	-- selection-registered exactly like a starting unit, so the watch list is
	-- re-listed every RELIST_EVERY_N_POLLS polls (40 x 250 ms = 10 s).
	-- rebuild_unit_list is additive: existing units are untouched, only
	-- genuinely new ones are added (and units the engine no longer returns
	-- are dropped), and it speaks ONE line only when the set actually
	-- changed. No return here: the refreshed list is processed on this very
	-- tick.
	if (tick_count % RELIST_EVERY_N_POLLS) == 0 then
		rebuild_unit_list()
	end

	local do_redetect = (tick_count % REDETECT_EVERY_N_POLLS) == 0
	local do_fallback_rescan = (tick_count % FALLBACK_RESCAN_EVERY_N_POLLS) == 0

	local gone_ui_id = nil    -- set when a fire proves a unit is gone this tick

	for i = 1, #tracked_units do
		local script_unit = tracked_units[i]
		local unit = script_unit and script_unit.unit

		-- Only look at units still alive on the field.
		if unit ~= nil and unit:number_of_men_alive() > 0 then
			-- The routing guard's ONE read for this unit this poll (section
			-- 7d): every ability below reuses this same value.
			local routing = unit_is_routing(unit)
			local ui_id = unit:unique_ui_id()
			local ability_key = target_key_by_unit[ui_id]

			-- Nothing of ours on this unit yet. THE IDENTITY WATCH (item
			-- 3.4): at the old 4 s cadence the cheap identity read runs
			-- INSTEAD of a full scan - unit_identity (section 4), one
			-- pcall'd battle_unit:type() - and the unit is re-scanned
			-- ONLY when that value CHANGES (a transformation / a mount
			-- moves the land_units key, so a loadout that gained
			-- abilities mid-battle is picked up and its new abilities
			-- arm and fire). The very first check merely records the
			-- value: the unit was already scanned when it entered the
			-- watch list, and the slow fallback below is the
			-- late-attachment insurance. THE SLOW SAFETY FALLBACK: one
			-- full scan every 60 s whatever the identity says, so an
			-- unreadable or unchanging identity degrades to the old
			-- behaviour, just far rarer.
			if ability_key == nil and (do_redetect or do_fallback_rescan) then
				local id_text = tostring(ui_id)
				local old_identity = identity_by_unit[id_text]
				local new_identity = unit_identity(unit)
				identity_by_unit[id_text] = new_identity

				local identity_moved = (old_identity ~= nil and new_identity ~= nil
					and new_identity ~= old_identity)
				local rescan = identity_moved or do_fallback_rescan

				if rescan then
					local found, all_keys = scan_unit_abilities(unit)
					owned_keys_by_unit[id_text] = our_keys_of(all_keys)   -- refresh the owned-key cache
					-- item 1.3: the learned keys change this unit's
					-- owned-ability list, so rebuild it too...
					owned_abilities_by_unit[id_text] =
						owned_abilities_of(owned_keys_by_unit[id_text])
					-- ...and tell item 1.4: the owned keys were just
					-- learned, so the active set (the UI tick's
					-- badge paths) must see them at once. Silent
					-- unless the membership actually moved.
					refresh_active_abilities()
					-- ONE line, and ONLY when the re-scan discovered
					-- something of ours - completely silent otherwise
					-- (a re-scan that finds nothing writes nothing).
					if found ~= nil then
						target_key_by_unit[ui_id] = found
						ability_key = found
						local why = "fallback rescan"
						if identity_moved then
							why = "identity changed (" .. tostring(old_identity)
								.. " -> " .. tostring(new_identity) .. ")"
						end
						log("re-scan: unit " .. tostring(ui_id) .. " " .. why
							.. " - keys: " .. table.concat(all_keys, ", "))
					end
				end
			end

			-- One pass per ability (section 1): its own per-UNIT switch, its
			-- own trigger, then the readiness gate and the short guard.
			-- ITEM 1.3: iterate only the markers THIS unit OWNS - the list
			-- the scan cached (owned_abilities_by_unit, section 2), mapped
			-- from the owned DB keys and variant-deduped, so a unit carrying
			-- one of three abilities costs ONE evaluation instead of three.
			-- A unit whose owned-key cache is UNKNOWN (nil - never scanned)
			-- falls back to the FULL table, exactly like today, so no unit
			-- is ever silently skipped.
			local unit_abilities = owned_abilities_by_unit[tostring(ui_id)]
			if unit_abilities == nil then
				unit_abilities = ABILITIES
			end
			for _, ability in ipairs(unit_abilities) do

				-- THE PER-UNIT SWITCH: this (unit, ability) pair must be
				-- armed. Nothing fires for a unit the player has not armed -
				-- two units carrying the same ability are independent.
				if is_armed(unit, ability.marker) then
					local reason = nil

					if ability.trigger == "charge" then
						-- The existing charge conditions, verbatim (section 5).
						local m = measure_charge(unit)

						if FIRE_ON_CHARGE and m.charging and not routing then
							reason = string.format(
								"charging (gap=%.1fm dist=%.1fm eta=%.1fs)",
								m.order_gap, m.target_dist, m.ttc)
						elseif FIRE_ON_MELEE and m.melee and not routing then
							reason = "in melee"
						end
					elseif ability.trigger == "running" then
						-- The engine's own run-versus-walk test.
						if unit:is_moving_fast() and not routing then
							reason = "running"
						end
					elseif ability.trigger == "melee" then
						-- The engine's own in-melee test (the ability's
						-- own AI usage is augment_melee_area).
						if unit:is_in_melee() and not routing then
							reason = "in melee"
						end
					end

					if reason ~= nil then
						-- The readiness gate: the engine's own check.
						-- One query, on the key this unit was found to
						-- own (section 2); the variant list is walked
						-- only when no usable key is cached, and the
						-- answer is logged on this evaluation.
						local ready_key, readiness = check_readiness(unit, ability, ability_key)
						log("  readiness " .. ability.marker .. " on ui id " .. tostring(ui_id)
							.. ": " .. readiness)

						if ready_key ~= nil then
							-- The SHORT SAFETY BRAKE, alongside the readiness
							-- gate: one attempt per (unit, ability) per
							-- GUARD_SECONDS. No 60/90 s timers anywhere.
							local guard = last_attempt_at[ui_id]
							local last_attempt = (guard ~= nil and guard[ability.marker]) or -999999

							if (tick_count - last_attempt) >= GUARD_TICKS then
								if guard == nil then
									guard = {}
									last_attempt_at[ui_id] = guard
								end
								guard[ability.marker] = tick_count
								-- THE OUTCOME (this build): "gone" means the
								-- pre-fire check or an engine rejection proved
								-- this unit is no longer there. Leave the walk
								-- and drop it after the loop (never mid-iteration).
								local outcome = attempt_activation(script_unit, unit, ready_key, reason,
									ui_id, ability.marker)
								if outcome == "gone" then
									gone_ui_id = ui_id
									break
								end
							end
						end
					end
				end
			end
			if gone_ui_id ~= nil then break end
		end
	end
	if gone_ui_id ~= nil then
		drop_unit_by_ui_id(gone_ui_id)
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

local logged_no_parent = false

-- (The single button reference, watch chain and feedback flag that used to sit
--  here are per ability now - ability_state[marker].button / .watch_chain /
--  .feedback_on, section 2.)

-- THE FEEDBACK: a plain image swap on the ability icon. Static - no pulse, no blink.
-- The icon slot is the one the vanilla layout marks with icon_index = 8 (round 21's layout read).
-- Both paths are read off / given by the game, so nothing has to resolve a guessed skin path.
local ICON_INDEX = 8
local original_icon = nil          -- whatever the button was showing before we touched it

local function read_icon(button)
	if button == nil then return nil end
	local ok, path = pcall(function() return button:GetImagePath(ICON_INDEX) end)
	if ok then return tostring(path) end
	return nil
end

local original_state = nil

-- THE BADGES - one per ability (option B, done right). Rounds 32-33 measured two things: an
-- engine-owned ability button does not draw children, and writing to it rebuilds it. So each
-- badge is created on the button's own ancestor (a plain container, the kind that demonstrably
-- draws components we create). Reading the button is safe; only writing to it is fatal.
--
-- Each ability has ONE badge component (the id from the table in section 1: zz_auto_badge for
-- Deadly Onslaught, zz_auto_badge_fs for Foe-Seeker), created HIDDEN and SHOWN only while ITS
-- ability is positively confirmed on the dial (the ui_tick test at the bottom of the file).
-- Its letter shows the collective switch for this ability (ONE selected unit: that unit's own
-- switch; SEVERAL: A only while every selected owner is armed) - "A" = armed/auto, "M" =
-- manual - and a click on it flips the selected owners' pairs (the checkbox rule, section 10):
-- the only control.
-- The components and flags live in ability_state[marker] (section 2).
local badge_parent = nil
local track = false          -- no computed tracking: the frames of reference do not match
                             -- (round 42). Position is the hand-tuned offset above.
local BADGE_X, BADGE_Y = -865, -209   -- the spot tuned by hand in-game (round 41), used as-is.
                                     -- MINUS is left/up, PLUS is right/down, from the bottom-centre
                                     -- dock of the badge's parent. Each ability's badge adds its
                                     -- own ox/oy from the table in section 1 (foe_seeker:
                                     -- +70,+30 - the measured top-slot-to-45-degree step), so a
                                     -- re-tune of these two numbers carries Foe-Seeker along.

-- THE MEASURED WHEEL (this build): the visible wheel is a circle centred
-- (95,944) radius 99 with six slots ~45 degrees apart; the six positions
-- below were measured over two battles. Deadly Onslaught sat on slot 1 (top)
-- in every observation - the slot the hand-tuned BADGE_X/BADGE_Y above were
-- tuned for - so slot 1 is the reference (WHEEL_TOP_X/WHEEL_TOP_Y).
--
-- WHICH SLOT AN ABILITY SITS ON IS ITS BAR POSITION: the claimed button's
-- ORDINAL among the key-bearing children of its parent bar (button_parent -
-- where the claimed buttons actually live) equals its wheel slot number,
-- 1-based. The claim walk counts it into slot_index (bar_ordinal_for,
-- section 8b), and every badge's offset is then
--     BADGE_X + (WHEEL_SLOT[k][1] - WHEEL_TOP_X),
--     BADGE_Y + (WHEEL_SLOT[k][2] - WHEEL_TOP_Y)
-- - that slot's delta from the top slot - so an ability on any of the six
-- slots gets the hand-tuned pair moved to its slot, and re-tuning the Deadly
-- Onslaught badge (zz_badge_set) still carries every other ability along.
-- Only when k is unknown (no claim yet, the bar unreadable, or more than six
-- key-bearing children - unexpected) does the badge fall back to section 1's
-- ox/oy pair, and that use is logged.
local WHEEL_TOP_X, WHEEL_TOP_Y = 96, 845

-- The six measured wheel slot positions, in slot order: 1 top (96,845),
-- 2 the 45-degree slot, 3 right, 4 the -45-degree slot, 5 the 135-degree
-- slot, 6 left. WHEEL_SLOT[k] is where the ability whose bar position is k
-- sits on the wheel.
local WHEEL_SLOT = {
	{ 96, 845 },      -- 1 - top (the hand-tuned reference slot)
	{ 166, 875 },     -- 2 - 45 degrees
	{ 194, 947 },     -- 3 - right
	{ 162, 1017 },    -- 4 - -45 degrees
	{ 28, 877 },      -- 5 - 135 degrees
	{ 2, 949 },       -- 6 - left
}

-- THE DEFERRED, STEPPED BADGE CREATION. The scan walk only records the button
-- and raises pending_badge[marker]; the badge is built HERE, on the ui tick,
-- one engine call group at a time, and every step is pcall'd and bracketed by
-- its own log lines ("step N <name>", then "step N ok" / "step N err: ..."),
-- so the last line of a crashed log names the step that died. A failed step
-- leaves the badge ABSENT (state.badge = nil) and the next tick tries again,
-- up to MAX_BADGE_ATTEMPTS per claim; after that the marker gives up until
-- the dial rebuilds (a fresh claim resets the budget).
--
-- The calls themselves are the stable single-badge path's, unchanged: the
-- same parent walk to hud_battle, the same template layout, the same
-- docking/resize/art-blank/SetText/place calls - only split into steps.
local MAX_BADGE_ATTEMPTS = 3

-- THE BADGE OFFSET, DERIVED FROM THE CLAIMED BUTTON'S BAR POSITION (this
-- build). slot_index[marker] is the claimed button's 1-based position among
-- the key-bearing children of its parent bar - which two measured battles
-- proved IS the wheel slot. When it is a slot number 1..6, the offset is
-- BADGE_X/BADGE_Y - the hand-tuned pair for the measured TOP slot (slot 1,
-- WHEEL_TOP_X/WHEEL_TOP_Y) - shifted by this slot's delta from that top slot,
-- through the static WHEEL_SLOT table above. Only when k is unknown (never
-- claimed, the bar unreadable, or more than six key-bearing children) does
-- it fall back to section 1's ox/oy pair (onslaught BADGE_X/BADGE_Y,
-- foe_seeker BADGE_X+70/BADGE_Y+30); the callers log which one was used.
-- Returns: ox, oy, wheel (slot number, nil on fallback), slot_x, slot_y.
local function badge_offsets_for(marker)
	local ability = ability_for(marker)
	if ability == nil then return nil end
	local k = slot_index[marker]
	if k ~= nil and k >= 1 and k <= 6 then
		local slot = WHEEL_SLOT[k]
		if slot ~= nil then
			return BADGE_X + (slot[1] - WHEEL_TOP_X), BADGE_Y + (slot[2] - WHEEL_TOP_Y),
				k, slot[1], slot[2]
		end
	end
	return BADGE_X + ability.ox, BADGE_Y + ability.oy, nil, nil, nil
end

-- One instrumented step: opening breadcrumb, the step's engine calls inside a
-- pcall, then ok/err. Returns true when the step completed.
local function badge_step(marker, step_no, step_name, fn)
	log("badge " .. marker .. ": step " .. tostring(step_no) .. " " .. step_name)
	local ok, err = pcall(fn)
	if ok then
		log("badge " .. marker .. ": step " .. tostring(step_no) .. " ok")
	else
		log("badge " .. marker .. ": step " .. tostring(step_no) .. " err: " .. tostring(err))
	end
	return ok
end

-- THE LAYOUT NUDGE (this build): THE ONE LETTER WRITE below is this
-- function's only caller, and it runs immediately after every REAL letter
-- write - creation step 5, the badge-click/feedback path and the selection
-- refresh all write through that one primitive - asking the engine to
-- re-run its layout/repaint pass for the badge AND for the parent it was
-- created on (the same badge_parent the placement code uses); when no
-- parent is known the badge alone is nudged. Layout() is the only
-- redraw-adjacent call the game exposes to script, so it is the one lever
-- against the delay between a letter write and its pixels. Both calls are
-- pcall'd: an error is swallowed and never aborts a letter write - the
-- outcome is reported on the letter's own log line
-- ('layout ok=<true|false>', the failing side named). Never called on a
-- cache hit: a write that did not happen gets no nudge and no line.
local function nudge_badge_layout(state)
	local ok_badge = pcall(function() state.badge:Layout() end)
	local ok_parent = true
	if badge_parent ~= nil then
		ok_parent = pcall(function() badge_parent:Layout() end)
	end
	if ok_badge and ok_parent then return true end
	if not ok_badge then return false, "badge" end
	return false, "parent"
end

-- THE ONE LETTER WRITE (this build): every path that moves a badge's letter
-- goes through this function and NOTHING else writes a badge's text - the
-- SetText call and the layout nudge are one primitive, so a caller cannot
-- write the letter without repainting it. (Before this build the nudge
-- lived at each call site; a path that forgot it produced exactly the bare,
-- outcome-less letter lines the battle log kept showing, so the last
-- un-nudged writer is now structurally impossible.) state.last_letter is
-- the one shared cache and moves only when SetText did not raise, so a
-- failed write does not poison it and the next path retries. Returns the
-- SetText outcome plus the nudge's outcome, so the caller's line can carry
-- both.
local function write_badge_letter(state, letter)
	local ok_text = pcall(function() state.badge:SetText(letter) end)
	if ok_text then state.last_letter = letter end
	local ok_layout, layout_err = nudge_badge_layout(state)
	return ok_text, ok_layout, layout_err
end

-- THE DISCARD (this build): the one way a created badge leaves the engine
-- tree. Dropping the Lua reference does NOT remove a created component - it
-- stays parented to hud_battle forever, and a systematic-failure state would
-- leak one doomed component per tick (every retry creates one more). Every
-- site that abandons a created-but-unfinished badge - a failed creation
-- step, or a creation attempt that raised mid-way - calls this instead of
-- clearing the reference directly: with the reference live and the component
-- supporting Destroy, the engine call is made inside a pcall (an engine-side
-- refusal is swallowed and logged, never raised into the retry path), and
-- the reference is cleared whatever happened - the badge is dead to this
-- code either way. NEVER called on a placed, working badge: only the
-- discard-on-failure sites and the create-attempt cleanup.
local function discard_badge(state)
	if state == nil or state.badge == nil then return end
	local ok_has, has_destroy = pcall(function() return state.badge.Destroy ~= nil end)
	if ok_has and has_destroy then
		local ok_destroy, destroy_err = pcall(function() state.badge:Destroy() end)
		if not ok_destroy then
			log("badge discard: Destroy raised: " .. tostring(destroy_err))
		end
	end
	state.badge = nil
end

local function create_badge(marker)
	local state = ability_state[marker]
	local ability = ability_for(marker)
	if state == nil or ability == nil or state.button == nil or state.badge ~= nil then return false end

	-- STEP 1 - create: walk up to hud_battle (the proven parent) and create
	-- the component there. Same walk, same template as the stable path.
	if not badge_step(marker, 1, "create", function()
		local node = state.button
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
		state.badge = UIComponent(badge_parent:CreateComponent(ability.badge,
			"ui/templates/zz_auto_badge"))
		if state.badge == nil then error("CreateComponent returned nothing", 0) end
	end) then
		state.badge = nil
		return false
	end
	local ok_cid, pid = pcall(function() return badge_parent:Id() end)
	log("badge [" .. marker .. "]: created on '" .. tostring(ok_cid and pid or "?")
		.. "' (not on the ability button)")

	-- STEP 2 - dock the fresh component to the top-left of its parent.
	if not badge_step(marker, 2, "dock", function()
		state.badge:SetDockingPoint(0)
	end) then
		discard_badge(state)
		return false
	end

	-- STEP 3 - resize: room for the letter.
	if not badge_step(marker, 3, "resize", function()
		state.badge:Resize(24, 24)
	end) then
		discard_badge(state)
		return false
	end

	-- STEP 4 - blank art: the letter carries the look, so the template's own
	-- title-bar art is blanked on every slot (0-4). A failed art WRITE fails
	-- the step; a failed read is logged as '?' and does not (stable's rule).
	if not badge_step(marker, 4, "blank art", function()
		for i = 0, 4 do
			state.badge:SetImagePath("ui/zz_auto/blank.png", i)
			local ok_r, rep = pcall(function() return state.badge:GetImagePath(i) end)
			log("   badge [" .. marker .. "] art slot " .. i .. " -> '"
				.. tostring(ok_r and rep or "?") .. "'")
		end
	end) then
		discard_badge(state)
		return false
	end

	-- STEP 5 - SetText: the letter is supplied here (our copy of a vanilla
	-- text layout; SetText exists, SetTextColour does not). The letter shows
	-- the COLLECTIVE armed state for this ability (ONE selected unit: exactly
	-- the old read - the single unit's own flag; SEVERAL: A only while every
	-- selected unit that owns the ability is armed), and the write - the
	-- SetText call, its layout nudge and the state.last_letter cache update
	-- - goes through THE ONE LETTER WRITE like every later write, so this
	-- first write cannot repaint any differently from the others. A SetText
	-- that raises still fails this step (the badge is discarded and the
	-- next tick retries), so ok_text is always true by the time the line is
	-- logged.
	if not badge_step(marker, 5, "SetText", function()
		local letter = collective_armed(marker) and "A" or "M"
		local ok_text, ok_layout, layout_err = write_badge_letter(state, letter)
		if not ok_text then error("SetText raised - discarding the badge", 0) end
		local ok_g, got = pcall(function() return state.badge:GetText() end)
		log("   badge [" .. marker .. "] set text ok=true engine reports='"
			.. tostring(ok_g and got or "?") .. "' layout ok=" .. tostring(ok_layout)
			.. (layout_err and (" (" .. layout_err .. ")") or ""))
	end) then
		discard_badge(state)
		return false
	end

	-- STEP 6 - place: HIDDEN AT BIRTH first (so a discarded badge can never
	-- linger on screen), then the stable's proven placement - dock point 8
	-- (bottom-centre) and THIS ability's own offset: derived from the bar
	-- position its button was claimed at (badge_offsets_for -> WHEEL_SLOT),
	-- or section 1's fallback pair when no bar position could be determined -
	-- and which one was used is logged.
	if not badge_step(marker, 6, "place", function()
		local ox, oy, wheel, sx, sy = badge_offsets_for(marker)
		state.badge_shown = false
		state.badge:SetVisible(false)
		state.badge:SetDockingPoint(8)                 -- 8 = bottom-centre
		state.badge:SetDockOffset(ox, oy)
		badge_parent:Layout()
		state.placed = true
		state.applied_ox, state.applied_oy = ox, oy
		local ok_pid, pid2 = pcall(function() return badge_parent:Id() end)
		if wheel ~= nil then
			log("badge " .. marker .. ": placed bottom-centre of '" .. tostring(ok_pid and pid2 or "?")
				.. "' (offset " .. tostring(ox) .. "," .. tostring(oy) .. ") [wheel slot "
				.. tostring(wheel) .. " (" .. tostring(sx) .. "," .. tostring(sy) .. ")] ok=true")
		else
			log("badge " .. marker .. ": using fallback offset ("
				.. tostring(ox) .. "," .. tostring(oy) .. ")")
			log("badge " .. marker .. ": placed bottom-centre of '" .. tostring(ok_pid and pid2 or "?")
				.. "' (offset " .. tostring(ox) .. "," .. tostring(oy) .. ") [fallback] ok=true")
		end
	end) then
		discard_badge(state)
		return false
	end
	return true
end

local function button_xy(button)
	if button == nil then return nil, nil end
	local ok, a, b = pcall(function() return button:Position() end)
	if ok and type(a) == "number" and type(b) == "number" then return a, b end
	return nil, nil
end

local function place_badge(marker)
	local state = ability_state[marker]
	local ability = ability_for(marker)
	if state == nil or state.badge == nil or ability == nil then return end

	-- The badge's own offset (this build): DERIVED FROM THE CLAIMED BUTTON'S
	-- BAR POSITION - badge_offsets_for reads slot_index (the 1-based position
	-- among the key-bearing children of the claimed button's parent bar, which
	-- IS the wheel slot) and moves the hand-tuned pair by that slot's delta
	-- from the measured top slot; only when no bar position is known does it
	-- fall back to section 1's ox/oy pair.
	local ox, oy, wheel, sx, sy = badge_offsets_for(marker)

	-- TRACK MODE (round 40): the two numbers above stop being "where on the bar" and become the
	-- constant delta from the ability button's OWN position, recomputed every tick. Tune the delta
	-- once with the console while tracking, and the badge follows that icon - and, per ability, its
	-- own icon, since each badge is created for its own button.
	if track then
		local bx, by = button_xy(state.button)
		if bx ~= nil then
			pcall(function() state.badge:SetDockOffset(bx + ox, by + oy) end)
		end
		return
	end

	-- Re-place when the offset has MOVED (a fresh claim can bring a new slot),
	-- not only the first time: state.applied_ox/applied_oy remember what is on
	-- screen, so an unchanged offset stays quiet.
	if state.placed and state.applied_ox == ox and state.applied_oy == oy then return end
	-- AI General's proven configuration, and nothing cleverer than it: dock the created component to
	-- the BOTTOM-CENTRE of the bar and give it one offset. Round 38 proved the engine both reinterprets
	-- offsets and misreports the component's position, so there is nothing to steer by - one shot, and
	-- the numbers above are the only knobs left.
	pcall(function() state.badge:SetDockingPoint(8) end)                 -- 8 = bottom-centre
	local ok_o = pcall(function() state.badge:SetDockOffset(ox, oy) end)
	pcall(function() badge_parent:Layout() end)
	state.placed = true
	state.applied_ox, state.applied_oy = ox, oy
	if wheel ~= nil then
		log("badge " .. marker .. ": placed bottom-centre of '" .. tostring(badge_parent:Id())
			.. "' (offset " .. tostring(ox) .. "," .. tostring(oy) .. ") [wheel slot "
			.. tostring(wheel) .. " (" .. tostring(sx) .. "," .. tostring(sy) .. ")] ok=" .. tostring(ok_o))
	else
		log("badge " .. marker .. ": using fallback offset ("
			.. tostring(ox) .. "," .. tostring(oy) .. ")")
		log("badge " .. marker .. ": placed bottom-centre of '" .. tostring(badge_parent:Id())
			.. "' (offset " .. tostring(ox) .. "," .. tostring(oy) .. ") [fallback] ok="
			.. tostring(ok_o))
	end
end

-- Re-place every ability's badge from the current BADGE_X/BADGE_Y (the console
-- hooks call this, so a re-tune of the Deadly Onslaught badge carries Foe-Seeker).
local function replace_all_badges()
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		if state ~= nil then
			state.placed = false
			pcall(place_badge, ability.marker)
		end
	end
end
local function badge_visible(marker, on)
	local state = ability_state[marker]
	if state == nil or state.badge == nil then return end
	state.badge_visible_state = on    -- legacy bookkeeping; the letter cache is state.last_letter now
	-- THE LETTER IS THIS PATH'S WHOLE JOB - it must NOT touch visibility any
	-- more. The unconditional SetVisible(true) that used to sit here is one
	-- of the paths that left a stale badge visible while its marker was not
	-- on the dial (a card click or a toggle re-showed a badge the tick had
	-- hidden). Visibility now belongs to the ui tick's claimed-set logic
	-- alone, which re-applies the desired state on every single tick.
	-- THE CACHE (this build): the letter line happens ONLY when the desired
	-- letter differs from state.last_letter - the one shared cache every
	-- letter write updates - so a path that calls this with a letter the
	-- badge already shows is completely silent. A changed letter goes
	-- through THE ONE LETTER WRITE (SetText plus the layout nudge in one
	-- primitive) so the engine repaints it sooner and no caller can skip the
	-- nudge; a cache hit writes nothing and nudges nothing.
	local letter = on and "A" or "M"
	if state.last_letter == letter then return end
	local ok_t, ok_layout, layout_err = write_badge_letter(state, letter)
	log("   badge [" .. marker .. "] letter='" .. letter .. "' (auto "
		.. (on and "ON" or "OFF") .. ") layout ok=" .. tostring(ok_layout)
		.. (layout_err and (" (" .. layout_err .. ")") or "")
		.. " visible=" .. tostring(state.badge_shown == true)
		.. " text=" .. tostring(ok_t))
end

-- THE LETTER CACHE AND THE ONE LETTER WRITE (this build). The desired letter
-- is the COLLECTIVE armed state for this ability (collective_armed, section
-- 4): ONE selected unit - exactly the single unit's armed flag, as before;
-- SEVERAL selected units - "A" only while EVERY selected unit that owns the
-- ability is armed, "M" the moment any member is off or none owns it. The
-- write runs ONLY when the desired letter differs from state.last_letter -
-- the cache of what the badge was last told to show - so a steady letter is
-- never re-written and the per-tick safety net can run on every tick (any
-- change converges on screen within one tick; a write that failed does not
-- move the cache and is retried by the next path). Every actual write goes
-- through THE ONE LETTER WRITE (write_badge_letter: SetText + the layout
-- nudge in a single primitive) and its line carries the nudge's outcome
-- right after the letter; force_line additionally logs the line when the
-- letter was already correct (the selection-change refresh uses that, so its
-- header is followed by one line per badge whatever they show - a forced
-- line wrote nothing and is marked '(no write)', so no log reader can
-- mistake it for a write that skipped its nudge). Returns true when the
-- letter changed.
local function refresh_badge_letter(marker, force_line)
	local state = ability_state[marker]
	if state == nil or state.badge == nil then return false end
	local on = collective_armed(marker)
	local letter = on and "A" or "M"
	if state.last_letter == letter then
		if force_line then
			log("   badge [" .. marker .. "] letter='" .. letter .. "' (auto "
				.. (on and "ON" or "OFF") .. ") (no write)")
		end
		return false
	end
	local ok_text, ok_layout, layout_err = write_badge_letter(state, letter)
	log("   badge [" .. marker .. "] letter='" .. letter .. "' (auto "
		.. (on and "ON" or "OFF") .. ") layout ok=" .. tostring(ok_layout)
		.. (layout_err and (" (" .. layout_err .. ")") or ""))
	return true
end

-- THE SELECTION CHANGED - refresh BOTH badges' letters from the new
-- selection, immediately (this build). Called from every path that sets
-- selected_unit_id (the fast card path on every ui tick, the once-per-second
-- census when it adopts first, the card click fast-path), in the same call,
-- so the letters never lag the selection. Logged once per change: the header
-- line names the new selection, followed by each existing badge's own letter
-- line (the write inside still runs only when a letter actually changed -
-- the cache above; a forced line says '(no write)').
-- THE OPTIONAL TICK (this build) stamps the header with the battle clock:
--   selection changed to <ui_id> - refreshing badge letters (tick N)
-- The fast card path (section 8e) passes tick_count, so an adoption can be
-- measured against the tick it happened on; the click path and the census
-- call it without a tick and keep their headers exactly as they were.
local function refresh_badge_letters_for_selection(new_id, tick)
	local header = "selection changed to " .. tostring(new_id or "none")
		.. " - refreshing badge letters"
	if tick ~= nil then
		header = header .. " (tick " .. tostring(tick) .. ")"
	end
	log(header)
	for _, ability in ipairs(active_abilities_list()) do
		refresh_badge_letter(ability.marker, true)
	end
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
	-- re-place EVERY ability's badge: each one's offset is computed in
	-- place_badge (its wheel slot's delta when its bar position is known,
	-- its own ox/oy otherwise), so a re-tune of the Deadly Onslaught badge
	-- carries Foe-Seeker along.
	replace_all_badges()
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
	local master = ability_state[ABILITIES[1].marker]
	local bx, by = button_xy(master ~= nil and master.button or nil)
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
	replace_all_badges()
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

function zz_badge_show(marker)
	marker = marker or "onslaught"
	local state = ability_state[marker]
	if state == nil or state.badge == nil then return "badge not created yet" end
	state.badge_shown = true    -- the next ui tick re-checks this against the claimed set
	pcall(function() state.badge:SetVisible(true) end)
	local ability = ability_for(marker)
	return "badge shown at " .. tostring(BADGE_X + ability.ox) .. "," .. tostring(BADGE_Y + ability.oy)
end

function zz_badge_hide(marker)
	marker = marker or "onslaught"
	local state = ability_state[marker]
	if state == nil or state.badge == nil then return "badge not created yet" end
	state.badge_shown = false   -- the next ui tick re-checks this against the claimed set
	pcall(function() state.badge:SetVisible(false) end)
	return "badge hidden"
end

function zz_badge_parent(marker)
	marker = marker or "onslaught"
	if badge_parent == nil then return "no parent yet" end
	local ability = ability_for(marker)
	if ability == nil then return "no ability with marker '" .. tostring(marker) .. "'" end
	local state = ability_state[marker]
	local ok, id = pcall(function() return badge_parent:Id() end)
	local ok2, w = pcall(function() return badge_parent:Width() end)
	local ok3, h = pcall(function() return badge_parent:Height() end)
	local bx, by = button_xy(state ~= nil and state.button or nil)
	local msg = "BADGE parent=" .. tostring(ok and id or "?") .. " size=" .. tostring(w)
		.. "x" .. tostring(h) .. " offset=" .. tostring(BADGE_X + ability.ox) .. ","
		.. tostring(BADGE_Y + ability.oy)
		.. " track=" .. tostring(track) .. " button=" .. tostring(bx) .. "," .. tostring(by)
		.. " marker=" .. tostring(marker)
	log(msg)
	return msg
end

local function set_armed_look(marker, on)
	-- Availability is NEVER touched: the ability can always be used by hand.
	-- The state is shown by the badge instead.
	badge_visible(marker, on)
end
local function apply_ability_feedback(marker)
	local state = ability_state[marker]
	if state == nil or state.button == nil then return end
	local on = collective_armed(marker)            -- the collective state (one unit: its own flag)
	if state.feedback_on == on then return end     -- nothing to change

	set_armed_look(marker, on)
	state.feedback_on = on
end

-- The one place a per-unit switch is flipped, whichever control did it
-- (currently: a click on the ability's M/A badge - the click handler calls
-- this once per unit its checkbox rule acts on). The state belongs to ONE
-- (unit, ability) pair; every other unit's state for the same ability is
-- untouched. The letter line comes from apply_ability_feedback right after,
-- so a toggle always reports both what changed and what the badge now shows.
local function set_auto_for_unit(ui_id, marker, value)
	local id = unit_slot(ui_id)
	local per = armed[id]
	if per == nil then
		per = {}
		armed[id] = per
	end
	per[marker] = value == true
	log("AUTO " .. tostring(marker) .. " for unit " .. tostring(ui_id) .. ": now "
		.. (value and "ON" or "OFF"))
	apply_ability_feedback(marker)   -- the letter on the badge - the only feedback now
end

-- Find the ability icon. Round 18 showed the engine's own highlight path
-- (battle_orders/orders_parent/behaviour_parent) is the fire-at-will/skirmish row: for Boris
-- all three slots report an EMPTY ability key, so Deadly Onslaught is not there. So scan the
-- HUD instead, bounded, and ask every component the one question the engine documents for
-- identifying an ability button - InterfaceFunction("AbilityKeyForScript") - logging each hit
-- with its Address(). A scan that finds nothing still reports how far it got.
local walk_visits = 0
local walk_skipped = 0        -- components this scan skipped after an error

-- ============================================================================
-- 1a's logging helpers (the switch itself, CLAIM_BISECT, sits in section 1a).
-- Every claim-test operation runs between a bisect_enter() and its bisect_ok()
-- (or bisect_fail(), when the operation itself errored). REMOVED steps (7-8,
-- the find that killed the engine) run nothing and always log their removal.
-- A DISABLED step logs SKIPPED and its result simply does not contribute -
-- the claim verdict falls back to 'not ours' and the walk keeps going.
-- ============================================================================

local last_key_type = nil     -- bisect step 1's answer, for the scan probe line

-- What each step may log per battle (an enter/ok pair = 1, a SKIPPED line = 1)
-- before it goes quiet. The crash this hunt is after happens on the FIRST
-- key-bearing component, so a small budget loses no evidence - it only keeps
-- a long battle's log readable.
local BISECT_LINE_CAP = 40

local bisect_slots_used = {}  -- step -> line-events written so far
local bisect_muted = {}       -- step -> true once its budget is spent

local function bisect_on(step)
	return step <= CLAIM_BISECT
end

-- One slot per logged event; the ok/fail line rides the entering line's slot,
-- so an `entering` with no `ok` (and no `FAILED`) after it can ONLY mean the
-- game itself died inside that operation - which is exactly the signal.
local function bisect_slot(step)
	local used = bisect_slots_used[step] or 0
	if used < BISECT_LINE_CAP then
		bisect_slots_used[step] = used + 1
		return true
	end
	if not bisect_muted[step] then
		bisect_muted[step] = true
		log("bisect: step " .. tostring(step) .. " - further lines suppressed for this battle (cap "
			.. tostring(BISECT_LINE_CAP) .. ")")
	end
	return false
end

-- Immediately BEFORE the step's operation. Returns enabled, shown.
local function bisect_enter(step, name)
	local enabled = bisect_on(step)
	local shown = bisect_slot(step)
	if shown then
		log("bisect: step " .. tostring(step) .. " " .. name
			.. (enabled and " entering" or " SKIPPED (disabled)"))
	end
	return enabled, shown
end

-- Immediately AFTER the step's operation completed cleanly.
local function bisect_ok(step, name, shown)
	if shown and bisect_on(step) then
		log("bisect: step " .. tostring(step) .. " " .. name .. " ok")
	end
end

-- The operation ran but failed (pcall caught it): the step is NAMED in the
-- log instead of an 'ok' line that would be a lie.
local function bisect_fail(step, name, shown, err)
	if shown and bisect_on(step) then
		log("bisect: step " .. tostring(step) .. " " .. name .. " FAILED: " .. tostring(err))
	end
end

-- A REMOVED SLOT (steps 7-8). The operation that used to sit here was
-- string.find - the four-argument plain form is what the bisect caught
-- killing the engine - and no find of any kind remains in the match paths.
-- The slot still logs so the ladder's record stays honest: it names the
-- removal, never `entering`/`ok`, at any level (there is no operation left
-- to enable or disable).
local function bisect_removed(step, name)
	if bisect_slot(step) then
		log("bisect: step " .. tostring(step) .. " " .. name
			.. " SKIPPED (equality match - find removed)")
	end
end

local function bisect_summary()
	local bits = {}
	for step = 1, 9 do
		bits[#bits + 1] = tostring(step) .. (bisect_on(step) and "=on" or "=off")
	end
	return table.concat(bits, " ")
end

-- A FRESH PLAIN-LUA COPY OF WHATEVER THE ENGINE RETURNED. The value a read
-- like InterfaceFunction("AbilityKeyForScript") answers with has passed
-- `type(key) == "string"` and still killed the game the moment it reached a C
-- string function (the crashed sessions' last line was the walk's own header
-- for our key - `.. key ..` printed fine just before the crash; the
-- `^ that one is ours` line and the claim line never followed, and between
-- them the only work was string.lower / find in key_is_ours below). The
-- bisect later named the killer: the four-argument plain-mode find, now
-- removed entirely - the match is exact key equality and runs on the copy
-- only. So nothing in the claim path ever hands the engine's value to a
-- string function: the copy is made by Lua's own concatenation - the one
-- operation the engine's value provably survives - with tostring as the
-- fallback, pcall'd like everything else here. nil when even that fails.
local function as_plain_string(v)
	if v == nil then return nil end

	-- BISECT STEP 1 - type(v): the value's Lua type (remembered for the probe).
	local on1, shown1 = bisect_enter(1, "type(v)")
	if on1 then
		local ok1, t1 = pcall(type, v)
		if ok1 then
			last_key_type = t1
			bisect_ok(1, "type(v)", shown1)
		else
			bisect_fail(1, "type(v)", shown1, t1)
		end
	end

	-- BISECT STEP 2 - tostring(v): pcall'd, the copy's fallback source.
	local text = nil
	local on2, shown2 = bisect_enter(2, "tostring(v)")
	if on2 then
		local ok2, t2 = pcall(tostring, v)
		if ok2 and type(t2) == "string" then
			text = t2
			bisect_ok(2, "tostring(v)", shown2)
		else
			bisect_fail(2, "tostring(v)", shown2,
				ok2 and "tostring answered a non-string" or t2)
		end
	end

	-- BISECT STEP 3 - v .. "": the fresh plain copy; tostring is the fallback.
	local on3, shown3 = bisect_enter(3, "v .. '' (concat copy)")
	if on3 then
		local ok_copy, copied = pcall(function() return v .. "" end)
		if ok_copy and type(copied) == "string" then
			bisect_ok(3, "v .. '' (concat copy)", shown3)
			return copied
		end
		bisect_fail(3, "v .. '' (concat copy)", shown3,
			ok_copy and "the concat did not make a plain string" or copied)
	end
	return text
end

-- A LENGTH READ MUST NEVER KILL THE SCAN. The engine can hand back a STRING
-- from a length read on these long ability keys (the in-battle failure this
-- guards: `string.len(key) > 3` raised "attempt to compare string with number"
-- and killed the whole walk before the button was ever claimed). The value is
-- copied FIRST (as_plain_string) - the length read and the # fallback below
-- only ever act on the copy, never on the engine value. The read is pcall'd,
-- the # operator is the language-level fallback, and nil means "unreadable".
local function safe_len(s)
	local plain = as_plain_string(s)
	if plain == nil then return nil end

	-- BISECT STEP 4 - string.len on the copy.
	local n = nil
	local on4, shown4 = bisect_enter(4, "string.len on the copy")
	if on4 then
		local ok4, n4 = pcall(string.len, plain)
		if ok4 and type(n4) == "number" then
			n = n4
			bisect_ok(4, "string.len on the copy", shown4)
		else
			bisect_fail(4, "string.len on the copy", shown4,
				ok4 and "the length read answered a non-number" or n4)
		end
	end
	if n ~= nil then return n end

	-- BISECT STEP 5 - # on the copy (the language-level fallback).
	local on5, shown5 = bisect_enter(5, "# on the copy")
	if on5 then
		local ok5, n5 = pcall(function() return #plain end)
		if ok5 and type(n5) == "number" then
			n = n5
			bisect_ok(5, "# on the copy", shown5)
		else
			bisect_fail(5, "# on the copy", shown5,
				ok5 and "the # read answered a non-number" or n5)
		end
	end
	return n
end

-- IS THIS BUTTON SHOWING THIS ABILITY? The claim test is the KEY ALONE - no
-- Id(): on a real ability button the engine answers Id() with a function (the
-- quirk the battle log printed as 'function: 0000000154EC9390') or fails
-- outright, so anything Id-gated rejects every ability button before its key
-- is ever considered. The match is EXACT KEY EQUALITY, hardened like safe_len
-- AND COPY-FIRST: string.lower only ever sees a fresh plain copy of the key
-- (as_plain_string), and the lowered copy is then compared, character for
-- character, against every key listed for the ability in ABILITIES (section
-- 1) - the table is the single source of truth. No find of any kind runs
-- here any more: the bisect proved the four-argument plain-mode string.find
-- kills the engine (the log's last line was `bisect: step 7 string.find
-- plain entering`, with no `ok`), so steps 7-8 are removed slots that only
-- log the removal and contribute nothing to the verdict.
--
-- THE NARROWING IS DELIBERATE: a key that merely CONTAINS an ability's name
-- (e.g. 'zz_wh_main_character_abilities_deadly_onslaught_xx') no longer
-- claims. Only the exact keys listed in ABILITIES are accepted - and the
-- scan probe prints every key-bearing component we did not claim (ours=no),
-- so an unknown engine variant shows up in the battle log immediately and
-- the fix is one line in the table.
--
-- THE BISECT (section 1a) splits this sequence into steps 6-9: at level 9 the
-- behaviour is the equality match; a disabled step logs SKIPPED and its
-- result simply does not contribute, so the verdict falls back to 'not ours'.
-- (The lower is pcall'd on its own, so an error in it is NAMED, not a silent
-- skip - and if it fails, the un-lowered copy is compared instead: a
-- misbehaving helper must not lose a button.)
local function key_is_ours(ability, key)
	if ability == nil then return false end
	local plain = as_plain_string(key)
	if plain == nil then return false end

	-- BISECT STEP 6 - string.lower on the copy.
	local lowered = nil
	local on6, shown6 = bisect_enter(6, "string.lower on the copy")
	if on6 then
		local ok6, l6 = pcall(string.lower, plain)
		if ok6 then
			lowered = l6
			bisect_ok(6, "string.lower on the copy", shown6)
		else
			bisect_fail(6, "string.lower on the copy", shown6, l6)
		end
	end

	-- BISECT STEPS 7-8 - REMOVED SLOTS. Step 7 was `string.find plain` and
	-- step 8 `string.find pattern-form`; the bisect named the plain form as
	-- the killer, so both are gone from every match path. The slots always
	-- log their removal and run nothing - they can never crash, and the
	-- ladder's record of what happened stays honest.
	bisect_removed(7, "string.find plain")
	bisect_removed(8, "string.find pattern-form")

	-- BISECT STEP 9 - THE EQUALITY COMPARE, the verdict gate. Equality, not
	-- containment: the lowered copy must EQUAL one of the ability's listed
	-- keys (they are lowercase already). If the lower failed or its step was
	-- disabled, the un-lowered copy is compared instead.
	local verdict = false
	local on9, shown9 = bisect_enter(9, "the equality compare")
	if on9 then
		local candidate = lowered or plain
		for _, listed_key in ipairs(ability.keys) do
			if candidate == listed_key then
				verdict = true
			end
		end
		bisect_ok(9, "the equality compare", shown9)
	end
	return verdict
end

-- THE LIVE CLAIM TEST, shared by the ui tick and the badge click guard: a
-- marker is ON THE CURRENTLY SELECTED UNIT'S DIAL right now when its claimed
-- button reference still exists AND its key read passes key_is_ours - the
-- same gate the scan claimed it with. One test in one place, so a click can
-- never act on a badge the tick considers unclaimed (or the other way round).
local function marker_claimed_now(ability)
	if ability == nil then return false end
	local state = ability_state[ability.marker]
	if state == nil or state.button == nil then return false end
	local ok_k, key = pcall(function() return state.button:InterfaceFunction("AbilityKeyForScript") end)
	if ok_k and (safe_len(key) or 0) > 3 and key_is_ours(ability, key) then
		return true
	end
	return false
end

-- THE SCAN PROBE: every component that reported a key but was NOT claimed is
-- recorded here (up to scan_probe_cap), and find_ability_buttons writes the
-- block - rate-limited - so a seen-but-unclaimed button can never be silent
-- again. ours= says whether our own matcher would have claimed it.
local scan_probe_queue = {}
local scan_probe_cap = 3
local scan_probe_diag_cap = 2         -- keytype/copyok/lenok line: at most this many per write
local scan_count = 0                  -- how many scans this battle
local last_probe_claim_count = -1     -- claim count of the last probe block written

-- True when every ability has its dial button: the scan stops there.
local function all_buttons_found()
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		if state == nil or state.button == nil then return false end
	end
	return true
end

-- THE CLAIMED BUTTON'S 1-BASED POSITION AMONG THE KEY-BEARING CHILDREN OF
-- ITS PARENT BAR (this build). This is what maps to the wheel: two measured
-- battles showed the bar's key-bearing children sit in wheel order 1..6, so
-- the ordinal IS the slot number. ("Key-bearing" is the same gate the scan
-- walk uses: the child's key read passes safe_len > 3.) Every read here is
-- pcall'd exactly like the walk's, so no sibling - however hostile its key -
-- can kill the claim; a component whose reads fail simply does not count
-- (the badges then fall back, logged). "Ours" is found by IDENTITY first
-- (the component's own Address(), the stable per-component pointer the
-- battle log prints) and by EXACT key equality second (key_is_ours), so a
-- twin of our key earlier on the bar cannot steal our position. Returns
-- k >= 1, or nil when the parent or the children cannot be read.
local function bar_ordinal_for(uic, ability)
	if uic == nil or ability == nil then return nil end

	local ok_p, parent = pcall(function() return uic:Parent() end)
	if not ok_p or parent == nil then return nil end
	local ok_w, container = pcall(function() return UIComponent(parent) end)
	if not ok_w or container == nil then return nil end

	local ok_n, n = pcall(function() return container:ChildCount() end)
	if not ok_n or type(n) ~= "number" or n <= 0 then return nil end

	-- Our own address, for the identity test (nil when unreadable).
	local my_addr = nil
	local ok_my, my = pcall(function() return uic:Address() end)
	if ok_my and my ~= nil then my_addr = tostring(my) end

	local seen = 0
	for i = 0, n - 1 do
		local ok_c, child = pcall(function() return container:Find(i) end)
		if ok_c and child ~= nil then
			local ok_cw, cc = pcall(function() return UIComponent(child) end)
			if ok_cw and cc ~= nil then
				local ok_k, key = pcall(function() return cc:InterfaceFunction("AbilityKeyForScript") end)
				if ok_k and (safe_len(key) or 0) > 3 then
					seen = seen + 1

					local is_ours = false
					if my_addr ~= nil then
						local ok_a, addr = pcall(function() return cc:Address() end)
						if ok_a and addr ~= nil and tostring(addr) == my_addr then
							is_ours = true
						end
					end
					if not is_ours and key_is_ours(ability, key) then
						is_ours = true
					end

					if is_ours then return seen end
				end
			end
		end
	end
	return nil
end

-- ONE COMPONENT'S WORTH OF SCAN WORK. The walk below runs this inside its own
-- pcall, so no single component - however hostile its reads - can kill the
-- walk (the known in-game failure) or abort the scan silently.
local function scan_component_body(uic)
	local ok_key, key = pcall(function() return uic:InterfaceFunction("AbilityKeyForScript") end)
	if not ok_key then
		walk_skipped = walk_skipped + 1
		if walk_skipped <= 5 then
			log("scan: " .. tostring(walk_skipped) .. " component(s) skipped after an error: "
				.. tostring(key))
		end
	end
	-- The gate is the COPY's length (as_plain_string inside safe_len), not a
	-- type() test on the engine value: a value the engine dressed as anything
	-- other than a plain string still gets its chance, and nothing raw is
	-- string-op'd anywhere in this body.
	if ok_key and (safe_len(key) or 0) > 3 then
		-- The id is LOGGED for diagnostics but never judged: on a real ability
		-- button the engine can answer Id() with a function, or fail outright,
		-- and an un-pcall'd read here killed the whole body BEFORE the key was
		-- considered. Nothing in this block may reject the component - the
		-- claim below is the key alone.
		local ok_addr, addr = pcall(function() return uic:Address() end)
		local ok_id, id = pcall(function() return uic:Id() end)
		log("   ability button: key='" .. key .. "' id='" .. tostring(ok_id and id or "?")
			.. "' address=" .. tostring(addr))

		-- One claim per ability: the judgement is the KEY ALONE - it passed
		-- safe_len() > 3 in the gate above and must EQUAL one of the
		-- ability's listed keys, lowercased (key_is_ours; exact equality,
		-- no find of any kind). Every database variant listed in the table
		-- attaches; an unlisted variant shows up in the probe below.
		-- No Id check, no Id-based liveness gate in this path.
		local claimed = nil
		for _, ability in ipairs(ABILITIES) do
			local state = ability_state[ability.marker]
			if state.button == nil and key_is_ours(ability, key) then
				-- RECORD ONLY - nothing is created, painted or written to the
				-- engine from inside this walk. The reference and the flag are
				-- all a claim leaves behind; the ui tick builds the badge from
				-- the flag, step by step, instrumented (section 8b).
				state.button = uic
				pending_badge[ability.marker] = true
				badge_attempts[ability.marker] = 0
				badge_gave_up[ability.marker] = nil
				claimed = ability
				log("   ^ that one is ours (" .. ability.marker .. ")")
				log("claim: " .. ability.marker
					.. " button found - badge creation deferred to the tick")
				-- THE BAR POSITION (this build): the old live Position()
				-- read is GONE - it read the wrong widget (the claimed
				-- button lives in the HIDDEN BAR, so its Position() is a
				-- bar coordinate like (1130,1052), not a wheel slot, and
				-- the badges landed off-screen). What maps to the wheel is
				-- the button's 1-based position among the KEY-BEARING
				-- children of its parent bar - measured over two battles.
				-- bar_ordinal_for walks the siblings (every read pcall'd),
				-- and slot_index is refreshed on every claim; the badge's
				-- offset follows through WHEEL_SLOT (section 8b).
				local k = bar_ordinal_for(uic, ability)
				if k ~= nil and k >= 1 and k <= 6 then
					slot_index[ability.marker] = k
					local slot = WHEEL_SLOT[k]
					log("claim: " .. ability.marker .. " is bar position " .. tostring(k)
						.. " -> wheel slot (" .. tostring(slot[1]) .. "," .. tostring(slot[2]) .. ")")
				elseif k ~= nil then
					slot_index[ability.marker] = nil
					log("claim: " .. ability.marker .. " is bar position " .. tostring(k)
						.. " - MORE THAN SIX key-bearing bar children (unexpected) - badge will use its fallback offset")
				else
					slot_index[ability.marker] = nil
					log("claim: " .. ability.marker
						.. " bar position unreadable - badge will use its fallback offset")
				end
			end
		end

		-- The probe, collected here and written by find_ability_buttons: this
		-- component reported a key but did not become a button. ours=yes is
		-- the alarming case - our own matcher would have taken it.
		if claimed == nil and #scan_probe_queue < scan_probe_cap then
			local ours = false
			for _, ability in ipairs(ABILITIES) do
				if key_is_ours(ability, key) then
					ours = true
				end
			end
			local ok_id2, probe_id = pcall(function() return uic:Id() end)
			-- The key's own properties, so the next battle's log names exactly
			-- which of them is hostile: keytype is what the bisect's step 1
			-- (type(v)) answered for this value, copyok whether
			-- as_plain_string could make the fresh plain copy, lenok whether
			-- the copy measured (safe_len acts on the copy).
			scan_probe_queue[#scan_probe_queue + 1] = {
				id = tostring(ok_id2 and probe_id or "?"),
				key = key,
				keytype = last_key_type,
				copyok = (as_plain_string(key) ~= nil),
				lenok = (safe_len(key) ~= nil),
				ours = ours,
			}
		end

		if claimed ~= nil then
			-- NOTHING RUNS HERE ANY MORE. The claim used to continue with the
			-- event-reporter chain (7 x AddScriptEventReporter on the button and
			-- its ancestors), the container-chain walk, the icon/state reads and
			-- the feedback call - a dozen engine touches on a freshly claimed,
			-- engine-owned button, inside a walk, while the HUD may be mid-rebuild.
			-- The crashed session's log ends at the claim with no line after it,
			-- so a successful claim now leaves only the reference and the flag
			-- (above); every engine touch on the badge path happens on the ui
			-- tick, instrumented step by step (section 8b). The event reporters
			-- existed to hear right-clicks on the button - a control this mod no
			-- longer has (the M/A badge click is the only control).
			do end
		end
	end
end

local function scan_component(uic, depth)
	if uic == nil or depth > 6 or walk_visits > 4000 or all_buttons_found() then return end
	walk_visits = walk_visits + 1

	local ok_one, err_one = pcall(scan_component_body, uic)
	if not ok_one then
		walk_skipped = walk_skipped + 1
		if walk_skipped <= 5 then
			log("scan: " .. tostring(walk_skipped) .. " component(s) skipped after an error: "
				.. tostring(err_one))
		end
	end

	local ok_n, n = pcall(function() return uic:ChildCount() end)
	if ok_n and type(n) == "number" then
		for i = 0, n - 1 do
			local ok_c, child = pcall(function() return uic:Find(i) end)
			if ok_c and child ~= nil then
				local ok_r, err_r = pcall(function()
					scan_component(UIComponent(child), depth + 1)
				end)
				if not ok_r then
					walk_skipped = walk_skipped + 1
					if walk_skipped <= 5 then
						log("scan: " .. tostring(walk_skipped) .. " component(s) skipped after an error: "
							.. tostring(err_r))
					end
				end
			end
		end
	end
end

local function find_ability_buttons()
	if all_buttons_found() then return end
	walk_visits = 0
	walk_skipped = 0
	scan_probe_queue = {}
	scan_count = scan_count + 1

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

		local found = {}
		local claim_bits = {}
		local claimed_count = 0
		for _, ability in ipairs(ABILITIES) do
			local is_claimed = ability_state[ability.marker].button ~= nil
			if is_claimed then
				found[#found + 1] = ability.marker
				claimed_count = claimed_count + 1
			end
			claim_bits[#claim_bits + 1] = ability.marker .. "=" .. tostring(is_claimed)
		end
		log("   scan done: " .. tostring(walk_visits) .. " component(s) visited - "
			.. (#found > 0 and ("found: " .. table.concat(found, ", ")) or "none of ours found")
			.. " | scan: claimed " .. table.concat(claim_bits, " "))

		-- HANDLE HEALTH: a scan that cannot walk the HUD is never silent again.
		-- A HUD that has children yet yields a one-component walk is the known
		-- dead-handle signature (the engine rebuilt hud_battle), so it is
		-- called out too and the next scan re-fetches.
		local children_str = "invalid"
		local ok_hc, hc = pcall(function() return hud:ChildCount() end)
		if ok_hc and type(hc) == "number" then children_str = tostring(hc) end
		log("   scan: hud_battle children=" .. children_str .. " visits=" .. tostring(walk_visits)
			.. " skipped=" .. tostring(walk_skipped))
		if children_str == "invalid"
			or (ok_hc and type(hc) == "number" and hc >= 1 and walk_visits <= 1) then
			log("   scan: hud_battle handle unusable this scan - refetching next time")
		end

		-- THE PROBE: write the collected unclaimed keys, rate-limited to a
		-- claim-count change or every 10th scan, so a mismatch is never
		-- silent and the log stays readable.
		if #scan_probe_queue > 0
			and (claimed_count ~= last_probe_claim_count or (scan_count % 10) == 0) then
			for i = 1, #scan_probe_queue do
				local entry = scan_probe_queue[i]
				-- Up to scan_probe_diag_cap entries also get the key's property
				-- line, immediately before the ours verdict.
				if i <= scan_probe_diag_cap then
					log("scan probe: keytype=" .. tostring(entry.keytype)
						.. " copyok=" .. tostring(entry.copyok)
						.. " lenok=" .. tostring(entry.lenok))
				end
				log("scan probe: id='" .. entry.id .. "' key='" .. entry.key .. "' ours="
					.. (entry.ours and "yes" or "no"))
			end
			last_probe_claim_count = claimed_count
		end
	end)

	if not ok then log("ability icon scan failed: " .. tostring(err)) end

	-- ITEM 1.4 - the scan just ran: a claim (or a fresh owned-key read) may
	-- have changed the inputs, so refresh the active set. Silent unless it moved.
	refresh_active_abilities()
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
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		for i = 1, #state.watch_chain do
			local e = state.watch_chain[i]
			if e.addr ~= nil and context.component ~= nil and context.component == e.addr then
				return e.id or "?"
			end
		end
	end
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		for i = 1, #state.watch_chain do
			local e = state.watch_chain[i]
			if e.id ~= nil and context.string == e.id then return e.id end
		end
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
			-- (the right-click toggle is gone: the badge click is the only control)
		else
			if rclick_other < 15 then
				rclick_other = rclick_other + 1
				log("RCLICK: right-click on '" .. tostring(context.string) .. "' - not ours")
			end
		end
	end,
	true
)

-- (2) THE KEYBOARD: gone. The shortcut listeners and their on_shortcut helper were deleted,
-- so pressing '8' (usegroup8) no longer reaches the mod at all. The badge click is the only control.

-- (3) THE CONTROL: a left-click on the same icon, which happens whenever the ability is used -
-- so this one is seen without the player doing anything special. If this reports and the
-- right-click does not, the reporter works and the engine simply never raises the right-click.
local lclick_other = 0
core:add_listener(
	"zz_deadly_onslaught_lclick_control",
	"ComponentLClickUp",
	function(context) return true end,          -- unfiltered ON PURPOSE: the log labels it
	function(context)
		local clicked_id = tostring(context.string)

		-- THE BADGE CLICK: a left-click on our OWN badge flips the per-unit
		-- switch(es) for that badge's ability. Round 43+ measured that these
		-- clicks DO reach script - six clicks each arrived as a "left-click
		-- on 'zz_auto_badge'" and were simply logged as "not ours". The badge
		-- is the component created on hud_battle with the id 'zz_auto_badge';
		-- any future 'zz_auto_*' component is routed the same way, so an
		-- added or renamed badge keeps working. Each badge id resolves to its
		-- own ability (section 1), so a click flips ONLY that ability - for
		-- every unit the engine reports as selected that owns it: one
		-- selected unit - exactly as before; several - the checkbox rule
		-- (all armed -> disarm all, else arm all; selected non-owners are
		-- never touched). With no unit selected the click does nothing but
		-- say so.
		if string.sub(clicked_id, 1, 8) == "zz_auto_" then
			local ability = ability_for_badge(clicked_id)
			if ability == nil then
				log("badge click on '" .. clicked_id
					.. "' - no ability has that badge id, ignored")
				return
			end
			if selected_unit_id == nil and #selected_ui_ids == 0 then
				log("click ignored: no unit selected yet - click the unit's card first")
				return
			end

			-- THE CLICK GUARD (this build): a badge whose marker is NOT
			-- currently claimed - i.e. NOT on the selected unit's dial - is
			-- INERT. The battle log showed a stale, still-visible badge
			-- being clicked while the dial had no Deadly Onslaught, and the
			-- click toggled the ability on for a unit that does not even
			-- own it. The test is marker_claimed_now, the same one the ui
			-- tick uses, so the tick and the click can never disagree.
			if not marker_claimed_now(ability) then
				log("click ignored: " .. ability.marker .. " is not on this unit's dial")
				return
			end

			-- THE SELECTED SET (this build): the badge click acts on EVERY
			-- unit the engine reports as selected, not just the single
			-- tracker below - the vanilla "common ability" behaviour. The
			-- shared card read keeps the set current (section 8e); when it
			-- is empty the tracker stands in alone, exactly as before.
			local targets, target_ids = {}, {}
			for i = 1, #selected_ui_ids do
				local id = selected_ui_ids[i]
				if id ~= nil then
					targets[#targets + 1] = id
					target_ids[#target_ids + 1] = tostring(id)
				end
			end
			if #targets == 0 then
				if selection_callback_alive then
					-- THE ENGINE'S OWN ANSWER: nothing is selected. The
					-- tracker may still name the last unit, but acting on
					-- it would toggle a unit the player has deselected -
					-- the callback set is authoritative, so the click acts
					-- on nobody.
					log("click ignored: no unit selected yet - click the unit's card first")
					return
				end
				targets[1] = tostring(selected_unit_id)
				target_ids[1] = tostring(selected_unit_id)
			end

			if #targets <= 1 then
				-- ONE SELECTED UNIT - one unit's own pair flips, whether or
				-- not the scan has seen the ability on it yet (a
				-- late-arriving ability stays armable). When the callback set
				-- is in charge, the one id IS the engine's answer (and may
				-- already be newer than the tracker, which catches up at the
				-- next convergence); the fallback world keeps acting on the
				-- tracker, exactly as before. The click-time context - the
				-- unit, its type and the state as it was - is written BEFORE
				-- the toggle takes effect: the diagnostic for the reported
				-- cross-unit toggle, so the log names the unit a click
				-- really acted on.
				local single_id = target_ids[1]
				if not selection_callback_alive then single_id = tostring(selected_unit_id) end
				local unit = units_by_ui_id[tostring(single_id)]
				local arm_slot = unit_slot(single_id)
				local per = armed[arm_slot]
				local was_armed = per ~= nil and per[ability.marker] == true
				local ok_t, unit_type = pcall(function() return unit:type() end)
				log("click: " .. ability.marker .. " badge -> selected unit "
					.. tostring(single_id) .. " ('" .. tostring(ok_t and unit_type or "?")
					.. "') armed was " .. (was_armed and "ON" or "OFF"))
				set_auto_for_unit(single_id, ability.marker, not was_armed)
				return
			end

			-- SEVERAL SELECTED UNITS - THE CHECKBOX RULE (this build): over
			-- every selected unit that OWNS one of this ability's keys (the
			-- per-unit owned-key cache, section 4), ALL armed -> disarm
			-- all, otherwise -> arm all. Selected units that do not own the
			-- ability are never touched, so per-unit independence holds.
			local owners, owner_ids = {}, {}
			for i = 1, #targets do
				if unit_owns_marker(targets[i], ability.marker) then
					owners[#owners + 1] = targets[i]
					owner_ids[#owner_ids + 1] = target_ids[i]
				end
			end
			if #owners == 0 then
				log("click: " .. ability.marker .. " badge -> " .. tostring(#targets)
					.. " selected unit(s), none owns the ability - nothing toggled")
				return
			end
			local all_armed = true
			for i = 1, #owners do
				local per = armed[unit_slot(owners[i])]
				if per == nil or per[ability.marker] ~= true then
					all_armed = false
				end
			end
			local value = not all_armed
			for i = 1, #owners do
				set_auto_for_unit(owners[i], ability.marker, value)
			end
			log("click: " .. ability.marker .. " badge -> " .. tostring(#owners)
				.. " selected unit(s) toggled " .. (value and "ON" or "OFF")
				.. " (" .. table.concat(owner_ids, ", ") .. ")")
			return
		end

		-- THE UNIT CARD: a click on a unit's card selects the unit the badge
		-- clicks act on. The card's component id IS its unit's own
		-- unique_ui_id (the proven bridge - vanilla matches
		-- uic_card:Id() == unit:unique_ui_id() the same way), so this is a
		-- plain table lookup, never a find. This is the FAST-PATH: the card
		-- sweep (section 8e) re-derives the selection from the engine's own
		-- card states within ~1 s and WINS over whatever this click set.
		local clicked_unit = units_by_ui_id[clicked_id]
		if clicked_unit ~= nil then
			-- IS THIS A SELECTION CHANGE? (this build) The letters are
			-- driven from a card click ONLY when the click actually moves
			-- the selection; a click that re-selects the same unit stays
			-- silent (the letter cache has nothing to change).
			local selection_changed = (selected_unit_id ~= clicked_id)
			selected_unit_id = clicked_id
			local ok_t, unit_type = pcall(function() return clicked_unit:type() end)
			log("SELECTED unit ui id " .. clicked_id .. " ('"
				.. tostring(ok_t and unit_type or "?")
				.. "') - badge clicks now act on it")
			if selection_changed then
				walk_on_selection_change = true   -- the dial now belongs to this unit
				-- THE SELECTION CHANGED: refresh BOTH badges' letters from
				-- the new selection in this same handler call (this build) -
				-- the letters never wait for a timer - then log the
				-- tick-stamped card-click line, so the click itself is the
				-- refresh trigger. The feedback caches are re-synced right
				-- after, so every other path agrees.
				refresh_badge_letters_for_selection(selected_unit_id)
				log("card click: selection -> " .. tostring(selected_unit_id)
					.. " - letters refreshed at tick " .. tostring(tick_count))
			end
			for _, ability in ipairs(ABILITIES) do
				apply_ability_feedback(ability.marker)
			end
			return
		end

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

-- ============================================================================
-- 8c. THE DIAL DUMP - a once-per-second, READ-ONLY census of the ability dial
--     What the script sees vs what the screen shows: every child of our button's
--     parent container (the 'button_parent' next to our button), each with its
--     id, its AbilityKeyForScript and its Position(), plus the parent's and the
--     'SA_dial' ancestor's own positions and our badge's position/offset/letter.
--     The caller gates it to one block per ~1 s of battle time (4 x 250 ms), and
--     every engine read is pcall'd and type-checked, so it can never error out of
--     the tick. NOTHING here writes to any button.
-- ============================================================================

local DIAL_DUMP_EVERY_N_POLL_TICKS = 4      -- 4 x 250 ms = ~1 s of battle time
local last_dial_dump_tick = -1000           -- so the first confirmed tick dumps at once

local function fmt_xy(x, y)
	if type(x) == "number" and type(y) == "number" then
		return "(" .. tostring(x) .. "," .. tostring(y) .. ")"
	end
	return "(?,?)"
end

local function read_xy(uic)
	local ok, x, y = pcall(function() return uic:Position() end)
	if ok and type(x) == "number" and type(y) == "number" then return x, y end
	return nil, nil
end

local function log_dial_dump()
	local master = ability_state[ABILITIES[1].marker]
	if master == nil or master.button == nil then return end

	local ok_p, parent = pcall(function() return master.button:Parent() end)
	if not ok_p or parent == nil then return end
	local ok_w, container = pcall(function() return UIComponent(parent) end)
	if not ok_w or container == nil then return end

	-- The dial itself: the first 'SA_dial' on the way up from our button.
	local dial_str = "?"
	local node = master.button
	for _ = 1, 8 do
		local ok_up, up = pcall(function() return node:Parent() end)
		if not ok_up or up == nil then break end
		local ok_w2, wrapped = pcall(function() return UIComponent(up) end)
		if not ok_w2 or wrapped == nil then break end
		node = wrapped
		local ok_id, id = pcall(function() return node:Id() end)
		if ok_id and type(id) == "string" and id == "SA_dial" then
			local dx, dy = read_xy(node)
			dial_str = fmt_xy(dx, dy)
			break
		end
	end

	local slot_count = nil
	local ok_n, n = pcall(function() return container:ChildCount() end)
	if ok_n and type(n) == "number" then slot_count = n end

	local px, py = read_xy(container)
	log("DIAL t=" .. string.format("%.1f", tick_count * POLL_MS / 1000) .. "s slots="
		.. (slot_count ~= nil and tostring(slot_count) or "?")
		.. " parent=" .. fmt_xy(px, py) .. " dial=" .. dial_str)

	if slot_count ~= nil then
		for i = 0, slot_count - 1 do
			local ok_c, child = pcall(function() return container:Find(i) end)
			if ok_c and child ~= nil then
				local ok_c2, cc = pcall(function() return UIComponent(child) end)
				if ok_c2 and cc ~= nil then
					local cid = "?"
					local ok_i, id = pcall(function() return cc:Id() end)
					if ok_i and type(id) == "string" then cid = id end

					local ckey = "-"
					local ok_k, key = pcall(function() return cc:InterfaceFunction("AbilityKeyForScript") end)
					if ok_k and type(key) == "string" and (safe_len(key) or 0) > 3 then
						ckey = key
					end

					local cx, cy = read_xy(cc)
					log("  slot " .. tostring(i + 1) .. ": id='" .. cid
						.. "' key='" .. ckey .. "' pos=" .. fmt_xy(cx, cy))
				end
			end
		end
	end

	-- ONE FOOTER LINE PER ABILITY: the badge's visibility, position and letter,
	-- plus the offset it was placed at (BADGE_X/BADGE_Y + its own ox/oy). The
	-- onslaught footer keeps its original wording; added abilities get a tag.
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		local bvis, bpos, bletter = false, "(?,?)", "-"
		if state.badge ~= nil then
			bvis = state.badge_shown == true
			local bx, by = read_xy(state.badge)
			bpos = fmt_xy(bx, by)
			local ok_g, got = pcall(function() return state.badge:GetText() end)
			if ok_g and type(got) == "string" then
				bletter = got
			else
				bletter = is_armed(selected_unit(), ability.marker) and "A" or "M"
			end
		end
		local prefix = "OUR BADGE"
		if ability.marker ~= "onslaught" then
			prefix = prefix .. " [" .. ability.marker .. "]"
		end
		log(prefix .. ": visible=" .. (bvis and "true" or "false") .. " pos=" .. bpos
			.. " offset=(" .. tostring(BADGE_X + ability.ox) .. "," .. tostring(BADGE_Y + ability.oy)
			.. ") letter='" .. bletter .. "'")
	end
end

-- ============================================================================
-- 8d. THE INVENTORY SWEEP - a once-per-second, READ-ONLY census of every
--     candidate ability component, in TWO coordinate spaces at once.
--     The player sees a CIRCLE, but the DIAL dump above reports the button bar
--     as a straight line (same y, x stepping by 59 px). So either the circle is
--     a component outside button_parent, or Position() and the drawn position
--     live in different spaces - RelativePosition() and GetDockOffset() have
--     never been read. This sweep reads them, pcall'd, for every candidate id
--     and logs ONE line per candidate; a read that fails prints '?' and NEVER
--     skips its line. It runs whenever our ability button OR any candidate can
--     be found - NOT only while the dial is confirmed - once per ~1 s.
-- ============================================================================

local INVENTORY_EVERY_N_POLL_TICKS = 4      -- 4 x 250 ms = ~1 s of battle time
local last_inventory_tick = -1000           -- so the first tick with a find dumps at once

-- The fixed candidate ids, read and logged in this order. Every one is looked
-- up by id from the UI root: root:Find(id) is the engine's own recursive search.
local INVENTORY_FIXED = {
	"SA_dial", "dial_frame", "button_parent",
	"button_ability",
	"button_ability1", "button_ability2", "button_ability3",
	"button_ability4", "button_ability5", "button_ability6",
	"button_slot1", "button_slot2", "button_slot3",
	"button_slot4", "button_slot5", "button_slot6",
	"behaviour_parent", "orders_parent", "army_ability_parent", "ability_parent",
	"zz_auto_badge", "zz_auto_badge_fs",
}

local function inv_id_of(uic)
	local ok, id = pcall(function() return uic:Id() end)
	if ok and type(id) == "string" and string.len(id) > 0 then return id end
	return nil
end

-- Find one candidate: the engine's recursive Find from the ui root first, and
-- a bounded walk of the tree as a fallback. Returns the component, or nil.
local function inv_find(wanted)
	local ok, got = pcall(function()
		local root = core:get_ui_root()
		if root == nil then return nil end
		local raw = root:Find(wanted, false)      -- false = do not assert when missing
		if raw == nil then return nil end
		local ok_w, wrapped = pcall(UIComponent, raw)
		if ok_w and wrapped ~= nil then return wrapped end
		return raw
	end)
	if ok and got ~= nil then
		local id = inv_id_of(got)
		if id == nil or id == wanted then return got end
	end
	return nil
end

-- ONE bounded walk from the ui root, collecting every still-missing id at once.
-- Read-only; depth- and visit-bounded; every read pcall'd.
local function inv_walk(missing, found)
	local ok_r, root = pcall(function() return core:get_ui_root() end)
	if not ok_r or root == nil then return end

	local visits, max_visits = 0, 900
	local stack = { { node = root, depth = 0 } }
	while #stack > 0 and visits < max_visits do
		local item = table.remove(stack)
		local node, depth = item.node, item.depth
		visits = visits + 1

		local id = inv_id_of(node)
		if id ~= nil and missing[id] ~= nil and found[id] == nil then
			found[id] = node
		end

		if depth < 8 then
			local ok_n, n = pcall(function() return node:ChildCount() end)
			if ok_n and type(n) == "number" and n > 0 then
				for i = n - 1, 0, -1 do
					local ok_c, child = pcall(function() return node:Find(i) end)
					if ok_c and child ~= nil then
						local ok_w, wrapped = pcall(UIComponent, child)
						if ok_w and wrapped ~= nil then
							stack[#stack + 1] = { node = wrapped, depth = depth + 1 }
						end
					end
				end
			end
		end
	end
end

-- Resolve every wanted id, fresh each sweep: the engine's own Find per id,
-- then one shared walk for whatever is still missing.
local function inv_resolve(ids)
	local found = {}

	for i = 1, #ids do
		local got = inv_find(ids[i])
		if got ~= nil then found[ids[i]] = got end
	end

	local missing = {}
	local anything_missing = false
	for i = 1, #ids do
		if found[ids[i]] == nil then
			missing[ids[i]] = true
			anything_missing = true
		end
	end
	if anything_missing then inv_walk(missing, found) end

	-- Our own badges are special: if the engine's search cannot see a component
	-- WE created, the handle we already hold is the truth about it.
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		if found[ability.badge] == nil and state.badge ~= nil
			and inv_id_of(state.badge) == ability.badge then
			found[ability.badge] = state.badge
		end
	end

	return found
end

local function inv_rel_xy(uic)
	local ok, x, y = pcall(function() return uic:RelativePosition() end)
	if ok and type(x) == "number" and type(y) == "number" then return x, y end
	return nil, nil
end

local function inv_dock_xy(uic)
	local ok, x, y = pcall(function() return uic:GetDockOffset() end)
	if ok and type(x) == "number" and type(y) == "number" then return x, y end
	return nil, nil
end

-- One INVENTORY line. Every read is pcall'd and type-checked; a failed read
-- prints '?' and NEVER shortens the line. comp == nil means the candidate does
-- not exist right now - still a line, all fields '?', marked [not found].
local function inv_line(wanted, comp)
	if comp == nil then
		return "INVENTORY " .. wanted
			.. ": visible=? pos=(?,?) relpos=(?,?) dock=(?,?) state='?' key='?' [not found]"
	end

	local vis = "?"
	local ok_v, v = pcall(function() return comp:Visible(true) end)
	if ok_v and type(v) == "boolean" then
		vis = v and "true" or "false"
	end

	local px, py = read_xy(comp)
	local rx, ry = inv_rel_xy(comp)
	local dx, dy = inv_dock_xy(comp)

	local state = "?"
	local ok_s, s = pcall(function() return comp:CurrentState() end)
	if ok_s and type(s) == "string" then state = s end

	local key = "?"
	local ok_k, k = pcall(function() return comp:InterfaceFunction("AbilityKeyForScript") end)
	if ok_k then
		if type(k) == "string" and (safe_len(k) or 0) > 3 then
			key = k
		else
			key = "-"
		end
	end

	return "INVENTORY " .. wanted
		.. ": visible=" .. vis
		.. " pos=" .. fmt_xy(px, py)
		.. " relpos=" .. fmt_xy(rx, ry)
		.. " dock=" .. fmt_xy(dx, dy)
		.. " state='" .. state .. "'"
		.. " key='" .. key .. "'"
end

local function log_inventory_sweep()
	local found = inv_resolve(INVENTORY_FIXED)

	-- Children of button_parent whose id starts with 'button_order' (dynamic:
	-- the engine names them button_order1, button_order12, ... per unit).
	local order_children = {}
	local bp = found["button_parent"]
	if bp ~= nil then
		local ok_n, n = pcall(function() return bp:ChildCount() end)
		if ok_n and type(n) == "number" and n > 0 then
			for i = 0, n - 1 do
				local ok_c, child = pcall(function() return bp:Find(i) end)
				if ok_c and child ~= nil then
					local ok_w, cc = pcall(UIComponent, child)
					if ok_w and cc ~= nil then
						local cid = inv_id_of(cc)
						if cid ~= nil and string.sub(cid, 1, 12) == "button_order" then
							order_children[#order_children + 1] = { id = cid, comp = cc }
						elseif cid == nil then
							-- a child whose id cannot be read: still a line, never skipped
							order_children[#order_children + 1] =
								{ id = "button_order?[" .. tostring(i + 1) .. "]", comp = cc }
						end
					end
				end
			end
		end
	end

	local found_count = #order_children
	for i = 1, #INVENTORY_FIXED do
		if found[INVENTORY_FIXED[i]] ~= nil then found_count = found_count + 1 end
	end
	local total = #INVENTORY_FIXED + #order_children

	-- Run whenever one of our ability buttons OR any candidate exists; stay
	-- silent only when there is nothing at all to report on.
	local any_button = false
	for _, ability in ipairs(ABILITIES) do
		if ability_state[ability.marker].button ~= nil then any_button = true end
	end
	if not any_button and found_count == 0 then return end

	log("INVENTORY sweep t=" .. string.format("%.1f", tick_count * POLL_MS / 1000) .. "s"
		.. " found=" .. tostring(found_count) .. "/" .. tostring(total))

	log(inv_line("SA_dial", found["SA_dial"]))
	log(inv_line("dial_frame", found["dial_frame"]))
	log(inv_line("button_parent", found["button_parent"]))
	for i = 1, #order_children do
		log(inv_line(order_children[i].id, order_children[i].comp))
	end
	log(inv_line("button_ability", found["button_ability"]))
	for i = 1, 6 do
		log(inv_line("button_ability" .. tostring(i), found["button_ability" .. tostring(i)]))
	end
	for i = 1, 6 do
		log(inv_line("button_slot" .. tostring(i), found["button_slot" .. tostring(i)]))
	end
	log(inv_line("behaviour_parent", found["behaviour_parent"]))
	log(inv_line("orders_parent", found["orders_parent"]))
	log(inv_line("army_ability_parent", found["army_ability_parent"]))
	log(inv_line("ability_parent", found["ability_parent"]))
	log(inv_line("zz_auto_badge", found["zz_auto_badge"]))
	log(inv_line("zz_auto_badge_fs", found["zz_auto_badge_fs"]))
end

-- ============================================================================
-- 8e. THE SELECTION - the engine's selection callback FIRST, the card sweep
--     as the fallback and reconciliation, both converging on ONE set
--     (selected_ui_ids) and ONE tracker (selected_unit_id):
--
--     * THE ENGINE SELECTION CONVERGENCE (converge_engine_selection) runs on
--       every ui tick BEFORE the sweep: the callback (section 3b) maintains
--       the set event by event; the convergence folds any change into ONE
--       logged line naming the whole set
--           selection callback: <n> unit(s) selected now (<id1>, <id2>, ...)
--       adopts the tracker with the same rule the card derivation uses, and
--       refreshes the badge letters - all ONCE per change, never once per
--       unit event (a ten-unit box selection is one line, not ten).
--
--     * THE CARD SWEEP - the player's unit cards DRIVE THE SELECTION when no
--       callback event has EVER been delivered (API missing / behaviour
--       differs - the unchanged fallback), and RECONCILE the callback-fed
--       set otherwise (a card-reported id is added; a card-added id is
--       dropped once the cards stop reporting it). At TWO cadences:
--
--     * THE FAST PATH (fast_card_selection) runs on EVERY ui tick: it reads
--       the tracked units' card states and derives the selection the same
--       way the census always did (exactly one card reports 'selected' ->
--       adopt its id; several -> keep the tracker when it is one of them,
--       else the deterministic first; none/failed -> keep). On any change it
--       adopts the derived id and refreshes both badges' letters with the
--       tick number on the established header:
--           selection changed to <ui_id> - refreshing badge letters (tick N)
--       so the change reaches the tracker AND the letters within ONE ui tick
--       (~50 ms) instead of waiting up to a second for the next census. It
--       is QUIET while nothing changes - no notes, no summary, no repeated
--       lines - and on a change it includes the card lines ONCE, so the
--       change is documented with the states that caused it.
--
--     * THE VERBOSE CENSUS (log_card_sweep) stays at ONE BLOCK PER ~1 s of
--       battle time exactly as before (the 4 x 250 ms gate, same lines): the
--       once-per-change notes, its own adoption line should it ever get
--       there first, then the summary and one line per card:
--           card <ui_id> state='<CurrentState()>' visible=<true|false>
--           cards: selected-tracker=<ui_id or none>
--       with the [selected-tracker] tag on the card the tracker currently
--       names. The fast path runs first on every tick, so in practice the
--       census reports; its adoption branch stays as the safety net.
--
--     Both cadences share ONE read and ONE derivation (read_tracked_card_states
--     + derive_selection_from_cards) and one card-line writer (log_card_lines),
--     so they can never disagree about what the cards say.
--
--     The engine marks the selected unit's card with CurrentState() ==
--     'selected' (measured in battle: the selected card reads 'selected',
--     every other card reads 'active'); the card CLICK path stays as an
--     immediate fast-path (it sets the tracker on the spot), but the card
--     states win: whatever a click set, the next ui tick's read follows the
--     game. For each tracked unit (the read collects up to CARD_SWEEP_MAX
--     wanted ids first - a runaway guard, not a working limit: see the
--     constant below), the unit's CARD is the component in the cards panel
--     whose Id() EQUALS
--     the unit's unique_ui_id() - the proven bridge (vanilla matches
--     uic_card:Id() == unit:unique_ui_id() the same way; the card clicks
--     this build routes rely on exactly that identity). Every engine read is
--     pcall'd and type-checked: a failing or hostile read prints '?' and
--     NEVER shortens a line, and nothing here can error out of the tick.
--     Ids are matched by EXACT EQUALITY on a copied string - there is no
--     find of any kind (string.find is banned from this file). The walk is
--     depth- and visit-bounded; NOTHING here writes to any component.
-- ============================================================================

local CARD_SWEEP_EVERY_N_POLL_TICKS = 4      -- 4 x 250 ms = ~1 s of battle time
local last_card_sweep_tick = -1000           -- so the first tick with units sweeps at once
-- A RUNAWAY GUARD, not a working limit: a single-player unit-card panel
-- tops out at 20 cards, so 40 can never bind for a real army - it is only
-- a belt against a pathological wanted-list (the walk itself is separately
-- visit-bounded). The old value (12) was a legacy work-cap that made units
-- past the 12th collected card invisible to selection tracking.
local CARD_SWEEP_MAX = 40                    -- at most this many wanted ids per read

-- The last state-note this sweep logged (the multiple-selected and the
-- no-card-selected lines). A note is logged only when its TEXT changes -
-- once per change - so a steady state stays quiet however many sweeps pass.
local last_selection_note = nil

-- Resolve the cards-panel container by id: the engine's recursive Find from
-- the ui root first (the same call the inventory sweep proves works),
-- verified against the component's own id; nil when the search finds nothing
-- usable, so the caller can fall back to the ui root itself.
local function card_panel_find(root, wanted)
	local ok, got = pcall(function()
		local raw = root:Find(wanted, false)   -- false = do not assert when missing
		if raw == nil then return nil end
		local ok_w, wrapped = pcall(UIComponent, raw)
		if ok_w and wrapped ~= nil then return wrapped end
		return raw
	end)
	if ok and got ~= nil and inv_id_of(got) == wanted then return got end
	return nil
end

-- ONE bounded walk of the panel subtree, collecting the wanted cards: every
-- node's id is read through pcall (a failing read is simply not a card - the
-- walk carries on), the walk is visit- and depth-bounded like the inventory
-- walk, and each child read is pcall'd. Nothing here can raise.
local function card_collect_from(start, wanted, found)
	local visits, max_visits = 0, 900
	local stack = { { node = start, depth = 0 } }
	while #stack > 0 and visits < max_visits do
		local item = table.remove(stack)
		local node, depth = item.node, item.depth
		visits = visits + 1

		local id = inv_id_of(node)
		if id ~= nil and wanted[id] ~= nil and found[id] == nil then
			found[id] = node
		end

		if depth < 8 then
			local ok_n, n = pcall(function() return node:ChildCount() end)
			if ok_n and type(n) == "number" and n > 0 then
				for i = n - 1, 0, -1 do
					local ok_c, child = pcall(function() return node:Find(i) end)
					if ok_c and child ~= nil then
						local ok_w, wrapped = pcall(UIComponent, child)
						if ok_w and wrapped ~= nil then
							stack[#stack + 1] = { node = wrapped, depth = depth + 1 }
						end
					end
				end
			end
		end
	end
end

-- THE SHARED CARD READ (this build - the sweep is split into two cadences).
-- Resolves the tracked units' cards and reads each card's engine state ONCE.
-- Both cadences use it - the FAST path on every ui tick and the verbose
-- once-per-second census - so they can never disagree about what the cards
-- say. Every read is pcall'd and type-checked like the census always was: a
-- failing or hostile read prints '?' and NEVER shortens a line.
-- Returns:
--   ordered  - the wanted ids, sorted, so "the first selected card" is a
--              stable, reproducible choice (pairs() order is not)
--   found    - id -> the card component found for it (absent = not found)
--   states   - id -> the card's CurrentState() string ('?' on a failed read)
--   selected - the ids whose state reads exactly 'selected', ordered order
local function read_tracked_card_states()
	-- The wanted card ids: the tracked units' unique_ui_id strings - the
	-- proven bridge. The collection stops after CARD_SWEEP_MAX ids - a
	-- runaway guard only (see the constant above): real panels top out at
	-- 20 cards, so every tracked unit of a real army is always collected.
	local wanted, wanted_count = {}, 0
	for ui_id in pairs(units_by_ui_id) do
		if wanted_count >= CARD_SWEEP_MAX then break end
		if wanted[ui_id] == nil then
			wanted[ui_id] = true
			wanted_count = wanted_count + 1
		end
	end

	local ordered = {}
	for ui_id in pairs(wanted) do
		ordered[#ordered + 1] = tostring(ui_id)
	end
	table.sort(ordered)

	local found = {}
	if wanted_count > 0 then
		local ok_r, root = pcall(function() return core:get_ui_root() end)
		if ok_r and root ~= nil then
			-- The cards panel: 'card_panel_docker', else 'cards_panel', else
			-- the ui root itself (the walk then simply looks from the top).
			-- NOT finding the panel is not fatal - the derivation simply
			-- sees no cards this read.
			local start = card_panel_find(root, "card_panel_docker")
			if start == nil then start = card_panel_find(root, "cards_panel") end
			if start == nil then start = root end
			card_collect_from(start, wanted, found)
		end
	end

	-- Every card's engine state, read ONCE (pcall'd and type-checked; '?' on
	-- failure and never a claim): a card whose state reads exactly 'selected'
	-- is one of the units the game currently has selected.
	local states = {}
	local selected = {}
	for i = 1, #ordered do
		local ui_id = ordered[i]
		local card = found[ui_id]
		if card ~= nil then
			local state = "?"
			local ok_s, s = pcall(function() return card:CurrentState() end)
			if ok_s and type(s) == "string" then state = s end
			states[ui_id] = state
			if state == "selected" then
				selected[#selected + 1] = ui_id
			end
		end
	end

	-- THE SELECTED SET (this build): expose the WHOLE group, not just the
	-- single-choice derivation built over it - the badge click and the
	-- collective letter read selected_ui_ids (section 2). Two regimes:
	--   * NO callback event has EVER been delivered (API missing, or the
	--     engine never called back): the cards are in charge and REPLACE the
	--     set, exactly as before - the unchanged fallback. A read that found
	--     no cards at all leaves the set alone, like the derivation keeping
	--     the tracker.
	--   * the callback HAS delivered (it is the engine's own word on group
	--     selections, which the cards do not report): the callback-fed set is
	--     in charge. The cards may still ADD an id the set has not seen (a
	--     single selection whose event did not arrive) - and such a
	--     card-added id is dropped again once the cards stop reporting it, so
	--     the reconciliation can never leave a phantom selected unit behind.
	if next(found) ~= nil then
		if not selection_callback_alive then
			selected_ui_ids = selected
		else
			for i = 1, #selected do
				local id = selected[i]
				if not engine_selection_has(id) then
					selected_ui_ids[#selected_ui_ids + 1] = id
					reconciled_card_ids[id] = true
					selection_set_dirty = true
				end
			end
			for id in pairs(reconciled_card_ids) do
				local still_reported = false
				for i = 1, #selected do
					if selected[i] == id then still_reported = true end
				end
				if not still_reported then
					reconciled_card_ids[id] = nil
					for i = #selected_ui_ids, 1, -1 do
						if selected_ui_ids[i] == id then
							table.remove(selected_ui_ids, i)
							selection_set_dirty = true
						end
					end
				end
			end
		end
	end

	return ordered, found, states, selected
end

-- THE SHARED DERIVATION (this build): the engine's own signal decides the
-- selection, exactly as the census always did. Given the ordered selected
-- list:
--   * exactly one card reports 'selected' -> adopt its id;
--   * several (group selection)           -> keep the tracker when it is one
--     of them, else take the first (ordered) selected card;
--   * none (or the reads fail)            -> keep the tracker.
-- Returns the id to adopt (nil when nothing can be adopted) plus the note
-- text the verbose census logs once per change; the FAST path stays quiet
-- and ignores the note.
local function derive_selection_from_cards(previous, selected)
	local derived = nil
	local note = nil
	if #selected == 1 then
		derived = selected[1]
	elseif #selected > 1 then
		-- Group selection: keep the tracker when it is one of the selected
		-- cards, else take the first (ordered) one.
		derived = previous
		local among = false
		for i = 1, #selected do
			if selected[i] == previous then among = true end
		end
		if not among then derived = selected[1] end
		note = "multiple selected cards - tracker=" .. tostring(derived)
	else
		-- No card reports 'selected' (or the reads failed): keep the current
		-- value, and say so once per change (the note-text dedupe below).
		note = "no card reports selected - tracker stays " .. tostring(previous)
	end
	return derived, note
end

-- ONE CARD-LINE BLOCK (this build): the per-card census lines, in the same
-- ordered sequence: each card's state and visibility, the card the tracker
-- currently names tagged [selected-tracker]. Used by the verbose census once
-- per second AND by the fast path when the selection changes (the change is
-- then documented with the card states that caused it, once). Every read is
-- pcall'd and type-checked: a failing read prints '?' and NEVER shortens a
-- line. Nothing here writes to any component.
local function log_card_lines(ordered, found, states, tracker)
	for i = 1, #ordered do
		local ui_id = ordered[i]
		local card = found[ui_id]
		if card ~= nil then
			local state = states[ui_id] or "?"

			local vis = "?"
			local ok_v, v = pcall(function() return card:Visible(true) end)
			if ok_v and type(v) == "boolean" then vis = v and "true" or "false" end

			local line = "card " .. tostring(ui_id) .. " state='" .. state .. "' visible=" .. vis
			if tracker ~= "none" and tostring(ui_id) == tracker then
				line = line .. " [selected-tracker]"
			end
			log(line)
		end
	end
end

-- THE FAST PATH (this build): the selection is derived from the card states
-- on EVERY ui tick, so a change - a card click on the battlefield, a group
-- select, the engine's own reselection - is adopted, and both badges'
-- letters refreshed, within ONE ui tick instead of waiting for the next
-- census. It is QUIET unless the tracker actually changes: no notes, no
-- summary, no repeated lines. On a change it adopts the derived id, logs the
-- established header with the tick number on it
--     selection changed to <ui_id> - refreshing badge letters (tick N)
-- refreshes both badges' letters in the same call, and includes the card
-- lines ONCE - the change's own evidence block. Every read is pcall'd (the
-- shared reader above) and the caller pcalls this function, so nothing here
-- can error out of the ui tick.
-- In callback mode (section 3b) this path keeps only its single-select job:
-- the shared read hands the set to the callback regime, and the derivation
-- below adopts a change the callback has not reported yet (or adopts first in
-- the fallback world, exactly as it always did).
local function fast_card_selection()
	local previous = "none"
	if selected_unit_id ~= nil then previous = tostring(selected_unit_id) end

	local ordered, found, states, selected = read_tracked_card_states()
	local derived = derive_selection_from_cards(previous, selected)
	if derived == nil or derived == previous then return end

	-- THE SELECTION CHANGED: adopt it, refresh the letters (tick-stamped),
	-- and include the card lines once.
	walk_on_selection_change = true   -- the dial now belongs to the adopted unit
	selected_unit_id = derived
	refresh_badge_letters_for_selection(derived, tick_count)
	log_card_lines(ordered, found, states, tostring(derived))
end

-- THE ENGINE SELECTION CONVERGENCE (this build): the callback (section 3b)
-- maintains selected_ui_ids event by event; this runs on every ui tick and
-- turns whatever it collected into ONE coalesced act:
--   * ONE log line per set change, naming the whole set - a box selection of
--     ten units is ONE line, never ten (the signature below collapses any
--     burst of events between two ticks, and a steady set costs one string
--     compare and nothing else);
--   * the tracker adoption - the same rule the card derivation uses, so the
--     two mechanisms can never disagree (one selected id -> adopt it; several
--     -> keep the tracker when it is among them, else the first; none -> keep
--     it);
--   * the badge letters: refreshed in the same call (with the established
--     tick-stamped line when the tracker moves, per letter - silently unless
--     a letter really changed - when only the collective state changed).
local function converge_engine_selection(tick)
	if not selection_set_dirty then return end
	selection_set_dirty = false

	local ids = {}
	for i = 1, #selected_ui_ids do ids[i] = tostring(selected_ui_ids[i]) end
	table.sort(ids)
	local sig = table.concat(ids, ",")
	if sig == selection_set_sig then return end
	selection_set_sig = sig

	log("selection callback: " .. tostring(#ids) .. " unit(s) selected now ("
		.. (#ids > 0 and table.concat(ids, ", ") or "none") .. ")")

	local previous = "none"
	if selected_unit_id ~= nil then previous = tostring(selected_unit_id) end
	local derived = derive_selection_from_cards(previous, ids)
	if derived ~= nil and derived ~= previous then
		walk_on_selection_change = true   -- the dial now belongs to the adopted unit
		selected_unit_id = derived
		refresh_badge_letters_for_selection(derived, tick)
	else
		for _, ability in ipairs(active_abilities_list()) do
			refresh_badge_letter(ability.marker)
		end
	end
end

-- THE VERBOSE CENSUS (the once-per-second half of the split - the same gate,
-- the same lines, the same formats as it has had since it was built): the
-- notes once per change, its own adoption (the safety net - in practice the
-- fast path above ran first on every tick), the summary, then the per-card
-- lines. See the section header. Every engine read is pcall'd and
-- type-checked; nothing here can error out of the tick.
local function log_card_sweep()
	local previous = "none"
	if selected_unit_id ~= nil then previous = tostring(selected_unit_id) end

	local ordered, found, states, selected = read_tracked_card_states()
	local derived, note = derive_selection_from_cards(previous, selected)

	if note ~= nil then
		if note ~= last_selection_note then
			log(note)
			last_selection_note = note
		end
	else
		last_selection_note = nil
	end

	if derived ~= nil and derived ~= previous then
		log("selection updated from card states: " .. previous .. " -> " .. derived)
		selected_unit_id = derived
		walk_on_selection_change = true   -- the census adoption re-homes the dial too
		-- THE SELECTION CHANGED: refresh BOTH badges' letters from the new
		-- selection in this same call. The fast path and its per-tick
		-- safety net are the convergence mechanism now; this stays for the
		-- case where the census itself adopts first.
		refresh_badge_letters_for_selection(derived)
	end

	local tracker = "none"
	if selected_unit_id ~= nil then tracker = tostring(selected_unit_id) end
	log("cards: selected-tracker=" .. tracker)

	-- One line per card found, in the same ordered sequence: its state and
	-- visibility, the card the tracker currently names tagged.
	log_card_lines(ordered, found, states, tracker)
end

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
	find_ability_buttons()          -- the abilities' own icons (section 8b)
	for _, ability in ipairs(ABILITIES) do
		apply_ability_feedback(ability.marker)  -- keep each badge's letter in step with the collective switch
	end
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
	-- THE DEFERRED CREATION (this build): a claim in the walk only records the
	-- button and raises pending_badge[marker] (scan_component_body); the badge
	-- itself is built HERE, on the tick, one instrumented pcall'd step at a
	-- time - never from inside the walk. A step that fails is logged with its
	-- own err line, the badge stays absent and the next tick retries, up to
	-- MAX_BADGE_ATTEMPTS per claim; after that the marker waits for the dial to
	-- rebuild (a fresh claim resets the budget).
	for _, ability in ipairs(active_abilities_list()) do
		local marker = ability.marker
		local state = ability_state[marker]
		if state.badge == nil and state.button ~= nil and pending_badge[marker] ~= nil
			and badge_gave_up[marker] == nil then
			if (badge_attempts[marker] or 0) >= MAX_BADGE_ATTEMPTS then
				badge_gave_up[marker] = true
				log("badge " .. marker .. ": giving up until the dial rebuilds ("
					.. tostring(MAX_BADGE_ATTEMPTS) .. " failed attempts)")
			else
				badge_attempts[marker] = (badge_attempts[marker] or 0) + 1
				local ok, err = pcall(create_badge, marker)
				if not ok then
					discard_badge(state)
					log("badge " .. marker .. ": create attempt raised: " .. tostring(err))
				end
			end
		end
		if state.badge ~= nil then pending_badge[marker] = nil end
	end

	-- HIDDEN RELIABLY, NOT ON TRANSITIONS ALONE. Every tick, per ability: the
	-- DESIRED visibility is recomputed from the CLAIMED SET - the marker is
	-- claimed on the dial right now (marker_claimed_now: the claimed button
	-- reference still read as ours by the same key gate the scan used) AND
	-- there is a button reference - and whenever it differs from what the
	-- tick last applied (state.badge_shown), the badge is set to the desired
	-- state again, with exactly one log line for the change. No path can
	-- leave a badge visible while its marker is unclaimed: badge_visible
	-- (the letter path) no longer touches visibility at all, and the console
	-- hooks write the same bookkeeping so the next tick corrects them too.
	-- This holds after a dial rebuild, a slot change and an ability
	-- disappearing from the dial - whatever moved the dial.
	-- Per ability: judge ITS marker and show/hide/letter ITS own badge.
	local onslaught_confirmed = false
	local active_dropped = false    -- item 1.4: a stale claim died this tick - the set shrank

	for _, ability in ipairs(active_abilities_list()) do
		local state = ability_state[ability.marker]

		-- IS THE MARKER CLAIMED ON THIS DIAL RIGHT NOW? The same test the
		-- badge click guard runs, from the one shared place. A read that
		-- raises, an empty key or a foreign key means gone: the claim dies
		-- with the button (a rebuilt dial loses its stale claim).
		local claimed = marker_claimed_now(ability)
		if not claimed and state.button ~= nil then
			state.button = nil
			pending_badge[ability.marker] = nil   -- a stale claim dies with the button
			active_dropped = true
		end

		if ability.marker == "onslaught" then onslaught_confirmed = claimed end

		if state.badge ~= nil then
			local desired = claimed and state.button ~= nil

			if (state.badge_shown == true) ~= desired then
				state.badge_shown = desired
				pcall(function() state.badge:SetVisible(desired) end)
				if desired then
					log("badge " .. ability.marker .. ": shown (marker claimed)")
				else
					log("badge " .. ability.marker .. ": hidden (marker not claimed on this dial)")
				end
			end

			if state.badge_shown == true then
				-- THE PER-TICK SAFETY NET (this build): whichever event moved
				-- the selection or a unit's armed state, the letter is
				-- re-derived here every tick from the COLLECTIVE switch read
				-- (one unit: its own flag; several: all owners armed?) and
				-- re-written ONLY when it differs from the cached last
				-- letter (state.last_letter). So the display converges
				-- within one tick (250 ms) of ANY change, and a steady letter
				-- stays completely silent - no repeated SetText, no repeated
				-- line.
				refresh_badge_letter(ability.marker)
			end
		end
		if state.badge ~= nil then pcall(place_badge, ability.marker) end
	end

	-- ITEM 1.4 - a stale claim dropped this tick shrank the inputs: refresh
	-- the active set (silent unless the membership moved).
	if active_dropped then refresh_active_abilities() end

	-- THE DIAL DUMP (section 8c): while the dial positively shows our ability, one
	-- read-only census block per ~1 s of battle time. pcall'd so a surprise can
	-- never take the UI tick down with it.
	if onslaught_confirmed and (tick_count - last_dial_dump_tick) >= DIAL_DUMP_EVERY_N_POLL_TICKS then
		last_dial_dump_tick = tick_count
		pcall(log_dial_dump)
	end

	-- THE INVENTORY SWEEP (section 8d): one read-only block per ~1 s of battle
	-- time, whenever our ability button OR any candidate component can be found
	-- - not only while the dial is confirmed. pcall'd like the dump above so a
	-- surprise can never take the UI tick down with it.
	if (tick_count - last_inventory_tick) >= INVENTORY_EVERY_N_POLL_TICKS then
		last_inventory_tick = tick_count
		pcall(log_inventory_sweep)
	end

	-- THE ENGINE SELECTION CONVERGENCE (section 8e): the callback (section 3b)
	-- may have collected selection/deselection events since the last tick;
	-- fold them into ONE logged set change (exactly one line naming the whole
	-- set), adopt the tracker and refresh the badge letters before the card
	-- fast path reads anything. pcall'd like everything else so a surprise
	-- can never take the UI tick down.
	pcall(converge_engine_selection, tick_count)

	-- THE CARD SELECTION, FAST (section 8e): derived from the engine's own
	-- 'selected' card states on EVERY ui tick, so a selection change reaches
	-- the tracker and both badge letters within ONE tick (~50 ms). Quiet
	-- unless the tracker changes; on a change it logs the tick-stamped header
	-- and the card lines once. pcall'd like everything else so a surprise can
	-- never take the UI tick down.
	pcall(fast_card_selection)

	-- THE VERBOSE CARD SWEEP (section 8e): still one block per ~1 s of battle
	-- time - the same gate, the same lines. The fast path above ran first on
	-- this tick, so the sweep mostly reports; its own adoption branch stays
	-- as the safety net. pcall'd like the sweeps above so a surprise can
	-- never take the UI tick down.
	if (tick_count - last_card_sweep_tick) >= CARD_SWEEP_EVERY_N_POLL_TICKS then
		last_card_sweep_tick = tick_count
		pcall(log_card_sweep)
	end

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

	-- THE REASONED HUD WALK (this build). The walk runs only when there is a
	-- reason to expect OUR buttons on the dial:
	--   * a selection change this tick, or a newly tracked unit from the
	--     re-list (coalesced - one walk at most): walk immediately;
	--   * nothing known yet about the selected unit's keys (early battle, or
	--     nothing selected): walk as before, every other tick - the
	--     BOOTSTRAPPING phase;
	--   * the selected unit OWNS one of our keys whose claim is missing: retry
	--     every 4th tick (~200 ms) until the dial yields it;
	--   * otherwise: a coarse safety net, every 100th tick (~5 s), so a bound
	--     ability, a granted ability or a wrong owned-keys read can never
	--     leave us permanently blind.
	-- The walk itself, its cap and its probe behaviour are unchanged;
	-- all_buttons_found() still ends every walk the moment the dial is
	-- complete (and no walk runs at all then).
	if not all_buttons_found() then
		local walk_now = false
		if walk_on_selection_change or walk_on_new_unit then
			walk_now = true
			walk_on_selection_change = false
			walk_on_new_unit = false
		elseif not selection_walk_info_known() then
			walk_now = (ui_ticks % 2) == 0
		elseif selected_unit_owns_unclaimed_key() then
			walk_now = (ui_ticks % 4) == 0
		else
			walk_now = (ui_ticks % 100) == 0
		end
		if walk_now then
			find_ability_buttons()
		end
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
	.. " | automatic activation is PER UNIT: " .. armed_states_string()
	.. " | click a unit's card to select it, then the ability's M/A badge to flip it")
log("control: take=" .. (TAKE_CONTROL_FIRST and "explicit before every attempt" or "disabled")
	.. ", release=" .. (RELEASE_CONTROL_AFTER and "runs only after a successful take" or "off"))
log("claim-test bisect level " .. tostring(CLAIM_BISECT) .. "/9 - " .. bisect_summary()
	.. " (steps 1-6 + 9 run - the equality match; steps 7-8 log their removal; a step with 'entering' but no 'ok' names a crash)")
log("claim-test bisect steps: 1 type(v) | 2 tostring(v) | 3 concat copy | 4 string.len | 5 # | 6 string.lower | 7 find plain (removed) | 8 find pattern (removed) | 9 equality compare")
for _, ability in ipairs(ABILITIES) do
	for _, wanted_key in ipairs(ability.keys) do
		log("  accepting ability (" .. ability.marker .. "): " .. wanted_key)
	end
end

-- The tooltip override is a localisation file (text/db/zz_deadly_onslaught__.loc) that
-- re-writes the vanilla description of this ability with the right-click instruction
-- appended. This line proves whether it actually loaded: vanilla flavour text with no
-- "Right-click" line means the override lost, and only the tooltip is affected.
local TOOLTIP_KEY = "unit_abilities_tooltip_text_wh_main_character_abilities_deadly_onslaught"
local loc_ok, loc_text = pcall(function() return common.get_localised_string(TOOLTIP_KEY) end)
log("tooltip text in use (" .. (loc_ok and "ok" or "FAILED") .. "): " .. tostring(loc_text))
