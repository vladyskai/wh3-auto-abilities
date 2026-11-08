
-- ============================================================================
-- BLOCKS 7-9 (this round) - FIVE new trigger types (and the redesigned pair).
-- Every evaluator is a FIELD of the FOURTH helper bag and every new piece of
-- state / constant rides the bag too: the chunk already sits at Lua's 200-local
-- ceiling, so NO new chunk-level locals are introduced. Each LIVE evaluator
-- answers its OWN distinct reason string so the field log tells the triggers
-- apart; the reading copy answers true / false.
-- ============================================================================

-- CHARGE ONLY (Ferocious Battle Howl): fire in the charge window WITHOUT the
-- melee arm - the split second before impact, cast on self. This is the plain
-- charge detector (measure_charge, section 5) with the FIRE_ON_MELEE arm
-- deliberately OMITTED.
function FOURTH.evaluate_charge_only(unit, routing)
	local reason = nil
	local m = measure_charge(unit)
	if FIRE_ON_CHARGE and m.charging and not routing then
		reason = string.format("charging (charge only) (gap=%.1fm dist=%.1fm eta=%.1fs)",
			m.order_gap, m.target_dist, m.ttc)
	end
	return reason
end

-- WAVERING SELF (Ferocious Fury of Ulric / Helm of Yvresse / Vial of Troll
-- Blood): fire while the OWNER itself is wavering (while not routing); cast on
-- self. The morale read is the SAME battle_unit:is_wavering the Stand Your
-- Ground trigger uses (FOURTH.wavering); only an EXACT true answer fires
-- (fail-closed - an unreadable morale never fires a self-only wavering buff).
function FOURTH.evaluate_wavering_self(unit, routing)
	local reason = nil
	if not routing and FOURTH.wavering(unit) == true then
		reason = "wavering (self)"
	end
	return reason
end

-- WAVERING SELF-OR-ALLY (Fury of Ulric / the redesigned Commanding Presence):
-- fire when the OWNER is wavering, OR a friendly in-melee WAVERING ally lies
-- within the conservative trigger range; cast ON SELF (the effect is a
-- self-centred aura). THE TRIGGER RANGE is DELIBERATELY CONSERVATIVE against
-- the game-data 35 m aura (unit_spec_abil.tsv effect_range 35.0000 for both
-- keys). THE SAME SAFETY PATTERN as Glorious Death / Verminking / Metallurgy:
-- the CLOSEST qualifying in-melee wavering ally is chosen, the gap is
-- RE-CHECKED immediately before the cast and the cast is SKIPPED on drift. The
-- self-wavering arm leaves FOURTH.ws_ally nil - never gated.
FOURTH.WAVERING_RANGE_M = 25

-- the chosen ally (this round): cleared with cast_target before every evaluate.
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
	local reason = nil
	if not routing then
		if FOURTH.wavering(unit) == true then
			reason = "wavering (self-or-ally)"
		else
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
				if best_gap ~= nil then
					log("  wavering_self_or_ally ally: ui " .. tostring(best_ally:unique_ui_id())
						.. " at " .. string.format("%.1f", best_gap) .. "m is the CLOSEST"
						.. " in-melee wavering ally within " .. tostring(FOURTH.WAVERING_RANGE_M) .. "m")
				end
				FOURTH.ws_ally = best_ally
				reason = "wavering in-melee ally (self-cast, self-or-ally)"
			end
		end
	end
	return reason
end

-- CHARGE OR WAVERING (Bangers & Smash): fire in the charge window OR while
-- wavering (while not routing); cast on self. The charge arm is the plain charge
-- detector (no melee arm); the wavering arm is FOURTH.wavering. The arms cannot
-- co-fire - the charge arm is tested first and wins.
function FOURTH.evaluate_charge_or_wavering(unit, routing)
	local reason = nil
	if not routing then
		local m = measure_charge(unit)
		if FIRE_ON_CHARGE and m.charging then
			reason = string.format("charging (charge or wavering) (gap=%.1fm dist=%.1fm eta=%.1fs)",
				m.order_gap, m.target_dist, m.ttc)
		elseif FOURTH.wavering(unit) == true then
			reason = "wavering (charge or wavering)"
		end
	end
	return reason
end

-- WAVERING ALLY IN RANGE ("Stay Here, I'll Get Help!"): fire when a friendly
-- WAVERING ally lies within the conservative trigger range; cast ON SELF. The
-- owner need NOT be wavering and the ally need NOT be in melee - this is the
-- Verminking evaluator shape with the ALLY-MELEE requirement REMOVED (the
-- tracker note records the difference). Same safety pattern: closest in-range
-- wavering ally, gap RE-CHECKED immediately before the cast, cast SKIPPED on
-- drift.
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
	local reason = nil
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
			if best_gap ~= nil then
				log("  wavering_ally_range ally: ui " .. tostring(best_ally:unique_ui_id())
					.. " at " .. string.format("%.1f", best_gap) .. "m is the CLOSEST"
					.. " wavering ally within " .. tostring(FOURTH.WAVERING_RANGE_M) .. "m")
			end
			FOURTH.wa_ally = best_ally
			reason = "wavering ally in range (self-cast)"
		end
	end
	return reason
end
