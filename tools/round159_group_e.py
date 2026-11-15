#!/usr/bin/env python3
"""Round 159 (harness 158): group E - the self-centred blasts, buffs and hexes (26 entries / 28 keys; 4 new families).

User rulings 2026-11-15 (earlier status "excluded (auto: vortex)", the 2026-10-09 R3 auto-exclusion, not user decisions;
Sword of Teclis's own 2026-10-08 skip is kept):
  * 13 blasts that cannot hurt our troops (Burp of Grom x3, Blood-Forged Armour, Daemon Flask of Ashak, Feaster of
    Souls, Spurting Bile-Blood, Arsebelcher, Violent Wind, Whirlwind of Pleasure, Whirl of Weeping Blades, Hurricane of
    Death, Acid Burps): "Like Bloodstorm" -> melee_unwavering.
  * 5 blasts that DO hurt our troops (Groundbreaker, Burning Rage, Bloodbeast, Emergency Vent, Land Mine): "Melee, no
    friend near" -> NEW melee_clear: in melee and not wavering AND none of our other units within the blast radius
    (GENERATED FOURTH.VORTEX_R) + SHOT_SAFE_M of the caster's centre.
  * the Phoenix dives (Emberstorm, Moon Flare; the game's grounded rule): "Flying over enemies" -> NEW fly_dive: flying
    (exact true), a visible enemy within 70% of the blast radius of the caster's centre, none of ours within radius +
    SHOT_SAFE_M.
  * buffs and hexes, "Look-alike set": Maneater Smoke Bomb charge_or_melee; Verminous Valour wavering_self; Heaven's
    Flash enemy_ground_melee; Slime Smoothie health_aura_ground; Slann Gold enemy_commander_value (commander);
    Deathmaster's Sigil enemy_commander_value with the NEW class commander_ground and the target kept blast + SHOT_SAFE_M
    clear of our units; Ancient Chaos Frost Dragon Scale on NEW enemy_blob_vortex (evaluate_enemy_blob with the vortex
    radius).
  * "Close 5, Necrotic last": Necrotic Explosion on NEW last_stand_clear (health at or below LAST_STAND_PCT in melee,
    none of ours within blast + SHOT_SAFE_M). Mist Form, Shadowstrider, Deep Tunneling, Sword of Teclis and the
    Unidentified Hydra Head are closed in the tracker (no code).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_shot_tables as GS  # noqa: E402
import gen_vortex_tables as GV  # noqa: E402
import gamedata_paths as GP  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"


def sub(s, a, b, n=1):
    assert s.count(a) == n, (a[:80], s.count(a))
    return s.replace(a, b)


def entry(marker, name, trig, keys, extra):
    lines = ['\t{ marker = "%s", name = "%s", trigger = "%s",' % (marker, name, trig),
             '\t\tbadge = "zz_auto_badge_%s",' % marker,
             '\t\tkeys = { %s },' % ", ".join('"%s"' % k for k in keys)]
    lines += ["\t\t%s," % e for e in extra]
    lines += ["\t\tox = 0, oy = 0 },"]
    return "\n".join(lines) + "\n"


MU, MC, FD = "melee_unwavering", "melee_clear", "fly_dive"
ROWS = [
    # the 13 safe blasts (11 entries)
    ("burp_of_grom", "Burp of Grom", MU, ["wh2_dlc15_character_abilities_burp_of_grom_0",
                                          "wh2_dlc15_character_abilities_burp_of_grom_1",
                                          "wh2_dlc15_character_abilities_burp_of_grom_2"], []),
    ("blood_forged_armour", "Blood-Forged Armour", MU, ["wh2_dlc15_item_abilities_blood_forged_armour"], []),
    ("daemon_flask_of_ashak", "Daemon Flask of Ashak", MU, ["wh3_dlc23_item_abilities_daemon_flask_of_ashak"], []),
    ("feaster_of_souls", "Feaster of Souls", MU, ["wh3_dlc29_mount_abilities_feaster_of_souls"], []),
    ("spurting_bile_blood", "Spurting Bile-Blood", MU, ["wh3_dlc27_item_abilities_spurting_bile_blood"], []),
    ("arsebelcher", "Arsebelcher", MU, ["wh3_main_character_abilities_arsebelcher"], []),
    ("violent_wind", "Violent Wind", MU, ["wh3_dlc20_unit_abilities_violent_wind"], []),
    ("whirlwind_of_pleasure", "Whirlwind of Pleasure", MU, ["wh3_dlc27_lord_abilities_whirlwind_of_pleasure"], []),
    ("whirl_of_weeping_blades", "Whirl of Weeping Blades", MU, ["wh2_dlc14_weapon_abilities_whirl_of_weeping_blades"],
     []),
    ("hurricane_of_death", "Hurricane of Death", MU, ["wh3_dlc25_character_abilities_hurricane_of_death"], []),
    ("acid_burps", "Acid Burps", MU, ["wh3_dlc26_unit_abilities_acid_vomit"], []),
    # the 5 friendly-fire blasts
    ("groundbreaker", "Groundbreaker", MC, ["wh3_main_character_abilities_groundbreaker"], []),
    ("burning_rage", "Burning Rage", MC, ["wh3_main_lord_abilities_burning_rage"], []),
    ("bloodbeast", "Bloodbeast", MC, ["wh2_dlc17_lord_abilities_bloodbeast"], []),
    ("emergency_vent", "Emergency Vent", MC, ["wh2_dlc13_unit_abilities_emergency_vent"], []),
    ("land_mine", "Land Mine", MC, ["wh3_dlc25_unit_abilities_marienburg_land_mines"], []),
    # the Phoenix dives
    ("emberstorm", "Emberstorm", FD, ["wh2_dlc15_unit_abilities_emberstorm"], []),
    ("moon_flare", "Moon Flare", FD, ["wh3_dlc24_unit_abilities_moon_flare"], []),
    # buffs and hexes
    ("maneater_smoke_bomb", "Maneater Smoke Bomb", "charge_or_melee", ["wh3_dlc26_unit_abilities_maneater_smoke_bomb"],
     []),
    ("verminous_valour", "Verminous Valour", "wavering_self", ["wh2_main_character_abilities_verminous_valour"], []),
    ("heavens_flash", "Heaven's Flash", "enemy_ground_melee", ["wh3_main_unit_abilities_stun_bomb"], ["range_real = 75"]),
    ("slime_smoothie", "Slime Smoothie", "health_aura_ground", ["wh2_dlc15_character_abilities_slimy_smoothie"],
     ["aura_real = 35"]),
    ("slann_gold", "Slann Gold", "enemy_commander_value", ["wh2_dlc11_item_abilities_slann_gold"],
     ["range_real = 200", 'target_class = "commander"']),
    ("deathmasters_sigil", "Deathmaster's Sigil", "enemy_commander_value", ["wh2_dlc14_lord_abilities_deathmasters_sigil"],
     ["range_real = 100", 'target_class = "commander_ground"']),
    ("frost_dragon_scale", "Ancient Chaos Frost Dragon Scale", "enemy_blob_vortex",
     ["wh_dlc08_item_abilities_ancient_frost_wyrm_scale"], ["range_real = 30"]),
    # the last stand
    ("necrotic_explosion", "Necrotic Explosion", "last_stand_clear", ["wh3_main_unit_abilities_necrotic_explosion"], []),
]
KEYS = [k for r in ROWS for k in r[3]]
assert len(ROWS) == 26 and len(KEYS) == 28
NEW_ENTRIES = "".join(entry(*r) for r in ROWS)


def tsv(n):
    f = open(os.path.join(GP.GAMEDATA, n), encoding="utf-8-sig")
    h = f.readline().rstrip("\n").split("\t")
    f.readline()
    return [dict(zip(h, l.rstrip("\n").split("\t"))) for l in f]


USA = {r["key"]: r for r in tsv("unit_spec_abil.tsv")}


def num(v):
    f = float(v)
    return str(int(f)) if f == int(f) else ("%.3f" % f).rstrip("0").rstrip(".")


HOLD = [(k, num(USA[k]["recharge_time"])) for k in KEYS if int(float(USA[k]["num_uses"])) > 1]
WIND = [(k, num(USA[k]["wind_up_time"])) for k in KEYS if float(USA[k]["wind_up_time"]) > 0]
print("multi-use keys:", len(HOLD), HOLD)
print("wind-up keys:", len(WIND), WIND)

RESTOCK = '\t{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",'
WIND_OLD = "\twind_up_s = {\n"
WIND_NEW = WIND_OLD + "\t\t-- ROUND 159: group E's wind-ups (unit_spec_abil wind_up_time)\n" + "".join(
    '\t\t["%s"] = %s,\n' % (k, v) for k, v in WIND)
HOLD_OLD = "\thold_s = {\n"
HOLD_NEW = HOLD_OLD + ("\t\t-- ROUND 159: group E's abilities with more than one use (recharge_time; Spurting Bile-Blood's\n"
                       "\t\t-- table recharge is 0)\n") + "".join('\t\t["%s"] = %s,\n' % (k, v) for k, v in HOLD)

# Deathmaster's Sigil: the game's unit_is_not_commander_class + flying_currently
CLS_OLD = ('\tlocal cls = FOURTH.eg_class\n'
           '\tif cls == nil then return true end\n'
           '\tlocal t = FOURTH.type_plain(enemy)\n'
           '\tif cls == "commander" then\n')
CLS_NEW = ('\tlocal cls = FOURTH.eg_class\n'
           '\tif cls == nil then return true end\n'
           '\tlocal t = FOURTH.type_plain(enemy)\n'
           '\t-- ROUND 159: Deathmaster\'s Sigil (the game: unit_is_not_commander_class and flying_currently) - a Lord or\n'
           '\t-- Hero that is not flying; only an exact false passes\n'
           '\tif cls == "commander_ground" then\n'
           '\t\tlocal ok_f, fly = pcall(function() return enemy:is_currently_flying() end)\n'
           '\t\tif not (ok_f and fly == false) then return false end\n'
           '\t\tcls = "commander"\n'
           '\tend\n'
           '\tif cls == "commander" then\n')
SAFE_OLD = ('\tif nosafe then return true end\n'
            '\tlocal g = FOURTH.blob_friend_gap(e, m, FOURTH.SHOT_SAFE_M)\n'
            '\treturn g == nil or g > FOURTH.SHOT_SAFE_M\n')
SAFE_NEW = ('\tif nosafe then return true end\n'
            '\t-- ROUND 159: an entry whose own blast lands on the target (Deathmaster\'s Sigil) keeps blast + SHOT_SAFE_M\n'
            '\tlocal safe = FOURTH.SHOT_SAFE_M + (FOURTH.entry_blast_r() or 0)\n'
            '\tlocal g = FOURTH.blob_friend_gap(e, m, safe)\n'
            '\treturn g == nil or g > safe\n')
REASON_OLD = '\tlocal safe = string.format("none of ours within %dm", FOURTH.SHOT_SAFE_M)\n'
REASON_NEW = ('\tlocal safe = string.format("none of ours within %dm", FOURTH.SHOT_SAFE_M + (FOURTH.entry_blast_r() or 0))'
              '   -- ROUND 159\n')
CV_OLD = ('\tlocal e, s = FOURTH.shot_pick(unit, m, "value", false, true)\n'
          '\tif e == nil then return %NO% end\n'
          '\tFOURTH.shot_take(unit, e, "value", false, true)\n')
CV_NEW = ('\t-- ROUND 159: a blast that hits our units too (Deathmaster\'s Sigil: the VORTEX table) keeps the target safe\n'
          '\tlocal nosafe = (FOURTH.entry_blast_r() == nil)\n'
          '\tlocal e, s = FOURTH.shot_pick(unit, m, "value", false, nosafe)\n'
          '\tif e == nil then return %NO% end\n'
          '\tFOURTH.shot_take(unit, e, "value", false, nosafe)\n')
BLOB_OLD = ('\tlocal r = key and FOURTH.BLAST_R[key]\n'
            '\tif r == nil then return %NO% end\n')
BLOB_NEW = ('\tlocal r = key and FOURTH.BLAST_R[key]\n'
            '\tif r == nil and key ~= nil then r = FOURTH.VORTEX_R[key] end   -- ROUND 159: a vortex blast (enemy_blob_vortex)\n'
            '\tif r == nil then return %NO% end\n')

EVALS = r'''-- ============================================================================
-- ROUND 159 - GROUP E: THE SELF-CENTRED BLASTS (user rulings 2026-11-15).
--   melee_clear ("Melee, no friend near"; Groundbreaker, Burning Rage,
--     Bloodbeast, Emergency Vent, Land Mine: the game marks their blasts
--     affects_allies): the caster in melee and not wavering (the
--     melee_unwavering rule) AND none of our OTHER units' rectangles within the
--     blast radius (the GENERATED VORTEX table) + SHOT_SAFE_M of its centre.
--   fly_dive ("Flying over enemies"; Emberstorm, Moon Flare: the game's grounded
--     rule, the caster must fly): is_currently_flying() exactly true, a visible
--     enemy rectangle within 70% of the blast radius of the caster's centre, and
--     none of our other units within the blast radius + SHOT_SAFE_M.
--   last_stand_clear ("Close 5, Necrotic last"; Necrotic Explosion: the
--     Nurglings destroy themselves): own health at or below LAST_STAND_PCT while
--     in melee (an exact true), and none of ours within blast + SHOT_SAFE_M.
--   enemy_blob_vortex (Ancient Chaos Frost Dragon Scale, "a blob attack"): the
--     enemy_blob evaluator with the vortex radius in place of a projectile blast.
--   enemy_commander_value keeps its target blast + SHOT_SAFE_M clear of our units
--     when the entry's blast hits allies (Deathmaster's Sigil).
--   Every read fails closed: an unreadable position, flight or health never fires.
-- ============================================================================
-- the current entry's blast radius from the GENERATED VORTEX table (nil: none)
function FOURTH.entry_blast_r()
	local key = FOURTH.rc_self_keys and FOURTH.rc_self_keys[1]
	return key and FOURTH.VORTEX_R[key]
end

-- the caster's centre on the ground plane (x, z); nil when unreadable
function FOURTH.self_xz(unit)
	local x, z = nil, nil
	pcall(function()
		local p = unit:position()
		x, z = p:get_x(), p:get_z()
	end)
	if type(x) ~= "number" or type(z) ~= "number" then return nil end
	return x, z
end

-- the closest of our OTHER units (its rectangle) to the caster's centre: readable, gap (nil = none of ours)
function FOURTH.self_friend_gap(unit, m)
	local x, z = FOURTH.self_xz(unit)
	if x == nil then return false, nil end
	local id = nil
	pcall(function() id = tostring(unit:unique_ui_id()) end)
	if id == nil then return false, nil end
	local best = nil
	for i = 1, #m.ours do
		local o = m.ours[i]
		local oid = nil
		pcall(function() oid = tostring(o.unit:unique_ui_id()) end)
		if oid ~= id then
			local g = FOURTH.blob_rect_gap(x, z, o)
			if best == nil or g < best then best = g end
		end
	end
	return true, best
end

-- none of our other units within the blast + SHOT_SAFE_M of the caster: ok, the log text
function FOURTH.self_clear(unit, r)
	local m = FOURTH.blob_map(false)
	local ok, g = FOURTH.self_friend_gap(unit, m)
	if not ok then return false, nil end
	local need = r + FOURTH.SHOT_SAFE_M
	if g ~= nil and g <= need then return false, nil end
	if g == nil then return true, string.format("none of our other units on the map (needs > %sm)", tostring(need)) end
	return true, string.format("closest of our other units %.1fm (needs > %sm)", g, tostring(need))
end

function FOURTH.evaluate_melee_clear(unit, routing)
	local r = FOURTH.entry_blast_r()
	if r == nil then return %NO% end
	local why = FOURTH.evaluate_in_melee_self(unit, routing)
	if not why then return %NO% end
	local ok, txt = FOURTH.self_clear(unit, r)
	if not ok then return %NO% end
	%RET_MC%
end

function FOURTH.evaluate_fly_dive(unit, routing)
	local r = FOURTH.entry_blast_r()
	if routing or r == nil then return %NO% end
	local ok_f, fly = pcall(function() return unit:is_currently_flying() end)
	if not (ok_f and fly == true) then return %NO% end
	local x, z = FOURTH.self_xz(unit)
	if x == nil then return %NO% end
	local reach = math.floor(r * FOURTH.RANGE_FRACTION + 1e-9)
	local m = FOURTH.blob_map(false)
	local best, bg = nil, nil
	for i = 1, #m.all do
		local e = m.all[i]
		local g = FOURTH.blob_rect_gap(x, z, e)
		if g <= reach and (bg == nil or g < bg) then best, bg = e, g end
	end
	if best == nil then return %NO% end
	local ok, txt = FOURTH.self_clear(unit, r)
	if not ok then return %NO% end
	%RET_FD%
end

function FOURTH.evaluate_last_stand_clear(unit, routing)
	local r = FOURTH.entry_blast_r()
	if routing or r == nil then return %NO% end
	local hp = FOURTH.health_pct(unit)
	if type(hp) ~= "number" or hp > FOURTH.LAST_STAND_PCT then return %NO% end
	if FOURTH.ah_in_melee(unit) ~= true then return %NO% end
	local ok, txt = FOURTH.self_clear(unit, r)
	if not ok then return %NO% end
	%RET_LS%
end

'''
LIVE_RET = {
    "%NO%": "nil",
    "%RET_MC%": ('return why .. string.format("; the %sm blast hits our units too: ", tostring(r)) .. txt'),
    "%RET_FD%": ('local etype = "enemy"\n'
                 '\tpcall(function() etype = tostring(best.unit:type()) end)\n'
                 '\treturn string.format("flying over %s (%.1fm from the centre, within %dm = 70%% of the %sm blast); ",\n'
                 '\t\tetype, bg, reach, tostring(r)) .. txt'),
    "%RET_LS%": ('return string.format("last stand: health %d%% (<= %d%%) in melee, the %sm blast destroys this unit; ",\n'
                 '\t\tmath.floor(hp), FOURTH.LAST_STAND_PCT, tostring(r)) .. txt'),
}
ANN_RET = {"%NO%": "false", "%RET_MC%": "return true", "%RET_FD%": "return true", "%RET_LS%": "return true"}


def render(tpl, rep):
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    assert "%NO%" not in tpl and "%RET_" not in tpl
    return tpl


FAMS = ["melee_clear", "fly_dive", "last_stand_clear"]
MAP_OLD = "\tenemy_commander_value = FOURTH.evaluate_enemy_commander_value,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 159\n" + "".join("\t%s = FOURTH.evaluate_%s,\n" % (f, f) for f in FAMS) + \
    "\tenemy_blob_vortex = FOURTH.evaluate_enemy_blob,\n"
TIP_OLD = '\tenemy_commander_value = "When armed, fires on the most valuable enemy lord or hero in range",\n'
TIPS = {
    "melee_clear": "When armed, fires when this unit is in melee and none of our other units are inside its blast",
    "fly_dive": "When armed, fires when this unit is flying over an enemy and none of our other units are inside its blast",
    "last_stand_clear": "When armed, fires when this unit is at 10% health or less in melee and none of our other units "
                        "are inside its blast",
    "enemy_blob_vortex": "When armed and standing still, fires at the enemy infantry where the blast destroys the most "
                         "value, when it hits enough soldiers and none of ours are near",
}
TIP_NEW = TIP_OLD + "".join('\t%s = "%s",\n' % (f, t) for f, t in TIPS.items())
ANCHOR = "FOURTH.evaluators = {\n"
GEN = re.compile(r"-- GENERATED by tools/gen_shot_tables\.py from unit_spec_abil.*?\nFOURTH\.load_area_table\(\)\n", re.S)

for path, live in ((SRC, True), (ANN, False)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "evaluate_melee_clear" not in s and "FOURTH.VORTEX_TEXT" not in s
    no = "nil" if live else "false"
    before = s.count("\t{ marker = ")
    s = sub(s, RESTOCK, NEW_ENTRIES + RESTOCK)
    s = sub(s, WIND_OLD, WIND_NEW)
    s = sub(s, HOLD_OLD, HOLD_NEW)
    s = sub(s, CLS_OLD, CLS_NEW)
    s = sub(s, SAFE_OLD, SAFE_NEW)
    if live:
        s = sub(s, REASON_OLD, REASON_NEW)
    s = sub(s, CV_OLD.replace("%NO%", no), CV_NEW.replace("%NO%", no))
    s = sub(s, BLOB_OLD.replace("%NO%", no), BLOB_NEW.replace("%NO%", no))
    s = sub(s, MAP_OLD, MAP_NEW)
    s = sub(s, TIP_OLD, TIP_NEW)
    s = sub(s, ANCHOR, render(EVALS, LIVE_RET if live else ANN_RET) + ANCHOR)
    assert s.count("\t{ marker = ") == before + 26
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "entries", before, "->", before + 26)

# the GENERATED tables: SHOT (+ Slann Gold, Deathmaster's Sigil on enemy_commander_value), EXEC, AREA unchanged in
# content; the NEW VORTEX table right after them
src_now = open(SRC, encoding="utf-8").read()
ks = GS.keys_in(src_now)
assert len(ks) == 35, len(ks)
area_keys = set(m.group(1) for m in re.finditer(
    r'trigger = "enemy_area_drain",\n\t\tbadge = "[^"]+",\n\t\tkeys = \{ "([^"]+)" \}', src_now))
assert len(area_keys) == 7
vrows = GV.derive(GV.keys_in(src_now))
print("VORTEX rows:", vrows)
assert len(vrows) == 10, len(vrows)
block = (GS.lua_block(GS.derive(ks)) + GS.exec_block(GS.exec_rows(set(ks)))
         + GS.area_block(GS.area_rows(area_keys)) + GV.lua_block(vrows))
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert len(GEN.findall(s)) == 1
    s = GEN.sub(lambda m: block, s)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("SHOT table re-derived (35 keys) + EXEC + AREA + VORTEX (10 keys)")

import gen_recharge_keys as G  # noqa: E402
new_block = G.lua_block(G.derive())
pat = re.compile(r"-- GENERATED by tools/gen_recharge_keys\.py.*?\nFOURTH\.load_recharge\(\)\n", re.S)
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert len(pat.findall(s)) == 1
    s = pat.sub(lambda m: new_block, s)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("lock table re-derived:", len(G.derive()), "keys")
