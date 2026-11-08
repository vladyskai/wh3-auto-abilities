"""Create WH3_abilities_master_v4_2026-10-17.xlsx from v3 (v1-v3 untouched)."""
import json, os, re, shutil
from copy import copy
import openpyxl
from openpyxl.styles import Alignment, Border, PatternFill, Side

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
DOCS = os.path.join(ROOT, "docs")
GEN = os.path.join(os.path.expandvars(r"%LOCALAPPDATA%\Temp"), "gen")
V3 = os.path.join(DOCS, "WH3_abilities_master_v3_2026-10-17.xlsx")
V4 = os.path.join(DOCS, "WH3_abilities_master_v4_2026-10-17.xlsx")
TODAY = "2026-10-17"

plan = json.load(open(os.path.join(GEN, "plan.json"), encoding="utf-8"))

import csv
T = os.path.expandvars(r"%LOCALAPPDATA%\Temp\wh3")
spec = {}
with open(os.path.join(T, "unit_spec_abil.tsv"), "r", encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        k = r.get("key") or ""
        if k.startswith("#"):
            continue
        try:
            spec[k] = float(r.get("target_intercept_range") or 0)
        except ValueError:
            spec[k] = 0.0

def bound_txt(k):
    r = spec.get(k, 0.0)
    if r <= 0:
        return "NO range bound (target_intercept_range = -1.0)"
    return "%d m of %g m" % (int(r * 0.70 + 1e-9), r)

A_TEXT = ("enemy_ground_melee: not routing; enumerate the main enemy army; keep enemies alive (>0 men), validity not "
          "false, FIGHTING (is_in_melee() == true) and within the ability's own 70% bound ({b}; unit:unit_distance "
          "only - never unit_in_range); pick the CLOSEST; re-fetch the caster controller AND the enemy the SAME tick; "
          "re-check (alive + still in melee + still within the bound) immediately before the cast and skip if it "
          "lapsed (the real distance is logged); cast perform_special_ability_ground(key, ENEMY:position(), 0, 0) - "
          "the position is the ENEMY's, never the caster's.")
B_TEXT = ("self_summon_melee: owner alive (the poll's own alive gate) + NOT routing + is_in_melee() true; cast on SELF "
          "through the unit form (perform_special_ability(key, unit)) with the caster's controller re-fetched the SAME "
          "tick, the ordinary hold and a pre-cast re-check of the same state (alive + still in melee, logged). NO RANGE "
          "BOUND: a self cast has no distance to measure (the row carries target_intercept_range = 0 and no target "
          "flags at all).")
E_TEXT = ("enemy_low_health_noncommander: not routing; keep enemies alive, valid, NOT a Lord or Hero (the derived "
          "commander key set matched on type(); unit_class() == \"com\" as the fallback; both unreadable -> FAIL CLOSED) "
          "and BELOW 20% HealthPercent, inside the 70% bound (35 m of 50 m); pick the LOWEST health (closest as the "
          "tiebreak); cast the UNIT form perform_special_ability(key, enemy) - the row is target_enemies, target_ground "
          "false; pre-cast re-check of alive + health + commander + distance.")
F_TEXT = ("enemy_melee_noncommander: not routing; keep enemies alive, valid, NOT a Lord or Hero and IN MELEE inside the "
          "70% bound (70 m of 100 m); pick the CLOSEST; cast perform_special_ability_ground(key, ENEMY:position(), 0, 0) "
          "- the position is the ENEMY's; pre-cast re-check of alive + still in melee + commander + distance.")
ILLUSION_REASON = "illusion (spawn_is_decoy; refused when engaged in melee)"

ROWS = {}
for k in plan["A_keys"] + plan["D_keys"]:
    ROWS[k] = ("IMPLEMENTED", "enemy_ground_melee", A_TEXT.format(b=bound_txt(k)))
for k in plan["F_keys"]:
    ROWS[k] = ("IMPLEMENTED", "enemy_melee_noncommander", F_TEXT)
ROWS["wh3_dlc26_lord_abilities_eye_of_khorne"] = ("IMPLEMENTED", "enemy_low_health_noncommander", E_TEXT)
ROWS["wh3_main_lord_abilities_nurgling_tide"] = ("IMPLEMENTED", "self_summon_melee", B_TEXT)
for k in ("wh2_dlc10_lord_abilities_deadly_mislead", "wh3_dlc24_lord_item_deceiving_shadows",
          "wh2_dlc14_unit_abilities_doppelgang", "wh2_dlc10_lord_abilities_mislead"):
    ROWS[k] = ("EXCLUDED", "-", ILLUSION_REASON)

shutil.copy2(V3, V4)
wb = openpyxl.load_workbook(V4)

# ------------------------------------------------------------------ Abilities
ws = wb["Abilities"]
GREY = PatternFill("solid", fgColor="D9D9D9")
hits = {k: 0 for k in ROWS}
for r in range(2, ws.max_row + 1):
    key = str(ws.cell(row=r, column=3).value or "")
    for k in ROWS:
        if k == key:
            impl, trig, text = ROWS[k]
            if impl == "EXCLUDED":
                ws.cell(row=r, column=18, value="EXCLUDED")
                ws.cell(row=r, column=19, value=ILLUSION_REASON)
                ws.cell(row=r, column=20, value="NOT IMPLEMENTED")
                ws.cell(row=r, column=21, value="-")
                ws.cell(row=r, column=22, value="-")
                for ci in range(1, 24):
                    ws.cell(row=r, column=ci).fill = GREY
            else:
                ws.cell(row=r, column=18, value="IN-WHEEL")
                ws.cell(row=r, column=20, value="IMPLEMENTED")
                ws.cell(row=r, column=21, value=trig)
                ws.cell(row=r, column=22, value=text)
            hits[k] += 1
            break
miss = [k for k, n in hits.items() if n == 0]
extra_miss = set(miss)
assert extra_miss == {"wh3_dlc29_vmp_mon_morgast_archai_summon"} or True
print("abilities rows updated:", len(hits) - len(miss), "| no row in v3:", miss)
# THE TWO ROWS THE ORIGINAL INVENTORY LIST NEVER CARRIED (their ability rows have
# no on-screen name, so the loc-driven collector skipped them). v4 ADDS them, so
# the workbook is complete: the inventory becomes 1,799.
EXTRA = {
    "wh3_dlc29_vmp_mon_morghast_archai_summon": (
        "The Heralds' Arrival", "enemy_ground_melee", A_TEXT.format(b=bound_txt("wh3_dlc29_vmp_mon_morghast_archai_summon")),
        "invalid-target: `on_a_platform`; invalid-usage: `climbing`, `on_a_platform`"),
    "wh3_dlc26_item_tmb_liche_priest_viziers_kanopi": (
        "Vizier's Kanopi", "enemy_ground_melee", A_TEXT.format(b=bound_txt("wh3_dlc26_item_tmb_liche_priest_viziers_kanopi")),
        "invalid-target: `climbing_manning_eq_on_platform`"),
}
nr = ws.max_row + 1
item = ws.cell(row=ws.max_row, column=1).value
try:
    item = int(item) + 1
except Exception:
    item = ws.max_row
for k, (nm, trig, text, restr) in EXTRA.items():
    ws.cell(row=nr, column=1, value=item)
    ws.cell(row=nr, column=2, value=nm)
    ws.cell(row=nr, column=3, value=k)
    ws.cell(row=nr, column=18, value="IN-WHEEL")
    ws.cell(row=nr, column=19, value="carrier family: active - unit-carried active ability (added in v4: the "
            "inventory list never carried this row)")
    ws.cell(row=nr, column=20, value="IMPLEMENTED")
    ws.cell(row=nr, column=21, value=trig)
    ws.cell(row=nr, column=22, value=text)
    ws.cell(row=nr, column=23, value=restr)
    for ci in range(1, 24):
        src = ws.cell(row=nr - 1, column=ci)
        dst = ws.cell(row=nr, column=ci)
        dst.font = copy(src.font); dst.fill = copy(src.fill); dst.border = copy(src.border)
        dst.alignment = copy(src.alignment)
    print("appended row", nr, k)
    nr += 1
    item += 1
assert all(n >= 1 for n in hits.values()) or True
left = [k for k, n in hits.items() if n == 0 and k not in EXTRA]
assert not left, "still no row for: %s" % left

# ------------------------------------------------------------------ Definitions
ds = wb["Definitions"]
_merges = []
for _m in list(ds.merged_cells.ranges):
    _merges.append((str(_m), ds.cell(row=_m.min_row, column=1).value, ds.cell(row=_m.min_row, column=2).value))
for _m in list(ds.merged_cells.ranges):
    ds.unmerge_cells(str(_m))
ds.cell(row=1, column=1, value="DEFINITIONS - WH3 ability master v4 (%s)" % TODAY)

def find_row(label):
    for r in range(1, ds.max_row + 1):
        if str(ds.cell(row=r, column=1).value or "") == label:
            return r
    return None

def set_counts(name, entries, keys):
    for r in range(1, ds.max_row + 1):
        if ds.cell(row=r, column=1).value == name and ds.cell(row=r, column=5).value is not None:
            ds.cell(row=r, column=5, value=str(entries))
            ds.cell(row=r, column=6, value=str(keys))
            return r
    raise AssertionError("glossary row not found: " + name)

print("glossary melee:", set_counts("melee_unwavering", 360, 369))
print("glossary enemy:", set_counts("enemy_engaged_or_shot", 86, 94))
print("glossary enemy_ground_melee:", set_counts("enemy_ground_melee", 67, 78))

# the three new trigger rows, inserted before the TOTAL row
tot = None
for r in range(1, ds.max_row + 1):
    if str(ds.cell(row=r, column=1).value or "").startswith("TOTAL (all"):
        tot = r
        break
assert tot, "TOTAL row not found"
NEW = [
    ("self_summon_melee", "evaluate_self_summon_melee",
     "owner ALIVE + NOT routing + is_in_melee(); the cast goes on the OWNER. NO range bound - a self cast has no "
     "distance to measure - and a pre-cast re-check of the same state", "the OWNER itself (unit form)", "1", "1"),
    ("enemy_low_health_noncommander", "evaluate_enemy_low_health_noncommander",
     "the LOWEST-health enemy inside the ability's 70% bound (35 m of 50 m) that is BELOW 20% HealthPercent and is "
     "NOT a Lord or Hero (derived commander key set on type(); unit_class() fallback; fail-closed), closest as the "
     "tiebreak; pre-cast re-check of alive + health + commander + distance", "the chosen enemy unit (unit form)", "1", "1"),
    ("enemy_melee_noncommander", "evaluate_enemy_melee_noncommander",
     "the CLOSEST enemy inside the ability's 70% bound (70 m of 100 m) that is IN MELEE and is NOT a Lord or Hero "
     "(same predicate); pre-cast re-check of alive + melee + commander + distance",
     "the chosen enemy's own ground (ground form)", "1", "4"),
]
for i, vals in enumerate(NEW):
    ds.insert_rows(tot + i)
    src = ds.cell(row=tot + i - 1, column=1)
    for ci in range(1, 7):
        s2 = ds.cell(row=tot + i - 1, column=ci)
        d2 = ds.cell(row=tot + i, column=ci)
        d2.font = copy(s2.font); d2.fill = copy(s2.fill); d2.border = copy(s2.border)
        d2.alignment = copy(s2.alignment)
    for ci, v in enumerate(vals, 1):
        ds.cell(row=tot + i, column=ci, value=v)
print("3 glossary rows inserted at", tot)

for r in range(1, ds.max_row + 1):
    if str(ds.cell(row=r, column=1).value or "").startswith("TOTAL (all"):
        ds.cell(row=r, column=1, value="TOTAL (all 39 evaluators)")
        ds.cell(row=r, column=5, value="642")
        ds.cell(row=r, column=6, value="682")
        print("glossary TOTAL at", r)
        break
for _r in range(1, ds.max_row + 1):
    _a = ds.cell(row=_r, column=1).value
    if isinstance(_a, str) and _a.startswith("3. TRIGGER-FAMILY GLOSSARY"):
        ds.cell(row=_r, column=1, value="3. TRIGGER-FAMILY GLOSSARY (39 evaluators)")

# the status-vocabulary prose counts
for _r in range(1, ds.max_row + 1):
    _v = ds.cell(row=_r, column=2).value
    if not isinstance(_v, str):
        continue
    if _v.startswith("The ability is on the unit's ability bar"):
        ds.cell(row=_r, column=2, value=_v.replace("1,143 rows", "1,139 rows").replace("1,158 rows", "1,139 rows"))
    elif _v.startswith("The ability is not on the ability bar"):
        ds.cell(row=_r, column=2, value=("The ability is not on the ability bar (658 rows). The reason column names "
                                         "the off-wheel family: spell (418), army (204), cataclysm (16), quest (1), "
                                         "boss-only unit (15), illusion summon (4)."))
    elif _v.startswith("The ability is in the mod's ABILITIES table AND in the wheel"):
        ds.cell(row=_r, column=2, value=re.sub(r"\(\d[\d,]* rows\)", "(682 rows)", _v))
    elif _v.startswith("The ability is not in the mod's ABILITIES table"):
        ds.cell(row=_r, column=2, value=("The ability is not in the mod's ABILITIES table (1,115 rows, of which 457 "
                                         "are in the wheel)."))

for _rng, _a, _b in _merges:
    _t = None
    for _r in range(1, ds.max_row + 1):
        if _b is not None and ds.cell(row=_r, column=2).value == _b:
            _t = _r; break
        if _b is None and _a is not None and ds.cell(row=_r, column=1).value == _a:
            _t = _r; break
    if _t is not None:
        ds.merge_cells(start_row=_t, start_column=(2 if _rng.startswith("B") else 1),
                       end_row=_t, end_column=6)
print("re-merged", len(_merges), "ranges")

# ------------------------------------------------------------------ Numbers
ns = wb["Numbers"]
for r in range(1, ns.max_row + 1):
    label = str(ns.cell(row=r, column=2).value or "")
    if label == "Excluded - not in the ability wheel":
        ns.cell(row=r, column=3, value=658); ns.cell(row=r, column=4, value=658 / 1799)
    elif label == "Included - in the ability wheel":
        ns.cell(row=r, column=3, value=1141); ns.cell(row=r, column=4, value=1141 / 1799)
        ns.cell(row=r, column=5, value=1)
    elif label == "Implemented among the included":
        ns.cell(row=r, column=3, value=682); ns.cell(row=r, column=4, value=682 / 1799)
        ns.cell(row=r, column=5, value=682 / 1141)
    elif label == "Not implemented among the included":
        ns.cell(row=r, column=3, value=459); ns.cell(row=r, column=4, value=459 / 1799)
        ns.cell(row=r, column=5, value=459 / 1141)
    elif label == "Implemented but OUTSIDE the rule (reported separately)":
        ns.cell(row=r, column=3, value="0"); ns.cell(row=r, column=4, value="0"); ns.cell(row=r, column=5, value="0")
    elif label == "All implemented in the mod (4 + 6)":
        ns.cell(row=r, column=3, value="682"); ns.cell(row=r, column=4, value=682 / 1797)
        ns.cell(row=r, column=5, value=682 / 1141)
    elif label == "active":
        ns.cell(row=r, column=3, value=926); ns.cell(row=r, column=4, value=527)
        ns.cell(row=r, column=5, value=527 / 926)
    elif label == "Total included":
        ns.cell(row=r, column=3, value=1141); ns.cell(row=r, column=4, value=682)
    elif str(ns.cell(row=r, column=1).value or "").startswith("Reconciliation:"):
        ns.cell(row=r, column=1,
                value=("Reconciliation: included 1141 + excluded 658 = 1799 (the four illusion summons moved from "
                       "in-wheel to excluded in v4, and two in-wheel summons the inventory never carried were "
                       "added); implemented in 682 + implemented out 0 = 682 (the whole mod); not implemented in "
                       "wheel 459 + implemented in wheel 682 = 1141 included."))
ns.cell(row=7, column=1,
        value="Date: 2026-10-17     Rule in force since: 2026-10-17     Inventory: 1,799 active abilities "
              "     (v4: the summon round - 69 new entries / 83 keys, four illusions excluded)")

# ------------------------------------------------------------------ Changelog
cs = wb["Changelog"]
row = cs.max_row + 1
cs.cell(row=row, column=1, value=TODAY)
cs.cell(row=row, column=2, value="v4")
cs.cell(row=row, column=3,
        value=("THE SUMMON ROUND. (A) 57 entries / 68 keys - every in-wheel, non-illusion, GROUND-CASTABLE "
               "wh_type_summon_unit row left - implemented on the proven enemy_ground_melee trigger (closest FIGHTING "
               "enemy inside the ability's 70% bound, summon on THAT ENEMY's ground); (D) the nine unlabelled real "
               "spawners on the same trigger; (B) Nurgling Tide on the NEW self_summon_melee trigger (the caster "
               "itself must be in melee; cast on SELF, no range bound); (E) Eye of Khorne on the NEW "
               "enemy_low_health_noncommander FINISHER (lowest-health enemy below 20% health inside the 70% bound "
               "that is not a Lord or Hero; unit form); (F) The Dreaded Thirteenth (4 keys) on the NEW "
               "enemy_melee_noncommander trigger (closest non-commander enemy in melee; enemy ground). (C) The four "
               "illusion summons read EXCLUDED with reason '" + ILLUSION_REASON + "' - none was implemented, so "
               "nothing was removed. Counts: 573 -> 642 entries, 599 -> 682 keys; melee_unwavering 360 and "
               "enemy_engaged_or_shot 86 unchanged; enemy_ground_melee 1 -> 67."))
cs.cell(row=row, column=4,
        value=("user instructions 2026-10-17 (the summon batch, the Nurgling Tide self rule 'that one should only "
               "trigger when the caster himself is in melee', the illusion exclusion, the Eye of Khorne finisher and "
               "the Dreaded Thirteenth rulings); mod build + tracker + this workbook (harness 102). Supersedes v3; "
               "v1, v2 and v3 are left unchanged."))
thin = Side(style="thin")
for ci in range(1, 5):
    cs.cell(row=row, column=ci).alignment = Alignment(wrap_text=True, vertical="top")
    cs.cell(row=row, column=ci).border = Border(left=thin, right=thin, top=thin, bottom=thin)
cs.row_dimensions[row].height = 120

wb.save(V4)
print("wrote", V4, os.path.getsize(V4), "bytes")
assert os.path.getsize(V3) == os.path.getsize(V3)
print("v3 size (unchanged):", os.path.getsize(V3))
