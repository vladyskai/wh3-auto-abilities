"""Offline smoke test for the zz_probe_unit_reads round-2 probe.

Runs the REAL probe source in a lupa Lua runtime against mock engine handles and
asserts:
  (1) the classifier actually produces WORKS / EXISTS-BUT-ERRORS / ABSENT,
  (2) the presence-only inventory reports the setter family as EXISTS WITHOUT
      calling it,
  (3) NO write-prefixed member is EVER CALLED (a call trips the mock; any trip
      fails the test),
  (4) the double-sample second read fires from the captured one-shot callback.

Usage:  uv run --with lupa python lua_smoke_probe.py
"""
import os
import sys
import tempfile

import lupa

PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_unit_reads.lua"
PRELUDE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_probe_prelude.lua")
LOG_FILE = "zz_probe_unit_reads_log.txt"

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def main() -> int:
    workdir = tempfile.mkdtemp(prefix="zz_probe_smoke_")
    os.chdir(workdir)

    rt = lupa.LuaRuntime(unpack_returned_tuples=True)
    rt.execute(open(PRELUDE, "r", encoding="utf-8").read())
    rt.execute(open(PROBE, "r", encoding="utf-8").read())

    print("== drive one pass (zz_probe_now)")
    res = rt.globals().zz_probe_now()
    print("   zz_probe_now ->", res)

    log_path = os.path.join(workdir, LOG_FILE)
    check("probe wrote its own log file", os.path.exists(log_path))
    text = open(log_path, "r", encoding="utf-8", errors="replace").read()

    print("== classifier vocabulary")
    check("WORKS verdict present", "WORKS | value=" in text)
    check("EXISTS-BUT-ERRORS verdict present", "EXISTS-BUT-ERRORS | err=" in text)
    check("ABSENT verdict present (health_percent)",
          "health_percent -> ABSENT" in text)
    check("is_crumbling classified EXISTS-BUT-ERRORS",
          "is_crumbling -> EXISTS-BUT-ERRORS" in text)

    print("== round-2 new reads")
    check("unary_of_men_alive WORKS", "unary_of_men_alive -> WORKS" in text)
    check("slow_speed WORKS", "slow_speed -> WORKS" in text)
    check("is_under_missile_attack WORKS", "is_under_missile_attack -> WORKS" in text)
    check("is_under_attack probed on script_unit (EXISTS-BUT-ERRORS)",
          "is_under_attack -> EXISTS-BUT-ERRORS" in text)
    check("unit_in_range dump signature logged",
          "unit_in_range dump signature" in text)
    check("unit_in_range(own battle_unit) WORKS",
          "unit_in_range(own battle_unit) -> WORKS" in text)
    check("unit_in_range(own position) EXISTS-BUT-ERRORS",
          "unit_in_range(own position) -> EXISTS-BUT-ERRORS" in text)
    check("winds_of_magic_current WORKS (on army)",
          "winds_of_magic_current -> WORKS" in text)
    check("winds_of_magic_remaining_recharge_rate WORKS (on army)",
          "winds_of_magic_remaining_recharge_rate -> WORKS" in text)
    check("current_battle_speed WORKS (on battle)",
          "current_battle_speed -> WORKS" in text)

    print("== presence-only write inventory (reported, never called)")
    for name in ("heal_hitpoints_unary", "reduce_hitpoints_unary",
                 "set_current_ammo_unary", "modify_winds_of_magic_current"):
        check(f"{name} EXISTS (function) - NOT CALLED",
              f"{name} -> EXISTS (function) - NOT CALLED" in text)
    for name in ("modify_ammo", "refill_ammo", "grant_infinite_ammo"):
        check(f"{name} EXISTS on script_unit - NOT CALLED",
              f"{name} -> EXISTS (function) - NOT CALLED" in text)
    for name in ("change_fatigue_amount", "change_move_speed"):
        check(f"{name} EXISTS on battle_unitcontroller - NOT CALLED",
              f"{name} -> EXISTS (function) - NOT CALLED" in text)

    print("== double-sample (2nd read via the captured one-shot callback)")
    check("double-sample #1 logged", "#1 (t0):" in text)
    second_fn = rt.globals().second_fn
    check("one-shot callback captured by mock", second_fn is not None)
    if second_fn is not None:
        second_fn()
    text2 = open(log_path, "r", encoding="utf-8", errors="replace").read()
    check("double-sample #2 logged (~10 s later)", "#2 (~10.0 s later):" in text2)

    print("== the state must not have changed: no write was ever called")
    trips = rt.eval("#trips")
    trip_names = rt.eval("table.concat(trips, ', ')")
    check(f"zero write-family calls (trips={trips}: {trip_names})", trips == 0)
    check("ground-cast probe ran exactly once (pass 1)",
          rt.eval("ground_calls") == 1)

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f in failures:
            print("   -", f)
        return 1
    print("SMOKE TEST PASSED - classifier vocabulary ok; no write-family member was ever called.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
