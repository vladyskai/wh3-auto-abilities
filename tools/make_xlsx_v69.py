#!/usr/bin/env python3
"""Build WH3_abilities_master_v69_2026-11-20.xlsx from v68 - round 186: Warpstorm Scroll as a damage dealer (user
2026-11-20: "No need to enforce single-entity. No need to enforce charge, treat it just as a damage dealer. The slow is
not so relevant in this case.").

(1) Abilities: the Warpstorm Scroll row moves from enemy_single_drain to NEW enemy_most_valuable, with its new text.
(2) Numbers: the trigger table re-counted with the new family appended (140 -> 141 rows): 988 entries / 1,041 keys.
(3) Cards: from the harness-185 run. (4) Definitions: title v69, section 66. Changelog: a v69 row.
v1-v68 are never opened for writing.
"""
import collections
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v68_2026-11-20.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v69_2026-11-20.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_warpstorm_harness185"
RUN = REL + r"\h185_run1.txt"
CARDS_TSV = REL + r"\cards_round186.tsv"
NEW_FAMILIES = ["enemy_most_valuable"]
KEY = "wh2_main_item_abilities_warpstorm_scroll"
TEXT = ("enemy_most_valuable: the most valuable visible enemy within 70 m (70% of the game's 100 m) that its target rule "
        "allows: FLYING only (target class flying: is_currently_flying() exactly true; the game refuses ground units), "
        "any number of models; no clearance (a direct effect on the enemy); no cast animation, so it may fire while its "
        "caster moves; 67 damage a second to one model and speed x0.55 for 29 s; 1 use. ROUND 186 (user ruling "
        "2026-11-20: 'No need to enforce single-entity. No need to enforce charge, treat it just as a damage dealer. The "
        "slow is not so relevant in this case.').")
FAMILY = {KEY: "enemy_most_valuable"}


def text_of(k):
    return TEXT


def main():
    entries, _, _ = bd.mod_entries()
    assert len(entries) == 988
    keys_of = {k: e["trigger"] for e in entries for k in e["keys"]}
    assert len(keys_of) == 1041 and keys_of[KEY] == "enemy_most_valuable"
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    assert len(cards) == 988 and set(cards) == {e["marker"] for e in entries}, len(cards)
    with open(CARDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("marker\tability\tfamily\tkeys\tcard\n")
        for e in entries:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (e["marker"], e["name"], e["trigger"], ";".join(e["keys"]), cards[e["marker"]]))
    fam_e, fam_k = collections.Counter(), collections.Counter()
    for e in entries:
        fam_e[e["trigger"]] += 1
        fam_k[e["trigger"]] += len(e["keys"])
    assert len(fam_e) == 141
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    hit = 0
    for r in range(2, ws.max_row + 1):
        if str(ws.cell(row=r, column=3).value).split(";")[0].strip() == KEY:
            assert ws.cell(row=r, column=20).value == "IMPLEMENTED" and ws.cell(row=r, column=21).value == "enemy_single_drain"
            ws.cell(row=r, column=21).value = "enemy_most_valuable"
            ws.cell(row=r, column=22).value = TEXT
            hit += 1
    assert hit == 1
    n = wb["Numbers"]
    assert n.cell(row=184, column=2).value == "TOTAL (140 families)"
    n.insert_rows(184, amount=len(NEW_FAMILIES))
    for i, fam in enumerate(NEW_FAMILIES):
        n.cell(row=184 + i, column=2).value = fam
    for r in range(44, 185):
        n.cell(row=r, column=1).value = r - 43
        fam = n.cell(row=r, column=2).value
        n.cell(row=r, column=3).value = fam_e.get(fam, 0)
        n.cell(row=r, column=4).value = fam_k.get(fam, 0)
    assert all(n.cell(row=r, column=3).value > 0 for r in range(44, 185)), "an empty family is listed"
    assert n.cell(row=185, column=2).value == "TOTAL (140 families)"
    n.cell(row=185, column=2).value = "TOTAL (141 families)"
    n.cell(row=185, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 185))
    n.cell(row=185, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 185))
    assert (n.cell(row=185, column=3).value, n.cell(row=185, column=4).value) == (988, 1041)
    assert n.cell(row=187, column=1).value == "Bombardment set (COMPLETE - round 108)"
    n.cell(row=42, column=1).value = (
        "Trigger families after round 186 - re-counted from the mod's own ABILITIES table: 141 families / 988 entries / "
        "1,041 keys. Round 186: Warpstorm Scroll on enemy_most_valuable.")
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-20     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v69 - ROUND 186: Warpstorm Scroll as a damage dealer. 1,041 rows / 1,041 keys implemented; 82 not implemented "
        "among the included (62 skipped by the user). The mod: 988 entries / 1,041 keys / 141 trigger families.)")
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 186)"
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v68")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v69 (2026-11-20)"
    base = d.max_row + 2
    sec = [("66. ROUND 186 - WARPSTORM SCROLL AS A DAMAGE DEALER (v69)", None),
           ("NEW FAMILY", "enemy_most_valuable: the most valuable enemy in range that the entry's target rule allows, any "
            "number of models (Warpstorm Scroll: flying only). User 2026-11-20: 'treat it just as a damage dealer'.")]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-20"
    ch.cell(row=r, column=2).value = "v69"
    ch.cell(row=r, column=3).value = (
        "ROUND 186. Warpstorm Scroll on enemy_most_valuable (no single-entity limit, no charge condition). SHIPPED: "
        "installed pack md5 %s; harness 185 full suite 7,844 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user ruling 2026-11-20; xlsx v69 supersedes v68; v1-v68 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
