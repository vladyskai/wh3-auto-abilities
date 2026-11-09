#!/usr/bin/env python3
"""Round 135 (harness 134): audit batch 4 - the enemy slows, and the target filters.

User rulings 2026-11-09 (audit group R4):
  * group 1, slow plus a melee-stat cut (11): "Enemy in melee" (the existing enemy_melee family);
  * group 2, pure slows (Mither, Rune of Slowness, Master Rune of Slowness, Whispering Mist), the
    user's own design: "Enemy moving close to an ally that has at least cavalry speed ... No need to
    detect if the enemy charges or not ... the enemy cannot be far from the ally units."
    Settings: run speed 5 m/s or more (fast_speed()), within 40 m of one of our units -> the NEW
    enemy_fast_near_ally family;
  * group 3 (Looming Dread, Book of Secrets, Fecund Rebirth) and Hunter of Champions keep
    enemy_engaged_or_shot, "but make sure the trigger filters for the enemy unit type";
  * the target filters: "Yes, all 15 now" - every automated enemy-targeted ability whose game row
    says Lord/Hero only (unit_is_not_commander_class), large only (unit_is_not_large) or large single
    entity (+ unit_is_not_single_entity) gets target_class; the shared enemy picker and its pre-cast
    re-check skip an enemy outside the class.
No string.find. Every helper is a FOURTH field (the 200-local ceiling).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_unit_size_keys as G  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

TO_MELEE = ["acquiescence", "el_syf", "frost_shard_glaive", "hidden_huntress", "hidden_huntress_upgraded",
            "hornswaggle", "marked_for_eatin", "taunt", "titan_headsman", "youre_next", "tendrils_of_the_sea"]
TO_FAST = ["mither", "rune_of_slowness", "master_rune_of_slowness", "whispering_mist"]
CLASS = {m: "commander" for m in ("el_syf", "youre_next", "hunter_of_champions", "looming_dread", "assassins_trophy",
                                  "glory_seeker", "glory_seeker_upgraded", "headhunt", "prey_of_the_blood_god",
                                  "they_needs_stabbin", "trophy_heads", "transfix_hex")}
CLASS.update({"tendrils_of_the_sea": "large", "whip_of_misery": "large", "mark_of_the_monster": "large_single"})
assert len(CLASS) == 15


def entry_span(s, marker):
    tag = '\t{ marker = "%s",' % marker
    assert s.count(tag) == 1, marker
    a = s.index(tag)
    b = s.index("ox = 0, oy = 0 },\n", a) + len("ox = 0, oy = 0 },\n")
    block = s[a:b]
    assert block.count("\t{ marker = ") == 1, marker
    return a, b, block


def apply_roster(s):
    for m in TO_MELEE + TO_FAST:
        a, b, block = entry_span(s, m)
        assert 'trigger = "enemy_engaged_or_shot",' in block, m
        fam = "enemy_melee" if m in TO_MELEE else "enemy_fast_near_ally"
        s = s[:a] + block.replace('trigger = "enemy_engaged_or_shot",', 'trigger = "%s",' % fam) + s[b:]
    for m, cls in CLASS.items():
        a, b, block = entry_span(s, m)
        assert "target_class" not in block and "range_real = " in block, m
        nb = block.replace("\t\tox = 0, oy = 0 },\n", '\t\ttarget_class = "%s",\n\t\tox = 0, oy = 0 },\n' % cls)
        s = s[:a] + nb + s[b:]
    return s


def sub(s, a, b, n=1):
    assert s.count(a) == n, (a[:80], s.count(a))
    return s.replace(a, b)


HDR = """-- ============================================================================
-- ROUND 135 - AUDIT BATCH 4: THE ENEMY SLOWS AND THE TARGET FILTERS
-- (user rulings 2026-11-09).
--   enemy_melee gains the 11 slows that also cut melee stats (no missile arm).
--   enemy_fast_near_ally (NEW; Mither, Rune of Slowness, Master Rune of
--     Slowness, Whispering Mist), the user's own design: the closest enemy
--     inside the ability's 70% cast bound that is MOVING, has a run speed of
--     FAST_ENEMY_MPS or more (fast_speed(), the unit's live run speed in m/s)
--     and is within FAST_ENEMY_NEAR_M of one of our units (edge to edge, the
--     caster counting). No charge detection. Cast at that enemy.
--   target_class (15 entries): the engine refuses an enemy outside the
--     ability's own invalid-target flags, so the picker skips it:
--     "commander" (Lord/Hero only), "large", "large_single" (large and a
--     single entity). The large and single sets are GENERATED from the game
--     data (tools/gen_unit_size_keys.py); an unreadable type never qualifies.
-- ============================================================================
FOURTH.FAST_ENEMY_MPS = 5      -- user setting 2026-11-09 ("at least cavalry speed": 5 m/s run speed)
FOURTH.FAST_ENEMY_NEAR_M = 40  -- user setting 2026-11-09: closeness to one of our units, edge to edge
                               -- (a user-set test value, not an ability range: the cast bound stays 70%)
FOURTH.eg_class = nil

"""

LOGIC = """-- true when the enemy fits the current entry's target class (nil class = any enemy)
function FOURTH.eg_class_ok(enemy)
	local cls = FOURTH.eg_class
	if cls == nil then return true end
	local t = FOURTH.type_plain(enemy)
	if cls == "commander" then
		if t ~= nil then return FOURTH.commander_keys[t] == true end
		local ok, c = pcall(function() return enemy:unit_class() end)
		return ok and c == "com"
	end
	if t == nil then return false end
	if cls == "large" then return FOURTH.class_keys.large[t] == true end
	if cls == "large_single" then
		return FOURTH.class_keys.large[t] == true and FOURTH.class_keys.single[t] == true
	end
	return false
end

-- gap, speed when the enemy is MOVING with a run speed of FAST_ENEMY_MPS or
-- more and one of our units (the caster counting) is within FAST_ENEMY_NEAR_M
-- of it (edge to edge, the closest of ours); nil otherwise. Every read
-- fails closed.
function FOURTH.fast_enemy_near(enemy, caster)
	local ok_mv, mv = pcall(function() return enemy:is_moving() end)
	if not (ok_mv and mv == true) then return nil end
	local ok_sp, sp = pcall(function() return enemy:fast_speed() end)
	if not (ok_sp and type(sp) == "number" and sp >= FOURTH.FAST_ENEMY_MPS) then return nil end
	local best = nil
	local function try(u)
		if u == nil then return end
		local ok_m, men = pcall(function() return u:number_of_men_alive() end)
		if not (ok_m and type(men) == "number" and men > 0) then return end
		local ok_g, g = pcall(function() return u:unit_distance(enemy) end)
		if ok_g and type(g) == "number" and g >= 0 and (best == nil or g < best) then best = g end
	end
	try(caster)
	if tracked_units ~= nil then
		for i = 1, #tracked_units do
			try(tracked_units[i] and tracked_units[i].unit)
		end
	end
	if best ~= nil and best <= FOURTH.FAST_ENEMY_NEAR_M then return best, sp end
	return nil
end

"""

EVAL_LIVE = """-- the user's fast-enemy trigger: the qualifying enemy closest to our units wins
function FOURTH.evaluate_enemy_fast_near_ally(unit, routing)
	FOURTH.eg_mode = "fast"
	if routing then return nil end
	local marker = FOURTH.eg_marker or "fast_enemy"
	local ok_coll, coll = pcall(function() return bm:get_scriptunits_for_main_enemy_army_to_local_player() end)
	if not ok_coll or coll == nil then return nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil end
	local best, best_near, best_sp = nil, nil, nil
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		local enemy = nil
		if ok_su and su ~= nil then pcall(function() enemy = su.unit end) end
		if enemy ~= nil then
			local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
			local valid = FOURTH.eg_enemy_valid(enemy)
			if ok_alive and type(alive) == "number" and alive > 0 and (valid == nil or valid == true)
				and FOURTH.eg_class_ok(enemy) and FOURTH.eg_enemy_within_bound(unit, enemy) then
				local near, sp = FOURTH.fast_enemy_near(enemy, unit)
				if near ~= nil and (best_near == nil or near < best_near) then
					best, best_near, best_sp = enemy, near, sp
				end
			end
		end
	end
	if best == nil then return nil end
	local etype = "enemy"
	pcall(function() etype = tostring(best:type()) end)
	local gap = FOURTH.eg_enemy_gap(unit, best)
	FOURTH.eg_enemy = best
	FOURTH.eg_arm = "fast"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = best
	return string.format("fast enemy near our units (targeting %s, run speed %.1f m/s >= %d, %.1fm from our closest unit <= %dm, distance %sm bound %sm)",
		etype, best_sp, FOURTH.FAST_ENEMY_MPS, best_near, FOURTH.FAST_ENEMY_NEAR_M,
		(gap ~= nil) and string.format("%.1f", gap) or "?", tostring(FOURTH.eg_range_m))
end

"""

EVAL_ANN = """-- the user's fast-enemy trigger: the qualifying enemy closest to our units wins
function FOURTH.evaluate_enemy_fast_near_ally(unit, routing)
	FOURTH.eg_mode = "fast"
	if routing then return false end
	local ok_coll, coll = pcall(function() return bm:get_scriptunits_for_main_enemy_army_to_local_player() end)
	if not ok_coll or coll == nil then return false end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return false end
	local best, best_near = nil, nil
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		local enemy = nil
		if ok_su and su ~= nil then pcall(function() enemy = su.unit end) end
		if enemy ~= nil then
			local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
			local valid = FOURTH.eg_enemy_valid(enemy)
			if ok_alive and type(alive) == "number" and alive > 0 and (valid == nil or valid == true)
				and FOURTH.eg_class_ok(enemy) and FOURTH.eg_enemy_within_bound(unit, enemy) then
				local near = FOURTH.fast_enemy_near(enemy, unit)
				if near ~= nil and (best_near == nil or near < best_near) then
					best, best_near = enemy, near
				end
			end
		end
	end
	if best == nil then return false end
	FOURTH.eg_enemy = best
	FOURTH.eg_arm = "fast"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = best
	return true
end

"""

PICK_OLD = ("\t\t\t\t\t\t\t\tand (valid == nil or valid == true)\n"
            "\t\t\t\t\t\t\t\tand FOURTH.eg_enemy_within_bound(unit, enemy) then\n")
PICK_NEW = ("\t\t\t\t\t\t\t\tand (valid == nil or valid == true)\n"
            "\t\t\t\t\t\t\t\tand FOURTH.eg_class_ok(enemy)\n"
            "\t\t\t\t\t\t\t\tand FOURTH.eg_enemy_within_bound(unit, enemy) then\n")
MODE_OLD = ('\t\telseif eg_mode_now == "melee" then\n'
            '\t\t\tcond_now = still_melee\n'
            '\t\tend\n')
MODE_NEW = ('\t\telseif eg_mode_now == "melee" then\n'
            '\t\t\tcond_now = still_melee\n'
            '\t\telseif eg_mode_now == "fast" then\n'
            '\t\t\t-- ROUND 135: still moving fast and close to one of our units\n'
            '\t\t\tcond_now = (FOURTH.fast_enemy_near(enemy, unit) ~= nil)\n'
            '\t\tend\n')
SKIP_OLD = "\t\tif not alive_now or not cond_now or cmdr_now or not inf_now or not in_bound_now then\n"
SKIP_NEW = ("\t\t-- ROUND 135: the entry's target class (Lord/Hero, large) is re-checked too\n"
            "\t\tif not alive_now or not cond_now or cmdr_now or not inf_now or not in_bound_now\n"
            "\t\t\tor not FOURTH.eg_class_ok(enemy) then\n")
POLL_OLD = "\t\t\t\t\tFOURTH.eg_range_m = ability.range_m\n"
POLL_NEW = ("\t\t\t\t\tFOURTH.eg_range_m = ability.range_m\n"
            "\t\t\t\t\t-- ROUND 135: the entry's enemy target class (nil = any enemy)\n"
            "\t\t\t\t\tFOURTH.eg_class = ability.target_class\n")
MAP_OLD = "\tmelee_or_under_fire = FOURTH.evaluate_melee_or_under_fire,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 135\n\tenemy_fast_near_ally = FOURTH.evaluate_enemy_fast_near_ally,\n"
TIP_OLD = ('\tmelee_or_under_fire = "When armed, fires when this unit (or, for an aura, a friendly unit near it) '
           'is in melee or under missile fire",\n')
TIP_NEW = TIP_OLD + '\tenemy_fast_near_ally = "When armed, fires on a fast enemy unit moving close to your units",\n'
ANCHOR = "FOURTH.evaluators = {\n"

large, single = G.derive()
SETS = G.lua_block(large, single) + "\n"

for path, ev in ((SRC, EVAL_LIVE), (ANN, EVAL_ANN)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "enemy_fast_near_ally" not in s and "FOURTH.class_keys.large" not in s
    s = apply_roster(s)
    s = sub(s, PICK_OLD, PICK_NEW)
    s = sub(s, MODE_OLD, MODE_NEW)
    s = sub(s, SKIP_OLD, SKIP_NEW)
    s = sub(s, POLL_OLD, POLL_NEW)
    s = sub(s, MAP_OLD, MAP_NEW)
    s = sub(s, TIP_OLD, TIP_NEW)
    s = sub(s, ANCHOR, HDR + SETS + LOGIC + ev + ANCHOR)
    assert "string.find" not in s.split("ROUND 135 - AUDIT BATCH 4")[1].split("FOURTH.evaluators = {")[0]
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "enemy_melee", s.count('trigger = "enemy_melee"'), "fast", s.count('trigger = "enemy_fast_near_ally"'),
          "engaged_or_shot", s.count('trigger = "enemy_engaged_or_shot"'), "target_class", s.count("\t\ttarget_class = "))
print("large", len(large), "single", len(single))
