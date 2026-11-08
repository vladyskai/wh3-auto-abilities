"""Offline smoke test for the ROUND-2 zz_probe_ui_text probe (continuous capture).

Runs the REAL probe source in a lupa Lua runtime against a MUTABLE mock UI tree
and asserts the change-only capture contract:

  (1) an empty HUD produces NO capture-window header and NO component line
      (empty-tree passes are suppressed, never logged as a result);
  (2) a component APPEARING with text between two polls is logged as NEW;
  (3) a text CHANGE between two polls is logged as CHG with the previous text;
  (4) unchanged polls log NOTHING;
  (5) a digit-bearing / "Base value" text is flagged ***STAT-LIKE***;
  (6) the depth cap hides the too-deep node and the visit cap bites;
  (7) pcall walls: a raising read is recorded as <ERR>, a hostile value as
      <opaque>, and the walk continues past both;
  (8) the automatic window schedule is bounded (3 x 60 s) and a manual re-run
      works after the cap;
  (9) the one-shot hook walks hud_battle;
 (10) NO setter was ever called.

Usage:  cd <this dir> && uv run --with lupa python lua_smoke_ui_probe_v2.py
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
PRELUDE = os.path.join(HERE, "mock_ui_prelude_v2.lua")
LOG_FILE = "zz_probe_ui_text_log.txt"

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def main() -> int:
    workdir = tempfile.mkdtemp(prefix="zz_probe_ui_smoke2_")
    os.chdir(workdir)

    rt = lupa.LuaRuntime(unpack_returned_tuples=True)
    rt.execute(open(PRELUDE, "r", encoding="utf-8").read())
    rt.execute(open(PROBE, "r", encoding="utf-8").read())

    G = rt.globals()
    M = G.M
    log_path = os.path.join(workdir, LOG_FILE)

    def text():
        return open(log_path, "r", encoding="utf-8", errors="replace").read()

    def n_lines():
        return text().count("[zz_probe_ui_text]")

    def tick(n=1):
        for _ in range(n):
            G.poll_fn()

    print("== registration")
    check("poll fn captured (bm:repeat_callback ran at load)", G.poll_fn is not None)
    check("poll cadence is 250 ms", G.poll_ms == 250)
    check("poll name is zz_probe_ui_text_poll", G.poll_name == "zz_probe_ui_text_poll")
    check("probe wrote its own log file", os.path.exists(log_path))
    check("own log name in the log", LOG_FILE in text())

    print("\n== (1) an EMPTY hud logs NO window pass (suppressed)")
    tick(4)
    check("a capture window armed automatically (battle is running)",
          "capture window 1 armed (auto)" in text())
    check("no CAPTURE WINDOW header while the tree is empty",
          "CAPTURE WINDOW" not in text())
    check("no component line while the tree is empty", "NEW  " not in text())

    print("\n== (2) a component APPEARING with text is logged as NEW")
    a = M.new("stat_melee_defence", rt.table(stext="Melee Defence", tip="Base value: 53"))
    M.attach(M.hud, a)
    tick(1)
    t = text()
    check("window header written once content exists",
          "CAPTURE WINDOW 1 (auto) t=5 root='hud_battle' children=1" in t)
    check("NEW line for the appearing component",
          'NEW  id="stat_melee_defence"' in t)
    check("its GetTooltipText text recorded", 'tip="Base value: 53"' in t)
    check("its GetStateText text recorded", 'stext="Melee Defence"' in t)
    check("visibility/position fields present", "vis=true vfr=true pos=(11,22)" in t)
    check("digit/'Base value' text flagged STAT-LIKE",
          "***STAT-LIKE tip (contains 'Base value')***" in t)
    check("stat-named component gets a NAME hint", "<<NAME~stat>>" in t)

    print("\n== (4) unchanged polls log NOTHING")
    before = n_lines()
    tick(3)
    check(f"three unchanged polls added no lines (before={before}, after={n_lines()})",
          n_lines() == before)

    print("\n== (3) a text CHANGE is logged, with the previous text")
    M.set_text(a, "Melee Defence", "Base value: 60")
    tick(1)
    t = text()
    check("CHG line for the changed component", 'CHG  id="stat_melee_defence"' in t)
    check("the NEW text is recorded", 'tip="Base value: 60"' in t)
    check("the PREVIOUS text rides along",
          '(was stext="Melee Defence" tip="Base value: 53")' in t)

    print("\n== a second appearing component is logged as NEW")
    b = M.new("stat_armour", rt.table(stext="Armour"))
    M.attach(M.hud, b)
    tick(1)
    check("NEW line for the second component", 'NEW  id="stat_armour"' in text())

    print("\n== (7) the walk is PCALL-WALLED")
    c = M.new("stat_bad", rt.table(stext_raises=True))
    d = M.new("after_c", rt.table(stext="Armour"))
    e = M.new("stat_hostile", rt.table(stext="Armour", hostile_state=M.hostile_value))
    M.attach(M.hud, c)
    M.attach(M.hud, d)
    M.attach(M.hud, e)
    tick(1)
    t = text()
    check("a raising GetStateText is recorded as <ERR>, not fatal", 'stext="<ERR>"' in t)
    check("the component AFTER the raising one is still logged",
          'id="after_c"' in t)
    check("a hostile CurrentState value is recorded as <opaque>",
          'id="stat_hostile" state="<opaque>"' in t)

    print("\n== (6a) the walk is DEPTH-capped (MAX_DEPTH=9)")
    M.clear(M.hud)
    M.chain(M.hud, 12)
    tick(1)
    t = text()
    check("node at the depth limit is logged", "deep_9" in t)
    check("node beyond the depth limit is NOT logged", "deep_10" not in t)

    print("\n== (6b) the walk is VISIT-capped (MAX_VISITS=1500)")
    M.clear(M.hud)
    M.fill(M.hud, 1600, "leaf_")
    tick(1)
    check("visit cap reached on the wide tree", "VISIT CAP reached" in text())
    M.clear(M.hud)   # keep the long window-lifecycle ticks fast

    print("\n== NO setter was ever called")
    trips = rt.eval("#trips")
    check(f"trips == 0 (got {trips})", trips == 0)

    print("\n== (8) the automatic window schedule is bounded: 3 x 60 s")
    def tick_until(pred, max_ticks=2000, chunk=50):
        done = 0
        while done < max_ticks:
            tick(chunk)
            done += chunk
            if pred():
                return True
        return pred()

    check("window 1 ended",
          tick_until(lambda: "capture window 1 (auto) ended" in text()))
    check("window 2 armed (auto)",
          tick_until(lambda: "capture window 2 armed (auto)" in text()))
    check("window 3 armed (auto)",
          tick_until(lambda: "capture window 3 armed (auto)" in text()))
    check("the cap is announced after the third window",
          tick_until(lambda: "all 3 automatic window(s) used" in text()))
    tick(200)
    check("no fourth AUTOMATIC window ever arms",
          "capture window 4 armed (auto)" not in text())

    print("\n== (8b) a MANUAL re-run works after the cap")
    r = G.zz_probe_ui_arm(5)
    check("zz_probe_ui_arm returns an instruction", "capture window armed for 5 s" in r)
    tick(1)
    check("a manual window 4 arms", "capture window 4 armed (manual)" in text())

    print("\n== (9) the one-shot hook walks hud_battle")
    M.attach(M.hud, M.new("stat_x", rt.table(stext="Armour")))
    res = G.zz_probe_ui("hud_battle")
    check("one-shot reports it walked", "one-shot walk done" in res)
    check("ONE-SHOT WALK header present", "ONE-SHOT WALK root='hud_battle'" in text())

    print("\n== status + help")
    st = G.zz_probe_ui_status()
    check("status names windows used", "windows used=" in st)
    check("status names the log file", LOG_FILE in st)
    hp = G.zz_probe_ui_help()
    check("help names the log file", LOG_FILE in hp)
    check("help names the manual arm hook", "zz_probe_ui_arm(60)" in hp)

    print("\n== final: still no setter called")
    trips = rt.eval("#trips")
    check(f"trips == 0 after every path (got {trips})", trips == 0)

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f in failures:
            print("   -", f)
        return 1
    print("SMOKE TEST PASSED - empty-tree suppressed, NEW/CHANGED logged, unchanged "
          "silent, caps + pcall walls hold, arming bounded, no setter called.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
