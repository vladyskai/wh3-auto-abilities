#!/usr/bin/env python3
"""Round 207 (tuning): the notes in CLAUDE.md (installed build, builder, suite, the round note) and the tracker (10.84)."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
LOG = """
### 10.84 Round 207 (tuning) - two more of the same kind, from the afternoon code review (2026-11-22)

**Request (user, 2026-11-22):** "Tested again, seems to be working. Good job!" (round 206 field-confirmed), then "do
another check of the code, maybe there are more bugs like the one we found" and "check in general, not only the wave
abilities". The review is `docs\\WH3_code_review_2026-11-22_afternoon.md`.

**Fixed in this round (inside the wave family and option A, no new ruling needed):** the 5 drifting waves counted walking
enemies in a path's value (`FOURTH.ww_path_value` now honours the slot `FOURTH.ww_still_only`, set by the wave evaluator
and cleared per entry). A ground-only wave without an aim (Blue Fire of Chaos, rare) fell back to the enemy's centre with
orientation 0 and now holds.

**Proof:** harness 205 full suite **8,350 checks / 0 failures** (once). RED on the round-206 snapshot: a walking unit
pulls Wind of Death across both blocks. Tuning round: no workbook version. Everything else the review found waits for
rulings.
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.84 Round 207" not in s
    open(p, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + LOG)
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `b4db526095800c24addb534931f398df`, 1,642,503 bytes" + nl
            + "  (round 206, 2026-11-22, tuning: an exact wave's value counts standing enemies only).",
            "- Installed build: md5 `346e1448d5de45e57c805a81dde8436f`, 1,643,299 bytes" + nl
            + "  (round 207, 2026-11-22, tuning: the drifting waves count standing enemies only, no orientation-0 wave).")
    s = one(s, "20261122_standing_harness204/build_and_install206.py", "20261122_review_harness205/build_and_install207.py")
    s = one(s, "(harness204: 8,335 checks; it takes about 2 minutes)", "(harness205: 8,350 checks; it takes about 2 minutes)")
    a = "- ROUND 206 (2026-11-22, TUNING, INSTALLED:"
    note = [
        "- AFTERNOON CODE REVIEW (2026-11-22, `docs\\WH3_code_review_2026-11-22_afternoon.md`; user: \"do another check of the",
        "  code ... check in general, not only the wave abilities\"; round 206 FIELD-CONFIRMED: \"seems to be working\"). Six",
        "  read-only reviewers (ground-form orientation, effect shapes, moving targets, today's wave code, the core machinery,",
        "  the other evaluators), each finding re-checked against the source / game data where the doc says VERIFIED. ROUND",
        "  207 (TUNING, INSTALLED: test pack md5 346e1448..., release pack md5 eff788e5...) fixed two inside the existing",
        "  rulings: FOURTH.ww_path_value counts standing enemies only for waves (slot FOURTH.ww_still_only, set by",
        "  evaluate_enemy_wave, cleared in entry_reset: the cones share ww_path_value and are unchanged), and a ground-only",
        "  wave with no aim holds. Harness 205: 8,350 / 0 (once). EVERYTHING ELSE IN THE REVIEW WAITS FOR RULINGS: read the",
        "  doc's ranked list before the next round (the Loons with no friendly test, Lamprey's Bite, the 5 cones' shape,",
        "  enemy_wander / enemy_blob counting walkers, Chain Lightning dlc27 near our units, the player's own cast replaced",
        "  by the mod, the dead transformation re-scan, phantom casts after the last use, the search cost). MEASURED: the",
        "  free-aim search costs 11 to 13 ms per search under lupa (20 v 20 mock, few enemies in range), once per second",
        "  per armed wave caster, also while the ability recharges. Next battle from byte 1,052,150,771 (re-measure).",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("tracker and CLAUDE.md updated")


if __name__ == "__main__":
    main()
