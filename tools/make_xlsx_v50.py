#!/usr/bin/env python3
"""Build WH3_abilities_master_v50_2026-11-17.xlsx from v49 - round 166: the short cards.

(1) Sheet "Cards": column E is the SHORT card of every entry (946), taken from the harness-165 run (CARD lines, every
    entry's FOURTH.compose_card result from the shipped source). The round-165 long cards are in v49.
(2) Column 22 of the wanderer keys whose safety check counted the caster (enemy_wander kinds 2 and 3 whose blast can hit
    our units) gets a round-166 note: the caster never blocks its own wanderer (user ruling 2026-11-17).
(3) No count changes: 1,003 implemented, 120 not implemented (36 skipped), 946 entries / 1,003 keys / 95 families.
    Definitions: title v50, section 47. Changelog: a v50 row. v1-v49 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v49_2026-11-17.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v50_2026-11-17.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_short_cards_harness165"
RUN = REL + r"\h165_run1.txt"
CARDS_TSV = REL + r"\cards_round166.tsv"
LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
NOTE = "ROUND 166: the caster never blocks its own wanderer (user ruling 2026-11-17, 'do not count the caster')."


def wander_keys():
    """the enemy_wander keys whose WW row is kind 2 or 3 and can hit our units (the loop round 166 changed)"""
    s = open(LIVE, encoding="utf-8").read()
    ww = s.split('FOURTH.WW_TEXT = "', 1)[1].split('"', 1)[0]
    rows = {}
    for item in ww.split(";"):
        if "=" in item:
            k, v = item.split("=", 1)
            rows[k] = v.split(",")
    entries, _, _ = bd.mod_entries()
    out = set()
    for e in entries:
        if e["trigger"] == "enemy_wander":
            for k in e["keys"]:
                r = rows.get(k)
                if r is not None and r[0] in ("2", "3") and r[5] == "1":
                    out.add(k)
    return out


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
    wk = wander_keys()
    print("wanderer keys noted:", len(wk))

    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    cs = wb["Cards"]
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 166, short)"
    n = 0
    for r in range(2, cs.max_row + 1):
        m = cs.cell(row=r, column=1).value
        cs.cell(row=r, column=5).value = cards[m]
        n += 1
    assert n == 946, n
    ws = wb["Abilities"]
    done = set()
    for r in range(2, ws.max_row + 1):
        ks = [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
        if any(k in wk for k in ks):
            assert str(ws.cell(row=r, column=20).value) == "IMPLEMENTED", ks
            ws.cell(row=r, column=22).value = str(ws.cell(row=r, column=22).value) + " " + NOTE
            done.update(k for k in ks if k in wk)
    assert done == wk, wk - done

    nb = wb["Numbers"]
    nb.cell(row=7, column=1).value = (
        "Date: 2026-11-17     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v50 - ROUND 166: the short cards. No roster change: 1,003 rows / 1,003 keys implemented; 120 not implemented "
        "among the included (36 skipped by the user). The mod: 946 entries / 1,003 keys / 95 trigger families. Sheet "
        "Cards: the short hover text of every M/A badge.)")
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v49")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v50 (2026-11-17)"
    base = d.max_row + 2
    sec = [
        ("47. ROUND 166 - THE SHORT CARDS (v50)", None),
        ("THE CARD", "User: 'too long and not thematic ... condense the meaning of the triggers in the least amount of "
         "words possible'. One short sentence per family, no distances (the 70% bounds stay in the code and the log), no "
         "name and no 'on A:'; the game's rules as short clauses. Sheet Cards lists all 946 (longest 115 characters)."),
        ("THE STATIC LINE", "The card's 'Automatic: click the M/A badge ...' line is gone: the mod no longer ships "
         "ui/common ui/special_ability_tooltip.twui.xml (it existed only for that line); the game's own layout applies."),
        ("THE ALL TOOLTIP", "Arm or disarm every automatic ability of the selected unit(s)."),
        ("THE WANDERERS", "The caster never blocks its own wanderer (user ruling 2026-11-17), as for the waves (round "
         "164). %d keys." % len(wk)),
        ("FRIENDLY FIRE", "User ruling: a vortex with affects_allies = false has no friendly-fire check. Already true "
         "(Heaven's Gate, Abyssal Swarm, Crackleblaze, Arcane Vassal); the build now refuses a fixed friendly-fire check on "
         "any blast the game says cannot hit our units (tools/ff_gate.py, 95 keys)."),
    ]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-17"
    ch.cell(row=r, column=2).value = "v50"
    ch.cell(row=r, column=3).value = (
        "ROUND 166. The short cards (sheet Cards), the static card line retired, the short ALL tooltip, the caster never "
        "blocks its wanderer, the friendly-fire gate. No roster change. SHIPPED: installed pack md5 %s; harness 165 full "
        "suite 7,025 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-17; xlsx v50 supersedes v49; v1-v49 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "cards", n, "wanderer notes", len(done))


if __name__ == "__main__":
    main()
