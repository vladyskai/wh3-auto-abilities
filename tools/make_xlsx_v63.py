#!/usr/bin/env python3
"""Build WH3_abilities_master_v63_2026-11-18.xlsx from v62 - round 180: the score-3 review, rows 87-114 and 128 (user,
2026-11-18).

(1) Abilities: the moved keys get their new family and text (earlier notes kept); Rock Bottom, Eat da Runts!,
    Cold-Blooded keep their family with the new text; the 80% WW keys get a note; Heaven's Gate, Snowflake Pendant and
    Stave of Avelorn become 'SKIPPED (user decision)'.
(2) Numbers: the trigger table re-counted; the 4 new families appended: 129 -> 133 rows (total row 173 -> 177);
    935 entries / 989 keys; implemented 992 -> 989, not implemented 131 -> 134.
(3) Cards: from the harness-179 run. (4) Definitions: title v63, section 60. Changelog: a v63 row.
v1-v62 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v62_2026-11-18.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v63_2026-11-18.xlsx"
REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows4_harness179"
RUN = REL + r"\h179_run1.txt"
CARDS_TSV = REL + r"\cards_round180.tsv"
NEW_FAMILIES = ["health_aura_ally_rule", "self_heal_clear", "self_hurt_attacked", "charge_or_tired"]
R180 = " ROUND 180 (user approval 2026-11-18, score-3 review row %d)."
ROOT = ("enemy_fast_near_ally: a visible fast enemy (5 m/s or more, moving) closing within 40 m of our units, within the "
        "70 m bound (the real 100 m cast range; the entry carried its AREA as its range by mistake until round 180); the "
        "root lands on its ground; no melee arm (user: 'Rows 87-90 implement without melee').")
RULE_HEAL = ("health_aura_ally_rule: the lowest unit at or below 75%% health that the game's own target rule allows "
             "(%s), the caster included, within the 70%% ally bound (%d m); cast on it.")
T = {
    "wh2_dlc10_character_abilities_entangle": (ROOT[:-1] + "; target class: not flying.", 87),
    "wh3_dlc25_character_abilities_get_em": (ROOT, 88),
    "wh2_dlc13_lord_abilities_hunters_snare": (ROOT, 89),
    "wh2_dlc13_lord_abilities_hunters_trap": (ROOT, 90),
    "wh2_dlc17_spell_bound_shield_of_thorns": ("melee_self_or_ally: the caster in melee (cast on self), else the nearest "
                                               "ally in melee within 140 m (70% of 200); reflection pays when struck.", 99),
    "wh_pro02_item_abilities_blood_chalice_of_bathori": (RULE_HEAL % ("Lords and Heroes only", 42), 104),
    "wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness": (RULE_HEAL % ("undead units only", 140), 105),
    "wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness_upgraded": (RULE_HEAL % ("undead units only", 140), 105),
    "wh3_cp1_character_abilities_protection_prayer": (RULE_HEAL % ("Tiger Warriors only: the GENERATED set from the "
                                                                   "game's 'tiger_warrior' attribute, 9 units", 70)
                                                      + " The user: 'I like the option'.", 107),
    "wh3_dlc26_item_abilities_bugmans_xxxxxx": ("self_heal_clear: at or below 75% health and no visible enemy within 38 m "
                                                "(70% of its 55 m intercept range: the game refuses it with an enemy "
                                                "inside).", 106),
    "wh2_main_lord_abilities_potion_of_charoi": ("self_hurt_attacked: at or below 75% health AND in melee or under "
                                                 "missile fire (a 9 s resistance burst).", 108),
    "wh3_main_weapon_abilities_skars_kraken_killer": ("self_hurt_attacked: at or below 75% health AND in melee or under "
                                                      "missile fire (user: 'caster at 75% and in melee or being shot at "
                                                      "is better').", 110),
    "wh_main_character_abilities_foe_seeker": ("charge_or_tired: in the charge window, or Tired or worse; no melee arm "
                                               "(user: 'include charge. Do not include melee, tired is enough in "
                                               "melee').", 111),
    "wh2_dlc15_unit_abilities_rock_bottom": ("self_out_of_ammo: out of ammunition AND above 50% health (user: 'option "
                                             "above 50% health'): the refill costs 350 damage.", 112),
    "wh3_dlc26_unit_abilities_eat_da_runts": ("eat_da_runts: the caster at or below 75% health; cast on the cheapest "
                                              "healthy ally within 70 m (an expendable unit first, then the lowest live "
                                              "value per soldier; never one at or below 75%); no self arm (user: 'A: "
                                              "cheapest ally').", 114),
    "wh2_main_character_abilities_cold_blooded": ("wavering_ally_range: the nearest wavering ally within 140 m that is a "
                                                  "Lizardmen unit (the game's rule unit_is_not_a_lizard_unit; the "
                                                  "GENERATED '_lzd_' set, 133 units, user: 'Row 128 set A').", 128),
}
FAMILY = {k: v[0].split(":", 1)[0] for k, v in T.items()}
WW_NOTE = {   # the 80% simulated reach (user: "Row 91-96 implement as in the doc")
    "wh2_dlc09_lord_abilities_sand_storm": (91, "the 80% simulated reach: buffer 46 -> 41 m"),
    "wh3_dlc24_unit_abilities_lampreys_bite": (93, "the 80% simulated reach: unchanged at 24 m (a straight path keeps its whole length)"),
    "wh3_dlc25_spell_bound_fire_the_burning_head": (95, "the 80% simulated drift: buffer 109 -> 78 m"),
    "wh3_dlc29_spell_bound_fire_skull_of_flaming_death": (95, "the 80% simulated drift: buffer 109 -> 78 m"),
    "wh2_dlc10_item_bound_arnizipals_black_horror": (96, "the 80% simulated drift: buffer 64 -> 44 m"),
}
CLOSED = {
    "wh3_cp1_item_abilities_heavens_gate": "row 92, 'remove the ruling. This is a teleportation and requires player control'",
    "wh3_main_item_abilities_snowflake_pendant": "row 100 (rule 10: it only helps before a friendly spell)",
    "wh2_dlc10_item_abilities_stave_of_avelorn": "row 101 (rule 10: it only helps before a friendly spell)",
}
NOTE_HEADS = ("PATCH 9.0.5", "ROUND 165 (night audit)", "ROUND 166", "ROUND 167", "ROUND 168", "ROUND 169")


def old_notes(old):
    idx = [old.find(h) for h in NOTE_HEADS if old.find(h) != -1]
    return (" " + old[min(idx):]) if idx else ""


def text_of(k, old):
    t, row = T[k]
    return t + (R180 % row) + old_notes(old)


def ww_text(k, old):
    row, note = WW_NOTE[k]
    return old + " ROUND 180 (user approval 2026-11-18, score-3 review row %d): %s." % (row, note)


def main():
    entries, _, _ = bd.mod_entries()
    assert len(entries) == 935
    keys_of = {}
    for e in entries:
        for k in e["keys"]:
            keys_of[k] = e["trigger"]
    for k, fam in FAMILY.items():
        assert keys_of.get(k) == fam, (k, fam, keys_of.get(k))
    for k in CLOSED:
        assert k not in keys_of, k
    cards = {}
    for line in open(RUN, encoding="utf-8"):
        if line.startswith("CARD "):
            m, c = line[5:].rstrip("\n").split(": ", 1)
            cards[m] = c
    assert len(cards) == 935 and set(cards) == {e["marker"] for e in entries}, len(cards)
    with open(CARDS_TSV, "w", encoding="utf-8", newline="\n") as f:
        f.write("marker\tability\tfamily\tkeys\tcard\n")
        for e in entries:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (e["marker"], e["name"], e["trigger"], ";".join(e["keys"]), cards[e["marker"]]))
    fam_e, fam_k = {}, {}
    for e in entries:
        fam_e[e["trigger"]] = fam_e.get(e["trigger"], 0) + 1
        fam_k[e["trigger"]] = fam_k.get(e["trigger"], 0) + len(e["keys"])
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    done, closed, noted = set(), set(), set()
    for r in range(2, ws.max_row + 1):
        ks = [x.strip() for x in str(ws.cell(row=r, column=3).value).split(";") if x.strip()]
        k = ks[0]
        # the twin keys of a multi-key entry (Shield of Thorns, Foe-Seeker) share their entry's family
        fk = next((x for x in ks if x in T), None) if k not in T else k
        if k in CLOSED:
            assert ws.cell(row=r, column=20).value == "IMPLEMENTED", k
            ws.cell(row=r, column=19).value = "skipped (user decision 2026-11-18: closed, " + CLOSED[k] + ")"
            ws.cell(row=r, column=20).value = "SKIPPED (user decision)"
            ws.cell(row=r, column=21).value = "-"
            ws.cell(row=r, column=22).value = "-"
            closed.add(k)
        elif k in WW_NOTE:
            ws.cell(row=r, column=22).value = ww_text(k, str(ws.cell(row=r, column=22).value or ""))
            noted.add(k)
        elif keys_of.get(k) in ("melee_self_or_ally", "charge_or_tired") and k not in T and \
                k.endswith(("shield_of_thorns", "foe_seeker", "foe_seeker_summoned")):
            src_k = "wh2_dlc17_spell_bound_shield_of_thorns" if k.endswith("shield_of_thorns") else "wh_main_character_abilities_foe_seeker"
            old = str(ws.cell(row=r, column=22).value or "")
            ws.cell(row=r, column=21).value = FAMILY[src_k]
            ws.cell(row=r, column=22).value = T[src_k][0] + (R180 % T[src_k][1]) + old_notes(old)
            done.add(k)
        elif fk is not None:
            assert ws.cell(row=r, column=20).value == "IMPLEMENTED", k
            old = str(ws.cell(row=r, column=22).value or "")
            ws.cell(row=r, column=21).value = FAMILY[fk]
            ws.cell(row=r, column=22).value = text_of(fk, old)
            done.add(k)
    assert set(T) <= done, set(T) - done
    assert closed == set(CLOSED) and noted == set(WW_NOTE), (set(CLOSED) - closed, set(WW_NOTE) - noted)
    n = wb["Numbers"]
    assert n.cell(row=173, column=2).value == "TOTAL (129 families)"
    n.insert_rows(173, amount=len(NEW_FAMILIES))
    for i, fam in enumerate(NEW_FAMILIES):
        n.cell(row=173 + i, column=2).value = fam
    for r in range(44, 177):
        n.cell(row=r, column=1).value = r - 43
        fam = n.cell(row=r, column=2).value
        n.cell(row=r, column=3).value = fam_e.get(fam, 0)
        n.cell(row=r, column=4).value = fam_k.get(fam, 0)
    assert n.cell(row=177, column=2).value == "TOTAL (129 families)"
    n.cell(row=177, column=2).value = "TOTAL (133 families)"
    n.cell(row=177, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 177))
    n.cell(row=177, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 177))
    assert (n.cell(row=177, column=3).value, n.cell(row=177, column=4).value) == (935, 989)
    assert all(n.cell(row=r, column=3).value > 0 for r in range(44, 177)), "an empty family is listed"
    assert n.cell(row=179, column=1).value == "Bombardment set (COMPLETE - round 108)"
    n.cell(row=13, column=3).value = 989
    n.cell(row=14, column=3).value = 134
    n.cell(row=42, column=1).value = (
        "Trigger families after round 180 - re-counted from the mod's own ABILITIES table: 133 families / 935 entries / "
        "989 keys. Round 180 (the score-3 review, rows 87-114 and 128): 4 NEW families; 3 closed.")
    n.cell(row=7, column=1).value = (
        "Date: 2026-11-18     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v63 - ROUND 180: the score-3 review, rows 87-114 and 128. 989 rows / 989 keys implemented; 134 not implemented "
        "among the included (50 skipped by the user). The mod: 935 entries / 989 keys / 133 trigger families.)")
    cs = wb["Cards"]
    cs.delete_rows(2, cs.max_row - 1)
    for e in entries:
        cs.append([e["marker"], e["name"], e["trigger"], "; ".join(e["keys"]), cards[e["marker"]]])
    cs.cell(row=1, column=5).value = "Card: the M/A badge's hover text (round 180)"
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v62")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v63 (2026-11-18)"
    base = d.max_row + 2
    sec = [("60. ROUND 180 - THE SCORE-3 REVIEW, ROWS 87-114 AND 128 (v63)", None),
           ("NEW FAMILIES", "health_aura_ally_rule (Blood Chalice of Bathori, Breath of Darkness x2, Mantra of "
            "Invigoration), self_heal_clear (Bugman's XXXXXX), self_hurt_attacked (Potion of Charoi, Skar's "
            "Kraken-Killer), charge_or_tired (Foe-Seeker)."),
           ("CLOSED BY THE USER", "Heaven's Gate (row 92), Snowflake Pendant (row 100), Stave of Avelorn (row 101)."),
           ("NEW RULE SETS", "lizard (the '_lzd_' land units, 133, user 'set A') and tiger (the game's 'tiger_warrior' "
            "attribute, 9): the ally target rule codes Z and T."),
           ("FOUND ON THE WAY", "The 4 ground roots carried their AREA (15 / 35 m) as their cast range: now 100 m (the "
            "game's target_intercept_range, 70 m bound). Curse of Khsar has the same slip (row in 57-86, not touched)."),
           ("NOT BUILT", "Row 98 Land Mine: its blast is 25 m, so 'half a packed block' is 415 soldiers: it would almost "
            "never fire. Options go to the user. Row 94: the data says the Loons hit our units, so the doc's option does "
            "not apply.")]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-18"
    ch.cell(row=r, column=2).value = "v63"
    ch.cell(row=r, column=3).value = (
        "ROUND 180. The score-3 review, rows 87-114 and 128: 13 entries moved, 4 new families, 3 closed, the 80%% WW "
        "reach for 5 keys. SHIPPED: installed pack md5 %s; harness 179 full suite 7,622 checks / 0 failures."
        % os.environ.get("WH3_PACK_MD5", "PENDING"))
    ch.cell(row=r, column=4).value = "user approval 2026-11-18; xlsx v63 supersedes v62; v1-v62 byte-unchanged."
    wb.save(DST)
    print("wrote", DST)


if __name__ == "__main__":
    main()
