#!/usr/bin/env python3
"""Build WH3_abilities_master_v29_2026-11-09.xlsx from v28 - round 137: audit batch 6, morale.

(1) 9 entries move from melee_unwavering to the NEW wavering_aura; 5 to wavering_ally_range (each with its own
    70% ally bound). Each keeps its GATES clause.
(2) Counts unchanged (750 / 373); 57 -> 58 families: the Numbers trigger table gains one row (the bombardment
    block moves 103 -> 104). Definitions: title v28 -> v29, glossary, section 26. Changelog: a v29 row.
v1-v28 are never opened for writing.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v28_2026-11-09.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v29_2026-11-09.xlsx"
MU, WA, WR = "melee_unwavering", "wavering_aura", "wavering_ally_range"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
TO_AURA = {"call_of_violence": 35, "get_back_ere": 35, "magical_animus": 35, "rally": 35, "tomb_king_rally": 35,
           "tomb_king_rally_upgraded": 35, "pearl_of_infinite_bleakness": 35, "unholy_clamour": -1,
           "mimic_cold_blooded": None}
TO_ALLY = {"crown_of_command": 100, "doom_lord": 200, "cold_blooded": 200, "pilgrimage_of_skulls": 100,
           "tacticians_rally": 100}


def aura_text(real):
    if real is None:
        arm = "; the effect reaches the caster only, so no ally counts (user ruling round 137)"
    elif real < 0:
        arm = ("; otherwise ANY tracked ally (alive, not the owner, not routing) with is_wavering() exactly true - "
               "the aura covers the whole army (effect_range -1)")
    else:
        arm = ("; otherwise the CLOSEST tracked ally (alive, not the owner, not routing) with is_wavering() exactly "
               "true within the aura bound by unit_distance; bound: %d m (70%% of the ability's %d m effect_range)"
               % (int(real * 0.70 + 1e-9), real))
    return (WA + ": not routing; the caster's is_wavering() exactly true fires at once (unreadable = no fire)" + arm +
            "; cast target: self (the aura is centred on the caster); " + SHARED_TAIL)


def ally_text(real):
    return (WR + ": not routing; the CLOSEST tracked ally that is alive, not the owner, not routing and is_wavering() "
            "== true within the entry's bound; the ally need NOT be in melee and the owner need not be wavering; "
            "bound: %d m (70%% of the ability's %d m ally cast reach); cast target: that ally (cast on the ally); "
            "pre-cast re-check: the chosen ally must still be alive, still wavering and still within the bound, else "
            "the cast is skipped; " % (int(real * 0.70 + 1e-9), real) + SHARED_TAIL)


assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
row_of = {}
for r in range(2, ws.max_row + 1):
    for k in keys_of(r):
        row_of.setdefault(k, []).append(r)
entries, _, _ = bd.mod_entries()
by_marker = {e["marker"]: e for e in entries}
n_rows = 0
for group, fam, textf in ((TO_AURA, WA, aura_text), (TO_ALLY, WR, ally_text)):
    for m, real in group.items():
        for k in by_marker[m]["keys"]:
            for r in row_of[k]:
                assert str(ws.cell(row=r, column=20).value) == "IMPLEMENTED" and str(ws.cell(row=r, column=21).value) == MU, (m, r)
                old = str(ws.cell(row=r, column=22).value or "")
                gates = (" GATES" + old.split(" GATES", 1)[1]) if " GATES" in old else ""
                ws.cell(row=r, column=21).value = fam
                ws.cell(row=r, column=22).value = textf(real) + gates
                n_rows += 1
assert n_rows == 14, n_rows
print("rows retriggered:", n_rows)

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
assert len(trig) == 58 and (trig[MU], trig[WA], trig[WR]) == (314, 9, 6), (len(trig), trig[MU], trig[WA], trig[WR])

n = wb["Numbers"]
assert n.cell(row=103, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert all(int(str(m).split(":")[0][1:]) < 101 for m in n.merged_cells.ranges)
n.insert_rows(101, 1)
assert n.cell(row=104, column=1).value == "Bombardment set (COMPLETE - round 108)"
n.cell(row=7, column=1).value = (
    "Date: 2026-11-09     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v29 - ROUND 137: audit batch 6, morale. Call of Violence, Get Back 'Ere!, Magical Animus, Rally!, Reanimate (both), "
    "Pearl of Infinite Bleakness, Unholy Clamour and Mirror (Cold-Blooded) on the NEW wavering_aura; Crown of Command, "
    "Doom Lord, Cold-Blooded, Pilgrimage of Skulls and Tacticians, Rally! on wavering_ally_range. Implemented 750 rows / "
    "750 keys and 373 not implemented, unchanged. The mod: 698 entries / 750 keys / 58 trigger families.)")
n.cell(row=42, column=1).value = (
    "Trigger families after round 137 - re-counted from the mod's own ABILITIES table: 58 families / 698 entries / "
    "750 keys (metallurgy_melee keeps 0 entries). Round 137: the NEW wavering_aura (9); wavering_ally_range 1 -> 6; "
    "melee_unwavering 328 -> 314.")
for r in range(44, 103):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t]
assert 44 + len(fam_sorted) == 102
n.cell(row=102, column=2).value = "TOTAL (58 families)"
n.cell(row=102, column=3).value = sum(trig.values())
n.cell(row=102, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v28")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v29 (2026-11-09)"
g = d.cell(row=21, column=1)
g.value = str(g.value) + "; the round-137 family (wavering_aura) in section 26"
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("26. ROUND 137 - AUDIT BATCH 6: MORALE (v29)", None),
    ("THE RULINGS (2026-11-09)", "Morale-only auras: \"Self or ally wavering\". Single-target Unbreakable / Leadership "
     "spells, Tacticians, Rally! and Pilgrimage of Skulls: \"On the wavering ally\" (the rampage arm dropped: no battle "
     "read exists). Morale plus a combat stat and the five on dedicated triggers: kept. Vigour: a one-by-one review "
     "later, \"Tired or worse\" as the line."),
    ("THE NEW FAMILY: wavering_aura", "evaluate_wavering_aura | the caster wavering, or a friendly unit inside the "
     "aura's 70% bound wavering (the whole army for Unholy Clamour, nobody else for Mirror (Cold-Blooded)) | cast "
     "target: self | 9 entries / 9 keys"),
    ("THE ARITHMETIC", "Implemented 750 rows / keys and 373 not implemented, unchanged. Mod 698 entries / 750 keys, "
     "57 -> 58 families; melee_unwavering 328 -> 314, wavering_ally_range 1 -> 6."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-09"
ch.cell(row=r, column=2).value = "v29"
ch.cell(row=r, column=3).value = (
    "ROUND 137. Audit batch 6, morale: 9 morale auras on the NEW wavering_aura; Crown of Command, Doom Lord, "
    "Cold-Blooded, Pilgrimage of Skulls, Tacticians, Rally! on wavering_ally_range. Counts unchanged; 58 families. "
    "SHIPPED: installed pack md5 %s; harness 136 full suite 5,948 checks / 0 failures."
    % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-09 (audit batch 6); xlsx v29 supersedes v28; v1-v28 byte-unchanged."
wb.save(DST)
print("wrote", DST)
