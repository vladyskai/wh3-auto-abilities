-- ============================================================================
-- ACCUSATION (this round) - the FIRST ENEMY-TARGETED trigger, and the first
-- ability whose cast target is an ENEMY unit.
--   THE RULE: fire when an ENEMY unit in range is in melee OR under missile
--   fire - per poll, for a unit that owns an enemy-targeted key: enumerate the
--   enemy script units; keep those that are valid and alive AND inside the
--   ability's own reach; of those pick one that is IN MELEE or UNDER MISSILE
--   FIRE (prefer in-melee; among equals the closest). If none qualifies, do
--   nothing. The chosen enemy becomes the CAST TARGET - NEVER the owner.
--   THE PROVEN ROUTE (round-4 probe, log-confirmed): the target is re-fetched
--   FRESH from the enemy enumerator on the SAME tick and the caster's
--   controller is re-read fresh (SECTION 6a's FOURTH.eg_fresh_caster_su) - the
--   bench_fresh shape `caster_su.uc:perform_special_ability(key, enemy_su.unit)`
--   that LANDED in the probe. A controller held from an earlier poll no-ops.
--   THE RANGE SOURCE: Accusation's own target_intercept_range (unit_spec_abil
--   .tsv = 75.0000 m), stored as the named FOURTH.ACCUSATION_RANGE_M.
--   THE SAFETY PATTERN: the chosen enemy rides FOURTH.eg_enemy; the condition
--   (alive + still in melee/under fire + still in range) is RE-CHECKED
--   immediately before the cast and the cast is SKIPPED if it lapsed. The HOLD
--   is the existing per-pair guard + cooldown hold.
--   is_under_missile_attack() is not proven on an enemy - an unreadable read is
--   treated as FALSE (fail-safe). Every helper/constant/slot rides the FOURTH
--   bag - NO new chunk-level locals.
-- ============================================================================

-- ACCUSATION'S TRIGGER RANGE - the ability's own target_intercept_range (75 m).
FOURTH.ACCUSATION_RANGE_M = 75

-- the chosen ENEMY unit, its arm and the fresh CASTER script_unit - cleared
-- before every evaluate so no ability can inherit a stale enemy.
FOURTH.eg_enemy = nil
FOURTH.eg_arm = nil
FOURTH.eg_caster_su = nil

-- the gap in metres from the OWNER to a candidate enemy.
function FOURTH.eg_enemy_gap(unit, enemy)
	local ok, gap = pcall(function() return unit:unit_distance(enemy) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

-- true while the enemy is inside the ability's own reach: unit_in_range first,
-- a readable distance next, caster-in-melee last. A wholly unreadable reach is
-- treated as OUT of range (fail-safe).
function FOURTH.eg_enemy_in_range(unit, enemy)
	local okr, inr = pcall(function() return unit:unit_in_range(enemy) end)
	if okr and inr == true then return true end
	if okr and inr == false then return false end
	local gap = FOURTH.eg_enemy_gap(unit, enemy)
	if gap ~= nil then return gap <= FOURTH.ACCUSATION_RANGE_M end
	local okm, m = pcall(function() return unit:is_in_melee() end)
	return (okm and m == true)
end

-- true / false / nil - the enemy's validity (is_valid_target() is the probed
-- read; is_valid() is the documented one). An unreadable validity is nil.
function FOURTH.eg_enemy_valid(enemy)
	local ok, v = pcall(function() return enemy:is_valid_target() end)
	if ok then
		if v == true then return true end
		if v == false then return false end
	end
	local ok2, v2 = pcall(function() return enemy:is_valid() end)
	if ok2 then
		if v2 == true then return true end
		if v2 == false then return false end
	end
	return nil
end

-- true when the enemy is currently TAKING missile fire. An unreadable read is
-- treated as FALSE (fail-safe) - is_under_missile_attack() was never proven on
-- an enemy.
function FOURTH.eg_under_missile_attack(enemy)
	local ok, v = pcall(function() return enemy:is_under_missile_attack() end)
	if ok and v == true then return true end
	return false
end

-- re-fetch the CASTER's script_unit FRESH from the friendly enumerator THIS
-- tick (never a controller held from an earlier poll). nil when not found.
function FOURTH.eg_fresh_caster_su(unit)
	local ok_coll, coll = pcall(function()
		return bm:get_scriptunits_for_local_players_army()
	end)
	if not ok_coll or coll == nil then return nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil end
	local want = nil
	pcall(function() want = tostring(unit:unique_ui_id()) end)
	if want == nil then return nil end
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		if ok_su and su ~= nil then
			local u = nil
			pcall(function() u = su.unit end)
			if u ~= nil then
				local id = nil
				pcall(function() id = u:unique_ui_id() end)
				if id ~= nil and tostring(id) == want then return su end
			end
		end
	end
	return nil
end

-- THE EVALUATOR: fire when an ENEMY unit in range is in melee OR under missile
-- fire; the chosen enemy is the CAST TARGET (never the owner). true = fire.
function FOURTH.evaluate_enemy_engaged_or_shot(unit, routing)
	if not routing then
		local ok_coll, coll = pcall(function()
			return bm:get_scriptunits_for_main_enemy_army_to_local_player()
		end)
		if ok_coll and coll ~= nil then
			local ok_n, n = pcall(function() return coll:count() end)
			if ok_n and type(n) == "number" then
				local best_enemy, best_gap, best_arm = nil, nil, nil
				for i = 1, n do
					local ok_su, su = pcall(function() return coll:item(i) end)
					if ok_su and su ~= nil then
						local enemy = nil
						pcall(function() enemy = su.unit end)
						if enemy ~= nil then
							local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
							local valid = FOURTH.eg_enemy_valid(enemy)
							local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)
							local arm = nil
							if ok_melee and melee == true then
								arm = "melee"
							elseif FOURTH.eg_under_missile_attack(enemy) then
								arm = "missile"
							end
							if arm ~= nil
								and ok_alive and type(alive) == "number" and alive > 0
								and (valid == nil or valid == true)
								and FOURTH.eg_enemy_in_range(unit, enemy) then
								local gap = FOURTH.eg_enemy_gap(unit, enemy)
								if best_enemy == nil
									or (arm == "melee" and best_arm ~= "melee")
									or (arm == best_arm and gap ~= nil and (best_gap == nil or gap < best_gap)) then
									best_enemy, best_gap, best_arm = enemy, gap, arm
								end
							end
						end
					end
				end
				if best_enemy ~= nil then
					FOURTH.eg_enemy = best_enemy
					FOURTH.eg_arm = best_arm
					FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
					FOURTH.cast_target = best_enemy
					return true
				end
			end
		end
	end
	return false
end
