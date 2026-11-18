#!/usr/bin/env python3
"""Round 178: CLAUDE.md (installed build, builder path, harness size, roster, workbook, open items)."""
P = r"C:\Users\vlady\Desktop\WH3_mod\CLAUDE.md"
s = open(P, encoding="utf-8").read()
R = [
    ("- Installed build: md5 `9efbf06698578da06329293ecdaee9b5`, 1,514,434 bytes\n"
     "  (round 177, 2026-11-18: the score-3 review rows 1-22; 9 new families).",
     "- Installed build: md5 `b8622a7b2b6c9bb6ed1c8c5844cac5bf`, 1,520,627 bytes\n"
     "  (round 178, 2026-11-18: the score-3 review rows 23-55; 3 new families)."),
    ("Current roster (round 177): 937 ABILITIES entries / 992 ability keys / 120 trigger evaluator families.",
     "Current roster (round 178): 938 ABILITIES entries / 992 ability keys / 123 trigger evaluator families."),
    ("Wheel audit (workbook v60):", "Wheel audit (workbook v61):"),
    ("../mod_source/releases/20261118_score3_rows_harness176/build_and_install177.py",
     "../mod_source/releases/20261118_score3_rows2_harness177/build_and_install178.py"),
    ("(harness176: 7,403 checks; it takes about 10 s)", "(harness177: 7,476 checks; it takes about 10 s)"),
    ("| `docs\\WH3_abilities_master_v60_2026-11-18.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v60.py`, verified by `tools\\verify_xlsx_v60.py`;",
     "| `docs\\WH3_abilities_master_v61_2026-11-18.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v61.py`, verified by `tools\\verify_xlsx_v61.py`;"),
    ("## 9. OPEN ITEMS\n\n",
     "## 9. OPEN ITEMS\n\n"
     "- ROUND 178 (2026-11-18, score-3 review rows 23-55; 'Approve rows 23-55. Row 56 stays the same.'): NEW\n"
     "  enemy_most_models (Chain Lightning x2, The Soulstealer: most models counted up to the AREA cap, FOURTH.MODELS_FLOOR\n"
     "  16, standing still), enemy_fast_or_melee (Glory Seeker x2, commander class on both arms), enemy_fast_fire_melee\n"
     "  (Prey of Anath Raema, Net Dem Up: FOURTH.eg_fire_first). The 6 plain roots on enemy_fast_near_ally (no melee arm).\n"
     "  Spellcaster list for Void Pendulum, Word of Change, Dweomer Leach Orb, Slann Gold. Eye of Khorne value-first. Trophy\n"
     "  Heads split (trophy_heads_daemon_wings). Bug fixed: a failed fast arm left eg_mode 'fast' (fallback cancelled).\n"
     "  LESSON, AGAIN (round 171's): the first pass built the FIRST proposals of rows 23-24, 29, 36-45 although the RULED\n"
     "  texts were committed in the doc; caught before the commit (first pass installed as bb0b9fe7..., never committed;\n"
     "  a second RED control H177_RED2=1 on docs\\backups\\round178\\first178_*.lua). Build from the CURRENT row text of the\n"
     "  doc on disk, every row, not from memory of the proposal. Surprise Squig (row 28) NOT built: it SUMMONS Explosive\n"
     "  Squigs, a new proposal is needed. Siegebreaker kept (100 + 100 AP to units). Rows 57-114 wait; rows 115-134 are\n"
     "  APPROVED (round 179; read their RULED texts and the doc's later edits: #92 closed, #126/#132 keep, #129, #133).\n"
     "  Next battle from byte 822,999,135.\n"),
    ("melee_health25, guard_aura, self_or_ally_fire_melee (ab_rank 'value_under_fire'), melee_healthy. Rows 23-134 of\n"
     "  docs\\WH3_score3_review_2026-11-18.md wait.",
     "melee_health25, guard_aura, self_or_ally_fire_melee (ab_rank 'value_under_fire'), melee_healthy. The rest of\n"
     "  docs\\WH3_score3_review_2026-11-18.md: see round 178."),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
assert "\u2014" not in "".join(b for _, b in R)
open(P, "w", encoding="utf-8", newline="").write(s)
print("CLAUDE.md updated")
