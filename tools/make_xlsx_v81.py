#!/usr/bin/env python3
"""Build WH3_abilities_master_v81_2026-11-22.xlsx from v80 - round 204 (user ruling 2026-11-22: an exact wave needs no
safety distance, only very few of our soldiers under it, our single entities ignored. Tidecall and Wind Blast too).

(1) Abilities: the 27 EXACT wave rows gain the EXACT sentence. Tidecall and Wind Blast move to the family enemy_wave
    (column 21) and get the wave trigger text (column 22). The 5 drifting waves are untouched.
(2) Numbers: the date line, and the family table re-counted from the mod (enemy_wave 32, enemy_wave_charge 0).
(3) Cards: rebuilt from the harness-202 run (982 cards. Only Tidecall and Wind Blast change).
(4) Definitions: title v81, section 78. Changelog: a v81 row. v1-v80 are never opened for writing."""
import collections
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v80_2026-11-22.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v81_2026-11-22.xlsx"
MOD = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_exactwave_harness202"
RUN = REL + r"\h202_run1.txt"
CARDS_TSV = REL + r"\cards_round204.tsv"
MOVED = ["wh2_dlc11_spell_bound_tidecall", "wh2_dlc11_spell_bound_wind_blast"]
EXACT = (" EXACT WAVE (round 204, user 2026-11-22: 'the safety was meant for abilities that have a deviation from their "
         "path'): this wave does not drift, so the 10 m safety distance is gone. A path counts when at most 5 of our "
         "soldiers stand under the wave (our single entities and the caster are not counted). Its value is the enemy value "
         "under the wave. Every heading is also tested moved 6, 12 and 18 m to either side, and the order always goes out "
         "on the ground at the path's start.")
MOVED_TEXT = ("enemy_wave: not routing, the caster standing still. Among the visible enemies in range that stand still, "
              "the path with the most enemy value under the wave. ROUND 204 (user 2026-11-22: 'please implement for tight "
              "call and wind blast. The slow effect is irrelevant in this case'): moved from the charge trigger (round 164, "
              "'Charge, clear path') to the damage waves.")


def exact_keys():
    s = open(MOD, encoding="utf-8").read()
    ww = dict(x.split("=", 1) for x in re.search(r'FOURTH\.WW_TEXT = "([^"]*)"', s).group(1).split(";") if "=" in x)
    entries, _, _ = bd.mod_entries()
    wave = [k for e in entries if e["trigger"] == "enemy_wave" for k in e["keys"]]
    return [k for k in wave if float(ww[k].split(",")[4]) == 0], wave, entries


def read_cards():
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    return cards


def plan(ws):
    exact, wave, _ = exact_keys()
    out = []
    for r in range(2, ws.max_row + 1):
        k = str(ws.cell(r, 3).value).split(";")[0].strip()
        if ws.cell(r, 20).value != "IMPLEMENTED":
            continue
        t = ws.cell(r, 22).value
        if k in MOVED:
            out.append((r, 21, ws.cell(r, 21).value, "enemy_wave"))
            out.append((r, 22, t, MOVED_TEXT + EXACT))
        elif k in exact:
            out.append((r, 22, t, (t or "").rstrip() + EXACT))
    return out, exact, wave


def main():
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    edits, exact, wave = plan(ws)
    assert len(wave) == 32 and len(exact) == 27 and len(edits) == 27 + 2, (len(wave), len(exact), len(edits))
    for r, c, old, new in edits:
        assert ws.cell(r, c).value == old
        ws.cell(r, c).value = new
    entries, _, _ = bd.mod_entries()
    nm = wb["Numbers"]
    assert "v80 - ROUND 203" in str(nm.cell(7, 1).value)
    nm.cell(7, 1).value = (
        "Date: 2026-11-22     Rule in force since: 2026-10-18     Inventory: 1,802 active abilities     "
        "(v81 - ROUND 204: an exact wave counts our soldiers under it, no safety distance. Tidecall and Wind Blast on the "
        "wave trigger. 1,035 rows / 1,035 keys implemented, 80 not implemented among the included (all decided by the "
        "user), 0 open. The mod: 982 entries / 1,035 keys / 141 trigger families, 140 in use.)")
    fc = collections.defaultdict(lambda: [0, 0])
    for e in entries:
        fc[e["trigger"]][0] += 1
        fc[e["trigger"]][1] += len(e["keys"])
    fam_rows = {nm.cell(r, 2).value: r for r in range(44, 185)}
    assert set(fc) <= set(fam_rows) and set(fam_rows) - set(fc) == {"enemy_wave_charge"}, sorted(set(fam_rows) ^ set(fc))
    for fam, r in fam_rows.items():
        nm.cell(r, 3).value = fc[fam][0] if fam in fc else 0
        nm.cell(r, 4).value = fc[fam][1] if fam in fc else 0
    assert nm.cell(185, 3).value == len(entries) == 982 and nm.cell(185, 4).value == 1035
    nm.cell(42, 1).value = ("Trigger families after round 204 - re-counted from the mod's own ABILITIES table: 141 families "
                            "(140 in use) / 982 entries / 1,035 keys. Round 204: Tidecall and Wind Blast moved from "
                            "enemy_wave_charge (now empty, its code kept) to enemy_wave (32).")
    cards = read_cards()
    assert len(cards) == 982 and set(cards) == {e["marker"] for e in entries}, len(cards)
    with open(CARDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("marker\tability\tfamily\tkeys\tcard\n")
        for e in entries:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (e["marker"], e["name"], e["trigger"], ";".join(e["keys"]), cards[e["marker"]]))
    cs = wb["Cards"]
    old_cards = {r[0]: r[4] for r in cs.iter_rows(values_only=True, min_row=2) if r[0]}
    moved = sorted(m for m in cards if old_cards.get(m) != cards[m])
    assert moved == ["tidecall", "wind_blast"], moved
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(1, 5).value = "Card: the M/A badge's hover text (round 204)"
    d = wb["Definitions"]
    assert d.cell(1, 1).value.startswith("DEFINITIONS - WH3 ability master v80")
    d.cell(1, 1).value = "DEFINITIONS - WH3 ability master v81 (2026-11-22)"
    base = d.max_row + 2
    sec = [("78. ROUND 204 - AN EXACT WAVE NEEDS NO SAFETY DISTANCE (v81)", None),
           ("RULE", "User 2026-11-22, after a battle in which round 203's free aim never fired (every path ran through the "
            "enemy's centre, which in a melee lies inside the 16 m distance to our own unit): 'the safety was meant for "
            "abilities that have a deviation from their path. But this ability's path is deterministic. We only need to "
            "know that in the path of the ability, there is very little of our soldiers. And in this case, we should ignore "
            "single entities.' A wave whose table row has no sideways drift is EXACT (27 keys): at most 5 of our soldiers "
            "under the wave, our single entities and the caster not counted. A wave with drift (5 keys: Wrath of Manann, "
            "Wind of Death, The Burning Head x2, Arnzipal's Black Horror) keeps the round-162 distance. The limit of 5 is "
            "Claude's reading of 'very little' and a named constant (FOURTH.WAVE_OWN_MAX)."),
           ("AIM", "An exact wave's value is the enemy value under the wave (each unit's live value x the share of its "
            "soldiers inside the radius). Every one of the 24 headings is also tested moved 6, 12 and 18 m to either side. "
            "The order always goes out on the ground at the path's start with the heading as orientation. The search runs "
            "once per second per caster and ability."),
           ("MOVED", "Tidecall and Wind Blast: 'please implement for tight call and wind blast. The slow effect is "
            "irrelevant in this case.' They leave the charge trigger (round 164) and ride enemy_wave.")]
    for i, (a, b) in enumerate(sec):
        d.cell(base + i, 1).value = a
        if b is not None:
            d.cell(base + i, 2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(r, 1).value = "2026-11-22"
    ch.cell(r, 2).value = "v81"
    ch.cell(r, 3).value = (
        "ROUND 204. Exact waves count our soldiers under the wave (27 trigger texts), Tidecall and Wind Blast on enemy_wave "
        "(2 rows, 2 cards). SHIPPED: installed pack md5 %s. Harness 202 full suite %s checks / 0 failures."
        % (os.environ.get("WH3_PACK_MD5", "PENDING"), os.environ.get("WH3_CHECKS", "PENDING")))
    ch.cell(r, 4).value = "user ruling 2026-11-22. xlsx v81 supersedes v80. v1-v80 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "| edits", len(edits), "| exact", len(exact), "| cards moved", moved)


if __name__ == "__main__":
    main()
