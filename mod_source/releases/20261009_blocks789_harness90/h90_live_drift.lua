
	-- WAVERING SELF-OR-ALLY RANGE RE-CHECK (blocks 7-9): the same safety pattern
	-- as Glorious Death / Verminking / Metallurgy. The ALLY arm chose the
	-- CLOSEST in-range in-melee wavering ally and left it in FOURTH.ws_ally;
	-- RE-READ the gap NOW, immediately before the cast. If the ally has drifted
	-- out of range the cast is wasted, so SKIP it rather than spend it. The
	-- self-wavering arm leaves FOURTH.ws_ally nil - never gated.
	if FOURTH.ws_ally ~= nil and not FOURTH.ws_ally_in_range(unit, FOURTH.ws_ally) then
		log("  wavering_self_or_ally SKIPPED: the chosen wavering ally drifted out of range"
			.. " before the cast (the aura would not cover it) - cast not spent")
		FOURTH.ws_ally = nil
		if RELEASE_CONTROL_AFTER and took_control then
			local ok_release, err_release = pcall(function() uc:release_control() end)
			log("  release_control         : ok=" .. tostring(ok_release)
				.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
		end
		return "held"
	end

	-- WAVERING ALLY IN RANGE RE-CHECK (blocks 7-9): the same safety pattern.
	-- The ally arm chose the CLOSEST in-range wavering ally and left it in
	-- FOURTH.wa_ally; RE-READ the gap NOW, immediately before the cast. If the
	-- ally has drifted out of range, SKIP rather than waste the cast.
	if FOURTH.wa_ally ~= nil and not FOURTH.wa_ally_in_range(unit, FOURTH.wa_ally) then
		log("  wavering_ally_range SKIPPED: the chosen wavering ally drifted out of range"
			.. " before the cast (the aura would not cover it) - cast not spent")
		FOURTH.wa_ally = nil
		if RELEASE_CONTROL_AFTER and took_control then
			local ok_release, err_release = pcall(function() uc:release_control() end)
			log("  release_control         : ok=" .. tostring(ok_release)
				.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
		end
		return "held"
	end
