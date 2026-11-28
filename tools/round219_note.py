#!/usr/bin/env python3
"""Round 219 (sign-off): the tracker (10.96) and CLAUDE.md."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
LOG = """
### 10.96 Round 219 - the placed blasts: most of the unit, standing cavalry (2026-11-28)

**Field (the round-218 build; archive\\logs\\battle_20261128_r218_perf.txt, bytes 1,172,897,502-1,188,201,797; 280 s,
40 units, 37 active abilities).**

Timing: the polls 62.9 ms per second, of which 13.4 ms log writes and about 1 ms the read-only probes:
**48.6 ms per second of real evaluator work**, the five worst seconds 102 to 113 ms. The UI timer 36.4 ms (cards 16.9,
the test log sweeps 9.8, the walks 6.6). The Workshop build would pay about 70 ms per second in a battle of this size.
Which evaluators are expensive is not known yet.

Brass Orb (user: "did not fire many times when I think it should have"): one cast per caster at t = 80 to 90 s, none
after. Locked until t = 185 s (13 s effect + 90 s recharge). From then on one target was free of our units: Free
Company Militia, 110 of 120 men, standing. The density line asks for 96 soldiers under the 12 m blast. The blast's
19-point sample gives 44 to 84 soldiers for that unit depending on its bearing (the first cast's 103 came from two
overlapping units). Two Outrider units (60 and 46 riders) stood still and clear and were never candidates: infantry
only. CORRECTION: the chat said 'about 94 soldiers, two short'. That figure was wrong (it scaled the first cast's 103,
which counted a second unit).

**Rulings (2026-11-28):** "A, most of the unit". Standing cavalry as a target: "yes". For the family: "yes".

**Change:**

- The 41 `enemy_wander` entries: a target qualifies on the old density line OR when the blast on its centre covers
  at least `FOURTH.COVER_FRACTION` 0.50 of the target unit's own living soldiers, never fewer than
  `FOURTH.COVER_MIN_MEN` 20 (`FOURTH.cover_need`, `FOURTH.cover_own`: a 16 x 8 grid in the unit's own frame). Both
  numbers are Claude's. The chat proposed 60% and a floor of 30. A 12 m circle covers 55% of the battle's 60 Outriders
  and 25 of the 46, so those numbers would never fire on them.
- Enemy cavalry (live unit_class cav..., at least 10 riders, not flying) is a target of the wanderers
  (`FOURTH.ww_map`, `m.cav`). Its depth: ranks x the game's mounted spacing, GENERATED `FOURTH.CAV_SPACING_TEXT`
  (`tools\\gen_blob_tables.py`, 183 units). Every other blob family keeps the infantry list.
- Live copy only: `FOURTH.perf_trig` times every evaluator call by trigger family, one `PERF TRIG 10s:` line per
  10 PERF lines.

**Proof:** harness 217 full suite **8,627 checks / 0 failures**. RED on the pre-round snapshot: no cast on the
110-man Militia, on the 60 Outriders, on the 46 Outriders (GREEN: one cast each). GREEN holds: moving cavalry, one
of our units 14 m from the target's centre, an 18-man remnant, 12 riders. The cast trace (2,244 worlds, 1,788 casts)
matches between the test build and the release build apart from the 3 probe casts. No older world changed its casts,
no rebased harness pin. Builder: the round-197 gate (the wanderers keep the plain trash rule) rebased to the rule's
new line. Workbook v85 (41 trigger texts).

**Not seen in game. Not done:** the cost of the evaluators (waiting for the PERF TRIG lines), the 5 s safety walk.
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.96 Round 219" not in s
    open(p, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + LOG)
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `95ebdc969775690fe5234cc33b91aa44`" + nl
            + "  (round 218, 2026-11-28, tuning, live copy only: the timing probe measures the test build's own log).",
            "- Installed build: md5 `d3e437f21661e7c6b2d8064a0c779e22`" + nl
            + "  (round 219, 2026-11-28: the placed blasts take most of a unit and standing cavalry, the evaluators timed by family).")
    s = one(s, "20261128_logcost_harness216/build_and_install218.py", "20261128_cover_harness217/build_and_install219.py")
    s = one(s, "(harness216: 8,594 checks; it takes about 2 minutes)", "(harness217: 8,627 checks; it takes about 2 minutes)")
    s = one(s, "| `docs\\WH3_abilities_master_v84_2026-11-22.xlsx` | the current master spreadsheet (versioned, newest wins). "
            "Built by `tools\\make_xlsx_v84.py`, verified by `tools\\verify_xlsx_v84.py <v83 md5> <pack md5>` (v84 = v83",
            "| `docs\\WH3_abilities_master_v85_2026-11-28.xlsx` | the current master spreadsheet (versioned, newest wins). "
            "Built by `tools\\make_xlsx_v85.py`, verified by `tools\\verify_xlsx_v85.py <v84 md5> <pack md5>` (v85 = v84 + "
            "the COVER sentence on the 41 enemy_wander rows. v84 = v83")
    a = "- ROUND 218 (2026-11-28, TUNING, LIVE COPY ONLY, TEST PACK INSTALLED: md5 95ebdc96...)."
    note = [
        "- ROUND 219 (2026-11-28, SIGN-OFF, TEST PACK INSTALLED: md5 d3e437f2...; workbook v85; tracker 10.96). FIELD on",
        "  round 218 (archive\\logs\\battle_20261128_r218_perf.txt, bytes 1,172,897,502-1,188,201,797, 280 s, 40 units, 37",
        "  active abilities): THE POLLS' REAL WORK IS 48.6 ms/s (62.9 measured, 13.4 log writes), worst seconds 102-113",
        "  ms: the Workshop build would pay about 70 ms/s in a battle this size. WHICH evaluators: unknown, hence",
        "  FOURTH.perf_trig (live only): 'PERF TRIG 10s: all evaluators X ms | family ms/calls | ...' (the 12 dearest).",
        "  NOTE FOR THE FIX: the poll calls ability.evaluate for EVERY armed pair on EVERY poll, also while the mod",
        "  itself knows the ability is locked (FOURTH.note_cast): a likely saving, NOT measured. BRASS ORB (user: 'did",
        "  not fire many times'): held on the only free target, 110 Free Company Militia, by the 96-soldier density line.",
        "  The 19-point blast sample (blob_score) gives 44 to 84 soldiers for the SAME thin line depending on its",
        "  bearing. Claude's chat figure 'about 94, two short' was WRONG. RULINGS: 'A, most of the unit', cavalry",
        "  'yes', the family 'yes'. BUILT for the 41 enemy_wander entries: the density line OR FOURTH.cover_own(e, r)",
        "  (a 16 x 8 grid in the unit's own frame) >= max(FOURTH.COVER_MIN_MEN 20, ceil(FOURTH.COVER_FRACTION 0.50 x",
        "  men)). Claude's numbers (60% / 30 were said in chat: a 12 m circle covers 55% of 60 Outriders and 25 of 46).",
        "  CAVALRY: blob_shape sets s.cav (unit_class cav...) with depth = ranks x GENERATED FOURTH.CAV_SPACING",
        "  (gen_blob_tables.cav_spacing_table, 183 units), blob_map fills m.cav, FOURTH.ww_map(m) = infantry + cavalry",
        "  for the wanderers ONLY (the build counts the uses of m.cav). Harness 217: 8,627 / 0, RED on the three field",
        "  targets, cast trace matches apart from the 3 probe casts, no rebased harness pin, the round-197 builder gate",
        "  rebased. NOT SEEN IN GAME. STILL OPEN: the 5 s safety walk (18-43 ms each). The WORKSHOP ITEM STILL CARRIES",
        "  ROUND 212. Next battle from byte 1,188,201,797 (re-measure): grep 'PERF TRIG' and the ATTEMPT lines of",
        "  brass_orb.",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("tracker and CLAUDE.md updated")


if __name__ == "__main__":
    main()
