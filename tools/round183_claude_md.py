#!/usr/bin/env python3
"""Round 183: CLAUDE.md (installed build, builder path, harness size, roster, workbook, the open-rule count, open items)."""
P = r"C:\Users\vlady\Desktop\WH3_mod\CLAUDE.md"
s = open(P, encoding="utf-8").read()
R = [
    ("- Installed build: md5 `d4d805f72cb520f034d0928ee0522ece`, 1,551,894 bytes\n"
     "  (round 182, 2026-11-20: the finishers).",
     "- Installed build: md5 `bde9bc18a104768c685084b70d274fa7`, 1,554,974 bytes\n"
     "  (round 183, 2026-11-20: the rule-shut review rows 1-9)."),
    ("Current roster (round 182): 936 ABILITIES entries / 989 ability keys / 136 trigger evaluator families.",
     "Current roster (round 183): 945 ABILITIES entries / 998 ability keys / 136 trigger evaluator families."),
    ("Wheel audit (workbook v65): 1,123 in-wheel, 677 excluded, of 1,800 inventory rows; 1,003 implemented,\n"
     "120 not implemented among the included: 65 decided by the user, 55 OPEN",
     "Wheel audit (workbook v66): 1,123 in-wheel, 677 excluded, of 1,800 inventory rows; 998 implemented,\n"
     "125 not implemented among the included: 79 decided by the user, 46 OPEN"),
    ("../mod_source/releases/20261120_finishers_harness181/build_and_install182.py",
     "../mod_source/releases/20261120_ruleshut1_harness182/build_and_install183.py"),
    ("(harness181: 7,688 checks; it takes about 10 s)", "(harness182: 7,721 checks; it takes about 10 s)"),
    ("| `docs\\WH3_abilities_master_v65_2026-11-20.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v65.py`, verified by `tools\\verify_xlsx_v65.py`;",
     "| `docs\\WH3_abilities_master_v66_2026-11-20.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v66.py`, verified by `tools\\verify_xlsx_v66.py`;"),
    ("## 9. OPEN ITEMS\n\n",
     "## 9. OPEN ITEMS\n\n"
     "- WORKING DOCS (2026-11-20): `docs\\WH3_open_points.md` is the living list of open points. The 55 rule-shut + 9 revisit\n"
     "  abilities are reviewed in `docs\\WH3_rule_shut_review_2026-11-20.md`; its LIVE copy is the Claude Docs doc 'Rule-shut\n"
     "  abilities review' (https://claude.ai/artifact/HvLbtHifSNsbH8aeWcER5h, project 8904b7db-9839-4dad-bfcb-b6a2f5b4bd88):\n"
     "  a Ruling dropdown per row and comment threads. READ THE RULINGS FROM THAT DOC (dropdowns AND threads) before building.\n"
     "- ROUND 183 (2026-11-20, review rows 1-9; 'You may start implementing #1-9 for now'): the 2026-10-09 'own-troop damage'\n"
     "  rule was WRONG for all 19 rows (every damage phase targets enemies only). 9 NEW entries, existing families: Defiling\n"
     "  Deluge, Murderous Exhortations, Rod of Corruption, Wail of Malice on enemy_melee_near (aura_real 35; start unarmed);\n"
     "  Plaguereaper, Reaper of Souls on melee_health75; Shard Blade, Web of Shadows, Warp-Quake on melee_unwavering. The\n"
     "  Numbers sheet's row 16 / carrier table had stayed at 1,003 (stale): v66 re-derives them. New entries need the\n"
     "  regenerated key tables (round171_regen_tables.main) and hold_s rows for num_uses > 1. Next battle from byte\n"
     "  822,999,135.\n"),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
assert "\u2014" not in "".join(b for _, b in R)
open(P, "w", encoding="utf-8", newline="").write(s)
print("CLAUDE.md updated")
