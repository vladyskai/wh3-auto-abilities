#!/usr/bin/env python3
"""Build WH3_abilities_master_v62_2026-11-18.xlsx from v61 - round 179: the score-3 review, rows 115-134 (user,
2026-11-18: "Items 115-134 approved").

(1) Abilities: the 12 moved keys get their new family and text (earlier notes kept); Commanding Presence, Fury of Ulric
    and Grut's Sickle keep their family with the new text.
(2) Numbers: the trigger table re-counted; the 6 new families appended: 123 -> 129 rows (total row 167 -> 173, the
    blocks below move down 6 rows); 938 entries.
(3) Cards: from the harness-178 run. (4) Definitions: title v62, section 59. Changelog: a v62 row.
v1-v61 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v61_2026-11-18.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v62_2026-11-18.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows3_harness178"
RUN = REL + r"\h178_run1.txt"
CARDS_TSV = REL + r"\cards_round179.tsv"
NEW_FAMILIES = ["ally_charge_or_melee", "ally_melee_wavering_first", "ally_value_melee", "ally_in_melee",
                "health_aura_ally_deep", "heal_ground_best"]
R179 = " ROUND 179 (user approval 2026-11-18, score-3 review row %d)."
T = {
    "ally_charge_or_melee": "ally_charge_or_melee: the nearest ally within the 70% bound charging, else in fresh contact "
                            "(entered melee at most 2 s ago), else in melee; never a missile unit; the caster need not "
                            "fight.",
    "ally_melee_wavering_first": "ally_melee_wavering_first: the nearest ally in melee within the 70% bound, a wavering "
                                 "one first; the caster need not fight.",
    "ally_value_melee": "ally_value_melee: the most valuable ally (live value) in melee within the 70% bound; never a "
                        "missile unit.",
    "ally_in_melee": "ally_in_melee: the nearest ally in melee within the 70% bound (the reflection pays when it is "
                     "struck).",
    "melee_self_or_ally": "melee_self_or_ally: the caster in melee (cast on self), else the nearest ally in melee within "
                          "the 70% bound.",
    "health_aura_ally_deep": "health_aura_ally_deep: the lowest-health unit (the caster or an ally in range) at or below "
                             "55% (user: a 45% heal wastes less than at 75%).",
    "heal_ground_best": "heal_ground_best: the ground under the hurt unit of ours (75% or less, the caster included) "
                        "within 140 m (70% of 200) with the most other hurt units within 10 m of it (70% of its 15 m "
                        "area); the lower health on a tie.",
}
MOVED = {
    "wh3_main_lord_abilities_inspired_assault_i": ("ally_charge_or_melee", 115),
    "wh3_main_lord_abilities_inspired_assault_ii": ("ally_charge_or_melee", 116),
    "wh3_main_lord_abilities_inspired_assault_iii": ("ally_charge_or_melee", 117),
    "wh3_main_lord_abilities_inspired_defence_i": ("ally_melee_wavering_first", 118),
    "wh3_main_lord_abilities_inspired_defence_ii": ("ally_melee_wavering_first", 119),
    "wh3_main_lord_abilities_inspired_defence_iii": ("ally_melee_wavering_first", 120),
    "wh3_dlc26_character_abilities_da_boss_as_a_plan": ("ally_melee_wavering_first", 121),
    "wh_dlc07_lord_abilities_favour_of_the_fay": ("melee_self_or_ally", 122),
    "wh3_dlc26_character_abilities_orcs_are_da_best": ("ally_value_melee", 123),
    "wh3_dlc29_lord_abilities_hellish_vigour": ("ally_in_melee", 124),
    "wh2_dlc16_item_abilities_berry_wine": ("health_aura_ally_deep", 127),
    "wh2_dlc10_item_abilities_star_of_avelorn": ("heal_ground_best", 129),
}
SAME = {   # same family, new text
    "wh3_dlc29_lord_active_commanding_presence": ("wavering_self_or_ally", 130,
        "wavering_self_or_ally: the caster wavering, or an ally within 24 m (70% of the 35 m aura) wavering, in melee or "
        "not (user: 'Not related to melee, only to morale'); cast on self (the aura)."),
    "wh3_dlc29_spell_bound_prayer_fury_of_ulric": ("wavering_self_or_ally", 131,
        "wavering_self_or_ally: the caster wavering, or an ally within 24 m (70% of the 35 m aura) wavering, in melee or "
        "not; cast on self (the aura)."),
    "wh3_main_item_abilities_gruts_sickle": ("ally_winds", 133,
        "ally_winds: only when the winds pool is below 30 with reserve 20 or more; an EXPENDABLE ally within the 70% bound "
        "(the game's attribute, the GENERATED set) with the most hit points, else the ally with the LOWEST live value "
        "above 75% health (user: 'on expendable ally first (highest hp), then on the ally with lowest value above 75%')."),
}
NOTE_HEADS = ("PATCH 9.0.5", "ROUND 165 (night audit)", "ROUND 166", "ROUND 167", "ROUND 168", "ROUND 169")


def old_notes(old):
    idx = [old.find(h) for h in NOTE_HEADS if old.find(h) != -1]
    return (" " + old[min(idx):]) if idx else ""


def text_of(k, old):
    if k in SAME:
        fam, row, t = SAME[k]
        return t + (R179 % row) + old_notes(old)
    fam, row = MOVED[k]
    return T[fam] + (R179 % row) + " Starts armed (its old family did)." + old_notes(old)


def main():
    entries, _, _ = bd.mod_entries()
    assert len(entries) == 938
    keys_of = {}
    for e in entries:
        for k in e["keys"]:
            keys_of[k] = e["trigger"]
    for k, v in list(MOVED.items()) + list(SAME.items()):
        assert keys_of.get(k) == v[0], (k, v[0], keys_of.get(k))
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    assert len(cards) == 938 and set(cards) == {e["marker"] for e in entries}, len(cards)
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
    done = set()
    for r in range(2, ws.max_row + 1):
        k = str(ws.cell(row=r, column=3).value).split(";")[0].strip()
        if k in MOVED or k in SAME:
            assert ws.cell(row=r, column=20).value == "IMPLEMENTED", k
            old = str(ws.cell(row=r, column=22).value or "")
            ws.cell(row=r, column=21).value = (MOVED.get(k) or SAME.get(k))[0]
            ws.cell(row=r, column=22).value = text_of(k, old)
            done.add(k)
    assert done == set(MOVED) | set(SAME), (set(MOVED) | set(SAME)) - done
    n = wb["Numbers"]
    assert n.cell(row=167, column=2).value == "TOTAL (123 families)"
    n.insert_rows(167, amount=len(NEW_FAMILIES))
    for i, fam in enumerate(NEW_FAMILIES):
        n.cell(row=167 + i, column=2).value = fam
    for r in range(44, 173):
        n.cell(row=r, column=1).value = r - 43
        fam = n.cell(row=r, column=2).value
        n.cell(row=r, column=3).value = fam_e.get(fam, 0)
        n.cell(row=r, column=4).value = fam_k.get(fam, 0)
    assert n.cell(row=173, column=2).value == "TOTAL (123 families)"
    n.cell(row=173, column=2).value = "TOTAL (129 families)"
    n.cell(row=173, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 173))
    n.cell(row=173, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 173))
    assert (n.cell(row=173, column=3).value, n.cell(row=173, column=4).value) == (938, 992)
    assert all(n.cell(row=r, column=3).value > 0 for r in range(44, 173)), "an empty family is listed"
    assert n.cell(row=175, column=1).value == "Bombardment set (COMPLETE - round 108)"
    n.cell(row=42, column=1).value = (
        "Trigger families after round 179 - re-counted from the mod's own ABILITIES table: 129 families / 938 entries / "
        "992 keys. Round 179 (the score-3 review, rows 115-134): 6 NEW families; ally_melee_buff 11 -> 1.")
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-18     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v62 - ROUND 179: the score-3 review, rows 115-134. 992 rows / 992 keys implemented; 131 not implemented among the "
        "included (47 skipped by the user). The mod: 938 entries / 992 keys / 129 trigger families.)")
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 179)"
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v61")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v62 (2026-11-18)"
    base = d.max_row + 2
    sec = [("59. ROUND 179 - THE SCORE-3 REVIEW, ROWS 115-134 (v62)", None),
           ("NEW FAMILIES", "ally_charge_or_melee (Inspired Assault I-III), ally_melee_wavering_first (Inspired Defence "
            "I-III, Da Boss 'as a Plan!), ally_value_melee (Orcs are da Best!), ally_in_melee (Hellish Vigour), "
            "health_aura_ally_deep (Berry Wine, 55%), heal_ground_best (Star of Avelorn)."),
           ("SAME FAMILY, NEW RULE", "Commanding Presence and Fury of Ulric: no hidden 'ally in melee' condition. Grut's "
            "Sickle: low winds only; an expendable ally first, else the cheapest ally above 75%. Favour of the Fay joins "
            "melee_self_or_ally."),
           ("KEPT", "Rows 125, 126, 132, 134 (your rulings). Row 128 Cold-Blooded keeps its trigger; its Lizardmen-only "
            "restriction waits: the game data has no lizard attribute, so the set needs your look first.")]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-18"
    ch.cell(row=r, column=2).value = "v62"
    ch.cell(row=r, column=3).value = (
        "ROUND 179. The score-3 review, rows 115-134: 12 keys on their approved triggers, 6 new families, 3 rules changed. "
        "SHIPPED: installed pack md5 %s; harness 178 full suite 7,537 checks / 0 failures."
        % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user approval 2026-11-18; xlsx v62 supersedes v61; v1-v61 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
