#!/usr/bin/env python3
"""Round 186: the tracker (Warpstorm Scroll's status, section 10.64), the review doc's row 18, the open-points doc and
CLAUDE.md."""
P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
REV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_rule_shut_review_2026-11-20.md"
OPN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_open_points.md"
CMD = r"C:\Users\vlady\Desktop\WH3_mod\CLAUDE.md"
KEY = "wh2_main_item_abilities_warpstorm_scroll"
SECTION = """
### 10.64 Round 186 - Warpstorm Scroll as a damage dealer (2026-11-20)

**Ruling (user, 2026-11-20):** "No need to enforce single-entity. No need to enforce charge, treat it just as a damage
dealer. The slow is not so relevant in this case." (the round-184 rule-10 question). Round document
`docs\\WH3_round186_warpstorm.md`.

**Change:** Warpstorm Scroll leaves `enemy_single_drain` for NEW `enemy_most_valuable`: the most valuable visible flying
enemy within 70 m, any number of models, no charge condition, no clearance. The trigger audit records the ruling (R4).

**Arithmetic:** 988 entries / 1,041 keys / 141 families. Harness 185 full suite **7,844 checks / 0 failures**, twice
byte-identical; RED 6/6. Pack md5 `8bf23234706e1647946a84cc0e33a969`; workbook v69.
"""


def sub(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


lines = open(P, encoding="utf-8").read().split("\n")
if "### 10.64 " not in "\n".join(lines):   # resumable: the tracker step ran once already
    hit = 0
    for i, l in enumerate(lines):
        if l.startswith("| ") and ("`%s`" % KEY) in l.split("|")[1]:
            cells = l.split("|")
            cells[2] = " `implemented (enemy_most_valuable, round 186)` "
            lines[i] = "|".join(cells)
            hit += 1
    assert hit == 1, hit
    s = "\n".join(lines)
    open(P, "w", encoding="utf-8", newline="\n").write(s.rstrip("\n") + "\n" + SECTION)
    print("tracker: Warpstorm Scroll, section 10.64")
else:
    assert "`implemented (enemy_most_valuable, round 186)`" in "\n".join(lines)
    print("tracker: already done")

rl = open(REV, encoding="utf-8").read().split("\n")
hit = 0
for i, l in enumerate(rl):
    if l.startswith("| 18 | ") and ("`%s`" % KEY) in l:
        rl[i] = l.replace("(**BUILT round 184: enemy_single_drain**)",
                          "(**BUILT round 184: enemy_single_drain; round 186: enemy_most_valuable, user 'treat it just as "
                          "a damage dealer'**)", 1)
        hit += 1
assert hit == 1, hit
open(REV, "w", encoding="utf-8", newline="\n").write("\n".join(rl))
print("review: row 18 marked")

o = open(OPN, encoding="utf-8").read()
o = sub(o, "| DONE (rounds 183-185: 51 built, 1 left as built with a question, 12 closed) |",
        "| DONE (rounds 183-186: 52 built, 12 closed; Warpstorm Scroll re-ruled in round 186) |")
open(OPN, "w", encoding="utf-8", newline="").write(o)
print("open points: item 3 updated")

c = open(CMD, encoding="utf-8").read()
for a, b in (
    ("- Installed build: md5 `0779eb3ef6eaf41e929b86d890270e4e`, 1,577,941 bytes\n"
     "  (round 185, 2026-11-20: the rule-shut review rows 20-64).",
     "- Installed build: md5 `8bf23234706e1647946a84cc0e33a969`, 1,579,341 bytes\n"
     "  (round 186, 2026-11-20: Warpstorm Scroll as a damage dealer)."),
    ("Current roster (round 185): 988 ABILITIES entries / 1,041 ability keys / 140 trigger evaluator families.",
     "Current roster (round 186): 988 ABILITIES entries / 1,041 ability keys / 141 trigger evaluator families."),
    ("Wheel audit (workbook v68):", "Wheel audit (workbook v69):"),
    ("../mod_source/releases/20261120_ruleshut3_harness184/build_and_install185.py",
     "../mod_source/releases/20261120_warpstorm_harness185/build_and_install186.py"),
    ("(harness184: 7,831 checks; it takes about 10 s)", "(harness185: 7,844 checks; it takes about 10 s)"),
    ("| `docs\\WH3_abilities_master_v68_2026-11-20.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v68.py`, verified by `tools\\verify_xlsx_v68.py`;",
     "| `docs\\WH3_abilities_master_v69_2026-11-20.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v69.py`, verified by `tools\\verify_xlsx_v69.py`;"),
    ("- ROUND 185 (2026-11-20, review rows 20-64;",
     "- ROUND 186 (2026-11-20): Warpstorm Scroll on NEW enemy_most_valuable (shot kind 'value', any model count, its\n"
     "  target_class flying; no charge arm). User: 'No need to enforce single-entity. No need to enforce charge, treat it\n"
     "  just as a damage dealer. The slow is not so relevant in this case.' Rule 10 does not bind it (audit R4 ruled). The\n"
     "  first install hit WinError 32 (the game was running); the user closed it.\n"
     "- ROUND 185 (2026-11-20, review rows 20-64;"),
):
    c = sub(c, a, b)
assert "\u2014" not in SECTION
open(CMD, "w", encoding="utf-8", newline="").write(c)
print("CLAUDE.md updated")
