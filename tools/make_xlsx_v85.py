#!/usr/bin/env python3
"""Build WH3_abilities_master_v85_2026-11-28.xlsx from v84 - round 219 (the placed blasts: most of the target unit,
standing cavalry as a target).

(1) Abilities: the 41 enemy_wander rows gain the COVER sentence in column 22. No family, no status changes.
(2) Cards: unchanged (checked against the harness-217 run).
(3) Numbers: the date line only.
(4) Definitions: title v85, section 82. Changelog: a v85 row. v1-v84 are never opened for writing."""
import collections
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v84_2026-11-22.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v85_2026-11-28.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_cover_harness217"
RUN = REL + r"\h217_run1.txt"
COVER_ADD = (" ROUND 219 (user rulings 2026-11-28 after a battle in which Brass Orb held on the only free target: 'A, most "
             "of the unit', standing cavalry as a target 'yes', the whole family 'yes'): the blob density line is no longer "
             "the only way in. A target also qualifies when the blast, placed on its centre, covers at least half of the "
             "target unit's own living soldiers and never fewer than 20 (the half and the 20 are Claude's numbers for the "
             "user's 'most of the unit' and 'a floor'. The count uses a 16 x 8 grid over the unit's own rectangle). "
             "Enemy CAVALRY (live unit class cav..., at least 10 riders, not flying) is a target too, with its depth from "
             "the game's own mounted spacing (GENERATED, 183 units). The trash rule, the standing-still rules and the "
             "friendly-fire distance are unchanged. NOT SEEN IN GAME.")


def read_cards():
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    return cards


def plan():
    wb = openpyxl.load_workbook(SRC, read_only=True)
    out = []
    for r, row in enumerate(wb["Abilities"].iter_rows(values_only=True, min_row=2), start=2):
        if row[20] == "enemy_wander":
            assert row[19] == "IMPLEMENTED", row[2]
            out.append((r, 22, row[21], (row[21] or "").rstrip() + COVER_ADD))
    wb.close()
    return out


def family_counts():
    entries, _, _ = bd.mod_entries()
    fc = collections.defaultdict(lambda: [0, 0])
    for e in entries:
        fc[e["trigger"]][0] += 1
        fc[e["trigger"]][1] += len(e["keys"])
    return entries, fc


def main():
    edits = plan()
    assert len(edits) == 41, len(edits)
    assert not os.path.exists(DST), DST
    entries, fc = family_counts()
    assert len(entries) == 982 and fc["enemy_wander"][0] == 41, fc["enemy_wander"]
    cards = read_cards()
    assert len(cards) == 982, len(cards)
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    for r, c, old, new in edits:
        assert ws.cell(row=r, column=c).value == old
        ws.cell(row=r, column=c).value = new
    cs = wb["Cards"]
    for r in range(2, cs.max_row + 1):
        m = cs.cell(row=r, column=1).value
        assert m is None or cs.cell(row=r, column=5).value == cards[m], m   # no card may have moved
    nm = wb["Numbers"]
    assert "v84 - ROUND 210" in str(nm.cell(row=7, column=1).value)
    nm.cell(row=7, column=1).value = (
        "Date: 2026-11-28     Rule in force since: 2026-10-18     Inventory: 1,802 active abilities     "
        "(v85 - ROUND 219: the 41 placed blasts take a target when the blast covers most of the unit, and standing cavalry "
        "too. 1,035 rows / 1,035 keys implemented, 80 not implemented among the included (all decided by the user), 0 "
        "open. The mod: 982 entries / 1,035 keys / 141 trigger families, all 141 in use.)")
    for r in range(44, 185):
        fam = nm.cell(row=r, column=2).value
        if fam is not None:
            assert [nm.cell(row=r, column=3).value, nm.cell(row=r, column=4).value] == fc[fam], fam
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v84")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v85 (2026-11-28)"
    base = d.max_row + 2
    sec = [("82. ROUND 219 - THE PLACED BLASTS: MOST OF THE UNIT, CAVALRY (v85)", None),
           ("FIELD", "The user's battle of 2026-11-28 (40 units): Brass Orb fired once per caster and then held. The only "
            "free target was a Free Company Militia unit of 110 men. The density line asks for 96 soldiers under a 12 m "
            "blast, and the 19-point sample of the blast gave far fewer for a 10 m deep line. Two Outrider units stood "
            "still and clear and were never candidates, because only infantry was."),
           ("RULE", "User: 'A, most of the unit', cavalry 'yes', the family 'yes'. The 41 enemy_wander entries take a "
            "target that passes the old density line OR whose own living soldiers are at least half covered by the blast "
            "(never fewer than 20). Enemy cavalry of at least 10 riders is a target. The cavalry spacing table is "
            "GENERATED (tools\\gen_blob_tables.py, cav_spacing_table)."),
           ("MACHINERY", "Not roster changes: rounds 213 to 218 cut the mod's own time per second (the HUD walk, the unit "
            "cards) and the development build now times every evaluator by trigger family.")]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-28"
    ch.cell(row=r, column=2).value = "v85"
    ch.cell(row=r, column=3).value = (
        "ROUND 219. The 41 enemy_wander rows: the COVER sentence (most of the target unit, standing cavalry as a target). "
        "No family, status or card change. SHIPPED: installed pack md5 %s. Harness 217 full suite %s checks / 0 failures."
        % (os.environ.get("WH3_PACK_MD5", "PENDING"), os.environ.get("WH3_CHECKS", "PENDING")))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-28. xlsx v85 supersedes v84. v1-v84 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "edits", len(edits))


if __name__ == "__main__":
    main()
