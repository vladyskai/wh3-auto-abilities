"""Offline smoke test for the ROUND-12 zz_probe_ui_text probe.
Run:
    cd C:/Users/vlady/Desktop/WH3_mod/tools && uv run --with lupa python lua_smoke_ui_probe_v10.py

Worlds (independent lupa runtimes, mock engine tree):
  W0 static: the R12 tokens exist; the BANNED name-lookup global is ABSENT from
     the source; the descend budget is 800 and the depth is 8; the total step
     count (6) is stated; no string.find call; zero SetContextObject call sites.
  W1 main: steps 1-6 run SAFELY, one armed step per call. Step 1 lists the roots;
     step 2 keeps the NUMERIC unit-id nodes as seeds; step 3 descends a unit-id
     subtree to DEPTH 8 (800-visit budget) and FINDS the stat rows at depths 5-8;
     step 4 locates + pairs the rows (Armour 85 / Leadership 60 / Deep Name 777);
     step 5 reads the CcoUnitDetails/CcoUnitStat/CcoBattleUnit context ids; step
     6 makes EXACTLY TWO common.get_context_value calls (selected ctx id, then a
     non-selected ui id). Every native call is preceded by an 'R12 CALL' line.
     The 7th call is the DONE transition; the 8th is ignored (no wrap-around).
  W2 depth cap: a stat_name at depth 10 is NOT located (the descent stops at 8).
  W3 visit budget: a 931-node fan-out is cut off at exactly 800 visits.
  W4 no seeds: unit_id_holder with no numeric children aborts step 3 cleanly and
     step 6 makes ZERO get_context_value calls.
  W5 disarm: driving the tick never auto-runs R12; simhover stays disarmed.
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
PRELUDE = os.path.join(HERE, "mock_ui_prelude_v7.lua")
ADDITIONS = os.path.join(HERE, "mock_r12_additions.lua")
LOG_FILE = "zz_probe_ui_text_log.txt"
R12_TAG = "[zz_probe_ui_text] R12 "

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def r12_lines(text):
    return [ln for ln in text.splitlines() if R12_TAG in ln]


def every_preceded_by_call(text, marker):
    """Every R12 line containing `marker` must, as the PREVIOUS R12 line, carry an
    'R12 CALL' line - proving the native call was logged before it was made."""
    lines = r12_lines(text)
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
        self.dir = tempfile.mkdtemp(prefix="r12_", dir=base)
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
            last = self.G.zz_probe_r12_step()
        return last

    def writes_zero(self):
        M = self.M
        return (M.setctx_calls == 0 and M.select_calls == 0 and M.cco_calls == 0
                and M.sim_on_calls == 0 and M.sim_off_calls == 0)

    def trips_zero(self):
        return self.rt.eval("#trips") == 0


def main():
    base = tempfile.mkdtemp(prefix="zz_probe_ui_smoke12_")

    # ------------------------------------------------------------------ W0
    print("\n== W0: static round-12 tokens + the BAN on the name-lookup global")
    SRC = open(PROBE, encoding="utf-8", errors="replace").read()
    check("W0: the BANNED name-lookup global is ABSENT", "find_uicomponent" not in SRC)
    for tok in ("ROUND 12", "zz_probe_r12", "zz_probe_r12_step", "zz_probe_r12_auto",
                "zz_probe_r12_status", "zz_probe_r12_help",
                "ROOTCOUNT", "UNITIDCHILD", "DOWN ", "LOCATED ",
                "PANEL row=", "CTXID ", "QUERY sel=", "QUERY nonsel=",
                "R12 TOTAL STEPS 6", "descend_visits", "descend_depth",
                "unit_id_holder", "is_numeric", "total_steps",
                "common.get_context_value", "GetContextObjectId", "StatList.Size"):
        check(f"W0: source carries {tok!r}", tok in SRC)
    check("W0: descend budget is 800", "descend_visits  = 800" in SRC)
    check("W0: descend depth is 8", "descend_depth   = 8" in SRC)
    check("W0: total step count is 6", "total_steps     = 6" in SRC)
    check("W0: before-call logger present", 'R12.out("CALL "' in SRC)
    check("W0: wrap() rejects a boolean", "if raw == nil or raw == false then return nil end" in SRC)
    check("W0: no string.find() call", "string.find(" not in SRC)
    check("W0: ZERO SetContextObject call site", SRC.count(":SetContextObject(") == 2)

    # ------------------------------------------------------------------ W1
    print("\n== W1: unit-id descent to depth 8 -> rows -> ctx ids -> TWO queries")
    W = World(base)
    W.G.M.build_r12_scene()
    res = W.G.zz_probe_r12()
    check("W1: zz_probe_r12() reports READY", "READY" in str(res))
    check("W1: the instruction states 6 total steps", "R12 TOTAL STEPS 6" in str(res))
    check("W1: the instruction says step 6 is the LAST step", "LAST step" in str(res))

    W.step(1)
    t = W.text()
    check("W1: step 1 header (1/6)", "R12 STEP 1/6" in t)
    check("W1: step 1 root count == 10 roots", "R12 ROOTCOUNT 10" in t)
    check("W1: step 1 surfaced unit_id_holder", 'id="unit_id_holder"' in t)
    ok, hits = every_preceded_by_call(t, "R12 ROOT 0 id=")
    check("W1: the first ROOT read is preceded by an R12 CALL line", ok and hits == 1)

    W.step(1)
    t = W.text()
    check("W1: step 2 header (2/6)", "R12 STEP 2/6" in t)
    for uid_ in ("1001", "1002", "1003"):
        check(f"W1: step 2 lists the unit-id child {uid_!r}",
              f'UNITIDCHILD' in t and f'id="{uid_}"' in t)
    check("W1: step 2 tags the numeric unit ids", 'numeric=true' in t)
    check("W1: step 2 kept 3 numeric seeds", "3 numeric unit-id seed(s)" in t)
    ok, hits = every_preceded_by_call(t, "R12 UNITIDCHILD ")
    check("W1: every UNITIDCHILD line is preceded by an R12 CALL line", ok and hits == 3)

    W.step(1)
    t = W.text()
    check("W1: step 3 header (3/6)", "R12 STEP 3/6" in t)
    check("W1: step 3 header states the depth-8 / 800 budget",
          "800 visits" in t and "depth 8" in t)
    # the descent reaches the stat rows at depth 5 and all the way down to depth 8
    check("W1: the descent reached template_stat at depth 5",
          'R12 DOWN path="unit_id_holder/1001/modular_parent/health_and_stats_parent/dynamic_stats/template_stat" id="template_stat"'
          in t)
    check("W1: the descent reached a stat_name at DEPTH 8",
          'R12 DOWN path="unit_id_holder/1001/modular_parent/deep3/deep4/deep5/deep6/template_stat/stat_name" id="stat_name"'
          in t)
    check("W1: step 3 located the panel nodes",
          "STEP 3 done: visits=" in t and " located=0" not in t)
    check("W1: step 3 stayed inside the 800-visit budget",
          "STEP 3 done: visits=" in t and int(t.split("STEP 3 done: visits=")[1].split(" ")[0]) <= 800)
    ok, hits = every_preceded_by_call(t, "R12 DOWN path=")
    check("W1: every DOWN line is preceded by an R12 CALL line", ok and hits > 0)

    W.step(1)
    t = W.text()
    check("W1: step 4 header (4/6)", "R12 STEP 4/6" in t)
    check("W1: step 4 logged the located path (dynamic_stats)",
          'R12 LOCATED path=' in t and 'id="dynamic_stats"' in t)
    check("W1: step 4 paired row 1 (Armour 85)",
          'PANEL row=1 name="Armour" value="85"' in t)
    check("W1: step 4 paired row 2 (Leadership 60)",
          'PANEL row=2 name="Leadership" value="60"' in t)
    check("W1: step 4 paired the depth-8 row (Deep Name 777)",
          'PANEL row=3 name="Deep Name" value="777"' in t)
    ok, hits = every_preceded_by_call(t, "R12 PANEL row=")
    check("W1: every PANEL row is preceded by an R12 CALL line", ok and hits == 3)

    W.step(1)
    t = W.text()
    check("W1: step 5 header (5/6)", "R12 STEP 5/6" in t)
    check("W1: step 5 read a CcoUnitDetails context id", 'CTXID ' in t and "CcoUnitDetails" in t)
    check("W1: step 5 surfaced the panel's CcoUnitDetails id 5001", '-> "5001"' in t)
    check("W1: step 5 surfaced a CcoUnitStat id", "CcoUnitStat" in t)
    check("W1: step 5 read the CcoBattleUnit type", "CcoBattleUnit" in t)
    check("W1: step 5 identified the SELECTED unit ui id 1001", 'selected_ui="1001"' in t)
    ok, hits = every_preceded_by_call(t, "R12 CTXID ")
    check("W1: every CTXID line is preceded by an R12 CALL line", ok and hits > 0)

    ret6 = W.step(1)
    t = W.text()
    check("W1: step 6 header (6/6)", "R12 STEP 6/6" in t)
    check("W1: step 6 QUERY sel", "R12 QUERY sel=" in t and "type=CcoUnitDetails" in t)
    check("W1: step 6 QUERY nonsel", "R12 QUERY nonsel=" in t and "type=CcoBattleUnit" in t)
    check("W1: step 6 used the StatList.Size field", "field=StatList.Size" in t)
    check("W1: step 6 used the non-selected ui id 1002 as text", 'QUERY nonsel="1002"' in t)
    check("W1: step 6 made EXACTLY TWO get_context_value calls", W.M.gcv_calls == 2)
    check("W1: step 6 reported 'calls=2'", "get_context_value calls=2" in t)
    ok, hits = every_preceded_by_call(t, "R12 QUERY sel=")
    check("W1: the selected QUERY is preceded by an R12 CALL line", ok and hits == 1)
    ok, hits = every_preceded_by_call(t, "R12 QUERY nonsel=")
    check("W1: the nonsel QUERY is preceded by an R12 CALL line", ok and hits == 1)
    check("W1: the step-6 return tells the user to STOP",
          "DONE - STOP" in str(ret6) and "6/6" in str(ret6))

    # the 7th call is the DONE transition; the 8th is ignored (no wrap-around)
    W.step(1)
    t = W.text()
    check("W1: run-done banner", "ROUND 12 RUN done after 6 steps" in t)
    check("W1: done banner states YOU ARE DONE", "YOU ARE DONE" in t)
    check("W1: no step 7 header (no wrap-around)", "R12 STEP 7" not in t)
    W.step(1)
    t = W.text()
    check("W1: an 8th call is ignored", "step ignored: the run is done" in t)
    check("W1: still no step 7 header", "R12 STEP 7" not in t)
    check("W1: the ignored call made no extra queries", W.M.gcv_calls == 2)
    check("W1: the BANNED global was NEVER called", W.M.fu_calls == 0)
    check("W1: UIComponent(boolean) was NEVER called", W.M.uic_bool_calls == 0)
    check("W1: ZERO writes (no context/selection/sim)", W.writes_zero())
    check("W1: ZERO UI-state setters", W.trips_zero())

    # ------------------------------------------------------------------ W2
    print("\n== W2: a stat node BEYOND the depth-8 cap is NOT located")
    W = World(base)
    W.G.M.build_r12_deep()
    W.G.zz_probe_r12()
    W.step(4)   # steps 1..4
    t = W.text()
    check("W2: the descent reached depth 8 (lvl8)", 'id="lvl8"' in t)
    check("W2: the depth-9 node was NOT visited", 'id="lvl9"' not in t)
    check("W2: the depth-10 stat_name 'TOO DEEP' was NOT found", "TOO DEEP" not in t)
    check("W2: NO panel component was located", "located NO stat-row node" in t)
    check("W2: no stat row was read", "PANEL row=" not in t)
    check("W2: the BANNED global was NEVER called", W.M.fu_calls == 0)
    check("W2: ZERO writes", W.writes_zero())

    # ------------------------------------------------------------------ W3
    print("\n== W3: the 800-visit budget cuts a 931-node fan-out")
    W = World(base)
    W.G.M.build_r12_wide()
    W.G.zz_probe_r12()
    W.step(3)
    t = W.text()
    n = t.count("R12 DOWN path=")
    check(f"W3: exactly 800 DESCEND visits (got {n})", n == 800)
    check("W3: step 3 reported visits=800", "STEP 3 done: visits=800" in t)
    check("W3: the BANNED global was NEVER called", W.M.fu_calls == 0)
    check("W3: ZERO writes", W.writes_zero())

    # ------------------------------------------------------------------ W4
    print("\n== W4: no numeric unit-id seed -> step 3 aborts, step 6 makes no call")
    W = World(base)
    W.G.M.build_r12_noseed()
    W.G.zz_probe_r12()
    W.step(6)
    t = W.text()
    check("W4: step 3 aborted for lack of a seed", "STEP 3 aborted: no numeric unit-id seed" in t)
    check("W4: step 6 skipped both queries (0 calls)", "0 calls made" in t)
    check("W4: ZERO get_context_value calls", W.M.gcv_calls == 0)
    check("W4: the BANNED global was NEVER called", W.M.fu_calls == 0)

    # ------------------------------------------------------------------ W5
    print("\n== W5: the tick never auto-runs R12; simhover stays disarmed")
    W = World(base)
    W.G.M.build_r12_scene()
    W.poll(40)
    t = W.text()
    check("W5: R12 did NOT auto-run from the tick", "R12 STEP" not in t)
    check("W5: no SimulateMouseOn (simhover disarmed)", W.M.sim_on_calls == 0)
    check("W5: the BANNED global was NEVER called", W.M.fu_calls == 0)

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f_ in failures:
            print("   -", f_)
        return 1
    print("SMOKE TEST PASSED - round 12: the descent is SEEDED on the numeric unit-id"
          " nodes under unit_id_holder and reaches DEPTH 8 (800-visit budget), finding"
          " the stat rows at depths 5-8; the rows are located and paired; the"
          " CcoUnitDetails/CcoUnitStat/CcoBattleUnit context ids are read; and EXACTLY"
          " TWO common.get_context_value calls run (selected ctx id, then a non-selected"
          " ui id) - SIX steps total, the ladder STOPS after step 6, with ZERO writes"
          " and the engine's name-lookup global BANNED (never called).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
