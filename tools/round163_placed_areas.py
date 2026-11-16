#!/usr/bin/env python3
"""Round 163 (harness 162): the placed / static area damage (26 entries / 26 keys; 2 new families) and the expendable
units, user rulings 2026-11-16. Earlier status: "excluded (auto: placed / static area damage (friendly fire, family
decision 2026-10-09))", a RULE, never a ruling on these abilities one by one.

  * 7 instant blasts (Acorns of the Oak of Ages, Blight Boil, Frost Fang, The Hammer of Smednir, Viletide, Crackleblaze,
    Lamprey's Bite): "Like Dwellers Below" -> enemy_wander (static: caster and target standing still, the blob rule,
    none of ours within radius + reach + 10 m; Crackleblaze cannot hit our units: no test).
  * 14 lingering areas (Boiling Cauldron, Simmering Pot, Brass Orb x3, Infernal Gateway, Pit of Shades x3, Rubric of
    Dark Dimensions, Irresistible Plague, Plaguemaster, Warp Junction, Magma Storm): "Same as the blasts" ->
    enemy_wander. Magma Storm's bombardment (60 m spread + 5 m blasts) widens its safety distance to 75 m.
  * Chain Lightning (Regiment of Renown): "Wanderer rule" -> enemy_wander (simulated 95% reach).
  * Arcane Vassal: "Most enemies around" -> NEW ally_blast: our unit (or the caster) within the 70% ally bound whose
    blast circle covers the most enemy value (the blob value and density line); cast on that unit.
  * Befuddlement of Mischiefs: "charge only", "Any fast enemy" -> enemy_fast_near_ally.
  * Winged Staff: "Area drain rule" -> enemy_area_drain (25 per tick, the GENERATED AREA table).
  * Siegebreaker: "Strike a standing large single" -> NEW enemy_strike: the most valuable standing single-entity enemy
    in range, none of ours within its 1.1 m blast + 10 m, cast on the ground under it (the game refuses a unit target
    unless it climbs, mans equipment or stands on a platform).
  * Rune and Master Rune of Wrath & Ruin: closed (tracker only).
  * EXPENDABLE (user: "the friendly fire checks skipped these units" -> "Game's set + cheap undead"): every friendly-fire
    check (they all read the map's list of our units) leaves out our units the game marks expendable (GENERATED
    FOURTH.EXPENDABLE_TEXT) and our units worth less than TRASH_VPS per soldier (live value).
Also: the WW table now reads bombardments; Hell Hammer (round 162) gains its 14 m bombardment blast as its radius.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ww_tables as GW  # noqa: E402
import gen_shot_tables as GS  # noqa: E402
import gen_expendable_keys as GE  # noqa: E402
import gamedata_paths as GP  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
WN = "enemy_wander"
ROWS = [
    ("acorns_of_the_oak", "Acorns of the Oak of Ages", WN, "wh2_dlc16_item_abilities_acorns_of_the_oak_of_ages"),
    ("blight_boil", "Blight Boil", WN, "wh3_main_item_abilities_deaths_head"),
    ("frost_fang", "Frost Fang", WN, "wh3_main_weapon_abilities_frost_fang"),
    ("hammer_of_smednir", "The Hammer of Smednir", WN, "wh3_dlc23_item_abilities_hammer_of_smednir"),
    ("viletide", "Viletide", WN, "wh_dlc03_spell_bound_viletide"),
    ("crackleblaze", "Crackleblaze", WN, "wh3_main_item_abilities_crackleblaze"),
    ("lampreys_bite", "Lamprey's Bite", WN, "wh3_dlc24_unit_abilities_lampreys_bite"),
    ("boiling_cauldron", "Boiling Cauldron", WN, "wh3_dlc26_lord_abilities_boiling_cauldron"),
    ("simmering_pot", "Simmering Pot", WN, "wh3_dlc26_lord_abilities_simmering_pot"),
    ("brass_orb", "Brass Orb", WN, "wh2_dlc12_character_abilities_brass_orb"),
    ("brass_orb_doom_flayer", "Brass Orb", WN, "wh2_dlc12_character_abilities_brass_orb_tech_lab_doom_flayer"),
    ("brass_orb_upgrade", "Brass Orb Upgraded", WN, "wh2_dlc12_character_abilities_brass_orb_upgrade"),
    ("infernal_gateway", "Infernal Gateway", WN, "wh3_dlc20_spell_bound_infernal_gateway"),
    ("pit_of_shades_dlc27", "Pit of Shades", WN, "wh3_dlc27_spell_bound_pit_of_shades"),
    ("pit_of_shades_main", "Pit of Shades", WN, "wh3_main_spell_bound_pit_of_shades"),
    ("pit_of_shades", "Pit of Shades", WN, "wh_dlc05_spell_shadow_pit_of_shades_bound"),
    ("rubric_of_dark_dimensions", "Rubric of Dark Dimensions", WN, "wh2_main_spell_bound_rubric_of_dark_dimensions"),
    ("irresistible_plague", "Irresistible Plague!", WN, "wh3_dlc29_spell_bound_plague"),
    ("plaguemaster", "Plaguemaster", WN, "wh3_dlc29_spell_bound_plaguemaster"),
    ("warp_junction", "Warp Junction", WN, "wh3_dlc29_lord_abilities_warp_junction"),
    ("magma_storm", "Magma Storm", WN, "wh3_pro10_cataclysm_fire_magma_storm_bound"),
    ("chain_lightning_ror", "Chain Lightning", WN, "wh_main_spell_bound_chain_lightning_ror"),
    ("arcane_vassal", "Arcane Vassal", "ally_blast", "wh2_main_character_abilities_arcane_vassal"),
    ("befuddlement_of_mischiefs", "Befuddlement of Mischiefs", "enemy_fast_near_ally",
     "wh2_dlc16_character_abilities_befuddlement_of_mischiefs"),
    ("winged_staff", "Winged Staff", "enemy_area_drain", "wh2_main_weapon_bound_winged_staff"),
    ("siegebreaker", "Siegebreaker", "enemy_strike", "wh3_main_weapon_abilities_siegebreaker"),
]
assert len(ROWS) == 26 and len(set(r[0] for r in ROWS)) == 26 and len(set(r[3] for r in ROWS)) == 26


def tsv(n):
    f = open(os.path.join(GP.GAMEDATA, n), encoding="utf-8-sig")
    h = f.readline().rstrip("\n").split("\t")
    f.readline()
    return [dict(zip(h, l.rstrip("\n").split("\t"))) for l in f]


USA = {r["key"]: r for r in tsv("unit_spec_abil.tsv")}
INV = {}
for r in tsv("special_ability_to_invalid_target_flags_tables.tsv"):
    INV.setdefault(r["special_ability"], set()).add(r["invalid_target"])


def num(v):
    f = float(v)
    return str(int(f)) if f == int(f) else ("%.3f" % f).rstrip("0").rstrip(".")


def entry(marker, name, trig, key):
    rng = float(USA[key]["target_intercept_range"])
    lines = ['\t{ marker = "%s", name = "%s", trigger = "%s",' % (marker, name, trig),
             '\t\tbadge = "zz_auto_badge_%s",' % marker,
             '\t\tkeys = { "%s" },' % key]
    if trig == "ally_blast":
        lines.append('\t\tally_range_real = %s,' % num(rng))
    elif rng > 0:
        lines.append('\t\trange_real = %s,' % num(rng))
    else:
        lines.append('\t\tunbounded = true,')   # Magma Storm: target_intercept_range -1 (no real range)
    if "flying_currently" in INV.get(key, set()):
        lines.append('\t\ttarget_class = "not_flying",')
    lines.append("\t\tox = 0, oy = 0 },")
    return "\n".join(lines) + "\n"


NEW_ENTRIES = "".join(entry(*r) for r in ROWS)
KEYS = [r[3] for r in ROWS]
HOLD = [(k, num(USA[k]["recharge_time"])) for k in KEYS if int(float(USA[k]["num_uses"])) > 1]
WIND = [(k, num(USA[k]["wind_up_time"])) for k in KEYS if float(USA[k]["wind_up_time"]) > 0]
NF = sum(1 for k in KEYS if "flying_currently" in INV.get(k, set()))
RR = sum(1 for r in ROWS if float(USA[r[3]]["target_intercept_range"]) > 0 and r[2] != "ally_blast")
print("multi-use:", len(HOLD), "wind-up:", len(WIND), "not_flying classes:", NF, "range_real:", RR)

RESTOCK = '\t{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",'
WIND_OLD = "\twind_up_s = {\n"
WIND_NEW = WIND_OLD + "\t\t-- ROUND 163: the placed areas' wind-ups (unit_spec_abil wind_up_time)\n" + "".join(
    '\t\t["%s"] = %s,\n' % (k, v) for k, v in WIND)
HOLD_OLD = "\thold_s = {\n"
HOLD_NEW = HOLD_OLD + "\t\t-- ROUND 163: the placed areas with more than one use (recharge_time)\n" + "".join(
    '\t\t["%s"] = %s,\n' % (k, v) for k, v in HOLD)
OURS_OLD = ("\t\t\tlocal s = FOURTH.blob_shape(u)\n"
            "\t\t\tif s ~= nil then m.ours[#m.ours + 1] = s end\n")
OURS_NEW = ("\t\t\tlocal s = FOURTH.blob_shape(u)\n"
            "\t\t\t-- ROUND 163 (user ruling 2026-11-16, \"Game's set + cheap undead\"): an EXPENDABLE unit of ours or a\n"
            "\t\t\t-- cheap one is left out of the list every friendly-fire check reads\n"
            "\t\t\tif s ~= nil and not FOURTH.ff_ignored(s) then m.ours[#m.ours + 1] = s end\n")
STILL_OLD1 = "\tlocal list = (row.kind == 1) and m.all or m.enemies\n"
STILL_NEW1 = "\tlocal list = (row.kind == 1 or row.kind == 4) and m.all or m.enemies   -- ROUND 163: a strike picks from all\n"
STILL_OLD2 = ("\t\t\tif row.kind == 1 then return FOURTH.ww_wave_value(unit, e, m, row) ~= nil end\n"
              "\t\t\treturn FOURTH.ww_wander_value(unit, e, m, row) ~= nil\n")
STILL_NEW2 = ("\t\t\tif row.kind == 1 then return FOURTH.ww_wave_value(unit, e, m, row) ~= nil end\n"
              "\t\t\tif row.kind == 4 then return FOURTH.ww_strike_value(unit, e, m, row) ~= nil end   -- ROUND 163\n"
              "\t\t\treturn FOURTH.ww_wander_value(unit, e, m, row) ~= nil\n")
WANDER_GUARD_OLD = "\tif routing or row == nil or row.kind == 1 or not FOURTH.blob_still(unit) then return %NO% end\n"
WANDER_GUARD_NEW = ("\tif routing or row == nil or row.kind == 1 or row.kind == 4 or not FOURTH.blob_still(unit) then"
                    " return %NO% end\n")

EVALS = r'''-- ============================================================================
-- ROUND 163 - THE PLACED AREAS AND THE EXPENDABLE UNITS (user rulings 2026-11-16; earlier a 2026-10-09 family RULE).
--   The instant blasts, the lingering areas and Chain Lightning (RoR) ride
--   enemy_wander (the WW table now reads bombardments: Magma Storm's 60 m spread
--   widens its safety distance, Hell Hammer's 14 m blast its corridor).
--   ally_blast (Arcane Vassal: cast on one of OUR units, the blast hits enemies
--   only): our unit (or the caster) within the 70% ally bound whose blast circle
--   covers the most enemy value (the blob value and density line).
--   enemy_strike (Siegebreaker): the most valuable STANDING single-entity enemy
--   in range, none of ours within its blast + SHOT_SAFE_M; cast on the ground
--   under it (the game refuses a unit target unless it climbs, mans equipment
--   or stands on a platform).
--   EXPENDABLE: every friendly-fire check reads the map's list of our units; an
--   expendable unit of ours (the game's attribute, GENERATED) or a cheap one
--   (live value below TRASH_VPS per soldier) is left out of it.
-- ============================================================================
-- an expendable or cheap unit of ours: the friendly-fire checks ignore it (an unreadable value keeps it protected)
function FOURTH.ff_ignored(s)
	if s.t ~= nil and FOURTH.class_keys.expendable[s.t] == true then return true end
	return s.vps ~= nil and s.vps < FOURTH.TRASH_VPS
end

-- a strike candidate: a standing single-entity enemy in range with none of ours near; its live value, or nil
function FOURTH.ww_strike_value(unit, e, m, row)
	if not (e.t ~= nil and FOURTH.class_keys.single[e.t] == true) then return nil end
	if not (FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit) and FOURTH.ww_target_still(e)) then
		return nil
	end
	if row.allies then
		local need = row.r + row.buf + FOURTH.SHOT_SAFE_M
		for i = 1, #m.ours do
			if FOURTH.blob_rect_gap(e.x, e.z, m.ours[i]) <= need then return nil end
		end
	end
	return e.value or 0
end

function FOURTH.evaluate_enemy_strike(unit, routing)
	FOURTH.eg_mode = "ww"
	local row = FOURTH.ww_row()
	if routing or row == nil or row.kind ~= 4 or not FOURTH.blob_still(unit) then return %NO% end
	local m = FOURTH.blob_map(false)
	local best, bv = nil, nil
	for i = 1, #m.all do
		local e = m.all[i]
		local v = FOURTH.ww_strike_value(unit, e, m, row)
		if v ~= nil and (bv == nil or v > bv) then best, bv = e, v end
	end
	if best == nil then return %NO% end
	FOURTH.ww_take(unit, best, row)
	%RET_STRIKE%
end

function FOURTH.evaluate_ally_blast(unit, routing)
	local row = FOURTH.ww_row()
	if routing or row == nil then return %NO% end
	local m = FOURTH.blob_map(false)
	if #m.enemies == 0 then return %NO% end
	local reach = FOURTH.ab_range_m
	local best, bv, bs, bg = nil, nil, nil, nil
	local function try(u, gap)
		local s = FOURTH.blob_shape(u)
		if s == nil then return end
		local sc = FOURTH.blob_score(s, m, row.r)
		if sc < FOURTH.blob_need(row.r) then return end
		local v = FOURTH.blob_value(s, m, row.r, nil)
		if bv == nil or v > bv then best, bv, bs, bg = u, v, sc, gap end
	end
	try(unit, 0)
	local self_id = nil
	pcall(function() self_id = tostring(unit:unique_ui_id()) end)
	for i = 1, #(tracked_units or {}) do
		local o = tracked_units[i] and tracked_units[i].unit
		if o ~= nil and o ~= unit then
			local oid = nil
			pcall(function() oid = tostring(o:unique_ui_id()) end)
			if oid ~= self_id and not unit_is_routing(o) then
				local gap = FOURTH.ab_ally_gap(unit, o)
				if gap ~= nil and reach ~= nil and gap <= reach then try(o, gap) end
			end
		end
	end
	if best == nil then return %NO% end
	if best ~= unit then
		FOURTH.ab_ally = best
		FOURTH.ab_caster_su = FOURTH.ab_fresh_friend_su(unit)
		FOURTH.ab_ally_su = FOURTH.ab_fresh_friend_su(best)
		FOURTH.cast_target = best
	end
	%RET_VASSAL%
end

'''
LIVE_RET = {
    "%NO%": "nil",
    "%RET_STRIKE%": ('local etype = "enemy"\n'
                     '\tpcall(function() etype = tostring(best.unit:type()) end)\n'
                     '\tlocal d = FOURTH.eg_enemy_gap(unit, best.unit)\n'
                     '\treturn string.format("strike on the most valuable standing single enemy (targeting %s): value %.0f; none of "\n'
                     '\t\t.. "ours within %sm; on the ground under it; distance %sm bound %sm", etype, bv,\n'
                     '\t\ttostring(row.r + row.buf + FOURTH.SHOT_SAFE_M), (d ~= nil) and string.format("%.1f", d) or "?",\n'
                     '\t\ttostring(FOURTH.eg_range_m))'),
    "%RET_VASSAL%": ('local atype = "ally"\n'
                     '\tpcall(function() atype = tostring(best:type()) end)\n'
                     '\treturn string.format("the most enemy value around %s (%s): value %.0f, %d enemy soldiers in the %sm blast "\n'
                     '\t\t.. "(line %d); distance %sm bound %sm", (best == unit) and "the caster" or "an ally", atype, bv,\n'
                     '\t\tmath.floor(bs + 0.5), tostring(row.r), FOURTH.blob_need(row.r),\n'
                     '\t\t(bg ~= nil) and string.format("%.1f", bg) or "?", tostring(reach))'),
}
ANN_RET = {"%NO%": "false", "%RET_STRIKE%": "return true", "%RET_VASSAL%": "return true"}


def render(tpl, rep):
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    assert "%NO%" not in tpl and "%RET_" not in tpl
    return tpl


MAP_OLD = "\tenemy_wander = FOURTH.evaluate_enemy_wander,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 163\n\tenemy_strike = FOURTH.evaluate_enemy_strike,\n\tally_blast = FOURTH.evaluate_ally_blast,\n"
TIP_ANCHOR = ('\tenemy_wander = "When armed and standing still, fires at a standing enemy blob worth the most, with none of our '
              'units within the blast\'s wandering reach",\n')
TIP_NEW = TIP_ANCHOR + (
    '\tenemy_strike = "When armed and standing still, strikes the ground under the most valuable standing single enemy, '
    'with none of our units near",\n'
    '\tally_blast = "When armed, fires on the friendly unit (or itself) with the most enemy value around it",\n')
ANCHOR = "FOURTH.evaluators = {\n"
WW_END = "FOURTH.load_ww_table()\n"
WW_GEN = re.compile(r"-- GENERATED by tools/gen_ww_tables\.py.*?\nFOURTH\.load_ww_table\(\)\n", re.S)
SHOT_GEN = re.compile(r"-- GENERATED by tools/gen_shot_tables\.py from unit_spec_abil.*?\nFOURTH\.load_area_table\(\)\n", re.S)

for path, live in ((SRC, True), (ANN, False)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "function FOURTH.evaluate_enemy_strike(" not in s and "FOURTH.EXPENDABLE_TEXT" not in s
    for r in ROWS:
        assert ('marker = "%s"' % r[0]) not in s, r[0]
    no = "nil" if live else "false"
    before = s.count("\t{ marker = ")
    for a, b in ((RESTOCK, NEW_ENTRIES + RESTOCK), (WIND_OLD, WIND_NEW), (HOLD_OLD, HOLD_NEW), (OURS_OLD, OURS_NEW),
                 (STILL_OLD1, STILL_NEW1), (STILL_OLD2, STILL_NEW2),
                 (WANDER_GUARD_OLD.replace("%NO%", no), WANDER_GUARD_NEW.replace("%NO%", no)),
                 (MAP_OLD, MAP_NEW), (TIP_ANCHOR, TIP_NEW),
                 (ANCHOR, render(EVALS, LIVE_RET if live else ANN_RET) + ANCHOR)):
        assert s.count(a) == 1, (path[-12:], a[:70], s.count(a))
        s = s.replace(a, b)
    assert s.count("\t{ marker = ") == before + 26
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "entries", before, "->", before + 26)

src_now = open(SRC, encoding="utf-8").read()
kf = GW.keys_in(src_now)
assert len(kf) == 56, len(kf)
ww_block = GW.lua_block(GW.derive(kf)) + GE.lua_block(GE.derive())
ks = GS.keys_in(src_now)
assert len(ks) == 36, len(ks)
area_keys = set(m.group(1) for m in re.finditer(
    r'trigger = "enemy_area_drain",\n\t\tbadge = "[^"]+",\n\t\tkeys = \{ "([^"]+)" \}', src_now))
assert len(area_keys) == 8
shot_block = (GS.lua_block(GS.derive(ks)) + GS.exec_block(GS.exec_rows(set(ks)))
              + GS.area_block(GS.area_rows(area_keys)))
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert len(WW_GEN.findall(s)) == 1 and len(SHOT_GEN.findall(s)) == 1
    s = WW_GEN.sub(lambda m: ww_block, s)
    s = SHOT_GEN.sub(lambda m: shot_block, s)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("WW table (56 keys) + EXPENDABLE (%d units) + SHOT (36) / AREA (8) re-derived" % len(GE.derive()))

import gen_recharge_keys as G  # noqa: E402
new_block = G.lua_block(G.derive())
pat = re.compile(r"-- GENERATED by tools/gen_recharge_keys\.py.*?\nFOURTH\.load_recharge\(\)\n", re.S)
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert len(pat.findall(s)) == 1
    s = pat.sub(lambda m: new_block, s)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("lock table re-derived:", len(G.derive()), "keys")
