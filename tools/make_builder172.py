#!/usr/bin/env python3
"""Build the round-172 build script from the round-171 one (rows 1, 3 and 5 of the low score review as RULED in the doc).

No count moves (939 entries, 994 keys). ROUND 172 GATE:
  * army_charge_or_melee wired, Waaagh! (the wh_main key) on it, Horn of the Wild Hunt alone on army_charge, Ursun's
    Roar's charge key alone on aura_charge;
  * the army count helper exists and takes N = min(3, living units) (the ruling's fallback);
  * Ursun's Roar's evaluator reads wavering; AURA_CHARGE_ALLIES and its card token are gone;
  * the three cards carry the rulings' sentences."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_review_rows_harness170\build_and_install171.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_ruled_rows_harness171\build_and_install172.py"
ANCHOR = ('print("ROUND 171 GATE OK: CONTACT (%d land units) matches the game; six families wired; Ursun\'s Roar and Waaagh! split; "\n'
          '      "nine abilities closed; the fresh-contact tracker polled" % len(_gc171.derive()))\n')
ADD = ANCHOR + r'''# ROUND 172: rows 1, 3 and 5 of the low score review as RULED in the doc (2026-11-18).
assert "\tarmy_charge_or_melee = FOURTH.evaluate_army_charge_or_melee," in script_txt, \
    "BUILD REFUSED (round 172): army_charge_or_melee is not wired"
assert '{ marker = "waaagh_army", name = "Waaagh!", trigger = "army_charge_or_melee",' in script_txt, \
    "BUILD REFUSED (round 172): Waaagh! is not on army charge or army melee"
assert script_txt.count('trigger = "army_charge"') == 1 and script_txt.count('trigger = "aura_charge"') == 1 \
    and script_txt.count('trigger = "army_charge_or_melee"') == 1, "BUILD REFUSED (round 172): the family counts moved"
assert "\tc.need = math.min(FOURTH.ARMY_CHARGE_MIN, c.living)\n" in script_txt, \
    "BUILD REFUSED (round 172): the army count lost the smaller-army fallback"
_ur172 = script_txt.split("function FOURTH.evaluate_aura_charge(unit, routing)", 1)[1].split("\nend\n", 1)[0]
assert _ur172.count("FOURTH.wavering(") == 2, "BUILD REFUSED (round 172): Ursun's Roar does not read wavering"
assert "AURA_CHARGE_ALLIES" not in script_txt.replace("-- ROUND 172: AURA_CHARGE_ALLIES is gone", "") \
    and "{ACA}" not in script_txt, "BUILD REFUSED (round 172): the 2-ally rule is back"
for _c172 in ('\tarmy_charge = "Fires when {ACN}+ of your units charge at once (all of them in a smaller army)",',
              '\tarmy_charge_or_melee = "Fires when {ACN}+ of your units charge or fight at once (all of them in a smaller army)",',
              '\taura_charge = "Fires when it or a nearby ally charges or wavers",'):
    assert _c172 in script_txt, "BUILD REFUSED (round 172): a card sentence differs: " + _c172
print("ROUND 172 GATE OK: Horn (every living unit in a smaller army), Waaagh! (army charge or army melee), "
      "Ursun's Roar (one unit charging or wavering)")
'''
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
