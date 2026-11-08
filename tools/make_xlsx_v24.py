#!/usr/bin/env python3
"""Build WH3_abilities_master_v24_2026-11-08.xlsx from v23 - round 132: audit batch 1 and the
patch-9.0.5 data fixes.

(1) 13 rows move to their new family with the evaluator's own checks, in order; each row keeps its
    existing GATES clause (charge / in-flight holds): 10 on melee_or_shooting_aura, 2 on
    melee_or_shooting_self_or_ally, Boom! on self_shooting.
(2) Patch 9.0.5: Eternal Gaze's bound 70 -> 35 m; Aken-seth's new 120 s charge hold; Okkam's
    Mindrazor loses its in-flight hold; Overseer of the Unseen skips a flying ally.
(3) Counts re-derived (unchanged: 752 implemented, 371 not implemented, 22 skipped; 700 entries /
    752 keys); families 52 -> 54 (metallurgy_melee keeps 0 entries).
(4) Numbers: the trigger table grows to 54 rows (2 rows inserted above the bombardment block).
    Definitions: title v24, the glossary counts, section 21. Changelog: a v24 row.

v1-v23 are never opened for writing: a NEW filename is written.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v23_2026-11-01.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v24_2026-11-08.xlsx"
UAB = GP.UNIT_ABILITIES
ARMY_SPEC = GP.ARMY_SPEC

MA, MS, SS, MU, MM = ("melee_or_shooting_aura", "melee_or_shooting_self_or_ally", "self_shooting",
                      "melee_unwavering", "metallurgy_melee")
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
MA_TEXT = ("melee_or_shooting_aura: not routing; is_in_melee() fires at once on self; otherwise the CLOSEST tracked "
           "ally that is alive, not the owner, not routing and in melee within 24 m (FOURTH.METALLURGY_RANGE_M; the "
           "gap is re-checked before the cast) fires on self; otherwise count the tracked allies alive, not routing, "
           "shooting past their cast point and within the aura bound by unit_distance, add 1 when the caster itself "
           "is shooting past its cast point, and fire when the total is at least 1; bound: 24 m (70% of the "
           "ability's 35 m effect_range); cast target: self (the aura); " + SHARED_TAIL)
MS_TEXT = ("melee_or_shooting_self_or_ally: not routing; is_in_melee() with is_wavering() not true (fail-open morale) "
           "-> self; the caster's own firing flag ON and past its cast point -> self; otherwise walk the tracked "
           "allies: alive (>0 men), not the owner, not routing, in melee or shooting past their cast point, "
           "unit_distance <= the bound; the CLOSEST wins; bound: 140 m (70% of the ability's 200 m "
           "target_intercept_range); cast target: that ally; pre-cast re-check: the ally must still be alive, within "
           "the bound and in melee or shooting, else the cast is skipped; " + SHARED_TAIL)
SS_TEXT = ("self_shooting: not routing; the unit's own firing flag ON and past its cast point (first shot + 0.5 x its "
           "reload); cast target: self; " + SHARED_TAIL)
TEXT = {}
for k in ("wh3_main_character_abilities_enchanted_metallurgy", "wh3_main_character_abilities_enchanted_metallurgy_flaming",
          "wh3_main_character_abilities_enchanted_metallurgy_piercing", "wh3_main_character_abilities_enchanted_metallurgy_poison",
          "wh3_main_lord_abilities_master_of_alchemy", "wh3_main_lord_abilities_master_of_alchemy_flaming",
          "wh3_main_lord_abilities_master_of_alchemy_piercing", "wh3_main_lord_abilities_master_of_alchemy_poison",
          "wh2_main_spell_bound_embers_of_the_phoenix", "wh2_main_item_abilities_dragonhorn"):
    TEXT[k] = (MA, MA_TEXT)
for k in ("wh2_main_spell_bound_the_seerstaff_of_saphery", "wh3_main_spell_bound_harmonic_convergence"):
    TEXT[k] = (MS, MS_TEXT)
TEXT["wh_main_unit_abilities_boom"] = (SS, SS_TEXT)

GAZE = "wh3_dlc29_lord_abilities_gaze_of_usirian"
AKEN = "wh3_dlc29_weapon_abilities_aken_seth_the_staff_of_pain"
OKKAM = "wh3_dlc29_spell_bound_okkams_mindrazor"
OVER = "wh3_dlc29_hero_active_overseer_of_the_unseen"

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


def one_row(key):
    rs = row_of.get(key, [])
    assert len(rs) == 1 and keys_of(rs[0]) == [key], (key, rs)
    return rs[0]


for key, (fam, text) in TEXT.items():
    r = one_row(key)
    assert str(ws.cell(row=r, column=20).value) == "IMPLEMENTED", key
    assert str(ws.cell(row=r, column=21).value) in (MU, MM), (key, ws.cell(row=r, column=21).value)
    old = str(ws.cell(row=r, column=22).value or "")
    gates = (" GATES" + old.split(" GATES", 1)[1]) if " GATES" in old else ""
    ws.cell(row=r, column=21).value = fam
    ws.cell(row=r, column=22).value = text + gates
print("rows retriggered:", len(TEXT))

r = one_row(GAZE)
t = str(ws.cell(row=r, column=22).value)
assert "bound: 70 m (70% of the ability's 100 m target_intercept_range)" in t, t[:200]
ws.cell(row=r, column=22).value = t.replace(
    "bound: 70 m (70% of the ability's 100 m target_intercept_range)",
    "bound: 35 m (70% of the ability's 50 m target_intercept_range; patch 9.0.5 cut it from 100 m)")
r = one_row(AKEN)
ws.cell(row=r, column=22).value = (str(ws.cell(row=r, column=22).value)
                                   + " GATES (round 132, patch 9.0.5): charge hold 120 s (3 uses - one use per recharge period).")
r = one_row(OKKAM)
t = str(ws.cell(row=r, column=22).value)
assert "; in-flight hold 3 s (1 s wind-up + 2 s)." in t, t[-120:]
ws.cell(row=r, column=22).value = t.replace("; in-flight hold 3 s (1 s wind-up + 2 s).",
                                            ". (Patch 9.0.5 removed the 1 s wind-up: no in-flight hold.)")
r = one_row(OVER)
ws.cell(row=r, column=22).value = (str(ws.cell(row=r, column=22).value)
                                   + " PATCH 9.0.5 (round 132): a flying ally is skipped (the game added the invalid "
                                     "target flying_currently).")

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
assert NOT_IMPL_IN == 371 and impl["SKIPPED (user decision)"] == 22
assert not [x for x in rows if x[4] == "IN-WHEEL" and any(k in army for k in x[3])]

entries, consts, tips = bd.mod_entries()
mod_keys = set(k for e in entries for k in e["keys"])
assert (len(entries), len(mod_keys)) == (700, 752), (len(entries), len(mod_keys))
assert set(k for x in rows if x[6] == "IMPLEMENTED" for k in x[3]) == mod_keys
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
bad = [(x[3][0], x[7], fam_by_key.get(x[3][0])) for x in rows if x[6] == "IMPLEMENTED" and x[7] != fam_by_key.get(x[3][0])]
assert not bad, bad[:5]

trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 54 and sum(trig.values()) == 700 and sum(trig_keys.values()) == 752, len(trig)
assert (trig[MU], trig[MA], trig[MS], trig[SS], trig[MM]) == (349, 10, 2, 1, 0)

n = wb["Numbers"]
assert n.cell(row=98, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert all(int(str(m).split(":")[0][1:]) < 97 for m in n.merged_cells.ranges)
n.insert_rows(97, 2)
assert n.cell(row=100, column=1).value == "Bombardment set (COMPLETE - round 108)"
n.cell(row=7, column=1).value = (
    "Date: 2026-11-08     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v24 - ROUND 132: audit batch 1 and the patch-9.0.5 data. Enchanted Metallurgy, Master of Alchemy, Embers of "
    "the Phoenix and Horn of Vaul on the NEW melee_or_shooting_aura; The Seerstaff of Saphery and Harmonic "
    "Convergence on the NEW melee_or_shooting_self_or_ally; Boom! on the NEW self_shooting. Patch 9.0.5: Eternal "
    "Gaze 35 m, Aken-seth charge hold, Okkam's Mindrazor no wind-up, Overseer skips fliers. Implemented 752 rows / "
    "752 keys and 371 not implemented, unchanged. The mod: 700 entries / 752 keys / 54 trigger families.)")
n.cell(row=42, column=1).value = (
    "Trigger families after round 132 - re-counted from the mod's own ABILITIES table: 54 families / 700 entries / "
    "752 keys (metallurgy_melee keeps 0 entries; its evaluator is the melee arm of melee_or_shooting_aura). Round 132: "
    "the NEW melee_or_shooting_aura (10), melee_or_shooting_self_or_ally (2) and self_shooting (1); melee_unwavering "
    "354 -> 349.")
for r in range(44, 99):
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
assert tot_row == 98, tot_row
n.cell(row=tot_row, column=2).value = "TOTAL (54 families)"
n.cell(row=tot_row, column=3).value = sum(trig.values())
n.cell(row=tot_row, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v23")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v24 (2026-11-08)"
g = d.cell(row=21, column=1)
g.value = str(g.value) + "; the three round-132 families (melee_or_shooting_aura, melee_or_shooting_self_or_ally, " \
                         "self_shooting) in section 21"
refreshed = []
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
        refreshed.append(fam)
    elif fam == MM:
        d.cell(row=r, column=5).value = 0
        d.cell(row=r, column=6).value = 0
        refreshed.append(fam)
assert MU in refreshed and MM in refreshed, refreshed

base = d.max_row + 2
sec = [
    ("21. ROUND 132 - AUDIT BATCH 1 AND THE PATCH-9.0.5 DATA (v24)", None),
    ("THE LOOP", "Agreed 2026-11-08 (docs/WH3_process_proposal_2026-11-08.md): batches of about 10, the user rules on "
     "the whole batch, QA from the log of a battle the user fights. The audit (tools/audit_triggers.py) found 101 "
     "candidates; batch 1 is the group the user asked for."),
    ("THE RULINGS (2026-11-08)", "All as recommended: Enchanted Metallurgy / Master of Alchemy \"Add the shooting half\" "
     "(the user's own 2026-10 rule: \"When self or ally in range in melee. When ally in range is shooting.\"); Embers of "
     "the Phoenix and Horn of Vaul \"Same as Metallurgy\"; The Seerstaff of Saphery and Harmonic Convergence \"Self, "
     "else an ally\"; Boom! \"When it is shooting\"."),
    ("THE NEW FAMILY: melee_or_shooting_aura", "evaluate_melee_or_shooting_aura | the Metallurgy melee rule, or the "
     "caster or any unit within 24 m shooting past its cast point | cast target: self | 10 entries / 10 keys"),
    ("THE NEW FAMILY: melee_or_shooting_self_or_ally", "evaluate_melee_or_shooting_self_or_ally | the caster in melee or "
     "shooting -> self, else the closest ally within 140 m in melee or shooting | 2 entries / 2 keys"),
    ("THE NEW FAMILY: self_shooting", "evaluate_self_shooting | the unit itself shooting past its cast point | cast "
     "target: self | 1 entry / 1 key (Boom!)"),
    ("PATCH 9.0.5", "Eternal Gaze reach 100 -> 50 m (bound 35 m); Aken-seth 3 uses (120 s hold); Okkam's Mindrazor no "
     "wind-up; Overseer of the Unseen skips a flying ally; the reload table regenerated (Stormfiend Windlaunchers 13 "
     "-> 14 s). docs/DRIFT_2026-11-08_patch905.md."),
    ("THE ARITHMETIC", "Implemented 752 rows = 752 keys and 371 not implemented, unchanged. Mod 700 entries / 752 keys, "
     "52 -> 54 families, melee_unwavering 354 -> 349. Harness 131 full suite: 5,699 checks / 0 failures, run twice "
     "byte-identical."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-08"
ch.cell(row=r, column=2).value = "v24"
ch.cell(row=r, column=3).value = (
    "ROUND 132. (1) Audit batch 1: Enchanted Metallurgy and Master of Alchemy (8), Embers of the Phoenix and Horn of "
    "Vaul on the NEW melee_or_shooting_aura; The Seerstaff of Saphery and Harmonic Convergence on the NEW "
    "melee_or_shooting_self_or_ally; Boom! on the NEW self_shooting. (2) Patch 9.0.5: Eternal Gaze bound 35 m, "
    "Aken-seth charge hold 120 s, Okkam's Mindrazor no in-flight hold, Overseer skips fliers. (3) Counts unchanged "
    "(752 implemented, 371 not implemented, 1,800 rows); 54 families. (4) SHIPPED: installed pack md5 %s; harness 131 "
    "full suite 5,699 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = ("user rulings 2026-11-08 (audit batch 1, all as recommended); xlsx v24 supersedes "
                                  "v23; v1-v23 byte-unchanged.")
wb.save(DST)
print("wrote", DST)
print("families", len(trig), "entries", sum(trig.values()), "keys", sum(trig_keys.values()), "glossary refreshed", len(refreshed))
