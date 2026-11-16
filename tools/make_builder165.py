#!/usr/bin/env python3
"""Build the round-165 build script from the round-164 one (the night audit: the cards, the game's caster and ally
target rules, the WW ground cast, the two sweep ranges).

No count gate moves (946 entries, 1,003 keys, 417 range_real fields, 56 target classes). Adds one gate:
  * USAGE_TEXT and ATARGET_TEXT REGENERATED from the game data (tools/gen_usage_keys.py) and equal to the shipped text;
  * every family an entry rides has a card sentence (FOURTH.CARD_TIP), and the badge shows it (STEP 5b);
  * the caster-rule gate first in try_pair, the ally-target gate first in ab_filter_ok;
  * the WW ground-only picks reach the enemy-ground cast form;
  * every range_real an entry carries has its 70% bound in FOURTH.ENEMY_CAST (the round-164 sweeps had none), and the
    two new constants obey floor(real x 0.70)."""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_breaths_harness163\build_and_install164.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_night_audit_harness164\build_and_install165.py"
ANCHOR = ('print("ROUND 164 GATE OK: the charge waves, the cones and the sweeps wired and unarmed; the caster no longer blocks its "\n'
          '      "own wave; WW_NOMELEE matches the game")\n')
ADD = ANCHOR + r'''# ROUND 165: the night audit (2026-11-17).
import gen_usage_keys as _g165
_u165 = _g165.derive(script_txt)
_t165 = _g165.derive_target(script_txt)
assert ('FOURTH.USAGE_TEXT = "%s"\n' % _g165.text(_u165)) in script_txt, \
    "BUILD REFUSED (round 165): the USAGE table differs from the game data"
assert ('FOURTH.ATARGET_TEXT = "%s"\n' % _g165.target_text(_t165)) in script_txt, \
    "BUILD REFUSED (round 165): the ATARGET table differs from the game data"
_card165 = script_txt.split("FOURTH.CARD_TIP = {", 1)[1].split("\n}", 1)[0]
_used165 = set(re.findall(r'trigger = "([a-z_0-9]+)"', script_txt.split("\nlocal ABILITIES = {", 1)[1].split("\n}\n", 1)[0]))
_miss165 = sorted(f for f in _used165 if ("\n\t%s = \"" % f) not in _card165)
assert not _miss165, "BUILD REFUSED (round 165): families without a card sentence: %s" % _miss165
assert "\t\tif not FOURTH.usage_ok(unit, ability, ui_id) then return nil end\n" in script_txt \
    and "\tif not FOURTH.ab_atarget_ok(unit) then return false end\n" in script_txt \
    and '\t\tor (FOURTH.eg_arm == "ww" and FOURTH.eg_ground == true) then\n' in script_txt \
    and "state.badge:SetTooltipText(ability.card, true)" in script_txt, \
    "BUILD REFUSED (round 165): a gate, the ground line or the badge card is missing"
_ec165 = script_txt.split("FOURTH.ENEMY_CAST = {", 1)[1].split("\n}", 1)[0]
_have165 = set(int(x) for x in re.findall(r"\[(\d+)\]\s*=", _ec165))
_rr165 = set(int(float(x)) for x in re.findall(r"\n\t\trange_real = ([\d.]+)", script_txt))
assert _rr165 <= _have165, "BUILD REFUSED (round 165): range_real without a 70%% bound: %s" % sorted(_rr165 - _have165)
for _r165 in (3, 6):
    assert ("FOURTH.ENEMY_CAST_R%-3d = %d " % (_r165, int(_r165 * 0.70 + 1e-9))) in script_txt, \
        "70%% rule broken for %d m" % _r165
print("ROUND 165 GATE OK: USAGE (%d keys) and ATARGET (%d keys) match the game; %d families carry a card; the gates, "
      "the ground line and the badge card are in place; every range_real has its 70%% bound"
      % (len(_u165), len(_t165), len(_used165)))
'''
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1, src.count(ANCHOR)
src = src.replace(ANCHOR, ADD)
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
