# Round 165: the night audit (sign-off round)

Date: 2026-11-17 (overnight). Harness: `harness164.lua`. Release folder: `mod_source\releases\20261117_night_audit_harness164\`.
The full audit (scores, open questions, feature ideas) is `docs\WH3_overnight_audit_2026-11-17.md`. This document covers
what changed in the mod.

## 1. The request (user, 2026-11-16)

- **Point 1:** check that each ability's card note matches how it fires when armed, and fix it if not. The text must be
  necessary and sufficient, with no fillers.
- **Point 2:** rank each trigger, and say how sure the ranking is.
- **Point 3:** check every game restriction ("if it only applies to flying units, and we do not check for that, we
  should add the check"), and suggest features.

## 2. What changed (what you will see in battle)

### The card: every M/A badge now says when its ability fires

- **The finding:** the per-family sentence written in round 93 (`FOURTH.TRIGGER_TIP` -> `ability.tip`) was never shown.
  Nothing reads `ability.tip`. The only text on the card is the generic twui line ("Automatic: click the M/A badge ...").
  Several of the old sentences also hid conditions: "not wavering", the 12-60 m / 4 s charge window, "in melee" inside
  "an ally is wavering", and the 70% radii.
- **The fix:** `FOURTH.CARD_TIP` holds one corrected sentence per family (95). `FOURTH.compose_card` fills in each
  ability's own numbers at load:
  - its 70% range and aura bounds;
  - the blast clearance (radius + 10 m);
  - the wave clearance at the path's start and end;
  - the charge window;
  - the execute line;
  - the strike count.

  It then appends the target-class clause, the game's caster rules and, for the ally pickers, the game's target rules.
- **Where it shows:** the card is the hover tooltip of the ability's own M/A badge. It uses `SetTooltipText`, the same
  call the ALL button uses, which you confirmed works in battle.
- **Not field-checked:** whether this badge template shows a tooltip. Please hover one M/A badge next battle. If nothing
  appears, the next step is a different template.
- **Example:** "Deadly Onslaught on A: fires when this unit runs at the enemy it is attacking, 12 to 60 m away and at
  most 4 s from contact, or when it is in melee."
- **All 946 cards:** the Cards sheet of workbook v49, and `cards_round165.tsv` in the release folder.

### The game's caster rules (point 3)

- **The source:** NEW GENERATED `FOURTH.USAGE_TEXT` (`tools\gen_usage_keys.py`, from
  `special_ability_to_invalid_usage_flags`; 60 of our keys).
- **The gate:** a new check, first in `FOURTH.try_pair`, skips an attempt the game would refuse. It logs once per change
  of state.
- **States checked:** in melee, on the ground, flying, moving, wavering, below or above a health line, and not a large
  unit.
- **New in effect for 10 abilities** (the other 50 keys were already honoured by their families):

| Ability | The game's rule | Now |
|---|---|---|
| Entice | health_below_50% | not below 50% health |
| Favoured by the Matriarch, the Loons of Eight Peaks, Spinning Loons | health_below_25% | not below 25% health |
| Curse of Khsar, Curse of Djaf | health_above_50% | only at or below 50% health |
| Daemon Flask of Ashak, Feaster of Souls | flying_currently | not while the caster flies |
| Eye of the Storm | unit_is_not_large | only when the caster is a large unit (the Storm Dragon form) |
| Stay Here, I'll Get Help! | engaged_in_melee | not while the caster is in melee |

**Not modelled (no battle read):**
- siege states (climbing, platform, manning);
- `morale_is_broken_or_lower` (the routing gate covers it, an assumption);
- `hp_replenish_cap_reached`;
- `enemies_in_intercept_range` (Bugman's XXXXXX);
- `cannot_perform_missile_attack`;
- `ground_unit` and `flying_unit`: Eye of the Storm, Wrath of the Storm. The two readings, a unit type that can fly versus
  flying now, give opposite results for a dragon fighting on the ground, so I did not guess.

### The game's ally target rules (point 3)

- **The source:** NEW GENERATED `FOURTH.ATARGET_TEXT` (`special_ability_to_invalid_target_flags`).
- **The gate:** the shared ally picker (`ab_filter_ok`) skips an ally the game would refuse. It applies only to the 20
  families that pick an ally.
- **New in effect:**
  - Helping Hand: the ally must be a Lord or Hero;
  - Captain of the Phoenix Guard: never a Lord, Hero or large unit;
  - Entrenchment: never a flying ally;
  - Whiplash!: never a Lord or Hero.

  Overseer of the Unseen already had all three of its rules.

### Two defects from rounds 162-164, found by the audit

1. **The ground-only WW abilities were cast in the unit form:**
   - **Affected:** Blue Fire of Chaos x2, Siegebreaker, Heaven's Gate, Lamprey's Bite, Flesh-eating Scarabs, Magma Storm.
   - **Cause:** `ww_take` set `FOURTH.eg_ground`, and nothing read it.
   - **Fix:** the dispatch now sends a WW pick with a ground row through `perform_special_ability_ground` at the chosen
     enemy.
   - **Why the tests missed it:** harness 163's "ONE ground cast" counted unit casts too. Harness 164 GR1 counts the two
     forms apart.
2. **The two sweeps had no 70% bound:**
   - **Affected:** Disembowelling Sweep (6 m) and Flesh-eating Scarabs (3 m).
   - **Cause:** `FOURTH.ENEMY_CAST` had no row for these ranges, so both fell back to the 52 m default.
   - **Fix:** NEW `ENEMY_CAST_R6 = 4` and `ENEMY_CAST_R3 = 2`.
   - **New guards:** a harness check (CD3) and a build gate refuse any `range_real` without its bound.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,004 | 0 | `h164_run1.txt` (it also prints all 946 cards) |
| FULL, run 2 | 7,004 | 0, byte-identical | `h164_run2.txt` |
| RED, pre-165 snapshot | 6,982 | 0; RED 20/20 | `h164_red.txt` |

**Section 164 (both files):**
- **CD1-CD3:** every card is whole, and the exact texts and clauses are pinned. Every `range_real` has its bound.
- **TT1:** the Entice badge's tooltip is its card.
- **US1-US8:** each ability has a refused state (no cast) and an allowed one (one cast). Entice: 40% vs 80% health.
  Daemon Flask: flying vs on the ground. Eye of the Storm: Huntsmen General vs Storm Dragon. Curse of Khsar: 90% vs 40%.
- **AT1/AT2:** Helping Hand with a Swordsmen ally gets no cast; with Arkhan, one cast on Arkhan.
- **GR1:** Blue Fire makes one ground cast and no unit cast. RED (round 164): one unit cast.

## 4. Pins rebased (harness 164 vs 163)

| Pin | Old | New | Why |
|---|---|---|---|
| h83 S1, the Eye of the Storm unit | `b2_eye_of_the_storm` | `wh3_main_cth_cha_storm_dragon_1` | the game refuses it unless the caster is large; this is its real owner |
| h142 DJ1, Curse of Djaf | caster at full health, 1 cast | caster at 40%, 1 cast | the game refuses it above 50% |
| h160 HH1, Helping Hand with a Swordsmen ally | 1 cast | 0 casts | the target must be a Lord or Hero (AT2 is the positive case) |

The tooltip mirror (h93) did not move: `FOURTH.TRIGGER_TIP` stays as the internal family label.

## 5. Build and install

- **`build_and_install165.py`:** ROUND 123 to 165 gates OK; `MATCHES SOURCE: True` for all five files. The new gate
  checks four things:
  - USAGE (60) and ATARGET (61) regenerate equal to the game data;
  - all 95 families have a card;
  - the two gates, the ground line and the badge card are present;
  - every `range_real` has its bound.
- **Installed pack:** md5 **`df53a1b19192d4afecf132049cecb6e0`**, 1,735,281 bytes, `IDENTICAL True`.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261117_round165.pack`;
  - `archive\mod_source\round165\` (source md5 `a774e3c36b987efd310679955f4b80bd`, annotated md5
    `a5e5d1c61c0c30ce30552a1b14923c2f`).
- **Backups:** `docs\backups\round165\pre165_*.lua` (md5 equal to round 164's archive).

## 6. Roster documents and audits

- **Workbook:** `docs\WH3_abilities_master_v49_2026-11-17.xlsx` plus `.ods`; `XLSX v49 VERIFY OK`.
  - No count change: 1,003 implemented, 36 skipped, 95 families.
  - NEW sheet Cards (946 rows, equal to the harness run).
  - The 22 changed keys carry a round-165 note.
  - v1 to v48 are byte-unchanged (92 files).
- **Database:** regenerated; `DATABASE VERIFY OK`.
- **Audits:** `WHEEL-STATUS AUDIT OK`; trigger audit R1 to R8 all 0.
- **Progress page:** 1,003 automated, 65 decided, 55 open.
- **Restriction audit:** `tools\audit_restrictions.py` -> `docs\WH3_restriction_audit_2026-11-17.md`.

## 7. Not done, and honest notes

- **Not seen in the game:** rounds 162 to 165 wait for a battle, from log byte 735,692,926.
- **Field checks for this round:**
  - hover an M/A badge: is the card shown?
  - Blue Fire / Siegebreaker: does the ground form cast?
  - Entice below 50%: does it stay silent?
- **No trigger was changed by design.** The audit's trigger proposals wait for your rulings (rule 9).
