#!/usr/bin/env python3
"""Round 203: CLAUDE.md (the installed build, the builder, the suite, the workbook, the round note) and open point 25."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `529eb5cc2e6e72c6a01de1df54f11de2`, 1,629,275 bytes" + nl
            + "  (round 202, 2026-11-22: the wave probe zz_wave, a console command).",
            "- Installed build: md5 `14e1d8cf6e1882279556c0a1bf80e2ee`, 1,635,145 bytes" + nl
            + "  (round 203, 2026-11-22: free aim for the 30 placed straight waves).")
    s = one(s, "20261122_waveprobe_harness200/build_and_install202.py", "20261122_freeaim_harness201/build_and_install203.py")
    s = one(s, "(harness200: 8,272 checks; it takes about 2 minutes)", "(harness201: 8,301 checks; it takes about 2 minutes)")
    s = one(s, "WH3_abilities_master_v79_2026-11-22.xlsx` | the current master spreadsheet (versioned, newest wins). Built by "
            "`tools\\make_xlsx_v79.py`, verified by `tools\\verify_xlsx_v79.py <v78 md5> <pack md5>` (v79 = v78 + ",
            "WH3_abilities_master_v80_2026-11-22.xlsx` | the current master spreadsheet (versioned, newest wins). Built by "
            "`tools\\make_xlsx_v80.py`, verified by `tools\\verify_xlsx_v80.py <v79 md5> <pack md5>` (v80 = v79 + the FREE AIM "
            "sentence on the 30 enemy_wave rows. v79 = v78 + ")
    a = "- ROUND 202 (2026-11-22, \"Yes, build the probe\";"
    note = [
        "- ROUND 203 (2026-11-22, \"A: but be careful ... check individually\" + \"All 30 placed\"; `docs\\WH3_round203_free_aim.md`):",
        "  FREE AIM for the 30 enemy_wave entries. Per standing enemy in range: the caster's line first (keeps a tie, old",
        "  unit-form order), then FOURTH.FREE_AIM_STEPS = 24 headings (FOURTH.ww_aim_value: start = centre - heading x (off +",
        "  half), the START inside eg_range_m of the caster, FOURTH.ww_line_value = the round-162 friendly test + path value).",
        "  A winning free heading sets FOURTH.ww_aim { x, z, deg, hx, hz } (cleared in entry_reset) and is ordered by",
        "  FOURTH.aim_cast: perform_special_ability_ground(key, v(x, terrain height, z), deg, 0), fail closed without a point.",
        "  ww_still_ok re-checks the same heading. Blue Fire x2 (ground-only) now go out at the path's start with the bearing",
        "  (legacy = true): before, on the enemy's centre with orientation 0 = misaimed since round 165. PERMANENT BUILD GATE:",
        "  every enemy_wave key is launch_source target_near_edge with target_ground true, every enemy_cone key",
        "  activator_front. TEST-ONLY ZZ_AUTO_TEST_NO_FREE_AIM / W.free_aim_on (a free-aim world also defines the global v and",
        "  bm.get_terrain_height). build_release counts 7 test switches. The cast trace differs from the release in exactly",
        "  the 3 zz_wave probe casts (expected). Log lines to grep in the next battle: 'FREE AIM: the wave starts at' and",
        "  'free-aim cast'. NOT SEEN IN GAME. Unverified: the exact start point, the 29 other keys, the poll cost of 24",
        "  headings. A heredoc broke two inline Python edits this round (again): edit tools with Edit / Write only.",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    p = ROOT + "docs\\WH3_open_points.md"
    s = open(p, encoding="utf-8", newline="").read()
    a = "| PROPOSED: waiting for the user | Today every straight wave and cone is tested on the caster-to-target heading only."
    s = one(s, a, "| BUILT (round 203, 2026-11-22): waiting for a battle | ROUND 203: free aim on the 30 placed waves (option A, "
            "standing targets, \"All 30 placed\"), `docs\\WH3_round203_free_aim.md`. The cones and the 2 charge waves keep the "
            "caster's line. Option B (moving targets, aimed ahead) was not chosen. Before: every straight wave and cone was "
            "tested on the caster-to-target heading only.")
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("docs updated")


if __name__ == "__main__":
    main()
