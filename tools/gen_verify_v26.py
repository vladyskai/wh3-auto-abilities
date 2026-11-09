#!/usr/bin/env python3
"""Write tools/verify_xlsx_v26.py from verify_xlsx_v25.py (round 134: the v25 checks with the round-134 counts,
the 12 speed rows on their families and the 2 Thunderburner rows SKIPPED)."""
T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\verify_xlsx_v25.py", encoding="utf-8").read()
SPD = ('EXPECT.update({k: "charge_only" for k in ("wh_pro04_unit_abilities_apocalyptic_charge", '
       '"wh2_dlc16_item_abilities_twilight_horn_i", "wh_main_item_abilities_potion_of_speed", '
       '"wh_main_unit_abilities_blooood")})\n'
       'EXPECT.update({k: "charge_or_melee" for k in ("wh_main_spell_bound_book_of_arkhan", '
       '"wh2_dlc17_rune_abilities_rune_of_speed", "wh2_dlc17_rune_abilities_master_rune_of_speed", '
       '"wh2_dlc11_lord_abilities_lightning_reflexes", "wh2_dlc12_lord_abilities_master_of_the_skies", '
       '"wh_main_item_abilities_pendant_of_slaanesh", "wh_main_hero_abilities_slippery", '
       '"wh2_dlc11_lord_abilities_transfix")})\n'
       'SKIPPED134 = ("wh3_dlc25_unit_abilities_thunderburner", "wh3_dlc25_unit_abilities_thunderburner_upgraded")\n')
SKIPCHK = ('check(all(str(by_key[k][19]) == "SKIPPED (user decision)" and str(by_key[k][20]) == "-" for k in SKIPPED134),\n'
           '      "B4: the Thunderburner rows are not SKIPPED")\n'
           'check(sum(1 for r in rows if str(r[19]) == "SKIPPED (user decision)") == 24, "B5: skipped count is not 24")\n')
R = [
    (r'XLSX = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v25_2026-11-08.xlsx"',
     r'XLSX = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v26_2026-11-09.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v24_2026-11-08.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v25_2026-11-08.xlsx"'),
    (r"backups\round133\pre_v25_workbook_md5.txt", r"backups\round134\pre_v26_workbook_md5.txt"),
    ('PACK_MD5 = "7045f8da3e5b20853eda75f92e46f489"', 'PACK_MD5 = "ecc56210716b57f8d5ab53dc442c263c"'),
    ("KEEP_GATES = {", SPD + "KEEP_GATES = {"),
    ('"A1: %d rows in v25, %d in v24"', '"A1: %d rows in v26, %d in v25"'),
    ('check(len(impl_rows) == 752 and len(impl_keys) == 752,', 'check(len(impl_rows) == 750 and len(impl_keys) == 750,'),
    ('check("bound: 24 m (70% of', SKIPCHK + 'check("bound: 24 m (70% of'),
    ('check(len(entries) == 700 and len(mod_keys) == 752,', 'check(len(entries) == 698 and len(mod_keys) == 750,'),
    ("sum(te) == cell(100, 3) == 700 and sum(tk) == cell(100, 4) == 752,",
     "sum(te) == cell(100, 3) == 698 and sum(tk) == cell(100, 4) == 750,"),
    ('{"melee_unwavering": 342, MA: 10, MS: 2, SS: 1, "allies_firing_aura": 8, "under_fire": 3, "melee_or_under_fire": 4}',
     '{"melee_unwavering": 328, MA: 10, MS: 2, SS: 1, "allies_firing_aura": 8, "under_fire": 3, "melee_or_under_fire": 4, '
     '"charge_only": 5, "charge_or_melee": 36}'),
    ("check(cell(13, 3) == 752 and cell(14, 3) == 371,", "check(cell(13, 3) == 750 and cell(14, 3) == 373,"),
    ('startswith("DEFINITIONS - WH3 ability master v25"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v26"), "G1: title")'),
    ('startswith("22. ROUND 133")', 'startswith("23. ROUND 134")'),
    ('"G2: section 22 missing"', '"G2: section 23 missing"'),
    ('== "v25" and PACK_MD5', '== "v26" and PACK_MD5'),
    ('"G3: changelog v25 row or pack md5 missing"', '"G3: changelog v26 row or pack md5 missing"'),
    ("check(len(pre) == 44 and not changed,", "check(len(pre) == 46 and not changed,"),
    ('print("XLSX v25 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v26 VERIFY: %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v25 VERIFY OK")', 'print("XLSX v26 VERIFY OK")'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
s = s.replace('"""Verify docs/WH3_abilities_master_v25_2026-11-08.xlsx',
              '"""Verify docs/WH3_abilities_master_v26_2026-11-09.xlsx (round 134: the v25 checks plus the 12 speed rows '
              'and the 2 skipped Thunderburner rows) - formerly', 1)
open(T + r"\verify_xlsx_v26.py", "w", encoding="utf-8", newline="\n").write(s)
print("verifier written")
