# Round 166: the short cards (sign-off round)

Date: 2026-11-17. Harness: `harness165.lua`. Release folder: `mod_source\releases\20261117_short_cards_harness165\`.

## 1. The rulings (user, 2026-11-17, after the Daemons battle)

1. Remove the note at the bottom of the ability card ("Automatic: click the M/A badge to switch automatic use on or off").
2. The ALL tooltip: keep only "arm or disarm every automatic ability of the selected unit(s)" (marked-up screenshot).
3. "The tooltip for our A/M badge is amazing, it works. But the text is too long and not thematic. We need to be concise
   and condense the meaning of the triggers in the least amount of words possible. For example, Deadly Onslaught might
   say 'fires when charging'."
4. "Vortex with affects_allies=false should have no friendly-fire check."
5. Read the Daemons of Chaos battle.
6. "'Caster doesn't count' for wanderers too?" "yes, do not count the caster."

## 2. What changed (what you will see in battle)

### The card on the M/A badge

- **Shorter:** one short sentence per family. No distances: the 70% bounds stay in the code and the log. No ability name,
  no "on A:". The game's own restrictions follow as short clauses.
- **Length:** the longest card is now 115 characters; in round 165 it was 289.
- **Cards that change form:** four aura families read differently when the unit has no aura. Example: "Fires under missile
  fire." rather than "Fires when it or a nearby ally is under missile fire."
- **Friendly-fire wording:** "clear of allies" appears only when the blast can hurt our units. Heaven's Gate, Abyssal
  Swarm and Crackleblaze do not carry it.

| Ability | Round 165 | Round 166 |
|---|---|---|
| Deadly Onslaught | Deadly Onslaught on A: fires when this unit runs at the enemy it is attacking, 12 to 60 m away and at most 4 s from contact, or when it is in melee. | Fires when charging or in melee. |
| Entice | Entice on A: fires when this unit is in melee and not wavering; not below 50% health. | Fires in melee unless wavering; not below 50% health. |
| Bloodbeast | Bloodbeast on A: fires when this unit is in melee and not wavering, with none of your other units within 25 m of it. | Fires in melee unless wavering, clear of allies. |
| Helping Hand | (long sentence); the ally must be a Lord or Hero. | Fires in melee unless wavering, on the nearest ally in range; Lord or Hero allies only. |
| Banishment | (long sentence with 38 m) | Fires when it and the target stand still, where the blast hurts the enemy most, clear of allies. |
| Heaven's Gate | (long sentence) | Fires when it and the target stand still, where the blast hurts the enemy most. |
| Unholy Clamour | (long sentence) | Fires when it or any ally wavers. |
| Eye of the Storm | (long sentence); only when this unit is a large unit. | Fires in melee unless wavering; only in large form. |

All 946 cards are in the Cards sheet of workbook v50 and in `cards_round166.tsv`.

### The static card line

The note is gone. The mod no longer ships `ui/common ui/special_ability_tooltip.twui.xml`. That file existed only to add
the line, and it was a copy of the game's layout taken before the 9.0.5 patch. The game's own current layout now applies.
The pack holds four files. The source file was removed; a copy is in `archive\mod_source\round166_retired\`.

### The ALL tooltip

"Arm or disarm every automatic ability of the selected unit(s)."

### The wanderers

The caster never blocks its own wanderer. This is the same rule as the waves (round 164). It covers the `enemy_wander`
rows of kinds 2 and 3 whose blast can hit our units (39 keys). Another unit of ours inside the safety ring still blocks
the cast. Da Boss' Loons (kind 6) already used the "other units" check.

### Friendly fire on ally-safe vortices

Already true before this round:
- the four vortices the game marks as harmless to our units (Heaven's Gate, Abyssal Swarm, Crackleblaze, Arcane Vassal)
  had no friendly-fire check;
- every other friendly-fire check sits on a blast the game says hits our units.

NEW permanent build gate: `tools\ff_gate.py` checks the 95 keys on families with a fixed check (blob attacks, the shots,
melee_clear, fly_dive, last_stand_clear, the Sigil). The build is refused if any of them has a vortex, projectile,
explosion or bombardment the game says cannot hit our units. Negative control: Heaven's Gate's key placed on
melee_clear is refused.

## 3. The Daemons battle (log bytes 735,692,926 to 760,068,621)

Archived as `archive\logs\battle_20261117_r165_daemons.txt` (24 MB).

| Fact | Value |
|---|---|
| Casts accepted | 86, on 34 abilities |
| Refused "on cooldown" | 74: mostly the expected retry one poll after an instant cast, which proves the first cast took (round 160) |
| Other refusals, script errors | 0 |
| Card tooltip set | 37 badges, all ok=true (and you saw it in game) |
| Ground casts | Searing Doom 2, The Portalglyph 1, Karanak's Howl 1 |
| Caster-rule refusals (round 165) | none needed in this army |

**Notes on individual abilities:**
- **Karanak's Howl:** two ground attempts were refused "does not support this special ability". The second was a real
  recharge. The first came 20 s before the accepted cast, at 34.5 m against a 35 m bound. It is unexplained and harmless.
- **Burning Rage:** fired with our nearest other unit 41.1 m away (it needs more than 25 m).
- **Gaze of Fate:** fired on a Wizard on a beast running at 13.5 m/s, 39.3 m from our units.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,025 | 0 | `h165_run1.txt` (it prints all 946 cards) |
| FULL, run 2 | 7,025 | 0, byte-identical | `h165_run2.txt` |
| RED, pre-166 snapshot | 7,023 | 0; RED 12/12 | `h165_red.txt` |

**Section 165 (both files):**
- **SC1:** every card is short and whole: 946/946, longest 115. RED: 0/946, longest 289.
- **SC2:** eleven exact cards are pinned.
- **TT2:** the Entice badge shows its short card.
- **AL2:** the ALL text is exact.
- **WD1:** Banishment with only its caster 20 m from the target casts once. RED: no cast.
- **WD2:** with our Swordsmen there too, it does not cast.

## 5. Pins rebased (harness 165 vs 164)

| Pin | Old | New | Why |
|---|---|---|---|
| h152 AP2a | the ALL tooltip contains "ALL: arm or disarm" | contains "Arm or disarm every automatic ability of the selected unit(s)." | ruling 2 |
| h153 BT1a | contains "The button stays pressed while all of them are on A." | the same new sentence | ruling 2 |
| h164 CD1 | a card starts "name on A: " | a card starts "Fires " | ruling 3 |
| h164 CD2 | twelve long cards / clauses | the same twelve abilities on their short cards | ruling 3 |
| h164 CARD print | printed every card | removed (h165 prints them; one copy per run) | |
| h93 D4a | the twui.xml carries the static line | the twui.xml is retired: no source file, no line | ruling 1 |

## 6. Build and install

- **`build_and_install166.py`:** ROUND 123 to 166 gates OK; `MATCHES SOURCE: True` for all four files; the pack holds no
  card xml.
- **Installed pack:** md5 **`5fdc60d3685f343e1efd2dc5869fd39e`**, 1,400,952 bytes, `IDENTICAL True`.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261117_round166.pack`;
  - `archive\mod_source\round166\` (source md5 `49f9e0b723c70d78dd798bc851dde1b0`, annotated md5
    `d9cdf72d6fd13c81a34ecbbff771a850`).
- **Backups:** `docs\backups\round166\pre166_*.lua`, equal to round 165's archive.

## 7. Roster documents and audits

- **Workbook:** `docs\WH3_abilities_master_v50_2026-11-17.xlsx` plus `.ods`; `XLSX v50 VERIFY OK`.
  - The Cards sheet holds the short cards.
  - The 39 wanderer keys carry a round-166 note.
  - No count change; v1 to v49 are byte-unchanged (94 files).
- **Database:** regenerated; `DATABASE VERIFY OK`.
- **Audits:** `WHEEL-STATUS AUDIT OK`; trigger audit R1 to R8 all 0.
- **Progress page:** 1,003 automated (416 seen in battle), 65 decided, 55 open.

## 8. Not done, and honest notes

- **Not yet seen in game:**
  - the game's own card layout without our xml (expected: the vanilla card, with no last line);
  - the short cards;
  - the wanderer rule.
- **Still waiting for a battle:** the round-162 to 165 field checks (Blue Fire, Siegebreaker and Magma Storm ground
  casts; Entice silent below 50%). The next battle starts at log byte 760,068,621.
- **Still waiting for your rulings:** the rest of the overnight audit (`docs\WH3_overnight_audit_2026-11-17.md`).
  - Commanding Presence and Fury of Ulric (the hidden "ally in melee" condition);
  - the score 1 to 3 trigger groups;
  - visibility for the old enemy pickers;
  - the feature ideas.
