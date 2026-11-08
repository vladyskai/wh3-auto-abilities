"""Offline smoke test for the zz_probe_step THROWAWAY step-probe.

Runs the REAL probe source in a lupa Lua runtime against mock engine handles,
drives enough polls for all 4 capped casts + their sampling windows, and asserts
the whole record shape: gate, BEFORE reads, the movement/order read inventory,
the exhaustive command-event instrument, CAST-PLAN/TRY/ACCEPTED/POSTPOS, the
per-poll SAMPLE lines with deltas, STEP RESULT + the machine-checkable VERDICT,
the refused-cast candidate-5 evidence, and ZERO forbidden writes.

Scenario (driven by mock_step_prelude.lua):
  cast 1 accepted, caster drifts +0.3 m/poll (grows -> full 6 samples),
         engine fires an "Attack Unit" command  -> order_after_attack=y
  cast 2 REFUSED, caster drifts +0.5 m/poll, engine fires a "Move" command
                                              -> refused=y, order_after_move=y
  cast 3 accepted, NO movement                -> all n, moved_total=0.00
  cast 4 accepted, caster already moving      -> already_moving_before=y

Usage:  uv run --with lupa python smoke_probe_step.py
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_step.lua"
PRELUDE = os.path.join(HERE, "mock_step_prelude.lua")
LOG_FILE = "zz_probe_step_log.txt"
POLLS = 34

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def main() -> int:
    workdir = tempfile.mkdtemp(prefix="zz_probe_step_smoke_")
    os.chdir(workdir)

    rt = lupa.LuaRuntime(unpack_returned_tuples=True)
    rt.execute(open(PRELUDE, "r", encoding="utf-8").read())
    src = open(PROBE, "r", encoding="utf-8").read()
    rt.execute(src)

    fn = rt.globals().repeat_fn
    check("probe captured the poll callback (timer registered)", fn is not None)
    if fn is None:
        return 1

    print(f"== drive {POLLS} polls, firing engine command events around the casts")
    prev = 0
    for _ in range(POLLS):
        rt.eval("advance()")
        fn()
        pc = int(rt.eval("perf_calls"))
        if pc > prev:
            if pc == 1:
                rt.execute("fire_cmd('Attack Unit', true, nil)")
            elif pc == 2:
                rt.execute("fire_cmd('Move', true, nil)")
            elif pc == 3:
                rt.execute("caster_is_moving = true")
            prev = pc

    log_path = os.path.join(workdir, LOG_FILE)
    check("probe wrote its own log file", os.path.exists(log_path))
    text = open(log_path, "r", encoding="utf-8", errors="replace").read()

    print("== gate + polling")
    check("conflict phase ENTERED logged", "GATE conflict phase ENTERED" in text)
    check("polls ran", text.count("=== poll ") >= 25)
    check("NO POLL ERROR", "POLL ERROR" not in text)

    print("== the exhaustive command-event instrument")
    check("command listeners registered 26/26",
          "command listeners registered: 26/26" in text)
    check("the source registers all command families (incl. Attack Unit / Move / Special Ability)",
          '"Special Ability"' in src and '"Attack Unit"' in src and '"Move"' in src
          and '"Halt"' in src and '"Battle Results"' in src)
    check("engine 'Attack Unit' command logged", "CMD tick=1 name=Attack Unit" in text)
    check("engine 'Move' command logged", "CMD tick=" in text and "name=Move " in text)

    print("== the movement/order read inventory")
    check("READ unit.is_moving line", "READ unit.is_moving =>" in text)
    check("READ unit.ordered_position line", "READ unit.ordered_position =>" in text)
    check("READ unit.is_moving_fast line", "READ unit.is_moving_fast =>" in text)
    check("READ unit.slow_speed line", "READ unit.slow_speed =>" in text)
    check("READ script_unit.has_moved line", "READ script_unit.has_moved =>" in text)
    check("an ABSENT line lists the names that do not exist",
          "ABSENT (" in text and "is_charging" in text)
    check("a write-shaped member guard exists in the source",
          "NOT CALLED (write-shaped)" in src and "P.is_write" in src)

    print("== the BEFORE record")
    check("BEFORE cast=1 line", "BEFORE cast=1 " in text)
    check("BEFORE carries edge-to-edge unit_distance",
          "unit_distance=" in text and "edge-to-edge" in text)
    check("BEFORE carries both melee flags + missile state",
          "caster_in_melee=" in text and "target_in_melee=" in text
          and "target_under_missile=" in text)

    print("== the cast record (CAST-PLAN / TRY / ACCEPTED / POSTPOS)")
    for n in (1, 2, 3, 4):
        check(f"CAST-PLAN cast={n}", f"CAST-PLAN cast={n} " in text)
        check(f"TRY cast={n}", f"TRY cast={n} " in text)
        check(f"ACCEPTED cast={n}", f"ACCEPTED cast={n} " in text)
        check(f"POSTPOS cast={n} (immediate same-tick re-read)",
              f"POSTPOS cast={n} " in text)
    check("ACCEPTED cast=2 accepted=false (the refusal)", "ACCEPTED cast=2 accepted=false" in text)
    check("REFUSED cast=2 logged (candidate-5 evidence)", "REFUSED cast=2" in text)

    print("== the per-poll sampler")
    check("SAMPLING cast=1 begins", "SAMPLING cast=1 " in text)
    check("SAMPLE lines carry delta_from_pre + step_delta",
          "delta_from_pre=" in text and "step_delta=" in text)
    check("SAMPLE cast=1 reaches the full 6 polls", "SAMPLE cast=1 n=6/6" in text)

    print("== STEP RESULT + the machine-checkable VERDICT")
    for n in (1, 2, 3, 4):
        check(f"STEP RESULT cast={n}", f"STEP RESULT cast={n} " in text)
        check(f"VERDICT cast={n}", f"VERDICT cast={n} " in text)
    check("VERDICT cast=1 order_after_attack=y",
          "VERDICT cast=1 moved_total=" in text and "order_after_attack=y" in text)
    check("VERDICT cast=1 not refused",
          "VERDICT cast=1" in text and "refused=n" in text)
    check("VERDICT cast=2 refused=y order_after_move=y",
          "order_after_move=y" in text and "VERDICT cast=2" in text)
    import re
    v2 = re.search(r"VERDICT cast=2 .*", text)
    check("cast=2 line shows refused=y", bool(v2) and "refused=y" in v2.group(0))
    v3 = re.search(r"VERDICT cast=3 .*", text)
    check("cast=3 shows moved_total=0.00 and no orders",
          bool(v3) and "moved_total=0.00" in v3.group(0)
          and "order_after_attack=n" in v3.group(0)
          and "order_after_move=n" in v3.group(0))
    v4 = re.search(r"VERDICT cast=4 .*", text)
    check("cast=4 shows already_moving_before=y",
          bool(v4) and "already_moving_before=y" in v4.group(0))
    check("cast=2 orders_seen names the engine Move",
          bool(re.search(r"STEP RESULT cast=2 .*orders_seen=.*Move", text)))

    print("== no state changed beyond the casts")
    trips = int(rt.eval("#trips"))
    names = rt.eval("table.concat(trips, ', ')")
    check(f"zero forbidden writes (trips={trips}: {names})", trips == 0)
    check("exactly 4 cast attempts (perf_calls)", int(rt.eval("perf_calls")) == 4)

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f in failures:
            print("   -", f)
        return 1
    print("SMOKE TEST PASSED - 4 casts, refused arm, deltas, orders and the "
          "VERDICT lines all recorded; zero forbidden writes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
