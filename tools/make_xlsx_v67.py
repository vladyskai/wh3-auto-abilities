#!/usr/bin/env python3
"""Build WH3_abilities_master_v67_2026-11-20.xlsx from v66 - round 184: the rule-shut review, rows 10-19 (user
2026-11-20: "Up to #19 ruled"; rulings from the Claude Docs review, rev 83).

(1) Abilities: 10 rows NOT IMPLEMENTED -> IMPLEMENTED: Flock of Doom x3, Sword of Daith, Zefet-nebtar on
    enemy_area_drain; Ring of Corin, Warpstorm Scroll on enemy_single_drain; Soul Stealer x2 on NEW enemy_area_drain_hurt;
    Raging Tornado on NEW enemy_ground_melee_cluster.
(2) Numbers: rows 13-14 (998 -> 1,008 implemented, 125 -> 115 not implemented), row 16, the carrier table re-derived;
    the trigger table re-counted with the 2 new families appended (136 -> 138 rows): 955 entries / 1,008 keys.
(3) Cards: from the harness-183 run. (4) Definitions: title v67, section 64. Changelog: a v67 row.
v1-v66 are never opened for writing.
"""
import collections
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402
import gamedata_paths as GP  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v66_2026-11-20.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v67_2026-11-20.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_ruleshut2_harness183"
RUN = REL + r"\h183_run1.txt"
CARDS_TSV = REL + r"\cards_round184.tsv"
NEW_FAMILIES = ["enemy_area_drain_hurt", "enemy_ground_melee_cluster"]
R184 = " ROUND 184 (the rule-shut review rows 10-19; user rulings 2026-11-20 in the Claude Docs review)."
AD = ("enemy_area_drain: not routing; the caster standing still for an animated cast; the visible enemy infantry within "
      "70 m (70%% of the game's 100 m) with at least the ability's own model count left (the GENERATED AREA table: %d) "
      "and the highest live value per soldier; the enemy may be moving; no clearance (the effect hits enemies only); %s; "
      "review row %d, ruling %s.")
SD = ("enemy_single_drain: not routing; the caster standing still for an animated cast; the most valuable visible "
      "single-entity enemy (Lord, Hero or monster) within %d m (70%% of the game's %d m)%s; %s; review row %d, ruling %s.")
T = {
    "wh3_dlc27_spell_bound_runecaller_flock_of_doom": ("enemy_area_drain", AD % (
        25, "5 damage a second to up to 25 models in a 35 m area for 6 s; wind-up 1 s; 3 uses, charge hold 60 s", 10,
        "\"Recommended\" = A2 (the enemy need not stand still: the shipped drain never checks it)")),
    "wh3_main_spell_bound_flock_of_doom": ("enemy_area_drain", AD % (
        25, "5 damage a second to up to 25 models in a 35 m area for 6 s; 2 uses, charge hold 60 s", 11,
        "\"Recommended\" = A2")),
    "wh_dlc08_spell_bound_flock_of_doom": ("enemy_area_drain", AD % (
        25, "5 damage a second to up to 25 models in a 35 m area for 6 s; 4 uses, charge hold 60 s", 12,
        "\"Recommended\" = A2")),
    "wh_dlc05_weapon_abilities_daiths_sword": ("enemy_area_drain", AD % (
        25, "5 damage a second to up to 25 models and armour -30 in a 35 m area for 17 s; 2 uses, charge hold 120 s", 13,
        "\"Recommended\" = A")),
    "wh3_dlc29_item_abilities_zefet_nebtar_the_mortis_blade": ("enemy_area_drain", AD % (
        25, "50 damage once to up to 25 models within 15 m, turned into healing; a 9 m knockback that also pushes our "
        "units (no damage); wind-up 1.5 s; 3 uses, charge hold 120 s", 14,
        "\"Recommended\" = A, no clearance (thread: 'if not damage, then no need for clearance check')")),
    "wh2_main_spell_bound_ring_of_corin": ("enemy_single_drain", SD % (
        140, 200, "", "67 damage a second to ONE model for 22 s; 2 uses, charge hold 90 s", 15, "\"Recommended\" = A")),
    "wh2_main_item_abilities_warpstorm_scroll": ("enemy_single_drain", SD % (
        70, 100, ", FLYING only (target class flying: is_currently_flying() exactly true; the game refuses ground units)",
        "67 damage a second to one model and speed x0.55 for 29 s; 1 use", 18, "\"Recommended\" = A")),
    "wh2_dlc10_spell_bound_soul_stealer_ror": ("enemy_area_drain_hurt", (
        "enemy_area_drain_hurt: the enemy_area_drain rule (the AREA table: 1 model a tick) while the caster is at or "
        "below 75% health (FOURTH.DRAIN_HURT_PCT), so its own heal (0.8% a second for 12 s) lands in full; 75 damage a "
        "second to ONE model in a 35 m area; 1 use; review row 16, ruling \"B\" with the 75% gate.")),
    "wh3_dlc27_spell_bound_soul_stealer": ("enemy_area_drain_hurt", (
        "enemy_area_drain_hurt: as row 16 (the RoR key); 1 use; review row 17, ruling \"same as #16\".")),
    "wh3_dlc29_unit_abilities_raging_tornado": ("enemy_ground_melee_cluster", (
        "enemy_ground_melee_cluster: not routing; the caster standing still (an animated 5 s cast); the visible enemy in "
        "melee within 70 m (70% of 100 m) with the most enemy value in melee within 24 m of it (FOURTH.cluster_pick); "
        "placed on the ground under it (the game allows ground only: enemy_ground_keys); pre-cast re-check: that enemy "
        "still in melee; no clearance (the damage hits enemies only); 32 s in 4 steps, 2/4/6/8 damage a second to up to "
        "25 models, speed x0.9 / 0.75 / 0.6 / 0.4; 3 uses, charge hold 120 s; review row 19, ruling \"Recommended\" = A.")),
}
FAMILY = {k: v[0] for k, v in T.items()}


import make_xlsx_v52 as M52  # noqa: E402   (the round-168 note for the stand-still families' non-animated keys)
MOVING = set(T) & M52.moving_keys()[0]   # Ring of Corin, Warpstorm Scroll, Sword of Daith: no cast animation


def text_of(k):
    return T[k][1] + R184 + ((" " + M52.NOTE) if k in MOVING else "")


def main():
    entries, _, _ = bd.mod_entries()
    assert len(entries) == 955
    keys_of = {}
    for e in entries:
        for k in e["keys"]:
            keys_of[k] = e["trigger"]
    assert len(keys_of) == 1008
    for k, fam in FAMILY.items():
        assert keys_of.get(k) == fam, (k, fam, keys_of.get(k))
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    assert len(cards) == 955 and set(cards) == {e["marker"] for e in entries}, len(cards)
    with open(CARDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("marker\tability\tfamily\tkeys\tcard\n")
        for e in entries:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (e["marker"], e["name"], e["trigger"], ";".join(e["keys"]), cards[e["marker"]]))
    fam_e, fam_k = collections.Counter(), collections.Counter()
    for e in entries:
        fam_e[e["trigger"]] += 1
        fam_k[e["trigger"]] += len(e["keys"])
    assert len(fam_e) == 138
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    done = set()
    for r in range(2, ws.max_row + 1):
        k = str(ws.cell(row=r, column=3).value).split(";")[0].strip()
        if k in T:
            assert str(ws.cell(row=r, column=18).value) == "IN-WHEEL" and ws.cell(row=r, column=20).value == "NOT IMPLEMENTED", k
            ws.cell(row=r, column=20).value = "IMPLEMENTED"
            ws.cell(row=r, column=21).value = FAMILY[k]
            ws.cell(row=r, column=22).value = text_of(k)
            done.add(k)
    assert done == set(T), set(T) - done
    rows = [(str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=20).value),
             [x.strip() for x in str(ws.cell(row=r, column=3).value).split(";")]) for r in range(2, ws.max_row + 1)]
    inc = [x for x in rows if x[0] == "IN-WHEEL"]
    impl = [x for x in inc if x[1] == "IMPLEMENTED"]
    assert (len(rows), len(inc), len(impl)) == (1800, 1123, 1008), (len(rows), len(inc), len(impl))
    assert set(k for x in impl for k in x[2]) == set(keys_of)
    n = wb["Numbers"]
    assert (n.cell(row=13, column=3).value, n.cell(row=14, column=3).value) == (998, 125)
    for r, v in ((13, 1008), (14, 115), (16, 1008)):
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
    assert sum(n.cell(row=r, column=4).value for r in range(20, 28)) == 1008
    n.cell(row=28, column=4).value = 1008
    n.cell(row=40, column=1).value = (
        "Reconciliation (v67): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 1,008 + not "
        "implemented 115 = 1,123. The carrier table and row 16 are re-derived from the rows (since v66).")
    assert n.cell(row=180, column=2).value == "TOTAL (136 families)"
    n.insert_rows(180, amount=len(NEW_FAMILIES))
    for i, fam in enumerate(NEW_FAMILIES):
        n.cell(row=180 + i, column=2).value = fam
    for r in range(44, 182):
        n.cell(row=r, column=1).value = r - 43
        fam = n.cell(row=r, column=2).value
        n.cell(row=r, column=3).value = fam_e.get(fam, 0)
        n.cell(row=r, column=4).value = fam_k.get(fam, 0)
    assert all(n.cell(row=r, column=3).value > 0 for r in range(44, 182)), "an empty family is listed"
    assert n.cell(row=182, column=2).value == "TOTAL (136 families)"
    n.cell(row=182, column=2).value = "TOTAL (138 families)"
    n.cell(row=182, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 182))
    n.cell(row=182, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 182))
    assert (n.cell(row=182, column=3).value, n.cell(row=182, column=4).value) == (955, 1008)
    assert n.cell(row=184, column=1).value == "Bombardment set (COMPLETE - round 108)"
    n.cell(row=42, column=1).value = (
        "Trigger families after round 184 - re-counted from the mod's own ABILITIES table: 138 families / 955 entries / "
        "1,008 keys. Round 184: the rule-shut review rows 10-19 (enemy_area_drain_hurt, enemy_ground_melee_cluster).")
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-20     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v67 - ROUND 184: the rule-shut review rows 10-19. 1,008 rows / 1,008 keys implemented; 115 not implemented among "
        "the included (50 skipped by the user). The mod: 955 entries / 1,008 keys / 138 trigger families.)")
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 184)"
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v66")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v67 (2026-11-20)"
    base = d.max_row + 2
    sec = [("64. ROUND 184 - THE RULE-SHUT REVIEW, ROWS 10-19 (v67)", None),
           ("NEW FAMILIES", "enemy_area_drain_hurt (Soul Stealer x2: the area drain at 75% health or less, so the "
            "self-heal lands in full); enemy_ground_melee_cluster (Raging Tornado: on the ground under the thickest "
            "melee of enemies, 24 m cluster)."),
           ("THE AREA DRAIN AND MOVING ENEMIES", "enemy_area_drain never required the ENEMY to stand still: its "
            "standing-still gate is the caster's, for animated casts only. Rows 10-12's 'A2' is the shipped rule.")]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-20"
    ch.cell(row=r, column=2).value = "v67"
    ch.cell(row=r, column=3).value = (
        "ROUND 184. The rule-shut review rows 10-19: Flock of Doom x3, Sword of Daith, Zefet-nebtar, Ring of Corin, Soul "
        "Stealer x2, Warpstorm Scroll, Raging Tornado. SHIPPED: installed pack md5 %s; harness 183 full suite 7,762 "
        "checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-20; xlsx v67 supersedes v66; v1-v66 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
