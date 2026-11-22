#!/usr/bin/env python3
"""Build WH3_abilities_master_v80_2026-11-22.xlsx from v79 - round 203 (user rulings 2026-11-22: free aim, option A,
"All 30 placed"). Column 22 gains the FREE AIM sentence on the rows of the 30 enemy_wave keys. Numbers: the date line
only (no roster change). Definitions: title v80, section 77. Changelog: a v80 row. v1-v79 are never opened for
writing."""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v79_2026-11-22.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v80_2026-11-22.xlsx"
AIM = (" FREE AIM (round 203, user 2026-11-22: 'A: but be careful' and 'All 30 placed'): the game places this wave, so "
       "besides the line from the caster the mod tests 24 headings across each standing enemy in range. The path with the "
       "most enemy value that is clear of our units wins, its start must lie inside the cast bound, and the caster's own "
       "line keeps a tie. Another heading is ordered on the ground at the path's start with the heading as orientation.")


def keys():
    entries, _, _ = bd.mod_entries()
    return {k for e in entries if e["trigger"] == "enemy_wave" for k in e["keys"]}


def plan():
    ks = keys()
    wb = openpyxl.load_workbook(SRC, read_only=True)
    out = []
    for r, row in enumerate(wb["Abilities"].iter_rows(values_only=True, min_row=2), start=2):
        k = str(row[2]).split(";")[0].strip()
        if k in ks and row[19] == "IMPLEMENTED":
            out.append((r, k, row[21], (row[21] or "").rstrip() + AIM))
    wb.close()
    return out, ks


def main():
    rows, ks = plan()
    assert len(ks) == 30 and len(rows) == 30, (len(ks), len(rows))
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    for r, k, t, n in rows:
        assert ws.cell(row=r, column=22).value == t
        ws.cell(row=r, column=22).value = n
    nm = wb["Numbers"]
    assert "v79 - ROUND 201" in str(nm.cell(row=7, column=1).value)
    nm.cell(row=7, column=1).value = (
        "Date: 2026-11-22     Rule in force since: 2026-10-18     Inventory: 1,802 active abilities     "
        "(v80 - ROUND 203: free aim for the 30 placed straight waves. 1,035 rows / 1,035 keys implemented, 80 not "
        "implemented among the included (all decided by the user), 0 open. The mod: 982 entries / 1,035 keys / 141 trigger "
        "families.)")
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v79")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v80 (2026-11-22)"
    base = d.max_row + 2
    d.cell(row=base, column=1).value = "77. ROUND 203 - FREE AIM FOR THE STRAIGHT WAVES (v80)"
    d.cell(row=base + 1, column=1).value = "RULE"
    d.cell(row=base + 1, column=2).value = (
        "User 2026-11-22, after two battles in which the Fiery Ring of Thori never fired (one of our units stood beside "
        "every line from the caster through an enemy) and a console probe (round 202: a ground-form order starts the wave "
        "at the point and sends it along the orientation). Rulings: 'A: but be careful. Dragon breaths always come from a "
        "caster. Other abilities might also, check individually to be sure.' and 'All 30 placed'. The 30 enemy_wave keys "
        "are placed by the game (battle_vortexs.launch_source target_near_edge, checked key by key by the build). For each "
        "standing enemy in range the mod tests the caster's line and 24 compass headings. The 5 cones start at the caster "
        "(activator_front) and the 2 charge waves keep the caster's line. Real dragon breaths are projectiles on the blob "
        "family and are not touched.")
    d.cell(row=base + 2, column=1).value = "ROWS"
    d.cell(row=base + 2, column=2).value = "%d trigger texts extended with the FREE AIM sentence." % len(rows)
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-22"
    ch.cell(row=r, column=2).value = "v80"
    ch.cell(row=r, column=3).value = (
        "ROUND 203. Free aim for the 30 placed straight waves. %d trigger texts extended. SHIPPED: installed pack md5 %s. "
        "Harness 201 full suite %s checks / 0 failures."
        % (len(rows), os.environ.get("WH3_PACK_MD5", "PENDING"), os.environ.get("WH3_CHECKS", "PENDING")))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-22. xlsx v80 supersedes v79. v1-v79 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "texts", len(rows))


if __name__ == "__main__":
    main()
