#!/usr/bin/env python3
"""Round 190: the animation decides in every shot trigger (user 2026-11-21: "Amber Bow canceled his movement, not good"
-> "Fix the 8"). The round-168 ruling ("Option A, animation decides all") never reached the shot triggers that passed
'no stand-still needed' (enemy_large_shot, enemy_large_value_shot) or had no caster check at all (enemy_spellcaster,
enemy_commander_wavering, enemy_summon_blob, enemy_execute, enemy_commander_value). FOURTH.blob_still answers true for a
cast without an animation, so only the 8 animated entries change: Amber Bow, Gaze of Nagash, Damned Pistol, Schalkain's
Teeth, Goggly Glare, Vindictive Glare, Shem's Burning Gaze, The Black Tongue.
Same edits in the live source and the annotated copy; backups to docs/backups/round190/pre190_*.lua first."""
import os
import shutil

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
LIVE = os.path.join(ROOT, r"mod_source\script\battle\mod\zz_test_deadly_onslaught.lua")
ANN = os.path.join(ROOT, r"docs\WH3_auto_ability_annotated.lua")
BK = os.path.join(ROOT, r"docs\backups\round190")
TAG = "   -- ROUND 190: the animation decides (Amber Bow stopped a walking Markus)"

EDITS = [
    # the shared caster check: standing is no longer the family's choice
    ("\tif still and not FOURTH.blob_still(unit) then return false end\n",
     "\tif not FOURTH.blob_still(unit) then return false end" + TAG + "\n"),
    # the pre-cast re-check, for every shot kind (the kinds with no caster check included)
    ("function FOURTH.shot_still_ok(enemy, unit)\n\tlocal kind = FOURTH.shot_kind\n\tif kind == nil then return false end\n",
     "function FOURTH.shot_still_ok(enemy, unit)\n\tlocal kind = FOURTH.shot_kind\n\tif kind == nil then return false end\n"
     "\tif not FOURTH.blob_still(unit) then return false end" + TAG + "\n"),
]
for fn, line in (("evaluate_enemy_spellcaster", "\tFOURTH.eg_class = \"spellcaster\"\n\tif routing then return nil end\n"),
                 ("evaluate_enemy_commander_wavering", "\tFOURTH.eg_class = \"commander\"\n\tif routing then return nil end\n"),
                 ("evaluate_enemy_summon_blob", "\tif routing or FOURTH.entry_blast_r() == nil then return nil end\n"),
                 ("evaluate_enemy_execute", "\tif routing then return nil end\n"),
                 ("evaluate_enemy_commander_value", "\tif routing then return nil end\n")):
    head = "function FOURTH.%s(unit, routing)\n\tFOURTH.eg_mode = \"shot\"\n\tFOURTH.shot_kind = nil\n" % fn
    # the reading copy answers 'false' where the live one answers 'nil' in two of them: the new line follows each copy
    EDITS.append(("ALT", head + line, head + line + "\tif not FOURTH.blob_still(unit) then return nil end" + TAG + "\n",
                  head + line.replace("return nil end", "return false end"),
                  head + line.replace("return nil end", "return false end")
                  + "\tif not FOURTH.blob_still(unit) then return false end" + TAG + "\n"))

os.makedirs(BK, exist_ok=True)
for path, tag in ((LIVE, "live"), (ANN, "ann")):
    bk = os.path.join(BK, "pre190_%s.lua" % tag)
    if not os.path.exists(bk):
        shutil.copy2(path, bk)
    src = open(bk, "rb").read().decode("utf-8")
    for ed in EDITS:
        if ed[0] == "ALT":
            a, b = (ed[1], ed[2]) if src.count(ed[1]) == 1 else (ed[3], ed[4])
        else:
            a, b = ed
        assert src.count(a) == 1, (tag, a[:80], src.count(a))
        src = src.replace(a, b)
    open(path, "wb").write(src.encode("utf-8"))
    print("patched", tag, len(src))
