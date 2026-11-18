#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v55_2026-11-18.xlsx (round 172; cloned from the v54 verifier) from disk: the v38 verifier's structural checks
re-pointed at v50 (counts unchanged since round 164: 1,003 implemented, 36 skipped, 946 entries, 95 families; v1-v49
byte-unchanged, 94 files), then the round-166 checks: the Cards sheet holds 946 rows equal to the harness-165 CARD
lines, every card short and whole ('Fires ...', at most 160 characters, no token, bracket, name or em dash), the 22
round-165 notes are still there, and every round-166 wanderer key carries its note."""
import os
import runpy
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

T = os.path.dirname(os.path.abspath(__file__))
V38 = open(os.path.join(T, "verify_xlsx_v38.py"), encoding="utf-8").read()
V49 = open(os.path.join(T, "verify_xlsx_v49.py"), encoding="utf-8").read()
# the v49 verifier's patch list (v38 -> v49), its targets re-pointed at v50
R49 = eval(V49.split("\nR = ", 1)[1].split("\nfor a, b, n in R:", 1)[0])
SUB = [("v49_2026-11-17", "v55_2026-11-18"), ("v48_2026-11-16", "v54_2026-11-17"), ('"melee_unwavering": 299', '"melee_unwavering": 282'),
       ("len(impl_rows) == 1003 and len(impl_keys) == 1003", "len(impl_rows) == 994 and len(impl_keys) == 994"),
       ('== "SKIPPED (user decision)") == 36, "B5: skipped count is not 36")', '== "SKIPPED (user decision)") == 45, "B5: skipped count is not 45")'),
       ("check(len(entries) == 946 and len(mod_keys) == 1003,", "check(len(entries) == 939 and len(mod_keys) == 994,"),
       ("range(44, 139)", "range(44, 146)"), ("len(te) == 95 and", "len(te) == 102 and"), ("is not 95 integer rows", "is not 102 integer rows"),
       ("cell(139, 3) == 946 and sum(tk) == cell(139, 4) == 1003", "cell(146, 3) == 939 and sum(tk) == cell(146, 4) == 994"),
       ("cell(141, 1) == \"Bombardment set (COMPLETE - round 108)\" and cell(143, 3) == 131", "cell(148, 1) == \"Bombardment set (COMPLETE - round 108)\" and cell(150, 3) == 131"),
       ("bombardment block not at row 141", "bombardment block not at row 148"),
       ("cell(13, 3) == 1003 and cell(14, 3) == 120", "cell(13, 3) == 994 and cell(14, 3) == 129"),
       ("1003 implemented; 36 skipped", "994 implemented; 45 skipped"),
       ("946 entries / 1003 keys, every family matching; trigger table 95 families / 946 / 1003", "939 entries / 994 keys, every family matching; trigger table 102 families / 939 / 994"),
       ("round165\\pre_v49_workbook_md5", "round172\\pre_v55_workbook_md5"),
       ("df53a1b19192d4afecf132049cecb6e0", "239b195b95d7734233d50a7ed1c75698"),
       ("rows in v49, %d in v48", "rows in v55, %d in v54"), ("master v49", "master v55"),
       ("46. ROUND 165", "52. ROUND 172"), ("section 46", "section 52"), ('"v49" and', '"v55" and'),
       ("changelog v49", "changelog v55"), ("== 92 and", "== 104 and"), ("XLSX v49", "XLSX v55"), ("v1-v48", "v1-v54")]
R = []
for a, b, n in R49:
    for x, y in SUB:
        b = b.replace(x, y)
    R.append((a, b, n))
R.append(('"when_ready": 21', '"when_ready": 22', 1))   # round 171: Wand of Jet
for a, b, n in R:
    assert V38.count(a) == n, (a[:70], V38.count(a))
    V38 = V38.replace(a, b)
head = V38
tmp = os.path.join(T, "_verify_v50_base.py")
open(tmp, "w", encoding="utf-8", newline="\n").write(head)
try:
    runpy.run_path(tmp, run_name="__main__")
except SystemExit as e:
    if e.code not in (None, 0):
        raise
finally:
    os.remove(tmp)

import make_xlsx_v49 as M49  # noqa: E402  (the round-165 notes; nothing is written on import)
import make_xlsx_v50 as M50  # noqa: E402
import make_xlsx_v51 as M51  # noqa: E402
import make_xlsx_v52 as M52  # noqa: E402
import make_xlsx_v53 as M53  # noqa: E402
import make_xlsx_v54 as M54  # noqa: E402
import make_xlsx_v55 as M  # noqa: E402
RUN_CARDS = {}
for line in open(M.RUN, encoding="utf-8"):
    if line.startswith("CARD "):
        m, c = line[5:].rstrip("\n").split(": ", 1)
        RUN_CARDS[m] = c
wb = openpyxl.load_workbook(M.DST, read_only=True)
cs = wb["Cards"]
rows = list(cs.iter_rows(min_row=2, values_only=True))
same = sum(1 for r in rows if RUN_CARDS.get(r[0]) == r[4])
whole = sum(1 for r in rows if r[4] and r[4].startswith("Fires ") and not r[4].endswith(".") and len(r[4]) <= 160
            and "{" not in r[4] and "[" not in r[4] and "\u2014" not in r[4] and " on A:" not in r[4])
ws = wb["Abilities"]
noted165, noted166, noted167, noted168 = set(), set(), set(), set()
wk = M50.wander_keys()
rk = M51.risky_armed()
mk, _n168 = M52.moving_keys()
for row in ws.iter_rows(min_row=2, values_only=True):
    for k in str(row[2]).split(";"):
        k = k.strip()
        if k in M49.NOTES and ("ROUND 165 (night audit): " + M49.NOTES[k] + ".") in str(row[21]):
            noted165.add(k)
        if k in wk and M50.NOTE in str(row[21]):
            noted166.add(k)
        if k in rk and M51.note(rk[k]) in str(row[21]):
            noted167.add(k)
        if k in mk and M52.NOTE in str(row[21]):
            noted168.add(k)
print("Cards: %d rows, %d equal to the harness-171 run, %d short and whole; round-165 notes %d / %d; round-166 "
      "wanderer notes %d / %d; round-167 safer-default notes %d / %d; round-168 moving notes %d / %d"
      % (len(rows), same, whole, len(noted165), len(M49.NOTES), len(noted166), len(wk), len(noted167), len(rk),
         len(noted168), len(mk)))
good = (len(rows) == 939 and same == 939 and whole == 939 and noted165 == set(M49.NOTES) and noted166 == wk
        and len(wk) > 0 and noted167 == set(rk) and len(rk) > 0 and noted168 == mk and len(mk) > 0)
pot = [r for r in ws.iter_rows(min_row=2, values_only=True) if str(r[2]).strip() == M53.KEY]
pot_ok = len(pot) == 1 and pot[0][20] == "charge_or_wavering" and pot[0][21] == M53.TEXT
by = {str(r[2]).strip(): r for r in ws.iter_rows(min_row=2, values_only=True)}
_mv = dict((k, v[0]) for k, v in M54.MOVED.items())
_mv.update((k, v[0]) for k, v in M.MOVED.items())
mv_ok = sum(1 for k, f in _mv.items() if by[k][19] == "IMPLEMENTED" and by[k][20] == f) == len(_mv) == 10
mv_ok = mv_ok and all((v[2] + (M.R172 % v[1])) == by[k][21] for k, v in M.MOVED.items())   # round 172: the ruled texts
cl_ok = sum(1 for k in M54.CLOSED if by[k][19] == "SKIPPED (user decision)" and by[k][20] == "-") == len(M54.CLOSED) == 9
print("rounds 171-172: moved rows %s, closed rows %s" % ("ok" if mv_ok else "WRONG", "ok" if cl_ok else "WRONG"))
pot_ok = pot_ok and mv_ok and cl_ok
print("Foolhardiness row: family %s, text %s" % (pot[0][20] if pot else None, "ok" if pot_ok else "WRONG"))
good = good and pot_ok
print("XLSX v55 VERIFY OK" if good else "XLSX v55 VERIFY: round-172 checks FAILED")
sys.exit(0 if good else 1)
