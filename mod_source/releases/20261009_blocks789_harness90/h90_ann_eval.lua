
-- ============================================================================
-- BLOCKS 7-9 (this round) - FIVE new trigger types (and the redesigned pair).
-- Every evaluator is a field of the FOURTH helper bag and every new piece of
-- state / constant rides the bag too (NO new chunk-level locals - the chunk is
-- at Lua's 200-local ceiling). The reading copy answers true / false.
-- ============================================================================

-- CHARGE ONLY (Ferocious Battle Howl): the charge window WITHOUT the melee arm.
function FOURTH.evaluate_charge_only(unit, routing)
	local m = measure_charge(unit)
	if FIRE_ON_CHARGE and m.charging and not routing then
		return true
	end
	return false
end

-- WAVERING SELF (Ferocious Fury of Ulric / Helm of Yvresse / Vial of Troll
-- Blood): the OWNER itself is wavering (while not routing); only an EXACT true
-- morale answer fires (fail-closed).
function FOURTH.evaluate_wavering_self(unit, routing)
	if not routing and FOURTH.wavering(unit) == true then
		return true
	end
	return false
end

-- WAVERING SELF-OR-ALLY (Fury of Ulric / redesigned Commanding Presence): the
-- OWNER is wavering, OR a friendly in-melee wavering ally is within the
-- conservative trigger range; cast on self. THE TRIGGER RANGE is DELIBERATELY
-- CONSERVATIVE against the game-data 35 m aura (unit_spec_abil.tsv effect_range
-- 35.0000). Same safety pattern as Glorious Death / Verminking / Metallurgy:
-- closest ally, pre-cast gap re-check, skip on drift.
FOURTH.WAVERING_RANGE_M = 25

FOURTH.ws_ally = nil

function FOURTH.ws_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

function FOURTH.ws_ally_in_range(unit, ally)
	local gap = FOURTH.ws_ally_gap(unit, ally)
	return (gap == nil) or (gap <= FOURTH.WAVERING_RANGE_M)
end

function FOURTH.evaluate_wavering_self_or_ally(unit, routing)
	if not routing then
		if FOURTH.wavering(unit) == true then
			return true
		end
		local self_id = tostring(unit:unique_ui_id())
		local best_ally = nil
		local best_gap = nil
		for i = 1, #tracked_units do
			local other = tracked_units[i] and tracked_units[i].unit
			if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
				if tostring(other:unique_ui_id()) ~= self_id
					and other:is_in_melee() and not unit_is_routing(other)
					and FOURTH.wavering(other) == true then
					local gap = FOURTH.ws_ally_gap(unit, other)
					if (gap == nil) or (gap <= FOURTH.WAVERING_RANGE_M) then
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
			FOURTH.ws_ally = best_ally
			return true
		end
	end
	return false
end

-- CHARGE OR WAVERING (Bangers & Smash): the charge window OR wavering.
function FOURTH.evaluate_charge_or_wavering(unit, routing)
	if not routing then
		local m = measure_charge(unit)
		if FIRE_ON_CHARGE and m.charging then
			return true
		end
		if FOURTH.wavering(unit) == true then
			return true
		end
	end
	return false
end

-- WAVERING ALLY IN RANGE ("Stay Here, I'll Get Help!"): a friendly WAVERING
-- ally within the conservative range; cast on self. The owner need not be
-- wavering and the ally need not be in melee - the Verminking shape with the
-- ally-melee requirement removed (see the tracker note). Same safety pattern.
FOURTH.wa_ally = nil

function FOURTH.wa_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

function FOURTH.wa_ally_in_range(unit, ally)
	local gap = FOURTH.wa_ally_gap(unit, ally)
	return (gap == nil) or (gap <= FOURTH.WAVERING_RANGE_M)
end

function FOURTH.evaluate_wavering_ally_range(unit, routing)
	if not routing then
		local self_id = tostring(unit:unique_ui_id())
		local best_ally = nil
		local best_gap = nil
		for i = 1, #tracked_units do
			local other = tracked_units[i] and tracked_units[i].unit
			if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
				if tostring(other:unique_ui_id()) ~= self_id
					and not unit_is_routing(other)
					and FOURTH.wavering(other) == true then
					local gap = FOURTH.wa_ally_gap(unit, other)
					if (gap == nil) or (gap <= FOURTH.WAVERING_RANGE_M) then
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
			FOURTH.wa_ally = best_ally
			return true
		end
	end
	return false
end
