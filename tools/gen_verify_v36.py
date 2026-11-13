#!/usr/bin/env python3
"""Write tools/verify_xlsx_v36.py from verify_xlsx_v35.py (round 144)."""
T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\verify_xlsx_v35.py", encoding="utf-8").read()
ADD = ('EXPECT.update({"wh3_dlc24_unit_abilities_hags_denial": "self_last_stand", '
       '"wh2_dlc15_unit_abilities_mimic_ruinshelter": "melee_unwavering", '
       '"wh3_main_banner_abilities_banner_of_hellfire": "melee_unwavering", '
       '"wh2_dlc15_unit_abilities_rock_bottom": "self_out_of_ammo", '
       '"wh3_dlc29_item_abilities_morikhane_the_black_armour": "under_fire", '
       '"wh2_dlc13_character_ability_hunters_call": "melee_or_wavering_aura", '
       '"wh3_dlc29_item_abilities_icon_of_the_king": "health_aura_self_undead", '
       '"wh3_dlc25_item_abilities_the_gold_standard": "ally_hurt_melee", '
       '"wh3_dlc29_hero_active_ghostly_howl": "enemy_wavering", '
       '"wh3_dlc24_unit_passive_petrifying_gaze": "enemy_fast_near_ally"})\n')
R = [
    (r'docs\WH3_abilities_master_v35_2026-11-13.xlsx"', r'docs\WH3_abilities_master_v36_2026-11-13.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v34_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v35_2026-11-13.xlsx"'),
    (r"backups\round143\pre_v35_workbook_md5.txt", r"backups\round144\pre_v36_workbook_md5.txt"),
    ('PACK_MD5 = "c2168f7908cb3e2403d7dbfbd94c017e"', 'PACK_MD5 = "826ef8834fbc437c35ecc86a298b931e"'),
    ("KEEP_GATES = {", ADD + "KEEP_GATES = {"),
    ('"A1: %d rows in v35, %d in v34"', '"A1: %d rows in v36, %d in v35"'),
    ("check(len(impl_rows) == 767 and len(impl_keys) == 767,", "check(len(impl_rows) == 777 and len(impl_keys) == 777,"),
    ("check(len(entries) == 712 and len(mod_keys) == 767,", "check(len(entries) == 722 and len(mod_keys) == 777,"),
    ('check(sum(1 for r in rows if str(r[19]) == "SKIPPED (user decision)") == 24, "B5: skipped count is not 24")',
     'check(sum(1 for r in rows if str(r[19]) == "SKIPPED (user decision)") == 27, "B5: skipped count is not 27")'),
    ("te = [cell(r, 3) for r in range(44, 112)]", "te = [cell(r, 3) for r in range(44, 117)]"),
    ("tk = [cell(r, 4) for r in range(44, 112)]", "tk = [cell(r, 4) for r in range(44, 117)]"),
    ("names = [str(cell(r, 2)) for r in range(44, 112)]", "names = [str(cell(r, 2)) for r in range(44, 117)]"),
    ('len(te) == 68 and all(isinstance(x, int) for x in te), "F1: trigger table is not 68 integer rows")',
     'len(te) == 73 and all(isinstance(x, int) for x in te), "F1: trigger table is not 73 integer rows")'),
    ("sum(te) == cell(112, 3) == 712 and sum(tk) == cell(112, 4) == 767,",
     "sum(te) == cell(117, 3) == 722 and sum(tk) == cell(117, 4) == 777,"),
    ('cell(114, 1) == "Bombardment set (COMPLETE - round 108)" and cell(116, 3) == 131, "F3: bombardment block not at row 114")',
     'cell(119, 1) == "Bombardment set (COMPLETE - round 108)" and cell(121, 3) == 131, "F3: bombardment block not at row 119")'),
    ('"melee_unwavering": 307,', '"melee_unwavering": 309, "self_last_stand": 1, "self_out_of_ammo": 1, '
     '"health_aura_self_undead": 1, "ally_hurt_melee": 1, "enemy_wavering": 1, "melee_or_wavering_aura": 2,'),
    ('"under_fire": 3,', '"under_fire": 4,'),
    ('"enemy_fast_near_ally": 7}', '"enemy_fast_near_ally": 8}'),
    ('"melee_or_wavering_aura": 1,', ''),
    ("check(cell(13, 3) == 767 and cell(14, 3) == 356,", "check(cell(13, 3) == 777 and cell(14, 3) == 346,"),
    ('startswith("DEFINITIONS - WH3 ability master v35"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v36"), "G1: title")'),
    ('startswith("32. ROUND 143")', 'startswith("33. ROUND 144")'),
    ('"G2: section 32 missing"', '"G2: section 33 missing"'),
    ('== "v35" and PACK_MD5', '== "v36" and PACK_MD5'),
    ('"G3: changelog v35 row or pack md5 missing"', '"G3: changelog v36 row or pack md5 missing"'),
    ("check(len(pre) == 64 and not changed,", "check(len(pre) == 66 and not changed,"),
    ('print("XLSX v35 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v36 VERIFY: %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v35 VERIFY OK")', 'print("XLSX v36 VERIFY OK")'),
    ("767 implemented; 24 skipped", "777 implemented; 27 skipped"),
    ("join: 712 entries / 767 keys, every family matching; trigger table 68 families / 712 / 767",
     "join: 722 entries / 777 keys, every family matching; trigger table 73 families / 722 / 777"),
    ('open batch 2 on their families")', 'open batch 3 on their families")'),
    ('print("  v1-v34: %d files byte-unchanged" % len(pre))', 'print("  v1-v35: %d files byte-unchanged" % len(pre))'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
open(T + r"\verify_xlsx_v36.py", "w", encoding="utf-8", newline="\n").write(s)
print("verifier written")
