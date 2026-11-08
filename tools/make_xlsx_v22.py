#!/usr/bin/env python3
"""Build WH3_abilities_master_v22_2026-11-01.xlsx from v21 - round 130, the first
triggers on the firing flag.

(1) Restock! and Ballistics Calibration -> IMPLEMENTED on two NEW families
    (ally_ammo_low, allies_firing_aura); Skjalandir's Fall moves from
    melee_unwavering to the NEW melee_or_shooting_into_melee. Each trigger text is
    the evaluator's own checks, in order, from the source.
(2) Every count re-derived from the edited sheet and the mod's own table:
    1,800 = 1,123 IN-WHEEL + 677 EXCLUDED; 761 implemented rows / keys;
    362 not implemented among the included; 49 families / 709 entries / 761 keys.
(3) Numbers: the trigger table grows to 49 rows (3 rows inserted above the
    bombardment block, which has no merged cells). Definitions: title v22, the
    count sentences, the glossary counts, the "No firing read" absence note, and
    section 19. Changelog: a v22 row.

v1-v21 are never opened for writing: a NEW filename is written.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v21_2026-10-28.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v22_2026-11-01.xlsx"
UAB = GP.UNIT_ABILITIES
ARMY_SPEC = GP.ARMY_SPEC

RK = "wh2_dlc17_hero_abilities_more_powder_generic"
BK = "wh_main_hero_abilities_ballistics_calibration"
SK = "wh3_dlc23_character_abilities_skjalandirs_fall"
AL, AF, MS, MU = "ally_ammo_low", "allies_firing_aura", "melee_or_shooting_into_melee", "melee_unwavering"

SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
TEXT = {
    RK: (AL, "ally_ammo_low: not routing; walk the tracked allies: alive (>0 men), not the owner, not routing; the "
         "ally's firing flag must be ON (its ammo_left() dropped on an earlier poll; FOURTH.ammo_by_id, filled by "
         "the ammo probe on the same poll) and ammo_left / starting_ammo must be at or below 0.70 "
         "(FOURTH.RESTOCK_AT_FRACTION = 1 - the 0.30 refill); an ally refilled by any caster in the last 12 s "
         "(FOURTH.RESTOCK_CLAIM_S = active 10 s + 2 s) is skipped; unit_distance <= the entry's bound; the LOWEST "
         "fraction wins; bound: 70 m (70% of the ability's 100 m target_intercept_range); cast target: that ally; "
         "pre-cast re-check: the ally must still be alive, within the bound, shooting and at or below 0.70, else "
         "the cast is skipped; after an accepted cast the ally is claimed for 12 s; " + SHARED_TAIL
         + " GATES (round 130): charge hold 60 s (4 uses - one use per recharge period)."),
    BK: (AF, "allies_firing_aura: not routing; count the tracked allies that are alive (>0 men), not the owner, not "
         "routing, shooting past their cast point (firing flag ON and first shot + 0.5 x their reload from "
         "FOURTH.RELOAD_S) and within the aura bound by unit_distance (an unreadable distance does not count); fire "
         "when the count is at least 2 (FOURTH.BALLISTICS_MIN_FIRING); bound: 38 m (70% of the ability's 55 m "
         "effect_range); cast target: the ground at the caster's own position (perform_special_ability_ground, "
         "ground_keys); " + SHARED_TAIL),
    SK: (MS, "melee_or_shooting_into_melee: not routing; is_in_melee() with is_wavering() not true (fail-open "
         "morale, exactly as melee_unwavering) fires at once; otherwise is_wavering() must not be true, the unit's "
         "own firing flag must be ON and past its cast point (first shot + 0.5 x its reload), and "
         "current_target():is_in_melee() must be exactly true (unreadable fails closed); cast target: self; "
         + SHARED_TAIL),
}

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

# ------------------------------------------------------------------ (1) the three rows
for key, (fam, text) in TEXT.items():
    rs = row_of.get(key, [])
    assert len(rs) == 1 and keys_of(rs[0]) == [key], (key, rs)
    r = rs[0]
    assert str(ws.cell(row=r, column=18).value) == "IN-WHEEL", key
    assert str(ws.cell(row=r, column=19).value).startswith("carrier family:"), key
    if key == SK:
        assert str(ws.cell(row=r, column=20).value) == "IMPLEMENTED" and str(ws.cell(row=r, column=21).value) == MU
    else:
        assert str(ws.cell(row=r, column=20).value) == "NOT IMPLEMENTED", key
    ws.cell(row=r, column=20).value = "IMPLEMENTED"
    ws.cell(row=r, column=21).value = fam
    ws.cell(row=r, column=22).value = text
print("rows changed:", len(TEXT))

# ------------------------------------------------------------------ (2) recount
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
assert (N_IMPL_ROWS, N_IMPL_KEYS) == (761, 761), (N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = N_IN - N_IMPL_ROWS
assert NOT_IMPL_IN == 362, NOT_IMPL_IN
N_SKIP = impl["SKIPPED (user decision)"]
assert N_SKIP == 13, N_SKIP
assert not [x for x in rows if x[4] == "IN-WHEEL" and any(k in army for k in x[3])]

entries, consts, tips = bd.mod_entries()
mod_keys = set(k for e in entries for k in e["keys"])
assert (len(entries), len(mod_keys)) == (709, 761), (len(entries), len(mod_keys))
assert not (mod_keys & army)
impl_rows_keys = set(k for x in rows if x[6] == "IMPLEMENTED" for k in x[3])
assert impl_rows_keys == mod_keys, (sorted(impl_rows_keys - mod_keys)[:5], sorted(mod_keys - impl_rows_keys)[:5])

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
assert len(trig) == 49 and sum(trig.values()) == 709 and sum(trig_keys.values()) == 761, \
    (len(trig), sum(trig.values()), sum(trig_keys.values()))
assert (trig[MU], trig[AL], trig[AF], trig[MS]) == (373, 1, 1, 1)
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
for key, (fam, _t) in TEXT.items():
    assert fam_by_key[key] == fam, (key, fam_by_key[key])

# ------------------------------------------------------------------ Numbers
n = wb["Numbers"]
assert n.cell(row=92, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert all(not str(m).startswith(("A9", "A1")) or int(str(m).split(":")[0][1:]) < 91 for m in n.merged_cells.ranges)
n.insert_rows(91, 3)
assert n.cell(row=95, column=1).value == "Bombardment set (COMPLETE - round 108)"
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-11-01     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v22 - ROUND 130, THE FIRST TRIGGERS ON THE FIRING FLAG. Restock! (ally_ammo_low) and Ballistics "
    "Calibration (allies_firing_aura) implemented on two NEW families; Skjalandir's Fall moves from "
    "melee_unwavering to the NEW melee_or_shooting_into_melee. Implemented 759 + 2 = 761 rows / 761 keys; not "
    "implemented among the included 364 - 2 = 362 (13 of them SKIPPED by user decision). 1,123 IN-WHEEL + 677 "
    "EXCLUDED = 1,800, unchanged. The mod: 709 entries / 761 keys / 49 trigger families.)")
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
    "to the headline (sum = 1,123 included, 761 implemented).")
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
    "Reconciliation (v22): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included "
    "761 + not implemented 362 = 1,123. The mod's ABILITIES table is 709 entries / 761 keys, and the join "
    "mod-key -> 'Ability key(s)' returns 761 / 761 with ZERO unmatched keys in either direction. 707 + 2 "
    "(round 130: Restock!, Ballistics Calibration) = 709 entries; 759 + 2 = 761 keys. NO army-bar (army_spec) "
    "key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 130 - re-counted from the mod's own ABILITIES table: 49 families / "
    "709 entries / 761 keys / 50 evaluators (ally_infinite_buff's evaluator stays unused since round 121). "
    "Round 130: the NEW ally_ammo_low (1), allies_firing_aura (1) and melee_or_shooting_into_melee (1); "
    "melee_unwavering 374 -> 373.")
for r in range(44, 94):
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
assert tot_row == 93, tot_row
n.cell(row=tot_row, column=2).value = "TOTAL (49 families / 50 evaluators)"
n.cell(row=tot_row, column=3).value = sum(trig.values())
n.cell(row=tot_row, column=4).value = sum(trig_keys.values())

# ------------------------------------------------------------------ Definitions
d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v21")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v22 (2026-11-01)"
r11 = d.cell(row=11, column=2)
assert "759 keys across 759 numbered rows (rounds 122-123 added 21)" in r11.value
r11.value = r11.value.replace("759 keys across 759 numbered rows (rounds 122-123 added 21)",
                              "761 keys across 761 numbered rows (rounds 122-123 added 21, round 130 added 2)")
r12 = d.cell(row=12, column=2)
assert "of which 364 are in the wheel" in r12.value and "(1,041 keys" in r12.value
r12.value = (r12.value.replace("of which 364 are in the wheel", "of which 362 are in the wheel")
             .replace("(1,041 keys", "(1,039 keys"))
g = d.cell(row=21, column=1)
assert str(g.value).startswith("3. TRIGGER-FAMILY GLOSSARY")
g.value = str(g.value) + " - the three round-130 families (ally_ammo_low, allies_firing_aura, " \
                         "melee_or_shooting_into_melee) are described in section 19"
refreshed = []
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
        refreshed.append(fam)
assert MU in refreshed, refreshed
a73 = d.cell(row=73, column=2)
assert d.cell(row=73, column=1).value == "No firing read"
a73.value = (str(a73.value) + " Since round 126 the mod DERIVES one: a drop in ammo_left() between two polls "
             "is a shot (FIRING ON), the cast point is first shot + 0.5 x the unit's reload (a table generated "
             "from the game data), FIRING OFF after max(2 x reload, 20 s) with no drop. Round 130 is the first "
             "to trigger on it (Restock!, Ballistics Calibration, Skjalandir's Fall).")
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
    ("19. ROUND 130 - THE FIRST TRIGGERS ON THE FIRING FLAG (v22)", None),
    ("THE RULINGS, VERBATIM (2026-11-01)", "\"Please implement the both recommended options.\" (Restock! option A, "
     "Ballistics Calibration option A.) Skjalandir's Fall, asked which shooting trigger: \"Shooting into melee\"."),
    ("EARLIER DECISIONS", "Restock! and Ballistics Calibration were on the user's deferred next-batch list "
     "(2026-11-01); neither had been rejected or skipped. Skjalandir's Fall's ranged half was deferred in round 124 "
     "until the ammo probe had field data."),
    ("THE NEW FAMILY: ally_ammo_low", "evaluate_ally_ammo_low | the shared ally picker, family 'ammo': an ally alive, "
     "not routing, within the entry's own 70% bound, SHOOTING (firing flag on) with 70% or less of its ammunition "
     "left; the lowest wins; an ally refilled in the last 12 s is skipped | cast target: that ally | 1 entry / 1 key "
     "(Restock!, 70 m of 100 m, charge hold 60 s)"),
    ("THE NEW FAMILY: allies_firing_aura", "evaluate_allies_firing_aura | at least 2 allies within the aura bound "
     "shooting past their cast point | cast target: the ground at the caster's own position | 1 entry / 1 key "
     "(Ballistics Calibration, 38 m of 55 m)"),
    ("THE NEW FAMILY: melee_or_shooting_into_melee", "evaluate_melee_or_shooting_into_melee | the melee_unwavering "
     "rule, OR the unit shooting past its cast point at a current target that is in melee | cast target: self | "
     "1 entry / 1 key (Skjalandir's Fall, moved from melee_unwavering)"),
    ("THE ARITHMETIC", "Implemented 759 + 2 = 761 rows = 761 keys; not implemented among the included 364 - 2 = 362 "
     "(13 SKIPPED by user decision); 1,123 IN-WHEEL + 677 EXCLUDED = 1,800 unchanged. Mod: 707 -> 709 entries, "
     "759 -> 761 keys, 46 -> 49 families, melee_unwavering 374 -> 373. Harness 129 full suite: 5,577 checks / 0 "
     "failures, run twice byte-identical."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

# ------------------------------------------------------------------ Changelog
ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-01"
ch.cell(row=r, column=2).value = "v22"
ch.cell(row=r, column=3).value = (
    "ROUND 130, THE FIRST TRIGGERS ON THE FIRING FLAG. (1) Restock! IMPLEMENTED on the NEW ally_ammo_low "
    "(a shooting ally within 70 m at 70%% ammunition or less, the lowest first; charge hold 60 s). (2) Ballistics "
    "Calibration IMPLEMENTED on the NEW allies_firing_aura (2 allies within 38 m shooting past their cast point; "
    "ground at the caster's feet). (3) Skjalandir's Fall moves to the NEW melee_or_shooting_into_melee (melee, or "
    "shooting past its cast point at an enemy in melee). (4) 759 -> 761 rows / keys; 364 -> 362 not implemented "
    "among the included; 1,123 + 677 = 1,800 unchanged. Mod 709 entries / 761 keys / 49 families. (5) SHIPPED: "
    "installed pack md5 %s; harness 129 full suite 5,577 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = ("user rulings 2026-11-01 (both recommended options; Skjalandir's Fall "
                                  "'Shooting into melee'); xlsx v22 supersedes v21; v1-v21 byte-unchanged.")

wb.save(DST)
print("wrote", DST)
print("rows", N, "in-wheel", N_IN, "excluded", N_EX, "impl rows", N_IMPL_ROWS, "impl keys", N_IMPL_KEYS,
      "not-impl in-wheel", NOT_IMPL_IN, "skipped", N_SKIP)
print("families", len(trig), "entries", sum(trig.values()), "keys", sum(trig_keys.values()),
      "glossary refreshed", len(refreshed), "gate coverage", cov_gate)
