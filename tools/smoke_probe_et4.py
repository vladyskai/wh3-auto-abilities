"""Offline smoke test for the zz_probe_enemy_target ROUND-4 probe.

Runs the REAL probe source in a lupa Lua runtime against mock engine handles,
drives enough polls for all 6 route casts, and asserts:
  * the conflict gate opens and polls run,
  * all SIX routes fired exactly once each (bench_fresh, queued_q, army_use,
    take_control, attack_then_cast, in_range_cast),
  * the distinct engine entry points were used (4x perform_special_ability,
    1x perform_special_ability_q, 1x battle_army:use_special_ability),
  * the take_control / release_control / attack_unit ORDERS were issued exactly
    once each (the two legitimisation routes),
  * a RESULT landed=yes line (ENEMY effect count moved) AND a RESULT landed=no
    line (inert) BOTH appear, and the SELF delta moved on the take_control route,
  * the in_range_cast DEFER path ran once before it fired (in_range=yes),
  * the "Special Ability" command-event listener was registered and fired,
  * the cooldown accessor inventory still reports no live cooldown read,
  * ZERO forbidden writes were called (a trip fails the test),
  * NO POLL ERROR line.

Usage:  uv run --with lupa python smoke_probe_et4.py
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_enemy_target.lua"
PRELUDE = os.path.join(HERE, "mock_et4_prelude.lua")
LOG_FILE = "zz_probe_enemy_target_log.txt"
POLLS = 70

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def main() -> int:
    workdir = tempfile.mkdtemp(prefix="zz_probe_et4_smoke_")
    os.chdir(workdir)

    rt = lupa.LuaRuntime(unpack_returned_tuples=True)
    rt.execute(open(PRELUDE, "r", encoding="utf-8").read())
    rt.execute(open(PROBE, "r", encoding="utf-8").read())

    print(f"== drive {POLLS} polls (routes at 0/15/30/45/60/75 s, POLL 2 s)")
    fn = rt.globals().repeat_fn
    check("probe captured the poll callback (timer registered)", fn is not None)
    if fn is None:
        return 1
    for _ in range(POLLS):
        fn()

    log_path = os.path.join(workdir, LOG_FILE)
    check("probe wrote its own log file", os.path.exists(log_path))
    text = open(log_path, "r", encoding="utf-8", errors="replace").read()

    print("== gate + polling")
    check("conflict phase ENTERED logged", "GATE conflict phase ENTERED" in text)
    check("60+ polls ran", text.count("=== poll ") >= 60)
    check("NO POLL ERROR", "POLL ERROR" not in text)

    print("== the six routes fired (each labelled, one cast each)")
    for label in ("bench_fresh", "queued_q", "army_use",
                  "take_control", "attack_then_cast", "in_range_cast"):
        check(f"TRY route={label} present",
              f"TRY route={label} " in text)
    check("6 CAST lines logged", text.count("CAST route=") == 6)
    check("ROUTES complete logged", "ROUTES complete" in text)

    print("== the distinct engine entry points")
    check("4 perform_special_ability calls", int(rt.eval("perf_calls")) == 4)
    check("1 perform_special_ability_q call", int(rt.eval("q_calls")) == 1)
    check("1 battle_army:use_special_ability call", int(rt.eval("army_calls")) == 1)

    print("== the legitimisation orders (counted, not forbidden writes)")
    check("take_control issued once", int(rt.eval("take_control_calls")) == 1)
    check("release_control issued once", int(rt.eval("release_control_calls")) == 1)
    check("attack_unit issued once", int(rt.eval("attack_unit_calls")) == 1)
    check("ORDER lines logged", text.count("ORDER route=") == 3)

    print("== CANPOST (cooldown-consumed test) per route")
    for label in ("bench_fresh", "queued_q", "army_use",
                  "take_control", "attack_then_cast", "in_range_cast"):
        check(f"CANPOST route={label} present", f"CANPOST route={label} " in text)

    print("== SELF / EFF / RESULT signal")
    check("SELF line present", "SELF route=" in text)
    check("EFF line present", "EFF route=" in text)
    check("a RESULT landed=yes line", "RESULT route=" in text and "landed=yes" in text)
    check("a RESULT landed=no line (an inert route)", "landed=no" in text)
    check("ENEMY effect-count LANDED reported", "the ENEMY-targeted effect LANDED" in text)
    check("SELF application reported (take_control self-move)",
          "the CASTER's effect count moved" in text)
    check("landed=yes appears on queued_q", "RESULT route=queued_q landed=yes" in text)
    check("landed=yes appears on in_range_cast", "RESULT route=in_range_cast landed=yes" in text)
    check("landed=no appears on bench_fresh", "RESULT route=bench_fresh landed=no" in text)

    print("== the in_range_cast defer path")
    check("defer line logged once", text.count("deferring: enemy out of the ability's reach") == 1)
    check("in_range=yes note logged", "in_range=yes" in text)

    print("== the command-event instrument")
    check("listener registered=true", "command listener 'Special Ability' registered=true" in text)
    check("CMD event fired", "CMD event=SpecialAbility" in text)

    print("== cooldown accessor inventory (kept evidence)")
    check("working getter reported a value (ability_charges)",
          "COOLDOWN unit.ability_charges => value=" in text)
    check("raising getter classified EXISTS-BUT-ERRORS",
          "COOLDOWN unit.special_ability_cooldown => EXISTS-BUT-ERRORS" in text)
    check("write-shaped reset_ability_cooldown present but NOT called",
          "COOLDOWN uc.reset_ability_cooldown => EXISTS (function) - NOT CALLED (write-shaped)" in text)

    print("== no state changed beyond the casts + the route orders")
    trips = rt.eval("#trips")
    trip_names = rt.eval("table.concat(trips, ', ')")
    check(f"zero forbidden writes (trips={trips}: {trip_names})", int(trips) == 0)
    check("no ground cast fired (round-4 has no ground route)",
          int(rt.eval("ground_calls")) == 0)
    total = int(rt.eval("#casts"))
    check(f"exactly 6 cast records (got {total})", total == 6)

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f in failures:
            print("   -", f)
        return 1
    print("SMOKE TEST PASSED - all 6 routes fired; landed=yes|no deltas detected; "
          "orders counted; zero forbidden writes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
