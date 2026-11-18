#!/usr/bin/env python3
"""Round 179: CLAUDE.md (installed build, builder path, harness size, roster, workbook, open items)."""
P = r"C:\Users\vlady\Desktop\WH3_mod\CLAUDE.md"
s = open(P, encoding="utf-8").read()
R = [
    ("- Installed build: md5 `b8622a7b2b6c9bb6ed1c8c5844cac5bf`, 1,520,627 bytes\n"
     "  (round 178, 2026-11-18: the score-3 review rows 23-55; 3 new families).",
     "- Installed build: md5 `d7588fbfd32a951c9c65b4b1b052c284`, 1,531,016 bytes\n"
     "  (round 179, 2026-11-18: the score-3 review rows 115-134; 6 new families)."),
    ("Current roster (round 178): 938 ABILITIES entries / 992 ability keys / 123 trigger evaluator families.",
     "Current roster (round 179): 938 ABILITIES entries / 992 ability keys / 129 trigger evaluator families."),
    ("Wheel audit (workbook v61):", "Wheel audit (workbook v62):"),
    ("../mod_source/releases/20261118_score3_rows2_harness177/build_and_install178.py",
     "../mod_source/releases/20261118_score3_rows3_harness178/build_and_install179.py"),
    ("(harness177: 7,476 checks; it takes about 10 s)", "(harness178: 7,537 checks; it takes about 10 s)"),
    ("| `docs\\WH3_abilities_master_v61_2026-11-18.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v61.py`, verified by `tools\\verify_xlsx_v61.py`;",
     "| `docs\\WH3_abilities_master_v62_2026-11-18.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v62.py`, verified by `tools\\verify_xlsx_v62.py`;"),
    ("## 9. OPEN ITEMS\n\n",
     "## 9. OPEN ITEMS\n\n"
     "- ROUND 179 (2026-11-18, score-3 review rows 115-134; 'Items 115-134 approved'): NEW ally_charge_or_melee\n"
     "  (Inspired Assault x3), ally_melee_wavering_first (Inspired Defence x3, Da Boss), ally_value_melee (Orcs are da\n"
     "  Best!), ally_in_melee (Hellish Vigour), health_aura_ally_deep (Berry Wine, FOURTH.HEAL_DEEP_PCT 55),\n"
     "  heal_ground_best (Star of Avelorn: ally_range_real 200 + aura 15 -> 140 m reach, 10 m spot); ranked ally modes\n"
     "  charge_contact_melee, melee_wavering_first, value_melee, expendable_hp, cheap_healthy. Favour of the Fay on\n"
     "  melee_self_or_ally. wavering_self_or_ally lost its hidden ally-in-melee condition. Grut's Sickle (ally_winds):\n"
     "  winds low only, expendable first, else cheapest above FOURTH.GRUT_HEALTHY_PCT 75. The 12 moved entries keep\n"
     "  start_armed (33 plain lines). BUG FOUND: the shared heal re-check tests the ally against ah_range_m (the AREA);\n"
     "  ah_mode 'spot' re-checks against ab_range_m, 'deep' against 55%. Mock: the ally-to-ally gap is the OTHER unit's\n"
     "  dist_by_target[uid] (heal_ground_best's spot count). WAITING: row 128 Cold-Blooded's Lizardmen set (A: key prefix\n"
     "  lzd, 133 units, recommended; B: Lizardmen voice culture, 107). Row 92 (Heaven's Gate) says CLOSE IT in the doc,\n"
     "  not done (outside 115-134). Rows 57-114 wait. Next battle from byte 822,999,135.\n"),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
assert "\u2014" not in "".join(b for _, b in R)
open(P, "w", encoding="utf-8", newline="").write(s)
print("CLAUDE.md updated")
