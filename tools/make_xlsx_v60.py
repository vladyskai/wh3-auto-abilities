#!/usr/bin/env python3
"""Build WH3_abilities_master_v60_2026-11-18.xlsx from v59 - round 177: the score-3 review, rows 1-22 (user,
2026-11-18: "Implement all until item 22, except the number 3 that should stay the same").

(1) Abilities: the 15 moved keys get their new family and trigger text (earlier notes kept).
(2) Numbers: the trigger table re-counted; the 9 new families appended: 111 -> 120 rows (total row 155 -> 164, the
    blocks below move down 9 rows). Implemented 992 / not implemented 131 unchanged.
(3) Cards: from the harness-176 run. (4) Definitions: title v60, section 57. Changelog: a v60 row.
v1-v59 are never opened for writing.
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v59_2026-11-18.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v60_2026-11-18.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows_harness176"
RUN = REL + r"\h176_run1.txt"
CARDS_TSV = REL + r"\cards_round177.tsv"
NEW_FAMILIES = ["slow_army", "melee_vs_large", "ally_squig_melee", "enemy_melee_near", "aura_charge_or_melee",
                "melee_health25", "guard_aura", "self_or_ally_fire_melee", "melee_healthy"]
R177 = " ROUND 177 (user approval 2026-11-18, score-3 review row %d)."
T = {
    "slow_army": "slow_army: fires when a visible fast enemy (run speed 5 m/s or more, moving) is within 40 m of any unit "
                 "of ours, or the caster is in melee. Rule 10: an enemy speed cut pays on their charge.",
    "melee_vs_large": "melee_vs_large: fires when the caster, or a unit of ours within 24 m (70% of 35 m), is in melee "
                      "with a LARGE enemy (the engagement set x the GENERATED large set).",
    "ally_squig_melee": "ally_squig_melee: cast on the nearest SQUIG ally within 70 m that is in melee (the game's "
                        "unit_is_not_squig rule; GENERATED squig set, 10 land units).",
    "enemy_melee_near": "enemy_melee_near: fires when the caster is in melee, or a visible enemy within 24 m (70% of 35 m) "
                        "is in melee.",
    "aura_charge_or_melee": "aura_charge_or_melee: fires when the caster, or a unit of ours within 38 m (70% of 55 m), is "
                            "charging, just made contact, or in melee.",
    "melee_health25": "melee_health25: fires in melee at or below 25% health (Cannot Die near death).",
    "melee_or_under_fire": "melee_or_under_fire: fires when the caster is in melee (not wavering) or under missile fire "
                           "(armour also stops arrows).",
    "guard_aura": "guard_aura: fires when the caster is in melee or under missile fire, or a visible fast enemy is moving "
                  "inside its aura (70%; an enemy charge).",
    "self_or_ally_fire_melee": "self_or_ally_fire_melee: the caster in melee or under fire -> on itself; else the most "
                               "valuable ally within 70 m under missile fire; else the nearest ally in melee.",
    "self_last_stand": "self_last_stand: at or below 10% health, in melee or under missile fire (the Hag's Denial rule "
                       "for a one-use Cannot Die).",
    "melee_healthy": "melee_healthy: fires in melee, not wavering, above 50% health (it costs 60 health every 2 s). Starts "
                     "on M (self-damage, round 167).",
}
MOVED = {
    "wh3_dlc29_unit_abilities_blood_omens": ("slow_army", 1),
    "wh2_dlc16_weapon_abilities_creature_killer": ("melee_vs_large", 2),
    "wh3_dlc26_character_abilities_empowering_shrooms": ("ally_squig_melee", 4),
    "wh3_main_lord_abilities_everyone_has_their_price": ("enemy_melee_near", 5),
    "wh3_dlc24_character_abilities_fury_of_the_land": ("aura_charge_or_melee", 6),
    "wh2_dlc12_unit_abilities_refuse_to_die": ("melee_health25", 11),
    "wh_main_rune_abilities_rune_of_oath_and_steel": ("melee_or_under_fire", 12),
    "wh2_dlc13_item_abilities_shield_of_aeons": ("guard_aura", 14),
    "wh3_dlc29_hero_active_dispatch_the_swarm_protect": ("self_or_ally_fire_melee", 15),
    "wh3_dlc29_hero_active_dispatch_the_swarm_protect_upgraded": ("self_or_ally_fire_melee", 16),
    "wh3_dlc23_item_abilities_slayer_for_chaos": ("self_last_stand", 17),
    "wh3_main_item_abilities_steppe_hunters_horn": ("melee_vs_large", 18),
    "wh3_dlc20_item_abilities_the_armour_of_morkar": ("guard_aura", 19),
    "wh2_dlc14_lord_abilities_the_blood_price": ("melee_healthy", 20),
    "wh2_dlc13_weapon_abilities_ostermark_runefang": ("melee_vs_large", 21),
}
NOTE_HEADS = ("PATCH 9.0.5", "ROUND 165 (night audit)", "ROUND 166", "ROUND 167", "ROUND 168", "ROUND 169")


def old_notes(old):
    idx = [old.find(h) for h in NOTE_HEADS if old.find(h) != -1]
    return (" " + old[min(idx):]) if idx else ""


def text_of(k, old):
    fam, row = MOVED[k]
    t = T[fam] + (R177 % row) + old_notes(old)
    # the round-167 note said the family starts armed; melee_healthy does not (The Blood Price still starts on M)
    if fam == "melee_healthy":
        t = re.sub(r" ROUND 167: starts on M even though its family starts armed \([^)]*\)\.", "", t)
    return t


def main():
    entries, _, _ = bd.mod_entries()
    assert len(entries) == 937
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    assert len(cards) == 937 and set(cards) == {e["marker"] for e in entries}, len(cards)
    with open(CARDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("marker\tability\tfamily\tkeys\tcard\n")
        for e in entries:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (e["marker"], e["name"], e["trigger"], ";".join(e["keys"]), cards[e["marker"]]))
    fam_e, fam_k = {}, {}
    for e in entries:
        fam_e[e["trigger"]] = fam_e.get(e["trigger"], 0) + 1
        fam_k[e["trigger"]] = fam_k.get(e["trigger"], 0) + len(e["keys"])
    for k, (fam, _) in MOVED.items():
        assert any(k in e["keys"] and e["trigger"] == fam for e in entries), (k, fam)
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    moved = set()
    for r in range(2, ws.max_row + 1):
        k = str(ws.cell(row=r, column=3).value).split(";")[0].strip()
        if k in MOVED:
            assert ws.cell(row=r, column=20).value == "IMPLEMENTED", k
            old = str(ws.cell(row=r, column=22).value or "")
            ws.cell(row=r, column=21).value = MOVED[k][0]
            ws.cell(row=r, column=22).value = text_of(k, old)
            moved.add(k)
    assert moved == set(MOVED), set(MOVED) - moved
    n = wb["Numbers"]
    assert n.cell(row=155, column=2).value == "TOTAL (111 families)"
    n.insert_rows(155, amount=len(NEW_FAMILIES))
    for i, fam in enumerate(NEW_FAMILIES):
        n.cell(row=155 + i, column=2).value = fam
    for r in range(44, 164):
        n.cell(row=r, column=1).value = r - 43
        fam = n.cell(row=r, column=2).value
        n.cell(row=r, column=3).value = fam_e.get(fam, 0)
        n.cell(row=r, column=4).value = fam_k.get(fam, 0)
    assert n.cell(row=164, column=2).value == "TOTAL (111 families)"
    n.cell(row=164, column=2).value = "TOTAL (120 families)"
    n.cell(row=164, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 164))
    n.cell(row=164, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 164))
    assert (n.cell(row=164, column=3).value, n.cell(row=164, column=4).value) == (937, 992)
    assert all(n.cell(row=r, column=3).value > 0 for r in range(44, 164)), "an empty family is listed"
    assert n.cell(row=166, column=1).value == "Bombardment set (COMPLETE - round 108)"
    n.cell(row=42, column=1).value = (
        "Trigger families after round 177 - re-counted from the mod's own ABILITIES table: 120 families / 937 entries / "
        "992 keys. Round 177 (the score-3 review, rows 1-22): 9 NEW families; melee_unwavering 280 -> 265.")
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-18     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v60 - ROUND 177: the score-3 review, rows 1-22. 992 rows / 992 keys implemented; 131 not implemented among the "
        "included (47 skipped by the user). The mod: 937 entries / 992 keys / 120 trigger families.)")
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 177)"
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v59")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v60 (2026-11-18)"
    base = d.max_row + 2
    sec = [("57. ROUND 177 - THE SCORE-3 REVIEW, ROWS 1-22 (v60)", None),
           ("NEW FAMILIES", ", ".join(NEW_FAMILIES) + "."),
           ("SQUIG SET", "GENERATED by tools/gen_squig_keys.py: the land units whose attribute group carries the game's "
            "'squig' attribute (10)."),
           ("UNCHANGED", "Daemonshield (the user's word), Terrorgheist Skull and Seductive Glory (ruled), Primal Roar, "
            "Rage Embodied, Rage Incarnate, Toad Rage (kept).")]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-18"
    ch.cell(row=r, column=2).value = "v60"
    ch.cell(row=r, column=3).value = (
        "ROUND 177. The score-3 review, rows 1-22: 15 keys on their approved triggers, 9 new families, the squig set. "
        "SHIPPED: installed pack md5 %s; harness 176 full suite 7,403 checks / 0 failures."
        % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user approval 2026-11-18; xlsx v60 supersedes v59; v1-v59 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
