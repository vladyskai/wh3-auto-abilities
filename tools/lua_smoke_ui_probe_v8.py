"""Offline smoke test for the ROUND-10 zz_probe_ui_text probe.
Run:
    cd C:/Users/vlady/Desktop/WH3_mod/tools && uv run --with lupa python lua_smoke_ui_probe_v8.py

Worlds (independent lupa runtimes, mock engine tree):
  W0 static: the R10 tokens exist; the round-9 defect guards exist; the unproven
     finders are gone from R9; the R9 auto-run is disarmed; no string.find call.
  W1 discovery + staging: hud_battle does NOT contain the info panel (the panel is
     a sibling under battle_orders) - the ROOT/ROOTCHILD enumeration surfaces it and
     the proved finder resolves it. Every risky call runs inside a step and is
     preceded by an 'R10 CALL' line. ZERO writes.
  W2 false-return defence: find_uicomponent returns FALSE for everything and the
     probe does NOT call UIComponent(boolean) (the round-9 crash) - no fatal wrap.
  W3 disarm: driving the tick never fires the R9 auto-run (it must not), and never
     auto-runs R10 (console-driven only); no SimulateMouseOn.
  W4 finder bisector: one candidate per call, advancing; candidate 5 is the round-9
     shape (returns false, survives), candidate 6 is UIComponent(false) (raises,
     engine survives).
  W5 auto: zz_probe_r10_auto() runs every step to done, zero writes.
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
PRELUDE = os.path.join(HERE, "mock_ui_prelude_v7.lua")
ADDITIONS = os.path.join(HERE, "mock_r10_additions.lua")
LOG_FILE = "zz_probe_ui_text_log.txt"
R10_TAG = "[zz_probe_ui_text] R10 "

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def r10_lines(text):
    return [ln for ln in text.splitlines() if R10_TAG in ln]


def every_preceded_by_call(text, marker):
    """Every line containing `marker` must have, as the PREVIOUS R10 line, an
    'R10 CALL' line - proving the call was logged before it was made."""
    lines = r10_lines(text)
    ok = True
    hits = 0
    for i, ln in enumerate(lines):
        if marker in ln:
            hits += 1
            if i == 0 or " CALL " not in lines[i - 1]:
                ok = False
    return ok, hits


class World:
    def __init__(self, base, additions=True):
        self.dir = tempfile.mkdtemp(prefix="r10_", dir=base)
        os.chdir(self.dir)
        self.rt = lupa.LuaRuntime(unpack_returned_tuples=True)
        with open(PRELUDE, encoding="utf-8") as f:
            self.rt.execute(f.read())
        if additions:
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
        for _ in range(n):
            self.G.zz_probe_r10_step()

    def writes_zero(self):
        M = self.M
        return (M.setctx_calls == 0 and M.select_calls == 0 and M.cco_calls == 0
                and M.sim_on_calls == 0 and M.sim_off_calls == 0)

    def trips_zero(self):
        n = self.rt.eval("#trips")
        return n == 0

    def has_under(self, node, want):
        f = self.rt.eval(
            "function(node, want) local hit=false "
            "local function w(c) if c.id==want then hit=true end "
            "for _,k in ipairs(c.children or {}) do w(k) end end "
            "w(node) return hit end")
        return bool(f(node, want))


def main():
    base = tempfile.mkdtemp(prefix="zz_probe_ui_smoke10_")

    # ------------------------------------------------------------------ W0
    print("\n== W0: static round-10 tokens + the round-9 defect fix")
    SRC = open(PROBE, encoding="utf-8", errors="replace").read()
    for tok in ("ROUND 10", "zz_probe_r10", "zz_probe_r10_step", "zz_probe_r10_auto",
                "zz_probe_r10_status", "zz_probe_r10_help", "zz_probe_r10_finder_test",
                "ROOTCHILD", "FINDERTEST", "root_max", "child_max", "panel_hints",
                "R10 STEP", "ROUND 10 RUN done"):
        check(f"W0: source carries {tok!r}", tok in SRC)
    check("W0: before-call logger present", 'R10.out("CALL "' in SRC and " CALL " in SRC)
    check("W0: wrap() rejects a boolean", "if raw == nil or raw == false then return nil end" in SRC)
    check("W0: R9 find_uicomponent guard (truthiness)", "if ok and raw then" in SRC)
    check("W0: unproven FindByScriptTag fallback GONE from R9", 'how = "FindByScriptTag"' not in SRC)
    check("W0: unproven SequentialFind fallback GONE from R9", 'how = "SequentialFind"' not in SRC)
    check("W0: R9 auto-run disarmed (field)", "auto_enabled = false" in SRC)
    check("W0: R9 auto-run gated on the flag", "if R9.auto_enabled and (not R9.ran)" in SRC)
    check("W0: no string.find() call", "string.find(" not in SRC)
    check("W0: ZERO SetContextObject call site", SRC.count(":SetContextObject(") == 2)

    # ------------------------------------------------------------------ W1
    print("\n== W1: enumerate the UI root -> discover the panel -> staged calls")
    W = World(base)
    W.G.M.build_r10_scene()
    # the panel is NOT under hud_battle (the round-8/9 blind spot)
    check("W1: hud_battle does NOT contain unit_information",
          not W.has_under(W.G.M.hud, "unit_information"))
    res = W.G.zz_probe_r10()
    check("W1: zz_probe_r10() reports READY", "READY" in str(res))
    W.step(1)
    t = W.text()
    check("W1: step 1 header", "R10 STEP 1" in t)
    check("W1: step 1 root count", "R10 ROOTCOUNT" in t)
    check("W1: step 1 lists top-level roots", 'R10 ROOT 0 id=' in t)
    check("W1: step 1 surfaced battle_orders", 'id="battle_orders"' in t)
    ok, hits = every_preceded_by_call(t, "R10 ROOT 0 id=")
    check("W1: the first ROOT read is preceded by an R10 CALL line", ok and hits == 1)
    W.step(1)
    t = W.text()
    check("W1: step 2 header", "R10 STEP 2" in t)
    check("W1: step 2 ROOTCHILD lines", 'ROOTCHILD root="battle_orders"' in t)
    check("W1: step 2 discovered unit_information (deeper)",
          'ROOTCHILD "battle_orders"' in t and 'id="unit_information"' in t)
    ok, hits = every_preceded_by_call(t, "R10 ROOTCHILD ")
    check("W1: every ROOTCHILD line is preceded by an R10 CALL line", ok and hits > 0)
    W.step(1)   # step 3
    t = W.text()
    check("W1: step 3 header", "R10 STEP 3" in t)
    check("W1: unit_information resolved via the proved finder",
          'FOUND unit_information -> yes' in t)
    W.step(7)   # steps 4..9 + the done transition
    t = W.text()
    check("W1: step 4 dynamic_stats resolved", "R10 STEP 4" in t and 'FOUND dynamic_stats -> yes' in t)
    check("W1: step 5 template_stat row + reads", "R10 STEP 5" in t and "template_stat=yes" in t)
    check("W1: step 5 read stat_name", 'stat_name="Armour"' in t)
    check("W1: step 5 read dy_value", 'dy_value="85"' in t)
    check("W1: step 6 explicit reads", "R10 STEP 6" in t and 'READ dy_value stext="85"' in t)
    check("W1: step 7 GetContextObjectId", "R10 STEP 7" in t and "CTXID " in t)
    check("W1: step 8 QUERY selected", "R10 STEP 8" in t and "QUERY selected" in t)
    check("W1: step 9 QUERY nonsel", "R10 STEP 9" in t and "QUERY nonsel" in t)
    check("W1: run-done banner", "ROUND 10 RUN done" in t)
    ok, hits = every_preceded_by_call(t, 'R10 CTXID "')
    check("W1: every CTXID call is preceded by an R10 CALL line", ok and hits > 0)
    ok, hits = every_preceded_by_call(t, "R10 QUERY selected")
    check("W1: every QUERY selected call is preceded by an R10 CALL line", ok and hits > 0)
    ok, hits = every_preceded_by_call(t, "R10 QUERY nonsel")
    check("W1: every QUERY nonsel call is preceded by an R10 CALL line", ok and hits > 0)
    check("W1: context values were actually queried", W.M.gcv_calls > 0)
    check("W1: ZERO writes (no context/selection/sim)", W.writes_zero())
    check("W1: ZERO UI-state setters", W.trips_zero())

    # ------------------------------------------------------------------ W2
    print("\n== W2: find_uicomponent returning FALSE must NOT crash the probe")
    W = World(base)
    W.G.M.build_r10_scene()
    W.G.M.fu_return_false = True          # every find_uicomponent call returns false
    W.G.zz_probe_r10()
    W.step(3)                              # steps 1..3 (step 3 uses the finder)
    t = W.text()
    check("W2: UIComponent(boolean) was NEVER called", W.M.uic_bool_calls == 0)
    check("W2: step 3 did not raise a swallowed error", "STEP 3 raised" not in t)
    check("W2: the false return was guarded (no fatal wrap)", W.M.uic_bool_calls == 0)

    # ------------------------------------------------------------------ W3
    print("\n== W3: the R9 auto-run stays disarmed; R10 is console-driven only")
    W = World(base)
    W.G.M.build_r10_scene()
    W.poll(40)                             # ~8 s of the tick, panel visible
    t = W.text()
    check("W3: the R9 auto-run never fired", "ROUND 9 RUN" not in t)
    check("W3: no 'R9 armed: waiting' line", "R9 armed: waiting" not in t)
    check("W3: R10 did NOT auto-run from the tick", "R10 STEP" not in t)
    check("W3: no SimulateMouseOn (simhover disarmed)", W.M.sim_on_calls == 0)

    # ------------------------------------------------------------------ W4
    print("\n== W4: the finder bisector - one candidate per call")
    W = World(base)
    W.G.M.build_r10_scene()
    for _ in range(6):
        W.G.zz_probe_r10_finder_test()
    t = W.text()
    check("W4: six FINDERTEST candidates logged", t.count("FINDERTEST candidate") == 6)
    check("W4: candidate 2 is root:Find(name,false)", 'root:Find("unit_information", false)' in t)
    check("W4: candidate 4 is the vanilla battle finder shape",
          'find_uicomponent(ui_root, "unit_information")' in t)
    check("W4: candidate 5 is the round-9 shape", "THE ROUND-9 SHAPE" in t)
    check("W4: candidate 5 returned a value (no crash)",
          "FINDERTEST 5 returned type=" in t and "FINDERTEST 5 RAISED" not in t)
    check("W4: candidate 6 (UIComponent(false)) RAISED but the engine survived",
          "FINDERTEST 6 RAISED" in t)
    check("W4: UIComponent(boolean) was reached exactly once (candidate 6)",
          W.M.uic_bool_calls == 1)
    r7 = W.G.zz_probe_r10_finder_test()
    check("W4: a seventh call reports all candidates tried",
          "already tried" in str(r7))

    # ------------------------------------------------------------------ W5
    print("\n== W5: zz_probe_r10_auto() runs every step to done")
    W = World(base)
    W.G.M.build_r10_scene()
    W.G.zz_probe_r10()
    res = W.G.zz_probe_r10_auto()
    t = W.text()
    check("W5: auto banner", "ROUND 10 AUTO RUN" in t)
    check("W5: auto reached every step header", all(f"R10 STEP {i}" in t for i in range(1, 10)))
    check("W5: auto finished", "ROUND 10 RUN done" in t)
    check("W5: auto reported done", "done" in str(res))
    check("W5: ZERO writes in auto", W.writes_zero())
    check("W5: ZERO UI-state setters in auto", W.trips_zero())

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f_ in failures:
            print("   -", f_)
        return 1
    print("SMOKE TEST PASSED - round 10: the UI root is enumerated first (the info"
          " panel is DISCOVERED, not assumed), every risky call runs inside an armed"
          " step and is logged BEFORE it is made, find_uicomponent's FALSE return can"
          " no longer be wrapped into UIComponent(false), the R9 auto-run is disarmed,"
          " and ZERO UI writes happen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
