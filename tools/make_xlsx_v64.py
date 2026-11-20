#!/usr/bin/env python3
"""Build WH3_abilities_master_v64_2026-11-20.xlsx from v63 - round 181 (user, 2026-11-20: "Row 98, Land Mine: A / Fix
the range mismatches / 28 Surprise Squig! implement blob with clearance").

(1) Abilities: Land Mine and Surprise Squig! get their new family and text (earlier notes kept); the range-fixed rows
    (Curse of Khsar, Ravaging Swarm x2, Lord of Undeath x6) get a note.
(2) Numbers: the trigger table re-counted; the 2 new families appended: 133 -> 135 rows (total row 177 -> 179);
    936 entries / 989 keys.
(3) Cards: from the harness-180 run. (4) Definitions: title v64, section 61. Changelog: a v64 row.
v1-v63 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v63_2026-11-18.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v64_2026-11-20.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_landmine_squig_harness180"
RUN = REL + r"\h180_run1.txt"
CARDS_TSV = REL + r"\cards_round181.tsv"
NEW_FAMILIES = ["melee_clear_block", "enemy_summon_blob"]
R181 = " ROUND 181 (user ruling 2026-11-20, score-3 review row %d)."
T = {
    "wh3_dlc25_unit_abilities_marienburg_land_mines": (
        "melee_clear_block: in melee, not wavering, none of our other units within the 25 m blast + 10 m, AND at least 60 "
        "enemy soldiers inside the blast (user: 'Row 98, Land Mine: A'; each enemy unit counted at most at its own "
        "strength).", 98),
    "wh3_dlc25_character_abilities_surprise_squig": (
        "enemy_summon_blob: the standing enemy infantry block with the most live value inside the summoned squig's "
        "explosion (21 m: Squigs Go Boom, GENERATED from the game data), none of ours within 31 m (the blast + 10 m); the "
        "squig is placed on that block's ground (user: '28 Surprise Squig! implement blob with clearance').", 28),
}
FAMILY = {k: v[0].split(":", 1)[0] for k, v in T.items()}
NOTE = {
    "wh2_dlc09_character_abilities_curse_of_khsar": "range_real 35 -> 100 (it carried its AREA as its range; the game's target_intercept_range is 100 m, bound 70 m)",
    "wh3_dlc29_hero_active_dispatch_the_swarm_attack": "range_real 30 -> 100 (the game's target_intercept_range; bound 21 -> 70 m)",
    "wh3_dlc29_hero_active_dispatch_the_swarm_attack_upgraded": "range_real 30 -> 100 (the game's target_intercept_range; bound 21 -> 70 m)",
}
for _k in ("", "_0", "_1", "_2", "_3"):
    NOTE["wh_pro03_lord_abilities_lord_of_undeath" + _k] = ("range_real 200 -> 50 (its target_intercept_range; bound 140 -> 35 m); "
                                                           "the 200 m key (_4) has its own entry now")
NOTE["wh_pro03_lord_abilities_lord_of_undeath_4"] = "its own entry (lord_of_undeath_4), range_real 200 (bound 140 m)"
NOTE_HEADS = ("PATCH 9.0.5", "ROUND 165 (night audit)", "ROUND 166", "ROUND 167", "ROUND 168", "ROUND 169")


def old_notes(old):
    idx = [old.find(h) for h in NOTE_HEADS if old.find(h) != -1]
    return (" " + old[min(idx):]) if idx else ""


def text_of(k, old):
    t, row = T[k]
    return t + (R181 % row) + old_notes(old)


def note_text(k, old):
    return old + " ROUND 181 (user ruling 2026-11-20, 'Fix the range mismatches'): " + NOTE[k] + "."


def main():
    entries, _, _ = bd.mod_entries()
    assert len(entries) == 936
    keys_of = {}
    for e in entries:
        for k in e["keys"]:
            keys_of[k] = e["trigger"]
    for k, fam in FAMILY.items():
        assert keys_of.get(k) == fam, (k, fam, keys_of.get(k))
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    assert len(cards) == 936 and set(cards) == {e["marker"] for e in entries}, len(cards)
    with open(CARDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("marker\tability\tfamily\tkeys\tcard\n")
        for e in entries:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (e["marker"], e["name"], e["trigger"], ";".join(e["keys"]), cards[e["marker"]]))
    fam_e, fam_k = {}, {}
    for e in entries:
        fam_e[e["trigger"]] = fam_e.get(e["trigger"], 0) + 1
        fam_k[e["trigger"]] = fam_k.get(e["trigger"], 0) + len(e["keys"])
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    done, noted = set(), set()
    for r in range(2, ws.max_row + 1):
        k = str(ws.cell(row=r, column=3).value).split(";")[0].strip()
        old = str(ws.cell(row=r, column=22).value or "")
        if k in T:
            assert ws.cell(row=r, column=20).value == "IMPLEMENTED", k
            ws.cell(row=r, column=21).value = FAMILY[k]
            ws.cell(row=r, column=22).value = text_of(k, old)
            done.add(k)
        elif k in NOTE:
            ws.cell(row=r, column=22).value = note_text(k, old)
            noted.add(k)
    assert done == set(T) and noted == set(NOTE), (set(T) - done, set(NOTE) - noted)
    n = wb["Numbers"]
    assert n.cell(row=177, column=2).value == "TOTAL (133 families)"
    n.insert_rows(177, amount=len(NEW_FAMILIES))
    for i, fam in enumerate(NEW_FAMILIES):
        n.cell(row=177 + i, column=2).value = fam
    for r in range(44, 179):
        n.cell(row=r, column=1).value = r - 43
        fam = n.cell(row=r, column=2).value
        n.cell(row=r, column=3).value = fam_e.get(fam, 0)
        n.cell(row=r, column=4).value = fam_k.get(fam, 0)
    assert n.cell(row=179, column=2).value == "TOTAL (133 families)"
    n.cell(row=179, column=2).value = "TOTAL (135 families)"
    n.cell(row=179, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 179))
    n.cell(row=179, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 179))
    assert (n.cell(row=179, column=3).value, n.cell(row=179, column=4).value) == (936, 989)
    assert all(n.cell(row=r, column=3).value > 0 for r in range(44, 179)), "an empty family is listed"
    assert n.cell(row=181, column=1).value == "Bombardment set (COMPLETE - round 108)"
    n.cell(row=42, column=1).value = (
        "Trigger families after round 181 - re-counted from the mod's own ABILITIES table: 135 families / 936 entries / "
        "989 keys. Round 181: Land Mine (60 soldiers), Surprise Squig! (blob with clearance), the range fixes.")
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-20     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v64 - ROUND 181: Land Mine, Surprise Squig!, the range fixes. 989 rows / 989 keys implemented; 134 not "
        "implemented among the included (50 skipped by the user). The mod: 936 entries / 989 keys / 135 trigger families.)")
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 181)"
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v63")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v64 (2026-11-20)"
    base = d.max_row + 2
    sec = [("61. ROUND 181 - LAND MINE, SURPRISE SQUIG!, THE RANGE FIXES (v64)", None),
           ("NEW FAMILIES", "melee_clear_block (Land Mine: 60 enemy soldiers in the 25 m blast), enemy_summon_blob "
            "(Surprise Squig!: the standing block worth the most in the 21 m explosion, none of ours within 31 m)."),
           ("THE RANGE FIXES", "Curse of Khsar 35 -> 100; Ravaging Swarm x2 30 -> 100; Lord of Undeath split (five 50 m "
            "keys, one 200 m key). The scan (tools/scan_range_real.py, every key) is now a build gate: 0 mismatches."),
           ("NEW GENERATED TABLE", "SUMMON_BLAST (tools/gen_summon_blast.py): the spawned unit's exploding bombardment.")]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-20"
    ch.cell(row=r, column=2).value = "v64"
    ch.cell(row=r, column=3).value = (
        "ROUND 181. Land Mine on 60 soldiers in the blast, Surprise Squig! on a blob with clearance, 4 range fixes and the "
        "Lord of Undeath split. SHIPPED: installed pack md5 %s; harness 180 full suite 7,663 checks / 0 failures."
        % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user ruling 2026-11-20; xlsx v64 supersedes v63; v1-v63 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
