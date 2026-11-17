#!/usr/bin/env python3
"""Build WH3_abilities_master_v54_2026-11-17.xlsx from v53 - round 171: the score 1-2 review, rows 1-15 and 21.

(1) Abilities: the 10 moved keys get their new family and trigger text; the 9 closed keys become
    'SKIPPED (user decision)' with the user's reason (family and trigger '-', as every skipped row).
(2) Numbers: the trigger table re-counted from the mod (six new families appended, 95 -> 101 rows; the total row and
    the blocks below move down six rows); the headline: implemented 1,003 -> 994, not implemented 120 -> 129.
(3) Cards: from the harness-170 run. (4) Definitions: title v54, section 51. Changelog: a v54 row.
v1-v53 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v53_2026-11-17.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v54_2026-11-17.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_review_rows_harness170"
RUN = REL + r"\h170_run1.txt"
CARDS_TSV = REL + r"\cards_round171.tsv"
NEW_FAMILIES = ["army_charge", "aura_charge", "self_or_ally_charge", "slow_aura", "winds_low", "contact_melee"]
R171 = "ROUND 171 (user ruling 2026-11-17, the score 1-2 review row %d): "
MOVED = {
    "wh_dlc05_item_abilities_horn_of_the_wild_hunt": ("army_charge", 1,
        "army_charge: fires when 3 or more of our units are charging (Deadly Onslaught's charge window) or entered melee "
        "at most 2 s ago (fresh contact). Its charge bonus x1.6 covers the whole army for 24 s."),
    "wh3_main_character_abilities_ursuns_roar": ("aura_charge", 3,
        "aura_charge (its own entry, ursuns_roar_charge): fires when the caster charges or is in fresh contact, or when "
        "2 or more units within its 24 m aura (70% of 35 m) do. Charge bonus x1.36 and leadership +8 for 9 s."),
    "wh_main_character_abilities_red_fury": ("self_or_ally_charge", 4,
        "self_or_ally_charge: on the caster when it charges; else on the nearest ally within 70 m that is charging or in "
        "fresh contact; else on the caster when it is in melee. Charge bonus x1.2 and AP damage x1.25 for 31 s."),
    "wh_main_character_abilities_waaagh": ("army_charge", 5,
        "army_charge (its own entry, waaagh_army): fires when 3 or more of our units charge or are in fresh contact. "
        "Speed x1.25, charge bonus x1.2 and melee attack +20 for the whole army, 30 s."),
    "wh3_main_item_abilities_the_rock_of_inevitability": ("slow_aura", 6,
        "slow_aura: fires when the caster is in melee, or when a visible fast enemy (run speed 5 m/s or more, moving) is "
        "inside its 24 m aura (70% of 35 m). Enemy speed and charge speed x0.75, melee defence -26, 22 s."),
    "wh2_dlc13_weapon_abilities_wissenland_runefang": ("slow_aura", 7,
        "slow_aura: fires when the caster is in melee, or when a visible fast enemy is inside its 24 m aura. Enemy speed "
        "x0.55, 29 s."),
    "wh2_main_spell_bound_black_staff": ("winds_low", 8,
        "winds_low: fires when the army's winds pool is below 30 with 20 or more in reserve, and the caster is above 50% "
        "health (it deals 33 damage per second to its target for 20 s). Starts on M (self-damage, round 167)."),
    "wh_main_item_abilities_forbidden_rod": ("winds_low", 9,
        "winds_low: fires when the winds pool is below 30 with 20 or more in reserve, and the caster is above 50% health "
        "(33 damage per second to the caster for 23 s). Starts on M (self-damage, round 167)."),
    "wh_main_item_abilities_wand_of_jet": ("when_ready", 10,
        "when_ready: fires as soon as it is ready (not while routing). Up 57 s of every 117."),
    "wh3_dlc25_item_abilities_necrotic_phylactry": ("contact_melee", 21,
        "contact_melee: fires in melee, not wavering, when an enemy in contact (or its current target) carries a melee "
        "contact effect (GENERATED contact list, 503 land units: the melee weapon's contact phase or a passive that "
        "imbues one). Immunity to enemy contact effects and magic resistance +15, 18 s, one use."),
}
CLOSED = {
    "wh_main_item_abilities_earthing_rod": "row 11, rule 10: helps only before a friendly spell",
    "wh_dlc03_item_abilities_hagtree_fetish": "row 12, rule 10: helps only before a friendly spell",
    "wh_main_lord_abilities_master_of_the_black_arts": "row 13, rule 10: helps only before a friendly spell",
    "wh3_main_item_abilities_maw_shard": "row 14, rule 10: helps only before a friendly spell",
    "wh3_dlc27_item_abilities_power_familiar": "row 15, rule 10: helps only before a friendly spell",
    "wh3_dlc24_character_abilities_watched_by_the_watcher": "row 17: 'close (no actuation)'",
    "wh_main_item_abilities_sceptre_of_stability": "row 19: 'close, no read against enemy magic'",
    "wh3_main_character_abilities_locus_of_abjuration": "row 20: 'close, no read against enemy magic'",
    "wh2_dlc12_lord_abilities_focus_instincts": "row 22: 'if not possible to read a rampaged unit, then close' (no read)",
}


def main():
    entries, _, _ = bd.mod_entries()
    assert len(entries) == 939
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    assert len(cards) == 939 and set(cards) == {e["marker"] for e in entries}, len(cards)
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
    moved, closed = set(), set()
    SPLIT = {"wh_main_character_abilities_waaagh", "wh3_dlc26_unit_abilities_waaagh_in_combat",
             "wh3_main_character_abilities_ursuns_roar"}
    for r in range(2, ws.max_row + 1):
        ks = [x.strip() for x in str(ws.cell(row=r, column=3).value).split(";") if x.strip()]
        k = ks[0]
        # the split: a split key no longer shares an entry with its old twins (and they no longer list it)
        if len(ks) > 1 and (set(ks) & SPLIT):
            if k in SPLIT:
                keep = [k]
            else:
                keep = [x for x in ks if x not in SPLIT]
            ws.cell(row=r, column=3).value = "; ".join(keep)
        if k in MOVED:
            fam, row, text = MOVED[k]
            assert ws.cell(row=r, column=20).value == "IMPLEMENTED"
            ws.cell(row=r, column=21).value = fam
            ws.cell(row=r, column=22).value = text + " " + (R171 % row).rstrip(": ") + "."
            moved.add(k)
        elif k in CLOSED:
            assert ws.cell(row=r, column=20).value == "IMPLEMENTED"
            ws.cell(row=r, column=19).value = "skipped (user decision 2026-11-17: closed, " + CLOSED[k] + ")"
            ws.cell(row=r, column=20).value = "SKIPPED (user decision)"
            ws.cell(row=r, column=21).value = "-"
            ws.cell(row=r, column=22).value = "-"
            closed.add(k)
    assert moved == set(MOVED) and closed == set(CLOSED), (set(MOVED) - moved, set(CLOSED) - closed)

    n = wb["Numbers"]
    names = [n.cell(row=r, column=2).value for r in range(44, 139)]
    assert len(names) == 95 and n.cell(row=139, column=2).value == "TOTAL (95 families)"
    for i, fam in enumerate(names):
        n.cell(row=44 + i, column=3).value = fam_e.get(fam, 0)
        n.cell(row=44 + i, column=4).value = fam_k.get(fam, 0)
    n.insert_rows(139, amount=6)
    for i, fam in enumerate(NEW_FAMILIES):
        n.cell(row=139 + i, column=1).value = 96 + i
        n.cell(row=139 + i, column=2).value = fam
        n.cell(row=139 + i, column=3).value = fam_e[fam]
        n.cell(row=139 + i, column=4).value = fam_k[fam]
    assert n.cell(row=145, column=2).value == "TOTAL (95 families)"
    n.cell(row=145, column=2).value = "TOTAL (101 families)"
    n.cell(row=145, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 145))
    n.cell(row=145, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 145))
    assert (n.cell(row=145, column=3).value, n.cell(row=145, column=4).value) == (939, 994)
    assert n.cell(row=147, column=1).value == "Bombardment set (COMPLETE - round 108)"
    n.cell(row=42, column=1).value = (
        "Trigger families after round 171 - re-counted from the mod's own ABILITIES table: 101 families / 939 entries / "
        "994 keys. Round 171 (the score 1-2 review): the NEW army_charge (2), aura_charge (1), self_or_ally_charge (1), "
        "slow_aura (2), winds_low (2) and contact_melee (1); 9 abilities closed by the user; melee_unwavering 298 -> 282.")
    n.cell(row=13, column=3).value = 994
    n.cell(row=14, column=3).value = 129
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-17     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v54 - ROUND 171: the score 1-2 review, rows 1-15 and 21; 9 abilities closed by the user. 994 rows / 994 keys "
        "implemented; 129 not implemented among the included (45 skipped by the user). The mod: 939 entries / 994 keys / "
        "101 trigger families.)")
    cs = wb["Cards"]
    keep = [(cs.cell(row=r, column=1).value) for r in range(2, cs.max_row + 1)]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 171)"
    print("Cards: %d rows (was %d)" % (cs.max_row - 1, len(keep)))
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v53")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v54 (2026-11-17)"
    base = d.max_row + 2
    sec = [
        ("51. ROUND 171 - THE SCORE 1-2 REVIEW, ROWS 1-15 AND 21 (v54)", None),
        ("NEW FAMILIES", "army_charge (Horn of the Wild Hunt, Waaagh!), aura_charge (Ursun's Roar, the charge key), "
         "self_or_ally_charge (Red Fury), slow_aura (The Rock of Inevitability, The Wissenland Runefang), winds_low "
         "(Black Staff, Forbidden Rod), contact_melee (Necrotic Phylactery). Wand of Jet moves to when_ready. FRESH "
         "CONTACT: a unit that entered melee at most 2 s ago (the charge bonus still pays about 80%)."),
        ("CLOSED BY THE USER", "Earthing Rod, Hagtree Fetish, Master of the Black Arts, Maw Shard, Power Familiar (rule "
         "10), Watched by the Watcher, Sceptre of Stability, Locus of Abjuration (no read of enemy magic), Focus "
         "Instincts (no read of a rampaging unit)."),
        ("THE CONTACT LIST", "GENERATED by tools/gen_contact_keys.py: 503 land units whose melee weapon has a contact "
         "phase or whose passive ability imbues one."),
    ]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-17"
    ch.cell(row=r, column=2).value = "v54"
    ch.cell(row=r, column=3).value = (
        "ROUND 171. The score 1-2 review, rows 1-15 and 21: six new families, Ursun's Roar and Waaagh! split, 9 "
        "abilities closed (implemented 1,003 -> 994). SHIPPED: installed pack md5 %s; harness 170 full suite 7,199 "
        "checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-17; xlsx v54 supersedes v53; v1-v53 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
