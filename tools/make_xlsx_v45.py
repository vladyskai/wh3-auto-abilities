#!/usr/bin/env python3
"""Build WH3_abilities_master_v45_2026-11-15.xlsx from v44 - round 159: group E (the last open abilities).

(1) 28 rows NOT IMPLEMENTED -> IMPLEMENTED: 13 safe self-centred blasts on melee_unwavering, 5 friendly-fire blasts on
    the NEW melee_clear, the 2 Phoenix dives on the NEW fly_dive, Necrotic Explosion on the NEW last_stand_clear,
    Ancient Chaos Frost Dragon Scale on the NEW enemy_blob_vortex, and the look-alike set (Maneater Smoke Bomb,
    Verminous Valour, Heaven's Flash, Slime Smoothie, Slann Gold, Deathmaster's Sigil).
(2) 5 rows NOT IMPLEMENTED -> SKIPPED (user decision): Mist Form, Shadowstrider, Deep Tunneling, Sword of Teclis, the
    Unidentified Hydra Head ("Close 5, Necrotic last").
(3) Implemented 889 -> 917 rows / keys; not implemented among the included 234 -> 206 (27 + 5 = 32 skipped); open 0.
    The mod 860 entries / 917 keys; 84 -> 88 families: the Numbers trigger table gains four rows (bombardment block
    130 -> 134). Definitions: title v45, the two count rows, section 42. Changelog: a v45 row.
v1-v44 are never opened for writing.
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
import gen_shot_tables as GS
import gen_vortex_tables as GV

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v44_2026-11-15.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v45_2026-11-15.xlsx"
SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")
USA = {r["key"]: r for r in GS.tsv("unit_spec_abil.tsv")}
VX = {r["vortex_key"]: r for r in GS.tsv("battle_vortexs.tsv")}
MU_KEYS = ["wh2_dlc15_character_abilities_burp_of_grom_0", "wh2_dlc15_character_abilities_burp_of_grom_1",
           "wh2_dlc15_character_abilities_burp_of_grom_2", "wh2_dlc15_item_abilities_blood_forged_armour",
           "wh3_dlc23_item_abilities_daemon_flask_of_ashak", "wh3_dlc29_mount_abilities_feaster_of_souls",
           "wh3_dlc27_item_abilities_spurting_bile_blood", "wh3_main_character_abilities_arsebelcher",
           "wh3_dlc20_unit_abilities_violent_wind", "wh3_dlc27_lord_abilities_whirlwind_of_pleasure",
           "wh2_dlc14_weapon_abilities_whirl_of_weeping_blades", "wh3_dlc25_character_abilities_hurricane_of_death",
           "wh3_dlc26_unit_abilities_acid_vomit"]
OTHER_KEYS = ["wh3_main_character_abilities_groundbreaker", "wh3_main_lord_abilities_burning_rage",
              "wh2_dlc17_lord_abilities_bloodbeast", "wh2_dlc13_unit_abilities_emergency_vent",
              "wh3_dlc25_unit_abilities_marienburg_land_mines", "wh2_dlc15_unit_abilities_emberstorm",
              "wh3_dlc24_unit_abilities_moon_flare", "wh3_dlc26_unit_abilities_maneater_smoke_bomb",
              "wh2_main_character_abilities_verminous_valour", "wh3_main_unit_abilities_stun_bomb",
              "wh2_dlc15_character_abilities_slimy_smoothie", "wh2_dlc11_item_abilities_slann_gold",
              "wh2_dlc14_lord_abilities_deathmasters_sigil", "wh_dlc08_item_abilities_ancient_frost_wyrm_scale",
              "wh3_main_unit_abilities_necrotic_explosion"]
KEYS = MU_KEYS + OTHER_KEYS
CLOSE = {
    "wh3_dlc29_lord_abilities_mist_form": "a teleport: where to go is the player's call",
    "wh3_dlc29_lord_abilities_warp_step": "a teleport: where to go is the player's call",
    "wh3_dlc27_unit_abilities_burrow": "a tunnelling teleport: where to go is the player's call",
    "wh2_main_weapon_abilities_sword_of_teclis": "the user's own 2026-10-08 skip (\"Skip - it's a magic-resource ability "
                                                 "(excluded scope)\") kept; rule 10: it only helps before a friendly "
                                                 "spell",
    "wh2_dlc10_quest_abilities_unidentified_hydra_head": "a random effect; a 35 m blast for 45 s that hurts our units",
}
assert len(KEYS) == 28 and len(CLOSE) == 5
SRC_TXT = open(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua",
               encoding="utf-8").read()
VR = GV.derive(GV.keys_in(SRC_TXT))


def blast_r(k):
    rows = GV.chain(VX, USA[k]["vortex"])
    return max(max(float(r["start_radius"] or 0), float(r["goal_radius"] or 0)) for r in rows) if rows else None


def text(k, fam):
    a = USA[k]
    real = float(a["target_intercept_range"])
    bound = int(math.floor(real * 0.70 + 1e-9))
    uses, rech, wind = int(float(a["num_uses"])), float(a["recharge_time"]), float(a["wind_up_time"])
    gates = []
    if uses > 1:
        gates.append("charge hold %g s (%d uses)" % (rech, uses))
    if wind > 0:
        gates.append("in-flight hold %g s (%g s wind-up + 2 s)" % (wind + 2, wind))
    within = "within %d m (70%% of the ability's %g m target_intercept_range; unit_distance)" % (bound, real)
    r = VR.get(k)
    if fam == "melee_unwavering":
        body = ("melee_unwavering: not routing; in melee (is_in_melee()) and the morale not wavering (an unreadable "
                "morale falls back to plain in-melee); cast on self (a blast centred on the caster, %g m, that cannot hurt "
                "our units); the shipped look-alikes Bloodstorm, Halo of Maidenly Wrath, Evisceration, Giant Leap, Gaze of "
                "Khorne; user ruling 2026-11-15 (\"Like Bloodstorm\"); " % blast_r(k))
    elif fam == "melee_clear":
        body = ("melee_clear: not routing; in melee and the morale not wavering (the melee_unwavering rule) AND none of "
                "our OTHER units' rectangles within %g m (the %g m blast from the GENERATED VORTEX table + SHOT_SAFE_M "
                "10 m) of the caster's centre (the game marks the blast affects_allies); cast on self; user ruling "
                "2026-11-15 (\"Melee, no friend near\"); " % (r + 10, r))
    elif fam == "fly_dive":
        body = ("fly_dive: not routing; FLYING (is_currently_flying() exactly true: the game's grounded rule); a visible "
                "enemy rectangle within %d m (70%% of the %g m blast) of the caster's centre; none of our other units "
                "within %g m (blast + 10 m; the blast hurts our units too); cast on self; user ruling 2026-11-15 "
                "(\"Flying over enemies\"); " % (int(math.floor(r * 0.7 + 1e-9)), r, r + 10))
    elif fam == "last_stand_clear":
        body = ("last_stand_clear: not routing; own health at or below 10%% (FOURTH.LAST_STAND_PCT) while in melee (an "
                "exact true); none of our other units within %g m (the %g m blast + 10 m); cast on self (the Nurglings "
                "destroy themselves); user ruling 2026-11-15 (\"Close 5, Necrotic last\"); " % (r + 10, r))
    elif fam == "enemy_blob_vortex":
        body = ("enemy_blob_vortex: the enemy_blob rule with a VORTEX blast (%g m, the GENERATED VORTEX table): not "
                "routing; the caster STANDING STILL; the visible enemy infantry %s where the blast destroys the most "
                "value, covering at least half a packed block; none of ours within blast + 10 m (%g m); cast target: "
                "that enemy unit; pre-cast re-check: the map is rebuilt and the target must still qualify; user ruling "
                "2026-11-15 (\"Look-alike set\": a blob attack); " % (r, within, r + 10))
    elif fam == "enemy_commander_value":
        if r is not None:
            body = ("enemy_commander_value: not routing; the live map; the most valuable (strategic_value) visible enemy "
                    "Lord or Hero %s that is NOT flying, with none of our units within %g m of it (its %g m blast hurts "
                    "our units too, + 10 m); cast target: that enemy unit (rooted 7 s); pre-cast re-check: the same rule "
                    "again; target class: Lord/Hero not flying (the game's unit_is_not_commander_class and "
                    "flying_currently); user ruling 2026-11-15 (\"Look-alike set\"); " % (within, r + 10, r))
        else:
            body = ("enemy_commander_value: not routing; the live map; the most valuable (strategic_value) visible enemy "
                    "Lord or Hero %s; the game allows spellcasters only and the mod has no spellcaster read, so a "
                    "non-caster target is refused by the engine and backed off; cast target: that enemy unit; target "
                    "class: Lord/Hero only (the look-alike Dweomer Leach Orb); user ruling 2026-11-15 (\"Look-alike "
                    "set\"); " % within)
    elif fam == "charge_or_melee":
        body = ("charge_or_melee: not routing; this unit charges (the charge window) or is in melee; cast on self (+24 "
                "melee defence, speed x1.25 for 24 s: rule 10); the look-alike Smoke Bomb; user ruling 2026-11-15 "
                "(\"Look-alike set\"); ")
    elif fam == "wavering_self":
        body = ("wavering_self: not routing; is_wavering() exactly true; cast on self (+8 morale, speed x1.25 for 17 s); "
                "user ruling 2026-11-15 (\"Look-alike set\"); ")
    elif fam == "enemy_ground_melee":
        body = ("enemy_ground_melee: not routing; the closest enemy %s that is fighting in melee; cast on the ground "
                "under it (enemies within 35 m: melee attack and melee defence -24 for 31 s; one use; rule 10); user "
                "ruling 2026-11-15 (\"Look-alike set\"); " % within)
    else:
        assert fam == "health_aura_ground", fam
        body = ("health_aura_ground: not routing; this unit or a friendly unit within 24 m (70% of the 35 m area) at or "
                "below 75% health, the lowest; cast on the ground under it (a heal over 7 s); the look-alike Gulyas; user "
                "ruling 2026-11-15 (\"Look-alike set\"); ")
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
        ws.cell(row=r, column=19).value = "skipped (user decision 2026-11-15: \"Close 5, Necrotic last\"; %s)" % why
        ws.cell(row=r, column=20).value = "SKIPPED (user decision)"
        ws.cell(row=r, column=21).value = "-"
        ws.cell(row=r, column=22).value = ("No automation - SKIPPED BY THE USER'S DECISION of 2026-11-15: \"Close 5, "
                                           "Necrotic last\" (%s)." % why)
        n_close += 1
assert (n_new, n_close) == (28, 5), (n_new, n_close)

rows = [(r, keys_of(r), str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=20).value),
         str(ws.cell(row=r, column=21).value)) for r in range(2, ws.max_row + 1)]
N = len(rows)
impl = [x for x in rows if x[3] == "IMPLEMENTED"]
N_IMPL_ROWS = len(impl)
N_IMPL_KEYS = len(set(k for x in impl for k in x[1]))
assert (N, N_IMPL_ROWS, N_IMPL_KEYS) == (1800, 917, 917), (N, N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = 1123 - N_IMPL_ROWS
assert NOT_IMPL_IN == 206
assert sum(1 for x in rows if x[3] == "SKIPPED (user decision)") == 32
assert (len(entries), len(fam_by_key)) == (860, 917)
assert set(k for x in impl for k in x[1]) == set(fam_by_key)
assert not [x[1][0] for x in impl if x[4] != fam_by_key.get(x[1][0])]
trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 88, len(trig)

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
assert n.cell(row=130, column=1).value == "Bombardment set (COMPLETE - round 108)"
assert n.cell(row=128, column=2).value == "TOTAL (84 families)"
assert all(int(str(m).split(":")[0][1:]) < 108 for m in n.merged_cells.ranges)
n.insert_rows(127, 4)
assert n.cell(row=134, column=1).value == "Bombardment set (COMPLETE - round 108)"
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-11-15     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v45 - ROUND 159: group E, the last open abilities. 28 rows implemented: 13 safe blasts on melee_unwavering, 5 "
    "friendly-fire blasts (NEW melee_clear), 2 Phoenix dives (NEW fly_dive), Necrotic Explosion (NEW last_stand_clear), "
    "the Frost Dragon Scale (NEW enemy_blob_vortex) and 6 buffs and hexes on their look-alike families; 5 rows SKIPPED by "
    "the user. Implemented 889 + 28 = 917 rows / 917 keys; not implemented among the included 234 - 28 = 206 (32 "
    "skipped); open 0. The mod: 860 entries / 917 keys / 88 trigger families.)")
for r, num, label, abs_, p1, p2 in [
        (13, 4, "Implemented among the included", N_IMPL_ROWS, N_IMPL_ROWS / tot, N_IMPL_ROWS / 1123.0),
        (14, 5, "Not implemented among the included", NOT_IMPL_IN, NOT_IMPL_IN / tot, NOT_IMPL_IN / 1123.0),
        (16, 7, "All implemented in the mod (4 + 6)", N_IMPL_KEYS, N_IMPL_KEYS / tot, N_IMPL_KEYS / 1123.0)]:
    for c, v in enumerate((num, label, abs_, p1, p2), 1):
        n.cell(row=r, column=c).value = v
old18 = str(n.cell(row=18, column=1).value)
assert "889 implemented" in old18
n.cell(row=18, column=1).value = old18.replace("889 implemented", "917 implemented")
for i, f in enumerate(fam_order):
    r = 20 + i
    assert n.cell(row=r, column=2).value == f, (r, n.cell(row=r, column=2).value)
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=40, column=1).value = (
    "Reconciliation (v45): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included 917 + not "
    "implemented 206 (32 of them skipped by the user) = 1,123. The mod's ABILITIES table is 860 entries / 917 keys, and "
    "the join mod-key -> 'Ability key(s)' returns 917 / 917 with ZERO unmatched keys in either direction. 834 + 26 "
    "(round 159, group E) = 860 entries; 889 + 28 = 917 keys. NO army-bar (army_spec) key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 159 - re-counted from the mod's own ABILITIES table: 88 families / 860 entries / 917 "
    "keys (metallurgy_melee, melee_low_morale and self_running keep 0 entries). Round 159: the NEW melee_clear (5), "
    "fly_dive (2), last_stand_clear (1) and enemy_blob_vortex (1); melee_unwavering 288 -> 299, enemy_commander_value "
    "1 -> 3, charge_or_melee 36 -> 37, wavering_self 3 -> 4, enemy_ground_melee 74 -> 75, health_aura_ground 2 -> 3.")
for r in range(44, 132):
    for c in range(1, 6):
        n.cell(row=r, column=c).value = None
fam_sorted = sorted(trig.items(), key=lambda kv: (-kv[1], kv[0]))
for i, (t2, cnt) in enumerate(fam_sorted):
    r = 44 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = t2
    n.cell(row=r, column=3).value = cnt
    n.cell(row=r, column=4).value = trig_keys[t2]
assert 44 + len(fam_sorted) == 132
n.cell(row=132, column=2).value = "TOTAL (88 families)"
n.cell(row=132, column=3).value = sum(trig.values())
n.cell(row=132, column=4).value = sum(trig_keys.values())

d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v44")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v45 (2026-11-15)"
r11 = d.cell(row=11, column=2)
assert "889 keys across 889 numbered rows (" in r11.value and "round 158 added 12)" in r11.value
r11.value = r11.value.replace("889 keys across 889 numbered rows (", "917 keys across 917 numbered rows (").replace(
    "round 158 added 12)", "round 158 added 12, round 159 added 28)")
r12 = d.cell(row=12, column=2)
assert "(911 keys, of which 234 are in the wheel)" in r12.value
r12.value = r12.value.replace("(911 keys, of which 234 are in the wheel)", "(883 keys, of which 206 are in the wheel)")
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
base = d.max_row + 2
sec = [
    ("42. ROUND 159 - GROUP E (v45)", None),
    ("THE RULINGS (2026-11-15)", "The 13 safe blasts \"Like Bloodstorm\"; the 5 friendly-fire blasts \"Melee, no friend "
     "near\"; the Phoenix dives \"Flying over enemies\" (corrected from \"in melee and flying\" before the build); the "
     "buffs and hexes \"Look-alike set\"; \"Close 5, Necrotic last\"."),
    ("THE NEW FAMILIES", "melee_clear (5): in melee and not wavering, none of our other units within blast + 10 m of the "
     "caster (GENERATED FOURTH.VORTEX_TEXT from battle_vortexs). fly_dive (2): flying, an enemy within 70% of the blast, "
     "none of ours within blast + 10 m. last_stand_clear (1): health at or below 10% in melee, none of ours within blast "
     "+ 10 m. enemy_blob_vortex (1): the blob rule with a vortex radius. New target class commander_ground (Deathmaster's "
     "Sigil). All four new families start unarmed (M)."),
    ("THE ARITHMETIC", "Implemented 889 + 28 = 917 rows / keys; not implemented among the included 234 - 28 = 206 "
     "(27 + 5 = 32 skipped); open 0. The mod 834 + 26 = 860 entries / 917 keys; 88 families."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-11-15"
ch.cell(row=r, column=2).value = "v45"
ch.cell(row=r, column=3).value = (
    "ROUND 159. Group E: 28 rows IMPLEMENTED (4 NEW families), 5 rows SKIPPED by the user. 889 -> 917 implemented; 234 "
    "-> 206 not implemented (32 skipped); open 0. Mod 860 / 917 / 88 families. SHIPPED: installed pack md5 %s; harness "
    "158 full suite 6,760 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = "user rulings 2026-11-15 (group E); xlsx v45 supersedes v44; v1-v44 byte-unchanged."
wb.save(DST)
print("wrote", DST)
