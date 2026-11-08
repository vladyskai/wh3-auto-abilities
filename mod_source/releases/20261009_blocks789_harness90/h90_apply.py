# -*- coding: utf-8 -*-
"""Round h90 edit: BLOCKS 7-9 - 69 new entries / 73 keys across the new and
existing trigger types.

Derived programmatically from WH3_ability_tracker.md 3a (see h90_derive.py):
every row carrying an `approved (...)` status that is NOT yet in the mod's
ABILITIES table, plus the two backlog `redesigned` abilities (#36 Commanding
Presence, #46 Dazh's Song of Winter Sunlight) and the one `pending review`
(#32 Chanson of Caging) = 69 entry-groups / 73 keys. The four shipped Enchanted
Metallurgy rows are skipped as already present.

New triggers (evaluators fields of the FOURTH bag):
  charge_only            - the charge window WITHOUT the melee arm
  wavering_self          - the OWNER is wavering (fail-closed)
  wavering_self_or_ally  - owner wavering OR an in-melee wavering ally in range
  charge_or_wavering     - the charge window OR wavering
  wavering_ally_range    - a wavering ally in range (owner need not waver, the
                           ally need not be in melee) - the Verminking shape
                           with the ally-melee requirement REMOVED
The redesigned pair rides: #36 Commanding Presence -> wavering_self_or_ally;
#46 Dazh's Song of Winter Sunlight -> the existing `tired` evaluator.

NO new chunk-level locals - the chunk sits at Lua's 200-local ceiling, so all
state/constants ride the FOURTH bag. LF only.
"""
import io, os, hashlib, json

ENTRIES = json.load(io.open(r"C:/Users/vlady/Desktop/WH3_mod/docs/helpers/_h90_entries.json", encoding="utf-8"))

DESK = "C:/Users/vlady/Desktop"
SRC_LIVE = DESK + "/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
SRC_ANN  = DESK + "/WH3_auto_ability_annotated.lua"
HERE = os.path.dirname(os.path.abspath(__file__))

def rd(p):
    with io.open(p, encoding="utf-8") as f:
        s = f.read()
    assert "\r" not in s, ("CRLF in " + p)
    return s

table_txt  = rd(os.path.join(HERE, "h90_table.lua"))
live_eval  = rd(os.path.join(HERE, "h90_live_eval.lua"))
ann_eval   = rd(os.path.join(HERE, "h90_ann_eval.lua"))
live_drift = rd(os.path.join(HERE, "h90_live_drift.lua"))
ann_drift  = rd(os.path.join(HERE, "h90_ann_drift.lua"))

# the last entry currently in the table (added by round h89), identical in both
# files - the anchor the new entries are inserted after.
POISON = ('\t{ marker = "enchanted_metallurgy_poison", name = "Enchanted Metallurgy: Poison", trigger = "metallurgy_melee",\n'
          '\t\tbadge = "zz_auto_badge_enchanted_metallurgy_poison",\n'
          '\t\tkeys = { "wh3_main_character_abilities_enchanted_metallurgy_poison" },\n'
          '\t\tox = 0, oy = 0 },\n')

EVAL_MAP_ANCHOR_LIVE = '-- THE TRIGGER -> EVALUATOR MAP, and the load-time wiring of EVERY entry.\n'
EVAL_MAP_ANCHOR_ANN  = '-- The trigger -> evaluator map and the load-time wiring of every entry\n'

MAP_TAIL_ANCHOR = '\tmetallurgy_melee = FOURTH.evaluate_metallurgy_melee,\n}'
MAP_TAIL_NEW = ('\tmetallurgy_melee = FOURTH.evaluate_metallurgy_melee,\n'
                '\t-- BLOCKS 7-9 (this round): five new triggers, each its own evaluator.\n'
                '\tcharge_only = FOURTH.evaluate_charge_only,\n'
                '\twavering_self = FOURTH.evaluate_wavering_self,\n'
                '\twavering_self_or_ally = FOURTH.evaluate_wavering_self_or_ally,\n'
                '\tcharge_or_wavering = FOURTH.evaluate_charge_or_wavering,\n'
                '\twavering_ally_range = FOURTH.evaluate_wavering_ally_range,\n}')

CALL_ANCHOR = '\t-- THE CALL. Ordinary keys (self- or unit-targeted) use the proven'

CLEAR_ANCHOR = '\t\t\t\t\tFOURTH.mtl_ally = nil\n'
CLEAR_NEW    = CLEAR_ANCHOR + '\t\t\t\t\tFOURTH.ws_ally = nil\n\t\t\t\t\tFOURTH.wa_ally = nil\n'


def repl(s, old, new, label, count=1):
    n = s.count(old)
    assert n == count, "%s: anchor x%d (want %d)" % (label, n, count)
    return s.replace(old, new, count)


def patch(name, s, eval_blk, drift_blk, eval_anchor):
    s = repl(s, POISON, POISON + table_txt, name + " table")
    s = repl(s, eval_anchor, eval_blk + "\n" + eval_anchor, name + " evaluators")
    s = repl(s, MAP_TAIL_ANCHOR, MAP_TAIL_NEW, name + " evaluator map")
    s = repl(s, CALL_ANCHOR, drift_blk + "\n" + CALL_ANCHOR, name + " drift re-check")
    s = repl(s, CLEAR_ANCHOR, CLEAR_NEW, name + " ally clears")
    return s


def count(s, tok):
    n, at = 0, 1
    while True:
        i = s.find(tok, at)
        if i < 0:
            return n
        n += 1
        at = i + 1


def post(name, s, is_live):
    assert count(s, 'trigger = "melee_unwavering"') == 216, (name, count(s, 'trigger = "melee_unwavering"'))
    assert count(s, 'trigger = "charge_or_melee"') == 15, name
    assert count(s, 'trigger = "charge_only"') == 1, name
    assert count(s, 'trigger = "wavering_self"') == 3, name
    assert count(s, 'trigger = "wavering_self_or_ally"') == 2, name
    assert count(s, 'trigger = "charge_or_wavering"') == 1, name
    assert count(s, 'trigger = "wavering_ally_range"') == 1, name
    assert count(s, 'trigger = "metallurgy_melee"') == 8, name
    assert count(s, 'trigger = "ushoran_health"') == 5, name
    assert count(s, 'trigger = "melee_health75"') == 2, name
    assert count(s, 'trigger = "verminking_wavering"') == 1, name
    assert count(s, 'trigger = "tired"') == 2, name
    assert count(s, "FOURTH.ws_ally = nil") == 3, (name, count(s, "FOURTH.ws_ally = nil"))
    assert count(s, "FOURTH.wa_ally = nil") == 3, name
    assert count(s, "FOURTH.mtl_ally = nil") == 3, name
    assert count(s, "FOURTH.vm_ally = nil") == 3, name
    assert count(s, "FOURTH.cast_target = unit") == 2, name
    assert count(s, "FOURTH.WAVERING_RANGE_M = 25") == 1, name
    assert count(s, "\t{ marker = ") == 262, (name, count(s, "\t{ marker = "))
    for tok in ("function FOURTH.evaluate_charge_only(unit, routing)",
                "function FOURTH.evaluate_wavering_self(unit, routing)",
                "function FOURTH.evaluate_wavering_self_or_ally(unit, routing)",
                "function FOURTH.evaluate_charge_or_wavering(unit, routing)",
                "function FOURTH.evaluate_wavering_ally_range(unit, routing)",
                "function FOURTH.ws_ally_gap(unit, ally)",
                "function FOURTH.wa_ally_gap(unit, ally)",
                "charge_only = FOURTH.evaluate_charge_only,",
                "wavering_self = FOURTH.evaluate_wavering_self,",
                "wavering_self_or_ally = FOURTH.evaluate_wavering_self_or_ally,",
                "charge_or_wavering = FOURTH.evaluate_charge_or_wavering,",
                "wavering_ally_range = FOURTH.evaluate_wavering_ally_range,"):
        assert tok in s, name + " missing " + tok
    for e in ENTRIES:
        assert 'marker = "%s"' % e["marker"] in s, name + " missing marker " + e["marker"]
        assert 'badge = "zz_auto_badge_%s"' % e["marker"] in s, name + " missing badge " + e["marker"]
        for k in e["keys"]:
            assert '"%s"' % k in s, name + " missing key " + k
    assert "army_abilities" not in s, name + ": an army-bar key is in the mod"
    if is_live:
        assert "wavering_self_or_ally SKIPPED:" in s, name
        assert "wavering_ally_range SKIPPED:" in s, name
        assert "wavering_self_or_ally ally: ui" in s, name
        assert "wavering_ally_range ally: ui" in s, name
        assert count(s, "string.find(") == 0, name
    else:
        assert "wavering_self_or_ally SKIPPED:" not in s, name
        assert count(s, "log(") == 0, name
        assert count(s, "string.find(") == 0, name


live = rd(SRC_LIVE); ann = rd(SRC_ANN)
bl, ba = len(live), len(ann)
live = patch("LIVE", live, live_eval, live_drift, EVAL_MAP_ANCHOR_LIVE)
ann  = patch("ANN",  ann,  ann_eval,  ann_drift,  EVAL_MAP_ANCHOR_ANN)
post("LIVE", live, True)
post("ANN", ann, False)

with io.open(SRC_LIVE, "w", encoding="utf-8", newline="\n") as f:
    f.write(live)
with io.open(SRC_ANN, "w", encoding="utf-8", newline="\n") as f:
    f.write(ann)
print("LIVE %d -> %d bytes" % (bl, len(live)))
print("ANN  %d -> %d bytes" % (ba, len(ann)))
print("sha256 LIVE", hashlib.sha256(live.encode("utf-8")).hexdigest())
print("sha256 ANN ", hashlib.sha256(ann.encode("utf-8")).hexdigest())
print("ALL EDIT POSTCONDITIONS OK")
