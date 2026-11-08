	-- WILL OF THE VERMINKING RANGE RE-CHECK (this round): the same safety
	-- pattern as Glorious Death. The ally arm chose the CLOSEST in-range
	-- wavering in-melee ally at evaluate time and left it in FOURTH.vm_ally;
	-- RE-READ the gap NOW, immediately before the cast. If the ally has drifted
	-- out of range the cast is wasted, so SKIP it rather than spend it.
	if FOURTH.vm_ally ~= nil and not FOURTH.vm_ally_in_range(unit, FOURTH.vm_ally) then
		log("  will_of_the_verminking SKIPPED: the chosen wavering ally drifted out of range"
			.. " before the cast (the aura would not cover it) - cast not spent")
		FOURTH.vm_ally = nil
		if RELEASE_CONTROL_AFTER and took_control then
			local ok_release, err_release = pcall(function() uc:release_control() end)
			log("  release_control         : ok=" .. tostring(ok_release)
				.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
		end
		return "held"
	end

