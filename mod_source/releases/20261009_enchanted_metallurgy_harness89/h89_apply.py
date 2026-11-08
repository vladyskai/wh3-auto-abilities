# -*- coding: utf-8 -*-
"""Round h89 edit: THE ENCHANTED METALLURGY FAMILY - ONE new trigger.

The user's new trigger (same answer for all four keys): "When self or ally in
range in melee. When ally in range is shooting."

  * MELEE half  -> SHIPS. Fire when the owner is in melee, OR any friendly
    unit other than the caster is in melee within the conservative trigger
    range (FOURTH.METALLURGY_RANGE_M = 25 m against the game-data 35 m aura);
    cast ON SELF, with the Glorious-Death / Verminking safety pattern (closest
    ally, pre-cast gap re-check, skip on drift).
  * SHOOTING half -> NOT BUILT. The battle API exposes NO per-unit
    "is firing / is shooting" read (battle_unit.lua research: only
    is_under_missile_attack - the unit RECEIVING fire; current_target /
    ammo_left / missile_range - no proof of firing NOW; battle_manager's
    under-fire counts are battle-level and defensive; flags.tsv is a
    DATA-TABLE vocabulary, not a Lua read). NO proxy is invented.

Four new ability entries -> the table grows 189 -> 193 entries (195 -> 199
keys), all on the ONE new trigger metallurgy_melee. NO new chunk-level locals:
every new piece of state/constant rides the FOURTH helper bag.

Applies to the REAL Desktop files (live + annotated) and writes copies to
h89work/next/. Every anchor asserted; line endings stay LF.
"""
import io, os, hashlib, re

DESK = "C:/Users/vlady/Desktop"
SRC_LIVE = DESK + "/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
SRC_ANN  = DESK + "/WH3_auto_ability_annotated.lua"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "h89work", "next")
os.makedirs(OUT_DIR, exist_ok=True)

def rd(p):
    with io.open(p, encoding="utf-8") as f:
        s = f.read()
    assert "\r" not in s, p
    return s

table_txt  = rd(os.path.join(HERE, "h89_table.lua"))
live_eval  = rd(os.path.join(HERE, "h89_live_eval.lua"))
ann_eval   = rd(os.path.join(HERE, "h89_ann_eval.lua"))
live_drift = rd(os.path.join(HERE, "h89_live_drift.lua"))
ann_drift  = rd(os.path.join(HERE, "h89_ann_drift.lua"))

WITS_ENTRY = ('\t{ marker = "witstealer_sword", name = "Witstealer Sword", trigger = "melee_unwavering",\n'
              '\t\tbadge = "zz_auto_badge_witstealer_sword",\n'
              '\t\tkeys = { "wh3_main_weapon_abilities_witstealer_sword" },\n'
              '\t\tox = 0, oy = 0 },\n')
TABLE_ANCHOR = WITS_ENTRY + '}\n'

EVAL_MAP_ANCHOR_LIVE = '-- THE TRIGGER -> EVALUATOR MAP, and the load-time wiring of EVERY entry.\n'
EVAL_MAP_ANCHOR_ANN  = '-- The trigger -> evaluator map and the load-time wiring of every entry\n'
MAP_TAIL_ANCHOR = '\tmelee_health75 = FOURTH.evaluate_potion_health,\n}'
MAP_TAIL_NEW    = ('\tmelee_health75 = FOURTH.evaluate_potion_health,\n'
                   '\t-- ROUND h89 (this round): the Enchanted Metallurgy family - one new trigger.\n'
                   '\tmetallurgy_melee = FOURTH.evaluate_metallurgy_melee,\n}')

CALL_ANCHOR = '\t-- THE CALL. Ordinary keys (self- or unit-targeted) use the proven'

CLEAR_ANCHOR = ('\t\t\t\t\tFOURTH.cast_target = nil\n'
                '\t\t\t\t\tFOURTH.gd_ally = nil\n'
                '\t\t\t\t\tFOURTH.vm_ally = nil\n')
CLEAR_NEW    = CLEAR_ANCHOR + '\t\t\t\t\tFOURTH.mtl_ally = nil\n'


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
    s = repl(s, TABLE_ANCHOR, WITS_ENTRY + table_txt + '}\n', name + " table")
    s = repl(s, eval_anchor, eval_blk + "\n" + eval_anchor, name + " evaluators")
    s = repl(s, MAP_TAIL_ANCHOR, MAP_TAIL_NEW, name + " evaluator map")
    s = repl(s, CALL_ANCHOR, drift_blk + CALL_ANCHOR, name + " drift re-check")
    s = repl(s, CLEAR_ANCHOR, CLEAR_NEW, name + " mtl_ally clear")
    return s


def post(name, s, is_live):
    print("-- " + name)
    assert count_plain(s, 'trigger = "melee_unwavering"') == 171, name
    assert count_plain(s, 'trigger = "charge_or_melee"') == 9, name
    assert count_plain(s, 'trigger = "verminking_wavering"') == 1, name
    assert count_plain(s, 'trigger = "melee_health75"') == 1, name
    assert count_plain(s, 'trigger = "metallurgy_melee"') == 4, name
    assert count_plain(s, "FOURTH.mtl_ally = nil") == 3, (name, count_plain(s, "FOURTH.mtl_ally = nil"))
    assert count_plain(s, "FOURTH.vm_ally = nil") == 3, name
    assert count_plain(s, "FOURTH.cast_target = unit") == 2, (name, count_plain(s, "FOURTH.cast_target = unit"))
    assert count_plain(s, "and not routing") == 7, (name, count_plain(s, "and not routing"))
    assert count_plain(s, "unit:is_in_melee() and not routing") == 4, name
    for tok in ("FOURTH.METALLURGY_RANGE_M = 25",
                "function FOURTH.mtl_ally_gap(unit, ally)",
                "function FOURTH.mtl_ally_in_range(unit, ally)",
                "function FOURTH.evaluate_metallurgy_melee(unit, routing)",
                "metallurgy_melee = FOURTH.evaluate_metallurgy_melee,",
                "effect_range =", "35 m", "DELIBERATELY CONSERVATIVE",
                'marker = "enchanted_metallurgy"',
                'marker = "enchanted_metallurgy_flaming"',
                'marker = "enchanted_metallurgy_piercing"',
                'marker = "enchanted_metallurgy_poison"',
                '"wh3_main_character_abilities_enchanted_metallurgy"',
                '"wh3_main_character_abilities_enchanted_metallurgy_flaming"',
                '"wh3_main_character_abilities_enchanted_metallurgy_piercing"',
                '"wh3_main_character_abilities_enchanted_metallurgy_poison"',
                'badge = "zz_auto_badge_enchanted_metallurgy"',
                'badge = "zz_auto_badge_enchanted_metallurgy_flaming"',
                'badge = "zz_auto_badge_enchanted_metallurgy_piercing"',
                'badge = "zz_auto_badge_enchanted_metallurgy_poison"'):
        assert tok in s, name + " missing " + tok
    # army-bar keys must NEVER be in the mod
    assert "army_abilities" not in s, name + ": an army-bar key is in the mod"
    n_marker = s.count("\t{ marker = ")
    assert n_marker == 193, (name, n_marker)
    if is_live:
        assert "enchanted_metallurgy SKIPPED:" in s, name
        assert "enchanted_metallurgy ally: ui" in s, name
        assert count_plain(s, "string.find(") == 0, name
    else:
        assert "enchanted_metallurgy SKIPPED:" not in s, name
        assert count_plain(s, "log(") == 0, name
        assert count_plain(s, "string.find(") == 0, name
    print("   ok")


live = rd(SRC_LIVE)
ann  = rd(SRC_ANN)
bl, ba = len(live), len(ann)
live = patch("LIVE", live, live_eval, live_drift, EVAL_MAP_ANCHOR_LIVE)
ann  = patch("ANN",  ann,  ann_eval,  ann_drift,  EVAL_MAP_ANCHOR_ANN)

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
