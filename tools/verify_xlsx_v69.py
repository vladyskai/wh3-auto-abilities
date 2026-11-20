#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v69_2026-11-20.xlsx (round 186; cloned from the v68 verifier) from disk: the v38 verifier's structural checks
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
SUB = [("v49_2026-11-17", "v69_2026-11-20"), ("v48_2026-11-16", "v68_2026-11-20"), ('"melee_self_or_ally": 1', '"melee_self_or_ally": 2'), ('"melee_unwavering": 299', '"melee_unwavering": 281'), ('"enemy_ground_melee": 75', '"enemy_ground_melee": 74'), ('"enemy_fast_near_ally": 9', '"enemy_fast_near_ally": 20'), ('"charge_or_melee": 37', '"charge_or_melee": 36'),
       ("len(impl_rows) == 1003 and len(impl_keys) == 1003", "len(impl_rows) == 1041 and len(impl_keys) == 1041"),
       ('== "SKIPPED (user decision)") == 36, "B5: skipped count is not 36")', '== "SKIPPED (user decision)") == 62, "B5: skipped count is not 62")'),
       ("check(len(entries) == 946 and len(mod_keys) == 1003,", "check(len(entries) == 988 and len(mod_keys) == 1041,"),
       ("range(44, 139)", "range(44, 185)"), ("len(te) == 95 and", "len(te) == 141 and"), ("is not 95 integer rows", "is not 141 integer rows"),
       ('"enemy_blob": 77', '"enemy_blob": 68'), ('"enemy_engaged_or_shot": 46', '"enemy_engaged_or_shot": 22'),
       ('"enemy_melee": 35', '"enemy_melee": 35'),
       ("cell(139, 3) == 946 and sum(tk) == cell(139, 4) == 1003", "cell(185, 3) == 988 and sum(tk) == cell(185, 4) == 1041"),
       ("cell(141, 1) == \"Bombardment set (COMPLETE - round 108)\" and cell(143, 3) == 131", "cell(187, 1) == \"Bombardment set (COMPLETE - round 108)\" and cell(189, 3) == 131"),
       ("bombardment block not at row 141", "bombardment block not at row 187"),
       ("cell(13, 3) == 1003 and cell(14, 3) == 120", "cell(13, 3) == 1041 and cell(14, 3) == 82"),
       ("1003 implemented; 36 skipped", "1041 implemented; 62 skipped"),
       ("946 entries / 1003 keys, every family matching; trigger table 95 families / 946 / 1003", "988 entries / 1041 keys, every family matching; trigger table 141 families / 988 / 1041"),
       ("round165\\pre_v49_workbook_md5", "round186\\pre_v69_workbook_md5"),
       ("df53a1b19192d4afecf132049cecb6e0", "8bf23234706e1647946a84cc0e33a969"),
       ("rows in v49, %d in v48", "rows in v69, %d in v68"), ("master v49", "master v69"),
       ("46. ROUND 165", "66. ROUND 186"), ("section 46", "section 66"), ('"v49" and', '"v69" and'),
       ("changelog v49", "changelog v69"), ("== 92 and", "== 132 and"), ("XLSX v49", "XLSX v69"), ("v1-v48", "v1-v68")]
R = []
for a, b, n in R49:
    for x, y in SUB:
        b = b.replace(x, y)
    R.append((a, b, n))
R.append(('"when_ready": 21', '"when_ready": 20', 1))   # round 180: 2 closed   # round 171: Wand of Jet
# round 174: six blob attacks left enemy_blob (77 -> 71); the 29 moved keys expect their new family
R.append(("assert len(_K37) == 77, len(_K37)", "assert len(_K37) == 68, len(_K37)", 1))   # round 182: 68   # round 178: 69
R.append(('"enemy_blob": 77', '"enemy_blob": 68', 1))
R.append(('"enemy_engaged_or_shot": 46', '"enemy_engaged_or_shot": 22', 1))
R.append(('"melee_or_under_fire": 4,', '"melee_or_under_fire": 5,', 1))   # round 177: Rune of Oath & Steel
R.append(('"self_last_stand": 1,', '"self_last_stand": 3,', 1))   # round 185: + the Black Gem of Gnar
R.append(('"self_recharging": 5,', '"self_recharging": 6,', 1))   # round 185: + Mad Cap Mushrooms
R.append(('"charge_only": 4,', '"charge_only": 5,', 1))   # round 185: + Swiftness of Itzl
R.append(('"melee_self_or_ally": 1,', '"melee_self_or_ally": 3,', 1))   # round 180: + Shield of Thorns   # round 179: Favour of the Fay   # round 177: Slayer for Chaos
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
          'EXPECT.update({k: v[0] for k, v in _M178.MOVED.items()})\n'
          'import make_xlsx_v62 as _M179\n'
          'EXPECT.update({k: v[0] for k, v in _M179.MOVED.items()})\n'
          'import make_xlsx_v63 as _M180\n'
          'EXPECT.update(_M180.FAMILY)\n'
          'EXPECT = {k: v for k, v in EXPECT.items() if k not in _M180.CLOSED}\n'
          'import make_xlsx_v64 as _M181\n'
          'EXPECT.update(_M181.FAMILY)\n'
          'import make_xlsx_v65 as _M182\n'
          'EXPECT.update(_M182.FAMILY)\n'
          'import make_xlsx_v66 as _M183\n'
          'EXPECT.update(_M183.FAMILY)\n'
          'import make_xlsx_v67 as _M184\n'
          'EXPECT.update(_M184.FAMILY)\n'
          'import make_xlsx_v68 as _M185\n'
          'EXPECT.update(_M185.FAMILY)\n'
          'import make_xlsx_v69 as _M186\n'
          'EXPECT.update(_M186.FAMILY)\n', 1))
R.append(('EXPECT.update({k: "when_ready" for k in _R150.WINDS})\n',
          'EXPECT.update({k: "when_ready" for k in _R150.WINDS})\n'
          'import make_xlsx_v63 as _M180c\n'
          'EXPECT = {k: v for k, v in EXPECT.items() if k not in _M180c.CLOSED}   # round 180: closed\n', 1))
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
import make_xlsx_v61 as M58  # noqa: E402   (round 178: its moves)
import make_xlsx_v62 as M62  # noqa: E402   (round 179: its moves)
import make_xlsx_v63 as M63  # noqa: E402   (round 180: its moves)
import make_xlsx_v64 as M64  # noqa: E402   (round 181: its moves)
import make_xlsx_v65 as M65  # noqa: E402   (round 182: its moves)
import make_xlsx_v66 as M66  # noqa: E402   (round 183: its rows)
import make_xlsx_v67 as M67  # noqa: E402   (round 184: its rows)
import make_xlsx_v68 as M68  # noqa: E402   (round 185: its rows)
import make_xlsx_v69 as M69  # noqa: E402   (round 186: the v69 module: RUN and DST)
RUN_CARDS = {}
for line in open(M69.RUN, encoding="utf-8"):
    if line.startswith("CARD "):
        m, c = line[5:].rstrip("\n").split(": ", 1)
        RUN_CARDS[m] = c
wb = openpyxl.load_workbook(M69.DST, read_only=True)
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
print("Cards: %d rows, %d equal to the harness-185 run, %d short and whole; round-165 notes %d / %d; round-166 "
      "wanderer notes %d / %d; round-167 safer-default notes %d / %d; round-168 moving notes %d / %d"
      % (len(rows), same, whole, len(noted165), len(M49.NOTES), len(noted166), len(wk), len(noted167), len(rk),
         len(noted168), len(mk)))
good = (len(rows) == 988 and same == 988 and whole == 988 and noted165 == set(M49.NOTES) - set(M63.CLOSED) and noted166 == wk
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
# round 179: the 12 moved keys and the 3 same-family keys carry their family and text
_old61 = {str(r[2]).split(";")[0].strip(): str(r[21] or "") for r in openpyxl.load_workbook(M62.SRC, read_only=True)["Abilities"].iter_rows(min_row=2, values_only=True)}
_all179 = dict((k, v[0]) for k, v in M62.MOVED.items())
_all179.update((k, v[0]) for k, v in M62.SAME.items())
mv179 = sum(1 for k, f in _all179.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M62.text_of(k, _old61[k]))
print("round 179: moved / re-ruled rows %d / %d" % (mv179, len(_all179)))
good = good and mv179 == len(_all179) == 15
# round 180: the moved / re-ruled rows carry their family and text; the closed rows are SKIPPED; the WW notes
_old62 = {str(r[2]).split(";")[0].strip(): str(r[21] or "") for r in openpyxl.load_workbook(M63.SRC, read_only=True)["Abilities"].iter_rows(min_row=2, values_only=True)}
mv180 = sum(1 for k, f in M63.FAMILY.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M63.text_of(k, _old62[k]))
cl180 = sum(1 for k in M63.CLOSED if by1[k][19] == "SKIPPED (user decision)" and by1[k][20] == "-")
ww180 = sum(1 for k in M63.WW_NOTE if by1[k][21] == M63.ww_text(k, _old62[k]))
print("round 180: moved / re-ruled rows %d / %d; closed %d / 3; WW notes %d / 5" % (mv180, len(M63.FAMILY), cl180, ww180))
good = good and mv180 == len(M63.FAMILY) == 16 and cl180 == 3 and ww180 == 5
# round 181: Land Mine and Surprise Squig! carry their family and text; the range-fixed rows carry their note
_old63 = {str(r[2]).split(";")[0].strip(): str(r[21] or "") for r in openpyxl.load_workbook(M64.SRC, read_only=True)["Abilities"].iter_rows(min_row=2, values_only=True)}
mv181 = sum(1 for k, f in M64.FAMILY.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M64.text_of(k, _old63[k]))
nt181 = sum(1 for k in M64.NOTE if by1[k][21] == M64.note_text(k, _old63[k]))
print("round 181: moved rows %d / 2; range notes %d / %d" % (mv181, nt181, len(M64.NOTE)))
good = good and mv181 == 2 and nt181 == len(M64.NOTE) == 9
# round 182: the finishers carry their family and text
_old64 = {str(r[2]).split(";")[0].strip(): str(r[21] or "") for r in openpyxl.load_workbook(M65.SRC, read_only=True)["Abilities"].iter_rows(min_row=2, values_only=True)}
mv182 = sum(1 for k, f in M65.FAMILY.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M65.text_of(k, _old64[k]))
print("round 182: finisher rows %d / %d" % (mv182, len(M65.FAMILY)))
good = good and mv182 == len(M65.FAMILY) == 4
# round 183: the rule-shut review rows 1-9 are IMPLEMENTED on their ruled family with their text
nw183 = sum(1 for k, f in M66.FAMILY.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M66.text_of(k))
print("round 183: new rows %d / %d" % (nw183, len(M66.FAMILY)))
good = good and nw183 == len(M66.FAMILY) == 9
# round 184: the rule-shut review rows 10-19 are IMPLEMENTED on their ruled family with their text
nw184 = sum(1 for k, f in M67.FAMILY.items() if k not in M69.FAMILY and by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M67.text_of(k))
print("round 184: new rows %d / %d" % (nw184, len(M67.FAMILY)))
good = good and nw184 == len(M67.FAMILY) - 1 == 9   # round 186: Warpstorm moved
print("XLSX v67 rows still right" if good else "XLSX v67 rows: FAILED")
# round 185: the rule-shut review rows 20-64: 33 IMPLEMENTED on their ruled family with their text, 12 closed
nw185 = sum(1 for k, f in M68.FAMILY.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M68.text_of(k))
cl185 = sum(1 for k in M68.CLOSED if by1[k][19] == "SKIPPED (user decision)" and by1[k][20] == "-"
            and by1[k][18] == M68.closed_reason(k))
print("round 185: new rows %d / %d; closed rows %d / %d" % (nw185, len(M68.FAMILY), cl185, len(M68.CLOSED)))
good = good and nw185 == len(M68.FAMILY) == 33 and cl185 == len(M68.CLOSED) == 12
print("XLSX v68 rows still right" if good else "XLSX v68 rows: FAILED")
# round 186: Warpstorm Scroll on enemy_most_valuable with its text
nw186 = sum(1 for k, f in M69.FAMILY.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M69.text_of(k))
print("round 186: moved rows %d / %d" % (nw186, len(M69.FAMILY)))
good = good and nw186 == len(M69.FAMILY) == 1
print("XLSX v69 VERIFY OK" if good else "XLSX v69 VERIFY: round-186 checks FAILED")
sys.exit(0 if good else 1)
