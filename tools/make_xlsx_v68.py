#!/usr/bin/env python3
"""Build WH3_abilities_master_v68_2026-11-20.xlsx from v67 - round 185: the rule-shut review, rows 20-64 (user
2026-11-20: "Review ended, implement pls"; rulings from the Claude Docs review, rev 127).

(1) Abilities: 33 rows NOT IMPLEMENTED -> IMPLEMENTED (round185_rows.ROWS); 12 rows NOT IMPLEMENTED -> SKIPPED (user
    decision): the 7 stealth rows ("Recommended" = keep shut) and the 5 mutually exclusive rows (parked with the stances).
(2) Numbers: rows 13-14 (1,008 -> 1,041 implemented, 115 -> 82 not implemented), row 16, the carrier table re-derived;
    the trigger table re-counted with the 2 new families appended (138 -> 140 rows): 988 entries / 1,041 keys.
(3) Cards: from the harness-184 run. (4) Definitions: title v68, section 65. Changelog: a v68 row.
v1-v67 are never opened for writing.
"""
import collections
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402
import gamedata_paths as GP  # noqa: E402
import make_xlsx_v52 as M52  # noqa: E402
import round185_rows as RR  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v67_2026-11-20.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v68_2026-11-20.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_ruleshut3_harness184"
RUN = REL + r"\h184_run1.txt"
CARDS_TSV = REL + r"\cards_round185.tsv"
NEW_FAMILIES = ["aura_charge_only", "ally_offering"]
R185 = " ROUND 185 (the rule-shut review rows 20-64; user rulings 2026-11-20 in the Claude Docs review)."
RULE = {
    "melee_unwavering": "melee_unwavering: not routing; in melee and not wavering; cast on self (a self-centred blast that "
                        "cannot hurt our units: 'Like Bloodstorm', round 159)",
    "melee_clear": "melee_clear: not routing; in melee and not wavering, and none of our OTHER units within the blast "
                   "(GENERATED VORTEX table) + 10 m of the caster; cast on self (the blast hurts our units too)",
    "melee_clear_block": "melee_clear_block: melee_clear AND at least 60 enemy soldiers inside the 25 m blast (as Land "
                         "Mine); cast on self (the caster also takes 600 damage)",
    "last_stand_clear": "last_stand_clear: not routing; at or below 10% health (LAST_STAND_PCT) in melee, none of our other "
                        "units within the blast + 10 m; cast on self",
    "aura_charge_only": "aura_charge_only: not routing; the caster charging (the charge window), or one of our units within "
                        "70% of the aura charging; cast on self (speed x1.25, charge speed x1.25, charge bonus x1.2 or "
                        "+12; no morale, so no wavering arm)",
    "self_or_ally_charge": "self_or_ally_charge: itself charging, else the nearest charging ally within 140 m (70% of 200), "
                           "cast on it (as Red Fury)",
    "charge_only": "charge_only: the caster charging (the charge window); cast on self",
    "enemy_blob_vortex": "enemy_blob_vortex: the caster standing still; the visible enemy within 140 m (70% of 200), not "
                         "flying, where the 8 m blast destroys the most value; none of ours within 18 m (blast + 10 m)",
    "ally_melee_risk": "ally_melee_risk: the nearest ally within 140 m (70% of 200) in melee that wavers or is badly hurt, "
                       "cast on it",
    "enemy_ground_melee_cluster": "enemy_ground_melee_cluster: the caster standing still; the visible enemy in melee, not "
                                  "flying, within 140 m (70% of 200) with the most enemy value in melee within 24 m of it; "
                                  "placed on the ground under it (enemy_ground_keys)",
    "enemy_melee_near": "enemy_melee_near: the caster in melee, or a visible enemy within 38 m (70% of the 55 m aura) in "
                        "melee; cast on self",
    "self_recharging": "self_recharging: while another of the caster's abilities recharges; cast on self",
    "enemy_fast_near_ally": "enemy_fast_near_ally: a visible enemy running at 5 m/s or more within 40 m of our units, at any "
                            "range (the game's range is -1: unbounded); placed on the ground under it (enemy_ground_keys)",
    "ally_offering": "ally_offering: the most valuable ally in melee within 70 m (70% of 100), no missile unit, at least "
                     "30 soldiers (OFFERING_MIN_MEN; the offering kills 3), never a Lord, Hero or large unit (the game's "
                     "rule); cast on it",
    "slow_aura": "slow_aura: the caster in melee, or a fast enemy entering 70% of the 35 m aura; cast on self (enemies "
                 "cannot move for 13 s)",
    "self_last_stand": "self_last_stand: at or below 10% health in melee or under missile fire (as Hag's Denial); cast on "
                       "self (invulnerable, melee attack x0, 13 s)",
}
RULING = {r[0]: "Recommended" for r in RR.ROWS}
RULING.update({37: "B", 38: "B", 39: "B", 40: "B", 55: "Other: 'Last stand' (option B)", 57: "A"})
CLOSED = {
    "wh2_main_item_abilities_armour_of_the_stars": "stealth",
    "wh2_main_character_abilities_concealment_bombs": "stealth",
    "wh2_main_unit_abilities_concealment_bombs": "stealth",
    "wh3_main_character_abilities_from_the_shadows": "stealth",
    "wh3_main_lord_abilities_hidden_in_time": "stealth",
    "wh_pro04_unit_abilities_loecs_shroud": "stealth",
    "wh2_dlc15_unit_abilities_mimic_loecs_shroud": "stealth",
    "wh3_dlc24_unit_abilities_bastion_of_the_great_cities": "stance",
    "wh3_dlc24_unit_abilities_disdain_of_the_dragon_emperor": "stance",
    "wh3_dlc24_unit_abilities_fury_of_the_falling_blade": "stance",
    "wh3_dlc20_lord_abilities_harbinger_of_pestilence": "stance",
    "wh3_dlc20_lord_abilities_healing_elixirs": "stance",
}
WHY = {"stealth": "rule-shut review rows 42-48, 'Recommended' = keep shut: a hide is the player's call (no read shows "
                  "whether the enemy sees our unit)",
       "stance": "rule-shut review rows 49-53, 'Recommended' = parked with the stances: it stays on until switched and "
                 "excludes its siblings (stances are never automated for now, user 2026-11-01)"}
T = {r[4]: (r[3], RULE[r[3]], r[0]) for r in RR.ROWS}
FAMILY = {k: v[0] for k, v in T.items()}
MOVING = set(T) & M52.moving_keys()[0]


def text_of(k):
    fam, rule, row = T[k]
    return ("%s; review row %d, ruling \"%s\".%s" % (rule, row, RULING[row], R185)
            + ((" " + M52.NOTE) if k in MOVING else ""))


def closed_reason(k):
    return "skipped (user decision 2026-11-20: %s)" % WHY[CLOSED[k]]


def main():
    entries, _, _ = bd.mod_entries()
    assert len(entries) == 988
    keys_of = {}
    for e in entries:
        for k in e["keys"]:
            keys_of[k] = e["trigger"]
    assert len(keys_of) == 1041
    for k, fam in FAMILY.items():
        assert keys_of.get(k) == fam, (k, fam, keys_of.get(k))
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    assert len(cards) == 988 and set(cards) == {e["marker"] for e in entries}, len(cards)
    with open(CARDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("marker\tability\tfamily\tkeys\tcard\n")
        for e in entries:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (e["marker"], e["name"], e["trigger"], ";".join(e["keys"]), cards[e["marker"]]))
    fam_e, fam_k = collections.Counter(), collections.Counter()
    for e in entries:
        fam_e[e["trigger"]] += 1
        fam_k[e["trigger"]] += len(e["keys"])
    assert len(fam_e) == 140
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    done, closed = set(), set()
    for r in range(2, ws.max_row + 1):
        k = str(ws.cell(row=r, column=3).value).split(";")[0].strip()
        if k in T or k in CLOSED:
            assert str(ws.cell(row=r, column=18).value) == "IN-WHEEL" and ws.cell(row=r, column=20).value == "NOT IMPLEMENTED", k
        if k in T:
            ws.cell(row=r, column=20).value = "IMPLEMENTED"
            ws.cell(row=r, column=21).value = FAMILY[k]
            ws.cell(row=r, column=22).value = text_of(k)
            done.add(k)
        elif k in CLOSED:
            ws.cell(row=r, column=19).value = closed_reason(k)
            ws.cell(row=r, column=20).value = "SKIPPED (user decision)"
            ws.cell(row=r, column=21).value = "-"
            ws.cell(row=r, column=22).value = ("No automation - SKIPPED BY THE USER'S DECISION of 2026-11-20 (%s)."
                                               % WHY[CLOSED[k]])
            closed.add(k)
    assert done == set(T) and closed == set(CLOSED), (set(T) - done, set(CLOSED) - closed)
    rows = [(str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=20).value),
             [x.strip() for x in str(ws.cell(row=r, column=3).value).split(";")]) for r in range(2, ws.max_row + 1)]
    inc = [x for x in rows if x[0] == "IN-WHEEL"]
    impl = [x for x in inc if x[1] == "IMPLEMENTED"]
    assert (len(rows), len(inc), len(impl)) == (1800, 1123, 1041), (len(rows), len(inc), len(impl))
    assert sum(1 for x in inc if x[1] == "SKIPPED (user decision)") == 62
    assert set(k for x in impl for k in x[2]) == set(keys_of)
    n = wb["Numbers"]
    assert (n.cell(row=13, column=3).value, n.cell(row=14, column=3).value) == (1008, 115)
    for r, v in ((13, 1041), (14, 82), (16, 1041)):
        n.cell(row=r, column=3).value = v
        n.cell(row=r, column=4).value = v / 1800
        n.cell(row=r, column=5).value = v / 1123
    src_type = {}
    with open(GP.UNIT_ABILITIES, encoding="utf-8", errors="replace") as f:
        hdr = f.readline().rstrip("\n").split("\t")
        si = hdr.index("source_type")
        for line in f:
            if line.startswith("#"):
                continue
            c = line.rstrip("\n").split("\t")
            if len(c) > si:
                src_type[c[0]] = c[si]
    car_inc, car_impl = collections.Counter(), collections.Counter()
    for x in inc:
        fam = src_type[x[2][0]]
        car_inc[fam] += 1
        if x[1] == "IMPLEMENTED":
            car_impl[fam] += 1
    for r in range(20, 28):
        fam = n.cell(row=r, column=2).value
        assert n.cell(row=r, column=3).value == car_inc[fam], fam
        n.cell(row=r, column=4).value = car_impl[fam]
        n.cell(row=r, column=5).value = car_impl[fam] / car_inc[fam]
    assert sum(n.cell(row=r, column=4).value for r in range(20, 28)) == 1041
    n.cell(row=28, column=4).value = 1041
    n.cell(row=40, column=1).value = (
        "Reconciliation (v68): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 1,041 + not "
        "implemented 82 (62 skipped by the user) = 1,123. The carrier table and row 16 are re-derived from the rows.")
    assert n.cell(row=182, column=2).value == "TOTAL (138 families)"
    n.insert_rows(182, amount=len(NEW_FAMILIES))
    for i, fam in enumerate(NEW_FAMILIES):
        n.cell(row=182 + i, column=2).value = fam
    for r in range(44, 184):
        n.cell(row=r, column=1).value = r - 43
        fam = n.cell(row=r, column=2).value
        n.cell(row=r, column=3).value = fam_e.get(fam, 0)
        n.cell(row=r, column=4).value = fam_k.get(fam, 0)
    assert all(n.cell(row=r, column=3).value > 0 for r in range(44, 184)), "an empty family is listed"
    assert n.cell(row=184, column=2).value == "TOTAL (138 families)"
    n.cell(row=184, column=2).value = "TOTAL (140 families)"
    n.cell(row=184, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 184))
    n.cell(row=184, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 184))
    assert (n.cell(row=184, column=3).value, n.cell(row=184, column=4).value) == (988, 1041)
    assert n.cell(row=186, column=1).value == "Bombardment set (COMPLETE - round 108)"
    n.cell(row=42, column=1).value = (
        "Trigger families after round 185 - re-counted from the mod's own ABILITIES table: 140 families / 988 entries / "
        "1,041 keys. Round 185: the rule-shut review rows 20-64 (aura_charge_only, ally_offering).")
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-20     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v68 - ROUND 185: the rule-shut review rows 20-64. 1,041 rows / 1,041 keys implemented; 82 not implemented among "
        "the included (62 skipped by the user). The mod: 988 entries / 1,041 keys / 140 trigger families.)")
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 185)"
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v67")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v68 (2026-11-20)"
    base = d.max_row + 2
    sec = [("65. ROUND 185 - THE RULE-SHUT REVIEW, ROWS 20-64 (v68)", None),
           ("NEW FAMILIES", "aura_charge_only (Battle Howl x2, Silver Horn of Vengeance: the caster or an ally in the aura "
            "charging, no wavering arm); ally_offering (Offering to the Gods: the most valuable ally of 30+ men in melee)."),
           ("CLOSED", "The 7 stealth rows stay shut and the 5 mutually exclusive rows are parked with the stances (user "
            "2026-11-20, 'Recommended')."),
           ("BOMBARDMENT RADIUS", "gen_vortex_tables reads a self-centred bombardment too (the Master Rune of Immolation: "
            "6 m shells + 4 m spread = 10 m).")]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-20"
    ch.cell(row=r, column=2).value = "v68"
    ch.cell(row=r, column=3).value = (
        "ROUND 185. The rule-shut review rows 20-64: 33 abilities built, 12 closed by the user. SHIPPED: installed pack "
        "md5 %s; harness 184 full suite 7,831 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-20; xlsx v68 supersedes v67; v1-v67 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
