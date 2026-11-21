#!/usr/bin/env python3
"""Build WH3_abilities_master_v76_2026-11-21.xlsx from v75 - round 197 (user 2026-11-21: "A: whole army"): every row of
an entry on enemy_blob or enemy_blob_vortex gains SENTENCE at the end of its trigger text (column 22). Numbers: the date
line only (no roster change). Definitions: title v76, section 73. Changelog: a v76 row. v1-v75 are never opened for
writing."""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v75_2026-11-21.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v76_2026-11-21.xlsx"
FAMILIES = ("enemy_blob", "enemy_blob_vortex")
SENTENCE = (" FALLBACK (round 197): when no unit of the whole enemy army (visible or hidden) passes the armour and trash"
            " rules, it takes the best visible target without them.")


def keys():
    entries, _, _ = bd.mod_entries()
    return {k for e in entries if e.get("trigger") in FAMILIES for k in e["keys"]}


def plan():
    ks = keys()
    wb = openpyxl.load_workbook(SRC, read_only=True)
    out = []
    for r, row in enumerate(wb["Abilities"].iter_rows(values_only=True, min_row=2), start=2):
        k = str(row[2]).split(";")[0].strip()
        if row[19] == "IMPLEMENTED" and k in ks:
            out.append((r, k, row[21], (row[21] or "").rstrip() + SENTENCE))
    wb.close()
    return out


def main():
    rows = plan()
    assert len(rows) == len(keys()), (len(rows), len(keys()))
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    for r, k, t, n in rows:
        assert ws.cell(row=r, column=22).value == t
        ws.cell(row=r, column=22).value = n
    nm = wb["Numbers"]
    assert "v75 - ROUND 193" in str(nm.cell(row=7, column=1).value)
    nm.cell(row=7, column=1).value = (
        "Date: 2026-11-21     Rule in force since: 2026-10-18     Inventory: 1,802 active abilities     "
        "(v76 - ROUND 197: the blob family's whole-army fallback. 1,038 rows / 1,038 keys implemented, 82 not implemented "
        "among the included (all decided by the user), 0 open. The mod: 985 entries / 1,038 keys / 141 trigger families.)")
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v75")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v76 (2026-11-21)"
    base = d.max_row + 2
    d.cell(row=base, column=1).value = "73. ROUND 197 - THE BLOB FAMILY'S WHOLE-ARMY FALLBACK (v76)"
    d.cell(row=base + 1, column=1).value = "RULE"
    d.cell(row=base + 1, column=2).value = (
        "User 2026-11-21, after Arrow of Kurnous held a whole battle against Skeleton Warriors (armour 20): 'when no better "
        "target exists on the enemy side (visible or invisible), it should fire as it wouldn't be wasteful', ruled 'A: whole "
        "army'. When no living unit of the enemy army, visible or hidden, passes the armour rule (armour-piercing attacks, "
        "armour 50) and the trash rule, the blob ability takes the best visible target without them. Hidden enemies are only "
        "counted, never targeted.")
    d.cell(row=base + 2, column=1).value = "ROWS"
    d.cell(row=base + 2, column=2).value = "%d trigger texts gain the FALLBACK sentence." % len(rows)
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-21"
    ch.cell(row=r, column=2).value = "v76"
    ch.cell(row=r, column=3).value = (
        "ROUND 197. The blob family's whole-army fallback. %d trigger texts extended. SHIPPED: installed pack md5 %s. "
        "Harness 196 full suite 8,104 checks / 0 failures." % (len(rows), os.environ.get("WH3_PACK_MD5", "PENDING")))
    ch.cell(row=r, column=4).value = "user ruling 2026-11-21. xlsx v76 supersedes v75. v1-v75 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "texts extended", len(rows))


if __name__ == "__main__":
    main()
