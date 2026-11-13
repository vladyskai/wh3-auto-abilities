#!/usr/bin/env python3
"""Write tools/make_xlsx_v37.py from make_xlsx_v36.py (round 146, the blob trigger)."""
import re

T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\make_xlsx_v36.py", encoding="utf-8").read()
HEAD = '''#!/usr/bin/env python3
"""Build WH3_abilities_master_v37_2026-11-13.xlsx from v36 - round 146: the blob trigger.

(1) 77 rows NOT IMPLEMENTED -> IMPLEMENTED on the NEW enemy_blob: the open group B attacks whose projectile explodes
    (Dead Eye and Focused Shot stay open: the game lets them target single-entity units only).
(2) Implemented 777 -> 854 rows / keys; not implemented among the included 346 -> 269 (27 skipped). The mod 799 entries /
    854 keys; 73 -> 74 families: the Numbers trigger table gains one row (bombardment block 119 -> 120). Definitions:
    title v37, the two count rows, section 34. Changelog: a v37 row.
v1-v36 are never opened for writing.
"""
'''
s = HEAD + s[s.index("import sys as _sys"):]
s = s.replace(r'docs\WH3_abilities_master_v36_2026-11-13.xlsx"', r'docs\WH3_abilities_master_v37_2026-11-13.xlsx"')
s = s.replace(r'docs\WH3_abilities_master_v35_2026-11-13.xlsx"', r'docs\WH3_abilities_master_v36_2026-11-13.xlsx"')
i0 = s.index('RULE = "user ruling 2026-11-13 (open batch 3); "')
i1 = s.index("assert not os.path.exists(DST), DST")
TEXTS = r'''RULE = "user rulings 2026-11-13 (the blob trigger: \"A. Density line\", \"10 m\", \"79 open attacks\"); "
import math as _math
import list_blob_candidates as _LC
import gen_blob_tables as _GB
_PM2 = _GB.packed_m2()


def _blob_text(r):
    bound = int(_math.floor(r["range"] * 0.70 + 1e-9))
    need = max(1, int(_math.floor(0.5 * _math.pi * r["blast"] ** 2 / _PM2 + 0.5)))
    gates = []
    if r["uses"] > 1:
        gates.append("charge hold %g s (%d uses)" % (r["recharge"], r["uses"]))
    if r["wind"] > 0:
        gates.append("in-flight hold %g s (%g s wind-up + 2 s)" % (r["wind"] + 2, r["wind"]))
    nf = "; target class not_flying (the game's flying_currently flag)" if "flying_currently" in r["flags"] else ""
    return ("enemy_blob: not routing; the live map (our units; the enemy INFANTRY we can see: an inf_* class, not in the "
            "generated large set, not flying, at least 10 men, is_visible_to_alliance exactly true); candidates = visible "
            "enemy infantry units within %d m (70%% of the ability's %g m target_intercept_range; unit_distance)%s; a "
            "candidate is UNSAFE when any of our units' estimated rectangles comes within the blast radius + 10 m of its "
            "rectangle; score = the enemy infantry soldiers inside the %g m blast around its centre (19 sample points, "
            "the soldier density of every block under each point; depth = ranks x the type's close spacing, generated); "
            "fire at the best safe candidate when the score reaches %d (half of what the blast holds inside a packed "
            "block: 0.5 x pi x %g^2 / %.3f m2); cast target: that enemy unit; pre-cast re-check: the map is rebuilt and "
            "the target must still be safe and reach the line; " % (bound, r["range"], nf, r["blast"], need, r["blast"],
                                                                   _PM2)
            + RULE + SHARED_TAIL + ((" GATES: " + "; ".join(gates) + ".") if gates else ""))


_ROWS = [r for r in _LC.candidates() if r["key"] not in ("wh3_dlc26_character_abilities_dead_eye",
                                                         "wh2_dlc13_lord_abilities_kill_shot")]
assert len(_ROWS) == 77
NEW = {r["key"]: ("enemy_blob", _blob_text(r)) for r in _ROWS}
SKIP = {}

'''
s = s[:i0] + TEXTS + s[i1:]


def cut(s, start, end, new):
    a = s.index(start)
    b = s.index(end, a)
    return s[:a] + new + s[b:]


R = [
    ("assert (n_new, n_skip) == (10, 3), (n_new, n_skip)", "assert (n_new, n_skip) == (77, 0), (n_new, n_skip)"),
    ("(1800, 777, 777)", "(1800, 854, 854)"),
    ("assert NOT_IMPL_IN == 346\n", "assert NOT_IMPL_IN == 269\n"),
    ("(len(entries), len(fam_by_key)) == (722, 777)", "(len(entries), len(fam_by_key)) == (799, 854)"),
    ('assert len(trig) == 73 and trig["melee_unwavering"] == 309 and trig["self_last_stand"] == 1 '
     'and trig["enemy_fast_near_ally"] == 8 and trig["under_fire"] == 4, (len(trig),)',
     'assert len(trig) == 74 and trig["enemy_blob"] == 77, (len(trig),)'),
    ('assert n.cell(row=114, column=1).value == "Bombardment set (COMPLETE - round 108)"',
     'assert n.cell(row=119, column=1).value == "Bombardment set (COMPLETE - round 108)"'),
    ("n.insert_rows(112, 5)\nassert n.cell(row=119, column=1).value",
     "n.insert_rows(117, 1)\nassert n.cell(row=120, column=1).value"),
    ('replace("767 implemented", "777 implemented")', 'replace("777 implemented", "854 implemented")'),
    ("for r in range(44, 118):", "for r in range(44, 119):"),
    ('assert 44 + len(fam_sorted) == 117\nn.cell(row=117, column=2).value = "TOTAL (73 families)"\n'
     'n.cell(row=117, column=3).value = sum(trig.values())\nn.cell(row=117, column=4).value = sum(trig_keys.values())',
     'assert 44 + len(fam_sorted) == 118\nn.cell(row=118, column=2).value = "TOTAL (74 families)"\n'
     'n.cell(row=118, column=3).value = sum(trig.values())\nn.cell(row=118, column=4).value = sum(trig_keys.values())'),
    ('startswith("DEFINITIONS - WH3 ability master v35")', 'startswith("DEFINITIONS - WH3 ability master v36")'),
    ('"DEFINITIONS - WH3 ability master v36 (2026-11-13)"', '"DEFINITIONS - WH3 ability master v37 (2026-11-13)"'),
    ('assert "(1,033 keys, of which 356 are in the wheel)" in r12.value\n'
     'r12.value = r12.value.replace("(1,033 keys, of which 356 are in the wheel)", "(1,023 keys, of which 346 are in the wheel)")',
     'assert "(1,023 keys, of which 346 are in the wheel)" in r12.value\n'
     'r12.value = r12.value.replace("(1,023 keys, of which 346 are in the wheel)", "(946 keys, of which 269 are in the wheel)")'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
s = s.replace('assert sum(1 for x in rows if x[3] == "SKIPPED (user decision)") == 27',
              'assert sum(1 for x in rows if x[3] == "SKIPPED (user decision)") == 27  # unchanged')
s = cut(s, '    "(v36 - ROUND 144', "for r, num, label, abs_, p1, p2 in", (
    '    "(v37 - ROUND 146: the blob trigger. 77 exploding enemy-unit attacks on the NEW enemy_blob (the best SAFE visible "\n'
    '    "enemy infantry unit whose blast reaches half a packed block\'s worth of soldiers; none of ours within blast + 10 m). "\n'
    '    "Implemented 777 + 77 = 854 rows / 854 keys; not implemented among the included 346 - 77 = 269 (27 skipped). The "\n'
    '    "mod: 799 entries / 854 keys / 74 trigger families.)")\n'))
s = cut(s, '    "Reconciliation (v36)', "n.cell(row=42, column=1).value = (", (
    '    "Reconciliation (v37): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 854 + not "\n'
    '    "implemented 269 = 1,123. The mod\'s ABILITIES table is 799 entries / 854 keys, and the join mod-key -> \'Ability "\n'
    '    "key(s)\' returns 854 / 854 with ZERO unmatched keys in either direction. 722 + 77 (round 146, the blob trigger) = "\n'
    '    "799 entries; 777 + 77 = 854 keys. NO army-bar (army_spec) key in the mod: 0.")\n'))
s = cut(s, '    "Trigger families after round 144', "for r in range(44, 119):", (
    '    "Trigger families after round 146 - re-counted from the mod\'s own ABILITIES table: 74 families / 799 entries / 854 "\n'
    '    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 146: the NEW enemy_blob (77).")\n'))
s = cut(s, "old11 = (", "r12 = d.cell(row=12, column=2)", (
    'old11 = ("777 keys across 777 numbered rows (rounds 122-123 added 21, round 130 added 2, round 131 removed the 9 "\n'
    '         "stances, round 134 removed the 2 Thunderburner keys, round 142 added 6, round 143 added 11, round 144 added 10)")\n'
    'assert old11 in r11.value\n'
    'r11.value = r11.value.replace(old11, "854 keys across 854 numbered rows (rounds 122-123 added 21, round 130 added 2, "\n'
    '                              "round 131 removed the 9 stances, round 134 removed the 2 Thunderburner keys, round 142 "\n'
    '                              "added 6, round 143 added 11, round 144 added 10, round 146 added 77)")\n'))
s = cut(s, "sec = [", "for i, (a, b) in enumerate(sec):", (
    'sec = [\n'
    '    ("34. ROUND 146 - THE BLOB TRIGGER (v37)", None),\n'
    '    ("THE RULINGS (2026-11-13)", "\\"A. Density line\\" (fire when the blast covers at least half of what it covers inside "\n'
    '     "a tightly packed infantry block), \\"10 m\\" (no soldier of ours within blast + 10 m of the target), \\"79 open "\n'
    '     "attacks\\" (77 built; Dead Eye and Focused Shot target single entities only)."),\n'
    '    ("THE NEW FAMILY", "enemy_blob, on the round-145 map reads; generated tables FOURTH.BLAST_TEXT (77 blast radii) and "\n'
    '     "FOURTH.SPACING_TEXT (535 infantry spacings), FOURTH.PACKED_M2 = 2.368; eight new 70% constants (55, 60, 80, 130, "\n'
    '     "250, 350, 400, 600 m)."),\n'
    '    ("THE ARITHMETIC", "Implemented 777 + 77 = 854 rows / keys; not implemented among the included 346 - 77 = 269 "\n'
    '     "(27 skipped). The mod 722 + 77 = 799 entries / 854 keys; 74 families."),\n'
    ']\n'))
s = cut(s, 'ch.cell(row=r, column=2).value = "v36"', "wb.save(DST)", (
    'ch.cell(row=r, column=2).value = "v37"\n'
    'ch.cell(row=r, column=3).value = (\n'
    '    "ROUND 146. The blob trigger: 77 exploding enemy-unit attacks IMPLEMENTED on the NEW enemy_blob. 777 -> 854 "\n'
    '    "implemented; 346 -> 269 not implemented (27 skipped). Mod 799 / 854 / 74 families. SHIPPED: installed pack md5 %s; "\n'
    '    "harness 145 full suite 6,339 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))\n'
    'ch.cell(row=r, column=4).value = "user rulings 2026-11-13 (the blob trigger); xlsx v37 supersedes v36; v1-v36 byte-unchanged."\n'))
assert "\u2014" not in s
left = [m.start() for m in re.finditer(r"\bv35\b", s)]
assert not left, [s[x - 40:x + 20] for x in left]
open(T + r"\make_xlsx_v37.py", "w", encoding="utf-8", newline="\n").write(s)
print("make_xlsx_v37 written")
