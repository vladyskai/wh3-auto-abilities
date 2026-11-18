#!/usr/bin/env python3
"""Round 175 (harness 174): Master of Mists, 'A: before range, else shooting' (user ruling 2026-11-18, after the
Aislinn battle: "But it also has plain damage boost!").

The game data (both keys): missile damage base and AP x1.25, reload +20, missile range x1.5, a 35 m area on the ground,
58 s (36 s for the custom key), 2 uses. The round-142 trigger (before range) stays first; when no missile unit of ours
is just out of range, the cast goes on the ground under a missile unit of ours (the caster or an ally within the 70%
bound) that is SHOOTING past its cast point, the one with the most shooting units within MIST_AREA_M (70% of the 35 m
area) around it, the closest on a tie. Re-checked before the cast (ah_mode "mist_shoot": still shooting).
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

CODE = '''-- ROUND 175: Master of Mists also raises missile damage x1.25 and reload +20 for its whole duration (user: "But it
-- also has plain damage boost!"; ruling 'A: before range, else shooting'). When no missile unit of ours is just out of
-- range, the ground under the SHOOTING missile unit with the most shooting units within MIST_AREA_M of it (the 35 m area
-- at the 70% rule), the closest on a tie.
FOURTH.MIST_AREA_REAL_M = 35   -- unit_special_abilities.effect_range of both Master of Mists keys
FOURTH.MIST_AREA_M = math.floor(FOURTH.MIST_AREA_REAL_M * 0.70)

function FOURTH.mist_shooting(unit)
	local cands = {}
	if FOURTH.shooting_past_cast_point(unit) then cands[#cands + 1] = { u = unit, gap = 0 } end
	local self_id = tostring(unit:unique_ui_id())
	for i = 1, #(tracked_units or {}) do
		local other = tracked_units[i] and tracked_units[i].unit
		if other ~= nil and other ~= unit then
			local ok_m, men = pcall(function() return other:number_of_men_alive() end)
			local ok_i, oid = pcall(function() return tostring(other:unique_ui_id()) end)
			if ok_m and type(men) == "number" and men > 0 and ok_i and oid ~= self_id and not unit_is_routing(other)
				and FOURTH.shooting_past_cast_point(other) then
				local gap = FOURTH.ab_ally_gap(unit, other)
				if gap ~= nil and FOURTH.ab_range_m ~= nil and gap <= FOURTH.ab_range_m then
					cands[#cands + 1] = { u = other, gap = gap }
				end
			end
		end
	end
	local best, bn = nil, nil
	for i = 1, #cands do
		local c = cands[i]
		local n = 0
		for j = 1, #cands do
			local near = (i == j)
			if not near then
				local ok_g, g = pcall(function() return c.u:unit_distance(cands[j].u) end)
				near = (ok_g and type(g) == "number" and g <= FOURTH.MIST_AREA_M)
			end
			if near then n = n + 1 end
		end
		if best == nil or n > bn or (n == bn and c.gap < best.gap) then best, bn = c, n end
	end
	if best == nil then return nil end
	FOURTH.ah_mode = "mist_shoot"
	FOURTH.ah_chosen = best.u
	FOURTH.ah_ground = true
	FOURTH.ah_caster_su = FOURTH.ab_fresh_friend_su(unit)
	local who = "the caster"
	if best.u ~= unit then
		FOURTH.ah_ally = best.u
		FOURTH.ah_ally_su = FOURTH.ab_fresh_friend_su(best.u)
		who = string.format("a friendly unit %.1fm away", best.gap)
	end
	return string.format("no missile unit is just out of range; %s is shooting with %d shooting unit(s) within %dm"
		.. " - cast on the ground under it (damage x1.25, reload +20)", who, bn, FOURTH.MIST_AREA_M)
end

'''

R = [
    ("function FOURTH.evaluate_ground_ally_before_range(unit, routing)\n",
     CODE + "function FOURTH.evaluate_ground_ally_before_range(unit, routing)\n"),
    # the recheck: the shooting arm re-checks that the chosen unit still shoots
    ('\t\tif FOURTH.ah_mode == "mist" then\n\t\t\thp_ok = (FOURTH.before_range(chosen, FOURTH.MIST_BAND) ~= nil)\n\t\tend\n',
     '\t\tif FOURTH.ah_mode == "mist" then\n\t\t\thp_ok = (FOURTH.before_range(chosen, FOURTH.MIST_BAND) ~= nil)\n\t\tend\n'
     '\t\tif FOURTH.ah_mode == "mist_shoot" then   -- ROUND 175: still shooting\n'
     '\t\t\thp_ok = FOURTH.shooting_past_cast_point(chosen)\n\t\tend\n'),
    ('\tground_ally_before_range = "When armed, fires under a friendly missile unit when the enemy is just out of its range",\n',
     '\tground_ally_before_range = "When armed, fires under a friendly missile unit when the enemy is just out of its range, else under the shooting missile units",   -- ROUND 175\n'),
    ('\tground_ally_before_range = "Fires under the nearest missile ally whose enemy is just beyond its range",\n',
     '\tground_ally_before_range = "Fires under missile allies just before their enemy is in range, else while they shoot",   -- ROUND 175\n'),
]
R_SRC = [('\tif best == nil then return nil end\n\tFOURTH.ah_chosen = best\n\tFOURTH.ah_ground = true\n',
          '\tif best == nil then return FOURTH.mist_shooting(unit) end   -- ROUND 175: else the shooting units\n'
          '\tFOURTH.ah_chosen = best\n\tFOURTH.ah_ground = true\n')]
R_ANN = [('\tif best == nil then return false end\n\tFOURTH.ah_chosen = best\n\tFOURTH.ah_ground = true\n',
          '\tif best == nil then return FOURTH.mist_shooting(unit) ~= nil end   -- ROUND 175: else the shooting units\n'
          '\tFOURTH.ah_chosen = best\n\tFOURTH.ah_ground = true\n')]

for path, extra in ((SRC, R_SRC), (ANN, R_ANN)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 175" not in s
    for o, n in R + extra:
        assert s.count(o) == 1, (path[-12:], o[:70], s.count(o))
        s = s.replace(o, n)
    if path == ANN:
        # the reading copy carries no log text: its shooting arm answers through the shared function above, which
        # returns a reason string (truthy); no log( call is added
        assert s.count("log(") == open(path, encoding="utf-8").read().count("log(")
    assert "\u2014" not in s
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path[-30:], "patched")
