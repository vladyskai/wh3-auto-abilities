"""Offline smoke test for the ROUND-5 zz_probe_ui_text probe (THE CROSS-UNIT
EXPERIMENT: can the stat panel be pointed at a NON-selected unit?).

Runs the REAL probe source in independent lupa Lua runtimes against a MUTABLE
mock UI tree (one world per runtime = fresh caps) and asserts:

  W1  panel NOT visible -> NO automatic run, NO experiment write; a manual run
      aborts cleanly BEFORE any write (the only-when-visible gate).
  W2  panel visible -> the auto run fires ONCE; all four tests are labelled
      blocks in order; R5.2 tries the exact candidate order (selected unit's
      script_unit / battle_unit / ui id number / ui id text / cco(...), then
      the same five for a NON-selected unit); a driver-armed value change is
      DETECTED and the original context object is set BACK; R5.3 select_in_ui
      swaps the selection and the panel is re-read; R5.4 SimulateMouseOn and
      SimulateMouseOff pair up; every experiment write's mock call count
      equals its pre-write log marker count; trips == 0 (no UI-state setter).
  W3a/W3b/W3c  the hard caps fire exactly at their limits (sets 20 / selects 6
      / sims 6) and no write happens past a cap.
  W4  hostile engine (every experiment call raises) -> rejections are logged,
      the run still completes, MouseOff is still attempted, trips == 0.

Usage:  cd <this dir> && uv run --with lupa python lua_smoke_ui_probe_v5.py
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
PRELUDE = os.path.join(HERE, "mock_ui_prelude_v5.lua")
LOG_FILE = "zz_probe_ui_text_log.txt"

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


class World:
    """One fresh lupa runtime + mock tree + the REAL probe source, its own
    working directory and log file."""

    def __init__(self, base):
        self.dir = tempfile.mkdtemp(prefix="w5_", dir=base)
        os.chdir(self.dir)
        self.rt = lupa.LuaRuntime(unpack_returned_tuples=True)
        with open(PRELUDE, "r", encoding="utf-8") as f:
            self.rt.execute(f.read())
        with open(PROBE, "r", encoding="utf-8") as f:
            self.rt.execute(f.read())
        self.G = self.rt.globals()
        self.M = self.G.M
        self.log_path = os.path.join(self.dir, LOG_FILE)
        self.lua_len = self.rt.eval("function(t) return #t end")
        self.lua_tostring = self.rt.eval("function(v) return tostring(v) end")

    def text(self):
        try:
            with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def count(self, sub):
        return self.text().count(sub)

    def tick(self, n=1):
        for _ in range(n):
            self.G.poll_fn()

    def tick_until(self, pred, max_ticks=8000, chunk=10):
        done = 0
        while done < max_ticks:
            self.tick(chunk)
            done += chunk
            if pred():
                return True
        return pred()

    def zeros(self):
        M = self.M
        return (M.getctx_calls == 0 and M.getctxid_calls == 0 and M.setctx_calls == 0
                and M.select_calls == 0 and M.sim_on_calls == 0 and M.sim_off_calls == 0
                and M.cco_calls == 0)


def scene(W, with_panel=True, hidden_stat=False, hostile=False, effect_at=None):
    """Build the battle scene: two cards, two units, and (by default) an open
    stat panel whose values are Range=42 / Armour=85."""
    rt, M = W.rt, W.M
    M.local_units = rt.table(1001, 1002)
    review = M.new("review_DY")
    card1 = M.new("1001", rt.table(callback_id="UnitCard", state="selected"))
    card2 = M.new("1002", rt.table(callback_id="UnitCard", state="active"))
    M.attach(review, card1)
    M.attach(review, card2)
    M.attach(M.hud, review)
    if with_panel:
        panel = M.new("dynamic_stats", rt.table(visible=True))
        for name, value in (("Range", "42"), ("Armour", "85")):
            row = M.new("template_stat")
            M.attach(row, M.new("stat_name", rt.table(stext=name)))
            M.attach(row, M.new("dy_value", rt.table(stext=value)))
            M.attach(panel, row)
        M.attach(panel, M.new("label_compare",
                              rt.table(stext="+100", state="positive", visible=True)))
        if hostile:
            panel.getctx_raises = True
            panel.getctxid_raises = True
            panel.setctx_raises = True
        M.attach(M.hud, panel)
    if hidden_stat:
        M.attach(M.hud, M.new("CcoUnitStat5755085424", rt.table(visible=True)))
    if effect_at is not None:
        M["setctx_effect_at"] = effect_at
    if hostile:
        card1.sim_raises = True
        card2.sim_raises = True
        M["select_raises"] = True
    return card1, card2


def world_hidden(base):
    print("\n== W1: the stat panel is NOT visible -> no run, no writes")
    W = World(base)
    scene(W, with_panel=False, hidden_stat=True)
    W.tick(60)
    t = W.text()
    check("W1: no R5 run even with other stat components visible",
          "R5 RUN" not in t)
    check("W1: zero experiment API calls (not even a context read)", W.zeros())
    res = W.G.zz_probe_r5()
    check("W1: the manual hook queues the run", "queued" in res)
    W.tick(6)
    t = W.text()
    check("W1: the run ABORTS before any write (panel absent)",
          "R5 RUN #1 ABORTED: the stat panel (dynamic_stats) was not found" in t)
    check("W1: still zero experiment API calls after the manual run", W.zeros())
    check("W1: no UI-state setter was ever called (trips == 0)", W.rt.eval("#trips") == 0)


def world_full(base):
    print("\n== W2: panel visible -> auto full run (order, change detection, restore)")
    W = World(base)
    scene(W, with_panel=True, effect_at=3)
    ok = W.tick_until(lambda: "R5 RUN #1 (auto, mode full)" in W.text(),
                      max_ticks=150, chunk=3)
    check("W2: the auto run queues when the panel becomes visible", ok)
    done = W.tick_until(lambda: "R5 RUN #1 (auto, mode full) DONE" in W.text(),
                        max_ticks=8000, chunk=20)
    check("W2: the auto run completes", done)
    t = W.text()
    M = W.M

    p1 = t.find("TEST 1: GetContextObject reads (READ-ONLY)")
    p2 = t.find("TEST 2: SetContextObject candidates")
    p3 = t.find("TEST 3: select_in_ui on a non-selected unit")
    p4 = t.find("TEST 4: SimulateMouseOn on another card")
    check("W2: all four test blocks present, labelled and ordered", -1 < p1 < p2 < p3 < p4)

    names = [
        "candidate: sel script_unit [",
        "candidate: sel battle_unit (su.unit) [",
        "candidate: sel ui id (number) [",
        "candidate: sel ui id (text) [",
        "candidate: cco('CcoUnitDetails', sel id number) [",
        "candidate: nonsel script_unit [",
        "candidate: nonsel battle_unit (su.unit) [",
        "candidate: nonsel ui id (number) [",
        "candidate: nonsel ui id (text) [",
        "candidate: cco('CcoUnitDetails', nonsel id number) [",
    ]
    pos = [t.find(n) for n in names]
    check("W2: candidate order exact (sel 4 + cco, then nonsel 4 + cco)",
          all(p >= 0 for p in pos) and pos == sorted(pos))
    check("W2: every candidate write is logged BEFORE it happens",
          t.count(" -> dynamic_stats:SetContextObject") == 10)

    n = W.lua_len(M.setctx_log)
    vals = [M.setctx_log[i + 1]["value"] for i in range(n)]

    def kind(v):
        if isinstance(v, bool) or v is None:
            return str(type(v).__name__)
        if isinstance(v, (int, float)):
            return "number"
        if isinstance(v, str):
            return "string"
        return "handle"

    check(f"W2: exactly 10 candidate sets + 1 restore (got {M.setctx_calls})",
          M.setctx_calls == 11)
    check("W2: candidates 1/2 carry the script_unit / battle_unit handles",
          kind(vals[0]) == "handle" and kind(vals[1]) == "handle")
    check(f"W2: candidate 3 is the ui id as a NUMBER (got {vals[2]!r})",
          kind(vals[2]) == "number" and vals[2] == 1001)
    # candidate #3's set triggers the armed change -> the restore fires RIGHT
    # THERE, before candidate #4 is tried (so later candidates compare against
    # the restored baseline)
    check("W2: the restore call (right after candidate 3) set the ORIGINAL context object back",
          str(W.lua_tostring(vals[3])) == "CCO(CcoUnitDetails):dynamic_stats")
    check(f"W2: candidate 4 is the ui id as TEXT (got {vals[4]!r})",
          kind(vals[4]) == "string" and vals[4] == "1001")
    check("W2: candidate 5 is the cco() object of the selected unit",
          str(W.lua_tostring(vals[5])) == "CCO(CcoUnitDetails):1001")
    check("W2: candidates 6/7 carry the NON-selected unit's handles (got 1002's)",
          kind(vals[6]) == "handle" and kind(vals[7]) == "handle")
    check(f"W2: candidates 8/9 target the NON-selected unit 1002 (got {vals[8]!r}/{vals[9]!r})",
          vals[8] == 1002 and vals[9] == "1002")
    check("W2: candidate 10 is the cco() of the NON-selected unit",
          str(W.lua_tostring(vals[10])) == "CCO(CcoUnitDetails):1002")
    check("W2: the armed value change was DETECTED", "values CHANGED ***" in t)
    check("W2: restore attempted and reported back at baseline",
          "restoring the original context object" in t
          and "restore result: values now back at the original baseline" in t)
    check("W2: the restore log sits between set #3 and set #4",
          t.find("set #3/10") < t.find("restoring the original context object") < t.find("set #4/10"))
    check("W2: TEST 2 finished all 10 candidates",
          "R5.2 TEST 2 done (10 candidate(s) tried)" in t)

    check(f"W2: select_in_ui called exactly once (got {M.select_calls})", M.select_calls == 1)
    check("W2: its pre-write marker appears exactly once",
          t.count("R5.3 calling battle_unit:select_in_ui()") == 1)
    check("W2: the selection swap was observed", "R5.3 selection DID change" in t)
    check("W2: card 1002 became selected", 'id="1002" state="selected"' in t)
    check("W2: card 1001 lost the selection", 'id="1001" state="active"' in t)

    check(f"W2: SimulateMouseOn/Off paired (got {M.sim_on_calls}/{M.sim_off_calls})",
          M.sim_on_calls == 1 and M.sim_off_calls == 1)
    check("W2: the mouse-on pre-write marker appears exactly once",
          t.count("R5.4 calling SimulateMouseOn()") == 1)
    check("W2: the mouse-off release was logged",
          "R5.4 SimulateMouseOff called (the mouse-on is released)" in t)
    check('W2: t4 hovered the NON-selected card after the swap',
          'R5.4 chosen card id="1001"' in t)

    check(f"W2: GetContextObject reads on the panel subtree (>= 6, got {M.getctx_calls})",
          M.getctx_calls >= 6)
    check("W2: the panel's own context id was read", "CTXID:dynamic_stats:CcoUnitDetails" in t)
    check("W2: a returned cco object was logged with its text",
          "CCO(CcoUnitDetails):dynamic_stats" in t)
    check("W2: no UI-state setter was ever called (trips == 0)", W.rt.eval("#trips") == 0)

    W.tick(150)
    check("W2: the automatic run fires exactly once", "R5 RUN #2" not in W.text())
    st = W.G.zz_probe_r5_status()
    check("W2: status reports runs=1/8", "runs=1/8" in st)


def world_set_cap(base):
    print("\n== W3a: the SetContextObject cap fires at 20")
    W = World(base)
    scene(W, with_panel=True)
    done = W.tick_until(lambda: "R5 RUN #1 (auto, mode full) DONE" in W.text(),
                        max_ticks=8000, chunk=20)
    check("W3a: the auto run completes", done)
    check(f"W3a: auto run used 10 sets (got {W.M.setctx_calls})", W.M.setctx_calls == 10)
    W.G.zz_probe_r5_setctx()
    done = W.tick_until(lambda: "R5 RUN #2 (manual, mode 2) DONE" in W.text(),
                        max_ticks=4000, chunk=20)
    check("W3a: a second test-2 run completes", done)
    check(f"W3a: sets now at the cap (got {W.M.setctx_calls})", W.M.setctx_calls == 20)
    W.G.zz_probe_r5_setctx()
    ok = W.tick_until(lambda: "R5.2 set cap reached (20)" in W.text(), max_ticks=400, chunk=5)
    check("W3a: the SET cap line fires on the next test-2 run", ok)
    check(f"W3a: no write past the cap (got {W.M.setctx_calls})", W.M.setctx_calls == 20)


def world_select_cap(base):
    print("\n== W3b: the select_in_ui cap fires at 6")
    W = World(base)
    scene(W, with_panel=True)
    done = W.tick_until(lambda: "R5 RUN #1 (auto, mode full) DONE" in W.text(),
                        max_ticks=8000, chunk=20)
    check("W3b: the auto run completes", done)
    check(f"W3b: auto run used 1 select (got {W.M.select_calls})", W.M.select_calls == 1)
    for i in range(5):
        run = i + 2
        W.G.zz_probe_r5_select()
        ok = W.tick_until(
            lambda run=run: ("R5 RUN #%d (manual, mode 3) DONE" % run) in W.text(),
            max_ticks=2000, chunk=10)
        if not ok:
            check(f"W3b: test-3 run #{run} completes", False)
            break
    check(f"W3b: selects reached the cap (got {W.M.select_calls})", W.M.select_calls == 6)
    W.G.zz_probe_r5_select()
    ok = W.tick_until(lambda: "R5.3 select cap reached (6)" in W.text(), max_ticks=400, chunk=5)
    check("W3b: the SELECT cap line fires", ok)
    check(f"W3b: no select past the cap (got {W.M.select_calls})", W.M.select_calls == 6)


def world_sim_cap(base):
    print("\n== W3c: the SimulateMouseOn cap fires at 6")
    W = World(base)
    scene(W, with_panel=True)
    done = W.tick_until(lambda: "R5 RUN #1 (auto, mode full) DONE" in W.text(),
                        max_ticks=8000, chunk=20)
    check("W3c: the auto run completes", done)
    check(f"W3c: auto run used 1 sim (got {W.M.sim_on_calls})", W.M.sim_on_calls == 1)
    for i in range(5):
        run = i + 2
        W.G.zz_probe_r5_hover()
        ok = W.tick_until(
            lambda run=run: ("R5 RUN #%d (manual, mode 4) DONE" % run) in W.text(),
            max_ticks=2000, chunk=10)
        if not ok:
            check(f"W3c: test-4 run #{run} completes", False)
            break
    check(f"W3c: sims reached the cap (got {W.M.sim_on_calls})", W.M.sim_on_calls == 6)
    W.G.zz_probe_r5_hover()
    ok = W.tick_until(lambda: "R5.4 simulation cap reached (6)" in W.text(), max_ticks=400, chunk=5)
    check("W3c: the SIM cap line fires", ok)
    check(f"W3c: no sim past the cap, Off still paired (got {W.M.sim_on_calls}/{W.M.sim_off_calls})",
          W.M.sim_on_calls == 6 and W.M.sim_off_calls == 6)


def world_hostile(base):
    print("\n== W4: hostile engine -> rejections logged, the run continues")
    W = World(base)
    scene(W, with_panel=True, hostile=True)
    done = W.tick_until(lambda: "R5 RUN #1 (auto, mode full) DONE" in W.text(),
                        max_ticks=8000, chunk=20)
    check("W4: the run completes despite every experiment call raising", done)
    t = W.text()
    check("W4: the SetContextObject rejections are logged",
          "R5.2 set #1 REJECTED" in t and "R5.2 set #10 REJECTED" in t)
    check("W4: the select_in_ui rejection is logged", "R5.3 select_in_ui REJECTED" in t)
    check("W4: the SimulateMouseOn rejection is logged", "R5.4 SimulateMouseOn REJECTED" in t)
    check("W4: SimulateMouseOff still attempted and reported",
          W.M.sim_off_calls == 1 and "R5.4 SimulateMouseOff call failed" in t)
    check(f"W4: all 10 candidates were attempted (got {W.M.setctx_calls})",
          W.M.setctx_calls == 10)
    check("W4: no restore was attempted (no change, no readable object)",
          "restoring the original context object" not in t)
    check("W4: raising context reads are logged as <ERR>", "value=<ERR>" in t)
    check("W4: the four tests still ran to the end", "R5.4 TEST 4 done" in t)
    check("W4: no UI-state setter was ever called (trips == 0)", W.rt.eval("#trips") == 0)


def main():
    base = tempfile.mkdtemp(prefix="zz_probe_ui_smoke5_")

    print("== static source tokens (round 5)")
    with open(PROBE, encoding="utf-8", errors="replace") as f:
        SRC = f.read()
    for tok in (
        "ROUND 5 - THE CROSS-UNIT EXPERIMENT",
        "zz_probe_r5", "zz_probe_r5_context", "zz_probe_r5_setctx",
        "zz_probe_r5_select", "zz_probe_r5_hover", "zz_probe_r5_status", "zz_probe_r5_help",
        "GetContextObject", "GetContextObjectId", "SetContextObject",
        "select_in_ui", "SimulateMouseOn", "SimulateMouseOff",
        "review_DY", "UnitCard", "CcoUnitDetails", "CcoUnitStat",
        "TEST 1: GetContextObject reads (READ-ONLY)",
        "TEST 2: SetContextObject candidates",
        "TEST 3: select_in_ui on a non-selected unit",
        "TEST 4: SimulateMouseOn on another card",
        "R5.2 set cap reached", "R5.3 select cap reached", "R5.4 simulation cap reached",
        "max_runs = 8", "max_sets = 20", "max_selects = 6", "max_sims = 6",
        "settle = 15", "auto_attempts = 3",
        "ABORTED",
    ):
        check(f"source carries {tok!r}", tok in SRC)
    print("== round-3/4 tokens still present (nothing loosened)")
    for tok in ("round 3: mouse-armed capture",
                "ROUND 4: targeted stat dump armed",
                "ComponentMouseOn", "ComponentMouseOff", "AddScriptEventReporter",
                "STAT_MAX_DEPTH    = 20", "STAT_MAX_VISITS   = 3000",
                "zz_probe_stat_dump", "zz_probe_ui_arm"):
        check(f"round-3/4 token still present {tok!r}", tok in SRC)

    world_hidden(base)
    world_full(base)
    world_set_cap(base)
    world_select_cap(base)
    world_sim_cap(base)
    world_hostile(base)

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f_ in failures:
            print("   -", f_)
        return 1
    print("SMOKE TEST PASSED - R5 runs ONLY with the panel visible; the four tests are")
    print("labelled blocks; the candidate order and the change/restore path are exact;")
    print("select_in_ui / SimulateMouseOn write only inside their blocks (Off paired);")
    print("the caps fire at 20/6/6; a hostile engine only produces logged rejections;")
    print("rounds 1-4 untouched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
