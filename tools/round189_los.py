#!/usr/bin/env python3
"""Round 189: the line of fire (user ruling 2026-11-21: terrain and units on all 35 'Requires line of sight' abilities;
"It's better for the mod if it doesn't fire."). Applies the same four edits to the live source and the annotated copy:
  1. the LOS block (generated key text + the check) before the shared enemy class test;
  2. eg_class_ok: an enemy behind a blocked line is not a target (every picker and the pre-cast re-check call it);
  3. the poll: FOURTH.eg_caster / FOURTH.eg_los per entry;
  4. the load loop: ability.los from the entry's keys.
Backups go to docs/backups/round189/pre189_*.lua first (the RED control)."""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_los_keys  # noqa: E402

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
LIVE = os.path.join(ROOT, r"mod_source\script\battle\mod\zz_test_deadly_onslaught.lua")
ANN = os.path.join(ROOT, r"docs\WH3_auto_ability_annotated.lua")
BK = os.path.join(ROOT, r"docs\backups\round189")
BLOCK = open(os.path.join(ROOT, r"tools\round189_los_block.lua"), encoding="utf-8").read()
BLOCK = BLOCK.replace("@LOS_TEXT@", gen_los_keys.lua_text(gen_los_keys.derive()))

EDITS = [
    ("-- true when the enemy fits the current entry's target class (nil class = any enemy)\n",
     BLOCK + "-- true when the enemy fits the current entry's target class (nil class = any enemy)\n"),
    ("\tif not FOURTH.enemy_not_hidden(enemy) then return false end   -- ROUND 168: never a hidden enemy\n",
     "\tif not FOURTH.enemy_not_hidden(enemy) then return false end   -- ROUND 168: never a hidden enemy\n"
     "\tif not FOURTH.eg_los_ok(enemy) then return false end   -- ROUND 189: never an enemy behind a blocked line\n"),
    ("\t\t\t\t\tFOURTH.eg_marker = ability.marker\n",
     "\t\t\t\t\tFOURTH.eg_marker = ability.marker\n"
     "\t\t\t\t\tFOURTH.eg_caster = unit   -- ROUND 189: the caster the line of fire is drawn from\n"
     "\t\t\t\t\tFOURTH.eg_los = (ability.los == true)   -- ROUND 189: the game's 'Requires line of sight'\n"),
    ("\tability.evaluate = FOURTH.evaluators[ability.trigger]\n",
     "\tability.evaluate = FOURTH.evaluators[ability.trigger]\n"
     "\tability.los = FOURTH.entry_los(ability)   -- ROUND 189: the line of fire (terrain and units)\n"),
]

# the reading copy stays free of log calls (a standing pin): its block carries the two log lines as comments
ANN_LOGS = [
    ('\tFOURTH.los_ground_said = text\n'
     '\tlog("LINE OF FIRE: " .. text .. " - the line-of-sight abilities hold (user ruling 2026-11-21: better not to fire)")\n',
     '\tFOURTH.los_ground_said = text   -- the live copy writes "LINE OF FIRE: <text> - the line-of-sight abilities hold"\n'),
    ('\t\tFOURTH.los_seen[lk] = tick_count\n'
     '\t\tlog("  " .. tostring(FOURTH.eg_marker) .. " LINE OF FIRE BLOCKED to " .. tostring(FOURTH.type_plain(enemy) or "?")\n'
     '\t\t\t.. ": " .. why .. " - not a target")\n',
     '\t\tFOURTH.los_seen[lk] = tick_count   -- the live copy writes "<marker> LINE OF FIRE BLOCKED to <enemy>: <why>"\n'),
]
ANN_EDITS = list(EDITS)
_ann_block = BLOCK
for a, b in ANN_LOGS:
    assert _ann_block.count(a) == 1, a[:60]
    _ann_block = _ann_block.replace(a, b)
assert "log(" not in _ann_block
ANN_EDITS[0] = (EDITS[0][0], _ann_block + EDITS[0][0])

os.makedirs(BK, exist_ok=True)
for path, tag, edits in ((LIVE, "live", EDITS), (ANN, "ann", ANN_EDITS)):
    bk = os.path.join(BK, "pre189_%s.lua" % tag)
    if not os.path.exists(bk):
        shutil.copy2(path, bk)
    src = open(bk, "rb").read().decode("utf-8")
    assert "\r\n" not in src
    for a, b in edits:
        assert src.count(a) == 1, (tag, a[:60], src.count(a))
        src = src.replace(a, b)
    open(path, "wb").write(src.encode("utf-8"))
    print("patched", tag, len(src))
