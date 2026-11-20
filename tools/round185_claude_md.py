#!/usr/bin/env python3
"""Round 185: CLAUDE.md (installed build, builder path, harness size, roster, workbook, the open-rule count, open items)."""
P = r"C:\Users\vlady\Desktop\WH3_mod\CLAUDE.md"
s = open(P, encoding="utf-8").read()
R = [
    ("- Installed build: md5 `18aac090ab99114b1ac3c83eb483dd8c`, 1,562,718 bytes\n"
     "  (round 184, 2026-11-20: the rule-shut review rows 10-19).",
     "- Installed build: md5 `0779eb3ef6eaf41e929b86d890270e4e`, 1,577,941 bytes\n"
     "  (round 185, 2026-11-20: the rule-shut review rows 20-64)."),
    ("Current roster (round 184): 955 ABILITIES entries / 1,008 ability keys / 138 trigger evaluator families.",
     "Current roster (round 185): 988 ABILITIES entries / 1,041 ability keys / 140 trigger evaluator families."),
    ("Wheel audit (workbook v67): 1,123 in-wheel, 677 excluded, of 1,800 inventory rows; 1,008 implemented,\n"
     "115 not implemented among the included: 79 decided by the user, 36 OPEN",
     "Wheel audit (workbook v68): 1,123 in-wheel, 677 excluded, of 1,800 inventory rows; 1,041 implemented,\n"
     "82 not implemented among the included: 82 decided by the user, 0 OPEN (round 185 closed the rule-shut review;\n"
     "the text below about rule-shut rows is history)"),
    ("../mod_source/releases/20261120_ruleshut2_harness183/build_and_install184.py",
     "../mod_source/releases/20261120_ruleshut3_harness184/build_and_install185.py"),
    ("(harness183: 7,762 checks; it takes about 10 s)", "(harness184: 7,831 checks; it takes about 10 s)"),
    ("| `docs\\WH3_abilities_master_v67_2026-11-20.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v67.py`, verified by `tools\\verify_xlsx_v67.py`;",
     "| `docs\\WH3_abilities_master_v68_2026-11-20.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v68.py`, verified by `tools\\verify_xlsx_v68.py`;"),
    ("- ROUND 184 (2026-11-20, review rows 10-19;",
     "- ROUND 185 (2026-11-20, review rows 20-64; 'Review ended, implement pls'): 33 built (13 safe blasts melee_unwavering;\n"
     "  Glacial Blast, Thundermace melee_clear; Cellular Instability melee_clear_block; Splode da Big 'Un! and the Master Rune\n"
     "  of Immolation last_stand_clear; Battle Howl x2 + Silver Horn on NEW aura_charge_only; Twilight Horn II; Itzl;\n"
     "  Bonecrusher; Beastlord's Gaze; Fog of the Damned (enemy_ground_melee_cluster, ground); Locus of Contagion; Mad Cap\n"
     "  Mushrooms; Mirror of Knowledge (unbounded, ground); Offering to the Gods on NEW ally_offering, OFFERING_MIN_MEN 30;\n"
     "  Seismic Snare x2; Black Gem). 12 CLOSED (7 stealth, 5 mutual exclusivity = stances). gen_vortex_tables reads a\n"
     "  self-centred BOMBARDMENT (explosion radius + radius_spread). The progress page shows 0 open. MOCK GOTCHA: an ally's\n"
     "  dist field is both its gap to the caster AND to its own target (a charging ally must sit near 20 m). A blanket\n"
     "  count swap (1008 -> 1041) hit a unit id in C6: exclude ids when rebasing.\n"
     "- ROUND 184 (2026-11-20, review rows 10-19;"),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
assert "\u2014" not in "".join(b for _, b in R)
open(P, "w", encoding="utf-8", newline="").write(s)
print("CLAUDE.md updated")
