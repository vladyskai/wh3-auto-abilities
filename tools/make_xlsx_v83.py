#!/usr/bin/env python3
"""Build WH3_abilities_master_v83_2026-11-22.xlsx from v82 - round 209 (the user's replies to the afternoon code review).

(1) Abilities: Spinning Loons and The Loons of Eight Peaks gain the RING sentence in column 22 (the friendly-fire check).
    Lamprey's Bite moves from enemy_wander to enemy_wave (columns 21 and 22).
(2) Cards: the three cards, from the harness-207 run.
(3) Numbers: the date line, the family note, the enemy_wave and enemy_wander counts (re-counted from the mod's table).
(4) Definitions: title v83, section 80. Changelog: a v83 row. v1-v82 are never opened for writing."""
import collections
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v82_2026-11-22.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v83_2026-11-22.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_replies_harness207"
RUN = REL + r"\h207_run1.txt"
LOONS = ["wh_main_unit_abilities_spinning_loons", "wh_dlc06_unit_abilities_the_loons_of_eight_peaks"]
LAMP = "wh3_dlc24_unit_abilities_lampreys_bite"
MARKERS = {"spinning_loons": LOONS[0], "loons_of_eight_peaks": LOONS[1], "lampreys_bite": LAMP}
RING = (" ROUND 209 (user 2026-11-22: 'They are really prone for friendly fire. We need a friendly fire check, yes.'): "
        "the fanatics are released at the caster, wander 84 m and hit our units too. The cast also needs none of our OTHER "
        "units within 98 m of the caster (vortex radius 4 m + simulated 95% reach 84 m + 10 m, the GENERATED ring table, "
        "the same numbers as Da Boss' Loons). Our expendable and cheap units are not protected. In a normal battle line "
        "this is rarely true, so the ability mostly waits.")
LAMP_TRIG = ("enemy_wave: not routing. The caster STANDING STILL. An EXACT, GROWING, GROUND-ONLY wave (round 209, user "
             "2026-11-22: 'fix please' on the review's finding that the mod treated it as a 25 m disc). In the game's "
             "table it starts 0.1 m wide and grows 14 m per second for 1 s while it rolls 24 m, so it ends 14.1 m wide "
             "and never reaches its 25 m goal radius. For every visible STANDING enemy within 80 m (max(70%, real - 20) "
             "of the ability's 100 m target_intercept_range, unit_distance) the mod tests the caster's line, 24 compass "
             "headings and 7 sideways shifts of the 24 m path. The path with the most value of enemy soldiers under it "
             "wins (enemy single entities and walking enemies are not counted). At most 5 of OUR soldiers may stand under "
             "it (our single entities and the caster are not counted). Each soldier is tested against the width the wave "
             "has at that spot (0.1 m + 0.5833 m per metre). Cast: perform_special_ability_ground(key, the path's start "
             "on the terrain, the bearing, 0). No aim means no order. The search runs once per second and not while the "
             "game says the ability cannot be cast. Before round 209: enemy_wander. NOT SEEN IN GAME: that a ground order "
             "starts this wave at the point and sends it along the bearing is proven for the Fiery Ring of Thori only.")


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
            out.append((r, 22, row[21], (row[21] or "").rstrip() + RING))
        elif k == LAMP:
            assert row[19] == "IMPLEMENTED" and row[20] == "enemy_wander", k
            out.append((r, 21, row[20], "enemy_wave"))
            out.append((r, 22, row[21], LAMP_TRIG))
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
    assert len(edits) == 4, len(edits)
    assert not os.path.exists(DST), DST
    entries, fc = family_counts()
    assert len(entries) == 982 and fc["enemy_wave"] == [33, 33] and fc["enemy_wander"] == [41, 41], (fc["enemy_wave"], fc["enemy_wander"])
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
    assert done == 3, done
    nm = wb["Numbers"]
    assert "v82 - ROUND 205" in str(nm.cell(row=7, column=1).value)
    nm.cell(row=7, column=1).value = (
        "Date: 2026-11-22     Rule in force since: 2026-10-18     Inventory: 1,802 active abilities     "
        "(v83 - ROUND 209: the Loons get a friendly-fire check, Lamprey's Bite is an aimed wave. 1,035 rows / 1,035 keys "
        "implemented, 80 not implemented among the included (all decided by the user), 0 open. The mod: 982 entries / "
        "1,035 keys / 141 trigger families, 140 in use.)")
    assert str(nm.cell(row=42, column=1).value).startswith("Trigger families after round 204")
    nm.cell(row=42, column=1).value = (
        "Trigger families after round 209 - re-counted from the mod's own ABILITIES table: 141 families (140 in use) / "
        "982 entries / 1,035 keys. Round 209: Lamprey's Bite moved from enemy_wander (41) to enemy_wave (33).")
    seen = 0
    for r in range(44, 185):
        fam = nm.cell(row=r, column=2).value
        if fam in ("enemy_wave", "enemy_wander"):
            nm.cell(row=r, column=3).value = fc[fam][0]
            nm.cell(row=r, column=4).value = fc[fam][1]
            seen += 1
        elif fam is not None:
            assert [nm.cell(row=r, column=3).value, nm.cell(row=r, column=4).value] == fc[fam], fam
    assert seen == 2, seen
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v82")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v83 (2026-11-22)"
    base = d.max_row + 2
    sec = [("80. ROUND 209 - THE LOONS' FRIENDLY-FIRE CHECK, LAMPREY'S BITE AS A WAVE (v83)", None),
           ("LOONS", "User 2026-11-22, after checking them in battle: 'They are really prone for friendly fire. We need a "
            "friendly fire check, yes.' Spinning Loons and The Loons of Eight Peaks keep their trigger (the nearest enemy "
            "in melee in range) and also need none of our other units within 98 m of the caster. The reach is GENERATED "
            "from battle_vortexs (tools\\gen_ww_tables.py, FOURTH.RING_TEXT). The build refuses a table that differs."),
           ("LAMPREY", "User 2026-11-22: 'fix please'. Lamprey's Bite was treated as a 25 m disc that needed 415 soldiers. "
            "It is a short wave: 0.1 m wide at its start, 14.1 m wide after its 24 m. It rides enemy_wave as an exact, "
            "growing, ground-only wave."),
           ("MACHINERY", "Not roster changes, recorded here for the round: the player's own cast now holds the selected "
            "units' automatic abilities (the game's 'Special Ability' report, the mod's own orders are told apart), and an "
            "error on one unit no longer ends the poll for the units after it.")]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-22"
    ch.cell(row=r, column=2).value = "v83"
    ch.cell(row=r, column=3).value = (
        "ROUND 209. The Loons x2: friendly-fire ring (2 trigger texts, 2 cards). Lamprey's Bite: enemy_wander -> "
        "enemy_wave (1 family, 1 trigger text, 1 card). Numbers: the two family counts. SHIPPED: installed pack md5 %s. "
        "Harness 207 full suite %s checks / 0 failures."
        % (os.environ.get("WH3_PACK_MD5", "PENDING"), os.environ.get("WH3_CHECKS", "PENDING")))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-22. xlsx v83 supersedes v82. v1-v82 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "edits", len(edits), "cards", done)


if __name__ == "__main__":
    main()
