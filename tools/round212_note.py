#!/usr/bin/env python3
"""Round 212: CLAUDE.md (installed build, builder, suite, the engine fact), the tracker (10.89), open point 26, the
round document."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
LOG = """
### 10.89 Round 212 - a transformed unit is a new unit (2026-11-22)

**Field (the round-211 probe, archive\\logs\\battle_20261122_r211_rawprobe.txt, bytes 1,101,281,606-1,103,952,090):**
before Tz'arkan the army's own list holds unit 1001 (wh2_dlc14_def_cha_malus_darkblade_0_mp). After it the same slot
holds unit 1002 (wh2_dlc14_def_cha_malus_darkblade_tzarkan_0) with the keys Bloodstorm and Reaper of Souls, moving and
in melee. The script-unit list the mod read keeps answering 1001, frozen. The probe's reads all answered
(bm:alliances(), armies(), units(), is_player_controlled()).

**Change:** the watch list is built from `bm:get_player_army():units()` (`cast_gate.raw_items`). A unit both lists
have keeps the game's script unit. A unit only the army lists gets a script unit made by the mod (the unit and a new
controller). A script unit the army no longer lists is left out and dropped. An unreadable or empty army list falls
back to the script units. The two fresh-handle fetchers fall back to the made script unit. The poll also re-lists 2 s
after any cast. Roster unchanged: 982 entries / 1,035 keys, no workbook version.

**Proof:** harness 210 full suite **8,510 checks / 0 failures**. RED on the pre-round snapshot: the new unit never
casts and the frozen copy keeps casting. The cast trace of the whole suite (2,200 worlds, 1,771 casts) matches between
the test build and the release build apart from the 3 probe casts. Not seen in game.
"""
DOC = """# Round 212: a transformed unit is a new unit (2026-11-22)

## 1. What the probe showed

The user transformed Malus Darkblade once more with the round-211 probe installed.

| Time | The army's own list | The list the mod read |
|---|---|---|
| before Tz'arkan | unit 1001, Malus Darkblade, Deadly Onslaught and his other abilities | unit 1001 |
| after Tz'arkan | unit 1002, "malus_darkblade_tzarkan", Bloodstorm and Reaper of Souls, moving, in melee, losing health | unit 1001, frozen: same place, full health, not in melee |

So the game replaces the unit. The transformed Malus is a new unit with a new number. The old one stays in the list
the mod used, as a frozen copy.

## 2. The change, in plain words

- Every 10 seconds (and now also 2 seconds after any ability is cast) the mod rebuilds its list of units to watch. It
  now takes that list from the army's own unit list.
- A unit that both lists know is handled exactly as before.
- A unit that only the army's list knows (the transformed Malus) is added. The mod creates the order handle it needs
  to cast for that unit. If the game refuses that handle, the unit is left out and nothing is ordered.
- A unit that the army's list no longer has (the frozen old Malus) is dropped. It no longer casts and no longer counts
  as one of your units in the friendly-fire tests.
- If the army's own list cannot be read or is empty, the mod uses the old list, as before.

In battle: about 2 seconds after Tz'arkan, Bloodstorm and Reaper of Souls belong to a unit the mod watches, with their
letters and their normal triggers (Bloodstorm in melee, Reaper of Souls in melee below 75% health).

## 3. Proof

- RED control (the pre-round snapshot, `docs\\backups\\round212\\`): the new unit never casts, the frozen copy keeps
  casting.
- GREEN: harness 210, full suite, 8,510 checks, 0 failures.
- The cast trace: 2,200 worlds, 1,771 casts, the two builds differ only in the 3 probe casts.
- Test pack md5 `c0cff66cf0cf511028f31f492334c590` (1,665,749 bytes), release pack md5
  `17d703e53634735c64fc87ddee57f744`. No workbook version: the roster and every trigger text are unchanged.

## 4. Rebased pins (old value, new value, why)

| Where | Old | New | Why |
|---|---|---|---|
| harness 66, the count of `rebuild_unit_list()` in the file | 3 (annotated), 4 (live) | 4, 5 | the poll also re-lists 2 s after a cast |
| harness 66, world H2 (a unit the game stops listing) | still read 39 times and 5 casts before the re-list at 10 s | read 8 times, 1 cast | it cast at the first poll, so the re-list 2 s later drops it |

## 5. What is not verified

- Nothing of this round has been seen in a battle.
- `army:create_unit_controller()` and `uc:add_units(unit)` are the calls the game's own script library uses to make
  its script units. The mod has never called them in a battle. If they fail, the transformed unit is left out.
- Whether the letters on the transformed unit's buttons react to clicks (the selection callback is registered for the
  new unit the same way as for every unit).
- What happens when the transformation runs out: if the game brings back unit 1001, the mod watches it again through
  the army's own list. If it makes yet another new unit, that one is added the same way. Neither has been seen.
- Summons that join the player's own army are now watched too, when they own abilities of ours.
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.89 Round 212" not in s
    open(p, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + LOG)
    open(ROOT + "docs\\WH3_round212_transformation.md", "w", encoding="utf-8", newline="\n").write(DOC)
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `69ee6533fde49d1f5b811ca6a6a29299`, 1,662,332 bytes" + nl
            + "  (round 211, 2026-11-22, tuning: the read-only raw unit probe for the transformation).",
            "- Installed build: md5 `c0cff66cf0cf511028f31f492334c590`, 1,665,749 bytes" + nl
            + "  (round 212, 2026-11-22: the watch list comes from the army's own unit list, a transformed unit is a new unit).")
    s = one(s, "20261122_rawprobe_harness209/build_and_install211.py", "20261122_transform_harness210/build_and_install212.py")
    s = one(s, "(harness209: 8,487 checks; it takes about 2 minutes)", "(harness210: 8,510 checks; it takes about 2 minutes)")
    a = "- ROUND 211 (2026-11-22, TUNING, INSTALLED: test pack md5 69ee6533..., release pack md5 c692a26b...). FIELD on round"
    note = [
        "- ROUND 212 (2026-11-22; `docs\\WH3_round212_transformation.md`). INSTALLED: test pack md5 c0cff66c..., release pack",
        "  md5 17d703e5..., harness 210: 8,510 / 0, the cast trace matches apart from the 3 probe casts, NO workbook (roster",
        "  and trigger texts unchanged), tracker 10.89. NOT SEEN IN GAME. ENGINE FACT (the round-211 probe,",
        "  archive\\logs\\battle_20261122_r211_rawprobe.txt, bytes 1,101,281,606-1,103,952,090): A TRANSFORMATION REPLACES THE",
        "  UNIT. bm:get_player_army():units() then holds a NEW unit (id 1002, type ..._malus_darkblade_tzarkan_0, keys",
        "  Bloodstorm + Reaper of Souls) in the old one's slot. bm:get_scriptunits_for_local_players_army() keeps answering",
        "  the OLD script unit (1001), frozen. bm:alliances() / armies() / units() / army:is_player_controlled() all answer",
        "  in battle, item() is 1-based, and two battle.unit objects for the same unit compare EQUAL although tostring()",
        "  prints different addresses. BUILT: cast_gate.raw_items(sunits, total) (on cast_gate because rebuild_unit_list sits",
        "  ABOVE the FOURTH table and the main chunk has no room for a local: it must not name FOURTH, log, tick_count or",
        "  gone_units) feeds rebuild_unit_list: same id in both lists = the game's script unit, only in the army's list = a",
        "  made script unit { unit, uc = army:create_unit_controller() + uc:add_units(unit), zz_raw = true } kept in",
        "  cast_gate.raw_sunits, only in the script units = a ghost (cast_gate.ghosts) left out so the existing drop removes",
        "  it. Unreadable or empty army list = the script units alone. FOURTH.eg_fresh_caster_su / ab_fresh_friend_su fall",
        "  back to cast_gate.raw_sunits[id]. The poll re-lists 2 s after any cast (FOURTH.relist_at, set in",
        "  FOURTH.rescan_soon). UNPROVEN IN BATTLE: create_unit_controller / add_units from the mod, clicks on the new unit's",
        "  letters, the end of the transformation. Summons in the player's own army are now watched too. The raw probe of",
        "  round 211 stays in the test build. Next battle from byte 1,103,952,090 (re-measure): grep 'RAW t=' and the",
        "  ATTEMPT lines of bloodstorm / reaper_of_souls on ui id 1002.",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    p = ROOT + "docs\\WH3_open_points.md"
    s = open(p, encoding="utf-8", newline="").read()
    a = "| BUILT (rounds 209 and 210), ONE PART OPEN: the transformation | ROUND 211"
    s = one(s, a, "| BUILT (rounds 209, 210, 212): waiting for a battle with the transformation | ROUND 212 "
            "(`docs\\WH3_round212_transformation.md`): the probe showed that a transformation replaces the unit (Malus 1001 "
            "becomes a new unit 1002). The mod now takes its unit list from the army's own list, so the new unit is watched "
            "and the frozen old one dropped. ROUND 211")
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("tracker, CLAUDE.md, the open points and the round document updated")


if __name__ == "__main__":
    main()
