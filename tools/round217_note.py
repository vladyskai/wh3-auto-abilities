#!/usr/bin/env python3
"""Round 217 (tuning): the tracker (10.94) and CLAUDE.md (the third measurement, the two fixes)."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
LOG = """
### 10.94 Round 217 (tuning) - the group walk and the card cadence (2026-11-28)

**Field (the round-216 build; archive\\logs\\battle_20261128_r216_perf.txt, bytes 1,136,053,587-1,142,970,468; 139 s,
21 units, the user's own PC):** the mod took 62 ms of every second (124, then 71).

| Where | Measured |
|---|---|
| The game's Find answers SA_dial | yes (`scan scope: dial`): a dial walk visits 12 components (empty) or 52 (a wheel), not 770 |
| HUD walks | 154 in 139 s, 11.6 ms on average, 12.9 ms per second, the worst UI tick 51 ms (63 before) |
| The whole HUD after the dial | 40 times, 39 found nothing: 14 on a group of 8, 13 on the whole army, 11 on the two owners together |
| The unit cards | 33 to 85 ms per second for the 57 s before the first selection event, then 10 to 30 |
| The test build's own log sweeps | 8.8 ms per second (not in the Workshop build) |
| The polls (the ability checks) | 6.4 ms per second |

**Change:**

- `FOURTH.walk_group_waiting`: with several units selected the whole-HUD walk follows the dial walk only for an ability
  EVERY selected unit owns and that has no letter yet (a group's wheel shows only shared abilities).
- `FOURTH.cards_due`: the unit cards are read every 4th UI tick as soon as the game accepted a selection callback
  (`cast_gate.sel_registered`), not only after the first event. No selection API = every tick as before.

**Proof:** harness 215 full suite **8,588 checks / 0 failures** (once). RED on the pre-round snapshot: the rest of the
HUD is entered twice for a group whose units own different abilities (GREEN 0), the cards are read on 100% of the ticks
before the first event (GREEN 25%). The cast trace (2,227 worlds, 1,777 casts) matches between the test build and the
release build apart from the 3 probe casts. Rebased pins: harness 76 DET, BL1 and BL2 / BL3 (one card sweep took one
UI tick, now four), harness 213 CD1a (the reads before the first event are at the slow rate too). The builder's
round-215 gate was rebased to the new card line. No workbook.

**Effect to expect:** a selection only the unit card reports (the game sent no event) reaches the letters within 4
UI ticks (0.2 s) from the start of the battle, where it was 1 tick before the first event.
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.94 Round 217" not in s
    open(p, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + LOG)
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `ae5536f9d59216189350a468f4b92f09`" + nl
            + "  (round 216, 2026-11-28, tuning: the HUD walk starts at the ability dial, no walk while nothing of ours is selected).",
            "- Installed build: md5 `72c2931c3cffc8860b2167f88af77d12`" + nl
            + "  (round 217, 2026-11-28, tuning: no whole-HUD walk for a group's unshared abilities, the unit cards 5 times a second from the start).")
    s = one(s, "20261128_walkscope_harness214/build_and_install216.py", "20261128_groupcards_harness215/build_and_install217.py")
    s = one(s, "(harness214: 8,569 checks; it takes about 2 minutes)", "(harness215: 8,588 checks; it takes about 2 minutes)")
    a = "- ROUND 216 (2026-11-28, TUNING, TEST PACK INSTALLED: md5 ae5536f9...)."
    note = [
        "- ROUND 217 (2026-11-28, TUNING, TEST PACK INSTALLED: md5 72c2931c...). FIELD on round 216",
        "  (archive\\logs\\battle_20261128_r216_perf.txt, bytes 1,136,053,587-1,142,970,468, 139 s): 62 ms OF EVERY SECOND",
        "  (124, 71). ENGINE FACT: core:get_ui_root():Find('SA_dial', false) ANSWERS (recursive): a dial walk visits 12",
        "  components (no wheel) or 52 (a wheel), the whole HUD 770. The whole HUD followed the dial 40 times, 39 for",
        "  nothing, ALL ON GROUPS (a group's wheel shows only the abilities every selected unit owns). Cards: 33-85 ms/s",
        "  for the 57 s before the first selection EVENT, then 10-30. BUILT: FOURTH.walk_group_waiting (several units",
        "  selected: wait only for an ability EVERY selected unit owns), cast_gate.sel_registered = true where the game",
        "  accepts a selection callback (that code sits ABOVE the FOURTH table) and FOURTH.cards_due reads it (5 Hz from",
        "  the start, every tick only where no callback was accepted). Harness 215: 8,588 / 0 (once), cast trace matches",
        "  apart from the 3 probe casts, rebased pins harness 76 DET / BL1 / BL2-3 (one sweep = 4 ticks) and harness 213",
        "  CD1a. A later round that changes a line an OLD builder gate pins must rebase that gate in make_builderNNN",
        "  (the round-215 gate refused the first build here, the installed pack stayed). The WORKSHOP ITEM STILL CARRIES",
        "  ROUND 212. WAITING: the user's battle on this pack, then the release pack. Next battle from byte",
        "  1,142,970,468 (re-measure).",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("tracker and CLAUDE.md updated")


if __name__ == "__main__":
    main()
