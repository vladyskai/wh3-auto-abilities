#!/usr/bin/env python3
"""Build WH3_abilities_master_v78_2026-11-22.xlsx from v77 - round 199 (user 2026-11-22, the overnight review's second
replies). Column 22 gains a sentence on the rows of the ten ally-arm entries (ARM / ONLY) and on the rows of the
bombardment family enemy_ground_melee_infantry (INF). Cards: the ten ally-arm cards. Numbers: the date line only (no
roster change). Definitions: title v78, section 75. Changelog: a v78 row. v1-v77 are never opened for writing."""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v77_2026-11-22.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v78_2026-11-22.xlsx"
ARM = (" ALLY ARM (round 199, user 2026-11-22: 'please implement, but also include the caster'): also cast on the most "
       "valuable ally in melee inside the game's range, when that ally is worth more than the caster or the caster's own "
       "trigger does not hold.")
ONLY = (" ALLY ONLY (round 199): cast on the most valuable ally in melee inside the game's range, never on the caster "
        "(the game's target_self is false and the ability has no ground form).")
INF = (" ROUND 199 (user 2026-11-22: 'agreed, please fix'): a unit of the generated large set, or one flying right now, "
       "is never infantry here, whatever the engine answers.")
CARD_TAIL = ", or on a more valuable ally in melee"
CARD_ONLY = "Fires on the most valuable ally in melee"


def groups():
    entries, _, _ = bd.mod_entries()
    arm, only, inf, markers = set(), set(), set(), {}
    src = open(bd.MOD if hasattr(bd, "MOD") else
               r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua",
               encoding="utf-8").read()
    for e in entries:
        ks = list(e["keys"])
        if e.get("trigger") == "enemy_ground_melee_infantry":
            inf.update(ks)
        i = src.index('{ marker = "%s",' % e["marker"])
        body = src[i:src.index("ox = 0, oy = 0 }", i)]
        if '\t\tally_value_arm = "only",' in body:
            only.update(ks)
            markers[e["marker"]] = "only"
        elif "\t\tally_value_arm = true," in body:
            arm.update(ks)
            markers[e["marker"]] = "arm"
    return arm, only, inf, markers


def plan():
    arm, only, inf, markers = groups()
    wb = openpyxl.load_workbook(SRC, read_only=True)
    out = []
    for r, row in enumerate(wb["Abilities"].iter_rows(values_only=True, min_row=2), start=2):
        k = str(row[2]).split(";")[0].strip()
        if row[19] != "IMPLEMENTED":
            continue
        add = ARM if k in arm else ONLY if k in only else INF if k in inf else None
        if add is not None:
            out.append((r, k, row[21], (row[21] or "").rstrip() + add))
    cards = []
    for r, row in enumerate(wb["Cards"].iter_rows(values_only=True, min_row=2), start=2):
        kind = markers.get(row[0])
        if kind == "only":
            cards.append((r, row[0], row[4], CARD_ONLY))
        elif kind == "arm":
            assert ";" not in row[4], row
            cards.append((r, row[0], row[4], row[4] + CARD_TAIL))
    wb.close()
    return out, cards, (len(arm), len(only), len(inf))


def main():
    rows, cards, counts = plan()
    assert counts[0] == 8 and counts[1] == 2 and len(cards) == 10, (counts, len(cards))
    assert len(rows) == sum(counts), (len(rows), counts)
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    for r, k, t, n in rows:
        assert ws.cell(row=r, column=22).value == t
        ws.cell(row=r, column=22).value = n
    cs = wb["Cards"]
    for r, m, t, n in cards:
        assert cs.cell(row=r, column=1).value == m and cs.cell(row=r, column=5).value == t
        cs.cell(row=r, column=5).value = n
    nm = wb["Numbers"]
    assert "v77 - ROUND 198" in str(nm.cell(row=7, column=1).value)
    nm.cell(row=7, column=1).value = (
        "Date: 2026-11-22     Rule in force since: 2026-10-18     Inventory: 1,802 active abilities     "
        "(v78 - ROUND 199: the ally arm, the infantry test, the remembered choice. 1,038 rows / 1,038 keys implemented, "
        "82 not implemented among the included (all decided by the user), 0 open. The mod: 985 entries / 1,038 keys / "
        "141 trigger families.)")
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v77")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v78 (2026-11-22)"
    base = d.max_row + 2
    d.cell(row=base, column=1).value = "75. ROUND 199 - THE ALLY ARM, THE INFANTRY TEST, THE REMEMBERED CHOICE (v78)"
    d.cell(row=base + 1, column=1).value = "RULE"
    d.cell(row=base + 1, column=2).value = (
        "User 2026-11-22 on the overnight review's rows 5, 9, 10 and 12. THE ALLY ARM: ten ally-targeted abilities that "
        "were cast on the caster only also go to the most valuable ally in melee inside the game's range. The more "
        "valuable of the caster (when its own trigger holds) and that ally wins, the caster on a tie. Wild Abandon and The "
        "Hand of Dust go to the ally only (the game gives them neither the caster nor the ground). THE INFANTRY TEST of the "
        "bombardments refuses a unit of the generated large set and a flying unit. THE REMEMBERED M/A CHOICE of a unit type "
        "sets the start of a battle only: a click changes the clicked unit and writes the type's choice for the next "
        "battle. A KEY WITH A CAPITAL LETTER (Doom & Darkness, gunnery school) can now get its badge.")
    d.cell(row=base + 2, column=1).value = "ROWS"
    d.cell(row=base + 2, column=2).value = ("%d trigger texts extended (%d ally arm, %d ally only, %d bombardments), "
                                            "%d cards restated." % (len(rows), counts[0], counts[1], counts[2], len(cards)))
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-22"
    ch.cell(row=r, column=2).value = "v78"
    ch.cell(row=r, column=3).value = (
        "ROUND 199. The ally arm, the infantry test, the remembered choice, the capital key. %d trigger texts and %d cards "
        "restated. SHIPPED: installed pack md5 %s. Harness 198 full suite %s checks / 0 failures."
        % (len(rows), len(cards), os.environ.get("WH3_PACK_MD5", "PENDING"), os.environ.get("WH3_CHECKS", "PENDING")))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-22. xlsx v78 supersedes v77. v1-v77 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "texts", len(rows), counts, "cards", len(cards))


if __name__ == "__main__":
    main()
