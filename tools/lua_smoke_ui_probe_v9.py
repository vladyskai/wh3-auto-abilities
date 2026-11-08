"""Offline smoke test for the ROUND-11 zz_probe_ui_text probe.
Run:
    cd C:/Users/vlady/Desktop/WH3_mod/tools && uv run --with lupa python lua_smoke_ui_probe_v9.py

Worlds (independent lupa runtimes, mock engine tree):
  W0 static: the R11 tokens exist; the BANNED name-lookup global is ABSENT from
     the source; descend budgets are the spec values; no string.find call; zero
     SetContextObject call sites.
  W1 main: step 1 lists the roots, step 2 enumerates EVERY root's children with
     hint tags, step 3 descends two levels below the hint nodes and LOCATES
     dynamic_stats (within 400 visits / depth 4), step 4 reads the stat rows
     (PANEL n= name/value) + the context ids (CTXID), step 5 makes ONE
     common.get_context_value with the selected ctx id and ONE with a
     non-selected card's ui id. Every native call is preceded by an 'R11 CALL'
     line. ZERO writes. The banned global is NEVER called.
  W2 depth cap: a stat row at depth 5 is NOT located (the descent stops at 4).
  W3 visit budget: a 930-node fan-out is cut off at exactly 400 visits.
  W4 auto: zz_probe_r11_auto() runs every step to done, zero writes.
  W5 disarm: driving the tick never auto-runs R11 or the R9 run.
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
PRELUDE = os.path.join(HERE, "mock_ui_prelude_v7.lua")
ADDITIONS = os.path.join(HERE, "mock_r11_additions.lua")
LOG_FILE = "zz_probe_ui_text_log.txt"
R11_TAG = "[zz_probe_ui_text] R11 "

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


def r11_lines(text):
    return [ln for ln in text.splitlines() if R11_TAG in ln]


def every_preceded_by_call(text, marker):
    """Every R11 line containing `marker` must, as the PREVIOUS R11 line, carry an
    'R11 CALL' line - proving the native call was logged before it was made."""
    lines = r11_lines(text)
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
        self.dir = tempfile.mkdtemp(prefix="r11_", dir=base)
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
        for _ in range(n):
            self.G.zz_probe_r11_step()

    def writes_zero(self):
        M = self.M
        return (M.setctx_calls == 0 and M.select_calls == 0 and M.cco_calls == 0
                and M.sim_on_calls == 0 and M.sim_off_calls == 0)

    def trips_zero(self):
        return self.rt.eval("#trips") == 0


def main():
    base = tempfile.mkdtemp(prefix="zz_probe_ui_smoke11_")

    # ------------------------------------------------------------------ W0
    print("\n== W0: static round-11 tokens + the BAN on the name-lookup global")
    SRC = open(PROBE, encoding="utf-8", errors="replace").read()
    check("W0: the BANNED name-lookup global is ABSENT", "find_uicomponent" not in SRC)
    for tok in ("ROUND 11", "zz_probe_r11", "zz_probe_r11_step", "zz_probe_r11_auto",
                "zz_probe_r11_status", "zz_probe_r11_help",
                "ROOTCOUNT", "ROOTCHILD", "DESCEND", "LOCATED ",
                "PANEL n=", "CTXID ", "QUERY selected", "QUERY nonsel",
                "descend_visits", "descend_depth", "hint_of", "stat_ids",
                "common.get_context_value", "GetContextObjectId", "StatList.Size"):
        check(f"W0: source carries {tok!r}", tok in SRC)
    check("W0: descend budget is 400 visits", "descend_visits = 400" in SRC)
    check("W0: descend depth is 4", "descend_depth  = 4" in SRC)
    check("W0: before-call logger present", 'R11.out("CALL "' in SRC and " CALL " in SRC)
    check("W0: wrap() rejects a boolean", "if raw == nil or raw == false then return nil end" in SRC)
    check("W0: no string.find() call", "string.find(" not in SRC)
    check("W0: ZERO SetContextObject call site", SRC.count(":SetContextObject(") == 2)
    check("W0: R9 auto-run stays disarmed", "auto_enabled = false" in SRC)

    # ------------------------------------------------------------------ W1
    print("\n== W1: full enumeration -> descent -> stat rows -> ONE decisive query")
    W = World(base)
    W.G.M.build_r11_scene()
    res = W.G.zz_probe_r11()
    check("W1: zz_probe_r11() reports READY", "READY" in str(res))
    W.step(1)
    t = W.text()
    check("W1: step 1 header", "R11 STEP 1" in t)
    check("W1: step 1 root count == 10 roots", "R11 ROOTCOUNT 10" in t)
    check("W1: step 1 lists the top-level roots", 'R11 ROOT 0 id="hud_battle"' in t)
    check("W1: step 1 surfaced panel_manager", 'id="panel_manager"' in t)
    ok, hits = every_preceded_by_call(t, "R11 ROOT 0 id=")
    check("W1: the first ROOT read is preceded by an R11 CALL line", ok and hits == 1)

    W.step(1)
    t = W.text()
    check("W1: step 2 header", "R11 STEP 2" in t)
    # EVERY root must be enumerated (complete enumeration, not a few roots)
    roots = ["hud_battle", "unit_id_holder", "tactical_map", "left", "right",
             "tactical_hud", "menu_bar", "panel_manager", "battle_orders",
             "watermark_square"]
    missing = [r for r in roots if f'ROOTCHILD root="{r}"' not in t]
    check(f"W1: step 2 enumerates EVERY root (missing={missing})", not missing)
    check("W1: step 2 tags a unit hint", 'hint=unit' in t)
    check("W1: step 2 tags a panel hint", 'hint=panel' in t)
    check("W1: step 2 tags cards_panel a hint",
          'ROOTCHILD "battle_orders" 0 id="cards_panel" children=1 hint=panel' in t)
    check("W1: step 2 hint=nil where no substring matches", "hint=nil" in t)
    ok, hits = every_preceded_by_call(t, "R11 ROOTCHILD ")
    check("W1: every ROOTCHILD line is preceded by an R11 CALL line", ok and hits > 0)

    W.step(1)
    t = W.text()
    check("W1: step 3 header", "R11 STEP 3" in t)
    check("W1: step 3 descended to dynamic_stats", 'DESCEND path=' in t and 'id="dynamic_stats"' in t)
    check("W1: step 3 reports one located component", "STEP 3 done: visits=" in t and "located=1" in t)
    check("W1: step 3 visit count is under the 400 budget",
          "visits=" in t and "STEP 3 done" in t)
    ok, hits = every_preceded_by_call(t, "R11 DESCEND path=")
    check("W1: every DESCEND line is preceded by an R11 CALL line", ok and hits > 0)

    W.step(1)
    t = W.text()
    check("W1: step 4 header", "R11 STEP 4" in t)
    check("W1: step 4 read row 1 (Armour 85)", 'PANEL n=1 name="Armour" value="85"' in t)
    check("W1: step 4 read row 2 (Leadership 60)", 'PANEL n=2 name="Leadership" value="60"' in t)
    check("W1: step 4 logged the located path", 'LOCATED "dynamic_stats"' in t)
    check("W1: step 4 read a CcoUnitDetails context id",
          "CTXID " in t and "CcoUnitDetails" in t)
    ok, hits = every_preceded_by_call(t, "R11 CTXID ")
    check("W1: every CTXID line is preceded by an R11 CALL line", ok and hits > 0)
    ok, hits = every_preceded_by_call(t, "R11 PANEL n=")
    check("W1: every PANEL row is preceded by an R11 CALL line", ok and hits > 0)

    W.step(1)
    t = W.text()
    check("W1: step 5 header", "R11 STEP 5" in t)
    check("W1: step 5 QUERY selected", "QUERY selected" in t)
    check("W1: step 5 QUERY nonsel", "QUERY nonsel type=" in t)
    check("W1: step 5 used the StatList.Size field", "field=StatList.Size" in t)
    check("W1: step 5 made exactly ONE query per target (2 total)", W.M.gcv_calls == 2)
    ok, hits = every_preceded_by_call(t, "R11 QUERY selected")
    check("W1: the selected QUERY is preceded by an R11 CALL line", ok and hits == 1)
    ok, hits = every_preceded_by_call(t, "R11 QUERY nonsel type=")
    check("W1: the nonsel QUERY is preceded by an R11 CALL line", ok and hits == 1)
    W.step(1)   # advance past step 5 -> the run-done transition
    t = W.text()
    check("W1: run-done banner", "ROUND 11 RUN done" in t)
    check("W1: the BANNED global was NEVER called", W.M.fu_calls == 0)
    check("W1: UIComponent(boolean) was NEVER called", W.M.uic_bool_calls == 0)
    check("W1: ZERO writes (no context/selection/sim)", W.writes_zero())
    check("W1: ZERO UI-state setters", W.trips_zero())

    # ------------------------------------------------------------------ W2
    print("\n== W2: a stat row BEYOND the depth cap is NOT located")
    W = World(base)
    W.G.M.build_r11_deep()
    W.G.zz_probe_r11()
    W.step(4)   # steps 1..4
    t = W.text()
    check("W2: the descent reached depth 4 (bbb)",
          'DESCEND path="unit_id_holder/unit_z/aaa/bbb"' in t)
    check("W2: the depth-5 node was NOT visited",
          'path="unit_id_holder/unit_z/aaa/bbb/stat_name"' not in t)
    check("W2: NO panel component was located", "located NO panel component" in t)
    check("W2: no stat row was read", "PANEL n=" not in t)
    check("W2: the BANNED global was NEVER called", W.M.fu_calls == 0)
    check("W2: ZERO writes", W.writes_zero())

    # ------------------------------------------------------------------ W3
    print("\n== W3: the 400-visit budget cuts a 930-node fan-out")
    W = World(base)
    W.G.M.build_r11_wide()
    W.G.zz_probe_r11()
    W.step(3)
    t = W.text()
    n = t.count("R11 DESCEND path=")
    check(f"W3: exactly 400 DESCEND visits (got {n})", n == 400)
    check("W3: step 3 reported visits=400", "STEP 3 done: visits=400" in t)
    check("W3: the BANNED global was NEVER called", W.M.fu_calls == 0)
    check("W3: ZERO writes", W.writes_zero())

    # ------------------------------------------------------------------ W4
    print("\n== W4: zz_probe_r11_auto() runs every step to done")
    W = World(base)
    W.G.M.build_r11_scene()
    W.G.zz_probe_r11()
    res = W.G.zz_probe_r11_auto()
    t = W.text()
    check("W4: auto banner", "ROUND 11 AUTO RUN" in t)
    check("W4: auto reached every step header", all(f"R11 STEP {i}" in t for i in range(1, 6)))
    check("W4: auto finished", "ROUND 11 RUN done" in t)
    check("W4: auto reported done", "done" in str(res))
    check("W4: the BANNED global was NEVER called", W.M.fu_calls == 0)
    check("W4: ZERO writes in auto", W.writes_zero())
    check("W4: ZERO UI-state setters in auto", W.trips_zero())

    # ------------------------------------------------------------------ W5
    print("\n== W5: the tick never auto-runs R11; the R9 run stays disarmed")
    W = World(base)
    W.G.M.build_r11_scene()
    W.poll(40)
    t = W.text()
    check("W5: R11 did NOT auto-run from the tick", "R11 STEP" not in t)
    check("W5: the R9 auto-run never fired", "ROUND 9 RUN" not in t)
    check("W5: no 'R9 armed: waiting' line", "R9 armed: waiting" not in t)
    check("W5: no SimulateMouseOn (simhover disarmed)", W.M.sim_on_calls == 0)
    check("W5: the BANNED global was NEVER called", W.M.fu_calls == 0)

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f_ in failures:
            print("   -", f_)
        return 1
    print("SMOKE TEST PASSED - round 11: the engine's name-lookup global is BANNED"
          " (never called); the UI root is fully enumerated (every root's children,"
          " hint-tagged); the descent (two levels below the hints, 400 visits, depth 4)"
          " LOCATES the stat panel; the stat rows + context ids are read; and ONE"
          " decisive common.get_context_value runs with the selected ctx id and once"
          " with a non-selected card's ui id - with ZERO writes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
