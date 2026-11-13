#!/usr/bin/env python3
"""Build WH3_abilities_master_v36_2026-11-13.xlsx from v35 - round 144: open batch 3 (the rest of group C).

(1) 10 rows NOT IMPLEMENTED -> IMPLEMENTED: Hag's Denial (NEW self_last_stand), Ruinshelter and Banner of Hellfire
    (melee_unwavering), Rock Bottom (NEW self_out_of_ammo), Morikhane (under_fire), Hunter's Call
    (melee_or_wavering_aura), Icon of the King (NEW health_aura_self_undead), The Gold Standard (NEW ally_hurt_melee),
    Ghostly Howl (NEW enemy_wavering), Petrifying Gaze (enemy_fast_near_ally).
(2) 3 rows NOT IMPLEMENTED -> SKIPPED (user decision): Storm of Blades and Whirling Death (stances), Cloak of the Dunes
    (stealth).
(3) Implemented 767 -> 777 rows / keys; not implemented among the included 356 -> 346 (24 -> 27 skipped). The mod 722
    entries / 777 keys; 68 -> 73 families: the Numbers trigger table gains five rows (bombardment block 114 -> 119).
    Definitions: title v36, the two count rows, section 33. Changelog: a v36 row.
v1-v35 are never opened for writing.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v35_2026-11-13.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v36_2026-11-13.xlsx"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
RULE = "user ruling 2026-11-13 (open batch 3); "
GENERIC = ("shared gate: unit alive (>0 men); this (unit, ability) pair must be armed; readiness = "
           "can_perform_special_ability on the owned key; 2 s per-pair guard; engine cooldown refusal back-off; "
           "pre-fire unit-alive check; cast.")
LAST = ("self_last_stand: not routing; the unit's OWN health readable and at or below FOURTH.LAST_STAND_PCT = 10% (an "
        "unreadable health never fires) AND the unit in melee (is_in_melee() exactly true) OR under missile fire "
        "(is_under_missile_attack() exactly true); cast target: self; " + RULE + "\"10%, melee or fire\" (Cannot Die "
        "and damage resistance +40 for 44 s, one use); " + SHARED_TAIL)
MU = ("melee_unwavering: not routing; is_in_melee(); is_wavering() must NOT be true - false and unreadable both pass "
      "(fail-open morale); cast target: self; " + RULE + "\"in melee\"; " + SHARED_TAIL)
AMMO0 = ("self_out_of_ammo: not routing; the unit's OWN ammo_left() readable and 0 (no ammunition left); cast target: "
         "self; " + RULE + "\"wait until no ammo left\" (it refills 30% of its own ammunition for 350 damage to itself); "
         + SHARED_TAIL + " GATES: in-flight hold 3 s (1 s wind-up + 2 s).")
MORI = ("under_fire: not routing; the unit itself under missile fire (is_under_missile_attack() exactly true); cast "
        "target: self (no aura: the reflection covers the wearer); " + RULE + "\"under fire\"; " + SHARED_TAIL
        + " GATES: in-flight hold 3 s (1 s wind-up + 2 s).")
HUNT = ("melee_or_wavering_aura: not routing; the unit itself in melee or WAVERING, or a friendly unit (alive, not "
        "routing) within the aura bound in melee or wavering; bound: 24 m (70% of the ability's 35 m effect_range); "
        "cast target: self (the aura is centred on it); " + RULE + "like Stand Your Ground (melee defence +24 and "
        "Unbreakable); " + SHARED_TAIL + " GATES: charge hold 120 s (3 uses).")
ICON = ("health_aura_self_undead: not routing; the OWNER or a friendly unit within 24 m (70% of the ability's 35 m "
        "effect_range) at or below 75% health that is a NON-LIVING unit (its type in the GENERATED undead set, "
        "tools/gen_undead_keys.py; the game's invalid-target flag living_unit); the lowest health wins; cast target: "
        "self (the aura is centred on it); pre-cast re-check: still alive, still at or below 75%, still non-living; "
        + RULE + "\"heals only non-living allies\"; " + SHARED_TAIL + " GATES: charge hold 120 s (2 uses).")
GOLD = ("ally_hurt_melee: not routing; the OWNER or a friendly unit within 70 m (70% of the ability's 100 m "
        "target_intercept_range) at or below 75% health AND in melee (is_in_melee() exactly true); the lowest health "
        "wins; cast target: that unit; pre-cast re-check: still alive, still at or below 75%, still in melee, still in "
        "range; " + RULE + "\"the lowest-health ally IN MELEE\" (invulnerable for 13 s); " + SHARED_TAIL)
HOWL = ("enemy_wavering: not routing; enumerate the main enemy army; keep enemies alive (>0 men), validity not false, "
        "WAVERING (is_wavering() exactly true; the game only lets Ghostly Howl target an enemy below half morale, "
        "invalid-target flag morale_is_higher_than_half_of_base_morale) and within 52 m (70% of the ability's 75 m "
        "target_intercept_range; unit_distance only); the closest wins; cast target: that enemy unit; pre-cast "
        "re-check: still alive, still wavering, still within the bound; " + RULE + "\"the closest wavering enemy\"; "
        + SHARED_TAIL + " GATES: in-flight hold 5 s (3 s wind-up + 2 s).")
GAZE = ("enemy_fast_near_ally: not routing; the closest enemy within 35 m (70% of the ability's 50 m "
        "target_intercept_range) that is MOVING with a run speed (fast_speed()) of 5 m/s or more and is within 40 m of "
        "one of our units (the user's settings, round 135); cast target: that enemy; pre-cast re-check: still moving "
        "fast near our units; " + RULE + "the immobiliser ruling of round 136 (\"fast enemy\"); " + SHARED_TAIL
        + " GATES: charge hold 120 s (2 uses).")
NEW = {"wh3_dlc24_unit_abilities_hags_denial": ("self_last_stand", LAST),
       "wh2_dlc15_unit_abilities_mimic_ruinshelter": ("melee_unwavering", MU),
       "wh3_main_banner_abilities_banner_of_hellfire": ("melee_unwavering", MU),
       "wh2_dlc15_unit_abilities_rock_bottom": ("self_out_of_ammo", AMMO0),
       "wh3_dlc29_item_abilities_morikhane_the_black_armour": ("under_fire", MORI),
       "wh2_dlc13_character_ability_hunters_call": ("melee_or_wavering_aura", HUNT),
       "wh3_dlc29_item_abilities_icon_of_the_king": ("health_aura_self_undead", ICON),
       "wh3_dlc25_item_abilities_the_gold_standard": ("ally_hurt_melee", GOLD),
       "wh3_dlc29_hero_active_ghostly_howl": ("enemy_wavering", HOWL),
       "wh3_dlc24_unit_passive_petrifying_gaze": ("enemy_fast_near_ally", GAZE),
       }
STANCE = ("skipped (user decision 2026-11-13: a stance - no end time, 1 s recharge, on the same units as The Shadow's "
          "Coil and Woven Mist; round 131: stances are not automated until a stance chooser weighs the unit's mutually "
          "exclusive stances)")
SKIP = {"wh_dlc05_unit_abilities_storm_of_blades": STANCE,
        "wh2_dlc16_unit_abilities_whirling_death": STANCE,
        "wh2_dlc09_item_abilities_cloak_of_the_dunes": (
            "skipped (user decision 2026-11-13, applying the 2026-10-09 family ruling: stealth / escape effects "
            "(Stalk, Unspottable) get no automatic logic)")}

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
assert (n_new, n_skip) == (10, 3), (n_new, n_skip)

rows = [(r, keys_of(r), str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=20).value),
         str(ws.cell(row=r, column=21).value)) for r in range(2, ws.max_row + 1)]
N = len(rows)
impl = [x for x in rows if x[3] == "IMPLEMENTED"]
N_IMPL_ROWS = len(impl)
N_IMPL_KEYS = len(set(k for x in impl for k in x[1]))
assert (N, N_IMPL_ROWS, N_IMPL_KEYS) == (1800, 777, 777), (N, N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = 1123 - N_IMPL_ROWS
assert NOT_IMPL_IN == 346
assert sum(1 for x in rows if x[3] == "SKIPPED (user decision)") == 27
entries, _, _ = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
assert (len(entries), len(fam_by_key)) == (722, 777)
assert set(k for x in impl for k in x[1]) == set(fam_by_key)
assert not [x[1][0] for x in impl if x[4] != fam_by_key.get(x[1][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 73 and trig["melee_unwavering"] == 309 and trig["self_last_stand"] == 1 and trig["enemy_fast_near_ally"] == 8 and trig["under_fire"] == 4, (len(trig),)

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
assert n.cell(row=114, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert all(int(str(m).split(":")[0][1:]) < 108 for m in n.merged_cells.ranges)
n.insert_rows(112, 5)
assert n.cell(row=119, column=1).value == "Bombardment set (COMPLETE - round 108)"
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-11-13     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v36 - ROUND 144: open batch 3. Hag's Denial on the NEW self_last_stand; Ruinshelter and Banner of Hellfire on "
    "melee_unwavering; Rock Bottom on the NEW self_out_of_ammo; Morikhane on under_fire; Hunter's Call on "
    "melee_or_wavering_aura; Icon of the King on the NEW health_aura_self_undead; The Gold Standard on the NEW "
    "ally_hurt_melee; Ghostly Howl on the NEW enemy_wavering; Petrifying Gaze on enemy_fast_near_ally. Storm of Blades, "
    "Whirling Death and Cloak of the Dunes SKIPPED. Implemented 767 + 10 = 777 rows / 777 keys; not implemented among "
    "the included 356 - 10 = 346 (27 skipped). The mod: 722 entries / 777 keys / 73 trigger families.)")
for r, num, label, abs_, p1, p2 in [
        (13, 4, "Implemented among the included", N_IMPL_ROWS, N_IMPL_ROWS / tot, N_IMPL_ROWS / 1123.0),
        (14, 5, "Not implemented among the included", NOT_IMPL_IN, NOT_IMPL_IN / tot, NOT_IMPL_IN / 1123.0),
        (16, 7, "All implemented in the mod (4 + 6)", N_IMPL_KEYS, N_IMPL_KEYS / tot, N_IMPL_KEYS / 1123.0)]:
    for c, v in enumerate((num, label, abs_, p1, p2), 1):
        n.cell(row=r, column=c).value = v
n.cell(row=18, column=1).value = str(n.cell(row=18, column=1).value).replace("767 implemented", "777 implemented")
for i, f in enumerate(fam_order):
    r = 20 + i
    assert n.cell(row=r, column=2).value == f, (r, n.cell(row=r, column=2).value)
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=40, column=1).value = (
    "Reconciliation (v36): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 777 + not "
    "implemented 346 = 1,123. The mod's ABILITIES table is 722 entries / 777 keys, and the join mod-key -> 'Ability "
    "key(s)' returns 777 / 777 with ZERO unmatched keys in either direction. 712 + 10 (round 144, open batch 3) = 722 "
    "entries; 767 + 10 = 777 keys. NO army-bar (army_spec) key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 144 - re-counted from the mod's own ABILITIES table: 73 families / 722 entries / 777 "
    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 144: melee_unwavering 307 -> 309, "
    "under_fire 3 -> 4, melee_or_wavering_aura 1 -> 2, enemy_fast_near_ally 7 -> 8; the NEW self_last_stand, "
    "self_out_of_ammo, health_aura_self_undead, ally_hurt_melee and enemy_wavering (1 each).")
for r in range(44, 118):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t2, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t2
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t2]
assert 44 + len(fam_sorted) == 117
n.cell(row=117, column=2).value = "TOTAL (73 families)"
n.cell(row=117, column=3).value = sum(trig.values())
n.cell(row=117, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v35")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v36 (2026-11-13)"
r11 = d.cell(row=11, column=2)
old11 = ("767 keys across 767 numbered rows (rounds 122-123 added 21, round 130 added 2, round 131 removed the 9 "
         "stances, round 134 removed the 2 Thunderburner keys, round 142 added 6, round 143 added 11)")
assert old11 in r11.value
r11.value = r11.value.replace(old11, "777 keys across 777 numbered rows (rounds 122-123 added 21, round 130 added 2, "
                              "round 131 removed the 9 stances, round 134 removed the 2 Thunderburner keys, round 142 "
                              "added 6, round 143 added 11, round 144 added 10)")
r12 = d.cell(row=12, column=2)
assert "(1,033 keys, of which 356 are in the wheel)" in r12.value
r12.value = r12.value.replace("(1,033 keys, of which 356 are in the wheel)", "(1,023 keys, of which 346 are in the wheel)")
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("33. ROUND 144 - OPEN BATCH 3 (v36)", None),
    ("THE RULINGS (2026-11-13)", "Hag's Denial: \"10%, melee or fire\". Rock Bottom: \"wait until no ammo left\". "
     "Ruinshelter in melee; Morikhane under fire; Hunter's Call, Icon of the King, The Gold Standard, Banner of "
     "Hellfire, Ghostly Howl, Petrifying Gaze as proposed. Storm of Blades, Whirling Death (stances) and Cloak of the "
     "Dunes (stealth): skipped."),
    ("THE NEW FAMILIES", "self_last_stand (FOURTH.LAST_STAND_PCT = 10), self_out_of_ammo, health_aura_self_undead "
     "(the generated undead set; re-check mode undead), ally_hurt_melee (re-check mode melee), enemy_wavering "
     "(re-check mode wavering)."),
    ("THE ARITHMETIC", "Implemented 767 + 10 = 777 rows / keys; not implemented among the included 356 - 10 = 346 "
     "(24 + 3 = 27 skipped). The mod 712 + 10 = 722 entries / 777 keys; 73 families."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-13"
ch.cell(row=r, column=2).value = "v36"
ch.cell(row=r, column=3).value = (
    "ROUND 144. Open batch 3: Hag's Denial, Ruinshelter, Rock Bottom, Morikhane, Hunter's Call, Icon of the King, The "
    "Gold Standard, Banner of Hellfire, Ghostly Howl, Petrifying Gaze IMPLEMENTED (5 new families); Storm of Blades, "
    "Whirling Death, Cloak of the Dunes SKIPPED. 767 -> 777 implemented; 356 -> 346 not implemented (27 skipped). Mod "
    "722 / 777 / 73 families. SHIPPED: installed pack md5 %s; harness 143 full suite 6,273 checks / 0 failures."
    % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-13 (open batch 3); xlsx v36 supersedes v35; v1-v35 byte-unchanged."
wb.save(DST)
print("wrote", DST)
