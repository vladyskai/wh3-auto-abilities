	-- WILL OF THE VERMINKING RANGE RE-CHECK (this round): the same safety
	-- pattern as Glorious Death - re-read the chosen ally's gap immediately
	-- before the cast; skip when it has drifted beyond the conservative
	-- trigger range.
	if FOURTH.vm_ally ~= nil and not FOURTH.vm_ally_in_range(unit, FOURTH.vm_ally) then
		FOURTH.vm_ally = nil
		return "held"
	end

