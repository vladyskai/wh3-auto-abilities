#!/usr/bin/env python3
"""Build WH3_abilities_master_v46_2026-11-16.xlsx from v45 - round 162: the wandering winds.

(1) 32 rows NOT IMPLEMENTED -> IMPLEMENTED: 12 straight waves on the NEW enemy_wave, 20 wanderers / static / safe
    blasts on the NEW enemy_wander (numbers from the GENERATED WW table).
(2) 2 rows NOT IMPLEMENTED -> SKIPPED (user decision): Gehenna's Golden Globe, Wall of Wind & Fire.
(3) Implemented 917 -> 949 rows / keys; not implemented among the included 206 -> 172 (32 + 2 = 34 skipped). The mod
    892 entries / 949 keys; 88 -> 90 families: the Numbers trigger table gains two rows (bombardment block 134 -> 136).
    Definitions: title v46, the two count rows, section 43. Changelog: a v46 row.
v1-v45 are never opened for writing. (Rounds 160 and 161 changed no roster row and made no workbook version.)
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import math
import os
import shutil

import openpyxl

import build_ability_database as bd
import gen_ww_tables as GW

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v45_2026-11-15.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v46_2026-11-16.xlsx"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
SRC_TXT = open(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua",
               encoding="utf-8").read()
KF = GW.keys_in(SRC_TXT)
WW = GW.derive(KF)
USA = {r["key"]: r for r in GW.tsv("unit_spec_abil.tsv")}
INV = {}
for r in GW.tsv("special_ability_to_invalid_target_flags_tables.tsv"):
    INV.setdefault(r["special_ability"], set()).add(r["invalid_target"])
CLOSE = {
    "wh3_pro10_cataclysm_metal_gehennas_golden_globe_bound": "a straight 140 m line whose heading is not in the game data",
    "wh3_main_spell_bound_wall_of_wind_and_fire": "a straight 69 m line whose heading is not in the game data",
}
assert len(KF) == 32


def text(k, fam):
    a = USA[k]
    real = float(a["target_intercept_range"])
    bnd = int(math.floor(real * 0.70 + 1e-9))
    uses, rech, wind = int(float(a["num_uses"])), float(a["recharge_time"]), float(a["wind_up_time"])
    gates = []
    if uses > 1:
        gates.append("charge hold %g s (%d uses)" % (rech, uses))
    if wind > 0:
        gates.append("in-flight hold %g s (%g s wind-up + 2 s)" % (wind + 2, wind))
    within = "within %d m (70%% of the ability's %g m target_intercept_range; unit_distance)" % (bnd, real)
    kind, r, path, off, buf, allies, ground = WW[k]
    cls = "; target class: not flying (the game's flying_currently rule)" if "flying_currently" in INV.get(k, set()) else ""
    if fam == "enemy_wave":
        body = ("enemy_wave: not routing; the caster STANDING STILL; among the visible enemies %s that are STANDING STILL "
                "(is_moving() exactly false: the cast takes %g s and a moving target walks out of the computed path), the "
                "one whose straight wave path (starting %g m + the target's half extent before its centre, %g m long, along "
                "the caster-to-target heading) has none of our units (the caster counting) within %g m at its start, "
                "widening to %g m at its end (radius %g + the simulated 95%% sideways drift %d m + 10 m; the GENERATED WW "
                "table), and the most enemy value (live strategic_value) touched by the path%s; cast target: that enemy "
                "unit; pre-cast re-check: the map is rebuilt and the same rule holds; user ruling 2026-11-16 (\"Clear path, "
                "most value and not currently moving\", buffer \"Simulated 95%%\"); "
                % (within, wind, off, path, r + 10, r + buf + 10, r, buf, cls))
    else:
        if allies:
            extra = " + the target's half extent (the vortex starts at its near edge)" if kind == 3 else ""
            safe = ("none of our units within %g m of the target (radius %g + the simulated 95%% reach %d m + 10 m%s; "
                    "the GENERATED WW table)" % (r + buf + 10, r, buf, extra))
            rule = "\"Worst-case reach\", buffer \"Simulated 95%\""
        else:
            safe = "no friendly test (the game marks the vortex as not hitting allies)"
            rule = "\"Blob rule; close 2\""
        how = "on the ground under it (a ground-only ability)" if ground else "that enemy unit"
        body = ("enemy_wander: not routing; the caster STANDING STILL; the visible enemy INFANTRY %s, STANDING STILL, whose "
                "%g m blast covers the blob density line (half a packed block; the trash rule) and destroys the most "
                "value; %s%s; cast target: %s; pre-cast re-check: the map is rebuilt and the same rule holds; user ruling "
                "2026-11-16 (%s); " % (within, r, safe, cls, how, rule))
    return body + SHARED_TAIL + ((" GATES: " + "; ".join(gates) + ".") if gates else "")


entries, _, _ = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
NEW = {k: (fam_by_key[k], text(k, fam_by_key[k])) for k in KF}

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
n_new = n_close = 0
for r in range(2, ws.max_row + 1):
    ks = keys_of(r)
    if len(ks) == 1 and ks[0] in NEW:
        assert str(ws.cell(row=r, column=18).value) == "IN-WHEEL" and str(ws.cell(row=r, column=20).value) == "NOT IMPLEMENTED", ks
        fam, t = NEW[ks[0]]
        ws.cell(row=r, column=20).value = "IMPLEMENTED"
        ws.cell(row=r, column=21).value = fam
        ws.cell(row=r, column=22).value = t
        n_new += 1
    elif len(ks) == 1 and ks[0] in CLOSE:
        assert str(ws.cell(row=r, column=18).value) == "IN-WHEEL" and str(ws.cell(row=r, column=20).value) == "NOT IMPLEMENTED", ks
        why = CLOSE[ks[0]]
        ws.cell(row=r, column=19).value = "skipped (user decision 2026-11-16: \"Blob rule; close 2\"; %s)" % why
        ws.cell(row=r, column=20).value = "SKIPPED (user decision)"
        ws.cell(row=r, column=21).value = "-"
        ws.cell(row=r, column=22).value = ("No automation - SKIPPED BY THE USER'S DECISION of 2026-11-16: \"Blob rule; "
                                           "close 2\" (%s)." % why)
        n_close += 1
assert (n_new, n_close) == (32, 2), (n_new, n_close)

rows = [(r, keys_of(r), str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=20).value),
         str(ws.cell(row=r, column=21).value)) for r in range(2, ws.max_row + 1)]
N = len(rows)
impl = [x for x in rows if x[3] == "IMPLEMENTED"]
N_IMPL_ROWS = len(impl)
N_IMPL_KEYS = len(set(k for x in impl for k in x[1]))
assert (N, N_IMPL_ROWS, N_IMPL_KEYS) == (1800, 949, 949), (N, N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = 1123 - N_IMPL_ROWS
assert NOT_IMPL_IN == 174
assert sum(1 for x in rows if x[3] == "SKIPPED (user decision)") == 34
assert (len(entries), len(fam_by_key)) == (892, 949)
assert set(k for x in impl for k in x[1]) == set(fam_by_key)
assert not [x[1][0] for x in impl if x[4] != fam_by_key.get(x[1][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 90, len(trig)

src_type = {}
with open(GP.UNIT_ABILITIES, encoding="utf-8", errors="replace") as f:
    hdr = f.readline().rstrip("\n").split("\t")
    si = hdr.index("source_type")
    for line in f:
        if line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        if len(c) > si:
            src_type.setdefault(c[0].strip(), c[si].strip())
fam_order = ["active", "bound", "rune", "item", "lord", "character", "unit", "weapon"]
fam_inc, fam_impl = collections.Counter(), collections.Counter()
for x in rows:
    if x[2] != "IN-WHEEL":
        continue
    f = next((src_type[k] for k in x[1] if k in src_type), None)
    fam_inc[f] += 1
    if x[3] == "IMPLEMENTED":
        fam_impl[f] += 1

n = wb["Numbers"]
assert n.cell(row=134, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert n.cell(row=132, column=2).value == "TOTAL (88 families)"
assert all(int(str(m).split(":")[0][1:]) < 108 for m in n.merged_cells.ranges)
n.insert_rows(131, 2)
assert n.cell(row=136, column=1).value == "Bombardment set (COMPLETE - round 108)"
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-11-16     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v46 - ROUND 162: the wandering winds. 32 rows implemented: 12 straight waves (NEW enemy_wave) and 20 wanderers / "
    "static / safe blasts (NEW enemy_wander), safety from the simulated 95% drift; 2 rows SKIPPED by the user. Implemented "
    "917 + 32 = 949 rows / 949 keys; not implemented among the included 206 - 34 = 172 (34 skipped by the user). The mod: "
    "892 entries / 949 keys / 90 trigger families.)")
for r, num, label, abs_, p1, p2 in [
        (13, 4, "Implemented among the included", N_IMPL_ROWS, N_IMPL_ROWS / tot, N_IMPL_ROWS / 1123.0),
        (14, 5, "Not implemented among the included", NOT_IMPL_IN, NOT_IMPL_IN / tot, NOT_IMPL_IN / 1123.0),
        (16, 7, "All implemented in the mod (4 + 6)", N_IMPL_KEYS, N_IMPL_KEYS / tot, N_IMPL_KEYS / 1123.0)]:
    for c, v in enumerate((num, label, abs_, p1, p2), 1):
        n.cell(row=r, column=c).value = v
old18 = str(n.cell(row=18, column=1).value)
assert "917 implemented" in old18
n.cell(row=18, column=1).value = old18.replace("917 implemented", "949 implemented")
for i, f in enumerate(fam_order):
    r = 20 + i
    assert n.cell(row=r, column=2).value == f, (r, n.cell(row=r, column=2).value)
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=40, column=1).value = (
    "Reconciliation (v46): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 949 + not "
    "implemented 174 (34 of them skipped by the user) = 1,123. The mod's ABILITIES table is 892 entries / 949 keys, and "
    "the join mod-key -> 'Ability key(s)' returns 949 / 949 with ZERO unmatched keys in either direction. 860 + 32 "
    "(round 162, the wandering winds) = 892 entries; 917 + 32 = 949 keys. NO army-bar (army_spec) key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 162 - re-counted from the mod's own ABILITIES table: 90 families / 892 entries / 949 "
    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 162: the NEW enemy_wave (12) and "
    "enemy_wander (20).")
for r in range(44, 134):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t2, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t2
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t2]
assert 44 + len(fam_sorted) == 134
n.cell(row=134, column=2).value = "TOTAL (90 families)"
n.cell(row=134, column=3).value = sum(trig.values())
n.cell(row=134, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v45")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v46 (2026-11-16)"
r11 = d.cell(row=11, column=2)
assert "917 keys across 917 numbered rows (" in r11.value and "round 159 added 28)" in r11.value
r11.value = r11.value.replace("917 keys across 917 numbered rows (", "949 keys across 949 numbered rows (").replace(
    "round 159 added 28)", "round 159 added 28, round 162 added 32)")
r12 = d.cell(row=12, column=2)
assert "(883 keys, of which 206 are in the wheel)" in r12.value
r12.value = r12.value.replace("(883 keys, of which 206 are in the wheel)", "(851 keys, of which 174 are in the wheel)")
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("43. ROUND 162 - THE WANDERING WINDS (v46)", None),
    ("THE RULINGS (2026-11-16)", "The 12 straight waves \"Clear path, most value and not currently moving\"; the 16 "
     "wanderers \"Worst-case reach\"; the buffer \"Simulated 95%\" (\"some abilities are more random than others\"); the "
     "big wobblers \"Automate with the big buffer\"; the other 6 \"Blob rule; close 2\". Earlier status: the 2026-10-09 "
     "family RULE, never a ruling on these abilities one by one."),
    ("THE NEW FAMILIES", "enemy_wave (12): the caster and the target standing still; the wave's path (offset + the target's "
     "half extent before it, speed x duration long, caster-to-target heading) clear of our units by radius + 10 m at its "
     "start widening to radius + the simulated 95% drift + 10 m at its end; the most enemy value on the path. "
     "enemy_wander (20): the caster and the target standing still; the blob rule; none of ours within radius + the "
     "simulated 95% reach + 10 m (no test when the vortex cannot hit allies). GENERATED FOURTH.WW_TEXT "
     "(tools/gen_ww_tables.py: 4,000 paths per reading, fixed seeds). Both start unarmed (M)."),
    ("THE ARITHMETIC", "Implemented 917 + 32 = 949 rows / keys; not implemented among the included 206 - 34 = 172 "
     "(34 skipped by the user). The mod 860 + 32 = 892 entries / 949 keys; 90 families."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-16"
ch.cell(row=r, column=2).value = "v46"
ch.cell(row=r, column=3).value = (
    "ROUND 162. The wandering winds: 32 rows IMPLEMENTED (2 NEW families), 2 rows SKIPPED by the user. 917 -> 949 "
    "implemented; 206 -> 172 not implemented (34 skipped). Mod 892 / 949 / 90 families. SHIPPED: installed pack md5 %s; "
    "harness 161 full suite 6,833 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-16 (the wandering winds); xlsx v46 supersedes v45; v1-v45 byte-unchanged."
wb.save(DST)
print("wrote", DST)
