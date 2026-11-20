#!/usr/bin/env python3
"""Round 184: CLAUDE.md (installed build, builder path, harness size, roster, workbook, the open-rule count, open items)."""
P = r"C:\Users\vlady\Desktop\WH3_mod\CLAUDE.md"
s = open(P, encoding="utf-8").read()
R = [
    ("- Installed build: md5 `bde9bc18a104768c685084b70d274fa7`, 1,554,974 bytes\n"
     "  (round 183, 2026-11-20: the rule-shut review rows 1-9).",
     "- Installed build: md5 `18aac090ab99114b1ac3c83eb483dd8c`, 1,562,718 bytes\n"
     "  (round 184, 2026-11-20: the rule-shut review rows 10-19)."),
    ("Current roster (round 183): 945 ABILITIES entries / 998 ability keys / 136 trigger evaluator families.",
     "Current roster (round 184): 955 ABILITIES entries / 1,008 ability keys / 138 trigger evaluator families."),
    ("Wheel audit (workbook v66): 1,123 in-wheel, 677 excluded, of 1,800 inventory rows; 998 implemented,\n"
     "125 not implemented among the included: 79 decided by the user, 46 OPEN",
     "Wheel audit (workbook v67): 1,123 in-wheel, 677 excluded, of 1,800 inventory rows; 1,008 implemented,\n"
     "115 not implemented among the included: 79 decided by the user, 36 OPEN"),
    ("../mod_source/releases/20261120_ruleshut1_harness182/build_and_install183.py",
     "../mod_source/releases/20261120_ruleshut2_harness183/build_and_install184.py"),
    ("(harness182: 7,721 checks; it takes about 10 s)", "(harness183: 7,762 checks; it takes about 10 s)"),
    ("| `docs\\WH3_abilities_master_v66_2026-11-20.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v66.py`, verified by `tools\\verify_xlsx_v66.py`;",
     "| `docs\\WH3_abilities_master_v67_2026-11-20.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v67.py`, verified by `tools\\verify_xlsx_v67.py`;"),
    ("- ROUND 183 (2026-11-20, review rows 1-9;",
     "- ROUND 184 (2026-11-20, review rows 10-19; 'Up to #19 ruled'): Flock of Doom x3, Sword of Daith, Zefet-nebtar on\n"
     "  enemy_area_drain (it NEVER checked the enemy standing still: its gate is the caster's, for animated casts; a doc\n"
     "  thread reply had said otherwise); Ring of Corin, Warpstorm Scroll (target_class flying) on enemy_single_drain; Soul\n"
     "  Stealer x2 on NEW enemy_area_drain_hurt (DRAIN_HURT_PCT 75); Raging Tornado on NEW enemy_ground_melee_cluster\n"
     "  (cluster_pick over enemies in melee, eg_mode 'melee'). A GROUND-ONLY key (target_ground, no target_enemies) MUST join\n"
     "  enemy_ground_keys or the cast goes out in unit form (the harness caught it). New stand-still-family rows with no\n"
     "  cast animation need the round-168 NOTE in the workbook (make_xlsx_v52.moving_keys). OPEN: Warpstorm's x0.55 slow\n"
     "  rides no melee/charge arm (rule 10), recorded as ruled in audit R4 and put to the user.\n"
     "- ROUND 183 (2026-11-20, review rows 1-9;"),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
assert "\u2014" not in "".join(b for _, b in R)
open(P, "w", encoding="utf-8", newline="").write(s)
print("CLAUDE.md updated")
