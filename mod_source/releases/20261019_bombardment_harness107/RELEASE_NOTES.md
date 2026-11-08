# Round 107 — the remaining bombardment work: the count, the 11 air-drops, Call of Tor, and the Moondial fix

Date: 2026-10-18 · Harness 107 · Installed pack md5 `c44f38d415e3e1e2e7b0bfb886c41e8c`

Four user rulings, all implemented. The full evidence is in
`docs/WH3_bombardment_round2.md`; the round-106 research stays in
`docs/WH3_bombardment_research.md`.

---

## 1. The count is 55, not 57

131 `wh_type_bombardment` rows → 58 unit-side, visible, drawable → **minus 3 army-bar junctions
(Thorsen's Thunderstorm ×2, Bubonic Broadside) = 55**. The old 57 was 58 − Bubonic Broadside, i.e.
it still counted the two Thorsen army-bar keys. Reconciliation: **54 implemented** after this round,
**1 awaiting a ruling** (Warp Lightning Rod). The "25 remaining" was really **21 keys**: 34 of the 55
were already implemented (30 abilities = 31 keys, plus Soulfire's 2 keys and Arachneruption).

---

## 2. Call of Tor → `melee_skip_commanders`

`wh3_twa07_spell_bound_call_of_tor` (Oath-Brothers of Tor, War Bear Riders RoR), self-centred,
unlimited uses, 90 s recharge, 1 s wind-up. The user's rule, verbatim: *"Call of Tor looks very
similar to Soulfire, so let's do the same trigger as a Soulfire."* It rides the **existing**
evaluator unchanged: in melee, unless every engaged enemy is a Lord or Hero, with the judged
engagement set logged under the `call_of_tor` marker. `melee_skip_commanders`: **3 entries / 4 keys**.

**Counts:** +1 entry, +1 key.

---

## 3. The 11 "on top of" abilities — 12 entries / 19 keys on `air_drop_on_infantry`

Death from Above, Drop Rocks (4 keys), Drop Sphere of Tepok (2), Fire Bombs (2), Gyrobomber Bomb (2),
Gyrocopter Bomb anti-large, Sky-Junk Bomb, Skyhammer Bomb (2), Wake of Fire, Searing Torrent,
Nan-Gau Grenades, Undeath from Above (the Deck Droppers set).

* **Rule**: the closest **INFANTRY** enemy (`is_infantry()`, `unit_class()` fallback, **fail closed**)
  inside the ability's own **70% bound = 7 m** (floor(10 × 0.70), `FOURTH.AIR_DROP_BOUND_M`), with
  `unit_distance(caster)` as the **overlap proxy**. The blast radius is **not in the extracted
  tables**, so 7 m is a **constant** (the row's own 10 m cast range at the 70% rule), stated as such
  in every log line.
* **Per-row usage gates from the data**: `air_only` where the engine declares `grounded` (Fire Bombs,
  Gyrobomber/Gyrocopter, Skyhammer, Nan-Gau) or every carrier flies; `no_melee` where it declares
  `engaged_in_melee` (Death from Above, Drop Rocks, Drop Sphere, Wake of Fire, Searing Torrent,
  Undeath from Above). Unreadable reads **hold** (fail-closed).
* **Documented exceptions**: Drop Sphere of Tepok (one lord key is the ground Tiktaq'to variant, no
  `grounded` flag) and Searing Torrent (ground carrier; the user's field note — it recharges in melee
  — is why melee is never required, only excluded).
* **Cast**: self-centred `perform_special_ability(key, OWNER)`; none of the 19 keys is a ground key.
* **Pre-cast re-check**: caster alive / still flying / still out of melee, enemy alive / still
  infantry / still inside the bound — logged with the real distance; a lapse skips the cast.

**Counts:** +12 entries, +19 keys, +1 evaluator. **Total: 675 → 688 entries, 721 → 741 keys,
45 → 46 evaluators.**

---

## 4. Wraith Storm blocked Captain Roth's Moondial — the per-unit serialisation window

**The log:** at t ≈ 84 s the Moondial was issued **first**, Wraith Storm **0.25 s later** in the same
tick, on the same unit (Count Noctilus, ui 1001). Both controller calls were **ACCEPTED**. The engine
executed the second during the first's 3 s wind-up and **replaced** it — the Moondial's effect never
landed, but its use was spent: the next Moondial attempt is at t ≈ 203 s, **119 s later**, exactly its
120 s recharge.

**The data:** no shared lock. `shared_recharge_time = −1` on both, different recharge times
(90 s vs 120 s) and use counts (3 vs 2), no `parent_ability`, **no cooldown-group or exclusivity
column anywhere** in `unit_spec_abil.tsv`. The block is the engine's **one special ability in flight
per unit** rule (the Nurgling Tide order-replacement behaviour).

**The fix:** `cast_gate.unit_until / .unit_marker / .unit_logged` — after any successful cast, no
**different** ability may be issued on that unit for the cast's **wind-up + 2 s**, never less than
**2.5 s** (`FOURTH.SERIAL_MIN_HOLD_SECONDS`). The firing ability keeps its own pair gates; a
**same-ability repeat does not extend** the window (so a 0.1 s bomber cannot starve the unit); the
window is purged with a dropped unit, and the wait is logged once per episode.

**Harness proof** (`S1`, both files): Moondial fires on the enemy's ground; Wraith Storm is held with
the gate line; **20 polls (5 s) later it fires**. The red control reproduces the bug — both fire in
the same tick.

---

## 5. Harness 107

* **Green: 3939 checks, 0 failures** (`h107_run1.txt`, `h107_run2.txt`), live source AND annotated copy.
* New worlds: A1–A10 (the air-drop rule, its five silence cases, the two documented exceptions, the
  1 s wind-up), C1–C2 (Call of Tor fire / hold), S1–S3 (the serialisation sequence, the same-marker
  repeat, the per-unit scope).
* **Red control** (H107_LIVE/H107_ANN → `docs/backups/round107/pre107_*.lua`): **160 failures**, all
  accounted for — 114 grown-table pins, 36 world/assertion discriminators, 10 inherited RED CONTROL
  notices. The silence worlds pass on the old build by design.
* **Pins moved:** 675→688 entries, 721→741 keys, `range_real` 193→205, charge gate 154→161, cast gate
  170→172, `melee_skip_commanders` 2→3, the A4a bootstrap walk 1350→1376, and the cumulative suite
  boundaries (H70–H87, harness-101..106). Five worlds that pinned "two abilities on one unit fire in
  the same poll" now assert the sequence.

---

## 6. Build + install

* Builder: `mod_source/releases/20261019_bombardment_harness107/build_and_install107.py`.
* **5 ship files byte-identical to source** (`MATCHES SOURCE: True` for all five).
* **built md5 = installed md5 = `c44f38d415e3e1e2e7b0bfb886c41e8c`**.
* `zz_probe_dist.pack` is left installed (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`).

---

## 7. Workbook v8 + tracker

* `docs/WH3_abilities_master_v8_2026-10-17.xlsx` (+ `.ods`), built by `tools/make_xlsx_v8.py` from v7.
  **v1–v7 are byte-unchanged** (md5 diff before/after = empty).
* Abilities: 1800 rows; 20 rows moved to IMPLEMENTED (19 air-drop keys + Call of Tor); Warp Lightning
  Rod is the single `AWAITING RULING` row with its two candidate rules stated.
* Definitions: title v8, IMPLEMENTED 741, NOT IMPLEMENTED 1,058 (400 in the wheel), a new
  `air_drop_on_infantry` glossary row, `melee_skip_commanders` 3/4, `TOTAL (all 46 evaluators)`
  688/741, the gate-layer note extended with the per-unit window, and the **55-not-57 correction**.
* Numbers: implemented 741, not implemented 400, included 1,141; the trigger block re-counted from the
  mod (46 families, 688/741); a new **Bombardment set (CORRECTED to 55)** block
  (131 → 58 → 55 → 54 implemented + 1 awaiting ruling); the reconciliation paragraph updated.
* Changelog: the v8 row with the md5 and the harness numbers.
* Tracker: the round-107 update paragraph, the 19 air-drop rows + two Call of Tor rows rewritten, the
  `air_drop_on_infantry` glossary row, and the Warp Lightning Rod row set to awaiting ruling.

---

## 8. Retest instructions

1. **Air drops** — fly a carrier over an infantry unit: one cast with
   `… target: '…' is the closest INFANTRY unit under the caster (distance=…m bound=7m air_only=…)`
   and the re-check line. Over cavalry or landed: nothing.
2. **Searing Torrent** — recharge in melee, step out with infantry within 7 m: fires; while fighting:
   `melee check: the caster is fighting in melee -> HOLDING`.
3. **Call of Tor** — in melee vs infantry: fires with `call_of_tor engagement set: …`; vs a lone
   Lord/Hero: `-> HOLDING`.
4. **Moondial** — both abilities ready in one tick: one cast, the per-unit gate line naming the
   blocker, the second ~5 s later, and the Moondial's summon actually appears (its 120 s recharge is
   not wasted).
5. Log: `...steamapps/common/Total War WARHAMMER III/zz_test_deadly_onslaught_log.txt`.
