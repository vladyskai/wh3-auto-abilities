"""Offline smoke test for the ROUND-3 zz_probe_ui_text probe (MOUSE-ARMED capture).

Runs the REAL probe source in a lupa Lua runtime against a MUTABLE mock UI tree
and asserts the mouse-armed capture contract:

  (1) a ComponentMouseOn over a card-like component ARMS a short 5 s / 200 ms
      capture (a non-card id does NOT);
  (2) the capture header names the hovered component id and the tick;
  (3) NEW components appearing during the window are logged (with the tooltip
      fields and the ***STAT-LIKE*** flags);
  (4) unchanged polls log NOTHING;
  (5) a hostile reader is skipped (<ERR> / <opaque>) and the walk continues;
  (6) the depth cap (9) and the visit cap (1500) hold;
  (7) a ComponentMouseOff closes the mouse window early (after the grace);
  (8) the reporter subscription happens on card-like components (the engine only
      fires the mouse events for components that have AddScriptEventReporter) -
      and NO UI-state setter is ever called (trips == 0);
  (9) the 2-window 60 s safety net is bounded and the manual hook still works;
 (10) the one-shot / status / help hooks work.

Usage:  cd <this dir> && uv run --with lupa python lua_smoke_ui_probe_v3.py
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
PRELUDE = os.path.join(HERE, "mock_ui_prelude_v3.lua")
LOG_FILE = "zz_probe_ui_text_log.txt"

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def main() -> int:
    workdir = tempfile.mkdtemp(prefix="zz_probe_ui_smoke3_")
    os.chdir(workdir)

    rt = lupa.LuaRuntime(unpack_returned_tuples=True)
    rt.execute(open(PRELUDE, "r", encoding="utf-8").read())
    rt.execute(open(PROBE, "r", encoding="utf-8").read())

    G = rt.globals()
    M = G.M
    M.local_units = rt.table("1001", "1002")   # the local player's units
    log_path = os.path.join(workdir, LOG_FILE)

    def text():
        return open(log_path, "r", encoding="utf-8", errors="replace").read()

    def count(sub):
        return text().count(sub)

    def n_lines():
        return count("[zz_probe_ui_text]")

    def tick(n=1):
        for _ in range(n):
            G.poll_fn()

    def tick_until(pred, max_ticks=1500, chunk=50):
        done = 0
        while done < max_ticks:
            tick(chunk)
            done += chunk
            if pred():
                return True
        return pred()

    print("== static source tokens")
    SRC = open(PROBE, encoding="utf-8", errors="replace").read()
    for tok in ("ComponentMouseOn", "ComponentMouseOff",
                "zz_probe_ui_mouse_on", "zz_probe_ui_mouse_off",
                "core:add_listener", "AddScriptEventReporter",
                "MOUSE_SECONDS  = 5", "SAFETY_SECONDS = 60",
                "MAX_SAFETY_WINDOWS = 2", "MAX_MOUSE_CAPTURES",
                "MAX_VISITS = 1500", "MAX_DEPTH  = 9",
                "GetStateText", "GetTooltipText", "CurrentState",
                "VisibleFromRoot", "***STAT-LIKE***"):
        check(f"source carries {tok!r}", tok in SRC)

    print("\n== registration")
    check("poll fn captured (bm:repeat_callback ran at load)", G.poll_fn is not None)
    check("poll cadence is 200 ms", G.poll_ms == 200)
    check("poll name is zz_probe_ui_text_poll", G.poll_name == "zz_probe_ui_text_poll")
    check("ComponentMouseOn listener registered",
          G.M.listeners["ComponentMouseOn"] is not None)
    check("ComponentMouseOff listener registered",
          G.M.listeners["ComponentMouseOff"] is not None)
    check("probe wrote its own log file", os.path.exists(log_path))
    check("own log name in the log", LOG_FILE in text())
    check("load is marked as round 3 (mouse-armed)",
          "round 3: mouse-armed capture" in text())
    check("load line announces the mouse arming",
          "MOUSE-ARMED" in text())

    print("\n== (1) an EMPTY hud logs NO window pass (suppressed) and no safety window")
    tick(3)
    check("no safety window armed while the battle has not started",
          "armed (safety" not in text())
    check("no CAPTURE WINDOW header while the tree is empty", "CAPTURE WINDOW" not in text())
    check("no component line while the tree is empty", "NEW  " not in text())

    print("\n== (1)+(2) a MouseOn over a unit card ARMS a 5 s capture")
    # local units 1001/1002; a card-like component carrying the unit id, and a
    # stat component with the tooltip text we are hunting.
    card = M.new("unit_card_1001", rt.table(stext="Boris Todbringer"))
    a = M.new("stat_melee_defence", rt.table(stext="Melee Defence", tip="Base value: 53"))
    M.attach(M.hud, card)
    M.attach(M.hud, a)
    # fire the synthetic ComponentMouseOn on the unit's ui id
    assert M.fire("ComponentMouseOn", rt.table(string="1001"))
    tick(1)                      # the tick consumes the pending arm
    t = text()
    check("a 5 s mouse capture armed on hover=\"1001\"",
          'armed (mouse), hover="1001"' in t)
    check("the arm line names the 5 s duration and the end tick",
          "5 s -> ends at tick" in t)
    tick(1)                      # the header + the NEW lines
    t = text()
    check("the capture header names the hover, the tick and the root",
          "CAPTURE WINDOW 1 (mouse) t=" in t and 'hover="1001"' in t
          and "root='hud_battle' children=2" in t)
    check("the card component is logged as NEW",
          'NEW  id="unit_card_1001"' in t)
    check("the stat component is logged as NEW",
          'NEW  id="stat_melee_defence"' in t)
    check("its GetTooltipText text recorded", 'tip="Base value: 53"' in t)
    check("its GetStateText text recorded", 'stext="Melee Defence"' in t)
    check("visibility/position fields present", "vis=true vfr=true pos=(11,22)" in t)
    check("digit/'Base value' text flagged STAT-LIKE",
          "***STAT-LIKE tip (contains 'Base value')***" in t)
    check("stat-named component gets a NAME hint", "<<NAME~stat>>" in t)
    check("card-named component gets a NAME hint", "<<NAME~unit_card>>" in t)

    print("\n== (8) the reporter was subscribed on the card-like component")
    check(f"AddScriptEventReporter was called (got {M.reporter_calls})", M.reporter_calls >= 1)
    check("the card was reported",
          "unit_card_1001" in [M.reporter_log[i] for i in range(1, M.reporter_calls + 1)])

    print("\n== a second MouseOn while a window is ACTIVE does not double-arm")
    armed_now = count("armed (mouse")
    M.fire("ComponentMouseOn", rt.table(string="1002"))
    tick(1)
    check("no second mouse capture while one is active", count("armed (mouse") == armed_now)

    print("\n== (4) unchanged polls log NOTHING")
    before = n_lines()
    tick(3)
    check(f"three unchanged polls added no lines (before={before}, after={n_lines()})",
          n_lines() == before)

    print("\n== a text CHANGE is logged, with the previous text")
    M.set_text(a, "Melee Defence", "Base value: 60")
    tick(1)
    t = text()
    check("CHG line for the changed component", 'CHG  id="stat_melee_defence"' in t)
    check("the NEW text is recorded", 'tip="Base value: 60"' in t)
    check("the PREVIOUS text rides along",
          '(was stext="Melee Defence" tip="Base value: 53")' in t)

    print("\n== (5) the walk is PCALL-WALLED (a hostile reader is skipped)")
    c = M.new("stat_bad", rt.table(stext_raises=True))
    d = M.new("after_c", rt.table(stext="Armour"))
    e = M.new("stat_hostile", rt.table(stext="Armour", hostile_state=M.hostile_value))
    M.attach(M.hud, c)
    M.attach(M.hud, d)
    M.attach(M.hud, e)
    tick(1)
    t = text()
    check("a raising GetStateText is recorded as <ERR>, not fatal", 'stext="<ERR>"' in t)
    check("the component AFTER the raising one is still logged", 'id="after_c"' in t)
    check("a hostile CurrentState value is recorded as <opaque>",
          'id="stat_hostile" state="<opaque>"' in t)

    print("\n== (6a) the walk is DEPTH-capped (MAX_DEPTH=9)")
    M.clear(M.hud)
    M.chain(M.hud, 12)
    # keep a window open: re-arm a mouse capture so the walk keeps running
    M.fire("ComponentMouseOn", rt.table(string="1001"))
    tick(2)
    t = text()
    check("node at the depth limit is logged", "deep_9" in t)
    check("node beyond the depth limit is NOT logged", "deep_10" not in t)

    print("\n== (6b) the walk is VISIT-capped (MAX_VISITS=1500)")
    M.clear(M.hud)
    M.fill(M.hud, 1600, "leaf_")
    M.fire("ComponentMouseOn", rt.table(string="1001"))
    tick(2)
    check("visit cap reached on the wide tree", "VISIT CAP reached" in text())
    M.clear(M.hud)   # keep the long window-lifecycle ticks fast

    print("\n== (7) no setter was ever called")
    trips = rt.eval("#trips")
    check(f"trips == 0 (got {trips})", trips == 0)

    print("\n== a MouseOff on the arming card closes the MOUSE window early")
    # make sure no window is active: tick past the current 5 s window
    tick_until(lambda: "active=true" not in G.zz_probe_ui_status(), max_ticks=60, chunk=10)
    M.fire("ComponentMouseOn", rt.table(string="1002"))
    tick(1)                      # arm
    tick(1)                      # header -> now active
    check("a fresh mouse capture is active", "active=true" in G.zz_probe_ui_status())
    before_ends = count("ended at t=")
    M.fire("ComponentMouseOff", rt.table(string="1002"))
    tick(3)
    check("the MouseOff closed the window early (grace = 2 ticks)",
          count("ended at t=") == before_ends + 1)
    check("that early end is the mouse window",
          "(mouse) ended at t=" in text())

    print("\n== a non-card MouseOn does NOT arm")
    armed_before = count("armed (mouse")
    M.fire("ComponentMouseOn", rt.table(string="some_random_button"))
    tick(2)
    check("no mouse capture armed for a non-card id", count("armed (mouse") == armed_before)

    print("\n== the address fallback arms (an unclassified id on a known reporter)")
    armed_before = count("armed (mouse")
    M.fire("ComponentMouseOn",
           rt.table(string="zzz_unclassified", component="Pointer<Component> (0xunit_card_1001)"))
    tick(1)
    check("a MouseOn on a known reporter address arms", count("armed (mouse") == armed_before + 1)
    # let that window close before the next phases
    tick_until(lambda: "active=true" not in G.zz_probe_ui_status(), max_ticks=60, chunk=10)

    print("\n== (9b) the manual hook still works")
    r = G.zz_probe_ui_arm(5)
    check("zz_probe_ui_arm returns an instruction", "capture window armed for 5 s" in r)
    tick(1)
    check("a manual window arms", "armed (manual" in text())

    print("\n== (9) the automatic safety net is bounded: 2 x 60 s")
    tick_until(lambda: "active=true" not in G.zz_probe_ui_status(), max_ticks=60, chunk=10)
    M.set_conflict(True)
    check("safety window 1 arms (battle running)",
          tick_until(lambda: count("armed (safety") >= 1, max_ticks=600, chunk=50))
    check("safety window 2 arms", tick_until(lambda: count("armed (safety") >= 2,
                                             max_ticks=1200, chunk=50))
    check("the 2-window cap is announced",
          tick_until(lambda: "all 2 safety window(s) used" in text(), max_ticks=1200, chunk=50))
    tick(200)
    check("no third AUTOMATIC window ever arms", count("armed (safety") == 2)

    print("\n== (10) the one-shot hook walks hud_battle")
    M.attach(M.hud, M.new("stat_x", rt.table(stext="Armour")))
    res = G.zz_probe_ui("hud_battle")
    check("one-shot reports it walked", "one-shot walk done" in res)
    check("ONE-SHOT WALK header present", "ONE-SHOT WALK root='hud_battle'" in text())

    print("\n== status + help")
    st = G.zz_probe_ui_status()
    check("status names windows used", "windows used=" in st)
    check("status names the safety net", "safety=" in st)
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
    print("SMOKE TEST PASSED - mouse-on over a card arms the 5 s capture, NEW/changed "
          "logged, unchanged silent, hostile reads skipped, caps + pcall walls hold, "
          "reporter subscribed, safety net bounded at 2, no setter called.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
