#!/usr/bin/env python3
"""Round 214 (tuning): the tracker (10.91) and CLAUDE.md (the pack type, the installed build, the timing probe)."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
LOG = """
### 10.91 Round 214 (tuning) - the test pack is a normal mod pack, the timing probe (2026-11-28)

**Rulings (user, 2026-11-28):** on testing changes without the Workshop: "Yes, set it up that way" (the test build as
a normal mod pack with a checkbox, the Workshop build stands down while it is ticked). And: "figure out a way we can
measure the FPS drop, what causes it and how to fix it (if it is there)".

**Change:**

- The test pack `zz_test_deadly_onslaught.pack` is type **Mod** since `build_and_install214.py` (it was Movie, which the
  game always loads). The build refuses any other type. The user ticks it in the mod manager to test.
- The local copy of the Workshop pack left the game's data folder (it had the same file name as the subscribed one).
  `build_release.py --pack` puts it back for an upload.
- The timing probe (test build only): `FOURTH.perf_now` / `perf_add` / `perf_end_ui` measure with `os.clock()` and
  write one `PERF 1s:` line per 20 UI ticks: the whole UI tick, the HUD walk, the unit cards, the selection events,
  the letters, the test build's own sweeps, the polls. `tools\\analyze_perf.py <log> --from <offset>` reads them.
- Round 213's fix (a unit whose button never came retries once) is in this pack.

**Proof:** harness 212 full suite **8,533 checks / 0 failures** (once). RED on the pre-round snapshot: no PERF line.
The cast trace (2,207 worlds, 1,777 casts) matches between the test build and the release build apart from the 3
probe casts. Tuning round: no workbook. NOT SEEN IN GAME: the test pack as a Mod pack, `os.clock()` in a battle.
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.91 Round 214" not in s
    open(p, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + LOG)
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Packed as a Movie pack and installed as",
            "- Packed as a **Mod** pack since round 214 (a checkbox in the mod manager: the user ticks it to test, and the" + nl
            + "  Workshop build stands down while it is loaded. It was a Movie pack, which the game always loads) and installed as")
    s = one(s, "- Installed build: md5 `c0cff66cf0cf511028f31f492334c590`, 1,665,749 bytes" + nl
            + "  (round 212, 2026-11-22: the watch list comes from the army's own unit list, a transformed unit is a new unit).",
            "- Installed build: md5 `2a8972cfce788db53d7cd05bc8d80118`" + nl
            + "  (round 214, 2026-11-28, tuning: type Mod, the timing probe, round 213's selection fix).")
    s = one(s, "20261122_transform_harness210/build_and_install212.py", "20261128_perfprobe_harness212/build_and_install214.py")
    s = one(s, "(harness211: 8,525 checks; it takes about 2 minutes)", "(harness212: 8,533 checks; it takes about 2 minutes)")
    a = "- ROUND 213 (2026-11-28, TUNING, SOURCE ONLY: NO PACK BUILT OR INSTALLED)."
    note = [
        "- ROUND 214 (2026-11-28, TUNING, TEST PACK INSTALLED: md5 2a8972cf..., type MOD). USER: \"Yes, set it up that way\"",
        "  = the workflow for testing without the Workshop: the test pack is a normal mod pack (build_and_install214.py:",
        "  SetPackFileType Mod, the build refuses another type), the user TICKS it in the mod manager to test and unticks",
        "  it to play the Workshop build. The release stands down while the test build is loaded, so both may be ticked.",
        "  The local copy of smart_ability_autocast.pack was REMOVED from the game's data folder (same file name as the",
        "  subscribed one; copy in archive\\packs\\removed_from_game\\): build_release.py --pack puts it back only for an",
        "  upload. The WORKSHOP ITEM STILL CARRIES ROUND 212: rounds 213-214 are not published. THE TIMING PROBE (live copy",
        "  only): FOURTH.perf_now / perf_add / perf_end_ui, os.clock(), one 'PERF 1s:' log line per 20 UI ticks (ui, walk,",
        "  cards, select, badges, diag, poll), active only when zz_badge_set exists (the development build) and",
        "  ZZ_AUTO_TEST_NO_PERF is not true (the 8th test switch: load_world sets it unless W.perf_on, build_release counts",
        "  8). Timed INSIDE ui_tick and poll, never by wrapping them: the harness identifies ui_tick, the poll body and",
        "  other functions by identity (CUR_UI_FN, POLL_BODY_FN), a wrapper would break those probes. Read a battle with",
        "  tools\\analyze_perf.py <log> --from <offset>. Harness 212: 8,533 / 0 (once), the cast trace matches apart from",
        "  the 3 probe casts. UNPROVEN IN GAME: a Mod-type test pack loading and logging, os.clock() in battle Lua. Next",
        "  battle from byte 1,111,622,234 (re-measure).",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("tracker and CLAUDE.md updated")


if __name__ == "__main__":
    main()
