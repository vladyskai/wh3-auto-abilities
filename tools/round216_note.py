#!/usr/bin/env python3
"""Round 216 (tuning): the tracker (10.93) and CLAUDE.md (the second measurement, the two fixes, what is left)."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
LOG = """
### 10.93 Round 216 (tuning) - the cost of the HUD walk (2026-11-28)

**Field (the round-215 build; archive\\logs\\battle_20261128_r215_perf.txt, bytes 1,129,297,788-1,136,053,587; 123 s,
21 units, the user's own PC):** the mod took 71 ms of every second (124 on the round-214 build).

| Where | Measured |
|---|---|
| The walk storm before the first selection | gone after 2 s (walks per second: 10, 10, 0, 0, 1, 0 ...) |
| The HUD walks | 157 in 123 s, 18.3 ms each (770 components), 21.9 ms per second, the worst UI ticks 60 to 63 ms |
| Walks that found nothing | 142 of 159 logged: 56 before any selection, 43 right after the selection became empty, about 20 on a unit that owns none of our abilities, 26 on a group |
| The unit cards | 40 to 85 ms per second until the first selection event (46 s in this battle), then 11 to 26 |
| The test build's own log sweeps | 8.9 ms per second (not in the Workshop build) |
| The polls (the ability checks) | 7.1 ms per second |

**Change:**

- `FOURTH.walk_start` / `FOURTH.walk_again`: the walk starts at the ability dial (`root:Find("SA_dial", false)`, the
  pattern the inventory sweep has used in every battle). The whole `hud_battle` is walked when the dial is not found,
  on the 5 s safety net, and when the dial walk claimed nothing while a selected unit still waits for a letter.
- `FOURTH.walk_useful`: once the game's selection events are alive, no walk while no selected unit owns one of our
  abilities (an empty selection included). The 5 s safety net stays.

**Proof:** harness 214 full suite **8,569 checks / 0 failures** (once). RED on the pre-round snapshot: the walk enters
the rest of the HUD although the dial holds the button (GREEN 0 times), 2 walks while a unit that owns nothing is
selected and dropped (GREEN 0). The cast trace (2,219 worlds, 1,777 casts) matches between the test build and the
release build apart from the 3 probe casts. Three rebased pins, all in harness 78: W3 (one of the three selected units
now owns the ability, else no walk is due and the coalescing test would test nothing), W5a and W5b (a newly tracked
unit while the selected unit owns nothing: 1 walk -> 0). No workbook.

**Unproven in game:** that the engine's Find answers `SA_dial` from the UI root (the mock does not, so every older
world keeps the whole-HUD walk). The test build logs `scan scope: dial` once when it does. The size of the dial walk
(the `scan done: N component(s) visited` lines).

**Not done:** the unit cards before the first selection event (read on every tick until an event arrives).
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.93 Round 216" not in s
    open(p, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + LOG)
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `978269788df09dbc23d79d94922d5074`" + nl
            + "  (round 215, 2026-11-28, tuning: no walk storm before the first selection, the unit cards 5 times a second).",
            "- Installed build: md5 `ae5536f9d59216189350a468f4b92f09`" + nl
            + "  (round 216, 2026-11-28, tuning: the HUD walk starts at the ability dial, no walk while nothing of ours is selected).")
    s = one(s, "20261128_owncost_harness213/build_and_install215.py", "20261128_walkscope_harness214/build_and_install216.py")
    s = one(s, "(harness213: 8,548 checks; it takes about 2 minutes)", "(harness214: 8,569 checks; it takes about 2 minutes)")
    a = "- ROUND 215 (2026-11-28, TUNING, TEST PACK INSTALLED: md5 97826978...)."
    note = [
        "- ROUND 216 (2026-11-28, TUNING, TEST PACK INSTALLED: md5 ae5536f9...). FIELD on round 215",
        "  (archive\\logs\\battle_20261128_r215_perf.txt, bytes 1,129,297,788-1,136,053,587, 123 s): 71 ms OF EVERY SECOND",
        "  (124 before). The deployment storm is gone after 2 s. 157 walks at 18.3 ms (770 components), worst ticks 60-63",
        "  ms. 142 OF 159 WALKS FOUND NOTHING: the active set is the WHOLE ARMY's abilities, so all_buttons_found() is",
        "  almost never true and EVERY selection event walks (43 after the selection became empty, about 20 on units that",
        "  own nothing of ours, 26 on groups, 56 before any selection: 20 boot walks + 24 in the 48-tick window the",
        "  re-list opens at combat start + the net). Cards: 40-85 ms/s until the first selection EVENT, then 11-26. BUILT:",
        "  FOURTH.walk_useful(walk, t) after the walk decision (events alive and no selected unit owns ours -> no walk,",
        "  the net stays, an unread unit keeps the walk), FOURTH.walk_start(hud) (root:Find('SA_dial', false) as inv_find",
        "  does it, the whole HUD when not found or on the net tick: FOURTH.walk_net is set by walk_useful because",
        "  ui_ticks is declared BELOW find_ability_buttons), FOURTH.walk_again() (the dial walk claimed nothing and a",
        "  selected unit waits -> the whole HUD in the same call). FOURTH.walk_claims uses an index loop: harness 78",
        "  counts 'ipairs(active_abilities_list())' (exactly 5). Harness 214: 8,569 / 0 (once), cast trace matches apart",
        "  from the 3 probe casts, 3 rebased pins (harness 78 W3, W5a, W5b). MOCK: root:Find answers only hud_battle and",
        "  the card panels, so a dial world overrides root.Find for 'SA_dial' (W.hud_battle._kids[1]._kids[1]). The live",
        "  copy's inventory sweep walks the mock's whole tree once on the first UI tick (comp._c.childcount counts it).",
        "  A walk world needs an owned ability the mock's dial never shows, else every button is claimed at boot and no",
        "  walk is ever due. UNPROVEN IN GAME: root:Find('SA_dial') answering (grep 'scan scope: dial' and the visit",
        "  counts in 'scan done:'). NOT DONE: the cards before the first event. The WORKSHOP ITEM STILL CARRIES ROUND",
        "  212. WAITING: the user's battle on this pack, then the release pack. Next battle from byte 1,136,053,587",
        "  (re-measure).",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("tracker and CLAUDE.md updated")


if __name__ == "__main__":
    main()
