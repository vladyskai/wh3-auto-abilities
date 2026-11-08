"""Create WH3_abilities_master_v8_2026-10-17.xlsx from v7 (v1-v7 untouched).

v8 folds in round 107 - THE REMAINING BOMBARDMENT WORK:
  * the 11 "on top of" abilities (12 entries / 19 keys) on the NEW
    air_drop_on_infantry trigger;
  * Call of Tor on Soulfire's melee_skip_commanders trigger;
  * the per-unit serialisation window (a cast-gate mechanism note);
  * the BOMBARDMENT COUNT CORRECTION: the wheel set is 55, not 57
    (58 unit-side wh_type_bombardment rows minus 3 army-bar junctions),
    reconciled in Definitions, Numbers and the Changelog.
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
V7 = os.path.join(DOCS, "WH3_abilities_master_v7_2026-10-17.xlsx")
V8 = os.path.join(DOCS, "WH3_abilities_master_v8_2026-10-17.xlsx")
TODAY = "2026-10-17"
MOD = os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua")
DATA = os.path.expandvars(r"%LOCALAPPDATA%\Temp\wh3\unit_spec_abil.tsv")

WRAP = Alignment(wrap_text=True, vertical="top")
thin = Side(style="thin")

CALL_KEY = "wh3_twa07_spell_bound_call_of_tor"
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
    "air_drop_on_infantry (round 107, 2026-10-18): the row has NO target flags at all "
    "(target_friends / target_enemies / target_ground / target_self all false), effect_range 0 and "
    "target_intercept_range 10, so the engine drops where the CASTER is and the only decision is WHEN. "
    "Fires when an enemy INFANTRY unit is inside the ability's own 70% bound ({BOUND} m of its real {REAL} m) "
    "- battle_unit:is_infantry() first, unit_class() exact-match inf_mel/inf_mis/inf_spr second, FAIL "
    "CLOSED - measured by unit:unit_distance(caster) (edge-to-edge) as the 'under the caster' overlap "
    "proxy (the blast radius is NOT in the extracted tables; 7 m is a constant, not a game radius). "
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
assert sum(cnt.values()) == 688, sum(cnt.values())
assert sum(keys.values()) == 741, sum(keys.values())
assert cnt["air_drop_on_infantry"] == 12 and keys["air_drop_on_infantry"] == 19
assert cnt["melee_skip_commanders"] == 3 and keys["melee_skip_commanders"] == 4
assert cnt["enemy_ground_melee_infantry"] == 30
assert cnt["health_below_15"] == 1 and keys["health_below_15"] == 5

shutil.copy2(V7, V8)
wb = openpyxl.load_workbook(V8)

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
    b, real = bound_of(k)
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
                  AIR_TEXT.replace("{BOUND}", str(b)).replace("{REAL}", str(real)).replace("{AIRNOTE}", note))
n += set_impl(CALL_KEY, "melee_skip_commanders", CALL_TEXT)

# WARP LIGHTNING ROD: the one bombardment key still awaiting a ruling
rows = row_keys.get("wh2_dlc16_unit_abilities_warp_lightning_rod")
assert rows and len(rows) == 1
r = rows[0]
ws.cell(row=r, column=19, value="awaiting ruling (round 107: only 1 of the 55 wheel bombardment keys is left)")
ws.cell(row=r, column=20, value="AWAITING RULING")
ws.cell(row=r, column=21, value="-")
ws.cell(row=r, column=22, value=(
    "Not automated yet. The row has NO target flags at all (target_friends / target_enemies / "
    "target_ground / target_self all false), target_intercept_range 0, effect_range 0 and "
    "ai_usage = aoe_bombardment - a self-centred nuke with no enemy to click. Two candidate rules need "
    "the user's decision: (a) fire while N enemy units are inside a stated radius of the caster "
    "(a count rule - no such rule exists in the mod yet), or (b) leave it manual. It cannot ride "
    "air_drop_on_infantry: that trigger needs a flying caster and a 10 m row range, and this row has neither."))
for c in (19, 20, 22):
    ws.cell(row=r, column=c).alignment = WRAP
print("abilities: implemented rows", n, "| awaiting ruling 1")

# the gate-clause coverage, COUNTED from the sheet we just wrote
_cov_tot, _cov_gate = 0, 0
for _row in ws.iter_rows(min_row=2, min_col=20, max_col=22):
    if _row[0].value == "IMPLEMENTED":
        _cov_tot += 1
        _t = str(_row[2].value or "")
        if ("wind-up" in _t) or ("charge gate" in _t) or ("recharge_time" in _t) \
                or ("in-flight" in _t) or ("per-unit" in _t):
            _cov_gate += 1
print("coverage: %d of %d implemented rows carry a gate clause" % (_cov_gate, _cov_tot))

# ---------------------------------------------------------------- Definitions
ds = wb["Definitions"]
merges = []
for m in list(ds.merged_cells.ranges):
    merges.append((str(m), ds.cell(row=m.min_row, column=1).value, ds.cell(row=m.min_row, column=2).value))
for m in list(ds.merged_cells.ranges):
    ds.unmerge_cells(str(m))
ds.cell(row=1, column=1, value="DEFINITIONS - WH3 ability master v8 (%s)" % TODAY)


def find_row(col, pred):
    for r in range(1, ds.max_row + 1):
        v = ds.cell(row=r, column=col).value
        if isinstance(v, str) and pred(v):
            return r
    return None


r = find_row(1, lambda v: v == "IMPLEMENTED")
assert r
ds.cell(row=r, column=2, value="The ability is in the mod's ABILITIES table AND in the wheel (741 keys across 740 numbered "
                              "rows - one row names two keys). The "
                              "trigger column states exactly what the evaluator does.")
r = find_row(1, lambda v: v == "NOT IMPLEMENTED")
assert r
ds.cell(row=r, column=2, value="The ability is not in the mod's ABILITIES table (1,058 keys, of which 400 are in the "
                              "wheel).")

tot = find_row(1, lambda v: v.startswith("TOTAL (all"))
assert tot, "TOTAL not found"
NEW = [
    ["air_drop_on_infantry", "evaluate_air_drop_on_infantry",
     "an enemy INFANTRY unit UNDER the caster: inside the ability's own 70% bound (7 m of the row's 10 m), "
     "measured by unit_distance(caster) as the overlap proxy (the blast radius is not in the extracted "
     "tables - 7 m is a constant); the caster must be airborne where the row says so (the `grounded` flag "
     "or a flying-only carrier) and OUT of melee where the row says so (`engaged_in_melee`); both the "
     "caster and the chosen enemy are re-read immediately before the cast",
     "the OWNER itself (the rows are self-centred: every target flag false)", 12, 19],
]
for g in NEW:
    ds.insert_rows(tot)
    for ci in range(1, 7):
        src = ds.cell(row=tot - 1, column=ci)
        dst = ds.cell(row=tot, column=ci)
        dst.font = copy(src.font)
        dst.fill = copy(src.fill)
        dst.border = copy(src.border)
        dst.alignment = copy(src.alignment)
        dst.value = None
    for ci, v in enumerate(g, 1):
        ds.cell(row=tot, column=ci, value=v)
    ds.cell(row=tot, column=3).alignment = WRAP
    tot += 1
print("definitions: glossary row inserted before TOTAL at", tot)

# the melee_skip_commanders row now carries THREE entries / FOUR keys
for rr in range(1, ds.max_row + 1):
    if ds.cell(row=rr, column=1).value == "melee_skip_commanders":
        ds.cell(row=rr, column=4, value="the OWNER itself (unit form; the rows are self-centred)")
        ds.cell(row=rr, column=5, value=3)
        ds.cell(row=rr, column=6, value=4)

for r in range(1, ds.max_row + 1):
    v = ds.cell(row=r, column=1).value
    if isinstance(v, str) and v.startswith("TOTAL (all"):
        ds.cell(row=r, column=1, value="TOTAL (all 46 evaluators)")
        ds.cell(row=r, column=5, value="688")
        ds.cell(row=r, column=6, value="741")
    if isinstance(v, str) and v.startswith("3. TRIGGER-FAMILY GLOSSARY"):
        ds.cell(row=r, column=1, value="3. TRIGGER-FAMILY GLOSSARY (46 evaluators)")

r = find_row(1, lambda v: v.startswith("Coverage in this workbook"))
if r:
    ds.cell(row=r, column=1, value=(
        "Coverage in this workbook: " + str(_cov_gate) + " of the " + str(_cov_tot) + " implemented rows (741 keys) carry at least one gate clause in their "
        "Trigger (as implemented) text; rows with neither a multi-use pool nor a wind-up keep the plain 2 s guard. "
        "BOMBARDMENT SET (CORRECTED, round 107): the wheel set is 55 abilities - 58 unit-side "
        "wh_type_bombardment rows minus the 3 army-bar junctions (Thorsen's Thunderstorm x2, Bubonic "
        "Broadside) - NOT 57. The old 57 = 58 minus Bubonic Broadside only, so it still counted the two "
        "Thorsen army-bar keys. Of the 55: 54 are implemented (Soulfire, Arachneruption, the 30, Call of "
        "Tor, the 19 air-drop keys) and 1 awaits a ruling (Warp Lightning Rod)."))
r = find_row(1, lambda v: v.startswith("7. FIRING-LAYER GATES"))
if r:
    ds.cell(row=r, column=1, value="7. FIRING-LAYER GATES (rounds 103-107)")
    ds.cell(row=r, column=2, value=(
        "Three gates act on a cast: the CHARGE gate (a multi-use pool is held for the row's own "
        "recharge_time), the IN-FLIGHT gate per (unit, ability) (wind-up + 2 s), and - round 107 - the "
        "PER-UNIT SERIALISATION window: after any successful cast no OTHER ability may be issued on that "
        "unit for its wind-up + 2 s, never less than 2.5 s. The engine allows only ONE special ability in "
        "flight per unit; a second order replaces the first during its wind-up while the replaced cast's "
        "use is still spent (field log 2026-10-17: Captain Roth's Moondial's 120 s recharge was consumed "
        "with no effect when Wraith Storm was issued 0.25 s later). A repeat of the SAME ability does not "
        "extend the window, so a fast-repeating ability cannot starve the others."))

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
IMP = 741
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
        value="Date: 2026-10-17     Rule in force since: 2026-10-17     Inventory: 1,799 active abilities"
              "     (v8: round 107 - Call of Tor on melee_skip_commanders, the 11 \"on top of\" abilities "
              "(12 entries / 19 keys) on air_drop_on_infantry, the per-unit serialisation window; and the "
              "BOMBARDMENT COUNT CORRECTION: the wheel set is 55, not 57)")

for r in range(1, ns.max_row + 1):
    v = ns.cell(row=r, column=1).value
    if isinstance(v, str) and v.startswith("Reconciliation:"):
        ns.cell(row=r, column=1, value=(
            "Reconciliation: included 1,141 + excluded 658 = 1,799. Implemented among the included 741 + not "
            "implemented 400 = 1,141. The mod's ABILITIES table is 688 entries / 741 keys (the two Soulfire "
            "keys are ONE entry, the two Slicing Shards keys are ONE entry). The tracker carries the "
            "implemented ROWS; implemented keys with no row of their own ride a row that names its sibling. "
            "Round 107 moved 20 keys from NOT IMPLEMENTED to IMPLEMENTED (721 -> 741: Call of Tor + the 19 "
            "air-drop keys); the in-wheel count, the exclusions and the carrier families' INCLUDED counts "
            "are unchanged."))
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
        value="Trigger families after round 107 - re-counted from the mod (688 entries / 741 keys)")
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
ns.cell(row=r, column=3, value=688).font = Font(bold=True)
ns.cell(row=r, column=4, value=741).font = Font(bold=True)
r += 2

# THE BOMBARDMENT RECONCILIATION (the 57 -> 55 correction, counted from the data)
ns.cell(row=r, column=1, value="Bombardment set (CORRECTED to 55 - round 107)").font = Font(bold=True)
r += 1
for ci, h in enumerate(["#", "Step", "Count"], 1):
    ns.cell(row=r, column=ci, value=h).font = Font(bold=True)
r += 1
BOMB_ROWS = [
    ("every wh_type_bombardment row in unit_abilities.tsv", 131),
    ("unit-side (source_type active/bound/lord/character/unit/item/rune/weapon) with a real ability row, visible, icon", 58),
    ("minus the army-bar junctions (Thorsen's Thunderstorm x2, Bubonic Broadside)", 3),
    ("= THE WHEEL BOMBARDMENT SET", 55),
    ("of which implemented after round 107 (34 + Call of Tor + 19 air-drop keys)", 54),
    ("of which awaiting the user's ruling (Warp Lightning Rod)", 1),
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
    "The old 57 was 58 minus Bubonic Broadside only - it still counted the two Thorsen army-bar keys. "
    "55 is the number under the wheel rule the workbook uses everywhere else."))
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
cs.cell(row=row, column=2, value="v8")
cs.cell(row=row, column=3, value=(
    "ROUND 107 - THE REMAINING BOMBARDMENT WORK. (1) THE COUNT IS CORRECTED: the wheel bombardment set is "
    "55, not 57 - 58 unit-side wh_type_bombardment rows minus 3 army-bar junctions (Thorsen's Thunderstorm "
    "x2 and Bubonic Broadside). The old 57 subtracted Bubonic Broadside only, so it still counted the two "
    "Thorsen army-bar keys; Numbers now reconciles 131 -> 58 -> 55 -> 54 implemented + 1 awaiting ruling. "
    "(2) CALL OF TOR (wh3_twa07_spell_bound_call_of_tor, Oath-Brothers of Tor) rides the EXISTING "
    "melee_skip_commanders trigger exactly like Soulfire: in melee, unless every engaged enemy is a Lord "
    "or a Hero, with the judged engagement set logged; melee_skip_commanders now carries 3 entries / 4 keys. "
    "(3) THE 11 \"ON TOP OF\" ABILITIES (12 entries / 19 keys: Death from Above, Drop Rocks x4 keys, Drop "
    "Sphere of Tepok x2, Fire Bombs x2, Gyrobomber Bomb x2, Gyrocopter Bomb anti-large, Sky-Junk Bomb, "
    "Skyhammer Bomb x2, Wake of Fire, Searing Torrent, Nan-Gau Grenades, Undeath from Above) ride the NEW "
    "air_drop_on_infantry evaluator: an enemy INFANTRY unit inside the row's own 70% bound (7 m of its "
    "10 m), airborne where the row declares `grounded` (or every carrier flies), out of melee where the row "
    "declares `engaged_in_melee`, self-centred cast on the OWNER, and a logged pre-cast re-check. Searing "
    "Torrent and Drop Sphere are documented NON-air-gated exceptions (a ground carrier / a ground lord "
    "variant with no `grounded` flag). (4) THE PER-UNIT SERIALISATION WINDOW fixes Wraith Storm blocking "
    "Captain Roth's Moondial: the field log shows the Moondial issued first (3 s wind-up), Wraith Storm "
    "issued 0.25 s later on the same caster, the Moondial's 120 s recharge consumed and its effect never "
    "landed - the engine allows ONE special ability in flight per unit. After any successful cast no OTHER "
    "ability may be issued on that unit for wind-up + 2 s (min 2.5 s); a same-ability repeat does not "
    "extend it. Counts: 675 -> 688 entries, 721 -> 741 keys, 45 -> 46 evaluators. Installed pack md5 "
    "c44f38d415e3e1e2e7b0bfb886c41e8c (harness 107: 3939 checks / 0 failures; red control 160 failures, "
    "all accounted for)."))
cs.cell(row=row, column=4, value=(
    "the user's four rulings (count correction; Call of Tor = Soulfire's trigger; the 11 on-top-of "
    "abilities on one evaluator; the Moondial / Wraith Storm serialisation fix); data re-derived from "
    "unit_abilities.tsv / unit_spec_abil.tsv / land_abil.tsv / uset_ability.tsv / army_spec.tsv; research "
    "in docs/WH3_bombardment_research.md and docs/WH3_bombardment_round2.md; mod + tracker + this workbook "
    "(harness 107). Supersedes v7; v1-v7 are left byte-unchanged."))
for ci in range(1, 5):
    cs.cell(row=row, column=ci).alignment = Alignment(wrap_text=True, vertical="top")
    cs.cell(row=row, column=ci).border = Border(left=thin, right=thin, top=thin, bottom=thin)
cs.row_dimensions[row].height = 300

wb.save(V8)
print("wrote", V8, os.path.getsize(V8), "bytes")
