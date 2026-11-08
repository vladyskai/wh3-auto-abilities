# -*- coding: utf-8 -*-
"""Round 107 - the remaining bombardment work.

Applies ONE deterministic set of edits to BOTH the shipped source and the
annotated reference copy (same control flow, no log()). Binary read/write so
the shipped file stays LF (a text-mode write on Windows would flip every
newline to CRLF and break the build's byte-identity gate).

EDITS
  item 1/2  Call of Tor on melee_skip_commanders (Soulfire's trigger)
  item 3    12 air-drop entries / 19 keys on the NEW air_drop_on_infantry
            evaluator, with the per-row air_only / no_melee flags
  item 4    the per-unit serialisation gate (cast_gate.unit_until/.unit_marker/
            .unit_logged) with the SERIAL_MIN_HOLD_SECONDS stagger
  plus      FOURTH.ENEMY_CAST_R10 = 7 and its map entry, the charge-gate and
            wind-up rows for the new keys, the poll slots, the tooltip line
"""
import hashlib
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BAK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round107"


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
    assert c == n, "anchor count %d (want %d): %r" % (c, n, old[:110])
    return s


# ---------------------------------------------------------------------------
# THE AIR-DROP ENTRIES: (marker, display name, keys, air_only, no_melee)
# air_only / no_melee come from the game's OWN rows:
#   air_only  <- the `grounded` invalid-usage flag OR every carrier flying
#   no_melee  <- the `engaged_in_melee` invalid-usage flag
# Drop Sphere of Tepok: one lord key is a GROUND variant and the row carries no
# `grounded` flag -> NOT air-gated (documented on the entry).
# Searing Torrent: a ground carrier (Doom Knights) -> NOT air-gated.
# ---------------------------------------------------------------------------
AIR = [
    ("death_from_above", "Death from Above",
     ["wh2_dlc09_unit_abilities_death_from_above"], True, True),
    ("drop_rocks", "Drop Rocks",
     ["wh2_main_unit_abilities_drop_rocks",
      "wh2_dlc12_unit_abilities_drop_rocks_character",
      "wh2_dlc12_unit_abilities_drop_rocks_of_chotec",
      "wh2_dlc12_unit_abilities_drop_rocks_of_sundering"], True, True),
    ("drop_sphere_of_tepok", "Drop Sphere of Tepok",
     ["wh2_dlc12_lord_abilities_drop_sphere_of_tepok",
      "wh2_dlc12_lord_abilities_drop_sphere_of_tepok_upgraded"], False, True),
    ("fire_bombs", "Fire Bombs",
     ["wh3_dlc25_unit_abilities_gyrobomber_fire_bomb",
      "wh3_dlc25_unit_abilities_thunderbarge_fire_bomb"], True, False),
    ("gyrobomber_bomb", "Gyrobomber Bomb",
     ["wh_main_unit_abilities_gyrobomber_bomb",
      "wh_main_unit_abilities_gyrocopter_bomb"], True, False),
    ("gyrocopter_bomb_anti_large", "Gyrocopter Bomb (anti-large)",
     ["wh3_dlc25_unit_abilities_gyrocopter_bomb_anti_large"], True, False),
    ("sky_junk_bomb", "Sky-Junk Bomb",
     ["wh3_main_unit_abilities_sky_junk_bomb"], True, False),
    ("skyhammer_bomb", "Skyhammer Bomb",
     ["wh_dlc06_unit_abilities_skyhammer_bomb",
      "wh_dlc06_unit_abilities_skyhammer_fire_bomb"], True, False),
    ("wake_of_fire", "Wake of Fire",
     ["wh2_main_unit_abilities_wake_of_fire"], True, True),
    ("searing_torrent", "Searing Torrent",
     ["wh3_twa07_unit_abilities_searing_torrent"], False, True),
    ("nan_gau_grenades", "Nan-Gau Grenades",
     ["wh3_dlc24_unit_abilities_nan_gau_grenades"], True, False),
    ("undeath_from_above", "Undeath from Above",
     ["wh3_dlc29_unit_abilities_undeath_from_above"], True, True),
]

CALLLINE = '''\t-- ROUND 107 (item 2): CALL OF TOR - the user's rule, verbatim: "Call of Tor
\t-- looks very similar to Soulfire, so let's do the same trigger as a
\t-- Soulfire." Its row is SELF-CENTRED exactly like Soulfire's (all four
\t-- target flags false, target_intercept_range 0, ai_usage =
\t-- aoe_centred_on_self), so it rides melee_skip_commanders unchanged: the
\t-- caster must be in melee and at least one engaged enemy must NOT be a Lord
\t-- or a Hero. The judged engagement set is logged with every member's type,
\t-- commander flag and real distance - the same line Soulfire writes.
\t{ marker = "call_of_tor", name = "Call of Tor", trigger = "melee_skip_commanders",
\t\tbadge = "zz_auto_badge_call_of_tor",
\t\tkeys = { "wh3_twa07_spell_bound_call_of_tor" },
\t\tox = 0, oy = 0 },
'''


def air_block():
    out = ["\t-- ======================================================================",
           "\t-- ROUND 107 (item 3): THE \"ON TOP OF\" FAMILY - 12 entries / 19 keys on",
           "\t-- the NEW trigger air_drop_on_infantry.",
           "\t--",
           "\t-- Every one of these rows has NO target flags at all (friends/enemies/",
           "\t-- ground/self all false), effect_range 0, target_intercept_range 10 and",
           "\t-- ai_usage always_use_only_land: the engine drops the ordnance where the",
           "\t-- CASTER is, so the mod's only decision is WHEN. The rule: fire when an",
           "\t-- enemy INFANTRY unit is within the ability's own 70% bound (7 m) of the",
           "\t-- caster - the edge-to-edge overlap proxy - and the caster satisfies the",
           "\t-- usage restrictions its own row declares:",
           "\t--   air_only = the row says the engine refuses it while `grounded`,",
           "\t--              OR every carrier of the key carries `flying`;",
           "\t--   no_melee = the row says the engine refuses it while `engaged_in_melee`.",
           "\t-- Two entries are deliberately NOT air-gated and say so on the entry:",
           "\t-- Drop Sphere of Tepok (one of its two lord keys is a GROUND variant and",
           "\t-- the row carries no `grounded` flag) and Searing Torrent (a ground",
           "\t-- carrier - the user's own field note is that it behaves the same and",
           "\t-- recharges in melee, so melee is NOT required, only excluded).",
           "\t-- The blast radius is NOT in the extracted tables (the aoe key lives in",
           "\t-- an aoe table outside this extraction), so 7 m is a CONSTANT: the row's",
           "\t-- own 10 m cast range at the standing 70% rule. Not a game radius.",
           "\t-- ======================================================================"]
    for marker, name, keys, air, nomelee in AIR:
        note = ""
        if marker == "drop_sphere_of_tepok":
            note = "\n\t\t-- NOT air-gated: wh2_dlc12_lzd_cha_tiktaqto_0 is a GROUND variant and\n\t\t-- the row declares no `grounded` flag, so the engine itself allows it on\n\t\t-- the ground. The enemy-under-the-caster test still decides WHEN."
        elif marker == "searing_torrent":
            note = "\n\t\t-- NOT air-gated: Knights of Immolation (Doom Knights) are a GROUND\n\t\t-- carrier. no_melee is the row's own `engaged_in_melee` flag: the user's\n\t\t-- field note is that it RECHARGES in melee, so melee is never required -\n\t\t-- only excluded, because the engine refuses the cast while fighting."
        elif marker == "undeath_from_above":
            note = "\n\t\t-- The Deck Droppers unit set wh2_dlc11_cst_deck_droppers (all four\n\t\t-- variants carry `flying`); the same set carries Drop Rocks."
        elif marker == "nan_gau_grenades":
            note = "\n\t\t-- Empress Crowmen (Onyx Crowmen), 2 uses / 60 s, air-only (`grounded`)."
        out.append(note)
        out.append('\t{ marker = "%s", name = "%s", trigger = "air_drop_on_infantry",' % (marker, name))
        out.append('\t\tbadge = "zz_auto_badge_%s",' % marker)
        if len(keys) == 1:
            out.append('\t\tkeys = { "%s" },' % keys[0])
        else:
            out.append('\t\tkeys = { "%s",' % keys[0])
            for k in keys[1:-1]:
                out.append('\t\t\t"%s",' % k)
            out.append('\t\t\t"%s" },' % keys[-1])
        out.append('\t\trange_real = 10,')
        out.append('\t\tair_only = %s,' % ("true" if air else "false"))
        out.append('\t\tno_melee = %s,' % ("true" if nomelee else "false"))
        out.append('\t\tox = 0, oy = 0 },')
    return "\n".join(out) + "\n"


HELPERS = r'''-- ============================================================================
-- ROUND 107 - THE "ON TOP OF" FAMILY: ONE new evaluator, air_drop_on_infantry.
--
-- THE MECHANIC, FROM THE GAME'S OWN ROWS (the 19 keys of the 11 abilities):
--   target_friends / target_enemies / target_ground / target_self are ALL
--   false, effect_range = 0, target_intercept_range = 10, ai_usage =
--   always_use_only_land and the `bombardment` column points at the ability
--   itself. There is no enemy to click: the engine releases the ordnance where
--   the CASTER is. The only decision the mod can make is WHEN to press it.
--
-- THE RULE (user-approved): fire when an enemy INFANTRY unit is UNDER the
-- caster - inside the ability's own 70% bound, floor(10 * 0.70) = 7 m, the
-- constant FOURTH.AIR_DROP_BOUND_M - and the caster satisfies the usage
-- restrictions its own row declares:
--   * air_only  - the row declares the engine's `grounded` invalid-usage flag
--                 (the Dwarf airframes), or every carrier of the key carries
--                 the `flying` unit attribute (the drop families). The mod
--                 reads battle_unit:is_currently_flying() and holds unless the
--                 answer is exactly true. An unreadable read FAILS CLOSED.
--   * no_melee  - the row declares the engine's `engaged_in_melee` invalid-
--                 usage flag, so a cast while fighting would only be refused.
--                 An unreadable read FAILS CLOSED.
--
-- THE OVERLAP PROXY, STATED PLAINLY: the battle script API exposes no per-unit
-- footprint and no blast radius, and the aoe key the row names
-- (wh_abilities_bomb_drop / wh_abilities_bomb_small_drop) lives in a table
-- this extraction does not carry. The ONE real read available is
-- unit:unit_distance(caster) - EDGE-TO-EDGE metres (battle_unit.lua:160) - so
-- "under the caster" is proxied by that gap being inside the 70% bound. 7 m is
-- a CONSTANT (the row's own 10 m cast range at 70%), NOT the bomb's radius,
-- and every log line that uses it says so.
--
-- THE CAST IS SELF-CENTRED: no target flags at all, so the unit form
-- perform_special_ability(key, OWNER) is the engine's own shape for it. The
-- chosen enemy is never a cast target - it is the justification for pressing
-- the button NOW, and it is re-read immediately before the call.
-- ============================================================================
FOURTH.AIR_DROP_BOUND_M = 7
FOURTH.ad_note = {}

-- One line per (unit, marker), and again only when the note CHANGES - the same
-- dedupe discipline as the engagement set, so a hovering unit does not flood
-- the log while it waits.
function FOURTH.ad_say(unit, marker, note)
	local ok_id, id = pcall(function() return unit:unique_ui_id() end)
	if not ok_id or id == nil then return end
	local slot = tostring(id)
	local per = FOURTH.ad_note[slot]
	if per == nil then per = {}; FOURTH.ad_note[slot] = per end
	if per[marker] == note then return end
	per[marker] = note
	ADLOG_SAY
end

-- THE AIR-DROP PICKER: the CLOSEST ALIVE enemy that IS INFANTRY and whose
-- edge-to-edge gap to the caster is inside the ability's 70% bound.
function FOURTH.ad_pick(unit, routing)
	if routing then return nil end
	local marker = FOURTH.ad_marker or "air_drop"
	local bound = FOURTH.ad_range_m
	if type(bound) ~= "number" then bound = FOURTH.AIR_DROP_BOUND_M end
	if FOURTH.ad_air_only then
		local ok_fly, flying = pcall(function() return unit:is_currently_flying() end)
		if not ok_fly or flying ~= true then
			FOURTH.ad_say(unit, marker, "airborne check: is_currently_flying() = "
				.. (ok_fly and tostring(flying) or "UNREADABLE")
				.. " -> HOLDING (this ability's row is air-only)")
			return nil
		end
	end
	if FOURTH.ad_no_melee then
		local ok_m, m = pcall(function() return unit:is_in_melee() end)
		if not ok_m then
			FOURTH.ad_say(unit, marker, "melee check: is_in_melee() UNREADABLE -> HOLDING (fail-closed)")
			return nil
		end
		if m == true then
			FOURTH.ad_say(unit, marker, "melee check: the caster is fighting in melee -> HOLDING"
				.. " (the row declares engaged_in_melee)")
			return nil
		end
	end
	local ok_coll, coll = pcall(function()
		return bm:get_scriptunits_for_main_enemy_army_to_local_player()
	end)
	if not ok_coll or coll == nil then return nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil end
	local best, best_gap = nil, nil
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		if ok_su and su ~= nil then
			local enemy = nil
			pcall(function() enemy = su.unit end)
			if enemy ~= nil then
				local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
				local gap = FOURTH.eg_enemy_gap(unit, enemy)
				if ok_alive and type(alive) == "number" and alive > 0
					and gap ~= nil and gap <= bound
					and FOURTH.enemy_is_infantry(enemy) then
					if best == nil or gap < best_gap then
						best, best_gap = enemy, gap
					end
				end
			end
		end
	end
	if best == nil then return nil end
	local etype = FOURTH.type_plain(best) or "enemy"
	FOURTH.ad_enemy = best
	FOURTH.ad_caster_su = FOURTH.eg_fresh_caster_su(unit)
	ADLOG_PICK
	return "closest INFANTRY enemy under the caster (targeting " .. etype
		.. ", distance=" .. string.format("%.1f", best_gap)
		.. "m, bound=" .. tostring(bound) .. "m)"
end

function FOURTH.evaluate_air_drop_on_infantry(unit, routing)
	return FOURTH.ad_pick(unit, routing)
end
'''

RECHECK = r'''	-- THE AIR-DROP RE-CHECK (round 107). Immediately before the call the CASTER
	-- must still be ALIVE, still AIRBORNE where its row is air-only and still
	-- OUT of melee where the engine forbids it; the chosen enemy must still be
	-- ALIVE, still INFANTRY and still inside the ability's 70% bound. Every
	-- number that decided it is written, and a lapsed condition SKIPS the cast
	-- rather than spending it.
	if FOURTH.ad_enemy ~= nil then
		local enemy = FOURTH.ad_enemy
		local ad_marker_now = FOURTH.ad_marker or "air_drop"
		local ad_bound_now = FOURTH.ad_range_m
		if type(ad_bound_now) ~= "number" then ad_bound_now = FOURTH.AIR_DROP_BOUND_M end
		local ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)
		local caster_alive = (ok_alive and type(alive) == "number" and alive > 0)
		local fly_now, fly_readable = true, true
		if FOURTH.ad_air_only then
			local ok_fly, v = pcall(function() return unit:is_currently_flying() end)
			fly_readable = ok_fly
			fly_now = (ok_fly and v == true)
		end
		local melee_now, melee_readable = false, true
		if FOURTH.ad_no_melee then
			local ok_m, m = pcall(function() return unit:is_in_melee() end)
			melee_readable = ok_m
			melee_now = (ok_m and m == true)
		end
		local ok_ea, ea = pcall(function() return enemy:number_of_men_alive() end)
		local enemy_alive = (ok_ea and type(ea) == "number" and ea > 0)
		local inf_now = FOURTH.enemy_is_infantry(enemy)
		local gap_now = FOURTH.eg_enemy_gap(unit, enemy)
		local in_bound_now = (gap_now ~= nil and gap_now <= ad_bound_now)
		if not (caster_alive and fly_readable and fly_now and melee_readable
			and (not melee_now) and enemy_alive and inf_now and in_bound_now) then
			ADLOG_SKIP
			FOURTH.ad_enemy = nil
			RELEASE_BLOCK
			return "held"
		end
		ADLOG_OK
	end

'''

GATE = r'''							-- THE PER-UNIT SERIALISATION GATE (round 107): the
							-- engine allows ONE special ability in flight per unit.
							-- A second order REPLACES the first during its wind-up
							-- and the replaced cast's use is still spent - the
							-- 2026-10-17 field log shows Captain Roth's Moondial
							-- issued first (3 s wind-up), Wraith Storm issued 0.25 s
							-- later on the same caster, and the Moondial's 120 s
							-- recharge consumed with no effect. So a unit that has
							-- just cast may not be ordered to cast a DIFFERENT
							-- ability until its window closes: the wind-up it
							-- declared + IN_FLIGHT_SETTLE_SECONDS, never less than
							-- SERIAL_MIN_HOLD_SECONDS. The ability that fired is NOT
							-- throttled here - its own pair gates govern its repeat.
							if eligible and cast_gate.unit_until[ui_id] ~= nil
								and cast_gate.unit_marker[ui_id] ~= ability.marker
								and tick_count < cast_gate.unit_until[ui_id] then
								eligible = false
								quiet = true
								local lg = cast_gate.unit_logged[ui_id]
								if lg == nil then
									lg = {}
									cast_gate.unit_logged[ui_id] = lg
								end
								if lg[ability.marker] ~= true then
									lg[ability.marker] = true
									ADLOG_GATE
								end
							end

'''

ARM = r'''								-- THE PER-UNIT SERIALISATION WINDOW (round 107): arm it
								-- for THIS unit - no OTHER ability may be issued
								-- until it closes. A repeat of the SAME ability does
								-- NOT extend it: a fast-repeating ability must not
								-- starve every other ability on the unit forever.
								if cast_gate.unit_marker[ui_id] ~= ability.marker then
									local unit_hold_s = ((ability.wind_up_s or 0) + IN_FLIGHT_SETTLE_SECONDS)
									if unit_hold_s < FOURTH.SERIAL_MIN_HOLD_SECONDS then
										unit_hold_s = FOURTH.SERIAL_MIN_HOLD_SECONDS
									end
									cast_gate.unit_until[ui_id] = tick_count + math.floor((unit_hold_s * 1000) / POLL_MS)
									cast_gate.unit_marker[ui_id] = ability.marker
									cast_gate.unit_logged[ui_id] = nil
									ADLOG_ARM
								end
'''


def fill(text, is_src):
    if is_src:
        text = text.replace("RELEASE_BLOCK",
            '\t\t\tif RELEASE_CONTROL_AFTER and took_control then\n'
            '\t\t\t\tlocal ok_release, err_release = pcall(function() uc:release_control() end)\n'
            '\t\t\t\tlog("  release_control         : ok=" .. tostring(ok_release)\n'
            '\t\t\t\t\t.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))\n'
            '\t\t\tend')
    else:
        text = text.replace("RELEASE_BLOCK",
            '\t\t\tif RELEASE_CONTROL_AFTER and took_control then\n'
            '\t\t\t\tpcall(function() uc:release_control() end)\n'
            '\t\t\tend')
    if is_src:
        text = text.replace("ADLOG_SAY",
            '\tlog("  " .. tostring(marker) .. " " .. note)')
        text = text.replace("ADLOG_PICK",
            '\tlog("  " .. marker .. " target: \'" .. etype .. "\' is the closest INFANTRY unit under the caster"\n'
            '\t\t.. " (distance=" .. string.format("%.1f", best_gap) .. "m bound=" .. tostring(bound)\n'
            '\t\t.. "m air_only=" .. tostring(FOURTH.ad_air_only == true) .. ")")')
        text = text.replace("ADLOG_SKIP",
            '\t\t\tlog("  " .. ad_marker_now .. " SKIPPED: the drop lapsed before the cast"\n'
            '\t\t\t\t.. " (caster_alive=" .. tostring(caster_alive) .. " flying=" .. tostring(fly_now)\n'
            '\t\t\t\t.. " melee=" .. tostring(melee_now) .. " enemy_alive=" .. tostring(enemy_alive)\n'
            '\t\t\t\t.. " infantry=" .. tostring(inf_now)\n'
            '\t\t\t\t.. ((gap_now ~= nil) and (" distance=" .. string.format("%.1f", gap_now) .. "m") or " distance=?")\n'
            '\t\t\t\t.. " bound=" .. tostring(ad_bound_now) .. "m) - cast not spent")')
        text = text.replace("ADLOG_OK",
            '\t\tlog("  " .. ad_marker_now .. " pre-cast re-check: still over an INFANTRY enemy"\n'
            '\t\t\t.. " (caster_alive=" .. tostring(caster_alive) .. " flying=" .. tostring(fly_now)\n'
            '\t\t\t.. " melee=" .. tostring(melee_now) .. " infantry=" .. tostring(inf_now)\n'
            '\t\t\t.. ", distance=" .. ((gap_now ~= nil) and string.format("%.1f", gap_now) or "?")\n'
            '\t\t\t.. "m bound=" .. tostring(ad_bound_now) .. "m) - firing")')
        text = text.replace("ADLOG_GATE",
            '\t\t\t\t\tlog("  per-unit cast gate " .. ability.marker .. ": unit " .. tostring(ui_id)\n'
            '\t\t\t\t\t\t.. " is still resolving \'" .. tostring(cast_gate.unit_marker[ui_id])\n'
            '\t\t\t\t\t\t.. "\' (" .. string.format("%.1f", ((cast_gate.unit_until[ui_id] - tick_count) * POLL_MS) / 1000)\n'
            '\t\t\t\t\t\t.. "s left) - waiting its turn (a second special ability would replace it)")')
        text = text.replace("ADLOG_ARM",
            '\t\t\t\t\tif not quiet then\n'
            '\t\t\t\t\t\tlog("  per-unit cast gate armed by " .. ability.marker .. ": no OTHER ability on unit "\n'
            '\t\t\t\t\t\t\t.. tostring(ui_id) .. " may be issued for " .. tostring(unit_hold_s)\n'
            '\t\t\t\t\t\t\t.. "s (wind-up + " .. tostring(IN_FLIGHT_SETTLE_SECONDS) .. "s, min "\n'
            '\t\t\t\t\t\t\t.. tostring(FOURTH.SERIAL_MIN_HOLD_SECONDS) .. "s)") \n'
            '\t\t\t\t\tend')
    else:
        text = text.replace("ADLOG_SAY", "\t-- (annotated copy: the held note is a log-only line)")
        text = text.replace("ADLOG_PICK", "\t-- (annotated copy: the target line is a log-only line)")
        text = text.replace("ADLOG_SKIP", "\t\t\t-- (annotated copy: the lapse line is a log-only line)")
        text = text.replace("ADLOG_OK", "\t\t-- (annotated copy: the re-check line is a log-only line)")
        text = text.replace("ADLOG_GATE", "\t\t\t\t\t-- (annotated copy: the wait line is a log-only line)")
        text = text.replace("RELEASE_BLOCK",
            '\t\t\tif RELEASE_CONTROL_AFTER and took_control then\n'
            '\t\t\t\tpcall(function() uc:release_control() end)\n'
            '\t\t\tend')
        text = text.replace("ADLOG_ARM", "\t\t\t\t\t-- (annotated copy: the armed line is a log-only line)")
    assert "ADLOG_" not in text and "RELEASE_BLOCK" not in text
    return text


def apply(s, is_src):
    # 1. Call of Tor on melee_skip_commanders, right after Arachneruption.
    a = ('\t{ marker = "arachneruption", name = "Arachneruption", trigger = "melee_skip_commanders",\n'
         '\t\tbadge = "zz_auto_badge_arachneruption",\n'
         '\t\tkeys = { "wh2_dlc15_unit_abilities_arachneruption" },\n'
         '\t\tox = 0, oy = 0 },\n')
    must(s, a)
    s = s.replace(a, a + fill(CALLLINE, is_src))

    # 2. The 12 air-drop entries after the last bombardment entry.
    a = ('\t{ marker = "wraith_storm", name = "Wraith Storm", trigger = "enemy_ground_melee_infantry",\n'
         '\t\tbadge = "zz_auto_badge_wraith_storm",\n'
         '\t\tkeys = { "wh2_dlc11_lord_abilities_wraith_storm" },\n'
         '\t\trange_real = 200,\n'
         '\t\tox = 0, oy = 0 },\n}')
    must(s, a)
    s = s.replace(a, a.replace("},\n}", "},\n") + fill(air_block(), is_src) + "}\n")

    # 3. The 10 m -> 7 m constant and its map entry.
    a = "FOURTH.ENEMY_CAST_R15  = 10"
    must(s, a)
    s = s.replace(a, "FOURTH.ENEMY_CAST_R10  = 7\n" + a)
    a = "\t[15]  = FOURTH.ENEMY_CAST_R15,"
    must(s, a)
    s = s.replace(a, "\t[10]  = FOURTH.ENEMY_CAST_R10,\n" + a)
    a = "--   real  15.0 m ->  10     real  75.0 m ->  52     real 180.0 m -> 126"
    must(s, a)
    s = s.replace(a, "--   real  10.0 m ->   7   (the air-drop family's own cast range)\n" + a)

    # 4. Charge-gate rows (multi-use pools whose recharge is slower than the
    #    2 s guard; the 0.1 s bombers refill faster than the guard).
    a = "\t\t-- ROUND 106: the bombardment family's multi-use pools (num_uses > 1)"
    must(s, a)
    s = s.replace(a, (
        "\t\t-- ROUND 107: Call of Tor and the air-drop family's multi-use pools.\n"
        "\t\t-- Only keys whose recharge is SLOWER than the 2 s guard are listed:\n"
        "\t\t-- the 0.1 s-recharge bombers (Gyrobomber 11 uses, Skyhammer 5, Wake\n"
        "\t\t-- of Fire 10, Gyrocopter 2) refill faster than the guard, so their\n"
        "\t\t-- pool can never drain and a hold would be dead weight.\n"
        '\t\t["wh3_twa07_spell_bound_call_of_tor"] = 90,\n'
        '\t\t["wh2_dlc12_lord_abilities_drop_sphere_of_tepok_upgraded"] = 5,\n'
        '\t\t["wh3_dlc25_unit_abilities_gyrobomber_fire_bomb"] = 3,\n'
        '\t\t["wh3_dlc25_unit_abilities_thunderbarge_fire_bomb"] = 3,\n'
        '\t\t["wh3_dlc24_unit_abilities_nan_gau_grenades"] = 60,\n'
        '\t\t["wh3_twa07_unit_abilities_searing_torrent"] = 60,\n'
        '\t\t["wh3_main_unit_abilities_sky_junk_bomb"] = 30,\n') + a)

    # 5. Wind-up rows for the two 1 s keys.
    a = ('\t\t["wh_main_spell_bound_soulfire"] = 1,\n'
         '\t\t["wh_dlc04_spell_bound_soulfire_upgraded"] = 1,\n')
    must(s, a)
    s = s.replace(a, a + (
        "\t\t-- ROUND 107: Call of Tor (1 s) and Sky-Junk Bomb (1 s). Every other\n"
        "\t\t-- air-drop declares wind_up_time = 0 and keeps the plain guard.\n"
        '\t\t["wh3_twa07_spell_bound_call_of_tor"] = 1,\n'
        '\t\t["wh3_main_unit_abilities_sky_junk_bomb"] = 1,\n'))

    # 6. The per-unit stagger constant.
    a = "local IN_FLIGHT_SETTLE_SECONDS = 2\n"
    must(s, a)
    s = s.replace(a, a + (
        "\n-- THE PER-UNIT SERIALISATION STAGGER (round 107). The engine allows ONE\n"
        "-- special ability in flight per unit: a second order REPLACES the first\n"
        "-- during its wind-up while the replaced cast's use is still spent (the\n"
        "-- Moondial / Wraith Storm pair in the 2026-10-17 field log - Moondial's\n"
        "-- 120 s recharge was consumed and its effect never landed). So a unit\n"
        "-- that has just cast may not be ordered to cast a DIFFERENT ability until\n"
        "-- its window closes: the wind-up it declared + IN_FLIGHT_SETTLE_SECONDS,\n"
        "-- never less than this stagger. 2.5 s is ten polls - two ready abilities\n"
        "-- fire in sequence, never together, and a buff is barely delayed.\n"
        "-- It is a FIELD of the FOURTH bag, not a chunk local: the main chunk sits\n"
        "-- exactly at Lua's 200-local ceiling.\n"
        "-- (The VALUE itself is set beside FOURTH.RANGE_FRACTION, below: the\n"
"-- FOURTH bag does not exist yet at this point in the chunk.)\n"))

    # 6b. The stagger VALUE, beside FOURTH.RANGE_FRACTION (FOURTH exists there).
    a = "FOURTH.RANGE_FRACTION = 0.70\n"
    must(s, a)
    s = s.replace(a, a + (
        "\n-- THE PER-UNIT SERIALISATION STAGGER (round 107): the minimum window a\n"
        "-- unit must wait after a cast before a DIFFERENT ability may be issued\n"
        "-- (the comment beside IN_FLIGHT_SETTLE_SECONDS states the why).\n"
        "FOURTH.SERIAL_MIN_HOLD_SECONDS = 2.5\n"))

    # 7. The cast_gate slots.
    a = ("\tlogged = {},       -- ui id -> (marker -> true once the gate has spoken for this pair)\n}")
    must(s, a)
    s = s.replace(a, (
        "\tlogged = {},       -- ui id -> (marker -> true once the gate has spoken for this pair)\n"
        "\t-- ROUND 107: THE PER-UNIT SERIALISATION WINDOW. One window per UNIT (not\n"
        "\t-- per pair): armed by every successful cast, it blocks a DIFFERENT\n"
        "\t-- ability on the same unit until it closes.\n"
        "\tunit_until = {},   -- ui id -> the tick before which no OTHER ability may be issued\n"
        "\tunit_marker = {},  -- ui id -> the marker of the cast that armed that window\n"
        "\tunit_logged = {},  -- ui id -> (marker -> true once the wait has been said this episode)\n"
        "}"))

    # 8. The helpers, right before the evaluator map.
    a = "\nFOURTH.evaluators = {"
    must(s, a)
    s = s.replace(a, "\n" + fill(HELPERS, is_src) + a)

    # 9. The fresh-controller hook in attempt_activation.
    a = ("\tif FOURTH.tz_self then\n"
         "\t\tif FOURTH.tz_caster_su ~= nil and FOURTH.tz_caster_su.uc ~= nil then\n"
         "\t\t\tuc = FOURTH.tz_caster_su.uc\n"
         "\t\tend\n"
         "\t\ttarget = unit\n"
         "\tend\n")
    must(s, a)
    s = s.replace(a, a + (
        "\t-- THE AIR-DROP FAMILY (round 107): the cast is SELF-CENTRED (the row has\n"
        "\t-- no target flags at all), so the target stays the OWNER - and the\n"
        "\t-- controller is the CASTER's script_unit re-fetched FRESH this tick, like\n"
        "\t-- every other cast here. The chosen enemy is the justification for the\n"
        "\t-- press, never the cast target.\n"
        "\tif FOURTH.ad_caster_su ~= nil and FOURTH.ad_caster_su.uc ~= nil then\n"
        "\t\tuc = FOURTH.ad_caster_su.uc\n"
        "\tend\n"))

    # 10. The air-drop pre-cast re-check, before the self-summon re-check.
    a = "\t-- SELF-SUMMON RE-CHECK (harness 102, Nurgling Tide)."
    must(s, a)
    s = s.replace(a, fill(RECHECK, is_src) + a)

    # 11. The per-unit gate, before the guard/attempt block.
    a = ("\t\t\t\t\t\t\tif eligible then\n"
         "\t\t\t\t\t\t\t\tlocal guard = last_attempt_at[ui_id]")
    must(s, a)
    s = s.replace(a, fill(GATE, is_src) + a)

    # 12. Arm the window on a real fire.
    a = ("\t\t\t\t\t\t\t\telseif outcome == \"fired\" then\n"
         "\t\t\t\t\t\t\t\t\t-- a real fire ends the cooldown episode\n"
         "\t\t\t\t\t\t\t\t\tlocal b = cooldown_hold[ui_id]\n"
         "\t\t\t\t\t\t\t\t\tif b ~= nil then\n"
         "\t\t\t\t\t\t\t\t\t\tb[ability.marker] = nil\n"
         "\t\t\t\t\t\t\t\t\tend\n")
    must(s, a)
    s = s.replace(a, a + fill(ARM, is_src))

    # 13. Purge the window with a dropped unit.
    a = ("\tcast_gate.until_tick[id_slot] = nil\n"
         "\tcast_gate.logged[id_slot] = nil\n")
    must(s, a)
    s = s.replace(a, a + (
        "\tcast_gate.unit_until[id_slot] = nil\n"
        "\tcast_gate.unit_marker[id_slot] = nil\n"
        "\tcast_gate.unit_logged[id_slot] = nil\n"))

    # 14. The poll: clear the air-drop slots before every evaluate...
    a = ("\t\t\t\t\tFOURTH.eg_noncommander = nil\n"
         "\t\t\t\t\tFOURTH.eg_infantry = nil\n"
         "\t\t\t\t\tFOURTH.eg_mode = nil\n")
    must(s, a)
    s = s.replace(a, a + (
        "\t\t\t\t\tFOURTH.ad_enemy = nil\n"
        "\t\t\t\t\tFOURTH.ad_caster_su = nil\n"
        "\t\t\t\t\tFOURTH.ad_air_only = nil\n"
        "\t\t\t\t\tFOURTH.ad_no_melee = nil\n"))

    # 15. ...and set them for the current ability.
    a = "\t\t\t\t\tFOURTH.eg_marker = ability.marker\n"
    must(s, a)
    s = s.replace(a, a + (
        "\t\t\t\t\t-- ROUND 107: the AIR-DROP family's own slots - its 70% bound\n"
        "\t\t\t\t\t-- (7 m from the row's 10 m), its marker, and the two usage\n"
        "\t\t\t\t\t-- flags the row declares.\n"
        "\t\t\t\t\tFOURTH.ad_range_m = ability.range_m\n"
        "\t\t\t\t\tFOURTH.ad_marker = ability.marker\n"
        "\t\t\t\t\tFOURTH.ad_air_only = (ability.air_only == true)\n"
        "\t\t\t\t\tFOURTH.ad_no_melee = (ability.no_melee == true)\n"))

    # 16. The evaluator map + the tooltip line.
    a = "\tmelee_skip_commanders = FOURTH.evaluate_melee_skip_commanders,\n"
    must(s, a)
    s = s.replace(a, a + (
        "\t-- ROUND 107: the \"on top of\" family - one evaluator, 12 entries.\n"
        "\tair_drop_on_infantry = FOURTH.evaluate_air_drop_on_infantry,\n"))

    a = ('\tenemy_ground_melee_infantry = "When armed, fires on the closest infantry unit in range that is fighting in melee",\n')
    must(s, a)
    s = s.replace(a, a + (
        '\tair_drop_on_infantry = "When armed, fires when this unit is over an infantry unit in range, airborne where the ability requires it",\n'))

    return s


def backup():
    os.makedirs(BAK, exist_ok=True)
    for p, name in ((SRC, "pre107_live.lua"), (ANN, "pre107_ann.lua")):
        dst = os.path.join(BAK, name)
        if not os.path.exists(dst):
            with open(p, "rb") as f:
                data = f.read()
            with open(dst, "wb") as f:
                f.write(data)
            print("backup", dst, hashlib.md5(data).hexdigest())


if __name__ == "__main__":
    backup()
    for path, is_src in ((SRC, True), (ANN, False)):
        s0 = read(path)
        s1 = apply(s0, is_src)
        write(path, s1)
        print("%-10s %d -> %d bytes" % (os.path.basename(path), len(s0), len(s1)))
