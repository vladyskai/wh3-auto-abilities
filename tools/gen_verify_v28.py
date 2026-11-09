#!/usr/bin/env python3
"""Write tools/verify_xlsx_v28.py from verify_xlsx_v27.py (round 136: the 23 retriggered enemy rows and the new
counts)."""
T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\verify_xlsx_v27.py", encoding="utf-8").read()
ADD = ('EXPECT.update({k: "enemy_melee" for k in ("wh3_main_weapon_abilities_torment_blade", '
       '"wh3_main_lord_abilities_virulent_contagion", "wh3_main_lord_abilities_virulent_contagion_upgraded", '
       '"wh2_main_lord_abilities_trophy_heads", "wh3_dlc29_hero_active_dispatch_the_swarm_attack")})\n'
       'EXPECT.update({k: "enemy_fast_near_ally" for k in ("wh3_main_lord_abilities_gaze_of_fate", '
       '"wh3_dlc23_lord_abilities_sadistic_snare", "wh2_dlc11_lord_abilities_spearfishers_net")})\n')
CHK = ('check("target class: not flying" in str(by_key["wh2_dlc11_lord_abilities_spearfishers_net"][21]), '
       '"B9: Spearfisher\'s Net lacks its not-flying class")\n'
       'check(sum(1 for r in rows if str(r[20]) == "enemy_engaged_or_shot") == 52, "B10: enemy_engaged_or_shot rows are not 52 (47 entries; some span two rows)")\n')
R = [
    ('== 17, "B6: the target-class rows are not 17")', '== 18, "B6: the target-class rows are not 18")'),
    (r'docs\WH3_abilities_master_v27_2026-11-09.xlsx"', r'docs\WH3_abilities_master_v28_2026-11-09.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v26_2026-11-09.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v27_2026-11-09.xlsx"'),
    (r"backups\round135\pre_v27_workbook_md5.txt", r"backups\round136\pre_v28_workbook_md5.txt"),
    ('PACK_MD5 = "79c8ffb8f6b0e052cc0feb337b87dde4"', 'PACK_MD5 = "104c049b22f675b1487f425eeb7fdb2e"'),
    ("KEEP_GATES = {", ADD + "KEEP_GATES = {"),
    ('"A1: %d rows in v27, %d in v26"', '"A1: %d rows in v28, %d in v27"'),
    ('check("bound: 24 m (70% of', CHK + 'check("bound: 24 m (70% of'),
    ('"enemy_engaged_or_shot": 70, "enemy_melee": 14, "enemy_fast_near_ally": 4}',
     '"enemy_engaged_or_shot": 47, "enemy_melee": 34, "enemy_fast_near_ally": 7}'),
    ('startswith("DEFINITIONS - WH3 ability master v27"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v28"), "G1: title")'),
    ('startswith("24. ROUND 135")', 'startswith("25. ROUND 136")'),
    ('"G2: section 24 missing"', '"G2: section 25 missing"'),
    ('== "v27" and PACK_MD5', '== "v28" and PACK_MD5'),
    ('"G3: changelog v27 row or pack md5 missing"', '"G3: changelog v28 row or pack md5 missing"'),
    ("check(len(pre) == 48 and not changed,", "check(len(pre) == 50 and not changed,"),
    ('print("XLSX v27 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v28 VERIFY: %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v27 VERIFY OK")', 'print("XLSX v28 VERIFY OK")'),
    ('15 enemy rows on their families")', '23 more enemy rows on their families")'),
    ('print("  v1-v26: %d files byte-unchanged" % len(pre))', 'print("  v1-v27: %d files byte-unchanged" % len(pre))'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
assert s.count("24 skipped; 17 target-class rows") == 1
s = s.replace("24 skipped; 17 target-class rows", "24 skipped; 18 target-class rows")
open(T + r"\verify_xlsx_v28.py", "w", encoding="utf-8", newline="\n").write(s)
print("verifier written")
