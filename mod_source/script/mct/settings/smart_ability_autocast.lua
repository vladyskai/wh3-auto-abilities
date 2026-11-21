-- ============================================================================
-- Smart Ability Autocast: the OPTIONAL MCT page (round 194, user 2026-11-21: "Do it the MCT route. MCT should not be
-- a requirement for the mod to work, only needed for this button").
-- Only the Mod Configuration Tool loads files from script/mct/settings/, so without MCT this file never runs and the
-- mod works as before. With MCT it adds one control that forgets the M/A choices the mod remembers between battles:
-- it empties the battle script's file, smart_ability_autocast_settings.txt, next to the game. In battle it also tells
-- the running battle script (smart_ability_autocast_reset_remembered) so the next click does not write them back.
-- The control is MCT's button type when this MCT version has it (add_new_action), else a checkbox: tick it and close
-- the MCT panel. Everything is guarded: an error here never reaches MCT or the game.
-- ROUND 195 (user 2026-11-21, screenshot): no tooltip (MCT pins its "?" marker to the bottom-left of the label, so a
-- wrapped label ran into it), a short one-line label under a named section (not "Default Category"), and feedback:
-- after a reset the button reads "Done" and greys out and the label reads "Forgotten" until the panel is reopened.
-- ============================================================================
if type(get_mct) ~= "function" then return end

pcall(function()
	local mct = get_mct()
	if mct == nil then return end
	local FILE = "smart_ability_autocast_settings.txt"
	local function reset()
		local ok, fh = pcall(io.open, FILE, "w")
		if ok and fh ~= nil then pcall(function() fh:close() end) end
		if type(smart_ability_autocast_reset_remembered) == "function" then pcall(smart_ability_autocast_reset_remembered) end
	end
	local mod = mct:register_mod("smart_ability_autocast")
	mod:set_title("Smart Ability Autocast")
	mod:set_description("Your units cast their own abilities. The mod remembers your M and A choices for each unit type"
		.. " between battles. Reset forgets them all: every ability goes back to its default M or A in your next battle.")
	if type(mod.add_new_section) == "function" then mod:add_new_section("remembered", "Remembered M/A choices") end
	if type(mod.add_new_action) == "function" then
		local opt = nil
		local function pressed()
			reset()
			-- the feedback: the button reads Done and greys out, the label reads Forgotten (until the panel reopens)
			if opt == nil or type(opt.get_uic_with_key) ~= "function" then return end
			local btn = opt:get_uic_with_key("option")
			if btn then
				btn:SetState("inactive")
				local txt = find_uicomponent(btn, "button_txt")
				if txt then txt:SetStateText("Done") end
			end
			local label = opt:get_uic_with_key("text")
			if label then label:SetStateText("Forgotten") end
		end
		opt = mod:add_new_action("reset_remembered", "All unit types", pressed)
		if type(opt.set_button_text) == "function" then opt:set_button_text("Reset") end
	else
		local opt = mod:add_new_option("reset_remembered", "checkbox")
		opt:set_default_value(false)
		if type(opt.set_is_global) == "function" then opt:set_is_global(true) end
		opt:set_text("Reset all")   -- one line: MCT pins its option icons below the label
		core:add_listener("smart_ability_autocast_reset", "MctOptionSettingFinalized",
			function(context)
				return context:mod():get_key() == "smart_ability_autocast"
					and context:option():get_key() == "reset_remembered" and context:setting() == true
			end,
			function(context)
				reset()
				pcall(function() context:option():set_finalized_setting(false) end)
			end,
			true)
	end
end)
