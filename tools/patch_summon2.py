"""Stage 2: the round's logic in BOTH files.

Live carries the log lines; the annotated copy gets the same decisions with no
reporting statements. Index-sliced block replacements with assertions.
"""
import os

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
LIVE = os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua")
ANN = os.path.join(ROOT, "docs", "WH3_auto_ability_annotated.lua")

def rd(p): return open(p, "rb").read().decode("utf-8")
def wr(p, s):
    assert "\r" not in s
    open(p, "wb").write(s.encode("utf-8"))

def sub(s, old, new, count=1, tag=""):
    n = s.count(old)
    assert n == count, "anchor %r hit %d (want %d) %s" % (old[:70], n, count, tag)
    return s.replace(old, new)

def cut_replace(s, start, end, new, tag=""):
    i = s.find(start)
    assert i >= 0, "start not found " + tag
    assert s.count(start) == 1, "start not unique " + tag
    j = s.find(end, i)
    assert j > i, "end not found " + tag
    return s[:i] + new + s[j:]

def eg_block(live):
    L = []
    a = L.append
    a("\t-- ENEMY-TARGETED RE-CHECK (Class A, harness 97): the enemy trigger chose an")
    a("\t-- unit and left it in FOURTH.eg_enemy (the cast target is the same unit,")
    a("\t-- in FOURTH.cast_target); RE-READ the condition NOW, immediately before the")
    a("\t-- cast - the enemy must still be ALIVE and still satisfy ITS OWN trigger")
    a("\t-- (in melee / under fire for the Class-A pickers, IN MELEE for Gate of")
    a("\t-- Khorne, BELOW 20% HEALTH AND NOT A LORD OR HERO for the Eye of Khorne")
    a("\t-- finisher, IN MELEE AND NOT A LORD OR HERO for The Dreaded Thirteenth) and")
    a("\t-- still within the ability's own 70% bound, RE-READ here via the engine's")
    a("\t-- `unit:unit_distance(enemy)` (EDGE-TO-EDGE metres, battle_unit.lua:160) and")
    a("\t-- whose REAL value is logged. If it lapsed the cast is wasted, so SKIP it")
    a("\t-- rather than spend it. The chosen enemy is the CAST TARGET - NEVER the")
    a("\t-- owner.")
    a("\tif FOURTH.eg_enemy ~= nil then")
    a("\t\tlocal enemy = FOURTH.eg_enemy")
    a("\t\tlocal eg_marker_now = FOURTH.eg_marker or \"accusation\"")
    a("\t\t-- A \"no bound\" entry (the game row declares target_intercept_range =")
    a("\t\t-- -1.0: no real range to take 70% of) skips the distance test entirely.")
    a("\t\tlocal eg_unbounded_now = (FOURTH.eg_no_bound == true)")
    a("\t\tlocal eg_bound_now = FOURTH.eg_range_m or FOURTH.ACCUSATION_RANGE_M")
    a("\t\tlocal eg_bound_text = tostring(eg_bound_now) .. \"m\"")
    a("\t\tif eg_unbounded_now then eg_bound_text = \"none\" end")
    a("\t\t-- GATE OF KHORNE (harness 101): a melee-only choice must STILL be")
    a("\t\t-- fighting; the missile arm is never a substitute for it.")
    a("\t\tlocal eg_melee_only_now = (FOURTH.eg_melee_only == true)")
    a("\t\t-- THE SUMMON-ROUND MODES (harness 102): the finisher (mode \"health\")")
    a("\t\t-- and The Dreaded Thirteenth (mode \"melee\") own their conditions; every")
    a("\t\t-- older enemy trigger leaves the mode nil.")
    a("\t\tlocal eg_mode_now = FOURTH.eg_mode")
    a("\t\tlocal ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)")
    a("\t\tlocal ok_melee, melee = pcall(function() return enemy:is_in_melee() end)")
    a("\t\tlocal still_melee = (ok_melee and melee == true)")
    a("\t\tlocal still_shot = false")
    a("\t\tif (not still_melee) and (not eg_melee_only_now) and eg_mode_now == nil then")
    a("\t\t\tstill_shot = FOURTH.eg_under_missile_attack(enemy)")
    a("\t\tend")
    a("\t\tlocal alive_now = (ok_alive and type(alive) == \"number\" and alive > 0)")
    a("\t\t-- RE-READ the bound NOW via the engine's edge-to-edge distance and log")
    a("\t\t-- its REAL value (the same primitive the offer test used).")
    a("\t\tlocal gap_now = FOURTH.eg_enemy_gap(unit, enemy)")
    a("\t\tlocal in_bound_now = eg_unbounded_now or (gap_now ~= nil and gap_now <= eg_bound_now)")
    a("\t\tlocal cond_now = (still_melee or still_shot)")
    a("\t\tlocal hp_now = nil")
    a("\t\tif eg_mode_now == \"health\" then")
    a("\t\t\thp_now = FOURTH.enemy_health_pct(enemy)")
    a("\t\t\tcond_now = (hp_now ~= nil and hp_now < FOURTH.HEALTH_LINE_PCT)")
    a("\t\telseif eg_mode_now == \"melee\" then")
    a("\t\t\tcond_now = still_melee")
    a("\t\tend")
    a("\t\tlocal cmdr_now = false")
    a("\t\tif FOURTH.eg_noncommander then")
    a("\t\t\tcmdr_now = FOURTH.enemy_is_commander(enemy)")
    a("\t\tend")
    a("\t\tlocal hp_text_now = \"\"")
    a("\t\tif hp_now ~= nil then")
    a("\t\t\thp_text_now = \" health=\" .. string.format(\"%.0f\", hp_now) .. \"%\"")
    a("\t\tend")
    a("\t\tif not alive_now or not cond_now or cmdr_now or not in_bound_now then")
    if live:
        a("\t\t\tlog(\"  \" .. eg_marker_now .. \" SKIPPED: the chosen enemy lapsed before the cast\"")
        a("\t\t\t\t.. \" (alive=\" .. tostring(alive_now) .. \" melee=\" .. tostring(still_melee)")
        a("\t\t\t\t.. \" shot=\" .. tostring(still_shot)")
        a("\t\t\t\t.. \" melee_only=\" .. tostring(eg_melee_only_now)")
        a("\t\t\t\t.. \" mode=\" .. tostring(eg_mode_now) .. hp_text_now")
        a("\t\t\t\t.. \" commander=\" .. tostring(cmdr_now)")
        a("\t\t\t\t.. ((gap_now ~= nil) and (\" distance=\" .. string.format(\"%.1f\", gap_now) .. \"m\") or \" distance=?\")")
        a("\t\t\t\t.. \" bound=\" .. eg_bound_text .. \") - cast not spent\")")
    a("\t\t\tFOURTH.eg_enemy = nil")
    a("\t\t\tFOURTH.eg_arm = nil")
    a("\t\t\tif RELEASE_CONTROL_AFTER and took_control then")
    a("\t\t\t\tlocal ok_release, err_release = pcall(function() uc:release_control() end)")
    if live:
        a("\t\t\t\tlog(\"  release_control         : ok=\" .. tostring(ok_release)")
        a("\t\t\t\t\t.. (ok_release and \"\" or (\"  ERROR: \" .. tostring(err_release))))")
    a("\t\t\tend")
    a("\t\t\treturn \"held\"")
    a("\t\tend")
    if live:
        a("\t\tlog(\"  \" .. eg_marker_now .. \" pre-cast re-check: target still engaged (\" .. tostring(FOURTH.eg_arm)")
        a("\t\t\t.. \", melee=\" .. tostring(still_melee) .. \" shot=\" .. tostring(still_shot)")
        a("\t\t\t.. \" melee_only=\" .. tostring(eg_melee_only_now)")
        a("\t\t\t.. \" mode=\" .. tostring(eg_mode_now) .. hp_text_now")
        a("\t\t\t.. \", distance=\" .. ((gap_now ~= nil) and string.format(\"%.1f\", gap_now) or \"?\")")
        a("\t\t\t.. \"m bound=\" .. eg_bound_text .. \") - firing\")")
    a("\tend")
    a("")
    return "\n".join(L) + "\n"

def ss_block(live):
    L = []
    a = L.append
    a("\t-- SELF-SUMMON RE-CHECK (harness 102, Nurgling Tide). The user's rule:")
    a("\t-- \"that one should only trigger when the caster himself is in melee.\"")
    a("\t-- Immediately before the call the OWNER must still be ALIVE and still IN")
    a("\t-- MELEE. NO RANGE BOUND is read or needed here: the cast is on the OWNER")
    a("\t-- itself, so there is no distance to measure and none is logged as a gap.")
    a("\tif FOURTH.ss_self then")
    a("\t\tlocal ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)")
    a("\t\tlocal ok_melee, melee = pcall(function() return unit:is_in_melee() end)")
    a("\t\tlocal alive_now = (ok_alive and type(alive) == \"number\" and alive > 0)")
    a("\t\tlocal melee_now = (ok_melee and melee == true)")
    a("\t\tif not alive_now or not melee_now then")
    if live:
        a("\t\t\tlog(\"  \" .. tostring(FOURTH.eg_marker) .. \" SKIPPED: the caster left melee before the self cast\"")
        a("\t\t\t\t.. \" (alive=\" .. tostring(alive_now) .. \" melee=\" .. tostring(melee_now)")
        a("\t\t\t\t.. \", no range bound - self cast) - cast not spent\")")
    a("\t\t\tFOURTH.ss_self = nil")
    a("\t\t\tif RELEASE_CONTROL_AFTER and took_control then")
    a("\t\t\t\tlocal ok_release, err_release = pcall(function() uc:release_control() end)")
    if live:
        a("\t\t\t\tlog(\"  release_control         : ok=\" .. tostring(ok_release)")
        a("\t\t\t\t\t.. (ok_release and \"\" or (\"  ERROR: \" .. tostring(err_release))))")
    a("\t\t\tend")
    a("\t\t\treturn \"held\"")
    a("\t\tend")
    if live:
        a("\t\tlog(\"  \" .. tostring(FOURTH.eg_marker) .. \" pre-cast re-check: the caster is still in melee\"")
        a("\t\t\t.. \" (alive=\" .. tostring(alive_now) .. \" melee=\" .. tostring(melee_now)")
        a("\t\t\t.. \", no range bound - self cast) - firing\")")
    a("\tend")
    a("")
    return "\n".join(L) + "\n"

for path, tag, live in ((LIVE, "live", True), (ANN, "ann", False)):
    s = rd(path)
    if live:
        A_SLOT = "FOURTH.eg_melee_only = nil\n\n-- one-time notice for an unreadable is_under_missile_attack."
        A_EG = "\t-- ENEMY-TARGETED RE-CHECK (Class A, harness 97): the enemy trigger chose an"
    else:
        A_SLOT = "FOURTH.eg_melee_only = nil\n\n-- THE DISTANCE PRIMITIVE (harness 96):"
        A_EG = ("\tif FOURTH.eg_enemy ~= nil then\n"
                "\t\tlocal enemy = FOURTH.eg_enemy\n"
                "\t\tlocal ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)")

    # 1. the new slots
    s = sub(s, A_SLOT,
            "FOURTH.eg_melee_only = nil\n"
            "-- THE SUMMON-ROUND SLOTS (harness 102): the SELF-SUMMON arm's own flag and\n"
            "-- its freshly re-fetched caster script_unit; the non-commander flag; the\n"
            "-- picker's MODE (\"health\" / \"melee\"); and the \"no bound\" flag for an\n"
            "-- entry whose own game row declares target_intercept_range = -1.0 (no real\n"
            "-- range, so there is no 70% value to take). Cleared before every evaluate.\n"
            "FOURTH.ss_self = nil\n"
            "FOURTH.ss_caster_su = nil\n"
            "FOURTH.eg_noncommander = nil\n"
            "FOURTH.eg_mode = nil\n"
            "FOURTH.eg_no_bound = nil\n\n"
            "-- one-time notice for an unreadable is_under_missile_attack.", 1, tag)

    # 2. the no-bound early return
    s = sub(s, "function FOURTH.eg_enemy_within_bound(unit, enemy)\n\tlocal gap = FOURTH.eg_enemy_gap(unit, enemy)",
            "function FOURTH.eg_enemy_within_bound(unit, enemy)\n"
            "\t-- AN UNBOUNDED ENTRY (harness 102): its game row declares\n"
            "\t-- target_intercept_range = -1.0 - NO real range - so there is no 70%\n"
            "\t-- bound to apply and every living enemy is inside it.\n"
            "\tif FOURTH.eg_no_bound == true then return true end\n"
            "\tlocal gap = FOURTH.eg_enemy_gap(unit, enemy)", 1, tag)

    # 3. the self-summon caster override, right after the ally block
    s = sub(s, "\t\tif FOURTH.ab_ally_su ~= nil and FOURTH.ab_ally_su.unit ~= nil then\n"
               "\t\t\ttarget = FOURTH.ab_ally_su.unit\n"
               "\t\tend\n\tend\n",
            "\t\tif FOURTH.ab_ally_su ~= nil and FOURTH.ab_ally_su.unit ~= nil then\n"
            "\t\t\ttarget = FOURTH.ab_ally_su.unit\n"
            "\t\tend\n\tend\n"
            "\t-- SELF-SUMMON (harness 102, Nurgling Tide): the cast is on the OWNER and\n"
            "\t-- the controller is the CASTER's script_unit re-fetched FRESH this tick\n"
            "\t-- (the same discipline as every other cast in this file).\n"
            "\tif FOURTH.ss_self then\n"
            "\t\tif FOURTH.ss_caster_su ~= nil and FOURTH.ss_caster_su.uc ~= nil then\n"
            "\t\t\tuc = FOURTH.ss_caster_su.uc\n"
            "\t\tend\n"
            "\t\ttarget = unit\n"
            "\tend\n", 1, tag)

    # 4. the enemy pre-cast block + the self pre-cast block
    new = eg_block(live) + ss_block(live)
    s = cut_replace(s, A_EG,
                    "\t-- THE CALL. Ordinary keys (self- or unit-targeted) use the proven",
                    new, tag)

    wr(path, s)
    print(tag, "stage 2 written", len(s), "bytes")
