# Round 106 — the bombardment round: Soulfire/Arachneruption and the 30 bombardment abilities

Date: 2026-10-18 · Harness 106 · Installed pack md5 `9108e7f685180cbb637ee8b9ef53cf24`

Two user-approved families, both implemented. The research answers (R1–R4) are in
`docs/WH3_bombardment_research.md`.

---

## 1. Soulfire + Arachneruption — `melee_skip_commanders`

**User's rule:** fire when the caster is in melee, but skip when it is fighting ONLY a Lord or a Hero.

* **Two entries**: `soulfire` carries BOTH keys (`wh_main_spell_bound_soulfire`,
  `wh_dlc04_spell_bound_soulfire_upgraded` = Grand Soulfire); `arachneruption` carries
  `wh2_dlc15_unit_abilities_arachneruption`. Both are self-centred rows (target flags all false, range 0),
  so the cast is on the OWNER through the unit form.
* **The engagement set** is read from the game's own enemy enumerator: every enemy that is ALIVE,
  `is_in_melee() == true`, and whose edge-to-edge `unit_distance()` to the caster is within
  **`FOURTH.ENGAGE_CONTACT_M = 12` m**. Each member is classified by the existing **1,409-key commander set**
  (`FOURTH.enemy_is_commander`: exact whole-key equality on `battle_unit:type()`, `unit_class() == "com"`
  fallback, FAIL CLOSED).
* **Fire rule**: any non-commander in the set → fire. Every member a commander → hold.
* **Auditable**: the judged set is written to the log with each member's type, its commander flag and the
  REAL distance, once per (unit, marker) and again only when it changes:

  ```
    soulfire engagement set: 2 enemy unit(s) in contact (<= 12m): 'wh_main_emp_cha_general_0' COMMANDER 1.0m, 'wh2_dlc13_emp_inf_spearmen_ror_0' non-commander 3.0m -> FIRING (a non-commander is engaged)
  ```
* **Fallbacks, in order**: nothing readable in contact → the caster's own `current_target()` (a commander
  target holds, anything else fires); no target at all → the plain in-melee rule fires and says so.
* **Limits** (stated plainly): the set is "in melee + within 12 m", not the engine's internal engagement
  graph — the API exposes no per-enemy engagement list. A distant enemy fighting someone else is correctly
  excluded by the distance test; a melee scrum where the caster is 13 m from the nearest enemy would read
  as "nothing engaged" and fall back to `current_target()`. The 12 m is one constant.

**Counts:** +2 entries, +3 keys, +1 evaluator.

---

## 2. The 32 approved bombardment abilities — 30 shipped

**User's rule:** the closest infantry enemy in range that is in melee; cast at its position, in whichever
form the ability declares.

* **New trigger `enemy_ground_melee_infantry`**: the CLOSEST enemy inside the ability's own **70% bound**
  that is **IN MELEE** and **IS INFANTRY**; the lowest `unit_distance` wins.
* **Infantry is a REAL read**: `battle_unit:is_infantry()` first (the API dump's own documented read),
  `battle_unit:unit_class()` exact-match against `inf_mel` / `inf_mis` / `inf_spr` as the fallback,
  **FAIL CLOSED** when neither answers. (The task asked for a derived `infantry_keys` set like
  `commander_keys`; the engine read is strictly better — a 942-key static list would miss every DLC unit
  whose key is not in it — so the READ comes first and the exact-match class test is the fallback.)
* **Cast form follows each row's own flags**: 24 ground-targeted keys use
  `perform_special_ability_ground(key, enemy:position(), 0, 0)`; 6 unit-targeted keys
  (Lesser Doombolt, Rod of Torment, Tome of Furion, Wand of the Kharaidon, Wolf's Howl, Wraith Storm) use
  `perform_special_ability(key, enemy)`.
* **Pre-cast re-check**: immediately before the call the chosen enemy is re-read (alive, still in melee,
  still INFANTRY, still inside the bound) and the cast is skipped rather than wasted.
* **New bound**: real 300 m → **210 m** (`FOURTH.ENEMY_CAST_R300`), used by Celestial Lightning,
  Lightning Strike, Rod of the Storm and Urannon's Thunderbolt.
* **Charge gate** +25 keys, **in-flight gate** +29 keys (the rows' own `num_uses` / `recharge_time` /
  `wind_up_time`).

**Skipped and reported (2 of 32):**

| ability | why |
|---|---|
| **Thorsen's Thunderstorm** (both keys) | army-bar: both are `army_spec.tsv` junctions → out of wheel scope |
| **Warp Lightning Rod** | no enemy target at all (all target flags false, range 0) → the same self-centred shape as Soulfire; it belongs on a caster-position rule, not this family |

**Everything else on the 32-list is in.** The alternate engine keys (base spell rows, the army Rod of the
Storm, the three Slicing Shards variants) were left out because they are `source_type = spell` / `army`,
i.e. out of wheel scope; the bound/active key of each ability is the one implemented.

**Counts:** +30 entries / +31 keys, +1 evaluator. **Total: 643 → 675 entries, 687 → 721 keys, 43 → 45
evaluators.**

---

## 3. Harness 106

* **Green: 3812 checks, 0 failures** (`h106_run4.txt`), against the live source AND the annotated copy
  (both files' decisions must agree; the annotated copy is log-free and `string.find`-free).
* New worlds (×2 files): **S1** non-commander in contact → fires + judged set logged; **S2** only a
  commander → silent + HOLDING verdict; **S3** caster not in melee → silent; **S4** commander + infantry →
  fires; **S5** nothing in contact + commander `current_target` → silent; **S6** nothing readable → plain
  in-melee fires; **F1** closer cavalry vs farther infantry → the infantry is chosen and the strike lands on
  ITS position vector; **F2** commander-only in melee → silent; **F3** 150 m vs the 140 m bound → silent;
  **F4** infantry unreadable on both reads → silent (fail-closed) + one-time notice; **F5** unit form on the
  enemy; **F6** ground form on the enemy's vector; **F7** `unit_class` fallback alone → fires.
* **Pins moved (documented, never edited in older harnesses):** table 643 → 675, key map 687 → 721,
  `range_real` 163 → 193, ground-key set 91 → 116, charge gate 129 → 154, cast gate 169 → 170.
  One harness-105 static pin (`A4a` bootstrap walk = 2 × 643) → 2 × 675; the last check of the 105 suite
  sits after `run_h106`, so its boundary reads 3701.
* **Red control** (H106_LIVE/H106_ANN → `docs/backups/round106/pre106_*.lua`): **136 failures**, wholly
  accounted for — 52 inherited harness-105 red deltas (unchanged), 61 grown-table pins, the new `0x`
  static block, and 15 new-world discriminators (S1a/S1c/S4a/S5b/S6a/F1a/F1b/F1c/F4b/F5a/F6a/F6b/F6c/F7a
  × files). The silence worlds (S2/S3/F2/F3) pass by design on the old build.

---

## 4. Build + install

* Builder: `mod_source/releases/20261018_bombardment_harness106/build_and_install106.py`
  (cloned from harness 105; contents gates updated to the new counts + new tokens).
* **5 ship files byte-identical to source** (`MATCHES SOURCE: True` for all five).
* **built md5 = installed md5 = `9108e7f685180cbb637ee8b9ef53cf24`**.
* `zz_probe_dist.pack` is left installed (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`).
* Installed pack re-grepped: `enemy_ground_melee_infantry` 36×, `melee_skip_commanders` 7×,
  `is_infantry()` 3×, the Arachneruption key 2×.

---

## 5. Workbook v7 + tracker

* `docs/WH3_abilities_master_v7_2026-10-17.xlsx` (+ `.ods`), built by `tools/make_xlsx_v7.py` from v6.
  **v1–v6 are byte-unchanged** (md5 diff before/after = empty).
* Abilities sheet: 1800 rows (unchanged), 33 rows moved to IMPLEMENTED on the new families, 3 rows marked
  `SKIPPED (round 106)`.
* Definitions: title v7, IMPLEMENTED 721 / NOT IMPLEMENTED 420 (of which 420 in-wheel), two new glossary
  rows (`melee_skip_commanders`, `enemy_ground_melee_infantry`), `TOTAL (all 45 evaluators)` = 675 / 721.
* Numbers: implemented 721, not implemented 420, included 1,141; carrier families active 546 / bound 69 /
  lord 6; trigger block re-counted from the mod (45 families, total 675 entries / 721 keys).
* Changelog: the v7 row with the md5.
* Tracker: 36 rows rewritten (30 bombardment + Soulfire ×2 appearances + Arachneruption + Thorsen's ×2
  + Warp Lightning Rod), the two new trigger rows in the glossary table, and the round-106 update
  paragraph at the top.

---

## 6. Retest instructions

1. **Soulfire**: field a Warrior Priest / Arch Lector (Soulfire is a bound ability on them) and charge it
   into a lord or hero alone. Expect **no cast** and one line
   `soulfire engagement set: 1 enemy unit(s) in contact … 'wh_main_…_cha_…' COMMANDER … -> HOLDING`.
   Then fight an infantry unit: it fires once and the log shows `-> FIRING (a non-commander is engaged)`.
2. **Arachneruption**: Lava Arachnarok Spider / Brood Mother — same rule, same log shape under the
   `arachneruption` marker.
3. **Bombardment**: field an item/weapon carrier of one of the 30 (e.g. Assault of Stone, Axe of Tor) or
   Kholek (Lord of the Storm) and let an INFANTRY enemy be fighting in range. Expect
   `ATTEMPT <marker> '<key>' … | reason: closest in-melee INFANTRY enemy within bound (targeting <enemy type>, distance=<n>m)`
   then either `enemy-ground cast` (24 keys) or `perform_special_ability(key, unit)` (6 keys).
   A cavalry-only or commander-only enemy in range must produce **no** attempt.
4. **The two skips**: Thorsen's Thunderstorm and Warp Lightning Rod are not in the pack by design —
   nothing to test.
5. Log: `...steamapps/common/Total War WARHAMMER III/zz_test_deadly_onslaught_log.txt`.
