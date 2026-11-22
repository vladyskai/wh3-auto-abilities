#!/usr/bin/env python3
"""Round 201 (user rulings 2026-11-22, after the Dwarf battle on the release build), both copies:

1. THE FIVE MASTER RUNES LEAVE THE MOD ("do it" on: remove the five Master Runes the game marks as runes). Master Rune
   of Slowness sits on the RIGHT-hand bar and fired by itself: its entry rode a default-armed family and a cast needs
   no badge. Rule 12 (the left-hand wheel only) and the 2026-11-21 ruling on the plain runes cover them: Breaking,
   Negation, Slowness, Speed, Oath & Steel (source_type rune). Entries and their charge_gate rows go. Master Rune of
   Flight and of Immolation (source_type active) stay.
2. ENDLESS WHIRLWIND OF DEATH ("do it" on: the same trigger as Whirlwind of Death): two new entries on
   melee_unwavering. The tracker's old 'rejected (friendly fire)' was wrong by the data: both keys launch the vortexes
   of Whirlwind of Death, affects_allies false.
The generated key tables are regenerated afterwards by tools/round171_regen_tables.py.
Backups: docs/backups/round201/pre201_{live,ann}.lua."""
import os
import shutil

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round201"

RUNES = ["master_rune_of_breaking", "master_rune_of_negation", "master_rune_of_slowness", "master_rune_of_speed",
         "master_rune_of_oath_and_steel"]
RUNE_KEYS = ["wh2_dlc17_rune_abilities_master_rune_of_breaking", "wh_dlc06_rune_abilities_master_rune_of_negation",
             "wh2_dlc17_rune_abilities_master_rune_of_slowness", "wh2_dlc17_rune_abilities_master_rune_of_speed",
             "wh_dlc06_rune_abilities_master_rune_of_oath_and_steel"]

ANCHOR = '\t-- ROUND 185 (rule-shut review row 33)\n\t{ marker = "glacial_blast", '
NEW = ('\t-- ROUND 201 (user 2026-11-22: the same trigger as Whirlwind of Death; the same vortexes, they do not hit allies)\n'
       '\t{ marker = "whirlwind_of_death_ror", name = "Endless Whirlwind of Death", trigger = "melee_unwavering",\n'
       '\t\tbadge = "zz_auto_badge_whirlwind_of_death_ror",\n'
       '\t\tkeys = { "wh3_dlc25_unit_abilities_whirlwind_of_death_ror" },\n'
       '\t\tox = 0, oy = 0 },\n'
       '\t{ marker = "whirlwind_of_death_ror_upgraded", name = "Endless Whirlwind of Death Upgraded", trigger = "melee_unwavering",\n'
       '\t\tbadge = "zz_auto_badge_whirlwind_of_death_ror_upgraded",\n'
       '\t\tkeys = { "wh3_dlc25_unit_abilities_whirlwind_of_death_ror_upgraded" },\n'
       '\t\tox = 0, oy = 0 },\n')


def cut_entry(s, marker):
    head = '\t{ marker = "%s", ' % marker
    assert s.count(head) == 1, (marker, s.count(head))
    i = s.index(head)
    j = s.index("\n\t{ marker = ", i + 1) + 1
    body = s[i:j]
    assert body.rstrip().endswith("},") and body.count("{ marker = ") == 1, body
    return s[:i] + s[j:]


def patch(path):
    s = open(path, encoding="utf-8", newline="").read()
    assert "whirlwind_of_death_ror" not in s, "already patched: " + path
    for m in RUNES:
        s = cut_entry(s, m)
    for k in RUNE_KEYS:
        line = '\t\t["%s"] = 3,\n' % k
        assert s.count(line) == 1, (k, s.count(line))
        s = s.replace(line, "")
    assert s.count(ANCHOR) == 1, s.count(ANCHOR)
    s = s.replace(ANCHOR, NEW + ANCHOR)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre201_live.lua"), (ANN, "pre201_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    patch(LIVE)
    patch(ANN)


if __name__ == "__main__":
    main()
