
-- ============================================================================
-- ENCHANTED METALLURGY (this round) - ONE new trigger for the whole family.
-- The user's new trigger: "when self or ally in range is in melee; when ally
-- in range is shooting". The MELEE half ships; the SHOOTING half COULD NOT be
-- built, and NO proxy is used. THE API RESEARCH: battle_unit.lua (the game
-- dump) has NO per-unit "is firing / is shooting" read - is_under_missile_
-- attack is the unit RECEIVING fire (wrong direction), current_target /
-- ammo_left / missile_range prove nothing about firing NOW, and the engine's
-- flags.tsv vocabulary (is_missile_unit, is_under_missile_fire, ...) is a
-- DATA-TABLE construct, not a Lua read. No proven predicate -> no shooting arm.
-- THE LOCAL CEILING: the per-unit state (mtl_ally) and the named range
-- constant ride the FOURTH helper bag - NO new chunk-level locals.
-- ============================================================================

-- ENCHANTED METALLURGY'S TRIGGER RANGE (this round) - DELIBERATELY
-- CONSERVATIVE, stored on the FOURTH bag (no new chunk local). The ability's
-- GAME DATA gives a 35 m ally aura (unit_spec_abil.tsv: effect_range =
-- 35.0000 for all four keys, ai_usage = augment_melee); following the
-- FIELD-PROVEN conservative pattern used for Glorious Death and Will of the
-- Verminking (25 m against a larger aura) the trigger radius here is a
-- deliberately conservative 25 m - 10 m INSIDE the 35 m aura. ONE place to tune.
FOURTH.METALLURGY_RANGE_M = 25

-- ENCHANTED METALLURGY's chosen ally (this round): the CLOSEST in-melee ally
-- within FOURTH.METALLURGY_RANGE_M, kept only so the cast can RE-CHECK the
-- gap immediately before firing. Cleared (with cast_target) before every
-- evaluate, so it can never leak into another ability's attempt.
FOURTH.mtl_ally = nil

-- the gap in metres from the OWNER to a candidate ally - the SAME
-- battle_unit:unit_distance primitive the charge detector, Glorious Death and
-- Will of the Verminking already use. nil when the read cannot be taken.
function FOURTH.mtl_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

-- true when the gap is within the conservative trigger range. An UNREADABLE
-- gap (nil) is treated as IN range (fail-open) - exactly how the Glorious
-- Death / Verminking gate treats an unknown distance - so a flaky read can
-- never silently disable the ability.
function FOURTH.mtl_ally_in_range(unit, ally)
	local gap = FOURTH.mtl_ally_gap(unit, ally)
	return (gap == nil) or (gap <= FOURTH.METALLURGY_RANGE_M)
end

-- ENCHANTED METALLURGY: fire when the OWNER ITSELF is in melee, OR any
-- friendly unit OTHER THAN THE CASTER is in melee within the conservative
-- trigger range of the owner; CAST ON SELF (the cast target is the OWNER, the
-- DEFAULT target or unit, so no cast_target write is needed). THE SAME SAFETY
-- PATTERN AS GLORIOUS DEATH / VERMINKING: for the ALLY arm the CLOSEST
-- qualifying in-melee ally is chosen, the gap is RE-CHECKED immediately before
-- the cast and the cast is SKIPPED on drift. The owner-in-melee self arm
-- leaves FOURTH.mtl_ally nil - never gated.
function FOURTH.evaluate_metallurgy_melee(unit, routing)
	if not routing then
		if unit:is_in_melee() then
			return true
		end
		local self_id = tostring(unit:unique_ui_id())
		local best_ally = nil
		local best_gap = nil
		for i = 1, #tracked_units do
			local other = tracked_units[i] and tracked_units[i].unit
			if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
				if tostring(other:unique_ui_id()) ~= self_id
					and other:is_in_melee() and not unit_is_routing(other) then
					local gap = FOURTH.mtl_ally_gap(unit, other)
					if (gap == nil) or (gap <= FOURTH.METALLURGY_RANGE_M) then
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
			FOURTH.mtl_ally = best_ally
			return true
		end
	end
	return false
end
