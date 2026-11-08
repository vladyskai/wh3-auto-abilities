"""Re-open v5 and assert the bookkeeping is consistent. Prints PASS/FAIL per check."""
import collections, csv, hashlib, json, os, sys
import openpyxl

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
DOCS = os.path.join(ROOT, "docs")
V4 = os.path.join(DOCS, "WH3_abilities_master_v4_2026-10-17.xlsx")
V5 = os.path.join(DOCS, "WH3_abilities_master_v5_2026-10-17.xlsx")
T = os.path.expandvars(r"%LOCALAPPDATA%\Temp\wh3")

fails = []


def check(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    if not cond:
        fails.append(msg)


def load(f):
    with open(os.path.join(T, f), encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


spec = {r["key"]: r for r in load("unit_spec_abil.tsv")}

wb4 = openpyxl.load_workbook(V4)
wb5 = openpyxl.load_workbook(V5)

# ---- 1. row count unchanged
r4 = wb4["Abilities"].max_row
r5 = wb5["Abilities"].max_row
check(r4 == r5 == 1800, "Abilities row count unchanged: v4=%d v5=%d (header + 1799)" % (r4, r5))
check(wb5.sheetnames[:4] == ["Abilities", "Numbers", "Changelog", "Definitions"] and "Transforms" in wb5.sheetnames,
      "sheets: %s" % wb5.sheetnames)

ws = wb5["Abilities"]


def keys_of(r):
    return [p.strip() for p in str(ws.cell(row=r, column=3).value or "").split(";") if p.strip()]


rows = {r: keys_of(r) for r in range(2, ws.max_row + 1)}

GROUND = {"wh2_dlc10_item_abilities_star_of_avelorn": 10, "wh3_dlc24_lord_abilities_gulyas": 24}
SELF = {"wh3_main_character_abilities_salyaks_lullaby": 24, "wh3_main_character_abilities_locus_of_fecundity": 38}
ALLY = {"wh2_dlc16_item_abilities_berry_wine": 42, "wh2_dlc16_item_abilities_dreaming_ring_i": 140,
        "wh2_dlc16_item_abilities_dreaming_ring_ii": 140, "wh2_dlc16_item_abilities_dreaming_ring_iii": 140,
        "wh2_dlc16_spell_bound_earth_blood": 140, "wh3_main_spell_bound_earth_blood": 140,
        "wh3_dlc20_spell_bound_fleshy_abundance": 140, "wh2_dlc16_spell_bound_regrowth": 140,
        "wh2_main_spell_bound_radiant_gem_of_hoeth": 140, "wh3_dlc26_spell_bound_trollguts": 140}

# ---- 2. every changed row carries its family + the reach number + health_pct
n = set()
for fam, table in (("ground", GROUND), ("self", SELF), ("ally", ALLY)):
    for k, reach in table.items():
        hits = [r for r, ks in rows.items() if k in ks]
        # Earth Blood's two keys share TWO inventory rows (duplicate rows), every other key one row
        check(1 <= len(hits) <= 2, "%s appears on 1-2 rows (%d)" % (k, len(hits)))
        for r in hits:
            trig = str(ws.cell(row=r, column=21).value)
            txt = str(ws.cell(row=r, column=22).value)
            check(trig == "health_aura_" + fam, "%s row %d trigger family = %s (got %s)" % (k, r, fam, trig))
            check(txt.startswith("health_aura_" + fam), "%s row %d text starts with its family" % (k, r))
            check(("= %d m" % reach) in txt, "%s row %d text carries the reach %d m" % (k, r, reach))
            check("FOURTH.health_pct" in txt, "%s row %d text names FOURTH.health_pct" % (k, r))
            n.add(r)
check(len(n) == 14, "14 rows / 13 entries carry the ally-aware trigger (got %d)" % len(n))

# ---- 3. the 20 owner-only rows
OWN = load("unit_spec_abil.tsv")
names20 = [
    "wh2_dlc11_lord_abilities_ghoul_king_of_ushoran", "wh3_dlc29_hero_abilities_blood_chalice",
    "wh3_dlc26_item_abilities_bugmans_xxxxxx", "wh2_dlc09_item_abilities_hieratic_jar",
    "wh_main_hero_abilities_immortal_will", "wh3_dlc29_spell_bound_invocation_of_nehek",
    "wh2_dlc16_unit_abilities_neuroparasites", "wh2_main_lord_abilities_potion_of_charoi",
    "wh_main_item_abilities_potion_of_healing", "wh_main_item_abilities_regenerating_flesh",
    "wh2_main_item_abilities_skalm", "wh3_main_weapon_abilities_skars_kraken_killer",
    "wh3_cp1_character_abilities_protection_prayer", "wh_pro02_item_abilities_blood_chalice_of_bathori",
    "wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness",
    "wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness_upgraded",
    "wh3_dlc25_item_abilities_necrotic_phylactry", "wh3_main_daemon_head_abilities_pestilent_regeneration",
    "wh3_main_item_abilities_saint_annushkas_finger_bone", "wh_main_item_abilities_scroll_of_power"]
own_rows = 0
for k in names20:
    hits = [r for r, ks in rows.items() if k in ks]
    check(len(hits) == 1, "owner-only %s one row" % k)
    r = hits[0]
    txt = str(ws.cell(row=r, column=22).value)
    check("OWNER-ONLY" in txt, "owner-only %s carries the OWNER-ONLY reason" % k)
    check(str(ws.cell(row=r, column=21).value) == "ushoran_health", "owner-only %s stays ushoran_health" % k)
    own_rows += 1
check(own_rows == 20, "20 owner-only rows")

# ---- 4. Eye of Khorne + Nurgling Tide
eye = [r for r, ks in rows.items() if "wh3_dlc26_lord_abilities_eye_of_khorne" in ks][0]
check("health_pct" in str(ws.cell(row=eye, column=22).value) and "20%" in str(ws.cell(row=eye, column=22).value),
      "Eye of Khorne text names health_pct and the 20% gate")
nt = [r for r, ks in rows.items() if "wh3_main_lord_abilities_nurgling_tide" in ks][0]
ntt = str(ws.cell(row=nt, column=22).value)
check("charge hold 90 s" in ntt and "in-flight hold 5 s" in ntt, "Nurgling Tide carries both gate clauses")

# ---- 5. gates on exactly the rows whose data declares them
gate_rows = 0
bad = []
for r, ks in rows.items():
    if ws.cell(row=r, column=20).value != "IMPLEMENTED":
        continue
    uses = max(float(spec.get(k, {}).get("num_uses") or 0) for k in ks)
    wind = max(float(spec.get(k, {}).get("wind_up_time") or 0) for k in ks)
    txt = str(ws.cell(row=r, column=22).value)
    if uses > 1 or wind > 0:
        gate_rows += 1
        if "GATES (" not in txt:
            bad.append((r, ks[0]))
    else:
        if "GATES (" in txt:
            bad.append((r, ks[0] + " (unexpected)"))
check(not bad, "gate clause exactly on the 225 data-declared rows (bad: %s)" % bad[:5])
check(gate_rows == 225, "225 implemented rows carry a gate (got %d)" % gate_rows)

# ---- 6. Numbers reconciliation against the rows themselves
wsc = wb5["Numbers"]
vals = {}
for r in range(1, wsc.max_row + 1):
    lab = str(wsc.cell(row=r, column=2).value or "")
    if lab in ("Total active abilities (the inventory)", "Excluded - not in the ability wheel",
               "Included - in the ability wheel", "Implemented among the included",
               "Not implemented among the included", "All implemented in the mod (4 + 6)"):
        vals[lab] = wsc.cell(row=r, column=3).value
cnt = collections.Counter()
for r in rows:
    cnt[ws.cell(row=r, column=18).value] += 1
impl = sum(1 for r in rows if ws.cell(row=r, column=20).value == "IMPLEMENTED")
wheel = cnt["IN-WHEEL"]
excl = cnt["EXCLUDED"]
check(wheel == 1141 and excl == 658 and impl == 682, "row counts: wheel=%d excluded=%d implemented=%d" % (wheel, excl, impl))
check(str(vals.get("Included - in the ability wheel")) == "1141", "Numbers included = 1141")
check(str(vals.get("Excluded - not in the ability wheel")) == "658", "Numbers excluded = 658")
check(str(vals.get("Implemented among the included")) == "682", "Numbers implemented = 682")
check(str(vals.get("Not implemented among the included")) == "459", "Numbers not implemented = 459")
check(str(vals.get("Total active abilities (the inventory)")) == "1797", "Numbers inventory = 1797")
check(wheel + excl == 1799 and impl + 459 == 1141, "Numbers arithmetic reconciles (1141+658=1799, 682+459=1141)")

# trigger block totals
tt = None
for r in range(1, wsc.max_row + 1):
    if str(wsc.cell(row=r, column=2).value or "").startswith("TOTAL (42 evaluators)"):
        tt = (wsc.cell(row=r, column=3).value, wsc.cell(row=r, column=4).value)
check(tt == (642, 682), "Numbers trigger block TOTAL = 642 entries / 682 keys (got %s)" % (tt,))

# trigger counts vs the mod's own table
mod = open(os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua"),
           encoding="utf-8").read()
import re
mc = collections.Counter(re.findall(r'trigger\s*=\s*"([a-z0-9_]+)"', mod))
check(sum(mc.values()) == 642, "mod trigger count sums to 642 entries (got %d)" % sum(mc.values()))
check(len(mc) == 42, "mod carries 42 evaluator names (got %d)" % len(mc))

# ---- 7. Definitions
ds = wb5["Definitions"]
dtext = "\n".join(str(ds.cell(row=r, column=c).value or "") for r in range(1, ds.max_row + 1) for c in (1, 2, 5, 6))
check("DEFINITIONS - WH3 ability master v5" in dtext, "Definitions title is v5")
check("TOTAL (all 42 evaluators)" in dtext, "Definitions TOTAL is 42 evaluators")
check("642" in dtext and "682" in dtext, "Definitions TOTAL carries 642 / 682")
check("7. FIRING-LAYER GATES" in dtext and "charge_gate.hold_s" in dtext and "cast_gate.wind_up_s" in dtext,
      "Definitions carries the gates section")
for t in ("health_aura_ground", "health_aura_self", "health_aura_ally"):
    check(t in dtext, "Definitions glossary carries %s" % t)

# ---- 8. Transforms sheet
tr = wb5["Transforms"]
tkeys = [str(tr.cell(row=r, column=3).value or "") for r in range(6, 23)]
check(len([k for k in tkeys if k.startswith("wh")]) == 17, "Transforms sheet lists 17 active transform keys")
check(str(tr.cell(row=1, column=1).value).startswith("TRANSFORM ACTIVE ABILITIES"), "Transforms title")

# ---- 9. v1-v4 unchanged
REF = {
    "WH3_abilities_master_v1_2026-10-17.xlsx": "84526b357c96d6209f085bc4a1178581",
    "WH3_abilities_master_v2_2026-10-17.xlsx": "c8f34afe50c1c93945a225618ea545ae",
    "WH3_abilities_master_v3_2026-10-17.xlsx": "aa3bf8af57a47cfe05af8525e2f840f5",
    "WH3_abilities_master_v4_2026-10-17.xlsx": "33de4f53293148c4d49dcadeed9c9e25",
}
for f, ref in REF.items():
    p = os.path.join(DOCS, f)
    got = hashlib.md5(open(p, "rb").read()).hexdigest()
    check(got == ref, "%s byte-unchanged (%s)" % (f, got[:12]))

print()
print("RESULT:", "ALL PASS" if not fails else "%d FAILURE(S)" % len(fails))
sys.exit(1 if fails else 0)
