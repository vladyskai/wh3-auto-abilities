#!/usr/bin/env python3
"""Write tools/make_xlsx_v36.py from make_xlsx_v35.py (round 144, open batch 3)."""
import re

T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\make_xlsx_v35.py", encoding="utf-8").read()
HEAD = '''#!/usr/bin/env python3
"""Build WH3_abilities_master_v36_2026-11-13.xlsx from v35 - round 144: open batch 3 (the rest of group C).

(1) 10 rows NOT IMPLEMENTED -> IMPLEMENTED: Hag's Denial (NEW self_last_stand), Ruinshelter and Banner of Hellfire
    (melee_unwavering), Rock Bottom (NEW self_out_of_ammo), Morikhane (under_fire), Hunter's Call
    (melee_or_wavering_aura), Icon of the King (NEW health_aura_self_undead), The Gold Standard (NEW ally_hurt_melee),
    Ghostly Howl (NEW enemy_wavering), Petrifying Gaze (enemy_fast_near_ally).
(2) 3 rows NOT IMPLEMENTED -> SKIPPED (user decision): Storm of Blades and Whirling Death (stances), Cloak of the Dunes
    (stealth).
(3) Implemented 767 -> 777 rows / keys; not implemented among the included 356 -> 346 (24 -> 27 skipped). The mod 722
    entries / 777 keys; 68 -> 73 families: the Numbers trigger table gains five rows (bombardment block 114 -> 119).
    Definitions: title v36, the two count rows, section 33. Changelog: a v36 row.
v1-v35 are never opened for writing.
"""
'''
s = HEAD + s[s.index("import sys as _sys"):]
s = s.replace(r'docs\WH3_abilities_master_v35_2026-11-13.xlsx"', r'docs\WH3_abilities_master_v36_2026-11-13.xlsx"')
s = s.replace(r'docs\WH3_abilities_master_v34_2026-11-13.xlsx"', r'docs\WH3_abilities_master_v35_2026-11-13.xlsx"')
i0 = s.index('RULE = "user ruling 2026-11-13 (open batch 2); "')
i1 = s.index("assert not os.path.exists(DST), DST")
TEXTS = r'''RULE = "user ruling 2026-11-13 (open batch 3); "
GENERIC = ("shared gate: unit alive (>0 men); this (unit, ability) pair must be armed; readiness = "
           "can_perform_special_ability on the owned key; 2 s per-pair guard; engine cooldown refusal back-off; "
           "pre-fire unit-alive check; cast.")
LAST = ("self_last_stand: not routing; the unit's OWN health readable and at or below FOURTH.LAST_STAND_PCT = 10% (an "
        "unreadable health never fires) AND the unit in melee (is_in_melee() exactly true) OR under missile fire "
        "(is_under_missile_attack() exactly true); cast target: self; " + RULE + "\"10%, melee or fire\" (Cannot Die "
        "and damage resistance +40 for 44 s, one use); " + SHARED_TAIL)
MU = ("melee_unwavering: not routing; is_in_melee(); is_wavering() must NOT be true - false and unreadable both pass "
      "(fail-open morale); cast target: self; " + RULE + "\"in melee\"; " + SHARED_TAIL)
AMMO0 = ("self_out_of_ammo: not routing; the unit's OWN ammo_left() readable and 0 (no ammunition left); cast target: "
         "self; " + RULE + "\"wait until no ammo left\" (it refills 30% of its own ammunition for 350 damage to itself); "
         + SHARED_TAIL + " GATES: in-flight hold 3 s (1 s wind-up + 2 s).")
MORI = ("under_fire: not routing; the unit itself under missile fire (is_under_missile_attack() exactly true); cast "
        "target: self (no aura: the reflection covers the wearer); " + RULE + "\"under fire\"; " + SHARED_TAIL
        + " GATES: in-flight hold 3 s (1 s wind-up + 2 s).")
HUNT = ("melee_or_wavering_aura: not routing; the unit itself in melee or WAVERING, or a friendly unit (alive, not "
        "routing) within the aura bound in melee or wavering; bound: 24 m (70% of the ability's 35 m effect_range); "
        "cast target: self (the aura is centred on it); " + RULE + "like Stand Your Ground (melee defence +24 and "
        "Unbreakable); " + SHARED_TAIL + " GATES: charge hold 120 s (3 uses).")
ICON = ("health_aura_self_undead: not routing; the OWNER or a friendly unit within 24 m (70% of the ability's 35 m "
        "effect_range) at or below 75% health that is a NON-LIVING unit (its type in the GENERATED undead set, "
        "tools/gen_undead_keys.py; the game's invalid-target flag living_unit); the lowest health wins; cast target: "
        "self (the aura is centred on it); pre-cast re-check: still alive, still at or below 75%, still non-living; "
        + RULE + "\"heals only non-living allies\"; " + SHARED_TAIL + " GATES: charge hold 120 s (2 uses).")
GOLD = ("ally_hurt_melee: not routing; the OWNER or a friendly unit within 70 m (70% of the ability's 100 m "
        "target_intercept_range) at or below 75% health AND in melee (is_in_melee() exactly true); the lowest health "
        "wins; cast target: that unit; pre-cast re-check: still alive, still at or below 75%, still in melee, still in "
        "range; " + RULE + "\"the lowest-health ally IN MELEE\" (invulnerable for 13 s); " + SHARED_TAIL)
HOWL = ("enemy_wavering: not routing; enumerate the main enemy army; keep enemies alive (>0 men), validity not false, "
        "WAVERING (is_wavering() exactly true; the game only lets Ghostly Howl target an enemy below half morale, "
        "invalid-target flag morale_is_higher_than_half_of_base_morale) and within 52 m (70% of the ability's 75 m "
        "target_intercept_range; unit_distance only); the closest wins; cast target: that enemy unit; pre-cast "
        "re-check: still alive, still wavering, still within the bound; " + RULE + "\"the closest wavering enemy\"; "
        + SHARED_TAIL + " GATES: in-flight hold 5 s (3 s wind-up + 2 s).")
GAZE = ("enemy_fast_near_ally: not routing; the closest enemy within 35 m (70% of the ability's 50 m "
        "target_intercept_range) that is MOVING with a run speed (fast_speed()) of 5 m/s or more and is within 40 m of "
        "one of our units (the user's settings, round 135); cast target: that enemy; pre-cast re-check: still moving "
        "fast near our units; " + RULE + "the immobiliser ruling of round 136 (\"fast enemy\"); " + SHARED_TAIL
        + " GATES: charge hold 120 s (2 uses).")
NEW = {"wh3_dlc24_unit_abilities_hags_denial": ("self_last_stand", LAST),
       "wh2_dlc15_unit_abilities_mimic_ruinshelter": ("melee_unwavering", MU),
       "wh3_main_banner_abilities_banner_of_hellfire": ("melee_unwavering", MU),
       "wh2_dlc15_unit_abilities_rock_bottom": ("self_out_of_ammo", AMMO0),
       "wh3_dlc29_item_abilities_morikhane_the_black_armour": ("under_fire", MORI),
       "wh2_dlc13_character_ability_hunters_call": ("melee_or_wavering_aura", HUNT),
       "wh3_dlc29_item_abilities_icon_of_the_king": ("health_aura_self_undead", ICON),
       "wh3_dlc25_item_abilities_the_gold_standard": ("ally_hurt_melee", GOLD),
       "wh3_dlc29_hero_active_ghostly_howl": ("enemy_wavering", HOWL),
       "wh3_dlc24_unit_passive_petrifying_gaze": ("enemy_fast_near_ally", GAZE),
       }
STANCE = ("skipped (user decision 2026-11-13: a stance - no end time, 1 s recharge, on the same units as The Shadow's "
          "Coil and Woven Mist; round 131: stances are not automated until a stance chooser weighs the unit's mutually "
          "exclusive stances)")
SKIP = {"wh_dlc05_unit_abilities_storm_of_blades": STANCE,
        "wh2_dlc16_unit_abilities_whirling_death": STANCE,
        "wh2_dlc09_item_abilities_cloak_of_the_dunes": (
            "skipped (user decision 2026-11-13, applying the 2026-10-09 family ruling: stealth / escape effects "
            "(Stalk, Unspottable) get no automatic logic)")}

'''
s = s[:i0] + TEXTS + s[i1:]


def cut(s, start, end, new):
    a = s.index(start)
    b = s.index(end, a)
    return s[:a] + new + s[b:]


s = cut(s, "n_new = n_b = 0\n", "rows = [(r, keys_of(r)", (
    "n_new = n_skip = 0\n"
    "for r in range(2, ws.max_row + 1):\n"
    "    ks = keys_of(r)\n"
    "    if len(ks) == 1 and (ks[0] in NEW or ks[0] in SKIP):\n"
    "        assert str(ws.cell(row=r, column=18).value) == \"IN-WHEEL\" and str(ws.cell(row=r, column=20).value) == \"NOT IMPLEMENTED\", ks\n"
    "        if ks[0] in NEW:\n"
    "            fam, text = NEW[ks[0]]\n"
    "            ws.cell(row=r, column=20).value = \"IMPLEMENTED\"\n"
    "            ws.cell(row=r, column=21).value = fam\n"
    "            ws.cell(row=r, column=22).value = text\n"
    "            n_new += 1\n"
    "        else:\n"
    "            ws.cell(row=r, column=19).value = SKIP[ks[0]]\n"
    "            ws.cell(row=r, column=20).value = \"SKIPPED (user decision)\"\n"
    "            ws.cell(row=r, column=21).value = \"-\"\n"
    "            ws.cell(row=r, column=22).value = \"-\"\n"
    "            n_skip += 1\n"
    "assert (n_new, n_skip) == (10, 3), (n_new, n_skip)\n\n"))
R = [
    ("(1800, 767, 767)", "(1800, 777, 777)"),
    ("assert NOT_IMPL_IN == 356", "assert NOT_IMPL_IN == 346\nassert sum(1 for x in rows if x[3] == \"SKIPPED (user decision)\") == 27"),
    ("(len(entries), len(fam_by_key)) == (712, 767)", "(len(entries), len(fam_by_key)) == (722, 777)"),
    ('assert len(trig) == 68 and trig["enemy_ground_shooting"] == 1 and trig["enemy_ground_melee"] == 74 '
     'and trig["melee_unwavering"] == 307, (len(trig),)',
     'assert len(trig) == 73 and trig["melee_unwavering"] == 309 and trig["self_last_stand"] == 1 '
     'and trig["enemy_fast_near_ally"] == 8 and trig["under_fire"] == 4, (len(trig),)'),
    ('assert n.cell(row=113, column=1).value == "Bombardment set (COMPLETE - round 108)"',
     'assert n.cell(row=114, column=1).value == "Bombardment set (COMPLETE - round 108)"'),
    ("n.insert_rows(111, 1)\nassert n.cell(row=114, column=1).value",
     "n.insert_rows(112, 5)\nassert n.cell(row=119, column=1).value"),
    ('replace("756 implemented", "767 implemented")', 'replace("767 implemented", "777 implemented")'),
    ("for r in range(44, 113):", "for r in range(44, 118):"),
    ('assert 44 + len(fam_sorted) == 112\nn.cell(row=112, column=2).value = "TOTAL (68 families)"\n'
     'n.cell(row=112, column=3).value = sum(trig.values())\nn.cell(row=112, column=4).value = sum(trig_keys.values())',
     'assert 44 + len(fam_sorted) == 117\nn.cell(row=117, column=2).value = "TOTAL (73 families)"\n'
     'n.cell(row=117, column=3).value = sum(trig.values())\nn.cell(row=117, column=4).value = sum(trig_keys.values())'),
    ('startswith("DEFINITIONS - WH3 ability master v34")', 'startswith("DEFINITIONS - WH3 ability master v35")'),
    ('"DEFINITIONS - WH3 ability master v35 (2026-11-13)"', '"DEFINITIONS - WH3 ability master v36 (2026-11-13)"'),
    ('assert "(1,044 keys, of which 367 are in the wheel)" in r12.value\n'
     'r12.value = r12.value.replace("(1,044 keys, of which 367 are in the wheel)", "(1,033 keys, of which 356 are in the wheel)")',
     'assert "(1,033 keys, of which 356 are in the wheel)" in r12.value\n'
     'r12.value = r12.value.replace("(1,033 keys, of which 356 are in the wheel)", "(1,023 keys, of which 346 are in the wheel)")'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)

s = cut(s, '    "(v35 - ROUND 143', "for r, num, label, abs_, p1, p2 in", (
    '    "(v36 - ROUND 144: open batch 3. Hag\'s Denial on the NEW self_last_stand; Ruinshelter and Banner of Hellfire on "\n'
    '    "melee_unwavering; Rock Bottom on the NEW self_out_of_ammo; Morikhane on under_fire; Hunter\'s Call on "\n'
    '    "melee_or_wavering_aura; Icon of the King on the NEW health_aura_self_undead; The Gold Standard on the NEW "\n'
    '    "ally_hurt_melee; Ghostly Howl on the NEW enemy_wavering; Petrifying Gaze on enemy_fast_near_ally. Storm of Blades, "\n'
    '    "Whirling Death and Cloak of the Dunes SKIPPED. Implemented 767 + 10 = 777 rows / 777 keys; not implemented among "\n'
    '    "the included 356 - 10 = 346 (27 skipped). The mod: 722 entries / 777 keys / 73 trigger families.)")\n'))
s = cut(s, '    "Reconciliation (v35)', "n.cell(row=42, column=1).value = (", (
    '    "Reconciliation (v36): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 777 + not "\n'
    '    "implemented 346 = 1,123. The mod\'s ABILITIES table is 722 entries / 777 keys, and the join mod-key -> \'Ability "\n'
    '    "key(s)\' returns 777 / 777 with ZERO unmatched keys in either direction. 712 + 10 (round 144, open batch 3) = 722 "\n'
    '    "entries; 767 + 10 = 777 keys. NO army-bar (army_spec) key in the mod: 0.")\n'))
s = cut(s, '    "Trigger families after round 143', "for r in range(44, 118):", (
    '    "Trigger families after round 144 - re-counted from the mod\'s own ABILITIES table: 73 families / 722 entries / 777 "\n'
    '    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 144: melee_unwavering 307 -> 309, "\n'
    '    "under_fire 3 -> 4, melee_or_wavering_aura 1 -> 2, enemy_fast_near_ally 7 -> 8; the NEW self_last_stand, "\n'
    '    "self_out_of_ammo, health_aura_self_undead, ally_hurt_melee and enemy_wavering (1 each).")\n'))
s = cut(s, "old11 = (", "r12 = d.cell(row=12, column=2)", (
    'old11 = ("767 keys across 767 numbered rows (rounds 122-123 added 21, round 130 added 2, round 131 removed the 9 "\n'
    '         "stances, round 134 removed the 2 Thunderburner keys, round 142 added 6, round 143 added 11)")\n'
    'assert old11 in r11.value\n'
    'r11.value = r11.value.replace(old11, "777 keys across 777 numbered rows (rounds 122-123 added 21, round 130 added 2, "\n'
    '                              "round 131 removed the 9 stances, round 134 removed the 2 Thunderburner keys, round 142 "\n'
    '                              "added 6, round 143 added 11, round 144 added 10)")\n'))
s = cut(s, "sec = [", "for i, (a, b) in enumerate(sec):", (
    'sec = [\n'
    '    ("33. ROUND 144 - OPEN BATCH 3 (v36)", None),\n'
    '    ("THE RULINGS (2026-11-13)", "Hag\'s Denial: \\"10%, melee or fire\\". Rock Bottom: \\"wait until no ammo left\\". "\n'
    '     "Ruinshelter in melee; Morikhane under fire; Hunter\'s Call, Icon of the King, The Gold Standard, Banner of "\n'
    '     "Hellfire, Ghostly Howl, Petrifying Gaze as proposed. Storm of Blades, Whirling Death (stances) and Cloak of the "\n'
    '     "Dunes (stealth): skipped."),\n'
    '    ("THE NEW FAMILIES", "self_last_stand (FOURTH.LAST_STAND_PCT = 10), self_out_of_ammo, health_aura_self_undead "\n'
    '     "(the generated undead set; re-check mode undead), ally_hurt_melee (re-check mode melee), enemy_wavering "\n'
    '     "(re-check mode wavering)."),\n'
    '    ("THE ARITHMETIC", "Implemented 767 + 10 = 777 rows / keys; not implemented among the included 356 - 10 = 346 "\n'
    '     "(24 + 3 = 27 skipped). The mod 712 + 10 = 722 entries / 777 keys; 73 families."),\n'
    ']\n'))
s = cut(s, 'ch.cell(row=r, column=2).value = "v35"', "wb.save(DST)", (
    'ch.cell(row=r, column=2).value = "v36"\n'
    'ch.cell(row=r, column=3).value = (\n'
    '    "ROUND 144. Open batch 3: Hag\'s Denial, Ruinshelter, Rock Bottom, Morikhane, Hunter\'s Call, Icon of the King, The "\n'
    '    "Gold Standard, Banner of Hellfire, Ghostly Howl, Petrifying Gaze IMPLEMENTED (5 new families); Storm of Blades, "\n'
    '    "Whirling Death, Cloak of the Dunes SKIPPED. 767 -> 777 implemented; 356 -> 346 not implemented (27 skipped). Mod "\n'
    '    "722 / 777 / 73 families. SHIPPED: installed pack md5 %s; harness 143 full suite 6,273 checks / 0 failures."\n'
    '    % os.environ.get("WH3_PACK_MD5", "PENDING"))\n'
    'ch.cell(row=r, column=4).value = "user rulings 2026-11-13 (open batch 3); xlsx v36 supersedes v35; v1-v35 byte-unchanged."\n'))
assert "\u2014" not in s
left = [m.start() for m in re.finditer(r"\bv34\b", s)]
assert not left, [s[x - 40:x + 20] for x in left]
open(T + r"\make_xlsx_v36.py", "w", encoding="utf-8", newline="\n").write(s)
print("make_xlsx_v36 written")
