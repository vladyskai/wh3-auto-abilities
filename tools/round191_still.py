#!/usr/bin/env python3
"""Round 191: the animation decides in group 1 of the stand-still audit (user 2026-11-21: "For now, please only implement
number 1."). Group 1 = the 8 triggers that fire at an enemy somewhere else and never asked FOURTH.blob_still:
enemy_ground_melee_infantry, enemy_ground_melee, enemy_engaged_or_shot, enemy_melee, enemy_fast_near_ally,
enemy_melee_or_fast, enemy_melee_noncommander, enemy_missile_shooting (40 animated entries).

How: at load, each entry on one of those triggers gets its evaluator wrapped: the wrapper asks FOURTH.blob_still(unit)
first (true for a cast without an animation, so only the animated entries change) and answers 'no' while the caster
moves. Per entry, not per evaluator: other triggers that call the same pickers (enemy_ground_area, ...) are untouched.
Same edit in the live source and the annotated copy (no log call: the reading copy stays log-free).
Backups to docs/backups/round191/pre191_*.lua first."""
import os
import shutil

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
LIVE = os.path.join(ROOT, r"mod_source\script\battle\mod\zz_test_deadly_onslaught.lua")
ANN = os.path.join(ROOT, r"docs\WH3_auto_ability_annotated.lua")
BK = os.path.join(ROOT, r"docs\backups\round191")

ANCHOR = ("for _, ability in ipairs(ABILITIES) do\n"
          "\tability.evaluate = FOURTH.evaluators[ability.trigger]\n"
          "\tability.los = FOURTH.entry_los(ability)   -- ROUND 189: the line of fire (terrain and units)\n")
BLOCK = (
    "-- ROUND 191 (user 2026-11-21: 'For now, please only implement number 1'): group 1 of the stand-still audit, the\n"
    "-- triggers that fire at an enemy somewhere else. An animated cast stops its caster (the 2026-11-17 ruling 'Option A,\n"
    "-- animation decides all'), so an entry on one of these triggers is not even evaluated while its caster moves.\n"
    "-- FOURTH.blob_still answers 'yes' for a cast without an animation: only the 40 animated entries wait.\n"
    "FOURTH.STILL_GATE_TRIGGERS = {\n"
    "\tenemy_ground_melee_infantry = true, enemy_ground_melee = true, enemy_engaged_or_shot = true, enemy_melee = true,\n"
    "\tenemy_fast_near_ally = true, enemy_melee_or_fast = true, enemy_melee_noncommander = true,\n"
    "\tenemy_missile_shooting = true,\n"
    "}\n"
    "function FOURTH.still_wrap(f)\n"
    "\treturn function(unit, routing)\n"
    "\t\tif not FOURTH.blob_still(unit) then return nil end   -- ROUND 191: a moving caster waits\n"
    "\t\treturn f(unit, routing)\n"
    "\tend\n"
    "end\n")
WRAP = ("\tif FOURTH.STILL_GATE_TRIGGERS[ability.trigger] == true and ability.evaluate ~= nil then\n"
        "\t\tability.evaluate = FOURTH.still_wrap(ability.evaluate)   -- ROUND 191: the animation decides (group 1)\n"
        "\t\tability.still_gate = true\n"
        "\tend\n")

os.makedirs(BK, exist_ok=True)
for path, tag in ((LIVE, "live"), (ANN, "ann")):
    bk = os.path.join(BK, "pre191_%s.lua" % tag)
    if not os.path.exists(bk):
        shutil.copy2(path, bk)
    src = open(bk, "rb").read().decode("utf-8")
    assert src.count(ANCHOR) == 1, (tag, src.count(ANCHOR))
    assert "STILL_GATE_TRIGGERS" not in src
    src = src.replace(ANCHOR, BLOCK + ANCHOR + WRAP)
    assert "\u2014" not in src[src.index("ROUND 191"):src.index("ROUND 191") + 2000]
    open(path, "wb").write(src.encode("utf-8"))
    print("patched", tag, len(src))
