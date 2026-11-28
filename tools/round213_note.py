#!/usr/bin/env python3
"""Round 213 (tuning): the tracker (10.90), CLAUDE.md and the open points. The packs are NOT built yet."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
LOG = """
### 10.90 Round 213 (tuning) - the cost of a selection (2026-11-28)

**Field (a Workshop comment, 2026-11-26):** "Works as intended, but it does add quite a bit of framerate lag (w/o
framerate counter noticing it) when selecting any own unit or unit groups during ongoing battle." The commenter runs
overhauls (SFO), an ability-wheel UI mod and mount expansions, and has not tested the mod alone.

**Reading of the code:** a selection change walks the whole battle HUD (600+ components) to find the ability buttons.
While one ability of the selected unit has no button, the walk is repeated every 4th UI tick for 48 ticks: 13 full
walks in 2.4 s, on every selection of that unit. A wheel that another mod rebuilt can make every claim fail, so every
selection pays that. This is the likely cause. It is NOT measured in the game.

**Change:** a unit whose button was still missing on the last tick of a window is remembered (`FOURTH.walk_quiet`).
Its later selections walk once on the event and retry once 4 ticks later. The first window of each unit, the two
cadences and the 5 s safety net are unchanged. No cast decision changes.

**Proof:** harness 211 full suite **8,525 checks / 0 failures** (once). RED on the pre-round snapshot: 13 walks on
the second and third selection, GREEN 2. The cast trace of the whole suite (2,204 worlds, 1,771 casts) matches between
the test build and the release build apart from the 3 probe casts. One rebased pin: harness 79 B2c, the later
selection of a unit whose button never came, 1 + the brisk retries -> 2. Tuning round: no workbook.

**NOT DONE:** no pack is built or installed. The round's build script installs the logged test pack, which the user
removed from the game on 2026-11-22 ("I just want the version that is in the workshop"). The release script
(`mod_source\\release\\`) is regenerated from the new source. Packing it and updating the Workshop item wait for the user.
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.90 Round 213" not in s
    open(p, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + LOG)
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "(harness210: 8,510 checks; it takes about 2 minutes)", "(harness211: 8,525 checks; it takes about 2 minutes)")
    a = "- ROUND 212 (2026-11-22; `docs\\WH3_round212_transformation.md`). INSTALLED: test pack md5 c0cff66c..., release pack"
    note = [
        "- ROUND 213 (2026-11-28, TUNING, SOURCE ONLY: NO PACK BUILT OR INSTALLED). FIELD (Workshop comment 2026-11-26, a user",
        "  with SFO, an ability-wheel UI mod and mount expansions): framerate lag when selecting own units or groups in",
        "  battle. LIKELY CAUSE (code reading + harness count, NOT measured in game): the HUD walk (600+ components) repeats",
        "  every 4th UI tick for the 48-tick window while a button of the selected unit is missing = 13 full walks per",
        "  selection, every time. BUILT: FOURTH.brisk_due(t, window_end, walk) + FOURTH.walk_quiet[unit id]: a unit whose",
        "  button was still missing on the LAST tick of a window retries ONCE (4 ticks after the event) on later selections",
        "  (13 walks -> 2). The line 'walk_now = (ui_ticks % 4) == 0' stays (harness 78/79 pin it) and the new call follows",
        "  it. A FIRST attempt that spaced ALL retries (4, 12, 28 ticks) broke about a dozen anti-regression pins on the",
        "  letter's response time (W4a, L3f, E3a-c, B1a, B2a) and was dropped. Harness 211: 8,525 / 0 (once), the cast trace",
        "  matches apart from the 3 probe casts, one rebased pin (harness 79 B2c: 1 + brisk -> 2). The mock counts walks in",
        "  W.hud_walks (the HUD handle is cached, so counting root:Find('hud_battle') counts nothing). THE TEST PACK IS OUT",
        "  OF THE GAME since 2026-11-22 by the user's wish (copy in archive\\packs\\removed_from_game\\): the round builder",
        "  (build_and_install213.py) was NOT run because it installs that pack. The release script is regenerated",
        "  (build_release.py without --pack). WAITING FOR THE USER: pack the release (build_release.py --pack writes",
        "  smart_ability_autocast.pack into the game's data folder) and press Update in the launcher. STILL UNEXAMINED cost",
        "  on the UI timer: fast_card_selection reads every unit card on every 50 ms tick, and the first-ever selection of",
        "  each unit still pays the 13 walks.",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("tracker and CLAUDE.md updated")


if __name__ == "__main__":
    main()
