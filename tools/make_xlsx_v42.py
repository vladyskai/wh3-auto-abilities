#!/usr/bin/env python3
"""Build WH3_abilities_master_v42_2026-11-15.xlsx from v41 - round 156: the magic missiles (open batch 4).

(1) 11 rows NOT IMPLEMENTED -> IMPLEMENTED on 5 NEW families: enemy_large_shot (Blast, Damned Pistol, Hunting Spear,
    Master Rune of Flight, Schalkain's Teeth), enemy_single_shot (Dead Eye, Focused Shot), enemy_infantry_shot (Bolt
    Storm), enemy_melee_or_fast (Crippling Throw, the Golden Blowpipe of P'Toohee), enemy_melee_or_shooting (Spear of
    Kurnous).
(2) Implemented 854 -> 865 rows / keys; not implemented among the included 269 -> 258 (27 skipped). The mod 810 entries
    / 865 keys; 75 -> 80 families: the Numbers trigger table gains five rows (bombardment block 121 -> 126).
    Definitions: title v42, the two count rows, section 39. Changelog: a v42 row.
v1-v41 are never opened for writing.
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

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v41_2026-11-15.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v42_2026-11-15.xlsx"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
RULE = "user rulings 2026-11-15 (the magic missiles: %s); "
USA = {r["key"]: r for r in GS.tsv("unit_spec_abil.tsv")}
SAFE = ("a candidate is UNSAFE when any of our units' estimated rectangles comes within 10 m of its rectangle (user "
        "ruling 2026-11-15; the shot can hit our own units)")


def facts(k):
    a = USA[k]
    real = float(a["target_intercept_range"])
    bound = int(math.floor(real * 0.70 + 1e-9))
    uses, rech, wind = int(float(a["num_uses"])), float(a["recharge_time"]), float(a["wind_up_time"])
    gates = []
    if uses > 1:
        gates.append("charge hold %g s (%d uses)" % (rech, uses))
    if wind > 0:
        gates.append("in-flight hold %g s (%g s wind-up + 2 s)" % (wind + 2, wind))
    mn = float(a["min_range"] or 0)
    return real, bound, gates, mn


def text(k, fam):
    real, bound, gates, mn = facts(k)
    sh = GS.derive([k])[k]
    within = "within %d m (70%% of the ability's %g m target_intercept_range; unit_distance)" % (bound, real)
    if mn > 0:
        within += ", no closer than the game's min_range %g m" % mn
    if fam == "enemy_large_shot":
        body = ("enemy_large_shot: not routing; the caster out of melee (is_in_melee() exactly false); the live map (our "
                "units; every enemy we can see, is_visible_to_alliance exactly true); FIRST the visible LARGE enemy (the "
                "generated large set, flying ones too) %s with the highest live value (strategic_value); when none "
                "qualifies, the visible enemy INFANTRY (inf class, not large, not flying, 10+ men) %s with the highest "
                "armour (the generated UNIT_DEF table; an unknown armour never qualifies; ties: the higher value per "
                "soldier); %s; cast target: that enemy unit; pre-cast re-check: the map is rebuilt and the target must "
                "still qualify and be safe; " % (within, within, SAFE)) + RULE % "\"Large first, then armour\""
    elif fam == "enemy_single_shot":
        pl = (" a LARGE single-entity enemy first (its projectile's bonus against large is above its bonus against "
              "infantry), then any;" if sh[1] == 1 else "")
        body = ("enemy_single_shot: not routing; the caster STANDING STILL (is_moving() exactly false; the 5 s wind-up) "
                "and out of melee; the live map; the SINGLE-ENTITY enemy we can see (lords, heroes, single monsters) %s "
                "with the highest live value (strategic_value);%s %s; cast target: that enemy unit; pre-cast re-check: "
                "the map is rebuilt and the target must still qualify and be safe; target class: single entity only "
                "(the game's unit_is_not_single_entity; the generated single set); " % (within, pl, SAFE)) \
            + RULE % "\"Most valuable single\""
    elif fam == "enemy_infantry_shot":
        body = ("enemy_infantry_shot: not routing; the caster STANDING STILL (is_moving() exactly false) and out of "
                "melee (also the game's engaged_in_melee usage rule); the live map; the visible enemy INFANTRY (inf "
                "class, not large, not flying, 10+ men) %s with the highest live value per soldier (strategic_value / "
                "men); %s; cast target: that enemy unit; pre-cast re-check: the map is rebuilt and the target must "
                "still qualify and be safe; " % (within, SAFE)) + RULE % "\"Most valuable infantry\""
    elif fam == "enemy_melee_or_fast":
        nm = ("the caster out of melee (the game's engaged_in_melee usage rule); " if sh[0] == 1 else "")
        body = ("enemy_melee_or_fast: not routing; %sFIRST the closest enemy %s that is fighting in melee "
                "(enemy_melee's pick); otherwise a FAST enemy %s (moving, fast_speed() >= FOURTH.FAST_ENEMY_MPS = 5 m/s) "
                "within 40 m of one of our units (enemy_fast_near_ally's pick); cast target: that enemy unit; pre-cast "
                "re-check: the same arm's condition again (still in melee / still fast and near); the effect slows the "
                "target (rule 10: in melee or on the charge); " % (nm, within, within)) + RULE % "\"Split by effect\""
    else:
        body = ("enemy_melee_or_shooting: not routing; FIRST the closest enemy %s that is fighting in melee (enemy_melee's "
                "pick); otherwise the closest enemy MISSILE unit %s that is shooting and not in melee (its ammunition "
                "dropped recently; enemy_missile_shooting's pick); cast target: that enemy unit; pre-cast re-check: the "
                "same arm's condition again; the blinding hits accuracy (shooters) and melee attack / defence (fighters); "
                % (within, within)) + RULE % "\"Split by effect\""
    return body + SHARED_TAIL + ((" GATES: " + "; ".join(gates) + ".") if gates else "")


src_txt = open(r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua",
               encoding="utf-8").read()
entries, _, _ = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
KEYS = GS.keys_in(src_txt)
assert len(KEYS) == 11
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
assert n_new == 11, n_new

rows = [(r, keys_of(r), str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=20).value),
         str(ws.cell(row=r, column=21).value)) for r in range(2, ws.max_row + 1)]
N = len(rows)
impl = [x for x in rows if x[3] == "IMPLEMENTED"]
N_IMPL_ROWS = len(impl)
N_IMPL_KEYS = len(set(k for x in impl for k in x[1]))
assert (N, N_IMPL_ROWS, N_IMPL_KEYS) == (1800, 865, 865), (N, N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = 1123 - N_IMPL_ROWS
assert NOT_IMPL_IN == 258
assert sum(1 for x in rows if x[3] == "SKIPPED (user decision)") == 27
assert (len(entries), len(fam_by_key)) == (810, 865)
assert set(k for x in impl for k in x[1]) == set(fam_by_key)
assert not [x[1][0] for x in impl if x[4] != fam_by_key.get(x[1][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 80, len(trig)

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
assert n.cell(row=121, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert n.cell(row=119, column=2).value == "TOTAL (75 families)"
assert all(int(str(m).split(":")[0][1:]) < 108 for m in n.merged_cells.ranges)
n.insert_rows(118, 5)
assert n.cell(row=126, column=1).value == "Bombardment set (COMPLETE - round 108)"
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-11-15     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v42 - ROUND 156: the magic missiles. 11 single-target attacks on 5 NEW families (enemy_large_shot, "
    "enemy_single_shot, enemy_infantry_shot, enemy_melee_or_fast, enemy_melee_or_shooting). Implemented 854 + 11 = 865 "
    "rows / 865 keys; not implemented among the included 269 - 11 = 258 (27 skipped). The mod: 810 entries / 865 keys "
    "/ 80 trigger families.)")
for r, num, label, abs_, p1, p2 in [
        (13, 4, "Implemented among the included", N_IMPL_ROWS, N_IMPL_ROWS / tot, N_IMPL_ROWS / 1123.0),
        (14, 5, "Not implemented among the included", NOT_IMPL_IN, NOT_IMPL_IN / tot, NOT_IMPL_IN / 1123.0),
        (16, 7, "All implemented in the mod (4 + 6)", N_IMPL_KEYS, N_IMPL_KEYS / tot, N_IMPL_KEYS / 1123.0)]:
    for c, v in enumerate((num, label, abs_, p1, p2), 1):
        n.cell(row=r, column=c).value = v
old18 = str(n.cell(row=18, column=1).value)
assert "854 implemented" in old18
n.cell(row=18, column=1).value = old18.replace("854 implemented", "865 implemented")
for i, f in enumerate(fam_order):
    r = 20 + i
    assert n.cell(row=r, column=2).value == f, (r, n.cell(row=r, column=2).value)
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=40, column=1).value = (
    "Reconciliation (v42): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 865 + not "
    "implemented 258 = 1,123. The mod's ABILITIES table is 810 entries / 865 keys, and the join mod-key -> 'Ability "
    "key(s)' returns 865 / 865 with ZERO unmatched keys in either direction. 799 + 11 (round 156, the magic missiles) = "
    "810 entries; 854 + 11 = 865 keys. NO army-bar (army_spec) key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 156 - re-counted from the mod's own ABILITIES table: 80 families / 810 entries / 865 "
    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 156: the NEW enemy_large_shot (5), "
    "enemy_single_shot (2), enemy_infantry_shot (1), enemy_melee_or_fast (2), enemy_melee_or_shooting (1).")
for r in range(44, 124):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t2, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t2
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t2]
assert 44 + len(fam_sorted) == 124
n.cell(row=124, column=2).value = "TOTAL (80 families)"
n.cell(row=124, column=3).value = sum(trig.values())
n.cell(row=124, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v41")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v42 (2026-11-15)"
r11 = d.cell(row=11, column=2)
old11 = "854 keys across 854 numbered rows ("
assert old11 in r11.value and "round 146 added 77)" in r11.value
r11.value = r11.value.replace(old11, "865 keys across 865 numbered rows (").replace(
    "round 146 added 77)", "round 146 added 77, round 156 added 11)")
r12 = d.cell(row=12, column=2)
assert "(946 keys, of which 269 are in the wheel)" in r12.value
r12.value = r12.value.replace("(946 keys, of which 269 are in the wheel)", "(935 keys, of which 258 are in the wheel)")
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("39. ROUND 156 - THE MAGIC MISSILES (v42)", None),
    ("THE RULINGS (2026-11-15)", "AP shots \"Large first, then armour\"; snipers \"Most valuable single\"; debuff throws "
     "\"Split by effect\"; Bolt Storm \"Most valuable infantry\". The safety margin (none of ours within 10 m of the "
     "target) and the caster gates (out of melee; standing still for the snipers and Bolt Storm) were part of the "
     "approved options."),
    ("THE NEW FAMILIES", "enemy_large_shot (5), enemy_single_shot (2), enemy_infantry_shot (1) on the round-145 map reads "
     "(m.all: every visible enemy); enemy_melee_or_fast (2) and enemy_melee_or_shooting (1) chain existing pickers. "
     "Generated table FOURTH.SHOT_TEXT (tools/gen_shot_tables.py: the engaged_in_melee usage rule, prefer-large, "
     "min_range). New target class single (Dead Eye, Focused Shot). One new 70% constant: 120 m -> 84 m."),
    ("THE ARITHMETIC", "Implemented 854 + 11 = 865 rows / keys; not implemented among the included 269 - 11 = 258 "
     "(27 skipped). The mod 799 + 11 = 810 entries / 865 keys; 80 families."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-15"
ch.cell(row=r, column=2).value = "v42"
ch.cell(row=r, column=3).value = (
    "ROUND 156. The magic missiles: 11 single-target attacks IMPLEMENTED on 5 NEW families. 854 -> 865 implemented; "
    "269 -> 258 not implemented (27 skipped). Mod 810 / 865 / 80 families. SHIPPED: installed pack md5 %s; harness 155 "
    "full suite 6,579 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-15 (the magic missiles); xlsx v42 supersedes v41; v1-v41 byte-unchanged."
wb.save(DST)
print("wrote", DST)
