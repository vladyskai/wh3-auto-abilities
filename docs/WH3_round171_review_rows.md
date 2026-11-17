# Round 171: the score 1-2 review, rows 1-15 and 21 (sign-off round)

Date: 2026-11-17. Harness: `harness170.lua`. Release folder: `mod_source\releases\20261117_review_rows_harness170\`.

## 1. The rulings (user, 2026-11-17, on `docs\WH3_low_score_review_2026-11-17.md`)

- **Rows 1-15:** "You can implement items 1-15."
- **Row 16 (Rock Eye):** "are you sure Rock Eye is not a passive?" Answered below; no change.
- **Row 17 (Watched by the Watcher):** "close (no actuation)".
- **Row 18 (Null Stone):** "seems like an item ability available only in multiplayer (pls confirm). If confirmed,
  close." NOT confirmed (below), so it is unchanged.
- **Rows 19-20 (Sceptre of Stability, Locus of Abjuration):** "close, no read against enemy magic. Under missile fire
  makes no sense, your assumption is incorrect."
- **Row 21 (Necrotic Phylactery):** "do the contact effect list please".
- **Row 22 (Focus Instincts):** "if not possible to read a rampaged unit, then close". There is no read (CLAUDE.md,
  round 137), so it is closed.
- **During the round:** "you also can check each ability in forums, reddit, etc." Results below.

## 2. What changed (what you will see in battle)

| Row | Ability | Before | Now |
|---|---|---|---|
| 1 | Horn of the Wild Hunt | in melee | **army_charge:** fires when 3+ of your units charge, or entered melee at most 2 s ago |
| 2 | Potion of Foolhardiness | (round 170) | charge or wavering |
| 3 | Ursun's Roar (`wh3_main_character_abilities_ursuns_roar`) | in melee, shared with 3 melee keys | its own entry on **aura_charge:** the caster charges or just made contact, or 2+ units within 24 m do |
| 4 | Red Fury | in melee, on self | **self_or_ally_charge:** the caster charging; else the nearest ally within 70 m charging or just in contact (cast on that ally); else the caster in melee |
| 5 | Waaagh! (`wh_main_character_abilities_waaagh`) | in melee, shared with the dlc26 key | its own entry on **army_charge**; the dlc26 key (melee attack and damage, self) stays in melee |
| 6 | The Rock of Inevitability | in melee | **slow_aura:** in melee, or a visible fast enemy inside its 24 m aura |
| 7 | The Wissenland Runefang | in melee | **slow_aura** |
| 8 | Black Staff | in melee | **winds_low:** winds pool below 30, reserve 20+, caster above 50% health (starts on M: self-damage) |
| 9 | Forbidden Rod | in melee | **winds_low** (starts on M) |
| 10 | Wand of Jet | in melee | **when_ready** |
| 11-15 | Earthing Rod, Hagtree Fetish, Master of the Black Arts, Maw Shard, Power Familiar | in melee | **CLOSED** (rule 10: they help only before a friendly spell) |
| 17 | Watched by the Watcher | in melee | **CLOSED** |
| 19, 20 | Sceptre of Stability, Locus of Abjuration | in melee | **CLOSED** (no read of enemy magic) |
| 21 | Necrotic Phylactery | at or below 75% health | **contact_melee:** in melee, not wavering, against an enemy whose melee blows carry a contact effect |
| 22 | Focus Instincts | in melee | **CLOSED** (no read of a rampaging unit) |

**New reads:**
- **Fresh contact:** `FOURTH.track_melee` runs once per poll for every unit of yours and remembers when it entered
  melee. "Just made contact" means within 2 s, when a charge bonus still pays about 80%.
- **The contact list:** GENERATED `FOURTH.CONTACT_TEXT` (`tools\gen_contact_keys.py`, from the newly extracted
  `melee_weapons` table). It holds 503 land units whose melee weapon has a contact phase, or whose passive ability
  imbues one (poison, sundered armour, blinded, flammable, ...).
  - Plaguebearers are on the list; Swordsmen and Grave Guard are not.
  - Missile contact effects are left out: the trigger is a melee one.

**Defaults:**
- Every moved entry keeps its old default (`start_armed`: 8 entries now).
- Black Staff and Forbidden Rod start on M (self-damage, round 167).

**Counts:**
- 946 → 939 entries; 1,003 → 994 keys;
- 101 trigger families (6 new);
- melee_unwavering 298 → 282; ushoran_health 19 → 18; when_ready 21 → 22.

## 3. Answers

**Row 16, Rock Eye: not a passive, by the game's data.** Despite "passive" in its key
(`wh3_main_item_passive_rock_eye`), the data says it is an activated ability:
- `unit_special_abilities.passive = false`;
- `unit_abilities.source_type = active`;
- one use, 60 s.

It has never been cast in any of your battle logs, so it is not field-proven. Row 16 is unchanged and still waits for
your ruling.

**Row 18, Null Stone: NOT multiplayer-only.** The game's item table (`ancillaries`, extracted this round) gives:
- `mp_exclusive = false`;
- `randomly_dropped = true`;
- `faction_set = anc_set_exclusive_high_elves`.

So it is a High Elf arcane item that drops in campaign. Your condition for closing it is not met, so it is unchanged.

**Row 22, a rampaging unit:** no battle read exists (CLAUDE.md, round 137). Closed as ruled.

**Forum and Reddit check:**
- A research agent searched the web for bug reports and player advice on the 18 abilities of this batch. It found
  nothing usable either way.
- Its search tool does not index Reddit, Steam discussions or the CA forums, so this is not evidence that they work.
- Two CA "known issues" threads on Steam turned up but were not read:
  - https://steamcommunity.com/app/1142710/discussions/2/3826413850811137613
  - https://steamcommunity.com/app/1142710/discussions/2/3272440173702026577

**Side finding:** the progress page's "seen in battle" count reads every `*log*.txt` on the PC, including the test-run
logs. That is how Null Stone came to be marked "seen": only a test unit called "lord" ever cast it. The count is
overstated. A fix is one line (read only the game's log and `archive\logs\`), not done.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,199 | 0 | `h170_run1.txt` |
| FULL, run 2 | 7,199 | 0, byte-identical | `h170_run2.txt` |
| RED, pre-171 snapshot | 7,197 | 0; RED 36/36 | `h170_red.txt` |

**Section 170 (both files):**
- **Horn of the Wild Hunt:**
  - AC1: 3 units charging, one cast;
  - AC2: 2 units, no cast;
  - AC3: 3 allies just in contact, one cast.
- **Waaagh!:** WA1, 3 units charging, one cast.
- **Ursun's Roar:**
  - UR1: the caster charging;
  - UR2: 2 allies within 24 m charging.
- **Red Fury:**
  - RF1: an ally 30 m away charging, cast on the ally;
  - RF2: the caster in melee.
- **The Rock of Inevitability:**
  - SA1: a fast enemy 15 m away, one cast;
  - SA2: the same enemy hidden, no cast.
- **The Wissenland Runefang:** WS1, in melee.
- **Black Staff:**
  - WL1: pool 20, reserve 50, 90% health, one cast;
  - WL2: pool 60, no cast;
  - WL3: 40% health, no cast.
- **Wand of Jet:** WJ1, when ready.
- **Necrotic Phylactery:**
  - CM1: in melee with Plaguebearers, one cast;
  - CM2: with Swordsmen, no cast.
- **CA2:** the six new cards.
- **RED:** the old build fires none of the new cases and still fires the two plain in-melee ones.

**One defect found and fixed during testing:** in the reading copy the ally picker answers `false` (not `nil`) when no
ally qualifies. Red Fury then skipped its in-melee self-cast in that copy. Both copies now test `if r then`.

## 5. Pins rebased (harness 170 vs 169)

| Pin | Old | New | Why |
|---|---|---|---|
| every entry count (80 places) | 946 | 939 | 9 closed, 2 split |
| key-count comparisons (11) | 1,003 | 994 | 9 closed keys |
| melee_unwavering (15 + 2 EXP) | 298 | 282 | 7 moved out, 9 closed |
| ushoran_health (5 + 1 EXP) | 19 | 18 | Necrotic Phylactery moved |
| when_ready (1) | 21 | 22 | Wand of Jet |
| ally_range_real fields (3) | 58 | 59 | Red Fury |
| start_armed entries (1) | 1 | 8 | the moved entries keep their default |
| h103 charge-gate rows | 328 | 327 | Watched by the Watcher's hold row removed |
| h105 A4a iterations | 1,892 | 1,878 | 2 x 939 |
| h101 0aa neighbours list | includes Hagtree Fetish | without it | closed |
| h91 O3 twin keys | Waaagh!'s two keys | Ursun's Roar's pro twin keys | Waaagh! split |
| h93 label mirror | 95 families | + the 6 new labels | new families |

**Builder:**
- the same counts;
- the auto-accepted list (AUTO327) loses the 9 closed markers (300 → 291 entries, 315 → 306 keys);
- the ROUND 171 gate regenerates CONTACT and refuses a closed key back in the source.

**Generated tables:** RECHARGE was regenerated (the closed keys left it). ANIM, USAGE, ATARGET, RISKY and the wind-up
table were unchanged.

## 6. Build, install, documents

- **Installed pack:** md5 **`1b034829db0943b35e777f06d31a2914`**, 1,445,218 bytes; `MATCHES SOURCE: True` for all
  four files; ROUND 123 to 171 gates OK.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261117_round171.pack`;
  - `archive\mod_source\round171\` (source md5 `a6264c790605c86505a1035ae1900ea3`).
- **Workbook:** `docs\WH3_abilities_master_v54_2026-11-17.xlsx` plus `.ods`; `XLSX v54 VERIFY OK`.
  - 994 implemented, 45 skipped, 101 families;
  - the moved rows carry their new family and text;
  - the 9 closed rows read "SKIPPED (user decision)";
  - Waaagh!'s and Ursun's Roar's twin lists follow the split;
  - v1 to v53 are byte-unchanged (102 files).
- **Tracker:** 20 inventory rows updated (9 closed, 11 with their new family).
- **Database:** `DATABASE VERIFY OK`.
- **Audits:** `WHEEL-STATUS AUDIT OK`; trigger audit all 0 (`slow_aura` joins the melee-or-charge families).
- **Progress page:** 994 automated, 74 decided, 55 open.
- **Game data:** `gamedata\wh3\ancillaries.tsv` and `melee_weapons.tsv` were extracted (git-ignored, as all game
  data).

## 7. Not done

- **Not seen in game:** the next battle starts from the log's current end.
- **Waiting for your rulings:**
  - row 16 (Rock Eye: active by the data);
  - row 18 (Null Stone: campaign item, not multiplayer-only);
  - rows 23-50 of the review (tomorrow).
