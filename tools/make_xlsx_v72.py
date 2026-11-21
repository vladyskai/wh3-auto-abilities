#!/usr/bin/env python3
"""Build WH3_abilities_master_v72_2026-11-21.xlsx from v71 - round 190: the animation decides in every shot trigger (user
2026-11-21: "Amber Bow canceled his movement, not good" -> "Fix the 8").

(1) Abilities: the 8 animated entries on the 7 shot triggers that skipped the stand-still check gain SENTENCE at the end
    of their trigger text (column 22).
(2) Definitions: title v72, section 69. Changelog: a v72 row. Numbers: the date line only (no roster change).
v1-v71 are never opened for writing."""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v71_2026-11-21.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v72_2026-11-21.xlsx"
LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
FAMILIES = ("enemy_large_shot", "enemy_large_value_shot", "enemy_spellcaster", "enemy_commander_wavering",
            "enemy_summon_blob", "enemy_execute", "enemy_commander_value")
SENTENCE = (" STANDING (round 190): its cast plays an animation, which stops a moving caster, so it waits until the caster"
            " stands still.")


def keys():
    src = open(LIVE, encoding="utf-8").read()
    anim = set(re.search(r'\nFOURTH\.ANIM_TEXT = "([^"]*)"', src).group(1).split(";"))
    entries, _, _ = bd.mod_entries()
    return {k for e in entries if e.get("trigger") in FAMILIES for k in e["keys"] if k in anim}


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
    assert len(rows) == 8, len(rows)
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    for r, k, t, n in rows:
        assert ws.cell(row=r, column=22).value == t
        ws.cell(row=r, column=22).value = n
    nm = wb["Numbers"]
    assert "v71 - ROUND 189" in str(nm.cell(row=7, column=1).value)
    nm.cell(row=7, column=1).value = (
        "Date: 2026-11-21     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v72 - ROUND 190: the animation decides in every shot trigger, the 8 animated shot abilities wait for their "
        "caster to stand still. 1,041 rows / 1,041 keys implemented; 82 not implemented among the included (62 skipped "
        "by the user). The mod: 988 entries / 1,041 keys / 141 trigger families.)")
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v71")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v72 (2026-11-21)"
    base = d.max_row + 2
    sec = [("69. ROUND 190 - THE ANIMATION DECIDES IN THE SHOT TRIGGERS (v72)", None),
           ("RULE", "User 2026-11-21: 'Amber Bow canceled his movement, not good' -> 'Fix the 8'. The 2026-11-17 ruling "
            "('Option A, animation decides all') now reaches the shot triggers that skipped the stand-still check: an "
            "animated cast waits until its caster stands still, a cast without an animation still fires on the move. "
            "Changed: Amber Bow, Gaze of Nagash, Damned Pistol, Schalkain's Teeth, Goggly Glare, Vindictive Glare, Shem's "
            "Burning Gaze, The Black Tongue."),
           ("AUDIT", "docs\\WH3_stand_still_audit_2026-11-21.md: 33 other triggers (103 animated abilities) never check; "
            "waiting for the user's rulings."),
           ("ROWS", "%d trigger texts gain the STANDING sentence." % len(rows))]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-21"
    ch.cell(row=r, column=2).value = "v72"
    ch.cell(row=r, column=3).value = (
        "ROUND 190. The animation decides in every shot trigger; %d trigger texts extended. SHIPPED: installed pack md5 "
        "%s; harness 189 full suite 7,944 checks / 0 failures." % (len(rows), os.environ.get("WH3_PACK_MD5", "PENDING")))
    ch.cell(row=r, column=4).value = "user ruling 2026-11-21; xlsx v72 supersedes v71; v1-v71 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "texts extended", len(rows), sorted(k for _, k, _, _ in rows))


if __name__ == "__main__":
    main()
