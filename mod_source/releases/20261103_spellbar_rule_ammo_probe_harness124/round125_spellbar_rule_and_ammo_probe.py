#!/usr/bin/env python3
"""Round 125 (harness 124): the spell-bar rule and the read-only ammo probe.

Starts from docs/backups/round124/pre124_*.lua (= the round-123 shipped source,
md5 4f9e0d31...), so the round-124 TEST code (the spell-bar badge placement and its
SPELLBAR sweep lines) is REMOVED, not left behind a switch. Then two changes,
applied to the live source and the annotated (log-free) copy:

(A) THE SPELL-BAR RULE. User ruling 2026-11-03, verbatim in the round doc: whatever
    is on the right-hand bar (spells, and runes now that we know they sit there)
    gets no letter and no trigger; an ability on the left-hand wheel stays ours,
    including a rune that appears there (item- or ability-granted). A button whose
    Id() reads 'button_spell...' is NEVER claimed: no badge, so it can never be
    armed, so it never fires. The same key on a wheel button is claimed as before.
    The live file logs the skip ONCE per ability per battle.

(B) THE AMMO PROBE (read-only; nothing is cast from it). Per poll, per player unit
    that started with ammunition: ammo_left() drop -> FIRING ON; no drop for longer
    than 1.25 x the unit's own measured gap between volleys (a default window
    before that) -> FIRING OFF; a rise is a resupply. Every change is logged with
    the unit's target and whether that target is in melee.
"""
import shutil

BASE_SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round124\pre124_zz_test_deadly_onslaught.lua"
BASE_ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round124\pre124_annotated.lua"
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

# ---------------------------------------------------------------- (A) spell bar
A1_ANCHOR = "local function scan_component_body(uic)\n"
A1_BEFORE = """-- ============================================================================
-- ROUND 125 - THE RIGHT-HAND SPELL BAR IS LEFT TO THE PLAYER (user ruling
-- 2026-11-03). The left-hand ability wheel is the mod's job; the right-hand
-- bar - spells, and the runes a Rune Smith carries, which the game also puts
-- there - gets no letter and no trigger. A button whose Id() reads
-- 'button_spell...' is therefore never claimed: no badge is built, the ability
-- can never be armed, so it never fires. The same key on a WHEEL button (a rune
-- granted by an item or an active ability) is claimed exactly as before. The
-- round-124 spell-bar badge placement (a field-tested success, but activating
-- one rune locks the others, so automating them makes little sense) is gone.
-- spell_bar_noted[marker] = true once the skip has been reported this battle.
-- ============================================================================
FOURTH.spell_bar_noted = {}

"""

A2_OLD_SRC = """		local claimed = nil
		for _, ability in ipairs(ABILITIES) do
			local state = ability_state[ability.marker]
			if state.button == nil and key_is_ours(ability, key) then
"""
A2_NEW_SRC = """		-- ROUND 125: a button on the right-hand SPELL bar is never claimed (see
		-- the banner above scan_component_body). Only a plain-string Id() can say
		-- so; anything else is judged by its key alone, exactly as before.
		local on_spell_bar = (ok_id and type(id) == "string" and string.sub(id, 1, 12) == "button_spell")
		if on_spell_bar then
			for _, ability in ipairs(ABILITIES) do
				if FOURTH.spell_bar_noted[ability.marker] == nil and key_is_ours(ability, key) then
					FOURTH.spell_bar_noted[ability.marker] = true
					log("scan: " .. ability.marker .. " is on the right-hand SPELL bar ('" .. id
						.. "') - not claimed: no badge, no trigger (user rule 2026-11-03)")
				end
			end
		end
		local claimed = nil
		for _, ability in ipairs(ABILITIES) do
			local state = ability_state[ability.marker]
			if state.button == nil and not on_spell_bar and key_is_ours(ability, key) then
"""

A2_OLD_ANN = """	-- One claim per ability; the judgement is the key alone (no id check,
	-- no liveness gate).
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		if state.button == nil and key_is_ours(ability, key) then
"""
A2_NEW_ANN = """	-- ROUND 125: a button on the right-hand SPELL bar ('button_spell...') is
	-- never claimed - no badge, no trigger (user rule 2026-11-03).
	local ok_id, id = pcall(function() return uic:Id() end)
	local on_spell_bar = (ok_id and type(id) == "string" and string.sub(id, 1, 12) == "button_spell")

	-- One claim per ability; the judgement is the key alone (no id check,
	-- no liveness gate) - on the left-hand wheel only.
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		if state.button == nil and not on_spell_bar and key_is_ours(ability, key) then
"""

# ---------------------------------------------------------------- (B) ammo probe
B1_ANCHOR = "local function poll_body()\n"
B1_HEAD = """-- ============================================================================
-- ROUND 125 - THE AMMO PROBE (READ-ONLY: nothing is cast from it).
-- The user's design (proposed 2026-10-28, approved 2026-11-01): the battle API
-- has no "this unit is shooting" read, but ammo_left() - "the remaining
-- ammunition count of this unit" - drops when the unit fires. Every poll
-- (250 ms) the probe reads ammo_left() for each of the player's units that
-- started the battle with ammunition, and keeps ONE firing flag per unit:
--   * ON  on the first poll whose count is LOWER than the poll before;
--   * OFF once no drop has been seen for longer than the unit's window:
--     AMMO_WINDOW_FACTOR (1.25) x the unit's own measured gap between two
--     volleys (read live, no baked reload stat), or AMMO_WINDOW_DEFAULT_S
--     before such a gap has been measured. Drops less than AMMO_SAME_VOLLEY_S
--     apart are one volley (models fire a fraction of a second apart), so
--     they never set the gap;
--   * a count that goes UP is a resupply: logged, never a shot.
-- The first volley can never be anticipated: the flag rises on the poll after
-- the ammunition is spent. Units with no ammunition (starting_ammo() 0, or
-- unreadable) are read ONCE and never again.
-- ============================================================================
FOURTH.AMMO_WINDOW_DEFAULT_S = 10     -- TEST VALUE (the user's to set): the window before a gap is measured
FOURTH.AMMO_WINDOW_FACTOR = 1.25      -- the window is 1.25 x the unit's own measured gap between volleys
FOURTH.AMMO_SAME_VOLLEY_S = 1.0       -- TEST VALUE: drops closer than this are one volley, not a reload gap
FOURTH.ammo = setmetatable({}, { __mode = "k" })   -- per tracked entry: start, last, last_drop_s, gap_s, firing

"""

B1_DESCRIBE_SRC = """-- One unit's description for an AMMO / FIRING line: ui id, type, and its
-- current target with that target's melee state (every read pcall'd).
function FOURTH.ammo_describe(u)
	local id, ty = "?", "?"
	pcall(function() id = tostring(u:unique_ui_id()) end)
	pcall(function() ty = tostring(u:type()) end)
	local tgt, tmelee = "none", "?"
	local ok_t, t = pcall(function() return u:current_target() end)
	if ok_t and t ~= nil then
		tgt = "?"
		pcall(function() tgt = tostring(t:type()) end)
		local ok_m, m = pcall(function() return t:is_in_melee() end)
		if ok_m and type(m) == "boolean" then tmelee = m and "true" or "false" end
	end
	return "unit " .. id .. " '" .. ty .. "'", "target='" .. tgt .. "' target_in_melee=" .. tmelee
end

"""

PROBE_BODY = """function FOURTH.ammo_probe(units)
	if units == nil then return end
	local now_s = tick_count * POLL_MS / 1000
	for i = 1, #units do
		local su = units[i]
		local u = su and su.unit
		if u ~= nil then
			local st = FOURTH.ammo[su]
			if st == nil then
				local ok_s, start = pcall(function() return u:starting_ammo() end)
				st = { start = (ok_s and type(start) == "number") and start or 0, firing = false }
				FOURTH.ammo[su] = st
			end
			if st.start > 0 then
				local ok_a, now = pcall(function() return u:ammo_left() end)
				if ok_a and type(now) == "number" then
					if st.last ~= nil and now < st.last then
						local gap = (st.last_drop_s ~= nil) and (now_s - st.last_drop_s) or nil
						if st.firing and gap ~= nil and gap >= FOURTH.AMMO_SAME_VOLLEY_S then
							st.gap_s = gap
						end
						local was_firing = st.firing
						st.firing = true
						st.last_drop_s = now_s
%%DROP_LOG%%
					elseif st.last ~= nil and now > st.last then
%%RISE_LOG%%
					end
					st.last = now
				end
				if st.firing then
					local window = (st.gap_s ~= nil) and (FOURTH.AMMO_WINDOW_FACTOR * st.gap_s)
						or FOURTH.AMMO_WINDOW_DEFAULT_S
					if (now_s - st.last_drop_s) > window then
						st.firing = false
%%OFF_LOG%%
					end
				end
			end
		end
	end
end

"""
DROP_LOG = """						local who, aim = FOURTH.ammo_describe(u)
						log(string.format("AMMO %s: %s -> %s of %s at t=%.2fs (gap %s, window %s) %s",
							who, tostring(st.last), tostring(now), tostring(st.start), now_s,
							gap and string.format("%.2fs", gap) or "-",
							st.gap_s and string.format("%.2fs measured", FOURTH.AMMO_WINDOW_FACTOR * st.gap_s)
								or string.format("%.0fs default", FOURTH.AMMO_WINDOW_DEFAULT_S),
							aim))
						if not was_firing then
							log("FIRING ON " .. who .. " at t=" .. string.format("%.2f", now_s) .. "s " .. aim)
						end"""
RISE_LOG = """						local who = FOURTH.ammo_describe(u)
						log("AMMO " .. who .. ": " .. tostring(st.last) .. " -> " .. tostring(now)
							.. " of " .. tostring(st.start) .. " - RESUPPLIED (not a shot)")"""
OFF_LOG = """						local who = FOURTH.ammo_describe(u)
						log("FIRING OFF " .. who .. " at t=" .. string.format("%.2f", now_s)
							.. "s (no drop for " .. string.format("%.2f", now_s - st.last_drop_s)
							.. "s > window " .. string.format("%.2f", window) .. "s)")"""

PROBE_SRC = (PROBE_BODY.replace("%%DROP_LOG%%", DROP_LOG).replace("%%RISE_LOG%%", RISE_LOG)
             .replace("%%OFF_LOG%%", OFF_LOG))
PROBE_ANN = (PROBE_BODY.replace("%%DROP_LOG%%\n", "").replace("%%RISE_LOG%%\n", "")
             .replace("%%OFF_LOG%%\n", "")
             .replace("\t\t\t\t\t\tlocal was_firing = st.firing\n", "")
             .replace("\t\t\t\t\telseif st.last ~= nil and now > st.last then\n", ""))

B2_OLD = """	local active_refresh_pending = false

	for i = 1, #tracked_units do
		local script_unit = tracked_units[i]
"""
B2_NEW = """	local active_refresh_pending = false

	-- ROUND 125: the read-only ammo probe (above poll_body) - its own pcall, so
	-- nothing it meets can cost the army its tick.
	pcall(FOURTH.ammo_probe, tracked_units)

	for i = 1, #tracked_units do
		local script_unit = tracked_units[i]
"""

PLAN = {
    SRC: (BASE_SRC, [(A1_ANCHOR, A1_BEFORE + A1_ANCHOR), (A2_OLD_SRC, A2_NEW_SRC),
                     (B1_ANCHOR, B1_HEAD + B1_DESCRIBE_SRC + PROBE_SRC + B1_ANCHOR), (B2_OLD, B2_NEW)]),
    ANN: (BASE_ANN, [(A1_ANCHOR, A1_BEFORE + A1_ANCHOR), (A2_OLD_ANN, A2_NEW_ANN),
                     (B1_ANCHOR, B1_HEAD + PROBE_ANN + B1_ANCHOR), (B2_OLD, B2_NEW)]),
}

for dst, (base, edits) in PLAN.items():
    s = open(base, encoding="utf-8", newline="").read()
    assert "\r\n" not in s and "SPELLBAR_BADGES" not in s, base
    for i, (a, b) in enumerate(edits, 1):
        n = s.count(a)
        assert n == 1, (dst.split("\\")[-1], "edit", i, "anchor count", n)
        s = s.replace(a, b, 1)
    assert "\u2014" not in "".join(b for _, b in edits)
    if dst == ANN:
        assert "log(" not in PROBE_ANN and "log(" not in A2_NEW_ANN
    open(dst, "w", encoding="utf-8", newline="").write(s)
    print("wrote %s from %s (%d edits)" % (dst.split("\\")[-1], base.split("\\")[-1], len(edits)))
