#!/usr/bin/env python3
"""Round 181: CLAUDE.md (installed build, builder path, harness size, roster, workbook, open items)."""
P = r"C:\Users\vlady\Desktop\WH3_mod\CLAUDE.md"
s = open(P, encoding="utf-8").read()
R = [
    ("- Installed build: md5 `6fbdf834e0a2e7cee83d529d7a3c3700`, 1,543,625 bytes\n"
     "  (round 180, 2026-11-18: the score-3 review rows 87-114 and 128; 4 new families, 3 closed).",
     "- Installed build: md5 `3e567bc557f624b8298378fb8107d156`, 1,548,820 bytes\n"
     "  (round 181, 2026-11-20: Land Mine, Surprise Squig!, the range fixes)."),
    ("Current roster (round 180): 935 ABILITIES entries / 989 ability keys / 133 trigger evaluator families.",
     "Current roster (round 181): 936 ABILITIES entries / 989 ability keys / 135 trigger evaluator families."),
    ("Wheel audit (workbook v63):", "Wheel audit (workbook v64):"),
    ("../mod_source/releases/20261118_score3_rows4_harness179/build_and_install180.py",
     "../mod_source/releases/20261120_landmine_squig_harness180/build_and_install181.py"),
    ("(harness179: 7,622 checks; it takes about 10 s)", "(harness180: 7,663 checks; it takes about 10 s)"),
    ("| `docs\\WH3_abilities_master_v63_2026-11-18.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v63.py`, verified by `tools\\verify_xlsx_v63.py`;",
     "| `docs\\WH3_abilities_master_v64_2026-11-20.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v64.py`, verified by `tools\\verify_xlsx_v64.py`;"),
    ("## 9. OPEN ITEMS\n\n",
     "## 9. OPEN ITEMS\n\n"
     "- ROUND 181 (2026-11-20; 'Row 98, Land Mine: A / Fix the range mismatches / 28 Surprise Squig! implement blob with\n"
     "  clearance'): NEW melee_clear_block (Land Mine: melee_clear + FOURTH.LAND_MINE_MIN_MEN 60 soldiers in its 25 m\n"
     "  blast; FOURTH.blast_cover caps each unit at its strength), NEW enemy_summon_blob (Surprise Squig!: shot kind\n"
     "  'summon', the standing block worth the most in the 21 m explosion, none of ours within 31 m; GENERATED\n"
     "  FOURTH.SUMMON_BLAST_TEXT, tools\\gen_summon_blast.py: spawned_unit -> its abilities -> bombardment; no density line).\n"
     "  Range fixes: Curse of Khsar 100, Ravaging Swarm x2 100, Lord of Undeath split (lord_of_undeath_4 = the 200 m key).\n"
     "  tools\\scan_range_real.py checks EVERY key and is a build gate (0 mismatches). gen_vortex_tables.SELF_FAMILIES\n"
     "  gained melee_clear_block. Curse of Khsar's game rule: refused above 50% caster health. Next battle from byte\n"
     "  822,999,135. Still not built: the last review's row 23 + finishers.\n"),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
assert "\u2014" not in "".join(b for _, b in R)
open(P, "w", encoding="utf-8", newline="").write(s)
print("CLAUDE.md updated")
