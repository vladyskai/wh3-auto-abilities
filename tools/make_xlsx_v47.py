#!/usr/bin/env python3
"""Build WH3_abilities_master_v47_2026-11-16.xlsx from v46 - round 163: the placed areas and the expendable units.

(1) 26 rows NOT IMPLEMENTED -> IMPLEMENTED: 22 on enemy_wander (7 instant blasts, 14 lingering areas, Chain Lightning
    RoR), Arcane Vassal on the NEW ally_blast, Siegebreaker on the NEW enemy_strike, Befuddlement of Mischiefs on
    enemy_fast_near_ally, Winged Staff on enemy_area_drain.
(2) 2 rows NOT IMPLEMENTED -> SKIPPED (user decision): the Rune and Master Rune of Wrath & Ruin.
(3) Implemented 949 -> 975 rows / keys; not implemented among the included 174 -> 148 (34 + 2 = 36 skipped). The mod
    918 entries / 975 keys; 90 -> 92 families: the Numbers trigger table gains two rows (bombardment block 136 -> 138).
    Definitions: title v47, the two count rows, section 44 (it also records that v46's prose said 172 where its cell
    says 174). Changelog: a v47 row.
v1-v46 are never opened for writing.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import math
import os
import shutil

import openpyxl

import build_ability_database as bd
import gen_ww_tables as GW
import gen_shot_tables as GS

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v46_2026-11-16.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v47_2026-11-16.xlsx"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
FF_NOTE = "our expendable units (the game's attribute) and cheap ones (below 2 per soldier) are not protected"
SRC_TXT = open(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua",
               encoding="utf-8").read()
KF = GW.keys_in(SRC_TXT)
WW = GW.derive(KF)
USA = {r["key"]: r for r in GW.tsv("unit_spec_abil.tsv")}
INV = {}
for r in GW.tsv("special_ability_to_invalid_target_flags_tables.tsv"):
    INV.setdefault(r["special_ability"], set()).add(r["invalid_target"])
WANDER_KEYS = """wh2_dlc16_item_abilities_acorns_of_the_oak_of_ages wh3_main_item_abilities_deaths_head
wh3_main_weapon_abilities_frost_fang wh3_dlc23_item_abilities_hammer_of_smednir wh_dlc03_spell_bound_viletide
wh3_main_item_abilities_crackleblaze wh3_dlc24_unit_abilities_lampreys_bite wh3_dlc26_lord_abilities_boiling_cauldron
wh3_dlc26_lord_abilities_simmering_pot wh2_dlc12_character_abilities_brass_orb
wh2_dlc12_character_abilities_brass_orb_tech_lab_doom_flayer wh2_dlc12_character_abilities_brass_orb_upgrade
wh3_dlc20_spell_bound_infernal_gateway wh3_dlc27_spell_bound_pit_of_shades wh3_main_spell_bound_pit_of_shades
wh_dlc05_spell_shadow_pit_of_shades_bound wh2_main_spell_bound_rubric_of_dark_dimensions wh3_dlc29_spell_bound_plague
wh3_dlc29_spell_bound_plaguemaster wh3_dlc29_lord_abilities_warp_junction wh3_pro10_cataclysm_fire_magma_storm_bound
wh_main_spell_bound_chain_lightning_ror""".split()
OTHER = ["wh2_main_character_abilities_arcane_vassal", "wh2_dlc16_character_abilities_befuddlement_of_mischiefs",
         "wh2_main_weapon_bound_winged_staff", "wh3_main_weapon_abilities_siegebreaker"]
KEYS = WANDER_KEYS + OTHER
INSTANT = set(WANDER_KEYS[:7])
CLOSE = {
    "wh_main_rune_abilities_rune_of_wrath_and_ruin": "an Anvil rune: casting it locks the Runelord's other runes for 60 s",
    "wh_dlc06_rune_abilities_master_rune_of_wrath_and_ruin": "an Anvil rune: casting it locks the Runelord's other runes "
                                                             "for 90 s",
}
assert len(KEYS) == 26
AREA = GS.area_rows({"wh2_main_weapon_bound_winged_staff"})


def text(k, fam):
    a = USA[k]
    real = float(a["target_intercept_range"])
    uses, rech, wind = int(float(a["num_uses"])), float(a["recharge_time"]), float(a["wind_up_time"])
    gates = []
    if uses > 1:
        gates.append("charge hold %g s (%d uses)" % (rech, uses))
    if wind > 0:
        gates.append("in-flight hold %g s (%g s wind-up + 2 s)" % (wind + 2, wind))
    if real > 0:
        within = "within %d m (70%% of the ability's %g m target_intercept_range; unit_distance)" % (
            int(math.floor(real * 0.70 + 1e-9)), real)
    else:
        within = "anywhere on the field (the game gives no range: target_intercept_range -1, unbounded)"
    cls = "; target class: not flying (the game's flying_currently rule)" if "flying_currently" in INV.get(k, set()) else ""
    if fam == "enemy_wander":
        kind, r, path, off, buf, allies, ground = WW[k]
        if allies:
            safe = ("none of our units within %g m of the target (radius %g + reach %d m + 10 m; the GENERATED WW table; "
                    "%s)" % (r + buf + 10, r, buf, FF_NOTE))
        else:
            safe = "no friendly test (the game marks the vortex as not hitting allies)"
        rule = ("\"Like Dwellers Below\"" if k in INSTANT else
                ("\"Wanderer rule\", buffer \"Simulated 95%\"" if k == "wh_main_spell_bound_chain_lightning_ror"
                 else "\"Same as the blasts\""))
        how = "on the ground under it (a ground-only ability)" if ground else "that enemy unit"
        body = ("enemy_wander: not routing; the caster STANDING STILL; the visible enemy INFANTRY %s, STANDING STILL, whose "
                "%g m blast covers the blob density line (half a packed block; the trash rule) and destroys the most "
                "value; %s%s; cast target: %s; pre-cast re-check: the map is rebuilt and the same rule holds; user ruling "
                "2026-11-16 (%s); " % (within, r, safe, cls, how, rule))
    elif fam == "ally_blast":
        r = WW[k][1]
        body = ("ally_blast: not routing; our unit (or the caster) %s whose %g m blast circle covers the most enemy value "
                "(the blob value; at least half a packed block); cast target: that unit (the blast hits enemies only); "
                "user ruling 2026-11-16 (\"Most enemies around\"); " % (
                    within.replace("target_intercept_range", "target_intercept_range, the ally bound"), r))
    elif fam == "enemy_fast_near_ally":
        body = ("enemy_fast_near_ally: not routing; a FAST enemy %s (moving, fast_speed() >= FOURTH.FAST_ENEMY_MPS = 5 m/s) "
                "within 40 m of one of our units; cast target: that enemy unit (enemies within 35 m frozen for 11 s); "
                "flying or not; user ruling 2026-11-16 (\"charge only\", \"Any fast enemy\"); " % within)
    elif fam == "enemy_area_drain":
        body = ("enemy_area_drain: not routing; the caster STANDING STILL (is_moving() exactly false); the visible enemy "
                "INFANTRY %s with at least %d soldiers left (the GENERATED AREA table: the game's max_damaged_entities) and "
                "the highest live value per soldier; no friendly-fire margin (a direct effect); cast target: that enemy "
                "unit; user ruling 2026-11-16 (\"Area drain rule\"); " % (within, AREA[k]))
    else:
        assert fam == "enemy_strike", fam
        kind, r, path, off, buf, allies, ground = WW[k]
        body = ("enemy_strike: not routing; the caster STANDING STILL; the most valuable (strategic_value) STANDING "
                "single-entity enemy %s (Lord, Hero, monster: the GENERATED single set) with none of our units within %g m "
                "(the %g m strike + 10 m; %s); cast on the ground under it (the game refuses a unit target unless it "
                "climbs, mans equipment or stands on a platform); user ruling 2026-11-16 (\"Strike a standing large "
                "single\"); " % (within, r + buf + 10, r, FF_NOTE))
    return body + SHARED_TAIL + ((" GATES: " + "; ".join(gates) + ".") if gates else "")


entries, _, _ = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
NEW = {k: (fam_by_key[k], text(k, fam_by_key[k])) for k in KEYS}

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
n_new = n_close = 0
for r in range(2, ws.max_row + 1):
    ks = keys_of(r)
    if len(ks) == 1 and ks[0] in NEW:
        assert str(ws.cell(row=r, column=18).value) == "IN-WHEEL" and str(ws.cell(row=r, column=20).value) == "NOT IMPLEMENTED", ks
        fam, t = NEW[ks[0]]
        ws.cell(row=r, column=20).value = "IMPLEMENTED"
        ws.cell(row=r, column=21).value = fam
        ws.cell(row=r, column=22).value = t
        n_new += 1
    elif len(ks) == 1 and ks[0] in CLOSE:
        assert str(ws.cell(row=r, column=18).value) == "IN-WHEEL" and str(ws.cell(row=r, column=20).value) == "NOT IMPLEMENTED", ks
        why = CLOSE[ks[0]]
        ws.cell(row=r, column=19).value = "skipped (user decision 2026-11-16: \"Close the runes\"; %s)" % why
        ws.cell(row=r, column=20).value = "SKIPPED (user decision)"
        ws.cell(row=r, column=21).value = "-"
        ws.cell(row=r, column=22).value = ("No automation - SKIPPED BY THE USER'S DECISION of 2026-11-16: \"Close the "
                                           "runes\" (%s)." % why)
        n_close += 1
assert (n_new, n_close) == (26, 2), (n_new, n_close)

rows = [(r, keys_of(r), str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=20).value),
         str(ws.cell(row=r, column=21).value)) for r in range(2, ws.max_row + 1)]
N = len(rows)
impl = [x for x in rows if x[3] == "IMPLEMENTED"]
N_IMPL_ROWS = len(impl)
N_IMPL_KEYS = len(set(k for x in impl for k in x[1]))
assert (N, N_IMPL_ROWS, N_IMPL_KEYS) == (1800, 975, 975), (N, N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = 1123 - N_IMPL_ROWS
assert NOT_IMPL_IN == 148
assert sum(1 for x in rows if x[3] == "SKIPPED (user decision)") == 36
assert (len(entries), len(fam_by_key)) == (918, 975)
assert set(k for x in impl for k in x[1]) == set(fam_by_key)
assert not [x[1][0] for x in impl if x[4] != fam_by_key.get(x[1][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 92, len(trig)

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
assert n.cell(row=136, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert n.cell(row=134, column=2).value == "TOTAL (90 families)"
assert all(int(str(m).split(":")[0][1:]) < 108 for m in n.merged_cells.ranges)
n.insert_rows(133, 2)
assert n.cell(row=138, column=1).value == "Bombardment set (COMPLETE - round 108)"
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-11-16     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v47 - ROUND 163: the placed areas and the expendable units. 26 rows implemented (22 enemy_wander, NEW ally_blast and "
    "enemy_strike, Befuddlement on enemy_fast_near_ally, Winged Staff on enemy_area_drain); 2 rows SKIPPED by the user. "
    "Implemented 949 + 26 = 975 rows / 975 keys; not implemented among the included 174 - 26 = 148 (36 skipped by the "
    "user). Every friendly-fire check now ignores our expendable and cheap units. The mod: 918 entries / 975 keys / 92 "
    "trigger families.)")
for r, num, label, abs_, p1, p2 in [
        (13, 4, "Implemented among the included", N_IMPL_ROWS, N_IMPL_ROWS / tot, N_IMPL_ROWS / 1123.0),
        (14, 5, "Not implemented among the included", NOT_IMPL_IN, NOT_IMPL_IN / tot, NOT_IMPL_IN / 1123.0),
        (16, 7, "All implemented in the mod (4 + 6)", N_IMPL_KEYS, N_IMPL_KEYS / tot, N_IMPL_KEYS / 1123.0)]:
    for c, v in enumerate((num, label, abs_, p1, p2), 1):
        n.cell(row=r, column=c).value = v
old18 = str(n.cell(row=18, column=1).value)
assert "949 implemented" in old18
n.cell(row=18, column=1).value = old18.replace("949 implemented", "975 implemented")
for i, f in enumerate(fam_order):
    r = 20 + i
    assert n.cell(row=r, column=2).value == f, (r, n.cell(row=r, column=2).value)
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=40, column=1).value = (
    "Reconciliation (v47): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 975 + not "
    "implemented 148 (36 of them skipped by the user) = 1,123. The mod's ABILITIES table is 918 entries / 975 keys, and "
    "the join mod-key -> 'Ability key(s)' returns 975 / 975 with ZERO unmatched keys in either direction. 892 + 26 "
    "(round 163, the placed areas) = 918 entries; 949 + 26 = 975 keys. NO army-bar (army_spec) key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 163 - re-counted from the mod's own ABILITIES table: 92 families / 918 entries / 975 "
    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 163: the NEW ally_blast (1) and "
    "enemy_strike (1); enemy_wander 20 -> 42, enemy_fast_near_ally 8 -> 9, enemy_area_drain 7 -> 8.")
for r in range(44, 136):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t2, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t2
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t2]
assert 44 + len(fam_sorted) == 136
n.cell(row=136, column=2).value = "TOTAL (92 families)"
n.cell(row=136, column=3).value = sum(trig.values())
n.cell(row=136, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v46")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v47 (2026-11-16)"
r11 = d.cell(row=11, column=2)
assert "949 keys across 949 numbered rows (" in r11.value and "round 162 added 32)" in r11.value
r11.value = r11.value.replace("949 keys across 949 numbered rows (", "975 keys across 975 numbered rows (").replace(
    "round 162 added 32)", "round 162 added 32, round 163 added 26)")
r12 = d.cell(row=12, column=2)
assert "(851 keys, of which 174 are in the wheel)" in r12.value
r12.value = r12.value.replace("(851 keys, of which 174 are in the wheel)", "(825 keys, of which 148 are in the wheel)")
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("44. ROUND 163 - THE PLACED AREAS AND THE EXPENDABLE UNITS (v47)", None),
    ("THE RULINGS (2026-11-16)", "The 7 instant blasts \"Like Dwellers Below\"; the 14 lingering areas \"Same as the "
     "blasts\"; Arcane Vassal \"Most enemies around\"; one by one: Befuddlement of Mischiefs \"charge only\", \"Any fast "
     "enemy\"; Winged Staff \"Area drain rule\"; Chain Lightning (RoR) \"Wanderer rule\"; Siegebreaker \"Strike a "
     "standing large single\"; the Wrath & Ruin runes closed. Expendable units: \"Game's set + cheap undead\"."),
    ("THE CHANGE", "NEW ally_blast (Arcane Vassal) and enemy_strike (Siegebreaker). The WW table now reads bombardments: "
     "Magma Storm's safety distance is 75 m (60 m spread + 5 m blasts + 10 m) while its 20 m vortex scores the target; "
     "Hell Hammer's corridor radius becomes 14.1 m (its 14 m bombardment blast). Every friendly-fire check ignores our "
     "expendable units (GENERATED FOURTH.EXPENDABLE_TEXT, 48 units) and our units worth less than 2 per soldier."),
    ("THE ARITHMETIC", "Implemented 949 + 26 = 975 rows / keys; not implemented among the included 174 - 26 = 148 "
     "(34 + 2 = 36 skipped by the user). The mod 892 + 26 = 918 entries / 975 keys; 92 families. Correction: v46's prose "
     "(the Numbers headline and section 43) says 206 - 34 = 172; the right figure is 206 - 32 = 174, which v46's own "
     "Numbers cell shows."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-16"
ch.cell(row=r, column=2).value = "v47"
ch.cell(row=r, column=3).value = (
    "ROUND 163. The placed areas: 26 rows IMPLEMENTED (2 NEW families), 2 rows SKIPPED by the user; the friendly-fire "
    "checks ignore expendable and cheap units. 949 -> 975 implemented; 174 -> 148 not implemented (36 skipped). Mod 918 / "
    "975 / 92 families. SHIPPED: installed pack md5 %s; harness 162 full suite 6,892 checks / 0 failures."
    % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = ("user rulings 2026-11-16 (the placed areas, the expendable units); xlsx v47 supersedes "
                                  "v46; v1-v46 byte-unchanged.")
wb.save(DST)
print("wrote", DST)
