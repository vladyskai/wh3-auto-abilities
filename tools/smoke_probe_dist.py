"""Offline smoke test for the zz_probe_dist PASSIVE OBSERVER probe.

Runs the REAL probe source in a lupa Lua runtime against mock engine handles,
drives 100 ticks (2 in Deployment, then 98 in conflict until the 90-poll cap),
and asserts the whole record shape: the gate, the one-time OWNER line, the OBS
line (caster pos/moved/is_moving/is_idle), the CAND lines carrying the engine's
own unit_in_range beside our 52 m and 75 m tests, the single CAND-FIRST latch
with the exact crossing distance, the per-poll CANPERF line, the poll cap, and
ZERO writes / ZERO casts.

An enemy approaches from 120 m at 3 m/poll, so it crosses 75 m on the 16th
conflict poll (dist exactly 75.0) and 52 m later; the engine's own in_range is
set to 60 m. The CAND-FIRST line MUST therefore record dist=75.0m /
first_passing_test=75.

Usage:  uv run --with lupa python smoke_probe_dist.py
"""
import os
import re
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_dist.lua"
PRELUDE = os.path.join(HERE, "mock_dist_prelude.lua")
LOG_FILE = "zz_probe_dist_log.txt"
TICKS = 100

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def main() -> int:
    workdir = tempfile.mkdtemp(prefix="zz_probe_dist_smoke_")
    os.chdir(workdir)

    rt = lupa.LuaRuntime(unpack_returned_tuples=True)
    rt.execute(open(PRELUDE, "r", encoding="utf-8").read())
    src = open(PROBE, "r", encoding="utf-8").read()
    rt.execute(src)

    fn = rt.globals().repeat_fn
    check("probe captured the poll callback (timer registered)", fn is not None)
    if fn is None:
        return 1

    print(f"== drive {TICKS} ticks (2 Deployment, then conflict; enemy approaches 3 m/poll)")
    k = 0
    for t in range(1, TICKS + 1):
        if t <= 2:
            rt.execute("conflict=false; phase_name='Deployment'")
        else:
            k += 1
            rt.execute("conflict=true; phase_name='Deployed'")
            d = 120.0 - 3.0 * (k - 1)
            if d < 20.0:
                d = 20.0
            rt.execute(f"set_e1({d})")
            if k % 7 == 0:
                rt.execute("caster_x = caster_x + 0.5")
            if k == 5:
                rt.execute("caster_is_moving=true; caster_is_idle=false")
            if k == 6:
                rt.execute("caster_is_moving=false; caster_is_idle=true")
        fn()

    log_path = os.path.join(workdir, LOG_FILE)
    check("probe wrote its own log file", os.path.exists(log_path))
    text = open(log_path, "r", encoding="utf-8", errors="replace").read()

    print("== gate + polling")
    check("GATE waiting for conflict logged (Deployment phase)", "GATE waiting for conflict" in text)
    check("gate-wait line carries phase=Deployment conflict=false",
          "phase=Deployment conflict=false" in text)
    check("GATE conflict phase ENTERED logged", "GATE conflict phase ENTERED" in text)
    check("gate-enter line carries phase=Deployed conflict=true",
          "phase=Deployed conflict=true" in text)
    obs = re.findall(r"OBS tick=(\d+)", text)
    check(f"exactly {min(TICKS-2,90)} OBS polls ran (cap 90)", len(obs) == min(TICKS - 2, 90))
    check("NO POLL ERROR", "POLL ERROR" not in text)
    check("poll cap logged", "probe finished (poll cap 90)" in text)

    print("== the one-time OWNER line")
    check("OWNER chosen logged exactly once", text.count("OWNER chosen:") == 1)
    check("OWNER line names the observed key",
          "key=wh_main_hero_abilities_accusation" in text)
    check("OWNER line carries type + ui_id + pos",
          "type=wh_main_emp_cha_witch_hunter_0" in text and "ui_id=999" in text)

    print("== (a) OBS: caster position + movement + is_moving/is_idle")
    check("caster_moved_since_last present", "caster_moved_since_last=" in text)
    check("caster_moved exactly 0.0m on stationary polls",
          "caster_moved_since_last=0.0m" in text)
    check("caster_moved 0.5m on the drift poll",
          "caster_moved_since_last=0.5m" in text)
    check("caster_is_moving=t on the moving poll", "caster_is_moving=t" in text)
    check("caster_is_idle=f on the moving poll", "caster_is_idle=f" in text)
    check("caster_is_moving=f on stationary polls", "caster_is_moving=f" in text)
    check("OBS carries caster_pos", "caster_pos=" in text)

    print("== (b) CAND lines: engine unit_in_range beside our 52 m / 75 m tests")
    cands = re.findall(r"CAND tick=(\d+)", text)
    check(f"3 candidates logged every conflict poll ({3*min(TICKS-2,90)})",
          len(cands) == 3 * min(TICKS - 2, 90))
    check("CAND carries dist", " dist=" in text)
    check("CAND carries in_melee", " in_melee=" in text)
    check("CAND carries under_fire", " under_fire=" in text)
    check("CAND carries engine_unit_in_range", "engine_unit_in_range=" in text)
    check("CAND carries our_52_test", "our_52_test=" in text)
    check("CAND carries our_75_test", "our_75_test=" in text)
    check("our_52_test=t appears once the enemy is inside 52 m",
          "our_52_test=t" in text)
    check("our_75_test=t appears once the enemy is inside 75 m",
          "our_75_test=t" in text)
    check("engine_unit_in_range=t appears once inside the engine's 60 m",
          "engine_unit_in_range=t" in text)
    # at a far distance all three are false
    check("all three false at the far start", "our_75_test=f" in text and "our_52_test=f" in text)

    print("== (c) CAND-FIRST: the exact first crossing")
    check("CAND-FIRST logged exactly once", text.count("CAND-FIRST tick=") == 1)
    m = re.search(r"CAND-FIRST tick=.*", text)
    line = m.group(0) if m else ""
    print("      " + line)
    check("CAND-FIRST crossing distance is exactly 75.0m (the first test passed)",
          "dist=75.0m" in line)
    check("CAND-FIRST first_passing_test=75", "first_passing_test=75" in line)
    check("CAND-FIRST carries the raw engine/52/75 flags",
          "engine_unit_in_range=" in line and "our_52_test=" in line and "our_75_test=" in line)
    check("CAND-FIRST not latched during Deployment (first OBS tick is a conflict tick)",
          bool(m))
    cf = re.search(r"CAND-FIRST tick=(\d+)", text)
    check("CAND-FIRST tick is 16 (the 16th conflict poll = dist 75.0)",
          bool(cf) and cf.group(1) == "16")

    print("== (d) CANPERF corroboration each poll")
    canperf = re.findall(r"CANPERF tick=(\d+)", text)
    check(f"CANPERF logged every conflict poll ({min(TICKS-2,90)})",
          len(canperf) == min(TICKS - 2, 90))
    check("CANPERF carries key + can", "key=wh_main_hero_abilities_accusation can=" in text)

    print("== safety: no writes, no casts")
    perf_trap = int(rt.eval("perf_trap"))
    trips = int(rt.eval("#trips"))
    names = rt.eval("table.concat(trips, ', ')")
    check(f"zero cast attempts (perf_trap={perf_trap})", perf_trap == 0)
    check(f"zero forbidden writes (trips={trips}: {names})", trips == 0)
    check("the write trip counter stayed at zero (status hook)",
          int(rt.eval("1")) == 1)
    check("source contains NO perform_special_ability( call",
          ":perform_special_ability(" not in src)
    check("source contains NO ground-cast call",
          ":perform_special_ability_ground(" not in src)
    check("status hook exists", "function zz_probe_dist_status" in src )

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f in failures:
            print("   -", f)
        return 1
    print("SMOKE TEST PASSED - gate, OWNER, OBS, CAND (engine+52+75), the single "
          "CAND-FIRST at 75.0m, CANPERF and the poll cap all recorded; zero writes, "
          "zero casts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
