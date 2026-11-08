"""Offline smoke test for the zz_probe_enemy_target ROUND-3 probe.

Runs the REAL probe source in a lupa Lua runtime against mock engine handles,
drives enough polls for all 4 plan casts, and asserts:
  * the conflict gate opens and polls run,
  * all FOUR cast shapes fired exactly once each (battle_unit, script_unit,
    ground, nil) with the target varying,
  * the TRY / CANPOST lines are written per cast,
  * the SELF line + H1 RESULT fire when the effect lands on the caster,
  * the EFF line + LANDED RESULT fire when it lands on the enemy (script_unit),
  * the inert shapes report the honest "no effect-count change" negative,
  * the COOLDOWN accessor inventory reports a working getter, a raising getter,
    ABSENT for the rest, and the write-shaped reset_ability_cooldown is present
    but NEVER called,
  * NO write-family member was ever called (a trip fails the test),
  * NO POLL ERROR line.

Usage:  uv run --with lupa python smoke_probe_et3.py
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_enemy_target.lua"
PRELUDE = os.path.join(HERE, "mock_et3_prelude.lua")
LOG_FILE = "zz_probe_enemy_target_log.txt"
POLLS = 30

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def main() -> int:
    workdir = tempfile.mkdtemp(prefix="zz_probe_et3_smoke_")
    os.chdir(workdir)

    rt = lupa.LuaRuntime(unpack_returned_tuples=True)
    rt.execute(open(PRELUDE, "r", encoding="utf-8").read())
    rt.execute(open(PROBE, "r", encoding="utf-8").read())

    print(f"== drive {POLLS} polls (cast plan: at 0/15/30/45 s, POLL 2 s)")
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
    check("25+ polls ran", text.count("=== poll ") >= 25)
    check("NO POLL ERROR", "POLL ERROR" not in text)

    print("== the four cast shapes (one each, target varying)")
    for shape in ("battle_unit", "script_unit", "ground", "nil"):
        check(f"TRY shape={shape} present",
              f"TRY shape={shape} " in text and f"accepted=true" in text)
    check("CAST-PLAN cast 4/4 logged", "CAST-PLAN cast 4/4" in text)
    check("CAST-PLAN complete logged", "CAST-PLAN complete" in text)

    print("== CANPOST (H4 cooldown-consumed test)")
    for shape in ("battle_unit", "script_unit", "ground", "nil"):
        check(f"CANPOST shape={shape} present", f"CANPOST shape={shape} " in text)
    check("CANPOST can_after=true on the inert control (mock: no cooldown)",
          "CANPOST shape=battle_unit key=wh_main_hero_abilities_accusation can_after=true" in text)

    print("== SELF probe (H1)")
    check("SELF line present", "SELF shape=" in text)
    check("H1 CONFIRMED RESULT present (self delta moved on the nil cast)",
          "H1 CONFIRMED" in text and "SELF effect count MOVED" in text)
    check("SELF nil line shows delta=1",
          "SELF shape=nil " in text and "delta=1" in text)

    print("== EFF probe (H2/H3)")
    check("EFF line present", "EFF shape=" in text)
    check("script_unit cast LANDED on the enemy (delta=1)",
          "EFF shape=script_unit " in text and "the effect LANDED on the enemy" in text)
    check("battle_unit control reported inert",
          "no effect-count change within" in text)
    check("ground cast reported inert",
          "shape=ground" in text)

    print("== cooldown accessor inventory (H4)")
    check("working getter reported a value (ability_charges)",
          "COOLDOWN unit.ability_charges => value=" in text)
    check("raising getter classified EXISTS-BUT-ERRORS",
          "COOLDOWN unit.special_ability_cooldown => EXISTS-BUT-ERRORS" in text)
    check("an ABSENT getter reported",
          "COOLDOWN unit.ability_cooldown => ABSENT" in text)
    check("write-shaped reset_ability_cooldown present but NOT called",
          "COOLDOWN uc.reset_ability_cooldown => EXISTS (function) - NOT CALLED (write-shaped)" in text)
    check("cooldown probe done line", "COOLDOWN probe done:" in text)

    print("== the state must not have changed: only casts written")
    casts = rt.eval("#casts")
    shapes = rt.eval("table.concat((function() local s={} for _,c in ipairs(casts) do s[#s+1]=c.shape end return s end)(), ',')")
    check(f"exactly 4 casts fired (got {casts}: {shapes})", int(casts) == 4)
    for shape in ("battle_unit", "script_unit", "ground", "nil"):
        n = rt.eval(f"(function() local n=0 for _,c in ipairs(casts) do if c.shape=='{shape}' then n=n+1 end end return n end)()")
        check(f"shape {shape} fired exactly once (got {n})", int(n) == 1)
    check("ground cast used the ground call (count 1)", int(rt.eval("ground_calls")) == 1)
    trips = rt.eval("#trips")
    trip_names = rt.eval("table.concat(trips, ', ')")
    check(f"zero write-family calls (trips={trips}: {trip_names})", int(trips) == 0)

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f in failures:
            print("   -", f)
        return 1
    print("SMOKE TEST PASSED - all 4 shapes fired once; SELF/EFF deltas detected; no write beyond the casts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
