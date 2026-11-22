#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v80_2026-11-22.xlsx (round 203), re-opened from disk, against v79: v79
byte-unchanged; the same 1,802 data rows; Abilities equal except column 22 of the 30 enemy_wave rows (v79 text + the
FREE AIM sentence; the keys are read from the MOD SOURCE); Cards and Transforms unchanged; Numbers equal except the
date line and still reconciling to the rows and the tracker; Definitions section 77; one v80 Changelog row with the
installed md5. Usage: verify_xlsx_v80.py <v79 md5> <installed pack md5>"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402
import make_xlsx_v74 as V74  # noqa: E402
import make_xlsx_v80 as M  # noqa: E402

V79_MD5 = sys.argv[1]
PACK_MD5 = sys.argv[2]
good = True


def ok(name, cond):
    global good
    print(("OK   " if cond else "FAIL ") + name)
    good = good and bool(cond)


def rows(path, sheet):
    wb = openpyxl.load_workbook(path, read_only=True)
    out = [list(r) for r in wb[sheet].iter_rows(values_only=True)]
    wb.close()
    return out


ok("v79 byte-unchanged (md5 %s)" % V79_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V79_MD5)
entries, _, _ = bd.mod_entries()
wave = {k for e in entries if e["trigger"] == "enemy_wave" for k in e["keys"]}
ok("the mod source has 30 enemy_wave keys (%d)" % len(wave), len(wave) == 30)
a79, a80 = rows(M.SRC, "Abilities"), rows(M.DST, "Abilities")
ok("the same data-row count as v79 (%d)" % (len(a80) - 1), len(a79) == len(a80) == 1803)
changed, bad = set(), []
for i, (x, y) in enumerate(zip(a79, a80), start=1):
    for j, (p, q) in enumerate(zip(x, y), start=1):
        if p != q:
            k = str(y[2]).split(";")[0].strip()
            if j == 22 and k in wave and q == (p or "").rstrip() + M.AIM:
                changed.add(k)
            else:
                bad.append((i, j))
ok("Abilities: exactly the 30 wave rows gained the FREE AIM sentence, nothing else changed (%d rows, %d other cells)"
   % (len(changed), len(bad)), changed == wave and not bad)
by = {str(x[2]).split(";")[0].strip(): x for x in a80[1:]}
ok("the Fiery Ring of Thori carries the sentence", by["wh_main_item_abilities_fiery_ring_of_thori"][21].endswith(M.AIM))
ok("the cones and the charge waves do not carry it",
   all("FREE AIM" not in str(by[k][21]) for e in entries if e["trigger"] in ("enemy_cone", "enemy_wave_charge")
       for k in e["keys"]))
ok("no semicolon and no em dash in the new sentence", ";" not in M.AIM and "\u2014" not in M.AIM)
st = V74.source_types()
tot, exc, inc, n_impl, car, ex = V74.counts(a80[1:], st)
nm = rows(M.DST, "Numbers")
ok("Numbers still reconcile to the rows (1,802 / 687 / 1,115 / 1,035)",
   [nm[r - 1][2] for r in range(10, 14)] == [tot, exc, inc, n_impl] and (tot, exc, inc, n_impl) == (1802, 687, 1115, 1035)
   and nm[184][2] == len(entries) == 982 and nm[184][3] == 1035)
trk = open(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md", encoding="utf-8").read()
ok("the tracker carries the round (section 10.80)", "### 10.80 Round 203" in trk)
for sheet, allow in (("Numbers", {7}), ("Transforms", set()), ("Cards", set())):
    x, y = rows(M.SRC, sheet), rows(M.DST, sheet)
    diff = [i for i, (p, q) in enumerate(zip(x, y), start=1) if p != q]
    ok("%s: same rows, changed only %s (%s)" % (sheet, sorted(allow) or "none", diff), len(x) == len(y) and set(diff) <= allow)
d = rows(M.DST, "Definitions")
ok("Definitions: title v80 and section 77", d[0][0] == "DEFINITIONS - WH3 ability master v80 (2026-11-22)"
   and any(str(r[0]).startswith("77. ROUND 203") for r in d))
h79, h80 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one v80 row with the installed md5", len(h80) == len(h79) + 1 and h80[-1][1] == "v80"
   and PACK_MD5 in h80[-1][2] and "PENDING" not in h80[-1][2] and h80[:-1] == h79)
print("XLSX v80 VERIFY OK" if good else "XLSX v80 VERIFY FAILED")
sys.exit(0 if good else 1)
