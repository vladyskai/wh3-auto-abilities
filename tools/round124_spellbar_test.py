#!/usr/bin/env python3
"""Round 124 (harness 123): THE SPELL-BAR BADGE TEST, applied identically to the
live source and the annotated copy.

The user's report (2026-10-28 field test): on a Rune Smith carrying runes, the
Hammer of Karak Drazh badge showed 'M' and 'A' on top of each other. The log
proved why: each rune's button sits on the SPELL bar (button_spell, button_spell2,
...), each alone under its own parent, so bar_ordinal_for() answered 1 for every
rune and all five rune badges were placed on WHEEL SLOT 1, the Hammer's slot.

The user's request (2026-11-01): test whether the letter can be put on the
right-hand bar (spells and runes), isolated from everything else.

The change, and nothing else:
  * FOURTH.SPELLBAR_BADGES = true (the test switch; false = the old behaviour).
  * A claimed button whose Id() reads 'button_spell...' is recorded as a
    SPELL-BAR button (FOURTH.spellbar_id[marker]); its badge does NOT get a
    wheel slot. Its offset is derived from that button's OWN live Position(),
    with the same formula the wheel slots use:
        BADGE_X + (x - WHEEL_TOP_X), BADGE_Y + (y - WHEEL_TOP_Y)
    (the six wheel slots ARE the visible wheel buttons' Position() values), so
    the badge lands on the button if Position() reports the drawn spot. If the
    position cannot be read, the badge takes its fallback offset (logged).
  * A read-only SPELLBAR line per spell-bar ability, in the once-a-second
    inventory sweep: the button's id, visibility, Position, RelativePosition,
    its parent's id and Position, and the offset applied. If the badge lands in
    the wrong place, these numbers are what the next round calibrates from.
Every wheel button follows exactly the old path. The Id() read is the one the
claim walk already logs; an Id() that is not a plain string keeps the old path.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

E1_ANCHOR = "local function badge_offsets_for(marker)\n"
E1_BEFORE = """-- ============================================================================
-- ROUND 124 (TEST): SPELL-BAR BADGES. A Rune Smith's runes (and any ability the
-- game puts on the right-hand SPELL bar) are claimed on 'button_spell',
-- 'button_spell2', ... Each sits alone under its own parent, so the bar ordinal
-- above answered 1 for all of them and every one of those badges landed on WHEEL
-- SLOT 1, on top of the real slot-1 ability (the Hammer of Karak Drazh 'M'+'A'
-- overlap, field test 2026-10-28). With the switch on, a spell-bar button gets
-- NO wheel slot: its badge offset comes from the button's OWN live Position(),
-- through the same formula the wheel slots use (the six slots are the visible
-- wheel buttons' Position() values). FOURTH.SPELLBAR_BADGES = false restores the
-- old behaviour exactly. spellbar_id[marker] = the claimed button's id when it is
-- a spell-bar button, nil otherwise.
-- ============================================================================
FOURTH.SPELLBAR_BADGES = true
FOURTH.spellbar_id = {}

"""

E2_OLD = """local function badge_offsets_for(marker)
	local ability = ability_for(marker)
	if ability == nil then return nil end
"""
E2_NEW = """local function badge_offsets_for(marker)
	local ability = ability_for(marker)
	if ability == nil then return nil end
	-- ROUND 124 (TEST): a spell-bar button's badge follows the button's own
	-- screen position; 'spell' in the third value tells the callers to log it so.
	if FOURTH.SPELLBAR_BADGES and FOURTH.spellbar_id[marker] ~= nil then
		local st = ability_state[marker]
		if st ~= nil and st.button ~= nil then
			local ok_p, px, py = pcall(function() return st.button:Position() end)
			if ok_p and type(px) == "number" and type(py) == "number" then
				return BADGE_X + (px - WHEEL_TOP_X), BADGE_Y + (py - WHEEL_TOP_Y), "spell", px, py
			end
		end
		return BADGE_X + ability.ox, BADGE_Y + ability.oy, nil, nil, nil
	end
"""

E3_OLD = """		if wheel ~= nil then
			log("badge " .. marker .. ": placed bottom-centre of '" .. tostring(ok_pid and pid2 or "?")
"""
E3_NEW = """		if wheel == "spell" then
			log("badge " .. marker .. ": placed bottom-centre of '" .. tostring(ok_pid and pid2 or "?")
				.. "' (offset " .. tostring(ox) .. "," .. tostring(oy) .. ") [SPELL-BAR button '"
				.. tostring(FOURTH.spellbar_id[marker]) .. "' at (" .. tostring(sx) .. "," .. tostring(sy)
				.. ")] ok=true")
		elseif wheel ~= nil then
			log("badge " .. marker .. ": placed bottom-centre of '" .. tostring(ok_pid and pid2 or "?")
"""

E4_OLD = """	if wheel ~= nil then
		log("badge " .. marker .. ": placed bottom-centre of '" .. tostring(badge_parent:Id())
"""
E4_NEW = """	if wheel == "spell" then
		log("badge " .. marker .. ": placed bottom-centre of '" .. tostring(badge_parent:Id())
			.. "' (offset " .. tostring(ox) .. "," .. tostring(oy) .. ") [SPELL-BAR button '"
			.. tostring(FOURTH.spellbar_id[marker]) .. "' at (" .. tostring(sx) .. "," .. tostring(sy)
			.. ")] ok=" .. tostring(ok_o))
	elseif wheel ~= nil then
		log("badge " .. marker .. ": placed bottom-centre of '" .. tostring(badge_parent:Id())
"""

E5_OLD = """				local k = bar_ordinal_for(uic, ability)
				if k ~= nil and k >= 1 and k <= 6 then
"""
E5_NEW = """				-- ROUND 124 (TEST): a SPELL-BAR button ('button_spell...') gets no
				-- wheel slot - its badge follows the button's own position (see
				-- badge_offsets_for). Only a plain-string Id() can say so; anything
				-- else keeps the wheel path below, exactly as before.
				local spell_id = nil
				if FOURTH.SPELLBAR_BADGES and ok_id and type(id) == "string"
					and string.sub(id, 1, 12) == "button_spell" then
					spell_id = id
				end
				FOURTH.spellbar_id[ability.marker] = spell_id
				local k = nil
				if spell_id == nil then k = bar_ordinal_for(uic, ability) end
				if spell_id ~= nil then
					slot_index[ability.marker] = nil
					log("claim: " .. ability.marker .. " is a SPELL-BAR button ('" .. spell_id
						.. "') - its badge follows that button's own screen position (round 124 test), not a wheel slot")
				elseif k ~= nil and k >= 1 and k <= 6 then
"""

E6_OLD = """	log(inv_line("zz_auto_badge", found["zz_auto_badge"]))
	log(inv_line("zz_auto_badge_fs", found["zz_auto_badge_fs"]))
end
"""
E6_NEW = """	log(inv_line("zz_auto_badge", found["zz_auto_badge"]))
	log(inv_line("zz_auto_badge_fs", found["zz_auto_badge_fs"]))
	-- ROUND 124 (TEST): one READ-ONLY SPELLBAR line per ability claimed on a
	-- spell-bar button - where the engine says that button and its parent are,
	-- and the offset its badge was given. If the badge lands in the wrong place,
	-- these are the numbers the next round calibrates from.
	for _, ability in ipairs(ABILITIES) do
		local sid = FOURTH.spellbar_id[ability.marker]
		local st = ability_state[ability.marker]
		if sid ~= nil and st ~= nil and st.button ~= nil then
			local vis = "?"
			local ok_v, v = pcall(function() return st.button:Visible(true) end)
			if ok_v and type(v) == "boolean" then vis = v and "true" or "false" end
			local px, py = read_xy(st.button)
			local rx, ry = inv_rel_xy(st.button)
			local pid, ppx, ppy = "?", nil, nil
			local ok_p, par = pcall(function() return UIComponent(st.button:Parent()) end)
			if ok_p and par ~= nil then
				pid = inv_id_of(par) or "?"
				ppx, ppy = read_xy(par)
			end
			log("SPELLBAR " .. ability.marker .. ": button='" .. sid .. "' visible=" .. vis
				.. " pos=" .. fmt_xy(px, py) .. " relpos=" .. fmt_xy(rx, ry)
				.. " parent='" .. pid .. "' parent_pos=" .. fmt_xy(ppx, ppy)
				.. " badge_offset=" .. fmt_xy(st.applied_ox, st.applied_oy))
		end
	end
end
"""

# THE ANNOTATED COPY is the log-free reading copy (harness 94's 0r pins it: no
# log( and no string.find), with a simplified claim walk that never reads Id().
# It gets the same switch, the same offset logic, and its own claim edit that
# reads Id() itself; the three logging edits (E3, E4, E6) have no counterpart.
E5A_OLD = """			-- The wheel slot this button sits on, for its badge offset.
			local k = bar_ordinal_for(uic, ability)
			if k ~= nil and k >= 1 and k <= 6 then
"""
E5A_NEW = """			-- ROUND 124 (TEST): a SPELL-BAR button ('button_spell...') gets no
			-- wheel slot; its badge follows the button's own position instead.
			local ok_id, id = pcall(function() return uic:Id() end)
			local spell_id = nil
			if FOURTH.SPELLBAR_BADGES and ok_id and type(id) == "string"
				and string.sub(id, 1, 12) == "button_spell" then
				spell_id = id
			end
			FOURTH.spellbar_id[ability.marker] = spell_id

			-- The wheel slot this button sits on, for its badge offset.
			local k = nil
			if spell_id == nil then k = bar_ordinal_for(uic, ability) end
			if spell_id ~= nil then
				slot_index[ability.marker] = nil -- no wheel slot: the spell bar
			elseif k ~= nil and k >= 1 and k <= 6 then
"""

PLAN = {
    SRC: [(E1_ANCHOR, E1_BEFORE + E1_ANCHOR), (E2_OLD, E2_NEW), (E3_OLD, E3_NEW),
          (E4_OLD, E4_NEW), (E5_OLD, E5_NEW), (E6_OLD, E6_NEW)],
    ANN: [(E1_ANCHOR, E1_BEFORE + E1_ANCHOR), (E2_OLD, E2_NEW), (E5A_OLD, E5A_NEW)],
}

for path, edits in PLAN.items():
    s = open(path, encoding="utf-8", newline="").read()
    assert "\r\n" not in s, path
    if "FOURTH.SPELLBAR_BADGES = true" in s:
        # already applied (the live source took its edits on the first run):
        # prove every replacement text is present exactly once, then skip.
        for i, (_, b) in enumerate(edits, 1):
            assert s.count(b) == 1, (path.split("\\")[-1], "edit", i, "not present exactly once")
        print("already applied, verified:", path.split("\\")[-1])
        continue
    for i, (a, b) in enumerate(edits, 1):
        n = s.count(a)
        assert n == 1, (path.split("\\")[-1], "edit", i, "anchor count", n)
        s = s.replace(a, b, 1)
    assert "\u2014" not in "".join(b for _, b in edits)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("applied %d edits:" % len(edits), path.split("\\")[-1])
