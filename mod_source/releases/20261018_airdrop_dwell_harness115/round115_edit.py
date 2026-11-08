#!/usr/bin/env python3
"""Round 115 edit: the air-drop trigger WAITS.

Adds a per-pair 1-second dwell on top of the round-114 edge-gap rule, plus the
short-crossing fallback. Applied to BOTH copies (live + annotated) with exact
occurrence assertions. Binary read/write so the shipped file stays LF.
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
    assert n == count, "anchor %r matched %d (want %d)" % (old[:70], n, count)
    return s.replace(old, new)


# ============================================================================
# 1. THE TWO NEW CONSTANTS + THE DWELL HEADER
# ============================================================================
HEADER_LIVE = '''-- ============================================================================
-- ROUND 115 - THE TRIGGER WAITS: A 1-SECOND DWELL ON THE PAIR
--
-- THE USER'S RULING, verbatim: "I mean the trigger fires too soon. So we need
-- a delay of 1 second for the trigger."
--
-- THE DWELL, in full - round 114's edge rule is unchanged, it now has to LAST:
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
-- ============================================================================
FOURTH.AIR_DROP_DWELL_S = 1.0
FOURTH.AIR_DROP_MIN_CONTACT_S = 0.3
'''

HEADER_ANN = '''-- ============================================================================
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
FOURTH.AIR_DROP_DWELL_S = 1.0
FOURTH.AIR_DROP_MIN_CONTACT_S = 0.3
'''

STATE_LIVE = '''-- THE DWELL STATE (round 115). ONE row per pair, and nothing else: the tick the
-- contact started on and the two ui ids, so a dropped unit can purge its rows.
-- No gap history, no closing rate, no velocity.
FOURTH.ad_pair = {}
FOURTH.ad_fired = nil
'''

STATE_ANN = '''-- THE DWELL STATE (round 115): one row per pair - the tick the contact started
-- on and the two ui ids (for the purge). No gap history, no closing rate.
FOURTH.ad_pair = {}
FOURTH.ad_fired = nil
'''

HELPERS_LIVE = '''-- ============================================================================
-- THE DWELL HELPERS (round 115) - all FIELDS on FOURTH, so the chunk adds no
-- locals (the file sits at Lua's 200-local ceiling).
-- ============================================================================

-- THE PAIR KEYS: the caster's and the enemy's engine ui id, both as TEXT, and
-- nil when either cannot be read - a pair that cannot be named cannot be timed,
-- so it does not fire. NESTED (ad_pair[caster][enemy]), exactly like the arming
-- tables, so no composite string key exists anywhere in the file.
function FOURTH.ad_pair_key(unit, enemy)
	local ok_c, cid = pcall(function() return unit:unique_ui_id() end)
	local ok_e, eid = pcall(function() return enemy:unique_ui_id() end)
	if not ok_c or cid == nil or not ok_e or eid == nil then return nil end
	return tostring(cid), tostring(eid)
end

-- STAMP the contact: ONE timestamp, the fast-pass tick the pair went under on.
function FOURTH.ad_pair_stamp(cid, eid)
	local per = FOURTH.ad_pair[cid]
	if per == nil then per = {}; FOURTH.ad_pair[cid] = per end
	per[eid] = { first = tick_count }
end

-- DROP the contact row, and the caster's slot with it when it was the last one.
function FOURTH.ad_pair_drop(cid, eid)
	local per = FOURTH.ad_pair[cid]
	if per == nil then return end
	per[eid] = nil
	if next(per) == nil then FOURTH.ad_pair[cid] = nil end
end

-- THE DWELL EVENT LINE. One per EVENT (started / held / satisfied / cancelled /
-- short crossing), NOT change-gated like ad_say: every one of these is a
-- transition the tuning depends on being able to read back.
function FOURTH.ad_event(unit, marker, note)
	log("  " .. FOURTH.ad_tag(unit) .. tostring(marker) .. " " .. note)
end

-- SECONDS the pair has been CONTINUOUSLY under the edge line, on THE POLL'S OWN
-- CLOCK: tick_count advances once per poll (POLL_MS = 250 ms) and always runs,
-- whether or not the fast pass is doing anything, so a pair can never be stuck
-- waiting on a timer that is not registered. One tick = 0.25 s; the fire lands
-- between AIR_DROP_DWELL_S and AIR_DROP_DWELL_S + 0.25 s. Zero for an unstamped
-- pair, and never negative (a stale stamp can only delay, never advance).
function FOURTH.ad_under(st)
	if st == nil or st.first == nil then return 0 end
	local n = tick_count - st.first
	if n < 0 then n = 0 end
	return (n * POLL_MS) / 1000
end

-- PURGE, WITH THE UNIT: every contact row that names this ui id goes - as the
-- caster (its whole slot) or as the enemy (that one row). Called from
-- drop_unit_by_ui_id, the ONE drop routine, so a dead unit can never leave a
-- stamp behind for a later re-contact to inherit.
function FOURTH.ad_purge_unit(id_text)
	local idt = tostring(id_text)
	FOURTH.ad_pair[idt] = nil
	for cid, per in pairs(FOURTH.ad_pair) do
		per[idt] = nil
		if next(per) == nil then FOURTH.ad_pair[cid] = nil end
	end
end

-- NO VALID PAIR AT ALL: every contact row this caster holds is stale (the enemy
-- died, fell to <= AIR_DROP_MIN_MEN models, or stopped answering its distance).
-- They are cleared WITHOUT firing - there is nothing under the drop to fire at -
-- and a later re-contact has to start a fresh dwell.
function FOURTH.ad_contact_clear(unit, marker)
	local ok_c, cid = pcall(function() return unit:unique_ui_id() end)
	if not ok_c or cid == nil then return end
	local idt = tostring(cid)
	local per = FOURTH.ad_pair[idt]
	if per == nil then return end
	local n = 0
	for _ in pairs(per) do n = n + 1 end
	FOURTH.ad_pair[idt] = nil
	if n > 0 then
		FOURTH.ad_event(unit, marker, "dwell cancelled: no valid pair any more ("
			.. tostring(n) .. " contact row(s) cleared)")
	end
end

'''

HELPERS_ANN = '''-- ============================================================================
-- THE DWELL HELPERS (round 115) - all FIELDS on FOURTH, so the chunk adds no
-- locals (the file sits at Lua's 200-local ceiling).
-- ============================================================================

-- THE PAIR KEYS: the caster's and the enemy's engine ui id, both as TEXT, and
-- nil when either cannot be read - a pair that cannot be named cannot be timed,
-- so it does not fire. NESTED (ad_pair[caster][enemy]), exactly like the arming
-- tables, so no composite string key exists anywhere in the file.
function FOURTH.ad_pair_key(unit, enemy)
	local ok_c, cid = pcall(function() return unit:unique_ui_id() end)
	local ok_e, eid = pcall(function() return enemy:unique_ui_id() end)
	if not ok_c or cid == nil or not ok_e or eid == nil then return nil end
	return tostring(cid), tostring(eid)
end

-- STAMP the contact: ONE timestamp, the fast-pass tick the pair went under on.
function FOURTH.ad_pair_stamp(cid, eid)
	local per = FOURTH.ad_pair[cid]
	if per == nil then per = {}; FOURTH.ad_pair[cid] = per end
	per[eid] = { first = tick_count }
end

-- DROP the contact row, and the caster's slot with it when it was the last one.
function FOURTH.ad_pair_drop(cid, eid)
	local per = FOURTH.ad_pair[cid]
	if per == nil then return end
	per[eid] = nil
	if next(per) == nil then FOURTH.ad_pair[cid] = nil end
end

-- (annotated copy: the dwell event line - started / held / satisfied /
-- cancelled / short crossing - is a log-only line written here in the live
-- build. The hook stays so the call sites read the same in both copies.)
function FOURTH.ad_event(unit, marker, note)
end

-- SECONDS the pair has been CONTINUOUSLY under the edge line, on THE POLL'S OWN
-- CLOCK: tick_count advances once per poll (POLL_MS = 250 ms) and always runs,
-- whether or not the fast pass is doing anything, so a pair can never be stuck
-- waiting on a timer that is not registered. One tick = 0.25 s; the fire lands
-- between AIR_DROP_DWELL_S and AIR_DROP_DWELL_S + 0.25 s. Zero for an unstamped
-- pair, and never negative (a stale stamp can only delay, never advance).
function FOURTH.ad_under(st)
	if st == nil or st.first == nil then return 0 end
	local n = tick_count - st.first
	if n < 0 then n = 0 end
	return (n * POLL_MS) / 1000
end

-- PURGE, WITH THE UNIT: every contact row that names this ui id goes - as the
-- caster (its whole slot) or as the enemy (that one row). Called from
-- drop_unit_by_ui_id, the ONE drop routine, so a dead unit can never leave a
-- stamp behind for a later re-contact to inherit.
function FOURTH.ad_purge_unit(id_text)
	local idt = tostring(id_text)
	FOURTH.ad_pair[idt] = nil
	for cid, per in pairs(FOURTH.ad_pair) do
		per[idt] = nil
		if next(per) == nil then FOURTH.ad_pair[cid] = nil end
	end
end

-- NO VALID PAIR AT ALL: every contact row this caster holds is stale (the enemy
-- died, fell to <= AIR_DROP_MIN_MEN models, or stopped answering its distance).
-- They are cleared WITHOUT firing - there is nothing under the drop to fire at -
-- and a later re-contact has to start a fresh dwell.
function FOURTH.ad_contact_clear(unit, marker)
	local ok_c, cid = pcall(function() return unit:unique_ui_id() end)
	if not ok_c or cid == nil then return end
	local idt = tostring(cid)
	local per = FOURTH.ad_pair[idt]
	if per == nil then return end
	local n = 0
	for _ in pairs(per) do n = n + 1 end
	FOURTH.ad_pair[idt] = nil
	if n > 0 then
		FOURTH.ad_event(unit, marker, "dwell cancelled: no valid pair any more ("
			.. tostring(n) .. " contact row(s) cleared)")
	end
end

'''

# ============================================================================
# 2. THE DECISION BLOCK OF ad_pick
# ============================================================================
OLD_TAIL_LIVE = '''\tlocal enemy, dist, men, etype = FOURTH.ad_nearest(unit)
\tif enemy == nil then return nil end
\tetype = etype or "enemy"
\tlocal edge_text = string.format("%.2f", dist)
\tlocal need = string.format("%.2f", FOURTH.AIR_DROP_EDGE_M)
\tif dist >= FOURTH.AIR_DROP_EDGE_M then
\t\tFOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
\t\t\t.. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m) -> NOT YET")
\t\treturn nil
\tend
\tFOURTH.ad_enemy = enemy
\tFOURTH.ad_caster_su = FOURTH.eg_fresh_caster_su(unit)
\t-- THE FIRING DECISION, on the same change gate as the NOT YET line: a pair
\t-- that is already firing repeats with identical numbers every 0.2 s, and the
\t-- ATTEMPT + re-check lines below are what mark each actual cast.
\tFOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
\t\t.. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m) -> FIRING"
\t\t.. " (the nearest of the valid enemies; unit_distance is edge-to-edge)")
\treturn "nearest valid '" .. etype .. "' has " .. tostring(men) .. " models and its EDGE gap is "
\t\t.. edge_text .. "m, under the " .. need .. "m line (unit_distance, edge-to-edge)"
end
'''

NEW_TAIL_LIVE = '''	local enemy, dist, men, etype = FOURTH.ad_nearest(unit)
	if enemy == nil then
		-- NO VALID PAIR AT ALL: every contact row this caster holds is stale.
		-- Cleared WITHOUT firing - nothing is under the drop to fire at.
		FOURTH.ad_contact_clear(unit, marker)
		return nil
	end
	etype = etype or "enemy"
	local edge_text = string.format("%.2f", dist)
	local need = string.format("%.2f", FOURTH.AIR_DROP_EDGE_M)
	local cid, eid = FOURTH.ad_pair_key(unit, enemy)
	if cid == nil then
		FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
			.. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m)"
			.. " -> HOLDING (the pair's ui ids are unreadable, so no dwell can be timed)")
		return nil
	end
	local per = FOURTH.ad_pair[cid]
	local st = nil
	if per ~= nil then st = per[eid] end
	local under = 0
	if dist >= FOURTH.AIR_DROP_EDGE_M then
		-- SEPARATION (or a pass that never touched the line). The dwell is over.
		if st == nil then
			FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
				.. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m) -> NOT YET")
			return nil
		end
		under = FOURTH.ad_under(st)
		FOURTH.ad_pair_drop(cid, eid)
		if under >= FOURTH.AIR_DROP_MIN_CONTACT_S then
			-- THE SHORT-CROSSING FALLBACK: the pair DID hold long enough to count,
			-- so the drop leaves NOW, on the separation evaluation, instead of
			-- being lost.
			FOURTH.ad_event(unit, marker, string.format(
				"short crossing: under for %.2fs (>= %.2fs) -> FIRING on separation"
				.. " (gap %.2fm, the dwell is %.2fs)",
				under, FOURTH.AIR_DROP_MIN_CONTACT_S, dist, FOURTH.AIR_DROP_DWELL_S))
		else
			-- CANCELLED, and the time actually under is the tuning datum.
			FOURTH.ad_event(unit, marker, string.format(
				"dwell cancelled: separated after %.2fs (gap %.2fm; the dwell is %.2fs"
				.. " and the short-crossing floor is %.2fs)",
				under, dist, FOURTH.AIR_DROP_DWELL_S, FOURTH.AIR_DROP_MIN_CONTACT_S))
			FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
				.. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m) -> NOT YET")
			return nil
		end
	else
		-- UNDER THE LINE: the dwell decides.
		if st == nil then
			FOURTH.ad_pair_stamp(cid, eid)
			FOURTH.ad_event(unit, marker, string.format(
				"dwell started: under at gap %.2fm, waiting %.2fs (pair '%s')",
				dist, FOURTH.AIR_DROP_DWELL_S, etype))
			return nil     -- THE FIRST EVALUATION OF A CONTACT NEVER FIRES
		end
		under = FOURTH.ad_under(st)
		if (under + 0.000001) >= FOURTH.AIR_DROP_DWELL_S then
			FOURTH.ad_event(unit, marker, string.format(
				"dwell satisfied after %.2fs -> FIRING (gap %.2fm, pair '%s')",
				under, dist, etype))
			-- the contact is CONSUMED: a repeat has to earn its own dwell
			FOURTH.ad_pair_drop(cid, eid)
		else
			FOURTH.ad_event(unit, marker, string.format(
				"dwell: under %.2fs of %.2fs (gap %.2fm)", under, FOURTH.AIR_DROP_DWELL_S, dist))
			return nil
		end
	end
	FOURTH.ad_enemy = enemy
	FOURTH.ad_caster_su = FOURTH.eg_fresh_caster_su(unit)
	-- THE DWELL EVIDENCE the pre-cast re-check re-verifies: how long the pair had
	-- really been under, and whether it fired on the fallback (in which case the
	-- gap at the re-check is over the line BY CONSTRUCTION).
	FOURTH.ad_fired = { under = under, fallback = (under < FOURTH.AIR_DROP_DWELL_S) }
	-- THE FIRING DECISION, on the same change gate as the NOT YET line: the
	-- ATTEMPT + re-check lines below are what mark each actual cast.
	FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
		.. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m) -> FIRING"
		.. " (the nearest of the valid enemies; unit_distance is edge-to-edge)")
	if under < FOURTH.AIR_DROP_DWELL_S then
		return "nearest valid '" .. etype .. "' has " .. tostring(men)
			.. " models; SHORT CROSSING - it held " .. string.format("%.2f", under)
			.. "s under the " .. need .. "m edge line and has separated to " .. edge_text
			.. "m (fallback floor " .. string.format("%.2f", FOURTH.AIR_DROP_MIN_CONTACT_S) .. "s)"
	end
	return "nearest valid '" .. etype .. "' has " .. tostring(men) .. " models, its EDGE gap is "
		.. edge_text .. "m - under the " .. need .. "m line for " .. string.format("%.2f", under)
		.. "s, so the dwell of " .. string.format("%.2f", FOURTH.AIR_DROP_DWELL_S) .. "s is satisfied"
end
'''

OLD_TAIL_ANN = '''\tlocal enemy, dist, men, etype = FOURTH.ad_nearest(unit)
\tif enemy == nil then return nil end
\tetype = etype or "enemy"
\tlocal edge_text = string.format("%.2f", dist)
\tlocal need = string.format("%.2f", FOURTH.AIR_DROP_EDGE_M)
\tif dist >= FOURTH.AIR_DROP_EDGE_M then
\t\tFOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
\t\t\t.. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m) -> NOT YET")
\t\treturn nil
\tend
\tFOURTH.ad_enemy = enemy
\tFOURTH.ad_caster_su = FOURTH.eg_fresh_caster_su(unit)
\treturn "nearest valid '" .. etype .. "' has " .. tostring(men) .. " models and its EDGE gap is "
\t\t.. edge_text .. "m, under the " .. need .. "m line (unit_distance, edge-to-edge)"
end
'''

NEW_TAIL_ANN = '''	local enemy, dist, men, etype = FOURTH.ad_nearest(unit)
	if enemy == nil then
		-- NO VALID PAIR AT ALL: every contact row this caster holds is stale.
		-- Cleared WITHOUT firing - nothing is under the drop to fire at.
		FOURTH.ad_contact_clear(unit, marker)
		return nil
	end
	etype = etype or "enemy"
	local edge_text = string.format("%.2f", dist)
	local need = string.format("%.2f", FOURTH.AIR_DROP_EDGE_M)
	local cid, eid = FOURTH.ad_pair_key(unit, enemy)
	if cid == nil then
		FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
			.. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m)"
			.. " -> HOLDING (the pair's ui ids are unreadable, so no dwell can be timed)")
		return nil
	end
	local per = FOURTH.ad_pair[cid]
	local st = nil
	if per ~= nil then st = per[eid] end
	local under = 0
	if dist >= FOURTH.AIR_DROP_EDGE_M then
		-- SEPARATION (or a pass that never touched the line). The dwell is over.
		if st == nil then
			FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
				.. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m) -> NOT YET")
			return nil
		end
		under = FOURTH.ad_under(st)
		FOURTH.ad_pair_drop(cid, eid)
		if under >= FOURTH.AIR_DROP_MIN_CONTACT_S then
			-- THE SHORT-CROSSING FALLBACK: the pair DID hold long enough to count,
			-- so the drop leaves NOW, on the separation evaluation, instead of
			-- being lost.
			FOURTH.ad_event(unit, marker, string.format(
				"short crossing: under for %.2fs (>= %.2fs) -> FIRING on separation"
				.. " (gap %.2fm, the dwell is %.2fs)",
				under, FOURTH.AIR_DROP_MIN_CONTACT_S, dist, FOURTH.AIR_DROP_DWELL_S))
		else
			-- CANCELLED, and the time actually under is the tuning datum.
			FOURTH.ad_event(unit, marker, string.format(
				"dwell cancelled: separated after %.2fs (gap %.2fm; the dwell is %.2fs"
				.. " and the short-crossing floor is %.2fs)",
				under, dist, FOURTH.AIR_DROP_DWELL_S, FOURTH.AIR_DROP_MIN_CONTACT_S))
			FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
				.. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m) -> NOT YET")
			return nil
		end
	else
		-- UNDER THE LINE: the dwell decides.
		if st == nil then
			FOURTH.ad_pair_stamp(cid, eid)
			FOURTH.ad_event(unit, marker, string.format(
				"dwell started: under at gap %.2fm, waiting %.2fs (pair '%s')",
				dist, FOURTH.AIR_DROP_DWELL_S, etype))
			return nil     -- THE FIRST EVALUATION OF A CONTACT NEVER FIRES
		end
		under = FOURTH.ad_under(st)
		if (under + 0.000001) >= FOURTH.AIR_DROP_DWELL_S then
			FOURTH.ad_event(unit, marker, string.format(
				"dwell satisfied after %.2fs -> FIRING (gap %.2fm, pair '%s')",
				under, dist, etype))
			-- the contact is CONSUMED: a repeat has to earn its own dwell
			FOURTH.ad_pair_drop(cid, eid)
		else
			FOURTH.ad_event(unit, marker, string.format(
				"dwell: under %.2fs of %.2fs (gap %.2fm)", under, FOURTH.AIR_DROP_DWELL_S, dist))
			return nil
		end
	end
	FOURTH.ad_enemy = enemy
	FOURTH.ad_caster_su = FOURTH.eg_fresh_caster_su(unit)
	-- THE DWELL EVIDENCE the pre-cast re-check re-verifies: how long the pair had
	-- really been under, and whether it fired on the fallback (in which case the
	-- gap at the re-check is over the line BY CONSTRUCTION).
	FOURTH.ad_fired = { under = under, fallback = (under < FOURTH.AIR_DROP_DWELL_S) }
	-- (annotated copy: the FIRING decision line is a log-only line that repeats
	-- the nearest enemy, its entity count and the exact edge on every cast)
	if under < FOURTH.AIR_DROP_DWELL_S then
		return "nearest valid '" .. etype .. "' has " .. tostring(men)
			.. " models; SHORT CROSSING - it held " .. string.format("%.2f", under)
			.. "s under the " .. need .. "m edge line and has separated to " .. edge_text
			.. "m (fallback floor " .. string.format("%.2f", FOURTH.AIR_DROP_MIN_CONTACT_S) .. "s)"
	end
	return "nearest valid '" .. etype .. "' has " .. tostring(men) .. " models, its EDGE gap is "
		.. edge_text .. "m - under the " .. need .. "m line for " .. string.format("%.2f", under)
		.. "s, so the dwell of " .. string.format("%.2f", FOURTH.AIR_DROP_DWELL_S) .. "s is satisfied"
end
'''

# ============================================================================
# 3. THE PRE-CAST RE-CHECK: re-verify the dwell and the gap
# ============================================================================
DWELL_RECHECK_LIVE = '''\t\tlocal men_text = ((ok_ea and type(ea) == "number") and tostring(ea) or "?")
\t\t-- ROUND 115: THE DWELL IS RE-VERIFIED HERE, from the evidence the
\t\t-- evaluator recorded at the decision - how long the pair had really been
\t\t-- under the line and whether it fired on the short-crossing fallback. A
\t\t-- dwell fire must have held AIR_DROP_DWELL_S; a fallback fire must have
\t\t-- held AIR_DROP_MIN_CONTACT_S. A FALLBACK FIRE HAPPENS ON THE SEPARATION
\t\t-- EVALUATION, so the gap at this re-check is at or over the line BY
\t\t-- CONSTRUCTION: the fallback is therefore exempt from the gap test, and
\t\t-- the measured gap is still written so the log shows what it really was.
\t\tlocal fired = FOURTH.ad_fired
\t\tlocal fallback_now = (fired ~= nil and fired.fallback == true)
\t\tlocal dwell_ok, dwell_text = true, "?"
\t\tif fired ~= nil and type(fired.under) == "number" then
\t\t\tlocal floor_s = FOURTH.AIR_DROP_DWELL_S
\t\t\tif fallback_now then floor_s = FOURTH.AIR_DROP_MIN_CONTACT_S end
\t\t\tdwell_ok = ((fired.under + 0.000001) >= floor_s)
\t\t\tdwell_text = string.format("%.2fs of %.2fs", fired.under, floor_s)
\t\tend
\t\tlocal gap_ok = (edge_ok or (fallback_now and dwell_ok))
'''

DWELL_RECHECK_ANN = '''\t\tlocal men_text = ((ok_ea and type(ea) == "number") and tostring(ea) or "?")
\t\t-- ROUND 115: the dwell is re-verified from the evidence the evaluator
\t\t-- recorded (how long the pair held, and whether it fired on the fallback).
\t\t-- A fallback fire happens ON the separation evaluation, so its gap is over
\t\t-- the line by construction and it is exempt from the gap test.
\t\tlocal fired = FOURTH.ad_fired
\t\tlocal fallback_now = (fired ~= nil and fired.fallback == true)
\t\tlocal dwell_ok, dwell_text = true, "?"
\t\tif fired ~= nil and type(fired.under) == "number" then
\t\t\tlocal floor_s = FOURTH.AIR_DROP_DWELL_S
\t\t\tif fallback_now then floor_s = FOURTH.AIR_DROP_MIN_CONTACT_S end
\t\t\tdwell_ok = ((fired.under + 0.000001) >= floor_s)
\t\t\tdwell_text = string.format("%.2fs of %.2fs", fired.under, floor_s)
\t\tend
\t\tlocal gap_ok = (edge_ok or (fallback_now and dwell_ok))
'''

# ============================================================================
# APPLY
# ============================================================================
def apply(path, ann):
    s = rd(path)
    tag = "ANN" if ann else "LIVE"

    # 1 constants
    s = must(s, "\nFOURTH.AIR_DROP_FAST_S = 0.2\nFOURTH.ad_note = {}\n",
             "\nFOURTH.AIR_DROP_FAST_S = 0.2\n" + (HEADER_ANN if ann else HEADER_LIVE)
             + "FOURTH.ad_note = {}\n")

    # 2 state tables
    s = must(s, "FOURTH.ad_fast_abilities = {}\n",
             "FOURTH.ad_fast_abilities = {}\n" + (STATE_ANN if ann else STATE_LIVE))

    # 3 helpers, inserted before the evaluator's own comment banner
    s = must(s, "-- THE AIR-DROP EVALUATOR. ONE comparison decides",
             (HELPERS_ANN if ann else HELPERS_LIVE) + "-- THE AIR-DROP EVALUATOR. ONE comparison decides")

    # 4 the decision block
    if ann:
        s = must(s, OLD_TAIL_ANN, NEW_TAIL_ANN)
    else:
        s = must(s, OLD_TAIL_LIVE, NEW_TAIL_LIVE)

    # 4b every decision starts with NO dwell evidence
    s = must(s, "function FOURTH.ad_pick(unit, routing)\n\tif routing then return nil end\n",
             "function FOURTH.ad_pick(unit, routing)\n"
             "\t-- ROUND 115: a fresh decision starts with NO dwell evidence; only the\n"
             "\t-- firing path below sets it, so a stale value can never reach a re-check.\n"
             "\tFOURTH.ad_fired = nil\n"
             "\tif routing then return nil end\n")

    # 5 the pre-cast re-check: the dwell evidence + the gap/dwell gates
    s = must(s, '\t\tlocal men_text = ((ok_ea and type(ea) == "number") and tostring(ea) or "?")\n\t\tif not (caster_alive and fly_readable and fly_now and melee_readable\n\t\t\tand (not melee_now) and enemy_alive and men_ok and edge_ok) then',
             (DWELL_RECHECK_ANN if ann else DWELL_RECHECK_LIVE)
             + '\t\tif not (caster_alive and fly_readable and fly_now and melee_readable\n\t\t\tand (not melee_now) and enemy_alive and men_ok and gap_ok and dwell_ok) then')

    if not ann:
        # the skip line names the dwell evidence too
        s = must(s, '\t\t\t\t.. " over_min_men=" .. tostring(men_ok) .. " edge_ok=" .. tostring(edge_ok)\n',
                 '\t\t\t\t.. " over_min_men=" .. tostring(men_ok) .. " edge_ok=" .. tostring(edge_ok)\n'
                 '\t\t\t\t.. " gap_ok=" .. tostring(gap_ok) .. " dwell=" .. dwell_text\n'
                 '\t\t\t\t.. " dwell_ok=" .. tostring(dwell_ok) .. " short_cross=" .. tostring(fallback_now)\n')
        # and the firing line states the dwell it re-verified
        s = must(s, '\t\t\t.. string.format("%.2f", FOURTH.AIR_DROP_EDGE_M) .. "m) -> FIRING (re-checked)")\n',
                 '\t\t\t.. string.format("%.2f", FOURTH.AIR_DROP_EDGE_M) .. "m) -> FIRING (re-checked)"\n'
                 '\t\t\t.. (fallback_now and (" (short crossing: held " .. dwell_text .. ")") or (" (dwell " .. dwell_text .. ")")))\n')

    # 6 the purge hook, in the ONE drop routine. NOTE: drop_unit_by_ui_id is
    # declared ABOVE the `local FOURTH = {` bag (chunk order) and the chunk is
    # at Lua's 200-local ceiling, so the routine cannot name FOURTH at all. It
    # reaches the purge through ONE named global, set beside ad_purge_unit
    # (edit 9 below): explicit, greppable, and it touches no table.
    s = must(s, "\tlocal id_text = tostring(ui_id)\n\tlocal id_slot = unit_slot(ui_id)\n\tgone_units[id_text] = true",
             "\tlocal id_text = tostring(ui_id)\n\tlocal id_slot = unit_slot(ui_id)\n"
             "\t-- ROUND 115: the pair's dwell row dies WITH the unit (caster OR enemy),\n"
             "\t-- through the ONE named global set beside ad_purge_unit below: this\n"
             "\t-- chunk is at Lua's local ceiling, so the routine cannot name FOURTH.\n"
             "\tif zz_ad_dwell_purge ~= nil then zz_ad_dwell_purge(id_text) end\n"
             "\tgone_units[id_text] = true")

    # 9 attach the purge hook ONCE, immediately after the dwell helpers and
    # before the evaluator banner, so it is defined before any evaluation runs
    s = must(s, "\n-- THE AIR-DROP EVALUATOR. ONE comparison decides",
             "\n-- THE PURGE HOOK: drop_unit_by_ui_id is defined ABOVE the FOURTH bag\n"
             "-- (chunk order) and this chunk is at Lua's local ceiling, so it cannot\n"
             "-- name FOURTH at all; the hook is THIS ONE named global.\n"
             "zz_ad_dwell_purge = FOURTH.ad_purge_unit\n"
             "\n-- THE AIR-DROP EVALUATOR. ONE comparison decides")

    # 8 the tooltip states the dwell
    s = must(s,
             "air_drop_on_infantry = \"When armed, fires when the nearest enemy unit with more than 10 models is within 0.1 m of this unit's edge, airborne where the ability requires it\",",
             "air_drop_on_infantry = \"When armed, fires when the nearest enemy unit with more than 10 models stays within 0.1 m of this unit's edge for 1 second, airborne where the ability requires it\",")

    wr(path, s)
    print("edited %-3s %s (%d bytes)" % (tag, path, len(s.encode("utf-8"))))


apply(LIVE, False)
apply(ANN, True)
