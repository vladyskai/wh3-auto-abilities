#!/usr/bin/env python3
"""Build WH3_abilities_master_v33_2026-11-13.xlsx from v32 - round 141: the nine recharge reducers, one by one.

(1) 9 rows retriggered (5 self_recharging, 1 self_recharging_2, Armour of Caledor on melee_health75, Terrorgheist Skull on
    melee_self_or_ally, Spell-Wrought Sceptre on recharging_in_reach).
(2) Counts unchanged (750 / 373); 60 -> 64 families: the Numbers trigger table gains four rows (bombardment block
    106 -> 110). Definitions: title v33, section 30. Changelog: a v33 row. v1-v32 are never opened for writing.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v32_2026-11-13.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v33_2026-11-13.xlsx"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
RC = ("'recharging' = an ability of that unit that the MOD cast (accepted) whose lock - active_time + recharge_time "
      "from the GENERATED FOURTH.RECHARGE_S - has not run out; the reducer's own keys never count; spells and abilities "
      "the player clicks, and campaign recharge bonuses, are invisible to it; ")
RULE = "user ruling 2026-11-13 (the recharge reducers, one by one); "
T = {
    "self_recharging": "self_recharging: not routing; at least 1 of the caster's abilities recharging; " + RC + RULE
                       + "cast target: self; " + SHARED_TAIL,
    "self_recharging_2": "self_recharging_2: not routing; at least 2 of the caster's abilities recharging; " + RC + RULE
                         + "cast target: self; " + SHARED_TAIL,
    "melee_health75": "melee_health75: not routing; is_in_melee() and health 75% or less (FOURTH.health_pct); " + RULE
                      + "cast target: self; " + SHARED_TAIL,
    "melee_self_or_ally": "melee_self_or_ally: not routing; the caster in melee -> cast on itself; otherwise the CLOSEST "
                          "tracked ally (alive, not routing) in melee within the bound by unit_distance -> cast on that "
                          "ally; bound: 70 m (70% of the ability's 100 m ally cast reach); pre-cast re-check: the ally "
                          "must still be alive, in melee and within the bound; " + RULE + SHARED_TAIL,
    "recharging_in_reach": "recharging_in_reach: not routing; at least 1 of the caster's abilities recharging -> cast on "
                           "itself; otherwise the CLOSEST tracked ally (alive, not routing) with at least 1 recharging "
                           "ability within the bound -> cast on that ally; bound: 70 m (70% of the ability's 100 m ally "
                           "cast reach); " + RC + RULE + SHARED_TAIL,
}
ROWS = {"wh_main_item_abilities_scroll_of_power": ("ushoran_health", "self_recharging_2"),
        "wh2_dlc09_item_abilities_staff_of_nagash": ("melee_unwavering", "self_recharging"),
        "wh3_main_weapon_abilities_staff_of_tomorrow": ("melee_unwavering", "self_recharging"),
        "wh_dlc04_item_abilities_the_liber_noctus": ("melee_unwavering", "self_recharging"),
        "wh_main_item_abilities_channelling_staff": ("melee_unwavering", "self_recharging"),
        "wh3_dlc29_weapon_abilities_aken_seth_the_staff_of_pain": ("melee_unwavering", "self_recharging"),
        "wh2_dlc15_item_abilities_armour_of_caledor": ("melee_unwavering", "melee_health75"),
        "wh_dlc08_item_abilities_terrorgheist_skull": ("melee_unwavering", "melee_self_or_ally"),
        "wh3_dlc23_weapon_abilities_spell_wrought_sceptre": ("melee_unwavering", "recharging_in_reach")}
NEW_FAMS = ("self_recharging", "self_recharging_2", "recharging_in_reach", "melee_self_or_ally")

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
done = 0
for r in range(2, ws.max_row + 1):
    ks = keys_of(r)
    if len(ks) == 1 and ks[0] in ROWS:
        old_f, new_f = ROWS[ks[0]]
        assert str(ws.cell(row=r, column=21).value) == old_f, ks
        old = str(ws.cell(row=r, column=22).value or "")
        gates = (" GATES" + old.split(" GATES", 1)[1]) if " GATES" in old else ""
        ws.cell(row=r, column=21).value = new_f
        ws.cell(row=r, column=22).value = T[new_f] + gates
        done += 1
assert done == 9, done

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
assert len(trig) == 64 and [trig[f] for f in NEW_FAMS] == [5, 1, 1, 1], (len(trig), [trig[f] for f in NEW_FAMS])

n = wb["Numbers"]
assert n.cell(row=106, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert all(int(str(m).split(":")[0][1:]) < 104 for m in n.merged_cells.ranges)
n.insert_rows(104, 4)
assert n.cell(row=110, column=1).value == "Bombardment set (COMPLETE - round 108)"
n.cell(row=7, column=1).value = (
    "Date: 2026-11-13     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v33 - ROUND 141: the nine recharge reducers, one by one: Scroll of Power on self_recharging_2; Staff of Nagash, "
    "Staff of Tomorrow, The Liber Noctus, Channelling Staff, Aken-seth on self_recharging; Armour of Caledor on "
    "melee_health75; Terrorgheist Skull on melee_self_or_ally; Spell-Wrought Sceptre on recharging_in_reach. Implemented "
    "750 rows / 750 keys and 373 not implemented, unchanged. The mod: 698 entries / 750 keys / 64 trigger families.)")
n.cell(row=42, column=1).value = (
    "Trigger families after round 141 - re-counted from the mod's own ABILITIES table: 64 families / 698 entries / "
    "750 keys (metallurgy_melee and melee_low_morale keep 0 entries). Round 141: the NEW self_recharging (5), "
    "self_recharging_2 (1), recharging_in_reach (1), melee_self_or_ally (1); melee_unwavering 314 -> 306, ushoran_health "
    "20 -> 19, melee_health75 1 -> 2.")
for r in range(44, 109):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t2, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t2
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t2]
assert 44 + len(fam_sorted) == 108
n.cell(row=108, column=2).value = "TOTAL (64 families)"
n.cell(row=108, column=3).value = sum(trig.values())
n.cell(row=108, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v32")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v33 (2026-11-13)"
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("30. ROUND 141 - THE NINE RECHARGE REDUCERS (v33)", None),
    ("THE RULINGS (2026-11-13, one by one)", "Scroll of Power: 2+ abilities recharging. Staff of Nagash, Staff of "
     "Tomorrow, The Liber Noctus, Channelling Staff, Aken-seth: 1 ability recharging. Armour of Caledor: in melee and "
     "health 75% or less. Terrorgheist Skull: the caster or an ally in melee. Spell-Wrought Sceptre: the caster or an "
     "ally within 70 m with an ability recharging."),
    ("RECHARGING", "The mod remembers every cast the game accepted and its lock: active_time + recharge_time from the "
     "GENERATED FOURTH.RECHARGE_S (618 keys; tools/gen_recharge_keys.py). It cannot see spells or abilities the player "
     "clicks, nor campaign recharge bonuses."),
    ("THE NEW FAMILIES", "self_recharging (5), self_recharging_2 (1), recharging_in_reach (1), melee_self_or_ally (1)."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-13"
ch.cell(row=r, column=2).value = "v33"
ch.cell(row=r, column=3).value = (
    "ROUND 141. The nine recharge reducers, one by one (four NEW families). Counts unchanged; 64 families. SHIPPED: "
    "installed pack md5 %s; harness 140 full suite 6,088 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-13; xlsx v33 supersedes v32; v1-v32 byte-unchanged."
wb.save(DST)
print("wrote", DST)
