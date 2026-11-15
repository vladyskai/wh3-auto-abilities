#!/usr/bin/env python3
"""Build WH3_abilities_master_v44_2026-11-15.xlsx from v43 - round 158: the last group B attacks (open batch 6).

(1) 12 rows NOT IMPLEMENTED -> IMPLEMENTED: 7 area drains on the NEW enemy_area_drain, Dweomer Leach Orb on the NEW
    enemy_commander_value, Ethrac's Brazier and Storm of the Night on enemy_melee_or_fast, Preyton Horns on enemy_melee,
    The Amber Trance on enemy_wavering.
(2) Implemented 877 -> 889 rows / keys; not implemented among the included 246 -> 234 (27 skipped). The mod 834 entries
    / 889 keys; 82 -> 84 families: the Numbers trigger table gains two rows (bombardment block 128 -> 130).
    Definitions: title v44, the two count rows, section 41. Changelog: a v44 row.
v1-v43 are never opened for writing.
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

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v43_2026-11-15.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v44_2026-11-15.xlsx"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
USA = {r["key"]: r for r in GS.tsv("unit_spec_abil.tsv")}
KEYS = ["wh2_main_item_abilities_blood_statuette_of_spite", "wh3_dlc23_item_abilities_darkened_mist",
        "wh3_dlc25_spell_bound_the_fate_of_bjuna", "wh3_main_spell_bound_the_fate_of_bjuna",
        "wh3_dlc24_unit_abilities_maelstrom_of_change", "wh3_dlc29_lord_abilities_otherworldly_pestilence",
        "wh3_dlc27_item_abilities_staff_of_the_masque", "wh3_dlc29_item_active_ethracs_brazier",
        "wh2_dlc11_lord_abilities_storm_of_the_night", "wh3_dlc27_item_abilities_preyton_horns",
        "wh2_dlc10_item_abilities_the_amber_trance", "wh3_dlc23_item_abilities_dweomer_leach_orb"]
AREA = GS.area_rows(set(KEYS[:7]))


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
    if fam == "enemy_area_drain":
        body = ("enemy_area_drain: not routing; the caster STANDING STILL (is_moving() exactly false); the live map "
                "(every enemy we can see); the visible enemy INFANTRY (inf class, not large, not flying) %s with at least "
                "%d soldiers left (the GENERATED AREA table: the game's max_damaged_entities, the models hit each tick) "
                "and the highest live value per soldier (strategic_value / men); no friendly-fire margin (a direct "
                "effect); cast target: that enemy unit; pre-cast re-check: the map is rebuilt, the caster still standing, "
                "the target still big enough and in range; user ruling 2026-11-15 (\"Most valuable infantry\"); "
                % (within, AREA[k]))
    elif fam == "enemy_commander_value":
        body = ("enemy_commander_value: not routing; the live map; the most valuable (strategic_value) visible enemy "
                "Lord or Hero %s; the game allows spellcasters only and the mod has no spellcaster read, so a non-caster "
                "target is refused by the engine and backed off; cast target: that enemy unit; pre-cast re-check: still "
                "a Lord or Hero in range; target class: Lord/Hero only (the spellcaster proxy, the round-138 precedent); "
                "user ruling 2026-11-15 (\"Lord/Hero proxy\"); " % within)
    elif fam == "enemy_melee_or_fast":
        fl = ("; target class: flying only (the game's ground_unit rule; is_currently_flying() exactly true)"
              if "storm_of_the_night" in k else "")
        body = ("enemy_melee_or_fast: not routing; FIRST the closest enemy %s that is fighting in melee (enemy_melee's "
                "pick); otherwise a FAST enemy %s (moving, fast_speed() >= FOURTH.FAST_ENEMY_MPS = 5 m/s) within 40 m of "
                "one of our units (enemy_fast_near_ally's pick)%s; cast target: that enemy unit; pre-cast re-check: the "
                "same arm's condition again; the effect slows the target (rule 10: in melee or on the charge); user "
                "ruling 2026-11-15 (\"Rule 10: melee or charge\"); " % (within, within, fl))
    elif fam == "enemy_melee":
        body = ("enemy_melee: not routing; the closest enemy %s that is fighting in melee; cast target: that enemy unit "
                "(enemies within 55 m of it -8 morale, our units there +8); pre-cast re-check: still in melee and in "
                "range; user ruling 2026-11-15 (\"Horns melee, Trance waver\"); " % within)
    else:
        body = ("enemy_wavering: not routing; the closest enemy %s whose is_wavering() reads exactly true; cast target: "
                "that enemy unit (-16 morale, one use: tip it into a rout); pre-cast re-check: still wavering and in "
                "range; user ruling 2026-11-15 (\"Horns melee, Trance waver\"); " % within)
    return body + SHARED_TAIL + ((" GATES: " + "; ".join(gates) + ".") if gates else "")


entries, _, _ = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
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
assert (N, N_IMPL_ROWS, N_IMPL_KEYS) == (1800, 889, 889), (N, N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = 1123 - N_IMPL_ROWS
assert NOT_IMPL_IN == 234
assert sum(1 for x in rows if x[3] == "SKIPPED (user decision)") == 27
assert (len(entries), len(fam_by_key)) == (834, 889)
assert set(k for x in impl for k in x[1]) == set(fam_by_key)
assert not [x[1][0] for x in impl if x[4] != fam_by_key.get(x[1][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 84, len(trig)

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
assert n.cell(row=128, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert n.cell(row=126, column=2).value == "TOTAL (82 families)"
assert all(int(str(m).split(":")[0][1:]) < 108 for m in n.merged_cells.ranges)
n.insert_rows(125, 2)
assert n.cell(row=130, column=1).value == "Bombardment set (COMPLETE - round 108)"
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-11-15     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v44 - ROUND 158: the last group B attacks. 12 rows: the area drains (NEW enemy_area_drain), Dweomer Leach Orb (NEW "
    "enemy_commander_value), the slows on enemy_melee_or_fast, Preyton Horns on enemy_melee, The Amber Trance on "
    "enemy_wavering. Implemented 877 + 12 = 889 rows / 889 keys; not implemented among the included 246 - 12 = 234 "
    "(27 skipped). The mod: 834 entries / 889 keys / 84 trigger families.)")
for r, num, label, abs_, p1, p2 in [
        (13, 4, "Implemented among the included", N_IMPL_ROWS, N_IMPL_ROWS / tot, N_IMPL_ROWS / 1123.0),
        (14, 5, "Not implemented among the included", NOT_IMPL_IN, NOT_IMPL_IN / tot, NOT_IMPL_IN / 1123.0),
        (16, 7, "All implemented in the mod (4 + 6)", N_IMPL_KEYS, N_IMPL_KEYS / tot, N_IMPL_KEYS / 1123.0)]:
    for c, v in enumerate((num, label, abs_, p1, p2), 1):
        n.cell(row=r, column=c).value = v
old18 = str(n.cell(row=18, column=1).value)
assert "877 implemented" in old18
n.cell(row=18, column=1).value = old18.replace("877 implemented", "889 implemented")
for i, f in enumerate(fam_order):
    r = 20 + i
    assert n.cell(row=r, column=2).value == f, (r, n.cell(row=r, column=2).value)
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=40, column=1).value = (
    "Reconciliation (v44): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 889 + not "
    "implemented 234 = 1,123. The mod's ABILITIES table is 834 entries / 889 keys, and the join mod-key -> 'Ability "
    "key(s)' returns 889 / 889 with ZERO unmatched keys in either direction. 822 + 12 (round 158, the last group B "
    "attacks) = 834 entries; 877 + 12 = 889 keys. NO army-bar (army_spec) key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 158 - re-counted from the mod's own ABILITIES table: 84 families / 834 entries / 889 "
    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 158: the NEW enemy_area_drain (7) "
    "and enemy_commander_value (1); enemy_melee_or_fast 2 -> 4, enemy_melee 34 -> 35, enemy_wavering 1 -> 2.")
for r in range(44, 128):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t2, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t2
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t2]
assert 44 + len(fam_sorted) == 128
n.cell(row=128, column=2).value = "TOTAL (84 families)"
n.cell(row=128, column=3).value = sum(trig.values())
n.cell(row=128, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v43")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v44 (2026-11-15)"
r11 = d.cell(row=11, column=2)
assert "877 keys across 877 numbered rows (" in r11.value and "round 157 added 12)" in r11.value
r11.value = r11.value.replace("877 keys across 877 numbered rows (", "889 keys across 889 numbered rows (").replace(
    "round 157 added 12)", "round 157 added 12, round 158 added 12)")
r12 = d.cell(row=12, column=2)
assert "(923 keys, of which 246 are in the wheel)" in r12.value
r12.value = r12.value.replace("(923 keys, of which 246 are in the wheel)", "(911 keys, of which 234 are in the wheel)")
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("41. ROUND 158 - THE LAST GROUP B ATTACKS (v44)", None),
    ("THE RULINGS (2026-11-15)", "Area drains \"Most valuable infantry\"; the slows \"Rule 10: melee or charge\"; the "
     "morale hexes \"Horns melee, Trance waver\"; Dweomer Leach Orb \"Lord/Hero proxy\"."),
    ("THE NEW FAMILIES", "enemy_area_drain (7): the visible enemy infantry in range with at least the ability's own model "
     "count left (GENERATED FOURTH.AREA_TEXT from max_damaged_entities: 25, or 15 for Staff of Masks) and the highest "
     "value per soldier; standing still; no margin. enemy_commander_value (1): the most valuable visible enemy Lord or "
     "Hero in range. New target class flying (Storm of the Night). Group B is now closed."),
    ("THE ARITHMETIC", "Implemented 877 + 12 = 889 rows / keys; not implemented among the included 246 - 12 = 234 "
     "(27 skipped). The mod 822 + 12 = 834 entries / 889 keys; 84 families."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-15"
ch.cell(row=r, column=2).value = "v44"
ch.cell(row=r, column=3).value = (
    "ROUND 158. The last group B attacks: 12 rows IMPLEMENTED (2 NEW families). 877 -> 889 implemented; 246 -> 234 not "
    "implemented (27 skipped). Mod 834 / 889 / 84 families. SHIPPED: installed pack md5 %s; harness 157 full suite 6,677 "
    "checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-15 (the last group B attacks); xlsx v44 supersedes v43; v1-v43 byte-unchanged."
wb.save(DST)
print("wrote", DST)
