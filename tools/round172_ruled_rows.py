#!/usr/bin/env python3
"""Round 172 (harness 171): rows 1, 3 and 5 of docs\\WH3_low_score_review_2026-11-17.md as RULED in the doc
(round 171 built the first proposals instead; the user: "I feel like you ignored the current version").

  Row 1 Horn of the Wild Hunt (army_charge): N of our units charging or in fresh contact, N = ARMY_CHARGE_MIN (3), or
        every living unit of ours when the army has fewer than 3 ("N = 3, or every living unit of ours when the army
        has fewer than 3").
  Row 3 Ursun's Roar, the charge key (aura_charge): at least ONE unit (the caster, or any ally within the 70% aura)
        charging, in fresh contact, or wavering ("Agreed, and include the wavering").
  Row 5 Waaagh!, the wh_main key: NEW army_charge_or_melee: N units charging or in fresh contact, OR N units in melee
        (the +20 melee attack pays in any fight), with the same N.
"""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

OLD_HDR = (
    "--   army_charge (Horn of the Wild Hunt, Waaagh!): ARMY_CHARGE_MIN or more of our units charging or in fresh contact.\n"
    "--   aura_charge (Ursun's Roar, the charge key): the caster charging or in fresh contact, or AURA_CHARGE_ALLIES other\n"
    "--     units within its 70% aura doing so.\n")
NEW_HDR = (
    "--   army_charge (Horn of the Wild Hunt): ARMY_CHARGE_MIN or more of our units charging or in fresh contact; when the\n"
    "--     army has fewer living units than that, every living unit (ROUND 172, the doc's ruling).\n"
    "--   army_charge_or_melee (Waaagh!, the wh_main key; ROUND 172): the same count charging or in fresh contact, OR the\n"
    "--     same count in melee (its +20 melee attack pays in any fight).\n"
    "--   aura_charge (Ursun's Roar, the charge key; ROUND 172): ONE unit, the caster or any unit within its 70% aura,\n"
    "--     charging, in fresh contact or wavering (its leadership +8; user: \"Agreed, and include the wavering\").\n")

OLD_CONST = "FOURTH.ARMY_CHARGE_MIN = 3\nFOURTH.AURA_CHARGE_ALLIES = 2\n"
NEW_CONST = "FOURTH.ARMY_CHARGE_MIN = 3\n"

OLD_EVAL = '''function FOURTH.evaluate_army_charge(unit, routing)
	if routing or tracked_units == nil then return nil end
	local nc, nf = 0, 0
	for i = 1, #tracked_units do
		local u = tracked_units[i] and tracked_units[i].unit
		if u ~= nil and not unit_is_routing(u) then
			local ok_a, men = pcall(function() return u:number_of_men_alive() end)
			if ok_a and type(men) == "number" and men > 0 then
				local w = FOURTH.charge_moment(u)
				if w == "charging" then nc = nc + 1 elseif w ~= nil then nf = nf + 1 end
			end
		end
	end
	if nc + nf >= FOURTH.ARMY_CHARGE_MIN then
		return string.format("army charge: %d unit(s) charging and %d in fresh contact (need %d)", nc, nf,
			FOURTH.ARMY_CHARGE_MIN)
	end
	return nil
end

function FOURTH.evaluate_aura_charge(unit, routing)
	if routing then return nil end
	local own = FOURTH.charge_moment(unit)
	if own ~= nil then return "the caster: " .. own .. " (aura charge)" end
	local reach = FOURTH.ah_range_m
	if reach == nil or tracked_units == nil then return nil end
	local self_id = nil
	pcall(function() self_id = tostring(unit:unique_ui_id()) end)
	local n = 0
	for i = 1, #tracked_units do
		local u = tracked_units[i] and tracked_units[i].unit
		if u ~= nil then
			local ok_id, id = pcall(function() return tostring(u:unique_ui_id()) end)
			if ok_id and id ~= self_id and not unit_is_routing(u) then
				local ok_g, g = pcall(function() return unit:unit_distance(u) end)
				if ok_g and type(g) == "number" and g <= reach and FOURTH.charge_moment(u) ~= nil then n = n + 1 end
			end
		end
	end
	if n >= FOURTH.AURA_CHARGE_ALLIES then
		return string.format("aura charge: %d unit(s) within %sm charging or in fresh contact (need %d)", n,
			tostring(reach), FOURTH.AURA_CHARGE_ALLIES)
	end
	return nil
end
'''

NEW_EVAL = '''-- ROUND 172: count the army once - living units, charging, in fresh contact, in melee (routing units are living but
-- never count as charging or fighting)
function FOURTH.army_moments()
	local c = { living = 0, charging = 0, fresh = 0, melee = 0 }
	if tracked_units == nil then return c end
	for i = 1, #tracked_units do
		local u = tracked_units[i] and tracked_units[i].unit
		if u ~= nil then
			local ok_a, men = pcall(function() return u:number_of_men_alive() end)
			if ok_a and type(men) == "number" and men > 0 then
				c.living = c.living + 1
				if not unit_is_routing(u) then
					local w = FOURTH.charge_moment(u)
					if w == "charging" then c.charging = c.charging + 1 elseif w ~= nil then c.fresh = c.fresh + 1 end
					local ok_m, m = pcall(function() return u:is_in_melee() end)
					if ok_m and m == true then c.melee = c.melee + 1 end
				end
			end
		end
	end
	-- the ruling: N = ARMY_CHARGE_MIN, or every living unit when the army has fewer
	c.need = math.min(FOURTH.ARMY_CHARGE_MIN, c.living)
	return c
end

function FOURTH.evaluate_army_charge(unit, routing)
	if routing or tracked_units == nil then return nil end
	local c = FOURTH.army_moments()
	if c.need >= 1 and c.charging + c.fresh >= c.need then
		return string.format("army charge: %d unit(s) charging and %d in fresh contact (need %d of %d living)",
			c.charging, c.fresh, c.need, c.living)
	end
	return nil
end

-- ROUND 172 (Waaagh!): the army charge, or the same count of our units in melee
function FOURTH.evaluate_army_charge_or_melee(unit, routing)
	if routing or tracked_units == nil then return nil end
	local c = FOURTH.army_moments()
	if c.need < 1 then return nil end
	if c.charging + c.fresh >= c.need then
		return string.format("army charge: %d unit(s) charging and %d in fresh contact (need %d of %d living)",
			c.charging, c.fresh, c.need, c.living)
	end
	if c.melee >= c.need then
		return string.format("army melee: %d unit(s) in melee (need %d of %d living)", c.melee, c.need, c.living)
	end
	return nil
end

-- ROUND 172 (Ursun's Roar): ONE unit - the caster or any unit within the 70% aura - charging, in fresh contact or
-- wavering
function FOURTH.evaluate_aura_charge(unit, routing)
	if routing then return nil end
	local own = FOURTH.charge_moment(unit)
	if own ~= nil then return "the caster: " .. own .. " (aura charge)" end
	if FOURTH.wavering(unit) == true then return "the caster is wavering (aura charge or wavering)" end
	local reach = FOURTH.ah_range_m
	if reach == nil or tracked_units == nil then return nil end
	local self_id = nil
	pcall(function() self_id = tostring(unit:unique_ui_id()) end)
	for i = 1, #tracked_units do
		local u = tracked_units[i] and tracked_units[i].unit
		if u ~= nil then
			local ok_id, id = pcall(function() return tostring(u:unique_ui_id()) end)
			local ok_a, men = pcall(function() return u:number_of_men_alive() end)
			if ok_id and id ~= self_id and ok_a and type(men) == "number" and men > 0 and not unit_is_routing(u) then
				local ok_g, g = pcall(function() return unit:unit_distance(u) end)
				if ok_g and type(g) == "number" and g <= reach then
					local w = FOURTH.charge_moment(u)
					if w ~= nil then
						return string.format("a unit %.1fm away (aura %sm): %s (aura charge)", g, tostring(reach), w)
					end
					if FOURTH.wavering(u) == true then
						return string.format("a unit %.1fm away (aura %sm) is wavering (aura charge or wavering)", g,
							tostring(reach))
					end
				end
			end
		end
	end
	return nil
end
'''

R = [
    (OLD_HDR, NEW_HDR),
    (OLD_CONST, NEW_CONST),
    (OLD_EVAL, NEW_EVAL),
    # the Waaagh! entry moves to its own family
    ('\t-- ROUND 171 (review row 5): the Warboss\'s army-wide Waaagh! (speed, charge, melee attack) gets its own entry\n'
     '\t{ marker = "waaagh_army", name = "Waaagh!", trigger = "army_charge",\n',
     '\t-- ROUND 171 (review row 5): the Warboss\'s army-wide Waaagh! (speed, charge, melee attack) gets its own entry\n'
     '\t-- ROUND 172: the doc\'s ruling - army charge OR army melee\n'
     '\t{ marker = "waaagh_army", name = "Waaagh!", trigger = "army_charge_or_melee",\n'),
    ('\t-- ROUND 171 (review row 1): the whole army\'s charge bonus x1.6 - when 3+ of our units charge at once\n',
     '\t-- ROUND 171 (review row 1): the whole army\'s charge bonus x1.6 - when 3+ of our units charge at once\n'
     '\t-- (ROUND 172: or every living unit in a smaller army)\n'),
    ('\t-- ROUND 171 (review row 3): the charge-bonus key (9 s, 35 m aura) gets its own entry\n',
     '\t-- ROUND 171 (review row 3): the charge-bonus key (9 s, 35 m aura) gets its own entry\n'
     '\t-- (ROUND 172: one unit charging or wavering is enough)\n'),
    # wiring
    ("\tarmy_charge = FOURTH.evaluate_army_charge,   -- ROUND 171\n",
     "\tarmy_charge = FOURTH.evaluate_army_charge,   -- ROUND 171\n"
     "\tarmy_charge_or_melee = FOURTH.evaluate_army_charge_or_melee,   -- ROUND 172\n"),
    # the internal labels
    ('\tarmy_charge = "When armed, fires when 3 or more of our units charge or have just made contact",   -- ROUND 171\n'
     '\taura_charge = "When armed, fires when this unit, or 2 or more units in its aura, charge or have just made contact",\n',
     '\tarmy_charge = "When armed, fires when 3 or more of our units (every unit in a smaller army) charge or have just made contact",   -- ROUND 171/172\n'
     '\tarmy_charge_or_melee = "When armed, fires when 3 or more of our units (every unit in a smaller army) charge, have just made contact, or fight in melee",\n'
     '\taura_charge = "When armed, fires when this unit or a unit in its aura charges, has just made contact, or wavers",\n'),
    # the cards (no final period, no distances)
    ('\tarmy_charge = "Fires when {ACN}+ of your units charge at once",   -- ROUND 171\n'
     '\taura_charge = "Fires when charging, or when {ACA}+ nearby allies charge",\n',
     '\tarmy_charge = "Fires when {ACN}+ of your units charge at once (all of them in a smaller army)",   -- ROUND 171/172\n'
     '\tarmy_charge_or_melee = "Fires when {ACN}+ of your units charge or fight at once (all of them in a smaller army)",\n'
     '\taura_charge = "Fires when it or a nearby ally charges or wavers",\n'),
    ("\tt.ACN, t.ACA = FOURTH.card_num(FOURTH.ARMY_CHARGE_MIN), FOURTH.card_num(FOURTH.AURA_CHARGE_ALLIES)\n",
     "\tt.ACN = FOURTH.card_num(FOURTH.ARMY_CHARGE_MIN)   -- ROUND 172: AURA_CHARGE_ALLIES is gone (one unit is enough)\n"),
]


def main():
    for path in (SRC, ANN):
        s = open(path, encoding="utf-8", newline="").read()
        assert "ROUND 172" not in s
        for o, n in R:
            assert s.count(o) == 1, (path[-12:], o[:80], s.count(o))
            s = s.replace(o, n)
        assert "AURA_CHARGE_ALLIES =" not in s and "{ACA}" not in s
        assert "\u2014" not in s
        open(path, "w", encoding="utf-8", newline="").write(s)
        print(path, "patched")


if __name__ == "__main__":
    main()
