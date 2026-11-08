#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v20_2026-10-20.xlsx from disk (no in-memory state).

Independent re-read of everything round 121 claims:
  A. shape and the re-derived counts (1,800 = 1,123 + 677; 738 implemented);
  B. all 17 army-bar rows EXCLUDED with the ruling reason, the 4 removed ones
     marked REMOVED and stripped of family/trigger;
  C. the DATA gate: no IN-WHEEL row carries an army_spec key (and none carries
     army-bar text);
  D. the join: mod 687 entries / 738 keys <-> sheet 738 implemented keys, zero
     unmatched in either direction, and 0 army_spec keys in the mod;
  E. the Numbers sheet: every block re-derived and tying, including the 45-family
     trigger table;
  F. bookkeeping: autofilter, Definitions v20 + section 17, Changelog v20.

Exit 0 = all checks pass; exit 1 = at least one failed (printed).
"""
import collections
import sys

import openpyxl

sys.path.insert(0, r"C:\Users\vlady\Desktop\WH3_mod\tools")
import build_ability_database as bd

XLSX = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v20_2026-10-20.xlsx"
ARMY_SPEC = r"C:\Users\vlady\AppData\Local\Temp\wh3\army_spec.tsv"

RULING_REASON = ("excluded (army-bar ability - army_spec junction - not in the battle ability "
                 "wheel, so it can never be cast; user ruling round 121)")
REMOVED_IMPL = "REMOVED (army-bar: not in the battle wheel, cannot be cast)"
ARMY_TOKENS = ("army_spec", "army-bar", "army bar", "army ability", "campaign-side junction")

EXPECTED = [
    "wh2_dlc15_character_abilities_wardens_cage",
    "wh3_dlc20_cataclysm_bound_ashes_and_dust",
    "wh3_dlc20_cataclysm_bound_dance_of_despair",
    "wh3_dlc20_cataclysm_bound_gehennas_golden_globe",
    "wh3_dlc20_cataclysm_bound_magma_storm",
    "wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment",
    "wh3_dlc20_cataclysm_bound_storm_of_renewal",
    "wh3_dlc20_cataclysm_bound_time_amok",
    "wh3_dlc27_cataclysm_bound_ashes_and_dust",
    "wh3_dlc27_cataclysm_bound_dance_of_despair",
    "wh3_dlc27_cataclysm_bound_gehennas_golden_globe",
    "wh3_dlc27_cataclysm_bound_magma_storm",
    "wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment",
    "wh3_dlc27_cataclysm_bound_storm_of_renewal",
    "wh3_dlc27_cataclysm_bound_time_amok",
    "wh3_dlc29_army_abilities_pestilential_bombardment",
    "wh3_main_cataclysm_khorne_greater_gate_of_khorne",
]
REMOVED_ROWS_KEYS = ["wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment",
                     "wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment",
                     "wh3_main_cataclysm_khorne_greater_gate_of_khorne",
                     "wh2_dlc15_character_abilities_wardens_cage"]

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


army = set()
with open(ARMY_SPEC, encoding="utf-8", errors="replace") as f:
    f.readline()
    for line in f:
        if line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        if c and c[0].strip():
            army.add(c[0].strip())

wb = openpyxl.load_workbook(XLSX, data_only=True)
ws = wb["Abilities"]
rows = [tuple(ws.cell(row=r, column=c).value for c in range(1, 24))
        for r in range(2, ws.max_row + 1)]
N = len(rows)
ident = lambda r: [x.strip() for x in str(r[2] or "").split(";") if x.strip()]

# ------------------------------------------------------------------ A. shape
check(N == 1800, "A1: %d ability rows, expected 1,800" % N)
check([r[0] for r in rows] == list(range(1, N + 1)), "A2: the Item # column is not 1..1800 in order")
st = collections.Counter(str(r[17]) for r in rows)
check(st == {"IN-WHEEL": 1123, "EXCLUDED": 677}, "A3: status counts %s" % dict(st))
impl_rows = [r for r in rows if str(r[19]) == "IMPLEMENTED"]
check(len(impl_rows) == 738, "A4: %d implemented rows, expected 738" % len(impl_rows))
removed_rows = [r for r in rows if str(r[19]) == REMOVED_IMPL]
check(len(removed_rows) == 4, "A5: %d rows read `%s`, expected 4" % (len(removed_rows), REMOVED_IMPL))
keys = [k for r in rows for k in ident(r)]
check(len(set(keys)) == 1800, "A6: %d DISTINCT keys across %d rows" % (len(set(keys)), N))
impl_keys = set(k for r in impl_rows for k in ident(r))
check(len(impl_keys) == 738, "A7: implemented rows carry %d distinct keys, expected 738" % len(impl_keys))

# ------------------------------------------------------------------ B. the 17 rows
hit = {}
for r in rows:
    for k in ident(r):
        if k in EXPECTED:
            hit.setdefault(k, []).append(r)
check(sorted(hit) == sorted(EXPECTED), "B1: the 17 army-bar keys are not on the sheet exactly: %s"
      % sorted(set(EXPECTED) ^ set(hit)))
for k in EXPECTED:
    for r in hit.get(k, []):
        check(str(r[17]) == "EXCLUDED", "B2: `%s` (item %s) still reads %s" % (k, r[0], r[17]))
        check(str(r[18]) == RULING_REASON,
              "B3: `%s` (item %s) reason is not the ruling text: %s" % (k, r[0], str(r[18])[:90]))
for k in REMOVED_ROWS_KEYS:
    rs = hit[k]
    check(all(str(r[19]) == REMOVED_IMPL for r in rs),
          "B4: `%s` is not marked REMOVED (%s)" % (k, [r[19] for r in rs]))
    check(all(str(r[20]) == "-" and str(r[21]) == "-" for r in rs),
          "B5: `%s` still names a family/trigger (%s / %s)"
          % (k, [r[20] for r in rs], [str(r[21])[:40] for r in rs]))
for k in EXPECTED:
    if k in REMOVED_ROWS_KEYS:
        continue
    check(all(str(r[19]) != "IMPLEMENTED" for r in hit[k]),
          "B6: `%s` is still marked IMPLEMENTED but its key left the mod" % k)

# ------------------------------------------------------------------ C. the gates
bad_data = [(r[0], ident(r)) for r in rows if str(r[17]) == "IN-WHEEL" and any(k in army for k in ident(r))]
check(not bad_data, "C1: IN-WHEEL rows carrying an army_spec key: %s" % bad_data)
bad_text = [(r[0], ident(r)[:1]) for r in rows if str(r[17]) == "IN-WHEEL"
            and any(t in (str(r[18]) + " " + str(r[19])).lower() for t in ARMY_TOKENS)]
check(not bad_text, "C2: IN-WHEEL rows whose text says army-bar: %s" % bad_text)
for r in rows:
    if str(r[17]) == "IN-WHEEL":
        check(str(r[18]).startswith(("carrier family:", "skipped ")),
              "C3: IN-WHEEL row %s has an unexplained reason: %s" % (r[0], str(r[18])[:80]))

# ------------------------------------------------------------------ D. the join
entries, consts, tips = bd.mod_entries()
mod_keys = set(k for e in entries for k in e["keys"])
check(len(mod_keys) == 738 and len(entries) == 687,
      "D1: the mod parses %d entries / %d keys, expected 687 / 738" % (len(entries), len(mod_keys)))
check(not (mod_keys & army), "D2: army_spec keys in the mod: %s" % sorted(mod_keys & army))
check(not (mod_keys - set(keys)), "D3: mod keys with NO inventory row: %s"
      % sorted(mod_keys - set(keys))[:5])
check(impl_keys == mod_keys,
      "D4: implemented rows and the mod's keys differ: rows-only %s, mod-only %s"
      % (sorted(impl_keys - mod_keys)[:5], sorted(mod_keys - impl_keys)[:5]))

# ------------------------------------------------------------------ E. Numbers
n = wb["Numbers"]
cell = lambda r, c: n.cell(row=r, column=c).value
check(cell(10, 3) == 1800, "E1: inventory cell %s" % cell(10, 3))
check(cell(11, 3) == 677, "E2: excluded cell %s, expected 677" % cell(11, 3))
check(cell(12, 3) == 1123, "E3: included cell %s, expected 1123" % cell(12, 3))
check(cell(13, 3) == 738, "E4: implemented cell %s, expected 738" % cell(13, 3))
check(cell(14, 3) == 385, "E5: not-implemented-included cell %s, expected 385" % cell(14, 3))
check(cell(16, 3) == 738, "E6: all-implemented cell %s, expected 738" % cell(16, 3))
check(cell(11, 3) + cell(12, 3) == cell(10, 3), "E7: excluded + included != the inventory")
check(cell(13, 3) + cell(14, 3) == cell(12, 3), "E8: implemented + not-implemented != included")
fam_inc = [cell(r, 3) for r in range(20, 28)]
fam_imp = [cell(r, 4) for r in range(20, 28)]
check(sum(fam_inc) == cell(28, 3) == 1123,
      "E9: the family block's included column sums to %s against a %s total"
      % (sum(fam_inc), cell(28, 3)))
check(sum(fam_imp) == cell(28, 4) == 738,
      "E10: the family block's implemented column sums to %s against a %s total"
      % (sum(fam_imp), cell(28, 4)))
exc = [cell(r, 3) for r in range(32, 38)]
check(sum(exc) == cell(38, 3) == 677,
      "E11: the exclusion block sums to %s against a %s total" % (sum(exc), cell(38, 3)))
check(exc[1] == 223, "E12: the army-bar exclusion row is %s, expected 223" % exc[1])
check("1,123" in str(cell(7, 1)) and "677" in str(cell(7, 1)) and "1,800" in str(cell(7, 1)),
      "E13: the date line does not carry the v20 figures")
check("ALL ARMY ABILITIES\" makes no sense" in str(cell(7, 1)).replace("'", '"')
      or "ALL ARMY ABILITIES" in str(cell(7, 1)),
      "E14: the date line does not quote the ruling")
check("ROW-LEVEL" in str(cell(18, 1)), "E15: the family block is not labelled as a row-level count")
trig_ent = [cell(r, 3) for r in range(44, 89)]
trig_key = [cell(r, 4) for r in range(44, 89)]
check(len(trig_ent) == 45 and all(isinstance(x, int) for x in trig_ent),
      "E16: the trigger-family table is not 45 rows: %s" % trig_ent[:5])
check(sum(trig_ent) == cell(89, 3) == 687,
      "E17: the trigger-family entries sum to %s against %s" % (sum(trig_ent), cell(89, 3)))
check(sum(trig_key) == cell(89, 4) == 738,
      "E18: the trigger-family keys sum to %s against %s" % (sum(trig_key), cell(89, 4)))
names = [str(cell(r, 2)) for r in range(44, 89)]
check("ally_infinite_buff" not in names, "E19: the removed ally_infinite_buff family is still listed")
check("enemy_engaged_or_shot" in names and trig_ent[names.index("enemy_engaged_or_shot")] == 85,
      "E20: enemy_engaged_or_shot is not 85 entries")
check(any("ROUND 121" in str(cell(r, 1)) for r in range(100, 130)),
      "E21: the Numbers sheet has no round-121 block")

# ------------------------------------------------------------------ F. bookkeeping
check(ws.auto_filter.ref == "A1:W%d" % ws.max_row,
      "F1: the autofilter stops at %s while the sheet ends at row %d" % (ws.auto_filter.ref, ws.max_row))
d = wb["Definitions"]
check(str(d.cell(row=1, column=1).value).startswith("DEFINITIONS - WH3 ability master v20"),
      "F2: the Definitions title is not v20")
check(any("17. ROUND 121" in str(d.cell(row=r, column=1).value or "") for r in range(1, d.max_row + 1)),
      "F3: Definitions section 17 is missing")
ch = wb["Changelog"]
check(str(ch.cell(row=ch.max_row, column=2).value) == "v20", "F4: the last changelog row is not v20")
check("ALL ARMY ABILITIES PLEASE EXCLUDE" in str(ch.cell(row=ch.max_row, column=3).value),
      "F5: the v20 changelog does not quote the ruling")
check("17" in str(ch.cell(row=ch.max_row, column=3).value)
      and "687" in str(ch.cell(row=ch.max_row, column=3).value),
      "F6: the v20 changelog does not state the 17 rows / the 687-entry table")

if fails:
    print("XLSX v20 VERIFY: %d FAILURE(S)" % len(fails))
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("XLSX v20 VERIFY OK")
print("  rows 1,800 = 1,123 IN-WHEEL + 677 EXCLUDED; 738 implemented rows / 738 implemented keys")
print("  17 army-bar rows: %d EXCLUDED with the ruling reason, %d marked REMOVED"
      % (len(set(k for k in hit)), len(removed_rows)))
print("  join: mod %d entries / %d keys -> %d implemented rows matched, 0 unmatched, 0 army_spec keys"
      % (len(entries), len(mod_keys), len(impl_keys)))
print("  Numbers: family block 1,123 / 738, exclusion block 677 (army-bar 223), trigger table 687 / 738")
