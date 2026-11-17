#!/usr/bin/env python3
"""Round 171 (harness 170): the score 1-2 review, rows 1-15 and 21, and the closures (user rulings 2026-11-17).

  Row 1  Horn of the Wild Hunt           -> NEW army_charge (3+ of our units charging or in fresh contact)
  Row 2  Potion of Foolhardiness         (round 170)
  Row 3  Ursun's Roar (main key)         -> its own entry on NEW aura_charge (the caster, or 2+ units within its
                                            70% aura, charging or in fresh contact)
  Row 4  Red Fury                        -> NEW self_or_ally_charge (caster charging; else the nearest ally within
                                            70 m charging or in fresh contact; else the caster in melee)
  Row 5  Waaagh! (wh_main key)           -> its own entry on army_charge
  Row 6  The Rock of Inevitability       -> NEW slow_aura (caster in melee, or a fast enemy inside its 70% aura)
  Row 7  The Wissenland Runefang         -> slow_aura
  Row 8  Black Staff                     -> NEW winds_low (pool below 30, reserve 20+, caster above 50% health)
  Row 9  Forbidden Rod                   -> winds_low
  Row 10 Wand of Jet                     -> when_ready
  Rows 11-15 Earthing Rod, Hagtree Fetish, Master of the Black Arts, Maw Shard, Power Familiar -> CLOSED (rule 10)
  Row 17 Watched by the Watcher          -> CLOSED (user: "close (no actuation)")
  Rows 19, 20 Sceptre of Stability, Locus of Abjuration -> CLOSED (user: "no read against enemy magic")
  Row 21 Necrotic Phylactery             -> NEW contact_melee (in melee, not wavering, fighting an enemy whose melee
                                            blows carry a contact effect: GENERATED FOURTH.CONTACT_TEXT)
  Row 22 Focus Instincts                 -> CLOSED (user: "if not possible to read a rampaged unit, then close";
                                            CLAUDE.md: no battle read for a rampaging unit)
Every moved entry keeps its old default (start_armed = true where its old family started armed); the two winds items
are risky (self-damage) and start on M (round 167). The fresh-contact read: FOURTH.track_melee runs once per poll for
every unit of ours and remembers the tick each one entered melee.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_contact_keys as GC  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

CLOSE = ["earthing_rod", "hagtree_fetish", "master_of_the_black_arts", "maw_shard", "power_familiar",
         "watched_by_the_watcher", "sceptre_of_stability", "locus_of_abjuration", "focus_instincts"]


def entry(marker, name, trig, keys, extra=""):
    ks = ",\n\t\t\t".join('"%s"' % k for k in keys)
    return ('\t{ marker = "%s", name = "%s", trigger = "%s",\n\t\tbadge = "zz_auto_badge_%s",\n\t\tkeys = { %s },\n%s'
            '\t\tox = 0, oy = 0 },\n' % (marker, name, trig, marker, ks, extra))


ARMED = "\t\tstart_armed = true,\n"
MOVES = [
    (entry("horn_of_the_wild_hunt", "Horn of the Wild Hunt", "melee_unwavering",
           ["wh_dlc05_item_abilities_horn_of_the_wild_hunt"]),
     "\t-- ROUND 171 (review row 1): the whole army's charge bonus x1.6 - when 3+ of our units charge at once\n"
     + entry("horn_of_the_wild_hunt", "Horn of the Wild Hunt", "army_charge",
             ["wh_dlc05_item_abilities_horn_of_the_wild_hunt"], ARMED)),
    ('\t{ marker = "ursuns_roar", name = "Ursun\'s Roar", trigger = "melee_unwavering",\n'
     '\t\tbadge = "zz_auto_badge_ursuns_roar",\n'
     '\t\tkeys = { "wh3_main_character_abilities_ursuns_roar",\n'
     '\t\t\t"wh3_main_pro_character_abilities_ursuns_roar",\n'
     '\t\t\t"wh3_main_pro_character_abilities_ursuns_roar_1",\n'
     '\t\t\t"wh3_main_pro_character_abilities_ursuns_roar_3" },\n'
     '\t\tox = 0, oy = 0 },\n',
     entry("ursuns_roar", "Ursun's Roar", "melee_unwavering",
           ["wh3_main_pro_character_abilities_ursuns_roar", "wh3_main_pro_character_abilities_ursuns_roar_1",
            "wh3_main_pro_character_abilities_ursuns_roar_3"])
     + "\t-- ROUND 171 (review row 3): the charge-bonus key (9 s, 35 m aura) gets its own entry\n"
     + entry("ursuns_roar_charge", "Ursun's Roar", "aura_charge", ["wh3_main_character_abilities_ursuns_roar"],
             "\t\taura_real = 35,\n" + ARMED)),
    (entry("red_fury", "Red Fury", "melee_unwavering", ["wh_main_character_abilities_red_fury"]),
     "\t-- ROUND 171 (review row 4): charge bonus + AP damage on the caster or a charging ally\n"
     + entry("red_fury", "Red Fury", "self_or_ally_charge", ["wh_main_character_abilities_red_fury"],
             "\t\tally_range_real = 100,\n" + ARMED)),
    ('\t{ marker = "waaagh_in_combat", name = "Waaagh!", trigger = "melee_unwavering",\n'
     '\t\tbadge = "zz_auto_badge_waaagh_in_combat",\n'
     '\t\tkeys = { "wh3_dlc26_unit_abilities_waaagh_in_combat",\n'
     '\t\t\t"wh_main_character_abilities_waaagh" },\n'
     '\t\tox = 0, oy = 0 },\n',
     entry("waaagh_in_combat", "Waaagh!", "melee_unwavering", ["wh3_dlc26_unit_abilities_waaagh_in_combat"])
     + "\t-- ROUND 171 (review row 5): the Warboss's army-wide Waaagh! (speed, charge, melee attack) gets its own entry\n"
     + entry("waaagh_army", "Waaagh!", "army_charge", ["wh_main_character_abilities_waaagh"], ARMED)),
    (entry("the_rock_of_inevitability", "The Rock of Inevitability", "melee_unwavering",
           ["wh3_main_item_abilities_the_rock_of_inevitability"]),
     "\t-- ROUND 171 (review row 6): enemies within 35 m slowed, melee defence -26\n"
     + entry("the_rock_of_inevitability", "The Rock of Inevitability", "slow_aura",
             ["wh3_main_item_abilities_the_rock_of_inevitability"], "\t\taura_real = 35,\n" + ARMED)),
    (entry("wissenland_runefang", "The Wissenland Runefang", "melee_unwavering",
           ["wh2_dlc13_weapon_abilities_wissenland_runefang"]),
     "\t-- ROUND 171 (review row 7): enemies within 35 m slowed (speed x0.55)\n"
     + entry("wissenland_runefang", "The Wissenland Runefang", "slow_aura",
             ["wh2_dlc13_weapon_abilities_wissenland_runefang"], "\t\taura_real = 35,\n" + ARMED)),
    (entry("black_staff", "Black Staff", "melee_unwavering", ["wh2_main_spell_bound_black_staff"]),
     "\t-- ROUND 171 (review row 8): winds recharge; damages its target (risky: starts on M)\n"
     + entry("black_staff", "Black Staff", "winds_low", ["wh2_main_spell_bound_black_staff"])),
    (entry("forbidden_rod", "Forbidden Rod", "melee_unwavering", ["wh_main_item_abilities_forbidden_rod"]),
     "\t-- ROUND 171 (review row 9): winds recharge; damages the caster (risky: starts on M)\n"
     + entry("forbidden_rod", "Forbidden Rod", "winds_low", ["wh_main_item_abilities_forbidden_rod"])),
    (entry("wand_of_jet", "Wand of Jet", "melee_unwavering", ["wh_main_item_abilities_wand_of_jet"]),
     "\t-- ROUND 171 (review row 10): up 57 s of every 117 - when ready\n"
     + entry("wand_of_jet", "Wand of Jet", "when_ready", ["wh_main_item_abilities_wand_of_jet"])),
    (entry("necrotic_phylactry", "Necrotic Phylactery", "ushoran_health", ["wh3_dlc25_item_abilities_necrotic_phylactry"]),
     "\t-- ROUND 171 (review row 21): immunity to enemy contact effects - in melee against an enemy that applies one\n"
     + entry("necrotic_phylactry", "Necrotic Phylactery", "contact_melee",
             ["wh3_dlc25_item_abilities_necrotic_phylactry"], ARMED)),
]

KEYS = {"earthing_rod": "wh_main_item_abilities_earthing_rod", "hagtree_fetish": "wh_dlc03_item_abilities_hagtree_fetish",
        "master_of_the_black_arts": "wh_main_lord_abilities_master_of_the_black_arts",
        "maw_shard": "wh3_main_item_abilities_maw_shard", "power_familiar": "wh3_dlc27_item_abilities_power_familiar",
        "watched_by_the_watcher": "wh3_dlc24_character_abilities_watched_by_the_watcher",
        "sceptre_of_stability": "wh_main_item_abilities_sceptre_of_stability",
        "locus_of_abjuration": "wh3_main_character_abilities_locus_of_abjuration",
        "focus_instincts": "wh2_dlc12_lord_abilities_focus_instincts"}
NAMES = {"earthing_rod": "Earthing Rod", "hagtree_fetish": "Hagtree Fetish", "master_of_the_black_arts":
         "Master of the Black Arts", "maw_shard": "Maw Shard", "power_familiar": "Power Familiar",
         "watched_by_the_watcher": "Watched by the Watcher", "sceptre_of_stability": "Sceptre of Stability",
         "locus_of_abjuration": "Locus of Abjuration", "focus_instincts": "Focus Instincts"}

CODE = r'''
-- ============================================================================
-- ROUND 171 - THE SCORE 1-2 REVIEW, ROWS 1-15 AND 21 (user rulings 2026-11-17: "You can implement items 1-15 in the
-- low score review doc"; row 21 "do the contact effect list please").
--   FRESH CONTACT: FOURTH.track_melee runs once per poll for every unit of ours and remembers the tick it entered
--     melee; a unit is in FRESH CONTACT for FRESH_CONTACT_S after that (a charge bonus still pays about 80% 2 s
--     after impact, docs\WH3_battle_knowledge.md).
--   army_charge (Horn of the Wild Hunt, Waaagh!): ARMY_CHARGE_MIN or more of our units charging or in fresh contact.
--   aura_charge (Ursun's Roar, the charge key): the caster charging or in fresh contact, or AURA_CHARGE_ALLIES other
--     units within its 70% aura doing so.
--   self_or_ally_charge (Red Fury): the caster charging -> self; else the nearest ally within the 70% bound charging or
--     in fresh contact -> that ally; else the caster in melee -> self.
--   slow_aura (The Rock of Inevitability, The Wissenland Runefang): the caster in melee, or a visible fast enemy (run
--     speed FAST_ENEMY_MPS or more, moving) inside its 70% aura.
--   winds_low (Black Staff, Forbidden Rod): the army's winds pool below WINDS_LOW_POOL with WINDS_LOW_RESERVE or more
--     reserve, and the caster above WINDS_LOW_HEALTH % health (the item damages it).
--   contact_melee (Necrotic Phylactery): in melee, not wavering, and an enemy in contact (or its current target)
--     whose melee blows carry a contact effect (GENERATED FOURTH.CONTACT_TEXT).
-- ============================================================================
FOURTH.FRESH_CONTACT_S = 2
FOURTH.ARMY_CHARGE_MIN = 3
FOURTH.AURA_CHARGE_ALLIES = 2
FOURTH.WINDS_LOW_POOL = 30
FOURTH.WINDS_LOW_RESERVE = 20
FOURTH.WINDS_LOW_HEALTH = 50
FOURTH.melee_since = {}

-- once per poll: remember when each unit of ours entered melee (nil = not in melee)
function FOURTH.track_melee()
	if tracked_units == nil then return end
	local seen = {}
	for i = 1, #tracked_units do
		local u = tracked_units[i] and tracked_units[i].unit
		if u ~= nil then
			local ok_id, id = pcall(function() return tostring(u:unique_ui_id()) end)
			if ok_id and id ~= nil then
				seen[id] = true
				local ok_m, m = pcall(function() return u:is_in_melee() end)
				if ok_m and m == true then
					if FOURTH.melee_since[id] == nil then FOURTH.melee_since[id] = tick_count end
				else
					FOURTH.melee_since[id] = nil
				end
			end
		end
	end
	for id in pairs(FOURTH.melee_since) do
		if not seen[id] then FOURTH.melee_since[id] = nil end
	end
end

-- true when u entered melee at most FRESH_CONTACT_S ago
function FOURTH.fresh_contact(u)
	local ok_id, id = pcall(function() return tostring(u:unique_ui_id()) end)
	if not ok_id or id == nil then return false end
	local since = FOURTH.melee_since[id]
	if since == nil then return false end
	return (tick_count - since) * POLL_MS / 1000 <= FOURTH.FRESH_CONTACT_S
end

-- true when u is in its charge window (Deadly Onslaught's detector)
function FOURTH.unit_charging(u)
	if not FIRE_ON_CHARGE then return false end
	local ok, m = pcall(measure_charge, u)
	return ok and m ~= nil and m.charging == true
end

-- "charging", "fresh contact" or nil
function FOURTH.charge_moment(u)
	if FOURTH.unit_charging(u) then return "charging" end
	if FOURTH.fresh_contact(u) then return "fresh contact" end
	return nil
end

function FOURTH.evaluate_army_charge(unit, routing)
	if routing or tracked_units == nil then return nil end
	local nc, nf = 0, 0
	for i = 1, #tracked_units do
		local u = tracked_units[i] and tracked_units[i].unit
		if u ~= nil and not unit_is_routing(u) then
			local ok_a, men = pcall(function() return u:number_of_men_alive() end)
			if ok_a and type(men) == "number" and men > 0 then
				local w = FOURTH.charge_moment(u)
				if w == "charging" then nc = nc + 1 elseif w ~= nil then nf = nf + 1 end
			end
		end
	end
	if nc + nf >= FOURTH.ARMY_CHARGE_MIN then
		return string.format("army charge: %d unit(s) charging and %d in fresh contact (need %d)", nc, nf,
			FOURTH.ARMY_CHARGE_MIN)
	end
	return nil
end

function FOURTH.evaluate_aura_charge(unit, routing)
	if routing then return nil end
	local own = FOURTH.charge_moment(unit)
	if own ~= nil then return "the caster: " .. own .. " (aura charge)" end
	local reach = FOURTH.ah_range_m
	if reach == nil or tracked_units == nil then return nil end
	local self_id = nil
	pcall(function() self_id = tostring(unit:unique_ui_id()) end)
	local n = 0
	for i = 1, #tracked_units do
		local u = tracked_units[i] and tracked_units[i].unit
		if u ~= nil then
			local ok_id, id = pcall(function() return tostring(u:unique_ui_id()) end)
			if ok_id and id ~= self_id and not unit_is_routing(u) then
				local ok_g, g = pcall(function() return unit:unit_distance(u) end)
				if ok_g and type(g) == "number" and g <= reach and FOURTH.charge_moment(u) ~= nil then n = n + 1 end
			end
		end
	end
	if n >= FOURTH.AURA_CHARGE_ALLIES then
		return string.format("aura charge: %d unit(s) within %sm charging or in fresh contact (need %d)", n,
			tostring(reach), FOURTH.AURA_CHARGE_ALLIES)
	end
	return nil
end

function FOURTH.evaluate_self_or_ally_charge(unit, routing)
	if routing then return nil end
	if FOURTH.unit_charging(unit) then return "the caster is charging, cast on self" end
	local r = FOURTH.ab_pick_ally(unit, routing, "charging")
	if r then return r end   -- the reading copy's picker answers false, the live one nil
	local ok, m = pcall(function() return unit:is_in_melee() end)
	if ok and m == true then return "the caster is in melee, cast on self" end
	return nil
end

function FOURTH.evaluate_slow_aura(unit, routing)
	if routing then return nil end
	local ok, m = pcall(function() return unit:is_in_melee() end)
	if ok and m == true then return "in melee (slow aura)" end
	local reach = FOURTH.ah_range_m
	if reach == nil then return nil end
	local ok_c, coll = pcall(function() return bm:get_scriptunits_for_main_enemy_army_to_local_player() end)
	if not ok_c or coll == nil then return nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil end
	for i = 1, n do
		local e = nil
		pcall(function() e = coll:item(i).unit end)
		if e ~= nil and FOURTH.enemy_not_hidden(e) then
			local ok_a, men = pcall(function() return e:number_of_men_alive() end)
			local ok_mv, mv = pcall(function() return e:is_moving() end)
			local ok_sp, sp = pcall(function() return e:fast_speed() end)
			local ok_g, g = pcall(function() return unit:unit_distance(e) end)
			if ok_a and type(men) == "number" and men > 0 and ok_mv and mv == true
				and ok_sp and type(sp) == "number" and sp >= FOURTH.FAST_ENEMY_MPS
				and ok_g and type(g) == "number" and g <= reach then
				return string.format("a fast enemy (run speed %.1f m/s) %.1fm away, inside the %sm aura (slow aura)",
					sp, g, tostring(reach))
			end
		end
	end
	return nil
end

-- the army's winds pool and reserve (the WINDS map row's reads); nil, nil when unreadable
function FOURTH.winds_now()
	local ok_a, army = pcall(function() return bm:get_player_army() end)
	if not ok_a or army == nil then return nil, nil end
	local ok_c, c = pcall(function() return army:winds_of_magic_current() end)
	local ok_r, r = pcall(function() return army:winds_of_magic_reserve() end)
	if not (ok_c and type(c) == "number" and ok_r and type(r) == "number") then return nil, nil end
	return c, r
end

function FOURTH.evaluate_winds_low(unit, routing)
	if routing then return nil end
	local c, r = FOURTH.winds_now()
	if c == nil or c >= FOURTH.WINDS_LOW_POOL or r < FOURTH.WINDS_LOW_RESERVE then return nil end
	local hp = FOURTH.health_pct(unit)
	if type(hp) ~= "number" or hp <= FOURTH.WINDS_LOW_HEALTH then return nil end
	return string.format("winds low: pool %.0f (< %d), reserve %.0f (>= %d), caster health %d%% (> %d%%)", c,
		FOURTH.WINDS_LOW_POOL, r, FOURTH.WINDS_LOW_RESERVE, math.floor(hp), FOURTH.WINDS_LOW_HEALTH)
end

-- GENERATED by tools/gen_contact_keys.py from land_units, melee_weapons (contact_phase), the land unit abilities and
-- phases (imbue_contact of a passive): the land units whose melee blows carry a contact effect. The build refuses a
-- pack whose table differs from the game data. Do not hand-edit.
FOURTH.CONTACT_TEXT = "%CONTACT%"
FOURTH.CONTACT = {}
function FOURTH.load_contact_table()   -- a function, so the loop adds no main-chunk locals
	for k in string.gmatch(FOURTH.CONTACT_TEXT, "([^;]+)") do FOURTH.CONTACT[k] = true end
end
FOURTH.load_contact_table()

function FOURTH.evaluate_contact_melee(unit, routing)
	if routing then return nil end
	local ok, m = pcall(function() return unit:is_in_melee() end)
	if not (ok and m == true) then return nil end
	if FOURTH.wavering(unit) == true then return nil end
	local members = FOURTH.engagement_set(unit)
	if members ~= nil then
		for _, e in ipairs(members) do
			if e.type ~= nil and FOURTH.CONTACT[e.type] == true then
				return "in melee with '" .. e.type .. "', whose blows carry a contact effect"
			end
		end
	end
	local ok_t, t = pcall(function() return unit:current_target() end)
	if ok_t and t ~= nil and FOURTH.enemy_not_hidden(t) then
		local tt = FOURTH.type_plain(t)
		if tt ~= nil and FOURTH.CONTACT[tt] == true then
			return "in melee, its target '" .. tt .. "' carries a contact effect"
		end
	end
	return nil
end
'''

R = [
    # the new code after the charge-or-melee evaluator
    ('\tif reason == "in melee" then\n\t\treason = "in melee (charge or melee)"\n\tend\n\treturn reason\nend\n',
     '\tif reason == "in melee" then\n\t\treason = "in melee (charge or melee)"\n\tend\n\treturn reason\nend\n' + "%CODE%"),
    # the per-poll melee tracker
    ("local function poll_body()\n\ttick_count = tick_count + 1\n",
     "local function poll_body()\n\ttick_count = tick_count + 1\n"
     "\tpcall(FOURTH.track_melee)   -- ROUND 171: the fresh-contact read (once per poll, every unit of ours)\n"),
    # the ally picker's charging family and its two re-checks
    ('\t\t\t\t\telseif family == "ammo" then\n\t\t\t\t\t\t-- ROUND 130: Restock!',
     '\t\t\t\t\telseif family == "charging" then\n'
     '\t\t\t\t\t\t-- ROUND 171: Red Fury - an ally charging or in fresh contact (the closest wins)\n'
     '\t\t\t\t\t\teligible = (FOURTH.charge_moment(other) ~= nil)\n'
     '\t\t\t\t\telseif family == "ammo" then\n\t\t\t\t\t\t-- ROUND 130: Restock!'),
    ('\t\tif FOURTH.ab_family == "fighting" then\n\t\t\thp_ok_now = FOURTH.fighting(ally)\n\t\tend\n',
     '\t\tif FOURTH.ab_family == "fighting" then\n\t\t\thp_ok_now = FOURTH.fighting(ally)\n\t\tend\n'
     '\t\tif FOURTH.ab_family == "charging" then   -- ROUND 171\n'
     '\t\t\thp_ok_now = (FOURTH.charge_moment(ally) ~= nil)\n\t\tend\n'),
    ('\tif FOURTH.ab_family == "fighting" then\n\t\treturn FOURTH.fighting(ally)\n\tend\n\treturn true\nend\n',
     '\tif FOURTH.ab_family == "fighting" then\n\t\treturn FOURTH.fighting(ally)\n\tend\n'
     '\tif FOURTH.ab_family == "charging" then   -- ROUND 171\n'
     '\t\treturn FOURTH.charge_moment(ally) ~= nil\n\tend\n\treturn true\nend\n'),
    # evaluator wiring
    ("\twhen_ready = FOURTH.evaluate_when_ready,\n",
     "\twhen_ready = FOURTH.evaluate_when_ready,\n"
     "\tarmy_charge = FOURTH.evaluate_army_charge,   -- ROUND 171\n"
     "\taura_charge = FOURTH.evaluate_aura_charge,\n"
     "\tself_or_ally_charge = FOURTH.evaluate_self_or_ally_charge,\n"
     "\tslow_aura = FOURTH.evaluate_slow_aura,\n"
     "\twinds_low = FOURTH.evaluate_winds_low,\n"
     "\tcontact_melee = FOURTH.evaluate_contact_melee,\n"),
    # the internal family labels (round 93)
    ("FOURTH.TRIGGER_TIP = {\n",
     "FOURTH.TRIGGER_TIP = {\n"
     '\tarmy_charge = "When armed, fires when 3 or more of our units charge or have just made contact",   -- ROUND 171\n'
     '\taura_charge = "When armed, fires when this unit, or 2 or more units in its aura, charge or have just made contact",\n'
     '\tself_or_ally_charge = "When armed, fires on this unit or the nearest charging ally, else when this unit is in melee",\n'
     '\tslow_aura = "When armed, fires in melee, or when a fast enemy enters the aura",\n'
     '\twinds_low = "When armed, fires when the winds pool is low with reserve left, the caster above 50% health",\n'
     '\tcontact_melee = "When armed, fires in melee against an enemy whose blows carry a contact effect",\n'),
    # the card sentences
    ('\tcharge_or_wavering = "Fires when charging or wavering",\n',
     '\tcharge_or_wavering = "Fires when charging or wavering",\n'
     '\tarmy_charge = "Fires when {ACN}+ of your units charge at once",   -- ROUND 171\n'
     '\taura_charge = "Fires when charging, or when {ACA}+ nearby allies charge",\n'
     '\tself_or_ally_charge = "Fires on itself or the nearest charging ally, else in melee",\n'
     '\tslow_aura = "Fires in melee, or when a fast enemy comes near",\n'
     '\twinds_low = "Fires when the winds pool is low, above {WLH}% health",\n'
     '\tcontact_melee = "Fires in melee unless wavering, against an enemy with contact effects",\n'),
    ("\trecharging_in_reach = true, melee_self_or_ally = true, melee_or_self_or_ally_shooting = true }\n",
     "\trecharging_in_reach = true, melee_self_or_ally = true, melee_or_self_or_ally_shooting = true,\n"
     "\tself_or_ally_charge = true }   -- ROUND 171\n"),
    ('\tif not (row ~= nil and not row.allies) then t.FF = "" end\n',
     '\tif not (row ~= nil and not row.allies) then t.FF = "" end\n'
     "\t-- ROUND 171: the review's constants\n"
     "\tt.ACN, t.ACA = FOURTH.card_num(FOURTH.ARMY_CHARGE_MIN), FOURTH.card_num(FOURTH.AURA_CHARGE_ALLIES)\n"
     "\tt.WLH = FOURTH.card_num(FOURTH.WINDS_LOW_HEALTH)\n"),
]


ALT = {
    '\tif reason == "in melee" then\n\t\treason = "in melee (charge or melee)"\n\tend\n\treturn reason\nend\n':
        "function FOURTH.evaluate_charge_or_melee(unit, routing)\n\tif FOURTH.evaluate_charge(unit, routing) then\n"
        "\t\treturn true\n\tend\n\treturn false\nend\n",
    "local function poll_body()\n\ttick_count = tick_count + 1\n":
        "local function poll_body()\n\ttick_count = tick_count + 1     -- one step of the mod's own battle clock\n",
}


def main():
    contact = GC.text(GC.derive())
    code = CODE.replace("%CONTACT%", contact)
    for path in (SRC, ANN):
        s = open(path, encoding="utf-8", newline="").read()
        assert "ROUND 171" not in s
        for o, n in MOVES:
            assert s.count(o) == 1, (path[-12:], o[:80], s.count(o))
            s = s.replace(o, n)
        for m in CLOSE:
            o = entry(m, NAMES[m], "melee_unwavering", [KEYS[m]])
            assert s.count(o) == 1, (path[-12:], m, s.count(o))
            s = s.replace(o, "")
        for o, n in R:
            n = n.replace("%CODE%", code)
            if path == ANN and o in ALT:
                # the annotated reading copy words these two anchors differently: keep its own text, add the same code
                o2 = ALT[o]
                n = o2 + n[len(o):] if n.startswith(o) else n
                o = o2
            assert s.count(o) == 1, (path[-12:], o[:70], s.count(o))
            s = s.replace(o, n)
        assert "\u2014" not in s
        open(path, "w", encoding="utf-8", newline="").write(s)
        print(path, "patched")


if __name__ == "__main__":
    main()
