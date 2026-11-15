#!/usr/bin/env python3
"""Build WH3_abilities_master_v43_2026-11-15.xlsx from v42 - round 157: the drains and the Executioner (open batch 5).

(1) 12 rows NOT IMPLEMENTED -> IMPLEMENTED on 2 NEW families: enemy_single_drain (Spirit Leech x5, The Liber
    Bubonicus, Death's Timekeeper, Rancid Visitations, 'Effagee' of da Git, Punch-Dagger) and enemy_execute (The
    Emperor's Executioner, base and upgrade).
(2) Implemented 865 -> 877 rows / keys; not implemented among the included 258 -> 246 (27 skipped). The mod 822 entries
    / 877 keys; 80 -> 82 families: the Numbers trigger table gains two rows (bombardment block 126 -> 128).
    Definitions: title v43, the two count rows, section 40. Changelog: a v43 row.
v1-v42 are never opened for writing.
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
import gen_shot_tables as GS

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v42_2026-11-15.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v43_2026-11-15.xlsx"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
USA = {r["key"]: r for r in GS.tsv("unit_spec_abil.tsv")}


def text(k, fam):
    a = USA[k]
    real = float(a["target_intercept_range"])
    bound = int(math.floor(real * 0.70 + 1e-9))
    uses, rech, wind = int(float(a["num_uses"])), float(a["recharge_time"]), float(a["wind_up_time"])
    gates = []
    if uses > 1:
        gates.append("charge hold %g s (%d uses)" % (rech, uses))
    if wind > 0:
        gates.append("in-flight hold %g s (%g s wind-up + 2 s)" % (wind + 2, wind))
    within = "within %d m (70%% of the ability's %g m target_intercept_range; unit_distance)" % (bound, real)
    if fam == "enemy_single_drain":
        body = ("enemy_single_drain: not routing; the caster STANDING STILL (is_moving() exactly false); the live map "
                "(every enemy we can see, is_visible_to_alliance exactly true); the SINGLE-ENTITY enemy (the generated "
                "single set: lords, heroes, single monsters) %s with the highest live value (strategic_value); no "
                "friendly-fire margin (a direct effect: the game's max_damaged_entities = 1, it cannot hit our units), "
                "so an enemy fighting ours qualifies; cast target: that enemy unit; pre-cast re-check: the map is "
                "rebuilt, the caster still standing and the target still a single entity in range; user rulings "
                "2026-11-15 (\"Most valuable single\", \"Standing still\"); " % within)
    else:
        ratio = GS.exec_rows({k})[k]
        cls = ("; target class: Lord/Hero only (the game's unit_is_not_commander_class)"
               if "upgrade" not in k else "; a single entity (the generated single set)")
        body = ("enemy_execute: not routing; the live map; the enemy %s whose health (the ONE health reader, 0-100) is "
                "at or below the execute line %d%% (the GENERATED EXEC table from the game's execute_ratio %g)%s, the "
                "most valuable (strategic_value) first; cast target: that enemy unit; pre-cast re-check: still at or "
                "below the line and in range; user ruling 2026-11-15 (\"At the execute line\"); "
                % (within, int(round(ratio * 100)), ratio, cls))
    return body + SHARED_TAIL + ((" GATES: " + "; ".join(gates) + ".") if gates else "")


src_txt = open(r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua",
               encoding="utf-8").read()
entries, _, _ = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
KEYS = [k for k in GS.keys_in(src_txt) if fam_by_key[k] in ("enemy_single_drain", "enemy_execute")]
assert len(KEYS) == 12
NEW = {k: (fam_by_key[k], text(k, fam_by_key[k])) for k in KEYS}

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
n_new = 0
for r in range(2, ws.max_row + 1):
    ks = keys_of(r)
    if len(ks) == 1 and ks[0] in NEW:
        assert str(ws.cell(row=r, column=18).value) == "IN-WHEEL" and str(ws.cell(row=r, column=20).value) == "NOT IMPLEMENTED", ks
        fam, t = NEW[ks[0]]
        ws.cell(row=r, column=20).value = "IMPLEMENTED"
        ws.cell(row=r, column=21).value = fam
        ws.cell(row=r, column=22).value = t
        n_new += 1
assert n_new == 12, n_new

rows = [(r, keys_of(r), str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=20).value),
         str(ws.cell(row=r, column=21).value)) for r in range(2, ws.max_row + 1)]
N = len(rows)
impl = [x for x in rows if x[3] == "IMPLEMENTED"]
N_IMPL_ROWS = len(impl)
N_IMPL_KEYS = len(set(k for x in impl for k in x[1]))
assert (N, N_IMPL_ROWS, N_IMPL_KEYS) == (1800, 877, 877), (N, N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = 1123 - N_IMPL_ROWS
assert NOT_IMPL_IN == 246
assert sum(1 for x in rows if x[3] == "SKIPPED (user decision)") == 27
assert (len(entries), len(fam_by_key)) == (822, 877)
assert set(k for x in impl for k in x[1]) == set(fam_by_key)
assert not [x[1][0] for x in impl if x[4] != fam_by_key.get(x[1][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 82, len(trig)

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
assert n.cell(row=126, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert n.cell(row=124, column=2).value == "TOTAL (80 families)"
assert all(int(str(m).split(":")[0][1:]) < 108 for m in n.merged_cells.ranges)
n.insert_rows(123, 2)
assert n.cell(row=128, column=1).value == "Bombardment set (COMPLETE - round 108)"
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-11-15     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v43 - ROUND 157: the drains and the Executioner. 12 single-target attacks on 2 NEW families (enemy_single_drain, "
    "enemy_execute). Implemented 865 + 12 = 877 rows / 877 keys; not implemented among the included 258 - 12 = 246 "
    "(27 skipped). The mod: 822 entries / 877 keys / 82 trigger families.)")
for r, num, label, abs_, p1, p2 in [
        (13, 4, "Implemented among the included", N_IMPL_ROWS, N_IMPL_ROWS / tot, N_IMPL_ROWS / 1123.0),
        (14, 5, "Not implemented among the included", NOT_IMPL_IN, NOT_IMPL_IN / tot, NOT_IMPL_IN / 1123.0),
        (16, 7, "All implemented in the mod (4 + 6)", N_IMPL_KEYS, N_IMPL_KEYS / tot, N_IMPL_KEYS / 1123.0)]:
    for c, v in enumerate((num, label, abs_, p1, p2), 1):
        n.cell(row=r, column=c).value = v
old18 = str(n.cell(row=18, column=1).value)
assert "865 implemented" in old18
n.cell(row=18, column=1).value = old18.replace("865 implemented", "877 implemented")
for i, f in enumerate(fam_order):
    r = 20 + i
    assert n.cell(row=r, column=2).value == f, (r, n.cell(row=r, column=2).value)
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=40, column=1).value = (
    "Reconciliation (v43): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 877 + not "
    "implemented 246 = 1,123. The mod's ABILITIES table is 822 entries / 877 keys, and the join mod-key -> 'Ability "
    "key(s)' returns 877 / 877 with ZERO unmatched keys in either direction. 810 + 12 (round 157, the drains and the "
    "Executioner) = 822 entries; 865 + 12 = 877 keys. NO army-bar (army_spec) key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 157 - re-counted from the mod's own ABILITIES table: 82 families / 822 entries / 877 "
    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 157: the NEW enemy_single_drain "
    "(10) and enemy_execute (2).")
for r in range(44, 126):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t2, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t2
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t2]
assert 44 + len(fam_sorted) == 126
n.cell(row=126, column=2).value = "TOTAL (82 families)"
n.cell(row=126, column=3).value = sum(trig.values())
n.cell(row=126, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v42")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v43 (2026-11-15)"
r11 = d.cell(row=11, column=2)
assert "865 keys across 865 numbered rows (" in r11.value and "round 156 added 11)" in r11.value
r11.value = r11.value.replace("865 keys across 865 numbered rows (", "877 keys across 877 numbered rows (").replace(
    "round 156 added 11)", "round 156 added 11, round 157 added 12)")
r12 = d.cell(row=12, column=2)
assert "(935 keys, of which 258 are in the wheel)" in r12.value
r12.value = r12.value.replace("(935 keys, of which 258 are in the wheel)", "(923 keys, of which 246 are in the wheel)")
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("40. ROUND 157 - THE DRAINS AND THE EXECUTIONER (v43)", None),
    ("THE RULINGS (2026-11-15)", "Drains \"Most valuable single\" and \"Standing still\"; the Executioner \"At the "
     "execute line\"."),
    ("THE NEW FAMILIES", "enemy_single_drain (10): the most valuable visible single-entity enemy in range, the caster "
     "standing still, no friendly-fire margin (a direct effect). enemy_execute (2): the most valuable enemy in range at "
     "or below the GENERATED execute line (FOURTH.EXEC_TEXT from execute_ratio: 20% base, Lord/Hero only; 33% upgrade, "
     "single entities). The SHOT table now carries 23 keys."),
    ("THE ARITHMETIC", "Implemented 865 + 12 = 877 rows / keys; not implemented among the included 258 - 12 = 246 "
     "(27 skipped). The mod 810 + 12 = 822 entries / 877 keys; 82 families."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-15"
ch.cell(row=r, column=2).value = "v43"
ch.cell(row=r, column=3).value = (
    "ROUND 157. The drains and the Executioner: 12 single-target attacks IMPLEMENTED on 2 NEW families. 865 -> 877 "
    "implemented; 258 -> 246 not implemented (27 skipped). Mod 822 / 877 / 82 families. SHIPPED: installed pack md5 %s; "
    "harness 156 full suite 6,618 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-15 (the drains, the Executioner); xlsx v43 supersedes v42; v1-v42 byte-unchanged."
wb.save(DST)
print("wrote", DST)
