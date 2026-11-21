#!/usr/bin/env python3
"""Round 198 (user 2026-11-22, the overnight review: "fix" on rows 1, 2, 3, 6, 7, 8, 11), both copies.
 1 THE SERIAL WINDOW: a per-unit window that has already closed forgets who armed it, so a repeat of the SAME ability
   arms it again (before, the repeat armed nothing and another ability could replace it mid wind-up). NO STARVING: the
   ability that armed the last window yields one poll to an ability that waited through it.
 2 THE ENTRY RESET: the poll's per-entry slot reset becomes ONE function (FOURTH.entry_reset) and the air-drop fast pass
   calls it too (before, the fast pass inherited the last poll's chosen targets).
 3 Get Tha Gitz! (3 uses): its charge-hold row.
 6 The Necromancer (Undeath) on a Nightmare: its land_units key joins the Lord/Hero list (the main_units key stays).
 7 slow_aura and guard_aura: the round-192 fast-enemy read (running and closing), then inside the aura.
 8 Favour of the Fay, Shielding Swarm x2: the game's target_self is false, so the self arm is skipped (entry field
   no_self); their card says so.
11 Bugman's XXXXXX: the keep-out distance is the game's whole 55 m (was 38).
Backups: docs/backups/round198/pre198_{live,ann}.lua."""
import os
import shutil

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round198"

T4, T5, T8 = "\t" * 4, "\t" * 5, "\t" * 8

# ---- 1. the serial window --------------------------------------------------------------------------------------
E1_OLD = T4 + "if cast_gate.unit_marker[ui_id] ~= ability.marker then\n"
E1_NEW = (T4 + "-- ROUND 198: a window that has already CLOSED forgets who armed it, so a repeat of the\n"
          + T4 + "-- same ability arms it again (an open window is still not extended by a repeat).\n"
          + T4 + "if cast_gate.unit_until[ui_id] ~= nil and tick_count >= cast_gate.unit_until[ui_id] then\n"
          + T5 + "cast_gate.unit_marker[ui_id] = nil\n"
          + T4 + "end\n"
          + E1_OLD)

# ---- 1b. no starving: the ability that armed the last window yields one poll to an ability that waited through it
T3 = "\t" * 3
E1B_OLD = (T3 + "if eligible and cast_gate.unit_until[ui_id] ~= nil\n"
           + T4 + "and cast_gate.unit_marker[ui_id] ~= ability.marker\n")
E1B_NEW = (T3 + "-- ROUND 198: NO STARVING. Since a repeat re-arms a closed window, an ability that repeats\n"
           + T3 + "-- exactly when its own window closes would lock the unit's other abilities out for good.\n"
           + T3 + "-- So the ability that armed the last window YIELDS ONE POLL when another ability waited\n"
           + T3 + "-- through that window: the waiter (evaluated later in this poll, or in the next) goes first.\n"
           + T3 + "if eligible and cast_gate.unit_waiting[ui_id] == true\n"
           + T4 + "and cast_gate.unit_marker[ui_id] == ability.marker\n"
           + T4 + "and cast_gate.unit_until[ui_id] ~= nil and tick_count >= cast_gate.unit_until[ui_id] then\n"
           + T4 + "cast_gate.unit_waiting[ui_id] = nil\n"
           + T4 + "eligible = false\n"
           + T4 + "quiet = true\n"
           + T3 + "end\n" + E1B_OLD)
E1C_OLD = T4 + "quiet = true\n" + T4 + "local lg = cast_gate.unit_logged[ui_id]\n"
E1C_NEW = (T4 + "quiet = true\n" + T4 + "cast_gate.unit_waiting[ui_id] = true   -- ROUND 198: it waited through this window\n"
           + T4 + "local lg = cast_gate.unit_logged[ui_id]\n")
E1D_OLD = "\tunit_marker = {},  -- ui id -> the marker of the cast that armed that window\n"
E1D_NEW = E1D_OLD + "\tunit_waiting = {}, -- ROUND 198: ui id -> true while another ability waited through the open window\n"
E1E_OLD = "\tcast_gate.unit_marker[id_slot] = nil\n"
E1E_NEW = E1E_OLD + "\tcast_gate.unit_waiting[id_slot] = nil\n"
E1F_OLD = T5 + "cast_gate.unit_marker[ui_id] = ability.marker\n"
E1F_NEW = E1F_OLD + T5 + "cast_gate.unit_waiting[ui_id] = nil   -- ROUND 198: a new window, nobody has waited through it yet\n"

# ---- 2. the entry reset ----------------------------------------------------------------------------------------
BLOCK_FIRST = T5 + "FOURTH.cast_target = nil\n"
BLOCK_LAST = T5 + "FOURTH.ah_marker = ability.marker\n"
RESET_HEAD = """-- ============================================================================
-- ROUND 198 - THE ENTRY RESET (overnight review 2026-11-22, row 2). Every slot
-- an evaluator may fill (the chosen ally, enemy, ground flag, cast mode ...) is
-- cleared, and the current entry's own bounds and markers are set, before EVERY
-- evaluate. It was a block inside the poll; the air-drop fast pass (its own
-- 0.2 s timer) reset only its six air-drop slots and so inherited whatever the
-- last entry of the last poll had chosen. Both now call this ONE function.
-- ============================================================================
function FOURTH.entry_reset(ability, unit)
"""
RESET_CALL = T5 + "FOURTH.entry_reset(ability, unit)   -- ROUND 198: the slot reset, shared with the fast pass\n"
POLL_ANCHOR = "local function poll_body()\n"
NOSELF_ANCHOR = "FOURTH.ab_atarget = ability.atarget"
NOSELF_LINE = "FOURTH.ab_no_self = (ability.no_self == true)   -- ROUND 198: the game's target_self is false\n"
FAST_OLD = (T8 + "-- THE CURRENT ENTRY'S OWN SLOTS, exactly as the poll\n"
            + T8 + "-- sets them before its evaluate call.\n"
            + T8 + "FOURTH.ad_marker = ability.marker\n"
            + T8 + "FOURTH.ad_air_only = (ability.air_only == true)\n"
            + T8 + "FOURTH.ad_no_melee = (ability.no_melee == true)\n"
            + T8 + "FOURTH.ad_range_m = ability.range_m\n"
            + T8 + "FOURTH.ad_enemy = nil\n"
            + T8 + "FOURTH.ad_caster_su = nil\n")
FAST_NEW = (T8 + "-- ROUND 198: EVERY slot, exactly as the poll resets them before its\n"
            + T8 + "-- evaluate call (before, only the six air-drop slots were reset here).\n"
            + T8 + "FOURTH.entry_reset(ability, unit)\n")

# ---- 3. Get Tha Gitz! ------------------------------------------------------------------------------------------
E3_OLD = "\t\t-- ROUND 193: Scry-Orb, 3 uses (recharge_time)\n"
E3_NEW = ("\t\t-- ROUND 198: Get Tha Gitz!, 3 uses (recharge_time): the one multi-use key that had no row\n"
          "\t\t[\"wh3_dlc23_hero_abilities_get_tha_gitz!\"] = 120,\n" + E3_OLD)

# ---- 6. the Necromancer on a Nightmare -------------------------------------------------------------------------
E6_OLD = "\t\t[\"wh3_dlc29_vmp_cha_necromancer_undeath_barded_nightmare\"] = true,\n"
E6_NEW = (E6_OLD + "\t\t[\"wh3_dlc29_vmp_cha_necromancer_undeath_nightmare\"] = true,"
          "   -- ROUND 198: the land_units key of the row above (a main_units key)\n")

# ---- 7. slow_aura / guard_aura ---------------------------------------------------------------------------------
E7A_OLD = """			local ok_a, men = pcall(function() return e:number_of_men_alive() end)
			local ok_mv, mv = pcall(function() return e:is_moving() end)
			local ok_sp, sp = pcall(function() return e:fast_speed() end)
			local ok_g, g = pcall(function() return unit:unit_distance(e) end)
			if ok_a and type(men) == "number" and men > 0 and ok_mv and mv == true
				and ok_sp and type(sp) == "number" and sp >= FOURTH.FAST_ENEMY_MPS
				and ok_g and type(g) == "number" and g <= reach then
				return string.format("a fast enemy (run speed %.1f m/s) %.1fm away, inside the %sm aura (slow aura)",
"""
E7A_NEW = """			local ok_a, men = pcall(function() return e:number_of_men_alive() end)
			-- ROUND 198: the round-192 read (RUNNING and CLOSING on our units), then inside the aura
			local near, sp = nil, nil
			if ok_a and type(men) == "number" and men > 0 then near, sp = FOURTH.fast_enemy_near(e, unit) end
			local ok_g, g = pcall(function() return unit:unit_distance(e) end)
			if near ~= nil and ok_g and type(g) == "number" and g <= reach then
				return string.format("a fast enemy (run speed %.1f m/s) %.1fm away, inside the %sm aura (slow aura)",
"""
E7B_OLD = """		local ok_mv, mv = pcall(function() return x:is_moving() end)
		local ok_sp, s = pcall(function() return x:fast_speed() end)
		local ok_g, gap = pcall(function() return unit:unit_distance(x) end)
		if ok_mv and mv == true and ok_sp and type(s) == "number" and s >= FOURTH.FAST_ENEMY_MPS
			and ok_g and type(gap) == "number" and gap <= reach then
			return gap, s
"""
E7B_NEW = """		-- ROUND 198: the round-192 read (RUNNING and CLOSING on our units), then inside the aura
		local near, s = FOURTH.fast_enemy_near(x, unit)
		local ok_g, gap = pcall(function() return unit:unit_distance(x) end)
		if near ~= nil and ok_g and type(gap) == "number" and gap <= reach then
			return gap, s
"""

# ---- 8. no self arm --------------------------------------------------------------------------------------------
E8_ENTRIES = [
    "\t\tkeys = { \"wh_dlc07_lord_abilities_favour_of_the_fay\" },\n\t\tally_range_real = 100,\n",
    "\t\tkeys = { \"wh3_dlc29_hero_active_dispatch_the_swarm_protect\" },\n\t\tally_range_real = 100,\n",
    "\t\tkeys = { \"wh3_dlc29_hero_active_dispatch_the_swarm_protect_upgraded\" },\n\t\tally_range_real = 100,\n",
]
E8_FIELD = "\t\tno_self = true,   -- ROUND 198: the game's target_self is false (never cast on the caster)\n"
E8A_OLD_LIVE = "\tif ok and m == true then return \"the caster is in melee, cast on self\" end\n\treturn FOURTH.ab_pick_ally(unit, routing, \"melee\")\n"
E8A_NEW_LIVE = ("\tif ok and m == true and not FOURTH.ab_no_self then return \"the caster is in melee, cast on self\" end"
                "   -- ROUND 198\n\treturn FOURTH.ab_pick_ally(unit, routing, \"melee\")\n")
E8A_OLD_ANN = "\tif ok and m == true then return true end\n\treturn FOURTH.ab_pick_ally(unit, routing, \"melee\")\n"
E8A_NEW_ANN = ("\tif ok and m == true and not FOURTH.ab_no_self then return true end   -- ROUND 198\n"
               "\treturn FOURTH.ab_pick_ally(unit, routing, \"melee\")\n")
E8B_OLD = "\tif FOURTH.in_melee_now(unit) or FOURTH.under_fire(unit) then\n\t\treturn \"the caster is in melee or under missile fire, cast on self\"\n"
E8B_NEW = ("\tif not FOURTH.ab_no_self and (FOURTH.in_melee_now(unit) or FOURTH.under_fire(unit)) then   -- ROUND 198\n"
           "\t\treturn \"the caster is in melee or under missile fire, cast on self\"\n")
E8C_OLD = "FOURTH.CARD_TIP_NOAURA = "
E8C_NEW = ("-- ROUND 198: the card of an entry the game never lets target its own caster (entry field no_self)\n"
           "FOURTH.CARD_TIP_NOSELF = { melee_self_or_ally = \"Fires on the nearest ally in melee\",\n"
           "\tself_or_ally_fire_melee = \"Fires on an ally under fire, else on an ally in melee\" }\n" + E8C_OLD)
E8D_OLD = "\tif ability.aura_m == nil and FOURTH.CARD_TIP_NOAURA[ability.trigger] ~= nil then"
E8D_NEW = ("\tif ability.no_self == true and FOURTH.CARD_TIP_NOSELF[ability.trigger] ~= nil then   -- ROUND 198\n"
           "\t\ttpl = FOURTH.CARD_TIP_NOSELF[ability.trigger]\n\tend\n" + E8D_OLD)

# ---- 11. Bugman's ----------------------------------------------------------------------------------------------
E11_OLD = "FOURTH.BUGMAN_CLEAR_M = 38   -- floor(55 * 0.70): Bugman's XXXXXX's own 55 m intercept range (target_intercept_range)\n"
E11_NEW = ("FOURTH.BUGMAN_CLEAR_M = 55   -- ROUND 198: Bugman's XXXXXX's own 55 m intercept range, WHOLE (a keep-out distance"
           " takes no 70% cut: the game refuses the cast with an enemy inside 55 m; was 38)\n")


def one(s, old, new, path):
    assert s.count(old) == 1, (path, old[:80], s.count(old))
    return s.replace(old, new)


def move_block(s, path):
    assert s.count(BLOCK_FIRST) == 1 and s.count(BLOCK_LAST) == 1, path
    i = s.index(BLOCK_FIRST)
    j = s.index(BLOCK_LAST) + len(BLOCK_LAST)
    assert i < j
    block = s[i:j]
    body = []
    for line in block.split("\n")[:-1]:
        assert line.startswith(T5) or line == "", (path, line)
        body.append(line[4:] if line else line)
        if NOSELF_ANCHOR in line:
            body.append("\t" + NOSELF_LINE.rstrip("\n"))
    assert sum(1 for b in body if "FOURTH.ab_no_self" in b) == 1, path
    func = RESET_HEAD + "\n".join(body) + "\nend\n\n"
    s = s[:i] + RESET_CALL + s[j:]
    assert s.count(POLL_ANCHOR) == 1, path
    return s.replace(POLL_ANCHOR, func + POLL_ANCHOR)


def patch(path, ann):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 198" not in s, "already patched: " + path
    s = one(s, E1_OLD, E1_NEW, path)
    for o, n in ((E1B_OLD, E1B_NEW), (E1C_OLD, E1C_NEW), (E1D_OLD, E1D_NEW), (E1E_OLD, E1E_NEW), (E1F_OLD, E1F_NEW)):
        s = one(s, o, n, path)
    s = move_block(s, path)
    s = one(s, FAST_OLD, FAST_NEW, path)
    s = one(s, E3_OLD, E3_NEW, path)
    s = one(s, E6_OLD, E6_NEW, path)
    s = one(s, E7A_OLD, E7A_NEW, path)
    s = one(s, E7B_OLD, E7B_NEW, path)
    for e in E8_ENTRIES:
        s = one(s, e, e + E8_FIELD, path)
    if ann:
        s = one(s, E8A_OLD_ANN, E8A_NEW_ANN, path)
    else:
        s = one(s, E8A_OLD_LIVE, E8A_NEW_LIVE, path)
    s = one(s, E8B_OLD, E8B_NEW, path)
    s = one(s, E8C_OLD, E8C_NEW, path)
    s = one(s, E8D_OLD, E8D_NEW, path)
    s = one(s, E11_OLD, E11_NEW, path)
    assert "\r" not in s and "\u2014" not in s
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre198_live.lua"), (ANN, "pre198_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    patch(LIVE, False)
    patch(ANN, True)


if __name__ == "__main__":
    main()
