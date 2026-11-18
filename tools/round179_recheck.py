#!/usr/bin/env python3
"""Round 179: the shared heal re-check learns the two new rules (found by harness 177 world S3: Star of Avelorn never
cast past its 10 m area because the re-check tested the chosen ally against the AREA, not the 140 m cast bound).

  ah_mode "spot" (heal_ground_best): the chosen unit must still be inside the 70% CAST bound (FOURTH.ab_range_m).
  ah_mode "deep" (health_aura_ally_deep): the chosen unit must still be at or below FOURTH.HEAL_DEEP_PCT.
The live heal_ground_best writes its own ally line (the shared ah_log_ally prints the area radius as the reach)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
R = [
    ("\t\t\tin_reach = (FOURTH.ah_range_m == nil) or (gap_now == nil) or (gap_now <= FOURTH.ah_range_m)\n",
     "\t\t\tin_reach = (FOURTH.ah_range_m == nil) or (gap_now == nil) or (gap_now <= FOURTH.ah_range_m)\n"
     "\t\t\tif FOURTH.ah_mode == \"spot\" then   -- ROUND 179: Star of Avelorn reaches its 70% cast bound, not its area\n"
     "\t\t\t\tin_reach = (FOURTH.ab_range_m == nil) or (gap_now == nil) or (gap_now <= FOURTH.ab_range_m)\n"
     "\t\t\tend\n"),
    ("\t\tlocal hp_ok = (type(hp_now) ~= \"number\") or (hp_now <= 75)\n",
     "\t\tlocal hp_ok = (type(hp_now) ~= \"number\") or (hp_now <= 75)\n"
     "\t\tif FOURTH.ah_mode == \"deep\" then   -- ROUND 179: Berry Wine's deeper line\n"
     "\t\t\thp_ok = (type(hp_now) ~= \"number\") or (hp_now <= FOURTH.HEAL_DEEP_PCT)\n"
     "\t\tend\n"),
    ("\tif chosen == nil then return nil end\n\tFOURTH.ah_chosen = chosen\n\tFOURTH.ah_caster_su = FOURTH.ab_fresh_friend_su(unit)\n"
     "\tif chosen == unit then\n\t\treturn string.format(\"health %d%% (<= %d%%)\", math.floor(hp), FOURTH.HEAL_DEEP_PCT)\n",
     "\tif chosen == nil then return nil end\n\tFOURTH.ah_mode = \"deep\"\n\tFOURTH.ah_chosen = chosen\n"
     "\tFOURTH.ah_caster_su = FOURTH.ab_fresh_friend_su(unit)\n"
     "\tif chosen == unit then\n\t\treturn string.format(\"health %d%% (<= %d%%)\", math.floor(hp), FOURTH.HEAL_DEEP_PCT)\n"),
    ("\tif best == nil then return nil end\n\tFOURTH.ah_chosen = best.u\n\tFOURTH.ah_ground = true\n",
     "\tif best == nil then return nil end\n\tFOURTH.ah_mode = \"spot\"\n\tFOURTH.ah_chosen = best.u\n\tFOURTH.ah_ground = true\n"),
]
LIVE_ONLY = [
    ('\tFOURTH.ah_log_ally(best.u, best.hp, best.gap, "cast on the ground under that ally")\n',
     '\tlocal atype = "ally"\n'
     '\tpcall(function() atype = tostring(best.u:type()) end)\n'
     '\tlog("  " .. tostring(FOURTH.ah_marker) .. " ally: \'" .. atype .. "\' is the chosen spot (health "\n'
     '\t\t.. string.format("%.0f", best.hp) .. "%, distance " .. string.format("%.1f", best.gap) .. "m of "\n'
     '\t\t.. tostring(reach) .. "m cast bound, " .. best_n .. " other hurt unit(s) within " .. tostring(spot)\n'
     '\t\t.. "m) - cast on the ground under that ally")\n'),
]
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    for a, b in R + (LIVE_ONLY if path == SRC else []):
        assert s.count(a) == 1, (path[-12:], a[:80], s.count(a))
        s = s.replace(a, b)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path[-36:], "patched")
