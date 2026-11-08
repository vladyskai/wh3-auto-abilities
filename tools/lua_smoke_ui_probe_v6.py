"""Offline smoke test for the ROUND-7 zz_probe_ui_text probe (ZERO-WRITE READS
+ the slimmed walks). Run:
    cd C:/Users/vlady/Desktop/WH3_mod/tools && uv run --with lupa python lua_smoke_ui_probe_v6.py

Worlds (independent lupa runtimes, mutable mock tree):
  W1  static: the round-7 tokens exist; every former write-call site is GONE;
      the safety windows are GONE; the slim caps are in.
  W2  panel NOT visible + nothing armed -> NO R7 reads at all; the manual R5
      run aborts before anything; a manual R7 sweep reads nothing.
  W3  panel visible -> the R7 sweep reads BOTH cards (selected "1001" and the
      NON-selected "1002") through common.get_context_value, logs values
      change-only (a mutation is detected; an identical sweep is silent), and
      performs ZERO writes (setctx/select/sim/cco all 0; trips == 0).
  W4  hover: a ComponentMouseOn on the other card arms a mouse capture; the
      sweep reads the hovered card and the panel's label_compare rows (the
      comparison deltas), change-only.
  W5  hostile: get_context_value raises -> the error is logged ONCE per field,
      the sweep continues, zero writes.
  W6  slim dump: a 300-child panel still costs at most the 200-visit budget
      (the budget line fires once).
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
PRELUDE = os.path.join(HERE, "mock_ui_prelude_v6.lua")
LOG_FILE = "zz_probe_ui_text_log.txt"

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


class World:
    def __init__(self, base):
        self.dir = tempfile.mkdtemp(prefix="w7_", dir=base)
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

    def tick_until(self, pred, max_ticks=400, chunk=2):
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

    def writes_zero(self):
        """ROUND 7: the invariant is ZERO WRITES - the read calls (GetContextObjectId
        / get_context_value) are the point of the build and are expected."""
        M = self.M
        return (M.setctx_calls == 0 and M.select_calls == 0 and M.sim_on_calls == 0
                and M.sim_off_calls == 0 and M.cco_calls == 0)


def scene(W, with_panel=True):
    """Two cards (1001 selected, 1002 active) + an open stat panel whose rows
    are Range=42 / Armour=85 and one label_compare (+100)."""
    rt, M = W.rt, W.M
    M.local_units = rt.table(1001, 1002)
    review = M.new("review_DY")
    card1 = M.new("1001", rt.table(callback_id="UnitCard", state="selected"))
    card2 = M.new("1002", rt.table(callback_id="UnitCard", state="active"))
    M.attach(review, card1)
    M.attach(review, card2)
    M.attach(M.hud, review)
    panel = None
    compare = None
    if with_panel:
        panel = M.new("dynamic_stats", rt.table(visible=True))
        for name, value in (("Range", "42"), ("Armour", "85")):
            row = M.new("template_stat")
            M.attach(row, M.new("stat_name", rt.table(stext=name)))
            M.attach(row, M.new("dy_value", rt.table(stext=value)))
            M.attach(panel, row)
        compare = M.new("label_compare",
                        rt.table(stext="+100", state="positive", visible=True))
        M.attach(panel, compare)
        M.attach(M.hud, panel)
    return card1, card2, panel, compare


def main():
    base = tempfile.mkdtemp(prefix="zz_probe_ui_smoke7_")

    # ------------------------------------------------------------------ W1
    print("\n== W1: static round-7 tokens (both directions)")
    SRC = open(PROBE, encoding="utf-8", errors="replace").read()
    for tok in ("ROUND 7 - ZERO-WRITE READ EXPERIMENT",
                "zz_probe_r7", "zz_probe_r7_status", "zz_probe_r7_help",
                "common.get_context_value", "ComparisonValue", "label_compare",
                "R7-SKIP", "r7_skip_write",
                "STAT_MAX_DEPTH    = 12", "STAT_MAX_VISITS   = 200",
                "STAT_WATCH_VISITS = 250",
                "NO AUTOMATIC WINDOWS"):
        check(f"W1: source carries {tok!r}", tok in SRC)
    for tok in ("MAX_SAFETY_WINDOWS", "SAFETY_SECONDS", "safety_windows_started",
                "next_safety_arm_tick",
                'start_window("safety"',
                "pcall(function() r5.panel:SetContextObject",
                "pcall(function() e.unit:select_in_ui() end)",
                "pcall(function() c.uic:SimulateMouseOn() end)",
                "pcall(function() r5.sim_card.uic:SimulateMouseOff() end)",
                "pcall(function() bits.ds:SetContextObject(obj) end)"):
        check(f"W1: retired token is GONE: {tok!r}", tok not in SRC)

    # ------------------------------------------------------------------ W2
    print("\n== W2: panel hidden -> no R7 reads; the manual ladders write nothing")
    W = World(base)
    scene(W, with_panel=False)
    W.tick(40)
    t = W.text()
    check("W2: no R7 value lines without the panel", "R7 NEW" not in t)
    check("W2: zero get_context_value calls without the panel", W.M.gcv_calls == 0)
    check("W2: no capture window armed itself (no auto windows)", "CAPTURE WINDOW" not in t)
    res = W.G.zz_probe_r5()
    check("W2: the manual R5 hook still queues a run", "queued" in res or "queued" in str(res))
    W.tick(10)
    t = W.text()
    check("W2: the R5 run aborts before anything (no panel)", "ABORTED" in t)
    check("W2: zero writes across the aborted run", W.zeros())
    res7 = W.G.zz_probe_r7()
    check("W2: the manual R7 sweep returns its status", "R7 sweep done" in str(res7))
    check("W2: the manual R7 sweep read nothing (no panel, no window)", W.M.gcv_calls == 0)
    check("W2: no UI-state setter was ever called (trips == 0)", W.rt.eval("#trips") == 0)
    check("W2: the help text says NO automatic windows",
          "NO automatic windows" in str(W.G.zz_probe_ui_help()))
    check("W2: the status text has no safety counters",
          "safety=" not in str(W.G.zz_probe_ui_status()))

    # ------------------------------------------------------------------ W3
    print("\n== W3: both cards read via common.get_context_value, change-only, zero writes")
    W = World(base)
    scene(W, with_panel=True)
    M = W.M
    M.gcv_values["1001|Name"] = "Karl Franz"
    M.gcv_values["1001|HealthPercent"] = "0.85"
    M.gcv_values["1002|Name"] = "Spearmen"
    M.gcv_values["1002|HealthPercent"] = "0.72"

    ok = W.tick_until(lambda: "R7 NEW  sel card: GetContextObjectId(CcoBattleUnit)" in W.text(),
                      max_ticks=60, chunk=2)
    check("W3: the R7 sweep ran (the selected card was read)", ok)
    t = W.text()
    check("W3: the SELECTED card answered its ui id (1001)",
          'R7 NEW  sel card: GetContextObjectId(CcoBattleUnit) = "1001"' in t)
    check("W3: the NON-SELECTED card answered its ui id (1002)",
          'R7 NEW  nonsel card: GetContextObjectId(CcoBattleUnit) = "1002"' in t)
    check("W3: the selected card's Name value was read via get_context_value",
          'R7 NEW  sel Name = "Karl Franz"' in t)
    check("W3: the NON-selected card's Name value was read too",
          'R7 NEW  nonsel Name = "Spearmen"' in t)
    calls_join = W.rt.eval("function(t) local p = {} for i = 1, #t do p[#p+1] = tostring(t[i]) end return table.concat(p, '|') end")(M.calls)
    check("W3: values went to the 1002 context id (not only 1001)",
          "gcv:CcoBattleUnit:1002:Name" in calls_join)
    check("W3: zero writes (setctx/select/sim/cco)", W.writes_zero())

    # change-only: mutate one value, wait for the next sweep, expect ONE CHG line
    M.gcv_values["1001|HealthPercent"] = "0.50"
    ok = W.tick_until(lambda: 'CHG  sel HealthPercent = "0.50"' in W.text(),
                      max_ticks=40, chunk=2)
    check("W3: a mutated value is logged as CHG with the previous text", ok)
    check("W3: the CHG line names the old value",
          '(was "0.85")' in W.text())
    before = W.count("sel HealthPercent")
    W.tick(20)   # two more sweeps, nothing changed
    check("W3: unchanged sweeps are SILENT (no repeat lines)",
          W.count("sel HealthPercent") == before)
    check("W3: still zero writes after the change detection", W.writes_zero())
    check("W3: no UI-state setter was ever called (trips == 0)", W.rt.eval("#trips") == 0)

    # ------------------------------------------------------------------ W4
    print("\n== W4: a hover arms a capture; the hovered card + compare rows are read")
    W = World(base)
    card1, card2, panel, compare = scene(W, with_panel=True)
    M = W.M
    M.gcv_values["1002|Name"] = "Spearmen"
    M.gcv_values["CTXID:label_compare:CcoUnitStat|ComparisonValue"] = "12"
    W.M.fire("ComponentMouseOn", {"string": "1002", "component": "Pointer<Component> (0x1002)"})
    ok = W.tick_until(lambda: 'hover="1002"' in W.text(), max_ticks=30, chunk=1)
    check("W4: the hover armed a capture window naming card 1002", ok)
    ok = W.tick_until(lambda: 'R7 NEW  hover card: GetContextObjectId(CcoBattleUnit) = "1002"' in W.text(),
                      max_ticks=40, chunk=2)
    check("W4: the HOVERED card was read by the sweep", ok)
    check("W4: the compare row was read (stext +100)",
          'R7 NEW  compare#1 stext="+100"' in W.text())
    check("W4: the compare context probe ran once, read-only",
          'R7 compare#1 GetContextObjectId("CcoUnitStat")' in W.text())
    check("W4: a CcoUnitStat context id surfaced -> its fields were read",
          'R7 NEW  CcoUnitStat.ComparisonValue = "12"' in W.text())
    # the panel delta changes: the next sweep logs it change-only
    W.M.set_text(compare, "+12")
    ok = W.tick_until(lambda: 'CHG  compare#1 stext="+12"' in W.text(), max_ticks=40, chunk=2)
    check("W4: a changed comparison delta is logged as CHG", ok)
    check("W4: zero writes during hover reads", W.writes_zero())
    check("W4: no UI-state setter was ever called (trips == 0)", W.rt.eval("#trips") == 0)

    # ------------------------------------------------------------------ W5
    print("\n== W5: hostile get_context_value -> one ERR line per field, sweep survives")
    W = World(base)
    scene(W, with_panel=True)
    W.M.gcv_raises = True
    W.tick(30)
    t = W.text()
    check("W5: the hostile read is logged as an ERR (once per field)",
          "R7 ERR  CcoBattleUnit.Name" in t)
    W.tick(30)
    check("W5: the error is NOT re-logged on later sweeps",
          W.count("R7 ERR  CcoBattleUnit.Name") == 1)
    check("W5: the sweep still reads the card ids (survives the hostility)",
          'R7 NEW  sel card: GetContextObjectId(CcoBattleUnit) = "1001"' in W.text())
    check("W5: zero writes under a hostile engine", W.writes_zero())
    check("W5: no UI-state setter was ever called (trips == 0)", W.rt.eval("#trips") == 0)

    # ------------------------------------------------------------------ W6
    print("\n== W6: the slim dump - a 300-child panel costs at most the 200-visit budget")
    W = World(base)
    card1, card2, panel, compare = scene(W, with_panel=True)
    W.M.fill(panel, 300, "junk_")
    W.tick(12)
    t = W.text()
    check("W6: the stat dump ran and hit the shared 200-visit budget",
          "STAT DUMP visit budget reached (200 components total)" in t)
    check("W6: the dump still pairs stat_name -> dy_value with text",
          'stext="Range"' in t and 'stext="42"' in t)
    check("W6: no capture window appeared (nothing armed)", "CAPTURE WINDOW" not in t)
    check("W6: zero writes in the dump world", W.writes_zero())

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f_ in failures:
            print("   -", f_)
        return 1
    print("SMOKE TEST PASSED - round 7 ships ZERO writes (every former write site")
    print("is gone and R5/R6 log skips), both cards are read via")
    print("common.get_context_value change-only, the hover comparison rows are read,")
    print("a hostile engine only yields one ERR per field, and the slim dump respects")
    print("its 200-visit budget.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
