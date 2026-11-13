#!/usr/bin/env python3
"""Write tools/make_xlsx_v35.py from make_xlsx_v34.py (round 143, open batch 2)."""
import re

T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\make_xlsx_v34.py", encoding="utf-8").read()
HEAD = '''#!/usr/bin/env python3
"""Build WH3_abilities_master_v35_2026-11-13.xlsx from v34 - round 143: open batch 2.

(1) 11 rows NOT IMPLEMENTED -> IMPLEMENTED: The Curse of Anraheir (3 keys), Transmutation of Lead, Soulblight
    (Doomfire), The Soulstealer, Squig Thinkin', Spinning Loons, The Loons of Eight Peaks on enemy_ground_melee; Curse
    of Djaf on the NEW enemy_ground_shooting; Soulblight (Handmaidens) on melee_unwavering.
(2) Implemented 756 -> 767 rows / keys; not implemented among the included 367 -> 356. The mod 712 entries / 767 keys;
    67 -> 68 families: the Numbers trigger table gains one row (bombardment block 113 -> 114). Definitions: title v35,
    the two count rows, section 32. Changelog: a v35 row.
v1-v34 are never opened for writing.
"""
'''
s = HEAD + s[s.index("import sys as _sys"):]
s = s.replace(r'docs\WH3_abilities_master_v34_2026-11-13.xlsx"', r'docs\WH3_abilities_master_v35_2026-11-13.xlsx"')
s = s.replace(r'docs\WH3_abilities_master_v33_2026-11-13.xlsx"', r'docs\WH3_abilities_master_v34_2026-11-13.xlsx"')
i0 = s.index('RULE = "user ruling 2026-11-13 (open batch 1); "')
i1 = s.index("assert not os.path.exists(DST), DST")
TEXTS = r'''RULE = "user ruling 2026-11-13 (open batch 2); "


def egm(bound, real, extra=""):
    return ("enemy_ground_melee: not routing; enumerate the main enemy army; keep enemies alive (>0 men), validity not "
            "false, FIGHTING (is_in_melee() == true) and within the ability's own 70%% bound (%d m of %d m; "
            "unit:unit_distance only - never unit_in_range)%s; pick the CLOSEST; re-fetch the caster controller AND the "
            "enemy the SAME tick; re-check (alive + still in melee + still within the bound) immediately before the cast "
            "and skip if it lapsed; cast perform_special_ability_ground(key, ENEMY:position(), 0, 0) - the position is "
            "the ENEMY's, never the caster's; " % (bound, real, extra) + RULE + "\"Fighting enemy\"; " + SHARED_TAIL)


DJAF = ("enemy_ground_shooting: not routing; the enemy_missile_shooting pick (main enemy army; alive; validity not false; "
        "target class missile; SHOOTING = its ammo_left() dropped within ENEMY_AMMO_FRESH_S = 2 s and the last drop lies "
        "inside the firing-flag window; an unreadable enemy ammunition never fires; not in melee; within the bound; the "
        "closest wins); bound: 70 m (70% of the ability's 100 m reach); cast target: the GROUND under that enemy "
        "(perform_special_ability_ground at the ENEMY's position); pre-cast re-check: still alive, shooting, not in melee "
        "and within the bound; " + RULE + "\"Shooting enemy\"; " + SHARED_TAIL)
HAND = ("melee_unwavering: not routing; is_in_melee(); is_wavering() must NOT be true - false and unreadable both pass "
        "(fail-open morale); cast target: self; " + RULE + "\"In melee\"; " + SHARED_TAIL)
NF = "; target class not_flying (live is_currently_flying() must read exactly false)"
NEW = {"wh2_dlc16_spell_bound_the_curse_of_anraheir": ("enemy_ground_melee", egm(140, 200)),
       "wh3_main_spell_bound_the_curse_of_anraheir": ("enemy_ground_melee", egm(140, 200)),
       "wh_dlc05_spell_bound_the_curse_of_anraheir": ("enemy_ground_melee", egm(140, 200)),
       "wh3_main_spell_bound_transmutation_of_lead": ("enemy_ground_melee", egm(140, 200)
                                                      + " GATES: in-flight hold 7 s (5 s wind-up + 2 s)."),
       "wh2_dlc10_spell_bound_soulblight": ("enemy_ground_melee", egm(140, 200)
                                            + " GATES: charge hold 90 s (2 uses); in-flight hold 5 s (3 s wind-up + 2 s)."),
       "wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer": ("enemy_ground_melee", egm(70, 100)
                                                                 + " GATES: in-flight hold 5 s (3 s wind-up + 2 s)."),
       "wh2_dlc09_character_abilities_curse_of_djaf": ("enemy_ground_shooting", DJAF),
       "wh3_dlc29_spell_bound_soulblight": ("melee_unwavering", HAND
                                            + " GATES: charge hold 45 s (2 uses); in-flight hold 3 s (1 s wind-up + 2 s)."),
       "wh3_dlc26_character_abilities_squig_thinkin": ("enemy_ground_melee", egm(52, 75)),
       "wh_main_unit_abilities_spinning_loons": ("enemy_ground_melee", egm(17, 25, NF) + " GATES: charge hold 30 s (3 uses)."),
       "wh_dlc06_unit_abilities_the_loons_of_eight_peaks": ("enemy_ground_melee", egm(17, 25, NF)
                                                            + " GATES: charge hold 30 s (3 uses)."),
       }

'''
s = s[:i0] + TEXTS + s[i1:]


def cut(s, start, end, new):
    a = s.index(start)
    b = s.index(end, a)
    return s[:a] + new + s[b:]


R = [
    ('    elif ks == ["wh_main_unit_abilities_blooood"]:\n'
     '        assert str(ws.cell(row=r, column=21).value) == "self_running"\n'
     '        ws.cell(row=r, column=21).value = "self_moving"\n'
     '        ws.cell(row=r, column=22).value = MOVING\n'
     '        n_b += 1\n', ""),
    ("assert (n_new, n_b) == (6, 1), (n_new, n_b)", "assert (n_new, n_b) == (11, 0), (n_new, n_b)"),
    ("(1800, 756, 756)", "(1800, 767, 767)"),
    ("assert NOT_IMPL_IN == 367", "assert NOT_IMPL_IN == 356"),
    ("(len(entries), len(fam_by_key)) == (703, 756)", "(len(entries), len(fam_by_key)) == (712, 767)"),
    ('assert len(trig) == 67 and trig["ally_ammo_low"] == 3 and trig["self_running"] == 0, (len(trig), trig["ally_ammo_low"])',
     'assert len(trig) == 68 and trig["enemy_ground_shooting"] == 1 and trig["enemy_ground_melee"] == 74 '
     'and trig["melee_unwavering"] == 307, (len(trig),)'),
    ('assert n.cell(row=110, column=1).value == "Bombardment set (COMPLETE - round 108)"',
     'assert n.cell(row=113, column=1).value == "Bombardment set (COMPLETE - round 108)"'),
    ("n.insert_rows(108, 3)\nassert n.cell(row=113, column=1).value",
     "n.insert_rows(111, 1)\nassert n.cell(row=114, column=1).value"),
    ('replace("750 implemented", "756 implemented")', 'replace("756 implemented", "767 implemented")'),
    ("for r in range(44, 112):", "for r in range(44, 113):"),
    ('assert 44 + len(fam_sorted) == 111\nn.cell(row=111, column=2).value = "TOTAL (67 families)"\n'
     'n.cell(row=111, column=3).value = sum(trig.values())\nn.cell(row=111, column=4).value = sum(trig_keys.values())',
     'assert 44 + len(fam_sorted) == 112\nn.cell(row=112, column=2).value = "TOTAL (68 families)"\n'
     'n.cell(row=112, column=3).value = sum(trig.values())\nn.cell(row=112, column=4).value = sum(trig_keys.values())'),
    ('startswith("DEFINITIONS - WH3 ability master v33")', 'startswith("DEFINITIONS - WH3 ability master v34")'),
    ('"DEFINITIONS - WH3 ability master v34 (2026-11-13)"', '"DEFINITIONS - WH3 ability master v35 (2026-11-13)"'),
    ('assert "(1,050 keys, of which 373 are in the wheel)" in r12.value\n'
     'r12.value = r12.value.replace("(1,050 keys, of which 373 are in the wheel)", "(1,044 keys, of which 367 are in the wheel)")',
     'assert "(1,044 keys, of which 367 are in the wheel)" in r12.value\n'
     'r12.value = r12.value.replace("(1,044 keys, of which 367 are in the wheel)", "(1,033 keys, of which 356 are in the wheel)")'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)

s = cut(s, '    "(v34 - ROUND 142', "for r, num, label, abs_, p1, p2 in", (
    '    "(v35 - ROUND 143: open batch 2. The Curse of Anraheir (3 keys), Transmutation of Lead, Soulblight (Doomfire), The "\n'
    '    "Soulstealer, Squig Thinkin\', Spinning Loons and The Loons of Eight Peaks on enemy_ground_melee; Curse of Djaf on "\n'
    '    "the NEW enemy_ground_shooting; Soulblight (Handmaidens) on melee_unwavering. Implemented 756 + 11 = 767 rows / 767 "\n'
    '    "keys; not implemented among the included 367 - 11 = 356. The mod: 712 entries / 767 keys / 68 trigger families.)")\n'))
s = cut(s, '    "Reconciliation (v34)', "n.cell(row=42, column=1).value = (", (
    '    "Reconciliation (v35): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 767 + not "\n'
    '    "implemented 356 = 1,123. The mod\'s ABILITIES table is 712 entries / 767 keys, and the join mod-key -> \'Ability "\n'
    '    "key(s)\' returns 767 / 767 with ZERO unmatched keys in either direction. 703 + 9 (round 143, open batch 2) = 712 "\n'
    '    "entries; 756 + 11 = 767 keys. NO army-bar (army_spec) key in the mod: 0.")\n'))
s = cut(s, '    "Trigger families after round 142', "for r in range(44, 113):", (
    '    "Trigger families after round 143 - re-counted from the mod\'s own ABILITIES table: 68 families / 712 entries / 767 "\n'
    '    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 143: enemy_ground_melee 67 -> 74 "\n'
    '    "entries; melee_unwavering 306 -> 307; the NEW enemy_ground_shooting (1).")\n'))
s = cut(s, "old11 = ", "r12 = d.cell(row=12, column=2)", (
    'old11 = ("756 keys across 756 numbered rows (rounds 122-123 added 21, round 130 added 2, round 131 removed the 9 "\n'
    '         "stances, round 134 removed the 2 Thunderburner keys, round 142 added 6)")\n'
    'assert old11 in r11.value\n'
    'r11.value = r11.value.replace(old11, "767 keys across 767 numbered rows (rounds 122-123 added 21, round 130 added 2, "\n'
    '                              "round 131 removed the 9 stances, round 134 removed the 2 Thunderburner keys, round 142 "\n'
    '                              "added 6, round 143 added 11)")\n'))
s = cut(s, "sec = [", "for i, (a, b) in enumerate(sec):", (
    'sec = [\n'
    '    ("32. ROUND 143 - OPEN BATCH 2 (v35)", None),\n'
    '    ("THE RULINGS (2026-11-13)", "The Curse of Anraheir, Transmutation of Lead, Soulblight (Doomfire), The Soulstealer: "\n'
    '     "\\"Fighting enemy, all four\\". Curse of Djaf: \\"Shooting enemy\\". Soulblight (Handmaidens): \\"In melee\\". Squig "\n'
    '     "Thinkin\', Spinning Loons, The Loons of Eight Peaks: \\"Fighting enemy, all three\\"."),\n'
    '    ("THE NEW FAMILY", "enemy_ground_shooting (Curse of Djaf): the Missile Mirror pick, placed on the enemy\'s ground. "\n'
    '     "The 25 m reach of the fanatic releases -> FOURTH.ENEMY_CAST_R25 = 17; the loons carry target_class not_flying."),\n'
    '    ("THE ARITHMETIC", "Implemented 756 + 11 = 767 rows / keys; not implemented among the included 367 - 11 = 356. "\n'
    '     "The mod 703 + 9 = 712 entries / 767 keys; 68 families."),\n'
    ']\n'))
s = cut(s, 'ch.cell(row=r, column=2).value = "v34"', "wb.save(DST)", (
    'ch.cell(row=r, column=2).value = "v35"\n'
    'ch.cell(row=r, column=3).value = (\n'
    '    "ROUND 143. Open batch 2: The Curse of Anraheir (3 keys), Transmutation of Lead, Soulblight (Doomfire), The "\n'
    '    "Soulstealer, Squig Thinkin\', Spinning Loons, The Loons of Eight Peaks on enemy_ground_melee; Curse of Djaf on the "\n'
    '    "NEW enemy_ground_shooting; Soulblight (Handmaidens) on melee_unwavering. 756 -> 767 implemented; 367 -> 356 not "\n'
    '    "implemented. Mod 712 / 767 / 68 families. SHIPPED: installed pack md5 %s; harness 142 full suite 6,194 checks / "\n'
    '    "0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))\n'
    'ch.cell(row=r, column=4).value = "user rulings 2026-11-13 (open batch 2); xlsx v35 supersedes v34; v1-v34 byte-unchanged."\n'))
assert "\u2014" not in s
left = [m.start() for m in re.finditer(r"\bv33\b", s)]
assert not left, [s[x - 40:x + 20] for x in left]
open(T + r"\make_xlsx_v35.py", "w", encoding="utf-8", newline="\n").write(s)
print("make_xlsx_v35 written")
