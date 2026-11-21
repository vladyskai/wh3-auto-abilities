#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v75_2026-11-21.xlsx (round 193), re-opened from disk, against v74: v74
byte-unchanged; Abilities equal except the three Scry-Orb cells; Numbers tie (1,038 + 82 = 1,120, families 985 / 1,038);
Cards = the harness-192 run; Definitions section 72; one v75 Changelog row with the installed md5."""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import make_xlsx_v75 as M  # noqa: E402

V74_MD5 = sys.argv[1] if len(sys.argv) > 1 else ""
PACK_MD5 = "9f3107dd086756560d98caf1516de831"
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


ok("v74 byte-unchanged (md5 %s)" % V74_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V74_MD5)
a74, a75 = rows(M.SRC, "Abilities"), rows(M.DST, "Abilities")
diff = [(i, j) for i, (x, y) in enumerate(zip(a74, a75), start=1) for j, (p, q) in enumerate(zip(x, y), start=1) if p != q]
ok("Abilities: same 1,802 rows, only Scry-Orb's 3 cells changed %s" % diff,
   len(a74) == len(a75) == 1803 and [j for _, j in diff] == [20, 21, 22] and a75[diff[0][0] - 1][2] == M.SCRY)
ok("Scry-Orb: IMPLEMENTED on when_ready", a75[-1][19] == "IMPLEMENTED" and a75[-1][20] == "when_ready")
num = rows(M.DST, "Numbers")
ok("Numbers headline 1,802 / 682 / 1,120 / 1,038 / 82 / 0 / 1,038",
   [num[i][2] for i in range(9, 16)] == [1802, 682, 1120, 1038, 82, 0, 1038])
ok("carrier table ties 1,120 / 1,038", sum(num[i][2] for i in range(19, 28)) == 1120
   and sum(num[i][3] for i in range(19, 28)) == 1038 and num[28][2] == 1120 and num[28][3] == 1038)
ok("family table 985 / 1,038", num[184][2] == 985 and num[184][3] == 1038
   and sum(num[i][2] for i in range(43, 184)) == 985)
cards = M.read_cards()
cs = rows(M.DST, "Cards")
ok("Cards: 985, each the harness-192 card, Scry-Orb listed", len(cs) == 986 and all(cards[r[0]] == r[4] for r in cs[1:])
   and any(r[0] == "scry_orb" for r in cs[1:]))
ok("Transforms unchanged", rows(M.SRC, "Transforms") == rows(M.DST, "Transforms"))
d = rows(M.DST, "Definitions")
ok("Definitions: title v75 and section 72", d[0][0] == "DEFINITIONS - WH3 ability master v75 (2026-11-21)"
   and any(str(r[0]).startswith("72. ROUND 193") for r in d))
c74, c75 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one v75 row with the installed md5", len(c75) == len(c74) + 1 and c75[-1][1] == "v75"
   and PACK_MD5 in c75[-1][2] and c75[:-1] == c74)
print("XLSX v75 VERIFY OK" if good else "XLSX v75 VERIFY FAILED")
sys.exit(0 if good else 1)
