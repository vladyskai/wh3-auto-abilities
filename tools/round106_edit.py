# -*- coding: utf-8 -*-
"""Round 106 - the bombardment round: Soulfire/Arachneruption + the 32-list.

Applies ONE deterministic set of edits to BOTH the shipped source and the
annotated reference copy (which carries the same control flow WITHOUT log()).
Binary read/write so the shipped file stays LF (a text-mode write on Windows
would flip every newline to CRLF and break the build's byte-identity gate).
"""
import sys, hashlib

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

def read(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8")

def write(p, s):
    data = s.encode("utf-8")
    assert b"\r" not in data, "CR found - refusing to write " + p
    with open(p, "wb") as f:
        f.write(data)

def must(s, old, n=1):
    c = s.count(old)
    assert c == n, "anchor count %d (want %d): %r" % (c, n, old[:90])
    return s

# ---------------------------------------------------------------------------
# THE 30 IMPLEMENTED BOMBARDMENT ENTRIES (the 32 list minus Thorsen's
# Thunderstorm - army-bar - and Warp Lightning Rod - no enemy target at all).
# (marker, display name, keys, real range, ground-form?)
ENTRIES = [
    ("assault_of_stone", "Assault of Stone", ["wh2_dlc10_item_bound_assault_of_stone"], 200, True),
    ("axe_of_tor", "Axe of Tor", ["wh3_main_weapon_abilities_axe_of_tor"], 200, True),
    ("celestial_comet", "Celestial Comet", ["wh3_main_mount_bound_celestial_comet"], 200, True),
    ("celestial_lightning", "Celestial Lightning", ["wh3_main_mount_bound_celestial_lightning"], 300, True),
    ("chalice_of_potions", "Chalice of Potions", ["wh_dlc07_item_abilities_chalice_of_potions"], 200, True),
    ("comet_of_casandora", "Comet of Casandora", ["wh3_main_spell_bound_comet_of_casandora"], 200, True),
    ("dragon_ogres_great_horn", "Dragon Ogre's Great Horn", ["wh_dlc08_item_abilities_great_horn_of_dragon_ogre"], 200, True),
    ("flame_and_shadow", "Flame & Shadow", ["wh3_dlc23_lord_abilities_flame_and_shadow"], 100, True),
    ("hawks_talon", "Hawk's Talon", ["wh_dlc05_weapon_abilities_hawks_talon"], 200, True),
    ("ishas_rain", "Isha's Rain", ["wh2_dlc13_character_ability_ishas_rain"], 200, True),
    ("klad_brakak", "Klad Brakak", ["wh2_dlc17_spell_bound_urannons_thunderbolt_upgraded"], 30, True),
    ("lesser_doombolt", "Lesser Doombolt", ["wh2_dlc10_spell_bound_lesser_doombolt"], 200, False),
    ("lightning_strike", "Lightning Strike", ["wh3_dlc29_unit_abilities_lightning_strike"], 300, True),
    ("lord_of_the_storm", "Lord of the Storm", ["wh_main_lord_abilities_lord_of_the_storm"], 200, True),
    ("master_of_lightning", "Master of Lightning", ["wh3_dlc29_spell_bound_warp_lightning"], 200, True),
    ("meteor_strike", "Meteor Strike", ["wh3_dlc29_unit_abilities_meteor_strike"], 200, True),
    ("nemesis_crown", "Nemesis Crown", ["wh3_dlc25_lord_abilities_nemesis_crown"], 100, True),
    ("piercing_bolts_of_burning", "Piercing Bolts of Burning", ["wh_main_spell_bound_piercing_bolts_of_burning"], 200, True),
    ("pigeon_bomb", "Pigeon Bomb", ["wh3_dlc25_character_abilities_pigeon_bomb"], 200, True),
    ("rod_of_the_storm", "Rod of the Storm", ["wh2_main_spell_bound_rod_of_the_storm"], 300, True),
    ("rod_of_torment", "Rod of Torment", ["wh3_dlc20_item_abilities_rod_of_torment"], 200, False),
    ("sceptre_of_stone", "Sceptre of Stone", ["wh2_dlc10_item_abilities_sceptre_of_stone"], 200, True),
    ("searing_doom", "Searing Doom", ["wh3_twa08_spell_bound_searing_doom"], 200, True),
    ("slicing_shards", "Slicing Shards", ["wh3_dlc20_spell_bound_slicing_shards",
                                          "wh3_main_spell_slaanesh_slicing_shards_bound"], 200, True),
    ("the_bow_of_loren", "The Bow of Loren", ["wh_dlc05_weapon_abilities_the_bow_of_loren"], 200, True),
    ("tome_of_furion", "Tome of Furion", ["wh2_main_spell_bound_tome_of_furion"], 200, False),
    ("urannons_thunderbolt", "Urannon's Thunderbolt", ["wh2_dlc17_spell_bound_urannons_thunderbolt"], 300, True),
    ("wand_of_the_kharaidon", "Wand of the Kharaidon", ["wh2_main_spell_bound_wand_of_the_kharaidon"], 200, False),
    ("wolfs_howl", "Wolf's Howl", ["wh3_main_weapon_abilities_the_traitors_sword"], 200, False),
    ("wraith_storm", "Wraith Storm", ["wh2_dlc11_lord_abilities_wraith_storm"], 200, False),
]

def entries_block():
    out = []
    out.append("\t-- ======================================================================")
    out.append("\t-- ROUND 106 - THE BOMBARDMENT ROUND, family (1): Soulfire (both keys)")
    out.append("\t-- and Arachneruption on the NEW trigger melee_skip_commanders.")
    out.append("\t-- The user's rule: fire when the caster is IN MELEE, but SKIP when every")
    out.append("\t-- enemy it is fighting is a Lord or a Hero. Both rows are SELF-CENTRED")
    out.append("\t-- (target flags all false, target_intercept_range 0), so the cast is on")
    out.append("\t-- the OWNER through the unit form - there is no target to pick.")
    out.append("\t-- ======================================================================")
    out.append('\t{ marker = "soulfire", name = "Soulfire", trigger = "melee_skip_commanders",')
    out.append('\t\tbadge = "zz_auto_badge_soulfire",')
    out.append('\t\tkeys = { "wh_main_spell_bound_soulfire",')
    out.append('\t\t\t"wh_dlc04_spell_bound_soulfire_upgraded" },')
    out.append("\t\tox = 0, oy = 0 },")
    out.append('\t{ marker = "arachneruption", name = "Arachneruption", trigger = "melee_skip_commanders",')
    out.append('\t\tbadge = "zz_auto_badge_arachneruption",')
    out.append('\t\tkeys = { "wh2_dlc15_unit_abilities_arachneruption" },')
    out.append("\t\tox = 0, oy = 0 },")
    out.append("\t-- ======================================================================")
    out.append("\t-- ROUND 106 - THE BOMBARDMENT ROUND, family (2): the 30 approved")
    out.append("\t-- bombardment abilities on the NEW trigger enemy_ground_melee_infantry.")
    out.append("\t-- Trigger: the CLOSEST enemy inside the ability's own 70% bound, IN")
    out.append("\t-- MELEE, that IS INFANTRY (battle_unit:is_infantry, unit_class fallback,")
    out.append("\t-- fail-closed). Cast form follows EACH row's own flags: the 24")
    out.append("\t-- ground-targeted keys are placed on the chosen enemy's ground (they are")
    out.append("\t-- listed in FOURTH.enemy_ground_keys above); the 6 unit-targeted keys")
    out.append("\t-- (lesser_doombolt, rod_of_torment, tome_of_furion, wand_of_the_kharaidon,")
    out.append("\t-- wolfs_howl, wraith_storm) cast on the enemy unit itself. Two of the 32")
    out.append("\t-- are NOT here and are reported instead: Thorsen's Thunderstorm (both")
    out.append("\t-- keys sit in army_spec - an ARMY-bar ability, out of wheel scope) and")
    out.append("\t-- Warp Lightning Rod (target flags all false, range 0: it has no enemy")
    out.append("\t-- target at all, so no enemy-triggered cast can be issued).")
    out.append("\t-- ======================================================================")
    for marker, name, keys, rng, ground in ENTRIES:
        ks = ", ".join('"%s"' % k for k in keys)
        out.append('\t{ marker = "%s", name = "%s", trigger = "enemy_ground_melee_infantry",' % (marker, name))
        out.append('\t\tbadge = "zz_auto_badge_%s",' % marker)
        out.append("\t\tkeys = { %s }," % ks)
        out.append("\t\trange_real = %d," % rng)
        out.append("\t\tox = 0, oy = 0 },")
    return "\n".join(out) + "\n"

GROUND_KEYS = [e for e in ENTRIES if e[4]]

def ground_block():
    out = []
    out.append("\t\t-- ROUND 106: the 24 ground-targeted bombardment keys of the")
    out.append("\t\t-- enemy_ground_melee_infantry family - each cast PLACES the strike on the")
    out.append("\t\t-- chosen INFANTRY enemy's own ground through the ground form.")
    for marker, name, keys, rng, ground in GROUND_KEYS:
        for k in keys:
            out.append('\t\t["%s"] = true,' % k)
    return "\n".join(out) + "\n"

CHARGE = [
    ("wh3_main_weapon_abilities_axe_of_tor", 90),
    ("wh3_main_mount_bound_celestial_comet", 49),
    ("wh3_main_mount_bound_celestial_lightning", 42),
    ("wh_dlc07_item_abilities_chalice_of_potions", 120),
    ("wh_dlc08_item_abilities_great_horn_of_dragon_ogre", 120),
    ("wh3_dlc23_lord_abilities_flame_and_shadow", 90),
    ("wh_dlc05_weapon_abilities_hawks_talon", 90),
    ("wh2_dlc13_character_ability_ishas_rain", 120),
    ("wh2_dlc10_spell_bound_lesser_doombolt", 90),
    ("wh3_dlc29_unit_abilities_lightning_strike", 42),
    ("wh_main_lord_abilities_lord_of_the_storm", 90),
    ("wh3_dlc29_spell_bound_warp_lightning", 30),
    ("wh3_dlc29_unit_abilities_meteor_strike", 49),
    ("wh_main_spell_bound_piercing_bolts_of_burning", 120),
    ("wh3_dlc25_character_abilities_pigeon_bomb", 120),
    ("wh2_main_spell_bound_rod_of_the_storm", 90),
    ("wh3_dlc20_item_abilities_rod_of_torment", 90),
    ("wh2_dlc10_item_abilities_sceptre_of_stone", 90),
    ("wh3_twa08_spell_bound_searing_doom", 60),
    ("wh2_main_spell_bound_tome_of_furion", 60),
    ("wh2_dlc17_spell_bound_urannons_thunderbolt", 90),
    ("wh2_main_spell_bound_wand_of_the_kharaidon", 120),
    ("wh3_main_weapon_abilities_the_traitors_sword", 90),
    ("wh2_dlc11_lord_abilities_wraith_storm", 90),
    ("wh2_dlc15_unit_abilities_arachneruption", 90),
]

WINDUP = [
    ("wh2_dlc10_item_bound_assault_of_stone", 3),
    ("wh3_main_weapon_abilities_axe_of_tor", 3),
    ("wh3_main_mount_bound_celestial_comet", 5),
    ("wh3_main_mount_bound_celestial_lightning", 3),
    ("wh_dlc07_item_abilities_chalice_of_potions", 5),
    ("wh3_main_spell_bound_comet_of_casandora", 5),
    ("wh3_dlc23_lord_abilities_flame_and_shadow", 3),
    ("wh_dlc05_weapon_abilities_hawks_talon", 3),
    ("wh2_dlc13_character_ability_ishas_rain", 3),
    ("wh2_dlc17_spell_bound_urannons_thunderbolt_upgraded", 3),
    ("wh2_dlc10_spell_bound_lesser_doombolt", 3),
    ("wh3_dlc29_unit_abilities_lightning_strike", 3),
    ("wh_main_lord_abilities_lord_of_the_storm", 1),
    ("wh3_dlc29_spell_bound_warp_lightning", 1),
    ("wh3_dlc29_unit_abilities_meteor_strike", 5),
    ("wh3_dlc25_lord_abilities_nemesis_crown", 6),
    ("wh2_main_spell_bound_rod_of_the_storm", 3),
    ("wh3_dlc20_item_abilities_rod_of_torment", 3),
    ("wh2_dlc10_item_abilities_sceptre_of_stone", 5),
    ("wh3_twa08_spell_bound_searing_doom", 1),
    ("wh3_dlc20_spell_bound_slicing_shards", 5),
    ("wh3_main_spell_slaanesh_slicing_shards_bound", 5),
    ("wh_dlc05_weapon_abilities_the_bow_of_loren", 3),
    ("wh2_main_spell_bound_tome_of_furion", 5),
    ("wh2_dlc17_spell_bound_urannons_thunderbolt", 3),
    ("wh2_main_spell_bound_wand_of_the_kharaidon", 5),
    ("wh2_dlc11_lord_abilities_wraith_storm", 3),
    ("wh_main_spell_bound_soulfire", 1),
    ("wh_dlc04_spell_bound_soulfire_upgraded", 1),
]

def table_block(rows, note):
    out = ["\t\t-- " + note]
    for k, v in rows:
        out.append('\t\t["%s"] = %s,' % (k, v))
    return "\n".join(out) + "\n"

HELPERS_COMMON_HEAD = r'''
-- ============================================================================
-- ROUND 106 - THE BOMBARDMENT ROUND: the two approved families' helpers.
--
-- (1) melee_skip_commanders - Soulfire (2 keys) and Arachneruption.
--     The user's rule: fire when the caster is IN MELEE, but SKIP when the
--     caster is fighting ONLY a Lord or a Hero. The engagement set is read
--     from the game's own enemy enumerator: every ALIVE enemy that reports
--     is_in_melee() == true and whose edge-to-edge unit_distance() to the
--     caster is within FOURTH.ENGAGE_CONTACT_M (12 m - melee CONTACT for
--     bounding boxes, the same primitive the range rule uses everywhere).
--     Each member is classified by FOURTH.enemy_is_commander (the 1,409-key
--     derived set, unit_class() == "com" fallback, FAIL CLOSED).
--     The judged set is LOGGED once per (unit, marker) and again only when it
--     CHANGES - type, commander flag and the REAL distance - so the rule is
--     auditable in the field log without flooding it.
--     When NO enemy can be read as engaged, the caster's own current_target()
--     is the fallback; when that is absent too the ability fires on the plain
--     in-melee rule (the older behaviour) and says so.
--
-- (2) enemy_ground_melee_infantry - the 30 bombardment abilities of the
--     approved list. Trigger: the CLOSEST enemy inside the ability's own 70%
--     bound that is IN MELEE and IS INFANTRY.
--     INFANTRY IS A REAL READ: battle_unit:is_infantry() (API dump: "Returns
--     whether this is a unit of infantry"), with battle_unit:unit_class() as
--     the fallback - EXACT equality against the three land_units infantry
--     classes (inf_mel / inf_mis / inf_spr) - and FAIL CLOSED when neither
--     answers. This is the same READ-first discipline as the commander set;
--     a derived 942-key land_units list would also work but would miss every
--     DLC unit whose key is not in it, while the engine read cannot.
--     The cast follows EACH ability's own targeting data: a ground-targeted
--     key is placed with perform_special_ability_ground(key, enemy position);
--     a unit-targeted key goes through perform_special_ability(key, enemy).
--     The chosen enemy is re-checked immediately before the cast (alive, in
--     melee, still infantry, still inside the bound).
--
-- NO NEW CHUNK-LEVEL LOCALS: every table, counter and function below is a
-- field of the FOURTH bag (the main chunk sits at Lua's 200-local ceiling).
-- ============================================================================
FOURTH.ENGAGE_CONTACT_M = 12
FOURTH.engage_note = {}
FOURTH.infantry_unreadable_logged = false

-- true / false - IS THIS ENEMY INFANTRY? The engine's own read first, the
-- land_units class second (EXACT string equality - no substring search anywhere),
-- FAIL CLOSED (not infantry) when neither answers.
function FOURTH.enemy_is_infantry(enemy)
	local ok, v = pcall(function() return enemy:is_infantry() end)
	if ok then
		if v == true then return true end
		if v == false then return false end
	end
	local ok2, cls = pcall(function() return enemy:unit_class() end)
	if ok2 and type(cls) == "string" and cls ~= "" then
		return (cls == "inf_mel") or (cls == "inf_mis") or (cls == "inf_spr")
	end
	LOG_INF_UNREADABLE
	return false
end

-- ONE read of the enemy enumerator (the collection every enemy trigger uses).
-- Returns members (each { unit, type, commander, gap }), the count of
-- NON-COMMANDER members; nil, nil when the enumerator itself cannot be read.
function FOURTH.engagement_set(unit)
	local ok_coll, coll = pcall(function()
		return bm:get_scriptunits_for_main_enemy_army_to_local_player()
	end)
	if not ok_coll or coll == nil then return nil, nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil, nil end
	local members, noncmd = {}, 0
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		if ok_su and su ~= nil then
			local enemy = nil
			pcall(function() enemy = su.unit end)
			if enemy ~= nil then
				local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
				local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)
				local gap = nil
				local ok_gap, g = pcall(function() return unit:unit_distance(enemy) end)
				if ok_gap and type(g) == "number" then gap = g end
				if ok_alive and type(alive) == "number" and alive > 0
					and ok_melee and melee == true
					and (gap == nil or gap <= FOURTH.ENGAGE_CONTACT_M) then
					local etype = FOURTH.type_plain(enemy) or "enemy"
					local cmdr = FOURTH.enemy_is_commander(enemy)
					members[#members + 1] = { unit = enemy, type = etype, commander = cmdr, gap = gap }
					if not cmdr then noncmd = noncmd + 1 end
				end
			end
		end
	end
	return members, noncmd
end

-- RECORD THE JUDGED SET once, then only on a CHANGE (dedupe by note text).
function FOURTH.note_engagement(unit, marker, note)
	local ok_id, id = pcall(function() return unit:unique_ui_id() end)
	if not ok_id or id == nil then return end
	local slot = tostring(id)
	local per = FOURTH.engage_note[slot]
	if per == nil then per = {}; FOURTH.engage_note[slot] = per end
	if per[marker] == note then return end
	per[marker] = note
	LOG_ENGAGE
end

-- THE SOULFIRE / ARACHNERUPTION TRIGGER.
function FOURTH.evaluate_melee_skip_commanders(unit, routing)
	if routing then return nil end
	local ok_melee, melee = pcall(function() return unit:is_in_melee() end)
	if not (ok_melee and melee == true) then return nil end
	local marker = FOURTH.eg_marker or "ability"
	local members, noncmd = FOURTH.engagement_set(unit)
	local note, reason
	if members == nil then
		note = "engagement set UNREADABLE (the enemy enumerator failed) - plain in-melee rule"
		reason = "in melee (engagement set unreadable - plain in-melee rule)"
	elseif #members == 0 then
		local ok_t, t = pcall(function() return unit:current_target() end)
		if ok_t and t ~= nil then
			local cmdr = FOURTH.enemy_is_commander(t)
			local tt = FOURTH.type_plain(t) or "enemy"
			if cmdr then
				note = "no enemy in contact - current_target '" .. tt
					.. "' is a COMMANDER (Lord/Hero) -> HOLDING"
				FOURTH.note_engagement(unit, marker, note)
				return nil
			end
			note = "no enemy in contact - current_target '" .. tt
				.. "' is not a commander -> firing"
			reason = "in melee - the current target ('" .. tt .. "') is not a Lord or Hero"
		else
			note = "no enemy readable in contact and no current target - plain in-melee rule (older behaviour)"
			reason = "in melee (engagement set unreadable - plain in-melee rule)"
		end
	else
		local parts = {}
		for i = 1, #members do
			local m = members[i]
			parts[#parts + 1] = "'" .. m.type .. "' "
				.. (m.commander and "COMMANDER" or "non-commander")
				.. ((m.gap ~= nil) and (" " .. string.format("%.1f", m.gap) .. "m") or " ?m")
		end
		if noncmd == 0 then
			note = "engagement set: " .. tostring(#members) .. " enemy unit(s) in contact (<= "
				.. tostring(FOURTH.ENGAGE_CONTACT_M) .. "m): " .. table.concat(parts, ", ")
				.. " -> HOLDING (every engaged enemy is a Lord or Hero)"
			FOURTH.note_engagement(unit, marker, note)
			return nil
		end
		note = "engagement set: " .. tostring(#members) .. " enemy unit(s) in contact (<= "
			.. tostring(FOURTH.ENGAGE_CONTACT_M) .. "m): " .. table.concat(parts, ", ")
			.. " -> FIRING (a non-commander is engaged)"
		reason = "in melee - " .. tostring(noncmd) .. " non-commander enemy unit(s) in contact"
	end
	FOURTH.note_engagement(unit, marker, note)
	return reason
end

-- THE BOMBARDMENT TRIGGER: closest in-melee INFANTRY enemy inside the bound,
-- cast at that enemy's own position in whichever form its row declares.
function FOURTH.evaluate_enemy_ground_melee_infantry(unit, routing)
	FOURTH.eg_melee_only = true
	return FOURTH.enc_pick_enemy(unit, routing, nil, "infantry")
end
'''

INF_UNREADABLE_SRC = ('\tif not FOURTH.infantry_unreadable_logged then\n'
                      '\t\tFOURTH.infantry_unreadable_logged = true\n'
                      '\t\tlog("infantry check: NEITHER is_infantry() NOR unit_class() could be read on an enemy -"\n'
                      '\t\t\t.. " treating it as NOT infantry (fail-closed). One-time notice.")\n'
                      '\tend')
ENGAGE_SRC = ('\tlog("  " .. tostring(marker) .. " " .. note)')
INF_UNREADABLE_ANN = '\t-- (annotated copy: the one-time unreadable notice is a log-only line)'
ENGAGE_ANN = '\t-- (annotated copy: the judged-set line is a log-only line)'


def helpers(src):
    s = HELPERS_COMMON_HEAD
    if src:
        s = s.replace("LOG_INF_UNREADABLE", INF_UNREADABLE_SRC).replace("LOG_ENGAGE", ENGAGE_SRC)
    else:
        s = s.replace("LOG_INF_UNREADABLE", INF_UNREADABLE_ANN).replace("LOG_ENGAGE", ENGAGE_ANN)
    return s


def apply(path, is_src):
    s = read(path)
    orig = s

    # --- A. the 300 m bound (real 300 -> floor(210)) --------------------------
    s = must(s, "FOURTH.ENEMY_CAST_R500 = 350\n")
    s = s.replace("FOURTH.ENEMY_CAST_R500 = 350\n",
                  "FOURTH.ENEMY_CAST_R300 = 210\nFOURTH.ENEMY_CAST_R500 = 350\n", 1)
    s = must(s, "\t[500] = FOURTH.ENEMY_CAST_R500,\n")
    s = s.replace("\t[500] = FOURTH.ENEMY_CAST_R500,\n",
                  "\t[300] = FOURTH.ENEMY_CAST_R300,\n\t[500] = FOURTH.ENEMY_CAST_R500,\n", 1)

    # --- B. the 24 enemy-GROUND keys -----------------------------------------
    anchor = ("\t\t[\"wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol_1\"] = true,\n"
              "\t},\n")
    s = must(s, anchor)
    s = s.replace(anchor, anchor[:-len("\t},\n")] + ground_block() + "\t},\n", 1)

    # --- C. the 30 entries (appended at the END of the ABILITIES table) ------
    if is_src:
        tail = "-- Every key from the table above"
    else:
        tail = "-- A flat list of every key above"
    anchor = "\t\tox = 0, oy = 0 },\n\n\n}\n\n" + tail
    s = must(s, anchor)
    s = s.replace(anchor,
                  "\t\tox = 0, oy = 0 },\n\n" + entries_block() + "}\n\n" + tail, 1)

    # --- D. charge gate -------------------------------------------------------
    anchor = "local charge_gate = {\n\thold_s = {\n"
    s = must(s, anchor)
    s = s.replace(anchor, anchor + table_block(CHARGE, "ROUND 106: the bombardment family's multi-use pools (num_uses > 1)") + "", 1)

    # --- E. cast gate ---------------------------------------------------------
    anchor = "local cast_gate = {\n\twind_up_s = {\n"
    s = must(s, anchor)
    s = s.replace(anchor, anchor + table_block(WINDUP, "ROUND 106: the bombardment family's wind-up times (wind_up_time > 0)") + "", 1)

    # --- F. evaluator map -----------------------------------------------------
    anchor = "\tally_winds = FOURTH.evaluate_ally_winds,\n}"
    s = must(s, anchor)
    s = s.replace(anchor,
                  "\tally_winds = FOURTH.evaluate_ally_winds,\n"
                  "\t-- ROUND 106: the two bombardment families.\n"
                  "\tmelee_skip_commanders = FOURTH.evaluate_melee_skip_commanders,\n"
                  "\tenemy_ground_melee_infantry = FOURTH.evaluate_enemy_ground_melee_infantry,\n}", 1)

    # --- G. tooltip sentences -------------------------------------------------
    anchor = '\tally_winds = "When armed, fires on the ally with the most hit points remaining, cast on that ally",\n}'
    s = must(s, anchor)
    s = s.replace(anchor,
                  '\tally_winds = "When armed, fires on the ally with the most hit points remaining, cast on that ally",\n'
                  '\tmelee_skip_commanders = "When armed, fires when this unit is in melee, unless every enemy it is fighting is a Lord or Hero",\n'
                  '\tenemy_ground_melee_infantry = "When armed, fires on the closest infantry unit in range that is fighting in melee",\n}', 1)

    # --- H. the helpers, immediately before the evaluator map -----------------
    anchor = "FOURTH.evaluators = {\n"
    s = must(s, anchor)
    s = s.replace(anchor, helpers(is_src) + "\n" + anchor, 1)

    # --- I. enc_pick_enemy: the infantry mode --------------------------------
    anchor = "\tFOURTH.eg_noncommander = true\n"
    s = must(s, anchor)
    s = s.replace(anchor, anchor + '\tFOURTH.eg_infantry = (mode == "infantry")\n', 1)

    anchor = ("\t\t\t\t\t\t\tif mode == \"health\" then\n"
              "\t\t\t\t\t\t\t\thp = FOURTH.enemy_health_pct(enemy)\n"
              "\t\t\t\t\t\t\t\tqualifies = (hp ~= nil and hp < FOURTH.HEALTH_LINE_PCT)\n"
              "\t\t\t\t\t\t\telse\n")
    s = must(s, anchor)
    s = s.replace(anchor,
                  "\t\t\t\t\t\t\tif mode == \"health\" then\n"
                  "\t\t\t\t\t\t\t\thp = FOURTH.enemy_health_pct(enemy)\n"
                  "\t\t\t\t\t\t\t\tqualifies = (hp ~= nil and hp < FOURTH.HEALTH_LINE_PCT)\n"
                  "\t\t\t\t\t\t\telseif mode == \"infantry\" then\n"
                  "\t\t\t\t\t\t\t\t-- ROUND 106: IN MELEE **and** INFANTRY (real reads, fail-closed).\n"
                  "\t\t\t\t\t\t\t\tqualifies = (ok_melee and melee == true) and FOURTH.enemy_is_infantry(enemy)\n"
                  "\t\t\t\t\t\t\telse\n", 1)

    anchor = ("\t\t\t\t\telse\n"
              "\t\t\t\t\t\treason = \"closest non-commander enemy in melee within bound (targeting \"\n")
    s = must(s, anchor)
    s = s.replace(anchor,
                  "\t\t\t\t\telseif mode == \"infantry\" then\n"
                  "\t\t\t\t\t\treason = \"closest in-melee INFANTRY enemy within bound (targeting \"\n"
                  "\t\t\t\t\t\t\t.. etype .. \", distance=\"\n"
                  "\t\t\t\t\t\t\t.. ((best_gap ~= nil) and string.format(\"%.1f\", best_gap) or \"?\") .. \"m)\"\n"
                  "\t\t\t\t\telse\n"
                  "\t\t\t\t\t\treason = \"closest non-commander enemy in melee within bound (targeting \"\n", 1)

    # --- J. the pre-cast re-check: infantry ----------------------------------
    anchor = ("\t\tlocal cmdr_now = false\n"
              "\t\tif FOURTH.eg_noncommander then\n"
              "\t\t\tcmdr_now = FOURTH.enemy_is_commander(enemy)\n"
              "\t\tend\n")
    s = must(s, anchor)
    s = s.replace(anchor, anchor +
                  "\t\t-- ROUND 106: an INFANTRY choice is re-verified NOW, like the\n"
                  "\t\t-- commander exclusion - a unit that died, left melee or is no\n"
                  "\t\t-- longer readable as infantry makes the cast be skipped.\n"
                  "\t\tlocal inf_now = true\n"
                  "\t\tif FOURTH.eg_infantry then\n"
                  "\t\t\tinf_now = FOURTH.enemy_is_infantry(enemy)\n"
                  "\t\tend\n", 1)

    s = must(s, "\t\tif not alive_now or not cond_now or cmdr_now or not in_bound_now then\n")
    s = s.replace("\t\tif not alive_now or not cond_now or cmdr_now or not in_bound_now then\n",
                  "\t\tif not alive_now or not cond_now or cmdr_now or not inf_now or not in_bound_now then\n", 1)

    if is_src:
        # the skip line gains the infantry flag (before commander=, so every
        # older substring pin that ends with commander=false) still matches)
        s = must(s, '\t\t\t\t.. " commander=" .. tostring(cmdr_now)\n')
        s = s.replace('\t\t\t\t.. " commander=" .. tostring(cmdr_now)\n',
                      '\t\t\t\t.. " infantry=" .. tostring(inf_now)\n'
                      '\t\t\t\t.. " commander=" .. tostring(cmdr_now)\n', 1)
        s = must(s, '\t\t\t.. " mode=" .. tostring(eg_mode_now) .. hp_text_now\n\t\t\t.. ", distance="')
        s = s.replace('\t\t\t.. " mode=" .. tostring(eg_mode_now) .. hp_text_now\n\t\t\t.. ", distance="',
                      '\t\t\t.. " mode=" .. tostring(eg_mode_now) .. hp_text_now\n'
                      '\t\t\t.. " infantry=" .. tostring(inf_now)\n'
                      '\t\t\t.. ", distance="', 1)

    # --- K. the per-evaluate clearing ---------------------------------------
    anchor = "\t\t\t\t\tFOURTH.eg_noncommander = nil\n"
    s = must(s, anchor)
    s = s.replace(anchor, anchor + "\t\t\t\t\tFOURTH.eg_infantry = nil\n", 1)

    # --- L. the slot's own declaration --------------------------------------
    anchor = "FOURTH.eg_no_bound = nil\n"
    s = must(s, anchor)
    s = s.replace(anchor, anchor + "FOURTH.eg_infantry = nil\n", 1)

    assert s != orig
    write(path, s)
    print("edited", path, "md5", hashlib.md5(s.encode("utf-8")).hexdigest())

apply(SRC, True)
apply(ANN, False)
print("OK")
