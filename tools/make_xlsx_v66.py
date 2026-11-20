#!/usr/bin/env python3
"""Build WH3_abilities_master_v66_2026-11-20.xlsx from v65 - round 183: the rule-shut review, rows 1-9 (user
2026-11-20: "You may start implementing #1-9 for now"; rulings from the Claude Docs review, rev 44).

(1) Abilities: 9 rows NOT IMPLEMENTED -> IMPLEMENTED (the "own-troop damage" rule was wrong for them: every damage phase
    targets enemies only): 4 on enemy_melee_near, 2 on melee_health75, 3 on melee_unwavering.
(2) Numbers: rows 13-14 (implemented 989 -> 998, not implemented 134 -> 125); row 16 and the carrier table re-derived
    from the rows (they had stayed at 1,003 since an earlier version: corrected here); row 40's reconciliation text;
    the trigger table re-counted (136 families, 945 entries / 998 keys).
(3) Cards: from the harness-182 run. (4) Definitions: title v66, section 63. Changelog: a v66 row.
v1-v65 are never opened for writing.
"""
import collections
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402
import gamedata_paths as GP  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v65_2026-11-20.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v66_2026-11-20.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_ruleshut1_harness182"
RUN = REL + r"\h182_run1.txt"
CARDS_TSV = REL + r"\cards_round183.tsv"
R183 = " ROUND 183 (the rule-shut review rows 1-9; user rulings 2026-11-20 in the Claude Docs review)."
NEAR = ("enemy_melee_near: not routing; the caster in melee, or a visible enemy within 24 m (70%% of the game's 35 m aura, "
        "unit_distance) in melee; cast on self (enemies within 35 m: %s); review row %d, ruling \"Recommended\" (B). The "
        "2026-10-09 'own-troop damage' rule was wrong: every damage phase targets enemies only.")
H75 = ("melee_health75: not routing; in melee at or below 75%% health; cast on self (%s); review row %d, ruling %s.")
MU = ("melee_unwavering: not routing; in melee and not wavering; cast on self (%s); review row %d, ruling %s.")
T = {
    "wh3_twa08_unit_abilities_defiling_deluge": ("enemy_melee_near", NEAR % (
        "5 damage a second to up to 25 models for 6 s; the caster heals 0.8% a second; 2 uses, charge hold 120 s", 1)),
    "wh3_dlc26_lord_abilities_murderous_exhortations": ("enemy_melee_near", NEAR % (
        "5 damage a second to up to 10 models and morale -8 for 20 s; 3 uses, charge hold 120 s", 2)),
    "wh2_main_item_abilities_rod_of_corruption": ("enemy_melee_near", NEAR % (
        "10 damage a second to up to 25 models for 11 s; 3 uses, charge hold 120 s", 3)),
    "wh2_dlc14_unit_abilities_wail_of_malice": ("enemy_melee_near", NEAR % (
        "10 damage a second to up to 18 models for 7 s; 2 uses, charge hold 90 s", 4)),
    "wh3_dlc29_item_abilities_plaguereaper": ("melee_health75", H75 % (
        "enemies within 15 m take 12 damage a second, up to 4 models, for 25 s; the caster heals 0.8% a second, 20% in all; "
        "2 uses, charge hold 120 s", 5, "\"B\" (thread: 'the heal is considerable, we shouldn't waste it')")),
    "wh2_dlc14_lord_abilities_reaper_of_souls": ("melee_health75", H75 % (
        "enemies within 35 m: 96 damage a second to ONE model for 9 s; the caster heals 0.8% a second", 6,
        "\"Recommended\" = C (thread: 'just in melee and less that 75% health')")),
    "wh3_main_weapon_abilities_shard_blade": ("melee_unwavering", MU % (
        "enemies within 15 m: 67 damage a second to ONE model and speed x0.55 for 15 s; 2 uses, charge hold 120 s", 7, "\"A\"")),
    "wh2_main_weapon_abilities_web_of_shadows": ("melee_unwavering", MU % (
        "enemies within 35 m: 67 damage a second to ONE model and speed x0.75 for 17 s; 1 use", 8, "\"A\"")),
    "wh2_dlc14_unit_abilities_warp_quake": ("melee_unwavering", MU % (
        "enemies within 35 m, not flying: 5 damage every 0.5 s to up to 18 models and speed x0.75 for 17 s", 9,
        "\"Other\": 'Melee_unwavering'")),
}
FAMILY = {k: v[0] for k, v in T.items()}


def text_of(k):
    return T[k][1] + R183


def main():
    entries, _, _ = bd.mod_entries()
    assert len(entries) == 945
    keys_of = {}
    for e in entries:
        for k in e["keys"]:
            keys_of[k] = e["trigger"]
    assert len(keys_of) == 998
    for k, fam in FAMILY.items():
        assert keys_of.get(k) == fam, (k, fam, keys_of.get(k))
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    assert len(cards) == 945 and set(cards) == {e["marker"] for e in entries}, len(cards)
    with open(CARDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("marker\tability\tfamily\tkeys\tcard\n")
        for e in entries:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (e["marker"], e["name"], e["trigger"], ";".join(e["keys"]), cards[e["marker"]]))
    fam_e, fam_k = collections.Counter(), collections.Counter()
    for e in entries:
        fam_e[e["trigger"]] += 1
        fam_k[e["trigger"]] += len(e["keys"])
    assert len(fam_e) == 136
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
    rows = [(str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=19).value or ""),
             str(ws.cell(row=r, column=20).value), [x.strip() for x in str(ws.cell(row=r, column=3).value).split(";")])
            for r in range(2, ws.max_row + 1)]
    inc = [x for x in rows if x[0] == "IN-WHEEL"]
    impl = [x for x in inc if x[2] == "IMPLEMENTED"]
    assert (len(rows), len(inc), len(impl)) == (1800, 1123, 998), (len(rows), len(inc), len(impl))
    assert set(k for x in impl for k in x[3]) == set(keys_of)
    n = wb["Numbers"]
    assert (n.cell(row=13, column=3).value, n.cell(row=14, column=3).value) == (989, 134)
    n.cell(row=13, column=3).value = 998
    n.cell(row=13, column=4).value = 998 / 1800
    n.cell(row=13, column=5).value = 998 / 1123
    n.cell(row=14, column=3).value = 125
    n.cell(row=14, column=4).value = 125 / 1800
    n.cell(row=14, column=5).value = 125 / 1123
    assert n.cell(row=15, column=3).value == 0
    n.cell(row=16, column=3).value = 998
    n.cell(row=16, column=4).value = 998 / 1800
    n.cell(row=16, column=5).value = 998 / 1123
    # the carrier table: implemented per carrier family (unit_abilities.source_type of the row's first key)
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
        fam = src_type[x[3][0]]
        car_inc[fam] += 1
        if x[2] == "IMPLEMENTED":
            car_impl[fam] += 1
    for r in range(20, 28):
        fam = n.cell(row=r, column=2).value
        assert n.cell(row=r, column=3).value == car_inc[fam], (fam, n.cell(row=r, column=3).value, car_inc[fam])
        n.cell(row=r, column=4).value = car_impl[fam]
        n.cell(row=r, column=5).value = car_impl[fam] / car_inc[fam]
    assert sum(n.cell(row=r, column=4).value for r in range(20, 28)) == 998
    assert str(n.cell(row=28, column=2).value).startswith("Total included") and n.cell(row=28, column=3).value == 1123
    n.cell(row=28, column=4).value = 998
    n.cell(row=40, column=1).value = (
        "Reconciliation (v66): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 998 + not "
        "implemented 125 = 1,123. The carrier table and row 16 re-derived from the rows in v66 (they had stayed at 1,003).")
    assert n.cell(row=180, column=2).value == "TOTAL (136 families)"
    for r in range(44, 180):
        fam = n.cell(row=r, column=2).value
        n.cell(row=r, column=3).value = fam_e.get(fam, 0)
        n.cell(row=r, column=4).value = fam_k.get(fam, 0)
    assert all(n.cell(row=r, column=3).value > 0 for r in range(44, 180))
    n.cell(row=180, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 180))
    n.cell(row=180, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 180))
    assert (n.cell(row=180, column=3).value, n.cell(row=180, column=4).value) == (945, 998)
    assert n.cell(row=182, column=1).value == "Bombardment set (COMPLETE - round 108)"
    n.cell(row=42, column=1).value = (
        "Trigger families after round 183 - re-counted from the mod's own ABILITIES table: 136 families / 945 entries / "
        "998 keys. Round 183: the rule-shut review rows 1-9 (9 new entries on existing families).")
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-20     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v66 - ROUND 183: the rule-shut review rows 1-9. 998 rows / 998 keys implemented; 125 not implemented among the "
        "included (50 skipped by the user). The mod: 945 entries / 998 keys / 136 trigger families.)")
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 183)"
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v65")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v66 (2026-11-20)"
    base = d.max_row + 2
    sec = [("63. ROUND 183 - THE RULE-SHUT REVIEW, ROWS 1-9 (v66)", None),
           ("THE FINDING", "The 2026-10-09 'own-troop damage' rule was wrong for all 19 of its rows: every damage phase "
            "targets enemies only (phase_junc). Rows 1-9 are built; rows 10-19 wait for the user's rulings."),
           ("THE RULINGS", "Rows 1-4 enemy_melee_near (35 m aura, 24 m bound); rows 5-6 melee_health75 (the self-heal is "
            "not wasted); rows 7-9 melee_unwavering. Read from the Claude Docs review 'Rule-shut abilities review'.")]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-20"
    ch.cell(row=r, column=2).value = "v66"
    ch.cell(row=r, column=3).value = (
        "ROUND 183. The rule-shut review rows 1-9: Defiling Deluge, Murderous Exhortations, Rod of Corruption, Wail of "
        "Malice, Plaguereaper, Reaper of Souls, Shard Blade, Web of Shadows, Warp-Quake. SHIPPED: installed pack md5 %s; "
        "harness 182 full suite 7,721 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-20; xlsx v66 supersedes v65; v1-v65 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
