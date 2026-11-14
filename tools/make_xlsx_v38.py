#!/usr/bin/env python3
"""Build WH3_abilities_master_v38_2026-11-14.xlsx from v37 - round 150.

(1) The 77 enemy_blob rows: the target is the one whose blast destroys the most enemy value (armour, hit points, live
    value per soldier); AP-heavy attacks never target armour below 50; never while the caster moves.
(2) The 21 Winds of Magic rows move from melee_unwavering to the NEW when_ready.
(3) No count changes: 854 implemented / 269 not implemented (27 skipped); the mod 799 entries / 854 keys; 74 -> 75
    families (the Numbers trigger table gains one row; bombardment block 120 -> 121). Definitions: title v38, section
    35. Changelog: a v38 row.
v1-v37 are never opened for writing.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v37_2026-11-13.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v38_2026-11-14.xlsx"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
RULE = ("user rulings 2026-11-13 (the blob trigger: \"A. Density line\", \"10 m\", \"79 open attacks\") and 2026-11-14 "
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

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
n_new = 0
for r in range(2, ws.max_row + 1):
    ks = keys_of(r)
    if len(ks) == 1 and ks[0] in NEW:
        assert str(ws.cell(row=r, column=20).value) == "IMPLEMENTED" and str(ws.cell(row=r, column=21).value) == WAS[ks[0]], ks
        fam, text = NEW[ks[0]]
        ws.cell(row=r, column=21).value = fam
        ws.cell(row=r, column=22).value = text
        n_new += 1
assert n_new == 98, n_new

rows = [(r, keys_of(r), str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=20).value),
         str(ws.cell(row=r, column=21).value)) for r in range(2, ws.max_row + 1)]
N = len(rows)
impl = [x for x in rows if x[3] == "IMPLEMENTED"]
N_IMPL_ROWS = len(impl)
N_IMPL_KEYS = len(set(k for x in impl for k in x[1]))
assert (N, N_IMPL_ROWS, N_IMPL_KEYS) == (1800, 854, 854), (N, N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = 1123 - N_IMPL_ROWS
assert NOT_IMPL_IN == 269
assert sum(1 for x in rows if x[3] == "SKIPPED (user decision)") == 27  # unchanged
entries, _, _ = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
assert (len(entries), len(fam_by_key)) == (799, 854)
assert set(k for x in impl for k in x[1]) == set(fam_by_key)
assert not [x[1][0] for x in impl if x[4] != fam_by_key.get(x[1][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 75 and trig["enemy_blob"] == 77 and trig["when_ready"] == 21 and trig["melee_unwavering"] == 288, (len(trig),)

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
assert n.cell(row=120, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert all(int(str(m).split(":")[0][1:]) < 108 for m in n.merged_cells.ranges)
n.insert_rows(118, 1)
assert n.cell(row=121, column=1).value == "Bombardment set (COMPLETE - round 108)"
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-11-14     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v38 - ROUND 150: the 77 blob attacks pick the target whose blast destroys the most enemy value and never fire "
    "while the caster moves; AP-heavy ones never target armour below 50. The 21 Winds of Magic abilities move to the "
    "NEW when_ready. No count change: 854 implemented / 269 not implemented (27 skipped); the mod 799 entries / 854 "
    "keys / 75 trigger families.)")
for r, num, label, abs_, p1, p2 in [
        (13, 4, "Implemented among the included", N_IMPL_ROWS, N_IMPL_ROWS / tot, N_IMPL_ROWS / 1123.0),
        (14, 5, "Not implemented among the included", NOT_IMPL_IN, NOT_IMPL_IN / tot, NOT_IMPL_IN / 1123.0),
        (16, 7, "All implemented in the mod (4 + 6)", N_IMPL_KEYS, N_IMPL_KEYS / tot, N_IMPL_KEYS / 1123.0)]:
    for c, v in enumerate((num, label, abs_, p1, p2), 1):
        n.cell(row=r, column=c).value = v
for i, f in enumerate(fam_order):
    r = 20 + i
    assert n.cell(row=r, column=2).value == f, (r, n.cell(row=r, column=2).value)
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=40, column=1).value = (
    "Reconciliation (v38): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 854 + not "
    "implemented 269 = 1,123. The mod's ABILITIES table is 799 entries / 854 keys, and the join mod-key -> 'Ability "
    "key(s)' returns 854 / 854 with ZERO unmatched keys in either direction. Round 150 changed triggers only. NO "
    "army-bar (army_spec) key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 150 - re-counted from the mod's own ABILITIES table: 75 families / 799 entries / 854 "
    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 150: the NEW when_ready (21), "
    "melee_unwavering 309 -> 288.")
for r in range(44, 120):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t2, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t2
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t2]
assert 44 + len(fam_sorted) == 119
n.cell(row=119, column=2).value = "TOTAL (75 families)"
n.cell(row=119, column=3).value = sum(trig.values())
n.cell(row=119, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v37")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v38 (2026-11-14)"
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("35. ROUND 150 - VALUE TARGETS, STANDSTILL, WINDS WHEN READY (v38)", None),
    ("THE RULINGS (2026-11-14)", "Blob attacks: \"Most value destroyed\" (AP-heavy attacks skip armour below 50); "
     "they wait until the caster stands still (\"For now, only the Blob attacks\"); charge abilities: \"Nothing\". "
     "Winds of Magic abilities: \"All when ready\". The map probe also logs our army's winds."),
    ("THE NEW FAMILY", "when_ready (21 Winds of Magic abilities). Generated tables: FOURTH.BLOB_DMG_TEXT (the 77 blast "
     "damage splits and AP-heavy flags) and FOURTH.UNIT_DEF_TEXT (armour and hit points of 587 infantry types)."),
    ("THE ARITHMETIC", "No count change: 854 implemented / 269 not implemented (27 skipped); 799 entries / 854 keys; "
     "75 families; melee_unwavering 309 -> 288."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-14"
ch.cell(row=r, column=2).value = "v38"
ch.cell(row=r, column=3).value = (
    "ROUND 150. The 77 blob attacks: the most enemy value destroyed, armour rule 50 for AP-heavy attacks, never while "
    "the caster moves. The 21 Winds of Magic abilities on the NEW when_ready. 854 / 269 unchanged; 75 families. "
    "SHIPPED: installed pack md5 %s; harness 149 full suite 6,374 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-14; xlsx v38 supersedes v37; v1-v37 byte-unchanged."
wb.save(DST)
print("wrote", DST)
