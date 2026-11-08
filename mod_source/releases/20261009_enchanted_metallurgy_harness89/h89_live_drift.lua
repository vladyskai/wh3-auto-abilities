
	-- ENCHANTED METALLURGY RANGE RE-CHECK (this round): the same safety pattern
	-- as Glorious Death / Will of the Verminking. The ALLY arm chose the CLOSEST
	-- in-range in-melee ally at evaluate time and left it in FOURTH.mtl_ally;
	-- RE-READ the gap NOW, immediately before the cast. If the ally has drifted
	-- out of range the cast is wasted, so SKIP it rather than spend it. The
	-- owner-in-melee self arm leaves FOURTH.mtl_ally nil - never gated.
	if FOURTH.mtl_ally ~= nil and not FOURTH.mtl_ally_in_range(unit, FOURTH.mtl_ally) then
		log("  enchanted_metallurgy SKIPPED: the chosen in-melee ally drifted out of range"
			.. " before the cast (the aura would not cover it) - cast not spent")
		FOURTH.mtl_ally = nil
		if RELEASE_CONTROL_AFTER and took_control then
			local ok_release, err_release = pcall(function() uc:release_control() end)
			log("  release_control         : ok=" .. tostring(ok_release)
				.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
		end
		return "held"
	end
