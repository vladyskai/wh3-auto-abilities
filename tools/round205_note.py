#!/usr/bin/env python3
"""Round 205, first note in CLAUDE.md: built and proven, the INSTALL is pending (the game was running: WinError 32)."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"


def main():
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    a = "- ROUND 204 (2026-11-22; `docs\\WH3_round204_exact_wave.md`). USER RULING:"
    assert s.count(a) == 1
    note = [
        "- ROUND 205 (2026-11-22) BUILT AND PROVEN, **INSTALL PENDING**: the game was running (WinError 32), the installed",
        "  test pack is still round 204 (md5 11a01a69...). TO FINISH: ask the user to close the game, run",
        "  mod_source\\releases\\20261122_cone_harness203\\build_and_install205.py, then `build_release.py --pack`, the cast",
        "  trace, workbook v82 (a CONE / single-entity sentence on the 27 exact wave rows), tracker 10.82, the round doc, ONE",
        "  commit. FIELD (archive\\logs\\battle_20261122_r204_exact.txt, bytes 1,027,314,867-1,036,362,003): round 204 FIELD-",
        "  CONFIRMED on the Fiery Ring (\"it worked perfectly this time with the dwarves\"). Sunfang \"casted on the terrain,",
        "  not on the enemy unit\": its vortex is a CONE (start_radius 0.1 -> goal 12 at expansion_speed / movement_speed =",
        "  0.25 m per metre), the mod modelled a 12 m band and slid the path 12 m off our line. BUILT: GENERATED",
        "  FOURTH.WW_CONE_TEXT (tools\\gen_wave_cone.py, 19 growing exact waves: key=r0,growth per metre; only where the WW",
        "  table radius is the vortex's goal radius, so Hell Hammer is out) -> FOURTH.WW[k].r0 / .grow. FOURTH.ww_in_wave",
        "  tests a point against the radius the wave has THERE (the slot FOURTH.ww_cone is set by ww_line_value: wave_cover's",
        "  signature is pinned). USER RULING: \"we should also ignore enemy single entities as the damage to them would be",
        "  negligible\": an exact wave's value skips enemy units of 1 man (a path over single entities only is never",
        "  ordered). The live reason line of an exact wave now names its rule. Harness 203: 8,320 checks / 0 failures. RED:",
        "  the round-204 order covers 27 of 120 enemy soldiers with the real cone, the new one 104. One rebased pin (harness",
        "  202 EX5: 120 -> 100, a band measure of a cone-chosen path). Next battle from byte 1,036,362,003.",
    ]
    s = s.replace(a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("CLAUDE.md updated")


if __name__ == "__main__":
    main()
