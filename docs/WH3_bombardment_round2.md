# WH3 bombardment — round 2 (harness 107): the count, the remaining rows, the air-drop family, the Moondial fix

Date: 2026-10-18 · round 107 · installed pack md5 `c44f38d415e3e1e2e7b0bfb886c41e8c`
Sources: the game's own tables under `%LOCALAPPDATA%\Temp\wh3\` (`unit_abilities.tsv`,
`unit_spec_abil.tsv`, `land_abil.tsv`, `uset_ability.tsv`, `army_spec.tsv`,
`special_ability_to_invalid_usage_flags_tables.tsv`, `land_units.loc.tsv`,
`db_unit_attributes_to_groups_junctions.tsv`), the shipped mod
(`mod_source\script\battle\mod\zz_test_deadly_onslaught.lua`) and the field log
(`.../Total War WARHAMMER III/zz_test_deadly_onslaught_log.txt`).

---

## 1. The count is 55, not 57 — and the "25 remaining" is really 21 rows

The derivation (recomputed from the tables, not copied):

| step | rows |
|---|---|
| every `wh_type_bombardment` row in `unit_abilities.tsv` | **131** |
| … unit-side (`source_type` active/bound/lord/character/unit/item/rune/weapon) with a real visible, drawable ability row | **58** |
| … of which are army-bar junctions in `army_spec.tsv` — Thorsen's Thunderstorm ×2 and Bubonic Broadside | **3** |
| **= the wheel bombardment set** | **55** |

**Where 57 came from:** 58 − Bubonic Broadside. That subtraction keeps the two Thorsen army-bar
keys, so it is only correct if the army-bar rule is applied to exactly one of the three army-bar
rows. Under the same rule the workbook applies everywhere else (army-bar = excluded) the number is
**55**.

**Why the difference is 21 rows, not 25.** The 30 shipped in round 106 are **31 keys**, and two more
keys of the 55 were already implemented on another trigger — Soulfire (2 keys) and Arachneruption
on `melee_skip_commanders`. So **34 of the 55 keys (32 abilities) were already in the table**, and
**55 − 34 = 21 keys remained**. The arithmetic "55 − 30 = 25" counts the 30 abilities as 30 keys
(they are 31) and ignores Soulfire/Arachneruption (3 keys), which is exactly the missing 4.

After round 107: **54 of the 55 are implemented; 1 awaits a ruling** (Warp Lightning Rod).

---

## 2. The 21 remaining rows

Flags are `target_friends / target_enemies / target_ground / target_self` from `unit_spec_abil.tsv`;
every row here has **all four false**, `effect_range 0`, `target_intercept_range 10` (Warp Lightning
Rod: 0) and `ai_usage = always_use_only_land` (Warp Lightning Rod: `aoe_bombardment`) — the engine
drops where the caster is, there is no enemy to click.

| # | Ability | Key | Granting unit (from `land_abil` / `uset_ability`) | Uses / recharge | Status after round 107 |
|---|---|---|---|---|---|
| 1 | Death from Above | `wh2_dlc09_unit_abilities_death_from_above` | The Flock of Djaf (Carrion), `wh2_dlc09_tmb_mon_carrion_ror` (flying) | 1 / 0.1 s | **implemented** `air_drop_on_infantry` |
| 2 | Drop Rocks | `wh2_main_unit_abilities_drop_rocks` | Terradon Riders ×6 (all flying); also the Deck Droppers set | 1 / 5 s | **implemented** |
| 3 | Drop Rocks (character) | `wh2_dlc12_unit_abilities_drop_rocks_character` | Skink Chief / Skink Priest (Beasts, Heavens) on Terradon | 1 / 5 s | **implemented** |
| 4 | Drop Rocks of Chotec | `wh2_dlc12_unit_abilities_drop_rocks_of_chotec` | Terradon Riders (Fireleech Bolas) | 1 / 5 s | **implemented** |
| 5 | Drop Rocks of Sundering | `wh2_dlc12_unit_abilities_drop_rocks_of_sundering` | Terradon Riders; Pahaux Sentinels (Terradon Riders RoR) | 1 / 5 s | **implemented** |
| 6 | Drop Sphere of Tepok | `wh2_dlc12_lord_abilities_drop_sphere_of_tepok` | Tiktaq'to (`_0` ground variant, `_1` flying) | 1 / 5 s | **implemented** (NOT air-gated: ground variant exists, no `grounded` flag) |
| 7 | Drop Sphere of Tepok (upgraded) | `wh2_dlc12_lord_abilities_drop_sphere_of_tepok_upgraded` | no junction in the extract (Tiktaq'to's upgraded lord row) | 2 / 5 s | **implemented** |
| 8 | Fire Bombs | `wh3_dlc25_unit_abilities_gyrobomber_fire_bomb` | Gyrobombers (set `dwf_gyrobombers_no_ror`) | 3 / 3 s | **implemented** |
| 9 | Fire Bombs (Thunderbarge) | `wh3_dlc25_unit_abilities_thunderbarge_fire_bomb` | Thunderbarge (no junction row in the extract; the airframe carries `always_flying`) | 3 / 3 s | **implemented** |
| 10 | Gyrobomber Bomb | `wh_main_unit_abilities_gyrobomber_bomb` | Gyrobombers; set `dwf_gyrobombers_no_ror` | 11 / 0.1 s | **implemented** |
| 11 | Gyrocopter Bomb | `wh_main_unit_abilities_gyrocopter_bomb` | Gyrocopters ×4 (all flying) | 2 / 0.1 s | **implemented** |
| 12 | Gyrocopter Bomb (anti-large) | `wh3_dlc25_unit_abilities_gyrocopter_bomb_anti_large` | Gyrocopters (Trollhammers – Grudge Settlers) | 2 / 0.1 s | **implemented** |
| 13 | Sky-Junk Bomb | `wh3_main_unit_abilities_sky_junk_bomb` | Sky-junk (`wh3_main_cth_veh_sky_junk_0`, flying airframe) | 3 / 30 s, wind-up 1 s | **implemented** |
| 14 | Skyhammer Bomb | `wh_dlc06_unit_abilities_skyhammer_bomb` | Skyhammer Squadron (Gyrobombers) | 5 / 0.1 s | **implemented** |
| 15 | Skyhammer Fire Bomb | `wh_dlc06_unit_abilities_skyhammer_fire_bomb` | Skyhammer set `dwf_skyhammer_gyrobomber_only` | 5 / 0.1 s | **implemented** |
| 16 | Wake of Fire | `wh2_main_unit_abilities_wake_of_fire` | Flamespyre Phoenix | 10 / 0.1 s | **implemented** |
| 17 | Searing Torrent | `wh3_twa07_unit_abilities_searing_torrent` | Knights of Immolation (Doom Knights of Tzeentch RoR), **ground** | 5 / 60 s | **implemented** (NOT air-gated; `no_melee`) |
| 18 | Nan-Gau Grenades | `wh3_dlc24_unit_abilities_nan_gau_grenades` | Empress Crowmen (Onyx Crowmen RoR), flying | 2 / 60 s | **implemented** |
| 19 | Undeath from Above | `wh3_dlc29_unit_abilities_undeath_from_above` | Deck Droppers set `wh2_dlc11_cst_deck_droppers` = Deck Droppers, (Bombers), (Handgunners), Salt Lord Scuttlers (all flying) | 1 / 0.1 s | **implemented** |
| 20 | Call of Tor | `wh3_twa07_spell_bound_call_of_tor` | Oath-Brothers of Tor (War Bear Riders RoR) | unlimited / 90 s, wind-up 1 s | **implemented** on `melee_skip_commanders` (item 2) |
| 21 | Warp Lightning Rod | `wh2_dlc16_unit_abilities_warp_lightning_rod` | no carrier junction in the battle tables (item/agent path the extract does not carry) | 3 / 60 s, wind-up 1 s | **AWAITING THE USER'S RULING** |

**Warp Lightning Rod — what is proposed and why it is not decidable yet.** Its row has no target
flags at all and `target_intercept_range 0`, `effect_range 0`, `ai_usage aoe_bombardment` — a
self-centred nuke. Two candidate rules: (a) fire while **N enemy units** are inside a stated radius
of the caster — a **count rule** that does not exist anywhere in the mod, and the user has not set
the N or the radius; (b) leave it manual. It cannot ride `air_drop_on_infantry` (that needs a flying
caster and a 10 m row range). No proxy was invented.

---

## 3. The 11 "on top of" abilities — 12 entries / 19 keys on `air_drop_on_infantry`

### What the data says (per key)

Every one of the 19 rows: all four target flags **false**, `effect_range 0`,
`target_intercept_range 10`, `ai_usage always_use_only_land`, `bombardment` = itself, aoe
`wh_abilities_bomb_drop` or `wh_abilities_bomb_small_drop`.

The **engine's own usage restrictions** decide which gate each entry carries:

| engine invalid-usage flag | keys | what the evaluator does |
|---|---|---|
| `grounded` | Fire Bombs ×2, Gyrobomber Bomb ×2, Gyrocopter anti-large, Skyhammer ×2, Nan-Gau Grenades | `air_only = true` — `is_currently_flying()` must be exactly true |
| `engaged_in_melee` | Death from Above, Drop Rocks ×4, Drop Sphere ×2, Wake of Fire, Searing Torrent, Undeath from Above | `no_melee = true` — `is_in_melee()` must be false |
| none | Sky-Junk Bomb | neither gate |
| no `grounded`, ground carrier | Drop Sphere (one lord key is the ground Tiktaq'to variant), Searing Torrent (Doom Knights) | `air_only = false`, documented on the entry |

### The overlap proxy and the constants — stated plainly

The battle script API has **no per-unit footprint and no blast radius**, and the aoe key
(`wh_abilities_bomb_drop` / `wh_abilities_bomb_small_drop`) lives in an aoe table this extraction
does **not** carry. The one real read is `unit:unit_distance(caster)` — **edge-to-edge metres**
(`battle_unit.lua:160`). So "under the caster" is proxied by that gap being inside the ability's own
**70% bound**.

**The constant for every one of the 19 keys is 7 m** (floor(10 × 0.70), `FOURTH.AIR_DROP_BOUND_M`,
mapped through `FOURTH.ENEMY_CAST_R10 = 7`). It is the row's own 10 m `target_intercept_range` at
the standing 70% rule — **not** the bomb's blast radius. Every log line prints it as a bound.

### The rule and the cast

* enemy **alive**, **`is_infantry()`** (fallback `unit_class()` exact-match `inf_mel`/`inf_mis`/`inf_spr`,
  **fail closed**), gap ≤ 7 m — the **closest** wins;
* caster **airborne** where `air_only`, **out of melee** where `no_melee`; an unreadable read on
  either **holds** (fail-closed);
* cast **self-centred**: `perform_special_ability(key, OWNER)` (none of the 19 keys is in
  `enemy_ground_keys`, and the build asserts that);
* **pre-cast re-check**: caster alive, still flying / still out of melee, enemy alive, still infantry,
  still inside the bound — logged with the real distance, and a lapse **skips the cast**.

### Per-ability detail

| Ability | Entry | Keys | air_only | no_melee | bound |
|---|---|---|---|---|---|
| Death from Above | `death_from_above` | 1 | yes | yes | 7 m |
| Drop Rocks | `drop_rocks` | 4 | yes | yes | 7 m |
| Drop Sphere of Tepok | `drop_sphere_of_tepok` | 2 | **no** (ground lord variant, no `grounded`) | yes | 7 m |
| Fire Bombs | `fire_bombs` | 2 | yes (`grounded`) | no | 7 m |
| Gyrobomber Bomb | `gyrobomber_bomb` | 2 | yes (`grounded`) | no | 7 m |
| Gyrocopter Bomb (anti-large) | `gyrocopter_bomb_anti_large` | 1 | yes (`grounded`) | no | 7 m |
| Sky-Junk Bomb | `sky_junk_bomb` | 1 | yes (flying airframe) | no | 7 m |
| Skyhammer Bomb | `skyhammer_bomb` | 2 | yes (`grounded`) | no | 7 m |
| Wake of Fire | `wake_of_fire` | 1 | yes | yes | 7 m |
| Searing Torrent | `searing_torrent` | 1 | **no** (ground carrier) | yes | 7 m |
| Nan-Gau Grenades | `nan_gau_grenades` | 1 | yes (`grounded`) | no | 7 m |
| Undeath from Above | `undeath_from_above` | 1 | yes | yes | 7 m |

**Searing Torrent, the user's field note.** The user checked it and reported it behaves like the
others, with the only difference that it recharges in melee. The row's `engaged_in_melee` invalid
flag means the engine refuses the cast **while fighting**, so the evaluator never requires melee —
it only **excludes** it. The carrier is a ground unit, so no flight requirement.

**Charge-gate rows added** (multi-use pools slower than the 2 s guard): Call of Tor 90,
Drop Sphere upgraded 5, Fire Bombs 3, Thunderbarge Fire Bombs 3, Nan-Gau 60, Searing Torrent 60,
Sky-Junk 30. The 0.1 s-recharge bombers are deliberately **not** listed — they refill faster than
the guard, so their pool can never drain.

**Wind-up rows added**: Call of Tor 1 s, Sky-Junk Bomb 1 s.

---

## 4. Wraith Storm blocking Captain Roth's Moondial

### What the log shows (the only relevant episode)

The caster is Count Noctilus (`wh2_dlc11_cst_inf_count_noctilus_0`, ui id 1001); both abilities are
on the same unit. In one tick, at t ≈ 84 s:

```
873989  captain_roths_moondial target: 'wh_main_vmp_inf_grave_guard_0' ... distance=99.1m bound=105m
873991  ATTEMPT captain_roths_moondial ... | reason: closest fighting (in-melee) enemy within bound ... | armed=ON
873995  perform_special_ability(key, unit) : ACCEPTED
873998  in-flight gate captain_roths_moondial: the cast needs 3s wind-up - the next attempt on this unit waits 5s
873999  wraith_storm target: 'wh_main_vmp_inf_grave_guard_0' ... distance=99.1m bound=140m
874001  ATTEMPT wraith_storm ... | reason: closest in-melee INFANTRY enemy within bound ... | armed=ON
874004  perform_special_ability(key, unit) : ACCEPTED
874007  in-flight gate wraith_storm: the cast needs 3s wind-up - the next attempt on this unit waits 5s
874012  command: 'Special Ability' issued for 'wh2_dlc11_item_abilities_captain_roths_moondial'
874013  command: 'Special Ability' issued for 'wh2_dlc11_lord_abilities_wraith_storm'
874019  INVENTORY button_order12: ... state='active' key='wh2_dlc11_item_abilities_captain_roths_moondial'
```

**Order and answer:** the **Moondial was issued first**, Wraith Storm **0.25 s later**, in the same
tick, on the same unit. Both controller calls were **ACCEPTED** — the controller does not refuse a
second order. The engine then executed them in order; the second order **replaced the first during
its 3 s wind-up**, so the Moondial's effect never landed while its **use was already spent**. The
proof is the next Moondial attempt: `879470` at t ≈ 203 s — **119 s later**, exactly its own 120 s
`recharge_time`. The Wraith Storm worked because it was the second, surviving order.

### What the data says: no shared lock exists

| field | Wraith Storm | Moondial |
|---|---|---|
| `shared_recharge_time` | −1 (per-use) | −1 (per-use) |
| `recharge_time` | 90 s | 120 s |
| `num_uses` | 3 | 2 |
| `wind_up_time` | 3 s | 3 s |
| `parent_ability` | empty | empty |
| exclusivity / cooldown-group column | **none in `unit_spec_abil.tsv`** | same |
| grant path | lord ability | item ability |

Both are `source_type active` on the same caster. There is **no shared cooldown, no charge group and
no exclusivity field** anywhere in the extracted tables — so nothing in the data blocks the Moondial;
the block is the engine's **one-special-ability-in-flight-per-unit** rule (the same
order-replacement behaviour established for Nurgling Tide).

### The fix

**A per-caster serialisation window** (`cast_gate.unit_until / .unit_marker / .unit_logged`):

* armed by **every successful cast** of a unit, for **that ability's wind-up + 2 s**, never less than
  **2.5 s** (`FOURTH.SERIAL_MIN_HOLD_SECONDS`);
* while it is open, a **different** ability on the same unit is **not issued** — it waits, silently,
  with one log line per episode:
  `per-unit cast gate wraith_storm: unit 11731 is still resolving 'captain_roths_moondial' (5.0s left) - waiting its turn (a second special ability would replace it)`;
* the ability that fired keeps its own per-pair gates (`in-flight` = wind-up + 2 s, `charge` = its
  recharge) — so a 0.1 s bomber is **not** throttled by the unit window;
* a repeat of the **same** ability does **not** extend the window (otherwise a fast-repeating ability
  starves every other ability on the unit — this was caught by the harness and is pinned);
* the window is purged when the unit is dropped.

### The harness proof

`S1` (both files): a unit owning Moondial + Wraith Storm with an infantry enemy at 3 m, both armed.
Green build: **Moondial fires on the enemy's ground at tick 2; Wraith Storm is held (0 unit fires);
at tick 22 — 20 polls = 5 s later — Wraith Storm fires**. Red control (pre-107 snapshot): the same
world fires **both** in the same tick (`ground=1 unit=1`) — the bug reproduced, and the fix
discriminated.

`S2`: the same ability repeats after its own 2 s guard, exactly 8 polls apart — the unit window adds
nothing to a same-marker repeat. `S3`: two casters fire in the same poll — the window is per unit,
not global.

---

## 5. Harness 107 — numbers and pins

* **Green: 3939 checks, 0 failures** (`h107_run1.txt`/`h107_run2.txt`), against the live source AND
  the annotated copy.
* New worlds (×2 files): **A1** infantry under a flying caster → fires, cast on the OWNER;
  **A2** non-infantry → silent; **A3** not flying → silent + `airborne check ... HOLDING`;
  **A4** flight read unreadable → silent (fail-closed); **A5** 8 m > 7 m bound → silent;
  **A6** both infantry reads fail → silent + one-time notice; **A7** `engaged_in_melee` row with the
  caster in melee → silent; **A8** Drop Sphere from a ground caster → fires; **A9** Searing Torrent
  out of melee → fires; **A10** Sky-Junk's 1 s wind-up arms a 3 s hold; **C1** Call of Tor fires on a
  non-commander; **C2** Call of Tor holds on a commander alone; **S1/S2/S3** the serialisation proof.
* **Pins moved** (documented, never edited in the older harness files): table 675 → 688, keys
  721 → 741, `range_real` 193 → 205, charge gate 154 → 161, cast gate 170 → 172,
  `melee_skip_commanders` 2 → 3, the A4a bootstrap walk 2 × 675 → 2 × 688 (1350 → 1376), and the
  cumulative suite boundaries (H70 882 → 886, H71..H78 +4/+3, H79..H87 +3/+4,
  harness-101..106 boundaries +4). Five worlds that pinned "two abilities on one unit fire in the
  same poll" (B3, N3, C6) now assert the **sequence** the fix creates.
* **Red control** (H107_LIVE/H107_ANN → `docs/backups/round107/pre107_*.lua`): **160 failures**,
  wholly accounted for — **114 grown-table pins** (the snapshot is the 675-entry build),
  **36 world discriminators** (A1/A8/A9/A10/C1/S1/S2/S3 fire checks and the S1/S2/S3 assertions), and
  **10 inherited RED CONTROL notices** from earlier rounds whose own snapshots are older. The
  pure-silence worlds (A2–A7, C2) pass on the old build by design.

---

## 6. Retest instructions

1. **Air drops.** Field a flyer that carries one of the 11 — Gyrobombers (Gyrobomber Bomb / Fire
   Bombs), Terradon Riders (Drop Rocks), Flamespyre Phoenix (Wake of Fire), Sky-junk, Empress Crowmen
   (Nan-Gau), Deck Droppers (Undeath from Above) — and fly it over an **infantry** unit. Expect
   `death_from_above target: '…inf…' is the closest INFANTRY unit under the caster (distance=…m bound=7m air_only=true)`
   then `pre-cast re-check: still over an INFANTRY enemy (...) - firing`. Over cavalry: nothing.
   Landed: nothing (`airborne check ... -> HOLDING`).
2. **Searing Torrent.** Knights of Immolation: charge into melee to recharge, walk out of melee with
   infantry within 7 m → fires; while still fighting → nothing, with `melee check: the caster is
   fighting in melee -> HOLDING`.
3. **Call of Tor.** Oath-Brothers of Tor in melee vs infantry → fires with
   `call_of_tor engagement set: …`. Against a lone Lord/Hero → nothing, `-> HOLDING`.
4. **The Moondial fix.** Captain Noctilus with 2 Wraith Storms and Captain Roth's Moondial. Once
   both are ready in the same tick, expect **one** cast, then
   `per-unit cast gate wraith_storm: ... still resolving 'captain_roths_moondial' (5.0s left)`,
   and the second ability to fire ~5 s later. The Moondial must **land** (a summon appears) and its
   120 s recharge must not be spent on a cancelled cast.
5. Log: `...steamapps/common/Total War WARHAMMER III/zz_test_deadly_onslaught_log.txt`.
