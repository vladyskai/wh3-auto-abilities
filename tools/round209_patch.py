#!/usr/bin/env python3
"""Round 209 (2026-11-22, the user's replies to the afternoon code review).

1. THE LOONS GET A FRIENDLY-FIRE CHECK (user: "They are really prone for friendly fire. We need a friendly fire check,
   yes."). Spinning Loons and The Loons of Eight Peaks keep their trigger (the nearest enemy in melee in range) and get
   the entry field ring_clear = true: the evaluator is wrapped at load (FOURTH.ring_wrap) and also needs none of our
   OTHER units within the fanatics' reach + 10 m of the caster. The reach is GENERATED (FOURTH.RING_TEXT,
   tools/gen_ww_tables.py: vortex radius 4 m + simulated 95% reach 84 m), the numbers Da Boss' Loons has had since
   round 164. Card: FOURTH.CARD_TIP_RING.
2. LAMPREY'S BITE IS A SHORT WAVE (user: "fix please"). It was modelled as a 25 m disc on the target. In the game's
   table it starts 0.1 m wide, grows 14 m per second for 1 s while it rolls 24 m, so it ends 14.1 m wide and never
   reaches 25 m. It moves to enemy_wave (an exact, growing, ground-only wave: aimed like Blue Fire of Chaos). The WW
   table and the cone table are regenerated.
3. THE PLAYER'S OWN CAST IS PROTECTED (user: "Fixable?"). The game reports every ability order ("Special Ability"
   command, the key). The mod notes its own orders (FOURTH.note_own_order). A report that is not one of them is the
   player's: every selected unit gets the per-unit cast window (the ability's wind-up + 2 s when it is one of ours,
   FOURTH.PLAYER_CAST_HOLD_S for a key the mod does not know, nothing for one of ours with no wind-up), so the mod
   orders nothing else on that unit until the cast is out.
4. ONE BAD UNIT NO LONGER COSTS THE ARMY ITS POLL (user: "fixable?"). The per-unit body of the poll runs in its own
   guard: an error on one unit is counted (and logged in the test build) and the walk goes on.
Backups: docs/backups/round209/pre209_{live,ann}.lua."""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ww_tables as G  # noqa: E402
import gen_wave_cone as GC  # noqa: E402

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round209"

LOON_A = """		keys = { "wh_main_unit_abilities_spinning_loons" },
		range_real = 25,
		target_class = "not_flying",
"""
LOON_B = """		keys = { "wh_dlc06_unit_abilities_the_loons_of_eight_peaks" },
		range_real = 25,
		target_class = "not_flying",
"""
RING_LINE = "\t\tring_clear = true,   -- ROUND 209: none of our other units inside the fanatics' reach\n"
LAMP_OLD = '\t{ marker = "lampreys_bite", name = "Lamprey\'s Bite", trigger = "enemy_wander",\n'
LAMP_NEW = '\t{ marker = "lampreys_bite", name = "Lamprey\'s Bite", trigger = "enemy_wave",\n'

A_RING = "end\nFOURTH.load_ww_nomelee()\n"

A_WRAP = "function FOURTH.still_wrap(f)\n"
N_WRAP = """-- ============================================================================
-- ROUND 209 (2026-11-22, the user's replies to the afternoon code review).
--   ring_clear (the Loons): the fanatics are released at the caster, wander and
--   hit our units too. The entry's own trigger must hold AND none of our OTHER
--   units may stand within their reach + SHOT_SAFE_M of the caster (the rule Da
--   Boss' Loons has). The reach comes from the GENERATED FOURTH.RING.
--   THE PLAYER'S OWN CAST: the game reports every ability order with its key.
--   The mod notes its own orders; a report it did not order is the player's, and
--   every selected unit then gets the per-unit cast window, so the mod does not
--   replace the player's cast with one of its own.
--   ONE BAD UNIT: the per-unit body of the poll runs in its own guard.
-- ============================================================================
FOURTH.CARD_TIP_RING = "Fires at the nearest enemy in melee when none of our other units is near"
function FOURTH.ring_wrap(f, reach)
	return function(unit, routing)
		local why = f(unit, routing)
		if not why then return why end
		if reach == nil then return %(miss)s end   -- no table row: fail closed
		local ok, txt = FOURTH.self_clear(unit, reach)
		if not ok then return %(miss)s end
		if type(why) == "string" then
			return why .. "; released at the caster, they hit our units too: " .. tostring(txt)
		end
		return why
	end
end
FOURTH.PLAYER_CAST_HOLD_S = 5   -- the window after the player's cast of a key the mod does not know (a spell)
FOURTH.OWN_ECHO_TICKS = 8       -- the game's report of one of the mod's own orders is expected within 2 s
FOURTH.own_orders = {}          -- key -> { n = the mod's orders not yet reported back, at = the poll of the last one }
FOURTH.unit_errors = 0
function FOURTH.note_own_order(key)
	if key == nil then return end
	local r = FOURTH.own_orders[key]
	if r == nil or tick_count - r.at > FOURTH.OWN_ECHO_TICKS then
		r = { n = 0, at = tick_count }
		FOURTH.own_orders[key] = r
	end
	r.n = r.n + 1
	r.at = tick_count
end
-- the game reported an order for <key>: 0 when it is one of the mod's own (or nothing needs protecting), else the
-- number of selected units that got the window, and its length in seconds
function FOURTH.player_cast(key)
	if key == nil then return 0 end
	local r = FOURTH.own_orders[key]
	if r ~= nil and r.n > 0 and tick_count - r.at <= FOURTH.OWN_ECHO_TICKS then
		r.n = r.n - 1
		return 0
	end
	local hold_s = FOURTH.PLAYER_CAST_HOLD_S
	local wu = cast_gate.wind_up_s[key]
	if wu ~= nil then
		hold_s = wu + IN_FLIGHT_SETTLE_SECONDS
	elseif ALL_ABILITY_KEYS_SET[key] then
		return 0   -- one of ours with no wind-up: it is out at once, nothing to protect
	end
	local until_tick = tick_count + math.floor((hold_s * 1000) / POLL_MS)
	local n = 0
	for i = 1, #selected_ui_ids do
		local u = units_by_ui_id[selected_ui_ids[i]]
		local ok, raw = pcall(function() return u:unique_ui_id() end)
		if ok and raw ~= nil then
			if cast_gate.unit_until[raw] == nil or cast_gate.unit_until[raw] < until_tick then
				cast_gate.unit_until[raw] = until_tick
			end
			cast_gate.unit_marker[raw] = "(the player's own cast)"
			cast_gate.unit_waiting[raw] = nil
			cast_gate.unit_logged[raw] = nil
			n = n + 1
		end
	end
	return n, hold_s
end
function FOURTH.unit_error(err)
	FOURTH.unit_errors = FOURTH.unit_errors + 1
%(errlog)send
"""
ERRLOG_LIVE = """	if FOURTH.unit_errors <= 3 or (FOURTH.unit_errors % 40) == 0 then
		log("UNIT ERROR #" .. tostring(FOURTH.unit_errors) .. " (the walk goes on): " .. tostring(err))
	end
"""
ERRLOG_ANN = "\t-- (the test build logs the first three and every 40th)\n"

A_LOAD = "\t\tability.still_gate = true\n\tend\n"
N_LOAD = A_LOAD + """	if ability.ring_clear == true and ability.evaluate ~= nil then   -- ROUND 209: the Loons' friendly-fire ring
		ability.evaluate = FOURTH.ring_wrap(ability.evaluate, FOURTH.RING[ability.keys[1]])
	end
"""

A_CARD = "\t\ttpl = FOURTH.CARD_TIP_NOAURA[ability.trigger]\n\tend\n\tif tpl == nil then return nil end\n"
N_CARD = ("\t\ttpl = FOURTH.CARD_TIP_NOAURA[ability.trigger]\n\tend\n"
          "\tif ability.ring_clear == true then tpl = FOURTH.CARD_TIP_RING end   -- ROUND 209\n"
          "\tif tpl == nil then return nil end\n")

A_FIRED = '\t\t\t\telseif outcome == "fired" then\n\t\t\t\t\t-- a real fire ends the cooldown episode\n'
N_FIRED = A_FIRED + "\t\t\t\t\tFOURTH.note_own_order(ready_key)   -- ROUND 209: the game will report this order back\n"

A_LOOP = ("\tfor i = 1, #tracked_units do\n\t\tlocal script_unit = tracked_units[i]\n"
          "\t\tlocal unit = script_unit and script_unit.unit\n\n\t\t-- Only look at units still alive on the field.\n")
A_LOOP_END = "\t\tend\n\tend\n\t-- DROP EVERY COLLECTED id via the ONE drop routine"
# the three edits inside the per-unit block (the text between A_LOOP and A_LOOP_END)
L_IF = "\t\tif unit ~= nil and unit:number_of_men_alive() > 0 then\n"
N_IF = ("\t\t-- ROUND 209: the unit's own reads run in a guard, and so does each ability's step below, so an error on one\n"
        "\t\t-- unit never costs the rest of the army their poll (the ability loop itself stays in this function)\n"
        "\t\tlocal ok_unit, routing, ui_id, ability_key, unit_abilities = pcall(function()\n" + L_IF)
L_FOR = ("\t\t\tif unit_abilities == nil then\n\t\t\t\tunit_abilities = ABILITIES\n\t\t\tend\n"
         "\t\t\tfor _, ability in ipairs(unit_abilities) do\n")
N_FOR = ("\t\t\tif unit_abilities == nil then\n\t\t\t\tunit_abilities = ABILITIES\n\t\t\tend\n"
         "\t\t\treturn routing, ui_id, ability_key, unit_abilities\n"
         "\t\tend\n"
         "\t\tend)\n"
         "\t\tif not ok_unit then FOURTH.unit_error(routing) end\n"
         "\t\tif ok_unit and unit_abilities ~= nil then\n"
         "\t\t\tfor _, ability in ipairs(unit_abilities) do\n"
         "\t\t\t\tlocal ok_ab, res_ab = pcall(function()\n")
L_BREAK = 'gone_ids) == "gone" then\n\t\t\t\t\t\t\tbreak\n'
N_BREAK = 'gone_ids) == "gone" then\n\t\t\t\t\t\t\treturn "gone"\n'
L_TAIL = "\t\t\t\tend\n\t\t\tend\n"
N_TAIL = ("\t\t\t\tend\n"
          "\t\t\t\tend)\n"
          "\t\t\t\tif not ok_ab then FOURTH.unit_error(res_ab) elseif res_ab == \"gone\" then break end\n"
          "\t\t\tend\n")


def loop_patch(s):
    i = s.index(A_LOOP)
    j = s.index(A_LOOP_END)
    assert s.count(A_LOOP) == 1 and s.count(A_LOOP_END) == 1 and i < j
    b = s[i:j]
    for old in (L_IF, L_FOR, L_BREAK):
        assert b.count(old) == 1, (old, b.count(old))
    assert b.endswith(L_TAIL) and b.count("break") == 1 and b.count("return") == 0
    b = b[:-len(L_TAIL)] + N_TAIL
    b = b.replace(L_IF, N_IF).replace(L_FOR, N_FOR).replace(L_BREAK, N_BREAK)
    return s[:i] + b + s[j:]

A_CB_LIVE = """bm:register_command_handler_callback("Special Ability", function(context)
	local ability = "?"
	pcall(function() ability = context:get_string1() end)
	log("command: 'Special Ability' issued for '" .. tostring(ability) .. "'")
end, "zz_deadly_onslaught_ability_used")
"""
N_CB_LIVE = """bm:register_command_handler_callback("Special Ability", function(context)
	local ability = "?"
	local key = nil
	pcall(function()
		local s = context:get_string1()
		if s ~= nil then key = tostring(s) end
	end)
	if key ~= nil then ability = key end
	log("command: 'Special Ability' issued for '" .. tostring(ability) .. "'")
	-- ROUND 209: an order the mod did not give is the player's own cast: the selected units wait it out
	local ok_p, n, hold = pcall(FOURTH.player_cast, key)
	if ok_p and type(n) == "number" and n > 0 then
		log("  the player's own cast of '" .. tostring(ability) .. "': " .. tostring(n) .. " selected unit(s) hold their "
			.. "automatic abilities for " .. tostring(hold) .. "s")
	end
end, "zz_deadly_onslaught_ability_used")
"""
A_CB_ANN = """bm:register_phase_change_callback("Deployment", function()
	pcall(phase_ui_refresh)          -- scan for the buttons; sync the letters
end)
"""
N_CB_ANN = """-- ROUND 209: the game's report of an ability order (its key). An order the mod did not give is the player's own
-- cast: the selected units wait it out (FOURTH.player_cast).
bm:register_command_handler_callback("Special Ability", function(context)
	local key = nil
	pcall(function()
		local s = context:get_string1()
		if s ~= nil then key = tostring(s) end
	end)
	pcall(FOURTH.player_cast, key)
end, "zz_deadly_onslaught_ability_used")

""" + A_CB_ANN


def one(s, a, b, what):
    assert s.count(a) == 1, (what, s.count(a))
    return s.replace(a, b)


def patch(path, live):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 209" not in s, "already patched: " + path
    assert "\r\n" not in s
    s = one(s, LOON_A, LOON_A + RING_LINE, "spinning loons")
    s = one(s, LOON_B, LOON_B + RING_LINE, "loons of eight peaks")
    s = one(s, LAMP_OLD, LAMP_NEW, "lamprey")
    # the regenerated tables
    old_ww = re.search(r'FOURTH\.WW_TEXT = "[^"]*"', s).group(0)
    new_ww = re.search(r'FOURTH\.WW_TEXT = "[^"]*"', G.lua_block(G.derive(G.keys_in(s)))).group(0)
    assert old_ww != new_ww
    s = one(s, old_ww, new_ww, "WW_TEXT")
    old_cone = re.search(r'FOURTH\.WW_CONE_TEXT = "[^"]*"', s).group(0)
    cone = GC.derive(s)
    assert len(cone) == 20 and "wh3_dlc24_unit_abilities_lampreys_bite" in cone, len(cone)
    s = one(s, old_cone, 'FOURTH.WW_CONE_TEXT = "%s"' % GC.text(cone), "WW_CONE_TEXT")
    rk = G.ring_keys(s)
    assert sorted(rk) == ["wh_dlc06_unit_abilities_the_loons_of_eight_peaks", "wh_main_unit_abilities_spinning_loons"], rk
    s = one(s, A_RING, A_RING + G.ring_block(G.ring_rows(rk)), "ring table")
    miss = "nil" if live else "false"
    s = one(s, A_WRAP, N_WRAP % {"miss": miss, "errlog": ERRLOG_LIVE if live else ERRLOG_ANN} + A_WRAP, "wrap")
    s = one(s, A_LOAD, N_LOAD, "load loop")
    s = one(s, A_CARD, N_CARD, "card")
    s = one(s, A_FIRED, N_FIRED, "fired")
    s = loop_patch(s)
    if live:
        s = one(s, A_CB_LIVE, N_CB_LIVE, "callback")
    else:
        s = one(s, A_CB_ANN, N_CB_ANN, "callback")
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre209_live.lua"), (ANN, "pre209_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        elif "--again" in sys.argv:
            shutil.copy2(dst, src)   # start again from the pre-round snapshot
    patch(LIVE, True)
    patch(ANN, False)


if __name__ == "__main__":
    main()
