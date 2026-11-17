#!/usr/bin/env python3
"""Build WH3_abilities_master_v52_2026-11-17.xlsx from v51 - round 168: the cast animation decides the stand-still
rule; the older enemy pickers skip hidden enemies.

(1) Sheet "Cards": column E from the harness-167 run (the stand-still words now only on animated casts).
(2) Column 22 of the 63 entries' keys that may now fire while the caster moves gets a round-168 note.
(3) No count changes. Definitions: title v52, section 49. Changelog: a v52 row. v1-v51 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402
import gen_anim_keys as GA  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v51_2026-11-17.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v52_2026-11-17.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_anim_visibility_harness167"
RUN = REL + r"\h167_run1.txt"
CARDS_TSV = REL + r"\cards_round168.tsv"
LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
STAND = ("enemy_blob", "enemy_blob_vortex", "enemy_wave", "enemy_wave_charge", "enemy_wander", "enemy_strike", "enemy_cone",
         "enemy_single_drain", "enemy_area_drain", "enemy_single_shot", "enemy_infantry_shot")
NOTE = ("ROUND 168: may fire while its caster moves (no cast animation, so the cast does not stop it; user ruling "
        "2026-11-17, 'animation decides all').")


def moving_keys():
    """the keys of the stand-still-family entries with no animated key"""
    a = set(GA.derive(open(LIVE, encoding="utf-8").read()))
    entries, _, _ = bd.mod_entries()
    out, n = set(), 0
    for e in entries:
        if e["trigger"] in STAND and not any(k in a for k in e["keys"]):
            out.update(e["keys"])
            n += 1
    return out, n


def main():
    entries, _, _ = bd.mod_entries()
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    assert len(cards) == 946 and set(cards) == {e["marker"] for e in entries}, len(cards)
    with open(CARDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("marker\tability\tfamily\tkeys\tcard\n")
        for e in entries:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (e["marker"], e["name"], e["trigger"], ";".join(e["keys"]), cards[e["marker"]]))
    mk, n_entries = moving_keys()
    print("entries that may fire on the move:", n_entries, "keys:", len(mk))

    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    cs = wb["Cards"]
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 168)"
    n = 0
    for r in range(2, cs.max_row + 1):
        cs.cell(row=r, column=5).value = cards[cs.cell(row=r, column=1).value]
        n += 1
    assert n == 946, n
    ws = wb["Abilities"]
    done = set()
    for r in range(2, ws.max_row + 1):
        ks = [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
        if any(k in mk for k in ks):
            assert str(ws.cell(row=r, column=20).value) == "IMPLEMENTED", ks
            ws.cell(row=r, column=22).value = str(ws.cell(row=r, column=22).value) + " " + NOTE
            done.update(k for k in ks if k in mk)
    assert done == mk, mk - done

    nb = wb["Numbers"]
    nb.cell(row=7, column=1).value = (
        "Date: 2026-11-17     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v52 - ROUND 168: the cast animation decides the stand-still rule; the older enemy pickers skip hidden enemies. "
        "No roster change: 1,003 rows / 1,003 keys implemented; 120 not implemented among the included (36 skipped by "
        "the user). The mod: 946 entries / 1,003 keys / 95 trigger families.)")
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v51")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v52 (2026-11-17)"
    base = d.max_row + 2
    sec = [
        ("49. ROUND 168 - THE CAST ANIMATION, THE VISIBILITY (v52)", None),
        ("STAND STILL", "User ruling: 'Option A, animation decides all'. A cast stops its moving caster only when the "
         "ability plays a cast animation (unit_special_abilities.wind_up_stance; field 4 of 4). GENERATED "
         "FOURTH.ANIM_TEXT (tools/gen_anim_keys.py, 228 of 1,003 keys). The stand-still families wait for the caster only "
         "for an animated cast: %d entries may now fire on the move. The target-still rules are unchanged." % n_entries),
        ("VISIBILITY", "User: 'please implement the visibility'. Every enemy picker (eg_class_ok, and the non-commander "
         "picker of Eye of Khorne, The Dreaded Thirteenth and the infantry ground attacks) skips an enemy the game reads as "
         "NOT visible to our alliance. An unreadable read passes, as before."),
    ]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-17"
    ch.cell(row=r, column=2).value = "v52"
    ch.cell(row=r, column=3).value = (
        "ROUND 168. The cast animation decides the stand-still rule (%d entries may fire on the move); the older enemy "
        "pickers skip hidden enemies. No roster change. SHIPPED: installed pack md5 %s; harness 167 full suite 7,082 "
        "checks / 0 failures." % (n_entries, os.environ.get("WH3_PACK_MD5", "PENDING")))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-17; xlsx v52 supersedes v51; v1-v51 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "cards", n, "moving notes", len(done))


if __name__ == "__main__":
    main()
