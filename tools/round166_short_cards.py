#!/usr/bin/env python3
"""Round 166 (harness 165): the short cards (user rulings 2026-11-17, after the Daemons battle).

  * THE CARD (user: "The tooltip for our A/M badge is amazing, it works. But the text is too long and not thematic. We
    need to be concise and condense the meaning of the triggers in the least amount of words possible. For example,
    Deadly Onslaught might say 'fires when charging'."): FOURTH.CARD_TIP is rewritten as one short sentence per family
    with no distances; the ability's name and 'on A:' are gone (the badge sits on the ability's own icon). The clause
    tables are rewritten the same way. Two tokens: {ALLYA} ('a nearby ally' / 'any ally' for an army-wide aura, absent
    without an aura) and {FF} (present unless the entry's WW row says its blast cannot hit our units).
  * THE ALL TOOLTIP (user's marked-up screenshot): only 'Arm or disarm every automatic ability of the selected
    unit(s).' stays.
  * THE WANDERERS (user: "'Caster doesn't count' for wanderers too? yes, do not count the caster"): the wanderer safety
    loop (kinds 2 and 3) skips the caster, as the waves (round 164) and Da Boss' Loons (kind 6, self_clear) already do.
The static card line ('Automatic: click the M/A badge ...') is removed by no longer shipping
ui/common ui/special_ability_tooltip.twui.xml (the round builder); nothing in the Lua changes for it.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

CARD_HEAD = '''-- ROUND 166 (user, 2026-11-17: "too long and not thematic ... condense the meaning of the triggers in the
-- least amount of words possible. For example, Deadly Onslaught might say 'fires when charging'"): ONE short
-- sentence per family, no distances (the 70% bounds stay in the code and the log); no name, no 'on A:'.
-- Tokens: {ALLYA} 'a nearby ally' ('any ally' for an army-wide aura; absent without an aura), {FF} present unless
-- the entry's WW row says its blast cannot hit our units, and the numbers {LS} {HL} {EXEC} {AREA} {AMMO} {ADMEN}.
FOURTH.CARD_TIP = {
	charge = "Fires when charging or in melee",
	charge_or_melee = "Fires when charging or in melee",
	charge_only = "Fires when charging",
	charge_or_wavering = "Fires when charging or wavering",
	tired = "Fires when tired",
	melee = "Fires in melee",
	melee_low_morale = "Fires in melee when wavering",
	melee_unwavering = "Fires in melee unless wavering",
	melee_health75 = "Fires in melee below 75% health",
	melee_skip_commanders = "Fires in melee, unless fighting only Lords or Heroes",
	melee_self_or_ally = "Fires on itself or the nearest ally in melee",
	self_summon_melee = "Fires in melee",
	barrier_broken = "Fires when its barrier breaks",
	ushoran_health = "Fires below 75% health",
	health_below_15 = "Fires below 15% health",
	self_last_stand = "Fires below {LS}% health in melee or under fire",
	health_aura_ground = "Fires under the most hurt unit nearby, below 75% health",
	health_aura_ally = "Fires on the most hurt unit nearby, below 75% health",
	health_aura_self = "Fires when it or a nearby ally is below 75% health",
	health_aura_self_undead = "Fires when it or a nearby undead ally is below 75% health",
	ally_hurt_melee = "Fires on the most hurt unit in melee nearby, below 75% health",
	glorious_death = "Fires when a nearby Slayer is in melee",
	verminking_wavering = "Fires when a nearby ally wavers in melee",
	metallurgy_melee = "Fires when it or a nearby ally is in melee",
	wavering_self = "Fires when wavering",
	wavering_self_or_ally = "Fires when it wavers, or a nearby ally wavers in melee",
	wavering_ally_range = "Fires on the nearest wavering ally",
	wavering_aura = "Fires when it or {ALLYA} wavers",
	melee_or_wavering_aura = "Fires when it or {ALLYA} is in melee or wavering",
	blood_sacrifice = "Fires on the most hurt nearby ally below 75% health",
	eat_da_runts = "Fires on itself, else the most hurt nearby ally, below 75% health",
	ally_heal = "Fires on the most hurt ally in range below 75% health",
	ally_heal_melee = "Fires in melee, on the most hurt ally in range below 75% health",
	ally_warmachine_heal = "Fires on the most hurt war machine in range below 75% health",
	ally_hellforged_heal = "Fires on the most hurt Hell-Forged unit in range below 75% health",
	ally_monster_heal = "Fires on the most hurt monster in range below 75% health",
	ally_construct_heal = "Fires on the most hurt construct in range below 75% health",
	ally_wavering = "Fires on the nearest wavering ally in range",
	ally_melee_buff = "Fires in melee unless wavering, on the nearest ally in range",
	ally_overseer = "Fires on the nearest ally in range",
	ally_beast = "Fires on the nearest beast ally in range",
	ally_broken = "Fires on the nearest routing ally in range",
	ally_missile = "Fires on the nearest missile ally in range",
	ally_infinite_buff = "Fires on the nearest ally",
	ally_winds = "Fires on the healthiest ally in range",
	ally_ammo_low = "Fires on the shooting ally in range lowest on ammo, at {AMMO}% or less",
	ally_blast = "Fires on itself or the ally amid the most enemies",
	allies_firing_aura = "Fires when it or {ALLYA} is shooting",
	self_or_ally_shooting = "Fires on itself, else the nearest ally in range, while shooting",
	melee_or_self_or_ally_shooting = "Fires in melee unless wavering, or on itself or the nearest ally in range while shooting",
	melee_or_shooting_self_or_ally = "Fires in melee unless wavering or while shooting, else on the nearest ally in range doing either",
	melee_or_shooting_aura = "Fires when it or a nearby ally is in melee or shooting",
	melee_or_shooting_into_melee = "Fires in melee unless wavering, or when shooting into a melee",
	self_shooting = "Fires while shooting",
	self_shooting_clear = "Fires while shooting at a target not in melee",
	self_shooting_healthy = "Fires while shooting, above 50% health",
	self_out_of_ammo = "Fires when out of ammo",
	self_moving = "Fires when moving",
	self_running = "Fires when running",
	no_enemy_in_range_within_boost = "Fires when an enemy is just beyond its missile range",
	ground_ally_before_range = "Fires under the nearest missile ally whose enemy is just beyond its range",
	under_fire = "Fires when it or {ALLYA} is under missile fire",
	melee_or_under_fire = "Fires in melee unless wavering, or under missile fire[, or when {ALLYA} is in melee or under fire]",
	self_recharging = "Fires while another of its abilities recharges",
	self_recharging_2 = "Fires while two of its other abilities recharge",
	recharging_in_reach = "Fires on itself or an ally in range while one of their abilities recharges",
	when_ready = "Fires when ready",
	enemy_engaged_or_shot = "Fires on the nearest enemy in melee, else one under missile fire",
	enemy_ground_area = "Fires under the nearest enemy in melee, else one under missile fire",
	enemy_melee = "Fires on the nearest enemy in melee",
	enemy_ground_melee = "Fires at the nearest enemy in melee",
	enemy_ground_melee_infantry = "Fires at the nearest enemy infantry in melee, not Lords or Heroes",
	enemy_melee_noncommander = "Fires on the nearest enemy in melee, not Lords or Heroes",
	enemy_low_health_noncommander = "Fires on the most hurt enemy below {HL}% health, not Lords or Heroes",
	enemy_wavering = "Fires on the nearest wavering enemy",
	enemy_missile_shooting = "Fires on the nearest shooting enemy missile unit",
	enemy_ground_shooting = "Fires under the nearest shooting enemy missile unit",
	enemy_melee_or_shooting = "Fires on the nearest enemy in melee, else a shooting missile unit",
	enemy_fast_near_ally = "Fires on a fast enemy closing on allies",
	enemy_melee_or_fast = "Fires on the nearest enemy in melee, else a fast enemy closing on allies",
	enemy_commander_value = "Fires on the most valuable enemy Lord or Hero",
	enemy_single_drain = "Fires when standing still, on the most valuable enemy monster or character",
	enemy_execute = "Fires on the most valuable enemy below {EXEC}% health",
	enemy_area_drain = "Fires when standing still, on the most valuable enemy infantry of {AREA}+ men",
	enemy_large_shot = "Fires on the most valuable large enemy clear of allies, else armoured infantry",
	enemy_single_shot = "Fires when standing still, on the most valuable enemy monster or character clear of allies",
	enemy_infantry_shot = "Fires when standing still, on the most valuable enemy infantry clear of allies",
	enemy_blob = "Fires when standing still, where the blast hurts the enemy most[, clear of allies{FF}]",
	enemy_blob_vortex = "Fires when standing still, where the blast hurts the enemy most[, clear of allies{FF}]",
	enemy_wave = "Fires when it and the target stand still, down the path with the most enemies[, clear of allies{FF}]",
	enemy_wave_charge = "Fires when standing still, at a fast enemy closing on allies[, its path clear of allies{FF}]",
	enemy_wander = "Fires when it and the target stand still, where the blast hurts the enemy most[, clear of allies{FF}]",
	enemy_strike = "Fires when standing still, under the most valuable standing monster or character[, clear of allies{FF}]",
	enemy_cone = "Fires when standing still, through the standing enemies it hurts most[, clear of allies{FF}]",
	enemy_sweep = "Fires in melee unless wavering, at the nearest enemy in melee[, clear of allies{FF}]",
	melee_clear = "Fires in melee unless wavering[, clear of allies{FF}]",
	fly_dive = "Fires while flying over an enemy[, clear of allies{FF}]",
	last_stand_clear = "Fires below {LS}% health in melee[, clear of allies{FF}]",
	air_drop_on_infantry = "Fires when over an enemy unit of more than {ADMEN} men",
}
-- the entry's enemy target class (round 135 onward), as a clause
FOURTH.CARD_CLASS = {
	commander = "Lords and Heroes only",
	commander_ground = "no flying targets[, clear of allies{FF}]",
	large = "large targets only",
	large_single = "monsters and large characters only",
	single = "monsters and characters only",
	not_flying = "no flying targets",
	flying = "flying targets only",
	not_undead = "no undead targets",
	missile = "missile units only",
}
'''

CARD_RULES = '''-- the four aura families without an aura (the caster alone)
FOURTH.CARD_TIP_NOAURA = { wavering_aura = "Fires when wavering", melee_or_wavering_aura = "Fires in melee or when wavering",
	allies_firing_aura = "Fires while shooting", under_fire = "Fires under missile fire" }
-- a clause the family's sentence already states is left out
FOURTH.CARD_SKIP = { enemy_commander_value = { commander = true }, enemy_single_shot = { single = true },
	enemy_single_drain = { single = true }, fly_dive = { G = true }, enemy_missile_shooting = { missile = true },
	enemy_ground_shooting = { missile = true } }
-- the game's caster rules (FOURTH.USAGE_TEXT) and ally target rules (FOURTH.ATARGET_TEXT), as clauses
FOURTH.CARD_USAGE = { M = "not in melee", G = "only in flight", F = "not in flight", V = "not while moving",
	W = "not when wavering", L = "only in large form" }
FOURTH.CARD_ATARGET = { C = "Lord or Hero allies only", c = "no Lords or Heroes", L = "large allies only",
	l = "no large units", F = "no flying units", U = "undead allies only", u = "no undead", S = "monster or character allies only",
	P = "missile allies only" }
'''

TOKENS_OLD = "\tt.MIST = string.format(\"%.2f\", FOURTH.MIST_BAND)\n\treturn t\nend\n"
TOKENS_NEW = ("\tt.MIST = string.format(\"%.2f\", FOURTH.MIST_BAND)\n"
              "\t-- ROUND 166: the short card's two words-only tokens\n"
              "\tif type(ability.aura_m) == \"number\" then t.ALLYA = (ability.aura_m < 0) and \"any ally\" or \"a nearby ally\" end\n"
              "\tif not (row ~= nil and not row.allies) then t.FF = \"\" end\n"
              "\treturn t\nend\n")
HEALTH_OLD = ('\t\tif u.hmin ~= nil then parts[#parts + 1] = "not below " .. FOURTH.card_num(u.hmin) .. "% health" end\n'
              '\t\tif u.hmax ~= nil then parts[#parts + 1] = "only at or below " .. FOURTH.card_num(u.hmax) .. "% health" end\n')
HEALTH_NEW = ('\t\tif u.hmin ~= nil then parts[#parts + 1] = "not below " .. FOURTH.card_num(u.hmin) .. "% health" end\n'
              '\t\tif u.hmax ~= nil then parts[#parts + 1] = "only at " .. FOURTH.card_num(u.hmax) .. "% health or less" end\n')
TPL_OLD = "\tlocal tpl = FOURTH.CARD_TIP[ability.trigger]\n"
TPL_NEW = ("\tlocal tpl = FOURTH.CARD_TIP[ability.trigger]\n"
           "\tif ability.aura_m == nil and FOURTH.CARD_TIP_NOAURA[ability.trigger] ~= nil then   -- ROUND 166\n"
           "\t\ttpl = FOURTH.CARD_TIP_NOAURA[ability.trigger]\n"
           "\tend\n")
RET_OLD = '\treturn tostring(ability.name) .. " on A: " .. table.concat(parts, "; ") .. "."\n'
RET_NEW = '\treturn table.concat(parts, "; ") .. "."   -- ROUND 166: no name, no \'on A:\'\n'
ALL_OLD = ('FOURTH.ALL_TIP = "ALL: arm or disarm every automatic ability of the selected unit(s). If any of them is on M, "\n'
           '\t.. "all go to A (automatic); if all are already on A, all go to M (manual). The button stays pressed while all "\n'
           '\t.. "of them are on A."\n')
ALL_NEW = ('-- ROUND 166 (the user\'s marked-up screenshot): only the first sentence stays\n'
           'FOURTH.ALL_TIP = "Arm or disarm every automatic ability of the selected unit(s)."\n')
WANDER_OLD = ("\telseif row.allies then\n"
              "\t\tlocal need = row.r + row.buf + FOURTH.SHOT_SAFE_M\n"
              "\t\tif row.kind == 3 then need = need + (e.half or 0) end\n"
              "\t\tfor i = 1, #m.ours do\n"
              "\t\t\tif FOURTH.blob_rect_gap(e.x, e.z, m.ours[i]) <= need then return nil end\n"
              "\t\tend\n"
              "\tend\n")
WANDER_NEW = ("\telseif row.allies then\n"
              "\t\tlocal need = row.r + row.buf + FOURTH.SHOT_SAFE_M\n"
              "\t\tif row.kind == 3 then need = need + (e.half or 0) end\n"
              "\t\t-- ROUND 166 (user ruling 2026-11-17, \"do not count the caster\"): the caster never blocks its own wanderer\n"
              "\t\tlocal self_id = nil\n"
              "\t\tpcall(function() self_id = tostring(unit:unique_ui_id()) end)\n"
              "\t\tfor i = 1, #m.ours do\n"
              "\t\t\tlocal oid = nil\n"
              "\t\t\tpcall(function() oid = tostring(m.ours[i].unit:unique_ui_id()) end)\n"
              "\t\t\tif (oid == nil or oid ~= self_id) and FOURTH.blob_rect_gap(e.x, e.z, m.ours[i]) <= need then return nil end\n"
              "\t\tend\n"
              "\tend\n")


def cut(s, start, end_marker):
    i = s.index(start)
    j = s.index(end_marker, i) + len(end_marker)
    return s[:i], s[i:j], s[j:]


def main():
    for path in (SRC, ANN):
        s = open(path, encoding="utf-8", newline="").read()
        assert "ROUND 166" not in s
        # the CARD_TIP and CARD_CLASS tables (from the table start to the end of CARD_CLASS)
        a, old, b = cut(s, "FOURTH.CARD_TIP = {\n", "\tmissile = \"missile units only\",\n}\n")
        assert old.count("FOURTH.CARD_CLASS = {") == 1
        s = a + CARD_HEAD + b
        a, old, b = cut(s, "-- a clause the family's sentence already states is left out\nFOURTH.CARD_SKIP = { enemy_commander_value",
                        "\tu = \"never on an undead unit\", S = \"single-entity allies only\", P = \"missile allies only\" }\n")
        assert old.count("FOURTH.CARD_ATARGET = {") == 1 and old.count("FOURTH.CARD_ALLY_FAMILY = {") == 1, old
        keep = old[old.index("-- the families whose target is chosen"):old.index("-- the game's caster rules (FOURTH.USAGE_TEXT)")]
        s = a + keep + CARD_RULES + b
        for o, n in ((TOKENS_OLD, TOKENS_NEW), (HEALTH_OLD, HEALTH_NEW), (RET_OLD, RET_NEW), (TPL_OLD, TPL_NEW), (ALL_OLD, ALL_NEW),
                     (WANDER_OLD, WANDER_NEW)):
            assert s.count(o) == 1, (path[-12:], o[:60], s.count(o))
            s = s.replace(o, n)
        assert "\u2014" not in s and "string.find" not in s.split("ROUND 166", 1)[1][:200]
        open(path, "w", encoding="utf-8", newline="").write(s)
        print(path, "patched")


if __name__ == "__main__":
    main()
