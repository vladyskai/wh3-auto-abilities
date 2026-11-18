#!/usr/bin/env python3
"""Round 180: CLAUDE.md (installed build, builder path, harness size, roster, workbook, open items)."""
P = r"C:\Users\vlady\Desktop\WH3_mod\CLAUDE.md"
s = open(P, encoding="utf-8").read()
R = [
    ("- Installed build: md5 `d7588fbfd32a951c9c65b4b1b052c284`, 1,531,016 bytes\n"
     "  (round 179, 2026-11-18: the score-3 review rows 115-134; 6 new families).",
     "- Installed build: md5 `6fbdf834e0a2e7cee83d529d7a3c3700`, 1,543,625 bytes\n"
     "  (round 180, 2026-11-18: the score-3 review rows 87-114 and 128; 4 new families, 3 closed)."),
    ("Current roster (round 179): 938 ABILITIES entries / 992 ability keys / 129 trigger evaluator families.",
     "Current roster (round 180): 935 ABILITIES entries / 989 ability keys / 133 trigger evaluator families."),
    ("Wheel audit (workbook v62):", "Wheel audit (workbook v63):"),
    ("../mod_source/releases/20261118_score3_rows3_harness178/build_and_install179.py",
     "../mod_source/releases/20261118_score3_rows4_harness179/build_and_install180.py"),
    ("(harness178: 7,537 checks; it takes about 10 s)", "(harness179: 7,622 checks; it takes about 10 s)"),
    ("| `docs\\WH3_abilities_master_v62_2026-11-18.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v62.py`, verified by `tools\\verify_xlsx_v62.py`;",
     "| `docs\\WH3_abilities_master_v63_2026-11-18.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v63.py`, verified by `tools\\verify_xlsx_v63.py`;"),
    ("## 9. OPEN ITEMS\n\n",
     "## 9. OPEN ITEMS\n\n"
     "- ROUND 180 (2026-11-18, score-3 review rows 87-114 and 128; 'Row 128 set A / Rows 57-86 do not touch / Rows 87-90\n"
     "  implement without melee / Row 91-96 implement as in the doc / Row 98 improve / Rows 99-114 implement / 107 ... I like\n"
     "  the option'). The 4 ground roots on enemy_fast_near_ally (the key forces the ground form) and on their REAL 100 m\n"
     "  (they carried their AREA as range_real). NEW health_aura_ally_rule (ah_pick_where with FOURTH.ab_atarget_ok:\n"
     "  Blood Chalice C, Breath of Darkness U, Mantra T), self_heal_clear (Bugman's, BUGMAN_CLEAR_M 38), self_hurt_attacked\n"
     "  (Charoi, Skar's, HURT_ATTACKED_PCT 75), charge_or_tired (Foe-Seeker; legacy badge zz_auto_badge_fs). Rock Bottom\n"
     "  > ROCK_BOTTOM_PCT 50. Eat da Runts!: hurt caster, cheapest healthy ally, no self arm. GENERATED lizard / tiger sets\n"
     "  (tools\\gen_rule_sets.py; ATARGET codes Z / T in gen_usage_keys.TARGET); CARD_ALLY_FAMILY gained wavering_ally_range\n"
     "  and health_aura_ally_rule. gen_ww_tables.Q80: the 80% reach for 5 keys. CLOSED: Heaven's Gate, Snowflake Pendant,\n"
     "  Stave of Avelorn. WAITING: row 98 Land Mine (its blast is 25 m: 'half a packed block' = 415 soldiers; options A 60\n"
     "  soldiers in the blast (recommended), B two enemy units touched, C keep); row 28 Surprise Squig (a new proposal).\n"
     "  NOT TOUCHED (range scan, tools\\scan_range_real.py): Curse of Khsar 35 vs 100 m (row in 57-86), Dispatch the Swarm\n"
     "  x2 30 vs 100 m, Lord of Undeath 200 vs 50 m. Every row of the score-3 review now has a decision: the user's\n"
     "  enemy-charge test proposal was given (Markus Wulfhart's Hunter's Snare, skill wh2_dlc13_skill_emp_wulfhart_personal_5).\n"
     "  GOTCHAS: the builder's content gates run AFTER the RPFM pack step (a scratch offline gate runner saved rounds);\n"
     "  the mock grants ammo_left only with ammo_start AND ammo_seq; the blob coverage samples 19 points (it overcounts\n"
     "  small units in a big blast). Next battle from byte 822,999,135.\n"),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
assert "\u2014" not in "".join(b for _, b in R)
open(P, "w", encoding="utf-8", newline="").write(s)
print("CLAUDE.md updated")
