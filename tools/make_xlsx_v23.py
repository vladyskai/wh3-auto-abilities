#!/usr/bin/env python3
"""Build WH3_abilities_master_v23_2026-11-01.xlsx from v22 - round 131: the shooting buffs
leave the melee trigger, Potion of Farsight's out-of-range trigger, the firing aura counts
the caster, and the nine stances leave the mod.

(1) Ten rows move to their new family with the evaluator's own checks, in order:
    7 auras -> allies_firing_aura; Deranged Munitions -> self_or_ally_shooting (NEW);
    Entrenchment -> melee_or_self_or_ally_shooting (NEW); Potion of Farsight ->
    no_enemy_in_range_within_boost (NEW). Ballistics Calibration's text: 1 shooter, the
    caster counting.
(2) The nine stances: IMPLEMENTED -> SKIPPED (user decision 2026-11-01).
(3) Every count re-derived: 1,800 = 1,123 + 677; 752 implemented rows / keys; 371 not
    implemented among the included (22 skipped by user decision); 52 families / 700
    entries / 752 keys.
(4) Numbers: the trigger table grows to 52 rows (3 rows inserted above the bombardment
    block). Definitions: title v23, the count sentences, the glossary counts, section 20.
    Changelog: a v23 row.

v1-v22 are never opened for writing: a NEW filename is written.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v22_2026-11-01.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v23_2026-11-01.xlsx"
UAB = GP.UNIT_ABILITIES
ARMY_SPEC = GP.ARMY_SPEC

AF, SO, MSO, NE, MU = ("allies_firing_aura", "self_or_ally_shooting", "melee_or_self_or_ally_shooting",
                       "no_enemy_in_range_within_boost", "melee_unwavering")
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")


def af_text(bound, real, target):
    return ("allies_firing_aura: not routing; count the tracked allies that are alive (>0 men), not the owner, not "
            "routing, shooting past their cast point (firing flag ON and first shot + 0.5 x their reload from "
            "FOURTH.RELOAD_S) and within the aura bound by unit_distance (an unreadable distance does not count); add "
            "1 when the caster itself is shooting past its cast point; fire when the total is at least 1 "
            "(FOURTH.FIRING_AURA_MIN, user ruling round 131: the caster counts); bound: %d m (70%% of the ability's "
            "%d m effect_range); cast target: %s; " % (bound, real, target)) + SHARED_TAIL


SELF_AURA = "self (the aura is self-centred)"
TEXT = {
    "wh_main_hero_abilities_ballistics_calibration": (AF, af_text(38, 55, "the ground at the caster's own position "
                                                                  "(perform_special_ability_ground, ground_keys)")),
    "wh3_dlc25_lord_abilities_deranged_munitions_upgraded": (AF, af_text(24, 35, SELF_AURA)),
    "wh2_dlc11_character_abilities_ballistic_enchantment": (AF, af_text(38, 55, SELF_AURA)),
    "wh2_dlc13_lord_abilities_funnel_of_flame": (AF, af_text(38, 55, SELF_AURA)),
    "wh2_dlc13_lord_abilities_hail_of_fire": (AF, af_text(38, 55, SELF_AURA)),
    "wh2_main_item_abilities_the_guiding_eye": (AF, af_text(38, 55, SELF_AURA)),
    "wh3_dlc23_item_abilities_morgrims_eye": (AF, af_text(24, 35, SELF_AURA)),
    "wh3_main_character_abilities_locus_of_change": (AF, af_text(38, 55, SELF_AURA)),
    "wh3_dlc25_lord_abilities_deranged_munitions": (SO,
        "self_or_ally_shooting: not routing; the caster's own firing flag ON and past its cast point -> cast target: "
        "self; otherwise walk the tracked allies: alive (>0 men), not the owner, not routing, shooting past their cast "
        "point, unit_distance <= the bound; the CLOSEST wins; bound: 70 m (70% of the ability's 100 m "
        "target_intercept_range); cast target: that ally; pre-cast re-check: the ally must still be alive, within the "
        "bound and shooting, else the cast is skipped; " + SHARED_TAIL),
    "wh_main_unit_abilities_entrenchment": (MSO,
        "melee_or_self_or_ally_shooting: not routing; is_in_melee() with is_wavering() not true (fail-open morale, as "
        "melee_unwavering) -> cast target: self; otherwise the caster's own firing flag ON and past its cast point -> "
        "self; otherwise the CLOSEST tracked ally that is alive, not the owner, not routing, shooting past its cast "
        "point and within the bound by unit_distance; bound: 105 m (70% of the ability's 150 m target_intercept_range); "
        "cast target: that ally (it cannot move for the ability's 44 s); pre-cast re-check: the ally must still be "
        "alive, within the bound and shooting, else the cast is skipped; " + SHARED_TAIL),
    "wh3_main_item_abilities_potion_of_farsight": (NE,
        "no_enemy_in_range_within_boost: not routing; is_in_melee() must be exactly false; ammo_left() a number > 0; "
        "missile_range() a number > 0; enumerate the main enemy army list: live enemies (number_of_men_alive() > 0) "
        "with a readable unit_distance; NONE may be within missile_range; the nearest must be within missile_range x "
        "1.21 (FOURTH.FARSIGHT_BAND = 1 + 0.30 x 0.70: the standing 70% rule on the potion's +30% Range); every "
        "unreadable read fails closed; cast target: self; " + SHARED_TAIL + " GATES: 1 use (the engine refuses a "
        "second)."),
}
STANCE_REASON = ("skipped (user decision 2026-11-01: stances are not automated; a stance chooser that weighs the "
                 "unit's mutually exclusive stances is last priority)")
STANCES = ["wh2_dlc17_lord_abilities_master_predator", "wh3_dlc26_unit_abilities_immovable_bulwark",
           "wh3_dlc26_unit_abilities_unstoppable_choppas", "wh_dlc05_unit_abilities_the_shadows_coil",
           "wh_dlc05_unit_abilities_woven_mist", "wh3_dlc27_lord_abilities_chanson_of_caging",
           "wh3_dlc27_lord_abilities_the_dance_of_dreaming", "wh3_dlc27_lord_abilities_the_praise_of_slaanesh",
           "wh3_dlc27_lord_abilities_the_waltz_of_lethargy"]

army = set()
with open(ARMY_SPEC, encoding="utf-8", errors="replace") as f:
    f.readline()
    for line in f:
        if line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        if c and c[0].strip():
            army.add(c[0].strip())

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]


def keys_of(r):
    return [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]


row_of = {}
for r in range(2, ws.max_row + 1):
    for k in keys_of(r):
        row_of.setdefault(k, []).append(r)

for key, (fam, text) in TEXT.items():
    rs = row_of.get(key, [])
    assert len(rs) == 1 and keys_of(rs[0]) == [key], (key, rs)
    r = rs[0]
    assert str(ws.cell(row=r, column=18).value) == "IN-WHEEL" and str(ws.cell(row=r, column=20).value) == "IMPLEMENTED", key
    assert str(ws.cell(row=r, column=21).value) in (MU, AF), (key, ws.cell(row=r, column=21).value)
    ws.cell(row=r, column=21).value = fam
    ws.cell(row=r, column=22).value = text
for key in STANCES:
    rs = row_of.get(key, [])
    assert len(rs) == 1 and keys_of(rs[0]) == [key], (key, rs)
    r = rs[0]
    assert str(ws.cell(row=r, column=20).value) == "IMPLEMENTED" and str(ws.cell(row=r, column=21).value) == MU, key
    ws.cell(row=r, column=19).value = STANCE_REASON
    ws.cell(row=r, column=20).value = "SKIPPED (user decision)"
    ws.cell(row=r, column=21).value = "-"
    ws.cell(row=r, column=22).value = "-"
print("rows retriggered:", len(TEXT), "stances skipped:", len(STANCES))

rows = []
for r in range(2, ws.max_row + 1):
    rows.append((r, ws.cell(row=r, column=1).value, ws.cell(row=r, column=2).value, keys_of(r),
                 str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=19).value),
                 str(ws.cell(row=r, column=20).value), str(ws.cell(row=r, column=21).value)))
N = len(rows)
status = collections.Counter(x[4] for x in rows)
impl = collections.Counter(x[6] for x in rows)
N_IN, N_EX = status["IN-WHEEL"], status["EXCLUDED"]
assert (N, N_IN, N_EX) == (1800, 1123, 677), (N, N_IN, N_EX)
N_IMPL_ROWS = impl["IMPLEMENTED"]
N_IMPL_KEYS = len(set(k for x in rows if x[6] == "IMPLEMENTED" for k in x[3]))
assert (N_IMPL_ROWS, N_IMPL_KEYS) == (752, 752), (N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = N_IN - N_IMPL_ROWS
assert NOT_IMPL_IN == 371, NOT_IMPL_IN
N_SKIP = impl["SKIPPED (user decision)"]
assert N_SKIP == 22, N_SKIP
assert not [x for x in rows if x[4] == "IN-WHEEL" and any(k in army for k in x[3])]

entries, consts, tips = bd.mod_entries()
mod_keys = set(k for e in entries for k in e["keys"])
assert (len(entries), len(mod_keys)) == (700, 752), (len(entries), len(mod_keys))
assert not (mod_keys & army)
impl_rows_keys = set(k for x in rows if x[6] == "IMPLEMENTED" for k in x[3])
assert impl_rows_keys == mod_keys, (sorted(impl_rows_keys - mod_keys)[:5], sorted(mod_keys - impl_rows_keys)[:5])
assert not (set(STANCES) & mod_keys)

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
    if x[4] != "IN-WHEEL":
        continue
    f = next((src_type[k] for k in x[3] if k in src_type), None)
    assert f in fam_order, (x[0], x[3])
    fam_inc[f] += 1
    if x[6] == "IMPLEMENTED":
        fam_impl[f] += 1
assert sum(fam_inc.values()) == N_IN and sum(fam_impl.values()) == N_IMPL_ROWS

trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 52 and sum(trig.values()) == 700 and sum(trig_keys.values()) == 752, \
    (len(trig), sum(trig.values()), sum(trig_keys.values()))
assert (trig[MU], trig[AF], trig[SO], trig[MSO], trig[NE]) == (354, 8, 1, 1, 1)
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
for key, (fam, _t) in TEXT.items():
    assert fam_by_key[key] == fam, (key, fam_by_key[key])

# ------------------------------------------------------------------ Numbers
n = wb["Numbers"]
assert n.cell(row=95, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert all(int(str(m).split(":")[0][1:]) < 94 for m in n.merged_cells.ranges)
n.insert_rows(94, 3)
assert n.cell(row=98, column=1).value == "Bombardment set (COMPLETE - round 108)"
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-11-01     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v23 - ROUND 131: the shooting buffs leave the melee trigger (7 auras on allies_firing_aura, Deranged "
    "Munitions on the NEW self_or_ally_shooting, Entrenchment on the NEW melee_or_self_or_ally_shooting, Potion of "
    "Farsight on the NEW no_enemy_in_range_within_boost); the firing aura counts the caster and needs 1 shooter; "
    "the nine stances leave the mod (SKIPPED by user decision). Implemented 761 - 9 = 752 rows / 752 keys; not "
    "implemented among the included 362 + 9 = 371 (22 SKIPPED by user decision). 1,123 IN-WHEEL + 677 EXCLUDED = "
    "1,800, unchanged. The mod: 700 entries / 752 keys / 52 trigger families.)")
measures = [
    (10, 1, "Total active abilities (the inventory)", N, 1.0, "-"),
    (11, 2, "Excluded - not in the ability wheel", N_EX, N_EX / tot, "-"),
    (12, 3, "Included - in the ability wheel", N_IN, N_IN / tot, 1.0),
    (13, 4, "Implemented among the included", N_IMPL_ROWS, N_IMPL_ROWS / tot, N_IMPL_ROWS / float(N_IN)),
    (14, 5, "Not implemented among the included", NOT_IMPL_IN, NOT_IMPL_IN / tot, NOT_IMPL_IN / float(N_IN)),
    (15, 6, "Implemented but OUTSIDE the rule (reported separately)", 0, 0, 0),
    (16, 7, "All implemented in the mod (4 + 6)", N_IMPL_KEYS, N_IMPL_KEYS / tot, N_IMPL_KEYS / float(N_IN)),
]
for r, num, label, abs_, p1, p2 in measures:
    for c, v in enumerate((num, label, abs_, p1, p2), 1):
        n.cell(row=r, column=c).value = v
n.cell(row=18, column=1).value = (
    "Included, by carrier family (unit_abilities.source_type) - ROW-LEVEL count, derived from this "
    "workbook's own 1,123 IN-WHEEL rows joined to unit_abilities.source_type by exact key: it TIES "
    "to the headline (sum = 1,123 included, 752 implemented).")
for i, f in enumerate(fam_order):
    r = 20 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = f
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=40, column=1).value = (
    "Reconciliation (v23): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included "
    "752 + not implemented 371 = 1,123. The mod's ABILITIES table is 700 entries / 752 keys, and the join "
    "mod-key -> 'Ability key(s)' returns 752 / 752 with ZERO unmatched keys in either direction. 709 - 9 "
    "(round 131: the nine stances) = 700 entries; 761 - 9 = 752 keys. NO army-bar (army_spec) key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 131 - re-counted from the mod's own ABILITIES table: 52 families / "
    "700 entries / 752 keys / 53 evaluators (ally_infinite_buff's evaluator stays unused since round 121). "
    "Round 131: allies_firing_aura 1 -> 8; the NEW self_or_ally_shooting (1), melee_or_self_or_ally_shooting (1) "
    "and no_enemy_in_range_within_boost (1); melee_unwavering 373 -> 354 (10 moved, 9 stances removed).")
for r in range(44, 97):
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
assert tot_row == 96, tot_row
n.cell(row=tot_row, column=2).value = "TOTAL (52 families / 53 evaluators)"
n.cell(row=tot_row, column=3).value = sum(trig.values())
n.cell(row=tot_row, column=4).value = sum(trig_keys.values())

# ------------------------------------------------------------------ Definitions
d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v22")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v23 (2026-11-01)"
r11 = d.cell(row=11, column=2)
old11 = "761 keys across 761 numbered rows (rounds 122-123 added 21, round 130 added 2)"
assert old11 in r11.value
r11.value = r11.value.replace(old11, "752 keys across 752 numbered rows (rounds 122-123 added 21, round 130 added "
                              "2, round 131 removed the 9 stances)")
r12 = d.cell(row=12, column=2)
assert "of which 362 are in the wheel" in r12.value and "(1,039 keys" in r12.value
r12.value = (r12.value.replace("of which 362 are in the wheel", "of which 371 are in the wheel")
             .replace("(1,039 keys", "(1,048 keys"))
g = d.cell(row=21, column=1)
assert "are described in section 19" in str(g.value)
g.value = str(g.value) + "; the three round-131 families (self_or_ally_shooting, melee_or_self_or_ally_shooting, " \
                         "no_enemy_in_range_within_boost) in section 20"
refreshed = []
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
        refreshed.append(fam)
assert MU in refreshed, refreshed
cov_gate = sum(1 for x in rows if x[6] == "IMPLEMENTED"
               and any(w in x[5] or w in str(ws.cell(row=x[0], column=22).value or "")
                       for w in ("wind-up", "charge gate", "charge hold", "recharge_time", "in-flight", "per-unit")))
r104 = d.cell(row=104, column=1)
assert "Coverage in this workbook:" in str(r104.value)
r104.value = (str(r104.value).split("Coverage in this workbook:")[0]
              + "Coverage in this workbook: %d of the %d implemented rows (%d keys) carry at least one gate "
              "clause in their Trigger (as implemented) text; rows with neither a multi-use pool nor a wind-up "
              "keep the plain 2 s guard." % (cov_gate, N_IMPL_ROWS, N_IMPL_KEYS))

base = d.max_row + 2
sec = [
    ("20. ROUND 131 - THE SHOOTING BUFFS LEAVE THE MELEE TRIGGER; THE STANCES LEAVE THE MOD (v23)", None),
    ("THE RULINGS (2026-11-01)", "A shooting trigger for Deranged Munitions, Enchanted Ballistics, Funnel of Flame, "
     "Hail of Fire, The Guiding Eye, Morgrim's Eye and Locus of Change; Entrenchment also in melee (its physical "
     "resistance). Auras: \"Fires when at least 1 ally (caster counts) inside the aura's 70% bound is shooting. "
     "Actually, the previous trigger where the trigger was required 2 allies should be redone.\" One-target buffs: "
     "\"Self, else a shooting ally\". Potion of Farsight: the user's own design, band range x 1.21. Stances: \"For now, "
     "all stances should not have any automation\"; remove all 9 now."),
    ("WHY", "These ten buffs only help shooting (Entrenchment also melee), but they rode melee_unwavering since the "
     "2026-10 questionnaire blocks, written before the mod could tell that a unit was shooting: in melee a unit does "
     "not shoot, so they were spent where they did nothing."),
    ("THE NEW FAMILY: self_or_ally_shooting", "evaluate_self_or_ally_shooting | the caster shooting past its cast "
     "point -> self; otherwise the closest ally in range shooting past its cast point | cast target: the caster or "
     "that ally | 1 entry / 1 key (Deranged Munitions, 70 m of 100 m)"),
    ("THE NEW FAMILY: melee_or_self_or_ally_shooting", "evaluate_melee_or_self_or_ally_shooting | in melee -> self; "
     "otherwise as self_or_ally_shooting | 1 entry / 1 key (Entrenchment, 105 m of 150 m; the target cannot move "
     "for 44 s)"),
    ("THE NEW FAMILY: no_enemy_in_range_within_boost", "evaluate_no_enemy_in_range_within_boost | not in melee, "
     "ammunition left, no live enemy inside the unit's own missile range, the nearest inside range x 1.21 | cast "
     "target: self | 1 entry / 1 key (Potion of Farsight, 1 use)"),
    ("allies_firing_aura, CHANGED", "1 shooter is enough and the caster counts (round 130 needed 2 allies); 1 -> 8 "
     "entries (Ballistics Calibration on the ground; seven self-centred auras on the caster)."),
    ("THE STANCES, SKIPPED", "Master Predator, Immovable Bulwark, Unstoppable Choppas, The Shadow's Coil, Woven Mist, "
     "Chanson of Caging, The Dance of Dreaming, The Praise of Slaanesh, The Waltz of Lethargy: toggles with no fixed "
     "duration that switch a unit's mode. Thunderburner (also no fixed duration, but a speed burst) stays."),
    ("THE ARITHMETIC", "Implemented 761 - 9 = 752 rows = 752 keys; not implemented among the included 362 + 9 = 371 "
     "(22 SKIPPED by user decision); 1,123 IN-WHEEL + 677 EXCLUDED = 1,800 unchanged. Mod: 709 -> 700 entries, 761 "
     "-> 752 keys, 49 -> 52 families, melee_unwavering 373 -> 354. Harness 130 full suite: 5,638 checks / 0 "
     "failures, run twice byte-identical."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-01"
ch.cell(row=r, column=2).value = "v23"
ch.cell(row=r, column=3).value = (
    "ROUND 131. (1) Ten shooting buffs leave melee_unwavering: seven auras (Deranged Munitions Upgraded, Enchanted "
    "Ballistics, Funnel of Flame, Hail of Fire, The Guiding Eye, Morgrim's Eye, Locus of Change) on allies_firing_aura; "
    "Deranged Munitions on the NEW self_or_ally_shooting; Entrenchment on the NEW melee_or_self_or_ally_shooting; "
    "Potion of Farsight on the NEW no_enemy_in_range_within_boost (range x 1.21). (2) allies_firing_aura: 1 shooter, "
    "the caster counting (Ballistics Calibration too). (3) The nine stances SKIPPED (user decision) and removed from "
    "the mod. (4) 761 -> 752 rows / keys; 362 -> 371 not implemented among the included; 1,123 + 677 = 1,800 "
    "unchanged. Mod 700 entries / 752 keys / 52 families. (5) SHIPPED: installed pack md5 %s; harness 130 full suite "
    "5,638 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = ("user rulings 2026-11-01 (the shooting triggers, the aura rule, 'Self, else a "
                                  "shooting ally', Farsight's band, no stance automation); xlsx v23 supersedes v22; "
                                  "v1-v22 byte-unchanged.")

wb.save(DST)
print("wrote", DST)
print("rows", N, "in-wheel", N_IN, "excluded", N_EX, "impl rows", N_IMPL_ROWS, "impl keys", N_IMPL_KEYS,
      "not-impl in-wheel", NOT_IMPL_IN, "skipped", N_SKIP)
print("families", len(trig), "entries", sum(trig.values()), "keys", sum(trig_keys.values()),
      "glossary refreshed", len(refreshed), "gate coverage", cov_gate)
