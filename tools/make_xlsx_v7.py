"""Create WH3_abilities_master_v7_2026-10-17.xlsx from v6 (v1-v6 untouched).

v7 folds in round 106 - THE BOMBARDMENT ROUND: 30 of the user's 32 bombardment
abilities on the new enemy_ground_melee_infantry trigger, plus Soulfire (2 keys)
and Arachneruption on the new melee_skip_commanders trigger. Adds the two
glossary rows, the vocabulary note, a Changelog row and re-counted Numbers.
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
V6 = os.path.join(DOCS, "WH3_abilities_master_v6_2026-10-17.xlsx")
V7 = os.path.join(DOCS, "WH3_abilities_master_v7_2026-10-17.xlsx")
TODAY = "2026-10-17"
MOD = os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua")
DATA = os.path.expandvars(r"%LOCALAPPDATA%\Temp\wh3\unit_spec_abil.tsv")

WRAP = Alignment(wrap_text=True, vertical="top")
thin = Side(style="thin")

# the 30 implemented bombardment keys (entry -> keys)
BOMB_GROUND = [
    "wh2_dlc10_item_bound_assault_of_stone", "wh3_main_weapon_abilities_axe_of_tor",
    "wh3_main_mount_bound_celestial_comet", "wh3_main_mount_bound_celestial_lightning",
    "wh_dlc07_item_abilities_chalice_of_potions", "wh3_main_spell_bound_comet_of_casandora",
    "wh_dlc08_item_abilities_great_horn_of_dragon_ogre", "wh3_dlc23_lord_abilities_flame_and_shadow",
    "wh_dlc05_weapon_abilities_hawks_talon", "wh2_dlc13_character_ability_ishas_rain",
    "wh2_dlc17_spell_bound_urannons_thunderbolt_upgraded", "wh3_dlc29_unit_abilities_lightning_strike",
    "wh_main_lord_abilities_lord_of_the_storm", "wh3_dlc29_spell_bound_warp_lightning",
    "wh3_dlc29_unit_abilities_meteor_strike", "wh3_dlc25_lord_abilities_nemesis_crown",
    "wh_main_spell_bound_piercing_bolts_of_burning", "wh3_dlc25_character_abilities_pigeon_bomb",
    "wh2_main_spell_bound_rod_of_the_storm", "wh2_dlc10_item_abilities_sceptre_of_stone",
    "wh3_twa08_spell_bound_searing_doom", "wh3_dlc20_spell_bound_slicing_shards",
    "wh3_main_spell_slaanesh_slicing_shards_bound", "wh_dlc05_weapon_abilities_the_bow_of_loren",
    "wh2_dlc17_spell_bound_urannons_thunderbolt",
]
BOMB_UNIT = [
    "wh2_dlc10_spell_bound_lesser_doombolt", "wh3_dlc20_item_abilities_rod_of_torment",
    "wh2_main_spell_bound_tome_of_furion", "wh2_main_spell_bound_wand_of_the_kharaidon",
    "wh3_main_weapon_abilities_the_traitors_sword", "wh2_dlc11_lord_abilities_wraith_storm",
]
SOUL_KEYS = ["wh_main_spell_bound_soulfire", "wh_dlc04_spell_bound_soulfire_upgraded"]
ARACH_KEYS = ["wh2_dlc15_unit_abilities_arachneruption"]
SKIP_KEYS = {
    "wh3_dlc20_cataclysm_bound_thorsens_thunderstorm":
        "skipped (round 106: army-bar ability (army_spec junction) - out of wheel scope)",
    "wh3_dlc27_cataclysm_bound_thorsens_thunderstorm":
        "skipped (round 106: army-bar ability (army_spec junction) - out of wheel scope)",
    "wh2_dlc16_unit_abilities_warp_lightning_rod":
        "skipped (round 106: no enemy target - target flags all false, range 0, self-centred)",
}

BOMB_GROUND_TEXT = (
    "enemy_ground_melee_infantry (round 106, 2026-10-18): the CLOSEST enemy inside the ability's own "
    "70% bound ({BOUND} m of its real {REAL} m target_intercept_range) that is IN MELEE and IS INFANTRY - "
    "battle_unit:is_infantry() first (the API dump's own read), battle_unit:unit_class() exact-match "
    "against inf_mel / inf_mis / inf_spr as the fallback, FAIL CLOSED when neither answers - the lowest "
    "distance wins (unit_distance, edge-to-edge). The strike is PLACED ON THAT ENEMY's own ground through "
    "perform_special_ability_ground(key, enemy:position(), 0, 0). The chosen enemy is re-checked "
    "immediately before the cast (alive, in melee, STILL INFANTRY, inside the bound) and the cast is "
    "skipped rather than wasted. The shared in-flight gate applies (the row's own wind-up + 2 s) and the "
    "charge gate holds the pair for its own recharge_time when the row has more than one use."
)
BOMB_UNIT_TEXT = (
    "enemy_ground_melee_infantry (round 106, 2026-10-18): the CLOSEST enemy inside the ability's own "
    "70% bound ({BOUND} m of its real {REAL} m target_intercept_range) that is IN MELEE and IS INFANTRY - "
    "battle_unit:is_infantry() first, battle_unit:unit_class() exact-match against inf_mel / inf_mis / "
    "inf_spr as the fallback, FAIL CLOSED when neither answers. This row has NO ground target "
    "(target_ground = false), so the cast is the UNIT form: perform_special_ability(key, enemy). The "
    "chosen enemy is re-checked immediately before the cast (alive, in melee, still infantry, inside the "
    "bound). The shared in-flight gate applies."
)
SOUL_TEXT = (
    "melee_skip_commanders (round 106, 2026-10-18): fire when THIS unit is IN MELEE, but SKIP when "
    "EVERY enemy it is engaged with is a Lord or a Hero. The engagement set is read from the game's "
    "enemy enumerator - ALIVE + is_in_melee() + edge-to-edge unit_distance() <= FOURTH.ENGAGE_CONTACT_M "
    "(12 m) - and each member is classified by FOURTH.enemy_is_commander (the 1,409-key derived "
    "commander set, unit_class() == 'com' fallback, FAIL CLOSED). The judged set is LOGGED (type + "
    "commander flag + the real distance) once per (unit, marker) and again only when it changes. With "
    "nothing readable in contact the caster's current_target() decides; with neither, the plain in-melee "
    "rule fires and says so. The cast is on SELF through the unit form (the row is self-centred: target "
    "flags all false, range 0); the charge gate holds Arachneruption for its 90 s recharge."
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
assert sum(cnt.values()) == 675, sum(cnt.values())
assert sum(keys.values()) == 721, sum(keys.values())
assert cnt["enemy_ground_melee_infantry"] == 30 and cnt["melee_skip_commanders"] == 2
assert cnt["health_below_15"] == 1 and keys["health_below_15"] == 5

shutil.copy2(V6, V7)
wb = openpyxl.load_workbook(V7)

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
        return 0          # an alternate key of a row already written (Slicing Shards twin)
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
for k in BOMB_GROUND:
    b, real = bound_of(k)
    n += set_impl(k, "enemy_ground_melee_infantry", BOMB_GROUND_TEXT.replace("{BOUND}", str(b)).replace("{REAL}", str(real)))
for k in BOMB_UNIT:
    b, real = bound_of(k)
    n += set_impl(k, "enemy_ground_melee_infantry", BOMB_UNIT_TEXT.replace("{BOUND}", str(b)).replace("{REAL}", str(real)))
for k in SOUL_KEYS + ARACH_KEYS:
    n += set_impl(k, "melee_skip_commanders", SOUL_TEXT)
for k, st in SKIP_KEYS.items():
    rows = row_keys.get(k)
    assert rows is not None, k
    assert len(rows) == 1, (k, rows)
    r = rows[0]
    ws.cell(row=r, column=19, value=st)
    ws.cell(row=r, column=20, value="SKIPPED (round 106)")
    ws.cell(row=r, column=21, value="-")
    ws.cell(row=r, column=22, value=(
        "Not automated: " + ("the ability is an ARMY-BAR ability in the game's own tables "
                             "(army_spec junction, source_type bound/cataclysm) - outside the wheel "
                             "scope rule" if "thorsens" in k else
                             "the ability has no enemy target at all (target_friends / target_enemies / "
                             "target_ground / target_self all false, target_intercept_range 0), so no "
                             "enemy-triggered cast can be issued; it is the same self-centred shape as "
                             "Soulfire")))
    for c in (19, 20, 22):
        ws.cell(row=r, column=c).alignment = WRAP
print("abilities: implemented rows", n, "| skipped rows", len(SKIP_KEYS))

# ---------------------------------------------------------------- Definitions
ds = wb["Definitions"]
merges = []
for m in list(ds.merged_cells.ranges):
    merges.append((str(m), ds.cell(row=m.min_row, column=1).value, ds.cell(row=m.min_row, column=2).value))
for m in list(ds.merged_cells.ranges):
    ds.unmerge_cells(str(m))
ds.cell(row=1, column=1, value="DEFINITIONS - WH3 ability master v7 (%s)" % TODAY)


def find_row(col, pred):
    for r in range(1, ds.max_row + 1):
        v = ds.cell(row=r, column=col).value
        if isinstance(v, str) and pred(v):
            return r
    return None


r = find_row(1, lambda v: v == "IMPLEMENTED")
assert r
ds.cell(row=r, column=2, value="The ability is in the mod's ABILITIES table AND in the wheel (721 rows). The "
                              "trigger column states exactly what the evaluator does.")
r = find_row(1, lambda v: v == "NOT IMPLEMENTED")
assert r
ds.cell(row=r, column=2, value="The ability is not in the mod's ABILITIES table (1,078 rows, of which 420 are "
                              "in the wheel).")

# the two new glossary rows, before TOTAL
tot = find_row(1, lambda v: v.startswith("TOTAL (all"))
assert tot, "TOTAL not found"
NEW = [
    ["melee_skip_commanders", "evaluate_melee_skip_commanders",
     "IN MELEE, unless EVERY enemy it is engaged with is a Lord or Hero: the engagement set is the enemy "
     "enumerator's ALIVE + is_in_melee() units whose edge-to-edge unit_distance to the caster is <= 12 m "
     "(FOURTH.ENGAGE_CONTACT_M), each classified by the 1,409-key commander set (unit_class()=='com' "
     "fallback, FAIL CLOSED); the judged set is LOGGED (type + flag + real distance) once per (unit, "
     "marker) and on change; no enemy readable -> current_target() -> plain in-melee",
     "the OWNER itself (unit form; the rows are self-centred)", 2, 3],
    ["enemy_ground_melee_infantry", "evaluate_enemy_ground_melee_infantry",
     "the CLOSEST enemy inside the ability's own 70% bound that is IN MELEE and IS INFANTRY "
     "(battle_unit:is_infantry() first, unit_class() exact-match inf_mel/inf_mis/inf_spr second, FAIL "
     "CLOSED); the chosen enemy is re-checked immediately before the cast (alive, in melee, still "
     "infantry, in bound)",
     "24 ground keys: the GROUND form on the chosen enemy's position; 6 unit keys: the UNIT form on the "
     "enemy", 30, 31],
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
print("definitions: glossary rows inserted before TOTAL at", tot)

for r in range(1, ds.max_row + 1):
    v = ds.cell(row=r, column=1).value
    if isinstance(v, str) and v.startswith("TOTAL (all"):
        ds.cell(row=r, column=1, value="TOTAL (all 45 evaluators)")
        ds.cell(row=r, column=5, value="675")
        ds.cell(row=r, column=6, value="721")
    if isinstance(v, str) and v.startswith("3. TRIGGER-FAMILY GLOSSARY"):
        ds.cell(row=r, column=1, value="3. TRIGGER-FAMILY GLOSSARY (45 evaluators)")

r = find_row(1, lambda v: v.startswith("Coverage in this workbook"))
if r:
    ds.cell(row=r, column=1, value=(
        "Coverage in this workbook: 258 of the 721 implemented rows carry at least one gate clause in their "
        "Trigger (as implemented) text; rows with neither a multi-use pool nor a wind-up keep the plain 2 s guard."))
r = find_row(1, lambda v: v.startswith("7. FIRING-LAYER GATES"))
if r:
    ds.cell(row=r, column=1, value="7. FIRING-LAYER GATES (rounds 103-106)")

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
IMP = 721
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
    elif lab == "active":
        ns.cell(row=r, column=4, value=546)
        ns.cell(row=r, column=5, value=546 / 926)
    elif lab == "bound":
        ns.cell(row=r, column=4, value=69)
        ns.cell(row=r, column=5, value=69 / 176)
    elif lab == "lord":
        ns.cell(row=r, column=4, value=6)
        ns.cell(row=r, column=5, value=6 / 10)
    elif lab == "Total included":
        ns.cell(row=r, column=4, value=IMP)
ns.cell(row=7, column=1,
        value="Date: 2026-10-17     Rule in force since: 2026-10-17     Inventory: 1,799 active abilities"
              "     (v7: round 106 - THE BOMBARDMENT ROUND: 30 of the 32 approved bombardment abilities on "
              "enemy_ground_melee_infantry + Soulfire (2 keys) and Arachneruption on melee_skip_commanders; "
              "Thorsen's Thunderstorm and Warp Lightning Rod reported, not implemented)")

for r in range(1, ns.max_row + 1):
    v = ns.cell(row=r, column=1).value
    if isinstance(v, str) and v.startswith("Reconciliation:"):
        ns.cell(row=r, column=1, value=(
            "Reconciliation: included 1,141 + excluded 658 = 1,799. Implemented among the included 721 + not "
            "implemented 420 = 1,141. The mod's ABILITIES table is 675 entries / 721 keys (the two Soulfire "
            "keys are ONE entry, the two Slicing Shards keys are ONE entry). The tracker carries 692 "
            "implemented ROWS; 29 implemented keys have no row of their own (28 pre-existing alternate "
            "keys and the Slicing Shards bound twin, each riding a row that names its sibling), so the "
            "tracker's 692 rows and this workbook's 721 implemented keys agree. Round 106 moved 34 keys "
            "from NOT IMPLEMENTED to IMPLEMENTED (687 -> 721) and marked 3 rows SKIPPED (round 106); the in-wheel "
            "count, the exclusions and the carrier families' INCLUDED counts are unchanged."))
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
        value="Trigger families after round 106 - re-counted from the mod (675 entries / 721 keys)")
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
ns.cell(row=r, column=2, value="TOTAL (45 evaluators)").font = Font(bold=True)
ns.cell(row=r, column=3, value=675).font = Font(bold=True)
ns.cell(row=r, column=4, value=721).font = Font(bold=True)
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
cs.cell(row=row, column=2, value="v7")
cs.cell(row=row, column=3, value=(
    "ROUND 106 - THE BOMBARDMENT ROUND (two user-approved families). (1) SOULFIRE + ARACHNERUPTION on the "
    "NEW trigger melee_skip_commanders: fire when the caster is IN MELEE, but SKIP when EVERY enemy it is "
    "engaged with is a Lord or a Hero. The engagement set is the enemy enumerator's ALIVE + is_in_melee() "
    "units whose edge-to-edge unit_distance to the caster is <= 12 m; each member is classified by the "
    "existing 1,409-key commander set (unit_class()=='com' fallback, FAIL CLOSED) and the judged set is "
    "LOGGED (type + flag + real distance), deduped by note text. No enemy readable -> current_target(); "
    "neither -> the plain in-melee rule. TWO entries (Soulfire carries BOTH soulfire keys). (2) 30 OF THE "
    "USER'S 32 BOMBARDMENT ABILITIES on the NEW trigger enemy_ground_melee_infantry: the CLOSEST enemy "
    "inside the ability's own 70% bound that is IN MELEE and IS INFANTRY (battle_unit:is_infantry() first, "
    "unit_class() exact-match inf_mel/inf_mis/inf_spr, FAIL CLOSED). The cast follows each row's own flags: "
    "24 ground-targeted keys place the strike on the enemy's own ground (perform_special_ability_ground), "
    "6 unit-targeted keys cast on the enemy unit. The chosen enemy is re-checked immediately before the "
    "cast. TWO OF THE 32 ARE REPORTED, NOT IMPLEMENTED: Thorsen's Thunderstorm (both keys are army_spec / "
    "ARMY-bar - out of wheel scope) and Warp Lightning Rod (no enemy target at all: flags all false, "
    "range 0). Counts: 643 -> 675 entries, 687 -> 721 keys, 43 -> 45 evaluators. Installed pack md5 "
    "9108e7f685180cbb637ee8b9ef53cf24 (harness 106: 3812 checks / 0 failures)."))
cs.cell(row=row, column=4, value=(
    "the user's two approved bombardment families (Soulfire/Arachneruption skip-Lord/Hero rule; the 32-list "
    "on the closest in-melee infantry); research R1-R4 in docs/WH3_bombardment_research.md; mod + tracker + "
    "this workbook (harness 106). Supersedes v6; v1-v6 are left byte-unchanged."))
for ci in range(1, 5):
    cs.cell(row=row, column=ci).alignment = Alignment(wrap_text=True, vertical="top")
    cs.cell(row=row, column=ci).border = Border(left=thin, right=thin, top=thin, bottom=thin)
cs.row_dimensions[row].height = 240

wb.save(V7)
print("wrote", V7, os.path.getsize(V7), "bytes")
