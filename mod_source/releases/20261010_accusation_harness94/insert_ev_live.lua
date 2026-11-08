-- ============================================================================
-- ACCUSATION (this round) - the FIRST ENEMY-TARGETED trigger, and the first
-- ability whose cast target is an ENEMY unit.
--   THE USER'S RULE (verbatim): "implement accusation automatic activation when
--   enemy unit in range is in melee or being shot at."
--   THE TRIGGER (per poll, for a unit that owns an enemy-targeted key):
--   enumerate the enemy script units; keep those that are (a) valid and alive
--   and (b) inside the ability's own reach; of those pick one that is IN MELEE
--   or UNDER MISSILE FIRE (prefer in-melee; among equals the closest). If none
--   qualifies, do nothing. The chosen enemy becomes the CAST TARGET - NEVER
--   the owner.
--   THE PROVEN ROUTE (round-4 probe, log-confirmed): the target is re-fetched
--   FRESH from the enemy enumerator on the SAME tick and the caster's
--   controller is re-read fresh (FOURTH.eg_fresh_caster_su) - the bench_fresh
--   shape `caster_su.uc:perform_special_ability(key, enemy_su.unit)`, which
--   LANDED in the probe (target effect count 0->1, `CMD event=SpecialAbility`,
--   RESULT route=bench_fresh landed=yes). A controller handle held from an
--   earlier poll silently no-ops (accepted=true, nothing applies).
--   THE RANGE SOURCE: Accusation's own target_intercept_range in
--   unit_spec_abil.tsv = 75.0000 m - the exact reach the round-4 probe named
--   and used. The enemy is offered only while unit:unit_in_range(enemy) is
--   true, else while unit:unit_distance(enemy) <= FOURTH.ACCUSATION_RANGE_M,
--   else while the caster itself is in melee. CONSERVATIVE: the value is a
--   named constant - ONE place to tune.
--   THE SAFETY PATTERN: the chosen enemy rides FOURTH.eg_enemy; the condition
--   (alive + still in melee/under fire + still in range) is RE-CHECKED
--   immediately before the cast and the cast is SKIPPED if it lapsed. The HOLD
--   is the existing per-pair guard + cooldown hold - it never fires every tick.
--   FIELD READS (round 4, proven live on enemies): type(), number_of_men_alive(),
--   is_in_melee(), is_valid_target(). is_under_missile_attack() is NOT proven
--   on an enemy - an unreadable read is treated as FALSE (fail-safe), logged
--   once for the whole battle.
--   THE LOCAL CEILING: every helper, constant and slot rides the FOURTH bag -
--   NO new chunk-level locals.
-- ============================================================================

-- ACCUSATION'S TRIGGER RANGE - the ability's own target_intercept_range (75 m),
-- the reach the round-4 probe named. DELIBERATELY a named constant.
FOURTH.ACCUSATION_RANGE_M = 75

-- the chosen ENEMY unit (re-fetched fresh each tick), its arm ("melee" /
-- "missile") and the fresh CASTER script_unit - all cleared before every
-- evaluate so no ability can inherit a stale enemy.
FOURTH.eg_enemy = nil
FOURTH.eg_arm = nil
FOURTH.eg_caster_su = nil

-- one-time notice for an unreadable is_under_missile_attack.
FOURTH.eg_unreadable_logged = false

-- the gap in metres from the OWNER to a candidate enemy - the SAME
-- battle_unit:unit_distance primitive the charge detector and every ally
-- trigger already use. nil when the read cannot be taken.
function FOURTH.eg_enemy_gap(unit, enemy)
	local ok, gap = pcall(function() return unit:unit_distance(enemy) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

-- true while the enemy is inside the ability's own reach. unit_in_range is the
-- engine's reach read (the probe logged in_range=yes(unit_in_range)); a
-- readable distance is the fallback; caster-in-melee is the last resort. A
-- wholly unreadable reach is treated as OUT of range (fail-safe: never offer an
-- enemy the ability may not cover).
function FOURTH.eg_enemy_in_range(unit, enemy)
	local okr, inr = pcall(function() return unit:unit_in_range(enemy) end)
	if okr and inr == true then return true end
	if okr and inr == false then return false end
	local gap = FOURTH.eg_enemy_gap(unit, enemy)
	if gap ~= nil then return gap <= FOURTH.ACCUSATION_RANGE_M end
	local okm, m = pcall(function() return unit:is_in_melee() end)
	return (okm and m == true)
end

-- true / false / nil - the enemy's validity. is_valid_target() is the read the
-- round-4 probe took; is_valid() is the documented name. A raising read on both
-- answers nil (the caller fail-opens: an unreadable validity never blocks).
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

-- true when the enemy is currently TAKING missile fire. battle_unit:
-- is_under_missile_attack() exists but was NEVER probed on an enemy, so an
-- unreadable read is treated as FALSE (fail-safe) and a raising read writes ONE
-- loud line for the whole battle (never a per-tick stream).
function FOURTH.eg_under_missile_attack(enemy)
	local ok, v = pcall(function() return enemy:is_under_missile_attack() end)
	if ok and v == true then return true end
	if not ok and not FOURTH.eg_unreadable_logged then
		FOURTH.eg_unreadable_logged = true
		log("accusation: enemy is_under_missile_attack read UNAVAILABLE (raised) - treated as FALSE (fail-safe). One-time notice.")
	end
	return false
end

-- re-fetch the CASTER's script_unit FRESH from the friendly enumerator THIS
-- tick (never a controller held from an earlier poll - the round-4 lesson).
-- nil when the army or the matching unit cannot be found.
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
-- fire. The chosen enemy rides FOURTH.cast_target (the CAST TARGET) and
-- FOURTH.eg_enemy (the pre-cast re-check slot) - the owner is NEVER the target.
-- Returns the ATTEMPT reason string, or nil when nothing qualifies.
function FOURTH.evaluate_enemy_engaged_or_shot(unit, routing)
	local reason = nil
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
					local etype = "enemy"
					pcall(function() etype = tostring(best_enemy:type()) end)
					log("  accusation target: '" .. etype .. "' is the chosen enemy (" .. tostring(best_arm)
						.. ") within " .. tostring(FOURTH.ACCUSATION_RANGE_M) .. "m")
					FOURTH.eg_enemy = best_enemy
					FOURTH.eg_arm = best_arm
					FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
					FOURTH.cast_target = best_enemy
					if best_arm == "melee" then
						reason = "enemy in melee (targeting " .. etype .. ")"
					else
						reason = "enemy under missile fire (targeting " .. etype .. ")"
					end
				end
			end
		end
	end
	return reason
end
