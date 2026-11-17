#!/usr/bin/env python3
"""Build WH3_abilities_master_v51_2026-11-17.xlsx from v50 - round 167: no final period, the safer defaults.

(1) Sheet "Cards": column E is the card of every entry (946) WITHOUT its final period, from the harness-166 run.
(2) Column 22 of the risky keys whose family starts armed gets a round-167 note: the entry starts on M (the game marks
    the ability rampage or self-damage).
(3) No count changes. Definitions: title v51, section 48. Changelog: a v51 row. v1-v50 are never opened for writing.
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402
import gen_risky_keys as GR  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v50_2026-11-17.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v51_2026-11-17.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_periods_risky_harness166"
RUN = REL + r"\h166_run1.txt"
CARDS_TSV = REL + r"\cards_round167.tsv"
LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
WHY = {"R": "rampage", "D": "self-damage", "RD": "rampage and self-damage"}


def note(flag):
    return "ROUND 167: starts on M even though its family starts armed (the game marks it %s; user ruling 2026-11-17)." % WHY[flag]


def risky_armed():
    """{key: flag} of the risky keys whose entry rides a family that starts armed"""
    s = open(LIVE, encoding="utf-8").read()
    rows = GR.derive(s)
    d = s.split("FOURTH.DEFAULT_ON_TRIGGERS = {", 1)[1].split("\n}", 1)[0]
    armed = set(re.findall(r"\n\t([a-z_0-9]+) = true", d))
    entries, _, _ = bd.mod_entries()
    out = {}
    for e in entries:
        if e["trigger"] in armed:
            for k in e["keys"]:
                if k in rows:
                    out[k] = rows[k]
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
    rk = risky_armed()
    print("risky keys in armed families:", len(rk))

    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    cs = wb["Cards"]
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 167, no final period)"
    n = 0
    for r in range(2, cs.max_row + 1):
        cs.cell(row=r, column=5).value = cards[cs.cell(row=r, column=1).value]
        n += 1
    assert n == 946, n
    ws = wb["Abilities"]
    done = set()
    for r in range(2, ws.max_row + 1):
        ks = [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
        hit = [k for k in ks if k in rk]
        if hit:
            assert str(ws.cell(row=r, column=20).value) == "IMPLEMENTED", ks
            ws.cell(row=r, column=22).value = str(ws.cell(row=r, column=22).value) + " " + note(rk[hit[0]])
            done.update(hit)
    assert done == set(rk), set(rk) - done

    nb = wb["Numbers"]
    nb.cell(row=7, column=1).value = (
        "Date: 2026-11-17     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v51 - ROUND 167: no final period; rampage and self-damage abilities start on M. No roster change: 1,003 rows / "
        "1,003 keys implemented; 120 not implemented among the included (36 skipped by the user). The mod: 946 entries / "
        "1,003 keys / 95 trigger families.)")
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v50")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v51 (2026-11-17)"
    base = d.max_row + 2
    sec = [
        ("48. ROUND 167 - NO FINAL PERIOD, THE SAFER DEFAULTS (v51)", None),
        ("NO FINAL PERIOD", "User: 'Do you need to put a point at the end of a sentence when there is no sentence after "
         "it? Please remove the point. Check the other tooltips also.' The mod sets two tooltips (the M/A badge card, the "
         "ALL button); neither ends with a period."),
        ("THE SAFER DEFAULTS", "User: 'Safer defaults for Rampage and self-damage abilities. They stay on M even in "
         "families that start armed.' GENERATED FOURTH.RISKY_TEXT (tools/gen_risky_keys.py): the game's 'rampage' phase "
         "attribute on the caster or its allies, and phases that damage the caster; 20 of the mod's keys, %d in families "
         "that start armed (15 entries). A badge click still arms them." % len(rk)),
    ]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-17"
    ch.cell(row=r, column=2).value = "v51"
    ch.cell(row=r, column=3).value = (
        "ROUND 167. No final period on the cards and the ALL text; rampage and self-damage abilities start on M. No roster "
        "change. SHIPPED: installed pack md5 %s; harness 166 full suite 7,048 checks / 0 failures."
        % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-17; xlsx v51 supersedes v50; v1-v50 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "cards", n, "risky notes", len(done))


if __name__ == "__main__":
    main()
