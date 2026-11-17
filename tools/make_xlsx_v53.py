#!/usr/bin/env python3
"""Build WH3_abilities_master_v53_2026-11-17.xlsx from v52 - round 170: Potion of Foolhardiness on charge_or_wavering.

(1) Abilities: the potion's row: family melee_unwavering -> charge_or_wavering, and the trigger text.
(2) Numbers: the trigger table: melee_unwavering 299 / 310 -> 298 / 309; charge_or_wavering 1 / 1 -> 2 / 2 (sums unchanged).
(3) Cards: from the harness-169 run (the potion's card changes).
(4) Definitions: title v53, section 50. Changelog: a v53 row. v1-v52 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v52_2026-11-17.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v53_2026-11-17.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_foolhardiness_harness169"
RUN = REL + r"\h169_run1.txt"
CARDS_TSV = REL + r"\cards_round170.tsv"
KEY = "wh_main_item_abilities_potion_of_foolhardiness"
TEXT = ("charge_or_wavering: not routing; fires in its own charge window (running at the enemy it attacks, 12 to 60 m away, "
        "at most 4 s from contact) or when it is wavering; cast on self. Starts armed (start_armed). ROUND 170 (user ruling "
        "2026-11-17, 'Charge or wavering', after a test where the armed potion fired only at contact): the charge bonus pays "
        "on its own charge, Unbreakable when it wavers.")


def main():
    entries, _, _ = bd.mod_entries()
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    assert len(cards) == 946, len(cards)
    assert cards["potion_of_foolhardiness"] == "Fires when charging or wavering"
    with open(CARDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("marker\tability\tfamily\tkeys\tcard\n")
        for e in entries:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (e["marker"], e["name"], e["trigger"], ";".join(e["keys"]), cards[e["marker"]]))

    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    hit = 0
    for r in range(2, ws.max_row + 1):
        if str(ws.cell(row=r, column=3).value).strip() == KEY:
            assert ws.cell(row=r, column=21).value == "melee_unwavering"
            ws.cell(row=r, column=21).value = "charge_or_wavering"
            ws.cell(row=r, column=22).value = TEXT
            hit += 1
    assert hit == 1, hit
    n = wb["Numbers"]
    moved = {}
    for r in range(44, 139):
        fam = n.cell(row=r, column=2).value
        if fam == "melee_unwavering":
            assert (n.cell(row=r, column=3).value, n.cell(row=r, column=4).value) == (299, 310)
            n.cell(row=r, column=3).value, n.cell(row=r, column=4).value = 298, 309
            moved[fam] = r
        elif fam == "charge_or_wavering":
            assert (n.cell(row=r, column=3).value, n.cell(row=r, column=4).value) == (1, 1)
            n.cell(row=r, column=3).value, n.cell(row=r, column=4).value = 2, 2
            moved[fam] = r
    assert len(moved) == 2, moved
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-17     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v53 - ROUND 170: Potion of Foolhardiness on charge_or_wavering. No roster count change: 1,003 rows / 1,003 keys "
        "implemented; 120 not implemented among the included (36 skipped by the user). The mod: 946 entries / 1,003 keys / "
        "95 trigger families.)")
    cs = wb["Cards"]
    for r in range(2, cs.max_row + 1):
        cs.cell(row=r, column=5).value = cards[cs.cell(row=r, column=1).value]
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 170)"
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v52")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v53 (2026-11-17)"
    base = d.max_row + 2
    d.cell(row=base, column=1).value = "50. ROUND 170 - POTION OF FOOLHARDINESS (v53)"
    d.cell(row=base + 1, column=1).value = "THE RULING"
    d.cell(row=base + 1, column=2).value = (
        "A test with two Empire Captains: the armed potion fired only at contact (it rode melee_unwavering). User ruling "
        "'Charge or wavering': charge bonus x1.4 on its own charge, Unbreakable when it wavers. It still starts armed "
        "(a new entry field, start_armed; charge_or_wavering itself does not start armed).")
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-17"
    ch.cell(row=r, column=2).value = "v53"
    ch.cell(row=r, column=3).value = (
        "ROUND 170. Potion of Foolhardiness on charge_or_wavering (melee_unwavering 299 -> 298, charge_or_wavering 1 -> 2). "
        "SHIPPED: installed pack md5 %s; harness 169 full suite 7,126 checks / 0 failures."
        % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user ruling 2026-11-17; xlsx v53 supersedes v52; v1-v52 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
