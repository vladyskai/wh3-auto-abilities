#!/usr/bin/env python3
"""Build WH3_abilities_master_v19_2026-10-20.xlsx from v18.

ROUND 120 - three defects the user found, plus the one the review flagged.

(1) WHEEL STATUS vs STATUS REASON. Two rows (Thorsen's Thunderstorm, both keys)
    read IN-WHEEL while their reason/implementation said "skipped (round 106:
    army-bar ability (army_spec junction) - out of wheel scope)". An army-bar
    ability cannot be in the wheel. Both become EXCLUDED and the reason keeps
    its original text with the round-120 correction appended. A hard scan
    asserts no other row can carry that contradiction.
(2) THE ORPHAN KEY. `wh3_main_spell_slaanesh_slicing_shards_bound` is the
    second key of the mod entry `slicing_shards` and had NO row in the
    1,799-row inventory. The row is added next to its shipped twin, with its
    own game-data fields (game tables, not copied numbers), IN-WHEEL,
    IMPLEMENTED, the twin's trigger family and the twin's trigger text (the mod
    carries ONE evaluator for the entry).
(3) NUMBERS. Every figure is recomputed from the edited sheet, in the unit it
    is counted in. THE PER-CARRIER-FAMILY BLOCK IS NOW A ROW-LEVEL COUNT that
    ties to the headline - it used to be an older key-level count (1,143 keys
    against a 1,141-row headline) and could not tie by construction.
(4) The reconciliation names the 17 remaining army_spec-junction rows that
    still read IN-WHEEL, so the same default cannot hide again.

v1-v18 are never opened for writing: a NEW filename is written.
"""
import collections
import shutil

import openpyxl

import build_abilities_master_xlsx as bx

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v18_2026-10-18.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v19_2026-10-20.xlsx"
UAB = r"C:\Users\vlady\AppData\Local\Temp\wh3\unit_abilities.tsv"
ARMY_SPEC = r"C:\Users\vlady\AppData\Local\Temp\wh3\army_spec.tsv"

MISS_KEY = "wh3_main_spell_slaanesh_slicing_shards_bound"
TWIN_KEY = "wh3_dlc20_spell_bound_slicing_shards"
CORRECTION = (" - wheel status corrected in round 120: army-bar abilities are outside the wheel "
              "by the user's own rule")
ARMY_TOKENS = ("army_spec", "army-bar", "army bar", "army ability", "campaign-side junction")

shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]


def row_keys(r):
    return [p.strip() for p in str(ws.cell(row=r, column=3).value or "").split(";") if p.strip()]


key2row = {}
for r in range(2, ws.max_row + 1):
    for k in row_keys(r):
        key2row.setdefault(k, []).append(r)

# ------------------------------------------------------------------ (1) the two rows
moved = []
for r in range(2, ws.max_row + 1):
    reason = str(ws.cell(row=r, column=19).value or "")
    status = str(ws.cell(row=r, column=18).value or "")
    if status != "IN-WHEEL":
        continue
    if not any(t in reason.lower() for t in ARMY_TOKENS):
        continue
    assert r in (key2row.get("wh3_dlc20_cataclysm_bound_thorsens_thunderstorm", []) +
                 key2row.get("wh3_dlc27_cataclysm_bound_thorsens_thunderstorm", [])), \
        ("an unexpected army-bar row reads IN-WHEEL", r, ws.cell(row=r, column=2).value)
    assert CORRECTION.strip() not in reason
    ws.cell(row=r, column=18).value = "EXCLUDED"
    ws.cell(row=r, column=19).value = reason + CORRECTION
    moved.append((r, ws.cell(row=r, column=1).value, ws.cell(row=r, column=2).value,
                  ws.cell(row=r, column=3).value))
assert len(moved) == 2, moved

# the ONE row whose reason cell carried a STATUS string instead of a carrier family
warp_row = key2row["wh2_dlc16_unit_abilities_warp_lightning_rod"][0]
warp_reason = str(ws.cell(row=warp_row, column=19).value)
assert warp_reason.startswith("implemented (melee, skipping Lord/Hero-only fights)"), warp_reason
ws.cell(row=warp_row, column=19).value = (
    "carrier family: active - unit-carried active ability | reason text corrected in round 120: this "
    "cell carried a STATUS string, not a carrier family (the only such row in the sheet) | round 108: "
    "the last of the 55 wheel bombardment keys; in campaign it is granted by the Clan Moulder "
    "Lobotomy mutation")

# ------------------------------------------------------------------ (2) the missing row
assert len(key2row[TWIN_KEY]) == 1
assert MISS_KEY not in key2row, "the key already has a row"
twin_row = key2row[TWIN_KEY][0]
ins = twin_row + 1
ws.insert_rows(ins)
for c in range(1, ws.max_column + 1):
    src_cell = ws.cell(row=twin_row, column=c)
    dst_cell = ws.cell(row=ins, column=c)
    dst_cell._style = src_cell._style          # StyleArray is immutable - safe to share
ws.row_dimensions[ins].height = ws.row_dimensions[twin_row].height or 45

rec = bx.tooltip_record(MISS_KEY)
restr = []
if rec["invalid_target"]:
    restr.append("invalid-target: " + ", ".join("`%s`" % x for x in rec["invalid_target"]))
if rec["invalid_usage"]:
    restr.append("invalid-usage: " + ", ".join("`%s`" % x for x in rec["invalid_usage"]))
if rec["auto_deactivate"]:
    restr.append("auto-deactivate: " + ", ".join("`%s`" % x for x in rec["auto_deactivate"]))

twin_trigger = ws.cell(row=twin_row, column=22).value
twin_reason = ws.cell(row=twin_row, column=19).value

vals = {
    1: ins - 1,                      # renumbered below
    2: "Slicing Shards",
    3: MISS_KEY,
    4: rec["category"], 5: rec["uses"], 6: rec["dps"], 7: rec["stats"],
    8: rec["duration"], 9: rec["radius"], 10: rec["speed"], 11: rec["range"],
    12: rec["phase_durations"], 13: rec["cooldown"], 14: rec["affects"],
    15: rec["can_use"], 16: rec["tactical"], 17: bx.tooltip_full(rec),
    18: "IN-WHEEL",
    19: twin_reason + (" | round 120: the MISSING ROW - this key is the second key of the mod "
                       "entry 'slicing_shards' and had no row in the inventory until v19; its "
                       "cooldown is 0 s because recharge_time is -1 (one use), which is the only "
                       "field that differs from its twin"),
    20: "IMPLEMENTED",
    21: ws.cell(row=twin_row, column=21).value,
    22: twin_trigger,
    23: "; ".join(restr) if restr else "none found",
}
assert vals[21] == "enemy_ground_melee_infantry", vals[21]
for c, v in vals.items():
    ws.cell(row=ins, column=c).value = v

# every row renumbered, so "Item #" is a clean sequence again
for i, r in enumerate(range(2, ws.max_row + 1), 1):
    ws.cell(row=r, column=1).value = i
ws.auto_filter.ref = "A1:W%d" % ws.max_row

# ------------------------------------------------------------------ recount (row level)
rows = [(r, ws.cell(row=r, column=2).value, row_keys(r),
         str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=19).value),
         str(ws.cell(row=r, column=20).value), str(ws.cell(row=r, column=21).value))
        for r in range(2, ws.max_row + 1)]
N = len(rows)
status = collections.Counter(x[3] for x in rows)
impl = collections.Counter(x[5] for x in rows)
assert set(status) == {"IN-WHEEL", "EXCLUDED"}, status
N_IN, N_EX = status["IN-WHEEL"], status["EXCLUDED"]
assert (N, N_IN, N_EX) == (1800, 1140, 660), (N, N_IN, N_EX)
N_IMPL_ROWS = impl["IMPLEMENTED"]
N_IMPL_KEYS = len(set(k for x in rows if x[5] == "IMPLEMENTED" for k in x[2]))
assert (N_IMPL_ROWS, N_IMPL_KEYS) == (742, 742), (N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = N_IN - N_IMPL_ROWS
ALL_KEYS = set(k for x in rows for k in x[2])
assert len(ALL_KEYS) == N, (len(ALL_KEYS), N)      # one key per row

# source_type join, for the included family block
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
    if x[3] != "IN-WHEEL":
        continue
    f = None
    for k in x[2]:
        if k in src_type:
            f = src_type[k]
            break
    assert f in fam_order, ("no source_type for an included row", x[0], x[2])
    fam_inc[f] += 1
    if x[5] == "IMPLEMENTED":
        fam_impl[f] += 1
assert sum(fam_inc.values()) == N_IN, (sum(fam_inc.values()), N_IN)
assert sum(fam_impl.values()) == N_IMPL_ROWS, (sum(fam_impl.values()), N_IMPL_ROWS)

exc_spell = sum(1 for x in rows if x[5] == "NOT IMPLEMENTED" and x[4].startswith("excluded family: spell"))
exc_army = (sum(1 for x in rows if x[4].startswith("excluded family: army"))
            + sum(1 for x in rows if x[4].startswith("skipped (round 106: army-bar")))
exc_cat = sum(1 for x in rows if x[4].startswith("excluded family: cataclysm"))
exc_quest = sum(1 for x in rows if x[4].startswith("excluded family: quest"))
exc_boss = sum(1 for x in rows if x[4].startswith("boss-only"))
exc_ill = sum(1 for x in rows if x[4].startswith("illusion"))
assert (exc_spell, exc_army, exc_cat, exc_quest, exc_boss, exc_ill) == (418, 206, 16, 1, 15, 4), \
    (exc_spell, exc_army, exc_cat, exc_quest, exc_boss, exc_ill)
assert exc_spell + exc_army + exc_cat + exc_quest + exc_boss + exc_ill == N_EX

# the residual army_spec question, counted (not fixed)
army_spec = set()
with open(ARMY_SPEC, encoding="utf-8", errors="replace") as f:
    f.readline()
    for line in f:
        if line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        if c and c[0].strip():
            army_spec.add(c[0].strip())
resid = [x for x in rows if x[3] == "IN-WHEEL" and any(k in army_spec for k in x[2])]
resid_keys = sorted(set(k for x in resid for k in x[2] if k in army_spec))
assert len(resid) == 17, len(resid)
assert len(resid_keys) == 17, len(resid_keys)

# ------------------------------------------------------------------ Numbers
n = wb["Numbers"]
n.cell(row=7, column=1).value = (
    "Date: 2026-10-20     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v19 - ROUND 120, THE THREE DEFECTS + THE NUMBERS BLOCK. (a) TWO ROWS MOVED OUT OF THE WHEEL: "
    "Thorsen's Thunderstorm, both keys, read IN-WHEEL while their reason column said 'skipped (round "
    "106: army-bar ability (army_spec junction) - out of wheel scope)' - an army-bar ability cannot "
    "be in the wheel. They are EXCLUDED now, so the workbook reads 1,140 IN-WHEEL / 660 EXCLUDED = "
    "1,800 (it was 1,141 / 658 / 1,799). (b) ONE ROW ADDED: 'wh3_main_spell_slaanesh_slicing_shards_"
    "bound' is implemented in the mod as the second key of the 'slicing_shards' entry and had no row "
    "anywhere in the inventory - it now has one, IN-WHEEL / IMPLEMENTED, so 742 implemented ROWS "
    "carry 742 implemented keys and every implemented key has a row of its own. (c) THE PER-CARRIER-"
    "FAMILY BLOCK IS RE-DERIVED AS A ROW-LEVEL COUNT from this sheet's own rows and now ties to the "
    "headline exactly; it used to be an older key-level count (1,143 keys) that could not tie to a "
    "1,141-row headline. (d) The reconciliation names the 17 army_spec-junction rows that STILL read "
    "IN-WHEEL and are NOT corrected here - that needs a ruling, because 4 of them are implemented.)")

n.cell(row=9, column=1).value = "#"
n.cell(row=9, column=4).value = "% of total (1,800)"
n.cell(row=9, column=5).value = "% of included (1,140)"
tot = float(N)
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
    "workbook's own 1,140 IN-WHEEL rows joined to unit_abilities.source_type by exact key: it TIES to "
    "the headline (sum = 1,140 included, 742 implemented). The pre-v19 block was an older KEY-level "
    "count (1,143 keys / 638 implemented) and could not tie to a row-level headline by construction; "
    "it has been re-derived, not relabelled.")
fam_rows = [(20 + i, i + 1, f, fam_inc[f], fam_impl[f]) for i, f in enumerate(fam_order)]
for r, num, f, inc, imp in fam_rows:
    n.cell(row=r, column=1).value = num
    n.cell(row=r, column=2).value = f
    n.cell(row=r, column=3).value = inc
    n.cell(row=r, column=4).value = imp
    n.cell(row=r, column=5).value = (imp / float(inc)) if inc else 0
n.cell(row=28, column=1).value = None
n.cell(row=28, column=2).value = "Total included (ties to row 12)"
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=28, column=5).value = None

n.cell(row=30, column=1).value = "The %d exclusions, by family - ROW count" % N_EX
n.cell(row=31, column=2).value = "Family"
n.cell(row=31, column=3).value = "Rows"
excl = [(32, 1, "Spells (source_type = spell)", exc_spell),
        (33, 2, "Army-bar abilities (source_type = army, plus the 2 army_spec-junction bound keys "
                "corrected in round 120)", exc_army),
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
    "Reconciliation (v19): included 1,140 + excluded 660 = 1,800 ROWS. Implemented among the "
    "included 742 + not implemented 398 = 1,140. The mod's ABILITIES table is 689 entries / 742 keys. "
    "All 742 implemented keys now have a row of their own: 742 implemented rows carry 742 distinct "
    "keys, the count of implemented keys is 742, and the join mod-key -> 'Ability key(s)' returns "
    "zero unmatched keys (round 120 audit). The last remainder, 'wh3_main_spell_slaanesh_slicing_"
    "shards_bound', is now a row. The per-carrier-family block above is a ROW-level count that ties "
    "to this line; the pre-v19 block was a KEY-level count of an older vintage and has been "
    "re-derived. NO other count on this sheet moved: the 46 trigger families still sum to 689 "
    "entries / 742 keys.")

n.cell(row=101, column=1).value = (
    "ROUND 120 RECONCILIATION - EACH NUMBER IN THE UNIT IT IS COUNTED IN, AND EACH DEFECT NAMED. "
    "(1) INVENTORY 1,800 ROWS = 1,800 DISTINCT KEYS: 1,799 rows in v18 plus the row added for "
    "'wh3_main_spell_slaanesh_slicing_shards_bound'. %s key STRINGS ride those rows because %d rows "
    "name a base key and its twin together. (2) THE WHEEL STATUS, RECOUNTED HONESTLY: v18 "
    "read 1,141 IN-WHEEL + 658 EXCLUDED. Round 120 moved TWO rows out of the wheel - Thorsen's "
    "Thunderstorm 'wh3_dlc20_cataclysm_bound_thorsens_thunderstorm' (v18 item 1334) and "
    "'wh3_dlc27_cataclysm_bound_thorsens_thunderstorm' (v18 item 1335) - both army_spec junction "
    "entries whose reason column already said so, and added ONE row in-wheel (the Slicing Shards "
    "bound twin). 1,141 - 2 + 1 = 1,140 IN-WHEEL, and 658 + 2 = 660 EXCLUDED; 1,140 + 660 = 1,800. "
    "(3) THE ROOT CAUSE, NAMED SO IT CANNOT RECUR: the Status column was never derived from the "
    "army-bar test. build_abilities_master_xlsx.py computes it as 'IN-WHEEL if unit_abilities."
    "source_type in {active, bound, lord, character, unit, item, rune, weapon}, else EXCLUDED' - the "
    "IN-WHEEL rule's third clause names an army-bar ability only as 'source_type = army', and the "
    "army_spec junction (the table that actually makes an ability an ARMY-BAR button) was never "
    "consulted. Both Thorsen keys are source_type 'bound' (a bound spell), so the classifier put them "
    "IN-WHEEL; round 106 then discovered the army_spec junction and wrote the skip through "
    "make_xlsx_v7.py's SKIP_KEYS loop, which writes columns 19-22 and NEVER column 18 - unlike "
    "set_impl(), which asserts column 18 == IN-WHEEL before it writes. There was no mirror assertion "
    "for skips, so the status kept the classifier's IN-WHEEL and the reason said army-bar. The gate "
    "against a repeat is tools/audit_wheel_status.py: it FAILS if any row whose reason, implementation "
    "or trigger text names an army-bar / army_spec exclusion reads IN-WHEEL, and it reports (does not "
    "silently fix) every army_spec row that still reads IN-WHEEL. (4) WHAT THE SAME DEFAULT COULD HAVE "
    "MISLABELLED, LISTED NOT SMOOTHED: 17 further rows are army_spec junction entries that read "
    "IN-WHEEL - Warden's Cage (implemented), Greater Gate of Khorne (implemented), Merciw's Monstrous "
    "Regiment (2 rows, implemented), Bubonic Broadside (round 107's own arithmetic already calls it an "
    "army-bar junction and subtracts it from the 55), Ashes & Dust x2, Dance of Despair x2, Gehenna's "
    "Golden Globe x2, Magma Storm x2, Storm of Renewal x2, Time Amok x2. They are NOT corrected here: "
    "moving them is a roster decision (4 of them are implemented in the mod today), so the figure "
    "stands at 1,140 and the consequence of the stricter reading is stated instead - 1,140 - 17 = "
    "1,123 IN-WHEEL, 660 + 17 = 677 EXCLUDED. The army-bar rule, applied to the two rows the user "
    "named, is 1,140. (5) IMPLEMENTED 742 KEYS / 689 ENTRIES, ZERO ORPHANS: counted by parsing the "
    "shipped ABILITIES table (742 distinct key strings over 689 entries; 53 entries carry more than "
    "one key) and joined key-by-key to this sheet's 'Ability key(s)' column - 742 of 742 matched, 0 "
    "unmatched. (6) 46 EVALUATORS: FOURTH.evaluators holds 46 keys and their entries / keys sum to "
    "689 / 742. (7) BOMBARDMENT 55: unchanged, all 55 implemented."
    % ("{:,}".format(sum(len(x[2]) for x in rows)),
       sum(1 for x in rows if len(x[2]) > 1)))

# a short, explicit block under the reconciliation
base = n.max_row + 2
n.cell(row=base, column=1).value = (
    "ROUND 120 - THE TWO ROWS THAT MOVED, AND THE 17 THAT ARE FLAGGED BUT NOT MOVED")
n.cell(row=base + 1, column=1).value = "Moved to EXCLUDED (v18 item # | name | key | new status)"
for i, (v18_item, name, key) in enumerate((
        (1334, "Thorsen's Thunderstorm", "wh3_dlc20_cataclysm_bound_thorsens_thunderstorm"),
        (1335, "Thorsen's Thunderstorm", "wh3_dlc27_cataclysm_bound_thorsens_thunderstorm"))):
    n.cell(row=base + 2 + i, column=1).value = (
        "%d | %s | %s | EXCLUDED (was IN-WHEEL; Implementation stays SKIPPED (round 106))"
        % (v18_item, name, key))
n.cell(row=base + 4, column=1).value = (
    "Both reasons keep their round-106 text and now end '- wheel status corrected in round 120: "
    "army-bar abilities are outside the wheel by the user's own rule'. Neither key is in the mod, so "
    "NOTHING in the mod or the shipped pack changed in this round.")
n.cell(row=base + 5, column=1).value = (
    "Flagged, NOT moved (army_spec junction, still IN-WHEEL - a roster decision): " +
    ", ".join(resid_keys))
n.cell(row=base + 6, column=1).value = (
    "If that reading is applied: 1,140 - 17 = 1,123 IN-WHEEL and 660 + 17 = 677 EXCLUDED; 4 of the "
    "17 rows are implemented today, so the ruling also decides whether they stay in the mod.")

# ------------------------------------------------------------------ Definitions
d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v14")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v19 (2026-10-20)"

r5 = d.cell(row=5, column=1)
t5 = r5.value
assert "658 abilities are out and 1,141 are in" in t5
r5.value = t5.replace("658 abilities are out and 1,141 are in",
                      "660 abilities are out and 1,140 are in")
r5.value = r5.value.replace("Bound spells (176)", "Bound spells (%d)" % fam_inc["bound"])

assert d.cell(row=9, column=1).value == "IN-WHEEL"
r9 = d.cell(row=9, column=2)
assert "1,141 rows" in r9.value
r9.value = r9.value.replace("1,141 rows", "1,140 rows")

assert d.cell(row=10, column=1).value == "EXCLUDED"
r10 = d.cell(row=10, column=2)
assert "(658 rows)" in r10.value
r10.value = r10.value.replace("(658 rows)", "(660 rows)").replace("army (204)", "army (206)")

assert d.cell(row=11, column=1).value == "IMPLEMENTED"
r11 = d.cell(row=11, column=2)
assert "742 keys across 741 numbered rows" in r11.value
r11.value = r11.value.replace(
    "742 keys across 741 numbered rows - one row names two keys",
    "742 keys across 742 numbered rows - every implemented key now has a row of its own (round 120: "
    "the Slicing Shards bound twin was the last one without)")

assert d.cell(row=12, column=1).value == "NOT IMPLEMENTED"
r12 = d.cell(row=12, column=2)
assert "of which 399 are in the wheel" in r12.value
r12.value = r12.value.replace("1,057 keys", "1,058 keys").replace(
    "of which 399 are in the wheel", "of which 398 are in the wheel")

# the two stale coverage sentences (re-counted, not left to drift)
cov_tot = sum(1 for x in rows if x[5] == "IMPLEMENTED")
cov_gate = sum(1 for x in rows if x[5] == "IMPLEMENTED"
               and any(w in x[6] for w in ("wind-up", "charge gate", "recharge_time",
                                           "in-flight", "per-unit")))
r104 = d.cell(row=104, column=1)
assert "180 of the 741 implemented rows (742 keys)" in str(r104.value)
r104.value = str(r104.value).replace(
    "180 of the 741 implemented rows (742 keys)",
    "%d of the %d implemented rows (%d keys)" % (cov_gate, cov_tot, N_IMPL_KEYS))

r92 = d.cell(row=92, column=2)
assert "Every one of the 1,797 keys" in str(r92.value)
r92.value = str(r92.value).replace("Every one of the 1,797 keys",
                                   "Every one of the %s keys" % "{:,}".format(N))

# new section 16
base = d.max_row + 2
sec = [
    ("16. ROUND 120 - THE WHEEL STATUS WAS DERIVED FROM THE WRONG TEST (and what now stops it)",
     None, None),
    ("THE DEFECT, IN ONE LINE",
     "Two rows read IN-WHEEL in a column whose neighbouring reason column said 'skipped (round 106: "
     "army-bar ability (army_spec junction) - out of wheel scope)'. An army-bar ability cannot be in "
     "the wheel: the two statements contradicted each other in the same row.", None),
    ("THE PIPELINE, TRACED",
     "build_abilities_master_xlsx.py:590 computes Status as 'IN-WHEEL if unit_abilities.source_type "
     "in {active, bound, lord, character, unit, item, rune, weapon} else EXCLUDED'. The IN-WHEEL rule "
     "in this sheet names the army-bar family only as 'source_type = army', so the army_spec junction "
     "- the table that actually makes an ability an ARMY-BAR button - was never consulted. Both "
     "Thorsen keys are source_type 'bound', so the classifier said IN-WHEEL. Round 106 found the "
     "junction by hand and wrote the skip through make_xlsx_v7.py's SKIP_KEYS loop, which writes the "
     "reason, implementation, family and trigger columns and NEVER writes or asserts the Status "
     "column - while set_impl() in the same script asserts Status == IN-WHEEL before it writes. The "
     "asymmetry is the bug: a skip could be recorded against a row whose status was never "
     "re-derived.", None),
    ("WHAT WAS CORRECTED",
     "Thorsen's Thunderstorm, both keys ('wh3_dlc20_cataclysm_bound_thorsens_thunderstorm', "
     "'wh3_dlc27_cataclysm_bound_thorsens_thunderstorm'): Status EXCLUDED, reason kept and appended "
     "'- wheel status corrected in round 120: army-bar abilities are outside the wheel by the user's "
     "own rule'. In-wheel 1,141 -> 1,139 before the added row, 1,140 after it.", None),
    ("WHAT NOW FAILS INSTEAD OF DRIFTING",
     "tools/audit_wheel_status.py - gate 1 fails if ANY row reads IN-WHEEL while its reason, "
     "implementation or trigger text names an army-bar / army_spec / army-ability / campaign-side-"
     "junction exclusion; gate 2 fails if an IN-WHEEL row's reason does not start with 'carrier "
     "family:' or 'skipped ('; gate 3 REPORTS every army_spec junction entry that still reads "
     "IN-WHEEL instead of fixing it silently.", None),
    ("WHY THE OTHER 17 ARE NOT 'FIXED'",
     "17 more rows are army_spec junction entries and still read IN-WHEEL. Under the strict reading "
     "they are army-bar and out of scope - round 107's own arithmetic already subtracts Bubonic "
     "Broadside on exactly that basis - but 4 of the 17 rows are IMPLEMENTED in the mod today "
     "(Warden's Cage, Greater Gate of Khorne, Merciw's Monstrous Regiment x2 rows), so moving them "
     "would put implemented abilities outside the wheel and implies removing them from the mod. That "
     "is a roster decision, not a data correction: the sheet states both figures (1,140 as shipped, "
     "1,123 under the strict reading) and lists the keys on the Numbers sheet so the ruling can be "
     "made once.", None),
    ("THE MISSING ROW",
     "'wh3_main_spell_slaanesh_slicing_shards_bound' - Slicing Shards' second key, the Keeper of "
     "Secrets' bound version (uset_ability.tsv unit_set wh3_main_sla_mon_keeper_of_secrets_0), "
     "source_type bound, num_uses 1, recharge_time -1, target_intercept_range 200, 5 s wind-up. The "
     "mod has carried it since round 106 as the second key of the 'slicing_shards' entry; the "
     "inventory never had a row for it, which is why 741 implemented rows carried 742 keys. It is "
     "now a row: IN-WHEEL, IMPLEMENTED, trigger family enemy_ground_melee_infantry, trigger text "
     "identical to its twin (ONE evaluator in the mod covers both keys).", None),
]
for i, (a, b, c) in enumerate(sec):
    row = base + i
    d.cell(row=row, column=1).value = a
    if b is not None:
        d.cell(row=row, column=2).value = b
    if c is not None:
        d.cell(row=row, column=3).value = c

# ------------------------------------------------------------------ Changelog
ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-10-20"
ch.cell(row=r, column=2).value = "v19"
ch.cell(row=r, column=3).value = (
    "ROUND 120 - THE THREE DEFECTS THE USER FOUND, PLUS THE NUMBERS BLOCK. (1) ARMY-BAR ROWS "
    "CORRECTED OUT OF THE WHEEL: Thorsen's Thunderstorm (both keys) read IN-WHEEL while their reason "
    "said 'skipped (round 106: army-bar ability (army_spec junction) - out of wheel scope)'. Both are "
    "EXCLUDED now, with the reason kept and the round-120 correction appended. The pipeline cause is "
    "traced in Definitions section 16: Status comes from unit_abilities.source_type only (both keys "
    "are 'bound'), the army_spec junction is never consulted, and make_xlsx_v7.py's SKIP_KEYS loop "
    "writes columns 19-22 but never column 18 - unlike set_impl(), which asserts it. Gate: "
    "tools/audit_wheel_status.py fails on any such contradiction and reports the 17 army_spec rows "
    "that still read IN-WHEEL (not moved: 4 of them are implemented, so that is a roster decision). "
    "(2) THE ORPHAN KEY ROWED: 'wh3_main_spell_slaanesh_slicing_shards_bound' - implemented in the "
    "mod as the second key of 'slicing_shards', absent from the 1,799-row inventory - now has its own "
    "row (IN-WHEEL, IMPLEMENTED, enemy_ground_melee_infantry, the twin's trigger text, its own game-"
    "data fields: 1 use, recharge_time -1 so 0 s cooldown, 200 m reach, 5 s wind-up). The full audit "
    "of the mod's 742 implemented keys against the sheet's key column now returns 742 / 742 matched, "
    "0 unmatched. (3) NUMBERS: every figure recomputed in the unit it is counted in - 1,800 rows = "
    "1,140 IN-WHEEL + 660 EXCLUDED; 742 implemented rows / 742 implemented keys + 398 not "
    "implemented among the included = 1,140; 46 evaluators / 689 entries / 742 keys; bombardment 55. "
    "(4) THE PER-CARRIER-FAMILY BLOCK IS NOW A ROW-LEVEL COUNT derived from this sheet's own 1,140 "
    "in-wheel rows joined to unit_abilities.source_type, and it TIES (sum 1,140 included / 742 "
    "implemented). v18's block was an older KEY-level count (1,143 keys / 638 implemented) that could "
    "not tie to a row-level headline; it was re-derived, not relabelled. (5) NO MOD CHANGE, NO "
    "REBUILD: neither corrected key is in the mod and the added row is a row for a key the mod "
    "already carried, so the shipped pack is untouched at md5 "
    "2f215bc4c35845452103327fb62ba554.")
ch.cell(row=r, column=4).value = (
    "user instruction 2026-10-20 (the three defects found in v18) - data and documentation only; "
    "xlsx v19 supersedes v18; v1-v18 byte-unchanged.")

wb.save(DST)
print("wrote", DST)
print("rows", N, "in-wheel", N_IN, "excluded", N_EX,
      "impl rows", N_IMPL_ROWS, "impl keys", N_IMPL_KEYS, "not-impl in-wheel", NOT_IMPL_IN)
print("families", dict(fam_inc), "impl", dict(fam_impl))
print("moved:", moved)
print("residual army_spec in-wheel rows:", len(resid), "keys:", len(resid_keys))
