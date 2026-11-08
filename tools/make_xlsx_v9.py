"""Create WH3_abilities_master_v9_2026-10-17.xlsx from v8 (v1-v8 untouched).

v9 folds in round 108 - the two field rulings:
  * THE AIR-DROP BOUND IS 1 m: the user tested the family ("Drop Bombs" ->
    Drop Rocks / Terradon Riders in the field log) and said the bombs released
    too soon. The overlap bound drops from the 70% rule's 7 m to a USER-CHOSEN
    1 m test value, one constant (FOURTH.AIR_DROP_BOUND_M), with the
    edge-to-edge note: a unit directly on top reads near 0-5 m, and if it never
    fires the constant is easy to raise.
  * WARP LIGHTNING ROD implemented on melee_skip_commanders (Soulfire's
    trigger), with the Clan Moulder Lobotomy mutation note that explains the
    missing carrier junction.
"""
import collections
import csv
import os
import re
import shutil
from copy import copy

import openpyxl
from openpyxl.styles import Alignment, Border, Font, Side

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
DOCS = os.path.join(ROOT, "docs")
V8 = os.path.join(DOCS, "WH3_abilities_master_v8_2026-10-17.xlsx")
V9 = os.path.join(DOCS, "WH3_abilities_master_v9_2026-10-17.xlsx")
TODAY = "2026-10-18"
MOD = os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua")
DATA = os.path.expandvars(r"%LOCALAPPDATA%\Temp\wh3\unit_spec_abil.tsv")

WRAP = Alignment(wrap_text=True, vertical="top")
thin = Side(style="thin")

CALL_KEY = "wh3_twa07_spell_bound_call_of_tor"
WLR_KEY = "wh2_dlc16_unit_abilities_warp_lightning_rod"
AIR_KEYS = [
    "wh2_dlc09_unit_abilities_death_from_above",
    "wh2_main_unit_abilities_drop_rocks",
    "wh2_dlc12_unit_abilities_drop_rocks_character",
    "wh2_dlc12_unit_abilities_drop_rocks_of_chotec",
    "wh2_dlc12_unit_abilities_drop_rocks_of_sundering",
    "wh2_dlc12_lord_abilities_drop_sphere_of_tepok",
    "wh2_dlc12_lord_abilities_drop_sphere_of_tepok_upgraded",
    "wh3_dlc25_unit_abilities_gyrobomber_fire_bomb",
    "wh3_dlc25_unit_abilities_thunderbarge_fire_bomb",
    "wh_main_unit_abilities_gyrobomber_bomb",
    "wh_main_unit_abilities_gyrocopter_bomb",
    "wh3_dlc25_unit_abilities_gyrocopter_bomb_anti_large",
    "wh3_main_unit_abilities_sky_junk_bomb",
    "wh_dlc06_unit_abilities_skyhammer_bomb",
    "wh_dlc06_unit_abilities_skyhammer_fire_bomb",
    "wh2_main_unit_abilities_wake_of_fire",
    "wh3_twa07_unit_abilities_searing_torrent",
    "wh3_dlc24_unit_abilities_nan_gau_grenades",
    "wh3_dlc29_unit_abilities_undeath_from_above",
]
assert len(AIR_KEYS) == 19

AIR_TEXT = (
    "air_drop_on_infantry (round 107, bound CHANGED in round 108): the row has NO target flags at all "
    "(target_friends / target_enemies / target_ground / target_self all false), effect_range 0 and "
    "target_intercept_range 10, so the engine drops where the CASTER is and the only decision is WHEN. "
    "Fires when an enemy INFANTRY unit is inside the ability's overlap bound - battle_unit:is_infantry() "
    "first, unit_class() exact-match inf_mel/inf_mis/inf_spr second, FAIL CLOSED - measured by "
    "unit:unit_distance(caster) (EDGE-TO-EDGE) as the 'under the caster' proxy. THE BOUND IS 1 m "
    "(FOURTH.AIR_DROP_BOUND_M), A USER-CHOSEN TEST VALUE: the user field-tested this family (\"I tested "
    "Drop Bombs but it released them too soon. Please make the range only 1 meter, I will test it "
    "again.\") and the log names the tested row as Drop Rocks (wh2_main_unit_abilities_drop_rocks, "
    "Terradon Riders), accepted at 6.9 m and 6.0 m under the old 7 m proxy. 1 m is MUCH TIGHTER than the "
    "standing 70% rule (which says 7 m). Because unit_distance is EDGE-TO-EDGE, a unit DIRECTLY under "
    "the caster reads near 0-5 m rather than 0 m; if the ability never fires at 1 m the test is too "
    "tight, and the bound is ONE constant to raise (2, 3 or 5 m) - no per-row edit. "
    "{AIRNOTE} The cast is SELF-CENTRED: perform_special_ability(key, OWNER). The caster and the chosen "
    "enemy are re-read immediately before the cast (alive, still flying / out of melee where required, "
    "enemy still infantry and inside the bound) and the cast is skipped rather than spent."
)
AIRNOTE_AIR = ("AIR-ONLY: the row declares the engine's `grounded` invalid-usage flag (or every carrier "
               "carries the `flying` attribute), so is_currently_flying() must be exactly true - an "
               "unreadable read holds (fail-closed).")
AIRNOTE_NOFLY = ("NOT air-gated: one of its carriers is a GROUND variant and the row declares no "
                 "`grounded` flag, so the engine itself allows it on the ground.")
AIRNOTE_SEAR = ("NOT air-gated (a ground carrier - Doom Knights) and the row's `engaged_in_melee` flag is "
                "honoured: the cast only happens OUT of melee. The user's field note is that it recharges "
                "in melee, which is why melee is never required.")
AIRNOTE_MELEE = ("The row also declares `engaged_in_melee`, so the cast only happens OUT of melee.")

WLR_TEXT = (
    "melee_skip_commanders (round 108, 2026-10-18 - the user's rule, verbatim: \"Warp Lightning Rod "
    "seems to be an effect no unit has by default, but during the campaign some units can aquire it via "
    "mutation (Clan Moulder Lobotomy augmentation). Let's treat it the same as Soulfire.\"): fire when "
    "THIS unit is IN MELEE, but SKIP when EVERY enemy it is engaged with is a Lord or a Hero - the exact "
    "Soulfire / Call of Tor rule. The engagement set is the enemy enumerator's ALIVE + is_in_melee() "
    "units whose edge-to-edge unit_distance to the caster is <= 12 m (FOURTH.ENGAGE_CONTACT_M); each "
    "member is classified by the 1,409-key commander set (unit_class() == 'com' fallback, FAIL CLOSED) "
    "and the judged set is LOGGED under the warp_lightning_rod marker (type + flag + real distance), "
    "deduped by note text; the caster and the engagement set are re-read immediately before the cast. "
    "The cast is on SELF (the row is self-centred: affect_self true, all four target flags false, "
    "target_intercept_range 0); the charge gate holds it for its 60 s recharge (3 uses) and the "
    "in-flight gate for its 1 s wind-up. ITS GRANT, WHICH EXPLAINS THE MISSING CARRIER: this key has NO "
    "carrier junction row anywhere in the extracted data (no land_units / uset_ability entry - only the "
    "ability row, its `climbing` invalid-usage flag, its UI effects and its loc line), so it is NOT a "
    "default unit ability. In campaign it is granted by the Clan Moulder LOBOTOMY augmentation (a "
    "mutation), which is why no battle roster shows a carrier; the entry still fires because the mod "
    "arms per unit on whatever key that unit actually owns at battle time."
)

CALL_TEXT = (
    "melee_skip_commanders (round 107, 2026-10-18 - the user's rule, verbatim: \"Call of Tor looks very "
    "similar to Soulfire, so let's do the same trigger as a Soulfire.\"): fire when THIS unit is IN MELEE, "
    "but SKIP when EVERY enemy it is engaged with is a Lord or a Hero. The engagement set is the enemy "
    "enumerator's ALIVE + is_in_melee() units whose edge-to-edge unit_distance to the caster is <= 12 m "
    "(FOURTH.ENGAGE_CONTACT_M); each member is classified by the 1,409-key commander set (unit_class() == "
    "'com' fallback, FAIL CLOSED) and the judged set is LOGGED (type + flag + real distance), deduped by "
    "note text. The cast is on SELF (the row is self-centred: all four target flags false, range 0); the "
    "charge gate holds it for its 90 s recharge."
)

SPEC = {}
with open(DATA, encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        if not r["key"].startswith("#"):
            SPEC[r["key"]] = r


def bound_of(k):
    real = int(float(SPEC[k]["target_intercept_range"]))
    return real * 70 // 100, real


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
assert sum(cnt.values()) == 689, sum(cnt.values())
assert sum(keys.values()) == 742, sum(keys.values())
assert cnt["air_drop_on_infantry"] == 12 and keys["air_drop_on_infantry"] == 19
assert cnt["melee_skip_commanders"] == 4 and keys["melee_skip_commanders"] == 5
assert cnt["enemy_ground_melee_infantry"] == 30
assert cnt["health_below_15"] == 1 and keys["health_below_15"] == 5

shutil.copy2(V8, V9)
wb = openpyxl.load_workbook(V9)

# ---------------------------------------------------------------- Abilities
ws = wb["Abilities"]
row_keys = {}
for r in range(2, ws.max_row + 1):
    ks = [p.strip() for p in str(ws.cell(row=r, column=3).value or "").split(";") if p.strip()]
    for k in ks:
        row_keys.setdefault(k, []).append(r)

assert len(row_keys) >= 1797


def set_impl(k, family, text, status="IMPLEMENTED"):
    rows = row_keys.get(k)
    if rows is None:
        return 0
    assert len(rows) == 1, (k, rows)
    r = rows[0]
    assert ws.cell(row=r, column=18).value == "IN-WHEEL", (k, ws.cell(row=r, column=18).value)
    ws.cell(row=r, column=20, value=status)
    ws.cell(row=r, column=21, value=family)
    ws.cell(row=r, column=22, value=text)
    for c in (20, 21, 22):
        ws.cell(row=r, column=c).alignment = WRAP
    return 1


n = 0
for k in AIR_KEYS:
    real = int(float(SPEC[k]["target_intercept_range"]))
    if k == "wh2_dlc12_lord_abilities_drop_sphere_of_tepok":
        note = AIRNOTE_NOFLY
    elif k == "wh3_twa07_unit_abilities_searing_torrent":
        note = AIRNOTE_SEAR
    elif k == "wh2_dlc09_unit_abilities_death_from_above" or "drop_rocks" in k \
            or k == "wh2_main_unit_abilities_wake_of_fire" \
            or k == "wh3_dlc29_unit_abilities_undeath_from_above":
        note = AIRNOTE_AIR + " " + AIRNOTE_MELEE
    elif k in ("wh3_dlc25_unit_abilities_gyrobomber_fire_bomb",
               "wh3_dlc25_unit_abilities_thunderbarge_fire_bomb",
               "wh_main_unit_abilities_gyrobomber_bomb",
               "wh_main_unit_abilities_gyrocopter_bomb",
               "wh3_dlc25_unit_abilities_gyrocopter_bomb_anti_large",
               "wh_dlc06_unit_abilities_skyhammer_bomb",
               "wh_dlc06_unit_abilities_skyhammer_fire_bomb",
               "wh3_dlc24_unit_abilities_nan_gau_grenades"):
        note = AIRNOTE_AIR
    elif k == "wh3_main_unit_abilities_sky_junk_bomb":
        note = "AIR-ONLY: its carrier is the Sky-junk airframe; the row declares no invalid-usage flag."
    else:
        note = AIRNOTE_AIR
    n += set_impl(k, "air_drop_on_infantry",
                  AIR_TEXT.replace("{AIRNOTE}", note))
n += set_impl(CALL_KEY, "melee_skip_commanders", CALL_TEXT)

# WARP LIGHTNING ROD - the last of the 55, now IMPLEMENTED on Soulfire's trigger
rows = row_keys.get(WLR_KEY)
assert rows and len(rows) == 1
r = rows[0]
assert ws.cell(row=r, column=18).value == "IN-WHEEL", ws.cell(row=r, column=18).value
ws.cell(row=r, column=19, value=(
    "implemented (melee, skipping Lord/Hero-only fights) - round 108; "
    "the last of the 55 wheel bombardment keys"))
ws.cell(row=r, column=20, value="IMPLEMENTED")
ws.cell(row=r, column=21, value="melee_skip_commanders")
ws.cell(row=r, column=22, value=WLR_TEXT)
for c in (19, 20, 21, 22):
    ws.cell(row=r, column=c).alignment = WRAP
print("abilities: air-drop rows", n - 1, "| Call of Tor 1 | WLR 1")

# the gate-clause coverage, COUNTED from the sheet we just wrote
_cov_tot, _cov_gate, _cov_rows = 0, 0, 0
for _row in ws.iter_rows(min_row=2, min_col=20, max_col=22):
    if _row[0].value == "IMPLEMENTED":
        _cov_tot += 1
        _t = str(_row[2].value or "")
        if ("wind-up" in _t) or ("charge gate" in _t) or ("recharge_time" in _t) \
                or ("in-flight" in _t) or ("per-unit" in _t):
            _cov_gate += 1
print("coverage: %d of %d implemented rows carry a gate clause (%d keys)"
      % (_cov_gate, _cov_tot, sum(1 for _row in ws.iter_rows(min_row=2, min_col=20, max_col=20)
                                  if _row[0].value == "IMPLEMENTED")))

# ---------------------------------------------------------------- Definitions
ds = wb["Definitions"]
merges = []
for m in list(ds.merged_cells.ranges):
    merges.append((str(m), ds.cell(row=m.min_row, column=1).value, ds.cell(row=m.min_row, column=2).value))
for m in list(ds.merged_cells.ranges):
    ds.unmerge_cells(str(m))
ds.cell(row=1, column=1, value="DEFINITIONS - WH3 ability master v9 (%s)" % TODAY)


def find_row(col, pred):
    for r in range(1, ds.max_row + 1):
        v = ds.cell(row=r, column=col).value
        if isinstance(v, str) and pred(v):
            return r
    return None


r = find_row(1, lambda v: v == "IMPLEMENTED")
assert r
ds.cell(row=r, column=2, value="The ability is in the mod's ABILITIES table AND in the wheel (742 keys across 741 numbered "
                              "rows - one row names two keys). The "
                              "trigger column states exactly what the evaluator does.")
r = find_row(1, lambda v: v == "NOT IMPLEMENTED")
assert r
ds.cell(row=r, column=2, value="The ability is not in the mod's ABILITIES table (1,057 keys, of which 399 are in the "
                              "wheel).")

# the two round-108 glossary rows already exist (v8 inserted air_drop); update them
for rr in range(1, ds.max_row + 1):
    fam = ds.cell(row=rr, column=1).value
    if fam == "air_drop_on_infantry":
        ds.cell(row=rr, column=3, value=(
            "an enemy INFANTRY unit UNDER the caster: inside the family's overlap bound - 1 m "
            "(FOURTH.AIR_DROP_BOUND_M), a USER-CHOSEN TEST VALUE from round 108, not the 70% rule's 7 m - "
            "measured by unit_distance(caster) EDGE-TO-EDGE (a unit directly on top reads near 0-5 m; one "
            "constant to raise if it never fires); the caster must be airborne where the row says so (the "
            "`grounded` flag or a flying-only carrier) and OUT of melee where the row says so "
            "(`engaged_in_melee`); both the caster and the chosen enemy are re-read immediately before the cast"))
    if fam == "melee_skip_commanders":
        ds.cell(row=rr, column=3, value=(
            "the caster is IN MELEE, unless EVERY enemy it is engaged with is a Lord or Hero (the "
            "engagement set = alive + is_in_melee + edge-to-edge unit_distance <= 12 m, each classified "
            "with the 1,409-key commander set, fail-closed; the judged set is logged, deduped by note); "
            "round 108 adds Warp Lightning Rod (a campaign mutation grant), so the family is four entries"))
        ds.cell(row=rr, column=4, value="the OWNER itself (unit form; the rows are self-centred)")
        ds.cell(row=rr, column=5, value=4)
        ds.cell(row=rr, column=6, value=5)

for r in range(1, ds.max_row + 1):
    v = ds.cell(row=r, column=1).value
    if isinstance(v, str) and v.startswith("TOTAL (all"):
        ds.cell(row=r, column=1, value="TOTAL (all 46 evaluators)")
        ds.cell(row=r, column=5, value="689")
        ds.cell(row=r, column=6, value="742")

r = find_row(1, lambda v: v.startswith("Coverage in this workbook"))
if r:
    ds.cell(row=r, column=1, value=(
        "Coverage in this workbook: " + str(_cov_gate) + " of the " + str(_cov_tot) + " implemented rows (742 keys) carry at least one gate clause in their "
        "Trigger (as implemented) text; rows with neither a multi-use pool nor a wind-up keep the plain 2 s guard. "
        "BOMBARDMENT SET (round 108): all 55 wheel bombardment abilities are now implemented - the 55 = 58 "
        "unit-side wh_type_bombardment rows minus the 3 army-bar junctions (Thorsen's Thunderstorm x2, "
        "Bubonic Broadside); round 108 adds Warp Lightning Rod, the last one, on melee_skip_commanders."))
r = find_row(1, lambda v: v.startswith("7. FIRING-LAYER GATES"))
if r:
    ds.cell(row=r, column=1, value="7. FIRING-LAYER GATES (rounds 103-108)")

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
for m in list(ns.merged_cells.ranges):
    ns.unmerge_cells(str(m))

TOTAL, INCL = 1797, 1141
IMP = 742
NOTIMP = INCL - IMP

for r in range(1, ns.max_row + 1):
    lab = ns.cell(row=r, column=2).value
    if lab == "Implemented among the included":
        ns.cell(row=r, column=3, value=IMP)
        ns.cell(row=r, column=4, value=IMP / TOTAL)
        ns.cell(row=r, column=5, value=IMP / INCL)
    elif lab == "Not implemented among the included":
        ns.cell(row=r, column=3, value=NOTIMP)
        ns.cell(row=r, column=4, value=NOTIMP / TOTAL)
        ns.cell(row=r, column=5, value=NOTIMP / INCL)
    elif lab == "All implemented in the mod (4 + 6)":
        ns.cell(row=r, column=3, value=str(IMP))
        ns.cell(row=r, column=4, value=IMP / TOTAL)
        ns.cell(row=r, column=5, value=IMP / INCL)
    elif lab == "Total included":
        ns.cell(row=r, column=4, value=IMP)
ns.cell(row=7, column=1,
        value="Date: 2026-10-18     Rule in force since: 2026-10-17     Inventory: 1,799 active abilities"
              "     (v9: round 108 - the air-drop overlap bound is 1 m, a USER-CHOSEN TEST VALUE (was the "
              "70% rule's 7 m), and Warp Lightning Rod is implemented on melee_skip_commanders with its "
              "Clan Moulder Lobotomy mutation note)")

for r in range(1, ns.max_row + 1):
    v = ns.cell(row=r, column=1).value
    if isinstance(v, str) and v.startswith("Reconciliation:"):
        ns.cell(row=r, column=1, value=(
            "Reconciliation: included 1,141 + excluded 658 = 1,799. Implemented among the included 742 + not "
            "implemented 399 = 1,141. The mod's ABILITIES table is 689 entries / 742 keys (the two Soulfire "
            "keys are ONE entry, the two Slicing Shards keys are ONE entry). The tracker carries the "
            "implemented ROWS; implemented keys with no row of their own ride a row that names its sibling. "
            "Round 108 moved 1 key from NOT IMPLEMENTED to IMPLEMENTED (Warp Lightning Rod, 741 -> 742); the "
            "air-drop bound change is a BEHAVIOUR change, not a count change (12 entries / 19 keys, as in "
            "round 107); the in-wheel count, the exclusions and the carrier families' INCLUDED counts are "
            "unchanged."))
        break

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
        value="Trigger families after round 108 - re-counted from the mod (689 entries / 742 keys)")
ns.cell(row=start, column=1).font = Font(bold=True)
r = start + 1
for ci, h in enumerate(["#", "Trigger family", "Entries", "Keys"], 1):
    ns.cell(row=r, column=ci, value=h).font = Font(bold=True)
r += 1
for i, (t, n2) in enumerate(sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0])), 1):
    ns.cell(row=r, column=1, value=i)
    ns.cell(row=r, column=2, value=t)
    ns.cell(row=r, column=3, value=n2)
    ns.cell(row=r, column=4, value=keys[t])
    r += 1
ns.cell(row=r, column=2, value="TOTAL (46 evaluators)").font = Font(bold=True)
ns.cell(row=r, column=3, value=689).font = Font(bold=True)
ns.cell(row=r, column=4, value=742).font = Font(bold=True)
r += 2

# THE BOMBARDMENT RECONCILIATION (now complete)
ns.cell(row=r, column=1, value="Bombardment set (COMPLETE - round 108)").font = Font(bold=True)
r += 1
for ci, h in enumerate(["#", "Step", "Count"], 1):
    ns.cell(row=r, column=ci, value=h).font = Font(bold=True)
r += 1
BOMB_ROWS = [
    ("every wh_type_bombardment row in unit_abilities.tsv", 131),
    ("unit-side (source_type active/bound/lord/character/unit/item/rune/weapon) with a real ability row, visible, icon", 58),
    ("minus the army-bar junctions (Thorsen's Thunderstorm x2, Bubonic Broadside)", 3),
    ("= THE WHEEL BOMBARDMENT SET", 55),
    ("of which implemented after round 108 (34 + Call of Tor + 19 air-drop keys + Warp Lightning Rod)", 55),
    ("of which awaiting the user's ruling", 0),
]
for i, (lab, v) in enumerate(BOMB_ROWS, 1):
    ns.cell(row=r, column=1, value=i)
    ns.cell(row=r, column=2, value=lab)
    ns.cell(row=r, column=3, value=v)
    if i == 4:
        for c in (1, 2, 3):
            ns.cell(row=r, column=c).font = Font(bold=True)
    r += 1
ns.cell(row=r, column=1, value=(
    "Round 108 closes the set: Warp Lightning Rod (wh2_dlc16_unit_abilities_warp_lightning_rod) is the "
    "55th, implemented on melee_skip_commanders. Its grant is a Clan Moulder Lobotomy mutation in "
    "campaign, not a default unit ability - which is why the data has no carrier junction for it."))
print("numbers: trigger block + bombardment block end at", r)

ns.merge_cells("A4:E4")
for rr in range(1, ns.max_row + 1):
    if str(ns.cell(row=rr, column=1).value or "").startswith("Reconciliation:"):
        ns.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=5)
        break

# ---------------------------------------------------------------- Changelog
cs = wb["Changelog"]
row = cs.max_row + 1
cs.cell(row=row, column=1, value=TODAY)
cs.cell(row=row, column=2, value="v9")
cs.cell(row=row, column=3, value=(
    "ROUND 108 - THE 1 m AIR-DROP TEST BOUND + WARP LIGHTNING ROD. (1) THE AIR-DROP OVERLAP BOUND IS "
    "1 m, A USER-CHOSEN TEST VALUE. The user field-tested the family: \"I tested Drop Bombs but it "
    "released them too soon. Please make the range only 1 meter, I will test it again.\" 'Drop Bombs' is "
    "not a shipped ability name; the field log names the row actually tested - Drop Rocks "
    "(wh2_main_unit_abilities_drop_rocks, Terradon Riders) - accepted at 6.9 m and 6.0 m edge-to-edge "
    "under the old 7 m proxy. The whole air_drop_on_infantry family (12 entries / 19 keys) now takes the "
    "ONE constant FOURTH.AIR_DROP_BOUND_M = 1 m and BYPASSES the 70% map (the 10 m row range no longer "
    "maps to 7 m), because the constant is the single knob: unit_distance is EDGE-TO-EDGE, so a unit "
    "directly under the caster reads near 0-5 m rather than 0 m, and if the ability never fires at 1 m "
    "the test is too tight - raise the constant to 2, 3 or 5 m and nothing else changes. (2) WARP "
    "LIGHTNING ROD (wh2_dlc16_unit_abilities_warp_lightning_rod) is IMPLEMENTED on melee_skip_commanders "
    "exactly like Soulfire and Call of Tor: in melee, unless every engaged enemy is a Lord or a Hero, "
    "with the judged engagement set logged under the warp_lightning_rod marker and a pre-cast re-check. "
    "The user's ruling: \"Warp Lightning Rod seems to be an effect no unit has by default, but during the "
    "campaign some units can aquire it via mutation (Clan Moulder Lobotomy augmentation). Let's treat it "
    "the same as Soulfire.\" Its grant is a Clan Moulder LOBOTOMY mutation in campaign - NOT a default "
    "unit ability - which explains the missing carrier junction in the data. Counts: 688 -> 689 entries, "
    "741 -> 742 keys, melee_skip_commanders 3/4 -> 4/5, and the wheel bombardment set is COMPLETE at 55 "
    "implemented / 0 awaiting. Installed pack md5 4a1cedca34d0c4936eab4e9d5bd12f1a (harness 108: 4006 "
    "checks / 0 failures; red control 41 failures, all accounted for)."))
cs.cell(row=row, column=4, value=(
    "the user's two field rulings (1 m air-drop range; Warp Lightning Rod = Soulfire's trigger); the "
    "field log entry that identifies 'Drop Bombs' as Drop Rocks; data re-derived from unit_abilities.tsv "
    "/ unit_spec_abil.tsv / special_ability_to_invalid_usage_flags_tables.tsv / unit_abilities.loc.tsv; "
    "mod + tracker + this workbook (harness 108). Supersedes v8; v1-v8 are left byte-unchanged."))
for ci in range(1, 5):
    cs.cell(row=row, column=ci).alignment = Alignment(wrap_text=True, vertical="top")
    cs.cell(row=row, column=ci).border = Border(left=thin, right=thin, top=thin, bottom=thin)
cs.row_dimensions[row].height = 300

wb.save(V9)
print("wrote", V9, os.path.getsize(V9), "bytes")
