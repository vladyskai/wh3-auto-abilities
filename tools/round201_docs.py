#!/usr/bin/env python3
"""Round 201: CLAUDE.md (the installed build, the roster, the builder, the suite, the workbook, the round note)."""
P = r"C:\Users\vlady\Desktop\WH3_mod\CLAUDE.md"


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    s = open(P, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `8c61a82ae7f86bb2820b5156ad65fc5d`, 1,626,713 bytes" + nl
            + "  (round 199, 2026-11-22: the ally arm, the infantry test, the remembered choice, the capital key).",
            "- Installed build: md5 `d5535679368f82138f341b6138667818`, 1,625,301 bytes" + nl
            + "  (round 201, 2026-11-22: the five Master Runes removed, Endless Whirlwind of Death added).")
    s = one(s, "Current roster (round 193): 985 ABILITIES entries / 1,038 ability keys / 141 trigger evaluator families.",
            "Current roster (round 201): 982 ABILITIES entries / 1,035 ability keys / 141 trigger evaluator families.")
    s = one(s, "Wheel audit (workbook v75): 1,120 in-wheel, 682 excluded, of 1,802 inventory rows; 1,038 implemented,",
            "Wheel audit (workbook v79): 1,115 in-wheel, 687 excluded, of 1,802 inventory rows; 1,035 implemented,")
    s = one(s, "82 not implemented among the included: 82 decided by the user, 0 OPEN",
            "80 not implemented among the included: 80 decided by the user, 0 OPEN")
    s = one(s, "../mod_source/releases/20261122_reviewfixes2_harness198/build_and_install199.py",
            "../mod_source/releases/20261122_masterrunes_harness199/build_and_install201.py")
    s = one(s, "(harness198: 8,210 checks; it takes about 2 minutes)", "(harness199: 8,245 checks; it takes about 2 minutes)")
    s = one(s, "| `docs\\WH3_abilities_master_v78_2026-11-22.xlsx` | the current master spreadsheet (versioned, newest wins). "
            "Built by `tools\\make_xlsx_v78.py`, verified by `tools\\verify_xlsx_v78.py <v77 md5> <pack md5>` (v78 = v77 + ",
            "| `docs\\WH3_abilities_master_v79_2026-11-22.xlsx` | the current master spreadsheet (versioned, newest wins). "
            "Built by `tools\\make_xlsx_v79.py`, verified by `tools\\verify_xlsx_v79.py <v78 md5> <pack md5>` (v79 = v78 + "
            "round 201: the 5 Master Runes EXCLUDED, Endless Whirlwind of Death x2 IMPLEMENTED, Numbers recomputed, Cards "
            "rebuilt. v78 = v77 + ")
    i = s.index("- FIELD 2026-11-22 (the Dwarf battle on the RELEASE build")
    j = s.index("- ROUND 200 (2026-11-22,", i)
    note = [
        "- ROUND 201 (2026-11-22, `docs\\WH3_round201_master_runes.md`). FIELD (the user's Dwarf battle on the RELEASE build, no",
        "  log): Master Rune of Slowness, a RIGHT-hand-bar button, FIRED BY ITSELF (its entry rode a default-armed family, and",
        "  a cast needs no badge). Rulings: \"do it\" on removing the five Master Runes the game marks as runes (Breaking,",
        "  Negation, Slowness, Speed, Oath & Steel) and \"do it\" on Endless Whirlwind of Death = the trigger of Whirlwind of",
        "  Death (2 new entries on melee_unwavering; the tracker's old 'rejected (friendly fire)' was wrong by the data: the",
        "  same vortexes, affects_allies false). PERMANENT BUILD GATE: no key with unit_abilities.source_type = rune (12 keys)",
        "  may appear in the script. Master Rune of Flight / Immolation are source_type active and stay (asked the user where",
        "  he sees them, no answer yet). Harness 199: old worlds moved to siblings (harness 123/124 Hunter's Trap, harness 133",
        "  G3 Slippery). The release pack was rebuilt (`build_release.py --pack`, md5 007f09d5..., cast trace identical: 2,083",
        "  worlds / 1,656 casts; release_cast_trace.py takes the harness as a 3rd argument and must run from the project",
        "  root). The Workshop item (HIDDEN, title + text set by Claude in the Steam app through computer use: Chrome is not",
        "  signed in to Steam) still carries the ROUND 199 pack: the user must press UPDATE in TW Launcher (Legacy). Both",
        "  packs are in the data folder (the release stands down). Next battle from byte 983,121,663. DONATIONS (researched",
        "  2026-11-22): SEGA's EULA and CA's page forbid selling mods and say 'not permitted to charge or ask for money', no",
        "  source allows or names tips, big mods carry Patreon / Ko-fi links: a tolerated grey area. PayPal is excluded by the",
        "  user. Recommended Ko-fi with Stripe. GIFS: the user records the clips (Game Bar), Claude converts (ffmpeg is",
        "  installed). A leftover scratch folder C:\\t_red (two harness copies) could not be deleted by Claude.",
    ]
    s = s[:i] + nl.join(note) + nl + s[j:]
    open(P, "w", encoding="utf-8", newline="").write(s)
    print("CLAUDE.md updated")


if __name__ == "__main__":
    main()
