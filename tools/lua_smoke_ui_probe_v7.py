"""Offline smoke test for the ROUND-8 zz_probe_ui_text probe (THE DECISIVE
EXPERIMENT: the ground-truth table + the SIMULATED-HOVER LADDER + the manual
select test). Run:
    cd C:/Users/vlady/Desktop/WH3_mod/tools && uv run --with lupa python lua_smoke_ui_probe_v7.py

Worlds (independent lupa runtimes, mutable mock tree; the 50 ms r8 poll is
driven separately from the main poll):
  W1  static: every round-8 token exists; every retired write-token is GONE; the
      holds ladder is the required 50/150/300/1500; the ONLY SetContextObject
      mention is in the comments; both sim helpers log BEFORE the call.
  W2  truth: with the panel visible, each newly-selected unit logs exactly one
      'R8 TRUTH <id> <stat>=<value> ...'; switching selection + mutating the
      panel rows logs the new unit; after the settle the ladder AUTO-starts.
  W3  ladder (via zz_probe_r8()): one non-selected card, all four holds, each
      SimulateMouseOn paired with a SimulateMouseOff, one verdict per pass,
      comparison_seen=yes + delta_text captured, persisted_ms=0 when the engine
      clears the comparison on Off, and ZERO writes other than the sim pair.
  W4  persistence: with the comparison kept after Off, persisted_ms == the full
      2 s window (comparison values survive -> read once and cache).
  W5  default OFF: the ladder never calls select_in_ui and logs no DESELECT-TEST.
  W6  manual select test: armed by zz_probe_r8_toggle_select_test() it runs ONCE
      (exactly one select_in_ui on the non-selected unit) and logs the
      before/after + restored verdict; further ticks do not re-run it.
  W7  hostile: a raising SimulateMouseOn is swallowed, the pass still verdicts,
      and an Off is still issued (pairing holds under a hostile engine).
  W8  gate observability: a CLOSED gate (no stat panel, nothing selected) still
      logs its R8 GATE line (panel_seen=no, fired=none, ladder_state=idle) with
      the panel's tab state; and the FORCE path - zz_probe_r8() with the gate
      never opened - logs R8 FORCE + a gate line and runs the ladder.
  W8b condition B: a unit selected while the cards panel is up (no stat rows)
      OPENS the gate (fired=selection) and logs a no-rows truth line naming the
      panel's tab state.
"""
import os
import sys
import tempfile

import lupa

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
PRELUDE = os.path.join(HERE, "mock_ui_prelude_v7.lua")
LOG_FILE = "zz_probe_ui_text_log.txt"
R8_POLL = "zz_probe_r8_poll"
HOLDS = (50, 150, 300, 1500)

failures = []


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        failures.append(label)


class World:
    def __init__(self, base):
        self.dir = tempfile.mkdtemp(prefix="w8_", dir=base)
        os.chdir(self.dir)
        self.rt = lupa.LuaRuntime(unpack_returned_tuples=True)
        with open(PRELUDE, "r", encoding="utf-8") as f:
            self.rt.execute(f.read())
        with open(PROBE, "r", encoding="utf-8") as f:
            self.rt.execute(f.read())
        self.G = self.rt.globals()
        self.M = self.G.M
        self.log_path = os.path.join(self.dir, LOG_FILE)
        self.r8_poll = self.M.polls[R8_POLL]

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

    def tick_r8(self, n=1):
        for _ in range(n):
            self.r8_poll()

    def tick_both(self, n=1):
        for _ in range(n):
            self.G.poll_fn()
            self.r8_poll()

    def calls_join(self):
        return self.rt.eval(
            "function(t) local p = {} for i = 1, #t do p[#p+1] = tostring(t[i]) end "
            "return table.concat(p, '|') end")(self.M.calls)

    def trips(self):
        return self.rt.eval("#trips")

    def writes_zero_except_sim(self):
        """Round 8: the ONLY writes are the SimulateMouseOn/Off pair. No context
        write, no selection write (unless the manual test was armed)."""
        M = self.M
        return (M.setctx_calls == 0 and M.select_calls == 0 and M.cco_calls == 0)


def scene(W, with_panel=True):
    """Two cards (1001 selected, 1002 active) + an open stat panel whose rows
    are Range=42 / Armour=85 and one (hidden) label_compare comparison row.
    Hovering is modelled: M.sim_effect is on, so a SimulateMouseOn on 1002 makes
    the comparison row appear."""
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
    dys = {}
    if with_panel:
        panel = M.new("dynamic_stats", rt.table(visible=True))
        for name, value in (("Range", "42"), ("Armour", "85")):
            row = M.new("template_stat")
            M.attach(row, M.new("stat_name", rt.table(stext=name)))
            dyn = M.new("dy_value", rt.table(stext=value))
            M.attach(row, dyn)
            M.attach(panel, row)
            dys[name] = dyn
        compare = M.new("label_compare", rt.table(state="positive", visible=False))
        M.attach(panel, compare)
        M.attach(M.hud, panel)
    M.compare_comp = compare
    M.sim_effect = True
    M.compare_stext = "+100"
    return {"card1": card1, "card2": card2, "panel": panel,
            "compare": compare, "dys": dys}


def main():
    base = tempfile.mkdtemp(prefix="zz_probe_ui_smoke8_")

    # ------------------------------------------------------------------ W1
    print("\n== W1: static round-8 tokens (both directions)")
    SRC = open(PROBE, encoding="utf-8", errors="replace").read()
    for tok in ("ROUND 8 - THE DECISIVE EXPERIMENT", "zz_probe_r8",
                "zz_probe_r8_status", "zz_probe_r8_toggle_select_test",
                "zz_probe_r8_help", "R8_POLL_NAME", "zz_probe_r8_poll",
                "SIMHOVER", "TRUTH ", "DESELECT-TEST",
                "r8_sim_on", "r8_sim_off", "r8_poll", "r8_build_queue",
                "holds = { 50, 150, 300, 1500 }",
                "persisted_ms=", "comparison_seen=", "panel_changed=",
                "invisible=", "default_appear_val", "expand_delay_ms",
                "logged BEFORE the call", "ZERO SetContextObject",
                "GetContextObjectId", "label_compare"):
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
    # the only SetContextObject mention is in the two comment lines
    check("W1: no SetContextObject call site (mentions are comments only)",
          SRC.count(":SetContextObject(") == 2)
    # the sim helpers log before they call, and the ladder is a real loop over holds
    check("W1: sim_on logs before calling",
          SRC.index("SIMHOVER SimulateMouseOn") < SRC.index("uic:SimulateMouseOn()"))
    check("W1: sim_off logs before calling",
          SRC.index("SIMHOVER SimulateMouseOff") < SRC.index("uic:SimulateMouseOff()"))

    # ------------------------------------------------------------------ W2
    print("\n== W2: PART 1 truth table + the auto-started ladder")
    W = World(base)
    info = scene(W, with_panel=True)
    M = W.M
    W.tick_both(24)
    t = W.text()
    check("W2: the selected unit's row table is logged as R8 TRUTH",
          'R8 TRUTH 1001 Range=42 Armour=85' in t)
    # the user clicks the other unit: selection moves to 1002, rows change
    M.set_state(info["card1"], "active")
    M.set_state(info["card2"], "selected")
    M.set_text(info["dys"]["Range"], "50")
    W.tick_both(24)
    t = W.text()
    check("W2: clicking another unit logs a NEW truth line for it",
          'R8 TRUTH 1002 Range=50 Armour=85' in t)
    check("W2: exactly the two clicked units are in the truth table",
          W.M.calls is not None and W.G.zz_probe_r8_status().count("truth_entries=2") == 1)
    # stop clicking: after the settle the ladder must AUTO-start
    W.tick_both(300)
    t = W.text()
    check("W2: the ladder auto-started after the truth settled",
          "R8 LADDER starting (auto:" in t)
    check("W2: the auto ladder actually simulated hovers", W.M.sim_on_calls > 0)
    check("W2: the auto ladder paired every On with an Off",
          W.M.sim_on_calls == W.M.sim_off_calls)
    check("W2: zero context/selection writes in the auto flow",
          W.writes_zero_except_sim())
    check("W2: no UI-state setter (trips == 0)", W.trips() == 0)

    # ------------------------------------------------------------------ W3
    print("\n== W3: PART 2 the simulated-hover ladder (pairing + verdicts)")
    W = World(base)
    scene(W, with_panel=True)
    M = W.M
    W.tick_both(12)                       # one truth capture
    res = W.G.zz_probe_r8()
    check("W3: zz_probe_r8() starts the ladder", "ladder started" in str(res))
    W.tick_r8(700)
    t = W.text()
    check("W3: SimulateMouseOn is logged for the non-selected card",
          'R8 SIMHOVER SimulateMouseOn card="1002" hold=50ms' in t)
    check("W3: the matching SimulateMouseOff is logged",
          'R8 SIMHOVER SimulateMouseOff card="1002"' in t)
    for h in HOLDS:
        check(f"W3: the hold ladder ran the {h} ms pass",
              f'SimulateMouseOn card="1002" hold={h}ms' in t)
    check("W3: every pass wrote a verdict line",
          t.count('R8 SIMHOVER card="1002" hold=') == 4)
    check("W3: the verdict carries the comparison fields",
          'comparison_seen=yes' in t and 'panel_changed=no' in t
          and 'delta_text="+100"' in t)
    check("W3: the two short holds are labelled invisible=yes",
          'hold=50 comparison_seen=yes' in t and 'invisible=yes' in t)
    check("W3: comparison values are read via the compare context (read-only)",
          'SIMHOVER compare#1 GetContextObjectId("CcoUnitStat")' in t)
    check("W3: every SimulateMouseOn has a matching SimulateMouseOff",
          M.sim_on_calls == M.sim_off_calls and M.sim_on_calls == 4)
    check("W3: persisted_ms=0 (the engine cleared the comparison on Off)",
          'hold=50 comparison_seen=yes panel_changed=no persisted_ms=0' in t)
    check("W3: zero context/selection writes (only the sim pair)",
          W.writes_zero_except_sim())
    check("W3: the select test did NOT run (default OFF)",
          M.select_calls == 0 and "R8 DESELECT-TEST begin" not in t)
    check("W3: no UI-state setter (trips == 0)", W.trips() == 0)

    # ------------------------------------------------------------------ W4
    print("\n== W4: persistence - the comparison survives after MouseOff")
    W = World(base)
    scene(W, with_panel=True)
    W.M.keep_compare_after_off = True     # model the comparison lingering
    W.tick_both(12)
    W.G.zz_probe_r8()
    W.tick_r8(700)
    t = W.text()
    check("W4: comparison_seen=yes during the hold", 'comparison_seen=yes' in t)
    check("W4: the comparison persisted the full 2 s window (persisted_ms=2000)",
          'persisted_ms=2000' in t)
    check("W4: every On still paired with an Off",
          W.M.sim_on_calls == W.M.sim_off_calls)
    check("W4: zero writes other than the sim pair", W.writes_zero_except_sim())

    # ------------------------------------------------------------------ W5
    print("\n== W5: default OFF + a hostile SimulateMouseOn is swallowed")
    W = World(base)
    info = scene(W, with_panel=True)
    st = str(W.G.zz_probe_r8_status())
    check("W5: status says select_armed=false by default", "select_armed=false" in st)
    check("W5: status reports the hold ladder",
          "holds 50/150/300/1500 ms" in st)
    # hostile: the non-selected card raises on SimulateMouseOn
    W.M.set_state(info["card2"], "active")
    # arm a raise on the card via the mock's own sim_raises flag
    W.rt.execute('''do
      local c = nil
      for i = 1, #M.card_registry do
        if M.card_registry[i].id == "1002" then c = M.card_registry[i] end
      end
      if c ~= nil then c.sim_raises = true end
    end''')
    W.tick_both(12)
    W.G.zz_probe_r8()
    W.tick_r8(700)
    t = W.text()
    check("W5: the hostile SimulateMouseOn error is swallowed and logged",
          "SimulateMouseOn error (swallowed)" in t)
    check("W5: the pass still emits its verdicts after the hostility",
          t.count('R8 SIMHOVER card="1002" hold=') == 4)
    check("W5: an Off is still issued despite the hostile On",
          W.M.sim_off_calls == W.M.sim_on_calls and W.M.sim_on_calls == 4)
    check("W5: zero context/selection writes", W.writes_zero_except_sim())

    # ------------------------------------------------------------------ W6
    print("\n== W6: PART 4 - the manual select test runs ONCE")
    W = World(base)
    info = scene(W, with_panel=True)
    M = W.M
    W.tick_both(12)
    W.tick_r8(140)                        # let the truth settle timer open the gate
    res = W.G.zz_probe_r8_toggle_select_test()
    check("W6: the toggle ARMS the test",
          "ARMED" in str(res) and "select_armed=true" in str(W.G.zz_probe_r8_status()))
    W.tick_r8(80)
    t = W.text()
    check("W6: the DESELECT-TEST block ran", "R8 DESELECT-TEST begin" in t)
    check("W6: exactly ONE select_in_ui call was made", M.select_calls == 1)
    check("W6: it selected the NON-selected unit (1002)",
          "select_in_ui:1002" in W.calls_join())
    check("W6: the before/after + restored verdict were logged",
          "DESELECT-TEST cards before:" in t and "DESELECT-TEST cards after:" in t
          and "DESELECT-TEST restored=" in t)
    check("W6: the selection DID change (the fake-selection route worked)",
          "DESELECT-TEST selection DID change" in t)
    before = M.select_calls
    W.tick_r8(120)
    check("W6: the select test does NOT run again (single pass)",
          M.select_calls == before)
    check("W6: still zero SetContextObject writes", M.setctx_calls == 0)
    check("W6: no UI-state setter (trips == 0)", W.trips() == 0)

    # ------------------------------------------------------------------ W8
    print("\n== W8: the gate is OBSERVABLE - a CLOSED gate still logs its line")
    W = World(base)
    info = scene(W, with_panel=False)        # no stat panel at all
    W.M.set_state(info["card1"], "active")   # and nothing selected
    W.tick_r8(40)                            # ~2 s of the 50 ms poll
    t = W.text()
    check("W8: a CLOSED gate still logs an R8 GATE line",
          "R8 GATE panel_seen=no" in t)
    check("W8: the closed-gate line names the firing condition (none)",
          "fired=none" in t)
    check("W8: the closed-gate line reports ladder_state",
          "ladder_state=idle" in t)
    check("W8: the gate line carries the panel's tab state",
          "tab={" in t and "row_header_stats" in t)
    check("W8: the gate line reports selected_card=none",
          "selected_card=none" in t)
    res = W.G.zz_probe_r8()                  # the FORCE path
    t = W.text()
    check("W8: a forced run logs R8 FORCE", "R8 FORCE" in t)
    check("W8: the forced run logs the gate line too", "R8 GATE" in t)
    check("W8: the forced run started the ladder", "R8 LADDER starting" in t)
    check("W8: the force reply names the gate condition",
          "FORCED; gate fired=" in str(res))
    W.tick_r8(60)
    check("W8: the forced ladder simulated hovers", W.M.sim_on_calls > 0)
    check("W8: the forced ladder paired every On with an Off",
          W.M.sim_on_calls == W.M.sim_off_calls)
    check("W8: the forced run is a zero-write flow (no context/selection writes)",
          W.writes_zero_except_sim())
    check("W8: status reports the cached gate state",
          "gate[panel_seen=false" in str(W.G.zz_probe_r8_status())
          and "force=1" in str(W.G.zz_probe_r8_status()))

    # ------------------------------------------------------------------ W8b
    print("\n== W8b: CONDITION B - a selection with the cards panel up opens the gate")
    W = World(base)
    scene(W, with_panel=False)               # card 1001 is selected by scene()
    W.tick_r8(40)
    t = W.text()
    check("W8b: the selection opened the gate (fired=selection)",
          "fired=selection" in t)
    check("W8b: the opening condition is named",
          "GATE OPENED by selection" in t)
    check("W8b: a no-rows truth line names the panel's tab state",
          "no stat rows visible" in t and "tab={" in t)
    check("W8b: the gate line reports panel_seen=no (no stat rows)",
          "R8 GATE panel_seen=no" in t)
    check("W8b: the gate line reports selected_card=1001",
          "selected_card=1001" in t)

    print()
    if failures:
        print(f"SMOKE TEST FAILED - {len(failures)} assertion(s):")
        for f_ in failures:
            print("   -", f_)
        return 1
    print("SMOKE TEST PASSED - round 8: the truth table logs per click, the")
    print("simulated-hover ladder runs 50/150/300/1500 ms with every On paired with")
    print("an Off, the comparison fields are read (and their persistence measured),")
    print("the select test is OFF by default and runs ONCE when armed, and ZERO")
    print("SetContextObject / UI-state setters are ever called.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
