#!/usr/bin/env python3
"""Round 136 (harness 135): audit batch 5 - the melee hexes leave the missile arm.

User rulings 2026-11-09 (audit group R3, all as recommended):
  * the pure melee hexes (14) and the spreading melee-defence hexes (6): "Enemy in melee" (enemy_melee);
  * the immobilisers (Gaze of Fate, Sadistic Snare, Spearfisher's Net): "Fast enemy near us"
    (the round-135 enemy_fast_near_ally: moving, run speed 5 m/s or more, within 40 m of our units);
  * Spearfisher's Net: the game's flying_currently target flag, "Yes, add it now" -> target_class
    "not_flying", read live through is_currently_flying() (exactly false passes; true, nil or a raising
    read = not offered).
No string.find. Every helper is a FOURTH field.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

TO_MELEE = ["assassins_trophy", "lord_of_dragons", "beguile", "oath_of_vengeance", "ottos_scythe",
            "averland_runefang", "the_dark_master", "enfeebling_foe", "the_hammer_of_karak_drazh", "torment_blade",
            "trophy_heads", "willing_prey", "whip_of_agony", "fermented_fungi",
            "blight_swarm", "virulent_contagion", "virulent_contagion_upgraded", "dispatch_the_swarm_attack",
            "dispatch_the_swarm_attack_upgraded", "pestilent_potions"]
TO_FAST = ["gaze_of_fate", "sadistic_snare", "spearfishers_net"]
assert len(TO_MELEE) == 20


def entry_span(s, marker):
    tag = '\t{ marker = "%s",' % marker
    assert s.count(tag) == 1, marker
    a = s.index(tag)
    b = s.index("ox = 0, oy = 0 },\n", a) + len("ox = 0, oy = 0 },\n")
    block = s[a:b]
    assert block.count("\t{ marker = ") == 1 and 'trigger = "enemy_engaged_or_shot",' in block, marker
    return a, b, block


def sub(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a))
    return s.replace(a, b)


CLS_OLD = ('\tif t == nil then return false end\n'
           '\tif cls == "large" then return FOURTH.class_keys.large[t] == true end\n')
CLS_NEW = ('\t-- ROUND 136: Spearfisher\'s Net (the game\'s flying_currently flag) - read live;\n'
           '\t-- only an exact false passes, an unreadable flight never qualifies\n'
           '\tif cls == "not_flying" then\n'
           '\t\tlocal ok_f, fly = pcall(function() return enemy:is_currently_flying() end)\n'
           '\t\treturn ok_f and fly == false\n'
           '\tend\n' + CLS_OLD)
HDR_OLD = "--     data (tools/gen_unit_size_keys.py); an unreadable type never qualifies.\n"
HDR_NEW = HDR_OLD + ("--   ROUND 136 (audit batch 5): 20 melee hexes join enemy_melee; Gaze of Fate,\n"
                     "--     Sadistic Snare and Spearfisher's Net join enemy_fast_near_ally; the class\n"
                     "--     \"not_flying\" (Spearfisher's Net) reads is_currently_flying() live.\n")

for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    before = (s.count('trigger = "enemy_engaged_or_shot"'), s.count('trigger = "enemy_melee"'),
              s.count('trigger = "enemy_fast_near_ally"'), s.count("\t\ttarget_class = "))
    for m in TO_MELEE + TO_FAST:
        a, b, block = entry_span(s, m)
        fam = "enemy_melee" if m in TO_MELEE else "enemy_fast_near_ally"
        nb = block.replace('trigger = "enemy_engaged_or_shot",', 'trigger = "%s",' % fam)
        if m == "spearfishers_net":
            assert "target_class" not in nb
            nb = nb.replace("\t\tox = 0, oy = 0 },\n", '\t\ttarget_class = "not_flying",\n\t\tox = 0, oy = 0 },\n')
        s = s[:a] + nb + s[b:]
    s = sub(s, CLS_OLD, CLS_NEW)
    s = sub(s, HDR_OLD, HDR_NEW)
    after = (s.count('trigger = "enemy_engaged_or_shot"'), s.count('trigger = "enemy_melee"'),
             s.count('trigger = "enemy_fast_near_ally"'), s.count("\t\ttarget_class = "))
    assert after == (before[0] - 23, before[1] + 20, before[2] + 3, before[3] + 1), (before, after)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, before, "->", after)
