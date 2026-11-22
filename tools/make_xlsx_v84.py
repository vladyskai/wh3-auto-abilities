#!/usr/bin/env python3
"""Build WH3_abilities_master_v84_2026-11-22.xlsx from v83 - round 210 (the user's second replies to the code review).

(1) Abilities: Spinning Loons and The Loons of Eight Peaks move from enemy_ground_melee to enemy_wave_charge (columns
    21 and 22, the user's new rule). The five caster-front breaths gain the FROM THE CASTER sentence in column 22.
(2) Cards: the two Loons cards, from the harness-208 run.
(3) Numbers: the date line, the family note, the enemy_ground_melee and enemy_wave_charge counts.
(4) Definitions: title v84, section 81. Changelog: a v84 row. v1-v83 are never opened for writing."""
import collections
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v83_2026-11-22.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v84_2026-11-22.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_replies2_harness208"
RUN = REL + r"\h208_run1.txt"
LOONS = ["wh_main_unit_abilities_spinning_loons", "wh_dlc06_unit_abilities_the_loons_of_eight_peaks"]
MARKERS = {"spinning_loons": LOONS[0], "loons_of_eight_peaks": LOONS[1]}
CONES = ["wh2_dlc13_character_ability_shatter", "wh2_dlc15_character_abilities_fishy_breathe",
         "wh2_main_mount_bound_pestilent_breath", "wh3_main_spell_bound_pestilent_breath",
         "wh_main_weapon_abilities_skabscrath"]
LOON_TRIG = ("enemy_wave_charge: not routing. ROUND 210, the user's own rule (2026-11-22: 'they could only fire while the "
             "caster is standing. And there is ... infantry enemy unit that is approaching. And it's, let's say, between "
             "25 and 15 meters from the caster unit. And then you just cast in that direction ... single entities is okay, "
             "but any friendly units that are not single entity should [not] be in the path'). The caster STANDING "
             "(is_moving() exactly false). A visible enemy INFANTRY unit of more than one man (never a flying one) that "
             "is moving and coming closer to the caster (its gap shrinks at least 1 m per second, measured over 1 s), "
             "with its edge 15 to 25 m away (unit_distance, the user's distances, outside the range rule). None of our "
             "units of more than one man in the fanatics' path: from the caster towards that enemy, 84 m long, 4 m wide "
             "at the start, widening by the simulated 95% sideways drift of 56 m at the end (the GENERATED WW table, kind "
             "8). Our single entities and our expendable or cheap units do not count. The closest such enemy wins. Cast: "
             "perform_special_ability_ground(key, a point on the line towards the enemy at most 20 m from the caster, "
             "the bearing, 0). Re-checked on a fresh map before the cast. Before round 210: the nearest enemy in melee "
             "(round 143) plus a clear 98 m ring (round 209). NOT SEEN IN GAME.")
CONE_ADD = (" ROUND 210 (user test 2026-11-22: 'I tested Skarbscrath and it always starts at the caster'): the breath is "
            "now a CONE FROM THE CASTER, 0.1 m wide at the caster and growing per metre along its path (the GENERATED cone "
            "table), and its length is the path alone, without the launch offset. It follows the exact-wave rule: the "
            "value of the standing enemy soldiers under it must be above zero (single entities not counted), and at most "
            "5 of OUR soldiers may stand under it (single entities and the caster not counted). The band of the full "
            "radius plus 10 m described above no longer applies. Seen in game for Skabscrath only.")


def read_cards():
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    return cards


def plan():
    wb = openpyxl.load_workbook(SRC, read_only=True)
    out = []
    for r, row in enumerate(wb["Abilities"].iter_rows(values_only=True, min_row=2), start=2):
        k = str(row[2]).split(";")[0].strip()
        if k in LOONS:
            assert row[19] == "IMPLEMENTED" and row[20] == "enemy_ground_melee", k
            out.append((r, 21, row[20], "enemy_wave_charge"))
            out.append((r, 22, row[21], LOON_TRIG))
        elif k in CONES:
            assert row[19] == "IMPLEMENTED" and row[20] == "enemy_cone", k
            out.append((r, 22, row[21], (row[21] or "").rstrip() + CONE_ADD))
    wb.close()
    return out


def family_counts():
    entries, _, _ = bd.mod_entries()
    fc = collections.defaultdict(lambda: [0, 0])
    for e in entries:
        fc[e["trigger"]][0] += 1
        fc[e["trigger"]][1] += len(e["keys"])
    return entries, fc


def main():
    edits = plan()
    assert len(edits) == 9, len(edits)
    assert not os.path.exists(DST), DST
    entries, fc = family_counts()
    assert len(entries) == 982 and fc["enemy_wave_charge"] == [2, 2] and fc["enemy_ground_melee"][0] == 72, \
        (fc["enemy_wave_charge"], fc["enemy_ground_melee"])
    cards = read_cards()
    assert len(cards) == 982, len(cards)
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    for r, c, old, new in edits:
        assert ws.cell(row=r, column=c).value == old
        ws.cell(row=r, column=c).value = new
    cs = wb["Cards"]
    done = 0
    for r in range(2, cs.max_row + 1):
        m = cs.cell(row=r, column=1).value
        if m in MARKERS:
            e = [x for x in entries if x["marker"] == m][0]
            cs.cell(row=r, column=3).value = e["trigger"]
            cs.cell(row=r, column=5).value = cards[m]
            done += 1
        else:
            assert m is None or cs.cell(row=r, column=5).value == cards[m], m   # no other card may have moved
    assert done == 2, done
    nm = wb["Numbers"]
    assert "v83 - ROUND 209" in str(nm.cell(row=7, column=1).value)
    nm.cell(row=7, column=1).value = (
        "Date: 2026-11-22     Rule in force since: 2026-10-18     Inventory: 1,802 active abilities     "
        "(v84 - ROUND 210: the Loons on their own rule, the five caster-front breaths as cones from the caster. 1,035 rows "
        "/ 1,035 keys implemented, 80 not implemented among the included (all decided by the user), 0 open. The mod: 982 "
        "entries / 1,035 keys / 141 trigger families, all 141 in use.)")
    assert str(nm.cell(row=42, column=1).value).startswith("Trigger families after round 209")
    nm.cell(row=42, column=1).value = (
        "Trigger families after round 210 - re-counted from the mod's own ABILITIES table: 141 families (all in use) / "
        "982 entries / 1,035 keys. Round 210: the two Loons moved from enemy_ground_melee (72) to enemy_wave_charge (2), "
        "which had been empty since round 204.")
    seen = 0
    for r in range(44, 185):
        fam = nm.cell(row=r, column=2).value
        if fam in ("enemy_ground_melee", "enemy_wave_charge"):
            nm.cell(row=r, column=3).value = fc[fam][0]
            nm.cell(row=r, column=4).value = fc[fam][1]
            seen += 1
        elif fam is not None:
            assert [nm.cell(row=r, column=3).value, nm.cell(row=r, column=4).value] == fc[fam], fam
    assert seen == 2, seen
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v83")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v84 (2026-11-22)"
    base = d.max_row + 2
    sec = [("81. ROUND 210 - THE LOONS' OWN RULE, THE BREATHS FROM THE CASTER (v84)", None),
           ("LOONS", "User 2026-11-22, after testing round 209: 'They are not working as intended ... I would like to change "
            "them completely.' His rule: the caster standing, an enemy infantry unit approaching between 15 and 25 m, the "
            "cast in that direction, none of our units of more than one man in the path. The path's width comes from the "
            "simulated drift of the fanatics (tools\\gen_ww_tables.py, kind 8)."),
           ("BREATHS", "User 2026-11-22: 'I tested Skarbscrath and it always starts at the caster.' Shatter, Pestilent "
            "Breath x2, Fishy Breath and Skabscrath are tested as cones from the caster with the exact-wave rule. Their "
            "cone numbers are GENERATED (tools\\gen_wave_cone.py, 25 rows now)."),
           ("MACHINERY", "Not roster changes: a charge's run-up is the smaller of 12 m and 2 seconds of the unit's own run "
            "speed (user: 'okay, do it'), and a unit's owned abilities are read again after a cast on it (the "
            "transformation of Malus Darkblade keeps the unit id and the unit type).")]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-22"
    ch.cell(row=r, column=2).value = "v84"
    ch.cell(row=r, column=3).value = (
        "ROUND 210. The Loons x2: enemy_ground_melee -> enemy_wave_charge (the user's rule; 2 families, 2 trigger texts, 2 "
        "cards). The five caster-front breaths: cones from the caster (5 trigger texts). Numbers: the two family counts. "
        "SHIPPED: installed pack md5 %s. Harness 208 full suite %s checks / 0 failures."
        % (os.environ.get("WH3_PACK_MD5", "PENDING"), os.environ.get("WH3_CHECKS", "PENDING")))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-22. xlsx v84 supersedes v83. v1-v83 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "edits", len(edits), "cards", done)


if __name__ == "__main__":
    main()
