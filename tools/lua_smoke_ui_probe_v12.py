"""Offline smoke test for the ROUND-14 zz_probe_ui_text probe.
Run:
    cd C:/Users/vlady/Desktop/WH3_mod/tools && uv run --with lupa python lua_smoke_ui_probe_v12.py

Worlds (independent lupa runtimes, mock engine tree):
  W0 static: the R14 tokens exist; the BANNED name-lookup global is ABSENT from the
     source; the walk budget is 300 and the depth is 6; the total step count (8)
     is stated; no string.find call; zero SetContextObject call sites.
  W1 main: steps 1-8 run SAFELY, one armed step per call. Step 1 SEEDS the descent
     on the discovered chain (hud_battle > ... > list) and walks DOWN from `list`;
     step 2 pairs the rows (stat_name -> value_holder/dy_value); step 3 is the
     control (CcoBattleUnit/1001/Name); step 4 runs the 5 new-format A rungs (all
     fail); step 5 is the non-selected control (CcoBattleUnit/1002/Name -> WIN of
     the CONTROL); steps 6-7 run the 7 B rungs (all fail); step 8 states the
     verdict. 14 GCV calls, each logged before AND after; the 9th call is the DONE
     transition; the 10th is ignored.
  W2 stop-at-first-success: a SELECTED new-format rung answers -> LADDER A stops at
     rung 3; the remaining A rungs are NOT called.
  W3 WIN (BU_1002): a NON-selected new-format rung answers -> step 6 stops with the
     loud R14 *** WIN ***; step 7 is skipped.
  W4 WIN (bare 1002): every BU_1002 rung fails, the bare-id rung answers -> step 7
     WIN.
  W5 walk budget: a 506-node `list` is cut at exactly 300 visits.
  W6 no chain: the chain breaks at info_panel_background -> step 1 aborts, no rows,
     but the ladder still runs (0 values, no false WIN).
  W7 disarm: driving the tick never auto-runs R14; simhover stays disarmed.
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
PRELUDE = os.path.join(HERE, "mock_ui_prelude_v7.lua")
ADDITIONS = os.path.join(HERE, "mock_r14_additions.lua")
LOG_FILE = "zz_probe_ui_text_log.txt"
R14_TAG = "[zz_probe_ui_text] R14 "

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def r14_lines(text):
    return [ln for ln in text.splitlines() if R14_TAG in ln]


def preceded_ok(text, marker):
    """Every log line containing `marker` is immediately preceded by a CALL line."""
    lines = r14_lines(text)
    ok, hits = True, 0
    for i, ln in enumerate(lines):
        if marker in ln:
            hits += 1
            if i == 0 or " CALL " not in lines[i - 1]:
                ok = False
    return ok, hits


class World:
    def __init__(self, base):
        self.dir = tempfile.mkdtemp(prefix="r14_", dir=base)
        os.chdir(self.dir)
        self.rt = lupa.LuaRuntime(unpack_returned_tuples=True)
        with open(PRELUDE, encoding="utf-8") as f:
            self.rt.execute(f.read())
        with open(ADDITIONS, encoding="utf-8") as f:
            self.rt.execute(f.read())
        with open(PROBE, encoding="utf-8") as f:
            self.rt.execute(f.read())
        self.G = self.rt.globals()
        self.M = self.G.M
        self.log_path = os.path.join(self.dir, LOG_FILE)

    def text(self):
        try:
            with open(self.log_path, encoding="utf-8", errors="replace") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def poll(self, n=1):
        for _ in range(n):
            self.G.poll_fn()

    def step(self, n=1):
        last = None
        for _ in range(n):
            last = self.G.zz_probe_r14_step()
        return last

    def writes_zero(self):
        M = self.M
        return (M.setctx_calls == 0 and M.select_calls == 0 and M.cco_calls == 0
                and M.sim_on_calls == 0 and M.sim_off_calls == 0)

    def trips_zero(self):
        return self.rt.eval("#trips") == 0


def main():
    base = tempfile.mkdtemp(prefix="zz_probe_ui_smoke14_")

    # ------------------------------------------------------------------ W0
    print("\n== W0: static round-14 tokens + the BAN on the name-lookup global")
    SRC = open(PROBE, encoding="utf-8", errors="replace").read()
    check("W0: the BANNED name-lookup global is ABSENT", "find_uicomponent" not in SRC)
    for tok in ("ROUND 14", "zz_probe_r14", "zz_probe_r14_step", "zz_probe_r14_auto",
                "zz_probe_r14_status", "zz_probe_r14_help",
                "R14 TOTAL STEPS 8", "SEED link ", "SEED resolved the FULL chain",
                "DOWN path=", "PANEL row=", "ROWHEADER ", "R14 GCV n=", "R14 CALL ",
                "*** WIN: non-selected unit stat field readable ***",
                "info_panel_parent", "info_panel_background", "unit_information",
                "info_parent", "info_panel", "row_header_stats", "template_stat",
                "value_holder", "dy_value", "stat_name", "resolve_chain",
                "walk_visits", "walk_depth", "total_steps",
                "common.get_context_value", "CcoBattleUnit", "CcoUnitDetails", "CcoUnitStat",
                "BattleUnit_1001", "BattleUnit_1002", "StatList", "StatList.Size",
                "DisplayedValue"):
        check(f"W0: source carries {tok!r}", tok in SRC)
    check("W0: the walk budget is 300", "walk_visits         = 300" in SRC)
    check("W0: the walk depth is 6", "walk_depth          = 6" in SRC)
    check("W0: the total step count is 8", "total_steps         = 8" in SRC)
    check("W0: before-call logger present", 'R14.out("CALL "' in SRC)
    check("W0: no string.find() call", "string.find(" not in SRC)
    check("W0: ZERO SetContextObject call site", SRC.count(":SetContextObject(") == 2)

    # ------------------------------------------------------------------ W1
    print("\n== W1: seeded path -> rows -> controls -> the two ladders (no false WIN)")
    W = World(base)
    W.G.M.build_r14_scene()
    res = W.G.zz_probe_r14()
    check("W1: zz_probe_r14() reports READY", "READY" in str(res))
    check("W1: the instruction states 8 total steps", "R14 TOTAL STEPS 8" in str(res))
    check("W1: the instruction says step 8 is the LAST step", "LAST step" in str(res))

    W.step(1)
    t = W.text()
    check("W1: step 1 header (1/8)", "R14 STEP 1/8" in t)
    check("W1: SEED link 1 resolves hud_battle via root:Find",
          'SEED link 1/7 path="hud_battle" id="hud_battle" how="root:Find"' in t)
    check("W1: SEED link 4 resolves unit_information by direct child",
          'id="unit_information" how="direct child"' in t)
    check("W1: SEED link 7 resolves `list` on the full path",
          'SEED link 7/7 path="hud_battle/info_panel_parent/info_panel_background/'
          'unit_information/info_parent/info_panel/list" id="list"' in t)
    check("W1: the chain fully resolved", "SEED resolved the FULL chain" in t)
    check("W1: the walk reached unit_information on the way down",
          'id="row_header_stats"' in t)
    check("W1: step 1 done line", "STEP 1 done: chain links=7 walked=" in t)
    ok, hits = preceded_ok(t, "R14 SEED link ")
    check("W1: every SEED line is preceded by a CALL line", ok and hits == 7)
    ok, hits = preceded_ok(t, "R14 DOWN path=")
    check("W1: every DOWN line is preceded by a CALL line", ok and hits > 0)

    W.step(1)
    t = W.text()
    check("W1: step 2 header (2/8)", "R14 STEP 2/8" in t)
    check("W1: step 2 logged the row block header", "ROWHEADER " in t and 'id="row_header_stats"' in t)
    check("W1: step 2 paired row 1 (Melee Defence 53)",
          'PANEL row=1 name="Melee Defence" value="53" rowid="template_stat"' in t)
    check("W1: step 2 paired row 2 (Armour 85)",
          'PANEL row=2 name="Armour" value="85" rowid="template_stat"' in t)
    check("W1: step 2 paired row 3 (Movement 5.2, the stat_name-child row)",
          'PANEL row=3 name="Movement" value="5.2" rowid="CcoUnitStat5974444112"' in t)
    check("W1: step 2 done line", "STEP 2 done: rows=3" in t)
    ok, hits = preceded_ok(t, "R14 PANEL row=")
    check("W1: every PANEL row is preceded by a CALL line", ok and hits == 3)

    W.step(1)
    t = W.text()
    check("W1: step 3 header (3/8)", "R14 STEP 3/8" in t)
    check("W1: step 3 control A = CcoBattleUnit/1001/Name -> Karl Franz",
          'GCV n=1 type=CcoBattleUnit id="1001" field="Name" -> "Karl Franz" [CONTROL]' in t)
    check("W1: the control A VALUE is flagged", "**VALUE**" in t)

    W.step(1)
    t = W.text()
    check("W1: step 4 header (4/8)", "R14 STEP 4/8" in t)
    check("W1: step 4 tried the 5 A rungs and none returned a value",
          "STEP 4 done: LADDER A - no new-format rung returned a value (5 tried)" in t)
    check("W1: the A ladder logged StatList.Size",
          'type=CcoUnitDetails id="BattleUnit_1001" field="StatList.Size" -> "<nil>"' in t)
    check("W1: the A ladder logged CcoUnitStat Name",
          'type=CcoUnitStat id="BattleUnit_1001" field="Name" -> "<nil>"' in t)

    W.step(1)
    t = W.text()
    check("W1: step 5 header (5/8)", "R14 STEP 5/8" in t)
    check("W1: step 5 control B = CcoBattleUnit/1002/Name -> Balthasar Gelt",
          'GCV n=7 type=CcoBattleUnit id="1002" field="Name" -> "Balthasar Gelt" [CONTROL] [NON-SELECTED]' in t)
    check("W1: the control B success raises the loud WIN(control) line",
          "*** WIN(control): non-selected bare-id CcoBattleUnit field readable ***" in t)
    check("W1: no NEW-format WIN is raised by the control",
          "*** WIN: non-selected unit stat field readable ***" not in t)

    W.step(1)
    t = W.text()
    check("W1: step 6 header (6/8)", "R14 STEP 6/8" in t)
    check("W1: step 6 tried the 5 BattleUnit_1002 rungs and none returned",
          "STEP 6 done: LADDER B (BattleUnit_1002) - no rung returned a value (5 tried)" in t)

    W.step(1)
    t = W.text()
    check("W1: step 7 header (7/8)", "R14 STEP 7/8" in t)
    check("W1: step 7 tried the bare-id rungs and none returned",
          "STEP 7 done: LADDER B (bare 1002) - no rung returned a value" in t)
    check("W1: step 7 logged the bare 1002 CcoUnitDetails rung",
          'type=CcoUnitDetails id="1002" field="StatList.Size"' in t)

    ret8 = W.step(1)
    t = W.text()
    check("W1: step 8 header (8/8)", "R14 STEP 8/8" in t)
    check("W1: the verdict reports 14 GCV calls", "VERDICT get_context_value calls=14" in t)
    check("W1: the verdict says NO new-format non-selected field was readable",
          "VERDICT: NO non-selected NEW-format stat field was readable" in t)
    check("W1: the verdict confirms the bare-id control WAS readable",
          "the NON-selected bare-id control value WAS readable" in t)
    check("W1: NO central-question WIN was raised",
          "VERDICT: CENTRAL QUESTION ANSWERED" not in t)
    check("W1: EXACTLY 14 get_context_value calls", W.M.gcv_calls == 14)
    check("W1: the step-8 return tells the user to STOP",
          "DONE - STOP" in str(ret8) and "8/8" in str(ret8))
    # every GCV line is preceded by a CALL line, and the n= values run 1..14 in order
    ok, hits = preceded_ok(t, "R14 GCV n=")
    check("W1: every GCV line is preceded by a CALL line", ok and hits == 14)
    ns = []
    for ln in r14_lines(t):
        if "GCV n=" in ln:
            ns.append(int(ln.split("GCV n=")[1].split(" ")[0]))
    check("W1: the GCV n= sequence is 1..14 in order", ns == list(range(1, 15)))

    # the 9th call is the DONE transition; the 10th is ignored (no wrap-around)
    W.step(1)
    t = W.text()
    check("W1: run-done banner", "ROUND 14 RUN done after 8 steps" in t)
    check("W1: done banner states YOU ARE DONE", "YOU ARE DONE" in t)
    check("W1: no step 9 header (no wrap-around)", "R14 STEP 9" not in t)
    W.step(1)
    t = W.text()
    check("W1: a 10th call is ignored", "step ignored: the run is done" in t)
    check("W1: the ignored call made no extra queries", W.M.gcv_calls == 14)
    check("W1: the BANNED global was NEVER called", W.M.fu_calls == 0)
    check("W1: UIComponent(boolean) was NEVER called", W.M.uic_bool_calls == 0)
    check("W1: ZERO writes (no context/selection/sim)", W.writes_zero())
    check("W1: ZERO UI-state setters", W.trips_zero())

    # ------------------------------------------------------------------ W2
    print("\n== W2: the ladder STOPS at the first success (a SELECTED rung answers)")
    W = World(base)
    W.G.M.build_r14_stopA()
    W.G.zz_probe_r14()
    W.step(4)   # steps 1..4
    t = W.text()
    check("W2: LADDER A stopped at rung 3",
          "LADDER A STOPPED at first success: rung 3/5 CcoUnitDetails/BattleUnit_1001/StatList.Size" in t
          and '= "7"' in t)
    check("W2: exactly 4 GCV calls ran (control + 3 A rungs)", W.M.gcv_calls == 4)
    check("W2: rung 4 (DisplayedValue) was NOT called",
          'id="BattleUnit_1001" field="DisplayedValue"' not in t)
    check("W2: rung 5 (CcoUnitStat Name) was NOT called",
          'type=CcoUnitStat id="BattleUnit_1001" field="Name"' not in t)
    check("W2: ZERO writes", W.writes_zero())

    # ------------------------------------------------------------------ W3
    print("\n== W3: a NON-selected new-format rung answers -> step 6 WIN, step 7 skipped")
    W = World(base)
    W.G.M.build_r14_win()
    W.G.zz_probe_r14()
    W.step(6)   # steps 1..6
    t = W.text()
    check("W3: LADDER B stopped at rung 3",
          "LADDER B STOPPED at first success: rung 3/7 CcoUnitDetails/BattleUnit_1002/StatList.Size" in t
          and '= "12"' in t)
    check("W3: the loud non-selected WIN was raised",
          "*** WIN: non-selected unit stat field readable *** type=CcoUnitDetails "
          'id="BattleUnit_1002" field="StatList.Size" value="12"' in t)
    ret7 = W.step(1)
    t = W.text()
    check("W3: step 7 was skipped because the ladder already stopped",
          "the ladder already stopped" in t)
    check("W3: step 6 made only 3 B calls (10 total)", W.M.gcv_calls == 10)
    W.step(1)   # step 8
    t = W.text()
    check("W3: the verdict ANSWERS the central question",
          "VERDICT: CENTRAL QUESTION ANSWERED" in t)
    check("W3: ZERO writes", W.writes_zero())

    # ------------------------------------------------------------------ W4
    print("\n== W4: only the BARE non-selected id answers -> step 7 WIN")
    W = World(base)
    W.G.M.build_r14_bare()
    W.G.zz_probe_r14()
    W.step(7)   # steps 1..7
    t = W.text()
    check("W4: every BattleUnit_1002 rung failed",
          "STEP 6 done: LADDER B (BattleUnit_1002) - no rung returned a value (5 tried)" in t)
    check("W4: LADDER B (bare) stopped at rung 6",
          "LADDER B STOPPED at first success (bare id): rung 6/7 CcoUnitDetails/1002/StatList.Size" in t
          and '= "9"' in t)
    check("W4: the loud non-selected WIN was raised for the bare id",
          "*** WIN: non-selected unit stat field readable *** type=CcoUnitDetails "
          'id="1002" field="StatList.Size" value="9"' in t)
    check("W4: 13 GCV calls (1+5+1+5+1)", W.M.gcv_calls == 13)

    # ------------------------------------------------------------------ W5
    print("\n== W5: the 300-visit walk budget cuts a 506-node `list`")
    W = World(base)
    W.G.M.build_r14_wide()
    W.G.zz_probe_r14()
    W.step(1)
    t = W.text()
    n = t.count("R14 DOWN path=")
    check(f"W5: exactly 300 walk visits (got {n})", n == 300)
    check("W5: the walk reported the cap", "WALK visit budget reached (300)" in t)
    check("W5: step 1 done reports walked=300/300", "walked=300/300" in t)
    check("W5: the BANNED global was NEVER called", W.M.fu_calls == 0)
    check("W5: ZERO writes", W.writes_zero())

    # ------------------------------------------------------------------ W6
    print("\n== W6: the chain breaks -> step 1 aborts, no rows, the ladder still runs")
    W = World(base)
    W.G.M.build_r14_nolist()
    W.G.zz_probe_r14()
    W.step(8)
    t = W.text()
    check("W6: the chain named the missing link",
          'CHAIN link 3/7 id="info_panel_background" NOT FOUND' in t)
    check("W6: step 1 aborted", "the discovered chain did not resolve" in t)
    check("W6: step 2 reported nothing walked", "nothing was walked in step 1" in t)
    check("W6: no stat row was read", "PANEL row=" not in t)
    check("W6: the ladder still ran (14 calls)", W.M.gcv_calls == 14)
    check("W6: no false WIN (no value at all)",
          "VERDICT: NO non-selected NEW-format stat field was readable" in t
          and "CENTRAL QUESTION ANSWERED" not in t)
    check("W6: ZERO writes", W.writes_zero())

    # ------------------------------------------------------------------ W7
    print("\n== W7: the tick never auto-runs R14; simhover stays disarmed")
    W = World(base)
    W.G.M.build_r14_scene()
    W.poll(40)
    t = W.text()
    check("W7: R14 did NOT auto-run from the tick", "R14 STEP" not in t)
    check("W7: no SimulateMouseOn (simhover disarmed)", W.M.sim_on_calls == 0)
    check("W7: the BANNED global was NEVER called", W.M.fu_calls == 0)

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f_ in failures:
            print("   -", f_)
        return 1
    print("SMOKE TEST PASSED - round 14: the descent is SEEDED on the discovered panel")
    print("  path (hud_battle > ... > list), `list` is walked to depth 6 (budget 300), the")
    print("  stat rows are paired (PANEL row=), and the FIXED ladder of common.get_context_value")
    print("  calls runs with a control first, then CcoUnitDetails/BattleUnit_1001 (Name/StatList/")
    print("  StatList.Size), CcoUnitStat/BattleUnit_1001 (DisplayedValue/Name), then the SAME shape")
    print("  for the NON-selected unit (BattleUnit_1002 and bare 1002) - every call logged before")
    print("  AND after, the ladder STOPS at the first success, and a non-selected success raises")
    print("  the loud R14 *** WIN *** - EIGHT steps total, ZERO writes, the engine's name-lookup")
    print("  global BANNED (never called).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
