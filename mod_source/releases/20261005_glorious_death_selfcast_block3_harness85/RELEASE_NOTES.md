# Release 2026-10-05b — Glorious Death SELF-CAST fix + BLOCK 3 (38 entries) — harness85

Two jobs: fix the Glorious Death field-test defect (the caster was ordered to walk
to the Slayer ally), and implement block 3's approved abilities.

## Shipped source
`script/battle/mod/zz_test_deadly_onslaught.lua`  sha256 `6e06baa6a1c4cfddbbc4c11c39564194…` (262674 bytes)
`WH3_auto_ability_annotated.lua` (Desktop reading copy)  sha256 `f5e4383516458675a5da13f2d29622d5…` (174935 bytes)
Pack installed to `.../Total War WARHAMMER III/data/zz_test_deadly_onslaught.pack`
installed md5 `204d8cb72fa98f117b65b79d49663202` (dist == installed, IDENTICAL True);
per-file sha256 gate: all 5 shipped files MATCHES SOURCE True.
Independent PFH5 re-read (`verify_cleaned_independent.py`): RESULT PASS — 5/5 files
byte-identical, dist == installed, no probe paths.

## JOB 1 — GLORIOUS DEATH: the CAST TARGET is now ALWAYS the OWNER
* The **TRIGGER is unchanged** from harness 84 (the Slayer-only candidate set): (a) an
  in-melee **Slayer ally** (other than self) arms it; else (b) the **owner itself** arms
  it only when the owner is a Slayer and in melee; else silent. A non-Slayer ally is never
  offered. Who is a Slayer is still `FOURTH.slayer_keys` (the derived land_units type-key
  list, exact whole-key equality, no `string.find`).
* **The fix:** every firing arm now writes the **OWNER** into `FOURTH.cast_target`
  (`FOURTH.cast_target = unit`, x2); the old `FOURTH.cast_target = best_unit` (the ally)
  is **GONE**. The dispatch already passes `target or unit`, so
  `perform_special_ability(key, owner)` is issued and the caster is never ordered to move
  to the ally. The reason strings are reworded:
  * `slayer in melee (self-cast)`  (a Slayer ally armed it — cast still on self)
  * `self in melee (self-cast)`    (the owner's own Slayer-in-melee self arm)
* `FOURTH.cast_target` is **kept** as a field: the dispatch still clears it before each
  evaluate and passes it to the cast, so a self-targeted ability can never inherit a
  stale unit. No other ability writes it.

## JOB 2 — BLOCK 3: 38 approved entries
* **35 in-melee-self** entries ride the **EXISTING** shared `melee_unwavering` evaluator
  (`FOURTH.evaluate_in_melee_self`) — no new evaluator:
  legbiter, hellfire_sword, helm_of_discord, helm_of_many_eyes, heroic_killing_blow_2 /
  _dlc07 / _main, hydra_blade, inevitable_horror, karaghul, killing_blow_1, killing_blow,
  liarsbane, lightning_reflexes, locus_of_beguilement / _grace / _wrath, lucky_banner,
  mace_of_ulumak, mananns_luck, master_of_the_skies, mimic_waaagh, mimic_grom_waaagh,
  monstrous_strength, mortal_blow, mortal_blow_upgraded, mumbo_jumbo_chant,
  strike_of_nagash, nurgles_favoured_son, opal_amulet, oracle_of_eternity,
  pendant_of_slaanesh, plaguefathers_oration, primal_roar, puncture.
* **3 charge-or-melee** entries ride the **EXISTING** `charge_or_melee` evaluator (the one
  Fangspike uses): heart_piercing, horn_of_the_first_beast, morglor_the_mangler.
* Table rows only — **NO new chunk locals** (the file sits at Lua's 200-local ceiling);
  the table grew 64 -> **102 entries** and the key set 70 -> **108 keys**.
* **Count discrepancy (reported, not silently resolved):** the task text said "34
  abilities (31 in-melee-self + 3 charge-or-melee)" but its **explicit key list holds 35
  in-melee-self keys** (35 + 3 = **38**). Every one of the 35 is `approved (in-melee self)`
  in the tracker, so all 38 listed keys were implemented.
* Healing Elixirs, Harvestman's Scythe, In the Name of War, Manus of Ursun, Locus of
  Contagion and Mad Cap Mushrooms were **not** implemented (not approved).

## Harness 85
Built from harness84 (env pair now `H85_LIVE` / `H85_ANN`). Adapted in the harness-84-era
suite (same check counts, so the harness-84 suite still totals 2039): the h83 G1/G2 and h84
W1/W2/W4 Glorious-Death worlds rewritten for self-cast; the h83 0y and h84 0z reason tokens
reworded; the count pins A4 `128->204` / `64->102`, B4 `64->102`, H68 `64->102` and key map
`70->108`, C6c `64->102`; the h82/h83/h84 red aggregates re-based. Re-check counts unchanged.

New section 0h (block-3 + self-cast tokens in both files) and five worlds: **X1** (the
cast target IS the owner, the Slayer ally never passed), **X2** (the Slayer-in-melee trigger
with self-cast — the exact field defect: the owner not in melee, the ally in melee), **X3**
(self-in-melee self-cast), **S3** (all 35 new in-melee-self entries fire on in-melee alone),
**F3** (the 3 charge-or-melee entries fire on both arms).

GREEN: **checks: 2106, failures: 0** (harness-84 suite boundary `checks == 2038` holds;
+68 new checks).
RED (pre-edit snapshot, this dir's `pre85_snapshot/` = the shipped harness-84 build):
**failures: 67**, every one a designed delta — section-0h tokens (14), the 0y/0z reason
tokens (3), the adapted count pins A4 (4) + B4 (2) + H68 (5) + C6c (2) and their A/B
aggregates (2), the rewritten G1/G2 (5), W1/W2/W4 (8), and the X1/X2/X3/S3/F3 worlds (22).
No unrelated check fails.

## Tracker
`C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md` — exactly two changes: (i) new standing
**rule 8** ("mutual exclusivity is an automatic rejection … marked `rejected (auto: mutual
exclusivity)`"); (ii) the 10 existing mutual-exclusivity rejects re-marked
`rejected (auto: mutual exclusivity)`. Nothing else was touched (block-3 statuses and the
Glorious Death row were left as-is, per "mark nothing else").
