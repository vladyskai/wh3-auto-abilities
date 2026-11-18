#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v61_2026-11-18.xlsx (round 178; cloned from the v60 verifier) from disk: the v38 verifier's structural checks
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
SUB = [("v49_2026-11-17", "v61_2026-11-18"), ("v48_2026-11-16", "v60_2026-11-18"), ('"melee_unwavering": 299', '"melee_unwavering": 265'), ('"enemy_ground_melee": 75', '"enemy_ground_melee": 74'), ('"enemy_fast_near_ally": 9', '"enemy_fast_near_ally": 15'),
       ("len(impl_rows) == 1003 and len(impl_keys) == 1003", "len(impl_rows) == 992 and len(impl_keys) == 992"),
       ('== "SKIPPED (user decision)") == 36, "B5: skipped count is not 36")', '== "SKIPPED (user decision)") == 47, "B5: skipped count is not 47")'),
       ("check(len(entries) == 946 and len(mod_keys) == 1003,", "check(len(entries) == 938 and len(mod_keys) == 992,"),
       ("range(44, 139)", "range(44, 167)"), ("len(te) == 95 and", "len(te) == 123 and"), ("is not 95 integer rows", "is not 123 integer rows"),
       ('"enemy_blob": 77', '"enemy_blob": 69'), ('"enemy_engaged_or_shot": 46', '"enemy_engaged_or_shot": 22'),
       ('"enemy_melee": 35', '"enemy_melee": 35'),
       ("cell(139, 3) == 946 and sum(tk) == cell(139, 4) == 1003", "cell(167, 3) == 938 and sum(tk) == cell(167, 4) == 992"),
       ("cell(141, 1) == \"Bombardment set (COMPLETE - round 108)\" and cell(143, 3) == 131", "cell(169, 1) == \"Bombardment set (COMPLETE - round 108)\" and cell(171, 3) == 131"),
       ("bombardment block not at row 141", "bombardment block not at row 169"),
       ("cell(13, 3) == 1003 and cell(14, 3) == 120", "cell(13, 3) == 992 and cell(14, 3) == 131"),
       ("1003 implemented; 36 skipped", "992 implemented; 47 skipped"),
       ("946 entries / 1003 keys, every family matching; trigger table 95 families / 946 / 1003", "938 entries / 992 keys, every family matching; trigger table 123 families / 938 / 992"),
       ("round165\\pre_v49_workbook_md5", "round178\\pre_v61_workbook_md5"),
       ("df53a1b19192d4afecf132049cecb6e0", "b8622a7b2b6c9bb6ed1c8c5844cac5bf"),
       ("rows in v49, %d in v48", "rows in v61, %d in v60"), ("master v49", "master v61"),
       ("46. ROUND 165", "58. ROUND 178"), ("section 46", "section 58"), ('"v49" and', '"v61" and'),
       ("changelog v49", "changelog v61"), ("== 92 and", "== 116 and"), ("XLSX v49", "XLSX v61"), ("v1-v48", "v1-v60")]
R = []
for a, b, n in R49:
    for x, y in SUB:
        b = b.replace(x, y)
    R.append((a, b, n))
R.append(('"when_ready": 21', '"when_ready": 22', 1))   # round 171: Wand of Jet
# round 174: six blob attacks left enemy_blob (77 -> 71); the 29 moved keys expect their new family
R.append(("assert len(_K37) == 77, len(_K37)", "assert len(_K37) == 69, len(_K37)", 1))   # round 178: 69
R.append(('"enemy_blob": 77', '"enemy_blob": 69', 1))
R.append(('"enemy_engaged_or_shot": 46', '"enemy_engaged_or_shot": 22', 1))
R.append(('"melee_or_under_fire": 4,', '"melee_or_under_fire": 5,', 1))   # round 177: Rune of Oath & Steel
R.append(('"self_last_stand": 1,', '"self_last_stand": 2,', 1))   # round 177: Slayer for Chaos
# round 174: Transfix kept its target class in its new text; Silence the Prey and Power Siphon gained theirs (53 -> 55);
# 9 enemy_engaged_or_shot keys left (51 -> 42 rows)
R.append(('== 53, "B6: the target-class rows are not 53")', '== 50, "B6: the target-class rows are not 50")', 1))
R.append(('== 51, "B10: enemy_engaged_or_shot rows are not 51 (46 entries; some span two rows)")',
          '== 26, "B10: enemy_engaged_or_shot rows are not 26 (22 entries; some span two rows)")', 1))
# round 178: Void Pendulum targets spellcasters now (its Lord/Hero class text is gone)
R.append(('and "target class: Lord/Hero only" in str(by_key["wh3_main_item_abilities_void_pendulum"][21]),',
          'and "spellcaster" in str(by_key["wh3_main_item_abilities_void_pendulum"][21]),   # round 178', 1))
R.append(('EXPECT.update({k: "enemy_blob" for k in _K37})\n',
          'EXPECT.update({k: "enemy_blob" for k in _K37})\n'
          'import make_xlsx_v57 as _M174\n'
          'EXPECT.update({k: v[0] for k, v in _M174.MOVED.items()})\n', 1))
# round 177: the 15 moved keys expect their new family (applied after the round-174 line it extends)
R.append(('EXPECT.update({k: v[0] for k, v in _M174.MOVED.items()})\n',
          'EXPECT.update({k: v[0] for k, v in _M174.MOVED.items()})\n'
          'import make_xlsx_v60 as _M177\n'
          'EXPECT.update({k: v[0] for k, v in _M177.MOVED.items()})\n'
          'import make_xlsx_v61 as _M178\n'
          'EXPECT.update({k: v[0] for k, v in _M178.MOVED.items()})\n', 1))
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
import make_xlsx_v55 as M55  # noqa: E402
import make_xlsx_v56 as M56  # noqa: E402
import make_xlsx_v57 as M  # noqa: E402
import make_xlsx_v59 as M59  # noqa: E402
import make_xlsx_v60 as M60  # noqa: E402   (round 177: its moves)
import make_xlsx_v61 as M58  # noqa: E402   (round 178: the v61 module: RUN and DST)
RUN_CARDS = {}
for line in open(M58.RUN, encoding="utf-8"):
    if line.startswith("CARD "):
        m, c = line[5:].rstrip("\n").split(": ", 1)
        RUN_CARDS[m] = c
wb = openpyxl.load_workbook(M58.DST, read_only=True)
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
print("Cards: %d rows, %d equal to the harness-177 run, %d short and whole; round-165 notes %d / %d; round-166 "
      "wanderer notes %d / %d; round-167 safer-default notes %d / %d; round-168 moving notes %d / %d"
      % (len(rows), same, whole, len(noted165), len(M49.NOTES), len(noted166), len(wk), len(noted167), len(rk),
         len(noted168), len(mk)))
good = (len(rows) == 938 and same == 938 and whole == 938 and noted165 == set(M49.NOTES) and noted166 == wk
        and len(wk) > 0 and noted167 == set(rk) and len(rk) > 0 and noted168 == mk and len(mk) > 0)
pot = [r for r in ws.iter_rows(min_row=2, values_only=True) if str(r[2]).strip() == M53.KEY]
pot_ok = len(pot) == 1 and pot[0][20] == "charge_or_wavering" and pot[0][21] == M53.TEXT
by = {str(r[2]).strip(): r for r in ws.iter_rows(min_row=2, values_only=True)}
_mv = dict((k, v[0]) for k, v in M54.MOVED.items())
_mv.update((k, v[0]) for k, v in M55.MOVED.items())
mv_ok = sum(1 for k, f in _mv.items() if by[k][19] == "IMPLEMENTED" and by[k][20] == f) == len(_mv) == 10
mv_ok = mv_ok and all((v[2] + (M55.R172 % v[1])) == by[k][21] for k, v in M55.MOVED.items())   # round 172: the ruled texts
cl_ok = sum(1 for k in list(M54.CLOSED) + list(M56.CLOSED) if by[k][19] == "SKIPPED (user decision)" and by[k][20] == "-") == 11
# round 174: the 29 moved keys carry their family and ruled text
_old56 = {str(r[2]).split(";")[0].strip(): str(r[21] or "") for r in openpyxl.load_workbook(M.SRC, read_only=True)["Abilities"].iter_rows(min_row=2, values_only=True)}
mv174 = sum(1 for k, v in M.MOVED.items() if by[k][19] == "IMPLEMENTED" and by[k][20] == v[0]
            and by[k][21] == M.text_of(k, _old56[k]))
print("round 174: moved rows %d / %d" % (mv174, len(M.MOVED)))
# round 175: the two Master of Mists rows carry the new text
mm175 = sum(1 for k in M59.KEYS if by[k][19] == "IMPLEMENTED" and by[k][20] == "ground_ally_before_range" and by[k][21] == M59.TEXT)
_old59 = {str(r[2]).split(";")[0].strip(): str(r[21] or "") for r in openpyxl.load_workbook(M58.SRC, read_only=True)["Abilities"].iter_rows(min_row=2, values_only=True)}
mv177 = sum(1 for k, v in M60.MOVED.items() if by[k][19] == "IMPLEMENTED" and by[k][20] == v[0])
print("round 177: moved rows %d / %d" % (mv177, len(M60.MOVED)))
print("round 175: Master of Mists rows %d / 2" % mm175)
cl_ok = cl_ok and mv174 == len(M.MOVED) == 28 and mm175 == 2 and mv177 == len(M60.MOVED) == 15
print("rounds 171-172: moved rows %s, closed rows %s" % ("ok" if mv_ok else "WRONG", "ok" if cl_ok else "WRONG"))
pot_ok = pot_ok and mv_ok and cl_ok
print("Foolhardiness row: family %s, text %s" % (pot[0][20] if pot else None, "ok" if pot_ok else "WRONG"))
good = good and pot_ok
# round 178: the 22 moved keys carry their family and text; the Trophy Heads rows are split; Eye of Khorne value-first
_old60 = {str(r[2]).split(";")[0].strip(): str(r[21] or "") for r in openpyxl.load_workbook(M58.SRC, read_only=True)["Abilities"].iter_rows(min_row=2, values_only=True)}
by1 = {str(r[2]).split(";")[0].strip(): r for r in ws.iter_rows(min_row=2, values_only=True)}
mv178 = sum(1 for k, v in M58.MOVED.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == v[0]
            and by1[k][21] == M58.text_of(k, _old60[k]))
tr178 = (str(by[M58.TROPHY[0]][2]).strip() == M58.TROPHY[0] and str(by[M58.TROPHY[1]][2]).strip() == M58.TROPHY[1]
         and by[M58.TROPHY[1]][21] == M58.TROPHY_DW_TEXT and by[M58.TROPHY[0]][20] == by[M58.TROPHY[1]][20] == "enemy_melee")
ek178 = "highest live value" in str(by["wh3_dlc26_lord_abilities_eye_of_khorne"][21])
print("round 178: moved rows %d / %d; Trophy Heads split %s; Eye of Khorne value-first %s"
      % (mv178, len(M58.MOVED), tr178, ek178))
good = good and mv178 == len(M58.MOVED) == 22 and tr178 and ek178
print("XLSX v61 VERIFY OK" if good else "XLSX v61 VERIFY: round-178 checks FAILED")
sys.exit(0 if good else 1)
