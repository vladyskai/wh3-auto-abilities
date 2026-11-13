#!/usr/bin/env python3
"""Build WH3_abilities_master_v37_2026-11-13.xlsx from v36 - round 146: the blob trigger.

(1) 77 rows NOT IMPLEMENTED -> IMPLEMENTED on the NEW enemy_blob: the open group B attacks whose projectile explodes
    (Dead Eye and Focused Shot stay open: the game lets them target single-entity units only).
(2) Implemented 777 -> 854 rows / keys; not implemented among the included 346 -> 269 (27 skipped). The mod 799 entries /
    854 keys; 73 -> 74 families: the Numbers trigger table gains one row (bombardment block 119 -> 120). Definitions:
    title v37, the two count rows, section 34. Changelog: a v37 row.
v1-v36 are never opened for writing.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v36_2026-11-13.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v37_2026-11-13.xlsx"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
RULE = "user rulings 2026-11-13 (the blob trigger: \"A. Density line\", \"10 m\", \"79 open attacks\"); "
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

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
n_new = n_skip = 0
for r in range(2, ws.max_row + 1):
    ks = keys_of(r)
    if len(ks) == 1 and (ks[0] in NEW or ks[0] in SKIP):
        assert str(ws.cell(row=r, column=18).value) == "IN-WHEEL" and str(ws.cell(row=r, column=20).value) == "NOT IMPLEMENTED", ks
        if ks[0] in NEW:
            fam, text = NEW[ks[0]]
            ws.cell(row=r, column=20).value = "IMPLEMENTED"
            ws.cell(row=r, column=21).value = fam
            ws.cell(row=r, column=22).value = text
            n_new += 1
        else:
            ws.cell(row=r, column=19).value = SKIP[ks[0]]
            ws.cell(row=r, column=20).value = "SKIPPED (user decision)"
            ws.cell(row=r, column=21).value = "-"
            ws.cell(row=r, column=22).value = "-"
            n_skip += 1
assert (n_new, n_skip) == (77, 0), (n_new, n_skip)

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
assert len(trig) == 74 and trig["enemy_blob"] == 77, (len(trig),)

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
assert n.cell(row=119, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert all(int(str(m).split(":")[0][1:]) < 108 for m in n.merged_cells.ranges)
n.insert_rows(117, 1)
assert n.cell(row=120, column=1).value == "Bombardment set (COMPLETE - round 108)"
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-11-13     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v37 - ROUND 146: the blob trigger. 77 exploding enemy-unit attacks on the NEW enemy_blob (the best SAFE visible "
    "enemy infantry unit whose blast reaches half a packed block's worth of soldiers; none of ours within blast + 10 m). "
    "Implemented 777 + 77 = 854 rows / 854 keys; not implemented among the included 346 - 77 = 269 (27 skipped). The "
    "mod: 799 entries / 854 keys / 74 trigger families.)")
for r, num, label, abs_, p1, p2 in [
        (13, 4, "Implemented among the included", N_IMPL_ROWS, N_IMPL_ROWS / tot, N_IMPL_ROWS / 1123.0),
        (14, 5, "Not implemented among the included", NOT_IMPL_IN, NOT_IMPL_IN / tot, NOT_IMPL_IN / 1123.0),
        (16, 7, "All implemented in the mod (4 + 6)", N_IMPL_KEYS, N_IMPL_KEYS / tot, N_IMPL_KEYS / 1123.0)]:
    for c, v in enumerate((num, label, abs_, p1, p2), 1):
        n.cell(row=r, column=c).value = v
n.cell(row=18, column=1).value = str(n.cell(row=18, column=1).value).replace("777 implemented", "854 implemented")
for i, f in enumerate(fam_order):
    r = 20 + i
    assert n.cell(row=r, column=2).value == f, (r, n.cell(row=r, column=2).value)
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=40, column=1).value = (
    "Reconciliation (v37): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 854 + not "
    "implemented 269 = 1,123. The mod's ABILITIES table is 799 entries / 854 keys, and the join mod-key -> 'Ability "
    "key(s)' returns 854 / 854 with ZERO unmatched keys in either direction. 722 + 77 (round 146, the blob trigger) = "
    "799 entries; 777 + 77 = 854 keys. NO army-bar (army_spec) key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 146 - re-counted from the mod's own ABILITIES table: 74 families / 799 entries / 854 "
    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 146: the NEW enemy_blob (77).")
for r in range(44, 119):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t2, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t2
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t2]
assert 44 + len(fam_sorted) == 118
n.cell(row=118, column=2).value = "TOTAL (74 families)"
n.cell(row=118, column=3).value = sum(trig.values())
n.cell(row=118, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v36")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v37 (2026-11-13)"
r11 = d.cell(row=11, column=2)
old11 = ("777 keys across 777 numbered rows (rounds 122-123 added 21, round 130 added 2, round 131 removed the 9 "
         "stances, round 134 removed the 2 Thunderburner keys, round 142 added 6, round 143 added 11, round 144 added 10)")
assert old11 in r11.value
r11.value = r11.value.replace(old11, "854 keys across 854 numbered rows (rounds 122-123 added 21, round 130 added 2, "
                              "round 131 removed the 9 stances, round 134 removed the 2 Thunderburner keys, round 142 "
                              "added 6, round 143 added 11, round 144 added 10, round 146 added 77)")
r12 = d.cell(row=12, column=2)
assert "(1,023 keys, of which 346 are in the wheel)" in r12.value
r12.value = r12.value.replace("(1,023 keys, of which 346 are in the wheel)", "(946 keys, of which 269 are in the wheel)")
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("34. ROUND 146 - THE BLOB TRIGGER (v37)", None),
    ("THE RULINGS (2026-11-13)", "\"A. Density line\" (fire when the blast covers at least half of what it covers inside "
     "a tightly packed infantry block), \"10 m\" (no soldier of ours within blast + 10 m of the target), \"79 open "
     "attacks\" (77 built; Dead Eye and Focused Shot target single entities only)."),
    ("THE NEW FAMILY", "enemy_blob, on the round-145 map reads; generated tables FOURTH.BLAST_TEXT (77 blast radii) and "
     "FOURTH.SPACING_TEXT (535 infantry spacings), FOURTH.PACKED_M2 = 2.368; eight new 70% constants (55, 60, 80, 130, "
     "250, 350, 400, 600 m)."),
    ("THE ARITHMETIC", "Implemented 777 + 77 = 854 rows / keys; not implemented among the included 346 - 77 = 269 "
     "(27 skipped). The mod 722 + 77 = 799 entries / 854 keys; 74 families."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-13"
ch.cell(row=r, column=2).value = "v37"
ch.cell(row=r, column=3).value = (
    "ROUND 146. The blob trigger: 77 exploding enemy-unit attacks IMPLEMENTED on the NEW enemy_blob. 777 -> 854 "
    "implemented; 346 -> 269 not implemented (27 skipped). Mod 799 / 854 / 74 families. SHIPPED: installed pack md5 %s; "
    "harness 145 full suite 6,339 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-13 (the blob trigger); xlsx v37 supersedes v36; v1-v36 byte-unchanged."
wb.save(DST)
print("wrote", DST)
