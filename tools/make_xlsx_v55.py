#!/usr/bin/env python3
"""Build WH3_abilities_master_v55_2026-11-18.xlsx from v54 - round 172: rows 1, 3 and 5 of the low score review as
RULED in the doc (round 171 built the first proposals).

(1) Abilities: Horn of the Wild Hunt and Ursun's Roar (the charge key) get their ruled trigger text; Waaagh! (the
    wh_main key) moves to the NEW army_charge_or_melee.
(2) Numbers: the trigger table re-counted from the mod (one new family appended, 101 -> 102 rows; the total row and the
    blocks below move down one row). Implemented 994 / not implemented 129 unchanged.
(3) Cards: from the harness-171 run. (4) Definitions: title v55, section 52. Changelog: a v55 row.
v1-v54 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v54_2026-11-17.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v55_2026-11-18.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_ruled_rows_harness171"
RUN = REL + r"\h171_run1.txt"
CARDS_TSV = REL + r"\cards_round172.tsv"
NEW_FAMILY = "army_charge_or_melee"
R172 = " ROUND 172 (the doc's ruling 2026-11-17, review row %d)."
MOVED = {
    "wh_dlc05_item_abilities_horn_of_the_wild_hunt": ("army_charge", 1,
        "army_charge: fires when 3 or more of our units are charging (Deadly Onslaught's charge window) or entered melee "
        "at most 2 s ago (fresh contact); in an army of fewer than 3 living units, when every living unit does. Its "
        "charge bonus x1.6 covers the whole army for 24 s."),
    "wh3_main_character_abilities_ursuns_roar": ("aura_charge", 3,
        "aura_charge (its own entry, ursuns_roar_charge): fires when ONE unit, the caster or any unit within its 24 m "
        "aura (70% of 35 m), is charging, in fresh contact or wavering. Charge bonus x1.36 and leadership +8 for 9 s."),
    "wh_main_character_abilities_waaagh": ("army_charge_or_melee", 5,
        "army_charge_or_melee (its own entry, waaagh_army): fires when 3 or more of our units charge or are in fresh "
        "contact, OR when 3 or more are in melee (the +20 melee attack pays in any fight); in an army of fewer than 3 "
        "living units, every living unit. Speed x1.25, charge bonus x1.2 and melee attack +20 for the whole army, 30 s."),
}


def main():
    entries, _, _ = bd.mod_entries()
    assert len(entries) == 939
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    assert len(cards) == 939 and set(cards) == {e["marker"] for e in entries}, len(cards)
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
    moved = set()
    for r in range(2, ws.max_row + 1):
        ks = [x.strip() for x in str(ws.cell(row=r, column=3).value).split(";") if x.strip()]
        k = ks[0]
        if k in MOVED and len(ks) == 1:
            fam, row, text = MOVED[k]
            assert ws.cell(row=r, column=20).value == "IMPLEMENTED"
            ws.cell(row=r, column=21).value = fam
            ws.cell(row=r, column=22).value = text + (R172 % row)
            moved.add(k)
    assert moved == set(MOVED), set(MOVED) - moved

    n = wb["Numbers"]
    names = [n.cell(row=r, column=2).value for r in range(44, 145)]
    assert len(names) == 101 and n.cell(row=145, column=2).value == "TOTAL (101 families)"
    for i, fam in enumerate(names):
        n.cell(row=44 + i, column=3).value = fam_e.get(fam, 0)
        n.cell(row=44 + i, column=4).value = fam_k.get(fam, 0)
    n.insert_rows(145, amount=1)
    n.cell(row=145, column=1).value = 102
    n.cell(row=145, column=2).value = NEW_FAMILY
    n.cell(row=145, column=3).value = fam_e[NEW_FAMILY]
    n.cell(row=145, column=4).value = fam_k[NEW_FAMILY]
    assert n.cell(row=146, column=2).value == "TOTAL (101 families)"
    n.cell(row=146, column=2).value = "TOTAL (102 families)"
    n.cell(row=146, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 146))
    n.cell(row=146, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 146))
    assert (n.cell(row=146, column=3).value, n.cell(row=146, column=4).value) == (939, 994)
    assert n.cell(row=148, column=1).value == "Bombardment set (COMPLETE - round 108)"
    n.cell(row=42, column=1).value = (
        "Trigger families after round 172 - re-counted from the mod's own ABILITIES table: 102 families / 939 entries / "
        "994 keys. Round 172 (the review rows 1, 3 and 5 as ruled): Waaagh! (the wh_main key) moves to the NEW "
        "army_charge_or_melee; army_charge keeps Horn of the Wild Hunt (1); aura_charge (Ursun's Roar) adds wavering.")
    assert n.cell(row=13, column=3).value == 994 and n.cell(row=14, column=3).value == 129
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-18     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v55 - ROUND 172: the review rows 1, 3 and 5 as ruled in the doc. 994 rows / 994 keys implemented; 129 not "
        "implemented among the included (45 skipped by the user). The mod: 939 entries / 994 keys / 102 trigger "
        "families.)")
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 172)"
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v54")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v55 (2026-11-18)"
    base = d.max_row + 2
    sec = [
        ("52. ROUND 172 - THE REVIEW ROWS 1, 3 AND 5 AS RULED (v55)", None),
        ("WHY", "Round 171 built the first proposals for these three rows; the review doc already carried the user's "
         "rulings (2026-11-17)."),
        ("THE ARMY COUNT", "N = 3 of our units, or every living unit when the army has fewer than 3. Routing units are "
         "living but never count as charging or fighting."),
        ("NEW FAMILY", "army_charge_or_melee (Waaagh!, the wh_main key): N units charging or in fresh contact, OR N units "
         "in melee."),
        ("aura_charge", "Ursun's Roar's charge key: ONE unit, the caster or any unit within the 24 m aura, charging, in "
         "fresh contact or wavering ('Agreed, and include the wavering')."),
    ]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-18"
    ch.cell(row=r, column=2).value = "v55"
    ch.cell(row=r, column=3).value = (
        "ROUND 172. The review rows 1, 3 and 5 as ruled in the doc: Horn of the Wild Hunt (every living unit in a "
        "smaller army), Waaagh! on the NEW army_charge_or_melee, Ursun's Roar (one unit charging or wavering). "
        "SHIPPED: installed pack md5 %s; harness 171 full suite 7,240 checks / 0 failures."
        % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "the doc's rulings 2026-11-17; xlsx v55 supersedes v54; v1-v54 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
