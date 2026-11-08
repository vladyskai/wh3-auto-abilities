#!/usr/bin/env python3
"""Build WH3_abilities_master_v21_2026-10-28.xlsx from v20 - the sign-off for
rounds 122 and 123 (tuning rounds that shipped without a workbook).

(1) 21 rows -> IMPLEMENTED with their trigger family and the trigger text
    derived from the same evaluator's existing rows (or, for the new
    enemy_melee family, composed from the source's own rule):
      round 122: 10 self-cast melee buffs on melee_unwavering;
      round 123: 4 melee_unwavering, 3 charge_or_melee, 3 enemy_melee, and the
      upgraded Hunter of Champions key on enemy_engaged_or_shot.
(2) Daemonic Possession -> SKIPPED (user decision): it only helps just before
    a friendly spell, so it is not automated.
(3) Every count re-derived from the edited sheet and the mod's own table:
    1,800 = 1,123 IN-WHEEL + 677 EXCLUDED; 759 implemented rows / keys;
    46 trigger families / 707 entries / 759 keys.
(4) Definitions: title v21, the count sentences, the glossary counts refreshed
    from the mod, and section 18 (the two rulings, the enemy_melee family, the
    four superseded earlier decisions). Changelog: a v21 row.

v1-v20 are never opened for writing: a NEW filename is written.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import os
import shutil

import openpyxl

import build_ability_database as bd

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v20_2026-10-20.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v21_2026-10-28.xlsx"
UAB = GP.UNIT_ABILITIES
ARMY_SPEC = GP.ARMY_SPEC

MU, CM, EM, EG = "melee_unwavering", "charge_or_melee", "enemy_melee", "enemy_engaged_or_shot"
ROWS = {
    "wh3_main_daemon_head_abilities_call_for_power": MU,
    "wh3_main_weapon_abilities_ursuns_claws": MU,
    "wh3_dlc23_weapon_abilities_black_hammer_of_hashut": MU,
    "wh3_dlc23_weapon_abilities_the_graven_sceptre": MU,
    "wh3_cp1_weapon_abilities_tyrants_talon": MU,
    "wh3_dlc29_item_abilities_crimson_blade": MU,
    "wh2_dlc14_lord_abilities_bloodstorm": MU,
    "wh3_dlc23_hero_abilities_crooked_dice": MU,
    "wh3_dlc20_lord_abilities_temptator": MU,
    "wh3_dlc27_unit_abilities_consuming_hatred": MU,
    "wh2_main_item_abilities_rival_hide_talisman": MU,
    "wh3_main_lord_abilities_seductive_glory": MU,
    "wh2_dlc15_item_abilities_vine_dragon_scale": MU,
    "wh3_dlc23_weapon_abilities_dark_mace": MU,
    "wh2_dlc11_lord_abilities_seduction": CM,
    "wh2_dlc11_lord_abilities_song_of_enthrallment": CM,
    "wh_dlc06_unit_abilities_smoke_bomb": CM,
    "wh3_main_character_abilities_no_escape": EM,
    "wh3_dlc29_lord_abilities_transfix": EM,
    "wh_pro01_lord_abilities_flash_bomb": EM,
    "wh2_dlc17_character_abilities_hunter_of_champions_upgraded": EG,
}
EM_BOUND = {  # key: (70% bound, real target_intercept_range)
    "wh3_main_character_abilities_no_escape": (70, 100),
    "wh3_dlc29_lord_abilities_transfix": (70, 100),
    "wh_pro01_lord_abilities_flash_bomb": (52, 75),
}
HOLD = {"wh3_main_character_abilities_no_escape": 90, "wh3_dlc29_lord_abilities_transfix": 120}
HOC_BASE = "wh_dlc08_character_abilities_hunter_of_champions"
DP = "wh3_main_lord_abilities_daemonic_possession"
DP_REASON = ("skipped (user decision 2026-10-27: Daemonic Possession only helps just before a "
             "friendly spell, so it is not automated)")
DP_IMPL = "SKIPPED (user decision)"

SHARED_TAIL = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this "
               "unit is known to own are evaluated (full-table fallback while its owned set is unknown); this "
               "(unit, ability) pair must be armed; readiness = can_perform_special_ability on the owned key (a "
               "variant walk when no usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, "
               "then 8 s silent back-off, hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown "
               "episode clears only on an accepted fire.")


def em_text(bound, real):
    return ("enemy_melee: not routing; enumerate the main enemy army list; per enemy: number_of_men_alive() > 0; "
            "is_valid_target() (fallback is_valid()) must not be false - unreadable passes; is_in_melee() must be "
            "true - the under-missile-fire arm is OFF (the melee-only flag; user ruling round 123: a melee-only "
            "debuff makes no sense on an enemy that is only being shot); unit_distance <= the entry's bound; the "
            "closest wins; bound: %d m (70%% of the ability's %d m target_intercept_range); cast target: that "
            "enemy unit; pre-cast re-check: the enemy must still be alive, still in melee and still within the "
            "bound, else the cast is skipped; " % (bound, real)) + SHARED_TAIL


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


def keys_of(r):
    return [k.strip() for k in str(ws.cell(row=r, column=3).value or "").split(";") if k.strip()]


row_of = {}
for r in range(2, ws.max_row + 1):
    for k in keys_of(r):
        row_of.setdefault(k, []).append(r)

# templates: the existing rows of the same evaluator, without a GATES clause
template = {}
for r in range(2, ws.max_row + 1):
    fam = str(ws.cell(row=r, column=21).value or "").strip()
    txt = str(ws.cell(row=r, column=22).value or "")
    if str(ws.cell(row=r, column=20).value) == "IMPLEMENTED" and fam in (MU, CM) and fam not in template \
            and "GATES" not in txt and txt.startswith(fam + ":"):
        template[fam] = txt
assert set(template) == {MU, CM}, template.keys()
hoc_rows = row_of[HOC_BASE]
assert len(hoc_rows) == 1
hoc_text = str(ws.cell(row=hoc_rows[0], column=22).value)
assert "bound: 70 m (70% of the ability's 100 m target_intercept_range)" in hoc_text

# ------------------------------------------------------------------ (1) the 21 rows
for key, fam in ROWS.items():
    rs = row_of.get(key, [])
    assert len(rs) == 1, (key, rs)
    r = rs[0]
    assert keys_of(r) == [key], (key, keys_of(r))
    assert str(ws.cell(row=r, column=18).value) == "IN-WHEEL", (key, ws.cell(row=r, column=18).value)
    assert str(ws.cell(row=r, column=20).value) == "NOT IMPLEMENTED", (key, ws.cell(row=r, column=20).value)
    assert str(ws.cell(row=r, column=19).value).startswith("carrier family:"), key
    if fam in (MU, CM):
        text = template[fam]
    elif fam == EM:
        text = em_text(*EM_BOUND[key])
    else:
        text = hoc_text
    if key in HOLD:
        text += " GATES (rounds 103-104): charge hold %d s (3 uses - one use per recharge period)." % HOLD[key]
    ws.cell(row=r, column=20).value = "IMPLEMENTED"
    ws.cell(row=r, column=21).value = fam
    ws.cell(row=r, column=22).value = text
print("rows implemented:", len(ROWS))

# ------------------------------------------------------------------ (2) Daemonic Possession
rs = row_of[DP]
assert len(rs) == 1 and str(ws.cell(row=rs[0], column=20).value) == "NOT IMPLEMENTED"
ws.cell(row=rs[0], column=19).value = DP_REASON
ws.cell(row=rs[0], column=20).value = DP_IMPL

# ------------------------------------------------------------------ (3) recount
rows = []
for r in range(2, ws.max_row + 1):
    rows.append((r, ws.cell(row=r, column=1).value, ws.cell(row=r, column=2).value, keys_of(r),
                 str(ws.cell(row=r, column=18).value), str(ws.cell(row=r, column=19).value),
                 str(ws.cell(row=r, column=20).value), str(ws.cell(row=r, column=21).value)))
N = len(rows)
status = collections.Counter(x[4] for x in rows)
impl = collections.Counter(x[6] for x in rows)
N_IN, N_EX = status["IN-WHEEL"], status["EXCLUDED"]
assert (N, N_IN, N_EX) == (1800, 1123, 677), (N, N_IN, N_EX)
N_IMPL_ROWS = impl["IMPLEMENTED"]
N_IMPL_KEYS = len(set(k for x in rows if x[6] == "IMPLEMENTED" for k in x[3]))
assert (N_IMPL_ROWS, N_IMPL_KEYS) == (759, 759), (N_IMPL_ROWS, N_IMPL_KEYS)
NOT_IMPL_IN = N_IN - N_IMPL_ROWS
assert NOT_IMPL_IN == 364, NOT_IMPL_IN
N_SKIP = impl["SKIPPED (user decision)"]
assert N_SKIP == 13, N_SKIP
assert not [x for x in rows if x[4] == "IN-WHEEL" and any(k in army for k in x[3])]

entries, consts, tips = bd.mod_entries()
mod_keys = set(k for e in entries for k in e["keys"])
assert (len(entries), len(mod_keys)) == (707, 759), (len(entries), len(mod_keys))
assert not (mod_keys & army)
impl_rows_keys = set(k for x in rows if x[6] == "IMPLEMENTED" for k in x[3])
assert impl_rows_keys == mod_keys, (sorted(impl_rows_keys - mod_keys)[:5], sorted(mod_keys - impl_rows_keys)[:5])
assert DP not in mod_keys

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
fam_inc, fam_impl = collections.Counter(), collections.Counter()
for x in rows:
    if x[4] != "IN-WHEEL":
        continue
    f = next((src_type[k] for k in x[3] if k in src_type), None)
    assert f in fam_order, (x[0], x[3])
    fam_inc[f] += 1
    if x[6] == "IMPLEMENTED":
        fam_impl[f] += 1
assert sum(fam_inc.values()) == N_IN and sum(fam_impl.values()) == N_IMPL_ROWS

trig = collections.Counter(e["trigger"] for e in entries)
trig_keys = collections.Counter()
for e in entries:
    trig_keys[e["trigger"]] += len(e["keys"])
assert len(trig) == 46 and sum(trig.values()) == 707 and sum(trig_keys.values()) == 759, \
    (len(trig), sum(trig.values()), sum(trig_keys.values()))
assert (trig[MU], trig[CM], trig[EM], trig[EG]) == (374, 28, 3, 85), (trig[MU], trig[CM], trig[EM], trig[EG])
# every implemented row's trigger family matches the mod entry that carries its key
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
bad = [(x[1], x[3][0], x[7], fam_by_key.get(x[3][0])) for x in rows
       if x[6] == "IMPLEMENTED" and x[3][0] in ROWS and x[7] != fam_by_key.get(x[3][0])]
assert not bad, bad

# ------------------------------------------------------------------ Numbers
n = wb["Numbers"]
tot = float(N)
n.cell(row=7, column=1).value = (
    "Date: 2026-10-28     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
    "(v21 - THE SIGN-OFF FOR ROUNDS 122 AND 123. Round 122 added ten self-cast melee buffs on "
    "melee_unwavering; round 123 added the hex batch with one trigger per ability (4 melee_unwavering, "
    "3 charge_or_melee, 3 on the NEW enemy_melee trigger) and the upgraded Hunter of Champions key. "
    "Implemented 738 + 21 = 759 rows / 759 keys; not implemented among the included 385 - 21 = 364 "
    "(13 of them SKIPPED by user decision, Daemonic Possession now among them). 1,123 IN-WHEEL + 677 "
    "EXCLUDED = 1,800, unchanged. The mod: 707 entries / 759 keys / 46 trigger families.)")
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
    for c, v in enumerate((num, label, abs_, p1, p2), 1):
        n.cell(row=r, column=c).value = v
n.cell(row=18, column=1).value = (
    "Included, by carrier family (unit_abilities.source_type) - ROW-LEVEL count, derived from this "
    "workbook's own 1,123 IN-WHEEL rows joined to unit_abilities.source_type by exact key: it TIES "
    "to the headline (sum = 1,123 included, 759 implemented).")
for i, f in enumerate(fam_order):
    r = 20 + i
    n.cell(row=r, column=1).value = i + 1
    n.cell(row=r, column=2).value = f
    n.cell(row=r, column=3).value = fam_inc[f]
    n.cell(row=r, column=4).value = fam_impl[f]
    n.cell(row=r, column=5).value = (fam_impl[f] / float(fam_inc[f])) if fam_inc[f] else 0
n.cell(row=28, column=3).value = sum(fam_inc.values())
n.cell(row=28, column=4).value = sum(fam_impl.values())
n.cell(row=40, column=1).value = (
    "Reconciliation (v21): included 1,123 + excluded 677 = 1,800 ROWS. Implemented among the included "
    "759 + not implemented 364 = 1,123. The mod's ABILITIES table is 707 entries / 759 keys, and the join "
    "mod-key -> 'Ability key(s)' returns 759 / 759 with ZERO unmatched keys in either direction. 687 + 10 "
    "(round 122) + 10 (round 123) = 707 entries; 738 + 10 + 11 = 759 keys (round 123's eleventh key is the "
    "upgraded Hunter of Champions, added to its existing entry). NO army-bar (army_spec) key in the mod: 0.")
n.cell(row=42, column=1).value = (
    "Trigger families after round 123 - re-counted from the mod's own ABILITIES table: 46 families / "
    "707 entries / 759 keys / 47 evaluators (ally_infinite_buff's evaluator stays unused since round 121). "
    "Rounds 122-123: melee_unwavering 360 -> 374, charge_or_melee 25 -> 28, enemy_engaged_or_shot 85 entries "
    "(93 -> 94 keys), and the NEW enemy_melee family (3).")
for r in range(44, 92):
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
assert tot_row == 90, tot_row
n.cell(row=tot_row, column=2).value = "TOTAL (46 families / 47 evaluators)"
n.cell(row=tot_row, column=3).value = sum(trig.values())
n.cell(row=tot_row, column=4).value = sum(trig_keys.values())
assert n.cell(row=92, column=1).value == "Bombardment set (COMPLETE - round 108)"

# ------------------------------------------------------------------ Definitions
d = wb["Definitions"]
assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v20")
d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v21 (2026-10-28)"
r11 = d.cell(row=11, column=2)
assert "738 keys across 738 numbered rows" in r11.value
r11.value = r11.value.replace("738 keys across 738 numbered rows",
                              "759 keys across 759 numbered rows (rounds 122-123 added 21)")
r12 = d.cell(row=12, column=2)
assert "of which 385 are in the wheel" in r12.value and "(1,058 keys" in r12.value
r12.value = (r12.value.replace("of which 385 are in the wheel", "of which 364 are in the wheel")
             .replace("(1,058 keys", "(1,041 keys"))
assert str(d.cell(row=21, column=1).value).startswith("3. TRIGGER-FAMILY GLOSSARY")
refreshed = []
for r in range(24, 100):
    fam = d.cell(row=r, column=1).value
    if fam in trig and str(d.cell(row=r, column=5).value).isdigit():
        d.cell(row=r, column=5).value = trig[fam]
        d.cell(row=r, column=6).value = trig_keys[fam]
        refreshed.append(fam)
assert {MU, CM, EG} <= set(refreshed), refreshed
cov_gate = sum(1 for x in rows if x[6] == "IMPLEMENTED"
               and any(w in x[5] or w in str(ws.cell(row=x[0], column=22).value or "")
                       for w in ("wind-up", "charge gate", "recharge_time", "in-flight", "per-unit")))
r104 = d.cell(row=104, column=1)
assert "Coverage in this workbook:" in str(r104.value)
r104.value = (str(r104.value).split("Coverage in this workbook:")[0]
              + "Coverage in this workbook: %d of the %d implemented rows (%d keys) carry at least one gate "
              "clause in their Trigger (as implemented) text; rows with neither a multi-use pool nor a wind-up "
              "keep the plain 2 s guard." % (cov_gate, N_IMPL_ROWS, N_IMPL_KEYS))

base = d.max_row + 2
sec = [
    ("18. ROUNDS 122 AND 123 - TEN MELEE BUFFS, THE HEX BATCH AND THE enemy_melee TRIGGER (v21 sign-off)", None),
    ("ROUND 122 RULING, VERBATIM", "Approved as recommended: Group A on melee_unwavering, Group B on "
     "melee_unwavering. Implement as a tuning round."),
    ("ROUND 122 ROWS (10, melee_unwavering)", "Call for Power, Manus of Ursun, Black Hammer of Hashut, The Graven "
     "Sceptre, Tyrant's Talon, The Crimson Blade (melee damage); Bloodstorm, Crooked Dice, Temptator, "
     "All-Consuming Hatred (melee survival). All self-cast, self-only (no range constant)."),
    ("ROUND 123 RULING, VERBATIM", "Of Group A, the ones that have no speed effects should have the "
     "melee_unwavering trigger. The ones that reduce the enemies speed should trigger in melee or when charging. "
     "This way we avoid the issue of fire on an enemy that is only passing by. Of Group B, they need more "
     "diversity. The one with effect only -40 melee defense makes sense only when the enemy is in melee. It does "
     "not make sense to activate it when the enemy is shot (please learn from this example). The Transfix (dlc29 "
     "key) should be the same, since a trigger for the Silenced condition would be hard to implement. Flash bomb "
     "can be the same, we might think later if a trigger that leverages its speed reduction makes sense. Daemonic "
     "possesion would make sense only before a cast, so I say we do not automate that one. Hunter of champions is "
     "okay for enemy_engaged_or_shot."),
    ("ROUND 123 ROWS (11)", "melee_unwavering: Rival Hide Talisman, Seductive Glory, Vine Dragon Scale, Dark Mace. "
     "charge_or_melee: Seduction, Song of Enthrallment, Smoke Bomb. enemy_melee: No Escape (70 m, held 90 s), "
     "Transfix dlc29 hex key (70 m, held 120 s, marker transfix_hex), Flash Bomb (52 m). enemy_engaged_or_shot: "
     "the upgraded Hunter of Champions key, joined to the existing entry. Daemonic Possession: SKIPPED (user "
     "decision)."),
    ("THE NEW FAMILY: enemy_melee", "evaluate_enemy_melee | the shared enemy picker with the melee-only flag on: "
     "an enemy alive, a valid target, IN MELEE and within the entry's own 70% bound; the closest wins; an enemy "
     "only under missile fire never qualifies; the pre-cast re-check skips the cast if the enemy left melee | "
     "cast target: that enemy unit | 3 entries / 3 keys"),
    ("THE STANDING RULE IT CAME WITH", "The trigger follows the effect, per ability: name the stat each ability "
     "changes and the moment it pays off. A melee-only stat (melee attack, melee defence, weapon damage) never "
     "goes on a trigger with a missile arm; enemy speed reductions fire in melee or on the charge; an effect "
     "that only helps before something else happens is not automated."),
    ("EARLIER DECISIONS SUPERSEDED", "Four implemented abilities had an earlier questionnaire decision that the "
     "round-122/123 proposals missed (they were built from this workbook, which does not carry those decisions): "
     "Call for Power (rejected, Rampage), Manus of Ursun (rejected, Rampage rule), All-Consuming Hatred "
     "(rejected, drawback Melee Defence -12), Seductive Glory (skipped, 'Skip for now'). On 2026-10-28 the user "
     "ruled to keep all four; every ability starts unarmed (M)."),
    ("THE ARITHMETIC", "Implemented 738 + 21 = 759 rows = 759 keys; not implemented among the included "
     "385 - 21 = 364 (13 SKIPPED by user decision); 1,123 IN-WHEEL + 677 EXCLUDED = 1,800 unchanged. Mod: "
     "687 -> 707 entries, 738 -> 759 keys, 45 -> 46 families. Harness 122 full suite: 5,359 checks / 0 "
     "failures, run twice byte-identical."),
]
for i, (a, b) in enumerate(sec):
    d.cell(row=base + i, column=1).value = a
    if b is not None:
        d.cell(row=base + i, column=2).value = b

# ------------------------------------------------------------------ Changelog
ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-10-28"
ch.cell(row=r, column=2).value = "v21"
ch.cell(row=r, column=3).value = (
    "SIGN-OFF FOR ROUNDS 122 AND 123. (1) ROUND 122: ten self-cast melee buffs on melee_unwavering (Call for "
    "Power, Manus of Ursun, Black Hammer of Hashut, The Graven Sceptre, Tyrant's Talon, The Crimson Blade, "
    "Bloodstorm, Crooked Dice, Temptator, All-Consuming Hatred). (2) ROUND 123, one trigger per ability from "
    "its effect: melee_unwavering (Rival Hide Talisman, Seductive Glory, Vine Dragon Scale, Dark Mace), "
    "charge_or_melee (Seduction, Song of Enthrallment, Smoke Bomb), the NEW enemy_melee family (No Escape, "
    "Transfix dlc29, Flash Bomb), and the upgraded Hunter of Champions key on enemy_engaged_or_shot. Daemonic "
    "Possession SKIPPED by user decision. (3) 21 rows IMPLEMENTED: 738 -> 759 rows / keys; 385 -> 364 not "
    "implemented among the included; 1,123 + 677 = 1,800 unchanged. Mod 707 entries / 759 keys / 46 families. "
    "(4) Four earlier decisions superseded by the user's 2026-10-28 ruling (Call for Power, Manus of Ursun, "
    "All-Consuming Hatred, Seductive Glory). (5) SHIPPED: installed pack md5 %s; harness 122 full suite "
    "5,359 checks / 0 failures." % os.environ.get("WH3_PACK_MD5", "PENDING"))
ch.cell(row=r, column=4).value = ("user rulings 2026-10-27 (rounds 122, 123) and 2026-10-28 (keep the four); "
                                  "xlsx v21 supersedes v20; v1-v20 byte-unchanged.")

wb.save(DST)
print("wrote", DST)
print("rows", N, "in-wheel", N_IN, "excluded", N_EX, "impl rows", N_IMPL_ROWS, "impl keys", N_IMPL_KEYS,
      "not-impl in-wheel", NOT_IMPL_IN, "skipped", N_SKIP)
print("families", len(trig), "entries", sum(trig.values()), "keys", sum(trig_keys.values()),
      "glossary refreshed", len(refreshed), "gate coverage", cov_gate)
