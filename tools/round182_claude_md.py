#!/usr/bin/env python3
"""Round 182: CLAUDE.md (installed build, builder path, harness size, roster, workbook, rule 3's second exception, open
items)."""
P = r"C:\Users\vlady\Desktop\WH3_mod\CLAUDE.md"
s = open(P, encoding="utf-8").read()
R = [
    ("- Installed build: md5 `3e567bc557f624b8298378fb8107d156`, 1,548,820 bytes\n"
     "  (round 181, 2026-11-20: Land Mine, Surprise Squig!, the range fixes).",
     "- Installed build: md5 `d4d805f72cb520f034d0928ee0522ece`, 1,551,894 bytes\n"
     "  (round 182, 2026-11-20: the finishers)."),
    ("Current roster (round 181): 936 ABILITIES entries / 989 ability keys / 135 trigger evaluator families.",
     "Current roster (round 182): 936 ABILITIES entries / 989 ability keys / 136 trigger evaluator families."),
    ("Wheel audit (workbook v64):", "Wheel audit (workbook v65):"),
    ("../mod_source/releases/20261120_landmine_squig_harness180/build_and_install181.py",
     "../mod_source/releases/20261120_finishers_harness181/build_and_install182.py"),
    ("(harness180: 7,663 checks; it takes about 10 s)", "(harness181: 7,688 checks; it takes about 10 s)"),
    ("| `docs\\WH3_abilities_master_v64_2026-11-20.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v64.py`, verified by `tools\\verify_xlsx_v64.py`;",
     "| `docs\\WH3_abilities_master_v65_2026-11-20.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v65.py`, verified by `tools\\verify_xlsx_v65.py`;"),
    ("   constant, exempted explicitly from the range map, and commented as a test value.\n",
     "   constant, exempted explicitly from the range map, and commented as a test value. SECOND exception (user ruling\n"
     "   2026-11-20, round 182): the Executioner (a single-entity target) uses 90% of its real range\n"
     "   (`FOURTH.SINGLE_RANGE_FRACTION`, entry field `range_frac = 0.90`); the build refuses it on any other entry.\n"),
    ("## 9. OPEN ITEMS\n\n",
     "## 9. OPEN ITEMS\n\n"
     "- ROUND 182 (2026-11-20, the finishers): the Executioner on NEW enemy_finisher (shot kind 'finisher': the single\n"
     "  entity with the lowest health %, value on a tie, clear of ours, caster standing; 90% bound 225 m); the Emperor's\n"
     "  Executioner: shot kind 'execute' ranks the HIGHEST health % below the line (user); Skjalandir's Fall on NEW\n"
     "  melee_or_self_shooting (its phase imbue_contact = Blinded! on every hit; +90 accuracy). melee_or_shooting_into_melee\n"
     "  is empty (code kept). gen_shot_tables.FAMILIES gained enemy_finisher (61 keys); the blob tables 68. No battle read\n"
     "  since round 175. Next battle from byte 822,999,135.\n"),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
assert "\u2014" not in "".join(b for _, b in R)
open(P, "w", encoding="utf-8", newline="").write(s)
print("CLAUDE.md updated")
