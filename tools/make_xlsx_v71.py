#!/usr/bin/env python3
"""Build WH3_abilities_master_v71_2026-11-21.xlsx from v70 - round 189: the line of fire (user ruling 2026-11-21: "I
would just do the check for terrain on all 35 and units on all 35. Just let's be safe, and if it doesn't fire, that's
okay.").

(1) Abilities: every implemented row whose key the game marks 'Requires line of sight to the target'
    (tools/gen_los_keys.py) gains one sentence at the end of its trigger text (column 22): SENTENCE.
(2) Definitions: title v71, section 68 (the rule). Changelog: a v71 row. Numbers: the date line only (no roster change).
v1-v70 are never opened for writing."""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import gen_los_keys  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v70_2026-11-21.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v71_2026-11-21.xlsx"
SENTENCE = (" LINE OF FIRE (round 189): the game marks it 'Requires line of sight to the target', so it fires only at an"
            " enemy whose straight line from the caster is clear of every other unit (ours and the enemy's) and of the"
            " ground (bm:get_terrain_height); an unreadable read holds the cast.")


def plan():
    los = gen_los_keys.derive()
    wb = openpyxl.load_workbook(SRC, read_only=True)
    out = []
    for r, row in enumerate(wb["Abilities"].iter_rows(values_only=True, min_row=2), start=2):
        k = str(row[2]).split(";")[0].strip()
        if row[19] == "IMPLEMENTED" and k in los:
            t = row[21] or ""
            out.append((r, k, row[21], t.rstrip() + SENTENCE))
    wb.close()
    return out


def main():
    rows = plan()
    assert len(rows) == 35, len(rows)
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    for r, k, t, n in rows:
        assert ws.cell(row=r, column=22).value == t
        ws.cell(row=r, column=22).value = n
    nm = wb["Numbers"]
    assert str(nm.cell(row=7, column=1).value).startswith("Date: 2026-11-21")
    nm.cell(row=7, column=1).value = (
        "Date: 2026-11-21     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v71 - ROUND 189: the line of fire, the 35 abilities the game marks 'Requires line of sight to the target' "
        "fire only along a line clear of units and ground. 1,041 rows / 1,041 keys implemented; 82 not implemented "
        "among the included (62 skipped by the user). The mod: 988 entries / 1,041 keys / 141 trigger families.)")
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v70")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v71 (2026-11-21)"
    base = d.max_row + 2
    sec = [("68. ROUND 189 - THE LINE OF FIRE (v71)", None),
           ("RULE", "User 2026-11-21: 'I would just do the check for terrain on all 35 and units on all 35. Just let's "
            "be safe, and if it doesn't fire, that's okay. ... It's better for the mod if it doesn't fire.' The game "
            "marks 56 abilities 'Requires line of sight to the target' (ui effect "
            "wh3_main_projectile_requires_line_of_sight); 35 are ours. Such an ability fires only at an enemy whose "
            "straight line from the caster is clear of every other unit, ours and the enemy's (the unit's estimated "
            "rectangle, from its feet to its top: 2.5 m, 6 m for large units), and of the ground (bm:get_terrain_height "
            "sampled every 4 m; the line runs from 1.5 m above the caster to 1 m above the target). A blocked enemy is "
            "skipped; the next best one with a clear line is taken. Unreadable reads block (fail-closed)."),
           ("ASSUMPTIONS", "No API read exists for unit heights or for trees, buildings and walls; the ground read is "
            "assumed to be bare terrain and is checked against a standing unit's height (within 3 m) before it is "
            "trusted. The field test (Cackle Fruit, 2026-11-21) showed an arcing shot passing over our unit; the user "
            "chose the check for all 35 anyway."),
           ("ROWS", "%d trigger texts gain the LINE OF FIRE sentence." % len(rows))]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-21"
    ch.cell(row=r, column=2).value = "v71"
    ch.cell(row=r, column=3).value = (
        "ROUND 189. The line of fire: the 35 'Requires line of sight' abilities check units and terrain; %d trigger "
        "texts extended. SHIPPED: installed pack md5 %s; harness 188 full suite 7,921 checks / 0 failures."
        % (len(rows), os.environ.get("WH3_PACK_MD5", "PENDING")))
    ch.cell(row=r, column=4).value = "user ruling 2026-11-21; xlsx v71 supersedes v70; v1-v70 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "texts extended", len(rows))


if __name__ == "__main__":
    main()
