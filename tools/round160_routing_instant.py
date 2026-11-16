#!/usr/bin/env python3
"""Round 160 (harness 159): two fixes from the 2026-11-16 Beastmen battle (user ruling 2026-11-16: "Yes, fix it and
also the abilities that activate instantly (no casting time) do not need to trigger the 2.5 wait").

  1. when_ready (the 21 Winds of Magic abilities) skips a ROUTING unit, like every other family. Field: Jagged Dagger
     was "accepted" 6 times in 11 s while the Bray-Shaman fled (a routing unit cannot cast).
  2. The per-unit serialisation window: an entry with NO wind-up in any of its keys (cast_gate.wind_up_s, which lists
     exactly the game's 258 keys with wind_up_time > 0) holds the unit for ONE poll only (FOURTH.SERIAL_INSTANT_HOLD
     _SECONDS = POLL_MS), so a second order never lands in the same tick (the engine replaces a same-tick order).
     An entry WITH a wind-up keeps wind-up + 2 s, never less than 2.5 s (the round-107 Moondial evidence). Field: the
     Wargor's Deadly Onslaught (instant) took the charge and held Potion of Speed (instant) for 2.5 s, past the charge.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"


def sub(s, a, b, n=1):
    assert s.count(a) == n, (a[:80], s.count(a))
    return s.replace(a, b)


CONST_OLD = "FOURTH.SERIAL_MIN_HOLD_SECONDS = 2.5\n"
CONST_NEW = CONST_OLD + (
    "-- ROUND 160 (user ruling 2026-11-16): an INSTANT ability (no wind_up_time in any of its keys) holds the unit for\n"
    "-- ONE poll only - never two orders in the same tick (the engine replaces a same-tick order); the 2.5 s minimum\n"
    "-- above protects the abilities WITH a wind-up (the round-107 Moondial evidence: a 3 s wind-up was replaced)\n"
    "FOURTH.SERIAL_INSTANT_HOLD_SECONDS = POLL_MS / 1000\n")
GATE_OLD = ("\t\t\t\t\tif unit_hold_s < FOURTH.SERIAL_MIN_HOLD_SECONDS then\n"
            "\t\t\t\t\t\tunit_hold_s = FOURTH.SERIAL_MIN_HOLD_SECONDS\n"
            "\t\t\t\t\tend\n")
GATE_NEW = GATE_OLD + ("\t\t\t\t\t-- ROUND 160: an instant ability (no wind-up) holds the unit for one poll only\n"
                       "\t\t\t\t\tif ability.wind_up_s == nil then\n"
                       "\t\t\t\t\t\tunit_hold_s = FOURTH.SERIAL_INSTANT_HOLD_SECONDS\n"
                       "\t\t\t\t\tend\n")
LOG_OLD = ('\t\tlog("  per-unit cast gate armed by " .. ability.marker .. ": no OTHER ability on unit "\n'
           '\t\t\t.. tostring(ui_id) .. " may be issued for " .. tostring(unit_hold_s)\n'
           '\t\t\t.. "s (wind-up + " .. tostring(IN_FLIGHT_SETTLE_SECONDS) .. "s, min "\n'
           '\t\t\t.. tostring(FOURTH.SERIAL_MIN_HOLD_SECONDS) .. "s)") \n')
LOG_NEW = ('\t\tlog("  per-unit cast gate armed by " .. ability.marker .. ": no OTHER ability on unit "\n'
           '\t\t\t.. tostring(ui_id) .. " may be issued for " .. tostring(unit_hold_s)\n'
           '\t\t\t.. ((ability.wind_up_s == nil) and "s (instant: one poll)" or ("s (wind-up + "\n'
           '\t\t\t.. tostring(IN_FLIGHT_SETTLE_SECONDS) .. "s, min "\n'
           '\t\t\t.. tostring(FOURTH.SERIAL_MIN_HOLD_SECONDS) .. "s)"))) \n')
WR_LIVE_OLD = ('function FOURTH.evaluate_when_ready(unit, routing)\n'
               '\treturn "when ready (Winds of Magic), cast on self"\n'
               'end\n')
WR_LIVE_NEW = ('function FOURTH.evaluate_when_ready(unit, routing)\n'
               '\t-- ROUND 160: a routing unit cannot cast (field 2026-11-16: Jagged Dagger "accepted" 6 times in 11 s\n'
               '\t-- while its Bray-Shaman fled)\n'
               '\tif routing then return nil end\n'
               '\treturn "when ready (Winds of Magic), cast on self"\n'
               'end\n')
WR_ANN_OLD = ('function FOURTH.evaluate_when_ready(unit, routing)\n'
              '\treturn true\n'
              'end\n')
WR_ANN_NEW = ('function FOURTH.evaluate_when_ready(unit, routing)\n'
              '\t-- ROUND 160: a routing unit cannot cast\n'
              '\tif routing then return false end\n'
              '\treturn true\n'
              'end\n')

for path, live in ((SRC, True), (ANN, False)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "SERIAL_INSTANT_HOLD_SECONDS" not in s
    s = sub(s, CONST_OLD, CONST_NEW)
    s = sub(s, GATE_OLD, GATE_NEW)
    if live:
        s = sub(s, LOG_OLD, LOG_NEW)
        s = sub(s, WR_LIVE_OLD, WR_LIVE_NEW)
    else:
        s = sub(s, WR_ANN_OLD, WR_ANN_NEW)
    assert s.find("local POLL_MS = 250") < s.find("FOURTH.SERIAL_INSTANT_HOLD_SECONDS = POLL_MS / 1000")
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)
