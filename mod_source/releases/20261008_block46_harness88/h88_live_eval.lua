
-- ============================================================================
-- BLOCK 4/5/6 - THE TWO NEW-TRIGGER EVALUATORS (this round). Each carries its
-- OWN distinct reason text so the field log tells them apart.
-- THE LOCAL CEILING: their per-unit state (vm_ally, plus the named trigger-
-- range constant below) rides the FOURTH helper bag - the chunk compiles at
-- Lua's 200-local limit, so NO new chunk-level locals are introduced.
-- ============================================================================

-- WILL OF THE VERMINKING'S TRIGGER RANGE (this round) - DELIBERATELY
-- CONSERVATIVE, stored on the FOURTH bag (no new chunk local). The ability's
-- GAME DATA gives a 35 m ally aura (unit_spec_abil.tsv: effect_range =
-- 35.0000, ai_usage = augment_melee); following the FIELD-PROVEN conservative
-- pattern used for Glorious Death (25 m vs its 55 m wiki aura) the trigger
-- radius here is a deliberately conservative 25 m - 10 m INSIDE the 35 m
-- aura. The ally arm fires only while the OWNER is within
-- FOURTH.VERMINKING_RANGE_M of the wavering ally. ONE place to tune.
FOURTH.VERMINKING_RANGE_M = 25

-- WILL OF THE VERMINKING's chosen ally (this round): the CLOSEST in-melee
-- WAVERING ally within FOURTH.VERMINKING_RANGE_M, kept only so the cast can
-- RE-CHECK the gap immediately before firing. Cleared (with cast_target)
-- before every evaluate, so it can never leak into another ability's attempt.
FOURTH.vm_ally = nil

-- the gap in metres from the OWNER to a candidate ally - the SAME
-- battle_unit:unit_distance primitive the charge detector and Glorious Death
-- already use. nil when the read cannot be taken.
function FOURTH.vm_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

-- true when the gap is within the conservative trigger range. An UNREADABLE
-- gap (nil) is treated as IN range (fail-open) - exactly how Glorious Death's
-- gate treats an unknown distance - so a flaky read can never silently
-- disable the ability.
function FOURTH.vm_ally_in_range(unit, ally)
	local gap = FOURTH.vm_ally_gap(unit, ally)
	return (gap == nil) or (gap <= FOURTH.VERMINKING_RANGE_M)
end

-- WILL OF THE VERMINKING: fire when ANY friendly unit OTHER THAN THE CASTER is
-- IN MELEE and WAVERING and within the conservative trigger range of the
-- owner; CAST ON SELF (the effect is an ally aura centred on the caster - the
-- cast target is the OWNER, the DEFAULT target or unit, exactly how every
-- in-melee-self entry casts, so no cast_target write is needed).
-- THE SAME SAFETY PATTERN AS GLORIOUS DEATH: the CLOSEST qualifying ally is
-- chosen, the gap is RE-CHECKED immediately before the cast and the cast is
-- SKIPPED if the ally has drifted out of range. An unreadable morale
-- suppresses (only an EXACT wavering answer counts - fail-closed).
function FOURTH.evaluate_verminking_wavering(unit, routing)
	local reason = nil
	if not routing then
		local self_id = tostring(unit:unique_ui_id())
		local best_ally = nil
		local best_gap = nil
		for i = 1, #tracked_units do
			local other = tracked_units[i] and tracked_units[i].unit
			if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
				if tostring(other:unique_ui_id()) ~= self_id
					and other:is_in_melee() and not unit_is_routing(other)
					and FOURTH.wavering(other) == true then
					local gap = FOURTH.vm_ally_gap(unit, other)
					if (gap == nil) or (gap <= FOURTH.VERMINKING_RANGE_M) then
						if best_ally == nil then
							best_ally, best_gap = other, gap
						elseif gap ~= nil and (best_gap == nil or gap < best_gap) then
							best_ally, best_gap = other, gap
						end
					end
				end
			end
		end
		if best_ally ~= nil then
			if best_gap ~= nil then
				log("  will_of_the_verminking ally: ui " .. tostring(best_ally:unique_ui_id())
					.. " at " .. string.format("%.1f", best_gap) .. "m is the CLOSEST"
					.. " wavering in-melee ally within " .. tostring(FOURTH.VERMINKING_RANGE_M) .. "m")
			end
			FOURTH.vm_ally = best_ally
			reason = "wavering ally in melee (self-cast)"
		end
	end
	return reason
end

-- POTION OF TOUGHNESS: a ONE-TIME activation treated as a HEAL - fire when the
-- OWNER is in melee AND its own health is at or below 75%. Reuses the SAME
-- live health read (HealthPercent via FOURTH.context_value) and the SAME plain
-- hysteresis-free threshold style as Ghoul King of Ushoran; NO second
-- threshold. Repeat attempts are held back by the readiness gate, the engine
-- cooldown and the rejection-informed back-off only.
function FOURTH.evaluate_potion_health(unit, routing)
	local reason = nil
	if unit:is_in_melee() and not routing then
		local hp = FOURTH.context_value(unit, "HealthPercent")
		if type(hp) == "number" and hp <= 75 then
			reason = string.format("in melee, health %d%% (<= 75%%)", math.floor(hp))
		end
	end
	return reason
end
