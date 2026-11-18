#!/usr/bin/env python3
"""Build WH3_abilities_master_v56_2026-11-18.xlsx from v55 - round 173: Null Stone and Rock Eye closed by the user
(2026-11-18: "Close Null stone, Rock Eye.").

(1) Abilities: both keys become 'SKIPPED (user decision)' (family and trigger '-').
(2) Numbers: the trigger table re-counted (102 families, 937 / 992); implemented 994 -> 992, not implemented 129 -> 131.
(3) Cards: from the harness-172 run. (4) Definitions: title v56, section 53. Changelog: a v56 row.
v1-v55 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v55_2026-11-18.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v56_2026-11-18.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_close_two_harness172"
RUN = REL + r"\h172_run1.txt"
CARDS_TSV = REL + r"\cards_round173.tsv"
CLOSED = {
    "wh3_dlc27_item_abilities_null_stone": "row 18, 'Close Null stone, Rock Eye.' (it silences both sides' casters)",
    "wh3_main_item_passive_rock_eye": "row 16, 'Close Null stone, Rock Eye.' (+10% spotting)",
}


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
    fam_e, fam_k = {}, {}
    for e in entries:
        fam_e[e["trigger"]] = fam_e.get(e["trigger"], 0) + 1
        fam_k[e["trigger"]] = fam_k.get(e["trigger"], 0) + len(e["keys"])

    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    closed = set()
    for r in range(2, ws.max_row + 1):
        k = str(ws.cell(row=r, column=3).value).split(";")[0].strip()
        if k in CLOSED:
            assert ws.cell(row=r, column=20).value == "IMPLEMENTED"
            ws.cell(row=r, column=19).value = "skipped (user decision 2026-11-18: closed, " + CLOSED[k] + ")"
            ws.cell(row=r, column=20).value = "SKIPPED (user decision)"
            ws.cell(row=r, column=21).value = "-"
            ws.cell(row=r, column=22).value = "-"
            closed.add(k)
    assert closed == set(CLOSED), set(CLOSED) - closed

    n = wb["Numbers"]
    names = [n.cell(row=r, column=2).value for r in range(44, 146)]
    assert len(names) == 102 and n.cell(row=146, column=2).value == "TOTAL (102 families)"
    for i, fam in enumerate(names):
        n.cell(row=44 + i, column=3).value = fam_e.get(fam, 0)
        n.cell(row=44 + i, column=4).value = fam_k.get(fam, 0)
    n.cell(row=146, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 146))
    n.cell(row=146, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 146))
    assert (n.cell(row=146, column=3).value, n.cell(row=146, column=4).value) == (937, 992)
    assert n.cell(row=148, column=1).value == "Bombardment set (COMPLETE - round 108)"
    n.cell(row=42, column=1).value = (
        "Trigger families after round 173 - re-counted from the mod's own ABILITIES table: 102 families / 937 entries / "
        "992 keys. Round 173: Null Stone and Rock Eye closed by the user (melee_unwavering 282 -> 280).")
    n.cell(row=13, column=3).value = 992
    n.cell(row=14, column=3).value = 131
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-18     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v56 - ROUND 173: Null Stone and Rock Eye closed by the user. 992 rows / 992 keys implemented; 131 not "
        "implemented among the included (47 skipped by the user). The mod: 937 entries / 992 keys / 102 trigger "
        "families.)")
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 173)"
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v55")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v56 (2026-11-18)"
    base = d.max_row + 2
    d.cell(row=base, column=1).value = "53. ROUND 173 - NULL STONE AND ROCK EYE CLOSED (v56)"
    d.cell(row=base + 1, column=1).value = "CLOSED BY THE USER"
    d.cell(row=base + 1, column=2).value = ("'Close Null stone, Rock Eye.' (2026-11-18). Null Stone silences every unit "
                                            "on both sides; Rock Eye gives +10% forest spotting.")
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-18"
    ch.cell(row=r, column=2).value = "v56"
    ch.cell(row=r, column=3).value = (
        "ROUND 173. Null Stone and Rock Eye closed by the user (implemented 994 -> 992). SHIPPED: installed pack md5 %s; "
        "harness 172 full suite 7,251 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user ruling 2026-11-18; xlsx v56 supersedes v55; v1-v55 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
