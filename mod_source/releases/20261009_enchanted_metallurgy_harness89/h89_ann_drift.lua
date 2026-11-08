
	-- ENCHANTED METALLURGY RANGE RE-CHECK (this round): the same safety pattern
	-- as Glorious Death / Will of the Verminking - re-read the chosen ally's gap
	-- immediately before the cast; skip when it has drifted beyond the
	-- conservative trigger range.
	if FOURTH.mtl_ally ~= nil and not FOURTH.mtl_ally_in_range(unit, FOURTH.mtl_ally) then
		FOURTH.mtl_ally = nil
		return "held"
	end
