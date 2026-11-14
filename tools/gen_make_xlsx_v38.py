#!/usr/bin/env python3
"""Write tools/make_xlsx_v38.py from make_xlsx_v37.py (round 150: no count changes; 21 rows move to when_ready, the 77
blob rows get the value / standstill text)."""
import re

T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\make_xlsx_v37.py", encoding="utf-8").read()
HEAD = '''#!/usr/bin/env python3
"""Build WH3_abilities_master_v38_2026-11-14.xlsx from v37 - round 150.

(1) The 77 enemy_blob rows: the target is the one whose blast destroys the most enemy value (armour, hit points, live
    value per soldier); AP-heavy attacks never target armour below 50; never while the caster moves.
(2) The 21 Winds of Magic rows move from melee_unwavering to the NEW when_ready.
(3) No count changes: 854 implemented / 269 not implemented (27 skipped); the mod 799 entries / 854 keys; 74 -> 75
    families (the Numbers trigger table gains one row; bombardment block 120 -> 121). Definitions: title v38, section
    35. Changelog: a v38 row.
v1-v37 are never opened for writing.
"""
'''
s = HEAD + s[s.index("import sys as _sys"):]
s = s.replace(r'docs\WH3_abilities_master_v37_2026-11-13.xlsx"', r'docs\WH3_abilities_master_v38_2026-11-14.xlsx"')
s = s.replace(r'docs\WH3_abilities_master_v36_2026-11-13.xlsx"', r'docs\WH3_abilities_master_v37_2026-11-13.xlsx"')


def cut(s, start, end, new):
    a = s.index(start)
    b = s.index(end, a)
    return s[:a] + new + s[b:]


s = cut(s, 'RULE = "user rulings 2026-11-13 (the blob trigger:', "assert not os.path.exists(DST), DST", r'''RULE = ("user rulings 2026-11-13 (the blob trigger: \"A. Density line\", \"10 m\", \"79 open attacks\") and 2026-11-14 "
        "(\"Most value destroyed\"; standstill: \"For now, only the Blob attacks\"); ")
import math as _math
import gen_blob_tables as _GB
_PM2 = _GB.packed_m2()
_SRC_LUA = open(r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua", encoding="utf-8").read()
_KEYS = _GB.keys_in(_SRC_LUA)
assert len(_KEYS) == 77
_BLAST = _GB.blast_table(_KEYS)
_DMG = _GB.damage_table(_KEYS)
_SA = {r["key"]: r for r in _GB.tsv("unit_spec_abil.tsv")}
_FLAGS = {}
for _r in _GB.tsv("special_ability_to_invalid_target_flags_tables.tsv"):
    _v = list(_r.values())
    _FLAGS.setdefault(_v[1], []).append(_v[0])


def _blob_text(k):
    sp = _SA[k]
    rng, blast = float(sp["target_intercept_range"]), _BLAST[k]
    uses, rech, wind = int(float(sp["num_uses"] or -1)), float(sp["recharge_time"] or 0), float(sp["wind_up_time"] or 0)
    xb, xap, heavy = _DMG[k]
    bound = int(_math.floor(rng * 0.70 + 1e-9))
    need = max(1, int(_math.floor(0.5 * _math.pi * blast ** 2 / _PM2 + 0.5)))
    gates = []
    if uses > 1:
        gates.append("charge hold %g s (%d uses)" % (rech, uses))
    if wind > 0:
        gates.append("in-flight hold %g s (%g s wind-up + 2 s)" % (wind + 2, wind))
    nf = "; target class not_flying (the game's flying_currently flag)" if "flying_currently" in _FLAGS.get(k, []) else ""
    ap = ("; AP-HEAVY (armour-piercing at least half of its damage): never targets armour below 50" if heavy else "")
    return ("enemy_blob: not routing; the caster STANDING STILL (is_moving() exactly false: a cast stops a moving "
            "caster); the live map (our units; the enemy INFANTRY we can see: an inf_* class, not in the generated large "
            "set, not flying, at least 10 men, is_visible_to_alliance exactly true); candidates = visible enemy infantry "
            "units within %d m (70%% of the ability's %g m target_intercept_range; unit_distance)%s%s; a candidate is "
            "UNSAFE when any of our units' estimated rectangles comes within the blast radius + 10 m of its rectangle; it "
            "must reach the density line on its own: %d enemy infantry soldiers in the %g m blast (half of a packed "
            "block: 0.5 x pi x %g^2 / %.3f m2); among those, the one whose blast destroys the most enemy VALUE wins: every "
            "enemy block under the blast adds soldiers covered x the share of one soldier a hit kills (blast damage %g "
            "base x (1 - 0.0075 x armour) + %g AP, against the soldier's hit points; armour and hit points generated "
            "from unit_armour_types, battle_entities and land_units) x its live value per soldier (strategic_value / "
            "men); cast target: that enemy unit; pre-cast re-check: the map is rebuilt, the caster still standing, the "
            "target still allowed, safe and on the line; " % (bound, rng, nf, ap, need, blast, blast, _PM2, xb, xap)
            + RULE + SHARED_TAIL + ((" GATES: " + "; ".join(gates) + ".") if gates else ""))


WINDS_TEXT = ("when_ready: no condition (not even routing); the shared gates decide: this (unit, ability) pair must be "
              "armed; readiness = can_perform_special_ability on the owned key; the charge hold for multi-use abilities; "
              "2 s per-pair guard; engine cooldown refusal back-off; pre-fire unit-alive check; cast on self. User "
              "ruling 2026-11-14 for the Winds of Magic abilities: \"All when ready\".")
import round150_value_target as _R150
NEW = {k: ("enemy_blob", _blob_text(k)) for k in _KEYS}
NEW.update({k: ("when_ready", WINDS_TEXT) for k in _R150.WINDS})
WAS = {k: "enemy_blob" for k in _KEYS}
WAS.update({k: "melee_unwavering" for k in _R150.WINDS})

''')
s = cut(s, "n_new = n_skip = 0\n", "rows = [(r, keys_of(r)", '''n_new = 0
for r in range(2, ws.max_row + 1):
    ks = keys_of(r)
    if len(ks) == 1 and ks[0] in NEW:
        assert str(ws.cell(row=r, column=20).value) == "IMPLEMENTED" and str(ws.cell(row=r, column=21).value) == WAS[ks[0]], ks
        fam, text = NEW[ks[0]]
        ws.cell(row=r, column=21).value = fam
        ws.cell(row=r, column=22).value = text
        n_new += 1
assert n_new == 98, n_new

''')
R = [
    ('assert len(trig) == 74 and trig["enemy_blob"] == 77, (len(trig),)',
     'assert len(trig) == 75 and trig["enemy_blob"] == 77 and trig["when_ready"] == 21 and trig["melee_unwavering"] == 288, (len(trig),)'),
    ('assert n.cell(row=119, column=1).value == "Bombardment set (COMPLETE - round 108)"',
     'assert n.cell(row=120, column=1).value == "Bombardment set (COMPLETE - round 108)"'),
    ("n.insert_rows(117, 1)\nassert n.cell(row=120, column=1).value", "n.insert_rows(118, 1)\nassert n.cell(row=121, column=1).value"),
    ('n.cell(row=18, column=1).value = str(n.cell(row=18, column=1).value).replace("777 implemented", "854 implemented")\n', ''),
    ("for r in range(44, 119):", "for r in range(44, 120):"),
    ('assert 44 + len(fam_sorted) == 118\nn.cell(row=118, column=2).value = "TOTAL (74 families)"\n'
     'n.cell(row=118, column=3).value = sum(trig.values())\nn.cell(row=118, column=4).value = sum(trig_keys.values())',
     'assert 44 + len(fam_sorted) == 119\nn.cell(row=119, column=2).value = "TOTAL (75 families)"\n'
     'n.cell(row=119, column=3).value = sum(trig.values())\nn.cell(row=119, column=4).value = sum(trig_keys.values())'),
    ('startswith("DEFINITIONS - WH3 ability master v36")', 'startswith("DEFINITIONS - WH3 ability master v37")'),
    ('"DEFINITIONS - WH3 ability master v37 (2026-11-13)"', '"DEFINITIONS - WH3 ability master v38 (2026-11-14)"'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
s = cut(s, "r11 = d.cell(row=11, column=2)\n", "for r in range(24, 100):", "")
s = cut(s, '    "Date: 2026-11-13     Rule', "for r, num, label, abs_, p1, p2 in", (
    '    "Date: 2026-11-14     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "\n'
    '    "(v38 - ROUND 150: the 77 blob attacks pick the target whose blast destroys the most enemy value and never fire "\n'
    '    "while the caster moves; AP-heavy ones never target armour below 50. The 21 Winds of Magic abilities move to the "\n'
    '    "NEW when_ready. No count change: 854 implemented / 269 not implemented (27 skipped); the mod 799 entries / 854 "\n'
    '    "keys / 75 trigger families.)")\n'))
s = cut(s, '    "Reconciliation (v37)', "n.cell(row=42, column=1).value = (", (
    '    "Reconciliation (v38): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 854 + not "\n'
    '    "implemented 269 = 1,123. The mod\'s ABILITIES table is 799 entries / 854 keys, and the join mod-key -> \'Ability "\n'
    '    "key(s)\' returns 854 / 854 with ZERO unmatched keys in either direction. Round 150 changed triggers only. NO "\n'
    '    "army-bar (army_spec) key in the mod: 0.")\n'))
s = cut(s, '    "Trigger families after round 146', "for r in range(44, 120):", (
    '    "Trigger families after round 150 - re-counted from the mod\'s own ABILITIES table: 75 families / 799 entries / 854 "\n'
    '    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 150: the NEW when_ready (21), "\n'
    '    "melee_unwavering 309 -> 288.")\n'))
s = cut(s, "sec = [", "for i, (a, b) in enumerate(sec):", (
    'sec = [\n'
    '    ("35. ROUND 150 - VALUE TARGETS, STANDSTILL, WINDS WHEN READY (v38)", None),\n'
    '    ("THE RULINGS (2026-11-14)", "Blob attacks: \\"Most value destroyed\\" (AP-heavy attacks skip armour below 50); "\n'
    '     "they wait until the caster stands still (\\"For now, only the Blob attacks\\"); charge abilities: \\"Nothing\\". "\n'
    '     "Winds of Magic abilities: \\"All when ready\\". The map probe also logs our army\'s winds."),\n'
    '    ("THE NEW FAMILY", "when_ready (21 Winds of Magic abilities). Generated tables: FOURTH.BLOB_DMG_TEXT (the 77 blast "\n'
    '     "damage splits and AP-heavy flags) and FOURTH.UNIT_DEF_TEXT (armour and hit points of 587 infantry types)."),\n'
    '    ("THE ARITHMETIC", "No count change: 854 implemented / 269 not implemented (27 skipped); 799 entries / 854 keys; "\n'
    '     "75 families; melee_unwavering 309 -> 288."),\n'
    ']\n'))
s = cut(s, 'ch.cell(row=r, column=1).value = "2026-11-13"', "wb.save(DST)", (
    'ch.cell(row=r, column=1).value = "2026-11-14"\n'
    'ch.cell(row=r, column=2).value = "v38"\n'
    'ch.cell(row=r, column=3).value = (\n'
    '    "ROUND 150. The 77 blob attacks: the most enemy value destroyed, armour rule 50 for AP-heavy attacks, never while "\n'
    '    "the caster moves. The 21 Winds of Magic abilities on the NEW when_ready. 854 / 269 unchanged; 75 families. "\n'
    '    "SHIPPED: installed pack md5 %s; harness 149 full suite 6,374 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))\n'
    'ch.cell(row=r, column=4).value = "user rulings 2026-11-14; xlsx v38 supersedes v37; v1-v37 byte-unchanged."\n'))
assert "\u2014" not in s
open(T + r"\make_xlsx_v38.py", "w", encoding="utf-8", newline="\n").write(s)
print("make_xlsx_v38 written")
