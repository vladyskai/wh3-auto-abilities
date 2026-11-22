#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v79_2026-11-22.xlsx (round 201), re-opened from disk, against v78: v78
byte-unchanged; the same 1,802 data rows; Abilities equal except the 31 planned cells (5 Master Runes -> EXCLUDED, the
two Endless Whirlwind rows -> IMPLEMENTED); the implemented keys equal the mod's keys (read from the MOD SOURCE); Cards
= the mod's 982 entries, every kept card unchanged; Numbers reconcile to the rows and to the tracker; Transforms
unchanged; Definitions section 76; one v79 Changelog row with the installed md5.
Usage: verify_xlsx_v79.py <v78 md5> <installed pack md5>"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402
import make_xlsx_v74 as V74  # noqa: E402
import make_xlsx_v79 as M  # noqa: E402

V78_MD5 = sys.argv[1]
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


ok("v78 byte-unchanged (md5 %s)" % V78_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V78_MD5)
a78, a79 = rows(M.SRC, "Abilities"), rows(M.DST, "Abilities")
ok("the same data-row count as v78 (%d)" % (len(a79) - 1), len(a78) == len(a79) == 1803)
changed = {}
for i, (x, y) in enumerate(zip(a78, a79), start=1):
    for j, (p, q) in enumerate(zip(x, y), start=1):
        if p != q:
            changed.setdefault(str(y[2]), []).append(j)
ok("Abilities: only the 7 planned rows changed (%d rows, %d cells)" % (len(changed), sum(len(v) for v in changed.values())),
   set(changed) == set(M.RUNES + M.EW) and all(changed[k] == [18, 19, 20, 21, 22] for k in M.RUNES)
   and all(changed[k] == [20, 21, 22] for k in M.EW))
by = {str(x[2]).split(";")[0].strip(): x for x in a79[1:]}
ok("the five Master Runes read EXCLUDED / REMOVED with the user's ruling",
   all(by[k][17] == "EXCLUDED" and by[k][19] == M.RUNE_IMPL and by[k][20] == "-" and by[k][21] == M.RUNE_TRIG
       and "2026-11-22" in by[k][18] for k in M.RUNES))
ok("Endless Whirlwind of Death x2 read IMPLEMENTED on melee_unwavering with the new trigger text",
   all(by[k][17] == "IN-WHEEL" and by[k][19] == "IMPLEMENTED" and by[k][20] == "melee_unwavering" and by[k][21] == M.EW_TRIG
       for k in M.EW))
ok("no semicolon and no em dash in the new texts",
   all(";" not in s and "\u2014" not in s for s in (M.RUNE_REASON, M.RUNE_TRIG, M.EW_TRIG)))
entries, _, _ = bd.mod_entries()
mod_keys = {k for e in entries for k in e["keys"]}
impl = {str(x[2]).split(";")[0].strip() for x in a79[1:] if x[19] == "IMPLEMENTED"}
ok("the implemented rows are exactly the mod's keys (%d, read from the mod source)" % len(mod_keys),
   impl == mod_keys and len(mod_keys) == 1035 and len(entries) == 982
   and not (set(M.RUNES) & mod_keys) and set(M.EW) <= mod_keys)
st = V74.source_types()
tot, exc, inc, n_impl, car, ex = V74.counts(a79[1:], st)
nm = rows(M.DST, "Numbers")
ok("Numbers rows 10-16 are the counted rows (1,802 / 687 / 1,115 / 1,035 / 80 / 0 / 1,035)",
   [nm[r - 1][2] for r in range(10, 17)] == [tot, exc, inc, n_impl, inc - n_impl, 0, n_impl]
   and (tot, exc, inc, n_impl) == (1802, 687, 1115, 1035))
ok("Numbers: the carrier table ties (rune 2 / 0, total %d / %d)" % (nm[28][2], nm[28][3]),
   nm[21][2] == 2 and nm[21][3] == 0 and nm[28][2] == inc and nm[28][3] == n_impl
   and sum(nm[r][2] for r in range(19, 28)) == inc and sum(nm[r][3] for r in range(19, 28)) == n_impl)
ok("Numbers: the exclusions tie (spell-bar runes 10, total %d)" % nm[38][2],
   nm[37][2] == 10 and nm[38][2] == exc and sum(nm[r][2] for r in range(31, 38)) == exc)
ok("Numbers: the family table totals 982 entries / 1,035 keys, melee_unwavering 278",
   nm[184][2] == 982 and nm[184][3] == 1035 and nm[43][1] == "melee_unwavering" and nm[43][2] == 278
   and sum(nm[r][2] for r in range(43, 184)) == 982 and sum(nm[r][3] for r in range(43, 184)) == 1035)
trk = open(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md", encoding="utf-8").read()
ok("the tracker carries the round (section 10.78, the runes rejected, Endless Whirlwind implemented)",
   "10.78" in trk and trk.count("implemented (melee_unwavering, round 201)") == 2
   and all(("`%s` | `rejected (user 2026-11-22" % k) in trk for k in M.RUNES))
c78, c79 = rows(M.SRC, "Cards"), rows(M.DST, "Cards")
old = {r[0]: r for r in c78[1:]}
new = {r[0]: r for r in c79[1:]}
ok("Cards: the mod's 982 entries, the 5 runes gone, the 2 new cards read 'Fires in melee unless wavering'",
   set(new) == {e["marker"] for e in entries} and len(c79) == 983 and set(old) - set(new) == {
       "master_rune_of_breaking", "master_rune_of_negation", "master_rune_of_slowness", "master_rune_of_speed",
       "master_rune_of_oath_and_steel"}
   and set(new) - set(old) == {"whirlwind_of_death_ror", "whirlwind_of_death_ror_upgraded"}
   and all(new[m][4] == "Fires in melee unless wavering" for m in set(new) - set(old)))
ok("Cards: every kept card is unchanged", all(old[m] == new[m] for m in new if m in old))
x, y = rows(M.SRC, "Transforms"), rows(M.DST, "Transforms")
ok("Transforms: unchanged", x == y)
d = rows(M.DST, "Definitions")
ok("Definitions: title v79 and section 76", d[0][0] == "DEFINITIONS - WH3 ability master v79 (2026-11-22)"
   and any(str(r[0]).startswith("76. ROUND 201") for r in d))
h78, h79 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one v79 row with the installed md5", len(h79) == len(h78) + 1 and h79[-1][1] == "v79"
   and PACK_MD5 in h79[-1][2] and "PENDING" not in h79[-1][2] and h79[:-1] == h78)
print("XLSX v79 VERIFY OK" if good else "XLSX v79 VERIFY FAILED")
sys.exit(0 if good else 1)
