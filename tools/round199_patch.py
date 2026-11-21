#!/usr/bin/env python3
"""Round 199 (user 2026-11-22, the overnight review's second replies), both copies.
 5  "okay, then fix": a key the game spells with a capital letter (Doom & Darkness, gunnery school) can be claimed:
    the badge's equality compare also accepts the listed key in lower case (FOURTH.KEY_LOWER, built at load).
 9  "please implement, but also include the caster as I tested and it could cast on the caster": the ten ally-targeted
    abilities that were cast on the caster only get an ALLY ARM (entry field ally_value_arm): the most valuable unit in
    melee wins, the caster (when its own trigger holds) or an ally in melee inside the game's range. Wild Abandon and
    The Hand of Dust are single-target abilities the game never lets the caster take (target_self false, no ground
    form, the Favour of the Fay case): ally_value_arm = "only".
 10 "agreed, please fix": the bombardments' infantry test refuses a unit of the generated large set and a flying unit.
 12 "agreed, implement": the remembered M/A choice of a unit type sets the START of a battle only. A click changes the
    clicked unit, and writes the type's choice for the NEXT battle (ability.remember_next); the other units of that
    type keep what they had.
Backups: docs/backups/round199/pre199_{live,ann}.lua."""
import os
import shutil

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round199"

# ---- 5. the capital letter -------------------------------------------------------------------------------------
E5_OLD = "if candidate == listed_key then\n"
E5_NEW = "if candidate == listed_key or candidate == FOURTH.KEY_LOWER[listed_key] then   -- ROUND 199: a key with a capital\n"

# ---- 9. the ally arm -------------------------------------------------------------------------------------------
WRAP_ANCHOR = "function FOURTH.still_wrap(f)\n"
WRAP = """-- ============================================================================
-- ROUND 199 - THE ALLY ARM (overnight review row 9; user 2026-11-22: "please
-- implement, but also include the caster as I tested and it could cast on the
-- caster"). Ten ally-targeted abilities were cast on the caster only. An entry
-- with ally_value_arm keeps its own trigger for the caster and adds the most
-- valuable ally in melee inside the game's range (the round-179 value_melee
-- pick): the more valuable of the two wins, the caster on a tie.
-- ally_value_arm = "only": a single-target ability the game never lets the
-- caster take (target_self false and no ground form): the ally alone.
-- FOURTH.KEY_LOWER: a listed key the game spells with a capital letter, in
-- lower case (the badge compares the button's lowered key).
-- ============================================================================
FOURTH.KEY_LOWER = {}
function FOURTH.ally_arm_wrap(f, ally_only)
	return function(unit, routing)
		local own = f(unit, routing)
		if ally_only then own = nil end
		if routing then return own end
		local r = FOURTH.ab_pick_ally(unit, routing, "value_melee")
		if r then
			if not own then return r end
			local theirs, mine = FOURTH.unit_value(FOURTH.ab_ally), FOURTH.unit_value(unit)
			if type(theirs) == "number" and type(mine) == "number" and theirs > mine then return r end
		end
		-- the caster itself (or nothing): the ally pick leaves no slot behind
		FOURTH.cast_target, FOURTH.ab_ally, FOURTH.ab_caster_su, FOURTH.ab_ally_su, FOURTH.ab_family = nil, nil, nil, nil, nil
		return own
	end
end
"""
WIRE_OLD = "\t\tability.still_gate = true\n\tend\n"
WIRE_NEW = WIRE_OLD + """	if ability.ally_value_arm ~= nil and ability.evaluate ~= nil then   -- ROUND 199: the ally arm
		ability.evaluate = FOURTH.ally_arm_wrap(ability.evaluate, ability.ally_value_arm == "only")
	end
	for _, key in ipairs(ability.keys) do   -- ROUND 199: a key the game spells with a capital letter
		local lk = string.lower(key)
		if lk ~= key then FOURTH.KEY_LOWER[key] = lk end
	end
"""
CARD_ANCHOR = "function FOURTH.compose_card(ability)\n"
CARD_DEF = ("-- ROUND 199: the card of an entry with an ally arm\n"
            "FOURTH.CARD_ALLY_ARM = \", or on a more valuable ally in melee\"\n"
            "FOURTH.CARD_ALLY_ONLY = \"Fires on the most valuable ally in melee\"\n")
CARD_OLD = "\tif tpl == nil then return nil end\n"
CARD_NEW = CARD_OLD + ("\tif ability.ally_value_arm == \"only\" then   -- ROUND 199\n"
                       "\t\ttpl = FOURTH.CARD_ALLY_ONLY\n"
                       "\telseif ability.ally_value_arm == true then\n"
                       "\t\ttpl = tpl .. FOURTH.CARD_ALLY_ARM\n"
                       "\tend\n")
# key -> (the game's target_intercept_range, the field value)
ARMS = [
    ("wh3_dlc29_lord_abilities_hellish_vigour_upgraded", 75, "true"),
    ("wh3_dlc26_lord_abilities_wild_abandon", 100, "\"only\""),
    ("wh3_dlc29_spell_bound_undeath_sulekhim_hand_of_dust", 200, "\"only\""),
    ("wh3_dlc26_character_abilities_cash_cascade", 200, "true"),
    ("wh3_main_lord_abilities_master_of_alchemy", 100, "true"),
    ("wh3_main_lord_abilities_master_of_alchemy_flaming", 100, "true"),
    ("wh3_main_lord_abilities_master_of_alchemy_piercing", 100, "true"),
    ("wh3_main_lord_abilities_master_of_alchemy_poison", 100, "true"),
    ("wh_dlc06_rune_abilities_master_rune_of_oath_and_steel", 100, "true"),
    ("wh_dlc06_lord_abilities_spite_of_da_bad_moon", 150, "true"),
]

# ---- 10. the infantry test -------------------------------------------------------------------------------------
E10_OLD = "function FOURTH.enemy_is_infantry(enemy)\n"
E10_NEW = E10_OLD + """	-- ROUND 199 (overnight review row 10; user: "agreed, please fix"): the engine calls some monsters and fliers
	-- infantry (the map probe: Fell Bats, the Varghulf, the Zombie Dragon). A unit of the generated large set, or one
	-- flying right now, is not infantry here (the blob family's test).
	local t199 = FOURTH.type_plain(enemy)
	if t199 ~= nil and FOURTH.class_keys.large[t199] == true then return false end
	local ok_f199, fl199 = pcall(function() return enemy:is_currently_flying() end)
	if ok_f199 and fl199 == true then return false end
"""

# ---- 12. the remembered choice sets the start of a battle only ---------------------------------------------------
E12A_OLD = "for _, a in ipairs(ABILITIES) do a.remembered = nil end"
E12A_NEW = "for _, a in ipairs(ABILITIES) do a.remembered, a.remember_next = nil, nil end"
E12B_OLD = "\t\t\t\ta.remembered[t] = (v == \"A\")\n"
E12B_NEW = E12B_OLD + ("\t\t\t\ta.remember_next = a.remember_next or {}   -- ROUND 199: what the file holds for the next battle\n"
                       "\t\t\t\ta.remember_next[t] = (v == \"A\")\n")
E12C_OLD = "pairs(a.remembered or {})"
E12C_NEW = "pairs(a.remember_next or {})"
E12D_OLD = """	a.remembered = a.remembered or {}
	if (value == true) == (a.default_on == true) then
		a.remembered[t] = nil
	else
		a.remembered[t] = (value == true)
	end
	if next(a.remembered) == nil then a.remembered = nil end
"""
E12D_NEW = """	-- ROUND 199 (overnight review row 12; user: "agreed, implement"): ability.remembered is the START of this battle
	-- (read by is_armed for a unit with no switch of its own) and is NOT changed by a click: the other units of the
	-- type keep what they had. The click goes to ability.remember_next, the table the file is written from.
	a.remember_next = a.remember_next or {}
	if (value == true) == (a.default_on == true) then
		a.remember_next[t] = nil
	else
		a.remember_next[t] = (value == true)
	end
	if next(a.remember_next) == nil then a.remember_next = nil end
"""


def one(s, old, new, path, n=1):
    assert s.count(old) == n, (path, old[:80], s.count(old))
    return s.replace(old, new)


def patch(path):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 199" not in s, "already patched: " + path
    s = one(s, E5_OLD, E5_NEW, path)
    s = one(s, WRAP_ANCHOR, WRAP + WRAP_ANCHOR, path)
    s = one(s, WIRE_OLD, WIRE_NEW, path)
    s = one(s, CARD_ANCHOR, CARD_DEF + CARD_ANCHOR, path)
    s = one(s, CARD_OLD, CARD_NEW, path)
    for key, rng, val in ARMS:
        old = "\t\tkeys = { \"" + key + "\" },\n"
        new = (old + "\t\tally_range_real = %d,\n" % rng
               + "\t\tally_value_arm = %s,   -- ROUND 199: the ally arm (the most valuable unit in melee)\n" % val)
        s = one(s, old, new, path)
    s = one(s, E10_OLD, E10_NEW, path)
    s = one(s, E12A_OLD, E12A_NEW, path, 2)
    s = one(s, E12B_OLD, E12B_NEW, path)
    s = one(s, E12C_OLD, E12C_NEW, path)
    s = one(s, E12D_OLD, E12D_NEW, path)
    assert "\r" not in s and "\u2014" not in s
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre199_live.lua"), (ANN, "pre199_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    patch(LIVE)
    patch(ANN)


if __name__ == "__main__":
    main()
