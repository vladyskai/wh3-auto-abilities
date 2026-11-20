#!/usr/bin/env python3
"""Build WH3_abilities_master_v65_2026-11-20.xlsx from v64 - round 182: the finishers (user rulings 2026-11-17 and
2026-11-20).

(1) Abilities: the Executioner and Skjalandir's Fall get their new family and text; the Emperor's Executioner x2 keep
    their family with the new text (earlier notes kept).
(2) Numbers: the trigger table re-counted; melee_or_shooting_into_melee is empty now (its row leaves); the 2 new
    families appended: 135 -> 136 rows; 936 entries / 989 keys.
(3) Cards: from the harness-181 run. (4) Definitions: title v65, section 62. Changelog: a v65 row.
v1-v64 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v64_2026-11-20.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v65_2026-11-20.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_finishers_harness181"
RUN = REL + r"\h181_run1.txt"
CARDS_TSV = REL + r"\cards_round182.tsv"
NEW_FAMILIES = ["enemy_finisher", "melee_or_self_shooting"]
GONE_FAMILY = "melee_or_shooting_into_melee"
R182 = " ROUND 182 (the finishers; user rulings 2026-11-17 and 2026-11-20)."
EXEC = ("enemy_execute: the enemy in range at or below the execute line (the game's execute_ratio) with the HIGHEST health "
        "% left, the most valuable on a tie (user, 2026-11-20: 'the highest health % first that is below the 20/33% "
        "threshold').")
T = {
    "wh2_dlc13_lord_abilities_executioner": (
        "enemy_finisher: the visible single-entity enemy with the LOWEST live health % (its damage rises from x1 at full "
        "health to x4 at 1%), the most valuable on a tie, none of ours within 10 m, the caster standing still; the bound "
        "is 90% of its real 250 m = 225 m (user ruling 2026-11-20, 'let's do 90%': the documented exception to 70%)."),
    "wh3_dlc24_lord_abilities_the_emperors_executioner": (EXEC[:-1] + " (its 20% line); target class: commander."),
    "wh3_dlc24_lord_abilities_the_emperors_executioner_upgrade": (EXEC + " Single entities (its 33% line)."),
    "wh3_dlc23_character_abilities_skjalandirs_fall": (
        "melee_or_self_shooting: in melee (not wavering) or shooting past its cast point, at any target. The game's phase "
        "gives +90 accuracy and imbues EVERY hit (melee and shots) with Blinded! (x0.5 speed, -25 melee attack, melee "
        "defence, missile block and accuracy, 26 s) (user: 'Do what you think is more adequate')."),
}
FAMILY = {k: v.split(":", 1)[0] for k, v in T.items()}
NOTE_HEADS = ("PATCH 9.0.5", "ROUND 165 (night audit)", "ROUND 166", "ROUND 167", "ROUND 168", "ROUND 169")


def old_notes(old):
    idx = [old.find(h) for h in NOTE_HEADS if old.find(h) != -1]
    return (" " + old[min(idx):]) if idx else ""


def text_of(k, old):
    return T[k] + R182 + old_notes(old)


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
    assert GONE_FAMILY not in fam_e
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    done = set()
    for r in range(2, ws.max_row + 1):
        k = str(ws.cell(row=r, column=3).value).split(";")[0].strip()
        if k in T:
            assert ws.cell(row=r, column=20).value == "IMPLEMENTED", k
            old = str(ws.cell(row=r, column=22).value or "")
            ws.cell(row=r, column=21).value = FAMILY[k]
            ws.cell(row=r, column=22).value = text_of(k, old)
            done.add(k)
    assert done == set(T), set(T) - done
    n = wb["Numbers"]
    assert n.cell(row=179, column=2).value == "TOTAL (135 families)"
    gone = [r for r in range(44, 179) if n.cell(row=r, column=2).value == GONE_FAMILY]
    assert len(gone) == 1, gone
    n.delete_rows(gone[0], 1)
    assert n.cell(row=178, column=2).value == "TOTAL (135 families)"
    n.insert_rows(178, amount=len(NEW_FAMILIES))
    for i, fam in enumerate(NEW_FAMILIES):
        n.cell(row=178 + i, column=2).value = fam
    for r in range(44, 180):
        n.cell(row=r, column=1).value = r - 43
        fam = n.cell(row=r, column=2).value
        n.cell(row=r, column=3).value = fam_e.get(fam, 0)
        n.cell(row=r, column=4).value = fam_k.get(fam, 0)
    assert n.cell(row=180, column=2).value == "TOTAL (135 families)"
    n.cell(row=180, column=2).value = "TOTAL (136 families)"
    n.cell(row=180, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 180))
    n.cell(row=180, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 180))
    assert (n.cell(row=180, column=3).value, n.cell(row=180, column=4).value) == (936, 989)
    assert all(n.cell(row=r, column=3).value > 0 for r in range(44, 180)), "an empty family is listed"
    assert n.cell(row=182, column=1).value == "Bombardment set (COMPLETE - round 108)"
    n.cell(row=42, column=1).value = (
        "Trigger families after round 182 - re-counted from the mod's own ABILITIES table: 136 families / 936 entries / "
        "989 keys. Round 182: the finishers (enemy_finisher, melee_or_self_shooting; melee_or_shooting_into_melee empty).")
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-20     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v65 - ROUND 182: the finishers. 989 rows / 989 keys implemented; 134 not implemented among the included (50 "
        "skipped by the user). The mod: 936 entries / 989 keys / 136 trigger families.)")
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 182)"
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v64")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v65 (2026-11-20)"
    base = d.max_row + 2
    sec = [("62. ROUND 182 - THE FINISHERS (v65)", None),
           ("NEW FAMILIES", "enemy_finisher (the Executioner: the lowest health %, 90% bound), melee_or_self_shooting "
            "(Skjalandir's Fall: in melee or shooting; every hit blinds)."),
           ("THE 90% EXCEPTION", "User ruling 2026-11-20: a single-entity target has no edge-to-edge problem, so the "
            "Executioner uses 90% of its real range (225 m). The only other exception to 70% is the air-drop test value."),
           ("THE EXECUTE", "The Emperor's Executioner ranks the HIGHEST health % at or below its line (user, 2026-11-20).")]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-20"
    ch.cell(row=r, column=2).value = "v65"
    ch.cell(row=r, column=3).value = (
        "ROUND 182. The finishers: the Executioner, the Emperor's Executioner x2, Skjalandir's Fall. SHIPPED: installed "
        "pack md5 %s; harness 181 full suite 7,688 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-17 / 2026-11-20; xlsx v65 supersedes v64; v1-v64 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
