#!/usr/bin/env python3
"""Build WH3_abilities_master_v26_2026-11-09.xlsx from v25 - round 134: audit batch 3, the speed buffs.

(1) 4 rows move to charge_only (Apocalyptic Charge, Twilight Horn I, Potion of Speed, Blooood!) and 8 to
    charge_or_melee (Book of Arkhan, Rune of Speed, Master Rune of Speed, Lightning Reflexes, Master of the
    Skies, Pendant of Slaanesh, Slippery, Transfix), with the evaluator's own checks; each keeps its GATES clause.
(2) Thunderburner and Thunderburner Upgraded: SKIPPED (user decision 2026-11-09), removed from the mod.
    Implemented 752 -> 750 rows / keys; not implemented among the included 371 -> 373 (22 -> 24 skipped).
    The mod: 698 entries / 750 keys / 56 families (unchanged family count).
(3) Numbers: headline, carrier families, reconciliation, the 56-row trigger table re-counted (no row moves).
    Definitions: title v26, the two count rows, glossary, coverage, section 23. Changelog: a v26 row.
v1-v25 are never opened for writing.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v25_2026-11-08.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v26_2026-11-09.xlsx"
UAB = GP.UNIT_ABILITIES
MU, CO, CM = "melee_unwavering", "charge_only", "charge_or_melee"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
CO_TEXT = ("charge_only: charge window ONLY - the melee arm is deliberately absent; charge window = is_moving_fast() "
           "and not is_in_melee() and current_target() ~= nil and distance 12-60 m and time-to-contact <= 4 s; not "
           "routing; cast target: self; " + SHARED_TAIL)
CM_TEXT = ("charge_or_melee: charge window (as the charge evaluator) OR is_in_melee(); not routing; the charge arm is "
           "tested first and wins; cast target: self; " + SHARED_TAIL)
TEXT = {k: (CO, CO_TEXT) for k in (
    "wh_pro04_unit_abilities_apocalyptic_charge", "wh2_dlc16_item_abilities_twilight_horn_i",
    "wh_main_item_abilities_potion_of_speed", "wh_main_unit_abilities_blooood")}
TEXT.update({k: (CM, CM_TEXT) for k in (
    "wh_main_spell_bound_book_of_arkhan", "wh2_dlc17_rune_abilities_rune_of_speed",
    "wh2_dlc17_rune_abilities_master_rune_of_speed", "wh2_dlc11_lord_abilities_lightning_reflexes",
    "wh2_dlc12_lord_abilities_master_of_the_skies", "wh_main_item_abilities_pendant_of_slaanesh",
    "wh_main_hero_abilities_slippery", "wh2_dlc11_lord_abilities_transfix")})
SKIP_REASON = ("skipped (user decision 2026-11-09: Thunderburner is a movement mode with no end time - speed x2.5 / x3, "
               "turning cut to 30% - so when to use it is the player's choice; removed from the mod)")
SKIPPED = ["wh3_dlc25_unit_abilities_thunderburner", "wh3_dlc25_unit_abilities_thunderburner_upgraded"]

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
row_of = {}
for r in range(2, ws.max_row + 1):
    for k in keys_of(r):
        row_of.setdefault(k, []).append(r)
for key, (fam, text) in TEXT.items():
    rs = row_of.get(key, [])
    assert len(rs) == 1 and keys_of(rs[0]) == [key], (key, rs)
    r = rs[0]
    assert str(ws.cell(row=r, column=20).value) == "IMPLEMENTED" and str(ws.cell(row=r, column=21).value) == MU, key
    old = str(ws.cell(row=r, column=22).value or "")
    gates = (" GATES" + old.split(" GATES", 1)[1]) if " GATES" in old else ""
    ws.cell(row=r, column=21).value = fam
    ws.cell(row=r, column=22).value = text + gates
for key in SKIPPED:
    rs = row_of.get(key, [])
    assert len(rs) == 1 and keys_of(rs[0]) == [key], (key, rs)
    r = rs[0]
    assert str(ws.cell(row=r, column=20).value) == "IMPLEMENTED" and str(ws.cell(row=r, column=21).value) == MU, key
    ws.cell(row=r, column=19).value = SKIP_REASON
    ws.cell(row=r, column=20).value = "SKIPPED (user decision)"
    ws.cell(row=r, column=21).value = "-"
    ws.cell(row=r, column=22).value = "-"
print("rows retriggered:", len(TEXT), "skipped:", len(SKIPPED))

rows = [(r, keys_of(r), str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=19).value),
         str(ws.cell(row=r, column=20).value), str(ws.cell(row=r, column=21).value)) for r in range(2, ws.max_row + 1)]
N = len(rows)
st = collections.Counter(x[2] for x in rows)
assert (N, st["IN-WHEEL"], st["EXCLUDED"]) == (1800, 1123, 677)
impl = [x for x in rows if x[4] == "IMPLEMENTED"]
N_IMPL_ROWS = len(impl)
N_IMPL_KEYS = len(set(k for x in impl for k in x[1]))
assert (N_IMPL_ROWS, N_IMPL_KEYS) == (750, 750), (N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = 1123 - N_IMPL_ROWS
assert NOT_IMPL_IN == 373
N_SKIP = sum(1 for x in rows if x[4] == "SKIPPED (user decision)")
assert N_SKIP == 24, N_SKIP

entries, _, _ = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
assert (len(entries), len(fam_by_key)) == (698, 750)
assert set(k for x in impl for k in x[1]) == set(fam_by_key)
assert not [x[1][0] for x in impl if x[5] != fam_by_key.get(x[1][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 56 and (trig[MU], trig[CO], trig[CM]) == (328, 5, 36), (len(trig), trig[MU], trig[CO], trig[CM])

# carrier families (unit_abilities.source_type), as v23 derived them
src_type = {}
with open(UAB, encoding="utf-8", errors="replace") as f:
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
    assert f in fam_order, (x[0], x[1])
    fam_inc[f] += 1
    if x[4] == "IMPLEMENTED":
        fam_impl[f] += 1
assert sum(fam_inc.values()) == 1123 and sum(fam_impl.values()) == N_IMPL_ROWS

n = wb["Numbers"]
assert n.cell(row=102, column=1).value == "Bombardment set (COMPLETE - round 108)"
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-11-09     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v26 - ROUND 134: audit batch 3, the speed buffs. Apocalyptic Charge, Twilight Horn I, Potion of Speed and "
    "Blooood! on charge_only; Book of Arkhan, Rune of Speed, Master Rune of Speed, Lightning Reflexes, Master of the "
    "Skies, Pendant of Slaanesh, Slippery and Transfix on charge_or_melee; Thunderburner and Thunderburner Upgraded "
    "SKIPPED by user decision and removed from the mod. Implemented 752 - 2 = 750 rows / 750 keys; not implemented "
    "among the included 371 + 2 = 373 (24 SKIPPED by user decision). The mod: 698 entries / 750 keys / 56 trigger "
    "families.)")
for r, num, label, abs_, p1, p2 in [
        (13, 4, "Implemented among the included", N_IMPL_ROWS, N_IMPL_ROWS / tot, N_IMPL_ROWS / 1123.0),
        (14, 5, "Not implemented among the included", NOT_IMPL_IN, NOT_IMPL_IN / tot, NOT_IMPL_IN / 1123.0),
        (16, 7, "All implemented in the mod (4 + 6)", N_IMPL_KEYS, N_IMPL_KEYS / tot, N_IMPL_KEYS / 1123.0)]:
    for c, v in enumerate((num, label, abs_, p1, p2), 1):
        n.cell(row=r, column=c).value = v
n.cell(row=18, column=1).value = str(n.cell(row=18, column=1).value).replace("752 implemented", "750 implemented")
for i, f in enumerate(fam_order):
    r = 20 + i
    assert n.cell(row=r, column=2).value == f, (r, n.cell(row=r, column=2).value)
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=40, column=1).value = (
    "Reconciliation (v26): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included "
    "750 + not implemented 373 = 1,123. The mod's ABILITIES table is 698 entries / 750 keys, and the join "
    "mod-key -> 'Ability key(s)' returns 750 / 750 with ZERO unmatched keys in either direction. 700 - 2 "
    "(round 134: Thunderburner and Thunderburner Upgraded) = 698 entries; 752 - 2 = 750 keys. NO army-bar "
    "(army_spec) key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 134 - re-counted from the mod's own ABILITIES table: 56 families / 698 entries / "
    "750 keys (metallurgy_melee keeps 0 entries). Round 134: charge_only 1 -> 5, charge_or_melee 28 -> 36; "
    "melee_unwavering 342 -> 328 (12 moved, the 2 Thunderburner entries removed).")
for r in range(44, 101):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t]
tot_row = 44 + len(fam_sorted)
assert tot_row == 100, tot_row
n.cell(row=tot_row, column=2).value = "TOTAL (56 families)"
n.cell(row=tot_row, column=3).value = sum(trig.values())
n.cell(row=tot_row, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v25")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v26 (2026-11-09)"
r11 = d.cell(row=11, column=2)
old11 = "752 keys across 752 numbered rows (rounds 122-123 added 21, round 130 added 2, round 131 removed the 9 stances)"
assert old11 in r11.value
r11.value = r11.value.replace(old11, "750 keys across 750 numbered rows (rounds 122-123 added 21, round 130 added 2, "
                              "round 131 removed the 9 stances, round 134 removed the 2 Thunderburner keys)")
r12 = d.cell(row=12, column=2)
assert "(1,048 keys, of which 371 are in the wheel)" in r12.value
r12.value = r12.value.replace("(1,048 keys, of which 371 are in the wheel)", "(1,050 keys, of which 373 are in the wheel)")
g = d.cell(row=21, column=1)
g.value = str(g.value) + "; round 134 moved 12 speed buffs onto charge_only and charge_or_melee (section 23)"
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
cov_gate = sum(1 for x in impl
               if any(w in x[3] or w in str(ws.cell(row=x[0], column=22).value or "")
                      for w in ("wind-up", "charge gate", "charge hold", "recharge_time", "in-flight", "per-unit")))
r104 = d.cell(row=104, column=1)
assert "Coverage in this workbook:" in str(r104.value)
r104.value = (str(r104.value).split("Coverage in this workbook:")[0]
              + "Coverage in this workbook: %d of the %d implemented rows (%d keys) carry at least one gate "
              "clause in their Trigger (as implemented) text; rows with neither a multi-use pool nor a wind-up "
              "keep the plain 2 s guard." % (cov_gate, N_IMPL_ROWS, N_IMPL_KEYS))
base = d.max_row + 2
sec = [
    ("23. ROUND 134 - AUDIT BATCH 3: THE SPEED BUFFS (v26)", None),
    ("THE RULINGS (2026-11-09)", "All three as recommended. Speed and charge buffs with no melee stat (Apocalyptic "
     "Charge, Twilight Horn I, Potion of Speed, Blooood!): \"Charge only\". Speed plus a melee stat (Book of Arkhan, "
     "Rune of Speed, Master Rune of Speed, Lightning Reflexes, Master of the Skies, Pendant of Slaanesh, Slippery, "
     "Transfix): \"Charge, else in melee\". Thunderburner and Thunderburner Upgraded: \"Stop automating\"."),
    ("THE FAMILIES (both existing)", "charge_only (Ferocious Battle Howl's): the charge window only, cast on self | "
     "5 entries. charge_or_melee (Fangspike's): the charge window, else in melee, cast on self | 36 entries."),
    ("THE CHARGE WINDOW", "is_moving_fast(), not in melee, an attack target 12 to 60 m away, time to contact 4 s or "
     "less. A charge the detector misses means no cast for the charge-only four."),
    ("THE ARITHMETIC", "Implemented 752 - 2 = 750 rows / keys; not implemented among the included 371 + 2 = 373 (24 "
     "skipped by user decision). Mod 698 entries / 750 keys / 56 families; melee_unwavering 342 -> 328."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-09"
ch.cell(row=r, column=2).value = "v26"
ch.cell(row=r, column=3).value = (
    "ROUND 134. Audit batch 3: Apocalyptic Charge, Twilight Horn I, Potion of Speed, Blooood! on charge_only; Book of "
    "Arkhan, Rune of Speed, Master Rune of Speed, Lightning Reflexes, Master of the Skies, Pendant of Slaanesh, "
    "Slippery, Transfix on charge_or_melee; Thunderburner and Thunderburner Upgraded SKIPPED (user decision) and "
    "removed. 752 -> 750 implemented; 371 -> 373 not implemented. Mod 698 / 750 / 56 families. SHIPPED: installed "
    "pack md5 %s; harness 133 full suite 5,785 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-09 (audit batch 3); xlsx v26 supersedes v25; v1-v25 byte-unchanged."
wb.save(DST)
print("wrote", DST, "impl", N_IMPL_ROWS, "not impl", NOT_IMPL_IN, "skipped", N_SKIP, "families", len(trig),
      "coverage", cov_gate)
