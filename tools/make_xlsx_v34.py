#!/usr/bin/env python3
"""Build WH3_abilities_master_v34_2026-11-13.xlsx from v33 - round 142: open batch 1 and Blooood! when moving.

(1) 6 rows NOT IMPLEMENTED -> IMPLEMENTED: More Powder!, Restock! (gunnery school) on ally_ammo_low; Master of Mists
    (2 keys) on the NEW ground_ally_before_range; Of Warp and Ruin on the NEW self_shooting_clear; Ominous Powder on the
    NEW self_shooting_healthy. Blooood! moves to the NEW self_moving.
(2) Implemented 750 -> 756 rows / keys; not implemented among the included 373 -> 367. The mod 703 entries / 756 keys;
    64 -> 67 families (self_running has no entry left): the Numbers trigger table gains three rows (bombardment block
    110 -> 113). Definitions: title v34, the two count rows, section 31. Changelog: a v34 row.
v1-v33 are never opened for writing.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v33_2026-11-13.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v34_2026-11-13.xlsx"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
RULE = "user ruling 2026-11-13 (open batch 1); "
AMMO = ("ally_ammo_low: not routing; the tracked ally (alive, not the owner, not routing) within the bound that is "
        "SHOOTING (firing flag on; not moving unless it fires on the move) with 70% or less of its ammunition left; the "
        "one with the least left wins; an ally refilled in the last 12 s is skipped; bound: 70 m (70% of the ability's "
        "100 m ally cast reach); cast target: that ally; pre-cast re-check: still shooting and at or below the line; "
        + RULE + "same as Restock! (round 130); " + SHARED_TAIL)
MIST = ("ground_ally_before_range: not routing; the closest friendly MISSILE unit (the caster included; allies within "
        "175 m = 70% of the ability's 250 m reach) that is out of melee with ammunition, has NO live enemy inside its "
        "own missile_range() and the nearest one inside missile_range x 1.35 (1 + 0.50 x 0.70: the 70% rule on the "
        "+50% range bonus); cast target: the GROUND under that unit; pre-cast re-check: the same condition; " + RULE
        + SHARED_TAIL)
CLEAR = ("self_shooting_clear: not routing; shooting past its cast point (not moving unless it fires on the move) AND "
         "its current_target() readable and NOT in melee (its shots can hurt friendly units); cast target: self; "
         + RULE + SHARED_TAIL)
HEALTHY = ("self_shooting_healthy: not routing; shooting past its cast point (not moving unless it fires on the move) "
           "AND its own health readable and above 50% (the ability damages its carrier); cast target: self; " + RULE
           + SHARED_TAIL)
MOVING = ("self_moving: not routing; is_moving() exactly true (QA battles of 2026-11-13: a Hellcannon never runs, "
          "is_moving_fast() is always false); user ruling 2026-11-13: \"When moving\"; cast target: self; " + SHARED_TAIL)
NEW = {"wh2_dlc11_hero_abilities_more_powder": ("ally_ammo_low", AMMO),
       "wh3_dlc25_abilities_restock_gunnery_school": ("ally_ammo_low", AMMO),
       "wh3_dlc27_character_abilities_master_of_mists": ("ground_ally_before_range", MIST),
       "wh3_dlc27_character_abilities_master_of_mists_custom": ("ground_ally_before_range", MIST),
       "wh3_dlc29_unit_abilities_of_warp_and_ruin": ("self_shooting_clear", CLEAR),
       "wh3_dlc25_item_abilities_ominous_powder": ("self_shooting_healthy", HEALTHY)}

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
n_new = n_b = 0
for r in range(2, ws.max_row + 1):
    ks = keys_of(r)
    if len(ks) == 1 and ks[0] in NEW:
        assert str(ws.cell(row=r, column=18).value) == "IN-WHEEL" and str(ws.cell(row=r, column=20).value) == "NOT IMPLEMENTED", ks
        fam, text = NEW[ks[0]]
        ws.cell(row=r, column=20).value = "IMPLEMENTED"
        ws.cell(row=r, column=21).value = fam
        ws.cell(row=r, column=22).value = text
        n_new += 1
    elif ks == ["wh_main_unit_abilities_blooood"]:
        assert str(ws.cell(row=r, column=21).value) == "self_running"
        ws.cell(row=r, column=21).value = "self_moving"
        ws.cell(row=r, column=22).value = MOVING
        n_b += 1
assert (n_new, n_b) == (6, 1), (n_new, n_b)

rows = [(r, keys_of(r), str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=20).value),
         str(ws.cell(row=r, column=21).value)) for r in range(2, ws.max_row + 1)]
N = len(rows)
impl = [x for x in rows if x[3] == "IMPLEMENTED"]
N_IMPL_ROWS = len(impl)
N_IMPL_KEYS = len(set(k for x in impl for k in x[1]))
assert (N, N_IMPL_ROWS, N_IMPL_KEYS) == (1800, 756, 756), (N, N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = 1123 - N_IMPL_ROWS
assert NOT_IMPL_IN == 367
entries, _, _ = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
assert (len(entries), len(fam_by_key)) == (703, 756)
assert set(k for x in impl for k in x[1]) == set(fam_by_key)
assert not [x[1][0] for x in impl if x[4] != fam_by_key.get(x[1][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 67 and trig["ally_ammo_low"] == 3 and trig["self_running"] == 0, (len(trig), trig["ally_ammo_low"])

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
assert n.cell(row=110, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert all(int(str(m).split(":")[0][1:]) < 108 for m in n.merged_cells.ranges)
n.insert_rows(108, 3)
assert n.cell(row=113, column=1).value == "Bombardment set (COMPLETE - round 108)"
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-11-13     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v34 - ROUND 142: open batch 1. More Powder! and Restock! (gunnery school) on ally_ammo_low; Master of Mists on the "
    "NEW ground_ally_before_range; Of Warp and Ruin on the NEW self_shooting_clear; Ominous Powder on the NEW "
    "self_shooting_healthy; Blooood! on the NEW self_moving. Implemented 750 + 6 = 756 rows / 756 keys; not implemented "
    "among the included 373 - 6 = 367. The mod: 703 entries / 756 keys / 67 trigger families.)")
for r, num, label, abs_, p1, p2 in [
        (13, 4, "Implemented among the included", N_IMPL_ROWS, N_IMPL_ROWS / tot, N_IMPL_ROWS / 1123.0),
        (14, 5, "Not implemented among the included", NOT_IMPL_IN, NOT_IMPL_IN / tot, NOT_IMPL_IN / 1123.0),
        (16, 7, "All implemented in the mod (4 + 6)", N_IMPL_KEYS, N_IMPL_KEYS / tot, N_IMPL_KEYS / 1123.0)]:
    for c, v in enumerate((num, label, abs_, p1, p2), 1):
        n.cell(row=r, column=c).value = v
n.cell(row=18, column=1).value = str(n.cell(row=18, column=1).value).replace("750 implemented", "756 implemented")
for i, f in enumerate(fam_order):
    r = 20 + i
    assert n.cell(row=r, column=2).value == f, (r, n.cell(row=r, column=2).value)
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=40, column=1).value = (
    "Reconciliation (v34): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 756 + not "
    "implemented 367 = 1,123. The mod's ABILITIES table is 703 entries / 756 keys, and the join mod-key -> 'Ability "
    "key(s)' returns 756 / 756 with ZERO unmatched keys in either direction. 698 + 5 (round 142, open batch 1) = 703 "
    "entries; 750 + 6 = 756 keys. NO army-bar (army_spec) key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 142 - re-counted from the mod's own ABILITIES table: 67 families / 703 entries / 756 "
    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 142: ally_ammo_low 1 -> 3; the NEW "
    "ground_ally_before_range (1 entry / 2 keys), self_shooting_clear (1), self_shooting_healthy (1), self_moving (1).")
for r in range(44, 112):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t2, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t2
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t2]
assert 44 + len(fam_sorted) == 111
n.cell(row=111, column=2).value = "TOTAL (67 families)"
n.cell(row=111, column=3).value = sum(trig.values())
n.cell(row=111, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v33")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v34 (2026-11-13)"
r11 = d.cell(row=11, column=2)
old11 = "750 keys across 750 numbered rows (rounds 122-123 added 21, round 130 added 2, round 131 removed the 9 stances, round 134 removed the 2 Thunderburner keys)"
assert old11 in r11.value
r11.value = r11.value.replace(old11, "756 keys across 756 numbered rows (rounds 122-123 added 21, round 130 added 2, round "
                              "131 removed the 9 stances, round 134 removed the 2 Thunderburner keys, round 142 added 6)")
r12 = d.cell(row=12, column=2)
assert "(1,050 keys, of which 373 are in the wheel)" in r12.value
r12.value = r12.value.replace("(1,050 keys, of which 373 are in the wheel)", "(1,044 keys, of which 367 are in the wheel)")
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("31. ROUND 142 - OPEN BATCH 1 AND BLOOOOD! (v34)", None),
    ("THE RULINGS (2026-11-13)", "More Powder!, Restock! (gunnery school): \"Same as Restock!\". Master of Mists: "
     "\"Before range (Farsight-like)\". Of Warp and Ruin: \"Shooting, not into melee\". Ominous Powder: \"Shooting, "
     "health above 50%\". Blooood!: \"When moving\" (a Hellcannon never runs)."),
    ("THE NEW FAMILIES", "ground_ally_before_range (Master of Mists, 2 keys), self_shooting_clear (Of Warp and Ruin), "
     "self_shooting_healthy (Ominous Powder), self_moving (Blooood!). The 250 m reach -> FOURTH.ALLY_CAST_R250 = 175."),
    ("THE ARITHMETIC", "Implemented 750 + 6 = 756 rows / keys; not implemented among the included 373 - 6 = 367. The mod "
     "698 + 5 = 703 entries / 756 keys; 67 families."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-13"
ch.cell(row=r, column=2).value = "v34"
ch.cell(row=r, column=3).value = (
    "ROUND 142. Open batch 1: More Powder!, Restock! (gunnery school), Master of Mists (2 keys), Of Warp and Ruin, "
    "Ominous Powder IMPLEMENTED; Blooood! on the NEW self_moving. 750 -> 756 implemented; 373 -> 367 not implemented. "
    "Mod 703 / 756 / 67 families. SHIPPED: installed pack md5 %s; harness 141 full suite 6,135 checks / 0 failures."
    % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-13 (open batch 1); xlsx v34 supersedes v33; v1-v33 byte-unchanged."
wb.save(DST)
print("wrote", DST)
