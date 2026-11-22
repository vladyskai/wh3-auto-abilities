#!/usr/bin/env python3
"""Round 205, the closing notes: the tracker section 10.82 and CLAUDE.md (installed, the workbook, the suite)."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
LOG = """
### 10.82 Round 205 - the growing waves are cones, enemy single entities are not counted (2026-11-22)

**Field (user, 2026-11-22):** the Fiery Ring of Thori "worked perfectly this time with the dwarves" (round 204
field-confirmed). "I tested with Sunfang and it casted on the terrain, not on the enemy unit". Ruling in the same message:
"we should also ignore enemy single entities as the damage to them would be negligible".

**Cause:** Sunfang's vortex starts 0.1 m wide and grows to 12 m over its 48 m path (`battle_vortexs` start_radius,
goal_radius, expansion_speed 6 m/s at movement_speed 24 m/s). The mod treated it as 12 m wide from start to end, so it
moved the path 12 m away from our soldiers and the thin part of the cone burned empty ground.

**Change:** GENERATED `FOURTH.WW_CONE_TEXT` (`tools\\gen_wave_cone.py`): the 19 exact waves that grow, each with its
start radius and growth per metre. A soldier is under the wave when it is inside the width the wave has at that spot.
An exact wave's value counts enemy soldiers only (units of one man are skipped). Round document
`docs\\WH3_round205_cone.md`.

**Proof:** harness 203 full suite **8,320 checks / 0 failures**. RED on the round-204 snapshot: Sunfang's order puts 27 of
120 enemy soldiers under the real cone (the new one 104), and a lone enemy Lord draws a cast. Workbook v82 (27 trigger
texts). Not seen in game yet.
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.82 Round 205" not in s
    open(p, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + LOG)
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `11a01a69e4c513e1c4d444dab5f7606a`, 1,639,185 bytes" + nl
            + "  (round 204, 2026-11-22: exact waves count our soldiers under the wave, Tidecall and Wind Blast moved).",
            "- Installed build: md5 `c613f8a1338a6fce6fd87158bd2de72a`, 1,642,218 bytes" + nl
            + "  (round 205, 2026-11-22: the growing waves are cones, enemy single entities are not counted).")
    s = one(s, "20261122_exactwave_harness202/build_and_install204.py", "20261122_cone_harness203/build_and_install205.py")
    s = one(s, "(harness202: 8,305 checks; it takes about 2 minutes)", "(harness203: 8,320 checks; it takes about 2 minutes)")
    s = one(s, "WH3_abilities_master_v81_2026-11-22.xlsx` | the current master spreadsheet (versioned, newest wins). Built by "
            "`tools\\make_xlsx_v81.py`, verified by `tools\\verify_xlsx_v81.py <v80 md5> <pack md5>` (v81 = v80 + ",
            "WH3_abilities_master_v82_2026-11-22.xlsx` | the current master spreadsheet (versioned, newest wins). Built by "
            "`tools\\make_xlsx_v82.py`, verified by `tools\\verify_xlsx_v82.py <v81 md5> <pack md5>` (v82 = v81 + the SINGLE "
            "and CONE sentences on the 27 exact wave rows. v81 = v80 + ")
    s = one(s, "- ROUND 205 (2026-11-22) BUILT AND PROVEN, **INSTALL PENDING**: the game was running (WinError 32), the installed"
            + nl + "  test pack is still round 204 (md5 11a01a69...). TO FINISH: ask the user to close the game, run" + nl
            + "  mod_source\\releases\\20261122_cone_harness203\\build_and_install205.py, then `build_release.py --pack`, the cast"
            + nl + "  trace, workbook v82 (a CONE / single-entity sentence on the 27 exact wave rows), tracker 10.82, the round doc, ONE"
            + nl + "  commit. FIELD",
            "- ROUND 205 (2026-11-22, `docs\\WH3_round205_cone.md`) INSTALLED (the first install hit WinError 32, the user closed"
            + nl + "  the game): test pack md5 c613f8a1..., release pack md5 05556264..., the cast trace identical apart from the 3"
            + nl + "  probe casts, workbook v82, tracker 10.82. NOT SEEN IN GAME. FIELD")
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("tracker and CLAUDE.md updated")


if __name__ == "__main__":
    main()
