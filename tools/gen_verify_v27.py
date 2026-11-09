#!/usr/bin/env python3
"""Write tools/verify_xlsx_v27.py from verify_xlsx_v26.py (round 135: the v26 checks, the 15 retriggered enemy
rows on their families, the 17 target-class rows, 57 families and the bombardment block at row 103)."""
T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\verify_xlsx_v26.py", encoding="utf-8").read()
ADD = ('EXPECT.update({k: "enemy_melee" for k in ("wh3_dlc27_spell_bound_acquiescence", "wh_dlc05_weapon_abilities_el_syf", '
       '"wh3_main_weapon_abilities_frost_shard_glaive", "wh3_cp1_lord_abilities_hidden_huntress", '
       '"wh2_dlc11_character_abilities_hornswaggle", "wh3_dlc26_unit_abilities_marked_for_eatin", '
       '"wh2_dlc11_character_abilities_taunt", "wh3_dlc25_hero_abilities_titan_headsman", '
       '"wh2_dlc15_lord_abilities_youre_next", "wh3_dlc29_hero_active_tendrils_of_the_sea")})\n'
       'EXPECT.update({k: "enemy_fast_near_ally" for k in ("wh2_dlc15_hero_abilities_mither", '
       '"wh2_dlc17_rune_abilities_rune_of_slowness", "wh2_dlc17_rune_abilities_master_rune_of_slowness", '
       '"wh3_dlc29_hero_abilities_whispering_mist")})\n')
CLS = ('check(sum(1 for r in rows if "; target class: " in str(r[21])) == 17, "B6: the target-class rows are not 17")\n'
       'check("target class: Lord/Hero only" in str(by_key["wh2_dlc14_lord_abilities_looming_dread"][21])\n'
       '      and "target class: large single entity only" in str(by_key["wh3_dlc29_character_active_mark_of_the_monster"][21]),\n'
       '      "B7: Looming Dread / Fecund Rebirth lack their class text")\n'
       'check("fast_speed() (the live run speed, m/s) >= FOURTH.FAST_ENEMY_MPS = 5" in str(by_key["wh2_dlc15_hero_abilities_mither"][21])\n'
       '      and "40 m" in str(by_key["wh2_dlc15_hero_abilities_mither"][21]), "B8: the fast-enemy text is wrong")\n')
R = [
    (r'XLSX = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v26_2026-11-09.xlsx"',
     r'XLSX = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v27_2026-11-09.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v25_2026-11-08.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v26_2026-11-09.xlsx"'),
    (r"backups\round134\pre_v26_workbook_md5.txt", r"backups\round135\pre_v27_workbook_md5.txt"),
    ('PACK_MD5 = "ecc56210716b57f8d5ab53dc442c263c"', 'PACK_MD5 = "79c8ffb8f6b0e052cc0feb337b87dde4"'),
    ("KEEP_GATES = {", ADD + "KEEP_GATES = {"),
    ('"A1: %d rows in v26, %d in v25"', '"A1: %d rows in v27, %d in v26"'),
    ('check("bound: 24 m (70% of', CLS + 'check("bound: 24 m (70% of'),
    ("te = [cell(r, 3) for r in range(44, 100)]", "te = [cell(r, 3) for r in range(44, 101)]"),
    ("tk = [cell(r, 4) for r in range(44, 100)]", "tk = [cell(r, 4) for r in range(44, 101)]"),
    ("names = [str(cell(r, 2)) for r in range(44, 100)]", "names = [str(cell(r, 2)) for r in range(44, 101)]"),
    ('len(te) == 56 and all(isinstance(x, int) for x in te), "F1: trigger table is not 56 integer rows")',
     'len(te) == 57 and all(isinstance(x, int) for x in te), "F1: trigger table is not 57 integer rows")'),
    ("sum(te) == cell(100, 3) == 698 and sum(tk) == cell(100, 4) == 750,",
     "sum(te) == cell(101, 3) == 698 and sum(tk) == cell(101, 4) == 750,"),
    ('cell(102, 1) == "Bombardment set (COMPLETE - round 108)" and cell(104, 3) == 131, "F3: bombardment block not at row 102")',
     'cell(103, 1) == "Bombardment set (COMPLETE - round 108)" and cell(105, 3) == 131, "F3: bombardment block not at row 103")'),
    ('"charge_only": 5, "charge_or_melee": 36}',
     '"charge_only": 5, "charge_or_melee": 36, "enemy_engaged_or_shot": 70, "enemy_melee": 14, "enemy_fast_near_ally": 4}'),
    ('startswith("DEFINITIONS - WH3 ability master v26"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v27"), "G1: title")'),
    ('startswith("23. ROUND 134")', 'startswith("24. ROUND 135")'),
    ('"G2: section 23 missing"', '"G2: section 24 missing"'),
    ('== "v26" and PACK_MD5', '== "v27" and PACK_MD5'),
    ('"G3: changelog v26 row or pack md5 missing"', '"G3: changelog v27 row or pack md5 missing"'),
    ("check(len(pre) == 46 and not changed,", "check(len(pre) == 48 and not changed,"),
    ('print("XLSX v26 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v27 VERIFY: %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v26 VERIFY OK")', 'print("XLSX v27 VERIFY OK")'),
    ('print("  1,800 rows = 1,123 + 677; 750 implemented; 24 skipped (the 2 Thunderburner rows new)")',
     'print("  1,800 rows = 1,123 + 677; 750 implemented; 24 skipped; 17 target-class rows")'),
    ('print("  join: 698 entries / 750 keys, every family matching; trigger table 56 families / 698 / 750; 12 speed rows on their families")',
     'print("  join: 698 entries / 750 keys, every family matching; trigger table 57 families / 698 / 750; 15 enemy rows on their families")'),
    ('print("  v1-v25: %d files byte-unchanged" % len(pre))', 'print("  v1-v26: %d files byte-unchanged" % len(pre))'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
open(T + r"\verify_xlsx_v27.py", "w", encoding="utf-8", newline="\n").write(s)
print("verifier written")
