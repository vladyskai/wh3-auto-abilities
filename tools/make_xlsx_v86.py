#!/usr/bin/env python3
"""Build WH3_abilities_master_v86_2026-11-28.xlsx from v85 - round 220 (a placed effect does not wait for its caster).

(1) Abilities: the 51 rows whose key is a PLACED effect with a cast animation gain the PLACED sentence in column 22.
(2) Cards: the cards that changed between the harness-217 and harness-218 runs (the caster's stand-still words gone).
(3) Numbers: the date line only.
(4) Definitions: title v86, section 83. Changelog: a v86 row. v1-v85 are never opened for writing."""
import collections
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402
import gen_anim_keys as GA  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v85_2026-11-28.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v86_2026-11-28.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_placed_harness218"
RUN = REL + r"\h218_run1.txt"
OLD_RUN = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_cover_harness217\h217_run1.txt"
LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
PLACED_ADD = (" ROUND 220 (user test 2026-11-28: Brass Orb 'didn't stop the unit when I cast', and 'Yes' to all placed "
              "effects): this ability's effect is PLACED (a vortex, no projectile shot by the caster, no bombardment), so "
              "its cast does not stop a moving caster and the mod no longer waits for the CASTER to stand still. Where "
              "the text above says the caster must be standing, that no longer applies. Every rule about the TARGET "
              "standing still is unchanged. Seen in game for Brass Orb and Gaze of Malice only. The same cast animation "
              "stops a caster who shoots a projectile (Amber Bow).")


def read_cards(path=RUN):
    cards = {}
    for line in open(path, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    return cards


def placed():
    return set(GA.placed_keys(open(LIVE, encoding="utf-8").read()))


def plan():
    gone = placed()
    wb = openpyxl.load_workbook(SRC, read_only=True)
    out = []
    for r, row in enumerate(wb["Abilities"].iter_rows(values_only=True, min_row=2), start=2):
        ks = [k.strip() for k in str(row[2]).split(";")]
        if any(k in gone for k in ks):
            assert row[19] == "IMPLEMENTED", row[2]
            out.append((r, 22, row[21], (row[21] or "").rstrip() + PLACED_ADD))
    wb.close()
    return out


def changed_cards():
    old, new = read_cards(OLD_RUN), read_cards(RUN)
    assert set(old) == set(new)
    return sorted(m for m in new if new[m] != old[m])


def family_counts():
    entries, _, _ = bd.mod_entries()
    fc = collections.defaultdict(lambda: [0, 0])
    for e in entries:
        fc[e["trigger"]][0] += 1
        fc[e["trigger"]][1] += len(e["keys"])
    return entries, fc


def main():
    edits = plan()
    assert len(edits) == 51, len(edits)
    assert not os.path.exists(DST), DST
    entries, fc = family_counts()
    assert len(entries) == 982
    cards = read_cards()
    moved = changed_cards()
    assert len(cards) == 982 and len(moved) == 39, (len(cards), len(moved))
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
        if m in moved:
            cs.cell(row=r, column=5).value = cards[m]
            done += 1
        else:
            assert m is None or cs.cell(row=r, column=5).value == cards[m], m   # no other card may have moved
    assert done == 39, done
    nm = wb["Numbers"]
    assert "v85 - ROUND 219" in str(nm.cell(row=7, column=1).value)
    nm.cell(row=7, column=1).value = (
        "Date: 2026-11-28     Rule in force since: 2026-10-18     Inventory: 1,802 active abilities     "
        "(v86 - ROUND 220: 51 placed effects no longer wait for their caster to stand still. 1,035 rows / 1,035 keys "
        "implemented, 80 not implemented among the included (all decided by the user), 0 open. The mod: 982 entries / "
        "1,035 keys / 141 trigger families, all 141 in use.)")
    for r in range(44, 185):
        fam = nm.cell(row=r, column=2).value
        if fam is not None:
            assert [nm.cell(row=r, column=3).value, nm.cell(row=r, column=4).value] == fc[fam], fam
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v85")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v86 (2026-11-28)"
    base = d.max_row + 2
    sec = [("83. ROUND 220 - A PLACED EFFECT DOES NOT STOP ITS CASTER (v86)", None),
           ("FIELD", "The user cast Brass Orb by hand with a Warlock Master (2026-11-28): the unit kept walking through the "
            "cast. Brass Orb has the same cast-animation entry as Amber Bow, which stopped its caster. So the animation "
            "does not decide it, as round 168 assumed. In every case seen in battle the caster stopped when he shot a "
            "projectile (Volley of High Arrows, Soporific Breath, Amber Bow) and did not when the effect was placed at "
            "the target or had no animation (Brass Orb, Gaze of Malice, Book of Hoeth)."),
           ("RULE", "User: 'Yes' to all placed ones. The stand-still set is GENERATED (tools\\gen_anim_keys.py): a key with "
            "a cast animation stays in it unless its effect is a vortex with neither a projectile nor a bombardment. 51 "
            "keys left the set, 183 stay. Bombardments and the other animated kinds wait as before, they have not been "
            "seen."),
           ("MACHINERY", "Not roster changes: the mod no longer runs an ability's check while it knows the cast cannot go "
            "out (its recharge or wind-up is running, or the game refused it), and a target's blast numbers are worked "
            "out once per map.")]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-28"
    ch.cell(row=r, column=2).value = "v86"
    ch.cell(row=r, column=3).value = (
        "ROUND 220. 51 rows: the PLACED sentence (the caster no longer has to stand still). 39 cards. No family or status "
        "change. SHIPPED: installed pack md5 %s. Harness 218 full suite %s checks / 0 failures."
        % (os.environ.get("WH3_PACK_MD5", "PENDING"), os.environ.get("WH3_CHECKS", "PENDING")))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-28. xlsx v86 supersedes v85. v1-v85 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "edits", len(edits), "cards", done)


if __name__ == "__main__":
    main()
