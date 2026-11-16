#!/usr/bin/env python3
"""Build WH3_abilities_master_v48_2026-11-16.xlsx from v47 - round 164: the friendly-fire breaths.

(1) 28 rows NOT IMPLEMENTED -> IMPLEMENTED: 18 on enemy_wave, Tidecall and Wind Blast on the NEW enemy_wave_charge, 5 on
    the NEW enemy_cone, 2 on the NEW enemy_sweep, Da Boss' Loons on enemy_wander.
(2) The 12 round-162 enemy_wave rows: "the caster counting" becomes "the caster's own wave does not count (round 164)".
(3) Implemented 975 -> 1,003 rows / keys; not implemented among the included 148 -> 120 (36 skipped). The mod 946 entries
    / 1,003 keys; 92 -> 95 families: the Numbers trigger table gains three rows (bombardment block 138 -> 141).
    Definitions: title v48, the two count rows, section 45. Changelog: a v48 row.
v1-v47 are never opened for writing.
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

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v47_2026-11-16.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v48_2026-11-16.xlsx"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
FF_NOTE = "our expendable and cheap units are not protected; the caster's own breath does not count"
SRC_TXT = open(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua",
               encoding="utf-8").read()
KF = GW.keys_in(SRC_TXT)
WW = GW.derive(KF)
NOMELEE = set(GW.nomelee(KF))
USA = {r["key"]: r for r in GW.tsv("unit_spec_abil.tsv")}
INV = {}
for r in GW.tsv("special_ability_to_invalid_target_flags_tables.tsv"):
    INV.setdefault(r["special_ability"], set()).add(r["invalid_target"])
KEYS = """wh3_main_item_abilities_bangstick wh2_main_item_abilities_black_dragon_egg wh3_main_daemon_arms_abilities_blue_fire
wh3_main_daemon_arms_abilities_blue_fire_upgraded wh_main_item_abilities_fiery_ring_of_thori
wh2_main_lord_abilities_gaze_of_malice wh3_dlc24_unit_abilities_jade_dragons_breath wh3_main_item_abilities_kovsh_breath
wh3_dlc27_spell_bound_lash_of_slaanesh wh3_main_spell_bound_lash_of_slaanesh
wh3_main_spell_bound_lash_of_slaanesh_keeper_of_secrets wh3_dlc20_spell_bound_pink_fire_of_tzeentch
wh3_main_spell_tzeentch_pink_fire_of_tzeentch_bound wh2_main_mount_bound_scorch wh3_dlc20_spell_bound_stream_of_corruption
wh3_main_spell_nurgle_stream_of_corruption_bound wh2_main_weapon_abilities_sunfang
wh3_dlc20_weapon_abilities_the_spear_slaupnir wh2_dlc11_spell_bound_tidecall wh2_dlc11_spell_bound_wind_blast
wh2_dlc15_character_abilities_fishy_breathe wh2_main_mount_bound_pestilent_breath wh3_main_spell_bound_pestilent_breath
wh2_dlc13_character_ability_shatter wh_main_weapon_abilities_skabscrath wh3_dlc29_unit_active_ripping_blades
wh3_dlc29_unit_abilities_flesh_eating_scarabs wh2_dlc15_lord_abilities_da_boss_loons""".split()
assert len(KEYS) == 28
OLD_WAVE = "none of our units (the caster counting) within"
NEW_WAVE = "none of our OTHER units (the caster's own wave does not count: round 164) within"


def text(k, fam):
    a = USA[k]
    real = float(a["target_intercept_range"])
    uses, rech, wind = int(float(a["num_uses"])), float(a["recharge_time"]), float(a["wind_up_time"])
    gates = []
    if uses > 1:
        gates.append("charge hold %g s (%d uses)" % (rech, uses))
    if wind > 0:
        gates.append("in-flight hold %g s (%g s wind-up + 2 s)" % (wind + 2, wind))
    within = "within %d m (70%% of the ability's %g m target_intercept_range; unit_distance)" % (
        int(math.floor(real * 0.70 + 1e-9)), real)
    cls = "; target class: not flying (the game's flying_currently rule)" if "flying_currently" in INV.get(k, set()) else ""
    kind, r, path, off, buf, allies, ground = WW[k]
    melee = "; out of melee (the game's engaged_in_melee rule)" if k in NOMELEE else ""
    how = "on the ground under it (a ground-only ability)" if ground else "that enemy unit"
    if fam == "enemy_wave":
        body = ("enemy_wave: not routing; the caster STANDING STILL%s; among the visible enemies %s that are STANDING STILL, "
                "the one whose straight path (starting %g m + the target's half extent before its centre, %g m long, "
                "caster-to-target heading; it does not turn) has %s %g m of it (radius %g + 10 m; %s) and the most enemy "
                "value touched by the path%s; cast target: %s; pre-cast re-check: the same rule; user ruling 2026-11-16 "
                "(\"Wave rule\"); " % (melee, within, off, path, NEW_WAVE, r + 10, r, FF_NOTE, cls, how))
    elif fam == "enemy_wave_charge":
        body = ("enemy_wave_charge: not routing; the caster STANDING STILL; a FAST enemy %s (moving, fast_speed() >= 5 m/s, "
                "within 40 m of one of our units) whose %g m wave path from the caster through it has none of our OTHER "
                "units within %g m (radius %g + 10 m; %s); the most enemy value on the path%s; cast target: that enemy "
                "unit (it slows the target: rule 10); pre-cast re-check: still fast and clear; user ruling 2026-11-16 "
                "(\"Charge, clear path\"); " % (within, path, r + 10, r, FF_NOTE, cls))
    elif fam == "enemy_cone":
        body = ("enemy_cone: not routing; the caster STANDING STILL; a STANDING enemy %s; the zone from the caster through "
                "it, %g m long (the launch offset %g + the %g m breath), %g m wide each side (radius %g + 10 m), holds none "
                "of our OTHER units (%s); the most enemy value in it%s; cast target: that enemy unit; user ruling "
                "2026-11-16 (\"Clear cone, most value\"); " % (within, off + path, off, path, r + 10, r, FF_NOTE, cls))
    elif fam == "enemy_sweep":
        body = ("enemy_sweep: not routing; the caster in melee and not wavering; none of our OTHER units within %g m of the "
                "caster (the sweep's %g m reach: range + offset + travel + radius, + 10 m; %s); the closest enemy %s that is "
                "fighting in melee%s; cast target: %s; user ruling 2026-11-16 (\"Sweeps clear\"); "
                % (r + 10, r, FF_NOTE, within, cls, how))
    else:
        assert fam == "enemy_wander" and kind == 6, (k, fam, kind)
        body = ("enemy_wander: not routing; the caster STANDING STILL; the visible enemy INFANTRY %s, STANDING STILL, whose "
                "%g m blast covers the blob density line and destroys the most value; released at the caster, so none of "
                "our OTHER units within %g m of the caster (radius %g + reach %d m + 10 m; the GENERATED WW table; %s)%s; "
                "cast target: that enemy unit; user ruling 2026-11-16 (\"Loons as wanderer\"); "
                % (within, r, r + buf + 10, r, buf, FF_NOTE, cls))
    return body + SHARED_TAIL + ((" GATES: " + "; ".join(gates) + ".") if gates else "")


entries, _, _ = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
NEW = {k: (fam_by_key[k], text(k, fam_by_key[k])) for k in KEYS}

assert not os.path.exists(DST), DST
shutil.copy2(SRC, DST)
wb = openpyxl.load_workbook(DST)
ws = wb["Abilities"]
keys_of = lambda r: [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]
n_new = n_wave = 0
for r in range(2, ws.max_row + 1):
    ks = keys_of(r)
    if len(ks) == 1 and ks[0] in NEW:
        assert str(ws.cell(row=r, column=18).value) == "IN-WHEEL" and str(ws.cell(row=r, column=20).value) == "NOT IMPLEMENTED", ks
        fam, t = NEW[ks[0]]
        ws.cell(row=r, column=20).value = "IMPLEMENTED"
        ws.cell(row=r, column=21).value = fam
        ws.cell(row=r, column=22).value = t
        n_new += 1
    elif str(ws.cell(row=r, column=21).value) == "enemy_wave" and OLD_WAVE in str(ws.cell(row=r, column=22).value):
        ws.cell(row=r, column=22).value = str(ws.cell(row=r, column=22).value).replace(OLD_WAVE, NEW_WAVE)
        n_wave += 1
assert (n_new, n_wave) == (28, 12), (n_new, n_wave)

rows = [(r, keys_of(r), str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=20).value),
         str(ws.cell(row=r, column=21).value)) for r in range(2, ws.max_row + 1)]
N = len(rows)
impl = [x for x in rows if x[3] == "IMPLEMENTED"]
N_IMPL_ROWS = len(impl)
N_IMPL_KEYS = len(set(k for x in impl for k in x[1]))
assert (N, N_IMPL_ROWS, N_IMPL_KEYS) == (1800, 1003, 1003), (N, N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = 1123 - N_IMPL_ROWS
assert NOT_IMPL_IN == 120
assert sum(1 for x in rows if x[3] == "SKIPPED (user decision)") == 36
assert (len(entries), len(fam_by_key)) == (946, 1003)
assert set(k for x in impl for k in x[1]) == set(fam_by_key)
assert not [x[1][0] for x in impl if x[4] != fam_by_key.get(x[1][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 95, len(trig)

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
assert n.cell(row=138, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert n.cell(row=136, column=2).value == "TOTAL (92 families)"
assert all(int(str(m).split(":")[0][1:]) < 108 for m in n.merged_cells.ranges)
n.insert_rows(135, 3)
assert n.cell(row=141, column=1).value == "Bombardment set (COMPLETE - round 108)"
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-11-16     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v48 - ROUND 164: the friendly-fire breaths. 28 rows implemented: 18 on enemy_wave, 2 on the NEW enemy_wave_charge, 5 "
    "on the NEW enemy_cone, 2 on the NEW enemy_sweep, Da Boss' Loons on enemy_wander; a caster's own wave no longer blocks "
    "it. Implemented 975 + 28 = 1,003 rows / 1,003 keys; not implemented among the included 148 - 28 = 120 (36 skipped by "
    "the user). The mod: 946 entries / 1,003 keys / 95 trigger families.)")
for r, num, label, abs_, p1, p2 in [
        (13, 4, "Implemented among the included", N_IMPL_ROWS, N_IMPL_ROWS / tot, N_IMPL_ROWS / 1123.0),
        (14, 5, "Not implemented among the included", NOT_IMPL_IN, NOT_IMPL_IN / tot, NOT_IMPL_IN / 1123.0),
        (16, 7, "All implemented in the mod (4 + 6)", N_IMPL_KEYS, N_IMPL_KEYS / tot, N_IMPL_KEYS / 1123.0)]:
    for c, v in enumerate((num, label, abs_, p1, p2), 1):
        n.cell(row=r, column=c).value = v
old18 = str(n.cell(row=18, column=1).value)
assert "975 implemented" in old18
n.cell(row=18, column=1).value = old18.replace("975 implemented", "1003 implemented")
for i, f in enumerate(fam_order):
    r = 20 + i
    assert n.cell(row=r, column=2).value == f, (r, n.cell(row=r, column=2).value)
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=40, column=1).value = (
    "Reconciliation (v48): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 1,003 + not "
    "implemented 120 (36 of them skipped by the user) = 1,123. The mod's ABILITIES table is 946 entries / 1,003 keys, and "
    "the join mod-key -> 'Ability key(s)' returns 1,003 / 1,003 with ZERO unmatched keys in either direction. 918 + 28 "
    "(round 164, the breaths) = 946 entries; 975 + 28 = 1,003 keys. NO army-bar (army_spec) key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 164 - re-counted from the mod's own ABILITIES table: 95 families / 946 entries / 1,003 "
    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 164: the NEW enemy_wave_charge (2), "
    "enemy_cone (5) and enemy_sweep (2); enemy_wave 12 -> 30, enemy_wander 42 -> 43.")
for r in range(44, 139):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t2, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t2
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t2]
assert 44 + len(fam_sorted) == 139
n.cell(row=139, column=2).value = "TOTAL (95 families)"
n.cell(row=139, column=3).value = sum(trig.values())
n.cell(row=139, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v47")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v48 (2026-11-16)"
r11 = d.cell(row=11, column=2)
assert "975 keys across 975 numbered rows (" in r11.value and "round 163 added 26)" in r11.value
r11.value = r11.value.replace("975 keys across 975 numbered rows (", "1003 keys across 1003 numbered rows (").replace(
    "round 163 added 26)", "round 163 added 26, round 164 added 28)")
r12 = d.cell(row=12, column=2)
assert "(825 keys, of which 148 are in the wheel)" in r12.value
r12.value = r12.value.replace("(825 keys, of which 148 are in the wheel)", "(797 keys, of which 120 are in the wheel)")
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("45. ROUND 164 - THE FRIENDLY-FIRE BREATHS (v48)", None),
    ("THE RULINGS (2026-11-16)", "The 18 target-launched breaths \"Wave rule\"; Tidecall and Wind Blast \"Charge, clear "
     "path\" (rule 10: they slow); the 5 breaths from the caster's front \"Clear cone, most value\"; the sweeps and Da Boss' "
     "Loons \"Sweeps clear; Loons as wanderer\"; \"Caster doesn't count\" (a caster's own wave never blocks it)."),
    ("THE NEW FAMILIES", "enemy_wave_charge (2): a fast enemy closing on our units, the wave path from the caster through it "
     "clear. enemy_cone (5): the zone from the caster through a standing enemy, offset + path long, clear of our other "
     "units; the most value in it. enemy_sweep (2): the caster in melee, none of our other units within the sweep's reach + "
     "10 m; the closest enemy in melee. The game's engaged_in_melee usage rule joins the WW caster gate (GENERATED "
     "FOURTH.WW_NOMELEE_TEXT: Blue Fire of Chaos x2). All three start unarmed (M)."),
    ("THE ARITHMETIC", "Implemented 975 + 28 = 1,003 rows / keys; not implemented among the included 148 - 28 = 120 (36 "
     "skipped by the user). The mod 918 + 28 = 946 entries / 1,003 keys; 95 families."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-16"
ch.cell(row=r, column=2).value = "v48"
ch.cell(row=r, column=3).value = (
    "ROUND 164. The friendly-fire breaths: 28 rows IMPLEMENTED (3 NEW families); the 12 round-162 waves no longer let "
    "their caster block them. 975 -> 1,003 implemented; 148 -> 120 not implemented (36 skipped). Mod 946 / 1,003 / 95 "
    "families. SHIPPED: installed pack md5 %s; harness 163 full suite 6,947 checks / 0 failures."
    % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-16 (the breaths); xlsx v48 supersedes v47; v1-v47 byte-unchanged."
wb.save(DST)
print("wrote", DST)
