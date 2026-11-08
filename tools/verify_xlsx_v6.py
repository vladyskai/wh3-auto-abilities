"""Re-open v6 and assert the bookkeeping is consistent. Prints PASS/FAIL per check."""
import hashlib
import os
import sys

import openpyxl

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
DOCS = os.path.join(ROOT, "docs")
V5 = os.path.join(DOCS, "WH3_abilities_master_v5_2026-10-17.xlsx")
V6 = os.path.join(DOCS, "WH3_abilities_master_v6_2026-10-17.xlsx")
MOD = os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua")

TZ = ["wh2_dlc14_lord_abilities_tzarkan", "wh2_dlc14_lord_abilities_tzarkan_mp",
      "wh2_dlc14_lord_abilities_tzarkan_snikch", "wh2_dlc14_lord_abilities_tzarkan_spite",
      "wh2_dlc14_lord_abilities_tzarkan_spite_mp"]
SKIP = ["wh3_dlc24_lord_abilities_formless_horror", "wh3_dlc24_lord_abilities_formless_horror_changeling",
        "wh3_dlc24_lord_abilities_formless_horror_quest_battle",
        "wh3_dlc24_lord_abilities_formless_horror_quest_battle_changeling_form",
        "wh3_dlc24_lord_abilities_jade_dragon_dragon_form", "wh3_dlc24_lord_abilities_jade_dragon_human_form",
        "wh3_main_lord_abilities_iron_dragon_dragon_form", "wh3_main_lord_abilities_iron_dragon_human_form",
        "wh3_main_lord_abilities_storm_dragon_dragon_form", "wh3_main_lord_abilities_storm_dragon_human_form",
        "wh3_dlc27_unit_abilities_dread_maw_underground", "wh3_dlc27_unit_abilities_dread_maw_surface"]

fails = []


def check(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    if not cond:
        fails.append(msg)


wb5 = openpyxl.load_workbook(V5)
wb6 = openpyxl.load_workbook(V6)
w5, w6 = wb5["Abilities"], wb6["Abilities"]

check(w5.max_row == w6.max_row == 1800, "Abilities row count unchanged: v5=%d v6=%d (header + 1799)" % (w5.max_row, w6.max_row))
check(wb6.sheetnames[:4] == ["Abilities", "Numbers", "Changelog", "Definitions"] and "Transforms" in wb6.sheetnames,
      "sheets: %s" % wb6.sheetnames)

# ---------------------------------------------------------------- 1. the five Tz'arkan rows
rows = {}
for r in range(2, w6.max_row + 1):
    for k in str(w6.cell(row=r, column=3).value or "").split(";"):
        k = k.strip()
        if k:
            rows.setdefault(k, []).append(r)
for k in TZ:
    assert len(rows[k]) == 1, (k, rows[k])
    r = rows[k][0]
    txt = str(w6.cell(row=r, column=22).value or "")
    check(w6.cell(row=r, column=20).value == "IMPLEMENTED", "tzarkan %s is IMPLEMENTED" % k)
    check(w6.cell(row=r, column=21).value == "health_below_15", "tzarkan %s trigger family = health_below_15" % k)
    check(w6.cell(row=r, column=18).value == "IN-WHEEL", "tzarkan %s stays IN-WHEEL" % k)
    for tok in ("FOURTH.health_pct", "BELOW 15", "unit form", "pre-cast re-check", "FOURTH.TZARKAN_PCT",
                "in-flight gate"):
        check(tok in txt, "tzarkan %s text carries %r" % (k, tok))
    check("HealthPercent" in txt and "FRACTION" in txt, "tzarkan %s text warns about the raw fraction field" % k)

# ---------------------------------------------------------------- 2. the twelve skipped rows
for k in SKIP:
    assert len(rows[k]) == 1, (k, rows[k])
    r = rows[k][0]
    check(w6.cell(row=r, column=20).value == "SKIPPED (user decision)", "skipped %s Implementation = SKIPPED (user decision)" % k)
    check(str(w6.cell(row=r, column=19).value) == "skipped (user decision 2026-10-17: no automation wanted)",
          "skipped %s carries the unified status string" % k)
    check(w6.cell(row=r, column=21).value == "-", "skipped %s has no trigger family" % k)
    check("No automation" in str(w6.cell(row=r, column=22).value or ""), "skipped %s text says no automation" % k)
    check(w6.cell(row=r, column=18).value == "IN-WHEEL", "skipped %s stays IN-WHEEL (the wheel rule is untouched)" % k)

# ---------------------------------------------------------------- 3. nothing ELSE changed
target = set()
for k in TZ + SKIP:
    target.add(rows[k][0])
changed = set()
for r in range(1, w6.max_row + 1):
    for c in range(1, 24):
        if w5.cell(row=r, column=c).value != w6.cell(row=r, column=c).value:
            changed.add(r)
check(changed == target, "ONLY the 17 target rows changed in Abilities (changed=%s)" % sorted(changed - target))

# ---------------------------------------------------------------- 4. Definitions
ds = wb6["Definitions"]
dtext = "\n".join(str(ds.cell(row=r, column=c).value or "") for r in range(1, ds.max_row + 1) for c in (1, 2, 5, 6))
check("DEFINITIONS - WH3 ability master v6" in dtext, "Definitions title is v6")
check("SKIPPED (user decision)" in dtext, "Definitions vocabulary carries SKIPPED (user decision)")
check("health_below_15" in dtext and "evaluate_tzarkan_low_health" in dtext, "Definitions glossary carries health_below_15")
check("TOTAL (all 43 evaluators)" in dtext, "Definitions TOTAL is 43 evaluators")
check("TOTAL (all 42 evaluators)" not in dtext, "the old 42-evaluator TOTAL is gone from Definitions")
check("643" in dtext and "687" in dtext, "Definitions TOTAL carries 643 / 687")
check("3. TRIGGER-FAMILY GLOSSARY (43 evaluators)" in dtext, "glossary header says 43 evaluators")

# ---------------------------------------------------------------- 5. Numbers
ns = wb6["Numbers"]
vals = {}
for r in range(1, ns.max_row + 1):
    lab = str(ns.cell(row=r, column=2).value or "")
    vals[lab] = ns.cell(row=r, column=3).value
check(vals.get("Total active abilities (the inventory)") == 1797, "Numbers inventory = 1797")
check(vals.get("Excluded - not in the ability wheel") == 658, "Numbers excluded = 658")
check(vals.get("Included - in the ability wheel") == 1141, "Numbers included = 1141")
check(vals.get("Implemented among the included") == 687, "Numbers implemented = 687")
check(vals.get("Not implemented among the included") == 454, "Numbers not implemented = 454")
check(str(vals.get("All implemented in the mod (4 + 6)")) == "687", "Numbers all-implemented = 687")
tot = None
for r in range(1, ns.max_row + 1):
    if str(ns.cell(row=r, column=2).value or "").startswith("TOTAL (43 evaluators)"):
        tot = (ns.cell(row=r, column=3).value, ns.cell(row=r, column=4).value)
check(tot == (643, 687), "Numbers trigger block TOTAL = 643 entries / 687 keys (got %s)" % (tot,))
hdr = None
for r in range(1, ns.max_row + 1):
    if str(ns.cell(row=r, column=1).value or "").startswith("Trigger families after round 105"):
        hdr = r
        break
check(hdr is not None, "Numbers has the round-105 trigger-family header")
trig_rows = []
if hdr:
    for r in range(hdr, ns.max_row + 1):
        if str(ns.cell(row=r, column=2).value or "").startswith("TOTAL (43 evaluators)"):
            break
        if isinstance(ns.cell(row=r, column=1).value, int) and isinstance(ns.cell(row=r, column=2).value, str):
            trig_rows.append(r)
check(len(trig_rows) == 43, "Numbers trigger block lists 43 evaluators (got %d)" % len(trig_rows))
check(sum(ns.cell(row=r, column=3).value for r in trig_rows) == 643,
      "Numbers trigger entries sum to 643 (got %s)" % sum(ns.cell(row=r, column=3).value for r in trig_rows))
check(sum(ns.cell(row=r, column=4).value for r in trig_rows) == 687,
      "Numbers trigger keys sum to 687 (got %s)" % sum(ns.cell(row=r, column=4).value for r in trig_rows))

# ---------------------------------------------------------------- 6. Changelog
cs = wb6["Changelog"]
v6row = [r for r in range(1, cs.max_row + 1) if cs.cell(row=r, column=2).value == "v6"]
check(len(v6row) == 1, "Changelog has one v6 row")
if v6row:
    ctext = " ".join(str(cs.cell(row=v6row[0], column=c).value or "") for c in (3, 4))
    check("TZ'ARKAN" in ctext and "health_below_15" in ctext, "v6 changelog names Tz'arkan and the new trigger")
    check("Formless Horror" in ctext and "SKIPPED" in ctext, "v6 changelog names the skipped transforms")
    check("a8fea1b2ee6292e5c07ada2c621fa900" in ctext, "v6 changelog carries the installed md5")

# ---------------------------------------------------------------- 7. Transforms sheet
tr = wb6["Transforms"]
impl = skip = 0
for r in range(6, 23):
    k = str(tr.cell(row=r, column=3).value or "")
    h = str(tr.cell(row=r, column=8).value or "")
    if k in TZ:
        impl += 1
        check(h.startswith("IMPLEMENTED"), "Transforms %s marked IMPLEMENTED" % k)
    elif k in SKIP:
        skip += 1
        check(h == "SKIPPED (user decision)", "Transforms %s marked SKIPPED (user decision)" % k)
check(impl == 5 and skip == 12, "Transforms sheet: 5 implemented / 12 skipped (got %d / %d)" % (impl, skip))

# ---------------------------------------------------------------- 8. the mod itself
mod = open(MOD, encoding="utf-8").read()
import re
mc = re.findall(r'trigger\s*=\s*"([a-z0-9_]+)"', mod)
check(len(mc) == 643, "mod trigger count is 643 entries (got %d)" % len(mc))
check(len(set(mc)) == 43, "mod carries 43 evaluator names (got %d)" % len(set(mc)))
for k in SKIP:
    check('"%s"' % k not in mod, "skipped key %s is NOT in the mod" % k)

# ---------------------------------------------------------------- 9. v1-v5 byte-unchanged
REF = {
    "WH3_abilities_master_v1_2026-10-17.xlsx": "84526b357c96d6209f085bc4a1178581",
    "WH3_abilities_master_v2_2026-10-17.xlsx": "c8f34afe50c1c93945a225618ea545ae",
    "WH3_abilities_master_v3_2026-10-17.xlsx": "aa3bf8af57a47cfe05af8525e2f840f5",
    "WH3_abilities_master_v4_2026-10-17.xlsx": "33de4f53293148c4d49dcadeed9c9e25",
    "WH3_abilities_master_v5_2026-10-17.xlsx": "73582279d138f5d903cffc7df95aae10",
}
md5s = {}
for f in REF:
    p = os.path.join(DOCS, f)
    md5s[f] = hashlib.md5(open(p, "rb").read()).hexdigest()
    print("      %s  %s" % (md5s[f], f))
check(len(md5s) == 5, "all five earlier workbooks are present")
for f, ref in REF.items():
    if ref:
        check(md5s[f] == ref, "%s is byte-unchanged (%s)" % (f, md5s[f][:12]))

print()
print("RESULT:", "ALL PASS" if not fails else "%d FAILURE(S)" % len(fails))
sys.exit(1 if fails else 0)
