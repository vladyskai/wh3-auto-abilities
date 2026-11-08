#!/usr/bin/env python3
"""Round 130: the tracker rows, the tracker's round section and the database family texts
for Restock!, Ballistics Calibration and Skjalandir's Fall's shooting arm."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"

T_EDITS = [
    ("| Restock! `wh2_dlc17_hero_abilities_more_powder_generic` | `excluded (auto: no ammo-low read (ammo replenish))` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 60s · 10s · friend · ×4 uses |",
     "| Restock! `wh2_dlc17_hero_abilities_more_powder_generic` | `implemented (ally-targeted: ally_ammo_low)` | ally_unit | When a friendly unit within 70 m (70% of the 100 m reach) is shooting and has 70% or less of its ammunition left: cast on the one with the least left. | cd 60s · 10s · friend · ×4 uses · **round 130 (user ruling 2026-11-01, option A):** the firing flag (ammo_left() drop) says it is shooting; 70% = 100% - the 30% refill, so nothing is wasted; charge hold 60 s; an ally refilled in the last 12 s is skipped by every caster. |"),
    ("| Ballistics Calibration `wh_main_hero_abilities_ballistics_calibration` | `excluded (auto: ground-target-only)` | ready | Whenever the engine allows (no readable condition): cast on the ground. | cd 90s · 22s · ground |",
     "| Ballistics Calibration `wh_main_hero_abilities_ballistics_calibration` | `implemented (ground at the caster: allies_firing_aura)` | ground | When at least 2 friendly units within 38 m (70% of the 55 m aura) are shooting past their cast point: cast on the ground at the caster's own feet. | cd 90s · 22s · ground · **round 130 (user ruling 2026-11-01, option A):** Reload Skill +20 pays off while units reload; the cast point is first shot + 0.5 x reload; cast at the caster's own position, so no move order. |"),
    ("| Skjalandir's Fall `wh3_dlc23_character_abilities_skjalandirs_fall` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 39s · self |",
     "| Skjalandir's Fall `wh3_dlc23_character_abilities_skjalandirs_fall` | `implemented (melee or shooting into melee)` | ready | In melee (as before), OR shooting past its cast point at an enemy that is in melee: cast on self. | cd 120s · 39s · self · **round 130 (user ruling 2026-11-01, \"Shooting into melee\"):** the ranged half deferred in round 124; Accuracy +90 and Blinded! on arrow hits help the fighters in that melee. |"),
]

SECTION = """

### 10.11 Round 130 - the first triggers on the firing flag (2026-11-01)

**Rulings (2026-11-01), verbatim:** *"Please implement the both recommended options."* (Restock! option A,
Ballistics Calibration option A.) Skjalandir's Fall, asked which shooting trigger: *"Shooting into melee"*.
Earlier decision quoted in the proposal: both Restock! and Ballistics Calibration were on the user's deferred
next-batch list (2026-11-01); neither had been rejected or skipped.

- **Restock!** (`ally_ammo_low`, NEW): an ally within 70 m that is shooting (firing flag on) with 70% or less of
  its ammunition left; the one with the least left is the target. Charge hold 60 s (4 uses); an ally refilled in
  the last 12 s is skipped by every caster.
- **Ballistics Calibration** (`allies_firing_aura`, NEW): at least 2 allies within 38 m shooting past their cast
  point; the ground form at the caster's own position.
- **Skjalandir's Fall** (`melee_or_shooting_into_melee`, NEW): the melee trigger it had, or shooting past its cast
  point at an enemy that is in melee.

**Arithmetic.** Implemented rows 759 + 2 = **761 rows / 761 keys** (Skjalandir's Fall was already implemented).
Not implemented among the included 364 - 2 = **362**. The mod: 707 -> **709 entries**, 759 -> **761 keys**,
46 -> **49 trigger families** (melee_unwavering 374 -> 373). Harness 129 full suite: **5,577 checks / 0 failures**,
run twice byte-identical; RED on the round-129 build: 8/8 (none of the three casts). Installed pack md5
`0e786a41ce6a2a6f566f3b6c9b5172cd`.
"""

DB_OLD = '        "ally_missile": "A missile-capable ally in range (`land_units.primary_missile_weapon` non-empty). Casts on that ally.",\n'
DB_NEW = DB_OLD + (
    '        "ally_ammo_low": "An ally in range that is SHOOTING (the firing flag: its ammo_left() dropped) with 70% or less of its ammunition left (`FOURTH.RESTOCK_AT_FRACTION`, 100% minus the 30% refill); the one with the least left wins; an ally refilled in the last `FOURTH.RESTOCK_CLAIM_S` (12 s) is skipped. Casts on that ally.",\n'
    '        "allies_firing_aura": "At least `FOURTH.BALLISTICS_MIN_FIRING` (2) allies inside the aura bound are SHOOTING past their cast point (first shot + 0.5 x their reload). Cast on the ground at the caster\'s own position.",\n'
    '        "melee_or_shooting_into_melee": "In melee and not wavering (as melee_unwavering), OR shooting past its cast point at a current target that is in melee. Casts on the unit itself.",\n')
CT_OLD = "    CAST_TARGET = {\n"
CT_NEW = CT_OLD + '        "allies_firing_aura": "the ground at the caster\'s own position (ground form)",\n'

s = open(TRACKER, encoding="utf-8", newline="").read()
for a, b in T_EDITS:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
assert "### 10.11" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION + "".join(b for _, b in T_EDITS)
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: 3 rows + section 10.11")

d = open(DBB, encoding="utf-8", newline="").read()
for a, b in ((DB_OLD, DB_NEW), (CT_OLD, CT_NEW)):
    assert d.count(a) == 1, a[:60]
    d = d.replace(a, b)
open(DBB, "w", encoding="utf-8", newline="").write(d)
print("database builder: 3 family texts + 1 cast target")
