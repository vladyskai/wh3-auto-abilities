#!/usr/bin/env python3
"""Round 116 edit: the air-drop wait becomes VELOCITY-AWARE and DYNAMIC.

Replaces the fixed 1.0 s dwell with a delay measured ONCE at first contact from
the enemy's own velocity (projected onto the enemy -> caster axis), and adds the
read-verification log the user asked for.  Applied to BOTH copies (live +
annotated) with exact occurrence assertions.  Binary read/write so the shipped
file stays LF.
"""
import sys

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
LIVE = ROOT + r"\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = ROOT + r"\docs\WH3_auto_ability_annotated.lua"


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


def must(s, old, new, count=1):
    n = s.count(old)
    assert n == count, "anchor %r matched %d (want %d)" % (old[:80], n, count)
    return s.replace(old, new)


# ============================================================================
# 1. THE HEADER + THE TWO CONSTANTS
# ============================================================================
OLD_HEAD_1 = """-- ============================================================================
-- ROUND 115 - THE TRIGGER WAITS: A 1-SECOND DWELL ON THE PAIR
--
-- THE USER'S RULING, verbatim: \"I mean the trigger fires too soon. So we need
-- a delay of 1 second for the trigger.\"
--
"""
NEW_HEAD_1 = """-- ============================================================================
-- ROUND 116 - THE WAIT IS MEASURED, NOT FIXED: THE ENEMY'S OWN VELOCITY
--
-- THE USER'S RULING, verbatim: \"The issue is that if the enemy unit is running
-- away, then it is too soon. If the enemy moving is running towards, then it is
-- too late. So to actually make it work, I think we do need relative velocity.
-- But it must be calculated the moment the edge to edge distance is below our
-- theshold. Then, if the unit is running towards the caster, then the delay
-- would be 0. If running away, then the delay would be 2. If stationary or
-- perpedicular, then should be 1. ... the delay is dynamic in this way.\"
--
-- ROUND 115 (below) is the history: a FIXED 1-second dwell on the pair. The
-- user proved a fixed delay cannot be right - it is too late for an enemy
-- charging in and too soon for one running away - so round 116 REPLACES the
-- fixed value with a measurement taken from the enemy's own velocity. The
-- dwell MACHINERY (the pair row, the poll clock, the fallback, the purge, the
-- re-check) is kept; only the NUMBER it waits for is now dynamic.
--
-- THE FORMULA - one line, no dials:
--   axis  = normalise(caster.position - enemy.position)        (x/z only)
--   v     = speed * normalise(ordered_position - position)     (the heading)
--   proj  = dot(v, axis) / (speed * |axis|)                    (the COSINE,
--                                                              clamped to +-1)
--   delay = AIR_DROP_DWELL_MID_S - (AIR_DROP_DWELL_SWING_S * proj), floored at 0
-- with MID = 1.0 s and SWING = 1.0 s that is:
--   proj +1  running straight AT the caster        -> 0.0 s
--   proj  0  stationary, or perpendicular to it    -> 1.0 s
--   proj -1  running straight AWAY from the caster -> 2.0 s
-- and everything between interpolates linearly (proj +0.71 -> 0.29 s,
-- proj -0.71 -> 1.71 s). The user's three cases, and the smooth ramp between
-- them, come out of that one subtraction.
--
-- MEASURED ONCE PER CONTACT: on the FIRST evaluation of a contact - the one
-- that stamps the pair - and NEVER again inside that contact, even if the
-- enemy turns. A re-contact after a separation starts a FRESH measurement.
-- The fire condition keeps its shape: elapsed >= THIS pair's own delay, on the
-- poll's tick_count clock (POLL_MS = 250 ms), so the cast lands on the first
-- poll at or after the measured delay. A delay of 0 therefore fires on the
-- NEXT evaluation - never on the stamping one.
--
-- THE DELAY LANDS ON THE POLL GRID: tick_count moves in 250 ms steps, so a
-- measured 0.29 s waits 0.50 s (two polls) and a measured 1.71 s waits 1.75 s.
-- The log prints the MEASURED value; the grid is what the clock can deliver.
-- Quantisation can only delay a cast, never advance it.
--
-- THE READ-VERIFICATION LOG (the user's second request): EVERY contact episode
-- prints the RAW answers the projection depends on - is_moving,
-- is_moving_fast, slow_speed, fast_speed, position(), ordered_position(), the
-- heading length, the projected cosine, the delay and the velocity source -
-- with UNREADABLE where a read failed. If ordered_position() answers the
-- CURRENT position (the documented behaviour while a unit is ATTACKING), the
-- line says so directly: |h|=0.0 ... src=no-heading. Nothing here is assumed.
--
-- THE THREE CONSTANTS - one test value each, no per-entry edit needed:
--   AIR_DROP_DWELL_MID_S   = 1.0 s  the delay at proj 0 (stationary / across)
--   AIR_DROP_DWELL_SWING_S = 1.0 s  how far proj +-1 moves it: MID + SWING =
--                                   2.0 s receding, MID - SWING = 0.0 s
--                                   closing (floored at 0, never negative)
--   AIR_DROP_MIN_CONTACT_S = 0.3 s  the short-crossing floor (round 115,
--                                   unchanged): a separation after this much
--                                   contact fires on the way out
-- ============================================================================
"""
OLD_CONST = """FOURTH.AIR_DROP_DWELL_S = 1.0
FOURTH.AIR_DROP_MIN_CONTACT_S = 0.3
"""
NEW_CONST = """FOURTH.AIR_DROP_DWELL_MID_S = 1.0
FOURTH.AIR_DROP_DWELL_SWING_S = 1.0
FOURTH.AIR_DROP_MIN_CONTACT_S = 0.3
"""

# ============================================================================
# 2. THE CONTACT STATE COMMENT
# ============================================================================
OLD_STATE = """-- THE DWELL STATE (round 115). ONE row per pair, and nothing else: the tick the
-- contact started on and the two ui ids, so a dropped unit can purge its rows.
-- No gap history, no closing rate, no velocity.
"""
OLD_STATE_ANN = """-- THE DWELL STATE (round 115): one row per pair - the tick the contact started
-- on and the two ui ids (for the purge). No gap history, no closing rate.
"""
NEW_STATE = """-- THE CONTACT STATE (round 116). ONE row per pair: the tick the contact started
-- on, THE DELAY MEASURED AT THAT TICK, the cosine it came from and the source
-- that produced the velocity - so a second evaluation inside the same contact
-- READS THE DECISION BACK instead of re-taking it. No gap history, no closing
-- rate, no second measurement: the row is dropped on separation and rebuilt
-- from scratch on a re-contact.
"""

# ============================================================================
# 3. THE STAMP + THE NEED READER
# ============================================================================
OLD_STAMP = """-- STAMP the contact: ONE timestamp, the fast-pass tick the pair went under on.
function FOURTH.ad_pair_stamp(cid, eid)
\tlocal per = FOURTH.ad_pair[cid]
\tif per == nil then per = {}; FOURTH.ad_pair[cid] = per end
\tper[eid] = { first = tick_count }
end
"""
NEW_STAMP = """-- STAMP the contact: ONE timestamp - the fast-pass tick the pair went under on -
-- plus THE DELAY MEASURED ON THAT TICK and the evidence behind it (proj, src).
-- The hold and fire lines print those stored values, so the decision can never
-- be quietly re-taken halfway through a contact.
function FOURTH.ad_pair_stamp(cid, eid, delay, proj, src)
\tlocal per = FOURTH.ad_pair[cid]
\tif per == nil then per = {}; FOURTH.ad_pair[cid] = per end
\tper[eid] = { first = tick_count, delay = delay, proj = proj, src = src }
end

-- THE DELAY THIS PAIR WAS GIVEN at its own first contact. A row without one
-- (nothing writes such a row, but the guard costs nothing) answers the MID
-- baseline rather than nil.
function FOURTH.ad_pair_need(st)
\tif st ~= nil and type(st.delay) == "number" then return st.delay end
\treturn FOURTH.AIR_DROP_DWELL_MID_S
end
"""

# ============================================================================
# 4. THE VELOCITY + DELAY HELPERS (inserted before the evaluator banner)
# ============================================================================
HELPERS = r"""-- ============================================================================
-- THE VELOCITY READS (round 116) - every value the dynamic delay depends on,
-- taken ONCE, answered EXACTLY as the engine returned it, and turned into ONE
-- log line. is_moving / is_moving_fast / slow_speed / fast_speed / position /
-- ordered_position are the documented battle_unit reads (battle_unit.lua:171,
-- 175, 179, 183, 116, 120); ordered_position is documented as "the position to
-- which the unit has been ordered to move to. Note that if the unit is
-- attacking, as opposed to moving, then this will return the current position
-- of the unit" - which is exactly the case the log below exists to expose.
-- ============================================================================
-- THE RAW READS, VERBATIM, AS ONE STRING BODY (no prefix):
--   moving=true is_moving_fast=false slow_speed=2.30 fast_speed=4.10
--   pos=(123.4,567.8) ordered=(130.1,565.2) |h|=6.9
-- UNREADABLE stands in for any read whose pcall failed. The callers prefix it
-- with "reads: " (the measurement) or "reads(hold): " (a waiting tick).
FOURTH.ad_vread = ""
-- the enemy position the LAST ad_enemy_velocity() read, reused for the axis so
-- one contact is measured against ONE pair of positions
FOURTH.ad_vread_px = nil
FOURTH.ad_vread_pz = nil

-- THE ENEMY'S VELOCITY in the x/z plane, from the documented reads only:
--   v = speed * normalise(ordered_position - position)
-- Returns vx, vz, speed, src. EVERY read is pcalled and fails CLOSED: a read
-- that cannot be taken answers a ZERO velocity and a src that names the reason,
-- which the delay turns into the 1.0 s baseline. src is one of
--   ordered            a real heading was read; the velocity is built from it
--   stationary         is_moving() answered false - no motion at all
--   moving-unreadable  is_moving() raised
--   speed-unreadable   the speed read for the unit's state raised
--   speed-zero         the speed read answered <= 0 while the unit is moving
--   pos-unreadable     position() (or its co-ordinates) could not be read
--   no-heading         ordered_position() unreadable, OR the ordered point is
--                      under 0.5 m away - the documented "attacking" case
function FOURTH.ad_enemy_velocity(enemy)
	local parts = {}
	local function say(s) parts[#parts + 1] = s end
	local function put_num(tag, ok, v)
		if ok and type(v) == "number" then
			say(string.format("%s=%.2f", tag, v))
			return v
		end
		say(tag .. "=UNREADABLE")
		return nil
	end
	local function put_bool(tag, ok, v)
		if ok and type(v) == "boolean" then
			say(tag .. "=" .. tostring(v))
			return v
		end
		say(tag .. "=UNREADABLE")
		return nil
	end
	local function put_xy(tag, ok, obj)
		local x, z = nil, nil
		if ok and obj ~= nil then
			local ok_x, vx = pcall(function() return obj:get_x() end)
			local ok_z, vz = pcall(function() return obj:get_z() end)
			if ok_x and ok_z and type(vx) == "number" and type(vz) == "number" then
				x, z = vx, vz
			end
		end
		if x == nil then
			say(tag .. "=UNREADABLE")
		else
			say(string.format("%s=(%.1f,%.1f)", tag, x, z))
		end
		return x, z
	end

	local ok_m, moving = pcall(function() return enemy:is_moving() end)
	local ok_f, fast = pcall(function() return enemy:is_moving_fast() end)
	local ok_s, slow = pcall(function() return enemy:slow_speed() end)
	local ok_q, fastsp = pcall(function() return enemy:fast_speed() end)
	local moving_v = put_bool("moving", ok_m, moving)
	local fast_v = put_bool("is_moving_fast", ok_f, fast)
	local slow_speed = put_num("slow_speed", ok_s, slow)
	local fast_speed = put_num("fast_speed", ok_q, fastsp)

	local ok_p, pos = pcall(function() return enemy:position() end)
	local ok_o, ord = pcall(function() return enemy:ordered_position() end)
	local px, pz = put_xy("pos", ok_p, pos)
	local ox, oz = put_xy("ordered", ok_o, ord)
	FOURTH.ad_vread_px, FOURTH.ad_vread_pz = px, pz

	local hlen = nil
	if px ~= nil and ox ~= nil then
		hlen = math.sqrt(((ox - px) * (ox - px)) + ((oz - pz) * (oz - pz)))
		say(string.format("|h|=%.1f", hlen))
	else
		say("|h|=UNREADABLE")
	end
	FOURTH.ad_vread = table.concat(parts, " ")

	if moving_v ~= true then
		-- false: stationary. nil: the read failed. Either way there is no
		-- velocity to project, and the delay stays on its 1.0 s baseline.
		return 0, 0, 0, (moving_v == false and "stationary" or "moving-unreadable")
	end
	local speed = nil
	if fast_v == true then speed = fast_speed else speed = slow_speed end
	if speed == nil then return 0, 0, 0, "speed-unreadable" end
	if speed <= 0 then return 0, 0, speed, "speed-zero" end
	if px == nil then return 0, 0, speed, "pos-unreadable" end
	if hlen == nil or hlen < 0.5 then
		-- the ordered point IS the current position (or could not be read): the
		-- documented "attacking" shape. No heading can be built, so no cosine.
		return 0, 0, speed, "no-heading"
	end
	local ux, uz = (ox - px) / hlen, (oz - pz) / hlen
	return ux * speed, uz * speed, speed, "ordered"
end

-- THE COSINE AS THE LOG PRINTS IT. cos(90 deg) is 6e-17, so an exactly
-- perpendicular approach would otherwise read "-0.00" - a sign with no meaning.
-- Anything within half a printed unit of zero prints as +0.00.
function FOURTH.ad_proj_text(proj)
	local p = proj
	if type(p) ~= "number" then p = 0 end
	if p > -0.005 and p < 0.005 then p = 0 end
	return string.format("%+.2f", p)
end

-- THE DYNAMIC DELAY (round 116) - the user's formula, in one line:
--   proj  = cos(angle between the enemy's velocity and the enemy -> caster axis)
--   delay = MID - (SWING * proj), floored at 0
-- Returns delay (s), proj (the cosine actually used, clamped to +-1) and src
-- (why the velocity is what it is). An unreadable axis or an unknown / zero
-- velocity answers the MID baseline and names the reason instead.
function FOURTH.ad_dynamic_delay(caster, enemy)
	local vx, vz, speed, src = FOURTH.ad_enemy_velocity(enemy)
	if speed <= 0 or (vx == 0 and vz == 0) then
		return FOURTH.AIR_DROP_DWELL_MID_S, 0, src
	end
	local ok_cp, cpos = pcall(function() return caster:position() end)
	local cx, cz = nil, nil
	if ok_cp and cpos ~= nil then
		local ok_x, x = pcall(function() return cpos:get_x() end)
		local ok_z, z = pcall(function() return cpos:get_z() end)
		if ok_x and ok_z and type(x) == "number" and type(z) == "number" then
			cx, cz = x, z
		end
	end
	if cx == nil or FOURTH.ad_vread_px == nil then
		return FOURTH.AIR_DROP_DWELL_MID_S, 0, "axis-unreadable"
	end
	-- THE AXIS: from the ENEMY to the CASTER. The enemy's velocity projected on
	-- THIS axis is +1 when it is closing on the caster and -1 when it is
	-- running away from it.
	local ax, az = cx - FOURTH.ad_vread_px, cz - FOURTH.ad_vread_pz
	local alen = math.sqrt((ax * ax) + (az * az))
	if alen < 0.5 then
		-- the two centres are on top of each other in x/z: the axis has no
		-- direction, so there is nothing to project on. Baseline, and say so.
		return FOURTH.AIR_DROP_DWELL_MID_S, 0, "axis-degenerate"
	end
	local proj = ((vx * ax) + (vz * az)) / (speed * alen)
	if proj > 1 then proj = 1 elseif proj < -1 then proj = -1 end
	local delay = FOURTH.AIR_DROP_DWELL_MID_S - (FOURTH.AIR_DROP_DWELL_SWING_S * proj)
	if delay < 0 then delay = 0 end
	return delay, proj, src
end

"""
OLD_INSERT = "-- THE AIR-DROP EVALUATOR. ONE comparison decides"
NEW_INSERT = HELPERS + "-- THE AIR-DROP EVALUATOR. ONE comparison decides"

# ============================================================================
# 5. THE EVALUATOR TAIL (from the pair lookup to the function's end)
# ============================================================================
PICK_TAIL_HEAD = "\tlocal per = FOURTH.ad_pair[cid]\n\tlocal st = nil\n"

PICK_TAIL = r"""	local per = FOURTH.ad_pair[cid]
	local st = nil
	if per ~= nil then st = per[eid] end
	local under = 0
	local need_s = 0
	local on_sep = false
	if dist >= FOURTH.AIR_DROP_EDGE_M then
		-- SEPARATION (or a pass that never touched the line). The contact is over.
		if st == nil then
			FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
				.. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m) -> NOT YET")
			return nil
		end
		under = FOURTH.ad_under(st)
		need_s = FOURTH.ad_pair_need(st)
		FOURTH.ad_pair_drop(cid, eid)
		if under >= FOURTH.AIR_DROP_MIN_CONTACT_S then
			on_sep = true
			-- THE SHORT-CROSSING FALLBACK: the pair DID hold long enough to count,
			-- so the drop leaves NOW, on the separation evaluation, instead of
			-- being lost. The delay it was waiting for is logged with it, so a
			-- contact the measurement had made too long is visible as such.
			FOURTH.ad_event(unit, marker, string.format(
				"short crossing: under for %.2fs (>= %.2fs) -> FIRING on separation"
				.. " (gap %.2fm, the delay measured was %.2fs)",
				under, FOURTH.AIR_DROP_MIN_CONTACT_S, dist, need_s))
		else
			-- CANCELLED, and the time actually under is the tuning datum.
			FOURTH.ad_event(unit, marker, string.format(
				"dwell cancelled: separated after %.2fs (gap %.2fm; the dwell is %.2fs"
				.. " and the short-crossing floor is %.2fs)",
				under, dist, need_s, FOURTH.AIR_DROP_MIN_CONTACT_S))
			FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
				.. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m) -> NOT YET")
			return nil
		end
	else
		-- UNDER THE LINE: THE DELAY THIS PAIR WAS GIVEN decides.
		if st == nil then
			-- FIRST CONTACT: MEASURE ONCE, HERE, AND NEVER AGAIN IN THIS CONTACT.
			-- The velocity, the cosine and the delay are taken from the reads on
			-- THIS tick - the moment the edge gap dropped under the line, which
			-- is what the user asked for - and stored on the pair row.
			local delay, proj, vsrc = FOURTH.ad_dynamic_delay(unit, enemy)
			FOURTH.ad_pair_stamp(cid, eid, delay, proj, vsrc)
			FOURTH.ad_event(unit, marker, "reads: " .. FOURTH.ad_vread
				.. " proj=" .. FOURTH.ad_proj_text(proj)
				.. string.format(" src=%s delay=%.2fs (measured once for this contact)",
					vsrc, delay))
			FOURTH.ad_event(unit, marker, string.format(
				"dwell started: under at gap %.2fm, waiting %.2fs (pair '%s')",
				dist, delay, etype))
			return nil     -- THE FIRST EVALUATION OF A CONTACT NEVER FIRES
		end
		under = FOURTH.ad_under(st)
		need_s = FOURTH.ad_pair_need(st)
		if (under + 0.000001) >= need_s then
			FOURTH.ad_event(unit, marker, string.format(
				"dwell satisfied after %.2fs -> FIRING (gap %.2fm, pair '%s')",
				under, dist, etype))
			-- the contact is CONSUMED: a repeat has to earn its own measurement
			FOURTH.ad_pair_drop(cid, eid)
		else
			-- THE WAIT. The reads are re-taken and PRINTED (so the log shows what
			-- ordered_position() is answering right now) but the delay and the
			-- cosine printed are the ones MEASURED AT THE STAMP: nothing is
			-- re-measured inside a contact.
			FOURTH.ad_enemy_velocity(enemy)
			FOURTH.ad_event(unit, marker, "reads(hold): " .. FOURTH.ad_vread
				.. " proj=" .. FOURTH.ad_proj_text(st.proj or 0)
				.. string.format(" src=%s delay=%.2fs held=%.2fs",
					tostring(st.src or "?"), need_s, under))
			FOURTH.ad_event(unit, marker, string.format(
				"dwell: under %.2fs of %.2fs (gap %.2fm)", under, need_s, dist))
			return nil
		end
	end
	FOURTH.ad_enemy = enemy
	FOURTH.ad_caster_su = FOURTH.eg_fresh_caster_su(unit)
	-- THE DELAY EVIDENCE the pre-cast re-check re-verifies: how long the pair had
	-- really been under, THE DELAY IT WAS WAITING FOR, and whether it fired on the
	-- fallback (in which case the gap at the re-check is over the line BY
	-- CONSTRUCTION).
	FOURTH.ad_fired = { under = under, delay = need_s, fallback = (on_sep or under < need_s) }
__SAY__
	if under < need_s then
		return "nearest valid '" .. etype .. "' has " .. tostring(men)
			.. " models; SHORT CROSSING - it held " .. string.format("%.2f", under)
			.. "s under the " .. need .. "m edge line and has separated to " .. edge_text
			.. "m (fallback floor " .. string.format("%.2f", FOURTH.AIR_DROP_MIN_CONTACT_S) .. "s)"
	end
	return "nearest valid '" .. etype .. "' has " .. tostring(men) .. " models, its EDGE gap is "
		.. edge_text .. "m - under the " .. need .. "m line for " .. string.format("%.2f", under)
		.. "s, so the delay measured for this contact ("
		.. string.format("%.2f", need_s) .. "s) is satisfied"
end
"""

SAY_LIVE = r"""	-- THE FIRING DECISION, on the same change gate as the NOT YET line: the
	-- ATTEMPT + re-check lines below are what mark each actual cast.
	FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
		.. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m) -> FIRING"
		.. " (the nearest of the valid enemies; unit_distance is edge-to-edge)")
"""
SAY_ANN = r"""	-- (annotated copy: the FIRING decision line is a log-only line that repeats
	-- the nearest enemy, its entity count, the exact edge and the delay it waited
	-- for on every cast)
"""

# ============================================================================
# 6. THE PRE-CAST RE-CHECK FLOOR
# ============================================================================
OLD_FLOOR = """\t\tif fired ~= nil and type(fired.under) == \"number\" then
\t\t\tlocal floor_s = FOURTH.AIR_DROP_DWELL_S
\t\t\tif fallback_now then floor_s = FOURTH.AIR_DROP_MIN_CONTACT_S end
"""
NEW_FLOOR = """\t\tif fired ~= nil and type(fired.under) == \"number\" then
\t\t\t-- ROUND 116: THE FLOOR IS THIS PAIR'S OWN MEASURED DELAY, recorded by
\t\t\t-- the evaluator at the moment of contact. The re-check never re-measures
\t\t\t-- it (the enemy may already be somewhere else by the time it runs); it
\t\t\t-- verifies that the wait the cast was granted was really served.
\t\t\tlocal floor_s = FOURTH.AIR_DROP_DWELL_MID_S
\t\t\tif type(fired.delay) == \"number\" then floor_s = fired.delay end
\t\t\tif fallback_now then floor_s = FOURTH.AIR_DROP_MIN_CONTACT_S end
"""

# ============================================================================
# 7. THE TOOLTIP SENTENCE
# ============================================================================
OLD_TIP = ('\tair_drop_on_infantry = "When armed, fires when the nearest enemy unit with more '
           'than 10 models stays within 0.1 m of this unit\'s edge for 1 second, airborne '
           'where the ability requires it",')
NEW_TIP = ('\tair_drop_on_infantry = "When armed, fires when the nearest enemy unit with more '
           'than 10 models closes to 0.1 m of this unit\'s edge, after a wait measured from that '
           'enemy\'s velocity at the moment of contact: 0 s if it is running at this unit, 1 s '
           'if it is stationary or crossing, 2 s if it is running away, airborne where the '
           'ability requires it",')

# ============================================================================
# 8. THE ROUND-114 RULE SENTENCE (FIRE is no longer the bare comparison)
# ============================================================================
OLD_RULE = """--   FIRE      = unit_distance(caster, chosen) < AIR_DROP_EDGE_M (0.10 m)
"""
NEW_RULE = """--   UNDER     = unit_distance(caster, chosen) < AIR_DROP_EDGE_M (0.10 m)
--   FIRE      = UNDER, and the delay measured for that pair at the first
--               contact of the episode has elapsed (round 116 - see below)
"""

OLD_HEAD_2 = """-- THE DWELL, in full - round 114's edge rule is unchanged, it now has to LAST:
--   * when the NEAREST valid enemy's edge gap first drops under
--     AIR_DROP_EDGE_M the PAIR (caster ui id, enemy ui id) is stamped with the
--     poll tick it happened on and NOTHING is cast: the first evaluation
--     of a contact can never fire;
--   * it fires once the pair has been CONTINUOUSLY under the line for
--     AIR_DROP_DWELL_S = 1.0 s, with both units still valid at the pre-cast
--     re-check;
--   * a separation BEFORE that cancels the dwell and logs how long the pair was
--     actually under plus the gap it separated to - that line is the tuning
--     datum, read it to decide whether the dwell is too long for the crossings
--     actually being flown;
--   * a separation AFTER AIR_DROP_MIN_CONTACT_S = 0.3 s fires on the
--     SEPARATION EVALUATION (the short-crossing fallback), so a quick pass
--     through the formation is not silently lost;
--   * a re-contact after a separation starts a FRESH dwell - the old stamp is
--     gone and is never inherited;
--   * the row lives and dies with the unit: drop_unit_by_ui_id purges every
--     pair row that names it.
--
-- THE CLOCK IS THE POLL'S OWN tick_count (round 115). It advances once per poll
-- (POLL_MS = 250 ms), it always runs - the poll is registered at load and does
-- not depend on the fast pass being alive - and it is the same counter the
-- heartbeat and every guard already use. The fast pass therefore ADDS
-- evaluations (5/s) but never time: it can fire the moment the poll's clock
-- completes the dwell, so the drop lands between AIR_DROP_DWELL_S and
-- AIR_DROP_DWELL_S + 0.25 s after the contact began. No engine clock is read
-- anywhere (os.clock's meaning in this Lua state is unproven), and a missed
-- poll can only make a pair wait LONGER - never fire early, which is the safe
-- direction for a trigger that was reported as firing too soon.
--
-- THE TWO NEW CONSTANTS - one test value each, no per-entry edit needed:
--   AIR_DROP_DWELL_S       = 1.0 s  the pair must hold under the line this long
--   AIR_DROP_MIN_CONTACT_S = 0.3 s  the short-crossing floor: a separation
--                                   after this much contact fires on the way out
"""
NEW_HEAD_2 = """-- ============================================================================
-- ROUND 115 (HISTORY - the machinery survives, the fixed value does not):
--   * when the NEAREST valid enemy's edge gap first drops under
--     AIR_DROP_EDGE_M the PAIR (caster ui id, enemy ui id) is stamped with the
--     poll tick it happened on and NOTHING is cast: the first evaluation
--     of a contact can never fire;
--   * it fires once the pair has been CONTINUOUSLY under the line for the delay
--     THIS CONTACT was given (round 116: measured from the enemy's velocity;
--     round 115: a fixed 1.0 s), with both units still valid at the pre-cast
--     re-check;
--   * a separation BEFORE that cancels and logs how long the pair was actually
--     under plus the gap it separated to - that line is the tuning datum;
--   * a separation AFTER AIR_DROP_MIN_CONTACT_S = 0.3 s fires on the
--     SEPARATION EVALUATION (the short-crossing fallback), so a quick pass
--     through the formation is not silently lost;
--   * a re-contact after a separation starts a FRESH measurement - the old
--     stamp is gone and is never inherited;
--   * the row lives and dies with the unit: drop_unit_by_ui_id purges every
--     pair row that names it.
--
-- THE CLOCK IS THE POLL'S OWN tick_count. It advances once per poll
-- (POLL_MS = 250 ms), it always runs - the poll is registered at load and does
-- not depend on the fast pass being alive - and it is the same counter the
-- heartbeat and every guard already use. The fast pass therefore ADDS
-- evaluations (5/s) but never time: it can fire the moment the poll's clock
-- completes the delay, so a cast lands between the measured delay and 0.25 s
-- after it. No engine clock is read anywhere (os.clock's meaning in this Lua
-- state is unproven), and a missed poll can only make a pair wait LONGER -
-- never fire early, which is the safe direction for a trigger that was
-- reported as firing too soon.
-- ============================================================================
"""

OLD_UNDER = """-- waiting on a timer that is not registered. One tick = 0.25 s; the fire lands
-- between AIR_DROP_DWELL_S and AIR_DROP_DWELL_S + 0.25 s. Zero for an unstamped
-- pair, and never negative (a stale stamp can only delay, never advance).
"""
NEW_UNDER = """-- waiting on a timer that is not registered. One tick = 0.25 s, so the cast
-- lands on the first poll at or after the pair's MEASURED delay. Zero for an
-- unstamped pair, and never negative (a stale stamp can only delay, never
-- advance).
"""

OLD_RC_COMMENT = """\t\t-- dwell fire must have held AIR_DROP_DWELL_S; a fallback fire must have
"""
NEW_RC_COMMENT = """\t\t-- dwell fire must have served the delay MEASURED for that contact (round
\t\t-- 116; round 115 held a fixed 1.0 s); a fallback fire must have
"""

OLD_ANN_HEAD = """-- ============================================================================
-- ROUND 115 - THE TRIGGER WAITS: A 1-SECOND DWELL ON THE PAIR
--
-- The rule: the nearest valid enemy's edge gap must stay under AIR_DROP_EDGE_M
-- for AIR_DROP_DWELL_S = 1.0 s before the drop is cast. The first evaluation of
-- a contact stamps the pair and never fires; a separation cancels the dwell and
-- a separation after AIR_DROP_MIN_CONTACT_S = 0.3 s fires on the separation
-- evaluation (the short-crossing fallback); a re-contact starts a fresh dwell.
-- The clock is the poll's own tick_count (one tick = POLL_MS = 250 ms), so a
-- missed poll can only make the pair wait longer, never fire early.
-- ============================================================================
"""
NEW_ANN_HEAD = """-- ============================================================================
-- ROUND 116 - THE WAIT IS MEASURED, NOT FIXED: THE ENEMY'S OWN VELOCITY
--
-- The rule: the nearest valid enemy with more than AIR_DROP_MIN_MEN models must
-- stay under AIR_DROP_EDGE_M for a delay MEASURED at the first contact of the
-- episode and never re-measured inside it:
--   proj  = cos(angle between the enemy's velocity and the enemy -> caster axis)
--   delay = AIR_DROP_DWELL_MID_S - AIR_DROP_DWELL_SWING_S * proj, floored at 0
-- so a closing enemy waits 0 s, a stationary or perpendicular one 1 s and a
-- receding one 2 s, with every angle in between interpolated. The first
-- evaluation of a contact stamps the pair and never fires; a separation cancels
-- and a separation after AIR_DROP_MIN_CONTACT_S = 0.3 s fires on the separation
-- evaluation (the short-crossing fallback); a re-contact starts a fresh
-- MEASUREMENT. The clock is the poll's own tick_count (one tick = POLL_MS =
-- 250 ms), so a missed poll can only make the pair wait longer, never fire
-- early.
-- ============================================================================
"""

def _tabs(x):
    """The r-strings carry literal \\t sequences; Lua wants real tabs."""
    return x.replace(chr(92) + "t", chr(9))


# ============================================================================
# APPLY
# ============================================================================
def apply(path, ann):
    global HELPERS, PICK_TAIL, SAY_LIVE, SAY_ANN
    HELPERS = _tabs(HELPERS)
    PICK_TAIL = _tabs(PICK_TAIL)
    SAY_LIVE = _tabs(SAY_LIVE)
    SAY_ANN = _tabs(SAY_ANN)
    s = rd(path)
    tag = "ANN" if ann else "LIVE"

    s = must(s, OLD_ANN_HEAD if ann else OLD_HEAD_1, NEW_ANN_HEAD if ann else NEW_HEAD_1)
    if not ann:
        s = must(s, OLD_HEAD_2, NEW_HEAD_2)
    s = must(s, OLD_CONST, NEW_CONST)
    s = must(s, OLD_STATE_ANN if ann else OLD_STATE, NEW_STATE)
    s = must(s, OLD_STAMP, NEW_STAMP)
    s = must(s, OLD_INSERT, HELPERS + OLD_INSERT)
    s = must(s, OLD_RULE, NEW_RULE)
    s = must(s, OLD_UNDER, NEW_UNDER)
    if not ann:
        s = must(s, OLD_RC_COMMENT, NEW_RC_COMMENT)

    # the evaluator tail: from the pair lookup to the line before the trigger name
    i = s.index(PICK_TAIL_HEAD)
    j = s.index("\n-- THE TRIGGER NAME STAYS")
    assert j > i, "tail markers out of order"
    old_tail = s[i:j]
    assert "dwell satisfied after" in old_tail and "short crossing: under for" in old_tail
    say = SAY_ANN if ann else SAY_LIVE
    s = s[:i] + PICK_TAIL.replace("__SAY__", say.rstrip("\n")) + s[j:]

    s = must(s, OLD_FLOOR, NEW_FLOOR)
    s = must(s, OLD_TIP, NEW_TIP)

    # NOTHING may still reference the retired fixed constant (a prefix of the
    # two new names, so the boundary matters)
    import re as _re
    assert _re.search(r"AIR_DROP_DWELL_S(?![A-Z_])", s) is None, \
        "%s: a reference to the retired AIR_DROP_DWELL_S survives" % tag
    if ann:
        assert "log(" not in s, "ANN: the reading copy must stay log-free"
    wr(path, s)
    print("edited", tag, path)


apply(LIVE, False)
apply(ANN, True)
