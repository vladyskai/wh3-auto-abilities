#!/usr/bin/env python3
"""Build WH3_abilities_master_v35_2026-11-13.xlsx from v34 - round 143: open batch 2.

(1) 11 rows NOT IMPLEMENTED -> IMPLEMENTED: The Curse of Anraheir (3 keys), Transmutation of Lead, Soulblight
    (Doomfire), The Soulstealer, Squig Thinkin', Spinning Loons, The Loons of Eight Peaks on enemy_ground_melee; Curse
    of Djaf on the NEW enemy_ground_shooting; Soulblight (Handmaidens) on melee_unwavering.
(2) Implemented 756 -> 767 rows / keys; not implemented among the included 367 -> 356. The mod 712 entries / 767 keys;
    67 -> 68 families: the Numbers trigger table gains one row (bombardment block 113 -> 114). Definitions: title v35,
    the two count rows, section 32. Changelog: a v35 row.
v1-v34 are never opened for writing.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v34_2026-11-13.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v35_2026-11-13.xlsx"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
RULE = "user ruling 2026-11-13 (open batch 2); "


def egm(bound, real, extra=""):
    return ("enemy_ground_melee: not routing; enumerate the main enemy army; keep enemies alive (>0 men), validity not "
            "false, FIGHTING (is_in_melee() == true) and within the ability's own 70%% bound (%d m of %d m; "
            "unit:unit_distance only - never unit_in_range)%s; pick the CLOSEST; re-fetch the caster controller AND the "
            "enemy the SAME tick; re-check (alive + still in melee + still within the bound) immediately before the cast "
            "and skip if it lapsed; cast perform_special_ability_ground(key, ENEMY:position(), 0, 0) - the position is "
            "the ENEMY's, never the caster's; " % (bound, real, extra) + RULE + "\"Fighting enemy\"; " + SHARED_TAIL)


DJAF = ("enemy_ground_shooting: not routing; the enemy_missile_shooting pick (main enemy army; alive; validity not false; "
        "target class missile; SHOOTING = its ammo_left() dropped within ENEMY_AMMO_FRESH_S = 2 s and the last drop lies "
        "inside the firing-flag window; an unreadable enemy ammunition never fires; not in melee; within the bound; the "
        "closest wins); bound: 70 m (70% of the ability's 100 m reach); cast target: the GROUND under that enemy "
        "(perform_special_ability_ground at the ENEMY's position); pre-cast re-check: still alive, shooting, not in melee "
        "and within the bound; " + RULE + "\"Shooting enemy\"; " + SHARED_TAIL)
HAND = ("melee_unwavering: not routing; is_in_melee(); is_wavering() must NOT be true - false and unreadable both pass "
        "(fail-open morale); cast target: self; " + RULE + "\"In melee\"; " + SHARED_TAIL)
NF = "; target class not_flying (live is_currently_flying() must read exactly false)"
NEW = {"wh2_dlc16_spell_bound_the_curse_of_anraheir": ("enemy_ground_melee", egm(140, 200)),
       "wh3_main_spell_bound_the_curse_of_anraheir": ("enemy_ground_melee", egm(140, 200)),
       "wh_dlc05_spell_bound_the_curse_of_anraheir": ("enemy_ground_melee", egm(140, 200)),
       "wh3_main_spell_bound_transmutation_of_lead": ("enemy_ground_melee", egm(140, 200)
                                                      + " GATES: in-flight hold 7 s (5 s wind-up + 2 s)."),
       "wh2_dlc10_spell_bound_soulblight": ("enemy_ground_melee", egm(140, 200)
                                            + " GATES: charge hold 90 s (2 uses); in-flight hold 5 s (3 s wind-up + 2 s)."),
       "wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer": ("enemy_ground_melee", egm(70, 100)
                                                                 + " GATES: in-flight hold 5 s (3 s wind-up + 2 s)."),
       "wh2_dlc09_character_abilities_curse_of_djaf": ("enemy_ground_shooting", DJAF),
       "wh3_dlc29_spell_bound_soulblight": ("melee_unwavering", HAND
                                            + " GATES: charge hold 45 s (2 uses); in-flight hold 3 s (1 s wind-up + 2 s)."),
       "wh3_dlc26_character_abilities_squig_thinkin": ("enemy_ground_melee", egm(52, 75)),
       "wh_main_unit_abilities_spinning_loons": ("enemy_ground_melee", egm(17, 25, NF) + " GATES: charge hold 30 s (3 uses)."),
       "wh_dlc06_unit_abilities_the_loons_of_eight_peaks": ("enemy_ground_melee", egm(17, 25, NF)
                                                            + " GATES: charge hold 30 s (3 uses)."),
       }

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
n_new = n_b = 0
for r in range(2, ws.max_row + 1):
    ks = keys_of(r)
    if len(ks) == 1 and ks[0] in NEW:
        assert str(ws.cell(row=r, column=18).value) == "IN-WHEEL" and str(ws.cell(row=r, column=20).value) == "NOT IMPLEMENTED", ks
        fam, text = NEW[ks[0]]
        ws.cell(row=r, column=20).value = "IMPLEMENTED"
        ws.cell(row=r, column=21).value = fam
        ws.cell(row=r, column=22).value = text
        n_new += 1
assert (n_new, n_b) == (11, 0), (n_new, n_b)

rows = [(r, keys_of(r), str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=20).value),
         str(ws.cell(row=r, column=21).value)) for r in range(2, ws.max_row + 1)]
N = len(rows)
impl = [x for x in rows if x[3] == "IMPLEMENTED"]
N_IMPL_ROWS = len(impl)
N_IMPL_KEYS = len(set(k for x in impl for k in x[1]))
assert (N, N_IMPL_ROWS, N_IMPL_KEYS) == (1800, 767, 767), (N, N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = 1123 - N_IMPL_ROWS
assert NOT_IMPL_IN == 356
entries, _, _ = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
assert (len(entries), len(fam_by_key)) == (712, 767)
assert set(k for x in impl for k in x[1]) == set(fam_by_key)
assert not [x[1][0] for x in impl if x[4] != fam_by_key.get(x[1][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 68 and trig["enemy_ground_shooting"] == 1 and trig["enemy_ground_melee"] == 74 and trig["melee_unwavering"] == 307, (len(trig),)

src_type = {}
with open(GP.UNIT_ABILITIES, encoding="utf-8", errors="replace") as f:
    hdr = f.readline().rstrip("\n").split("\t")
    si = hdr.index("source_type")
    for line in f:
        if line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        if len(c) > si:
            src_type.setdefault(c[0].strip(), c[si].strip())
fam_order = ["active", "bound", "rune", "item", "lord", "character", "unit", "weapon"]
fam_inc, fam_impl = collections.Counter(), collections.Counter()
for x in rows:
    if x[2] != "IN-WHEEL":
        continue
    f = next((src_type[k] for k in x[1] if k in src_type), None)
    fam_inc[f] += 1
    if x[3] == "IMPLEMENTED":
        fam_impl[f] += 1

n = wb["Numbers"]
assert n.cell(row=113, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert all(int(str(m).split(":")[0][1:]) < 108 for m in n.merged_cells.ranges)
n.insert_rows(111, 1)
assert n.cell(row=114, column=1).value == "Bombardment set (COMPLETE - round 108)"
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-11-13     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v35 - ROUND 143: open batch 2. The Curse of Anraheir (3 keys), Transmutation of Lead, Soulblight (Doomfire), The "
    "Soulstealer, Squig Thinkin', Spinning Loons and The Loons of Eight Peaks on enemy_ground_melee; Curse of Djaf on "
    "the NEW enemy_ground_shooting; Soulblight (Handmaidens) on melee_unwavering. Implemented 756 + 11 = 767 rows / 767 "
    "keys; not implemented among the included 367 - 11 = 356. The mod: 712 entries / 767 keys / 68 trigger families.)")
for r, num, label, abs_, p1, p2 in [
        (13, 4, "Implemented among the included", N_IMPL_ROWS, N_IMPL_ROWS / tot, N_IMPL_ROWS / 1123.0),
        (14, 5, "Not implemented among the included", NOT_IMPL_IN, NOT_IMPL_IN / tot, NOT_IMPL_IN / 1123.0),
        (16, 7, "All implemented in the mod (4 + 6)", N_IMPL_KEYS, N_IMPL_KEYS / tot, N_IMPL_KEYS / 1123.0)]:
    for c, v in enumerate((num, label, abs_, p1, p2), 1):
        n.cell(row=r, column=c).value = v
n.cell(row=18, column=1).value = str(n.cell(row=18, column=1).value).replace("756 implemented", "767 implemented")
for i, f in enumerate(fam_order):
    r = 20 + i
    assert n.cell(row=r, column=2).value == f, (r, n.cell(row=r, column=2).value)
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=40, column=1).value = (
    "Reconciliation (v35): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 767 + not "
    "implemented 356 = 1,123. The mod's ABILITIES table is 712 entries / 767 keys, and the join mod-key -> 'Ability "
    "key(s)' returns 767 / 767 with ZERO unmatched keys in either direction. 703 + 9 (round 143, open batch 2) = 712 "
    "entries; 756 + 11 = 767 keys. NO army-bar (army_spec) key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 143 - re-counted from the mod's own ABILITIES table: 68 families / 712 entries / 767 "
    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 143: enemy_ground_melee 67 -> 74 "
    "entries; melee_unwavering 306 -> 307; the NEW enemy_ground_shooting (1).")
for r in range(44, 113):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t2, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t2
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t2]
assert 44 + len(fam_sorted) == 112
n.cell(row=112, column=2).value = "TOTAL (68 families)"
n.cell(row=112, column=3).value = sum(trig.values())
n.cell(row=112, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v34")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v35 (2026-11-13)"
r11 = d.cell(row=11, column=2)
old11 = ("756 keys across 756 numbered rows (rounds 122-123 added 21, round 130 added 2, round 131 removed the 9 "
         "stances, round 134 removed the 2 Thunderburner keys, round 142 added 6)")
assert old11 in r11.value
r11.value = r11.value.replace(old11, "767 keys across 767 numbered rows (rounds 122-123 added 21, round 130 added 2, "
                              "round 131 removed the 9 stances, round 134 removed the 2 Thunderburner keys, round 142 "
                              "added 6, round 143 added 11)")
r12 = d.cell(row=12, column=2)
assert "(1,044 keys, of which 367 are in the wheel)" in r12.value
r12.value = r12.value.replace("(1,044 keys, of which 367 are in the wheel)", "(1,033 keys, of which 356 are in the wheel)")
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("32. ROUND 143 - OPEN BATCH 2 (v35)", None),
    ("THE RULINGS (2026-11-13)", "The Curse of Anraheir, Transmutation of Lead, Soulblight (Doomfire), The Soulstealer: "
     "\"Fighting enemy, all four\". Curse of Djaf: \"Shooting enemy\". Soulblight (Handmaidens): \"In melee\". Squig "
     "Thinkin', Spinning Loons, The Loons of Eight Peaks: \"Fighting enemy, all three\"."),
    ("THE NEW FAMILY", "enemy_ground_shooting (Curse of Djaf): the Missile Mirror pick, placed on the enemy's ground. "
     "The 25 m reach of the fanatic releases -> FOURTH.ENEMY_CAST_R25 = 17; the loons carry target_class not_flying."),
    ("THE ARITHMETIC", "Implemented 756 + 11 = 767 rows / keys; not implemented among the included 367 - 11 = 356. "
     "The mod 703 + 9 = 712 entries / 767 keys; 68 families."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-13"
ch.cell(row=r, column=2).value = "v35"
ch.cell(row=r, column=3).value = (
    "ROUND 143. Open batch 2: The Curse of Anraheir (3 keys), Transmutation of Lead, Soulblight (Doomfire), The "
    "Soulstealer, Squig Thinkin', Spinning Loons, The Loons of Eight Peaks on enemy_ground_melee; Curse of Djaf on the "
    "NEW enemy_ground_shooting; Soulblight (Handmaidens) on melee_unwavering. 756 -> 767 implemented; 367 -> 356 not "
    "implemented. Mod 712 / 767 / 68 families. SHIPPED: installed pack md5 %s; harness 142 full suite 6,194 checks / "
    "0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-13 (open batch 2); xlsx v35 supersedes v34; v1-v34 byte-unchanged."
wb.save(DST)
print("wrote", DST)
