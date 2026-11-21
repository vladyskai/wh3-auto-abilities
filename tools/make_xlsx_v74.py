#!/usr/bin/env python3
"""Build WH3_abilities_master_v74_2026-11-21.xlsx from v73 - round 192 (user rulings 2026-11-21).

(1) Abilities:
    - the five spell-bar runes (Breaking, Negation, Slowness, Speed, Oath & Steel) -> EXCLUDED, REMOVED (spell bar)
      (user: "They should not be in the mod. Just mark them as closed because they are on the right ability wheel.");
    - every row of an entry whose trigger reads the fast-enemy test gains the CLOSING sentence (option A,
      "try to implement using is_moving_fast()");
    - Shock Collar and Remouldered gain the MOULDER sentence (user: "do it");
    - TWO NEW ROWS (the inventory's in-wheel rule had missed source_type = passive): Grombrindal Has No Fear (#1801,
      IMPLEMENTED on melee_or_wavering_aura; user: 'implement "at least one ally (caster included) in range in melee
      or wavering"') and Scry-Orb (#1802, NOT IMPLEMENTED: its trigger waits for a ruling; user: "then add").
(2) Numbers: every count recomputed from the v74 rows and the mod's ABILITIES table (1,802 rows).
(3) Definitions: title v74, section 71. Changelog: a v74 row. v1-v73 are never opened for writing."""
import collections
import csv
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402
import gamedata_paths as GP  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v73_2026-11-21.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v74_2026-11-21.xlsx"

RUNES = ["wh2_dlc17_rune_abilities_rune_of_breaking", "wh_main_rune_abilities_rune_of_negation",
         "wh2_dlc17_rune_abilities_rune_of_slowness", "wh2_dlc17_rune_abilities_rune_of_speed",
         "wh_main_rune_abilities_rune_of_oath_and_steel"]
RUNE_REASON = ("excluded family: spell bar - a rune the game shows on the right-hand spell bar, which the mod never claims "
               "(user ruling 2026-11-03); closed by the user 2026-11-21: 'They should not be in the mod. Just mark them as "
               "closed because they are on the right ability wheel.'")
RUNE_IMPL = "REMOVED (spell bar: on the right-hand bar, not the wheel)"
RUNE_TRIG = "No automation - removed from the mod in round 192 (user decision 2026-11-21): the rune sits on the right-hand spell bar."
FAST_FAMILIES = ("enemy_fast_near_ally", "enemy_fast_or_melee", "enemy_fast_fire_melee", "enemy_melee_or_fast",
                 "enemy_wave_charge", "slow_army")
FAST_SENTENCE = (" CLOSING (round 192): the fast enemy must be running (is_moving_fast) and its gap to our nearest unit must"
                 " shrink by at least 3 m/s over at least 1 s; an enemy riding past, walking or running away no longer counts.")
MOULDER = ["wh2_dlc16_hero_abilities_shock_collar", "wh2_dlc16_lord_abilities_remouldered"]
MOULDER_SENTENCE = (" MOULDER (round 192): only a Clan Moulder monster is a target (the game's rule; 28 unit types: Rat Ogres,"
                    " Hell Pit Abominations, Brood Horrors, Wolf Rats, Stormfiends, the Moulder lords on monsters).")
GHNF = "wh_pro01_lord_passive_grombrindal_has_no_fear"
SCRY = "wh3_dlc29_item_abilities_scry_orb"
PASSIVE_REASON = ("carrier family: passive - a castable wheel button the game files under source_type = passive (the inventory "
                  "rule had missed it; added in round 192)")
NEW_ROWS = [
    [1801, "Grombrindal Has No Fear", GHNF, "Augment (Area) - targeting: self + allies in range (all)", "1 use", "-",
     "Melee Defence: +24; Unbreakable", "24 s", "effect range (aura) 55 m; targeting area: wh_abilities_generic_buff", "-",
     "no range column (self-centred aura); effect_range 55 m", "phase 1: 24 s", "120 s", "self; allies in range (all)",
     "-", "As battle-hardened as he is ancient, the White Dwarf will always stand his ground, no matter the pandemonium "
     "unfolding around him.", "Category / Targeting Type: Augment (Area) - targeting: self + allies in range (all)",
     "IN-WHEEL", PASSIVE_REASON, "IMPLEMENTED", "melee_or_wavering_aura",
     "melee_or_wavering_aura: fires when the caster or a friendly unit (alive, not routing) within the aura's bound "
     "(55 m x 70% = 38 m) is in melee or wavering; cast centred on the caster. User ruling 2026-11-21: 'at least one ally "
     "(caster included) in range in melee or wavering'.", "none found"],
    [1802, "Scry-Orb", SCRY, "Augment of the Winds - targeting: self", "3 uses", "-",
     "Winds of Magic regeneration: x1.6; ability recharge: -30 s; mana_max_depletion_mod 0.2", "32 s",
     "targeting area: wh_abilities_generic_buff", "-", "no range column (self)", "phase 1: 32 s", "120 s", "self", "-",
     "Through the ominous green glow of the runes, whispers of futures fade, each one more horrifying than the previous.",
     "Category / Targeting Type: Augment of the Winds - targeting: self", "IN-WHEEL", PASSIVE_REASON, "NOT IMPLEMENTED",
     "-", "Not automated yet: its trigger waits for the user's ruling (proposal 2026-11-21: fire when ready, like the 21 "
     "pure winds abilities on when_ready).", "none found"],
]


REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_closing_harness191"
RUN = REL + r"\h191_run1.txt"
CARDS_TSV = REL + r"\cards_round192.tsv"


def read_cards():
    """The M/A card of every entry, as the mod composed it in the harness-191 run (one 'CARD marker: text' line each)."""
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    return cards


def source_types():
    out = {}
    with open(os.path.join(GP.GAMEDATA, "unit_abilities.tsv"), encoding="utf-8-sig") as f:
        rd = csv.reader(f, delimiter="\t")
        h = next(rd)
        next(rd)
        i = h.index("source_type")
        for r in rd:
            if r:
                out[r[0]] = r[i]
    return out


def excl_family(reason):
    s = str(reason)
    if s.startswith("excluded family: spell bar"):
        return "Spell-bar runes (a rune on the right-hand spell bar; closed by the user 2026-11-21)"
    if s.startswith("excluded family: spell"):
        return "Spells (source_type = spell)"
    if s.startswith(("excluded family: army", "excluded (army-bar", "skipped (round 106")):
        return "ARMY"
    if s.startswith("excluded family: cataclysm"):
        return "Cataclysm spells (source_type = cataclysm)"
    if s.startswith("excluded family: quest"):
        return "Quest-battle army ability (source_type = quest)"
    if s.startswith("boss-only"):
        return "Boss-only unit (granted only to a _boss unit)"
    if s.startswith("illusion"):
        return "Illusion summons (spawn_is_decoy)"
    raise ValueError(s)


def counts(rows, st):
    inc = [r for r in rows if r[17] == "IN-WHEEL"]
    exc = [r for r in rows if r[17] == "EXCLUDED"]
    impl = [r for r in inc if r[19] == "IMPLEMENTED"]
    car = collections.OrderedDict()
    for r in inc:
        k = str(r[2]).split(";")[0].strip()
        c = car.setdefault(st.get(k, "?"), [0, 0])
        c[0] += 1
        c[1] += (r[19] == "IMPLEMENTED")
    ex = collections.Counter(excl_family(r[18]) for r in exc)
    return len(rows), len(exc), len(inc), len(impl), car, ex


def plan(ws):
    """(row, column, old, new) for every edited cell of the existing rows."""
    entries, _, _ = bd.mod_entries()
    fast_keys = {k for e in entries if e["trigger"] in FAST_FAMILIES for k in e["keys"]}
    out = []
    for r in range(2, ws.max_row + 1):
        k = str(ws.cell(r, 3).value).split(";")[0].strip()
        t = ws.cell(r, 22).value
        if k in RUNES:
            assert ws.cell(r, 20).value == "IMPLEMENTED", k
            for col, new in ((18, "EXCLUDED"), (19, RUNE_REASON), (20, RUNE_IMPL), (21, "-"), (22, RUNE_TRIG)):
                out.append((r, col, ws.cell(r, col).value, new))
        elif k in fast_keys and ws.cell(r, 20).value == "IMPLEMENTED":
            out.append((r, 22, t, (t or "").rstrip() + FAST_SENTENCE))
        elif k in MOULDER:
            out.append((r, 22, t, (t or "").rstrip() + MOULDER_SENTENCE))
    return out, fast_keys


def main():
    assert not os.path.exists(DST), DST
    st = source_types()
    wb0 = openpyxl.load_workbook(SRC, read_only=True)
    rows0 = [list(r) for r in wb0["Abilities"].iter_rows(values_only=True, min_row=2)]
    wb0.close()
    # the method must reproduce v73's own Numbers before it may write v74's
    n0 = counts(rows0, st)
    assert n0[:4] == (1800, 677, 1123, 1041), n0[:4]
    assert dict(n0[4]) == {"active": [920, 849], "bound": [162, 159], "rune": [12, 10], "item": [12, 12],
                           "lord": [10, 4], "character": [3, 3], "unit": [3, 3], "weapon": [1, 1]}, dict(n0[4])
    assert n0[5]["ARMY"] == 223 and n0[5]["Spells (source_type = spell)"] == 418, n0[5]
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    edits, fast_keys = plan(ws)
    for r, c, old, new in edits:
        assert ws.cell(r, c).value == old
        ws.cell(r, c).value = new
    assert all(GHNF not in str(ws.cell(r, 3).value) and SCRY not in str(ws.cell(r, 3).value) for r in range(2, ws.max_row + 1))
    for nr in NEW_ROWS:
        r = ws.max_row + 1
        for c, v in enumerate(nr, start=1):
            ws.cell(r, c).value = v
    rows = [list(x) for x in ws.iter_rows(values_only=True, min_row=2)]
    tot, exc, inc, impl, car, ex = counts(rows, st)
    assert (tot, exc, inc, impl) == (1802, 682, 1120, 1037), (tot, exc, inc, impl)
    entries, _, _ = bd.mod_entries()
    assert len(entries) == 984 and sum(len(e["keys"]) for e in entries) == 1037
    mod_keys = {k for e in entries for k in e["keys"]}
    impl_keys = {str(x[2]).split(";")[0].strip() for x in rows if x[19] == "IMPLEMENTED"}
    assert impl_keys == mod_keys, (sorted(impl_keys - mod_keys)[:5], sorted(mod_keys - impl_keys)[:5])

    nm = wb["Numbers"]
    assert "v73 - ROUND 191" in str(nm.cell(7, 1).value)
    nm.cell(7, 1).value = (
        "Date: 2026-11-21     Rule in force since: 2026-10-18     Inventory: 1,802 active abilities     "
        "(v74 - ROUND 192: the five spell-bar runes closed and removed, Grombrindal Has No Fear and Scry-Orb added (the "
        "inventory had missed source_type = passive), the fast-enemy closing check, the Moulder rule. 1,037 rows / 1,037 "
        "keys implemented; 83 not implemented among the included (62 skipped by the user, 1 open: Scry-Orb). The mod: 984 "
        "entries / 1,037 keys / 141 trigger families.)")
    nm.cell(9, 4).value = "% of total (1,802)"
    nm.cell(9, 5).value = "% of included (1,120)"
    for row, val in ((10, tot), (11, exc), (12, inc), (13, impl), (14, inc - impl), (15, 0), (16, impl)):
        nm.cell(row, 3).value = val
        nm.cell(row, 4).value = val / tot
        if row >= 12:
            nm.cell(row, 5).value = val / inc
    assert nm.cell(18, 1).value.startswith("Included, by carrier family")
    nm.cell(18, 1).value = ("Included, by carrier family (unit_abilities.source_type) - ROW-LEVEL count, derived from this "
                            "workbook's own 1,120 IN-WHEEL rows joined to unit_abilities.source_type by exact key: it TIES to "
                            "the headline (sum = 1,120 included, 1,037 implemented). Round 192 adds the 'passive' family.")
    order = ["active", "bound", "rune", "item", "lord", "character", "unit", "weapon", "passive"]
    assert set(car) == set(order), sorted(car)
    for i, fam in enumerate(order):
        r = 20 + i
        nm.cell(r, 1).value = str(i + 1)
        nm.cell(r, 2).value = fam + ("  (round 192: Grombrindal Has No Fear, Scry-Orb)" if fam == "passive" else "")
        nm.cell(r, 3).value = car[fam][0]
        nm.cell(r, 4).value = car[fam][1]
        nm.cell(r, 5).value = car[fam][1] / car[fam][0]
    assert nm.cell(29, 1).value is None and nm.cell(29, 2).value is None
    nm.cell(29, 2).value = "Total included (ties to row 12)"
    nm.cell(29, 3).value = inc
    nm.cell(29, 4).value = impl
    nm.cell(30, 1).value = "The %d exclusions, by family - ROW count" % exc
    assert nm.cell(39, 1).value is None and nm.cell(39, 2).value is None
    labels = {r: nm.cell(r, 2).value for r in range(32, 38)}
    for r in range(32, 38):
        key = "ARMY" if str(labels[r]).startswith("Army-bar") else labels[r]
        nm.cell(r, 3).value = ex[key]
        nm.cell(r, 4).value = ex[key] / tot
        nm.cell(r, 5).value = ex[key] / exc
    sb = "Spell-bar runes (a rune on the right-hand spell bar; closed by the user 2026-11-21)"
    nm.cell(38, 1).value = "7"
    nm.cell(38, 2).value = sb
    nm.cell(38, 3).value = ex[sb]
    nm.cell(38, 4).value = ex[sb] / tot
    nm.cell(38, 5).value = ex[sb] / exc
    nm.cell(39, 2).value = "Total excluded (ties to row 11)"
    nm.cell(39, 3).value = exc
    assert sum(ex.values()) == exc
    nm.cell(40, 1).value = (
        "Reconciliation (v74): included 1,120 + excluded 682 = 1,802 ROWS. Implemented among the included 1,037 + not "
        "implemented 83 (82 decided by the user, 1 open: Scry-Orb) = 1,120. The carrier table and row 16 are re-derived from "
        "the rows. Round 192: the five spell-bar runes moved IN-WHEEL -> EXCLUDED; Grombrindal Has No Fear and Scry-Orb are "
        "the two new rows (source_type = passive).")
    fam_rows = {}
    for r in range(44, 185):
        fam_rows[nm.cell(r, 2).value] = r
    fc = collections.defaultdict(lambda: [0, 0])
    for e in entries:
        fc[e["trigger"]][0] += 1
        fc[e["trigger"]][1] += len(e["keys"])
    assert set(fc) == set(fam_rows), sorted(set(fc) ^ set(fam_rows))
    for fam, r in fam_rows.items():
        nm.cell(r, 3).value = fc[fam][0]
        nm.cell(r, 4).value = fc[fam][1]
    nm.cell(185, 3).value = len(entries)
    nm.cell(185, 4).value = sum(len(e["keys"]) for e in entries)
    nm.cell(42, 1).value = ("Trigger families after round 192 - re-counted from the mod's own ABILITIES table: 141 families / "
                            "984 entries / 1,037 keys. Round 192: the five spell-bar runes left melee_unwavering (2), "
                            "charge_or_melee, enemy_fast_near_ally and melee_or_under_fire; Grombrindal Has No Fear joined "
                            "melee_or_wavering_aura.")

    cards = read_cards()
    assert len(cards) == 984 and set(cards) == {e["marker"] for e in entries}, len(cards)
    with open(CARDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("marker\tability\tfamily\tkeys\tcard\n")
        for e in entries:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (e["marker"], e["name"], e["trigger"], ";".join(e["keys"]), cards[e["marker"]]))
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(1, 5).value = "Card: the M/A badge's hover text (round 192)"
    d = wb["Definitions"]
    assert d.cell(1, 1).value.startswith("DEFINITIONS - WH3 ability master v73")
    d.cell(1, 1).value = "DEFINITIONS - WH3 ability master v74 (2026-11-21)"
    base = d.max_row + 2
    sec = [("71. ROUND 192 - THE CLOSING CHECK, THE MOULDER RULE, THE SPELL-BAR RUNES, TWO NEW ROWS (v74)", None),
           ("CLOSING", "User 2026-11-21 (option A): 'try to implement using is_moving_fast()'. A fast enemy counts only "
            "while it RUNS (is_moving_fast) and its gap to our nearest unit shrinks by at least 3 m/s over at least 1 s "
            "(FOURTH.FAST_CLOSING_MPS / FOURTH.FAST_CLOSING_S). %d rows carry the sentence." %
            sum(1 for e in edits if e[1] == 22 and str(e[3]).endswith(FAST_SENTENCE))),
           ("MOULDER", "User 2026-11-21: 'do it'. Shock Collar and Remouldered take only a Clan Moulder monster (the game's "
            "rule unit_is_moulder_monster, whose own text reads 'Unit is not a Clan Moulder Monster'; GENERATED set of 28 "
            "units from the 'moulder_monster' attribute)."),
           ("RUNES", "User 2026-11-21: 'They should not be in the mod. Just mark them as closed because they are on the "
            "right ability wheel.' Rune of Breaking, Negation, Slowness, Speed, Oath & Steel: EXCLUDED, removed from the "
            "mod. The five Master Runes of the same names stay (a question to the user)."),
           ("NEW ROWS", "#1801 Grombrindal Has No Fear (implemented, melee_or_wavering_aura, 55 m aura -> 38 m bound) and "
            "#1802 Scry-Orb (not implemented, its trigger waits for a ruling): both castable wheel buttons the game files "
            "under source_type = passive, which the inventory rule had left out.")]
    for i, (a, b) in enumerate(sec):
        d.cell(base + i, 1).value = a
        if b is not None:
            d.cell(base + i, 2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(r, 1).value = "2026-11-21"
    ch.cell(r, 2).value = "v74"
    ch.cell(r, 3).value = (
        "ROUND 192. 5 runes EXCLUDED (spell bar); 2 new rows (Grombrindal Has No Fear, Scry-Orb); the CLOSING and MOULDER "
        "sentences; Numbers recomputed (1,802 rows). SHIPPED: installed pack md5 %s; harness 191 full suite 8,010 checks / "
        "0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(r, 4).value = "user rulings 2026-11-21; xlsx v74 supersedes v73; v1-v73 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "| edits", len(edits), "| fast rows", sum(1 for e in edits if str(e[3]).endswith(FAST_SENTENCE)),
          "| rows", tot, "included", inc, "implemented", impl, "| carrier", dict(car), "| spell-bar", ex[sb])


if __name__ == "__main__":
    main()
