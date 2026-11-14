#!/usr/bin/env python3
"""Round 151 (harness 150): large first + hold for the prefer-central blob attacks, the game's usage rules, breaths
prefer 90 degrees, 432 abilities start armed, and the ALL badge.

User rulings 2026-11-14:
  * "Large first, but also include a hold when there is a valuable large unit in the battlefield (not only in range).
    Also, all abilities with tags prefer_central_targets should consider using this rule." + valuable = "Worth more
    than infantry": the 53 prefer-central blob attacks fire first at a safe visible large enemy in range (the one losing
    the most value: all shots hit it, damage after armour vs its hit points x its live value); with none in range they
    hold while a visible large enemy anywhere would lose more value than the best infantry target now.
  * the game's own usage rules for the blob attacks: grounded (12: the caster must be flying), engaged_in_melee (26).
  * breaths (20): "Prefer 90 now" - among targets within 20% of the best value, the one whose side faces the breath.
  * defaults: the 21 when_ready + the melee/charge self-casts + protection & last stand + morale saves + heals + ammo
    refills start ARMED (432 entries); a badge click still switches each off.
  * "ALL badge per unit": one extra badge left of the wheel; a click arms every ability of ours on the selected
    unit(s), or disarms them all when every one is already armed.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_blob_tables as GB  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
DEFAULT_ON = ["when_ready",
              "melee_unwavering", "charge_or_melee", "charge_only", "charge", "melee", "melee_health75",
              "melee_skip_commanders", "glorious_death",
              "under_fire", "melee_or_under_fire", "self_last_stand",
              "wavering_self", "wavering_aura", "wavering_self_or_ally", "wavering_ally_range", "ally_wavering",
              "melee_or_wavering_aura",
              "ushoran_health", "health_below_15", "health_aura_self", "health_aura_self_undead", "health_aura_ally",
              "ally_heal", "health_aura_ground",
              "ally_ammo_low", "self_out_of_ammo"]


def sub(s, a, b):
    assert s.count(a) == 1, (a[:90], s.count(a))
    return s.replace(a, b)


def cut(s, start, end, new):
    a = s.index(start)
    b = s.index(end, a)
    assert s.count(start) == 1
    return s[:a] + new + s[b:]


# ---- the blob map: large enemies too -------------------------------------------------------------------------------
MAP_OLD = '''					local ok_v, vis = pcall(function() return e:is_visible_to_alliance(alliance) end)
					local ok_f, fly = pcall(function() return e:is_currently_flying() end)
					if ok_v and vis == true and not (ok_f and fly == true) then
						local s = FOURTH.blob_shape(e)
						if s ~= nil and s.inf and s.men >= FOURTH.BLOB_MIN_MEN then m.enemies[#m.enemies + 1] = s end
					end
'''
MAP_NEW = '''					local ok_v, vis = pcall(function() return e:is_visible_to_alliance(alliance) end)
					local ok_f, fly = pcall(function() return e:is_currently_flying() end)
					if ok_v and vis == true then
						local s = FOURTH.blob_shape(e)
						if s ~= nil and s.inf and s.men >= FOURTH.BLOB_MIN_MEN and not (ok_f and fly == true) then
							m.enemies[#m.enemies + 1] = s
						elseif s ~= nil and s.t ~= nil and FOURTH.class_keys.large[s.t] == true then
							-- ROUND 151: the LARGE enemies (flying ones too), for the prefer-central attacks
							local ok_h, hf = pcall(function() return e:unary_hitpoints() end)
							if ok_h and type(hf) == "number" then s.hp_frac = hf end
							local ok_i, m0 = pcall(function() return e:initial_number_of_men() end)
							if ok_i and type(m0) == "number" and m0 > 0 then s.men0 = m0 end
							local ok_s, sv = pcall(function() return e:strategic_value() end)
							if ok_s and type(sv) == "number" then s.sv = sv end
							m.large[#m.large + 1] = s
						end
					end
'''
M_OLD = "\tlocal m = { ours = {}, enemies = {}, alliance = (alliance ~= nil) }\n"
M_NEW = "\tlocal m = { ours = {}, enemies = {}, large = {}, alliance = (alliance ~= nil) }\n"

AP_OLD = '''function FOURTH.blob_ap_ok(e, dmg)
	if dmg == nil or dmg[3] ~= 1 then return true end
	local def = e.t and FOURTH.UNIT_DEF[e.t]
'''
AP_NEW = '''function FOURTH.blob_ap_ok(e, dmg)
	if dmg == nil or dmg[3] ~= 1 then return true end
	local def = e.t and (FOURTH.UNIT_DEF[e.t] or FOURTH.LARGE_DEF[e.t])   -- ROUND 151: large targets too
'''

PICK_START = "-- the best safe target for this caster: shape, soldiers, units, friendly gap, value; nil when none passes. A candidate\n"
PICK_END = "-- standing still: is_moving() must read exactly false"
PICK_NEW = '''-- the best safe target for this caster: shape, soldiers, units, friendly gap, value; nil when none passes. A candidate
-- must be allowed (armour rule), safe, and reach the density line on its own; the most value destroyed wins.
-- ROUND 151 (user ruling 2026-11-14, breaths: "Prefer 90 now"): a BREATH takes, among the candidates within
-- BREATH_VALUE_BAND of the best value, the one whose side faces it - the line of fire closest to 90 degrees off the
-- target's facing (its front runs along the breath).
FOURTH.BREATH_VALUE_BAND = 0.8   -- user ruling 2026-11-14: "within 20% of the best value"
function FOURTH.blob_pick(unit, m, r, key)
	local reach = r + FOURTH.BLOB_MARGIN_M
	local need = FOURTH.blob_need(r)
	local dmg = key and FOURTH.BLOB_DMG[key]
	local cands, bv = {}, nil
	for i = 1, #m.enemies do
		local e = m.enemies[i]
		if FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit) and FOURTH.blob_ap_ok(e, dmg) then
			local g = FOURTH.blob_friend_gap(e, m, reach)
			if g == nil or g > reach then
				local sc, un = FOURTH.blob_score(e, m, r)
				if sc >= need then
					local v = FOURTH.blob_value(e, m, r, dmg)
					cands[#cands + 1] = { e, sc, un, g, v }
					if bv == nil or v > bv then bv = v end
				end
			end
		end
	end
	if bv == nil then return nil end
	local shot = key and FOURTH.BLOB_SHOT[key]
	local cx, cz = nil, nil
	if shot ~= nil and shot[6] == 1 then
		pcall(function()
			local p = unit:position()
			cx, cz = p:get_x(), p:get_z()
		end)
	end
	local best, bcos = nil, nil
	for i = 1, #cands do
		local c = cands[i]
		if cx ~= nil then
			if c[5] >= FOURTH.BREATH_VALUE_BAND * bv then
				local dx, dz = c[1].x - cx, c[1].z - cz
				local len = math.sqrt(dx * dx + dz * dz)
				local cs = 1
				if len > 0 then cs = math.abs((dx * c[1].fx + dz * c[1].fz) / len) end
				if best == nil or cs < bcos or (cs == bcos and c[5] > best[5]) then best, bcos = c, cs end
			end
		elseif best == nil or c[5] > best[5] or (c[5] == best[5] and c[2] > best[2]) then
			best = c
		end
	end
	return best[1], best[2], best[3], best[4], best[5]
end

-- ROUND 151: the value a cast takes from a LARGE target (all its shots hit it: projectile and blast damage after
-- armour, bonus vs large included, against the unit's current hit points, times its live value); nil when unknown
function FOURTH.blob_large_value(e, key)
	local shot = key and FOURTH.BLOB_SHOT[key]
	local dmg = key and FOURTH.BLOB_DMG[key]
	local def = e.t and FOURTH.LARGE_DEF[e.t]
	if shot == nil or dmg == nil or def == nil or e.sv == nil or e.sv <= 0 then return nil end
	local af = 1 - FOURTH.ARMOUR_TAKES * math.min(def[1], 100)
	local per = (shot[2] + shot[4]) * af + shot[3] + dmg[1] * af + dmg[2]
	local men0 = e.men0 or e.men
	local cur = def[2] * men0 * (e.hp_frac or (e.men / men0))
	if cur <= 0 then return nil end
	return e.sv * math.min(1, shot[1] * per / cur)
end

-- ROUND 151: the best safe large target in range (allowed by the armour rule): shape, value, friendly gap
function FOURTH.blob_pick_large(unit, m, r, key)
	local reach = r + FOURTH.BLOB_MARGIN_M
	local dmg = key and FOURTH.BLOB_DMG[key]
	local best, bv, bg = nil, nil, nil
	for i = 1, #m.large do
		local e = m.large[i]
		if FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit) and FOURTH.blob_ap_ok(e, dmg) then
			local g = FOURTH.blob_friend_gap(e, m, reach)
			if g == nil or g > reach then
				local v = FOURTH.blob_large_value(e, key)
				if v ~= nil and (bv == nil or v > bv) then best, bv, bg = e, v, g end
			end
		end
	end
	return best, bv, bg
end

-- ROUND 151: the hold - a visible large enemy ANYWHERE that this cast would take more value from than the best
-- infantry target now
function FOURTH.blob_large_hold(m, key, inf_value)
	local dmg = key and FOURTH.BLOB_DMG[key]
	for i = 1, #m.large do
		local e = m.large[i]
		if FOURTH.blob_ap_ok(e, dmg) then
			local v = FOURTH.blob_large_value(e, key)
			if v ~= nil and v > inf_value then return true, e end
		end
	end
	return false, nil
end

-- ROUND 151: the game's own usage rules - grounded (the caster must be flying) and engaged_in_melee
function FOURTH.blob_usage_ok(unit, key)
	local shot = key and FOURTH.BLOB_SHOT[key]
	if shot == nil then return true end
	if shot[7] == 1 then
		local ok, fly = pcall(function() return unit:is_currently_flying() end)
		if not (ok and fly == true) then return false end
	end
	if shot[8] == 1 then
		local ok, mel = pcall(function() return unit:is_in_melee() end)
		if not (ok and mel == false) then return false end
	end
	return true
end

'''

STILL_OLD = '''	local m = FOURTH.blob_map(true)
	local id = nil
	pcall(function() id = tostring(enemy:unique_ui_id()) end)
'''
STILL_NEW = STILL_OLD + '''	-- ROUND 151: a large target is re-checked in the large list (standing, usage rules, safe, armour rule)
	if FOURTH.blob_kind == "large" then
		local key = FOURTH.rc_self_keys and FOURTH.rc_self_keys[1]
		if not FOURTH.blob_still(unit) or not FOURTH.blob_usage_ok(unit, key) then return false end
		for i = 1, #m.large do
			local e = m.large[i]
			local eid = nil
			pcall(function() eid = tostring(e.unit:unique_ui_id()) end)
			if eid ~= nil and eid == id then
				local reach = r + FOURTH.BLOB_MARGIN_M
				local g = FOURTH.blob_friend_gap(e, m, reach)
				if g ~= nil and g <= reach then return false end
				return FOURTH.blob_ap_ok(e, key and FOURTH.BLOB_DMG[key])
			end
		end
		return false
	end
'''

EV_START = "function FOURTH.evaluate_enemy_blob(unit, routing)\n"
EV_END = "-- GENERATED by tools/gen_blob_tables.py (round 150)"
EV_LIVE = '''function FOURTH.evaluate_enemy_blob(unit, routing)
	FOURTH.eg_mode = "blob"
	FOURTH.blob_kind = nil
	if routing then return nil end
	local key = FOURTH.rc_self_keys and FOURTH.rc_self_keys[1]
	local r = key and FOURTH.BLAST_R[key]
	if r == nil then return nil end
	-- ROUND 150: never while the caster moves (the cast would stop it)
	if not FOURTH.blob_still(unit) then return nil end
	-- ROUND 151: the game's own usage rules (grounded, in melee)
	if not FOURTH.blob_usage_ok(unit, key) then return nil end
	local m = FOURTH.blob_map(false)
	local shot = FOURTH.BLOB_SHOT[key]
	local central = (shot ~= nil and shot[5] == 1)
	local tgt, sc, un, gap, val, kind = nil, nil, nil, nil, nil, nil
	-- ROUND 151: LARGE FIRST for the prefer-central attacks
	if central and #m.large > 0 then
		local lt, lv, lg = FOURTH.blob_pick_large(unit, m, r, key)
		if lt ~= nil then tgt, val, gap, kind = lt, lv, lg, "large" end
	end
	if tgt == nil then
		if #m.enemies == 0 then return nil end
		tgt, sc, un, gap, val = FOURTH.blob_pick(unit, m, r, key)
		if tgt == nil or sc < FOURTH.blob_need(r) then return nil end
		-- ROUND 151: THE HOLD - a more valuable large enemy anywhere on the field keeps this cast for it
		if central then
			local hold, le = FOURTH.blob_large_hold(m, key, val or 0)
			if hold then
				local last = FOURTH.blob_hold_said[key]
				if last == nil or tick_count - last >= 40 then
					FOURTH.blob_hold_said[key] = tick_count
					local lt2 = "large"
					pcall(function() lt2 = tostring(le.unit:type()) end)
					log("  " .. tostring(FOURTH.eg_marker) .. " HOLD: a large enemy (" .. lt2 .. ") is worth more than the best"
						.. " infantry target (value " .. string.format("%.0f", val or 0) .. ") - saving the cast for it")
				end
				return nil
			end
		end
		kind = "infantry"
	end
	local etype = "enemy"
	pcall(function() etype = tostring(tgt.unit:type()) end)
	FOURTH.blob_r = r
	FOURTH.blob_kind = kind
	FOURTH.eg_enemy = tgt.unit
	FOURTH.eg_arm = "blob"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = tgt.unit
	local d = FOURTH.eg_enemy_gap(unit, tgt.unit)
	if kind == "large" then
		return string.format("large target first (targeting %s): value destroyed %.0f of %s; ours %s; distance %sm bound %sm",
			etype, val or 0, tgt.sv and string.format("%.0f", tgt.sv) or "?",
			(gap ~= nil) and string.format("%.1fm away (needs > %sm)", gap, tostring(r + FOURTH.BLOB_MARGIN_M)) or "not near",
			(d ~= nil) and string.format("%.1f", d) or "?", tostring(FOURTH.eg_range_m))
	end
	local def = tgt.t and FOURTH.UNIT_DEF[tgt.t]
	return string.format("infantry blob (targeting %s): value destroyed %.0f (armour %s, %.0f%% of a soldier per hit,"
		.. " value %s per soldier); %d enemy soldiers in the %sm blast (line %d), %d unit(s);"
		.. " ours %s; distance %sm bound %sm", etype, val or 0, def and tostring(def[1]) or "?",
		100 * FOURTH.blob_kill(tgt, key and FOURTH.BLOB_DMG[key]), tgt.vps and string.format("%.1f", tgt.vps) or "?",
		math.floor(sc + 0.5), tostring(r), FOURTH.blob_need(r), un,
		(gap ~= nil) and string.format("%.1fm away (needs > %sm)", gap, tostring(r + FOURTH.BLOB_MARGIN_M)) or "not near",
		(d ~= nil) and string.format("%.1f", d) or "?", tostring(FOURTH.eg_range_m))
end
FOURTH.blob_hold_said = {}

'''
EV_ANN = '''-- the blob trigger: standing still, the game's usage rules, LARGE FIRST for the prefer-central attacks (round 151),
-- then the infantry target destroying the most value - held while a more valuable large enemy is on the field
function FOURTH.evaluate_enemy_blob(unit, routing)
	FOURTH.eg_mode = "blob"
	FOURTH.blob_kind = nil
	if routing then return false end
	local key = FOURTH.rc_self_keys and FOURTH.rc_self_keys[1]
	local r = key and FOURTH.BLAST_R[key]
	if r == nil then return false end
	if not FOURTH.blob_still(unit) then return false end
	if not FOURTH.blob_usage_ok(unit, key) then return false end
	local m = FOURTH.blob_map(false)
	local shot = FOURTH.BLOB_SHOT[key]
	local central = (shot ~= nil and shot[5] == 1)
	local tgt, kind = nil, nil
	if central and #m.large > 0 then
		tgt = FOURTH.blob_pick_large(unit, m, r, key)
		if tgt ~= nil then kind = "large" end
	end
	if tgt == nil then
		if #m.enemies == 0 then return false end
		local sc, un, gap, val
		tgt, sc, un, gap, val = FOURTH.blob_pick(unit, m, r, key)
		if tgt == nil or sc < FOURTH.blob_need(r) then return false end
		if central and FOURTH.blob_large_hold(m, key, val or 0) then return false end
		kind = "infantry"
	end
	FOURTH.blob_r = r
	FOURTH.blob_kind = kind
	FOURTH.eg_enemy = tgt.unit
	FOURTH.eg_arm = "blob"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = tgt.unit
	return true
end

'''

# ---- defaults --------------------------------------------------------------------------------------------------------
ISA_OLD = "\treturn per ~= nil and per[marker] == true\nend\n"
ISA_NEW = ("\tif per ~= nil and per[marker] ~= nil then return per[marker] == true end\n"
           "\t-- ROUND 151: an ability whose trigger family starts ARMED (user ruling 2026-11-14) is on until clicked off\n"
           "\tlocal a = ability_for(marker)\n"
           "\treturn a ~= nil and a.default_on == true\n"
           "end\n")
LOAD_OLD = "\tability.tip = FOURTH.TRIGGER_TIP[ability.trigger]\n"
LOAD_NEW = LOAD_OLD + ("\t-- ROUND 151: the family default. ZZ_AUTO_TEST_NO_DEFAULTS is a TEST-ONLY global the harness sets for\n"
                       "\t-- its older worlds (which arm by clicking); the game never defines it, so the defaults always apply there.\n"
                       "\tability.default_on = (FOURTH.DEFAULT_ON_TRIGGERS[ability.trigger] == true)\n"
                       "\t\tand ZZ_AUTO_TEST_NO_DEFAULTS ~= true\n")
WAS_OLD = "local was_armed = per ~= nil and per[ability.marker] == true"
WAS_NEW = "local was_armed = FOURTH.armed_slot(arm_slot, ability.marker)   -- ROUND 151: the default counts"
ALL_OLD = "\t\t\t\tif per == nil or per[ability.marker] ~= true then\n"
ALL_NEW = "\t\t\t\tif not FOURTH.armed_slot(unit_slot(owners[i]), ability.marker) then   -- ROUND 151: the default counts\n"
DEF_BLOCK = ('-- ============================================================================\n'
             '-- ROUND 151 - THE TRIGGER FAMILIES THAT START ARMED (user ruling 2026-11-14): the no-condition Winds of\n'
             '-- Magic abilities, the in-melee / on-charge self-casts ("a no brainer"), protection and last stand, morale\n'
             '-- saves, heals and ammo refills. A badge click still switches each off (the explicit choice wins).\n'
             '-- ============================================================================\n'
             'FOURTH.DEFAULT_ON_TRIGGERS = {\n' + "".join('\t%s = true,\n' % t for t in DEFAULT_ON) + '}\n\n'
             '-- the armed state of a (unit slot, marker) pair: the explicit switch, else the family default\n'
             'function FOURTH.armed_slot(slot, marker)\n'
             '\tlocal per = armed[slot]\n'
             '\tif per ~= nil and per[marker] ~= nil then return per[marker] == true end\n'
             '\tlocal a = ability_for(marker)\n'
             '\treturn a ~= nil and a.default_on == true\n'
             'end\n\n')

# ---- the ALL badge -----------------------------------------------------------------------------------------------------
CLICK_OLD = '\t\tif string.sub(clicked_id, 1, 8) == "zz_auto_" then\n'
CLICK_NEW = CLICK_OLD + ('\t\t\t-- ROUND 151: the ALL badge arms / disarms every ability of ours on the selected unit(s)\n'
                         '\t\t\tif clicked_id == FOURTH.ALL_BADGE_ID then\n'
                         '\t\t\t\tFOURTH.all_click()\n'
                         '\t\t\t\treturn\n'
                         '\t\t\tend\n')
TICK_RE = re.compile(r"(\n\tlocal active_dropped = false[^\n]*\n)")
TICK_ADD = "\t-- ROUND 151: the ALL badge (created and shown with the ability badges)\n\tpcall(FOURTH.all_badge_tick)\n"
SET_END_LIVE = "\tapply_ability_feedback(marker)   -- the letter on the badge - the only feedback now\nend\n"
SET_END_ANN = "\tper[marker] = value == true\n\tapply_ability_feedback(marker)\nend\n"
ALL_COMMON = '''
-- ============================================================================
-- ROUND 151 - THE ALL BADGE (user ruling 2026-11-14: "ALL badge per unit"). One extra badge, built on the ui tick
-- with the ability badges' template and steps, left of the wheel's left slot; it shows "ALL" while any ability badge
-- is shown. A click acts on every selected unit: when every ability of ours it owns is armed, all are disarmed;
-- otherwise all are armed.
-- ============================================================================
FOURTH.ALL_BADGE_ID = "zz_auto_badge_all"
FOURTH.ALL_DX = -48          -- left of the wheel's left slot (WHEEL_SLOT[6]), in the ability badges' offset frame
FOURTH.all_state = { badge = nil, attempts = 0, shown = false }

function FOURTH.all_badge_tick()
	local st = FOURTH.all_state
	local any = false
	for _, ability in ipairs(active_abilities_list()) do
		local s = ability_state[ability.marker]
		if s ~= nil and s.badge_shown == true then
			any = true
			break
		end
	end
	if st.badge == nil then
		if not any or badge_parent == nil or st.attempts >= MAX_BADGE_ATTEMPTS then return end
		st.attempts = st.attempts + 1
		local ok, err = pcall(function()
			st.badge = UIComponent(badge_parent:CreateComponent(FOURTH.ALL_BADGE_ID, "ui/templates/zz_auto_badge"))
			if st.badge == nil then error("CreateComponent returned nothing", 0) end
			st.badge:SetDockingPoint(0)
			st.badge:Resize(36, 24)
			for i = 0, 4 do st.badge:SetImagePath("ui/zz_auto/blank.png", i) end
			local ok_text = write_badge_letter(st, "ALL")
			if not ok_text then error("SetText raised", 0) end
			st.badge:SetVisible(false)
			st.badge:SetDockingPoint(8)
			local slot = WHEEL_SLOT[6]
			st.badge:SetDockOffset(BADGE_X + (slot[1] - WHEEL_TOP_X) + FOURTH.ALL_DX, BADGE_Y + (slot[2] - WHEEL_TOP_Y))
			badge_parent:Layout()
		end)
		if not ok then
			discard_badge(st)
			FOURTH.all_said("ALL badge: create attempt raised: " .. tostring(err))
			return
		end
		st.shown = false
		FOURTH.all_said("ALL badge: created left of the wheel")
	end
	if st.shown ~= any then
		st.shown = any
		pcall(function() st.badge:SetVisible(any) end)
	end
end

function FOURTH.all_click()
	local targets = {}
	for i = 1, #selected_ui_ids do
		if selected_ui_ids[i] ~= nil then targets[#targets + 1] = selected_ui_ids[i] end
	end
	if #targets == 0 then
		if selection_callback_alive or selected_unit_id == nil then
			FOURTH.all_said("ALL click ignored: no unit selected")
			return
		end
		targets[1] = selected_unit_id
	end
	local todo, all_on = {}, true
	for i = 1, #targets do
		for _, entry in ipairs(owned_abilities_by_unit[tostring(targets[i])] or {}) do
			todo[#todo + 1] = { targets[i], entry.marker }
			if not FOURTH.armed_slot(unit_slot(targets[i]), entry.marker) then all_on = false end
		end
	end
	if #todo == 0 then
		FOURTH.all_said("ALL click: the selected unit(s) own none of our abilities")
		return
	end
	local value = not all_on
	for i = 1, #todo do set_auto_for_unit(todo[i][1], todo[i][2], value) end
	FOURTH.all_said("ALL click: " .. tostring(#todo) .. " ability switch(es) on " .. tostring(#targets)
		.. " unit(s) -> " .. (value and "ON" or "OFF"))
end
'''
ALL_SAID_LIVE = "\nfunction FOURTH.all_said(text) log(text) end\n"
ALL_SAID_ANN = "\nfunction FOURTH.all_said(text) end   -- the reading copy keeps no log\n"
TIP_OLD = '\twhen_ready = "When armed, fires as soon as it is ready",\n'
EVAL_ANCHOR = "FOURTH.evaluators = {\n"


def main():
    src0 = open(SRC, encoding="utf-8").read()
    keys = GB.keys_in(src0)
    assert len(keys) == 77
    lblock = GB.lua_block_large(GB.shot_table(keys), GB.large_def_table())
    for path, ev, set_end, said in ((SRC, EV_LIVE, SET_END_LIVE, ALL_SAID_LIVE), (ANN, EV_ANN, SET_END_ANN, ALL_SAID_ANN)):
        s = open(path, encoding="utf-8", newline="").read()
        assert "blob_pick_large" not in s
        s = sub(s, MAP_OLD, MAP_NEW)
        s = sub(s, M_OLD, M_NEW)
        s = sub(s, AP_OLD, AP_NEW)
        s = cut(s, PICK_START, PICK_END, PICK_NEW)
        s = sub(s, STILL_OLD, STILL_NEW)
        s = cut(s, EV_START, EV_END, ev)
        s = sub(s, EVAL_ANCHOR, lblock + "\n" + DEF_BLOCK + EVAL_ANCHOR)
        s = sub(s, ISA_OLD, ISA_NEW)
        s = sub(s, LOAD_OLD, LOAD_NEW)
        s = sub(s, WAS_OLD, WAS_NEW)
        s = sub(s, ALL_OLD, ALL_NEW)
        s = sub(s, CLICK_OLD, CLICK_NEW)
        assert len(TICK_RE.findall(s)) == 1
        s = TICK_RE.sub(lambda m: m.group(1) + TICK_ADD, s)
        s = sub(s, set_end, set_end + ALL_COMMON + said)
        assert "string.find" not in PICK_NEW + STILL_NEW + ev + ALL_COMMON + said + DEF_BLOCK
        if path == ANN:
            assert "log(" not in EV_ANN + ALL_SAID_ANN and "log(" not in ALL_COMMON
        open(path, "w", encoding="utf-8", newline="").write(s)
        print("patched", path)


if __name__ == "__main__":
    main()
