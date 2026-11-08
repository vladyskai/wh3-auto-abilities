"""Offline smoke test for the zz_probe_ui_text probe.

Runs the REAL probe source in a lupa Lua runtime against a mock UI tree and
asserts:
  (1) the walk is CAPPED (visit cap bites on a wide tree; depth cap hides the
      too-deep node);
  (2) the walk is PCALL-WALLED (a component whose tostring raises is skipped and
      the walk continues; per-read errors are recorded as <ERR>);
  (3) text/state/property reads are ATTEMPTED and RECORDED, and a rendered stat
      value ("Base value: 53") is flagged ***STAT-LIKE***;
  (4) the named-root / FindByScriptTag / SequentialFind paths and the
      default-sweep unit-card path all run;
  (5) the pass cap bites; the periodic callback is registered at 30 s;
  (6) NO setter was ever called.

Usage:  uv run --with lupa python lua_smoke_ui_probe.py
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
PRELUDE = os.path.join(HERE, "mock_ui_prelude.lua")
LOG_FILE = "zz_probe_ui_text_log.txt"

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def main() -> int:
    workdir = tempfile.mkdtemp(prefix="zz_probe_ui_smoke_")
    os.chdir(workdir)

    rt = lupa.LuaRuntime(unpack_returned_tuples=True)
    rt.execute(open(PRELUDE, "r", encoding="utf-8").read())
    rt.execute(open(PROBE, "r", encoding="utf-8").read())

    log_path = os.path.join(workdir, LOG_FILE)

    def text():
        return open(log_path, "r", encoding="utf-8", errors="replace").read()

    print("== the periodic safety callback is registered")
    pf = rt.globals().periodic_fn
    check("periodic_fn captured (bm:repeat_callback ran at load)", pf is not None)
    check("periodic interval is 30000 ms", rt.globals().periodic_ms == 30000)
    check("periodic name is zz_probe_ui_text_poll",
          rt.globals().periodic_name == "zz_probe_ui_text_poll")

    print("== load proof + periodic pass")
    check("probe wrote its own log file", os.path.exists(log_path))
    check("load line present", "loaded from script/battle/mod/ (auto-load proof)" in text())
    check("own log name in the log", LOG_FILE in text())
    if pf is not None:
        pf()
    check("periodic pass logged", "(periodic)" in text())

    print("\n== default sweep (zz_probe_ui)")
    res = rt.globals().zz_probe_ui()
    print("   zz_probe_ui() ->", res)
    check("hook reports a pass was requested", "pass requested" in res)
    t = text()
    check("hud_battle root walked", "root 'hud_battle' exists" in t)
    check("unit_information root walked", "root 'unit_information' exists" in t)
    check("tooltip_ai_stats_modifier root walked",
          "root 'tooltip_ai_stats_modifier' exists" in t)
    check("unit-card subtree found by unique_ui_id",
          "unit-card subtree 'card:101' exists" in t)

    print("== every read is attempted and recorded")
    check("a component line carries id=",
          'id="stat_melee_defence"' in t)
    check("GetStateText text recorded",
          'stext="Melee Defence"' in t)
    check("GetTooltipText recorded",
          'tip="Base value: 53"' in t)
    check("GetProperty probes recorded (props{...})", "props{" in t)
    check("GetProperty('armour') answered", "armour=53" in t)
    check("Visible/VisibleFromRoot/Position recorded",
          "vis=true vfr=true pos=(11,22)" in t)

    print("== a rendered stat is FLAGGED")
    check("STAT-LIKE tip flag ('Base value')",
          "***STAT-LIKE tip (contains 'Base value')***" in t)
    check("the tooltip's full text is recorded (Base value / Hold the Line)",
          "Base value: 53 / Hold the Line!: 5" in t)
    check("STAT-LIKE prop flag (digit property)",
          "***STAT-LIKE prop armour (contains a digit)***" in t)
    check("NAME hint flag for a stat-named component", "<<NAME~stat>>" in t)
    check("NAME hint flag for a tooltip-named component", "<<NAME~tooltip>>" in t)

    print("== the walk is PCALL-WALLED")
    check("hostile component skipped without aborting the walk",
          "component raised - skipped" in t)
    check("the component AFTER the hostile one was still logged",
          'id="after_hostile"' in t)
    check("a raising GetStateText is recorded as <ERR>, not fatal",
          "stext=<ERR>" in t)
    check("a raising GetTooltipText is recorded as <ERR>", "tip=<ERR>" in t)
    check("a raising GetProperty is recorded as <ERR>", "armour=<ERR>" in t)

    print("== the walk is DEPTH-capped (MAX_DEPTH)")
    check("node at the depth limit is logged", 'id="deep_9"' in t)
    check("node beyond the depth limit is NOT logged", 'id="too_deep"' not in t)

    print("\n== the walk is VISIT-capped (zz_probe_ui('big_root'))")
    rt.globals().zz_probe_ui("big_root")
    check("visit cap reached on the wide tree", "VISIT CAP reached" in text())

    print("== named-root resolution paths")
    r1 = rt.globals().zz_probe_ui("hud_battle")
    check("named root found via root:Find",
          "root 'hud_battle' FOUND via root:Find" in text())
    rt.globals().zz_probe_ui("no_such_thing")
    check("absent root reported NOT FOUND",
          "root 'no_such_thing' NOT FOUND" in text())

    print("\n== status + help")
    st = rt.globals().zz_probe_ui_status()
    check("status names the pass count", "passes=" in st)
    hp = rt.globals().zz_probe_ui_help()
    check("help names the log file", LOG_FILE in hp)

    print("\n== the pass CAP bites")
    capped = None
    for _ in range(30):
        r = rt.globals().zz_probe_ui()
        if "no pass run" in r:
            capped = r
            break
    check("a call eventually reports 'no pass run' (cap reached)", capped is not None)
    check("the log records CAP reached", "CAP reached" in text())

    print("\n== the UI must not have been mutated: no setter was ever called")
    trips = rt.eval("#trips")
    names = rt.eval("table.concat(trips, ', ')")
    check(f"zero setter calls (trips={trips}: {names})", trips == 0)

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f in failures:
            print("   -", f)
        return 1
    print("SMOKE TEST PASSED - capped, pcall-walled, reads attempted and recorded, "
          "stat value flagged, no setter called.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
