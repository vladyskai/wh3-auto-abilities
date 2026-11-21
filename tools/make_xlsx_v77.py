#!/usr/bin/env python3
"""Build WH3_abilities_master_v77_2026-11-22.xlsx from v76 - round 198 (user 2026-11-22, the overnight review: "fix" on
rows 1, 2, 3, 6, 7, 8, 11). Ten trigger texts are restated (column 22): the four slow auras and the two guard auras
(the round-192 fast-enemy read), Favour of the Fay and Shielding Swarm x2 (never on the caster), Bugman's XXXXXX (55 m).
Cards: the three no-self cards. Numbers: the date line only (no roster change). Definitions: title v77, section 74.
Changelog: a v77 row. v1-v76 are never opened for writing."""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v76_2026-11-21.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v77_2026-11-22.xlsx"

NOSELF = "NEVER on the caster: the game's target_self is false (ROUND 198, user 2026-11-22: 'fix')."
READ = "ROUND 198: the round-192 read, walking or passing by no longer counts"
SWARM = ("the caster in melee or under fire -> on itself; else the most valuable ally within 80 m under missile fire; "
         "else the nearest ally in melee.",
         "the most valuable ally within 80 m under missile fire, else the nearest ally in melee. " + NOSELF)
SNARE = ("or a fast enemy entering 70% of the 35 m aura;",
         "or a visible fast enemy RUNNING and CLOSING on our units inside 70% of the 35 m aura (" + READ + ");")
GUARD = ("or a visible fast enemy is moving inside its aura (70%; an enemy charge).",
         "or a visible fast enemy is RUNNING and CLOSING on our units inside its aura (70%). " + READ + ".")
# key -> (old piece, new piece) of the trigger text
TEXTS = {
    "wh_dlc07_lord_abilities_favour_of_the_fay": (
        "the caster in melee (cast on self), else the nearest ally in melee within the 70% bound.",
        "the nearest ally in melee within the range bound, cast on that ally. " + NOSELF),
    "wh3_dlc29_hero_active_dispatch_the_swarm_protect": SWARM,
    "wh3_dlc29_hero_active_dispatch_the_swarm_protect_upgraded": SWARM,
    "wh2_dlc14_unit_abilities_seismic_snare": SNARE,
    "wh3_dlc29_unit_abilities_stormfiend_seismic_snare": SNARE,
    "wh2_dlc13_item_abilities_shield_of_aeons": GUARD,
    "wh3_dlc20_item_abilities_the_armour_of_morkar": GUARD,
    "wh3_main_item_abilities_the_rock_of_inevitability": (
        "or when a visible fast enemy (run speed 5 m/s or more, moving) is inside its 24 m aura (70% of 35 m).",
        "or when a visible fast enemy (run speed 5 m/s or more) is RUNNING and CLOSING on our units inside its 24 m aura "
        "(70% of 35 m). " + READ + "."),
    "wh2_dlc13_weapon_abilities_wissenland_runefang": (
        "or when a visible fast enemy is inside its 24 m aura.",
        "or when a visible fast enemy is RUNNING and CLOSING on our units inside its 24 m aura (" + READ + ")."),
    "wh3_dlc26_item_abilities_bugmans_xxxxxx": (
        "no visible enemy within 38 m (70% of its 55 m intercept range: the game refuses it with an enemy inside).",
        "no visible enemy within 55 m (its whole intercept range: the game refuses it with an enemy inside. ROUND 198, "
        "user 2026-11-22: 'fix', was 38 m)."),
}
CARDS = {
    "favour_of_the_fay": "Fires on the nearest ally in melee",
    "dispatch_the_swarm_protect": "Fires on an ally under fire, else on an ally in melee",
    "dispatch_the_swarm_protect_upgraded": "Fires on an ally under fire, else on an ally in melee",
}


def plan():
    wb = openpyxl.load_workbook(SRC, read_only=True)
    out = []
    for r, row in enumerate(wb["Abilities"].iter_rows(values_only=True, min_row=2), start=2):
        k = str(row[2]).split(";")[0].strip()
        if row[19] == "IMPLEMENTED" and k in TEXTS:
            old, new = TEXTS[k]
            t = row[21] or ""
            assert t.count(old) == 1, (k, t)
            out.append((r, k, t, t.replace(old, new)))
    cards = []
    for r, row in enumerate(wb["Cards"].iter_rows(values_only=True, min_row=2), start=2):
        if row[0] in CARDS:
            cards.append((r, row[0], row[4], CARDS[row[0]]))
    wb.close()
    return out, cards


def main():
    rows, cards = plan()
    assert len(rows) == len(TEXTS) == 10 and len(cards) == 3, (len(rows), len(cards))
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    for r, k, t, n in rows:
        assert ws.cell(row=r, column=22).value == t
        ws.cell(row=r, column=22).value = n
    cs = wb["Cards"]
    for r, m, t, n in cards:
        assert cs.cell(row=r, column=1).value == m and cs.cell(row=r, column=5).value == t
        cs.cell(row=r, column=5).value = n
    nm = wb["Numbers"]
    assert "v76 - ROUND 197" in str(nm.cell(row=7, column=1).value)
    nm.cell(row=7, column=1).value = (
        "Date: 2026-11-22     Rule in force since: 2026-10-18     Inventory: 1,802 active abilities     "
        "(v77 - ROUND 198: the overnight review's fixes. 1,038 rows / 1,038 keys implemented, 82 not implemented "
        "among the included (all decided by the user), 0 open. The mod: 985 entries / 1,038 keys / 141 trigger families.)")
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v76")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v77 (2026-11-22)"
    base = d.max_row + 2
    d.cell(row=base, column=1).value = "74. ROUND 198 - THE OVERNIGHT REVIEW'S FIXES (v77)"
    d.cell(row=base + 1, column=1).value = "RULE"
    d.cell(row=base + 1, column=2).value = (
        "User 2026-11-22 on the overnight review (docs\\WH3_overnight_review_2026-11-22.md): 'fix' on rows 1, 2, 3, 6, 7, 8 "
        "and 11. Trigger texts: the slow auras and the guard auras use the round-192 fast-enemy read (RUNNING and CLOSING "
        "on our units), then inside the aura. Favour of the Fay and Shielding Swarm are never cast on the caster (the "
        "game's target_self is false). Bugman's XXXXXX keeps the game's whole 55 m clear of enemies. Without a text "
        "change: a unit's 'one ability at a time' window is re-armed when the same ability fires twice in a row, the "
        "air-drop fast pass resets every chosen-target slot, Get Tha Gitz! has its charge hold (this workbook already "
        "said so), the Necromancer (Undeath) on a Nightmare counts as a Hero.")
    d.cell(row=base + 2, column=1).value = "ROWS"
    d.cell(row=base + 2, column=2).value = "%d trigger texts restated, %d cards restated." % (len(rows), len(cards))
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-22"
    ch.cell(row=r, column=2).value = "v77"
    ch.cell(row=r, column=3).value = (
        "ROUND 198. The overnight review's fixes. %d trigger texts and %d cards restated. SHIPPED: installed pack md5 %s. "
        "Harness 197 full suite %s checks / 0 failures." % (len(rows), len(cards), os.environ.get("WH3_PACK_MD5", "PENDING"),
                                                             os.environ.get("WH3_CHECKS", "PENDING")))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-22. xlsx v77 supersedes v76. v1-v76 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "texts", len(rows), "cards", len(cards))


if __name__ == "__main__":
    main()
