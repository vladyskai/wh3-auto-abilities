import os
paths = [r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua",
         r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"]
checks = {
    "tail": '\t\tkeys = { "wh3_cp1_character_abilities_terrifying_presence" },\n\t\tox = 0, oy = 0 },\n}\n',
    "R35": "FOURTH.ENEMY_CAST_R35  = 24\n",
    "R75": "FOURTH.ENEMY_CAST_R75  = 52\n",
    "m35": "\t[35]  = FOURTH.ENEMY_CAST_R35,\n",
    "m75": "\t[75]  = FOURTH.ENEMY_CAST_R75,\n",
    "gk": '\t\t["wh3_main_character_abilities_gate_of_khorne"] = true,\n\t},\n',
    "eval": "FOURTH.evaluators = {\n",
}
for p in paths:
    s = open(p, "rb").read().decode("utf-8")
    print(os.path.basename(p), {k: s.count(v) for k, v in checks.items()})
