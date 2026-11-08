#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v19_2026-10-20.xlsx from disk (no in-memory state).

Independent re-read: every number this round claims is asserted here, plus the
join of the mod's 742 implemented keys against the sheet's key column and the
hard gate against an army-bar row reading IN-WHEEL.

Exit 0 = all checks pass; exit 1 = at least one failed (printed).
"""
import collections
import sys

import openpyxl

sys.path.insert(0, r"C:\Users\vlady\Desktop\WH3_mod\tools")
import build_ability_database as bd

XLSX = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v19_2026-10-20.xlsx"
MISS = "wh3_main_spell_slaanesh_slicing_shards_bound"
TH = ["wh3_dlc20_cataclysm_bound_thorsens_thunderstorm",
      "wh3_dlc27_cataclysm_bound_thorsens_thunderstorm"]
ARMY_TOKENS = ("army_spec", "army-bar", "army bar", "army ability", "campaign-side junction")
CORRECTION = ("wheel status corrected in round 120: army-bar abilities are outside the wheel by the "
              "user's own rule")

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


wb = openpyxl.load_workbook(XLSX, data_only=True)
ws = wb["Abilities"]
rows = [tuple(ws.cell(row=r, column=c).value for c in range(1, 24))
        for r in range(2, ws.max_row + 1)]
N = len(rows)

# ------------------------------------------------------------------ 1. shape
check(N == 1800, "1: %d ability rows, expected 1,800" % N)
check([r[0] for r in rows] == list(range(1, N + 1)), "1: the Item # column is not 1..1800 in order")
st = collections.Counter(str(r[17]) for r in rows)
check(st == {"IN-WHEEL": 1140, "EXCLUDED": 660}, "1: status counts %s" % dict(st))
impl_rows = [r for r in rows if str(r[19]) == "IMPLEMENTED"]
check(len(impl_rows) == 742, "1: %d implemented rows, expected 742" % len(impl_rows))

keys = [k.strip() for r in rows for k in str(r[2] or "").split(";") if k.strip()]
multi = sum(1 for r in rows if len([k for k in str(r[2] or "").split(";") if k.strip()]) > 1)
check(len(set(keys)) == 1800,
      "1: %d DISTINCT keys across %d rows" % (len(set(keys)), N))
check((len(keys), multi) == (1868, 46),
      "1: %d key strings over %d rows that name more than one key (expected 1,868 / 46)"
      % (len(keys), multi))
impl_keys = set(k.strip() for r in impl_rows for k in str(r[2] or "").split(";") if k.strip())
check(len(impl_keys) == 742, "1: implemented rows carry %d distinct keys" % len(impl_keys))

# ------------------------------------------------------------------ 2. the two corrected rows
for k in TH:
    hit = [r for r in rows if k in [x.strip() for x in str(r[2]).split(";")]]
    check(len(hit) == 1, "2: `%s` appears on %d rows" % (k, len(hit)))
    r = hit[0]
    check(str(r[17]) == "EXCLUDED", "2: `%s` still reads %s" % (k, r[17]))
    check("army_spec" in str(r[18]), "2: `%s` lost its original army_spec reason" % k)
    check(CORRECTION in str(r[18]), "2: `%s` does not carry the round-120 correction text" % k)
    check(str(r[19]) == "SKIPPED (round 106)", "2: `%s` implementation is %s" % (k, r[19]))
    check(str(r[20]) == "-", "2: `%s` still names a trigger family" % k)

# ------------------------------------------------------------------ 3. the added row
hit = [r for r in rows if [x.strip() for x in str(r[2]).split(";")] == [MISS]]
check(len(hit) == 1, "3: the added row is not there exactly once")
if hit:
    r = hit[0]
    check(str(r[17]) == "IN-WHEEL", "3: added row status %s" % r[17])
    check(str(r[19]) == "IMPLEMENTED", "3: added row implementation %s" % r[19])
    check(str(r[20]) == "enemy_ground_melee_infantry", "3: added row family %s" % r[20])
    check(str(r[1]) == "Slicing Shards", "3: added row name %s" % r[1])
    check(str(r[4]) == "1 use", "3: added row uses %s" % r[4])
    check(str(r[12]) == "0 s (no cooldown)", "3: added row cooldown %s" % r[12])
    check("70%" in str(r[21]) and "INFANTRY" in str(r[21]),
          "3: added row trigger text is not the shipped enemy_ground_melee_infantry rule")
    twin = [x for x in rows if str(x[2]) == "wh3_dlc20_spell_bound_slicing_shards"]
    check(len(twin) == 1 and str(twin[0][21]) == str(r[21]),
          "3: the added row's trigger text differs from its shipped twin's")

# ------------------------------------------------------------------ 4. the join audit
entries, consts, tips = bd.mod_entries()
mod_keys = set(k for e in entries for k in e["keys"])
sheet_keys = set(keys)
missing = sorted(mod_keys - sheet_keys)
extra_impl = sorted(impl_keys - mod_keys)
check(len(mod_keys) == 742 and len(entries) == 689,
      "4: the mod parses %d entries / %d keys" % (len(entries), len(mod_keys)))
check(not missing, "4: implemented keys with NO inventory row: %s" % missing)
check(not extra_impl, "4: rows marked IMPLEMENTED whose keys are not in the mod: %s" % extra_impl)
check(len(mod_keys & sheet_keys) == 742,
      "4: only %d of the mod's keys matched the sheet" % len(mod_keys & sheet_keys))

# ------------------------------------------------------------------ 5. the hard gate
bad = [r for r in rows if str(r[17]) == "IN-WHEEL"
       and any(t in str(r[18]).lower() for t in ARMY_TOKENS)]
check(not bad, "5: army-bar rows still reading IN-WHEEL: %s"
      % [(r[0], r[2]) for r in bad])
for r in rows:
    if str(r[17]) == "IN-WHEEL":
        check(str(r[18]).startswith(("carrier family:", "skipped ")),
              "5: IN-WHEEL row %s has an unexplained reason: %s" % (r[0], str(r[18])[:80]))
    else:
        check(not str(r[20]).startswith(("enemy_", "ally_", "melee", "charge", "wavering", "health",
                                        "air_drop", "ushoran", "glorious", "tired", "blood",
                                        "eat_da", "verminking", "barrier", "metallurgy", "self_")),
              "5: EXCLUDED row %s names a trigger family (%s)" % (r[0], r[20]))

# ------------------------------------------------------------------ 6. the Numbers sheet
n = wb["Numbers"]
cell = lambda r, c: n.cell(row=r, column=c).value
check(cell(10, 3) == 1800, "6: inventory cell %s" % cell(10, 3))
check(cell(11, 3) == 660, "6: excluded cell %s" % cell(11, 3))
check(cell(12, 3) == 1140, "6: included cell %s" % cell(12, 3))
check(cell(13, 3) == 742, "6: implemented cell %s" % cell(13, 3))
check(cell(14, 3) == 398, "6: not-implemented-included cell %s" % cell(14, 3))
check(cell(16, 3) == 742, "6: all-implemented cell %s" % cell(16, 3))
fam_inc = [cell(r, 3) for r in range(20, 28)]
fam_imp = [cell(r, 4) for r in range(20, 28)]
check(sum(fam_inc) == cell(28, 3) == 1140,
      "6: the family block's included column sums to %s against a %s total"
      % (sum(fam_inc), cell(28, 3)))
check(sum(fam_imp) == cell(28, 4) == 742,
      "6: the family block's implemented column sums to %s against a %s total"
      % (sum(fam_imp), cell(28, 4)))
exc = [cell(r, 3) for r in range(32, 38)]
check(sum(exc) == cell(38, 3) == 660,
      "6: the exclusion block sums to %s against a %s total" % (sum(exc), cell(38, 3)))
check("1,140" in str(cell(7, 1)) and "1,800" in str(cell(7, 1)),
      "6: the date line does not carry the v19 figures")
check("ROW-LEVEL" in str(cell(18, 1)),
      "6: the family block is not labelled as a row-level count")
check("17 further rows" in str(cell(101, 1)) or "17" in str(cell(101, 1)),
      "6: the reconciliation does not name the 17 residual army_spec rows")

# ------------------------------------------------------------------ 7. bookkeeping
check(ws.auto_filter.ref == "A1:W%d" % ws.max_row,
      "7: the autofilter stops at %s while the sheet ends at row %d"
      % (ws.auto_filter.ref, ws.max_row))
d = wb["Definitions"]
check(str(d.cell(row=1, column=1).value).startswith("DEFINITIONS - WH3 ability master v19"),
      "7: the Definitions title is not v19")
check("16. ROUND 120" in str(d.cell(row=d.max_row - 20, column=1).value or "") or
      any("16. ROUND 120" in str(d.cell(row=r, column=1).value or "") for r in range(1, d.max_row + 1)),
      "7: Definitions section 16 is missing")
ch = wb["Changelog"]
check(str(ch.cell(row=ch.max_row, column=2).value) == "v19",
      "7: the last changelog row is not v19")

if fails:
    print("XLSX v19 VERIFY: %d FAILURE(S)" % len(fails))
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("XLSX v19 VERIFY OK")
print("  rows 1,800 = 1,140 IN-WHEEL + 660 EXCLUDED; 742 implemented rows / 742 implemented keys")
print("  join: mod %d entries / %d keys -> %d matched, 0 unmatched" % (len(entries), len(mod_keys),
                                                                     len(mod_keys & sheet_keys)))
print("  corrected rows: %s (both EXCLUDED, reason kept + round-120 note)" % ", ".join(TH))
print("  added row: %s (IN-WHEEL, IMPLEMENTED, enemy_ground_melee_infantry)" % MISS)
print("  Numbers: family block sums 1,140 / 742 and the exclusion block 660 - both tie")
