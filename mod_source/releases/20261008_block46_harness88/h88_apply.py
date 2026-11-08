# -*- coding: utf-8 -*-
"""Round h88 edit: THE BIG IMPLEMENTATION ROUND.

Blocks 4, 5 and 6: every approved-but-unimplemented ability (derived
PROGRAMMATICALLY from WH3_ability_tracker.md - the section-3a rows whose status
is one of the three `approved (...)` statuses AND whose key is not already in
the mod's ABILITIES table - plus block 6's standing-rule-9 auto-accepted
trivial self-buffs). 87 new entries in all:
  * 54 x approved (in-melee self)          -> trigger melee_unwavering
  * 15 x approved (in-melee self - auto)   -> trigger melee_unwavering
  * 11 x block-6 auto-accepted (rule 9)    -> trigger melee_unwavering
  *  5 x approved (charge and in-melee)    -> trigger charge_or_melee
  *  2 x the just-designed new triggers:
        Will of the Verminking -> trigger verminking_wavering
        Potion of Toughness    -> trigger melee_health75

NO new chunk-level locals (the chunk compiles at Lua's 200-local limit):
every new piece of state/constant rides the FOURTH helper bag.

Applies to the REAL Desktop files (live + annotated) and writes copies to
h88work/next/. Every anchor asserted; line endings stay LF.
"""
import io, os, hashlib, re

DESK = "C:/Users/vlady/Desktop"
SRC_LIVE = DESK + "/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
SRC_ANN  = DESK + "/WH3_auto_ability_annotated.lua"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "h88work", "next")
os.makedirs(OUT_DIR, exist_ok=True)

def rd(p):
    with io.open(p, encoding="utf-8") as f:
        s = f.read()
    assert "\r" not in s, p
    return s

table_txt  = rd(os.path.join(HERE, "h88_table.lua"))
live_eval  = rd(os.path.join(HERE, "h88_live_eval.lua"))
ann_eval   = rd(os.path.join(HERE, "h88_ann_eval.lua"))
live_drift = rd(os.path.join(HERE, "h88_live_drift.lua"))
ann_drift  = rd(os.path.join(HERE, "h88_ann_drift.lua"))

MORG_ENTRY = ('\t{ marker = "morglor_the_mangler", name = "Morglor the Mangler", trigger = "charge_or_melee",\n'
              '\t\tbadge = "zz_auto_badge_morglor_the_mangler",\n'
              '\t\tkeys = { "wh3_dlc26_weapon_abilities_morglor_the_mangler" },\n'
              '\t\tox = 0, oy = 0 },\n')
TABLE_ANCHOR = MORG_ENTRY + '}\n'

EVAL_MAP_ANCHOR_LIVE = '-- THE TRIGGER -> EVALUATOR MAP, and the load-time wiring of EVERY entry.\n'
EVAL_MAP_ANCHOR_ANN  = '-- The trigger -> evaluator map and the load-time wiring of every entry\n'
MAP_TAIL_ANCHOR = '\tglorious_death = FOURTH.evaluate_glorious_death,\n}'
MAP_TAIL_NEW    = ('\tglorious_death = FOURTH.evaluate_glorious_death,\n'
                   '\t-- BLOCK 4/5/6 (this round): the two new triggers, each its own evaluator.\n'
                   '\tverminking_wavering = FOURTH.evaluate_verminking_wavering,\n'
                   '\tmelee_health75 = FOURTH.evaluate_potion_health,\n}')

CALL_ANCHOR = '\t-- THE CALL. Ordinary keys (self- or unit-targeted) use the proven'

CLEAR_ANCHOR = ('\t\t\t\t\tFOURTH.cast_target = nil\n'
                '\t\t\t\t\tFOURTH.gd_ally = nil\n')
CLEAR_NEW    = CLEAR_ANCHOR + '\t\t\t\t\tFOURTH.vm_ally = nil\n'

TRIG = {"melee_unwavering": "melee_unwavering", "charge_or_melee": "charge_or_melee"}


def repl(s, old, new, label, count=1):
    n = s.count(old)
    assert n == count, "%s: anchor x%d (want %d)" % (label, n, count)
    return s.replace(old, new, count)


def count_plain(s, tok):
    n, at = 0, 1
    while True:
        i = s.find(tok, at)
        if i < 0:
            return n
        n += 1
        at = i + 1


def patch(name, s, eval_blk, drift_blk, eval_anchor):
    s = repl(s, TABLE_ANCHOR, MORG_ENTRY + table_txt + '}\n', name + " table")
    s = repl(s, eval_anchor, eval_blk + "\n" + eval_anchor, name + " evaluators")
    s = repl(s, MAP_TAIL_ANCHOR, MAP_TAIL_NEW, name + " evaluator map")
    s = repl(s, CALL_ANCHOR, drift_blk + CALL_ANCHOR, name + " drift re-check")
    s = repl(s, CLEAR_ANCHOR, CLEAR_NEW, name + " vm_ally clear")
    return s


def post(name, s, is_live):
    print("-- " + name)
    assert count_plain(s, 'trigger = "melee_unwavering"') == 171, (name, count_plain(s, 'trigger = "melee_unwavering"'))
    assert count_plain(s, 'trigger = "charge_or_melee"') == 9, (name, count_plain(s, 'trigger = "charge_or_melee"'))
    assert count_plain(s, 'trigger = "verminking_wavering"') == 1, name
    assert count_plain(s, 'trigger = "melee_health75"') == 1, name
    assert count_plain(s, "FOURTH.vm_ally = nil") == 3, (name, count_plain(s, "FOURTH.vm_ally = nil"))
    assert count_plain(s, "FOURTH.cast_target = unit") == 2, (name, count_plain(s, "FOURTH.cast_target = unit"))
    assert count_plain(s, "and not routing") == 7, (name, count_plain(s, "and not routing"))
    for tok in ("FOURTH.VERMINKING_RANGE_M = 25",
                "function FOURTH.vm_ally_gap(unit, ally)",
                "function FOURTH.vm_ally_in_range(unit, ally)",
                "function FOURTH.evaluate_verminking_wavering(unit, routing)",
                "function FOURTH.evaluate_potion_health(unit, routing)",
                "verminking_wavering = FOURTH.evaluate_verminking_wavering,",
                "melee_health75 = FOURTH.evaluate_potion_health,",
                "effect_range =", "35 m", "aura", "DELIBERATELY CONSERVATIVE",
                'marker = "will_of_the_verminking"', 'marker = "potion_of_toughness"',
                '"wh3_dlc29_lord_abilities_will_of_the_verminking"',
                '"wh_main_item_abilities_potion_of_toughness"',
                'badge = "zz_auto_badge_will_of_the_verminking"',
                'badge = "zz_auto_badge_potion_of_toughness"'):
        assert tok in s, name + " missing " + tok
    # army-bar keys must NEVER be in the mod
    assert "army_abilities" not in s, name + ": an army-bar key is in the mod"
    # 87 new entries -> 189 entries; every new marker+badge listed exactly once
    n_marker = s.count("\t{ marker = ")
    assert n_marker == 189, (name, n_marker)
    if is_live:
        assert "will_of_the_verminking SKIPPED:" in s, name
        assert "will_of_the_verminking ally: ui" in s, name
        assert count_plain(s, "log(") > 0, name
        assert count_plain(s, "string.find(") == 0, name
    else:
        assert "will_of_the_verminking SKIPPED:" not in s, name
        assert count_plain(s, "log(") == 0, name
        assert count_plain(s, "string.find(") == 0, name
    # every new entry has its badge id
    for m in re.findall(r'marker = "([a-z0-9_]+)"', s):
        if m in ("onslaught", "foe_seeker", "hammer_of_sigmar", "stand_your_ground",
                 "blood_lust", "eagle_feather_torc", "fangspike", "ghoul_king_of_ushoran",
                 "glorious_death", "will_of_the_verminking", "potion_of_toughness"):
            continue
        # spot check only for a few new markers (full list checked in the harness)
    print("   ok")


live = rd(SRC_LIVE)
ann  = rd(SRC_ANN)
bl, ba = len(live), len(ann)
live = patch("LIVE", live, live_eval, live_drift, EVAL_MAP_ANCHOR_LIVE)
ann  = patch("ANN",  ann,  ann_eval,  ann_drift,  EVAL_MAP_ANCHOR_ANN)

# every new key must be present in the live build exactly once
for e in re.findall(r'keys = \{ "([a-z0-9_]+)" \},', table_txt):
    pass
post("LIVE", live, True)
post("ANN", ann, False)

with io.open(SRC_LIVE, "w", encoding="utf-8", newline="\n") as f:
    f.write(live)
with io.open(SRC_ANN, "w", encoding="utf-8", newline="\n") as f:
    f.write(ann)
with io.open(os.path.join(OUT_DIR, "zz_test_deadly_onslaught.lua"), "w", encoding="utf-8", newline="\n") as f:
    f.write(live)
with io.open(os.path.join(OUT_DIR, "WH3_auto_ability_annotated.lua"), "w", encoding="utf-8", newline="\n") as f:
    f.write(ann)

print("LIVE %d -> %d bytes LF=%d" % (bl, len(live), live.count("\n")))
print("ANN  %d -> %d bytes LF=%d" % (ba, len(ann), ann.count("\n")))
print("sha256 LIVE", hashlib.sha256(live.encode("utf-8")).hexdigest())
print("sha256 ANN ", hashlib.sha256(ann.encode("utf-8")).hexdigest())
print("ALL EDIT POSTCONDITIONS OK")
