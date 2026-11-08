"""Round 35: a second ability (Foe-Seeker) alongside Deadly Onslaught.

The same stable single-ability build becomes two-ability, per the agreed design:

  * ABILITIES table (section 1): onslaught (keys = wh_main only, trigger =
    "charge", badge "zz_auto_badge", offsets BADGE_X+0/BADGE_Y+0) and
    foe_seeker (keys = wh_main + wh_dlc03 variants, trigger = "running" via
    is_moving_fast, badge "zz_auto_badge_fs", offsets BADGE_X+70/BADGE_Y+30 -
    the measured top-slot -> 45-degree-slot step). The offsets are COMPUTED
    from BADGE_X/BADGE_Y in place_badge, so re-tuning the Deadly Onslaught
    badge carries Foe-Seeker along.
  * ONE badge per ability, same layout and parent, each created hidden and
    shown only while ITS ability is confirmed on the dial (alive Id +
    marker-substring test). Existing log lines kept, with the ability tag
    "[marker]" added.
  * Clicks: the zz_auto_ prefix path resolves the clicked badge id to its own
    ability and flips ONLY that ability's switch (auto_state[marker] - one
    switch per ability, no per-unit state). M/A letters kept.
  * Firing loop: per ability, per unit: auto_state -> trigger ("charge" =
    the existing charge conditions verbatim; "running" = is_moving_fast) ->
    readiness gate (can_perform_special_ability tried against every key; the
    first true key is fired; every answer logged) -> a SHORT guard / safety
    brake of GUARD_SECONDS (2 s) per (unit, ability). No 60/90 s timers.
  * The HUD scan matches BOTH abilities (marker substring) and tracks a button
    reference per ability; in_chain consults every ability's watch chain.
  * Kept: charge logic byte-identical, hide-by-default confirmation, tooltip
    and all ui/ files untouched, log style, the INVENTORY sweep (extended with
    the new badge id), the click-only toggle rule.
"""
from pathlib import Path

p = Path(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua")
s = p.read_text(encoding="utf-8")
before_lines = s.count("\n") + 1
report = []


def rep(old, new, why, n=1):
    global s
    assert s.count(old) == n, f"anchor {n}x expected, found {s.count(old)}: {why}"
    s = s.replace(old, new)
    report.append("ok  " + why)


# --- 1. section 1: the ABILITIES table replaces the single-ability key list ---
rep("""-- Ability keys we will fire. The first is the one Boris Todbringer carries.
-- The second is a legacy duplicate definition that currently sits on no unit,
-- kept as harmless insurance in case a future patch assigns it.
local ABILITY_KEYS = {
\t"wh_main_character_abilities_deadly_onslaught",
\t"wh_dlc03_character_abilities_deadly_onslaught",
}
""",
"""-- THE ABILITIES - one entry per ability, and this table drives everything:
-- the HUD scan (which dial buttons are ours), the firing loop (which trigger
-- and which keys to try) and the badges (one per ability, id and offset).
--   marker  - the string that identifies the ability's button on the battle
--             dial: the button's InterfaceFunction("AbilityKeyForScript") must
--             contain it (case-insensitive)
--   name    - the ability's display name, for the badge log lines
--   trigger - "charge" : the existing charge conditions (section 5), verbatim
--             "running": fire whenever the engine says the unit is moving fast
--   keys    - database keys tried against the engine's own readiness check
--             (can_perform_special_ability); the first that answers true is
--             the one fired
--   badge   - the component id of the ability's own M/A badge (its click is
--             the only control)
--   ox, oy  - the badge's offset from the onslaught badge's own BADGE_X /
--             BADGE_Y (section 8b): onslaught sits at BADGE_X+0/BADGE_Y+0,
--             foe_seeker at BADGE_X+70/BADGE_Y+30 - the measured +70,+30 from
--             the top dial slot to the 45-degree slot. Both offsets are
--             COMPUTED from BADGE_X/BADGE_Y at placement time, so re-tuning
--             the Deadly Onslaught badge (zz_badge_set) carries Foe-Seeker
--             along with it.
local ABILITIES = {
\t{ marker = "onslaught", name = "Deadly Onslaught", trigger = "charge",
\t\tbadge = "zz_auto_badge",
\t\tkeys = { "wh_main_character_abilities_deadly_onslaught" },
\t\tox = 0, oy = 0 },
\t{ marker = "foe_seeker", name = "Foe-Seeker", trigger = "running",
\t\tbadge = "zz_auto_badge_fs",
\t\tkeys = { "wh_main_character_abilities_foe_seeker",
\t\t\t"wh_dlc03_character_abilities_foe_seeker" },
\t\tox = 70, oy = 30 },
}

-- Every key from the table above, for the ownership scan and the log.
local ALL_ABILITY_KEYS = {}
for _, ability in ipairs(ABILITIES) do
\tfor _, key in ipairs(ability.keys) do
\t\tALL_ABILITY_KEYS[#ALL_ABILITY_KEYS + 1] = key
\tend
end

-- The ABILITIES entry behind a marker, and behind a badge id (the click
-- router works in badge ids).
local function ability_for(marker)
\tfor _, ability in ipairs(ABILITIES) do
\t\tif ability.marker == marker then return ability end
\tend
\treturn nil
end

local function ability_for_badge(badge_id)
\tfor _, ability in ipairs(ABILITIES) do
\t\tif ability.badge == badge_id then return ability end
\tend
\treturn nil
end
""",
"ABILITIES table + key list + lookups")

# --- 2. section 1: the 90 s / 20 s brakes become the SHORT guard ---
rep("""-- After an accepted activation, wait this long before trying again. This is the
-- ability's own recharge_time from the database - not a guess.
local ABILITY_RECHARGE_SECONDS = 90

-- How often, in milliseconds, we look at the battlefield. 250 ms = 4x a second.
local POLL_MS = 250

-- Safety brake: never fire the same unit twice within this many seconds.
-- The ability's own cooldown is 90 s; this only protects us if the game's
-- "can I use this?" check turns out not to include the cooldown.
local MIN_SECONDS_BETWEEN_FIRES = 20
""",
"""-- How often, in milliseconds, we look at the battlefield. 250 ms = 4x a second.
local POLL_MS = 250

-- THE SHORT GUARD - the short safety brake, in seconds, per (unit, ability):
-- no pair may attempt twice inside this window. The readiness gate (the
-- engine's own can_perform check, section 4) is the real brake now - there
-- are NO 60/90 s timers anywhere any more.
local GUARD_SECONDS = 2
""",
"the short guard replaces the 90 s / 20 s brakes")

# --- 3. section 2: bookkeeping - per-ability state, guard, switch table ---
rep("""local tracked_units = nil                 -- units we watch
local target_key_by_unit = {}
local last_fired_at_tick = {}             -- when we last fired, per unit
local pending_verify = nil                -- a deferred "did it take effect?" check
local tick_count = 0                      -- our battle clock
local MIN_TICKS_BETWEEN_FIRES = (MIN_SECONDS_BETWEEN_FIRES * 1000) / POLL_MS
""",
"""local tracked_units = nil                 -- units we watch
local target_key_by_unit = {}             -- ui id -> the first of our keys found on the unit
local auto_state = {}                     -- marker -> true/false (the M/A switch, one per ability)
local last_attempt_at = {}                -- "ui_id|marker" -> tick of the last attempt
local pending_verify = nil                -- a deferred "did it take effect?" check
local tick_count = 0                      -- our battle clock
local GUARD_TICKS = (GUARD_SECONDS * 1000) / POLL_MS

-- The per-ability state, indexed by marker: the dial button the HUD scan found,
-- its event-reporting chain, the M/A badge component and its placement and
-- visibility bookkeeping. Nothing per-unit lives here.
local ability_state = {}
for _, ability in ipairs(ABILITIES) do
\tability_state[ability.marker] = { watch_chain = {} }
\tauto_state[ability.marker] = false
end

-- One compact "which switches are on" string, for the tick and heartbeat logs.
local function auto_states_string()
\tlocal bits = {}
\tfor _, ability in ipairs(ABILITIES) do
\t\tbits[#bits + 1] = ability.marker .. "=" .. (auto_state[ability.marker] and "ON" or "OFF")
\tend
\treturn table.concat(bits, ",")
end
""",
"bookkeeping: auto_state, guard, ability_state")

# --- 4a. section 4: the ownership scan reads every ability key ---
rep("""\t\tfor _, wanted_key in ipairs(ABILITY_KEYS) do
\t\t\tif owned_key == wanted_key then""",
"""\t\tfor _, wanted_key in ipairs(ALL_ABILITY_KEYS) do
\t\t\tif owned_key == wanted_key then""",
"scan_unit_abilities uses ALL_ABILITY_KEYS")

# --- 4b. section 4: owned_key_in + the readiness gate ---
rep("""\treturn matching_key, all_keys
end


-- ============================================================================
-- 5. IS IT ACTUALLY CHARGING?""",
"""\treturn matching_key, all_keys
end

-- Which key of this ability (if any) did the unit list among its own? Used by
-- the watch-list log. owned_keys is the all_keys list scan_unit_abilities gave.
local function owned_key_in(ability, owned_keys)
\tfor _, wanted_key in ipairs(ability.keys) do
\t\tfor _, owned_key in ipairs(owned_keys) do
\t\t\tif owned_key == wanted_key then return wanted_key end
\t\tend
\tend
\treturn nil
end

-- THE READINESS GATE (the engine's own "can I use this?" check), tried against
-- every key this ability answers to. The first key that returns true is the one
-- to fire, so nothing has to guess which duplicate database definition a unit
-- is carrying. Returns the key or nil, plus a text summary of every answer
-- (logged on each evaluation, like the earlier two-ability build).
local function check_readiness(unit, ability)
\tlocal ready_key = nil
\tlocal parts = {}

\tfor _, wanted_key in ipairs(ability.keys) do
\t\tlocal ok_c, can = pcall(function()
\t\t\treturn unit:can_perform_special_ability(wanted_key)
\t\tend)
\t\tparts[#parts + 1] = wanted_key .. "=" .. tostring(ok_c and tostring(can) or "ERROR")
\t\tif ok_c and can == true and ready_key == nil then
\t\t\tready_key = wanted_key
\t\tend
\tend

\treturn ready_key, table.concat(parts, ", ")
end


-- ============================================================================
-- 5. IS IT ACTUALLY CHARGING?""",
"owned_key_in + check_readiness")

# --- 5. section 6: the watch-list log states ownership per ability ---
rep("""\t\tlog("  unit '" .. tostring(unit:type()) .. "'"
\t\t\t.. " ui id " .. tostring(ui_id)
\t\t\t.. " | " .. tostring(#all_keys) .. " abilities"
\t\t\t.. " | owns Deadly Onslaught = " .. tostring(matching_key ~= nil)
\t\t\t.. (matching_key and (" as '" .. matching_key .. "'") or "")
\t\t\t.. " | usable right now = "
\t\t\t.. tostring(unit:can_perform_special_ability(ABILITY_KEYS[1])))""",
"""\t\tlocal own_parts = {}
\t\tfor _, ability in ipairs(ABILITIES) do
\t\t\tlocal owned_key = owned_key_in(ability, all_keys)
\t\t\town_parts[#own_parts + 1] = "owns " .. ability.name .. " = "
\t\t\t\t.. tostring(owned_key ~= nil)
\t\t\t\t.. (owned_key and (" as '" .. owned_key .. "'") or "")
\t\tend

\t\tlog("  unit '" .. tostring(unit:type()) .. "'"
\t\t\t.. " ui id " .. tostring(ui_id)
\t\t\t.. " | " .. tostring(#all_keys) .. " abilities"
\t\t\t.. " | " .. table.concat(own_parts, " | ")
\t\t\t.. " | usable right now = "
\t\t\t.. tostring(unit:can_perform_special_ability(ALL_ABILITY_KEYS[1])))""",
"watch-list log: ownership per ability")

# --- 6. section 5b: the switch is per ability now ---
rep("""local AUTO_ENABLED = false         -- <- the switch itself: OFF at battle start (the badge shows
                                   --    M) until the player clicks the badge. The badge click is
                                   --    the ONLY control - the keyboard, right-click and
                                   --    double-click routes have all been removed (rounds 15-25
                                   --    measured that nothing else reaches script in battle).""",
"""-- (Each ability's switch is auto_state[marker], section 2: all false at battle
--  start (the badges show M) until the player clicks a badge. Each badge click
--  flips ONLY its own ability - there is no global switch any more. The badge
--  click is the ONLY control - the keyboard, right-click and double-click
--  routes have all been removed (rounds 15-25 measured that nothing else
--  reaches script in battle).)""",
"AUTO_ENABLED declaration becomes a note")

# --- 7. section 6: heartbeat shows every switch ---
rep("""\t\t"auto=" .. (AUTO_ENABLED and "ON" or "OFF"),""",
"""\t\t"auto=" .. auto_states_string(),""",
"heartbeat auto field is per ability")

# --- 8. section 7: drop the 90 s brake bookkeeping ---
rep("""-- How long after an accepted activation to leave the ability alone, in ticks.
local ACTIVATION_BRAKE_TICKS = (ABILITY_RECHARGE_SECONDS * 1000) / POLL_MS
local activated_at_tick = {}          -- ui id -> tick of the last accepted activation
""",
"""-- (The old fixed brakes - 90 s per unit after an accepted activation, and the
--  20 s floor between attempts - are gone. The readiness gate (section 4) and
--  the short guard (GUARD_SECONDS, section 1) are the whole brake now.)
""",
"activation brake bookkeeping removed")

# --- 9. attempt_activation: the marker names the ability in the log ---
rep("""local function attempt_activation(script_unit, unit, ability_key, reason, ui_id)
\tlog("ATTEMPT " .. ability_key .. " on '" .. tostring(unit:type())
\t\t.. "' ui id " .. tostring(ui_id) .. " | reason: " .. reason)""",
"""local function attempt_activation(script_unit, unit, ability_key, reason, ui_id, marker)
\tlog("ATTEMPT " .. tostring(marker) .. " '" .. ability_key .. "' on '" .. tostring(unit:type())
\t\t.. "' ui id " .. tostring(ui_id) .. " | reason: " .. reason)""",
"attempt_activation logs the marker")

rep("""\tif ok_call then
\t\tactivated_at_tick[ui_id] = tick_count
\t\tlog("  perform_special_ability(key, unit) : ACCEPTED")
\t\tlog("  next attempt for this unit in " .. tostring(ABILITY_RECHARGE_SECONDS) .. " s")""",
"""\tif ok_call then
\t\tlog("  perform_special_ability(key, unit) : ACCEPTED")
\t\tlog("  the readiness gate decides the next attempt (plus the "
\t\t\t.. tostring(GUARD_SECONDS) .. " s guard)")""",
"accepted branch: readiness gate wording")

rep("""\t\tif string.find(err_text, "does not support this special ability") ~= nil then
\t\t\tlog("  -> engine says the unit cannot use it right now, which is what it")
\t\t\tlog("     says while the ability is active/on cooldown. Treating that as")
\t\t\tlog("     evidence an earlier activation worked.")
\t\t\tactivated_at_tick[ui_id] = tick_count
\t\tend""",
"""\t\tif string.find(err_text, "does not support this special ability") ~= nil then
\t\t\tlog("  -> engine says the unit cannot use it right now, which is what it")
\t\t\tlog("     says while the ability is active/on cooldown. The readiness gate")
\t\t\tlog("     will hold the next attempt back until the engine says yes again.")
\t\tend""",
"rejected branch: readiness gate wording")

# --- 10. poll body: the tick log names every switch ---
rep("""\t\t\t.. " | conflict=" .. tostring(bm:is_conflict_phase())
\t\t\t.. " | auto=" .. (AUTO_ENABLED and "ON" or "OFF")""",
"""\t\t\t.. " | conflict=" .. tostring(bm:is_conflict_phase())
\t\t\t.. " | auto=" .. auto_states_string()""",
"tick log auto field is per ability")

# --- 11. poll body: the firing loop runs once per ability ---
rep("""\t\t\t-- The switch: when it is off, nothing is fired at all.
\t\t\tif AUTO_ENABLED and ability_key ~= nil then
\t\t\t\t-- The game's own gate, exactly as vanilla does it: only order
\t\t\t\t-- an ability the unit can actually perform right now.
\t\t\t\tif unit:can_perform_special_ability(ability_key) then

\t\t\t\t\tlocal m = measure_charge(unit)

\t\t\t\t\tlocal reason = nil

\t\t\t\t\tif FIRE_ON_CHARGE and m.charging then
\t\t\t\t\t\treason = string.format(
\t\t\t\t\t\t\t"charging (gap=%.1fm dist=%.1fm eta=%.1fs)",
\t\t\t\t\t\t\tm.order_gap, m.target_dist, m.ttc)
\t\t\t\t\telseif FIRE_ON_MELEE and m.melee then
\t\t\t\t\t\treason = "in melee"
\t\t\t\t\tend

\t\t\t\t\tif reason ~= nil then
\t\t\t\t\t\tlocal last_attempt = last_fired_at_tick[ui_id] or -999999
\t\t\t\t\t\tlocal last_success = activated_at_tick[ui_id] or -999999

\t\t\t\t\t\t-- Two brakes: a floor between attempts, and the ability's
\t\t\t\t\t\t-- own recharge time once it has actually fired.
\t\t\t\t\t\tif (tick_count - last_attempt) >= MIN_TICKS_BETWEEN_FIRES
\t\t\t\t\t\t\tand (tick_count - last_success) >= ACTIVATION_BRAKE_TICKS then

\t\t\t\t\t\t\tlast_fired_at_tick[ui_id] = tick_count
\t\t\t\t\t\t\tattempt_activation(script_unit, unit, ability_key, reason, ui_id)
\t\t\t\t\t\tend
\t\t\t\t\tend
\t\t\t\tend
\t\t\tend""",
"""\t\t\t-- One pass per ability (section 1): its own switch, its own
\t\t\t-- trigger, then the readiness gate and the short guard.
\t\t\tfor _, ability in ipairs(ABILITIES) do

\t\t\t\tif auto_state[ability.marker] == true then
\t\t\t\t\tlocal reason = nil

\t\t\t\t\tif ability.trigger == "charge" then
\t\t\t\t\t\t-- The existing charge conditions, verbatim (section 5).
\t\t\t\t\t\tlocal m = measure_charge(unit)

\t\t\t\t\t\tif FIRE_ON_CHARGE and m.charging then
\t\t\t\t\t\t\treason = string.format(
\t\t\t\t\t\t\t\t"charging (gap=%.1fm dist=%.1fm eta=%.1fs)",
\t\t\t\t\t\t\t\tm.order_gap, m.target_dist, m.ttc)
\t\t\t\t\t\telseif FIRE_ON_MELEE and m.melee then
\t\t\t\t\t\t\treason = "in melee"
\t\t\t\t\t\tend
\t\t\t\t\telseif ability.trigger == "running" then
\t\t\t\t\t\t-- The engine's own run-versus-walk test.
\t\t\t\t\t\tif unit:is_moving_fast() then
\t\t\t\t\t\t\treason = "running"
\t\t\t\t\t\tend
\t\t\t\t\tend

\t\t\t\t\tif reason ~= nil then
\t\t\t\t\t\t-- The readiness gate: the engine's own check, tried
\t\t\t\t\t\t-- against every key this ability answers to, with
\t\t\t\t\t\t-- every answer logged on this evaluation.
\t\t\t\t\t\tlocal ready_key, readiness = check_readiness(unit, ability)
\t\t\t\t\t\tlog("  readiness " .. ability.marker .. " on ui id " .. tostring(ui_id)
\t\t\t\t\t\t\t.. ": " .. readiness)

\t\t\t\t\t\tif ready_key ~= nil then
\t\t\t\t\t\t\t-- The SHORT SAFETY BRAKE, alongside the readiness
\t\t\t\t\t\t\t-- gate: one attempt per (unit, ability) per
\t\t\t\t\t\t\t-- GUARD_SECONDS. No 60/90 s timers anywhere.
\t\t\t\t\t\t\tlocal guard_key = tostring(ui_id) .. "|" .. ability.marker
\t\t\t\t\t\t\tlocal last_attempt = last_attempt_at[guard_key] or -999999

\t\t\t\t\t\t\tif (tick_count - last_attempt) >= GUARD_TICKS then
\t\t\t\t\t\t\t\tlast_attempt_at[guard_key] = tick_count
\t\t\t\t\t\t\t\tattempt_activation(script_unit, unit, ready_key, reason, ui_id,
\t\t\t\t\t\t\t\t\tability.marker)
\t\t\t\t\t\t\tend
\t\t\t\t\t\tend
\t\t\t\t\tend
\t\t\t\tend
\t\t\tend""",
"firing loop: per ability, readiness-gated, short guard")

# --- 12. section 8b: per-ability globals ---
rep("""local our_button = nil          -- the component itself, for the feedback
local watch_chain = {}          -- the ability button and its ancestors, all reporting events
local feedback_on = nil         -- last feedback state we applied""",
"""-- (The single button reference, watch chain and feedback flag that used to sit
--  here are per ability now - ability_state[marker].button / .watch_chain /
--  .feedback_on, section 2.)""",
"single-button globals become per-ability state")

rep("""local function read_icon()
\tif our_button == nil then return nil end
\tlocal ok, path = pcall(function() return our_button:GetImagePath(ICON_INDEX) end)
\tif ok then return tostring(path) end
\treturn nil
end""",
"""local function read_icon(button)
\tif button == nil then return nil end
\tlocal ok, path = pcall(function() return button:GetImagePath(ICON_INDEX) end)
\tif ok then return tostring(path) end
\treturn nil
end""",
"read_icon takes the button")

# --- 13. section 8b: the badge section, per ability ---
rep("""-- THE BADGE (option B, done right). Rounds 32-33 measured two things: an engine-owned ability
-- button does not draw children, and writing to it rebuilds it. So the badge is created on the
-- button's own ancestor (a plain container, the kind that demonstrably draws components we create),
-- and every UI tick it is MOVED to the ability button's top-right corner from the button's own
-- coordinates. Reading the button is safe; only writing to it is fatal.
local badge = nil
local badge_parent = nil
local placed = false
local badge_visible_state = nil
local badge_shown = false     -- is the badge currently SHOWN? Hide-by-default: only the ui_tick
                              -- confirmation (bottom of the file) may turn it on, and only while
                              -- the ability is positively confirmed on the dial
local track = false          -- no computed tracking: the frames of reference do not match
                             -- (round 42). Position is the hand-tuned offset above.
local BADGE_X, BADGE_Y = -865, -209   -- the spot tuned by hand in-game (round 41), used as-is.
                                     -- MINUS is left/up, PLUS is right/down, from the bottom-centre
                                     -- dock of the badge's parent.""",
"""-- THE BADGES - one per ability (option B, done right). Rounds 32-33 measured two things: an
-- engine-owned ability button does not draw children, and writing to it rebuilds it. So each
-- badge is created on the button's own ancestor (a plain container, the kind that demonstrably
-- draws components we create). Reading the button is safe; only writing to it is fatal.
--
-- Each ability has ONE badge component (the id from the table in section 1: zz_auto_badge for
-- Deadly Onslaught, zz_auto_badge_fs for Foe-Seeker), created HIDDEN and SHOWN only while ITS
-- ability is positively confirmed on the dial (the ui_tick test at the bottom of the file).
-- Its letter shows its own switch - "A" = auto, "M" = manual - and a click on it is the only
-- control. The components and flags live in ability_state[marker] (section 2).
local badge_parent = nil
local track = false          -- no computed tracking: the frames of reference do not match
                             -- (round 42). Position is the hand-tuned offset above.
local BADGE_X, BADGE_Y = -865, -209   -- the spot tuned by hand in-game (round 41), used as-is.
                                     -- MINUS is left/up, PLUS is right/down, from the bottom-centre
                                     -- dock of the badge's parent. Each ability's badge adds its
                                     -- own ox/oy from the table in section 1 (foe_seeker:
                                     -- +70,+30 - the measured top-slot-to-45-degree step), so a
                                     -- re-tune of these two numbers carries Foe-Seeker along.""",
"badge globals become per-ability")

rep("""local function create_badge()
\tif our_button == nil or badge ~= nil then return end
\t-- parent it on hud_battle (the HUD root): a plain container with no LayoutEngine arranging its
\t-- children, and its origin is the screen's, so the offset space equals the coordinates the button
\t-- reports. Round 37's log showed the previous parent (battle_orders) ignoring SetDockOffset.
\tlocal node = our_button
\tfor _ = 1, 8 do
\t\tlocal ok_id, id = pcall(function() return node:Id() end)
\t\tif ok_id and tostring(id) == "hud_battle" then break end
\t\tlocal ok_p, parent = pcall(function() return node:Parent() end)
\t\tif not ok_p or parent == nil then break end
\t\tlocal ok_w, wrapped = pcall(function() return UIComponent(parent) end)
\t\tif not ok_w or wrapped == nil then break end
\t\tnode = wrapped
\tend
\tbadge_parent = node
\tlocal ok, err = pcall(function()
\t\tbadge = UIComponent(badge_parent:CreateComponent("zz_auto_badge", "ui/templates/zz_auto_badge"))
\tend)
\tif not ok or badge == nil then
\t\tlog("badge: CreateComponent failed (" .. tostring(err) .. ")")
\t\tbadge = nil
\t\treturn
\tend
\tlocal ok_id, pid = pcall(function() return badge_parent:Id() end)
\tlog("badge: created on '" .. tostring(ok_id and pid or "?") .. "' (not on the ability button)")
\tpcall(function() badge:SetDockingPoint(0) end)
\tpcall(function() badge:Resize(24, 24) end)   -- room for the letter
\t-- the bronze "A": our copy of a real vanilla text layout (colour changed in the file),
\t-- the string supplied here - SetText exists, SetTextColour does not
\t-- the letter carries the look now, so blank the template's own title-bar art underneath it
\tfor i = 0, 4 do
\t\tpcall(function() badge:SetImagePath("ui/zz_auto/blank.png", i) end)
\t\tlocal ok_r, rep = pcall(function() return badge:GetImagePath(i) end)
\t\tlog("   art slot " .. i .. " -> '" .. tostring(ok_r and rep or "?") .. "'")
\tend
\tlocal ok_p = pcall(function() badge:SetText("A") end)
\tlocal ok_g, got = pcall(function() return badge:GetText() end)
\tlog("   set text ok=" .. tostring(ok_p) .. " engine reports='" .. tostring(ok_g and got or "?") .. "'")
\t-- HIDDEN AT BIRTH: showing is now strictly the ui_tick confirmation's job (bottom of the
\t-- file), so a fresh badge can never linger on screen by the template's own default.
\tbadge_shown = false
\tpcall(function() badge:SetVisible(false) end)
end""",
"""local function create_badge(marker)
\tlocal state = ability_state[marker]
\tlocal ability = ability_for(marker)
\tif state == nil or state.button == nil or state.badge ~= nil then return end
\t-- parent it on hud_battle (the HUD root): a plain container with no LayoutEngine arranging its
\t-- children, and its origin is the screen's, so the offset space equals the coordinates the button
\t-- reports. Round 37's log showed the previous parent (battle_orders) ignoring SetDockOffset.
\tlocal node = state.button
\tfor _ = 1, 8 do
\t\tlocal ok_id, id = pcall(function() return node:Id() end)
\t\tif ok_id and tostring(id) == "hud_battle" then break end
\t\tlocal ok_p, parent = pcall(function() return node:Parent() end)
\t\tif not ok_p or parent == nil then break end
\t\tlocal ok_w, wrapped = pcall(function() return UIComponent(parent) end)
\t\tif not ok_w or wrapped == nil then break end
\t\tnode = wrapped
\tend
\tbadge_parent = node
\tlocal ok, err = pcall(function()
\t\tstate.badge = UIComponent(badge_parent:CreateComponent(ability.badge,
\t\t\t"ui/templates/zz_auto_badge"))
\tend)
\tif not ok or state.badge == nil then
\t\tlog("badge [" .. marker .. "]: CreateComponent failed (" .. tostring(err) .. ")")
\t\tstate.badge = nil
\t\treturn
\tend
\tlocal ok_id, pid = pcall(function() return badge_parent:Id() end)
\tlog("badge [" .. marker .. "]: created on '" .. tostring(ok_id and pid or "?")
\t\t.. "' (not on the ability button)")
\tpcall(function() state.badge:SetDockingPoint(0) end)
\tpcall(function() state.badge:Resize(24, 24) end)   -- room for the letter
\t-- the bronze "A": our copy of a real vanilla text layout (colour changed in the file),
\t-- the string supplied here - SetText exists, SetTextColour does not
\t-- the letter carries the look now, so blank the template's own title-bar art underneath it
\tfor i = 0, 4 do
\t\tpcall(function() state.badge:SetImagePath("ui/zz_auto/blank.png", i) end)
\t\tlocal ok_r, rep = pcall(function() return state.badge:GetImagePath(i) end)
\t\tlog("   badge [" .. marker .. "] art slot " .. i .. " -> '"
\t\t\t.. tostring(ok_r and rep or "?") .. "'")
\tend
\tlocal ok_p = pcall(function() state.badge:SetText("A") end)
\tlocal ok_g, got = pcall(function() return state.badge:GetText() end)
\tlog("   badge [" .. marker .. "] set text ok=" .. tostring(ok_p) .. " engine reports='"
\t\t.. tostring(ok_g and got or "?") .. "'")
\t-- HIDDEN AT BIRTH: showing is strictly the ui_tick confirmation's job (bottom of the
\t-- file), so a fresh badge can never linger on screen by the template's own default.
\tstate.badge_shown = false
\tpcall(function() state.badge:SetVisible(false) end)
end""",
"create_badge(marker) with the ability's badge id")

rep("""local function button_xy()
\tif our_button == nil then return nil, nil end
\tlocal ok, a, b = pcall(function() return our_button:Position() end)
\tif ok and type(a) == "number" and type(b) == "number" then return a, b end
\treturn nil, nil
end""",
"""local function button_xy(button)
\tif button == nil then return nil, nil end
\tlocal ok, a, b = pcall(function() return button:Position() end)
\tif ok and type(a) == "number" and type(b) == "number" then return a, b end
\treturn nil, nil
end""",
"button_xy takes the button")

rep("""local function place_badge()
\tif badge == nil then return end

\t-- TRACK MODE (round 40): the two numbers below stop being "where on the bar" and become the
\t-- constant delta from the ability button's OWN position, recomputed every tick. Tune the delta
\t-- once with the console while tracking, and the badge follows that icon - and, per ability, its
\t-- own icon, since each badge is created for its own button.
\tif track then
\t\tlocal bx, by = button_xy()
\t\tif bx ~= nil then
\t\t\tpcall(function() badge:SetDockOffset(bx + BADGE_X, by + BADGE_Y) end)
\t\tend
\t\treturn
\tend

\tif placed then return end
\t-- AI General's proven configuration, and nothing cleverer than it: dock the created component to
\t-- the BOTTOM-CENTRE of the bar and give it one offset. Round 38 proved the engine both reinterprets
\t-- offsets and misreports the component's position, so there is nothing to steer by - one shot, and
\t-- the numbers below are the only knobs left.
\tpcall(function() badge:SetDockingPoint(8) end)                 -- 8 = bottom-centre
\tlocal ok_o = pcall(function() badge:SetDockOffset(BADGE_X, BADGE_Y) end)
\tpcall(function() badge_parent:Layout() end)
\tplaced = true
\tlog("badge: placed bottom-centre of '" .. tostring(badge_parent:Id()) .. "' (offset "
\t\t.. tostring(BADGE_X) .. "," .. tostring(BADGE_Y) .. ") ok=" .. tostring(ok_o))
end""",
"""local function place_badge(marker)
\tlocal state = ability_state[marker]
\tlocal ability = ability_for(marker)
\tif state == nil or state.badge == nil or ability == nil then return end

\t-- The badge's own offset: BADGE_X/BADGE_Y plus this ability's ox/oy from
\t-- section 1 (onslaught: +0,+0; foe_seeker: +70,+30), COMPUTED here so a
\t-- re-tune of BADGE_X/BADGE_Y carries every badge along.
\tlocal ox, oy = BADGE_X + ability.ox, BADGE_Y + ability.oy

\t-- TRACK MODE (round 40): the two numbers above stop being "where on the bar" and become the
\t-- constant delta from the ability button's OWN position, recomputed every tick. Tune the delta
\t-- once with the console while tracking, and the badge follows that icon - and, per ability, its
\t-- own icon, since each badge is created for its own button.
\tif track then
\t\tlocal bx, by = button_xy(state.button)
\t\tif bx ~= nil then
\t\t\tpcall(function() state.badge:SetDockOffset(bx + ox, by + oy) end)
\t\tend
\t\treturn
\tend

\tif state.placed then return end
\t-- AI General's proven configuration, and nothing cleverer than it: dock the created component to
\t-- the BOTTOM-CENTRE of the bar and give it one offset. Round 38 proved the engine both reinterprets
\t-- offsets and misreports the component's position, so there is nothing to steer by - one shot, and
\t-- the numbers above are the only knobs left.
\tpcall(function() state.badge:SetDockingPoint(8) end)                 -- 8 = bottom-centre
\tlocal ok_o = pcall(function() state.badge:SetDockOffset(ox, oy) end)
\tpcall(function() badge_parent:Layout() end)
\tstate.placed = true
\tlog("badge [" .. marker .. "]: placed bottom-centre of '" .. tostring(badge_parent:Id())
\t\t.. "' (offset " .. tostring(ox) .. "," .. tostring(oy) .. ") ok=" .. tostring(ok_o))
end

-- Re-place every ability's badge from the current BADGE_X/BADGE_Y (the console
-- hooks call this, so a re-tune of the Deadly Onslaught badge carries Foe-Seeker).
local function replace_all_badges()
\tfor _, ability in ipairs(ABILITIES) do
\t\tlocal state = ability_state[ability.marker]
\t\tif state ~= nil then
\t\t\tstate.placed = false
\t\t\tpcall(place_badge, ability.marker)
\t\tend
\tend
end""",
"place_badge(marker) + replace_all_badges")

rep("""local function badge_visible(on)
\tif badge == nil then return end
\tbadge_visible_state = on          -- keep the tick's idea of the state in step with the switch
\t-- The badge never hides for the switch any more: it stays on screen and shows the LETTER for
\t-- the state - "A" = auto, "M" = manual. SetText is the one call that has never failed us,
\t-- unlike colour (no API) and opacity (renders as nothing). The badge still hides only when
\t-- the dial stops showing our ability.
\tlocal ok_v = pcall(function() badge:SetVisible(true) end)
\tlocal ok_t = pcall(function() badge:SetText(on and "A" or "M") end)
\tlog("   badge letter='" .. (on and "A" or "M") .. "' (auto " .. (on and "ON" or "OFF")
\t\t.. ") visible=" .. tostring(ok_v) .. " text=" .. tostring(ok_t))
end""",
"""local function badge_visible(marker, on)
\tlocal state = ability_state[marker]
\tif state == nil or state.badge == nil then return end
\tstate.badge_visible_state = on    -- keep the tick's idea of the state in step with the switch
\t-- The badge never hides for the switch any more: it stays on screen and shows the LETTER for
\t-- the state - "A" = auto, "M" = manual. SetText is the one call that has never failed us,
\t-- unlike colour (no API) and opacity (renders as nothing). The badge still hides only when
\t-- the dial stops showing our ability.
\tlocal ok_v = pcall(function() state.badge:SetVisible(true) end)
\tlocal ok_t = pcall(function() state.badge:SetText(on and "A" or "M") end)
\tlog("   badge [" .. marker .. "] letter='" .. (on and "A" or "M") .. "' (auto "
\t\t.. (on and "ON" or "OFF") .. ") visible=" .. tostring(ok_v) .. " text=" .. tostring(ok_t))
end""",
"badge_visible(marker, on)")

# --- 14. console hooks, per ability ---
rep("""function zz_badge_set(x, y)
\tBADGE_X = tonumber(x) or BADGE_X
\tBADGE_Y = tonumber(y) or BADGE_Y
\tplaced = false
\tpcall(place_badge)
\tlocal msg = "BADGE offset = " .. tostring(BADGE_X) .. "," .. tostring(BADGE_Y)
\t\t.. " track=" .. tostring(track)
\tlog(msg)
\treturn msg
end""",
"""function zz_badge_set(x, y)
\tBADGE_X = tonumber(x) or BADGE_X
\tBADGE_Y = tonumber(y) or BADGE_Y
\t-- re-place EVERY ability's badge: each one's offset is BADGE_X/BADGE_Y plus
\t-- its own ox/oy, computed in place_badge, so a re-tune of the Deadly
\t-- Onslaught badge carries Foe-Seeker along.
\treplace_all_badges()
\tlocal msg = "BADGE offset = " .. tostring(BADGE_X) .. "," .. tostring(BADGE_Y)
\t\t.. " track=" .. tostring(track)
\tlog(msg)
\treturn msg
end""",
"zz_badge_set re-places every badge")

rep("""\tlocal bx, by = button_xy()
\tif bx == nil then
\t\tlocal m = "BADGE mode switch failed: no button position"
\t\tlog(m)
\t\treturn m
\tend
\tif want then
\t\tBADGE_X, BADGE_Y = BADGE_X - bx, BADGE_Y - by
\telse
\t\tBADGE_X, BADGE_Y = BADGE_X + bx, BADGE_Y + by
\tend
\ttrack = want
\tplaced = false
\tpcall(place_badge)""",
"""\tlocal master = ability_state[ABILITIES[1].marker]
\tlocal bx, by = button_xy(master ~= nil and master.button or nil)
\tif bx == nil then
\t\tlocal m = "BADGE mode switch failed: no button position"
\t\tlog(m)
\t\treturn m
\tend
\tif want then
\t\tBADGE_X, BADGE_Y = BADGE_X - bx, BADGE_Y - by
\telse
\t\tBADGE_X, BADGE_Y = BADGE_X + bx, BADGE_Y + by
\tend
\ttrack = want
\treplace_all_badges()""",
"zz_badge_track re-places every badge")

rep("""function zz_badge_show()
\tif badge == nil then return "badge not created yet" end
\tpcall(function() badge:SetVisible(true) end)
\treturn "badge shown at " .. tostring(BADGE_X) .. "," .. tostring(BADGE_Y)
end""",
"""function zz_badge_show(marker)
\tmarker = marker or "onslaught"
\tlocal state = ability_state[marker]
\tif state == nil or state.badge == nil then return "badge not created yet" end
\tpcall(function() state.badge:SetVisible(true) end)
\tlocal ability = ability_for(marker)
\treturn "badge shown at " .. tostring(BADGE_X + ability.ox) .. "," .. tostring(BADGE_Y + ability.oy)
end""",
"zz_badge_show is marker-aware")

rep("""function zz_badge_hide()
\tif badge == nil then return "badge not created yet" end
\tpcall(function() badge:SetVisible(false) end)
\treturn "badge hidden"
end""",
"""function zz_badge_hide(marker)
\tmarker = marker or "onslaught"
\tlocal state = ability_state[marker]
\tif state == nil or state.badge == nil then return "badge not created yet" end
\tpcall(function() state.badge:SetVisible(false) end)
\treturn "badge hidden"
end""",
"zz_badge_hide is marker-aware")

rep("""function zz_badge_parent()
\tif badge_parent == nil then return "no parent yet" end
\tlocal ok, id = pcall(function() return badge_parent:Id() end)
\tlocal ok2, w = pcall(function() return badge_parent:Width() end)
\tlocal ok3, h = pcall(function() return badge_parent:Height() end)
\tlocal bx, by = button_xy()
\tlocal msg = "BADGE parent=" .. tostring(ok and id or "?") .. " size=" .. tostring(w)
\t\t.. "x" .. tostring(h) .. " offset=" .. tostring(BADGE_X) .. "," .. tostring(BADGE_Y)
\t\t.. " track=" .. tostring(track) .. " button=" .. tostring(bx) .. "," .. tostring(by)
\tlog(msg)
\treturn msg
end""",
"""function zz_badge_parent(marker)
\tmarker = marker or "onslaught"
\tif badge_parent == nil then return "no parent yet" end
\tlocal ability = ability_for(marker)
\tif ability == nil then return "no ability with marker '" .. tostring(marker) .. "'" end
\tlocal state = ability_state[marker]
\tlocal ok, id = pcall(function() return badge_parent:Id() end)
\tlocal ok2, w = pcall(function() return badge_parent:Width() end)
\tlocal ok3, h = pcall(function() return badge_parent:Height() end)
\tlocal bx, by = button_xy(state ~= nil and state.button or nil)
\tlocal msg = "BADGE parent=" .. tostring(ok and id or "?") .. " size=" .. tostring(w)
\t\t.. "x" .. tostring(h) .. " offset=" .. tostring(BADGE_X + ability.ox) .. ","
\t\t.. tostring(BADGE_Y + ability.oy)
\t\t.. " track=" .. tostring(track) .. " button=" .. tostring(bx) .. "," .. tostring(by)
\t\t.. " marker=" .. tostring(marker)
\tlog(msg)
\treturn msg
end""",
"zz_badge_parent is marker-aware")

# --- 15. the feedback + set_auto go per ability ---
rep("""local function set_armed_look(on)
\t-- Availability is NEVER touched: the ability can always be used by hand.
\t-- The state is shown by the badge instead.
\tbadge_visible(on)
end
local function apply_ability_feedback()
\tif our_button == nil then return end
\tif feedback_on == AUTO_ENABLED then return end      -- nothing to change

\tset_armed_look(AUTO_ENABLED)
\tfeedback_on = AUTO_ENABLED
end

-- The one place the switch is flipped, whichever control did it.
local function set_auto(value, why)
\tAUTO_ENABLED = value
\tapply_ability_feedback()        -- the pulse on the ability icon - the only feedback now
\tlog("TOGGLE (" .. why .. ") - automatic activation is now "
\t\t.. (AUTO_ENABLED and "ON" or "OFF"))
end""",
"""local function set_armed_look(marker, on)
\t-- Availability is NEVER touched: the ability can always be used by hand.
\t-- The state is shown by the badge instead.
\tbadge_visible(marker, on)
end
local function apply_ability_feedback(marker)
\tlocal state = ability_state[marker]
\tif state == nil or state.button == nil then return end
\tif state.feedback_on == auto_state[marker] then return end   -- nothing to change

\tset_armed_look(marker, auto_state[marker])
\tstate.feedback_on = auto_state[marker]
end

-- The one place a switch is flipped, whichever control did it. Each ability
-- has its own switch and its own badge: a click flips ONLY that ability.
local function set_auto(value, why, marker)
\tauto_state[marker] = value
\tapply_ability_feedback(marker)   -- the letter on the badge - the only feedback now
\tlog("TOGGLE [" .. marker .. "] (" .. why .. ") - automatic activation is now "
\t\t.. (value and "ON" or "OFF"))
end""",
"set_auto is per ability")

# --- 16. the HUD scan claims one button per ability ---
rep("""local function scan_component(uic, depth)
\tif uic == nil or depth > 6 or walk_visits > 4000 or our_button ~= nil then return end
\twalk_visits = walk_visits + 1

\tlocal ok_key, key = pcall(function() return uic:InterfaceFunction("AbilityKeyForScript") end)
\tif ok_key and type(key) == "string" and string.len(key) > 3 then
\t\tlocal ok_addr, addr = pcall(function() return uic:Address() end)
\t\tlog("   ability button: key='" .. key .. "' id='" .. tostring(uic:Id())
\t\t\t.. "' address=" .. tostring(addr))
\t\tif string.find(string.lower(key), "onslaught") then
\t\t\tour_button = uic
\t\t\tlog("   ^ that one is ours")""",
"""-- True when every ability has its dial button: the scan stops there.
local function all_buttons_found()
\tfor _, ability in ipairs(ABILITIES) do
\t\tlocal state = ability_state[ability.marker]
\t\tif state == nil or state.button == nil then return false end
\tend
\treturn true
end

local function scan_component(uic, depth)
\tif uic == nil or depth > 6 or walk_visits > 4000 or all_buttons_found() then return end
\twalk_visits = walk_visits + 1

\tlocal ok_key, key = pcall(function() return uic:InterfaceFunction("AbilityKeyForScript") end)
\tif ok_key and type(key) == "string" and string.len(key) > 3 then
\t\tlocal ok_addr, addr = pcall(function() return uic:Address() end)
\t\tlog("   ability button: key='" .. key .. "' id='" .. tostring(uic:Id())
\t\t\t.. "' address=" .. tostring(addr))

\t\t-- One claim per ability: a button belongs to an ability when its key
\t\t-- contains the ability's marker as a case-insensitive substring, so
\t\t-- any database variant of the same ability attaches.
\t\tlocal claimed = nil
\t\tfor _, ability in ipairs(ABILITIES) do
\t\t\tlocal state = ability_state[ability.marker]
\t\t\tif state.button == nil
\t\t\t\tand string.find(string.lower(key), ability.marker, 1, true) ~= nil then
\t\t\t\tstate.button = uic
\t\t\t\tclaimed = ability
\t\t\t\tlog("   ^ that one is ours (" .. ability.marker .. ")")
\t\t\tend
\t\tend

\t\tif claimed ~= nil then""",
"scan claims one button per ability")

rep("""\t\t\twatch_chain = {}
\t\t\tlocal node = uic""",
"""\t\t\tlocal state = ability_state[claimed.marker]
\t\t\tstate.watch_chain = {}
\t\t\tlocal node = uic""",
"watch chain is per ability")

rep("""\t\t\t\twatch_chain[#watch_chain + 1] = { addr = (ok_a and addr or nil),""",
"""\t\t\t\tstate.watch_chain[#state.watch_chain + 1] = { addr = (ok_a and addr or nil),""",
"chain append is per ability")

rep("""\t\t\toriginal_icon = read_icon()""",
"""\t\t\toriginal_icon = read_icon(uic)""",
"read_icon gets the button")

rep("""\t\t\tapply_ability_feedback()

\t\t\t-- (Round 22: the property reads that used to live here are gone - every read echoed the""",
"""\t\t\tapply_ability_feedback(claimed.marker)

\t\t\t-- (Round 22: the property reads that used to live here are gone - every read echoed the""",
"feedback call is per ability")

rep("""local function find_ability_buttons()
\tif our_button ~= nil then return end
\twalk_visits = 0""",
"""local function find_ability_buttons()
\tif all_buttons_found() then return end
\twalk_visits = 0""",
"find_ability_buttons stops when all found")

rep("""\t\tlog("ability icons: scanning the HUD for ability buttons")
\t\tscan_component(hud, 0)
\t\tlog("   scan done: " .. tostring(walk_visits) .. " component(s) visited - "
\t\t\t.. (our_button ~= nil and "OURS FOUND" or "ours not found"))""",
"""\t\tlog("ability icons: scanning the HUD for ability buttons")
\t\tscan_component(hud, 0)

\t\tlocal found = {}
\t\tfor _, ability in ipairs(ABILITIES) do
\t\t\tif ability_state[ability.marker].button ~= nil then
\t\t\t\tfound[#found + 1] = ability.marker
\t\t\tend
\t\tend
\t\tlog("   scan done: " .. tostring(walk_visits) .. " component(s) visited - "
\t\t\t.. (#found > 0 and ("found: " .. table.concat(found, ", ")) or "none of ours found"))""",
"scan done line lists every found ability")

# --- 17. in_chain consults every ability's chain ---
rep("""local function in_chain(context)
\tfor i = 1, #watch_chain do
\t\tlocal e = watch_chain[i]
\t\tif e.addr ~= nil and context.component ~= nil and context.component == e.addr then
\t\t\treturn e.id or "?"
\t\tend
\tend
\tfor i = 1, #watch_chain do
\t\tlocal e = watch_chain[i]
\t\tif e.id ~= nil and context.string == e.id then return e.id end
\tend
\treturn nil
end""",
"""local function in_chain(context)
\tfor _, ability in ipairs(ABILITIES) do
\t\tlocal state = ability_state[ability.marker]
\t\tfor i = 1, #state.watch_chain do
\t\t\tlocal e = state.watch_chain[i]
\t\t\tif e.addr ~= nil and context.component ~= nil and context.component == e.addr then
\t\t\t\treturn e.id or "?"
\t\t\tend
\t\tend
\tend
\tfor _, ability in ipairs(ABILITIES) do
\t\tlocal state = ability_state[ability.marker]
\t\tfor i = 1, #state.watch_chain do
\t\t\tlocal e = state.watch_chain[i]
\t\t\tif e.id ~= nil and context.string == e.id then return e.id end
\t\tend
\tend
\treturn nil
end""",
"in_chain walks every ability's chain")

# --- 18. the click router flips only the clicked badge's ability ---
rep("""\t\t-- component is routed the same way, so an added or renamed badge keeps working. The flip
\t\t-- goes through set_auto() - the one place the switch changes.
\t\tif string.sub(clicked_id, 1, 8) == "zz_auto_" then
\t\t\tset_auto(not AUTO_ENABLED, "badge click on '" .. clicked_id .. "'")
\t\t\tlog("badge clicked - auto now "
\t\t\t\t.. (AUTO_ENABLED and "ON (letter 'A')" or "OFF (letter 'M')"))
\t\t\treturn
\t\tend""",
"""\t\t-- component is routed the same way, so an added or renamed badge keeps working. Each
\t\t-- badge id resolves to its own ability (section 1), so a click flips ONLY that ability;
\t\t-- the flip goes through set_auto() - the one place a switch changes.
\t\tif string.sub(clicked_id, 1, 8) == "zz_auto_" then
\t\t\tlocal ability = ability_for_badge(clicked_id)
\t\t\tif ability == nil then
\t\t\t\tlog("badge click on '" .. clicked_id
\t\t\t\t\t.. "' - no ability has that badge id, ignored")
\t\t\t\treturn
\t\t\tend
\t\t\tset_auto(not (auto_state[ability.marker] == true),
\t\t\t\t"badge click on '" .. clicked_id .. "'", ability.marker)
\t\t\tlog("badge [" .. ability.marker .. "] clicked - auto now "
\t\t\t\t.. (auto_state[ability.marker] and "ON (letter 'A')" or "OFF (letter 'M')"))
\t\t\treturn
\t\tend""",
"click router resolves the badge to its ability")

# --- 19. the dial dump: onslaught's button walks it, one footer per badge ---
rep("""local function log_dial_dump()
\tif our_button == nil then return end

\tlocal ok_p, parent = pcall(function() return our_button:Parent() end)""",
"""local function log_dial_dump()
\tlocal master = ability_state[ABILITIES[1].marker]
\tif master == nil or master.button == nil then return end

\tlocal ok_p, parent = pcall(function() return master.button:Parent() end)""",
"dial dump master button")

rep("""\tlocal dial_str = "?"
\tlocal node = our_button""",
"""\tlocal dial_str = "?"
\tlocal node = master.button""",
"dial dump walk starts at the master button")

rep("""\tlocal bvis, bpos, bletter = false, "(?,?)", "-"
\tif badge ~= nil then
\t\tbvis = badge_shown
\t\tlocal bx, by = read_xy(badge)
\t\tbpos = fmt_xy(bx, by)
\t\tlocal ok_g, got = pcall(function() return badge:GetText() end)
\t\tif ok_g and type(got) == "string" then
\t\t\tbletter = got
\t\telse
\t\t\tbletter = AUTO_ENABLED and "A" or "M"
\t\tend
\tend
\tlog("OUR BADGE: visible=" .. (bvis and "true" or "false") .. " pos=" .. bpos
\t\t.. " offset=(" .. tostring(BADGE_X) .. "," .. tostring(BADGE_Y) .. ") letter='" .. bletter .. "'")
end""",
"""\t-- ONE FOOTER LINE PER ABILITY: the badge's visibility, position and letter,
\t-- plus the offset it was placed at (BADGE_X/BADGE_Y + its own ox/oy). The
\t-- onslaught footer keeps its original wording; added abilities get a tag.
\tfor _, ability in ipairs(ABILITIES) do
\t\tlocal state = ability_state[ability.marker]
\t\tlocal bvis, bpos, bletter = false, "(?,?)", "-"
\t\tif state.badge ~= nil then
\t\t\tbvis = state.badge_shown == true
\t\t\tlocal bx, by = read_xy(state.badge)
\t\t\tbpos = fmt_xy(bx, by)
\t\t\tlocal ok_g, got = pcall(function() return state.badge:GetText() end)
\t\t\tif ok_g and type(got) == "string" then
\t\t\t\tbletter = got
\t\t\telse
\t\t\t\tbletter = auto_state[ability.marker] and "A" or "M"
\t\t\tend
\t\tend
\t\tlocal prefix = "OUR BADGE"
\t\tif ability.marker ~= "onslaught" then
\t\t\tprefix = prefix .. " [" .. ability.marker .. "]"
\t\tend
\t\tlog(prefix .. ": visible=" .. (bvis and "true" or "false") .. " pos=" .. bpos
\t\t\t.. " offset=(" .. tostring(BADGE_X + ability.ox) .. "," .. tostring(BADGE_Y + ability.oy)
\t\t\t.. ") letter='" .. bletter .. "'")
\tend
end""",
"dial dump footers: one per ability")

# --- 20. the INVENTORY sweep learns the new badge id ---
rep("""\t"behaviour_parent", "orders_parent", "army_ability_parent", "ability_parent",
\t"zz_auto_badge",
}""",
"""\t"behaviour_parent", "orders_parent", "army_ability_parent", "ability_parent",
\t"zz_auto_badge", "zz_auto_badge_fs",
}""",
"INVENTORY_FIXED carries the new badge id")

rep("""\t-- Our own badge is special: if the engine's search cannot see a component WE
\t-- created, the handle we already hold is the truth about it.
\tif found["zz_auto_badge"] == nil and badge ~= nil and inv_id_of(badge) == "zz_auto_badge" then
\t\tfound["zz_auto_badge"] = badge
\tend""",
"""\t-- Our own badges are special: if the engine's search cannot see a component
\t-- WE created, the handle we already hold is the truth about it.
\tfor _, ability in ipairs(ABILITIES) do
\t\tlocal state = ability_state[ability.marker]
\t\tif found[ability.badge] == nil and state.badge ~= nil
\t\t\tand inv_id_of(state.badge) == ability.badge then
\t\t\tfound[ability.badge] = state.badge
\t\tend
\tend""",
"inv_resolve falls back to every badge handle")

rep("""\t-- Run whenever our ability button OR any candidate exists; stay silent only
\t-- when there is nothing at all to report on.
\tif our_button == nil and found_count == 0 then return end""",
"""\t-- Run whenever one of our ability buttons OR any candidate exists; stay
\t-- silent only when there is nothing at all to report on.
\tlocal any_button = false
\tfor _, ability in ipairs(ABILITIES) do
\t\tif ability_state[ability.marker].button ~= nil then any_button = true end
\tend
\tif not any_button and found_count == 0 then return end""",
"inventory sweep runs on any of our buttons")

rep("""\tlog(inv_line("zz_auto_badge", found["zz_auto_badge"]))
end""",
"""\tlog(inv_line("zz_auto_badge", found["zz_auto_badge"]))
\tlog(inv_line("zz_auto_badge_fs", found["zz_auto_badge_fs"]))
end""",
"inventory sweep logs both badges")

# --- 21. section 9: phase refresh + the loading banner ---
rep("""local function phase_ui_refresh()
\tfind_ability_buttons()          -- the ability's own icon (section 8b)
\tapply_ability_feedback()        -- keep the icon's pulse in step with the switch
\tlast_seen_tick = tick_count     -- so the watchdog does not read this as a stall
end""",
"""local function phase_ui_refresh()
\tfind_ability_buttons()          -- the abilities' own icons (section 8b)
\tfor _, ability in ipairs(ABILITIES) do
\t\tapply_ability_feedback(ability.marker)  -- keep each badge's letter in step with its switch
\tend
\tlast_seen_tick = tick_count     -- so the watchdog does not read this as a stall
end""",
"phase refresh updates every ability")

rep("""log("loaded. polling every " .. tostring(POLL_MS) .. " ms"
\t.. " | fire on charge = " .. tostring(FIRE_ON_CHARGE)
\t.. " | fire on melee = " .. tostring(FIRE_ON_MELEE)
\t.. " | automatic activation starts " .. (AUTO_ENABLED and "ON" or "OFF")
\t.. " | click the M/A badge to flip it")
for _, wanted_key in ipairs(ABILITY_KEYS) do
\tlog("  accepting ability: " .. wanted_key)
end""",
"""log("loaded. polling every " .. tostring(POLL_MS) .. " ms"
\t.. " | fire on charge = " .. tostring(FIRE_ON_CHARGE)
\t.. " | fire on melee = " .. tostring(FIRE_ON_MELEE)
\t.. " | automatic activation starts " .. auto_states_string()
\t.. " | click an ability's own M/A badge to flip it")
for _, ability in ipairs(ABILITIES) do
\tfor _, wanted_key in ipairs(ability.keys) do
\t\tlog("  accepting ability (" .. ability.marker .. "): " .. wanted_key)
\tend
end""",
"loading banner lists every ability")

# --- 22. ui_tick: create/confirm/letter per ability ---
rep("""\tif badge == nil and our_button ~= nil then pcall(create_badge) end""",
"""\tfor _, ability in ipairs(ABILITIES) do
\t\tlocal state = ability_state[ability.marker]
\t\tif state.badge == nil and state.button ~= nil then pcall(create_badge, ability.marker) end
\tend""",
"ui_tick creates every missing badge")

rep("""\tlocal confirmed = false
\tlocal hide_why = "badge hidden - no ability button found yet"

\tif our_button ~= nil then
\t\tlocal ok_id, id = pcall(function() return our_button:Id() end)
\t\tif not ok_id or type(id) ~= "string" then
\t\t\tour_button = nil        -- dead: no usable button, reason = hide_why's default
\t\telse
\t\t\tlocal ok_k, key = pcall(function() return our_button:InterfaceFunction("AbilityKeyForScript") end)
\t\t\tif ok_k and type(key) == "string" and string.len(key) > 3
\t\t\t\tand string.find(string.lower(key), "onslaught") ~= nil then
\t\t\t\tconfirmed = true
\t\t\telse
\t\t\t\tour_button = nil
\t\t\t\thide_why = "badge hidden - the dial is not showing Deadly Onslaught"
\t\t\tend
\t\tend
\tend

\tif badge ~= nil then
\t\tif confirmed then
\t\t\tif not badge_shown then
\t\t\t\tbadge_shown = true
\t\t\t\tpcall(function() badge:SetVisible(true) end)
\t\t\t\tlog("badge shown - the dial is showing Deadly Onslaught")
\t\t\tend
\t\t\t-- while the dial shows our ability, the letter follows the switch (A = auto, M = manual)
\t\t\tif badge_visible_state ~= AUTO_ENABLED then
\t\t\t\tbadge_visible_state = AUTO_ENABLED
\t\t\t\tpcall(function() badge:SetText(AUTO_ENABLED and "A" or "M") end)
\t\t\t\tlog("   badge letter='" .. (AUTO_ENABLED and "A" or "M") .. "' (auto "
\t\t\t\t\t.. (AUTO_ENABLED and "ON" or "OFF") .. ")")
\t\t\tend
\t\telseif badge_shown then
\t\t\tbadge_shown = false
\t\t\tpcall(function() badge:SetVisible(false) end)
\t\t\tlog(hide_why)
\t\tend
\tend
\tif badge ~= nil then pcall(place_badge) end""",
"""\t-- Per ability: confirm ITS button and show/hide/letter ITS own badge.
\tlocal onslaught_confirmed = false

\tfor _, ability in ipairs(ABILITIES) do
\t\tlocal state = ability_state[ability.marker]
\t\tlocal confirmed = false
\t\tlocal hide_why = "badge [" .. ability.marker .. "] hidden - no ability button found yet"

\t\tif state.button ~= nil then
\t\t\tlocal ok_id, id = pcall(function() return state.button:Id() end)
\t\t\tif not ok_id or type(id) ~= "string" then
\t\t\t\tstate.button = nil        -- dead: no usable button, reason = hide_why's default
\t\t\telse
\t\t\t\tlocal ok_k, key = pcall(function() return state.button:InterfaceFunction("AbilityKeyForScript") end)
\t\t\t\tif ok_k and type(key) == "string" and string.len(key) > 3
\t\t\t\t\tand string.find(string.lower(key), ability.marker, 1, true) ~= nil then
\t\t\t\t\tconfirmed = true
\t\t\t\telse
\t\t\t\t\tstate.button = nil
\t\t\t\t\thide_why = "badge [" .. ability.marker .. "] hidden - the dial is not showing "
\t\t\t\t\t\t.. ability.name
\t\t\t\tend
\t\t\tend
\t\tend

\t\tif ability.marker == "onslaught" then onslaught_confirmed = confirmed end

\t\tif state.badge ~= nil then
\t\t\tif confirmed then
\t\t\t\tif not state.badge_shown then
\t\t\t\t\tstate.badge_shown = true
\t\t\t\t\tpcall(function() state.badge:SetVisible(true) end)
\t\t\t\t\tlog("badge [" .. ability.marker .. "] shown - the dial is showing " .. ability.name)
\t\t\t\tend
\t\t\t\t-- while the dial shows this ability, the letter follows its own switch
\t\t\t\t-- (A = auto, M = manual)
\t\t\t\tif state.badge_visible_state ~= auto_state[ability.marker] then
\t\t\t\t\tstate.badge_visible_state = auto_state[ability.marker]
\t\t\t\t\tpcall(function() state.badge:SetText(auto_state[ability.marker] and "A" or "M") end)
\t\t\t\t\tlog("   badge [" .. ability.marker .. "] letter='"
\t\t\t\t\t\t.. (auto_state[ability.marker] and "A" or "M") .. "' (auto "
\t\t\t\t\t\t.. (auto_state[ability.marker] and "ON" or "OFF") .. ")")
\t\t\t\tend
\t\t\telseif state.badge_shown then
\t\t\t\tstate.badge_shown = false
\t\t\t\tpcall(function() state.badge:SetVisible(false) end)
\t\t\t\tlog(hide_why)
\t\t\tend
\t\tend
\t\tif state.badge ~= nil then pcall(place_badge, ability.marker) end
\tend""",
"ui_tick confirms each ability independently")

rep("""\tif confirmed and (tick_count - last_dial_dump_tick) >= DIAL_DUMP_EVERY_N_POLL_TICKS then""",
"""\tif onslaught_confirmed and (tick_count - last_dial_dump_tick) >= DIAL_DUMP_EVERY_N_POLL_TICKS then""",
"dial dump gated on the onslaught confirmation")

rep("""\tif our_button == nil and (ui_ticks % 2) == 0 then
\t\tfind_ability_buttons()
\tend""",
"""\tif not all_buttons_found() and (ui_ticks % 2) == 0 then
\t\tfind_ability_buttons()
\tend""",
"ui_tick rescans until every button is found")

# --- write + report ---
p.write_text(s, encoding="utf-8", newline="")
for r in report:
    print(r)
print(f"lines: {before_lines} -> {s.count(chr(10)) + 1}")

leftovers = ("our_button", "AUTO_ENABLED", "activated_at_tick", "last_fired_at_tick",
             "ACTIVATION_BRAKE_TICKS", "ABILITY_RECHARGE_SECONDS",
             "MIN_SECONDS_BETWEEN_FIRES", "MIN_TICKS_BETWEEN_FIRES")
bad = {t: s.count(t) for t in leftovers if s.count(t) != 0}
assert not bad, f"leftover removed tokens: {bad}"
assert s.count("ABILITY_KEYS") == s.count("ALL_ABILITY_KEYS"), "a bare ABILITY_KEYS reference remains"
print("removed-token check clean; ALL_ABILITY_KEYS:", s.count("ALL_ABILITY_KEYS"))
print("GUARD_SECONDS:", s.count("GUARD_SECONDS"), "| check_readiness:", s.count("check_readiness"),
      "| is_moving_fast:", s.count("is_moving_fast"), "| zz_auto_badge_fs:", s.count("zz_auto_badge_fs"))
