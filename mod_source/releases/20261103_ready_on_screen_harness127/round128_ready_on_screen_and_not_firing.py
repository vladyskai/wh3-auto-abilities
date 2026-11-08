#!/usr/bin/env python3
"""Round 128 (harness 127): fix A for silently dropped multi-use casts, and the
read-only NOT FIRING snapshot.

(A) User ruling 2026-11-03: "You can implement only A, and we can implement that in
    general." Field case: Isha's Rain's third cast was ACCEPTED but never executed;
    can_perform_special_ability stays true for a multi-use ability, so the mod held its
    full 120 s while the ability sat ready. Now, for EVERY ability under a charge hold:
    when the caster is the SELECTED unit, at least wind-up + 3 s after the cast, and the
    ability's own button reads 'active' or 'hover' (the game shows it READY), the cast
    did not take - the hold is released and the trigger may cast on this same poll.
    Logged once per release. Units that are not selected keep the plain hold (the
    button exists only for the selected unit).

(B) User question 2026-11-03: why do units pause for 40 to 154 s? A READ-ONLY snapshot
    per ranged unit that is not firing, every 4 polls (1 s), logged only when its
    reasons change: the target (none / in range / out of range, in melee, hidden),
    and the unit itself (in melee, moving, idle, fire-at-will, skirmish, wavering,
    routing, limbered artillery, out of ammunition). Line of sight cannot be read.
    Live file only (pure logging; the annotated copy has no counterpart).
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

A_HELPER_ANCHOR = "function FOURTH.try_pair(script_unit, unit, ability, ui_id, ability_key, reason, gone_ids)\n"
A_HELPER = """-- ============================================================================
-- ROUND 128 - A DROPPED MULTI-USE CAST, SEEN ON SCREEN (user ruling 2026-11-03:
-- "implement only A ... in general"). The engine can ACCEPT a cast of a
-- multi-use ability and never execute it (Isha's Rain, field battle 2026-11-03:
-- the third cast left the button READY 32 s later). can_perform_special_ability
-- stays true for such an ability, so the charge hold below cannot tell. The one
-- honest signal is the ability's own button - and it exists only for the
-- SELECTED unit. So: while a charge hold runs, if this unit is the ONLY unit the
-- engine reports selected,
-- at least the wind-up + CHARGE_RELEASE_SETTLE_S after the cast, and the button
-- reads 'active' or 'hover' (ready), the cast did not take: release the hold.
-- Returns ready (bool), the state read, and the seconds since the cast.
-- ============================================================================
FOURTH.CHARGE_RELEASE_SETTLE_S = 3   -- seconds after the wind-up before a READY button is believed
function FOURTH.charge_hold_ready_on_screen(ui_id, ability, held_until)
	-- the ENGINE's live selection (not the tracker, which keeps the last unit when
	-- nothing is selected): exactly one unit selected, and it is this one
	if #selected_ui_ids ~= 1 or tostring(selected_ui_ids[1]) ~= tostring(ui_id) then return false end
	if ability.charge_s == nil or held_until == nil then return false end
	local cast_tick = held_until - math.floor((ability.charge_s * 1000) / POLL_MS)
	local since_s = (tick_count - cast_tick) * POLL_MS / 1000
	if since_s < (ability.wind_up_s or 0) + FOURTH.CHARGE_RELEASE_SETTLE_S then return false end
	local st = ability_state[ability.marker]
	if st == nil or st.button == nil then return false end
	local ok, s = pcall(function() return st.button:CurrentState() end)
	if not ok or type(s) ~= "string" then return false end
	return (s == "active" or s == "hover"), s, since_s
end

"""

A_HOLD_OLD = """				local held_until = (cu ~= nil and cu[ability.marker]) or nil
				if held_until ~= nil and tick_count < held_until then
					eligible = false
					quiet = true
				end
"""
A_HOLD_NEW_SRC = """				local held_until = (cu ~= nil and cu[ability.marker]) or nil
				if held_until ~= nil and tick_count < held_until then
					-- ROUND 128: the selected unit's button says READY -> the
					-- last cast did not take; release the hold (fix A).
					local ready, seen, since_s = FOURTH.charge_hold_ready_on_screen(ui_id, ability, held_until)
					if ready then
						cu[ability.marker] = nil
						log(string.format("  charge gate %s: unit %s is selected and its button reads '%s' (READY) %.2fs after the last cast - that cast did not take; the hold is released",
							ability.marker, tostring(ui_id), tostring(seen), since_s))
					else
						eligible = false
						quiet = true
					end
				end
"""
A_HOLD_NEW_ANN = """				local held_until = (cu ~= nil and cu[ability.marker]) or nil
				if held_until ~= nil and tick_count < held_until then
					-- ROUND 128: the selected unit's button says READY -> the
					-- last cast did not take; release the hold (fix A).
					if FOURTH.charge_hold_ready_on_screen(ui_id, ability, held_until) then
						cu[ability.marker] = nil
					else
						eligible = false
						quiet = true
					end
				end
"""

B_FN_ANCHOR = "function FOURTH.ammo_probe(units)\n"
B_FN = """-- ============================================================================
-- ROUND 128 - THE NOT FIRING SNAPSHOT (READ-ONLY; user question 2026-11-03: why
-- do units pause?). For a ranged unit that is NOT firing, every
-- NOT_FIRING_EVERY_N_POLLS polls, the readable reasons it may be holding fire,
-- logged ONLY when they change (st.why is the last one logged): its target
-- (none, in or out of its own live missile range, in melee, hidden) and the unit
-- itself (in melee, moving, idle, fire-at-will, skirmish, wavering, routing,
-- limbered artillery, out of ammunition). Line of sight has NO read in the API:
-- a pause with every reason here clear points there. '?' = the read is
-- unavailable. Nothing is decided from it.
-- ============================================================================
FOURTH.NOT_FIRING_EVERY_N_POLLS = 4   -- 4 x 250 ms = once a second
function FOURTH.not_firing_snapshot(u, st, now_s, inr, d, r)
	local function b(fn)
		local ok, v = pcall(fn)
		if ok and type(v) == "boolean" then return v and "yes" or "no" end
		return "?"
	end
	local tgt = "none"
	local ok_t, t = pcall(function() return u:current_target() end)
	local t_melee, t_hidden = "-", "-"
	if ok_t and t ~= nil then
		tgt = "?"
		pcall(function() tgt = tostring(t:type()) end)
		t_melee = b(function() return t:is_in_melee() end)
		t_hidden = b(function() return t:is_hidden() end)
	end
	local range_txt = "-"
	if inr == true then range_txt = "in range" elseif inr == false and tgt ~= "none" then range_txt = "OUT of range" end
	local ammo_txt = "?"
	if st.last ~= nil then ammo_txt = (st.last <= 0) and "OUT" or "ok" end
	local key = "target=" .. tgt .. " (" .. range_txt .. ") target_in_melee=" .. t_melee .. " target_hidden=" .. t_hidden
		.. " | self: melee=" .. b(function() return u:is_in_melee() end)
		.. " moving=" .. b(function() return u:is_moving() end)
		.. " idle=" .. b(function() return u:is_idle() end)
		.. " fire_at_will=" .. b(function() return u:is_behaviour_active("fire_at_will") end)
		.. " skirmish=" .. b(function() return u:is_behaviour_active("skirmish") end)
		.. " wavering=" .. b(function() return u:is_wavering() end)
		.. " routing=" .. b(function() return u:is_routing() end)
		.. " limbered=" .. b(function() return u:is_limbered_artillery() end)
		.. " ammo=" .. ammo_txt
	if key == st.why then return end
	st.why = key
	local who = FOURTH.ammo_describe(u)
	local dist_txt = ""
	if d ~= nil and r ~= nil then dist_txt = string.format(" [distance %.1fm, range %.1fm]", d, r) end
	log(string.format("NOT FIRING %s at t=%.2fs: %s%s", who, now_s, key, dist_txt))
end

"""
B_CALL_OLD = "				local ok_a, now = pcall(function() return u:ammo_left() end)\n"
B_CALL_NEW = """				-- ROUND 128: the read-only NOT FIRING snapshot (live file only)
				if not st.firing and (tick_count % FOURTH.NOT_FIRING_EVERY_N_POLLS) == 0 then
					FOURTH.not_firing_snapshot(u, st, now_s, inr, d, r)
				end
				local ok_a, now = pcall(function() return u:ammo_left() end)
"""
B_ON_OLD = "							st.cast_point_passed = false\n"
B_ON_NEW = "							st.cast_point_passed = false\n							st.why = nil   -- ROUND 128: the next pause is logged fresh\n"

PLAN = {
    SRC: [(A_HELPER_ANCHOR, A_HELPER + A_HELPER_ANCHOR), (A_HOLD_OLD, A_HOLD_NEW_SRC),
          (B_FN_ANCHOR, B_FN + B_FN_ANCHOR), (B_CALL_OLD, B_CALL_NEW), (B_ON_OLD, B_ON_NEW)],
    ANN: [(A_HELPER_ANCHOR, A_HELPER + A_HELPER_ANCHOR), (A_HOLD_OLD, A_HOLD_NEW_ANN)],
}
for path, edits in PLAN.items():
    s = open(path, encoding="utf-8", newline="").read()
    assert "\r\n" not in s and "charge_hold_ready_on_screen" not in s, path
    for i, (a, b) in enumerate(edits, 1):
        n = s.count(a)
        assert n == 1, (path.split("\\")[-1], "edit", i, "anchor count", n)
        s = s.replace(a, b, 1)
    assert "\u2014" not in "".join(b for _, b in edits)
    if path == ANN:
        assert "log(" not in A_HELPER + A_HOLD_NEW_ANN
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("applied %d edits:" % len(edits), path.split("\\")[-1])
