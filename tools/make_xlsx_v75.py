#!/usr/bin/env python3
"""Build WH3_abilities_master_v75_2026-11-21.xlsx from v74 - round 193 (user 2026-11-21: Scry-Orb "implement").

(1) Abilities: row #1802 Scry-Orb -> IMPLEMENTED on when_ready, with its trigger text.
(2) Numbers: recomputed from the rows and the mod (make_xlsx_v74's method): 1,038 implemented, 82 not implemented
    (all decided by the user), the carrier table, the family table (985 entries / 1,038 keys).
(3) Cards: from the harness-192 run (985). (4) Definitions: title v75, section 72. Changelog: a v75 row.
v1-v74 are never opened for writing."""
import collections
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402
import make_xlsx_v74 as V74  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v74_2026-11-21.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v75_2026-11-21.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_preshot_harness192"
RUN = REL + r"\h192_run1.txt"
CARDS_TSV = REL + r"\cards_round193.tsv"
SCRY = V74.SCRY
TEXT = ("when_ready: fires whenever it is ready and the unit is not routing (the winds abilities' family): Winds of Magic "
        "regeneration x1.6 and ability recharges -30 s for 32 s, 3 uses (held 120 s between casts). User 2026-11-21: "
        "'implement' (round 193).")


def read_cards():
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    return cards


def main():
    assert not os.path.exists(DST), DST
    st = V74.source_types()
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    hit = []
    for r in range(2, ws.max_row + 1):
        if str(ws.cell(r, 3).value).split(";")[0].strip() == SCRY:
            assert ws.cell(r, 1).value == 1802 and ws.cell(r, 20).value == "NOT IMPLEMENTED"
            ws.cell(r, 20).value = "IMPLEMENTED"
            ws.cell(r, 21).value = "when_ready"
            ws.cell(r, 22).value = TEXT
            hit.append(r)
    assert len(hit) == 1
    rows = [list(x) for x in ws.iter_rows(values_only=True, min_row=2)]
    tot, exc, inc, impl, car, ex = V74.counts(rows, st)
    assert (tot, exc, inc, impl) == (1802, 682, 1120, 1038), (tot, exc, inc, impl)
    entries, _, _ = bd.mod_entries()
    assert len(entries) == 985 and sum(len(e["keys"]) for e in entries) == 1038
    impl_keys = {str(x[2]).split(";")[0].strip() for x in rows if x[19] == "IMPLEMENTED"}
    assert impl_keys == {k for e in entries for k in e["keys"]}

    nm = wb["Numbers"]
    assert "v74 - ROUND 192" in str(nm.cell(7, 1).value)
    nm.cell(7, 1).value = (
        "Date: 2026-11-21     Rule in force since: 2026-10-18     Inventory: 1,802 active abilities     "
        "(v75 - ROUND 193: Scry-Orb on when_ready. 1,038 rows / 1,038 keys implemented, 82 not implemented among the "
        "included (all decided by the user), 0 open. The mod: 985 entries / 1,038 keys / 141 trigger families.)")
    for row, val in ((13, impl), (14, inc - impl), (16, impl)):
        nm.cell(row, 3).value = val
        nm.cell(row, 4).value = val / tot
        nm.cell(row, 5).value = val / inc
    for r in range(20, 29):
        fam = str(nm.cell(r, 2).value).split("  ")[0]
        nm.cell(r, 3).value = car[fam][0]
        nm.cell(r, 4).value = car[fam][1]
        nm.cell(r, 5).value = car[fam][1] / car[fam][0]
    nm.cell(29, 3).value = inc
    nm.cell(29, 4).value = impl
    nm.cell(18, 1).value = nm.cell(18, 1).value.replace("1,037 implemented", "1,038 implemented")
    nm.cell(40, 1).value = (
        "Reconciliation (v75): included 1,120 + excluded 682 = 1,802 ROWS. Implemented among the included 1,038 + not "
        "implemented 82 (all decided by the user) = 1,120. The carrier table and row 16 are re-derived from the rows. "
        "Round 193: Scry-Orb implemented on when_ready.")
    fc = collections.defaultdict(lambda: [0, 0])
    for e in entries:
        fc[e["trigger"]][0] += 1
        fc[e["trigger"]][1] += len(e["keys"])
    for r in range(44, 185):
        fam = nm.cell(r, 2).value
        nm.cell(r, 3).value = fc[fam][0]
        nm.cell(r, 4).value = fc[fam][1]
    nm.cell(185, 3).value = len(entries)
    nm.cell(185, 4).value = sum(len(e["keys"]) for e in entries)
    nm.cell(42, 1).value = ("Trigger families after round 193 - re-counted from the mod's own ABILITIES table: 141 families / "
                            "985 entries / 1,038 keys. Round 193: Scry-Orb joined when_ready.")

    cards = read_cards()
    assert len(cards) == 985 and set(cards) == {e["marker"] for e in entries}, len(cards)
    with open(CARDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("marker\tability\tfamily\tkeys\tcard\n")
        for e in entries:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (e["marker"], e["name"], e["trigger"], ";".join(e["keys"]), cards[e["marker"]]))
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(1, 5).value = "Card: the M/A badge's hover text (round 193)"

    d = wb["Definitions"]
    assert d.cell(1, 1).value.startswith("DEFINITIONS - WH3 ability master v74")
    d.cell(1, 1).value = "DEFINITIONS - WH3 ability master v75 (2026-11-21)"
    base = d.max_row + 2
    d.cell(base, 1).value = "72. ROUND 193 - SCRY-ORB ON when_ready, THE PRE-SHOT PROBE (v75)"
    d.cell(base + 1, 1).value = "SCRY-ORB"
    d.cell(base + 1, 2).value = "User 2026-11-21: 'implement' (fire when ready, like the 21 pure winds abilities). #1802."
    d.cell(base + 2, 1).value = "PROBE"
    d.cell(base + 2, 2).value = ("A read-only battle-log probe (WOULD CAST / WOULD CAST ENDED / PRESHOT): would a shooting "
                                 "buff cast before the first shot? Nothing is cast. Decided after a test battle.")
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(r, 1).value = "2026-11-21"
    ch.cell(r, 2).value = "v75"
    ch.cell(r, 3).value = ("ROUND 193. Scry-Orb implemented (when_ready). Numbers recomputed. SHIPPED: installed pack md5 %s. "
                           "Harness 192 full suite 8,047 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(r, 4).value = "user ruling 2026-11-21. xlsx v75 supersedes v74. v1-v74 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "| implemented", impl, "| carrier passive", car["passive"])


if __name__ == "__main__":
    main()
