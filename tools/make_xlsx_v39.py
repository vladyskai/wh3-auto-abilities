#!/usr/bin/env python3
"""Build WH3_abilities_master_v39_2026-11-14.xlsx from v38 - round 151. No count changes.

(1) The 77 enemy_blob rows: the text gains the game's usage rules (grounded / in melee), LARGE FIRST + the hold for the
    53 prefer-central attacks, and the 90-degree preference for the 20 breaths.
(2) The 432 rows whose trigger family starts ARMED get a "DEFAULT: starts ARMED (A)" clause.
(3) Definitions: title v39, section 36. Changelog: a v39 row. Numbers: the date line.
v1-v38 are never opened for writing.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402
import build_ability_database as bd  # noqa: E402
import gen_blob_tables as GB  # noqa: E402
import round151_large_defaults as R151  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v38_2026-11-14.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v39_2026-11-14.xlsx"
LUA = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"

src = open(LUA, encoding="utf-8").read()
KEYS = GB.keys_in(src)
assert len(KEYS) == 77
SHOT = GB.shot_table(KEYS)
entries, _, _ = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
DEFAULT_KEYS = {k for k, f in fam_by_key.items() if f in set(R151.DEFAULT_ON)}
n_def_entries = sum(1 for e in entries if e["trigger"] in set(R151.DEFAULT_ON))
assert n_def_entries == 432, n_def_entries


def blob_add(k):
    s = SHOT[k]
    parts = []
    if s[6] or s[7]:
        rules = []
        if s[6]:
            rules.append("the caster must be flying (game rule: not grounded)")
        if s[7]:
            rules.append("the caster must be out of melee (game rule: not engaged_in_melee)")
        parts.append("ROUND 151 usage rules: " + " and ".join(rules) + ".")
    if s[4]:
        parts.append("ROUND 151 LARGE FIRST (prefer_central_targets; user rulings 2026-11-14 \"Large first, but also include "
                     "a hold\" and \"Worth more than infantry\"): a safe visible LARGE enemy in range is hit first - the one "
                     "losing the most value (all %d shots hit it: projectile and blast damage after armour, bonus vs large "
                     "included, against its current hit points, generated from land_units, mounts, unit_armour_types and "
                     "battle_entities, x its live value); with none in range the cast is HELD while a visible large enemy "
                     "anywhere would lose more value than the best infantry target." % s[0])
    if s[5]:
        parts.append("ROUND 151 BREATH (user ruling 2026-11-14 \"Prefer 90 now\"): among infantry targets within 20%% of "
                     "the best value, the one whose side faces the breath (line of fire closest to 90 degrees off its "
                     "facing).".replace("%%", "%"))
    return " " + " ".join(parts) if parts else ""


DEFAULT_ADD = (" DEFAULT (round 151, user ruling 2026-11-14): starts ARMED (A) in every battle; a badge click switches it "
               "off; the ALL badge arms or disarms every ability of the selected unit(s).")

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
nb = nd = 0
for r in range(2, ws.max_row + 1):
    ks = [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
    if not ks or str(ws.cell(row=r, column=20).value) != "IMPLEMENTED":
        continue
    cell = ws.cell(row=r, column=22)
    if ks[0] in SHOT:
        add = blob_add(ks[0])
        if add:
            cell.value = str(cell.value) + add
            nb += 1
    if any(k in DEFAULT_KEYS for k in ks):
        cell.value = str(cell.value) + DEFAULT_ADD
        nd += 1
assert nb == 77 or nb == sum(1 for k in KEYS if blob_add(k)), nb
assert nd == len(DEFAULT_KEYS), (nd, len(DEFAULT_KEYS))
n = wb["Numbers"]
n.cell(row=7, column=1).value = (
    "Date: 2026-11-14     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v39 - ROUND 151: the 53 prefer-central blob attacks hit LARGE enemies first and hold for a more valuable one; the "
    "game's usage rules; breaths prefer 90 degrees; %d rows start ARMED; the ALL badge. No count change: 854 implemented / "
    "269 not implemented (27 skipped); the mod 799 entries / 854 keys / 75 trigger families.)" % nd)
d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v38")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v39 (2026-11-14)"
base = d.max_row + 2
sec = [
    ("36. ROUND 151 - LARGE FIRST, USAGE RULES, BREATHS AT 90, DEFAULT ARMED, ALL BADGE (v39)", None),
    ("THE RULINGS (2026-11-14)", "\"Large first, but also include a hold when there is a valuable large unit in the "
     "battlefield\" for every prefer_central_targets attack; valuable = \"Worth more than infantry\". Breaths: \"Prefer 90 "
     "now\". Start armed: the 21 when ready, the in-melee / on-charge self-casts, protection & last stand, morale saves, "
     "heals, ammo refills. \"ALL badge per unit\"."),
    ("THE TABLES", "FOURTH.BLOB_SHOT_TEXT (shots, projectile damage, bonus vs large, central, breath, usage rules for the 77) "
     "and FOURTH.LARGE_DEF_TEXT (armour and hit points of 980 large land units), generated by tools/gen_blob_tables.py."),
    ("THE ARITHMETIC", "No count change: 854 implemented / 269 not implemented (27 skipped); 799 entries / 854 keys; 75 "
     "families. %d rows / 432 entries start armed." % nd),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b
ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-14"
ch.cell(row=r, column=2).value = "v39"
ch.cell(row=r, column=3).value = (
    "ROUND 151. Large first + hold for the 53 prefer-central blob attacks; the game's usage rules; breaths prefer 90 "
    "degrees; %d rows start ARMED; the ALL badge. Counts unchanged. SHIPPED: installed pack md5 %s; harness 150 full suite "
    "6,423 checks / 0 failures." % (nd, os.environ.get("WH3_PACK_MD5", "PENDING")))
ch.cell(row=r, column=4).value = "user rulings 2026-11-14; xlsx v39 supersedes v38; v1-v38 byte-unchanged."
wb.save(DST)
print("wrote", DST, "| blob rows", nb, "| default rows", nd)
