#!/usr/bin/env python3
"""Build WH3_abilities_master_v20_2026-10-20.xlsx from v19.

ROUND 121 - THE USER'S RULING ON ARMY-BAR ABILITIES, applied in full.

    "The triggers will not work if the ability is not in the ability wheel on
     the lower left corner of the battle screen, meaning 'you'd lose working
     triggers' makes no sense. Therefore, ALL ARMY ABILITIES PLEASE EXCLUDE."

(1) ALL 17 remaining army_spec (army-bar) rows move from IN-WHEEL to EXCLUDED,
    with the ruling reason. They were listed but NOT moved in v19; that was
    wrong: an army-bar ability has no button on the battle ability wheel, so
    perform_special_ability can never be called for it.
(2) The 4 IMPLEMENTED rows among them are marked REMOVED (their keys are gone
    from the mod in this round): 742 implemented rows / keys -> 738.
(3) Every count is re-derived from the edited sheet and the mod's own table:
    1,800 = 1,123 IN-WHEEL + 677 EXCLUDED; 1,123 = 738 implemented + 385 not.
(4) The trigger-family table is re-derived too: 45 families, 687 entries /
    738 keys.
(5) Definitions gains section 17 and the Changelog a round-121 entry naming the
    ruling, the 17 rows, the 4 removed entries and the three permanent gates.

v1-v19 are never opened for writing: a NEW filename is written.
"""
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v19_2026-10-20.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v20_2026-10-20.xlsx"
UAB = r"C:\Users\vlady\AppData\Local\Temp\wh3\unit_abilities.tsv"
ARMY_SPEC = r"C:\Users\vlady\AppData\Local\Temp\wh3\army_spec.tsv"

RULING_REASON = ("excluded (army-bar ability - army_spec junction - not in the battle ability "
                 "wheel, so it can never be cast; user ruling round 121)")
REMOVED_IMPL = "REMOVED (army-bar: not in the battle wheel, cannot be cast)"

EXPECTED = {
    "wh2_dlc15_character_abilities_wardens_cage",
    "wh3_dlc20_cataclysm_bound_ashes_and_dust",
    "wh3_dlc20_cataclysm_bound_dance_of_despair",
    "wh3_dlc20_cataclysm_bound_gehennas_golden_globe",
    "wh3_dlc20_cataclysm_bound_magma_storm",
    "wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment",
    "wh3_dlc20_cataclysm_bound_storm_of_renewal",
    "wh3_dlc20_cataclysm_bound_time_amok",
    "wh3_dlc27_cataclysm_bound_ashes_and_dust",
    "wh3_dlc27_cataclysm_bound_dance_of_despair",
    "wh3_dlc27_cataclysm_bound_gehennas_golden_globe",
    "wh3_dlc27_cataclysm_bound_magma_storm",
    "wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment",
    "wh3_dlc27_cataclysm_bound_storm_of_renewal",
    "wh3_dlc27_cataclysm_bound_time_amok",
    "wh3_dlc29_army_abilities_pestilential_bombardment",
    "wh3_main_cataclysm_khorne_greater_gate_of_khorne",
}

army = set()
with open(ARMY_SPEC, encoding="utf-8", errors="replace") as f:
    f.readline()
    for line in f:
        if line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        if c and c[0].strip():
            army.add(c[0].strip())

shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]

# ------------------------------------------------------------------ (1)+(2) the 17 rows
moved, removed_impl = [], []
for r in range(2, ws.max_row + 1):
    keys = [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
    if str(ws.cell(row=r, column=18).value) != "IN-WHEEL":
        continue
    if not any(k in army for k in keys):
        continue
    assert str(ws.cell(row=r, column=19).value).startswith(("carrier family:", "skipped ")), \
        ws.cell(row=r, column=19).value
    item = ws.cell(row=r, column=1).value
    name = ws.cell(row=r, column=2).value
    impl = str(ws.cell(row=r, column=20).value or "")
    ws.cell(row=r, column=18).value = "EXCLUDED"
    ws.cell(row=r, column=19).value = RULING_REASON
    if impl == "IMPLEMENTED":
        ws.cell(row=r, column=20).value = REMOVED_IMPL
        ws.cell(row=r, column=21).value = "-"
        ws.cell(row=r, column=22).value = "-"
        removed_impl.append((item, name, keys[0]))
    moved.append((item, name, keys[0]))
moved_keys = set(k for _, _, k in moved)
assert moved_keys == EXPECTED, (sorted(moved_keys ^ EXPECTED), len(moved_keys))
assert len(moved) == 17, len(moved)
assert len(removed_impl) == 4, removed_impl
print("moved to EXCLUDED:", len(moved))
print("marked REMOVED (implemented):", len(removed_impl))

# ------------------------------------------------------------------ (3) recount
rows = []
for r in range(2, ws.max_row + 1):
    keys = [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
    rows.append((r, ws.cell(row=r, column=1).value, ws.cell(row=r, column=2).value, keys,
                 str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=19).value),
                 str(ws.cell(row=r, column=20).value), str(ws.cell(row=r, column=21).value)))
N = len(rows)
status = collections.Counter(x[4] for x in rows)
impl = collections.Counter(x[6] for x in rows)
assert set(status) == {"IN-WHEEL", "EXCLUDED"}, status
N_IN, N_EX = status["IN-WHEEL"], status["EXCLUDED"]
assert (N, N_IN, N_EX) == (1800, 1123, 677), (N, N_IN, N_EX)
N_IMPL_ROWS = impl["IMPLEMENTED"]
N_IMPL_KEYS = len(set(k for x in rows if x[6] == "IMPLEMENTED" for k in x[3]))
assert (N_IMPL_ROWS, N_IMPL_KEYS) == (738, 738), (N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = N_IN - N_IMPL_ROWS
assert NOT_IMPL_IN == 385
# no IN-WHEEL row now carries an army_spec key
assert not [x for x in rows if x[4] == "IN-WHEEL" and any(k in army for k in x[3])]

# the mod's own table
entries, consts, tips = bd.mod_entries()
mod_keys = set(k for e in entries for k in e["keys"])
assert (len(entries), len(mod_keys)) == (687, 738), (len(entries), len(mod_keys))
assert not (mod_keys & army), sorted(mod_keys & army)
# every IMPLEMENTED row is still a key in the mod, and every mod key is an IMPLEMENTED row
impl_rows_keys = set(k for x in rows if x[6] == "IMPLEMENTED" for k in x[3])
assert impl_rows_keys == mod_keys, (sorted(impl_rows_keys - mod_keys)[:5],
                                    sorted(mod_keys - impl_rows_keys)[:5])

# source_type join for the included family block
src_type = {}
with open(UAB, encoding="utf-8", errors="replace") as f:
    hdr = f.readline().rstrip("\n").split("\t")
    si = hdr.index("source_type")
    for line in f:
        if line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        if len(c) > si:
            src_type.setdefault(c[0].strip(), c[si].strip())

fam_order = ["active", "bound", "rune", "item", "lord", "character", "unit", "weapon"]
fam_inc = collections.Counter()
fam_impl = collections.Counter()
for x in rows:
    if x[4] != "IN-WHEEL":
        continue
    f = None
    for k in x[3]:
        if k in src_type:
            f = src_type[k]
            break
    assert f in fam_order, ("no source_type for an included row", x[0], x[3])
    fam_inc[f] += 1
    if x[6] == "IMPLEMENTED":
        fam_impl[f] += 1
assert sum(fam_inc.values()) == N_IN, (sum(fam_inc.values()), N_IN)
assert sum(fam_impl.values()) == N_IMPL_ROWS, (sum(fam_impl.values()), N_IMPL_ROWS)

exc_spell = sum(1 for x in rows if x[6] == "NOT IMPLEMENTED" and x[5].startswith("excluded family: spell"))
exc_army = (sum(1 for x in rows if x[5].startswith("excluded family: army"))
            + sum(1 for x in rows if x[5].startswith("skipped (round 106: army-bar"))
            + sum(1 for x in rows if x[5].startswith("excluded (army-bar ability")))
exc_cat = sum(1 for x in rows if x[5].startswith("excluded family: cataclysm"))
exc_quest = sum(1 for x in rows if x[5].startswith("excluded family: quest"))
exc_boss = sum(1 for x in rows if x[5].startswith("boss-only"))
exc_ill = sum(1 for x in rows if x[5].startswith("illusion"))
assert (exc_spell, exc_army, exc_cat, exc_quest, exc_boss, exc_ill) == (418, 223, 16, 1, 15, 4), \
    (exc_spell, exc_army, exc_cat, exc_quest, exc_boss, exc_ill)
assert exc_spell + exc_army + exc_cat + exc_quest + exc_boss + exc_ill == N_EX

# the trigger-family table, straight from the mod
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    for _k in e["keys"]:
        trig_keys[e["trigger"]] += 1
assert len(trig) == 45 and sum(trig.values()) == 687 and sum(trig_keys.values()) == 738, \
    (len(trig), sum(trig.values()), sum(trig_keys.values()))
assert "ally_infinite_buff" not in trig

# ------------------------------------------------------------------ Numbers
n = wb["Numbers"]
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-10-20     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v20 - ROUND 121, ALL ARMY-BAR ABILITIES EXCLUDED. The user's ruling, verbatim: 'The triggers "
    "will not work if the ability is not in the ability wheel on the lower left corner of the battle "
    "screen, meaning \"you'd lose working triggers\" makes no sense. Therefore, ALL ARMY ABILITIES "
    "PLEASE EXCLUDE.' An army-bar ability is not on the wheel, so perform_special_ability can never "
    "be called for it: it can never fire. (a) ALL 17 rows that still read IN-WHEEL on an army_spec "
    "(army-bar) key are EXCLUDED now: 1,140 - 17 = 1,123 IN-WHEEL and 660 + 17 = 677 EXCLUDED, "
    "1,123 + 677 = 1,800. (b) FOUR of the 17 were IMPLEMENTED and their keys are REMOVED from the "
    "mod: 742 - 4 = 738 implemented rows / 738 keys, and 'not implemented among the included' "
    "398 - 13 = 385 (738 + 385 = 1,123). (c) The mod's ABILITIES table is 687 entries / 738 keys "
    "(was 689 / 742): 2 whole entries removed (merciws_monstrous_regiment, 2 keys; wardens_cage, "
    "1 key) and 1 key removed from a kept entry (greater_gate_of_khorne keeps its in-wheel "
    "character key). 0 army_spec keys remain anywhere in either file.)")

n.cell(row=9, column=4).value = "% of total (1,800)"
n.cell(row=9, column=5).value = "% of included (1,123)"
measures = [
    (10, 1, "Total active abilities (the inventory)", N, 1.0, "-"),
    (11, 2, "Excluded - not in the ability wheel", N_EX, N_EX / tot, "-"),
    (12, 3, "Included - in the ability wheel", N_IN, N_IN / tot, 1.0),
    (13, 4, "Implemented among the included", N_IMPL_ROWS, N_IMPL_ROWS / tot, N_IMPL_ROWS / float(N_IN)),
    (14, 5, "Not implemented among the included", NOT_IMPL_IN, NOT_IMPL_IN / tot, NOT_IMPL_IN / float(N_IN)),
    (15, 6, "Implemented but OUTSIDE the rule (reported separately)", 0, 0, 0),
    (16, 7, "All implemented in the mod (4 + 6)", N_IMPL_KEYS, N_IMPL_KEYS / tot, N_IMPL_KEYS / float(N_IN)),
]
for r, num, label, abs_, p1, p2 in measures:
    n.cell(row=r, column=1).value = num
    n.cell(row=r, column=2).value = label
    n.cell(row=r, column=3).value = abs_
    n.cell(row=r, column=4).value = p1
    n.cell(row=r, column=5).value = p2

n.cell(row=18, column=1).value = (
    "Included, by carrier family (unit_abilities.source_type) - ROW-LEVEL count, derived from this "
    "workbook's own 1,123 IN-WHEEL rows joined to unit_abilities.source_type by exact key: it TIES "
    "to the headline (sum = 1,123 included, 738 implemented). The 17 army-bar rows that left the "
    "wheel in round 121 are no longer here: 1,140 - 17 = 1,123.")
for i, f in enumerate(fam_order):
    r = 20 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = f
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=1).value = None
n.cell(row=28, column=2).value = "Total included (ties to row 12)"
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=28, column=5).value = None

n.cell(row=30, column=1).value = "The %d exclusions, by family - ROW count" % N_EX
n.cell(row=31, column=2).value = "Family"
n.cell(row=31, column=3).value = "Rows"
excl = [(32, 1, "Spells (source_type = spell)", exc_spell),
        (33, 2, "Army-bar abilities (source_type = army, the 2 army_spec-junction bound keys "
                "corrected in round 120, and the 17 army_spec rows excluded in round 121)", exc_army),
        (34, 3, "Cataclysm spells (source_type = cataclysm)", exc_cat),
        (35, 4, "Quest-battle army ability (source_type = quest)", exc_quest),
        (36, 5, "Boss-only unit (granted only to a _boss unit)", exc_boss),
        (37, 6, "Illusion summons (spawn_is_decoy)", exc_ill)]
for r, num, label, cnt in excl:
    n.cell(row=r, column=1).value = num
    n.cell(row=r, column=2).value = label
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = cnt / tot
    n.cell(row=r, column=5).value = cnt / float(N_EX)
n.cell(row=38, column=1).value = None
n.cell(row=38, column=2).value = "Total excluded (ties to row 11)"
n.cell(row=38, column=3).value = sum(c for _, _, _, c in excl)

n.cell(row=40, column=1).value = (
    "Reconciliation (v20): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the "
    "included 738 + not implemented 385 = 1,123. The mod's ABILITIES table is 687 entries / 738 "
    "keys, and the join mod-key -> 'Ability key(s)' returns 738 / 738 with ZERO unmatched keys in "
    "either direction (round 121 audit). 689 - 2 = 687 entries and 742 - 4 = 738 keys: two whole "
    "entries removed (merciws_monstrous_regiment 2 keys, wardens_cage 1 key) and one army-bar key "
    "removed from the kept greater_gate_of_khorne entry. The per-carrier-family block above is a "
    "ROW-level count that ties to this line. NO army-bar (army_spec) key remains in the mod: 0.")

n.cell(row=42, column=1).value = (
    "Trigger families after round 121 - re-counted from the mod's own ABILITIES table: 45 families / "
    "687 entries / 738 keys / 46 evaluators. Round 121 removed the ally_infinite_buff family with "
    "Merciw's Monstrous Regiment (its evaluator and tip line stay - generic machinery), took "
    "enemy_engaged_or_shot from 86 to 85 (Warden's Cage) and left every other family untouched.")

for r in range(44, 91):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t]
tot_row = 44 + len(fam_sorted)
assert tot_row == 89, tot_row
n.cell(row=tot_row, column=2).value = "TOTAL (45 families / 46 evaluators)"
n.cell(row=tot_row, column=3).value = sum(trig.values())
n.cell(row=tot_row, column=4).value = sum(trig_keys.values())

n.cell(row=101, column=1).value = (
    str(n.cell(row=101, column=1).value).split(" (5) IMPLEMENTED")[0] +
    " [ROUND 120 HISTORY - the arithmetic below describes v19. Round 121 then applied the SAME "
    "army-bar rule to the 17 rows this block only flagged: see the round-121 block underneath.]")

# the round-120 "moved / flagged" block is superseded: rewrite it as round 121
for r in range(103, 110):
    n.cell(row=r, column=1).value = None
n.cell(row=103, column=1).value = (
    "ROUND 121 - ALL 17 ARMY-BAR ROWS MOVED TO EXCLUDED, AND THE 4 MOD ENTRIES REMOVED")
n.cell(row=104, column=1).value = "Moved to EXCLUDED (v19 item # | name | army_spec key | new status)"
order = sorted(moved)
for i, (item, name, key) in enumerate(order):
    n.cell(row=105 + i, column=1).value = (
        "%s | %s | %s | EXCLUDED (was IN-WHEEL). %s"
        % (item, name, key,
           REMOVED_IMPL + " - key removed from the mod" if any(item == ri[0] for ri in removed_impl)
           else "Implementation stays NOT IMPLEMENTED"))
base = 105 + len(order)
n.cell(row=base, column=1).value = (
    "Arithmetic: 1,140 - 17 = 1,123 IN-WHEEL; 660 + 17 = 677 EXCLUDED; 1,123 + 677 = 1,800. "
    "Implemented 742 - 4 = 738 rows = 738 keys; not implemented among the included 398 - 13 = 385; "
    "738 + 385 = 1,123. Exclusions by family: spell 418 + army-bar 206 + 17 = 223 + cataclysm 16 + "
    "quest 1 + boss 15 + illusion 4 = 677.")
n.cell(row=base + 1, column=1).value = (
    "The mod: ABILITIES 689 entries / 742 keys -> 687 / 738. Removal shape: TWO WHOLE ENTRIES "
    "(merciws_monstrous_regiment, 2 army-bar keys; wardens_cage, 1) and ONE KEY removed from a KEPT "
    "entry (greater_gate_of_khorne keeps wh3_main_character_abilities_greater_gate_of_khorne). The "
    "dead per-key data rows for those 4 keys (charge pool, wind-up, enemy-ground set) are gone too: "
    "0 army_spec keys anywhere in either file. Gates: tools/audit_wheel_status.py G3 fails on ANY "
    "IN-WHEEL row carrying an army_spec key (no baseline, no exceptions); tools/build_and_install.py "
    "refuses to build if any ABILITIES key is in the army_spec set; "
    "tools/verify_ability_database.py asserts the same on the regenerated database.")

# ------------------------------------------------------------------ Definitions
d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v19")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v20 (2026-10-20)"

r5 = d.cell(row=5, column=1)
assert "660 abilities are out and 1,140 are in" in r5.value
r5.value = r5.value.replace("660 abilities are out and 1,140 are in",
                            "677 abilities are out and 1,123 are in")
r5.value = r5.value.replace("Bound spells (176)", "Bound spells (%d)" % fam_inc["bound"])

r9 = d.cell(row=9, column=2)
assert "1,140 rows" in r9.value
r9.value = r9.value.replace("1,140 rows", "1,123 rows")

r10 = d.cell(row=10, column=2)
assert "(660 rows)" in r10.value
r10.value = r10.value.replace("(660 rows)", "(677 rows)").replace("army (206)", "army (223)")

r11 = d.cell(row=11, column=2)
assert "742 keys across 742 numbered rows" in r11.value
r11.value = r11.value.replace(
    "742 keys across 742 numbered rows",
    "738 keys across 738 numbered rows (round 121 removed the 4 implemented army-bar keys)")

r12 = d.cell(row=12, column=2)
assert "of which 398 are in the wheel" in r12.value
r12.value = r12.value.replace("of which 398 are in the wheel", "of which 385 are in the wheel")

# the coverage sentence: re-count off the edited rows
cov_gate = sum(1 for x in rows if x[6] == "IMPLEMENTED"
               and any(w in x[5] or w in str(ws.cell(row=x[0], column=22).value or "")
                       for w in ("wind-up", "charge gate", "recharge_time", "in-flight", "per-unit")))
r104 = d.cell(row=104, column=1)
assert "of the 742 implemented rows (742 keys)" in str(r104.value)
r104.value = (str(r104.value).split("Coverage in this workbook:")[0]
              + "Coverage in this workbook: %d of the %d implemented rows (%d keys) carry at least one "
              "gate clause in their Trigger (as implemented) text; rows with neither a multi-use pool "
              "nor a wind-up keep the plain 2 s guard. BOMBARDMENT SET (round 108): all 55 wheel "
              "bombardment abilities are implemented - the 55 = 58 unit-side wh_type_bombardment rows "
              "minus the 3 army-bar junctions (Thorsen's Thunderstorm x2, Bubonic Broadside), and "
              "round 121 removed Bubonic Broadside's row from the wheel altogether."
              % (cov_gate, N_IMPL_ROWS, N_IMPL_KEYS))

base = d.max_row + 2
sec = [
    ("17. ROUND 121 - ALL ARMY-BAR ABILITIES ARE EXCLUDED (the user's ruling), AND WHAT NOW STOPS THEM",
     None),
    ("THE RULING, VERBATIM",
     "The triggers will not work if the ability is not in the ability wheel on the lower left corner "
     "of the battle screen, meaning \"you'd lose working triggers\" makes no sense. Therefore, ALL "
     "ARMY ABILITIES PLEASE EXCLUDE."),
    ("WHY IT IS RIGHT",
     "An army-bar ability (a row in army_special_abilities_tables - a key in the army_spec junction) "
     "has no button on the battle ability wheel. perform_special_ability is therefore never callable "
     "for it, so an ABILITIES entry carrying such a key can never fire: it is dead weight, and it "
     "cannot be IN-WHEEL. v19 listed 17 such rows and moved none of them, on the mistaken ground "
     "that moving them would cost working triggers. It could not: there was nothing working to lose."),
    ("WHAT MOVED - 17 ROWS / 17 KEYS",
     "Warden's Cage (1), Greater Gate of Khorne's cataclysm key (1), Merciw's Monstrous Regiment "
     "(2 rows / 2 keys), Bubonic Broadside (1), and the 12 cataclysm_bound twins - Ashes & Dust x2, "
     "Dance of Despair x2, Gehenna's Golden Globe x2, Magma Storm x2, Storm of Renewal x2, Time Amok "
     "x2. All 17 are EXCLUDED with the reason 'excluded (army-bar ability - army_spec junction - not "
     "in the battle ability wheel, so it can never be cast; user ruling round 121)'."),
    ("WHAT LEFT THE MOD - 4 KEYS IN 3 ENTRIES",
     "Two WHOLE entries: merciws_monstrous_regiment (2 keys, both army-bar) and wardens_cage (1 key). "
     "One KEY from a KEPT entry: greater_gate_of_khorne loses "
     "wh3_main_cataclysm_khorne_greater_gate_of_khorne and keeps its in-wheel "
     "wh3_main_character_abilities_greater_gate_of_khorne. The dead per-key data rows (charge pool, "
     "wind-up table, enemy-ground set) went with them. 689 entries / 742 keys -> 687 / 738; 0 "
     "army_spec keys remain anywhere in the shipped source or the annotated copy."),
    ("THE THREE PERMANENT GATES",
     "(1) tools/audit_wheel_status.py - gate G3 FAILS on ANY row marked IN-WHEEL that carries an "
     "army_spec key; the old 17-row BASELINE and every exceptions list were deleted, so the gate "
     "cannot be satisfied by documenting a violation. (2) tools/build_and_install.py - an assertion "
     "BEFORE any pack is deleted or any RPFM command is sent refuses the build if any ABILITIES key "
     "is in the army_spec set: 'BUILD REFUSED (round 121 army-bar gate): N ABILITIES key(s) are in "
     "the army_spec junction ... Offending keys: [...]'. (3) tools/verify_ability_database.py - "
     "assertion A0 fails the database verification on the same test, so a regenerated database "
     "cannot bless a mod table that carries one."),
    ("THE ARITHMETIC",
     "1,140 - 17 = 1,123 IN-WHEEL; 660 + 17 = 677 EXCLUDED; 1,123 + 677 = 1,800. Implemented "
     "742 - 4 = 738 rows = 738 keys; not implemented among the included 398 - 13 = 385; "
     "738 + 385 = 1,123. Exclusions: 418 spell + 223 army-bar + 16 cataclysm + 1 quest + 15 boss + "
     "4 illusion = 677."),
    ("NO TRIGGER WAS LOST",
     "The three removed entries' evaluators: ally_infinite_buff's evaluator and tip line remain in "
     "the mod as generic machinery (now unused); enemy_engaged_or_shot keeps 85 entries (Warden's "
     "Cage was one); enemy_ground_melee keeps 66 entries (the Greater Gate entry survives on its "
     "wheel key). The full suite (harness 120) is 4,767 checks / 0 failures, run twice byte-identical."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

# ------------------------------------------------------------------ Changelog
ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-10-20"
ch.cell(row=r, column=2).value = "v20"
ch.cell(row=r, column=3).value = (
    "ROUND 121 - ALL ARMY-BAR ABILITIES EXCLUDED, BY THE USER'S RULING. Ruling, verbatim: 'The "
    "triggers will not work if the ability is not in the ability wheel on the lower left corner of "
    "the battle screen, meaning \"you'd lose working triggers\" makes no sense. Therefore, ALL ARMY "
    "ABILITIES PLEASE EXCLUDE.' An army-bar ability has no wheel button, so perform_special_ability "
    "can never be called for it and the entry can never fire - there was never a working trigger to "
    "lose. (1) THE 17 ROWS: every army_spec row still marked IN-WHEEL (Warden's Cage, Greater Gate of "
    "Khorne's cataclysm key, Merciw's Monstrous Regiment x2, Bubonic Broadside, and the 12 "
    "cataclysm_bound twins of Ashes & Dust / Dance of Despair / Gehenna's Golden Globe / Magma Storm "
    "/ Storm of Renewal / Time Amok) is EXCLUDED with reason 'excluded (army-bar ability - army_spec "
    "junction - not in the battle ability wheel, so it can never be cast; user ruling round 121)'. "
    "1,140 - 17 = 1,123 IN-WHEEL; 660 + 17 = 677 EXCLUDED. (2) THE MOD: 3 entries / 4 keys removed - "
    "merciws_monstrous_regiment (whole, 2 keys) and wardens_cage (whole, 1 key) went, and "
    "greater_gate_of_khorne kept its entry and lost its army-bar cataclysm key. 689 / 742 -> 687 / "
    "738; those 4 rows are marked REMOVED (army-bar: not in the battle wheel, cannot be cast), so "
    "742 - 4 = 738 implemented rows / keys and 398 - 13 = 385 not implemented among the included. "
    "(3) THREE PERMANENT GATES so it cannot recur: audit_wheel_status.py G3 fails on ANY IN-WHEEL row "
    "carrying an army_spec key (the 17-row baseline and all exceptions deleted); build_and_install.py "
    "refuses to build if any ABILITIES key is in the army_spec set; verify_ability_database.py "
    "asserts the same. (4) THE NUMBERS ARE RE-DERIVED from the edited sheet and the mod's own table: "
    "45 trigger families / 687 entries / 738 keys / 46 evaluators; exclusions 418 + 223 + 16 + 1 + 15 "
    "+ 4 = 677. (5) SHIPPED: the rebuilt pack (5 files byte-identical, md5 %s)"
    % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = (
    "user ruling 2026-10-20 (round 121) - data, mod, gates and documentation; xlsx v20 supersedes "
    "v19; v1-v19 byte-unchanged.")

wb.save(DST)
print("wrote", DST)
print("rows", N, "in-wheel", N_IN, "excluded", N_EX,
      "impl rows", N_IMPL_ROWS, "impl keys", N_IMPL_KEYS, "not-impl in-wheel", NOT_IMPL_IN)
print("families", dict(fam_inc), "impl", dict(fam_impl))
print("exclusions", exc_spell, exc_army, exc_cat, exc_quest, exc_boss, exc_ill)
print("moved:", len(moved), "removed_impl:", removed_impl)
