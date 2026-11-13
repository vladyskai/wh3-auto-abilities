#!/usr/bin/env python3
"""Build WH3_abilities_master_v32_2026-11-13.xlsx from v31 - round 140: QA battle 3 findings.

(1) Blooood! moves from charge_only to the NEW self_running (is_moving_fast()).
(2) Every row whose trigger reads the firing flag gains the moving clause ("not moving, unless the unit fires on the
    move" - user ruling 2026-11-13).
(3) Counts unchanged (750 / 373); 59 -> 60 families: the Numbers trigger table gains one row (bombardment block
    105 -> 106). Definitions: title v32, section 29. Changelog: a v32 row. v1-v31 are never opened for writing.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v31_2026-11-09.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v32_2026-11-13.xlsx"
SHOOT_FAMS = {"ally_ammo_low", "allies_firing_aura", "melee_or_shooting_into_melee", "self_or_ally_shooting",
              "melee_or_self_or_ally_shooting", "melee_or_shooting_aura", "melee_or_shooting_self_or_ally", "self_shooting",
              "enemy_missile_shooting"}
MOVE = (" MOVING RULE (round 140, user ruling 2026-11-13: \"Unless the unit can fire while moving, shooting and moving are "
        "incompatible\"): a unit whose is_moving() is true counts as NOT shooting unless its type is in the GENERATED "
        "fire_move set (unit attribute mounted_fire_move, 233 types); an unreadable is_moving() keeps the firing flag.")
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
RUN = ("self_running: not routing; is_moving_fast() exactly true (user ruling 2026-11-13 after QA battle 3: \"Running, "
       "any time\"); cast target: self; " + SHARED_TAIL)

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
n_move = n_run = 0
for r in range(2, ws.max_row + 1):
    fam = str(ws.cell(row=r, column=21).value)
    if "wh_main_unit_abilities_blooood" in keys_of(r):
        assert fam == "charge_only"
        old = str(ws.cell(row=r, column=22).value or "")
        gates = (" GATES" + old.split(" GATES", 1)[1]) if " GATES" in old else ""
        ws.cell(row=r, column=21).value = "self_running"
        ws.cell(row=r, column=22).value = RUN + gates
        n_run += 1
    elif fam in SHOOT_FAMS and str(ws.cell(row=r, column=20).value) == "IMPLEMENTED":
        t = str(ws.cell(row=r, column=22).value)
        assert "MOVING RULE" not in t
        ws.cell(row=r, column=22).value = t + MOVE
        n_move += 1
assert n_run == 1 and n_move > 0, (n_run, n_move)
print("rows: Blooood! 1, moving clause", n_move)

entries, _, _ = bd.mod_entries()
rows = [(r, keys_of(r), str(ws.cell(row=r, column=20).value), str(ws.cell(row=r, column=21).value))
        for r in range(2, ws.max_row + 1)]
impl = [x for x in rows if x[2] == "IMPLEMENTED"]
assert len(impl) == 750
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
assert not [x[1][0] for x in impl if x[3] != fam_by_key.get(x[1][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 60 and trig["self_running"] == 1 and trig["charge_only"] == 4, (len(trig), trig["charge_only"])

n = wb["Numbers"]
assert n.cell(row=105, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert all(int(str(m).split(":")[0][1:]) < 103 for m in n.merged_cells.ranges)
n.insert_rows(103, 1)
assert n.cell(row=106, column=1).value == "Bombardment set (COMPLETE - round 108)"
n.cell(row=7, column=1).value = (
    "Date: 2026-11-13     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v32 - ROUND 140: QA battle 3. Shooting and moving are incompatible unless the unit fires on the move (every "
    "firing-flag trigger); Blooood! on the NEW self_running. Implemented 750 rows / 750 keys and 373 not implemented, "
    "unchanged. The mod: 698 entries / 750 keys / 60 trigger families.)")
n.cell(row=42, column=1).value = (
    "Trigger families after round 140 - re-counted from the mod's own ABILITIES table: 60 families / 698 entries / "
    "750 keys (metallurgy_melee and melee_low_morale keep 0 entries). Round 140: the NEW self_running (1); "
    "charge_only 5 -> 4.")
for r in range(44, 105):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t2, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t2
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t2]
assert 44 + len(fam_sorted) == 104
n.cell(row=104, column=2).value = "TOTAL (60 families)"
n.cell(row=104, column=3).value = sum(trig.values())
n.cell(row=104, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v31")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v32 (2026-11-13)"
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("29. ROUND 140 - QA BATTLE 3: SHOOTING AND MOVING; BLOOOOD! (v32)", None),
    ("THE FINDING", "Boom! cast at 159 s while the Hellcannon was running: its last shot was at 135 s and the firing flag "
     "stays on for max(2 x reload, 20 s) after the last shot."),
    ("THE RULINGS (2026-11-13)", "\"Unless the unit can fire while moving, shooting and moving are incompatible.\" "
     "Blooood!: \"Running, any time\"."),
    ("THE MOVING RULE", "FOURTH.can_shoot_now: a moving unit is not shooting unless its type is in the GENERATED fire_move "
     "set (unit attribute mounted_fire_move, 233 types; tools/gen_fire_move_keys.py). Every firing-flag read uses it, "
     "Missile Mirror's enemy read included."),
    ("THE NEW FAMILY: self_running", "evaluate_self_running | is_moving_fast() | cast target: self | 1 entry / 1 key"),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-13"
ch.cell(row=r, column=2).value = "v32"
ch.cell(row=r, column=3).value = (
    "ROUND 140. QA battle 3: shooting and moving are incompatible unless the unit fires on the move (every firing-flag "
    "trigger); Blooood! on the NEW self_running. Counts unchanged; 60 families. SHIPPED: installed pack md5 %s; harness "
    "139 full suite 6,049 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-13 (QA battle 3); xlsx v32 supersedes v31; v1-v31 byte-unchanged."
wb.save(DST)
print("wrote", DST)
