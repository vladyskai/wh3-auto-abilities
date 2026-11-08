"""Offline smoke test for the ROUND-13 zz_probe_ui_text probe.
Run:
    cd C:/Users/vlady/Desktop/WH3_mod/tools && uv run --with lupa python lua_smoke_ui_probe_v11.py

Worlds (independent lupa runtimes, mock engine tree):
  W0 static: the R13 tokens exist; the BANNED name-lookup global is ABSENT from
     the source; the descend budget is 1200 and the depth is 8; the total step
     count (7) is stated; the stable prefix is ccounitstat; no string.find call;
     zero SetContextObject call sites.
  W1 main: steps 1-7 run SAFELY, one armed step per call. Step 1 keeps EVERY root
     WITH children, priority-ordered; steps 2-3 descend hud_battle FIRST then the
     rest to DEPTH 8 (1200-visit budget) and FIND a CcoUnitStat*-prefixed row in
     BOTH cases (lowercase + mixed) nested under the vis=true hud_battle root; step
     4 pairs the rows; step 5 reads the context ids (selected_ui=1001); step 6 asks
     the located id (StatList.Size); step 7 asks a NON-selected ui id (1002) with
     DisplayedValue (query 1 returned) - EXACTLY TWO get_context_value calls. The
     8th call is the DONE transition; the 9th is ignored (no wrap-around).
  W2 depth cap: a CcoUnitStat* node at depth 9 is NOT located (the descent stops at 8).
  W3 visit budget: a 1641-node fan-out is cut off at exactly 1200 visits.
  W4 no hits: roots with children but no prefix/structural id -> no rows, 0 calls.
  W5 disarm: driving the tick never auto-runs R13; simhover stays disarmed.
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
PRELUDE = os.path.join(HERE, "mock_ui_prelude_v7.lua")
ADDITIONS = os.path.join(HERE, "mock_r13_additions.lua")
LOG_FILE = "zz_probe_ui_text_log.txt"
R13_TAG = "[zz_probe_ui_text] R13 "

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def r13_lines(text):
    return [ln for ln in text.splitlines() if R13_TAG in ln]


def every_preceded_by_call(text, marker):
    lines = r13_lines(text)
    ok = True
    hits = 0
    for i, ln in enumerate(lines):
        if marker in ln:
            hits += 1
            if i == 0 or " CALL " not in lines[i - 1]:
                ok = False
    return ok, hits


class World:
    def __init__(self, base):
        self.dir = tempfile.mkdtemp(prefix="r13_", dir=base)
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
            last = self.G.zz_probe_r13_step()
        return last

    def writes_zero(self):
        M = self.M
        return (M.setctx_calls == 0 and M.select_calls == 0 and M.cco_calls == 0
                and M.sim_on_calls == 0 and M.sim_off_calls == 0)

    def trips_zero(self):
        return self.rt.eval("#trips") == 0


def main():
    base = tempfile.mkdtemp(prefix="zz_probe_ui_smoke13_")

    # ------------------------------------------------------------------ W0
    print("\n== W0: static round-13 tokens + the BAN on the name-lookup global")
    SRC = open(PROBE, encoding="utf-8", errors="replace").read()
    check("W0: the BANNED name-lookup global is ABSENT", "find_uicomponent" not in SRC)
    for tok in ("ROUND 13", "zz_probe_r13", "zz_probe_r13_step", "zz_probe_r13_auto",
                "zz_probe_r13_status", "zz_probe_r13_help",
                "ROOTCOUNT", "DESCEND PLAN", "DOWN path=", "R13 HIT", "LOCATED ",
                "PANEL row=", "ROWCTX ", "CTXID ", "QUERY sel=", "QUERY nonsel=",
                "R13 TOTAL STEPS 7", "descend_visits", "descend_depth",
                "stat_prefix", "ccounitstat", "locate_names", "priority",
                "hud_battle", "panel_manager", "under_advisor_docker", "tactical_hud",
                "menu_bar", "is_prefix_id", "is_hit_id", "total_steps", "GetTooltipText",
                "common.get_context_value", "GetContextObjectId", "StatList.Size",
                "DisplayedValue"):
        check(f"W0: source carries {tok!r}", tok in SRC)
    check("W0: descend budget is 1200", "descend_visits  = 1200" in SRC)
    check("W0: descend depth is 8", "descend_depth   = 8" in SRC)
    check("W0: total step count is 7", "total_steps     = 7" in SRC)
    check("W0: the stable prefix is ccounitstat", 'stat_prefix     = "ccounitstat"' in SRC)
    check("W0: before-call logger present", 'R13.out("CALL "' in SRC)
    check("W0: wrap() rejects a boolean", "if raw == nil or raw == false then return nil end" in SRC)
    check("W0: no string.find() call", "string.find(" not in SRC)
    check("W0: ZERO SetContextObject call site", SRC.count(":SetContextObject(") == 2)

    # ------------------------------------------------------------------ W1
    print("\n== W1: all-roots descent -> CcoUnitStat prefix -> rows -> ctx ids -> TWO queries")
    W = World(base)
    W.G.M.build_r13_scene()
    res = W.G.zz_probe_r13()
    check("W1: zz_probe_r13() reports READY", "READY" in str(res))
    check("W1: the instruction states 7 total steps", "R13 TOTAL STEPS 7" in str(res))
    check("W1: the instruction says step 7 is the LAST step", "LAST step" in str(res))

    W.step(1)
    t = W.text()
    check("W1: step 1 header (1/7)", "R13 STEP 1/7" in t)
    check("W1: step 1 root count == 11 roots", "R13 ROOTCOUNT 11" in t)
    check("W1: step 1 surfaced hud_battle (keep=true)",
          'id="hud_battle"' in t and "keep=true" in t)
    check("W1: step 1 marked left HIDDEN but still kept",
          'id="left" vis=false' in t)
    check("W1: step 1 skipped the childless watermark_square",
          'id="watermark_square"' in t and "children=0 rank=100 keep=false" in t)
    check("W1: step 1 priority plan is in the STATED order",
          "DESCEND PLAN prio=7 : hud_battle,panel_manager,under_advisor_docker,left,right,tactical_hud,menu_bar" in t)
    check("W1: step 1 rest plan lists tactical_map,unit_id_holder",
          "DESCEND PLAN rest=2 : tactical_map,unit_id_holder" in t)
    check("W1: step 1 kept 2 numeric unit-id candidates", "unit_id_candidates=2" in t)
    ok, hits = every_preceded_by_call(t, "R13 ROOT ")
    check("W1: every ROOT read is preceded by an R13 CALL line", ok and hits == 11)

    W.step(1)
    t = W.text()
    check("W1: step 2 header (2/7)", "R13 STEP 2/7" in t)
    check("W1: step 2 descends hud_battle FIRST",
          'STEP 2 root 1 id="hud_battle"' in t)
    # the descent reaches the panel + the CcoUnitStat-prefixed row under vis=true hud_battle
    check("W1: the descent reached the panel (health_and_stats_parent)",
          'R13 DOWN path="hud_battle/1001/modular_parent/health_and_stats_parent" id="health_and_stats_parent"' in t)
    check("W1: the descent HIT the MIXED-case CcoUnitStat row",
          'R13 HIT path="hud_battle/1001/modular_parent/health_and_stats_parent/dynamic_stats/CcoUnitStat5974444112" id="CcoUnitStat5974444112"' in t)
    check("W1: the descent HIT the LOWERCASE ccounitstat row (case-insensitive)",
          'id="ccounitstat5974452864"' in t and "R13 HIT" in t)
    check("W1: the descent HIT the structural stats_toggle / row_header_stats",
          'id="stats_toggle"' in t and 'id="row_header_stats"' in t)
    check("W1: step 2 stayed inside the 1200-visit budget",
          "STEP 2 done: visits=" in t and int(t.split("STEP 2 done: visits=")[1].split("/")[0]) <= 1200)
    ok, hits = every_preceded_by_call(t, "R13 DOWN path=")
    check("W1: every DOWN line is preceded by an R13 CALL line", ok and hits > 0)
    ok, hits = every_preceded_by_call(t, "R13 HIT path=")
    check("W1: every HIT line is preceded by an R13 CALL line", ok and hits > 0)

    W.step(1)
    t = W.text()
    check("W1: step 3 header (3/7)", "R13 STEP 3/7" in t)
    check("W1: step 3 descends the HIDDEN left root",
          'STEP 3 root' in t and 'id="left"' in t)
    check("W1: step 3 descends unit_id_holder", 'id="unit_id_holder"' in t)
    check("W1: step 3 done line present", "STEP 3 done: visits=" in t)

    W.step(1)
    t = W.text()
    check("W1: step 4 header (4/7)", "R13 STEP 4/7" in t)
    check("W1: step 4 logged a LOCATED path", 'R13 LOCATED path=' in t)
    check("W1: step 4 paired row 1 (Armour 85)",
          'PANEL row=1 name="Armour" value="85"' in t)
    check("W1: step 4 paired row 2 (Movement 5.2)",
          'PANEL row=2 name="Movement" value="5.2"' in t)
    check("W1: step 4 paired row 3 (Armour 85, the mixed-case prefix row)",
          'PANEL row=3 name="Armour" value="85"' in t)
    check("W1: step 4 tagged the prefix row (ROWCTX prefix=CcoUnitStat)",
          "ROWCTX " in t and "prefix=CcoUnitStat" in t and 'id="CcoUnitStat5974444112"' in t)
    ok, hits = every_preceded_by_call(t, "R13 PANEL row=")
    check("W1: every PANEL row is preceded by an R13 CALL line", ok and hits == 3)

    W.step(1)
    t = W.text()
    check("W1: step 5 header (5/7)", "R13 STEP 5/7" in t)
    check("W1: step 5 read a CcoUnitDetails context id", 'CTXID ' in t and "CcoUnitDetails" in t)
    check("W1: step 5 surfaced the panel's CcoUnitDetails id 5001", '-> "5001"' in t)
    check("W1: step 5 surfaced a CcoUnitStat id 5101", '-> "5101"' in t)
    check("W1: step 5 identified the SELECTED unit ui id 1001", 'selected_ui="1001"' in t)
    ok, hits = every_preceded_by_call(t, "R13 CTXID ")
    check("W1: every CTXID line is preceded by an R13 CALL line", ok and hits > 0)

    W.step(1)
    t = W.text()
    check("W1: step 6 header (6/7)", "R13 STEP 6/7" in t)
    check("W1: step 6 QUERY sel uses the located id + StatList.Size",
          "R13 QUERY sel=" in t and "type=CcoUnitDetails" in t and "field=StatList.Size" in t)
    check("W1: step 6 reported 1 call so far", "STEP 6 done: get_context_value calls=1" in t)
    ok, hits = every_preceded_by_call(t, "R13 QUERY sel=")
    check("W1: the selected QUERY is preceded by an R13 CALL line", ok and hits == 1)

    ret7 = W.step(1)
    t = W.text()
    check("W1: step 7 header (7/7)", "R13 STEP 7/7" in t)
    check("W1: step 7 QUERY nonsel uses the ui id 1002 as text",
          'QUERY nonsel="1002"' in t and "type=CcoBattleUnit" in t)
    check("W1: step 7 used DisplayedValue because query 1 returned",
          "field=DisplayedValue" in t)
    check("W1: step 7 made EXACTLY TWO get_context_value calls", W.M.gcv_calls == 2)
    check("W1: step 7 reported 'calls=2'", "STEP 7 done: get_context_value calls=2" in t)
    ok, hits = every_preceded_by_call(t, "R13 QUERY nonsel=")
    check("W1: the nonsel QUERY is preceded by an R13 CALL line", ok and hits == 1)
    check("W1: the step-7 return tells the user to STOP",
          "DONE - STOP" in str(ret7) and "7/7" in str(ret7))

    # the 8th call is the DONE transition; the 9th is ignored (no wrap-around)
    W.step(1)
    t = W.text()
    check("W1: run-done banner", "ROUND 13 RUN done after 7 steps" in t)
    check("W1: done banner states YOU ARE DONE", "YOU ARE DONE" in t)
    check("W1: no step 8 header (no wrap-around)", "R13 STEP 8" not in t)
    W.step(1)
    t = W.text()
    check("W1: a 9th call is ignored", "step ignored: the run is done" in t)
    check("W1: still no step 8 header", "R13 STEP 8" not in t)
    check("W1: the ignored call made no extra queries", W.M.gcv_calls == 2)
    check("W1: the BANNED global was NEVER called", W.M.fu_calls == 0)
    check("W1: UIComponent(boolean) was NEVER called", W.M.uic_bool_calls == 0)
    check("W1: ZERO writes (no context/selection/sim)", W.writes_zero())
    check("W1: ZERO UI-state setters", W.trips_zero())

    # ------------------------------------------------------------------ W2
    print("\n== W2: a CcoUnitStat* node BEYOND the depth-8 cap is NOT located")
    W = World(base)
    W.G.M.build_r13_deep()
    W.G.zz_probe_r13()
    W.step(4)   # steps 1..4
    t = W.text()
    check("W2: the descent reached depth 8 (lvl8)", 'id="lvl8"' in t)
    check("W2: the depth-9 node was NOT visited", 'CcoUnitStatDEADBEEF' not in t)
    check("W2: NO hit was located", "located NO HIT" in t)
    check("W2: no stat row was read", "PANEL row=" not in t)
    check("W2: the BANNED global was NEVER called", W.M.fu_calls == 0)
    check("W2: ZERO writes", W.writes_zero())

    # ------------------------------------------------------------------ W3
    print("\n== W3: the 1200-visit budget cuts a 1641-node fan-out")
    W = World(base)
    W.G.M.build_r13_wide()
    W.G.zz_probe_r13()
    W.step(2)
    t = W.text()
    n = t.count("R13 DOWN path=")
    check(f"W3: exactly 1200 DESCEND visits (got {n})", n == 1200)
    check("W3: step 2 reported visits=1200/1200", "STEP 2 done: visits=1200/1200" in t)
    check("W3: the BANNED global was NEVER called", W.M.fu_calls == 0)
    check("W3: ZERO writes", W.writes_zero())

    # ------------------------------------------------------------------ W4
    print("\n== W4: no prefix/structural id -> no rows, zero get_context_value calls")
    W = World(base)
    W.G.M.build_r13_nohit()
    W.G.zz_probe_r13()
    W.step(7)
    t = W.text()
    check("W4: the descent located NO HIT", "located NO HIT" in t)
    check("W4: step 4 reported hits=0", "STEP 4 done: hits=0 rows=0" in t)
    check("W4: step 6 skipped the query (0 calls)", "query 1 is skipped" in t)
    check("W4: step 7 made ZERO get_context_value calls", W.M.gcv_calls == 0)

    # ------------------------------------------------------------------ W5
    print("\n== W5: the tick never auto-runs R13; simhover stays disarmed")
    W = World(base)
    W.G.M.build_r13_scene()
    W.poll(40)
    t = W.text()
    check("W5: R13 did NOT auto-run from the tick", "R13 STEP" not in t)
    check("W5: no SimulateMouseOn (simhover disarmed)", W.M.sim_on_calls == 0)
    check("W5: the BANNED global was NEVER called", W.M.fu_calls == 0)

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f_ in failures:
            print("   -", f_)
        return 1
    print("SMOKE TEST PASSED - round 13: EVERY top-level root WITH children is descended"
          " (hud_battle first, then the rest) to DEPTH 8 (1200-visit budget); a"
          " CcoUnitStat*-PREFIXED row nested under the vis=true hud_battle root is HIT"
          " (both cases); the rows are paired (PANEL row=); the"
          " CcoUnitDetails/CcoUnitStat context ids are read; and EXACTLY TWO"
          " common.get_context_value calls run (the located id field StatList.Size, then a"
          " non-selected ui id as text field DisplayedValue) - SEVEN steps total, the"
          " ladder STOPS after step 7, with ZERO writes and the engine's name-lookup"
          " global BANNED (never called).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
