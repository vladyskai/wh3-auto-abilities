# Round 108 — the 1 m air-drop test bound and Warp Lightning Rod

Date: 2026-10-18 · Harness 108 · Installed pack md5 `4a1cedca34d0c4936eab4e9d5bd12f1a`

Two user rulings, both implemented and shipping.

---

## 1. "Drop Bombs" → the air-drop overlap bound is now **1 m** (was 7 m)

**What "Drop Bombs" resolved to.** No ability in the game's localisation is named *Drop Bombs*
(`unit_abilities.loc.tsv` carries no such string; the family's own onscreen names are Death from Above,
Drop Rocks, Drop Sphere of Tepok, Fire Bombs, Gyrobomber Bomb, Gyrocopter Bomb, Sky-Junk Bomb,
Skyhammer Bomb, Wake of Fire, Searing Torrent, Nan-Gau Grenades, Undeath from Above). The field log
decided it: in the **2026-10-18 session** the only air-drop ability the user actually cast is
**Drop Rocks — `wh2_main_unit_abilities_drop_rocks`, Terradon Riders** — and it was accepted at
**6.9 m and again at 6.0 m** edge-to-edge under the old 7 m proxy (`drop_rocks target: … distance=6.9m
bound=7m`, `ATTEMPT drop_rocks … distance=6.9m, bound=7m`, `ACCEPTED`). That is precisely "released them
too soon": the ordnance left the flyer while it was still short of being over the target. So the row the
user tested is **Drop Rocks**; the change below is applied to the **whole `air_drop_on_infantry` family**
because the bound is **one shared constant**, not a per-row field — and the release notes say so.

**The change.**

* `FOURTH.AIR_DROP_BOUND_M = 7` → **`= 1`**, with the comment stating in full that 1 m is a
  **USER-CHOSEN TEST VALUE**, much tighter than the standing 70% rule (which says 7 m).
* The family **bypasses the 70% map**: the entries carry the row's real `target_intercept_range = 10`,
  which `FOURTH.ENEMY_CAST[10]` would turn back into 7 m, so the load loop now does
  `if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then ability.range_m = FOURTH.AIR_DROP_BOUND_M end`.
  No entry, key list or other constant changed — `range_real = 10` stays as the row's documented value.
* The comment (and this note) records the **edge-to-edge** caveat: `battle_unit:unit_distance()` is
  bounding-box edge-to-edge (`battle_unit.lua:160`), so a unit **directly under** the caster should read
  **near 0-5 m, not 0 m** — two overlapping boxes still report the gap between their nearest edges, and a
  wide flyer over a wide infantry block can legitimately read a few metres while squarely on top.
* **If it never fires at 1 m the test is too tight, not the code**: the bound is **one constant**
  (`FOURTH.AIR_DROP_BOUND_M`), so raising it to 2, 3 or 5 m is a one-line change and nothing else moves.

**Counts:** behaviour only — the table stays **689 entries / 742 keys**, `air_drop_on_infantry` stays
**12 entries / 19 keys**.

---

## 2. Warp Lightning Rod → `melee_skip_commanders` (Soulfire's trigger)

**The key.** Exactly **one**: **`wh2_dlc16_unit_abilities_warp_lightning_rod`** (no upgraded twin exists;
the name in the brief, `wh3_main_item_abilities_warp_lightning_rod`, does not exist — the real row is a
`wh2_dlc16` *unit* ability, which is itself a hint that nothing carries it by default).

**The row (from `unit_spec_abil.tsv`):** `affect_self = true`, all four target flags false,
`target_intercept_range = 0`, `effect_range = 0`, `ai_usage = aoe_bombardment`, `active_time = 5 s`,
`num_uses = 3`, `recharge_time = 60 s`, **`wind_up_time = 1 s`**, `bombardment =
wh2_main_spell_ruin_warp_lightning`; its only invalid-usage flag is **`climbing`**. Tooltip: *"Dire
greenish-black lightning strikes at the Skaven's crude Warpstone implant."* — a self-centred bombardment,
the same shape as Soulfire, so it rides the **existing** evaluator unchanged:

* fires when the caster is **in melee**, unless **every** engaged enemy is a **Lord or Hero**
  (engagement set = alive + `is_in_melee()` + edge-to-edge `unit_distance` <= 12 m
  `FOURTH.ENGAGE_CONTACT_M`, each member classified by the 1,409-key commander set, fail-closed);
* the judged engagement set is **logged under its own `warp_lightning_rod` marker**, deduped by note text;
* the caster and the engagement set are **re-read immediately before the cast**;
* cast on the **OWNER** (`perform_special_ability(key, unit)`), charge gate **60 s**, in-flight gate **1 s**.

**Why there was no carrier junction (now recorded in the data docs).** The extraction contains **no
land_units / uset_ability row** for this key — only the ability row, the `climbing` flag row, its UI
effects and its loc line. It is **not a default unit ability**: in campaign it is granted by the **Clan
Moulder Lobotomy mutation** (the user's own explanation, in their words: *"Warp Lightning Rod seems to be an
effect no unit has by default, but during the campaign some units can aquire it via mutation (Clan Moulder
Lobotomy augmentation). Let's treat it the same as Soulfire."*). The entry still works because the mod arms
per unit on whatever key that unit actually owns at battle time.

**Counts:** +1 entry, +1 key. `melee_skip_commanders`: **3 entries / 4 keys → 4 entries / 5 keys**.
**Total: 688 → 689 entries, 741 → 742 keys, 46 evaluators (unchanged).** The wheel bombardment set is now
**complete: 55 implemented, 0 awaiting a ruling**.

---

## 3. Harness 108

* **Green: 4006 checks, 0 failures**, run twice, byte-identical output (`h108_run1.txt` = `h108_run2.txt`),
  against the **live source AND the annotated copy**.
* New worlds:
  * **B1** an enemy **0.4 m** under a flying caster **fires** at the 1 m bound, cast on the owner, log
    `distance=0.4m bound=1m`;
  * **B2** an enemy **3.0 m** away does **not** fire (under the old 7 m proxy it did) and nothing is attempted;
  * **B3** an enemy at **exactly 1.0 m** fires (the bound is inclusive, `<=`);
  * **W1** Warp Lightning Rod **fires vs a non-commander** in contact, cast on the owner, engagement set
    logged under `warp_lightning_rod`;
  * **W2** WLR **holds vs a lone Lord/Hero**, with the `-> HOLDING (every engaged enemy is a Lord or Hero)`
    verdict logged and no attempt.
* **Red control** (`H108_LIVE/H108_ANN` → `docs/backups/round108/pre108_*.lua`): **41 failures**, all
  accounted for — 24 × 0z (12 new-token checks per file), 4 × 0y (four-entries + the 1 m bypass), 2 × A5a
  (the old 7 m bound fires at 3 m), 1 × B1c, 2 × B2a + 1 × B2b, 1 × B3b, and 5 WLR checks (W1a/b/c live,
  W1a/b ann — the pre-108 build has no WLR entry).
* **Pins moved (documented):** entries **688→689**, keys **741→742**, the key→marker map **741→742**, the
  cast-gate table **172→173** wind-up keys, the charge-gate block **161→162** rows, the A4a bootstrap walk
  **1376→1378**, `melee_skip_commanders` **3→4** entries in both the h106 and h107 sections, and the
  air-drop worlds re-distanced for the 1 m bound (A1 2.0→**0.4**, A2/A6 2.0→**0.5** so their reads still
  execute, A5 8.0→**3.0**, A8/A9 3.0→**0.5**, A10/S2/S3 2.0→**0.5**).

---

## 4. Build + install

* Builder: `mod_source/releases/20261020_airdrops_wlr_harness108/build_and_install108.py`.
* **5 ship files byte-identical to source** (`MATCHES SOURCE: True` for all five).
* **built md5 = installed md5 = `4a1cedca34d0c4936eab4e9d5bd12f1a`**.
* `zz_probe_dist.pack` left installed (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`).

---

## 5. Workbook v9 + tracker

* `docs/WH3_abilities_master_v9_2026-10-17.xlsx` (+ `.ods`), built by `tools/make_xlsx_v9.py` from v8.
  **v1-v8 are byte-unchanged** (`md5sum -c` over all eight: all OK).
* **Abilities:** the 12 air-drop rows now state the **1 m user-chosen bound** (with the Drop Rocks field
  evidence and the edge-to-edge 0-5 m caveat); **Warp Lightning Rod** moved to `IMPLEMENTED` on
  `melee_skip_commanders` with the mutation note — **0 rows awaiting ruling**.
* **Definitions:** title v9, IMPLEMENTED **742**, NOT IMPLEMENTED **1,057 keys (399 in the wheel)**,
  `melee_skip_commanders` **4 / 5**, `air_drop_on_infantry` **12 / 19** with the 1 m text,
  `TOTAL (all 46 evaluators)` **689 / 742**, the bombardment note now "all 55 implemented", gates heading
  "rounds 103-108".
* **Numbers:** implemented **742**, not implemented **399**, included **1,141**; the trigger block
  re-counted from the mod (46 families, 689/742); the bombardment block now reads
  **131 → 58 → 55 → 55 implemented + 0 awaiting**; the reconciliation paragraph explains that round 108
  moved **one key** (WLR) and that the air-drop change is behaviour, not count.
* **Changelog:** the v9 row with the md5 and the harness numbers.
* **Tracker:** a round-108 update paragraph, the **Warp Lightning Rod** row rewritten to implemented (with
  the Lobotomy grant), all **19 air-drop key rows** re-stated at the 1 m bound, and both glossary rows
  updated.

---

## 6. Retest instructions

1. **Air drop (the fix under test)** — fly a carrier (e.g. Terradon Riders, Drop Rocks) **directly over**
   an infantry unit and arm the badge. Expect the target line only when the edge-to-edge gap is **<= 1 m**:
   `… target: '<unit>' is the closest INFANTRY unit under the caster (distance=0.4m bound=1m air_only=true)`
   followed by `pre-cast re-check: still over an INFANTRY enemy … firing`. While the flyer is 3-6 m away:
   **nothing** (that is the change — the old 7 m bound fired there).
   If it never fires even when the flyer is clearly on top, the test is too tight: raise
   `FOURTH.AIR_DROP_BOUND_M` (2 / 3 / 5 m) — one constant, nothing else.
2. **Warp Lightning Rod** — in campaign, give a unit the **Clan Moulder Lobotomy** mutation, then in battle
   arm the badge and fight infantry: `warp_lightning_rod engagement set: 1 enemy unit(s) in contact (<= 12m):
   '…' non-commander 3.0m -> FIRING (a non-commander is engaged)`. Against a lone Lord/Hero:
   `-> HOLDING (every engaged enemy is a Lord or Hero)`.
3. **Soulfire / Call of Tor / Arachneruption** — unchanged; the engagement-set line and the HOLDING verdict
   behave exactly as in round 107.
4. Log: `...steamapps/common/Total War WARHAMMER III/zz_test_deadly_onslaught_log.txt`.
