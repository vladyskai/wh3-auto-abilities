#!/usr/bin/env python3
"""Round 182 (user, 2026-11-20): the finishers (last review row 23 and section 7).

  Executioner (row 23; ruling 2026-11-17 "the lowest health percentage"; 2026-11-20 "let's do 90%"): NEW enemy_finisher
    - the visible single-entity enemy with the LOWEST live health %, the most valuable on a tie, none of ours within
    10 m, the caster standing still (5 s wind-up); its bound is 90% of its real 250 m = 225 m (user ruling 2026-11-20:
    single entities have no edge-to-edge problem; FOURTH.SINGLE_RANGE_FRACTION, the entry field range_frac = 0.90).
  The Emperor's Executioner x2 (user 2026-11-20: "highest health % first that is below the 20/33% threshold"): the shot
    kind "execute" ranks the HIGHEST health % at or below the line, the most valuable on a tie.
  Skjalandir's Fall (user 2026-11-20: "Do what you think is more adequate"): the game's phase gives +90 accuracy and
    imbues EVERY hit (melee and shots) with Blinded! (x0.5 speed, -25 melee attack / defence / missile block / accuracy,
    26 s). NEW melee_or_self_shooting: in melee (not wavering) or shooting past its cast point, at any target.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
R = [
    ('\t{ marker = "lord_abilities_executioner", name = "Executioner", trigger = "enemy_blob",\n'
     '\t\tbadge = "zz_auto_badge_lord_abilities_executioner",\n'
     '\t\tkeys = { "wh2_dlc13_lord_abilities_executioner" },\n'
     '\t\trange_real = 250,\n',
     '\t-- ROUND 182 (finishers): enemy_finisher, 90% bound (user ruling 2026-11-20)\n'
     '\t{ marker = "lord_abilities_executioner", name = "Executioner", trigger = "enemy_finisher",\n'
     '\t\tbadge = "zz_auto_badge_lord_abilities_executioner",\n'
     '\t\tkeys = { "wh2_dlc13_lord_abilities_executioner" },\n'
     '\t\trange_real = 250,\n'
     '\t\trange_frac = 0.90,\n'),
    ('\t{ marker = "skjalandirs_fall", name = "Skjalandir\'s Fall", trigger = "melee_or_shooting_into_melee",',
     '\t-- ROUND 182 (finishers): melee_or_self_shooting (every hit blinds)\n'
     '\t{ marker = "skjalandirs_fall", name = "Skjalandir\'s Fall", trigger = "melee_or_self_shooting",'),
    # the 90% bound for a single-entity target (the one documented exception besides the air drop)
    ('\tif ability.range_real ~= nil then\n\t\tability.range_m = FOURTH.ENEMY_CAST[ability.range_real]\n\tend\n',
     '\tif ability.range_real ~= nil then\n\t\tability.range_m = FOURTH.ENEMY_CAST[ability.range_real]\n'
     '\t\t-- ROUND 182 (user ruling 2026-11-20, "let\'s do 90%"): a single-entity target and caster have no edge-to-edge\n'
     '\t\t-- gap worth a 30% margin, so the Executioner uses 90% of its real range (the documented exception)\n'
     '\t\tif ability.range_frac == FOURTH.SINGLE_RANGE_FRACTION then\n'
     '\t\t\tability.range_m = math.floor(ability.range_real * FOURTH.SINGLE_RANGE_FRACTION + 1e-9)\n'
     '\t\tend\n\tend\n'),
    # the shot kinds
    ('\t\telseif kind == "execute" then\n\t\t\tok_kind = FOURTH.exec_ok(e)\n\t\t\ts1 = e.value or 0\n',
     '\t\telseif kind == "execute" then\n\t\t\tok_kind = FOURTH.exec_ok(e)\n'
     '\t\t\t-- ROUND 182 (user, 2026-11-20): the HIGHEST health % below the line first, the most valuable on a tie\n'
     '\t\t\ts1 = FOURTH.enemy_health_pct(e.unit) or 0\n'
     '\t\t\ts2 = e.value or 0\n'
     '\t\telseif kind == "finisher" then   -- ROUND 182: the Executioner, the LOWEST health % first\n'
     '\t\t\tlocal hp = FOURTH.enemy_health_pct(e.unit)\n'
     '\t\t\tok_kind = (e.t ~= nil and FOURTH.class_keys.single[e.t] == true and type(hp) == "number")\n'
     '\t\t\ts1 = -(hp or 101)\n'
     '\t\t\ts2 = e.value or 0\n'),
    ('\t\t\tif (kind == "single" or kind == "drain") and not (e.t ~= nil and FOURTH.class_keys.single[e.t] == true) then',
     '\t\t\tif (kind == "single" or kind == "drain" or kind == "finisher") and not (e.t ~= nil and FOURTH.class_keys.single[e.t] == true) then'),
    # wiring
    ('\tmelee_clear_block = FOURTH.evaluate_melee_clear_block,   -- ROUND 181\n',
     '\tenemy_finisher = FOURTH.evaluate_enemy_finisher,   -- ROUND 182\n'
     '\tmelee_or_self_shooting = FOURTH.evaluate_melee_or_self_shooting,\n'
     '\tmelee_clear_block = FOURTH.evaluate_melee_clear_block,   -- ROUND 181\n'),
    ('\tmelee_clear_block = "When armed, fires in melee when none of our other units is inside its blast and at least 60 enemy soldiers are",   -- ROUND 181\n',
     '\tenemy_finisher = "When armed and standing still, fires on the single-entity enemy in range with the lowest health, none of yours near it",   -- ROUND 182\n'
     '\tmelee_or_self_shooting = "When armed, fires when this unit is in melee or shooting",\n'
     '\tmelee_clear_block = "When armed, fires in melee when none of our other units is inside its blast and at least 60 enemy soldiers are",   -- ROUND 181\n'),
    ('\tmelee_clear_block = "Fires in melee unless wavering[, clear of allies{FF}], with 60+ enemies in the blast",   -- ROUND 181\n',
     '\tenemy_finisher = "Fires[ when standing still{ANIM},] on the most hurt enemy monster or character clear of allies",   -- ROUND 182\n'
     '\tmelee_or_self_shooting = "Fires in melee unless wavering, or while shooting",\n'
     '\tmelee_clear_block = "Fires in melee unless wavering[, clear of allies{FF}], with 60+ enemies in the blast",   -- ROUND 181\n'),
    ('\tenemy_execute = "When armed, fires on the most valuable enemy in range whose health is at or below the execute line",',
     '\tenemy_execute = "When armed, fires on the enemy in range with the most health left at or below the execute line",   -- ROUND 182'),
    ('\tenemy_execute = "Fires on the most valuable enemy below {EXEC}% health",',
     '\tenemy_execute = "Fires on the healthiest enemy below {EXEC}% health",   -- ROUND 182'),
]
NEW_FNS = '''
-- ============================================================================
-- ROUND 182 - THE FINISHERS (the last review's row 23 and section 7; user rulings 2026-11-17 and 2026-11-20).
--   enemy_finisher (Executioner: damage x1 at full health to x4 at 1%): the visible single-entity enemy with the LOWEST
--     live health %, the most valuable on a tie, none of ours within SHOT_SAFE_M, the caster standing still; 90% bound.
--   enemy_execute (The Emperor's Executioner): the HIGHEST health % at or below the line (the shot kind "execute").
--   melee_or_self_shooting (Skjalandir's Fall: +90 accuracy, every hit blinds): in melee (not wavering) or shooting.
-- ============================================================================
FOURTH.SINGLE_RANGE_FRACTION = 0.90   -- user ruling 2026-11-20 (the Executioner; the documented exception to 0.70)

function FOURTH.evaluate_enemy_finisher(unit, routing)
	FOURTH.eg_mode = "shot"
	FOURTH.shot_kind = nil
	if routing or not FOURTH.shot_caster_ok(unit, true) then return nil end
	local m = FOURTH.blob_map(false)
	local e, s = FOURTH.shot_pick(unit, m, "finisher", false)
	if e == nil then return nil end
	FOURTH.shot_take(unit, e, "finisher", true)
	@@FIN_RETURN@@
end

function FOURTH.evaluate_melee_or_self_shooting(unit, routing)
	local r = FOURTH.evaluate_in_melee_self(unit, routing)
	if r then return r end
	return FOURTH.evaluate_self_shooting(unit, routing)
end
'''
FIN_LIVE = ('return FOURTH.shot_reason(unit, e, "the most hurt single-entity enemy (a finisher), standing still",\n'
            '\t\tstring.format("health %.0f%%, value %.0f", -s, e.value or 0))')
FN_ANCHOR = "\n-- ============================================================================\n-- ROUND 181 - LAND MINE"

for path in (SRC, ANN):
    live = (path == SRC)
    s = open(path, encoding="utf-8", newline="").read()
    for a, b in R:
        assert s.count(a) == 1, (path[-12:], a[:90], s.count(a))
        s = s.replace(a, b)
    fns = NEW_FNS.replace("@@FIN_RETURN@@", FIN_LIVE if live else "return true")
    assert s.count(FN_ANCHOR) == 1, path
    s = s.replace(FN_ANCHOR, "\n" + fns.strip("\n") + "\n" + FN_ANCHOR, 1)
    assert "@@" not in s
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path[-36:], "patched")
