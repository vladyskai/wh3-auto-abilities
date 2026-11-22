#!/usr/bin/env python3
"""Round 208 (tuning): CLAUDE.md (installed build, builder, suite, the review note), the tracker (10.85), the review doc."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
LOG = """
### 10.85 Round 208 (tuning) - the cost of the free-aim search (2026-11-22)

From the afternoon code review (items C5 and D). No cast decision changes. The wave evaluator skips its path search while
`can_perform_special_ability` reads exactly false (the recharge), and the poll on which a caster searches depends on its
unit id, so several wave casters do not all search on the same poll. `FOURTH.aim_next` is gone.

**Proof:** harness 206 full suite **8,365 checks / 0 failures** (once). RED on the round-207 snapshot: the search runs
while the ability cannot be cast (7 reads against 1), and four casters search on one poll. The cast trace of the whole
suite matches between the test build and the release build apart from the 3 probe casts. Tuning round: no workbook.
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.85 Round 208" not in s
    open(p, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + LOG)
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `346e1448d5de45e57c805a81dde8436f`, 1,643,299 bytes" + nl
            + "  (round 207, 2026-11-22, tuning: the drifting waves count standing enemies only, no orientation-0 wave).",
            "- Installed build: md5 `1d2c5abb71b2267b0ce6ce8ceb95d5ba`, 1,643,517 bytes" + nl
            + "  (round 208, 2026-11-22, tuning: the free-aim search is skipped while not castable and spread by unit id).")
    s = one(s, "20261122_review_harness205/build_and_install207.py", "20261122_searchcost_harness206/build_and_install208.py")
    s = one(s, "(harness205: 8,350 checks; it takes about 2 minutes)", "(harness206: 8,365 checks; it takes about 2 minutes)")
    s = one(s, "  per armed wave caster, also while the ability recharges. Next battle from byte 1,052,150,771 (re-measure).",
            "  per armed wave caster, also while the ability recharges. ROUND 208 (TUNING, INSTALLED: test pack md5 1d2c5abb...,"
            + nl + "  release pack md5 04a868e8...): the wave evaluator returns before the search when can_perform_special_ability is"
            + nl + "  exactly false, and searches on the polls where (tick_count + unit id) % FREE_AIM_EVERY == 0 (FOURTH.aim_next is"
            + nl + "  gone). Harness 206: 8,365 / 0 (once), the cast trace matches the release apart from the 3 probe casts. The"
            + nl + "  LAST reviewer's finding E1 (VERIFIED in the code): a unit slower than 3 m/s can never be 'charging'"
            + nl + "  (CHARGE_MIN_DISTANCE_M 12 and CHARGE_TIME_TO_CONTACT_S 4 need gap >= 12 and gap / speed <= 4): charge-only"
            + nl + "  abilities never fire on slow foot units. A RULING IS NEEDED. Next battle from byte 1,052,150,771 (re-measure).")
    open(p, "w", encoding="utf-8", newline="").write(s)
    p = ROOT + "docs\\WH3_code_review_2026-11-22_afternoon.md"
    s = open(p, encoding="utf-8", newline="").read()
    s = one(s, "## 1. Fixed today (round 207, inside rulings that already exist)",
            "## 1. Fixed today (rounds 207 and 208, inside rulings that already exist)")
    s = one(s, "| F2 | Blue Fire of Chaos (ground-only) could fall back to the old order, the enemy's centre with direction 0 (north), when the caster's position was unreadable or the enemy stood on the caster. | It holds. |",
            "| F2 | Blue Fire of Chaos (ground-only) could fall back to the old order, the enemy's centre with direction 0 (north), when the caster's position was unreadable or the enemy stood on the caster. | It holds. |\n"
            "| F3 | The path search of a wave ran once per second for the whole battle, also while the ability recharged (item C5). | It is skipped while the game says the ability cannot be cast. |\n"
            "| F4 | All armed wave casters searched on the same poll (item D). | The poll depends on the unit's id, so they are spread out. |")
    s = one(s, "Proof: harness 205, 8,350 checks, 0 failures (once). The old build reproduces F1. Test pack md5\n"
            "`346e1448d5de45e57c805a81dde8436f`, release pack rebuilt.",
            "Proof: harness 206, 8,365 checks, 0 failures (once). The old builds reproduce F1, F3 and F4. Test pack md5\n"
            "`1d2c5abb71b2267b0ce6ce8ceb95d5ba`, release pack rebuilt, the casts of both builds compared.\n\n"
            "F3 has a limit: for an ability with several uses the game answers \"can be cast\" even with none left, so those\n"
            "still search.")
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("tracker, CLAUDE.md and the review doc updated")


if __name__ == "__main__":
    main()
