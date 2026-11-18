#!/usr/bin/env python3
"""Build WH3_abilities_master_v58_2026-11-18.xlsx from v57 - round 175: Master of Mists, 'A: before range, else
shooting' (user ruling 2026-11-18).

(1) Abilities: the two Master of Mists rows get the new trigger text (family unchanged: ground_ally_before_range).
(2) Numbers: unchanged counts (111 families / 937 / 992); the header lines name v58.
(3) Cards: from the harness-174 run. (4) Definitions: title v58, section 55. Changelog: a v58 row.
v1-v57 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v57_2026-11-18.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v58_2026-11-18.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_master_of_mists_harness174"
RUN = REL + r"\h174_run1.txt"
CARDS_TSV = REL + r"\cards_round175.tsv"
KEYS = ("wh3_dlc27_character_abilities_master_of_mists", "wh3_dlc27_character_abilities_master_of_mists_custom")
TEXT = ("ground_ally_before_range: first, the ground under the closest friendly missile unit (the caster included) within "
        "175 m that has no enemy inside its own missile range but one inside range x 1.35; else (ROUND 175) the ground "
        "under the friendly missile unit within 175 m that is shooting past its cast point with the most shooting units "
        "within 24 m (70% of the 35 m area), the closest on a tie. Missile damage x1.25, reload +20, range x1.5. ROUND "
        "175 (user ruling 2026-11-18: 'A: before range, else shooting'; 'But it also has plain damage boost!').")


def main():
    entries, _, _ = bd.mod_entries()
    assert len(entries) == 937
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    assert len(cards) == 937 and set(cards) == {e["marker"] for e in entries}, len(cards)
    with open(CARDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("marker\tability\tfamily\tkeys\tcard\n")
        for e in entries:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (e["marker"], e["name"], e["trigger"], ";".join(e["keys"]), cards[e["marker"]]))
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    done = set()
    for r in range(2, ws.max_row + 1):
        k = str(ws.cell(row=r, column=3).value).split(";")[0].strip()
        if k in KEYS:
            assert ws.cell(row=r, column=21).value == "ground_ally_before_range", k
            ws.cell(row=r, column=22).value = TEXT
            done.add(k)
    assert done == set(KEYS), done
    n = wb["Numbers"]
    assert n.cell(row=155, column=2).value == "TOTAL (111 families)"
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-18     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v58 - ROUND 175: Master of Mists fires before range, else under the shooting missile units. 992 rows / 992 "
        "keys implemented; 131 not implemented among the included (47 skipped by the user). The mod: 937 entries / 992 "
        "keys / 111 trigger families.)")
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 175)"
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v57")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v58 (2026-11-18)"
    base = d.max_row + 2
    d.cell(row=base, column=1).value = "55. ROUND 175 - MASTER OF MISTS: BEFORE RANGE, ELSE SHOOTING (v58)"
    d.cell(row=base + 1, column=1).value = "WHY"
    d.cell(row=base + 1, column=2).value = (
        "Master of Mists also raises missile damage x1.25 and reload +20 for its whole duration (user: 'But it also has "
        "plain damage boost!'). The before-range arm stays first; the shooting arm catches a late arming and the second "
        "use.")
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-18"
    ch.cell(row=r, column=2).value = "v58"
    ch.cell(row=r, column=3).value = (
        "ROUND 175. Master of Mists: before range, else under the shooting missile units. SHIPPED: installed pack md5 %s; "
        "harness 174 full suite 7,319 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user ruling 2026-11-18; xlsx v58 supersedes v57; v1-v57 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
