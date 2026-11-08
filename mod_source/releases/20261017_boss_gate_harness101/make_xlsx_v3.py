# -*- coding: utf-8 -*-
"""Create WH3_abilities_master_v3_2026-10-17.xlsx from v2 (v1/v2 untouched)."""
import os, shutil
from copy import copy
import openpyxl
from openpyxl.styles import Alignment, Border, Side

DOCS = r"C:\Users\vlady\Desktop\WH3_mod\docs"
V2 = os.path.join(DOCS, "WH3_abilities_master_v2_2026-10-17.xlsx")
V3 = os.path.join(DOCS, "WH3_abilities_master_v3_2026-10-17.xlsx")
TODAY = "2026-10-17"

BOSS = [  # key -> the only granting unit
    ("wh_dlc06_quest_abilities_grand_faiths_bastion", "wh_dlc06_emp_cha_arch_lector_0_boss", True),
    ("wh3_dlc27_qb_unit_abilities_bitter_sting", "wh3_dlc27_chs_feral_manticore_boss", True),
    ("wh3_dlc27_qb_unit_abilities_frenzied_challenge", "wh3_dlc27_bst_mon_ghorgon_boss", True),
    ("wh3_dlc27_qb_unit_abilities_visions_of_madness", "wh3_dlc27_bst_mon_jabberslythe_boss", True),
    ("wh3_dlc27_qb_unit_abilities_guttural_roar", "wh3_dlc27_cth_mon_celestial_lion_boss", True),
    ("wh2_dlc10_quest_abilities_fiery_head", "wh2_dlc10_def_mon_war_hydra_boss", False),
    ("wh2_dlc10_quest_abilities_regenerating_head", "wh2_dlc10_def_mon_war_hydra_boss", False),
    ("wh_dlc08_quest_abilities_howling_winter", "wh_dlc08_nor_mon_frost_wyrm_boss", False),
    ("wh_dlc08_quest_abilities_master_of_souls", "wh_dlc08_vmp_mon_terrorgheist_boss", False),
    ("wh_dlc04_quest_abilities_servant_of_nagash", "wh_dlc04_vmp_cha_strigoi_ghoul_king_0_boss", False),
    ("wh3_dlc27_qb_unit_abilities_dissolving_bone", "wh3_dlc27_tmb_mon_carrion_boss", False),
    ("wh3_dlc27_qb_unit_abilities_terrible_malice", "wh3_dlc27_sla_mon_preyton_boss", False),
    ("wh3_dlc27_qb_unit_abilities_copious_phlegm", "wh3_dlc27_nur_mon_toad_dragon_boss", False),
    ("wh2_dlc10_quest_abilities_magic_fiery_convocation", "wh2_dlc10_nor_mon_phoenix_flamespyre_boss", False),
    ("wh2_dlc10_quest_abilities_flame_storm", "wh2_dlc10_nor_mon_phoenix_flamespyre_boss", False),
]
GATE = "wh3_main_character_abilities_gate_of_khorne"
GATE_TEXT = (
    "enemy_ground_melee: not routing; enumerate the main enemy army; keep enemies alive (>0 men), validity not "
    "false, FIGHTING (is_in_melee() == true) and within the ability's own 70% bound (35 m = floor(50 * 0.70), "
    "FOURTH.ENEMY_CAST_R50; unit:unit_distance only - never unit_in_range); pick the CLOSEST; re-fetch the "
    "caster controller AND the enemy the SAME tick; re-check (alive + still in melee + still within 35 m) "
    "immediately before the cast and skip if it lapsed (the real distance is logged); cast "
    "perform_special_ability_ground(key, ENEMY:position(), 0, 0) - the position is the ENEMY's, never the "
    "caster's; reason: 'closest fighting (in-melee) enemy within bound (targeting <type>, distance=<x>m)'.")

wb = openpyxl.load_workbook(V2)

# ------------------------------------------------------------------ Abilities
ws = wb["Abilities"]
GREY = openpyxl.styles.PatternFill("solid", fgColor="D9D9D9")
hits = {k: [] for k, _, _ in BOSS}
gate_hits = []
for r in range(2, ws.max_row + 1):
    key = str(ws.cell(row=r, column=3).value or "")
    for k, unit, was in BOSS:
        if k in key:
            hits[k].append(r)
            ws.cell(row=r, column=18, value="EXCLUDED")
            ws.cell(row=r, column=19, value="boss-only unit (granted only to _boss units)")
            ws.cell(row=r, column=20, value=("REMOVED (boss-only)" if was else "NOT IMPLEMENTED"))
            ws.cell(row=r, column=21, value="-")
            ws.cell(row=r, column=22, value="-")
            for ci in range(1, 24):
                ws.cell(row=r, column=ci).fill = GREY
            break
    else:
        if GATE in key:
            gate_hits.append(r)
            ws.cell(row=r, column=20, value="IMPLEMENTED")
            ws.cell(row=r, column=21, value="enemy_ground_melee")
            ws.cell(row=r, column=22, value=GATE_TEXT)
assert all(len(v) == 1 for v in hits.values()), hits
assert len(gate_hits) == 1, gate_hits
print("boss rows:", [v[0] for v in hits.values()], "gate row:", gate_hits[0])

# ------------------------------------------------------------------ Definitions
ds = wb["Definitions"]
# openpyxl's insert_rows does NOT move merged ranges, so take them all off,
# remember their anchor TEXT, and re-merge after the inserts.
_merges = []
for _m in list(ds.merged_cells.ranges):
    _r = _m.min_row
    _merges.append((str(_m), ds.cell(row=_r, column=1).value, ds.cell(row=_r, column=2).value))
for _m in list(ds.merged_cells.ranges):
    ds.unmerge_cells(str(_m))
ds.cell(row=1, column=1, value="DEFINITIONS - WH3 ability master v3 (%s)" % TODAY)
# append two vocabulary rows after the REMOVED (outside rule) row
row_rem = None
for r in range(1, ds.max_row + 1):
    if ds.cell(row=r, column=1).value == "REMOVED (outside rule)":
        row_rem = r
        break
assert row_rem, "REMOVED (outside rule) row not found"
ds.insert_rows(row_rem + 1, 2)
for off, (a, b) in enumerate([
    ("REMOVED (boss-only)",
     "The ability WAS implemented but its ONLY grant path is a `_boss` unit (a quest-battle boss variant no "
     "player can obtain), so it was REMOVED from the mod's ABILITIES table in v3: Greater Faith Bastion, Bitter "
     "Sting, Frenzied Challenge, Visions of Madness, Guttural Roar. (5 rows.)"),
    ("boss-only unit (granted only to _boss units)",
     "The reason recorded in the Status-reason column for every ability whose only grant path is a `_boss` unit: "
     "15 rows carry it (the five REMOVED (boss-only) plus ten that never shipped). Verified from land_abil.tsv, "
     "uset_ability.tsv, sag_to_abilities/sag_to_units and army_ab_faction.tsv; skill/rite junctions are not in "
     "the extraction (see tracker §10.3)."),
]):
    src = ds.cell(row=row_rem, column=1)
    dst = ds.cell(row=row_rem + 1 + off, column=1)
    for ci in (1, 2):
        dst2 = ds.cell(row=row_rem + 1 + off, column=ci)
        src2 = ds.cell(row=row_rem, column=ci)
        dst2.font = copy(src2.font); dst2.fill = copy(src2.fill)
        dst2.border = copy(src2.border); dst2.alignment = copy(src2.alignment)
    ds.cell(row=row_rem + 1 + off, column=1, value=a)
    ds.cell(row=row_rem + 1 + off, column=2, value=b)

def set_counts(name, entries, keys):
    for r in range(1, ds.max_row + 1):
        if ds.cell(row=r, column=1).value == name and ds.cell(row=r, column=5).value is not None:
            ds.cell(row=r, column=5, value=str(entries))
            ds.cell(row=r, column=6, value=str(keys))
            return r
    raise AssertionError("glossary row not found: " + name)

print("glossary melee:", set_counts("melee_unwavering", 360, 369))
print("glossary enemy:", set_counts("enemy_engaged_or_shot", 86, 94))
# insert the new trigger row before the TOTAL row and update the totals
tot = None
for r in range(1, ds.max_row + 1):
    if str(ds.cell(row=r, column=1).value or "").startswith("TOTAL (all 35 evaluators)"):
        tot = r
        break
assert tot, "TOTAL row not found"
ds.insert_rows(tot)
src = ds.cell(row=tot - 1, column=1)
for ci in range(1, 7):
    s2 = ds.cell(row=tot - 1, column=ci)
    d2 = ds.cell(row=tot, column=ci)
    d2.font = copy(s2.font); d2.fill = copy(s2.fill); d2.border = copy(s2.border); d2.alignment = copy(s2.alignment)
vals = [
    "enemy_ground_melee", "evaluate_enemy_ground_melee",
    "not routing; the CLOSEST enemy that is alive, valid, FIGHTING (is_in_melee()) and within the ability's 70% "
    "bound (35 m of 50 m); the summon is placed on THAT ENEMY's ground (ground form) with fresh handles, a hold "
    "and a pre-cast re-check; never the caster's position",
    "the chosen enemy's own ground (ground form of the call)", "1", "1"]
for ci, v in enumerate(vals, 1):
    ds.cell(row=tot, column=ci, value=v)
print("glossary enemy_ground_melee inserted at", tot)
for r in range(tot, ds.max_row + 1):
    if str(ds.cell(row=r, column=1).value or "").startswith("TOTAL (all"):
        ds.cell(row=r, column=1, value="TOTAL (all 36 evaluators)")
        ds.cell(row=r, column=5, value="573")
        ds.cell(row=r, column=6, value="599")
        print("glossary TOTAL at", r)
        break

# the status-vocabulary prose carries counts - bring them to v3
for _r in range(1, ds.max_row + 1):
    _v = ds.cell(row=_r, column=2).value
    if not isinstance(_v, str):
        continue
    if _v.startswith("The ability is on the unit's ability bar"):
        ds.cell(row=_r, column=2, value=_v.replace("1,158 rows", "1,143 rows"))
    elif _v.startswith("The ability is not on the ability bar"):
        ds.cell(row=_r, column=2, value=("The ability is not on the ability bar (654 rows). The reason column names "
                                         "the off-wheel family: spell (418), army (204), cataclysm (16), quest (1), "
                                         "boss-only unit (15)."))
    elif _v.startswith("The ability is in the mod's ABILITIES table AND in the wheel"):
        ds.cell(row=_r, column=2, value=_v.replace("(603 rows)", "(599 rows)"))
    elif _v.startswith("The ability is not in the mod's ABILITIES table"):
        ds.cell(row=_r, column=2, value=("The ability is not in the mod's ABILITIES table (1,198 rows, of which 544 "
                                         "are in the wheel)."))
    elif _v.startswith("3. TRIGGER-FAMILY GLOSSARY"):
        ds.cell(row=_r, column=1 if ds.cell(row=_r, column=1).value else 1,
                value=None)
for _r in range(1, ds.max_row + 1):
    _a = ds.cell(row=_r, column=1).value
    if isinstance(_a, str) and _a.startswith("3. TRIGGER-FAMILY GLOSSARY"):
        ds.cell(row=_r, column=1, value="3. TRIGGER-FAMILY GLOSSARY (36 evaluators)")

# re-merge the paragraph rows at their NEW positions (matched by their text)
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
        ns.cell(row=r, column=3, value=654); ns.cell(row=r, column=4, value=654 / 1797)
    elif label == "Included - in the ability wheel":
        ns.cell(row=r, column=3, value=1143); ns.cell(row=r, column=4, value=1143 / 1797)
        ns.cell(row=r, column=5, value=1)
    elif label == "Implemented among the included":
        ns.cell(row=r, column=3, value=599); ns.cell(row=r, column=4, value=599 / 1797)
        ns.cell(row=r, column=5, value=599 / 1143)
    elif label == "Not implemented among the included":
        ns.cell(row=r, column=3, value=544); ns.cell(row=r, column=4, value=544 / 1797)
        ns.cell(row=r, column=5, value=544 / 1143)
    elif label == "Implemented but OUTSIDE the rule (reported separately)":
        ns.cell(row=r, column=3, value="0"); ns.cell(row=r, column=4, value="0"); ns.cell(row=r, column=5, value="0")
    elif label == "All implemented in the mod (4 + 6)":
        ns.cell(row=r, column=3, value="599"); ns.cell(row=r, column=4, value=599 / 1797)
        ns.cell(row=r, column=5, value=599 / 1143)
    elif label == "active":
        ns.cell(row=r, column=3, value=926); ns.cell(row=r, column=4, value=527)
        ns.cell(row=r, column=5, value=527 / 926)
    elif label == "Total included":
        ns.cell(row=r, column=3, value=1143); ns.cell(row=r, column=4, value=599)
    elif str(ns.cell(row=r, column=1).value or "").startswith("Reconciliation:"):
        ns.cell(row=r, column=1,
                value=("Reconciliation: included 1143 + excluded 654 = 1797 (15 boss-only keys moved from "
                       "in-wheel to excluded: 5 implemented + 10 not); implemented in 599 + implemented out 0 "
                       "= 599 (the whole mod); not implemented in wheel 544 + implemented in wheel 599 = 1143 "
                       "included."))
ns.cell(row=7, column=1,
        value="Date: 2026-10-17     Rule in force since: 2026-10-17     Inventory: 1,797 active abilities "
              "     (v3: boss-only exclusion + Gate of Khorne)")

# ------------------------------------------------------------------ Changelog
cs = wb["Changelog"]
row = cs.max_row + 1
cs.cell(row=row, column=1, value=TODAY)
cs.cell(row=row, column=2, value="v3")
cs.cell(row=row, column=3,
        value=("excluded the 15 boss-only abilities (Status EXCLUDED, reason 'boss-only unit (granted only to "
               "_boss units)'); the five that were implemented are marked REMOVED (boss-only) and were removed "
               "from the mod; Gate of Khorne implemented on the new enemy_ground_melee trigger (closest FIGHTING "
               "enemy within 35 m, summon on that enemy's ground)"))
cs.cell(row=row, column=4,
        value=("user instruction 2026-10-17 ('exclude the active abilities that are granted to boss units ...' and "
               "'The trigger will place it on the closest enemy that is in range of the ability and fighting'); "
               "mod build + tracker + this workbook (harness 101). Supersedes v2; v1 and v2 are left unchanged."))
thin = Side(style="thin")
for ci in range(1, 5):
    cs.cell(row=row, column=ci).alignment = Alignment(wrap_text=True, vertical="top")
    cs.cell(row=row, column=ci).border = Border(left=thin, right=thin, top=thin, bottom=thin)
cs.row_dimensions[row].height = 60

wb.save(V3)
print("wrote", V3, os.path.getsize(V3), "bytes")
assert os.path.getsize(V2) == 349270, "v2 changed!"
print("v2 untouched:", os.path.getsize(V2))
