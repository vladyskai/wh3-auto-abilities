#!/usr/bin/env python3
"""Build WH3_abilities_master_v49_2026-11-17.xlsx from v48 - round 165: the night audit.

(1) NEW sheet "Cards": one row per mod entry (946): marker, ability, family, keys, and the card - the text the mod now
    shows as the hover tooltip of the ability's M/A badge. Taken from the harness-164 run (CARD lines), which prints
    every entry's FOURTH.compose_card result from the shipped source.
(2) Column 22 (the plain-English trigger) of the 22 keys whose behaviour changed gets a round-165 note: the game's
    caster rule now honoured (10 keys), the ally target rule (4 entries), the ground cast form (7 WW keys), the sweep
    range (2 keys; Flesh-eating Scarabs is also a ground key, so 22 keys in all).
(3) No count changes: 1,003 implemented, 120 not implemented (36 skipped), 946 entries / 1,003 keys / 95 families.
    Definitions: title v49, section 46. Changelog: a v49 row. v1-v48 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402
from openpyxl.styles import Alignment, Font  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v48_2026-11-16.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v49_2026-11-17.xlsx"
RUN = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_night_audit_harness164\h164_run1.txt"
CARDS_TSV = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_night_audit_harness164\cards_round165.tsv"

NOTES = {
    "wh3_dlc29_unit_abilities_entice": "the game's caster rule health_below_50% is now honoured: not below 50% health",
    "wh3_dlc27_hero_abilities_favoured_by_the_matriarch": "the game's caster rule health_below_25% is now honoured: not below 25% health",
    "wh_dlc06_unit_abilities_the_loons_of_eight_peaks": "the game's caster rule health_below_25% is now honoured: not below 25% health",
    "wh_main_unit_abilities_spinning_loons": "the game's caster rule health_below_25% is now honoured: not below 25% health",
    "wh2_dlc09_character_abilities_curse_of_khsar": "the game's caster rule health_above_50% is now honoured: only at or below 50% health",
    "wh2_dlc09_character_abilities_curse_of_djaf": "the game's caster rule health_above_50% is now honoured: only at or below 50% health",
    "wh3_dlc23_item_abilities_daemon_flask_of_ashak": "the game's caster rule flying_currently is now honoured: not while the caster flies",
    "wh3_dlc29_mount_abilities_feaster_of_souls": "the game's caster rule flying_currently is now honoured: not while the caster flies",
    "wh2_dlc09_character_abilities_stay_here_ill_get_help": "the game's caster rule engaged_in_melee is now honoured: not while the caster is in melee",
    "wh3_main_lord_abilities_eye_of_the_storm": "the game's caster rule unit_is_not_large is now honoured: only when the caster is a large unit",
    "wh2_pro08_character_abilities_helping_hand": "the game's target rule unit_is_not_commander_class is now honoured: the ally must be a Lord or Hero",
    "wh3_dlc27_character_abilities_captain_of_the_phoenix_guard": "the game's target rules unit_is_commander_class and unit_is_large are now honoured: never a Lord, Hero or large unit",
    "wh_main_unit_abilities_entrenchment": "the game's target rule flying_currently is now honoured: never a flying ally",
    "wh2_dlc14_lord_abilities_whiplash": "the game's target rule unit_is_commander_class is now honoured: never a Lord or Hero",
    "wh3_main_daemon_arms_abilities_blue_fire": "now really cast in the ground form under the target (rounds 162-164 sent the unit form)",
    "wh3_main_daemon_arms_abilities_blue_fire_upgraded": "now really cast in the ground form under the target (rounds 162-164 sent the unit form)",
    "wh3_main_weapon_abilities_siegebreaker": "now really cast in the ground form under the target (rounds 162-164 sent the unit form)",
    "wh3_cp1_item_abilities_heavens_gate": "now really cast in the ground form under the target (rounds 162-164 sent the unit form)",
    "wh3_dlc24_unit_abilities_lampreys_bite": "now really cast in the ground form under the target (rounds 162-164 sent the unit form)",
    "wh3_dlc29_unit_abilities_flesh_eating_scarabs": "now really cast in the ground form under the target (rounds 162-164 sent the unit form); its 70% bound 2 m now applies (round 164 fell back to the 52 m default)",
    "wh3_pro10_cataclysm_fire_magma_storm_bound": "now really cast in the ground form under the target (rounds 162-164 sent the unit form)",
    "wh3_dlc29_unit_active_ripping_blades": "its 70% bound 4 m now applies (round 164 fell back to the 52 m default)",
}
assert len(NOTES) == 22


def main():
    entries, _, _ = bd.mod_entries()
    by_marker = {e["marker"]: e for e in entries}
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    assert len(cards) == 946 and set(cards) == set(by_marker), (len(cards), set(by_marker) ^ set(cards))
    with open(CARDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("marker\tability\tfamily\tkeys\tcard\n")
        for e in entries:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (e["marker"], e["name"], e["trigger"], ";".join(e["keys"]), cards[e["marker"]]))

    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    done = set()
    for r in range(2, ws.max_row + 1):
        ks = [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
        hit = [k for k in ks if k in NOTES]
        if hit:
            assert str(ws.cell(row=r, column=20).value) == "IMPLEMENTED", ks
            t = str(ws.cell(row=r, column=22).value)
            ws.cell(row=r, column=22).value = t + " ROUND 165 (night audit): " + NOTES[hit[0]] + "."
            done.update(hit)
    assert done == set(NOTES), set(NOTES) - done

    cs = wb.create_sheet("Cards")
    cs.append(["Marker", "Ability", "Family", "Key(s)", "Card: the M/A badge's hover text (round 165)"])
    for c in range(1, 6):
        cs.cell(row=1, column=c).font = Font(bold=True)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    for col, w in zip("ABCDE", (30, 34, 28, 60, 140)):
        cs.column_dimensions[col].width = w
    for row in cs.iter_rows(min_row=2, min_col=5, max_col=5):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    cs.freeze_panes = "A2"

    n = wb["Numbers"]
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-17     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v49 - ROUND 165: the night audit. No roster change: 1,003 rows / 1,003 keys implemented; 120 not implemented "
        "among the included (36 skipped by the user). The mod: 946 entries / 1,003 keys / 95 trigger families. NEW sheet "
        "Cards: the hover text of every M/A badge.)")
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v48")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v49 (2026-11-17)"
    base = d.max_row + 2
    sec = [
        ("46. ROUND 165 - THE NIGHT AUDIT (v49)", None),
        ("THE CARD", "The per-family sentence of round 93 was never shown (the only card text is the static twui line). "
         "Every entry now has a card composed at load from a corrected sentence per family, its own numbers (70% range and "
         "aura bounds, blast clearances, charge window) and the game's restriction clauses; it is the hover tooltip of the "
         "ability's own M/A badge. Sheet Cards lists all 946."),
        ("THE GAME'S CASTER RULES", "GENERATED FOURTH.USAGE_TEXT (special_ability_to_invalid_usage_flags; 60 keys): an "
         "attempt the game would refuse is not made (in melee, on the ground, in flight, moving, wavering, below or above a "
         "health line, not a large unit). New in effect for 10 keys; the other 50 were already honoured by their families."),
        ("THE ALLY TARGET RULES", "GENERATED FOURTH.ATARGET_TEXT (special_ability_to_invalid_target_flags): the shared ally "
         "picker skips an ally the game would refuse. New in effect: Helping Hand, Captain of the Phoenix Guard, "
         "Entrenchment, Whiplash."),
        ("FIXES", "The 7 ground-only WW keys are cast in the ground form (rounds 162-164 sent the unit form). The two sweeps "
         "(round 164) get their 70% bounds, 4 m and 2 m (they fell back to the 52 m default)."),
    ]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-17"
    ch.cell(row=r, column=2).value = "v49"
    ch.cell(row=r, column=3).value = (
        "ROUND 165. The night audit: the card on every M/A badge (sheet Cards); the game's caster rules (10 keys newly "
        "honoured) and ally target rules (4 entries); the WW ground cast; the sweep bounds. No roster change. SHIPPED: "
        "installed pack md5 %s; harness 164 full suite 7,004 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user request 2026-11-16 (the overnight audit); xlsx v49 supersedes v48; v1-v48 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "cards", len(cards), "notes", len(done))


if __name__ == "__main__":
    main()
