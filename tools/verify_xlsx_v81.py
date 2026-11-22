#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v81_2026-11-22.xlsx (round 204), re-opened from disk, against v80: v80
byte-unchanged; the same 1,802 data rows; Abilities equal except the planned cells (27 exact wave rows + the EXACT
sentence; Tidecall and Wind Blast: family and text), the keys read from the MOD SOURCE; Cards = the mod's 982 entries,
only Tidecall and Wind Blast changed; Numbers reconcile to the rows, the mod and the tracker; Transforms unchanged;
Definitions section 78; one v81 Changelog row with the installed md5.
Usage: verify_xlsx_v81.py <v80 md5> <installed pack md5>"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import make_xlsx_v74 as V74  # noqa: E402
import make_xlsx_v81 as M  # noqa: E402

V80_MD5 = sys.argv[1]
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


ok("v80 byte-unchanged (md5 %s)" % V80_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V80_MD5)
exact, wave, entries = M.exact_keys()
ok("the mod source: 32 wave keys, 27 exact (%d, %d), Tidecall and Wind Blast among the exact"
   % (len(wave), len(exact)), len(wave) == 32 and len(exact) == 27 and set(M.MOVED) <= set(exact))
a80, a81 = rows(M.SRC, "Abilities"), rows(M.DST, "Abilities")
ok("the same data-row count as v80 (%d)" % (len(a81) - 1), len(a80) == len(a81) == 1803)
changed, bad = {}, []
for i, (x, y) in enumerate(zip(a80, a81), start=1):
    for j, (p, q) in enumerate(zip(x, y), start=1):
        if p != q:
            k = str(y[2]).split(";")[0].strip()
            if k in M.MOVED and ((j == 21 and q == "enemy_wave") or (j == 22 and q == M.MOVED_TEXT + M.EXACT)):
                changed.setdefault(k, []).append(j)
            elif j == 22 and k in exact and q == (p or "").rstrip() + M.EXACT:
                changed.setdefault(k, []).append(j)
            else:
                bad.append((i, j))
ok("Abilities: exactly the 27 exact rows changed, nothing else (%d rows, %d other cells)" % (len(changed), len(bad)),
   set(changed) == set(exact) and not bad and all(changed[k] == [21, 22] for k in M.MOVED))
by = {str(x[2]).split(";")[0].strip(): x for x in a81[1:]}
ok("the 5 drifting waves do not carry the EXACT sentence",
   all("EXACT WAVE" not in str(by[k][21]) for k in wave if k not in exact) and len([k for k in wave if k not in exact]) == 5)
ok("no semicolon and no em dash in the new texts", all(";" not in s and "\u2014" not in s for s in (M.EXACT, M.MOVED_TEXT)))
impl = {str(x[2]).split(";")[0].strip() for x in a81[1:] if x[19] == "IMPLEMENTED"}
ok("the implemented rows are exactly the mod's keys (%d)" % len(impl), impl == {k for e in entries for k in e["keys"]})
st = V74.source_types()
tot, exc, inc, n_impl, car, ex = V74.counts(a81[1:], st)
nm = rows(M.DST, "Numbers")
fam = {nm[r][1]: (nm[r][2], nm[r][3]) for r in range(43, 184)}
ok("Numbers reconcile (1,802 / 687 / 1,115 / 1,035), enemy_wave 32 / 32, enemy_wave_charge 0 / 0, total 982 / 1,035",
   [nm[r - 1][2] for r in range(10, 14)] == [tot, exc, inc, n_impl] and (tot, exc, inc, n_impl) == (1802, 687, 1115, 1035)
   and fam["enemy_wave"] == (32, 32) and fam["enemy_wave_charge"] == (0, 0) and nm[184][2] == 982 and nm[184][3] == 1035
   and sum(v[0] for v in fam.values()) == 982 and sum(v[1] for v in fam.values()) == 1035)
trk = open(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md", encoding="utf-8").read()
ok("the tracker carries the round (section 10.81, the two moved rows)",
   "### 10.81 Round 204" in trk and trk.count("enemy_wave, round 204)`") == 2)
c80, c81 = rows(M.SRC, "Cards"), rows(M.DST, "Cards")
old = {r[0]: r for r in c80[1:]}
new = {r[0]: r for r in c81[1:]}
diff = sorted(m for m in new if old.get(m) != new[m])
ok("Cards: 982 entries, only Tidecall and Wind Blast changed (%s)" % diff,
   len(c81) == 983 and set(old) == set(new) and diff == ["tidecall", "wind_blast"]
   and all(new[m][2] == "enemy_wave" for m in diff))
x, y = rows(M.SRC, "Transforms"), rows(M.DST, "Transforms")
ok("Transforms: unchanged", x == y)
d = rows(M.DST, "Definitions")
ok("Definitions: title v81 and section 78", d[0][0] == "DEFINITIONS - WH3 ability master v81 (2026-11-22)"
   and any(str(r[0]).startswith("78. ROUND 204") for r in d))
h80, h81 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one v81 row with the installed md5", len(h81) == len(h80) + 1 and h81[-1][1] == "v81"
   and PACK_MD5 in h81[-1][2] and "PENDING" not in h81[-1][2] and h81[:-1] == h80)
print("XLSX v81 VERIFY OK" if good else "XLSX v81 VERIFY FAILED")
sys.exit(0 if good else 1)
