#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v82_2026-11-22.xlsx (round 205), re-opened from disk, against v81: v81
byte-unchanged; the same 1,802 data rows; Abilities equal except column 22 of the 27 exact wave rows (v81 text + the
planned sentences; the keys and the cone numbers come from the MOD SOURCE and the game data); Cards, Transforms
unchanged; Numbers equal except the date line and still reconciling; the tracker carries the round; Definitions section
79; one v82 Changelog row with the installed md5. Usage: verify_xlsx_v82.py <v81 md5> <installed pack md5>"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import make_xlsx_v74 as V74  # noqa: E402
import make_xlsx_v82 as M  # noqa: E402

V81_MD5 = sys.argv[1]
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


ok("v81 byte-unchanged (md5 %s)" % V81_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V81_MD5)
plan, exact, cone = M.plan()
want = {k: n for r, k, t, n in plan}
ok("the mod source and the game data: 27 exact waves, 19 growing (%d, %d)" % (len(exact), len(cone)),
   len(exact) == 27 and len(cone) == 19 and set(cone) <= set(exact) and set(want) == set(exact))
a81, a82 = rows(M.SRC, "Abilities"), rows(M.DST, "Abilities")
ok("the same data-row count as v81 (%d)" % (len(a82) - 1), len(a81) == len(a82) == 1803)
changed, bad = set(), []
for i, (x, y) in enumerate(zip(a81, a82), start=1):
    for j, (p, q) in enumerate(zip(x, y), start=1):
        if p != q:
            k = str(y[2]).split(";")[0].strip()
            if j == 22 and want.get(k) == q and q.startswith((p or "").rstrip()):
                changed.add(k)
            else:
                bad.append((i, j))
ok("Abilities: exactly the 27 exact wave rows changed, nothing else (%d rows, %d other cells)" % (len(changed), len(bad)),
   changed == set(exact) and not bad)
by = {str(x[2]).split(";")[0].strip(): x for x in a82[1:]}
sun, ring, conv = (by["wh2_main_weapon_abilities_sunfang"][21], by["wh_main_item_abilities_fiery_ring_of_thori"][21],
                   by["wh2_dlc10_spell_bound_magic_fiery_convocation"][21])
ok("Sunfang reads 0.1 m and 0.25 m per metre, the ring 0.1 m and 0.0833, Fiery Convocation (no growth) has no CONE sentence",
   "from 0.1 m wide at its start by 0.25 m per metre" in sun and "from 0.1 m wide at its start by 0.0833 m per metre" in ring
   and " CONE (round 205)" not in conv and conv.endswith(M.SINGLE))
ok("no semicolon and no em dash in the new sentences", all(";" not in s and "\u2014" not in s for s in (M.SINGLE, M.CONE)))
st = V74.source_types()
tot, exc, inc, n_impl, car, ex = V74.counts(a82[1:], st)
nm = rows(M.DST, "Numbers")
ok("Numbers still reconcile to the rows (1,802 / 687 / 1,115 / 1,035)",
   [nm[r - 1][2] for r in range(10, 14)] == [tot, exc, inc, n_impl] and (tot, exc, inc, n_impl) == (1802, 687, 1115, 1035))
trk = open(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md", encoding="utf-8").read()
ok("the tracker carries the round (section 10.82)", "### 10.82 Round 205" in trk)
for sheet, allow in (("Numbers", {7}), ("Transforms", set()), ("Cards", set())):
    x, y = rows(M.SRC, sheet), rows(M.DST, sheet)
    diff = [i for i, (p, q) in enumerate(zip(x, y), start=1) if p != q]
    ok("%s: same rows, changed only %s (%s)" % (sheet, sorted(allow) or "none", diff), len(x) == len(y) and set(diff) <= allow)
d = rows(M.DST, "Definitions")
ok("Definitions: title v82 and section 79", d[0][0] == "DEFINITIONS - WH3 ability master v82 (2026-11-22)"
   and any(str(r[0]).startswith("79. ROUND 205") for r in d))
h81, h82 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one v82 row with the installed md5", len(h82) == len(h81) + 1 and h82[-1][1] == "v82"
   and PACK_MD5 in h82[-1][2] and "PENDING" not in h82[-1][2] and h82[:-1] == h81)
print("XLSX v82 VERIFY OK" if good else "XLSX v82 VERIFY FAILED")
sys.exit(0 if good else 1)
