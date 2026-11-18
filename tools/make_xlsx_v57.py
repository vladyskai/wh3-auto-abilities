#!/usr/bin/env python3
"""Build WH3_abilities_master_v57_2026-11-18.xlsx from v56 - round 174: the score 1-2 review, rows 24-50.

(1) Abilities: the 29 moved keys get their new family and trigger text.
(2) Numbers: the trigger table re-counted from the mod; the 4 emptied families (ally_overseer, ally_beast, ally_broken,
    ally_missile) leave it and the 13 new ones are appended: 102 -> 111 rows (total row 146 -> 155, the blocks below
    move down 9 rows). Implemented 992 / not implemented 131 unchanged.
(3) Cards: from the harness-173 run. (4) Definitions: title v57, section 54. Changelog: a v57 row.
v1-v56 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402
import make_xlsx_v52 as M52  # noqa: E402  (the round-168 moving note; nothing is written on import)

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v56_2026-11-18.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v57_2026-11-18.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_review_rows_harness173"
RUN = REL + r"\h173_run1.txt"
CARDS_TSV = REL + r"\cards_round174.tsv"
NEW_FAMILIES = ["enemy_large_value_shot", "enemy_spellcaster", "enemy_ground_spellcasters", "enemy_missile_value",
                "enemy_ground_shooters", "enemy_commander_wavering", "ally_charge_melee", "ally_wavering_melee",
                "ally_lord_melee", "ally_missile_shooting", "ally_melee_risk", "ally_beast_charge", "ally_routing"]
EMPTIED = ["ally_overseer", "ally_beast", "ally_broken", "ally_missile"]
R174 = " ROUND 174 (user ruling 2026-11-18, review row %d)."
T = {
    "enemy_large_shot": "enemy_large_shot: the most valuable large enemy in range (clear of our units by 10 m), else the "
                        "most armoured enemy infantry; the caster out of melee.",
    "enemy_large_value_shot": "enemy_large_value_shot: the most valuable large enemy in range (clear of our units by 10 m), "
                              "else the most valuable enemy infantry per soldier (never the armour fallback); the caster "
                              "out of melee.",
    "enemy_single_drain": "enemy_single_drain: the most valuable single-entity enemy in range; no safety margin (a "
                          "direct effect).",
    "enemy_spellcaster": "enemy_spellcaster: the most valuable visible enemy spellcaster in range (GENERATED spellcaster "
                         "list: a spell lore in the game data, or a lore from the campaign skill tree).",
    "enemy_ground_spellcasters": "enemy_ground_spellcasters: on the ground under the visible enemy spellcaster in range "
                                 "with the most other enemy spellcasters within 24 m (70% of the 35 m spot), then their "
                                 "value.",
    "enemy_commander_value": "enemy_commander_value: the most valuable visible enemy Lord or Hero in range (characters "
                             "carry the most abilities).",
    "enemy_missile_value": "enemy_missile_value: the most valuable enemy missile unit in range that is shooting and not in "
                           "melee.",
    "enemy_ground_shooters": "enemy_ground_shooters: on the ground under the shooting enemy missile unit in range with the "
                             "most shooting value within 24 m (70% of the 35 m spot).",
    "enemy_commander_wavering": "enemy_commander_wavering: the visible enemy Lord or Hero in range that is wavering or "
                                "routing (the closest read to the game's half-morale rule; ASSUMPTION), one in melee "
                                "first, then the most valuable.",
    "ally_charge_melee": "ally_charge_melee: the nearest ally within 70 m that is charging, else one that made contact at "
                         "most 2 s ago; never a missile unit. Starts on M (Rampage).",
    "ally_wavering_melee": "ally_wavering_melee: the most valuable ally within 140 m in melee and wavering; never a "
                           "missile unit. Starts on M (Rampage).",
    "ally_lord_melee": "ally_lord_melee: the nearest Lord or Hero ally within 35 m that is in melee, whether or not the "
                       "caster fights (the game's own rule: Lord or Hero only). Keeps its default (armed).",
    "ally_missile_shooting": "ally_missile_shooting: the most valuable missile ally within 70 m that is shooting past its "
                             "cast point.",
    "ally_melee_risk": "ally_melee_risk: the most valuable eligible ally within 70 m (never a Lord or Hero, large or "
                       "flying) in melee and wavering or at or below 50% health.",
    "ally_beast_charge": "ally_beast_charge: the nearest beast ally within 70 m that is charging, else one that made "
                         "contact at most 2 s ago.",
    "ally_routing": "ally_routing: the most valuable routing (or morale-broken) ally within 140 m; the picker keeps routing "
                    "allies for this family only.",
}
MOVED = {
    "wh2_dlc13_weapon_abilities_amber_bow": ("enemy_large_shot", 24),
    "wh2_dlc15_spell_bound_gaze_of_nagash": ("enemy_large_shot", 25),
    "wh2_main_spell_bound_hand_of_gods": ("enemy_large_value_shot", 26),
    "wh_main_spell_light_shems_burning_gaze_bound": ("enemy_large_value_shot", 27),
    "wh2_dlc15_character_abilities_goggly_glare": ("enemy_large_value_shot", 28),
    "wh_dlc06_spell_bound_vindictive_glare": ("enemy_large_value_shot", 29),
    "wh2_dlc15_lord_abilities_dont_even_try_it": ("enemy_single_drain", 30),
    "wh2_dlc16_character_abilities_muster_of_malevolents": ("enemy_single_drain", 31),
    "wh2_main_item_abilities_cube_of_darkness": ("enemy_spellcaster", 32),
    "wh_main_item_abilities_scroll_of_leeching": ("enemy_spellcaster", 33),
    "wh2_main_item_abilities_the_vortex_shard": ("enemy_spellcaster", 34),
    "wh2_main_item_abilities_the_tricksters_pendant": ("enemy_ground_spellcasters", 35),
    "wh_main_item_abilities_tricksters_shard": ("enemy_ground_spellcasters", 36),
    "wh3_main_character_abilities_silence_the_prey": ("enemy_commander_value", 37),
    "wh2_dlc11_lord_abilities_power_siphon": ("enemy_commander_value", 38),
    "wh3_dlc27_character_abilities_the_black_tongue": ("enemy_spellcaster", 39),
    "wh2_dlc16_character_abilities_pageant_of_shrikes": ("enemy_missile_value", 40),
    "wh_dlc03_item_abilities_chalice_of_dark_rain": ("enemy_ground_shooters", 41),
    "wh3_dlc29_lord_abilities_transfix": ("enemy_commander_wavering", 42),
    "wh2_main_unit_abilities_fury_of_khaine": ("ally_charge_melee", 44),
    "wh3_dlc29_lord_abilities_verminous_fury": ("ally_wavering_melee", 45),
    "wh2_pro08_character_abilities_helping_hand": ("ally_lord_melee", 46),
    "wh3_main_lord_abilities_inspired_marksmanship_i": ("ally_missile_shooting", 47),
    "wh3_main_lord_abilities_inspired_marksmanship_ii": ("ally_missile_shooting", 47),
    "wh3_main_lord_abilities_inspired_marksmanship_iii": ("ally_missile_shooting", 47),
    "wh3_dlc29_hero_active_overseer_of_the_unseen": ("ally_melee_risk", 48),
    "wh2_dlc14_lord_abilities_whiplash": ("ally_beast_charge", 49),
    "wh3_dlc27_character_abilities_iron_hand_captain": ("ally_routing", 50),
}


CLASS = {"wh3_dlc29_lord_abilities_transfix": "commander", "wh3_main_character_abilities_silence_the_prey": "commander",
         "wh2_dlc11_lord_abilities_power_siphon": "commander"}   # the entries that carry target_class
# the notes earlier rounds appended to a row's text (kept: they still hold for the ability)
NOTE_HEADS = ("PATCH 9.0.5", "ROUND 165 (night audit)", "ROUND 166", "ROUND 167", "ROUND 168", "ROUND 169")
OLD = {}   # key -> the v56 text (filled by main before text_of is used)


def old_notes(old):
    idx = [old.find(h) for h in NOTE_HEADS if old.find(h) != -1]
    return (" " + old[min(idx):]) if idx else ""


def text_of(k, old=None):
    fam, row = MOVED[k]
    t = T[fam]
    if k in CLASS:
        t = t.rstrip(".") + "; target class: " + CLASS[k] + "."
    t = t + (R174 % row) + old_notes(OLD.get(k, "") if old is None else old)
    # the round-167 note said the family starts armed; the two Rampage buffs' new families start unarmed anyway
    t = t.replace(" ROUND 167: starts on M even though its family starts armed (the game marks it rampage; user "
                  "ruling 2026-11-17).", "")
    # the round-168 rule (no cast animation: may fire while its caster moves) now covers the two drains as well
    if k in moving() and M52.NOTE not in t:
        t = t + " " + M52.NOTE
    return t


_MOVING = []


def moving():
    if not _MOVING:
        _MOVING.append(M52.moving_keys()[0])
    return _MOVING[0]


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
            OLD[k] = str(ws.cell(row=r, column=22).value or "")
            ws.cell(row=r, column=21).value = MOVED[k][0]
            ws.cell(row=r, column=22).value = text_of(k)
            moved.add(k)
    assert moved == set(MOVED), set(MOVED) - moved

    n = wb["Numbers"]
    assert n.cell(row=146, column=2).value == "TOTAL (102 families)"
    names = [n.cell(row=r, column=2).value for r in range(44, 146)]
    assert len(names) == 102 and all(f in names for f in EMPTIED)
    for f in EMPTIED:
        assert fam_e.get(f, 0) == 0, f
    for r in sorted((44 + names.index(f) for f in EMPTIED), reverse=True):
        n.delete_rows(r, 1)
    kept = [n.cell(row=r, column=2).value for r in range(44, 142)]
    assert len(kept) == 98 and n.cell(row=142, column=2).value == "TOTAL (102 families)"
    n.insert_rows(142, amount=len(NEW_FAMILIES))
    for i, fam in enumerate(NEW_FAMILIES):
        n.cell(row=142 + i, column=2).value = fam
    for r in range(44, 155):
        n.cell(row=r, column=1).value = r - 43
        fam = n.cell(row=r, column=2).value
        n.cell(row=r, column=3).value = fam_e.get(fam, 0)
        n.cell(row=r, column=4).value = fam_k.get(fam, 0)
    assert n.cell(row=155, column=2).value == "TOTAL (102 families)"
    n.cell(row=155, column=2).value = "TOTAL (111 families)"
    n.cell(row=155, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 155))
    n.cell(row=155, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 155))
    assert (n.cell(row=155, column=3).value, n.cell(row=155, column=4).value) == (937, 992)
    assert all(n.cell(row=r, column=3).value > 0 for r in range(44, 155)), "an empty family is listed"
    assert n.cell(row=157, column=1).value == "Bombardment set (COMPLETE - round 108)"
    n.cell(row=42, column=1).value = (
        "Trigger families after round 174 - re-counted from the mod's own ABILITIES table: 111 families / 937 entries / "
        "992 keys. Round 174 (the score 1-2 review, rows 24-50): 13 NEW families; ally_overseer, ally_beast, ally_broken "
        "and ally_missile emptied (their entries moved); enemy_blob 77 -> 71.")
    assert n.cell(row=13, column=3).value == 992 and n.cell(row=14, column=3).value == 131
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-18     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v57 - ROUND 174: the score 1-2 review, rows 24-50. 992 rows / 992 keys implemented; 131 not implemented among "
        "the included (47 skipped by the user). The mod: 937 entries / 992 keys / 111 trigger families.)")
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 174)"
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v56")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v57 (2026-11-18)"
    base = d.max_row + 2
    sec = [
        ("54. ROUND 174 - THE SCORE 1-2 REVIEW, ROWS 24-50 (v57)", None),
        ("SPELLCASTER CLASS", "GENERATED by tools/gen_spellcaster_keys.py (865 land units): a spell lore in "
         "special_ability_groups_to_units_junctions, or a campaign skill tree that grants a lore or a lore spell (user "
         "ruling 2026-11-18: 'Okay, then let's use the caster list'). Never agent_subtypes.is_caster."),
        ("NEW FAMILIES", ", ".join(NEW_FAMILIES) + "."),
        ("ALLY SCORES", "The ally picker scores each ally: charging 2, fresh contact 1 (the closest on a tie), or the "
         "live strategic value (the most valuable wins). Iron-Handed Captain's family alone keeps routing allies."),
        ("CLUSTER", "The two ground items pick the enemy with the most of its kind within 24 m (70% of the 35 m spot)."),
    ]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-18"
    ch.cell(row=r, column=2).value = "v57"
    ch.cell(row=r, column=3).value = (
        "ROUND 174. The score 1-2 review, rows 24-50: 29 keys on their ruled triggers, 13 new families, the spellcaster "
        "class. SHIPPED: installed pack md5 %s; harness 173 full suite 7,304 checks / 0 failures."
        % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user ruling 2026-11-18; xlsx v57 supersedes v56; v1-v56 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
