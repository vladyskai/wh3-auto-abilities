#!/usr/bin/env python3
"""Round 211 (tuning): CLAUDE.md (installed build, builder, suite, the field note), the tracker (10.88), open point 26."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
LOG = """
### 10.88 Round 211 (tuning) - the raw unit probe after a transformation (2026-11-22)

**Field (user, 2026-11-22; archive\\logs\\battle_20261122_r210_malus.txt, bytes 1,092,330,525-1,101,281,606):** the
Loons' new rule: "tested and it worked perfectly" (one order at Crypt Ghouls 23.8 m away). "the lag is gone". Malus
Darkblade again: "Reaper of Souls and the other Tzarkan ability did not fire while transformed".

**Reading of the log:** after Tz'arkan the handle the mod holds on Malus is frozen. Its MAP rows show the same position
(x -86.0, z -157.5), hp 1.00 and melee=0 from the transformation to the end of the battle, while the user fought. The
ability list read through that handle never changed, so round 210's re-read had nothing to find (no "owned abilities
changed" line). The card and the letters use the same unit number, 1001.

**Change (test build only, read-only):** `FOURTH.raw_probe` walks the game's own lists (alliances, armies, units)
every 2 s from the map probe and writes RAW_ARMY and RAW lines: id, type, position, men, health, melee, whether the
object is the one the mod holds (held=same / OTHER / none) and its keys of ours. It orders nothing and writes no mod
state. The release build removes the map probe, so it never runs there.

**Proof:** harness 209 full suite **8,487 checks / 0 failures** (once). RED on the pre-round snapshot: no RAW line.
Tuning round: no workbook, and the cast trace was not run again (no cast decision changed).
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.88 Round 211" not in s
    open(p, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + LOG)
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `8760b82d91ec7feaff51eaf39a0f5ea1`, 1,659,510 bytes" + nl
            + "  (round 210, 2026-11-22: the Loons' own rule, the breaths as cones from the caster, slow charges, transformations).",
            "- Installed build: md5 `69ee6533fde49d1f5b811ca6a6a29299`, 1,662,332 bytes" + nl
            + "  (round 211, 2026-11-22, tuning: the read-only raw unit probe for the transformation).")
    s = one(s, "20261122_replies2_harness208/build_and_install210.py", "20261122_rawprobe_harness209/build_and_install211.py")
    s = one(s, "(harness208: 8,479 checks; it takes about 2 minutes)", "(harness209: 8,487 checks; it takes about 2 minutes)")
    a = "- ROUND 210 (2026-11-22, the user's second replies; `docs\\WH3_round210_review_replies2.md`). INSTALLED: test pack md5"
    note = [
        "- ROUND 211 (2026-11-22, TUNING, INSTALLED: test pack md5 69ee6533..., release pack md5 c692a26b...). FIELD on round",
        "  210 (archive\\logs\\battle_20261122_r210_malus.txt, bytes 1,092,330,525-1,101,281,606): the Loons' rule",
        "  FIELD-CONFIRMED (\"tested and it worked perfectly\"), the lag is gone. Malus again: \"Reaper of Souls and the other",
        "  Tzarkan ability did not fire while transformed\". ENGINE FACT: after a transformation the battle_unit handle the mod",
        "  holds is FROZEN (same position, hp 1.00, melee=0 to the end of the battle, the same owned list), the card and the",
        "  HUD keep the SAME unit id (1001), and bm:get_scriptunits_for_local_players_army() keeps answering that stale",
        "  script unit. Round 210's re-read (FOURTH.reread_unit) reads the stale handle and finds nothing. BUILT (live copy",
        "  only, read-only, runs from FOURTH.map_tick, which the release removes): FOURTH.raw_probe walks bm:alliances() ->",
        "  armies() -> units() (1-based item()) every 2 s and logs 'RAW_ARMY t=' and 'RAW t=' lines (id, type, x, z, men, hp,",
        "  melee, held=same/OTHER/none, obj addresses, our keys). Harness 209: 8,487 / 0 (once), no workbook, no cast trace.",
        "  NEXT: the user transforms Malus once more, then read the RAW lines: if a unit with held=OTHER (or a new id) shows",
        "  the moving position and the Tz'arkan keys, the fix is to re-fetch the unit (and a controller for it) from the raw",
        "  list. army:is_player_controlled() and the raw walk are UNPROVEN in a battle ('RAW probe failed' = said once).",
        "  Next battle from byte 1,101,281,606 (re-measure).",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    p = ROOT + "docs\\WH3_open_points.md"
    s = open(p, encoding="utf-8", newline="").read()
    a = "| BUILT (rounds 209 and 210): waiting for a battle | ROUND 210"
    s = one(s, a, "| BUILT (rounds 209 and 210), ONE PART OPEN: the transformation | ROUND 211 (2026-11-22): the Loons' rule is "
            "field-confirmed and the lag is gone. The transformed Malus still casts nothing: the mod's handle on him is frozen "
            "after the transformation. A read-only probe of the game's raw unit list is installed. WAITING: one more battle "
            "with the transformation, then the fix. ROUND 210")
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("tracker, CLAUDE.md and the open points updated")


if __name__ == "__main__":
    main()
