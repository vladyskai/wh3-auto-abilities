import os
ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
paths = [os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua"),
         os.path.join(ROOT, "docs", "WH3_auto_ability_annotated.lua")]
anchors = {
 "slot": "FOURTH.eg_melee_only = nil\n\n-- one-time notice for an unreadable is_under_missile_attack.",
 "wb": "function FOURTH.eg_enemy_within_bound(unit, enemy)\n\tlocal gap = FOURTH.eg_enemy_gap(unit, enemy)",
 "ab": "\t\tif FOURTH.ab_ally_su ~= nil and FOURTH.ab_ally_su.unit ~= nil then\n\t\t\ttarget = FOURTH.ab_ally_su.unit\n\t\tend\n\tend\n",
 "eg": "\t-- ENEMY-TARGETED RE-CHECK (Class A, harness 97): the enemy trigger chose an",
 "call": "\t-- THE CALL. Ordinary keys (self- or unit-targeted) use the proven",
}
for p in paths:
    s = open(p, "rb").read().decode("utf-8")
    print(os.path.basename(p), {k: s.count(v) for k, v in anchors.items()})
