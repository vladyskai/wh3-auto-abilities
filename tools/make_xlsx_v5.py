"""Create WH3_abilities_master_v5_2026-10-17.xlsx from v4 (v1-v4 untouched).

v5 folds in round 103 (charge gate + FOURTH.health_pct) and round 104 (in-flight
gate + ally-aware health family), adds the Transforms sheet, re-counts Numbers.
"""
import csv, hashlib, json, os, re, shutil
from copy import copy
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
DOCS = os.path.join(ROOT, "docs")
V4 = os.path.join(DOCS, "WH3_abilities_master_v4_2026-10-17.xlsx")
V5 = os.path.join(DOCS, "WH3_abilities_master_v5_2026-10-17.xlsx")
TODAY = "2026-10-17"
T = os.path.expandvars(r"%LOCALAPPDATA%\Temp\wh3")
SCRATCH = os.path.join(os.path.expandvars(r"%LOCALAPPDATA%\Hermes\cache\scratch"))


def load(f):
    with open(os.path.join(T, f), encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


spec = {r["key"]: r for r in load("unit_spec_abil.tsv")}
ua = {r["key"]: r for r in load("unit_abilities.tsv")}
land = {r["key"]: r for r in load("db_land_units.tsv")}


def fl(v):
    try:
        return float(v)
    except Exception:
        return 0.0


def num(x):
    return ("%d" % x) if abs(x - round(x)) < 1e-9 else ("%g" % x)


# ---------------------------------------------------------------- health family
GROUND = ["wh2_dlc10_item_abilities_star_of_avelorn", "wh3_dlc24_lord_abilities_gulyas"]
SELF = ["wh3_main_character_abilities_salyaks_lullaby", "wh3_main_character_abilities_locus_of_fecundity"]
ALLY = [
    "wh2_dlc16_item_abilities_berry_wine",
    "wh2_dlc16_item_abilities_dreaming_ring_i",
    "wh2_dlc16_item_abilities_dreaming_ring_ii",
    "wh2_dlc16_item_abilities_dreaming_ring_iii",
    "wh2_dlc16_spell_bound_earth_blood",
    "wh3_main_spell_bound_earth_blood",
    "wh3_dlc20_spell_bound_fleshy_abundance",
    "wh2_dlc16_spell_bound_regrowth",
    "wh2_main_spell_bound_radiant_gem_of_hoeth",
    "wh3_dlc26_spell_bound_trollguts",
]
OWNER_ONLY = {
    "wh2_dlc11_lord_abilities_ghoul_king_of_ushoran": "self",
    "wh3_dlc29_hero_abilities_blood_chalice": "self",
    "wh3_dlc26_item_abilities_bugmans_xxxxxx": "self",
    "wh2_dlc09_item_abilities_hieratic_jar": "self",
    "wh_main_hero_abilities_immortal_will": "self",
    "wh3_dlc29_spell_bound_invocation_of_nehek": "self",
    "wh2_dlc16_unit_abilities_neuroparasites": "self",
    "wh2_main_lord_abilities_potion_of_charoi": "self",
    "wh_main_item_abilities_potion_of_healing": "self",
    "wh_main_item_abilities_regenerating_flesh": "self",
    "wh2_main_item_abilities_skalm": "self",
    "wh3_main_weapon_abilities_skars_kraken_killer": "self",
    "wh3_cp1_character_abilities_protection_prayer": "tiger",
    "wh_pro02_item_abilities_blood_chalice_of_bathori": "commander",
    "wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness": "undead",
    "wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness_upgraded": "undead",
    "wh3_dlc25_item_abilities_necrotic_phylactry": "radius",
    "wh3_main_daemon_head_abilities_pestilent_regeneration": "radius",
    "wh3_main_item_abilities_saint_annushkas_finger_bone": "radius",
    "wh_main_item_abilities_scroll_of_power": "recharge",
}
WHY = {
    "self": "the game's own effect text says (to self) - a self-only heal",
    "tiger": "`invalid_target = unit_is_not_tiger_warrior` and the mod has no Tiger Warrior key list",
    "commander": "`invalid_target = unit_is_not_commander_class` - a commander list is derivable but was not wired",
    "undead": "`invalid_target = living_unit` - the recipient must be undead and the mod has no undead key list",
    "radius": "`effect_range = 0` and no target flags - no measurable radius, so no honest distance test",
    "recharge": "it is a recharge buff, not a heal - an ally's health is the wrong trigger",
}

AURA_GROUND = (
    "health_aura_ground (round 104): fire when the OWNER or a friendly unit inside the ability's own reach "
    "(floor(effect_range {er:g} x 0.70) = {reach} m aura) is at or below 75% health - read through "
    "FOURTH.health_pct, a real 0-100 %; choose the LOWEST-health qualifying unit; the owner's own arm is unchanged "
    "(<= 75 %, no distance test) and casts at her own feet; an ally arm casts the GROUND form at THAT ALLY's own "
    "position, perform_special_ability_ground(key, ally:position(), 0, 0); the chosen ally is re-checked the same "
    "tick (alive + still <= 75 % + still in reach) and the cast is skipped with a logged reason if it lapsed."
)
AURA_SELF = (
    "health_aura_self (round 104): fire when the OWNER or a friendly unit inside the self-centred aura "
    "(floor(effect_range {er:g} x 0.70) = {reach} m) is at or below 75% health - read through FOURTH.health_pct, a "
    "real 0-100 %; choose the LOWEST-health qualifying unit; the cast always goes ON THE CASTER (a hurt ally only "
    "ARMS the trigger and is never the cast target), re-checked the same tick."
)
AURA_ALLY = (
    "health_aura_ally (round 104): fire when the OWNER or a friendly unit inside the ability's own 70% bound "
    "(floor(target_intercept_range {tr:g} x 0.70) = {reach} m) is at or below 75% health - read through "
    "FOURTH.health_pct, a real 0-100 %; choose the LOWEST-health qualifying unit; cast the UNIT form "
    "perform_special_ability(key, chosen ally) ON that ally; the owner's arm is unchanged (<= 75 %, casts on "
    "herself); the chosen ally is re-checked the same tick (alive + still <= 75 % + still in range) and the cast is "
    "skipped with a logged reason on drift."
)
OWNER_TXT = (
    "ushoran_health (round 103 health reader + round 104 ruling): not routing; the OWNER's health through "
    "FOURTH.health_pct (0-100 %) is <= 75 - previously the 0..1 HealthPercent was compared against 75, so the gate "
    "fired on every unit; OWNER-ONLY: {why}; cast on SELF (unit form), no distance test, no hysteresis."
)
EYE_TXT = (
    "enemy_low_health_noncommander (round 103 health reader): not routing; keep enemies alive, valid, NOT a Lord or "
    "Hero (the derived 1,409-key commander set on type(); unit_class() == \"com\" fallback; both unreadable -> FAIL "
    "CLOSED) and BELOW 20% through FOURTH.health_pct (a real 0-100 % - HealthPercent was a 0..1 fraction, which made "
    "\"hp < 20\" true for every unit), inside the 70% bound (35 m of 50 m); pick the LOWEST health (closest as the "
    "tiebreak); cast the UNIT form perform_special_ability(key, enemy); pre-cast re-check of alive + health + "
    "commander + distance."
)

shutil.copy2(V4, V5)
print("copied v4 -> v5")
wb = openpyxl.load_workbook(V5)
ws = wb["Abilities"]

WRAP = Alignment(wrap_text=True, vertical="top")


def row_keys(r):
    return [p.strip() for p in str(ws.cell(row=r, column=3).value or "").split(";") if p.strip()]


updated = {"ground": 0, "self": 0, "ally": 0, "owner": 0, "eye": 0, "nurgling": 0, "gates": 0}
gate_rows = 0
for r in range(2, ws.max_row + 1):
    keys = row_keys(r)
    if not keys:
        continue
    k0 = keys[0]
    # --- the 13 ally-aware entries
    fam = None
    for k in keys:
        if k in GROUND:
            fam = "ground"
        elif k in SELF:
            fam = "self"
        elif k in ALLY:
            fam = "ally"
    if fam and ws.cell(row=r, column=20).value == "IMPLEMENTED":
        er = max(fl(spec.get(k, {}).get("effect_range")) for k in keys)
        tr = max(fl(spec.get(k, {}).get("target_intercept_range")) for k in keys)
        reach = int((er if fam != "ally" else tr) * 0.70 + 1e-9)
        txt = {"ground": AURA_GROUND, "self": AURA_SELF, "ally": AURA_ALLY}[fam].format(er=er, tr=tr, reach=reach)
        ws.cell(row=r, column=21, value="health_aura_" + fam)
        ws.cell(row=r, column=22, value=txt)
        updated[fam] += 1
    # --- owner-only health rows
    if any(k in OWNER_ONLY for k in keys) and ws.cell(row=r, column=20).value == "IMPLEMENTED":
        why = next(WHY[OWNER_ONLY[k]] for k in keys if k in OWNER_ONLY)
        ws.cell(row=r, column=21, value="ushoran_health")
        ws.cell(row=r, column=22, value=OWNER_TXT.format(why=why))
        updated["owner"] += 1
    # --- Eye of Khorne
    if "wh3_dlc26_lord_abilities_eye_of_khorne" in keys and ws.cell(row=r, column=20).value == "IMPLEMENTED":
        ws.cell(row=r, column=22, value=EYE_TXT)
        updated["eye"] += 1
    # --- Nurgling Tide + every implemented row whose behaviour the gates change
    if ws.cell(row=r, column=20).value != "IMPLEMENTED":
        continue
    uses = max([fl(spec.get(k, {}).get("num_uses")) for k in keys] + [0])
    wind = max([fl(spec.get(k, {}).get("wind_up_time")) for k in keys] + [0])
    charge_s = max([fl(spec.get(k, {}).get("recharge_time")) for k in keys
                    if fl(spec.get(k, {}).get("num_uses")) > 1] + [0])
    bits = []
    if uses > 1 and charge_s > 0:
        bits.append("charge hold %s s (%s uses - one use per recharge period)" % (num(charge_s), num(uses)))
    if wind > 0:
        bits.append("in-flight hold %s s (%s s wind-up + 2 s)" % (num(wind + 2), num(wind)))
    if not bits:
        continue
    gates = " GATES (rounds 103-104): " + "; ".join(bits) + "."
    old = str(ws.cell(row=r, column=22).value or "")
    if "GATES (" not in old:
        ws.cell(row=r, column=22, value=old.rstrip() + gates)
    if "nurgling_tide" in " ".join(keys):
        updated["nurgling"] += 1
    updated["gates"] += 1

print("row updates:", updated)

# ---------------------------------------------------------------- Definitions
ds = wb["Definitions"]
# openpyxl's insert_rows does NOT shift merged ranges: unmerge, edit, re-merge by text.
_dmerges = []
for _m in list(ds.merged_cells.ranges):
    _dmerges.append((str(_m), ds.cell(row=_m.min_row, column=1).value, ds.cell(row=_m.min_row, column=2).value))
for _m in list(ds.merged_cells.ranges):
    ds.unmerge_cells(str(_m))
ds.cell(row=1, column=1, value="DEFINITIONS - WH3 ability master v5 (%s)" % TODAY)

def settext(match, new):
    for r in range(1, ds.max_row + 1):
        v = ds.cell(row=r, column=1).value
        if isinstance(v, str) and v.startswith(match):
            ds.cell(row=r, column=1, value=new)
            return r
    raise AssertionError("not found: " + match)

settext("Consequence: 639 abilities",
        "Consequence: 658 abilities are out and 1,141 are in. Bound spells (176) are counted IN - a bound spell is "
        "drawable on the unit's own bar; spells, cataclysms, army-bar and quest abilities, the 15 boss-only "
        "abilities and the 4 illusion summons are out.")
for r in range(1, ds.max_row + 1):
    v = ds.cell(row=r, column=2).value
    if isinstance(v, str) and v.startswith("The ability is on the unit's ability bar"):
        ds.cell(row=r, column=2, value=v.replace("1,139 rows", "1,141 rows"))
    elif isinstance(v, str) and v.startswith("The ability is not in the mod's ABILITIES table"):
        ds.cell(row=r, column=2, value="The ability is not in the mod's ABILITIES table (1,117 rows, of which 459 "
                                       "are in the wheel).")

# ushoran_health glossary row
for r in range(1, ds.max_row + 1):
    if ds.cell(row=r, column=1).value == "ushoran_health":
        ds.cell(row=r, column=3, value=(
            "not routing; the OWNER's health through FOURTH.health_pct (a real 0-100 %) is <= 75; OWNER-ONLY by "
            "round 104 - the game's text says (to self), or the row has an unreadable target class / no measurable "
            "radius / is a recharge buff"))
        ds.cell(row=r, column=5, value="20")
        ds.cell(row=r, column=6, value="20")
        break

# three new health-aura rows before TOTAL
tot = None
for r in range(1, ds.max_row + 1):
    if str(ds.cell(row=r, column=1).value or "").startswith("TOTAL (all"):
        tot = r
        break
assert tot, "TOTAL row not found"
NEW = [
    ("health_aura_ground", "evaluate_health_aura_ground",
     "the OWNER or a friendly unit inside floor(effect_range x 0.70) is <= 75 % health (health_pct, 0-100); pick the "
     "LOWEST-health qualifying unit; an ally arm casts the GROUND form under that ally, the owner arm at her own feet",
     "ground under the chosen ally (owner arm: at the caster)", "2", "2"),
    ("health_aura_self", "evaluate_health_aura_self",
     "the OWNER or a friendly unit inside the self-centred aura (floor(effect_range x 0.70)) is <= 75 % health; the "
     "hurt ally only ARMS the trigger",
     "the CASTER (unit form)", "2", "2"),
    ("health_aura_ally", "evaluate_health_aura_ally",
     "the OWNER or a friendly unit inside floor(target_intercept_range x 0.70) is <= 75 % health; pick the "
     "LOWEST-health qualifying ally; re-check the ally the same tick (alive + still <= 75 % + still in range)",
     "the chosen ally (unit form)", "9", "10"),
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
        ds.cell(row=r, column=1, value="TOTAL (all 42 evaluators)")
        ds.cell(row=r, column=5, value="642")
        ds.cell(row=r, column=6, value="682")
        print("glossary TOTAL now at", r)
        break
for r in range(1, ds.max_row + 1):
    v = ds.cell(row=r, column=1).value
    if isinstance(v, str) and v.startswith("3. TRIGGER-FAMILY GLOSSARY"):
        ds.cell(row=r, column=1, value="3. TRIGGER-FAMILY GLOSSARY (42 evaluators)")

# section 7 - the gates (appended at the end)
last = ds.max_row
while last > 1 and all(ds.cell(row=last, column=c).value in (None, "") for c in range(1, 7)):
    last -= 1
GATES = [
    ("7. FIRING-LAYER GATES (rounds 103-104)", "", "", "", "", ""),
    ("", "", "", "", "", ""),
    ("Both gates sit in the SHARED poll, never in an evaluator: they apply to every trigger family below. They "
     "brake a cast that has just STARTED, which is the layer where the engine gives no readable state.", "", "", "", "", ""),
    ("Gate", "Table (Lua)", "Scope", "Rule", "", ""),
    ("charge gate", "charge_gate.hold_s", "129 keys whose own row has num_uses > 1",
     "after a successful cast the (unit, ability) pair is not eligible until its own recharge_time has passed - one "
     "use per charge cycle, silent, purged with the unit. Exists because can_perform answers true and the engine "
     "ACCEPTS a cast into an empty multi-use pool.", "", ""),
    ("in-flight gate", "cast_gate.wind_up_s", "136 keys whose own row has wind_up_time > 0",
     "after a successful cast the pair waits wind_up_time + 2 s (never less than the 2 s guard); one log line per "
     "pair per battle, purged with the unit. Exists because perform_special_ability issues an ORDER that replaces "
     "the current one, so a 2 s re-issue cancels a 3-5 s wind-up.", "", ""),
    ("", "", "", "", "", ""),
    ("Coverage in this workbook", "225 of the 682 implemented rows carry at least one gate clause in their Trigger "
     "(as implemented) text; rows with neither a multi-use pool nor a wind-up keep the plain 2 s guard.", "", "", "", ""),
]
start = last + 2
for i, vals in enumerate(GATES):
    for ci, v in enumerate(vals, 1):
        c = ds.cell(row=start + i, column=ci, value=v if v != "" else None)
        c.alignment = WRAP
    if vals[0].startswith("7."):
        ds.cell(row=start + i, column=1).font = Font(bold=True, size=12)
    elif vals[0] in ("Gate",):
        for ci in range(1, 5):
            ds.cell(row=start + i, column=ci).font = Font(bold=True)
print("gates section at", start)

for _rng, _a, _b in _dmerges:
    _t = None
    for _r in range(1, ds.max_row + 1):
        if _b is not None and ds.cell(row=_r, column=2).value == _b:
            _t = _r
            break
        if _b is None and _a is not None and ds.cell(row=_r, column=1).value == _a:
            _t = _r
            break
    if _t is not None:
        ds.merge_cells(start_row=_t, start_column=(2 if _rng.startswith("B") else 1),
                       end_row=_t, end_column=6)
print("Definitions: re-merged", len(_dmerges), "ranges")

# ---------------------------------------------------------------- Numbers
ns = wb["Numbers"]
_nmerges = []
for _m in list(ns.merged_cells.ranges):
    _nmerges.append(str(_m))
for _m in list(ns.merged_cells.ranges):
    ns.unmerge_cells(str(_m))
ns.cell(row=7, column=1,
        value="Date: 2026-10-17     Rule in force since: 2026-10-17     Inventory: 1,799 active abilities"
              "     (v5: rounds 103-104 - charge gate, one health reader, in-flight gate, ally-aware health;"
              " no entry added or removed)")
ns.cell(row=9, column=4, value="% of total (1,799)")
ns.cell(row=9, column=5, value="% of included (1,141)")
ns.cell(row=30, column=1, value="The 658 exclusions, by family")

# insert boss-only + illusion rows before the Total row
tot_r = None
for r in range(1, ns.max_row + 1):
    if str(ns.cell(row=r, column=2).value or "") == "Total excluded":
        tot_r = r
        break
assert tot_r, "Total excluded row not found"
ns.insert_rows(tot_r, 2)
for off, (i, fam, n) in enumerate([("5", "Boss-only unit (granted only to a _boss unit)", 15),
                                  ("6", "Illusion summons (spawn_is_decoy)", 4)]):
    r = tot_r + off
    for ci in range(1, 6):
        ns.cell(row=r, column=ci, value=None)
        src = ns.cell(row=r - 1, column=ci)
        dst = ns.cell(row=r, column=ci)
        dst.font = copy(src.font); dst.fill = copy(src.fill); dst.border = copy(src.border)
        dst.alignment = copy(src.alignment)
    ns.cell(row=r, column=1, value=i)
    ns.cell(row=r, column=2, value=fam)
    ns.cell(row=r, column=3, value=n)
    ns.cell(row=r, column=4, value=n / 1799)
    ns.cell(row=r, column=5, value=n / 658)
ns.cell(row=tot_r + 2, column=3, value=658)
print("numbers: exclusions block extended at", tot_r)

# reconciliation text
for r in range(1, ns.max_row + 1):
    v = ns.cell(row=r, column=1).value
    if isinstance(v, str) and v.startswith("Reconciliation:"):
        ns.cell(row=r, column=1, value=(
            "Reconciliation: included 1,141 + excluded 658 = 1,799 (658 = spell 418 + army 204 + cataclysm 16 + "
            "quest 1 + boss-only 15 + illusion 4). Implemented among the included 682 + implemented out 0 = 682 "
            "(the whole mod, 682 keys); not implemented in wheel 459 + implemented in wheel 682 = 1,141. Rounds "
            "103-104 changed NO row's in-wheel status and NO count: 642 entries / 682 keys before and after."))
        break

# trigger-family block at the bottom
tc = json.load(open(os.path.join(SCRATCH, "trigger_counts.json"), encoding="utf-8"))
r = ns.max_row + 2
ns.cell(row=r, column=1, value="Trigger families after rounds 103-104 - re-counted from the mod (642 entries / 682 keys)")
ns.cell(row=r, column=1).font = Font(bold=True)
r += 1
for ci, h in enumerate(["#", "Trigger family", "Entries", "Keys"], 1):
    ns.cell(row=r, column=ci, value=h).font = Font(bold=True)
r += 1
for i, (t, (en, ky)) in enumerate(sorted(tc.items(), key=lambda kv: (-kv[1][0], kv[0])), 1):
    ns.cell(row=r, column=1, value=i)
    ns.cell(row=r, column=2, value=t)
    ns.cell(row=r, column=3, value=en)
    ns.cell(row=r, column=4, value=ky)
    r += 1
ns.cell(row=r, column=1, value="")
ns.cell(row=r, column=2, value="TOTAL (42 evaluators)").font = Font(bold=True)
ns.cell(row=r, column=3, value=sum(v[0] for v in tc.values())).font = Font(bold=True)
ns.cell(row=r, column=4, value=sum(v[1] for v in tc.values())).font = Font(bold=True)
print("trigger block ends at", r)

# re-merge the two Numbers ranges (A4:E4 rule text; A:E on the reconciliation row)
ns.merge_cells("A4:E4")
for _r in range(1, ns.max_row + 1):
    if str(ns.cell(row=_r, column=1).value or "").startswith("Reconciliation:"):
        ns.merge_cells(start_row=_r, start_column=1, end_row=_r, end_column=5)
        break
print("Numbers: re-merged", len(_nmerges), "ranges")

# ---------------------------------------------------------------- Changelog
cs = wb["Changelog"]
row = cs.max_row + 1
cs.cell(row=row, column=1, value=TODAY)
cs.cell(row=row, column=2, value="v5")
cs.cell(row=row, column=3, value=(
    "ROUNDS 103-104 - THE FIRING-LAYER ROUND AND THE ALLY-AWARE HEALTH ROUND. (103a) CHARGE GATE: the engine "
    "answers can_perform = true and ACCEPTS a cast into an EMPTY multi-use pool (Nurgling Tide fired 55 times at a "
    "2.0 s cadence, 42 of them into nothing), so a new firing-layer table charge_gate.hold_s gives every one of the "
    "129 multi-use keys its own recharge_time and the (unit, ability) pair waits it after a successful cast - one "
    "use per charge cycle. (103b) ONE HEALTH READER: HealthPercent returns a 0..1 FRACTION, so 'hp < 20' was true "
    "for every unit and the Eye of Khorne finisher never gated anything; FOURTH.health_pct now returns 0-100 and "
    "all 11 call sites route through it, making the <=75 % heals and the 20 % finisher compare real percentages. "
    "(104a) IN-FLIGHT GATE: perform_special_ability issues an ORDER that replaces the current one, so a 2 s "
    "re-issue cancels a 3-5 s wind-up; cast_gate.wind_up_s carries the 136 wind-up keys and the pair now waits "
    "wind_up + 2 s. (104b) ALLY-AWARE HEALTH: Star of Avelorn and 13 entries changed - fire when the owner OR a "
    "friendly unit inside the ability's own reach is <= 75 %, pick the LOWEST-health unit and cast per the row's own "
    "targeting (ground under that ally / on that ally / on the caster for a self-centred aura); 20 entries stay "
    "owner-only with recorded reasons. Counts: 642 entries / 682 keys unchanged; ushoran_health 33 -> 20; new "
    "health_aura_ground 2, health_aura_self 2, health_aura_ally 9; evaluators 39 -> 42. Installed pack md5 "
    "1d7c199208d3892881fb6dea2adfbfac (harness 104: 3650 checks / 0 failures)."))
cs.cell(row=row, column=4, value=(
    "the user's field reports (Nurgling Tide counter loop and activation delay; Eye of Khorne above 20 %; Star of "
    "Avelorn only healing the caster); round docs WH3_bug_diagnosis_nurgling_eye.md and "
    "WH3_round104_inflight_and_star.md; mod + tracker + this workbook (harness 103-104). Supersedes v4; v1-v4 are "
    "left byte-unchanged."))
thin = Side(style="thin")
for ci in range(1, 5):
    cs.cell(row=row, column=ci).alignment = Alignment(wrap_text=True, vertical="top")
    cs.cell(row=row, column=ci).border = Border(left=thin, right=thin, top=thin, bottom=thin)
cs.row_dimensions[row].height = 190

# ---------------------------------------------------------------- Transforms sheet
TR = wb.create_sheet("Transforms")
TR.column_dimensions["A"].width = 5
TR.column_dimensions["B"].width = 44
TR.column_dimensions["C"].width = 58
TR.column_dimensions["D"].width = 44
TR.column_dimensions["E"].width = 12
TR.column_dimensions["F"].width = 16
TR.column_dimensions["G"].width = 10
TR.column_dimensions["H"].width = 15
TR.column_dimensions["I"].width = 40
TR.cell(row=1, column=1, value="TRANSFORM ACTIVE ABILITIES - derived from the game's own data (%s)" % TODAY)
TR.cell(row=1, column=1).font = Font(bold=True, size=13)
TR.cell(row=2, column=1, value=(
    "A TRANSFORM replaces the caster's unit with another unit. Two independent game-data signals identify them: "
    "unit_spec_abil.tsv spawn_is_transformation = true, and unit_abilities.type = wh_type_transform. They agree on "
    "16 keys; the union adds wh2_dlc14_lord_abilities_tzarkan_snikch (spawn flag only). A row whose spawn is a "
    "SEPARATE unit (spawn_shares_health_and_fatigue = false, spawned unit unrelated to the caster) is a summon, not "
    "a transform. No transform is implemented by the mod."))
TR.cell(row=2, column=1).alignment = WRAP
TR.merge_cells("A2:I2")
TR.row_dimensions[2].height = 58
TR.cell(row=3, column=1, value=(
    "17 active transform keys / 5 names - ALL IN-WHEEL, NONE IMPLEMENTED. 2 further keys are engine-typed "
    "wh_type_transform but do NOT replace the unit (no spawned_unit, no spawn flag) and are listed separately."))
TR.cell(row=3, column=1).font = Font(bold=True)
TR.merge_cells("A3:I3")
hdr = ["#", "Ability", "Key", "Replacement (spawned unit)", "spawn_is_transformation", "unit_abilities.type",
       "Wheel", "Implementation", "Tracker status"]
for ci, h in enumerate(hdr, 1):
    c = TR.cell(row=5, column=ci, value=h)
    c.font = Font(bold=True)
    c.fill = PatternFill("solid", fgColor="DDDDDD")
    c.border = Border(bottom=thin)
    c.alignment = WRAP

TRANSFORMS = [
    ("Tz'arkan", "wh2_dlc14_lord_abilities_tzarkan", "wh2_dlc14_def_cha_malus_darkblade_tzarkan_0", "true", "wh_type_transform"),
    ("Tz'arkan (MP)", "wh2_dlc14_lord_abilities_tzarkan_mp", "wh2_dlc14_def_cha_malus_darkblade_tzarkan_0", "true", "wh_type_transform"),
    ("Tz'arkan (Snikch)", "wh2_dlc14_lord_abilities_tzarkan_snikch", "wh2_dlc14_skv_cha_deathmaster_snikch_tzarkan_0", "true", "wh_type_augment"),
    ("Tz'arkan (spite form)", "wh2_dlc14_lord_abilities_tzarkan_spite", "wh2_dlc14_def_cha_malus_darkblade_tzarkan_1", "true", "wh_type_transform"),
    ("Tz'arkan (spite form, MP)", "wh2_dlc14_lord_abilities_tzarkan_spite_mp", "wh2_dlc14_def_cha_malus_darkblade_tzarkan_1", "true", "wh_type_transform"),
    ("Formless Horror", "wh3_dlc24_lord_abilities_formless_horror", "(no spawned_unit column value; spawn_type unit_position)", "true", "wh_type_transform"),
    ("Formless Horror (Changeling)", "wh3_dlc24_lord_abilities_formless_horror_changeling", "wh3_dlc24_tze_cha_changeling", "true", "wh_type_transform"),
    ("Formless Horror (quest battle)", "wh3_dlc24_lord_abilities_formless_horror_quest_battle", "wh3_dlc24_grn_cha_grimgor_ironhide_quest_battle", "true", "wh_type_transform"),
    ("Formless Horror (quest battle, Changeling form)", "wh3_dlc24_lord_abilities_formless_horror_quest_battle_changeling_form", "wh3_dlc24_tze_cha_changeling_quest_battle", "true", "wh_type_transform"),
    ("Transformation of the Dragon (Jade, dragon form)", "wh3_dlc24_lord_abilities_jade_dragon_dragon_form", "wh3_dlc24_cth_cha_yuan_bo_dragon", "true", "wh_type_transform"),
    ("Transformation of the Dragon (Jade, human form)", "wh3_dlc24_lord_abilities_jade_dragon_human_form", "wh3_dlc24_cth_cha_yuan_bo_human", "true", "wh_type_transform"),
    ("Transformation of the Dragon (Iron, dragon form)", "wh3_main_lord_abilities_iron_dragon_dragon_form", "wh3_main_cth_cha_iron_dragon_1", "true", "wh_type_transform"),
    ("Transformation of the Dragon (Iron, human form)", "wh3_main_lord_abilities_iron_dragon_human_form", "wh3_main_cth_cha_iron_dragon_0", "true", "wh_type_transform"),
    ("Transformation of the Dragon (Storm, dragon form)", "wh3_main_lord_abilities_storm_dragon_dragon_form", "wh3_main_cth_cha_storm_dragon_1", "true", "wh_type_transform"),
    ("Transformation of the Dragon (Storm, human form)", "wh3_main_lord_abilities_storm_dragon_human_form", "wh3_main_cth_cha_storm_dragon_0", "true", "wh_type_transform"),
    ("Burrow", "wh3_dlc27_unit_abilities_dread_maw_underground", "wh3_dlc27_nor_mon_dread_maw_underground", "true", "wh_type_transform"),
    ("Surface", "wh3_dlc27_unit_abilities_dread_maw_surface", "wh3_dlc27_nor_mon_dread_maw", "true", "wh_type_transform"),
]
TRACK = {
    "wh2_dlc14_lord_abilities_tzarkan": "excluded (impossible: no transform support)",
    "wh2_dlc14_lord_abilities_tzarkan_mp": "excluded (impossible: no transform support)",
    "wh2_dlc14_lord_abilities_tzarkan_snikch": "excluded (impossible: no transform support)",
    "wh2_dlc14_lord_abilities_tzarkan_spite": "excluded (impossible: no transform support)",
    "wh2_dlc14_lord_abilities_tzarkan_spite_mp": "excluded (impossible: no transform support)",
    "wh3_dlc24_lord_abilities_formless_horror": "skipped (revisit)",
    "wh3_dlc24_lord_abilities_formless_horror_changeling": "excluded (impossible: no transform support)",
    "wh3_dlc24_lord_abilities_formless_horror_quest_battle": "skipped (revisit)",
    "wh3_dlc24_lord_abilities_formless_horror_quest_battle_changeling_form": "excluded (impossible: no transform support)",
    "wh3_dlc24_lord_abilities_jade_dragon_dragon_form": "skipped (revisit)",
    "wh3_dlc24_lord_abilities_jade_dragon_human_form": "excluded (impossible: no transform support)",
    "wh3_main_lord_abilities_iron_dragon_dragon_form": "skipped (revisit)",
    "wh3_main_lord_abilities_iron_dragon_human_form": "excluded (impossible: no transform support)",
    "wh3_main_lord_abilities_storm_dragon_dragon_form": "skipped (revisit)",
    "wh3_main_lord_abilities_storm_dragon_human_form": "excluded (impossible: no transform support)",
    "wh3_dlc27_unit_abilities_dread_maw_underground": "excluded (auto: summon - actually a TRANSFORM)",
    "wh3_dlc27_unit_abilities_dread_maw_surface": "excluded (auto: summon - actually a TRANSFORM)",
}
r = 6
for i, (name, key, repl, flag, typ) in enumerate(TRANSFORMS, 1):
    TR.cell(row=r, column=1, value=i)
    TR.cell(row=r, column=2, value=name)
    TR.cell(row=r, column=3, value=key)
    TR.cell(row=r, column=4, value=repl)
    TR.cell(row=r, column=5, value=flag)
    TR.cell(row=r, column=6, value=typ)
    TR.cell(row=r, column=7, value="IN-WHEEL")
    TR.cell(row=r, column=8, value="NOT IMPLEMENTED")
    TR.cell(row=r, column=9, value=TRACK[key])
    for ci in range(1, 10):
        TR.cell(row=r, column=ci).alignment = WRAP
    r += 1

r += 1
TR.cell(row=r, column=1, value="Engine-typed wh_type_transform but NOT unit-replacing (no spawned_unit, no spawn flag) - excluded from the 17:")
TR.cell(row=r, column=1).font = Font(bold=True)
TR.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
r += 1
for name, key, note in [
    ("Mist Form", "wh3_dlc29_lord_abilities_mist_form", "model-state / movement effect; no unit swap"),
    ("Shadowstrider", "wh3_dlc29_lord_abilities_warp_step", "movement (teleport) effect; no unit swap"),
]:
    TR.cell(row=r, column=2, value=name)
    TR.cell(row=r, column=3, value=key)
    TR.cell(row=r, column=4, value="(none - no spawned_unit)")
    TR.cell(row=r, column=5, value="false")
    TR.cell(row=r, column=6, value="wh_type_transform")
    TR.cell(row=r, column=7, value="IN-WHEEL")
    TR.cell(row=r, column=8, value="NOT IMPLEMENTED")
    TR.cell(row=r, column=9, value="excluded (auto: vortex)")
    r += 1

r += 1
TR.cell(row=r, column=1, value="Checked and NOT a transform - Transformation of Kadon (implemented as a SUMMON in round 102):")
TR.cell(row=r, column=1).font = Font(bold=True)
TR.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
r += 1
for name, key, note, impl in [
    ("Transformation of Kadon", "wh3_dlc27_spell_bound_transformation_of_kadon",
     "spawn_is_transformation = false; spawn_shares_health_and_fatigue = false; type = wh_type_summon_unit; spawns the "
     "generic wh3_main_ogr_feral_manticore_summoned, unrelated to the caster -> a real SUMMON", "IMPLEMENTED (enemy_ground_melee)"),
    ("Transformation of Kadon (5 spellbook keys)", "wh2_dlc11_spell_beasts_transformation_of_kadon; wh2_dlc15_spell_beasts_transformation_of_kadon; wh2_dlc16_army_abilities_transformation_of_kadon; wh3_cp1_spell_beasts_transformation_of_kadon; wh_dlc03_spell_beasts_transformation_of_kadon",
     "same data shape (summon type, no transform flag); excluded as spells, none implemented", "NOT IMPLEMENTED"),
]:
    TR.cell(row=r, column=2, value=name)
    TR.cell(row=r, column=3, value=key)
    TR.cell(row=r, column=4, value=note)
    TR.cell(row=r, column=8, value=impl)
    for ci in range(1, 10):
        TR.cell(row=r, column=ci).alignment = WRAP
    TR.row_dimensions[r].height = 46
    r += 1

r += 1
notes = [
    "* All 17 transform keys are IN-WHEEL under the single rule; none is implemented, so NO transform is riding a summon trigger.",
    "* The earlier 11-key 'no transform/shapechange support' list was name-based: it held 10 real transforms plus Transformation of Kadon (a summon) and omitted 7 transform keys that sat under other statuses (3 dragon-form 'skipped (revisit)', Formless Horror base + quest battle, and the 2 Dread Maw rows mis-tagged 'excluded (auto: summon)').",
    "* Public-script API has no transform call: the battle API exposes perform_special_ability / _ground / _q only, so these remain unbuildable without an engine hook (same conclusion as the original exclusion, now on the correct key set).",
]
for n in notes:
    TR.cell(row=r, column=1, value=n).alignment = WRAP
    TR.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
    TR.row_dimensions[r].height = 34
    r += 1
TR.freeze_panes = "A6"

wb.save(V5)
print("wrote", V5, os.path.getsize(V5), "bytes")
