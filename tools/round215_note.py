#!/usr/bin/env python3
"""Round 215 (tuning): the tracker (10.92) and CLAUDE.md (the measurement, the two fixes, what is left)."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
LOG = """
### 10.92 Round 215 (tuning) - the mod's own cost, measured and cut (2026-11-28)

**Field (the round-214 timing probe; archive\\logs\\battle_20261128_r214_perf.txt, bytes 1,111,622,234-1,129,297,788;
147 s, 21 units, the user's own PC):** the mod took 124 ms of every second (12.4%).

| Where | Measured |
|---|---|
| The deployment phase, 46 s, nothing selected | 10 HUD walks a second, 150 ms per second, the worst tick 73 ms |
| One HUD walk | 15 to 18 ms (about 600 components) |
| The unit cards, read on every UI tick | 64 ms per second for the whole battle |
| The test build's own log sweeps | 9 ms per second (not in the Workshop build) |
| The polls (the ability checks) | 5 ms per second |
| Seconds with a UI tick over 16 ms | 94 of 147 |

The Workshop comment (lag when selecting units) is confirmed on a clean setup. Round 213's reading was right about the
walk and missed the two larger costs.

**Change:**

- `FOURTH.boot_due`: before the first selection of a battle the every-2nd-tick walk runs for the first 40 UI ticks
  only, then the 5 s safety net. Cause of the storm: during deployment the units are not listed yet, so the active set
  is the whole table, no walk can complete it, and no selection has opened a bounded window.
- `FOURTH.cards_due`: once the game's own selection events have arrived the unit cards are read every 4th UI tick.

**Proof:** harness 213 full suite **8,548 checks / 0 failures** (once). RED on the pre-round snapshot: 50 walks in 100
ticks of deployment (GREEN 1), the card reads unchanged after the events arrive (GREEN 25%). The cast trace (2,211
worlds, 1,777 casts) matches between the test build and the release build apart from the 3 probe casts. One rebased
pin: harness 58 C5, a selection only the card reports while the events are alive, 2 ticks -> 5 ticks. No workbook.

**Not done:** the cost of one walk (15 ms) is unchanged. A unit's first selection still pays it once or twice.
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.92 Round 215" not in s
    open(p, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + LOG)
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `2a8972cfce788db53d7cd05bc8d80118`" + nl
            + "  (round 214, 2026-11-28, tuning: type Mod, the timing probe, round 213's selection fix).",
            "- Installed build: md5 `978269788df09dbc23d79d94922d5074`" + nl
            + "  (round 215, 2026-11-28, tuning: no walk storm before the first selection, the unit cards 5 times a second).")
    s = one(s, "20261128_perfprobe_harness212/build_and_install214.py", "20261128_owncost_harness213/build_and_install215.py")
    s = one(s, "(harness212: 8,533 checks; it takes about 2 minutes)", "(harness213: 8,548 checks; it takes about 2 minutes)")
    a = "- ROUND 214 (2026-11-28, TUNING, TEST PACK INSTALLED: md5 2a8972cf..., type MOD)."
    note = [
        "- ROUND 215 (2026-11-28, TUNING, TEST PACK INSTALLED: md5 97826978...). FIELD, MEASURED (the round-214 probe,",
        "  archive\\logs\\battle_20261128_r214_perf.txt, bytes 1,111,622,234-1,129,297,788, 147 s, 21 units, the user's PC):",
        "  THE MOD TOOK 124 ms OF EVERY SECOND. (a) The DEPLOYMENT phase (46 s): 10 HUD walks a second = 150 ms/s, worst",
        "  tick 73 ms. CAUSE: before 'combat phase started' the units are not listed, the active set is the WHOLE table, no",
        "  walk can complete it, and no selection has opened the bounded window (brisk_walk_until < 0 = the old every-2nd-",
        "  tick cadence without end). (b) ONE HUD WALK = 15 to 18 ms (about 600 components). (c) fast_card_selection on",
        "  every UI tick = 64 ms/s for the whole battle. (d) the test build's log sweeps 9 ms/s, the polls 5 ms/s. os.clock()",
        "  WORKS in battle Lua, and the Mod-type test pack loads and logs when ticked. BUILT: FOURTH.boot_due (window < 0:",
        "  the old cadence for the first 40 UI ticks, then the 5 s net) and FOURTH.cards_due (selection_callback_alive ->",
        "  every 4th tick). Both keep the old line and add a line after it (harness pins). Harness 213: 8,548 / 0 (once),",
        "  RED 50 walks in 100 deployment ticks vs 1, the cast trace matches apart from the 3 probe casts, one rebased pin",
        "  (harness 58 C5: 2 -> 5 ticks). A harness world for the DEPLOYMENT phase: run_phase(W, 'Deployment') and",
        "  W.icons_on_screen = true WITHOUT run_phase(W, 'Deployed'). NOT DONE: the cost of one walk (scope it to the",
        "  ability dial instead of the whole hud_battle), the per-tick loops over the whole table during deployment. The",
        "  WORKSHOP ITEM STILL CARRIES ROUND 212. WAITING: the user's battle on this pack (tools\\analyze_perf.py), then",
        "  the release pack. Next battle from byte 1,129,297,788 (re-measure).",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("tracker and CLAUDE.md updated")


if __name__ == "__main__":
    main()
