"""Create WH3_abilities_master_v6_2026-10-17.xlsx from v5 (v1-v5 untouched).

v6 folds in round 105: Tz'arkan implemented on the new health_below_15 trigger
(one entry, five keys) and the other 12 transform keys marked
SKIPPED (user decision). Adds the vocabulary + glossary entries, a Changelog row
and re-counted Numbers.
"""
import collections
import os
import re
import shutil

import openpyxl
from openpyxl.styles import Alignment, Border, Font, Side

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
DOCS = os.path.join(ROOT, "docs")
V5 = os.path.join(DOCS, "WH3_abilities_master_v5_2026-10-17.xlsx")
V6 = os.path.join(DOCS, "WH3_abilities_master_v6_2026-10-17.xlsx")
TODAY = "2026-10-17"
MOD = os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua")

WRAP = Alignment(wrap_text=True, vertical="top")
thin = Side(style="thin")

TZ_KEYS = [
    "wh2_dlc14_lord_abilities_tzarkan",
    "wh2_dlc14_lord_abilities_tzarkan_mp",
    "wh2_dlc14_lord_abilities_tzarkan_snikch",
    "wh2_dlc14_lord_abilities_tzarkan_spite",
    "wh2_dlc14_lord_abilities_tzarkan_spite_mp",
]
SKIP_KEYS = [
    "wh3_dlc24_lord_abilities_formless_horror",
    "wh3_dlc24_lord_abilities_formless_horror_changeling",
    "wh3_dlc24_lord_abilities_formless_horror_quest_battle",
    "wh3_dlc24_lord_abilities_formless_horror_quest_battle_changeling_form",
    "wh3_dlc24_lord_abilities_jade_dragon_dragon_form",
    "wh3_dlc24_lord_abilities_jade_dragon_human_form",
    "wh3_main_lord_abilities_iron_dragon_dragon_form",
    "wh3_main_lord_abilities_iron_dragon_human_form",
    "wh3_main_lord_abilities_storm_dragon_dragon_form",
    "wh3_main_lord_abilities_storm_dragon_human_form",
    "wh3_dlc27_unit_abilities_dread_maw_underground",
    "wh3_dlc27_unit_abilities_dread_maw_surface",
]

TZ_TEXT = (
    "health_below_15 (round 105, 2026-10-17): the OWNER is ALIVE (the poll's own gate), NOT routing, and "
    "its health - read ONLY through FOURTH.health_pct (0-100; NEVER raw HealthPercent, which answers a 0..1 "
    "FRACTION and would make 'hp < 15' true for every unit) - is strictly BELOW 15. The cast is on the OWNER "
    "ITSELF through the unit form (perform_special_ability(key, owner)) with the caster's controller re-fetched "
    "FRESH that tick; a self cast has NO range bound, so no distance is read. The exact percentage is logged at "
    "the decision (the ATTEMPT reason) and AGAIN at the pre-cast re-check, which re-reads alive + health and "
    "SKIPS the cast ('cast not spent') when the unit died or rose to/above 15 inside the wind-up. The shared "
    "in-flight gate applies (this key's own 3 s wind-up - 1.5 s for the Snikch key - so the pair waits "
    "wind-up + 2 s after a cast); no charge gate (unlimited uses). NOTE: the transform is very likely ONE-WAY "
    "and a 14% caster can die inside the 3 s wind-up - the 15% line is the user's deliberate rule and is ONE "
    "constant, FOURTH.TZARKAN_PCT, easy to raise."
)
SKIP_TEXT = (
    "No automation - SKIPPED BY THE USER'S DECISION of 2026-10-17: \"I see no point to automate Formless Horror, "
    "Transformation of the Dragon, Burrow and Surface. So we skip them and mark them as skipped in the "
    "spreadsheet.\" Nothing rides a trigger, the key is not in the mod's ABILITIES table, and no code was added "
    "or removed for it."
)
SKIP_STATUS = "skipped (user decision 2026-10-17: no automation wanted)"


def trigger_counts():
    s = open(MOD, encoding="utf-8").read()
    i = s.index("local ABILITIES = {")
    j = s.index("\n}\n", i)
    table = s[i:j]
    entries = re.split(r"\n\t\{ marker = ", table)[1:]
    cnt = collections.Counter()
    keys = collections.Counter()
    for e in entries:
        m = re.search(r'trigger\s*=\s*"([a-z0-9_]+)"', e)
        assert m, e[:120]
        t = m.group(1)
        cnt[t] += 1
        k = re.search(r"keys = \{(.*?)\}\s*,", e, re.S)
        assert k, e[:120]
        keys[t] += len(re.findall(r'"[^"]+"', k.group(1)))
    return cnt, keys


cnt, keys = trigger_counts()
assert sum(cnt.values()) == 643, sum(cnt.values())
assert sum(keys.values()) == 687, sum(keys.values())
assert cnt["health_below_15"] == 1 and keys["health_below_15"] == 5

shutil.copy2(V5, V6)
wb = openpyxl.load_workbook(V6)

# ---------------------------------------------------------------- Abilities
ws = wb["Abilities"]
row_keys = {}
for r in range(2, ws.max_row + 1):
    ks = [p.strip() for p in str(ws.cell(row=r, column=3).value or "").split(";") if p.strip()]
    for k in ks:
        row_keys.setdefault(k, []).append(r)

assert len(row_keys) >= 1797
n_tz = n_sk = 0
for k in TZ_KEYS:
    assert len(row_keys[k]) == 1, (k, row_keys[k])
    r = row_keys[k][0]
    assert ws.cell(row=r, column=18).value == "IN-WHEEL"
    ws.cell(row=r, column=20, value="IMPLEMENTED")
    ws.cell(row=r, column=21, value="health_below_15")
    ws.cell(row=r, column=22, value=TZ_TEXT)
    for c in (20, 21, 22):
        ws.cell(row=r, column=c).alignment = WRAP
    n_tz += 1
for k in SKIP_KEYS:
    assert len(row_keys[k]) == 1, (k, row_keys[k])
    r = row_keys[k][0]
    assert ws.cell(row=r, column=18).value == "IN-WHEEL"
    ws.cell(row=r, column=19, value=SKIP_STATUS)
    ws.cell(row=r, column=20, value="SKIPPED (user decision)")
    ws.cell(row=r, column=21, value="-")
    ws.cell(row=r, column=22, value=SKIP_TEXT)
    for c in (19, 20, 22):
        ws.cell(row=r, column=c).alignment = WRAP
    n_sk += 1
print("abilities: tzarkan rows", n_tz, "| skipped rows", n_sk)

# ---------------------------------------------------------------- Definitions
ds = wb["Definitions"]
merges = []
for m in list(ds.merged_cells.ranges):
    merges.append((str(m), ds.cell(row=m.min_row, column=1).value, ds.cell(row=m.min_row, column=2).value))
for m in list(ds.merged_cells.ranges):
    ds.unmerge_cells(str(m))
ds.cell(row=1, column=1, value="DEFINITIONS - WH3 ability master v6 (%s)" % TODAY)


def find_row(col, pred):
    for r in range(1, ds.max_row + 1):
        v = ds.cell(row=r, column=col).value
        if isinstance(v, str) and pred(v):
            return r
    return None


r = find_row(1, lambda v: v == "IMPLEMENTED")
assert r
ds.cell(row=r, column=2, value="The ability is in the mod's ABILITIES table AND in the wheel (687 rows). The trigger "
                              "column states exactly what the evaluator does.")
r = find_row(1, lambda v: v == "NOT IMPLEMENTED")
assert r
ds.cell(row=r, column=2, value="The ability is not in the mod's ABILITIES table (1,112 rows, of which 454 are in "
                              "the wheel).")

# the new vocabulary row, right after NOT IMPLEMENTED
vocab_row = find_row(1, lambda v: v == "NOT IMPLEMENTED") + 1
assert "OUTSIDE-RULE-IMPLEMENTED" in str(ds.cell(row=vocab_row, column=1).value)
ds.insert_rows(vocab_row)
for ci in range(1, 7):
    src = ds.cell(row=vocab_row - 1, column=ci)
    dst = ds.cell(row=vocab_row, column=ci)
    from copy import copy
    dst.font = copy(src.font)
    dst.fill = copy(src.fill)
    dst.border = copy(src.border)
    dst.alignment = copy(src.alignment)
    dst.value = None
ds.cell(row=vocab_row, column=1, value="SKIPPED (user decision)")
ds.cell(row=vocab_row, column=2, value=(
    "IN-WHEEL but OUT OF AUTOMATION BY THE USER'S RULING of 2026-10-17 ('no point to automate ... so we "
    "skip them'). 12 rows carry it, ALL of them transforms: Formless Horror x4, Transformation of the "
    "Dragon x6, Burrow and Surface. The Trigger family / Trigger columns stay '-', nothing is in the mod's "
    "ABILITIES table, and the status holds until the user reopens the item."))
ds.cell(row=vocab_row, column=2).alignment = WRAP
print("definitions: vocabulary row inserted at", vocab_row)

# the glossary row, before TOTAL
tot = find_row(1, lambda v: v.startswith("TOTAL (all"))
assert tot, "TOTAL not found"
from copy import copy
ds.insert_rows(tot)
for ci in range(1, 7):
    src = ds.cell(row=tot - 1, column=ci)
    dst = ds.cell(row=tot, column=ci)
    dst.font = copy(src.font)
    dst.fill = copy(src.fill)
    dst.border = copy(src.border)
    dst.alignment = copy(src.alignment)
    dst.value = None
GLOSS = ["health_below_15", "evaluate_tzarkan_low_health",
         "not routing; the OWNER's health through FOURTH.health_pct (a real 0-100 percent) is strictly BELOW 15; "
         "cast on SELF through the unit form with the caster's script_unit re-fetched FRESH that tick; NO range "
         "bound (a self cast has no distance); the pre-cast re-check re-reads alive + the exact percentage and "
         "SKIPS when the unit died or rose to/above 15; the in-flight gate applies (3 s wind-up, 1.5 s on the "
         "Snikch key)",
         "the OWNER itself (unit form)", 1, 5]
for ci, v in enumerate(GLOSS, 1):
    ds.cell(row=tot, column=ci, value=v)
ds.cell(row=tot, column=3).alignment = WRAP
print("definitions: glossary row inserted at", tot)

for r in range(1, ds.max_row + 1):
    v = ds.cell(row=r, column=1).value
    if isinstance(v, str) and v.startswith("TOTAL (all"):
        ds.cell(row=r, column=1, value="TOTAL (all 43 evaluators)")
        ds.cell(row=r, column=5, value="643")
        ds.cell(row=r, column=6, value="687")
    if isinstance(v, str) and v.startswith("3. TRIGGER-FAMILY GLOSSARY"):
        ds.cell(row=r, column=1, value="3. TRIGGER-FAMILY GLOSSARY (43 evaluators)")

# section 7 coverage sentence
r = find_row(1, lambda v: v.startswith("Coverage in this workbook"))
assert r
ds.cell(row=r, column=1, value=(
    "Coverage in this workbook: 230 of the 687 implemented rows carry at least one gate clause in their "
    "Trigger (as implemented) text; rows with neither a multi-use pool nor a wind-up keep the plain 2 s guard."))
r = find_row(1, lambda v: v.startswith("7. FIRING-LAYER GATES"))
if r:
    ds.cell(row=r, column=1, value="7. FIRING-LAYER GATES (rounds 103-105)")

for rng, a, b in merges:
    t = None
    for rr in range(1, ds.max_row + 1):
        if b is not None and ds.cell(row=rr, column=2).value == b:
            t = rr
            break
        if b is None and a is not None and ds.cell(row=rr, column=1).value == a:
            t = rr
            break
    if t is not None:
        ds.merge_cells(start_row=t, start_column=(2 if rng.startswith("B") else 1), end_row=t, end_column=6)

# ---------------------------------------------------------------- Numbers
ns = wb["Numbers"]
nmerges = [str(m) for m in list(ns.merged_cells.ranges)]
for m in list(ns.merged_cells.ranges):
    ns.unmerge_cells(str(m))

for r in range(1, ns.max_row + 1):
    lab = ns.cell(row=r, column=2).value
    if lab == "Implemented among the included":
        ns.cell(row=r, column=3, value=687)
        ns.cell(row=r, column=4, value=687 / 1799)
        ns.cell(row=r, column=5, value=687 / 1141)
    elif lab == "Not implemented among the included":
        ns.cell(row=r, column=3, value=454)
        ns.cell(row=r, column=4, value=454 / 1799)
        ns.cell(row=r, column=5, value=454 / 1141)
    elif lab == "All implemented in the mod (4 + 6)":
        ns.cell(row=r, column=3, value="687")
        ns.cell(row=r, column=4, value=687 / 1799)
        ns.cell(row=r, column=5, value=687 / 1141)
    elif lab == "active":
        ns.cell(row=r, column=4, value=532)
        ns.cell(row=r, column=5, value=532 / 926)
    elif lab == "Total included":
        ns.cell(row=r, column=4, value=687)
ns.cell(row=7, column=1,
        value="Date: 2026-10-17     Rule in force since: 2026-10-17     Inventory: 1,799 active abilities"
              "     (v6: round 105 - Tz'arkan implemented on health_below_15, ONE entry / FIVE keys; the"
              " other 12 transform keys SKIPPED by the user's decision)")

# reconciliation text
for r in range(1, ns.max_row + 1):
    v = ns.cell(row=r, column=1).value
    if isinstance(v, str) and v.startswith("Reconciliation:"):
        ns.cell(row=r, column=1, value=(
            "Reconciliation: included 1,141 + excluded 658 = 1,799. Implemented among the included 687 + not "
            "implemented 454 = 1,141. The mod's ABILITIES table is 643 entries / 687 keys (the five Tz'arkan "
            "keys are ONE entry). Round 105 moved 5 rows from NOT IMPLEMENTED to IMPLEMENTED (682 -> 687) and "
            "marked 12 in-wheel transform rows SKIPPED (user decision); the in-wheel count, the exclusions "
            "and the carrier families' INCLUDED counts are unchanged."))
        break

# the trigger-family block at the bottom: replace it wholesale
start = None
for r in range(1, ns.max_row + 1):
    v = ns.cell(row=r, column=1).value
    if isinstance(v, str) and v.startswith("Trigger families after"):
        start = r
        break
assert start
for r in range(start, ns.max_row + 1):
    for c in range(1, 6):
        ns.cell(row=r, column=c, value=None)
ns.cell(row=start, column=1,
        value="Trigger families after round 105 - re-counted from the mod (643 entries / 687 keys)")
ns.cell(row=start, column=1).font = Font(bold=True)
r = start + 1
for ci, h in enumerate(["#", "Trigger family", "Entries", "Keys"], 1):
    ns.cell(row=r, column=ci, value=h).font = Font(bold=True)
r += 1
for i, (t, n) in enumerate(sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0])), 1):
    ns.cell(row=r, column=1, value=i)
    ns.cell(row=r, column=2, value=t)
    ns.cell(row=r, column=3, value=n)
    ns.cell(row=r, column=4, value=keys[t])
    r += 1
ns.cell(row=r, column=2, value="TOTAL (43 evaluators)").font = Font(bold=True)
ns.cell(row=r, column=3, value=643).font = Font(bold=True)
ns.cell(row=r, column=4, value=687).font = Font(bold=True)
print("numbers: trigger block ends at", r)

ns.merge_cells("A4:E4")
for rr in range(1, ns.max_row + 1):
    if str(ns.cell(row=rr, column=1).value or "").startswith("Reconciliation:"):
        ns.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=5)
        break

# ---------------------------------------------------------------- Changelog
cs = wb["Changelog"]
row = cs.max_row + 1
cs.cell(row=row, column=1, value=TODAY)
cs.cell(row=row, column=2, value="v6")
cs.cell(row=row, column=3, value=(
    "ROUND 105 - TZ'ARKAN IMPLEMENTED ON A LOW-HEALTH TRIGGER; THE OTHER TRANSFORMS SKIPPED. (1) TZ'ARKAN: "
    "the user's rule 'activate Tz'arkan when caster health is below 15%'. ONE new entry ('tzarkan') carries "
    "all FIVE Tz'arkan keys (base / _mp / _snikch / _spite / _spite_mp) on ONE new trigger family, "
    "health_below_15: owner ALIVE, NOT routing, health BELOW 15 through FOURTH.health_pct (the ONE 0-100 "
    "reader - never raw HealthPercent), cast on SELF via the unit form with the caster's fresh script_unit, "
    "no range bound, the shared in-flight gate applying (3 s wind-up; 1.5 s on the Snikch key). The exact "
    "percentage is logged at the decision and at the pre-cast re-check, which skips the cast when the unit "
    "died or rose to/above the line inside the wind-up. THE 15% LINE IS DELIBERATE AND ONE CONSTANT "
    "(FOURTH.TZARKAN_PCT): the transform is likely one-way and a 14% caster can die inside the wind-up. "
    "Counts: 642 -> 643 entries, 682 -> 687 keys, 42 -> 43 evaluators. (2) THE OTHER 12 TRANSFORM KEYS ARE "
    "SKIPPED BY THE USER'S DECISION ('no point to automate ... so we skip them'): Formless Horror x4, "
    "Transformation of the Dragon x6, Burrow and Surface - Implementation 'SKIPPED (user decision)', tracker "
    "status 'skipped (user decision 2026-10-17: no automation wanted)', trigger columns '-'. None was ever in "
    "the mod, so nothing was removed. Installed pack md5 a8fea1b2ee6292e5c07ada2c621fa900 (harness 105: 3702 "
    "checks / 0 failures)."))
cs.cell(row=row, column=4, value=(
    "the user's two rulings of 2026-10-17 (Tz'arkan below 15%; skip Formless Horror / Transformation of the "
    "Dragon / Burrow / Surface); round doc WH3_round105_tzarkan_and_skips.md; mod + tracker + this workbook "
    "(harness 105). Supersedes v5; v1-v5 are left byte-unchanged."))
for ci in range(1, 5):
    cs.cell(row=row, column=ci).alignment = Alignment(wrap_text=True, vertical="top")
    cs.cell(row=row, column=ci).border = Border(left=thin, right=thin, top=thin, bottom=thin)
cs.row_dimensions[row].height = 210

# ---------------------------------------------------------------- Transforms
tr = wb["Transforms"]
tr.cell(row=2, column=1, value=(
    "A TRANSFORM replaces the caster's unit with another unit. Two independent game-data signals identify "
    "them: unit_spec_abil.tsv spawn_is_transformation = true, and unit_abilities.type = wh_type_transform. "
    "They agree on 16 keys; the union adds wh2_dlc14_lord_abilities_tzarkan_snikch (spawn flag only). A row "
    "whose spawn is a SEPARATE unit (spawn_shares_health_and_fatigue = false, spawned unit unrelated to the "
    "caster) is a summon, not a transform. Round 105: TZ'ARKAN's five keys ARE implemented (health_below_15); "
    "the other 12 are SKIPPED by the user's decision of 2026-10-17."))
tr.cell(row=3, column=1, value=(
    "17 active transform keys / 5 names - ALL IN-WHEEL. 5 IMPLEMENTED (Tz'arkan, on health_below_15), 12 "
    "SKIPPED (user decision). 2 further keys are engine-typed wh_type_transform but do NOT replace the unit "
    "(no spawned_unit, no spawn flag) and are listed separately."))
for r in range(6, 23):
    k = str(tr.cell(row=r, column=3).value or "")
    if k in TZ_KEYS:
        tr.cell(row=r, column=8, value="IMPLEMENTED (health_below_15)")
        tr.cell(row=r, column=9, value="implemented (health_below_15: below 15% self)")
    elif k in SKIP_KEYS:
        tr.cell(row=r, column=8, value="SKIPPED (user decision)")
        tr.cell(row=r, column=9, value=SKIP_STATUS)
    for ci in (8, 9):
        tr.cell(row=r, column=ci).alignment = WRAP

# the notes at the bottom of the sheet
for r in range(20, tr.max_row + 1):
    v = str(tr.cell(row=r, column=1).value or "")
    if v.startswith("* All 17 transform keys"):
        tr.cell(row=r, column=1, value=(
            "* All 17 transform keys are IN-WHEEL under the single rule. FIVE are implemented (Tz'arkan, "
            "health_below_15, round 105); the other TWELVE are SKIPPED by the user's decision of 2026-10-17 "
            "(Formless Horror x4, Transformation of the Dragon x6, Burrow, Surface). No transform was ever "
            "removed from the mod, so nothing had to be deleted."))
        tr.cell(row=r, column=1).alignment = WRAP

wb.save(V6)
print("wrote", V6, os.path.getsize(V6), "bytes")
