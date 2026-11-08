"""Offline smoke test for the ROUND-4 zz_probe_ui_text probe (TARGETED STAT DUMP).

Runs the REAL probe source in a lupa Lua runtime against a MUTABLE mock UI tree
and asserts the round-4 contract, WITHOUT loosening the round-3 one (the
round-3 capture is exercised at the end):

  (1) no stat dump while the stat components are hidden / the HUD is empty;
  (2) a CcoUnitStat* component becoming VISIBLE (the panel opened) triggers ONE
      full dump, and only one - unchanged polls re-dump nothing;
  (3) a CHANGE of the visible-stat set re-dumps;
  (4) the dump walks DEEPER than the round-3 walk (a depth-20 node is logged, a
      depth-21 node is not) and with NO change-filtering (the same component is
      logged again when the root is dumped twice);
  (5) the dump logs id/state/GetStateText/GetTooltipText/Visible/VisibleFromRoot/
      Position/Bounds/GetImagePath and flags digits ***STAT-LIKE***;
  (6) the manual hooks zz_probe_stat_dump() and zz_probe_stat_dump('root id')
      work and log a clear header naming the trigger and the root;
  (7) the visit cap (3000) holds and speaks;
  (8) no UI-state setter is ever called (trips == 0);
  (9) the round-3 mouse-armed capture still arms.

Usage:  cd <this dir> && uv run --with lupa python lua_smoke_ui_probe_v4.py
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
PRELUDE = os.path.join(HERE, "mock_ui_prelude_v4.lua")
LOG_FILE = "zz_probe_ui_text_log.txt"

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def main() -> int:
    workdir = tempfile.mkdtemp(prefix="zz_probe_ui_smoke4_")
    os.chdir(workdir)

    rt = lupa.LuaRuntime(unpack_returned_tuples=True)
    rt.execute(open(PRELUDE, "r", encoding="utf-8").read())
    rt.execute(open(PROBE, "r", encoding="utf-8").read())

    G = rt.globals()
    M = G.M
    M.local_units = rt.table("1001", "1002")
    log_path = os.path.join(workdir, LOG_FILE)

    def text():
        return open(log_path, "r", encoding="utf-8", errors="replace").read()

    def count(sub):
        return text().count(sub)

    def n_dumps():
        return count("STAT DUMP #")

    def tick(n=1):
        for _ in range(n):
            G.poll_fn()

    def tick_until(pred, max_ticks=3000, chunk=10):
        done = 0
        while done < max_ticks:
            tick(chunk)
            done += chunk
            if pred():
                return True
        return pred()

    print("== static source tokens (round 4)")
    SRC = open(PROBE, encoding="utf-8", errors="replace").read()
    for tok in ("round 4: targeted stat dump",
                "zz_probe_stat_dump", "zz_probe_stat_status", "zz_probe_stat_help",
                "STAT_MAX_DEPTH    = 20", "STAT_MAX_VISITS   = 3000",
                "STAT_WATCH_VISITS = 2000", "STAT_DUMP_MAX     = 40",
                "STAT_SEED_MAX     = 60", "STAT_CARD_MAX     = 4",
                "CcoUnitStat", "dynamic_stats", "template_stat",
                "health_and_stats_parent", "row_header_stats", "stats_toggle",
                "Bounds", "GetImagePath", "NumStates", "GetStateByIndex",
                "***STAT-LIKE***", "hud id-search"):
        check(f"source carries {tok!r}", tok in SRC)
    print("== round-3 tokens still present (nothing loosened)")
    for tok in ("ComponentMouseOn", "ComponentMouseOff", "AddScriptEventReporter",
                "MOUSE_SECONDS  = 5", "MAX_VISITS = 1500", "MAX_DEPTH  = 9",
                "MAX_SAFETY_WINDOWS = 2", "round 3: mouse-armed capture"):
        check(f"round-3 token still present {tok!r}", tok in SRC)

    print("\n== registration")
    check("poll fn captured", G.poll_fn is not None)
    check("poll cadence is 200 ms", G.poll_ms == 200)
    check("ComponentMouseOn listener registered",
          G.M.listeners["ComponentMouseOn"] is not None)
    check("probe wrote its own log file", os.path.exists(log_path))
    check("log marks round 4 (targeted stat dump)",
          "round 4: targeted stat dump" in text())
    check("load line announces the round-4 seeds",
          "ROUND 4: targeted stat dump armed" in text())

    print("\n== (1) an EMPTY hud produces NO stat dump")
    tick(6)
    check("no stat dump on an empty HUD", n_dumps() == 0)

    print("\n== (1) a stat root that is HIDDEN produces NO stat dump")
    statroot = M.new("CcoUnitStat5755085424",
                     rt.table(visible=False,
                              img0="ui/mock/number_53.png",
                              nstates=2,
                              states=rt.table("active", "hover")))
    M.attach(M.hud, statroot)
    M.chain_named(statroot, 25, "chain_")   # depth 25 (cap is 20)
    tick(9)
    check("no dump while the stat root stays hidden", n_dumps() == 0)

    print("\n== (2) the stat root becoming VISIBLE triggers exactly ONE dump")
    M.set_visible(statroot, True)
    ok = tick_until(lambda: n_dumps() >= 1)
    check("a visible CcoUnitStat* triggered an auto dump", ok)
    t = text()
    check("the dump header names the auto trigger",
          "STAT DUMP #1 (trigger: auto: visible stat set changed" in t)
    check("the header names the seed it walks",
          "--- stat root 1/1 (id starts with CcoUnitStat) id=\"CcoUnitStat5755085424\" ---" in t)
    check("the seed-roots list is logged",
          "seed roots tried: id starts with CcoUnitStat" in t)

    print("\n== (3) the dump walks DEEPER than the round-3 walk (cap 20 vs 9)")
    check("a depth-10 node is logged (round 3 stops at 9)", "chain_10" in t)
    check("a depth-15 node is logged", "chain_15" in t)
    check("the depth-20 node is logged", "chain_20" in t)
    check("the depth-21 node is NOT logged", "chain_21" not in t)

    print("\n== (5) every requested field is dumped, digits flagged")
    check("id field", 'id="CcoUnitStat5755085424"' in t)
    check("state + GetStateText", " state=\"active\" states=[active|hover]" in t)
    check("stext field", " stext=" in t)
    check("tip field", " tip=" in t)
    check("Visible / VisibleFromRoot", " vis=true vfr=true" in t)
    check("Position", "pos=(11,22)" in t)
    check("Bounds", "bounds=(100,50)" in t)
    check("GetImagePath", 'img0="ui/mock/number_53.png"' in t)
    check("digit in the image path flagged ***STAT-LIKE***",
          "***STAT-LIKE (" in t and "digit in img0" in t)

    print("\n== (2) unchanged polls re-dump NOTHING (exactly one dump so far)")
    tick(30)
    check(f"still exactly one dump (got {n_dumps()})", n_dumps() == 1)

    print("\n== (4) a CHANGE of the visible-stat set re-dumps")
    M.attach(M.hud, M.new("stats_toggle", rt.table(visible=True)))
    ok = tick_until(lambda: n_dumps() >= 2)
    check("a second visible stat re-dumped", ok)
    check("dump #2 header present", "STAT DUMP #2 (trigger: auto: visible stat set changed" in text())

    print("\n== (6) the manual single-root hook works and re-logs the component")
    before_chain7 = count('id="chain_7"')
    res = G.zz_probe_stat_dump("CcoUnitStat5755085424")
    t = text()
    check("manual root hook reports it dumped", "stat dump done" in res)
    check("manual root header present",
          "STAT DUMP (manual: zz_probe_stat_dump('CcoUnitStat5755085424')) found via" in t)
    after_chain7 = count('id="chain_7"')
    check(f"the same component is logged again (un-filtered): {before_chain7} -> {after_chain7}",
          after_chain7 > before_chain7)

    print("\n== (6) the manual no-arg hook rescans and dumps the seeds")
    res = G.zz_probe_stat_dump()
    check("manual no-arg hook reports seed + card roots",
          "stat dump done (" in res and "seed +" in res)
    check("manual no-arg header present",
          "trigger: manual: zz_probe_stat_dump())" in text())

    print("\n== let the 2 automatic safety windows run out (round 3 goes quiet)")
    done = tick_until(
        lambda: ("active=false" in G.zz_probe_ui_status()
                 and "safety=2/2" in G.zz_probe_ui_status()),
        max_ticks=6000, chunk=25)
    check("both safety windows are spent and no window is active", done)

    print("\n== (7) the visit cap (3000) holds and speaks")
    M.clear(M.hud)
    wide = M.new("CcoUnitStat9999999999", rt.table(visible=False))
    M.attach(M.hud, wide)
    M.fill(wide, 3500, "wleaf_")
    tick_until(lambda: n_dumps() >= 3, max_ticks=60)   # settle + close
    tick(6)
    M.set_visible(wide, True)
    ok = tick_until(lambda: "STAT DUMP visit cap reached" in text(), max_ticks=120)
    check("the visit cap was reached and logged on the wide seed", ok)
    check("the cap line names 3000", "STAT DUMP visit cap reached (3000" in text())

    print("\n== (8) no setter was ever called")
    trips = rt.eval("#trips")
    check(f"trips == 0 (got {trips})", trips == 0)

    print("\n== (9) the round-3 mouse-armed capture still works")
    M.clear(M.hud)
    M.attach(M.hud, M.new("unit_card_1001", rt.table(stext="Boris Todbringer")))
    M.fire("ComponentMouseOn", rt.table(string="1001"))
    tick(2)
    check("a mouse-armed capture still arms",
          "armed (mouse), hover=\"1001\"" in text())

    print("\n== hooks: status + help")
    st = G.zz_probe_stat_status()
    check("stat status names the dump count", "stat dumps=" in st)
    check("stat status names the seed roots", "CcoUnitStat*" in st)
    check("stat status names the log file", LOG_FILE in st)
    hp = G.zz_probe_stat_help()
    check("stat help names the manual hook", "zz_probe_stat_dump()" in hp)
    check("stat help names the log file", LOG_FILE in hp)

    print("\n== final: still no setter called")
    trips = rt.eval("#trips")
    check(f"trips == 0 after every path (got {trips})", trips == 0)

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f in failures:
            print("   -", f)
        return 1
    print("SMOKE TEST PASSED - stat panel opening triggers ONE full unfiltered dump, "
          "depth 20 / 3000 visits, every field logged, digits flagged, re-dump on set "
          "change, manual hooks work, caps hold, no setter called, round 3 intact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
