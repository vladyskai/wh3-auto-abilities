#!/usr/bin/env python3
"""Round 134 (harness 133): audit batch 3 - the speed buffs leave the melee-only trigger.

User rulings 2026-11-09 (audit group R7, all three as recommended):
  * speed / charge buffs with no melee stat - Apocalyptic Charge, Twilight Horn I, Potion of
    Speed, Blooood!: "Charge only" (the existing charge_only family, Ferocious Battle Howl's);
  * speed plus a melee stat - Book of Arkhan, Rune of Speed, Master Rune of Speed, Lightning
    Reflexes, Master of the Skies, Pendant of Slaanesh, Slippery, Transfix: "Charge, else in
    melee" (the existing charge_or_melee family, Fangspike's);
  * Thunderburner and Thunderburner Upgraded (Thunderbarge): "Stop automating" - both entries
    and their two wind-up rows leave the mod.
No new code: both families exist. Both files (live source and annotated copy) are edited alike.
"""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

CHARGE_ONLY = ["apocalyptic_charge", "twilight_horn_i", "potion_of_speed", "blooood"]
CHARGE_OR_MELEE = ["book_of_arkhan", "rune_of_speed", "master_rune_of_speed", "lightning_reflexes",
                   "master_of_the_skies", "pendant_of_slaanesh", "slippery", "transfix"]
GONE = ["thunderburner", "thunderburner_upgraded"]
WINDUP_GONE = ["wh3_dlc25_unit_abilities_thunderburner", "wh3_dlc25_unit_abilities_thunderburner_upgraded"]


def entry_span(s, marker):
    tag = '\t{ marker = "%s",' % marker
    assert s.count(tag) == 1, marker
    a = s.index(tag)
    b = s.index("ox = 0, oy = 0 },\n", a) + len("ox = 0, oy = 0 },\n")
    block = s[a:b]
    assert block.count("\n") <= 5 and 'trigger = "melee_unwavering",' in block, (marker, block)
    return a, b, block


def apply(s):
    for m in GONE:
        a, b, _ = entry_span(s, m)
        s = s[:a] + s[b:]
    for k in WINDUP_GONE:
        line = '\t\t["%s"] = 1,\n' % k
        assert s.count(line) == 1, k
        s = s.replace(line, "")
    for fam, ms in (("charge_only", CHARGE_ONLY), ("charge_or_melee", CHARGE_OR_MELEE)):
        for m in ms:
            a, b, block = entry_span(s, m)
            s = s[:a] + block.replace('trigger = "melee_unwavering",', 'trigger = "%s",' % fam) + s[b:]
    assert "thunderburner" not in s
    return s


for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    before = (s.count('trigger = "melee_unwavering"'), s.count('trigger = "charge_only"'),
              s.count('trigger = "charge_or_melee"'))
    s = apply(s)
    after = (s.count('trigger = "melee_unwavering"'), s.count('trigger = "charge_only"'),
             s.count('trigger = "charge_or_melee"'))
    assert after == (before[0] - 14, before[1] + 4, before[2] + 8), (before, after)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "melee_unwavering/charge_only/charge_or_melee", before, "->", after)
