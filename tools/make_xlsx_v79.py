#!/usr/bin/env python3
"""Build WH3_abilities_master_v79_2026-11-22.xlsx from v78 - round 201 (user rulings 2026-11-22, after the Dwarf battle
on the release build).

(1) Abilities:
    - the five Master Runes the game marks source_type = rune (Breaking, Negation, Slowness, Speed, Oath & Steel)
      -> EXCLUDED, REMOVED (spell bar) (user: "do it" on "remove the five Master Runes the game marks as runes");
    - Endless Whirlwind of Death and its Upgraded twin -> IMPLEMENTED on melee_unwavering (user: "do it" on "the same
      trigger as Whirlwind of Death").
(2) Numbers: every count recomputed from the v79 rows and the mod's ABILITIES table (make_xlsx_v74's method).
(3) Cards: rebuilt from the harness-199 run (982 cards).
(4) Definitions: title v79, section 76. Changelog: a v79 row. v1-v78 are never opened for writing."""
import collections
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402
import make_xlsx_v74 as V74  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v78_2026-11-22.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v79_2026-11-22.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_masterrunes_harness199"
RUN = REL + r"\h199_run1.txt"
CARDS_TSV = REL + r"\cards_round201.tsv"

RUNES = ["wh2_dlc17_rune_abilities_master_rune_of_breaking", "wh_dlc06_rune_abilities_master_rune_of_negation",
         "wh2_dlc17_rune_abilities_master_rune_of_slowness", "wh2_dlc17_rune_abilities_master_rune_of_speed",
         "wh_dlc06_rune_abilities_master_rune_of_oath_and_steel"]
RUNE_REASON = ("excluded family: spell bar - a rune the game shows on the right-hand spell bar, which the mod never claims "
               "(user ruling 2026-11-03). Closed by the user 2026-11-22: 'do it' on 'remove the five Master Runes the game "
               "marks as runes' (Master Rune of Slowness fired by itself from the right-hand bar in his Dwarf battle)")
RUNE_IMPL = "REMOVED (spell bar: on the right-hand bar, not the wheel)"
RUNE_TRIG = ("No automation - removed from the mod in round 201 (user decision 2026-11-22): the Master Rune sits on the "
             "right-hand spell bar.")
EW = ["wh3_dlc25_unit_abilities_whirlwind_of_death_ror", "wh3_dlc25_unit_abilities_whirlwind_of_death_ror_upgraded"]
EW_TRIG = ("melee_unwavering: not routing, in melee and not wavering, cast on self (a self-centred blast that cannot hurt "
           "our units: it launches the vortexes of Whirlwind of Death, which the game marks as not hitting allies). ROUND "
           "201 (user ruling 2026-11-22: 'do it' on 'the same trigger as Whirlwind of Death'). The questionnaire's earlier "
           "'rejected (friendly fire)' rested on a wrong reading of the vortex.")


def read_cards():
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    return cards


def plan(ws):
    out = []
    for r in range(2, ws.max_row + 1):
        k = str(ws.cell(r, 3).value).split(";")[0].strip()
        if k in RUNES:
            assert ws.cell(r, 18).value == "IN-WHEEL" and ws.cell(r, 20).value == "IMPLEMENTED", k
            for col, new in ((18, "EXCLUDED"), (19, RUNE_REASON), (20, RUNE_IMPL), (21, "-"), (22, RUNE_TRIG)):
                out.append((r, col, ws.cell(r, col).value, new))
        elif k in EW:
            assert ws.cell(r, 18).value == "IN-WHEEL" and ws.cell(r, 20).value == "NOT IMPLEMENTED", k
            for col, new in ((20, "IMPLEMENTED"), (21, "melee_unwavering"), (22, EW_TRIG)):
                out.append((r, col, ws.cell(r, col).value, new))
    return out


def main():
    assert not os.path.exists(DST), DST
    st = V74.source_types()
    wb0 = openpyxl.load_workbook(SRC, read_only=True)
    rows0 = [list(r) for r in wb0["Abilities"].iter_rows(values_only=True, min_row=2)]
    wb0.close()
    # the method must reproduce v78's own Numbers before it may write v79's
    n0 = V74.counts(rows0, st)
    assert n0[:4] == (1802, 682, 1120, 1038), n0[:4]
    assert n0[4]["rune"] == [7, 5] and n0[4]["active"] == [920, 849], dict(n0[4])
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    edits = plan(ws)
    assert len(edits) == 5 * 5 + 2 * 3, len(edits)
    for r, c, old, new in edits:
        assert ws.cell(r, c).value == old
        ws.cell(r, c).value = new
    rows = [list(x) for x in ws.iter_rows(values_only=True, min_row=2)]
    tot, exc, inc, impl, car, ex = V74.counts(rows, st)
    assert (tot, exc, inc, impl) == (1802, 687, 1115, 1035), (tot, exc, inc, impl)
    entries, _, _ = bd.mod_entries()
    n_keys = sum(len(e["keys"]) for e in entries)
    assert len(entries) == 982 and n_keys == 1035, (len(entries), n_keys)
    mod_keys = {k for e in entries for k in e["keys"]}
    impl_keys = {str(x[2]).split(";")[0].strip() for x in rows if x[19] == "IMPLEMENTED"}
    assert impl_keys == mod_keys, (sorted(impl_keys - mod_keys)[:5], sorted(mod_keys - impl_keys)[:5])

    nm = wb["Numbers"]
    assert "v78 - ROUND 199" in str(nm.cell(7, 1).value)
    nm.cell(7, 1).value = (
        "Date: 2026-11-22     Rule in force since: 2026-10-18     Inventory: 1,802 active abilities     "
        "(v79 - ROUND 201: the five Master Runes closed and removed (the right-hand bar), Endless Whirlwind of Death "
        "implemented (2 keys). 1,035 rows / 1,035 keys implemented, 80 not implemented among the included (all decided by "
        "the user), 0 open. The mod: 982 entries / 1,035 keys / 141 trigger families.)")
    nm.cell(9, 5).value = "% of included (1,115)"
    for row, val in ((10, tot), (11, exc), (12, inc), (13, impl), (14, inc - impl), (15, 0), (16, impl)):
        nm.cell(row, 3).value = val
        nm.cell(row, 4).value = val / tot
        if row >= 12:
            nm.cell(row, 5).value = val / inc
    assert nm.cell(18, 1).value.startswith("Included, by carrier family")
    nm.cell(18, 1).value = ("Included, by carrier family (unit_abilities.source_type) - ROW-LEVEL count, derived from this "
                            "workbook's own 1,115 IN-WHEEL rows joined to unit_abilities.source_type by exact key: it TIES to "
                            "the headline (sum = 1,115 included, 1,035 implemented). Round 201: the five Master Runes left "
                            "the 'rune' family.")
    order = ["active", "bound", "rune", "item", "lord", "character", "unit", "weapon", "passive"]
    assert set(car) == set(order), sorted(car)
    for i, fam in enumerate(order):
        r = 20 + i
        assert str(nm.cell(r, 2).value).split(" ")[0] == fam, (r, nm.cell(r, 2).value)
        nm.cell(r, 3).value = car[fam][0]
        nm.cell(r, 4).value = car[fam][1]
        nm.cell(r, 5).value = car[fam][1] / car[fam][0]
    nm.cell(29, 3).value = inc
    nm.cell(29, 4).value = impl
    nm.cell(30, 1).value = "The %d exclusions, by family - ROW count" % exc
    labels = {r: nm.cell(r, 2).value for r in range(32, 39)}
    sb = "Spell-bar runes (a rune on the right-hand spell bar; closed by the user 2026-11-21)"
    assert labels[38] == sb
    for r in range(32, 39):
        key = "ARMY" if str(labels[r]).startswith("Army-bar") else labels[r]
        nm.cell(r, 3).value = ex[key]
        nm.cell(r, 4).value = ex[key] / tot
        nm.cell(r, 5).value = ex[key] / exc
    nm.cell(38, 2).value = "Spell-bar runes (a rune on the right-hand spell bar; closed by the user 2026-11-21 and 2026-11-22)"
    nm.cell(39, 3).value = exc
    assert sum(ex.values()) == exc and ex[sb] == 10
    nm.cell(40, 1).value = (
        "Reconciliation (v79): included 1,115 + excluded 687 = 1,802 ROWS. Implemented among the included 1,035 + not "
        "implemented 80 (all decided by the user) = 1,115. The carrier table and row 16 are re-derived from the rows. Round "
        "201: the five Master Runes moved IN-WHEEL -> EXCLUDED, Endless Whirlwind of Death (2 rows) moved NOT IMPLEMENTED "
        "-> IMPLEMENTED.")
    fam_rows = {}
    for r in range(44, 185):
        fam_rows[nm.cell(r, 2).value] = r
    fc = collections.defaultdict(lambda: [0, 0])
    for e in entries:
        fc[e["trigger"]][0] += 1
        fc[e["trigger"]][1] += len(e["keys"])
    assert set(fc) == set(fam_rows), sorted(set(fc) ^ set(fam_rows))
    for fam, r in fam_rows.items():
        nm.cell(r, 3).value = fc[fam][0]
        nm.cell(r, 4).value = fc[fam][1]
    nm.cell(185, 3).value = len(entries)
    nm.cell(185, 4).value = n_keys
    nm.cell(42, 1).value = ("Trigger families after round 201 - re-counted from the mod's own ABILITIES table: 141 families / "
                            "982 entries / 1,035 keys. Round 201: the five Master Runes left melee_unwavering (3), "
                            "charge_or_melee and enemy_fast_near_ally; the two Endless Whirlwind of Death entries joined "
                            "melee_unwavering.")

    cards = read_cards()
    assert len(cards) == 982 and set(cards) == {e["marker"] for e in entries}, len(cards)
    with open(CARDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("marker\tability\tfamily\tkeys\tcard\n")
        for e in entries:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (e["marker"], e["name"], e["trigger"], ";".join(e["keys"]), cards[e["marker"]]))
    cs = wb["Cards"]
    old_cards = {r[0]: r[4] for r in cs.iter_rows(values_only=True, min_row=2) if r[0]}
    moved = sorted(m for m in cards if m in old_cards and old_cards[m] != cards[m])
    assert moved == [], moved   # no card of a kept entry may change in this round
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(1, 5).value = "Card: the M/A badge's hover text (round 201)"
    d = wb["Definitions"]
    assert d.cell(1, 1).value.startswith("DEFINITIONS - WH3 ability master v78")
    d.cell(1, 1).value = "DEFINITIONS - WH3 ability master v79 (2026-11-22)"
    base = d.max_row + 2
    sec = [("76. ROUND 201 - THE MASTER RUNES LEAVE, ENDLESS WHIRLWIND OF DEATH JOINS (v79)", None),
           ("RUNES", "User 2026-11-22, after a Dwarf battle on the release build: Master Rune of Slowness, a button on the "
            "right-hand bar, fired by itself (its entry rode a family that starts armed, and a cast needs no M/A letter). "
            "Ruling: 'do it' on 'remove the five Master Runes the game marks as runes'. Master Rune of Breaking, Negation, "
            "Slowness, Speed, Oath & Steel: EXCLUDED, removed from the mod. The build now refuses any key the game marks "
            "source_type = rune. Master Rune of Flight and of Immolation are source_type active and stay."),
           ("WHIRLWIND", "User 2026-11-22: 'do it' on 'the same trigger as Whirlwind of Death'. Endless Whirlwind of Death "
            "and its Upgraded twin fire in melee unless wavering. Both launch the vortexes of Whirlwind of Death, which the "
            "game marks as not hitting allies (the build checks it).")]
    for i, (a, b) in enumerate(sec):
        d.cell(base + i, 1).value = a
        if b is not None:
            d.cell(base + i, 2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(r, 1).value = "2026-11-22"
    ch.cell(r, 2).value = "v79"
    ch.cell(r, 3).value = (
        "ROUND 201. 5 Master Runes EXCLUDED (spell bar), Endless Whirlwind of Death x2 IMPLEMENTED (melee_unwavering). "
        "Numbers recomputed (1,802 rows), Cards rebuilt (982). SHIPPED: installed pack md5 %s. Harness 199 full suite %s "
        "checks / 0 failures." % (os.environ.get("WH3_PACK_MD5", "PENDING"), os.environ.get("WH3_CHECKS", "PENDING")))
    ch.cell(r, 4).value = "user rulings 2026-11-22. xlsx v79 supersedes v78. v1-v78 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "| edits", len(edits), "| rows", tot, "excluded", exc, "included", inc, "implemented", impl,
          "| carrier", dict(car), "| spell-bar", ex[sb])


if __name__ == "__main__":
    main()
