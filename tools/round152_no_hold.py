#!/usr/bin/env python3
"""Round 152 (harness 151): field rulings 2026-11-15 after the round-151 battle.

  * the whole-map HOLD is removed ("let's do not hold for a large unit in the whole map"): in the battle it kept all
    three breaths silent for the whole fight;
  * large first stays for the 53 prefer-central attacks, but never at a FLYING large enemy ("Large first, skip fliers":
    breaths miss flying single entities); is_currently_flying() must read exactly false;
  * the 90-degree preference applies to all 53 prefer-central attacks ("All 53 central attacks"), breaths included;
  * Foe-Seeker and the other 'tired' ability start ARMED ("Foe-Seeker + tired");
  * the ALL badge moves on screen: below the portrait, right of the camera button (the user's screenshot), offset
    (-880, 8) calibrated from the top-slot and bottom-right-slot badges in that screenshot.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"


def sub(s, a, b):
    assert s.count(a) == 1, (a[:90], s.count(a))
    return s.replace(a, b)


def cut(s, start, end, new):
    assert s.count(start) == 1, start[:60]
    a = s.index(start)
    b = s.index(end, a)
    return s[:a] + new + s[b:]


HOLD_FN_START = "-- ROUND 151: the hold - a visible large enemy ANYWHERE"
HOLD_FN_END = "-- ROUND 151: the game's own usage rules - grounded"
HOLD_FN_NEW = ("-- ROUND 152 (user ruling 2026-11-15): the whole-map hold is GONE (\"let's do not hold for a large unit in the\n"
               "-- whole map\") - in the round-151 battle it kept every breath silent all fight.\n\n"
               "-- ROUND 152 (\"Large first, skip fliers\"): a large target must read is_currently_flying() exactly false\n"
               "function FOURTH.blob_not_flying(u)\n"
               "\tlocal ok, fly = pcall(function() return u:is_currently_flying() end)\n"
               "\treturn ok and fly == false\n"
               "end\n\n")
LIVE_HOLD_START = "\t\t-- ROUND 151: THE HOLD - a more valuable large enemy anywhere on the field keeps this cast for it\n"
LIVE_HOLD_END = "\t\tkind = \"infantry\"\n"
ANN_HOLD = "\t\tif central and FOURTH.blob_large_hold(m, key, val or 0) then return false end\n"
SAID = "FOURTH.blob_hold_said = {}\n"
LARGE_OLD = ("\tfor i = 1, #m.large do\n\t\tlocal e = m.large[i]\n"
             "\t\tif FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit) and FOURTH.blob_ap_ok(e, dmg) then\n")
LARGE_NEW = ("\tfor i = 1, #m.large do\n\t\tlocal e = m.large[i]\n"
             "\t\tif FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit) and FOURTH.blob_ap_ok(e, dmg)\n"
             "\t\t\tand FOURTH.blob_not_flying(e.unit) then   -- ROUND 152: never a flying large target\n")
RECHK_OLD = ("\t\t\t\tif g ~= nil and g <= reach then return false end\n"
             "\t\t\t\treturn FOURTH.blob_ap_ok(e, key and FOURTH.BLOB_DMG[key])\n")
RECHK_NEW = ("\t\t\t\tif g ~= nil and g <= reach then return false end\n"
             "\t\t\t\tif not FOURTH.blob_not_flying(e.unit) then return false end   -- ROUND 152\n"
             "\t\t\t\treturn FOURTH.blob_ap_ok(e, key and FOURTH.BLOB_DMG[key])\n")
ANGLE_OLD = "\tif shot ~= nil and shot[6] == 1 then\n"
ANGLE_NEW = ("\t-- ROUND 152 (user ruling 2026-11-15, \"All 53 central attacks\"): every prefer-central attack, breaths included\n"
             "\tif shot ~= nil and (shot[5] == 1 or shot[6] == 1) then\n")
TIRED_OLD = "\tally_ammo_low = true,\n"
TIRED_NEW = TIRED_OLD + "\ttired = true,   -- ROUND 152 (user ruling 2026-11-15: \"Foe-Seeker + tired\")\n"
DX_OLD = "FOURTH.ALL_DX = -48          -- left of the wheel's left slot (WHEEL_SLOT[6]), in the ability badges' offset frame\n"
DX_NEW = ("-- ROUND 152: the user's screenshot (2026-11-15) - below the portrait, right of the camera button. The offset was\n"
          "-- calibrated from the top-slot badge (-865,-209) and the bottom-right-slot badge (-799,-37) in that screenshot.\n"
          "FOURTH.ALL_OX, FOURTH.ALL_OY = -880, 8\n")
SLOT_OLD = "\t\t\tlocal slot = WHEEL_SLOT[6]\n"
OFF_OLD = ("\t\t\tst.badge:SetDockOffset(BADGE_X + (slot[1] - WHEEL_TOP_X) + FOURTH.ALL_DX, BADGE_Y + (slot[2] - WHEEL_TOP_Y))\n")
OFF_NEW = "\t\t\tst.badge:SetDockOffset(FOURTH.ALL_OX, FOURTH.ALL_OY)\n"

for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert "blob_not_flying" not in s
    s = cut(s, HOLD_FN_START, HOLD_FN_END, HOLD_FN_NEW)
    if path == SRC:
        s = cut(s, LIVE_HOLD_START, LIVE_HOLD_END, "")
        s = sub(s, SAID, "")
    else:
        s = sub(s, ANN_HOLD, "")
    s = sub(s, LARGE_OLD, LARGE_NEW)
    s = sub(s, RECHK_OLD, RECHK_NEW)
    s = sub(s, ANGLE_OLD, ANGLE_NEW)
    s = sub(s, TIRED_OLD, TIRED_NEW)
    s = sub(s, DX_OLD, DX_NEW)
    s = sub(s, SLOT_OLD, "")
    s = sub(s, OFF_OLD, OFF_NEW)
    assert "blob_large_hold" not in s and "blob_hold_said" not in s and "ALL_DX" not in s
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)
