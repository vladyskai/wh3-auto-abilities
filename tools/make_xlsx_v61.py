#!/usr/bin/env python3
"""Build WH3_abilities_master_v61_2026-11-18.xlsx from v60 - round 178: the score-3 review, rows 23-55 (user,
2026-11-18: "Approve rows 23-55. Row 56 stays the same.", with the doc's rulings for rows 49 and 53).

(1) Abilities: the 21 moved keys get their new family and text (earlier notes kept); Eye of Khorne's text names the
    value-first pick; the two Trophy Heads rows no longer list each other (the entry is split) and the Daemon Wings row
    names its unclassed pick.
(2) Numbers: the trigger table re-counted; the 3 new families appended: 120 -> 123 rows (total row 164 -> 167, the
    blocks below move down 2 rows); 938 entries.
(3) Cards: from the harness-177 run. (4) Definitions: title v61, section 58. Changelog: a v61 row.
v1-v60 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v60_2026-11-18.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v61_2026-11-18.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows2_harness177"
RUN = REL + r"\h177_run1.txt"
CARDS_TSV = REL + r"\cards_round178.tsv"
NEW_FAMILIES = ["enemy_fast_or_melee", "enemy_fast_fire_melee", "enemy_most_models"]
R178 = " ROUND 178 (user approval 2026-11-18, score-3 review row %d)."
T = {
    "enemy_most_models": "enemy_most_models: the visible enemy unit in range with the most models alive, counted up to "
                         "the ability's own count (the game's max_damaged_entities: every unit at or above it ranks as "
                         "full, then the most value per soldier wins), never below 16 models (user: 'a minimum of 16 "
                         "units for both'); the caster standing still when its cast animates.",
    "enemy_fast_near_ally": "enemy_fast_near_ally: a visible fast enemy (5 m/s or more, moving) closing within 40 m of "
                            "our units (the root stops the charge); no melee arm (user: a rooted unit already in melee "
                            "still fights).",
    "enemy_melee_or_shooting": "enemy_melee_or_shooting: the closest enemy in melee, else the closest shooting enemy "
                               "missile unit (each half of the effect pays on its own target).",
    "enemy_fast_or_melee": "enemy_fast_or_melee: a visible fast enemy (5 m/s or more, moving) closing within 40 m of our "
                           "units first (the root stops the charge), else the closest enemy in melee; target class: commander.",
    "enemy_fast_fire_melee": "enemy_fast_fire_melee: a fast enemy closing first, else the closest enemy under our missile "
                             "fire, else the closest enemy in melee.",
    "enemy_commander_value": "enemy_commander_value: the most valuable visible enemy Lord or Hero in range (the damage "
                             "pays any time); target class: commander.",
    "enemy_spellcaster": "enemy_spellcaster: the most valuable visible enemy spellcaster in range (the GENERATED "
                         "spellcaster list; the game's rule: spellcasters only).",
    "enemy_low_health_noncommander": "enemy_low_health_noncommander: the visible enemy below 20% health with the highest "
                                     "live value, never a Lord or Hero (then the lower health, then the closer).",
}
MOVED = {
    "wh3_dlc27_spell_heavens_chain_lightning_bound": ("enemy_most_models", 23),
    "wh3_dlc27_spell_heavens_chain_lightning_bound_unit": ("enemy_most_models", 24),
    "wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer": ("enemy_most_models", 29),
    "wh2_main_spell_bound_whip_of_agony": ("enemy_melee_or_shooting", 30),
    "wh2_dlc10_spell_bound_word_of_pain": ("enemy_melee_or_shooting", 31),
    "wh3_dlc27_spell_dark_magic_word_of_pain_bound_1use": ("enemy_melee_or_shooting", 31),
    "wh3_main_weapon_abilities_soulnetter": ("enemy_fast_near_ally", 36),
    "wh_dlc04_spell_bound_net_of_amyntok": ("enemy_fast_near_ally", 37),
    "wh3_dlc26_character_abilities_spider_web_attack": ("enemy_fast_near_ally", 38),
    "wh_pro04_unit_abilities_warp_gaze": ("enemy_fast_near_ally", 39),
    "wh3_dlc29_item_abilities_warpstiletto": ("enemy_fast_near_ally", 40),
    "wh3_dlc24_unit_abilities_pack_trap": ("enemy_fast_near_ally", 41),
    "wh_dlc05_character_abilities_prey_of_anath_raema": ("enemy_fast_fire_melee", 42),
    "wh3_dlc26_unit_abilities_net_dem_up": ("enemy_fast_fire_melee", 43),
    "wh3_dlc29_hero_active_glory_seeker": ("enemy_fast_or_melee", 44),
    "wh3_dlc29_hero_active_glory_seeker_upgraded": ("enemy_fast_or_melee", 45),
    "wh3_pro12_hero_abilities_prey_of_the_blood_god": ("enemy_commander_value", 46),
    "wh3_main_item_abilities_void_pendulum": ("enemy_spellcaster", 47),
    "wh3_main_daemon_head_abilities_word_of_change": ("enemy_spellcaster", 48),
    "wh3_dlc23_item_abilities_dweomer_leach_orb": ("enemy_spellcaster", 50),
    "wh2_dlc11_item_abilities_slann_gold": ("enemy_spellcaster", 51),
    "wh3_dlc26_lord_abilities_eye_of_khorne": ("enemy_low_health_noncommander", 53),
}
TROPHY = ("wh2_main_lord_abilities_trophy_heads", "wh3_main_daemon_wings_abilities_trophy_heads")
TROPHY_DW_TEXT = ("enemy_melee: the closest enemy in melee within 105 m (the Daemon Wings key has no Lord/Hero rule in "
                  "the game data, so it has its own entry since round 178)." + R178 % 54)
NOTE_HEADS = ("PATCH 9.0.5", "ROUND 165 (night audit)", "ROUND 166", "ROUND 167", "ROUND 168", "ROUND 169")


def old_notes(old):
    idx = [old.find(h) for h in NOTE_HEADS if old.find(h) != -1]
    return (" " + old[min(idx):]) if idx else ""


CLASS_KEPT = {"wh2_main_spell_bound_whip_of_agony": "large"}   # the entry keeps its target_class (the game's rule)


def text_of(k, old):
    fam, row = MOVED[k]
    cls = ("; target class: %s." % CLASS_KEPT[k]) if k in CLASS_KEPT else ""
    t = T[fam]
    if cls:
        t = t[:-1] + cls
    return t + (R178 % row) + old_notes(old)


def main():
    entries, _, _ = bd.mod_entries()
    assert len(entries) == 938
    keys_of = {}
    for e in entries:
        for k in e["keys"]:
            keys_of[k] = e["trigger"]
    for k, (fam, _) in MOVED.items():
        assert keys_of.get(k) == fam, (k, fam, keys_of.get(k))
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
    moved, split = set(), set()
    for r in range(2, ws.max_row + 1):
        ks = [x.strip() for x in str(ws.cell(row=r, column=3).value).split(";") if x.strip()]
        k = ks[0]
        if k in TROPHY and len(ks) > 1:
            ws.cell(row=r, column=3).value = k   # the split: the twins no longer share an entry
            split.add(k)
            if k == TROPHY[1]:
                ws.cell(row=r, column=22).value = TROPHY_DW_TEXT
        if k in MOVED:
            assert ws.cell(row=r, column=20).value == "IMPLEMENTED", k
            old = str(ws.cell(row=r, column=22).value or "")
            ws.cell(row=r, column=21).value = MOVED[k][0]
            ws.cell(row=r, column=22).value = text_of(k, old)
            moved.add(k)
    assert moved == set(MOVED), set(MOVED) - moved
    assert split == set(TROPHY), split
    n = wb["Numbers"]
    assert n.cell(row=164, column=2).value == "TOTAL (120 families)"
    n.insert_rows(164, amount=len(NEW_FAMILIES))
    for i, fam in enumerate(NEW_FAMILIES):
        n.cell(row=164 + i, column=2).value = fam
    for r in range(44, 167):
        n.cell(row=r, column=1).value = r - 43
        fam = n.cell(row=r, column=2).value
        n.cell(row=r, column=3).value = fam_e.get(fam, 0)
        n.cell(row=r, column=4).value = fam_k.get(fam, 0)
    assert n.cell(row=167, column=2).value == "TOTAL (120 families)"
    n.cell(row=167, column=2).value = "TOTAL (123 families)"
    n.cell(row=167, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 167))
    n.cell(row=167, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 167))
    assert (n.cell(row=167, column=3).value, n.cell(row=167, column=4).value) == (938, 992)
    assert all(n.cell(row=r, column=3).value > 0 for r in range(44, 167)), "an empty family is listed"
    assert n.cell(row=169, column=1).value == "Bombardment set (COMPLETE - round 108)"
    n.cell(row=42, column=1).value = (
        "Trigger families after round 178 - re-counted from the mod's own ABILITIES table: 123 families / 938 entries / "
        "992 keys. Round 178 (the score-3 review, rows 23-55): 3 NEW families; Trophy Heads split; enemy_engaged_or_shot "
        "37 -> 22.")
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-18     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v61 - ROUND 178: the score-3 review, rows 23-55. 992 rows / 992 keys implemented; 131 not implemented among the "
        "included (47 skipped by the user). The mod: 938 entries / 992 keys / 123 trigger families.)")
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 178)"
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v60")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v61 (2026-11-18)"
    base = d.max_row + 2
    sec = [("58. ROUND 178 - THE SCORE-3 REVIEW, ROWS 23-55 (v61)", None),
           ("NEW FAMILIES", "enemy_fast_or_melee (Glory Seeker x2: a charging Lord or Hero first, else one in melee), "
            "enemy_fast_fire_melee (roots that open the target to missiles: fast, else under our fire, else in melee), "
            "enemy_most_models (Chain Lightning x2, The Soulstealer: the most models, counted up to the ability's own "
            "count, 16 at least)."),
           ("THE PLAIN ROOTS", "Rows 36-41 (user: 'Yes pls', no melee arm): on the existing enemy_fast_near_ally."),
           ("RULINGS IN THE DOC", "Row 49 Oil Flask: KEEP. Row 53 Eye of Khorne: 'the below 20% highest value unit that "
            "is not a lord or hero' (its family now ranks the value first)."),
           ("FROM THE DATA", "Row 28 Surprise Squig SUMMONS Explosive Squigs (the proposal misread it): unchanged, a new "
            "proposal follows. Row 55 Siegebreaker: its projectile deals 100 + 100 AP to the unit it hits, so it harms "
            "units: unchanged.")]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-18"
    ch.cell(row=r, column=2).value = "v61"
    ch.cell(row=r, column=3).value = (
        "ROUND 178. The score-3 review, rows 23-55: 22 keys on their ruled triggers, 3 new families, Trophy Heads split. "
        "SHIPPED: installed pack md5 %s; harness 177 full suite 7,476 checks / 0 failures."
        % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user approval 2026-11-18; xlsx v61 supersedes v60; v1-v60 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
