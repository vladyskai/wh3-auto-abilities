
	-- WAVERING SELF-OR-ALLY RANGE RE-CHECK (blocks 7-9): re-read the chosen
	-- ally's gap immediately before the cast; skip when it has drifted beyond
	-- the conservative trigger range.
	if FOURTH.ws_ally ~= nil and not FOURTH.ws_ally_in_range(unit, FOURTH.ws_ally) then
		FOURTH.ws_ally = nil
		return "held"
	end

	-- WAVERING ALLY IN RANGE RE-CHECK (blocks 7-9): the same pattern for the
	-- Verminking-shape wavering-ally trigger.
	if FOURTH.wa_ally ~= nil and not FOURTH.wa_ally_in_range(unit, FOURTH.wa_ally) then
		FOURTH.wa_ally = nil
		return "held"
	end
