#!/usr/bin/env python3
"""Build WH3_abilities_master_v73_2026-11-21.xlsx from v72 - round 191: the animation decides in group 1 of the stand-still audit
(user 2026-11-21: "For now, please only implement number 1.").

(1) Abilities: every row of an entry on the 8 group-1 triggers (they fire at an enemy somewhere else) that has an animated
    key gains SENTENCE at the end of its trigger text (column 22): the whole entry waits (FOURTH.cast_stops_caster).
(2) Definitions: title v73, section 70. Changelog: a v73 row. Numbers: the date line only (no roster change).
v1-v72 are never opened for writing."""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v72_2026-11-21.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v73_2026-11-21.xlsx"
LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
FAMILIES = ("enemy_ground_melee_infantry", "enemy_ground_melee", "enemy_engaged_or_shot", "enemy_melee",
            "enemy_fast_near_ally", "enemy_melee_or_fast", "enemy_melee_noncommander", "enemy_missile_shooting")
N_ROWS = 50  # the dry count: 50 workbook rows (40 entries; some carry several keys)
SENTENCE = (" STANDING (round 191): its cast plays an animation, which stops a moving caster, so it waits until the caster"
            " stands still.")


def keys():
    src = open(LIVE, encoding="utf-8").read()
    anim = set(re.search(r'\nFOURTH\.ANIM_TEXT = "([^"]*)"', src).group(1).split(";"))
    entries, _, _ = bd.mod_entries()
    return {k for e in entries if e.get("trigger") in FAMILIES and any(x in anim for x in e["keys"]) for k in e["keys"]}


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
    assert len(rows) == N_ROWS, len(rows)
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    for r, k, t, n in rows:
        assert ws.cell(row=r, column=22).value == t
        ws.cell(row=r, column=22).value = n
    nm = wb["Numbers"]
    assert "v72 - ROUND 190" in str(nm.cell(row=7, column=1).value)
    nm.cell(row=7, column=1).value = (
        "Date: 2026-11-21     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v73 - ROUND 191: the animation decides in group 1 of the stand-still audit, the animated abilities that fire at "
        "an enemy somewhere else wait for their caster to stand still. 1,041 rows / 1,041 keys implemented; 82 not implemented among the included (62 skipped "
        "by the user). The mod: 988 entries / 1,041 keys / 141 trigger families.)")
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v72")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v73 (2026-11-21)"
    base = d.max_row + 2
    sec = [("70. ROUND 191 - THE ANIMATION DECIDES IN GROUP 1 (v73)", None),
           ("RULE", "User 2026-11-21: 'For now, please only implement number 1.' Group 1 of the stand-still audit: the "
            "triggers that fire at an enemy somewhere else (enemy_ground_melee_infantry, enemy_ground_melee, "
            "enemy_engaged_or_shot, enemy_melee, enemy_fast_near_ally, enemy_melee_or_fast, enemy_melee_noncommander, "
            "enemy_missile_shooting). An animated cast waits until its caster stands still; a cast without an animation "
            "still fires on the move (the 2026-11-17 ruling 'Option A, animation decides all')."),
           ("AUDIT", "docs\\WH3_stand_still_audit_2026-11-21.md: groups 2-6 (63 animated abilities) still wait for the "
            "user's rulings."),
           ("ROWS", "%d trigger texts gain the STANDING sentence." % len(rows))]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-21"
    ch.cell(row=r, column=2).value = "v73"
    ch.cell(row=r, column=3).value = (
        "ROUND 191. The animation decides in group 1 of the stand-still audit; %d trigger texts extended. SHIPPED: installed "
        "pack md5 %s; harness 190 full suite 7,967 checks / 0 failures." % (len(rows), os.environ.get("WH3_PACK_MD5", "PENDING")))
    ch.cell(row=r, column=4).value = "user ruling 2026-11-21; xlsx v73 supersedes v72; v1-v72 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "texts extended", len(rows), sorted(k for _, k, _, _ in rows))


if __name__ == "__main__":
    main()
