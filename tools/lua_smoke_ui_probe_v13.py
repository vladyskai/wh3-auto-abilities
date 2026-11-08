"""Offline smoke test for the ROUND-15 zz_probe_ui_text probe.
Run:
    cd C:/Users/vlady/Desktop/WH3_mod/tools && uv run --with lupa python lua_smoke_ui_probe_v13.py

Worlds (independent lupa runtimes, mock engine tree):
  W0 static: the R14 AND R15 tokens exist; the BANNED name-lookup global is ABSENT;
     no string.find call; zero SetContextObject call sites.
  W1-W7: the ROUND-14 regression worlds (unchanged from v12) - the seeded descent,
     row pairing, the fixed GCV ladders (stop at first success), the walk budget,
     the broken-chain abort and the disarm check all still pass.
  W8 R15 main (effect ON): step A dumps the comparison components + ctx ids and
     records 11 tracked fields (label_compare, compare-named, rowctx, vis) on 3 rows;
     then the four passes run ASYNCHRONOUSLY on the 25 ms poll: SimulateMouseOn is
     issued on the first poll, OFF after exactly hold/25 polls (4/6/10/60), sampling
     every poll. The hovered card's On changes label_compare +2 -> +7 and the row's
     CcoUnitStat ctx id -> BattleUnit_1002; Off reverts both, so every pass logs
     4 change events (2 on, 2 off) with before/after values, the DELTA arithmetic
     line carries selected value + expected hovered, and the verdict raises the
     loud WIN. The busy guard refuses a step while a pass is in flight; the On/Off
     calls alternate and total 4/4.
  W9 R15 no-effect: nothing changes during any pass -> every pass changed=0, no
     HOVER lines, the verdict says 'no invisible exposure; control_changed=0',
     no WIN - and the pairs still total 4/4 (Off always follows On).
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
PRELUDE = os.path.join(HERE, "mock_ui_prelude_v7.lua")
ADDITIONS14 = os.path.join(HERE, "mock_r14_additions.lua")
ADDITIONS15 = os.path.join(HERE, "mock_r15_additions.lua")
LOG_FILE = "zz_probe_ui_text_log.txt"
R14_TAG = "[zz_probe_ui_text] R14 "
R15_TAG = "[zz_probe_ui_text] R15 "

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def tagged_lines(text, tag):
    return [ln for ln in text.splitlines() if tag in ln]


def preceded_ok(text, tag, marker):
    """Every log line containing `marker` is immediately preceded by a CALL line."""
    lines = tagged_lines(text, tag)
    ok, hits = True, 0
    for i, ln in enumerate(lines):
        if marker in ln:
            hits += 1
            if i == 0 or " CALL " not in lines[i - 1]:
                ok = False
    return ok, hits


class World:
    def __init__(self, base):
        self.dir = tempfile.mkdtemp(prefix="r15_", dir=base)
        os.chdir(self.dir)
        self.rt = lupa.LuaRuntime(unpack_returned_tuples=True)
        for path in (PRELUDE, ADDITIONS14, ADDITIONS15, PROBE):
            with open(path, encoding="utf-8") as f:
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

    def r15step(self, n=1):
        last = None
        for _ in range(n):
            last = self.G.zz_probe_r15_step()
        return last

    def r15poll(self, n=1):
        for _ in range(n):
            self.G.zz_probe_r15_poll()

    def writes_zero(self):
        M = self.M
        return (M.setctx_calls == 0 and M.select_calls == 0 and M.cco_calls == 0
                and M.sim_on_calls == 0 and M.sim_off_calls == 0)

    def writes_zero_r15(self):
        """Zero context/selection writes; sim calls only the paired passes."""
        M = self.M
        return (M.setctx_calls == 0 and M.select_calls == 0 and M.cco_calls == 0)

    def trips_zero(self):
        return self.rt.eval("#trips") == 0

    def sim_seq(self):
        raw = self.rt.eval('table.concat(M.calls, "|")')
        return [c for c in str(raw).split("|") if c.startswith("SimulateMouse")]


def main():
    base = tempfile.mkdtemp(prefix="zz_probe_ui_smoke15_")

    # ------------------------------------------------------------------ W0
    print("\n== W0: static round-14 + round-15 tokens + the BAN on the name-lookup global")
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
        check(f"W0: source carries R14 token {tok!r}", tok in SRC)
    check("W0: the R14 walk budget is 300", "walk_visits         = 300" in SRC)
    check("W0: the R14 walk depth is 6", "walk_depth          = 6" in SRC)
    check("W0: the R14 total step count is 8", "total_steps         = 8" in SRC)
    check("W0: before-call logger present", 'R14.out("CALL "' in SRC)
    check("W0: no string.find() call", "string.find(" not in SRC)
    check("W0: ZERO SetContextObject call site", SRC.count(":SetContextObject(") == 2)

    # ---- round-15 static tokens
    for tok in ("ROUND 15", "zz_probe_r15", "zz_probe_r15_step", "zz_probe_r15_status",
                "zz_probe_r15_help", "zz_probe_r15_poll",
                "R15 TOTAL STEPS 7", "CMP row=", "CMPB", "CMPG",
                "CTXROW row=", "CTXID row=", "TRACK row=", "TARGET card=",
                "BASELINE rows=", "HOVER pass=", "PASS n=", "PAIRS sim_on=",
                "VERDICT pass1_changed=", "DELTA pass=",
                "*** WIN: hover exposes non-selected stats INVISIBLY ***",
                "no invisible exposure; control_changed=",
                "SIMHOVER SimulateMouseOn pass=", "SIMHOVER SimulateMouseOff pass=",
                "zz_probe_r15_poll", "label_compare", "comparison-named", "rowctx",
                "GetContextObjectId", "GetStateText", "SimulateMouseOn", "SimulateMouseOff",
                "tooltip draw delay", "first_evidence", "first_text", "hovered_expected"):
        check(f"W0: source carries R15 token {tok!r}", tok in SRC)
    check("W0: the R15 step hooks are functions",
          "function zz_probe_r15(" in SRC and "function zz_probe_r15_step(" in SRC
          and "function zz_probe_r15_poll(" in SRC)
    check("W0: the R15 holds are 100/150/250/1500", "holds               = { 100, 150, 250, 1500 }" in SRC)
    check("W0: the R15 total step count is 7", "total_steps         = 7," in SRC)
    check("W0: the R15 poll cadence is 25 ms", "poll_ms             = 25," in SRC)
    check("W0: the R15 tooltip-delay constant is 250 ms", "visible_ms          = 250," in SRC)
    check("W0: the R15 poll registration is present", "bm:repeat_callback(zz_probe_r15_poll, R15.poll_ms, R15.poll_name)" in SRC)

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
    check("W1: the walk reached row_header_stats", 'id="row_header_stats"' in t)
    check("W1: step 1 done line", "STEP 1 done: chain links=7 walked=" in t)
    ok, hits = preceded_ok(t, R14_TAG, "R14 SEED link ")
    check("W1: every SEED line is preceded by a CALL line", ok and hits == 7)
    ok, hits = preceded_ok(t, R14_TAG, "R14 DOWN path=")
    check("W1: every DOWN line is preceded by a CALL line", ok and hits > 0)

    W.step(1)
    t = W.text()
    check("W1: step 2 header (2/8)", "R14 STEP 2/8" in t)
    check("W1: step 2 paired row 1 (Melee Defence 53)",
          'PANEL row=1 name="Melee Defence" value="53" rowid="template_stat"' in t)
    check("W1: step 2 paired row 3 (Movement 5.2, the stat_name-child row)",
          'PANEL row=3 name="Movement" value="5.2" rowid="CcoUnitStat5974444112"' in t)
    check("W1: step 2 done line", "STEP 2 done: rows=3" in t)

    W.step(1)
    t = W.text()
    check("W1: step 3 header (3/8)", "R14 STEP 3/8" in t)
    check("W1: step 3 control A = CcoBattleUnit/1001/Name -> Karl Franz",
          'GCV n=1 type=CcoBattleUnit id="1001" field="Name" -> "Karl Franz" [CONTROL]' in t)

    W.step(1)
    t = W.text()
    check("W1: step 4 tried the 5 A rungs and none returned a value",
          "STEP 4 done: LADDER A - no new-format rung returned a value (5 tried)" in t)

    W.step(1)
    t = W.text()
    check("W1: step 5 control B -> the loud WIN(control) line",
          "*** WIN(control): non-selected bare-id CcoBattleUnit field readable ***" in t)
    check("W1: no NEW-format WIN is raised by the control",
          "*** WIN: non-selected unit stat field readable ***" not in t)

    W.step(1)
    W.step(1)
    W.step(1)
    t = W.text()
    check("W1: step 6 tried the 5 BattleUnit_1002 rungs and none returned",
          "STEP 6 done: LADDER B (BattleUnit_1002) - no rung returned a value (5 tried)" in t)
    check("W1: step 7 tried the bare-id rungs and none returned",
          "STEP 7 done: LADDER B (bare 1002) - no rung returned a value" in t)
    ret8 = W.step(1)
    t = W.text()
    check("W1: step 8 header (8/8)", "R14 STEP 8/8" in t)
    check("W1: the verdict reports 14 GCV calls", "VERDICT get_context_value calls=14" in t)
    check("W1: the verdict says NO new-format non-selected field was readable",
          "VERDICT: NO non-selected NEW-format stat field was readable" in t)
    check("W1: NO central-question WIN was raised", "VERDICT: CENTRAL QUESTION ANSWERED" not in t)
    check("W1: EXACTLY 14 get_context_value calls", W.M.gcv_calls == 14)
    check("W1: the step-8 return tells the user to STOP", "DONE - STOP" in str(ret8))
    W.step(1)
    t = W.text()
    check("W1: run-done banner", "ROUND 14 RUN done after 8 steps" in t)
    check("W1: the BANNED global was NEVER called", W.M.fu_calls == 0)
    check("W1: UIComponent(boolean) was NEVER called", W.M.uic_bool_calls == 0)
    check("W1: ZERO writes (no context/selection/sim)", W.writes_zero())
    check("W1: ZERO UI-state setters", W.trips_zero())

    # ------------------------------------------------------------------ W2
    print("\n== W2: the ladder STOPS at the first success (a SELECTED rung answers)")
    W = World(base)
    W.G.M.build_r14_stopA()
    W.G.zz_probe_r14()
    W.step(4)
    t = W.text()
    check("W2: LADDER A stopped at rung 3",
          "LADDER A STOPPED at first success: rung 3/5 CcoUnitDetails/BattleUnit_1001/StatList.Size" in t
          and '= "7"' in t)
    check("W2: exactly 4 GCV calls ran (control + 3 A rungs)", W.M.gcv_calls == 4)
    check("W2: ZERO writes", W.writes_zero())

    # ------------------------------------------------------------------ W3
    print("\n== W3: a NON-selected new-format rung answers -> step 6 WIN, step 7 skipped")
    W = World(base)
    W.G.M.build_r14_win()
    W.G.zz_probe_r14()
    W.step(6)
    t = W.text()
    check("W3: LADDER B stopped at rung 3",
          "LADDER B STOPPED at first success: rung 3/7 CcoUnitDetails/BattleUnit_1002/StatList.Size" in t
          and '= "12"' in t)
    check("W3: the loud non-selected WIN was raised",
          "*** WIN: non-selected unit stat field readable *** type=CcoUnitDetails "
          'id="BattleUnit_1002" field="StatList.Size" value="12"' in t)
    W.step(1)
    t = W.text()
    check("W3: step 7 was skipped because the ladder already stopped",
          "the ladder already stopped" in t)
    check("W3: step 6 made only 3 B calls (10 total)", W.M.gcv_calls == 10)
    W.step(1)
    t = W.text()
    check("W3: the verdict ANSWERS the central question", "VERDICT: CENTRAL QUESTION ANSWERED" in t)
    check("W3: ZERO writes", W.writes_zero())

    # ------------------------------------------------------------------ W4
    print("\n== W4: only the BARE non-selected id answers -> step 7 WIN")
    W = World(base)
    W.G.M.build_r14_bare()
    W.G.zz_probe_r14()
    W.step(7)
    t = W.text()
    check("W4: every BattleUnit_1002 rung failed",
          "STEP 6 done: LADDER B (BattleUnit_1002) - no rung returned a value (5 tried)" in t)
    check("W4: LADDER B (bare) stopped at rung 6",
          "LADDER B STOPPED at first success (bare id): rung 6/7 CcoUnitDetails/1002/StatList.Size" in t
          and '= "9"' in t)

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

    # ------------------------------------------------------------------ W6
    print("\n== W6: the chain breaks -> step 1 aborts, no rows, the ladder still runs")
    W = World(base)
    W.G.M.build_r14_nolist()
    W.G.zz_probe_r14()
    W.step(8)
    t = W.text()
    check("W6: the chain named the missing link",
          'CHAIN link 3/7 id="info_panel_background" NOT FOUND' in t)
    check("W6: the ladder still ran (14 calls)", W.M.gcv_calls == 14)
    check("W6: ZERO writes", W.writes_zero())

    # ------------------------------------------------------------------ W7
    print("\n== W7: the tick never auto-runs R14/R15; simhovers stay disarmed")
    W = World(base)
    W.G.M.build_r14_scene()
    W.poll(40)
    t = W.text()
    check("W7: R14 did NOT auto-run from the tick", "R14 STEP" not in t)
    check("W7: R15 did NOT auto-run from the tick", "R15 STEP" not in t)
    check("W7: no SimulateMouseOn (simhovers disarmed)", W.M.sim_on_calls == 0)
    check("W7: the BANNED global was NEVER called", W.M.fu_calls == 0)

    # ------------------------------------------------------------------ W8
    print("\n== W8: R15 main - baseline dump, the async hold ladder, change detection, WIN")
    W = World(base)
    W.G.M.build_r15_scene_effect()
    res = W.G.zz_probe_r15()
    check("W8: zz_probe_r15() reports READY", "READY" in str(res))
    check("W8: the instruction states 7 total steps", "R15 TOTAL STEPS 7" in str(res))
    check("W8: the instruction says SEVEN times", "SEVEN times" in str(res))
    t = W.text()
    check("W8: the R15 poll registered at 25 ms",
          "R15 poll registered: zz_probe_r15_poll every 25 ms" in t)
    check("W8: the poll is in the mock's registry",
          W.rt.eval('M.polls["zz_probe_r15_poll"] ~= nil') is True)

    ret1 = W.r15step(1)
    t = W.text()
    check("W8: step 1 header (1/7)", "R15 STEP 1/7" in t)
    check("W8: step 1 done in the return", "R15 step 1/7 done (was 0)" in str(ret1))
    check("W8: SEED link 7 resolves `list` on the full path",
          'SEED link 7/7 path="hud_battle/info_panel_parent/info_panel_background/'
          'unit_information/info_parent/info_panel/list" id="list"' in t)
    check("W8: the chain fully resolved", "SEED resolved the FULL chain" in t)
    check("W8: step A logged the row block header", "ROWHEADER " in t and 'id="row_header_stats"' in t)
    check("W8: CMP row 1 (Range 42)", 'CMP row=1 name="Range" value="42" rowid="template_stat"' in t)
    check("W8: CMP row 3 (Movement 5.2, CcoUnitStat* id shape)",
          'CMP row=3 name="Movement" value="5.2" rowid="CcoUnitStat5974444112"' in t)
    check("W8: CMPB dumped row 1's label_compare with its text",
          'CMPB row=1 o=4 id="label_compare" children=0 stext="+2"' in t)
    check("W8: CMPB dumped row 1's comparison_arrow",
          'CMPB row=1 o=5 id="comparison_arrow"' in t)
    check("W8: CMPG found the NESTED label_compare one level deeper",
          'CMPG row=3 o=2 g=0 id="label_compare" children=0 stext="+1"' in t)
    check("W8: CTXROW logged the row's own context ids",
          'CTXROW row=1 CcoUnitStat="CTXID:template_stat:CcoUnitStat" '
          'CcoUnitDetails="CTXID:template_stat:CcoUnitDetails"' in t)
    check("W8: CTXID logged a non-nil child context id",
          'CTXID row=1 o=0 comp="stat_name" type=CcoUnitStat -> "CTXID:stat_name:CcoUnitStat"' in t)
    check("W8: TRACK label_compare base",
          'TRACK row=1 field="label_compare" base="+2"' in t)
    check("W8: TRACK vis:label_compare base",
          'TRACK row=1 field="vis:label_compare" base="true"' in t)
    check("W8: TRACK rowctx base",
          'TRACK row=1 field="rowctx" base="CTXID:template_stat:CcoUnitStat"' in t)
    check("W8: TRACK the SECOND label_compare (row 2, nil text)",
          'TRACK row=2 field="compare:label_compare" base="<nil>"' in t)
    check("W8: TRACK the NESTED label_compare (row 3)",
          'TRACK row=3 field="compare:label_compare" base="+1"' in t)
    check("W8: the target is the NON-selected card 1002",
          'TARGET card="1002" ctx="1002" state="active" | selected_card="1001" cards=2' in t)
    check("W8: the BASELINE summary (3 rows, 11 tracked fields, 34 ctx calls)",
          "BASELINE rows=3 tracked=11 compar_comps=4 ctx_calls=34 "
          'target="1002" selected_card="1001" baseline_ok=true' in t)
    ok, hits = preceded_ok(t, R15_TAG, "R15 CMPB row=")
    check(f"W8: every CMPB line is preceded by a CALL line (hits={hits})", ok and hits == 14)
    ok, hits = preceded_ok(t, R15_TAG, "R15 CMPG row=")
    check(f"W8: every CMPG line is preceded by a CALL line (hits={hits})", ok and hits == 4)
    ok, hits = preceded_ok(t, R15_TAG, "R15 SEED link ")
    check("W8: every SEED line is preceded by a CALL line", ok and hits == 7)
    check("W8: no SimulateMouseOn yet (the pass is armed, not started)", W.M.sim_on_calls == 0)

    # ---- pass 1 (hold 100): arm, On on the first poll, busy guard, Off at 100 ms
    ret2 = W.r15step(1)
    check("W8: step 2 arms pass 1 (hold 100)",
          "R15 step 2/7 done (was 1)" in str(ret2) and "pass 1 armed (hold 100 ms" in str(ret2))
    check("W8: the step-2 return names the INVISIBLE kind",
          "INVISIBLE (below the 250 ms tooltip draw delay)" in str(ret2))
    W.r15poll(1)
    t = W.text()
    check("W8: SimulateMouseOn issued on the first pass poll", W.M.sim_on_calls == 1)
    check("W8: the On is logged BEFORE the call",
          'R15 SIMHOVER SimulateMouseOn pass=1 card="1002" hold=100ms (call 1; logged BEFORE the call)' in t)
    check("W8: first-sample rowctx change (ctx id -> BattleUnit_1002)",
          'R15 HOVER pass=1 hold=100 t=25 row=1 field="rowctx" '
          'was="CTXID:template_stat:CcoUnitStat" now="BattleUnit_1002"' in t)
    check("W8: first-sample label_compare change (+2 -> +7)",
          'R15 HOVER pass=1 hold=100 t=25 row=1 field="label_compare" was="+2" now="+7"' in t)
    check("W8: the DELTA line carries selected value + hovered_expected",
          'R15 DELTA pass=1 row=1 field="label_compare" delta="+7" selected("Range")="42" '
          'hovered_expected="35" (label = selected - hovered)' in t)
    ret2b = W.r15step(1)
    check("W8: a step while the pass is in flight is REFUSED",
          "NOT advanced (still 2/7)" in str(ret2b) and "still in flight" in str(ret2b))
    check("W8: the refusal did not advance the counter", W.rt.eval("R15.step") == 2)
    check("W8: the refusal left the pass alone (no extra On)", W.M.sim_on_calls == 1)
    W.r15poll(3)
    t = W.text()
    check("W8: SimulateMouseOff issued (4 polls = 100 ms hold)", W.M.sim_off_calls == 1)
    check("W8: the Off is logged BEFORE the call",
          'R15 SIMHOVER SimulateMouseOff pass=1 card="1002" (call 1; logged BEFORE the call)' in t)
    check("W8: the Off names its nominal time",
          "R15 PASS n=1 SimulateMouseOff issued at t=100 ms nominal (4 samples so far); settling 300 ms" in t)
    W.r15poll(12)
    t = W.text()
    check("W8: pass 1 finished after 16 polls (4 hold + 12 settle)",
          "R15 PASS n=1 hold=100 done changed=4 fields_dev=2 still_at_end=0 text_dev=1 ctx_dev=1 "
          "vis_dev=0 warns=0 on_ok=true off_ok=true samples=16 polls=16" in t)
    check("W8: the Off revert was caught (settle sample)",
          'R15 HOVER pass=1 hold=100 t=125 row=1 field="label_compare" was="+7" now="+2"' in t)
    check("W8: pass 1 logged exactly 4 change events", t.count('R15 HOVER pass=1 ') == 4)

    # ---- pass 2 (hold 150)
    ret3 = W.r15step(1)
    check("W8: step 3 arms pass 2 (hold 150)",
          "R15 step 3/7 done (was 2)" in str(ret3) and "pass 2 armed (hold 150 ms" in str(ret3))
    W.r15poll(18)
    t = W.text()
    check("W8: pass 2 finished after 18 polls",
          "R15 PASS n=2 hold=150 done changed=4 fields_dev=2 still_at_end=0 text_dev=1 ctx_dev=1 "
          "vis_dev=0 warns=0 on_ok=true off_ok=true samples=18 polls=18" in t)
    check("W8: pass 2 Off at t=150 ms nominal",
          "R15 PASS n=2 SimulateMouseOff issued at t=150 ms nominal" in t)

    # ---- pass 3 (hold 250)
    ret4 = W.r15step(1)
    check("W8: step 4 arms pass 3 (hold 250)",
          "R15 step 4/7 done (was 3)" in str(ret4) and "pass 3 armed (hold 250 ms" in str(ret4))
    W.r15poll(22)
    t = W.text()
    check("W8: pass 3 finished after 22 polls",
          "R15 PASS n=3 hold=250 done changed=4 fields_dev=2 still_at_end=0 text_dev=1 ctx_dev=1 "
          "vis_dev=0 warns=0 on_ok=true off_ok=true samples=22 polls=22" in t)

    # ---- control (hold 1500)
    ret5 = W.r15step(1)
    check("W8: step 5 arms the CONTROL pass (hold 1500)",
          "R15 step 5/7 done (was 4)" in str(ret5) and "pass 4 armed (hold 1500 ms" in str(ret5)
          and "CONTROL (the tooltip WILL draw - expected)" in str(ret5))
    W.r15poll(72)
    t = W.text()
    check("W8: the CONTROL pass was announced for watching",
          "CONTROL pass running - WATCH THE SCREEN NOW" in t)
    check("W8: control finished after 72 polls (60 hold + 12 settle)",
          "R15 PASS n=4 hold=1500 done changed=4 fields_dev=2 still_at_end=0 text_dev=1 ctx_dev=1 "
          "vis_dev=0 warns=0 on_ok=true off_ok=true samples=72 polls=72" in t)
    check("W8: the pair total is 4/4 paired", "R15 PAIRS sim_on=4 sim_off=4 paired=true" in t)
    seq = W.sim_seq()
    check("W8: the On/Off calls alternate, 4 pairs", seq == ["SimulateMouseOn:1002", "SimulateMouseOff:1002"] * 4)

    # ---- verdict + done
    ret6 = W.r15step(1)
    t = W.text()
    check("W8: step 6 header (6/7)", "R15 STEP 6/7" in t)
    check("W8: the verdict line",
          "R15 VERDICT pass1_changed=4 pass2_changed=4 pass3_changed=4 control_changed=4" in t)
    check("W8: the verdict detail",
          "R15 VERDICT detail invisible: text_dev=3 ctx_dev=3 vis_dev=0 | control: "
          "text_dev=1 ctx_dev=1 vis_dev=0 | deltas=4 events_total=16 warns=0" in t)
    check("W8: THE WIN LINE",
          'R15 *** WIN: hover exposes non-selected stats INVISIBLY *** first_evidence pass=1 '
          'row=1 field="label_compare" was="+2" now="+7"' in t)
    check("W8: the delta summary line",
          "R15 VERDICT deltas=4 (see the R15 DELTA lines for the selected value + the hover = selected - delta check)" in t)
    check("W8: the verdict return says win=true", "verdict done (win=true)" in str(ret6))
    ret7 = W.r15step(1)
    t = W.text()
    check("W8: step 7 header (7/7)", "R15 STEP 7/7" in t)
    check("W8: the done line",
          "R15 DONE run #1: sim pairs on=4 off=4 paired=true | events=16 deltas=4 win=true" in t)
    check("W8: the STOP instruction", "R15 TOTAL STEPS 7 - you are done (STOP)" in t)
    check("W8: the 7th return says DONE - STOP", "DONE - STOP" in str(ret7))
    W.r15step(1)
    t = W.text()
    check("W8: the run-done banner", "ROUND 15 RUN done after 7 steps" in t)
    W.r15step(1)
    t = W.text()
    check("W8: an 8th call is ignored", "step ignored: the run is done" in t)
    check("W8: the counter stayed at 7", W.rt.eval("R15.step") == 7)
    check("W8: no read warnings ever fired", "R15 WARN " not in t)
    check("W8: no REBASE drift lines in a clean scene", "R15 REBASE" not in t)
    check("W8: ZERO context/selection writes", W.writes_zero_r15())
    check("W8: ZERO UI-state setters", W.trips_zero())
    check("W8: the BANNED global was NEVER called", W.M.fu_calls == 0)
    check("W8: UIComponent(boolean) was NEVER called", W.M.uic_bool_calls == 0)

    # ------------------------------------------------------------------ W9
    print("\n== W9: R15 no-effect - nothing changes, the verdict must NOT claim a WIN")
    W = World(base)
    W.G.M.build_r15_scene_base()
    W.G.zz_probe_r15()
    W.r15step(1)
    t = W.text()
    check("W9: the BASELINE summary",
          'BASELINE rows=3 tracked=11 compar_comps=4 ctx_calls=34 '
          'target="1002" selected_card="1001" baseline_ok=true' in t)
    W.r15step(1)
    W.r15poll(16)
    W.r15step(1)
    W.r15poll(18)
    W.r15step(1)
    W.r15poll(22)
    W.r15step(1)
    W.r15poll(72)
    t = W.text()
    check("W9: pass 1 all zeros",
          "R15 PASS n=1 hold=100 done changed=0 fields_dev=0 still_at_end=0 text_dev=0 ctx_dev=0 "
          "vis_dev=0 warns=0 on_ok=true off_ok=true samples=16 polls=16" in t)
    check("W9: pass 4 (control) all zeros",
          "R15 PASS n=4 hold=1500 done changed=0 fields_dev=0 still_at_end=0 text_dev=0 ctx_dev=0 "
          "vis_dev=0 warns=0 on_ok=true off_ok=true samples=72 polls=72" in t)
    check("W9: no HOVER line anywhere", "R15 HOVER" not in t)
    check("W9: no DELTA line anywhere", "R15 DELTA" not in t)
    check("W9: the pair total is 4/4 paired", "R15 PAIRS sim_on=4 sim_off=4 paired=true" in t)
    check("W9: no REBASE drift lines", "R15 REBASE" not in t)
    W.r15step(1)
    t = W.text()
    check("W9: the verdict line",
          "R15 VERDICT pass1_changed=0 pass2_changed=0 pass3_changed=0 control_changed=0" in t)
    check("W9: the NO-exposure line",
          "R15 no invisible exposure; control_changed=0" in t)
    check("W9: NO WIN was claimed", "*** WIN: hover exposes non-selected stats INVISIBLY ***" not in t)
    W.r15step(1)
    t = W.text()
    check("W9: the done line", "R15 TOTAL STEPS 7 - you are done (STOP)" in t)
    check("W9: ZERO context/selection writes", W.writes_zero_r15())
    check("W9: the On/Off pairs still alternate, 4 pairs",
          W.sim_seq() == ["SimulateMouseOn:1002", "SimulateMouseOff:1002"] * 4)

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f_ in failures:
            print("   -", f_)
        return 1
    print("SMOKE TEST PASSED - round 15: the invisible-hover/control experiment.")
    print("  Step A dumps every stat row's comparison components + context ids (read-only); the")
    print("  four passes run on the 25 ms poll with SimulateMouseOn/Off paired (4/4), holds 100/")
    print("  150/250/1500 ms (Off at exactly hold/25 polls); changes in label_compare text,")
    print("  comparison-named text and the row's CcoUnitStat context id are logged with before/")
    print("  after values; the delta arithmetic carries selected value + expected hovered; the")
    print("  verdict raises the WIN on an invisible exposure and stays silent on a clean scene.")
    print("  SEVEN steps total, ZERO context writes, name-lookup helper BANNED (never called).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
