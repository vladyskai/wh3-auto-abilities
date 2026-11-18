#!/usr/bin/env python3
"""Round 179: the score-3 review, rows 115-134 (user, 2026-11-18: "Items 115-134 approved"), built from the CURRENT text
of each row in docs\\WH3_score3_review_2026-11-18.md (re-read from disk).

  115-117 Inspired Assault I-III: NEW ally_charge_or_melee - the nearest ally charging, else in fresh contact, else in
          melee; never a missile unit.
  118-121 Inspired Defence I-III, Da Boss 'as a Plan!: NEW ally_melee_wavering_first - the nearest ally in melee, a
          wavering one first.
  122     Favour of the Fay: melee_self_or_ally (exists).
  123     Orcs are da Best!: NEW ally_value_melee - the most valuable ally in melee, never a missile unit.
  124     Hellish Vigour: NEW ally_in_melee - the nearest ally in melee.
  127     Berry Wine: NEW health_aura_ally_deep - the lowest unit at or below 55%.
  129     Star of Avelorn: NEW heal_ground_best - the ground under the hurt unit of ours (the caster included, 75% or
          less) within 140 m with the most hurt units within 10 m of it (70% of its 15 m area).
  130-131 Commanding Presence, Fury of Ulric: wavering_self_or_ally drops its hidden "ally in melee" condition.
  133     Grut's Sickle: ally_winds - only when the winds pool is below 30 with reserve 20+; an EXPENDABLE ally first
          (the most hit points), else the ally with the LOWEST live value above 75% health.
  Kept: 125, 126, 132, 134 (RULED / KEEP). 128 (Cold-Blooded): its RULED trigger stays; the Lizardmen-only
  restriction waits (the doc promised to show the set first).
  Every moved entry left a family that starts armed; it keeps its default with start_armed = true.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

MOVES = [  # marker, name, old family, new family, extra field line (or "")
    ("inspired_assault_i", "Inspired Assault I", "ally_melee_buff", "ally_charge_or_melee", ""),
    ("inspired_assault_ii", "Inspired Assault II", "ally_melee_buff", "ally_charge_or_melee", ""),
    ("inspired_assault_iii", "Inspired Assault III", "ally_melee_buff", "ally_charge_or_melee", ""),
    ("inspired_defence_i", "Inspired Defence I", "ally_melee_buff", "ally_melee_wavering_first", ""),
    ("inspired_defence_ii", "Inspired Defence II", "ally_melee_buff", "ally_melee_wavering_first", ""),
    ("inspired_defence_iii", "Inspired Defence III", "ally_melee_buff", "ally_melee_wavering_first", ""),
    ("da_boss_as_a_plan", "Da Boss 'as a Plan!", "ally_melee_buff", "ally_melee_wavering_first", ""),
    ("favour_of_the_fay", "Favour of the Fay", "ally_melee_buff", "melee_self_or_ally", ""),
    ("orcs_are_da_best", "Orcs are da Best!", "ally_melee_buff", "ally_value_melee", ""),
    ("hellish_vigour", "Hellish Vigour", "ally_melee_buff", "ally_in_melee", ""),
    ("berry_wine", "Berry Wine", "health_aura_ally", "health_aura_ally_deep", ""),
    ("star_of_avelorn", "Star of Avelorn", "health_aura_ground", "heal_ground_best", "\t\tally_range_real = 200,\n"),
]


def move_entry(s, marker, name, old, new, extra):
    head = '\t{ marker = "%s", name = "%s", trigger = "%s",' % (marker, name, old)
    assert s.count(head) == 1, (marker, s.count(head))
    i = s.index(head)
    tail = "\t\tox = 0, oy = 0 },"
    j = s.index(tail, i)
    block = s[i:j]
    assert "start_armed" not in block, marker
    nb = ('\t-- ROUND 179 (score-3 review): %s\n' % new) + block.replace(head, '\t{ marker = "%s", name = "%s", trigger = "%s",' % (marker, name, new), 1)
    nb += extra + "\t\tstart_armed = true,   -- ROUND 179: its old family started armed\n"
    return s[:i] + nb + s[j:]


R = [
    # ---- the ranked ally modes
    ('\tvalue_under_fire = "the most valuable ally under missile fire",   -- ROUND 177\n}\n',
     '\tvalue_under_fire = "the most valuable ally under missile fire",   -- ROUND 177\n'
     '\tcharge_contact_melee = "the closest ally charging, else in fresh contact, else in melee",   -- ROUND 179\n'
     '\tmelee_wavering_first = "the closest ally in melee, a wavering one first",   -- ROUND 179\n'
     '\tvalue_melee = "the most valuable ally in melee",   -- ROUND 179\n'
     '\texpendable_hp = "the expendable ally with the most hit points",   -- ROUND 179\n'
     '\tcheap_healthy = "the cheapest ally above 75% health (score = minus its value)",   -- ROUND 179\n}\n'),
    ('function FOURTH.ab_rank(u, family)\n',
     'function FOURTH.ab_rank(u, family)\n'
     '\tif family == "charge_contact_melee" then   -- ROUND 179: Inspired Assault\n'
     '\t\tlocal w = FOURTH.charge_moment(u)\n'
     '\t\tif w == "charging" then return 3 end\n'
     '\t\tif w ~= nil then return 2 end\n'
     '\t\tlocal ok_c, mc = pcall(function() return u:is_in_melee() end)\n'
     '\t\tif ok_c and mc == true then return 1 end\n'
     '\t\treturn nil\n'
     '\tend\n'
     '\tif family == "expendable_hp" then   -- ROUND 179: Grut\'s Sickle, an expendable ally first\n'
     '\t\tlocal t = FOURTH.type_plain(u)\n'
     '\t\tif t == nil or FOURTH.class_keys.expendable[t] ~= true then return nil end\n'
     '\t\tlocal v = FOURTH.context_value(u, "HealthValue")\n'
     '\t\tif type(v) == "number" then return v end\n'
     '\t\treturn nil\n'
     '\tend\n'
     '\tif family == "cheap_healthy" then   -- ROUND 179: Grut\'s Sickle, else the cheapest ally above 75%\n'
     '\t\tlocal hp = FOURTH.health_pct(u)\n'
     '\t\tlocal v = FOURTH.unit_value(u)\n'
     '\t\tif type(hp) == "number" and hp > FOURTH.GRUT_HEALTHY_PCT and type(v) == "number" then return -v end\n'
     '\t\treturn nil\n'
     '\tend\n'),
    ('\tif family == "value_melee_risk" then\n',
     '\tif family == "melee_wavering_first" then   -- ROUND 179: Inspired Defence, Da Boss\n'
     '\t\tif FOURTH.wavering(u) == true then return 2 end\n'
     '\t\treturn 1\n'
     '\tend\n'
     '\tif family == "value_melee" then return FOURTH.unit_value(u) end   -- ROUND 179: Orcs are da Best!\n'
     '\tif family == "value_melee_risk" then\n'),
    # ---- Grut's Sickle
    ('function FOURTH.evaluate_ally_winds(unit, routing)\n\treturn FOURTH.ab_pick_ally(unit, routing, "winds")\nend\n',
     '-- ROUND 179 (user, 2026-11-18: "on expendable ally first (highest hp), then on the ally with lowest value above\n'
     '-- 75%"): only when the winds pool is low (the round-171 winds_low line: pool below 30, reserve 20 or more).\n'
     'FOURTH.GRUT_HEALTHY_PCT = 75\n'
     'function FOURTH.evaluate_ally_winds(unit, routing)\n'
     '\tif routing then return nil end\n'
     '\tlocal c, r = FOURTH.winds_now()\n'
     '\tif c == nil or c >= FOURTH.WINDS_LOW_POOL or r < FOURTH.WINDS_LOW_RESERVE then return nil end\n'
     '\tlocal res = FOURTH.ab_pick_ally(unit, routing, "expendable_hp")\n'
     '\tif res then return res end\n'
     '\treturn FOURTH.ab_pick_ally(unit, routing, "cheap_healthy")\n'
     'end\n'),
    # ---- Commanding Presence, Fury of Ulric: no hidden melee condition
    ('\t\t\t\t\t\tand other:is_in_melee() and not unit_is_routing(other)\n'
     '\t\t\t\t\t\tand FOURTH.wavering(other) == true then\n'
     '\t\t\t\t\t\tlocal gap = FOURTH.ws_ally_gap(unit, other)',
     '\t\t\t\t\t\tand not unit_is_routing(other)   -- ROUND 179: no melee condition (the user\'s ruling)\n'
     '\t\t\t\t\t\tand FOURTH.wavering(other) == true then\n'
     '\t\t\t\t\t\tlocal gap = FOURTH.ws_ally_gap(unit, other)'),
    ('\twavering_self_or_ally = "Fires when it wavers, or a nearby ally wavers in melee",',
     '\twavering_self_or_ally = "Fires when it wavers, or a nearby ally wavers",   -- ROUND 179'),
    # ---- wiring
    ('\tally_squig_melee = FOURTH.evaluate_ally_squig_melee,\n',
     '\tally_squig_melee = FOURTH.evaluate_ally_squig_melee,\n'
     '\tally_charge_or_melee = FOURTH.evaluate_ally_charge_or_melee,   -- ROUND 179\n'
     '\tally_melee_wavering_first = FOURTH.evaluate_ally_melee_wavering_first,\n'
     '\tally_value_melee = FOURTH.evaluate_ally_value_melee,\n'
     '\tally_in_melee = FOURTH.evaluate_ally_in_melee,\n'
     '\thealth_aura_ally_deep = FOURTH.evaluate_health_aura_ally_deep,\n'
     '\theal_ground_best = FOURTH.evaluate_heal_ground_best,\n'),
    ('\tally_squig_melee = "When armed, fires on the nearest squig ally in melee",\n',
     '\tally_squig_melee = "When armed, fires on the nearest squig ally in melee",\n'
     '\tally_charge_or_melee = "When armed, fires on the nearest ally charging, else just in contact, else in melee (never a missile unit)",   -- ROUND 179\n'
     '\tally_melee_wavering_first = "When armed, fires on the nearest ally in melee, a wavering one first",\n'
     '\tally_value_melee = "When armed, fires on the most valuable ally in melee (never a missile unit)",\n'
     '\tally_in_melee = "When armed, fires on the nearest ally in melee",\n'
     '\thealth_aura_ally_deep = "When armed, fires when this unit or a friendly unit in range is at or below 55% health, cast on it",\n'
     '\theal_ground_best = "When armed, fires on the ground under the hurt unit (75% or less) with the most hurt units around it",\n'),
    ('\tally_winds = "When armed, fires on the ally with the most hit points remaining, cast on that ally",',
     '\tally_winds = "When armed and the winds run low, fires on the expendable ally with the most hit points, else on the cheapest ally above 75% health",   -- ROUND 179'),
    ('\tally_squig_melee = "Fires on a squig ally in melee",\n',
     '\tally_squig_melee = "Fires on a squig ally in melee",\n'
     '\tally_charge_or_melee = "Fires on an ally charging, else just in contact, else in melee; no missile units",   -- ROUND 179\n'
     '\tally_melee_wavering_first = "Fires on the nearest ally in melee, a wavering one first",\n'
     '\tally_value_melee = "Fires on the most valuable ally in melee; no missile units",\n'
     '\tally_in_melee = "Fires on the nearest ally in melee",\n'
     '\thealth_aura_ally_deep = "Fires on the most hurt unit nearby, below 55% health",\n'
     '\theal_ground_best = "Fires under the hurt unit with the most hurt units around it",\n'),
    ('\tally_winds = "Fires on the healthiest ally in range",',
     '\tally_winds = "Fires when the winds run low, on an expendable ally, else the cheapest healthy one",   -- ROUND 179'),
]
NEW_FNS = '''
-- ============================================================================
-- ROUND 179 - THE SCORE-3 REVIEW, ROWS 115-134 (user, 2026-11-18: "Items 115-134 approved").
--   ally_charge_or_melee (Inspired Assault I-III): the nearest ally charging, else in fresh contact, else in melee;
--     never a missile unit.
--   ally_melee_wavering_first (Inspired Defence I-III, Da Boss 'as a Plan!): the nearest ally in melee, a wavering one
--     first.
--   ally_value_melee (Orcs are da Best!): the most valuable ally in melee, never a missile unit.
--   ally_in_melee (Hellish Vigour): the nearest ally in melee (the reflection pays when it is struck).
--   health_aura_ally_deep (Berry Wine): the health_aura_ally rule with the line at 55% (a 45% heal wastes less).
--   heal_ground_best (Star of Avelorn): the ground under the hurt unit of ours (the caster included, 75% or less)
--     within the 70% cast bound with the most OTHER hurt units within the 70% area (10 m of its 15 m); the lower
--     health on a tie.
-- ============================================================================
function FOURTH.evaluate_ally_charge_or_melee(unit, routing)
	FOURTH.ab_filter = "not_missile"
	return FOURTH.ab_pick_ally(unit, routing, "charge_contact_melee")
end
function FOURTH.evaluate_ally_melee_wavering_first(unit, routing)
	return FOURTH.ab_pick_ally(unit, routing, "melee_wavering_first")
end
function FOURTH.evaluate_ally_value_melee(unit, routing)
	FOURTH.ab_filter = "not_missile"
	return FOURTH.ab_pick_ally(unit, routing, "value_melee")
end
function FOURTH.evaluate_ally_in_melee(unit, routing)
	return FOURTH.ab_pick_ally(unit, routing, "melee")
end

FOURTH.HEAL_DEEP_PCT = 55   -- Berry Wine (user approval 2026-11-18, review row 127)
function FOURTH.evaluate_health_aura_ally_deep(unit, routing)
	local chosen, hp, gap = FOURTH.ah_pick_where(unit, routing, function(u)
		local h = FOURTH.health_pct(u)
		return type(h) == "number" and h <= FOURTH.HEAL_DEEP_PCT
	end)
	if chosen == nil then return nil end
	FOURTH.ah_chosen = chosen
	FOURTH.ah_caster_su = FOURTH.ab_fresh_friend_su(unit)
	if chosen == unit then
		return string.format("health %d%% (<= %d%%)", math.floor(hp), FOURTH.HEAL_DEEP_PCT)
	end
	FOURTH.ah_ally = chosen
	FOURTH.ah_ally_su = FOURTH.ab_fresh_friend_su(chosen)
	FOURTH.cast_target = chosen
	FOURTH.ah_log_ally(chosen, hp, gap, "cast on that ally")
	return string.format("%s: lowest-health unit in range is an ALLY at %d%% (<= %d%%), distance %s of %sm %s - cast on the ally",
		tostring(FOURTH.ah_marker or "ally"), math.floor(hp), FOURTH.HEAL_DEEP_PCT,
		((gap ~= nil) and string.format("%.1f", gap) or "?"), tostring(FOURTH.ah_range_m), tostring(FOURTH.ah_range_word))
end

FOURTH.HEAL_SPOT_PCT = 75   -- Star of Avelorn: a unit at or below this health counts as hurt
function FOURTH.evaluate_heal_ground_best(unit, routing)
	if routing then return nil end
	local reach, spot = FOURTH.ab_range_m, FOURTH.ah_range_m
	if reach == nil or spot == nil then return nil end
	local hurt = {}
	local self_hp = FOURTH.health_pct(unit)
	if type(self_hp) == "number" and self_hp <= FOURTH.HEAL_SPOT_PCT then hurt[#hurt + 1] = { u = unit, hp = self_hp, gap = 0 } end
	local self_id = tostring(unit:unique_ui_id())
	for i = 1, #tracked_units do
		local other = tracked_units[i] and tracked_units[i].unit
		if other ~= nil and other ~= unit and other:number_of_men_alive() > 0
			and tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other) then
			local hp = FOURTH.health_pct(other)
			if type(hp) == "number" and hp <= FOURTH.HEAL_SPOT_PCT then
				local gap = FOURTH.ab_ally_gap(unit, other)
				if gap ~= nil and gap <= reach then hurt[#hurt + 1] = { u = other, hp = hp, gap = gap } end
			end
		end
	end
	local best, best_n = nil, nil
	for i = 1, #hurt do
		local n = 0
		for j = 1, #hurt do
			if j ~= i then
				local g = FOURTH.ab_ally_gap(hurt[i].u, hurt[j].u)
				if g ~= nil and g <= spot then n = n + 1 end
			end
		end
		if best == nil or n > best_n or (n == best_n and hurt[i].hp < best.hp) then best, best_n = hurt[i], n end
	end
	if best == nil then return nil end
	FOURTH.ah_chosen = best.u
	FOURTH.ah_ground = true
	FOURTH.ah_caster_su = FOURTH.ab_fresh_friend_su(unit)
	if best.u == unit then
		return string.format("heal spot: the caster at %d%% (<= %d%%), %d other hurt unit(s) within %dm - cast at its feet",
			math.floor(best.hp), FOURTH.HEAL_SPOT_PCT, best_n, spot)
	end
	FOURTH.ah_ally = best.u
	FOURTH.ah_ally_su = FOURTH.ab_fresh_friend_su(best.u)
	FOURTH.ah_log_ally(best.u, best.hp, best.gap, "cast on the ground under that ally")
	return string.format("heal spot: an ally at %d%% (<= %d%%), %d other hurt unit(s) within %dm, distance %.1f of %dm - cast under the ally",
		math.floor(best.hp), FOURTH.HEAL_SPOT_PCT, best_n, spot, best.gap, reach)
end
'''
FN_ANCHOR = "\n-- ============================================================================\n-- ROUND 177 - THE SCORE-3 REVIEW, ROWS 1-22"

for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    for a, b in R:
        if s.count(a) == 0 and a.startswith("\t\t\t\t\t\tand other:is_in_melee()"):
            # the reading copy indents this loop one tab less
            a = a.replace("\n\t\t\t\t\t\t", "\n\t\t\t\t\t")[1:]
            b = b.replace("\n\t\t\t\t\t\t", "\n\t\t\t\t\t")[1:]
        assert s.count(a) == 1, (path[-12:], a[:90], s.count(a))
        s = s.replace(a, b)
    for m in MOVES:
        s = move_entry(s, *m)
    assert s.count(FN_ANCHOR) == 1, (path[-12:], s.count(FN_ANCHOR))
    s = s.replace(FN_ANCHOR, "\n" + NEW_FNS.strip("\n") + "\n" + FN_ANCHOR, 1)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path[-36:], "patched")
