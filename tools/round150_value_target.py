#!/usr/bin/env python3
"""Round 150 (harness 146): the blob trigger picks the target that destroys the most enemy VALUE, never fires while the
caster moves; the 21 Winds of Magic abilities fire when ready; the map probe logs our army's winds.

User rulings 2026-11-14 (after the High Elves blob battle):
  * "Most value destroyed": among safe candidates whose blast reaches the density line, the most value destroyed wins:
    each enemy block under the blast adds soldiers covered x the share of one soldier the blast's hit kills (blast
    damage after armour, expected reduction 0.75 x armour %, against the soldier's hit points; generated) x its live
    value per soldier (strategic_value / men). An AP-heavy attack (armour-piercing at least half its damage) never
    targets armour below 50.
  * standstill: "For now, only the Blob attacks" - the caster's is_moving() must read exactly false (both observed
    stoppers, Volley of High Arrows and Soporific Breath, were aimed casts that stopped a moving caster).
  * charge abilities: "Nothing" (unchanged).
  * Winds of Magic abilities: "All when ready" - 21 entries move from melee_unwavering to the NEW when_ready.
  * "let's read those reserves": the map probe adds a WINDS row (our army's winds_of_magic_current / _reserve /
    _remaining_recharge_rate) every 2 s.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_blob_tables as GB  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
WINDS = ["wh3_cp1_character_abilities_magic_prayer", "wh_main_item_abilities_black_periapt",
         "wh2_main_item_abilities_book_of_hoeth", "wh3_main_character_abilities_extra_ingredients",
         "wh_dlc03_item_abilities_jagged_dagger", "wh3_main_character_abilities_locus_of_conjuration",
         "wh2_dlc09_item_abilities_neferras_scrolls_of_mighty_incantations", "wh_main_item_abilities_power_stone",
         "wh3_main_item_abilities_prismatic_amplifier", "wh3_main_item_abilities_scroll_of_destiny",
         "wh_dlc03_item_abilities_skull_of_rarkos", "wh3_main_item_abilities_snowflake_pendant",
         "wh_main_item_abilities_staff_of_volans", "wh3_main_item_abilities_staff_of_wu_xing",
         "wh2_main_item_abilities_starwood_staff", "wh2_dlc10_item_abilities_stave_of_avelorn",
         "wh3_main_item_abilities_the_chromatic_tome", "wh2_dlc12_lord_abilities_unlimited_power",
         "wh3_dlc29_item_abilities_warpstone_tokens", "wh3_dlc29_item_abilities_whispering_skull",
         "wh3_main_daemon_body_abilities_winds_of_change"]
assert len(WINDS) == 21 and len(set(WINDS)) == 21


def sub(s, a, b):
    assert s.count(a) == 1, (a[:90], s.count(a))
    return s.replace(a, b)


SHAPE_OLD = "\ts.rx, s.rz = s.fz, -s.fx\n"
SHAPE_NEW = SHAPE_OLD + ("\t-- ROUND 150: the type and the live value per soldier (strategic_value / men; nil when unreadable)\n"
                         "\ts.t = t\n"
                         "\tlocal ok_v, sv = pcall(function() return u:strategic_value() end)\n"
                         "\tif ok_v and type(sv) == \"number\" and sv > 0 then s.vps = sv / men end\n")

PICK_OLD = '''-- the best safe target for this caster: shape, score, units, friendly gap; nil when none passes
function FOURTH.blob_pick(unit, m, r)
	local reach = r + FOURTH.BLOB_MARGIN_M
	local best, bs, bu, bg = nil, nil, nil, nil
	for i = 1, #m.enemies do
		local e = m.enemies[i]
		if FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit) then
			local g = FOURTH.blob_friend_gap(e, m, reach)
			if g == nil or g > reach then
				local sc, un = FOURTH.blob_score(e, m, r)
				if best == nil or sc > bs then best, bs, bu, bg = e, sc, un, g end
			end
		end
	end
	return best, bs, bu, bg
end
'''
PICK_NEW = '''-- ROUND 150 (user ruling 2026-11-14: "Most value destroyed").
FOURTH.BLOB_AP_ARMOUR_MIN = 50   -- an AP-heavy attack never targets armour below this (user ruling 2026-11-14)
FOURTH.ARMOUR_TAKES = 0.0075     -- base damage lost per armour point: the engine removes a random armour/2..armour %,
                                 -- 0.75 x armour % on average

-- the share of one soldier of block e that one hit of this blast kills (1 when the type or the damage is unknown)
function FOURTH.blob_kill(e, dmg)
	local def = e.t and FOURTH.UNIT_DEF[e.t]
	if def == nil or dmg == nil then return 1 end
	local a = math.min(def[1], 100)
	return math.min(1, (dmg[1] * (1 - FOURTH.ARMOUR_TAKES * a) + dmg[2]) / def[2])
end

-- the enemy value a blast of radius r centred on the target destroys: the 19 circle points, each adding every enemy
-- block's soldier density x the point's share of the area x the share of a soldier killed x its value per soldier
-- (1 when the value read failed)
function FOURTH.blob_value(tgt, m, r, dmg)
	local share = math.pi * r * r / #FOURTH.BLOB_RING
	local v = 0
	for k = 1, #FOURTH.BLOB_RING do
		local px = tgt.x + FOURTH.BLOB_RING[k][1] * r
		local pz = tgt.z + FOURTH.BLOB_RING[k][2] * r
		for i = 1, #m.enemies do
			local e = m.enemies[i]
			if FOURTH.blob_rect_gap(px, pz, e) == 0 then
				v = v + e.density * share * FOURTH.blob_kill(e, dmg) * (e.vps or 1)
			end
		end
	end
	return v
end

-- may this attack aim at block e at all? an AP-heavy attack needs armour of at least BLOB_AP_ARMOUR_MIN
function FOURTH.blob_ap_ok(e, dmg)
	if dmg == nil or dmg[3] ~= 1 then return true end
	local def = e.t and FOURTH.UNIT_DEF[e.t]
	return def ~= nil and def[1] >= FOURTH.BLOB_AP_ARMOUR_MIN
end

-- the best safe target for this caster: shape, soldiers, units, friendly gap, value; nil when none passes. A candidate
-- must be allowed (armour rule), safe, and reach the density line on its own; the most value destroyed wins.
function FOURTH.blob_pick(unit, m, r, key)
	local reach = r + FOURTH.BLOB_MARGIN_M
	local need = FOURTH.blob_need(r)
	local dmg = key and FOURTH.BLOB_DMG[key]
	local best, bs, bu, bg, bv = nil, nil, nil, nil, nil
	for i = 1, #m.enemies do
		local e = m.enemies[i]
		if FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit) and FOURTH.blob_ap_ok(e, dmg) then
			local g = FOURTH.blob_friend_gap(e, m, reach)
			if g == nil or g > reach then
				local sc, un = FOURTH.blob_score(e, m, r)
				if sc >= need then
					local v = FOURTH.blob_value(e, m, r, dmg)
					if best == nil or v > bv or (v == bv and sc > bs) then best, bs, bu, bg, bv = e, sc, un, g, v end
				end
			end
		end
	end
	return best, bs, bu, bg, bv
end

-- standing still: is_moving() must read exactly false (user ruling 2026-11-14; a cast stops a moving caster)
function FOURTH.blob_still(unit)
	local ok, mv = pcall(function() return unit:is_moving() end)
	return ok and mv == false
end
'''
STILL_OLD = '''			local reach = r + FOURTH.BLOB_MARGIN_M
			local g = FOURTH.blob_friend_gap(e, m, reach)
			if g ~= nil and g <= reach then return false end
			local sc = FOURTH.blob_score(e, m, r)
			return sc >= FOURTH.blob_need(r)
'''
STILL_NEW = '''			local reach = r + FOURTH.BLOB_MARGIN_M
			local g = FOURTH.blob_friend_gap(e, m, reach)
			if g ~= nil and g <= reach then return false end
			-- ROUND 150: the caster still standing, the armour rule still met
			if not FOURTH.blob_still(unit) then return false end
			local key = FOURTH.rc_self_keys and FOURTH.rc_self_keys[1]
			if not FOURTH.blob_ap_ok(e, key and FOURTH.BLOB_DMG[key]) then return false end
			local sc = FOURTH.blob_score(e, m, r)
			return sc >= FOURTH.blob_need(r)
'''
EV_LIVE_OLD = '''	local m = FOURTH.blob_map(false)
	if #m.enemies == 0 then return nil end
	local tgt, sc, un, gap = FOURTH.blob_pick(unit, m, r)
	local need = FOURTH.blob_need(r)
	if tgt == nil or sc < need then return nil end
	local etype = "enemy"
	pcall(function() etype = tostring(tgt.unit:type()) end)
	FOURTH.blob_r = r
	FOURTH.eg_enemy = tgt.unit
	FOURTH.eg_arm = "blob"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = tgt.unit
	local d = FOURTH.eg_enemy_gap(unit, tgt.unit)
	return string.format("infantry blob (targeting %s): %d enemy soldiers in the %sm blast (line %d), %d unit(s);"
		.. " ours %s; distance %sm bound %sm", etype, math.floor(sc + 0.5), tostring(r), need, un,'''
EV_LIVE_NEW = '''	-- ROUND 150: never while the caster moves (the cast would stop it)
	if not FOURTH.blob_still(unit) then return nil end
	local m = FOURTH.blob_map(false)
	if #m.enemies == 0 then return nil end
	local tgt, sc, un, gap, val = FOURTH.blob_pick(unit, m, r, key)
	local need = FOURTH.blob_need(r)
	if tgt == nil or sc < need then return nil end
	local etype = "enemy"
	pcall(function() etype = tostring(tgt.unit:type()) end)
	FOURTH.blob_r = r
	FOURTH.eg_enemy = tgt.unit
	FOURTH.eg_arm = "blob"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = tgt.unit
	local d = FOURTH.eg_enemy_gap(unit, tgt.unit)
	local def = tgt.t and FOURTH.UNIT_DEF[tgt.t]
	return string.format("infantry blob (targeting %s): value destroyed %.0f (armour %s, %.0f%% of a soldier per hit,"
		.. " value %s per soldier); %d enemy soldiers in the %sm blast (line %d), %d unit(s);"
		.. " ours %s; distance %sm bound %sm", etype, val or 0, def and tostring(def[1]) or "?",
		100 * FOURTH.blob_kill(tgt, key and FOURTH.BLOB_DMG[key]), tgt.vps and string.format("%.1f", tgt.vps) or "?",
		math.floor(sc + 0.5), tostring(r), need, un,'''
EV_ANN_OLD = '''	local m = FOURTH.blob_map(false)
	if #m.enemies == 0 then return false end
	local tgt, sc = FOURTH.blob_pick(unit, m, r)
'''
EV_ANN_NEW = '''	if not FOURTH.blob_still(unit) then return false end   -- ROUND 150: never while the caster moves
	local m = FOURTH.blob_map(false)
	if #m.enemies == 0 then return false end
	local tgt, sc = FOURTH.blob_pick(unit, m, r, key)
'''
WINDS_OLD = '\trows[#rows + 1] = "MAP_END t=" .. t .. " own=" .. n_own .. " enemy=" .. n_en\n'
WINDS_NEW = ('\t-- ROUND 150: our army\'s Winds of Magic (user 2026-11-14: "let\'s read those reserves")\n'
             '\tlocal wc, wr, wrr = "?", "?", "?"\n'
             '\tlocal ok_a, army = pcall(function() return bm:get_player_army() end)\n'
             '\tif ok_a and army ~= nil then\n'
             '\t\twc = FOURTH.map_num(function() return army:winds_of_magic_current() end, "%.1f")\n'
             '\t\twr = FOURTH.map_num(function() return army:winds_of_magic_reserve() end, "%.1f")\n'
             '\t\twrr = FOURTH.map_num(function() return army:winds_of_magic_remaining_recharge_rate() end, "%.3f")\n'
             '\tend\n'
             '\trows[#rows + 1] = "WINDS t=" .. t .. " current=" .. wc .. " reserve=" .. wr .. " recharge_rate=" .. wrr\n'
             + WINDS_OLD)
WR_LIVE = '''-- ROUND 150 (user ruling 2026-11-14, Winds of Magic abilities: "All when ready"): no condition at all; the shared
-- gates (armed, ready, charge hold, 2 s guard) decide when it fires.
function FOURTH.evaluate_when_ready(unit, routing)
	return "when ready (Winds of Magic), cast on self"
end

'''
WR_ANN = '''-- ROUND 150: the Winds of Magic abilities fire whenever they are ready (no condition)
function FOURTH.evaluate_when_ready(unit, routing)
	return true
end

'''
MAP_OLD = "\tenemy_blob = FOURTH.evaluate_enemy_blob,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 150\n\twhen_ready = FOURTH.evaluate_when_ready,\n"
TIP_OLD = ('\tenemy_blob = "When armed, fires at the densest enemy infantry in range when the blast hits enough '
           'soldiers and none of ours are near",\n')
TIP_NEW = ('\tenemy_blob = "When armed and standing still, fires at the enemy infantry where the blast destroys the most '
           'value, when it hits enough soldiers and none of ours are near",\n'
           '\twhen_ready = "When armed, fires as soon as it is ready",\n')
ANCHOR = "FOURTH.evaluators = {\n"


def main():
    src = open(SRC, encoding="utf-8").read()
    keys = GB.keys_in(src)
    assert len(keys) == 77
    vblock = GB.lua_block_value(GB.damage_table(keys), GB.defence_table())
    for path, ev_old, ev_new, wr in ((SRC, EV_LIVE_OLD, EV_LIVE_NEW, WR_LIVE), (ANN, EV_ANN_OLD, EV_ANN_NEW, WR_ANN)):
        s = open(path, encoding="utf-8", newline="").read()
        assert "evaluate_when_ready" not in s
        s = sub(s, SHAPE_OLD, SHAPE_NEW)
        s = sub(s, PICK_OLD, PICK_NEW)
        s = sub(s, STILL_OLD, STILL_NEW)
        s = sub(s, ev_old, ev_new)
        s = sub(s, WINDS_OLD, WINDS_NEW)
        s = sub(s, MAP_OLD, MAP_NEW)
        s = sub(s, TIP_OLD, TIP_NEW)
        s = sub(s, ANCHOR, vblock + "\n" + wr + ANCHOR)
        n = 0
        for k in WINDS:
            pat = re.compile(r'(\t\{ marker = "[^"]+", name = "[^"]+", trigger = )"melee_unwavering"(,\n(?:\t\t[^\n]*\n){0,3}?\t\tkeys = \{[^}]*"%s")' % re.escape(k))
            s, c = pat.subn(r'\1"when_ready"\2', s)
            assert c == 1, (k, c)
            n += 1
        assert "string.find" not in PICK_NEW + STILL_NEW + ev_new + WINDS_NEW + wr + vblock
        open(path, "w", encoding="utf-8", newline="").write(s)
        print(path, "patched; winds entries moved:", n)


if __name__ == "__main__":
    main()
