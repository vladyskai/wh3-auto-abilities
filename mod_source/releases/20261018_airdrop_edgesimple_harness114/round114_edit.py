#!/usr/bin/env python3
"""Round 114 edit: replace the air-drop evaluator with the simple edge-gap rule,
extract the per-pair gate+cast into FOURTH.try_pair, add the 0.2 s fast pass.

Applied to BOTH copies (live + annotated) with exact occurrence assertions.
Binary read/write so the shipped file stays LF.
"""
import io, sys, re
import lupa.lua55 as lua
LU = lua.LuaRuntime(unpack_returned_tuples=True)
LOAD = LU.eval('function(src) local f, e = load(src); return (f ~= nil), e end')

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
LIVE = ROOT + r"\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN  = ROOT + r"\docs\WH3_auto_ability_annotated.lua"
REL  = ROOT + r"\mod_source\releases\20261018_airdrop_edgesimple_harness114"


def rd(p):
    with open(p, "rb") as f:
        b = f.read()
    assert b.count(b"\r") == 0, "CR found in " + p
    return b.decode("utf-8")


def wr(p, s):
    with open(p, "wb") as f:
        f.write(s.encode("utf-8"))
    with open(p, "rb") as f:
        assert f.read().count(b"\r") == 0, "CR after write in " + p


def one(seq, what):
    assert len(seq) == 1, "anchor %s matched %d times" % (what, len(seq))
    return seq[0]


def idx(lines, text, what, start=0):
    return one([i for i in range(start, len(lines)) if lines[i] == text], what)


def splice(lines, a, b, new):
    """replace lines[a:b] (exclusive b) with new (list of str, no trailing NL)"""
    return lines[:a] + new + lines[b:]


PRECAST = """	-- THE AIR-DROP RE-CHECK (round 114). Immediately before the call the CASTER
	-- must still be ALIVE, still AIRBORNE where its row is air-only and still OUT
	-- of melee where the engine forbids it; the CHOSEN ENEMY must still be alive
	-- with MORE THAN AIR_DROP_MIN_MEN models, and the EDGE gap must still be under
	-- AIR_DROP_EDGE_M. The enemy reads and the distance are RE-TAKEN here from
	-- FRESH handles - the same number_of_men_alive() read and the SAME
	-- unit_distance primitive the picker used, so the two readings cannot
	-- disagree - and a lapsed condition SKIPS the cast rather than spending it.
	-- Every number that decided it is written, with `-> SKIPPED at re-check`.
	if FOURTH.ad_enemy ~= nil then
		local enemy = FOURTH.ad_enemy
		local ad_marker_now = FOURTH.ad_marker or "air_drop"
		local ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)
		local caster_alive = (ok_alive and type(alive) == "number" and alive > 0)
		local fly_now, fly_readable = true, true
		if FOURTH.ad_air_only then
			local ok_fly, v = pcall(function() return unit:is_currently_flying() end)
			fly_readable = ok_fly
			fly_now = (ok_fly and v == true)
		end
		local melee_now, melee_readable = false, true
		if FOURTH.ad_no_melee then
			local ok_m, m = pcall(function() return unit:is_in_melee() end)
			melee_readable = ok_m
			melee_now = (ok_m and m == true)
		end
		local ok_ea, ea = pcall(function() return enemy:number_of_men_alive() end)
		local enemy_alive = (ok_ea and type(ea) == "number" and ea > 0)
		local men_ok = (ok_ea and type(ea) == "number" and ea > FOURTH.AIR_DROP_MIN_MEN)
		local edge_now = FOURTH.eg_enemy_gap(unit, enemy)
		local edge_ok = (edge_now ~= nil and edge_now < FOURTH.AIR_DROP_EDGE_M)
		local edge_text = ((edge_now ~= nil) and (string.format("%.2f", edge_now) .. "m") or "?")
		local men_text = ((ok_ea and type(ea) == "number") and tostring(ea) or "?")
		if not (caster_alive and fly_readable and fly_now and melee_readable
			and (not melee_now) and enemy_alive and men_ok and edge_ok) then
			log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " nearest valid:'"
				.. (FOURTH.type_plain(enemy) or "enemy") .. "' entities=" .. men_text
				.. " edge=" .. edge_text .. " (need < "
				.. string.format("%.2f", FOURTH.AIR_DROP_EDGE_M) .. "m) -> SKIPPED at re-check"
				.. " (caster_alive=" .. tostring(caster_alive) .. " flying=" .. tostring(fly_now)
				.. " melee=" .. tostring(melee_now) .. " enemy_alive=" .. tostring(enemy_alive)
				.. " over_min_men=" .. tostring(men_ok) .. " edge_ok=" .. tostring(edge_ok)
				.. " min_men=" .. tostring(FOURTH.AIR_DROP_MIN_MEN) .. ") - cast not spent")
			FOURTH.ad_enemy = nil
			if RELEASE_CONTROL_AFTER and took_control then
				local ok_release, err_release = pcall(function() uc:release_control() end)
				log("  release_control         : ok=" .. tostring(ok_release)
					.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
			end
			return "held"
		end
		log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " nearest valid:'"
			.. (FOURTH.type_plain(enemy) or "enemy") .. "' entities=" .. men_text
			.. " edge=" .. edge_text .. " (need < "
			.. string.format("%.2f", FOURTH.AIR_DROP_EDGE_M) .. "m) -> FIRING (re-checked)")
	end""".split("\n")

PRECAST_ANN = """	-- THE AIR-DROP RE-CHECK (round 114). Immediately before the call the CASTER
	-- must still be ALIVE, still AIRBORNE where its row is air-only and still OUT
	-- of melee where the engine forbids it; the CHOSEN ENEMY must still be alive
	-- with MORE THAN AIR_DROP_MIN_MEN models, and the EDGE gap must still be under
	-- AIR_DROP_EDGE_M. The enemy reads and the distance are RE-TAKEN here from
	-- FRESH handles - the same number_of_men_alive() read and the SAME
	-- unit_distance primitive the picker used, so the two readings cannot
	-- disagree - and a lapsed condition SKIPS the cast rather than spending it.
	if FOURTH.ad_enemy ~= nil then
		local enemy = FOURTH.ad_enemy
		local ad_marker_now = FOURTH.ad_marker or "air_drop"
		local ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)
		local caster_alive = (ok_alive and type(alive) == "number" and alive > 0)
		local fly_now, fly_readable = true, true
		if FOURTH.ad_air_only then
			local ok_fly, v = pcall(function() return unit:is_currently_flying() end)
			fly_readable = ok_fly
			fly_now = (ok_fly and v == true)
		end
		local melee_now, melee_readable = false, true
		if FOURTH.ad_no_melee then
			local ok_m, m = pcall(function() return unit:is_in_melee() end)
			melee_readable = ok_m
			melee_now = (ok_m and m == true)
		end
		local ok_ea, ea = pcall(function() return enemy:number_of_men_alive() end)
		local enemy_alive = (ok_ea and type(ea) == "number" and ea > 0)
		local men_ok = (ok_ea and type(ea) == "number" and ea > FOURTH.AIR_DROP_MIN_MEN)
		local edge_now = FOURTH.eg_enemy_gap(unit, enemy)
		local edge_ok = (edge_now ~= nil and edge_now < FOURTH.AIR_DROP_EDGE_M)
		local edge_text = ((edge_now ~= nil) and (string.format("%.2f", edge_now) .. "m") or "?")
		local men_text = ((ok_ea and type(ea) == "number") and tostring(ea) or "?")
		if not (caster_alive and fly_readable and fly_now and melee_readable
			and (not melee_now) and enemy_alive and men_ok and edge_ok) then
			-- (annotated copy: the SKIPPED-at-re-check line is a log-only line - it
			-- prints the enemy type, entities=<n>, edge=<m>, the 0.10 m line and
			-- which of caster_alive / flying / melee / enemy_alive / over_min_men /
			-- edge_ok lapsed)
			FOURTH.ad_enemy = nil
			if RELEASE_CONTROL_AFTER and took_control then
				local ok_release, err_release = pcall(function() uc:release_control() end)
			end
			return "held"
		end
		-- (annotated copy: the FIRING (re-checked) line is a log-only line with the
		-- same four fields, re-measured on fresh handles)
	end"""

CALLER = """					if reason ~= nil then
						-- ROUND 114: the readiness read, every hold/gate and the cast
						-- itself now live in ONE function (FOURTH.try_pair), because
						-- the air-drop fast pass has to cast through the SAME gates
						-- rather than a copy of them. It answers "gone" when the unit
						-- must be dropped after this tick's walk.
						if FOURTH.try_pair(script_unit, unit, ability, ui_id, ability_key,
							reason, gone_ids) == "gone" then
							break
						end
					end""".split("\n")

CALLER_ANN = """					if want_fire then
						-- ROUND 114: the readiness read, every hold/gate and the cast
						-- itself live in ONE function (FOURTH.try_pair) so the
						-- air-drop fast pass casts through the SAME gates. It answers
						-- "gone" when the unit must be dropped after this tick's walk.
						if FOURTH.try_pair(script_unit, unit, ability, ui_id,
							target_key_by_unit[ui_id], want_fire, gone_ids) == "gone" then
							break
						end
					end""".split("\n")

FASTPASS = """-- ============================================================================
-- THE AIR-DROP FAST PASS (round 114) - a SECOND timer, and the only thing it
-- schedules.
--
-- THE USER'S RULING (verbatim): "I want the trigger to be checked much more
-- frequently when armed and less than 30 meters from a valid enemy unit."
--
-- WHAT IT RUNS: FOURTH.ad_pick - THE SAME EVALUATOR the poll runs (one copy of
-- the rule, not a second implementation) - and it casts through
-- FOURTH.try_pair, THE SAME readiness + gate + cast sequence the poll uses. The
-- air-drop rule is therefore identical whichever timer reaches it.
--
-- WHEN IT RUNS: only in the conflict phase, only when the watch list exists,
-- only for ALIVE units the player has ARMED for one of the air-drop markers
-- (FOURTH.ad_fast_abilities, the 12 entries built at load), and only while a
-- VALID enemy (alive, more than AIR_DROP_MIN_MEN models, readable unit_distance)
-- is inside AIR_DROP_NEAR_M = 30 m. Outside 30 m it does nothing but note the
-- transition.
--
-- ISOLATION: it never touches tick_count, the re-list, the heartbeat, the
-- identity watch, the active set or any NON-air-drop ability - the loop is over
-- FOURTH.ad_fast_abilities, never over ABILITIES. The global poll's interval and
-- every other ability's cadence are unchanged.
--
-- NO DOUBLE CAST: the guard, charge, in-flight and per-unit serialisation holds
-- are stamped in POLL ticks by the shared FOURTH.try_pair, and the guard is
-- written BEFORE the call. A second fast tick inside the same poll window finds
-- (tick_count - last_attempt) = 0, which is below GUARD_TICKS, so the pair is not
-- eligible - the fast pass can only ever advance a cast by less than one guard.
-- Harness 114 proves it with two consecutive fast ticks (one cast) and with a
-- fast tick immediately after a poll cast (still one).
function FOURTH.ad_fast_pass()
	if tracked_units == nil then return end
	if not bm:is_conflict_phase() then return end
	local list = FOURTH.ad_fast_abilities
	if list == nil or #list == 0 then return end
	local gone = {}
	for i = 1, #tracked_units do
		local script_unit = tracked_units[i]
		local unit = script_unit and script_unit.unit
		if unit ~= nil then
			local ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)
			if ok_alive and type(alive) == "number" and alive > 0 then
				local ok_id, uid = pcall(function() return unit:unique_ui_id() end)
				if ok_id and uid ~= nil then
					for j = 1, #list do
						local ability = list[j]
						if is_armed(unit, ability.marker) then
							-- THE SAME CANDIDATE SCAN the evaluator uses, once, for
							-- the 30 m gate: the fast pass must not decide anything
							-- about WHO is valid on its own.
							local enemy, dist = FOURTH.ad_nearest(unit)
							local near = (enemy ~= nil and dist ~= nil
								and dist < FOURTH.AIR_DROP_NEAR_M)
							local was = (FOURTH.ad_fast_on[uid] == true)
							if near ~= was then
								FOURTH.ad_fast_on[uid] = near
								if near then
									log("  " .. FOURTH.ad_tag(unit) .. "fast poll: ON (nearest valid "
										.. string.format("%.1f", dist) .. "m)")
								else
									log("  " .. FOURTH.ad_tag(unit) .. "fast poll: OFF")
								end
							end
							if near then
								-- THE CURRENT ENTRY'S OWN SLOTS, exactly as the poll
								-- sets them before its evaluate call.
								FOURTH.ad_marker = ability.marker
								FOURTH.ad_air_only = (ability.air_only == true)
								FOURTH.ad_no_melee = (ability.no_melee == true)
								FOURTH.ad_range_m = ability.range_m
								FOURTH.ad_enemy = nil
								FOURTH.ad_caster_su = nil
								local routing = unit_is_routing(unit)
								local reason = ability.evaluate(unit, routing)
								if reason ~= nil then
									local ability_key = target_key_by_unit[uid]
									if FOURTH.try_pair(script_unit, unit, ability, uid,
										ability_key, reason, gone) == "gone" then
										break
									end
								end
							end
						end
					end
				end
			end
		end
	end
	for g = 1, #gone do
		drop_unit_by_ui_id(gone[g])
	end
end

bm:repeat_callback(poll, POLL_MS, POLL_NAME)

-- THE FAST PASS'S OWN REGISTRATION (round 114). A second model timer at
-- AIR_DROP_FAST_S (0.2 s = 200 ms), wrapped in its own pcall exactly like the
-- poll: an error escaping a timer callback aborts the battle model's timer
-- driver and would kill EVERY repeating callback, so it is caught and counted.
-- The global poll above keeps POLL_MS and its own name - nothing about it moves.
FOURTH.ad_fast_errors = 0
bm:repeat_callback(function()
	local ok, err = pcall(FOURTH.ad_fast_pass)
	if not ok then
		FOURTH.ad_fast_errors = FOURTH.ad_fast_errors + 1
		if FOURTH.ad_fast_errors <= 3 or (FOURTH.ad_fast_errors % 40) == 0 then
			log("AIR-DROP FAST ERROR #" .. tostring(FOURTH.ad_fast_errors)
				.. " (the fast pass stops, the poll is untouched): " .. tostring(err))
		end
	end
end, math.floor(FOURTH.AIR_DROP_FAST_S * 1000), "zz_test_deadly_onslaught_air_drop_fast")""".split("\n")

FASTPASS_ANN = """-- ============================================================================
-- THE AIR-DROP FAST PASS (round 114) - a SECOND timer, and the only thing it
-- schedules.
--
-- THE USER'S RULING (verbatim): "I want the trigger to be checked much more
-- frequently when armed and less than 30 meters from a valid enemy unit."
--
-- WHAT IT RUNS: FOURTH.ad_pick - THE SAME EVALUATOR the poll runs (one copy of
-- the rule, not a second implementation) - and it casts through
-- FOURTH.try_pair, THE SAME readiness + gate + cast sequence the poll uses. The
-- air-drop rule is therefore identical whichever timer reaches it.
--
-- WHEN IT RUNS: only in the conflict phase, only when the watch list exists,
-- only for ALIVE units the player has ARMED for one of the air-drop markers
-- (FOURTH.ad_fast_abilities, the 12 entries built at load), and only while a
-- VALID enemy (alive, more than AIR_DROP_MIN_MEN models, readable unit_distance)
-- is inside AIR_DROP_NEAR_M = 30 m. Outside 30 m it does nothing but note the
-- transition.
--
-- ISOLATION: it never touches tick_count, the re-list, the heartbeat, the
-- identity watch, the active set or any NON-air-drop ability - the loop is over
-- FOURTH.ad_fast_abilities, never over ABILITIES. The global poll's interval and
-- every other ability's cadence are unchanged.
--
-- NO DOUBLE CAST: the guard, charge, in-flight and per-unit serialisation holds
-- are stamped in POLL ticks by the shared FOURTH.try_pair, and the guard is
-- written BEFORE the call. A second fast tick inside the same poll window finds
-- (tick_count - last_attempt) = 0, which is below GUARD_TICKS, so the pair is not
-- eligible - the fast pass can only ever advance a cast by less than one guard.
-- Harness 114 proves it with two consecutive fast ticks (one cast) and with a
-- fast tick immediately after a poll cast (still one).
function FOURTH.ad_fast_pass()
	if tracked_units == nil then return end
	if not bm:is_conflict_phase() then return end
	local list = FOURTH.ad_fast_abilities
	if list == nil or #list == 0 then return end
	local gone = {}
	for i = 1, #tracked_units do
		local script_unit = tracked_units[i]
		local unit = script_unit and script_unit.unit
		if unit ~= nil then
			local ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)
			if ok_alive and type(alive) == "number" and alive > 0 then
				local ok_id, uid = pcall(function() return unit:unique_ui_id() end)
				if ok_id and uid ~= nil then
					for j = 1, #list do
						local ability = list[j]
						if is_armed(unit, ability.marker) then
							-- THE SAME CANDIDATE SCAN the evaluator uses, once, for
							-- the 30 m gate: the fast pass must not decide anything
							-- about WHO is valid on its own.
							local enemy, dist = FOURTH.ad_nearest(unit)
							local near = (enemy ~= nil and dist ~= nil
								and dist < FOURTH.AIR_DROP_NEAR_M)
							local was = (FOURTH.ad_fast_on[uid] == true)
							if near ~= was then
								FOURTH.ad_fast_on[uid] = near
								if near then
									-- (annotated copy: the ON line is a log-only line -
									-- "fast poll: ON (nearest valid <d>m)", once per change)
								else
									-- (annotated copy: the OFF line is a log-only line,
									-- written once per change)
								end
							end
							if near then
								-- THE CURRENT ENTRY'S OWN SLOTS, exactly as the poll
								-- sets them before its evaluate call.
								FOURTH.ad_marker = ability.marker
								FOURTH.ad_air_only = (ability.air_only == true)
								FOURTH.ad_no_melee = (ability.no_melee == true)
								FOURTH.ad_range_m = ability.range_m
								FOURTH.ad_enemy = nil
								FOURTH.ad_caster_su = nil
								local routing = unit_is_routing(unit)
								local reason = ability.evaluate(unit, routing)
								if reason ~= nil then
									local ability_key = target_key_by_unit[uid]
									if FOURTH.try_pair(script_unit, unit, ability, uid,
										ability_key, reason, gone) == "gone" then
										break
									end
								end
							end
						end
					end
				end
			end
		end
	end
	for g = 1, #gone do
		drop_unit_by_ui_id(gone[g])
	end
end

bm:repeat_callback(poll, POLL_MS, POLL_NAME)

-- THE FAST PASS'S OWN REGISTRATION (round 114). A second model timer at
-- AIR_DROP_FAST_S (0.2 s = 200 ms), wrapped in its own pcall exactly like the
-- poll: an error escaping a timer callback aborts the battle model's timer
-- driver and would kill EVERY repeating callback, so it is caught and counted.
-- The global poll above keeps POLL_MS and its own name - nothing about it moves.
FOURTH.ad_fast_errors = 0
bm:repeat_callback(function()
	local ok, err = pcall(FOURTH.ad_fast_pass)
	if not ok then
		FOURTH.ad_fast_errors = FOURTH.ad_fast_errors + 1
	end
end, math.floor(FOURTH.AIR_DROP_FAST_S * 1000), "zz_test_deadly_onslaught_air_drop_fast")""".split("\n")

RANGEBLOCK = """	-- ROUND 114: the air-drop family is bounded by its OWN rule, not by the 70%
	-- table. The rule is ONE comparison - the nearest valid enemy's edge-to-edge
	-- unit_distance against FOURTH.AIR_DROP_EDGE_M - so the entry's range_m is
	-- carried for the inventory/diagnostics only and set to that same line; the
	-- evaluator never reads it. The 70% map would otherwise stamp the row's 10 m
	-- range onto it as 7 m, which is not the test any more.
	if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then
		ability.range_m = FOURTH.AIR_DROP_EDGE_M
		FOURTH.ad_fast_abilities[#FOURTH.ad_fast_abilities + 1] = ability
	end""".split("\n")


def edit(path, ann):
    lines = rd(path).split("\n")
    n0 = len(lines)

    # ---- 1. THE EVALUATOR BLOCK -------------------------------------------
    a = idx(lines, '-- ROUND 107 - THE "ON TOP OF" FAMILY: ONE new evaluator, air_drop_on_infantry.',
            "airdrop family header") - 1
    assert lines[a].startswith("-- ======"), lines[a]
    b = idx(lines, "function FOURTH.evaluate_air_drop_on_infantry(unit, routing)", "evaluator")
    assert lines[b + 1].strip() == "return FOURTH.ad_pick(unit, routing)"
    assert lines[b + 2] == "end"
    new = rd(REL + (r"\block_ann.lua" if ann else r"\block_live.lua")).split("\n")
    while new and new[-1] == "":
        new.pop()
    lines = splice(lines, a, b + 3, new)
    assert "function FOURTH.ad_pick(unit, routing)" in lines
    assert sum(1 for l in lines if l == "function FOURTH.ad_tag(unit)") == 1

    # ---- 2. THE PRE-CAST RE-CHECK -----------------------------------------
    a = idx(lines, "\t-- THE AIR-DROP RE-CHECK (round 110). Immediately before the call the CASTER",
            "precast header")
    if ann:
        b = idx(lines, "\t\t\t-- (annotated copy: the re-check line is a log-only line)",
                "precast tail (ann)", a)
        assert lines[b + 1] == "\tend", repr(lines[b + 1])
        _pa = PRECAST_ANN.split("\n")
        while _pa and _pa[-1] == "":
            _pa.pop()
        lines = splice(lines, a, b + 2, _pa)
    else:
        b = idx(lines, "\t\t\t.. \" bound=\" .. tostring(ad_bound_now) .. \"m) - firing\")",
                "precast tail", a)
        assert lines[b + 1] == "\tend", repr(lines[b + 1])
        lines = splice(lines, a, b + 2, PRECAST)

    # ---- 3. EXTRACT THE GATE + CAST SEQUENCE -------------------------------
    hdr = "\t\t\t\t\tif want_fire then" if ann else "\t\t\t\t\tif reason ~= nil then"
    a = idx(lines, hdr, "gate block header")
    # the block closes on the 5-tab `end` that is followed by the four closing
    # ends of the unit walk; that run is unique AFTER the header
    seq = ["\t\t\t\t\tend", "\t\t\t\tend", "\t\t\tend", "\t\tend", "\tend"]
    hits = [i for i in range(a, min(a + 400, len(lines) - 5)) if lines[i:i + 5] == seq]
    assert hits, "gate block tail not found"

    def dedent(body):
        out = []
        for l in body:
            if l.strip() == "break":
                out.append(l[5:].replace("break", 'return "gone"'))
            elif l.startswith("\t\t\t\t\t"):
                out.append(l[4:])
            else:
                out.append(l)
        return out

    def compiles(body):
        txt = "function FOURTH.try_pair(script_unit, unit, ability, ui_id, ability_key, reason, gone_ids)\n" \
              + "\n".join(dedent(body)) + "\n\treturn nil\nend\n"
        ok, err = LOAD(txt)
        return ok is True

    # the SHORTEST candidate that is a syntactically complete function body
    b = None
    for h in hits:
        if compiles(lines[a + 1:h]):
            b = h
            break
    assert b is not None, "no balanced end for the gate block: " + str(LOAD(
        "function FOURTH.try_pair(a,b,c,d,e,f,g)\n" + "\n".join(dedent(lines[a + 1:hits[0]]))
        + "\n\treturn nil\nend\n")[1])
    assert lines[b] == "\t\t\t\t\tend", repr(lines[b])
    h = b
    body = lines[a + 1:h]
    b = h + 1          # the caller text carries its own closing `end`
    assert sum(1 for l in body if l.strip() == "break") == 1, "unexpected break count"
    assert all(l.startswith("\t\t\t\t\t") or l == "" for l in body if l.strip()), "indent"
    ded = []
    for l in body:
        if l.strip() == "break":
            ded.append(l[len("\t\t\t\t\t"):].replace("break", 'return "gone"'))
        elif l.startswith("\t\t\t\t\t"):
            ded.append(l[4:])
        else:
            ded.append(l)
    fn = ["-- ROUND 114: ONE COPY of the readiness read + every gate + the cast, shared by",
          "-- the poll and the air-drop fast pass. It answers \"gone\" when the unit has",
          "-- to be dropped after this tick's walk, nil otherwise. Nothing in it changed",
          "-- in round 114 - it was MOVED here verbatim so the fast pass could not fork it.",
          "function FOURTH.try_pair(script_unit, unit, ability, ui_id, ability_key, reason, gone_ids)"]
    fn += ded
    fn += ["\treturn nil", "end", "", ""]
    lines = splice(lines, a, b, CALLER_ANN if ann else CALLER)

    # ---- 4. THE TIP SENTENCE ----------------------------------------------
    old_tip = '\tair_drop_on_infantry = "When armed, fires when this unit is over an infantry unit in range, airborne where the ability requires it",'
    new_tip = '\tair_drop_on_infantry = "When armed, fires when the nearest enemy unit with more than 10 models is within 0.1 m of this unit\'s edge, airborne where the ability requires it",'
    i = idx(lines, old_tip, "tip")
    lines[i] = new_tip
    if ann:
        old_tip2 = '\tair_drop_on_infantry = "When armed, fires when this unit is over an infantry unit in range, airborne where the ability requires it",'
        assert new_tip in lines

    # ---- 5. THE RANGE MAP EXEMPTION ---------------------------------------
    a = idx(lines, "\t-- ROUND 108 (item 1): THE AIR-DROP FAMILY IS NOT BOUNDED BY THE 70%",
            "range comment")
    b = idx(lines, "\t\tability.range_m = FOURTH.AIR_DROP_CENTER_M", "range assign", a)
    assert lines[b + 1] == "\tend", repr(lines[b + 1])
    lines = splice(lines, a, b + 2, RANGEBLOCK)

    # ---- 6. THE FAST PASS + ITS REGISTRATION ------------------------------
    a = idx(lines, "bm:repeat_callback(poll, POLL_MS, POLL_NAME)", "poll registration")
    lines = splice(lines, a, a + 1, FASTPASS_ANN if ann else FASTPASS)

    # ---- 7b. THE FAMILY COMMENT IN THE ABILITIES TABLE ---------------------
    a = idx(lines, '\t-- ROUND 107 (item 3): THE "ON TOP OF" FAMILY - 12 entries / 19 keys on',
            "family comment")
    b = idx(lines, '\t{ marker = "death_from_above", name = "Death from Above", trigger = "air_drop_on_infantry",',
            "first air-drop entry", a)
    assert lines[b - 2] == "\t-- ======================================================================", repr(lines[b - 2])
    assert lines[b - 1] == "", repr(lines[b - 1])
    fam = """	-- ======================================================================
	-- ROUND 107 (item 3), REWRITTEN IN ROUND 114: THE "ON TOP OF" FAMILY -
	-- 12 entries / 19 keys on the trigger air_drop_on_infantry.
	--
	-- Every one of these rows has NO target flags at all (friends / enemies /
	-- ground / self all false), effect_range 0, target_intercept_range 10 and
	-- ai_usage always_use_only_land: the engine drops the ordnance where the
	-- CASTER is, so the mod's only decision is WHEN.
	--
	-- THE RULE (round 114, the user's ruling): fire the moment the NEAREST
	-- VALID enemy's EDGE-TO-EDGE distance - battle_unit:unit_distance - is
	-- below FOURTH.AIR_DROP_EDGE_M = 0.1 m, where a valid enemy is one that is
	-- alive with MORE THAN FOURTH.AIR_DROP_MIN_MEN = 10 models, and while the
	-- caster satisfies the usage restrictions its own row declares:
	--   air_only = the row says the engine refuses it while `grounded`,
	--              OR every carrier of the key carries `flying`;
	--   no_melee = the row says the engine refuses it while `engaged_in_melee`.
	-- Two entries are deliberately NOT air-gated and say so on the entry:
	-- Drop Sphere of Tepok (one of its two lord keys is a GROUND variant and
	-- the row carries no `grounded` flag) and Searing Torrent (a ground
	-- carrier - the user's own field note is that it behaves the same and
	-- recharges in melee, so melee is NOT required, only excluded).
	-- The four constants and the fast pass are defined once, above the
	-- evaluator; nothing here is per-entry.
	-- ======================================================================""".split("\n")
    lines = splice(lines, a, b - 1, fam)
    a = idx(lines, "local function poll_body()", "poll_body")
    lines = splice(lines, a, a, fn)

    out = "\n".join(lines)
    wr(path, out)
    # ---- assertions --------------------------------------------------------
    for tok in ("FOURTH.AIR_DROP_CENTER_M", "FOURTH.AIR_DROP_DELAY_S",
                "FOURTH.AIR_DROP_ENEMY_LEAD", "FOURTH.AIR_DROP_CASTER_DELAY_S",
                "FOURTH.AIR_DROP_CASTER_LEAD", "FOURTH.AIR_DROP_INHERIT",
                "FOURTH.AIR_DROP_MODEL_RADIUS_M", "FOURTH.AIR_DROP_RANKS",
                "FOURTH.AIR_DROP_FRONTAGE_MIN_M", "FOURTH.AIR_DROP_FRONTAGE_MAX_M",
                "FOURTH.ad_frontage", "FOURTH.ad_seg_dist", "FOURTH.ad_lead",
                "FOURTH.ad_project", "FOURTH.ad_dial_text", "FOURTH.ad_centre_gap",
                "FOURTH.ad_single_say", "FOURTH.ad_single_clear",
                "FOURTH.ad_vec_text", "FOURTH.ad_velocity", "FOURTH.ad_pos",
                "FOURTH.ad_sep", "function FOURTH.ad_frontage_text"):
        assert tok not in out, "leftover: " + tok
    assert out.count("function FOURTH.try_pair(") == 1
    assert out.count("function FOURTH.ad_fast_pass()") == 1
    NL = chr(10)
    for k, v in (("EDGE_M", "0.1"), ("MIN_MEN", "10"), ("NEAR_M", "30"), ("FAST_S", "0.2")):
        body = "FOURTH.AIR_DROP_" + k + " = " + v
        assert (NL + body + NL) in out, k
        assert out.count(NL + body + NL) == 1, k
    assert out.count('trigger = "air_drop_on_infantry"') == 12
    assert out.count("enemy_is_infantry") == 3, out.count("enemy_is_infantry")
    print("%-8s lines %d -> %d  bytes %d" % ("ann" if ann else "live", n0, len(lines),
                                             len(out.encode("utf-8"))))


if __name__ == "__main__":
    edit(LIVE, False)
    edit(ANN, True)
    print("OK")
