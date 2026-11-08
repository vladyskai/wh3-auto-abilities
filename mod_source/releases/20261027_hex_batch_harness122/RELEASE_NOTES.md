# Round 123: the hex batch, one trigger per ability (tuning round)

Date: 2026-10-27. Harness: `harness122.lua`. Release folder:
`mod_source\releases\20261027_hex_batch_harness122\`.

## 1. The ruling

The user, verbatim:

> Of Group A, the ones that have no speed effects should have the melee_unwavering trigger.
> The ones that reduce the enemies speed should trigger in melee or when charging. This way
> we avoid the issue of fire on an enemy that is only passing by.
> Of Group B, they need more diversity. The one with effect only -40 melee defense makes sense
> only when the enemy is in melee. It does not make sense to activate it when the enemy is
> shot (please learn from this example). The Transfix (dlc29 key) should be the same, since a
> trigger for the Silenced condition would be hard to implement. Flash bomb can be the same,
> we might think later if a trigger that leverages its speed reduction makes sense. Daemonic
> possesion would make sense only before a cast, so I say we do not automate that one. Hunter
> of champions is okay for enemy_engaged_or_shot.

The lesson recorded for future proposals: pick each ability's trigger from the stat its
effect changes and the moment that stat pays off. A melee-only stat (melee attack, melee
defence) never goes on a trigger with a missile arm. This rule is now in `CLAUDE.md` section 2.

## 2. What changed

| Ability | Key | Trigger | Why (the effect) |
|---|---|---|---|
| Rival Hide Talisman | `wh2_main_item_abilities_rival_hide_talisman` | `melee_unwavering` | enemy melee attack -40 within 35 m, no speed effect |
| Seductive Glory | `wh3_main_lord_abilities_seductive_glory` | `melee_unwavering` | enemy melee defence -24, Rampage, no speed effect |
| Vine Dragon Scale | `wh2_dlc15_item_abilities_vine_dragon_scale` | `melee_unwavering` | enemy melee defence -24, no speed effect |
| Dark Mace | `wh3_dlc23_weapon_abilities_dark_mace` | `melee_unwavering` | enemy armour -30, no speed effect |
| Seduction | `wh2_dlc11_lord_abilities_seduction` | `charge_or_melee` | enemy speed -25%, melee attack -24 |
| Song of Enthrallment | `wh2_dlc11_lord_abilities_song_of_enthrallment` | `charge_or_melee` | enemy speed -45%, melee attack -24 |
| Smoke Bomb | `wh_dlc06_unit_abilities_smoke_bomb` | `charge_or_melee` | enemy charge speed and speed -60% |
| No Escape | `wh3_main_character_abilities_no_escape` | `enemy_melee` (new) | melee defence -40 on one enemy; 100 m, bound 70 m; 3 uses, held 90 s |
| Transfix (hex) | `wh3_dlc29_lord_abilities_transfix` | `enemy_melee` (new) | melee defence -40, Silenced; 100 m, bound 70 m; 3 uses, held 120 s |
| Flash Bomb | `wh_pro01_lord_abilities_flash_bomb` | `enemy_melee` (new) | slow -60%, melee defence -24; 75 m, bound 52 m |
| Hunter of Champions (upgraded) | `wh2_dlc17_character_abilities_hunter_of_champions_upgraded` | `enemy_engaged_or_shot` | second key on the existing entry (same 100 m range) |

Not automated, by user decision: Daemonic Possession (`wh3_main_lord_abilities_daemonic_possession`).

The new Transfix entry uses marker `transfix_hex`, because the Transfix already in the mod
(`wh2_dlc11_lord_abilities_transfix`) is a different ability: a self buff (speed +25%, damage
resistance +20).

### The new trigger, `enemy_melee`, in plain words

```lua
function FOURTH.evaluate_enemy_melee(unit, routing)
	FOURTH.eg_melee_only = true
	return FOURTH.eg_pick_enemy(unit, routing, false)
end
```

- Line 1: switch on the "melee only" flag. That flag already existed for Gate of Khorne; it
  turns off the "enemy under missile fire" half of the shared enemy picker.
- Line 2: run the same enemy picker that the 85 `enemy_engaged_or_shot` entries use. It walks
  the enemy army, keeps enemies that are alive, a valid target, in melee, and within this
  ability's own 70% limit (edge-to-edge distance), and picks the closest. `false` means cast
  at the enemy unit, not on the ground.
- Just before the cast, the shared re-check reads the enemy again: if it is no longer in melee,
  dead, or outside the limit, the cast is skipped and not spent.

What you see in battle: No Escape, Transfix and Flash Bomb fire only at an enemy within reach
that is locked in melee (with anyone, not only with the caster). An enemy that is only being
shot at, or is out of reach, is ignored.

### Counts

| Measure | Before | After |
|---|---:|---:|
| ABILITIES entries | 697 | 707 |
| ability keys | 748 | 759 |
| trigger evaluator families | 45 | 46 |
| `melee_unwavering` | 370 | 374 |
| `charge_or_melee` | 25 | 28 |
| `enemy_melee` | 0 | 3 |
| `enemy_engaged_or_shot` (entries) | 85 | 85 |
| `range_real` fields | 204 | 207 |
| charge-gate held keys | 161 | 163 |

Applied by `tools\round123_changes.py` to the live source and the annotated copy identically.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 5,359 | 0 | `h122_run1.txt` |
| FULL, run 2 | 5,359 | 0, byte-identical to run 1 | `h122_run2.txt` |
| LIGHT (`H118_LIGHT=1`) | 2,178 | 0 | `h122_light.txt` |
| RED control, pre-123 snapshot (light) | 2,178 | 128, all in section 122 | `h122_red.txt` |

Section 122 (345 checks, 76 worlds, each on the live source and the annotated copy):

- **A** (4 abilities): in melee FIRES on the owner; out of melee SILENT; wavering SILENT.
- **C** (3 abilities): in melee FIRES; CHARGING (running, targeted, 20 m) FIRES with the charge
  reason; running with NO target (a move order, an enemy only passing by) SILENT.
- **E** (3 abilities): enemy in melee at 20 m FIRES at the ENEMY; enemy only UNDER MISSILE FIRE
  stays SILENT; enemy in melee 1 m beyond the bound SILENT; exactly on the bound (70 m / 52 m)
  FIRES; enemy leaves melee between decide and cast: SKIPPED, cast not spent.
- **G**: No Escape casts once, then is still held 10 s later, and the log names its own 90 s recharge.
- **H**: the upgraded Hunter of Champions key fires on an enemy under missile fire, through the
  existing entry's badge.
- **0s**: tokens in both files, including no army-bar key (read from `army_spec.tsv`) and no
  Daemonic Possession.

RED control (`H122_LIVE` / `H122_ANN` on `docs\backups\round123\pre123_*.lua`): 128 failures,
all inside section 122 (the tokens and every world that needs the new entries); the 37 silent
worlds pass. No check outside the section failed. Before the final RED run I corrected the
section's own expectations twice (both harness-side, no mod change): a key-count check that
forgot the key also appears in the charge-gate table, the world total (76, not 90), and which
lapse worlds count as log proofs on the snapshot.

Pin rebase (`tools\make_harness122.py`, 66 non-comment lines, listed in
`make_harness122_out.txt`): entries 697 -> 707, keys 748 -> 759, `melee_unwavering` 370 -> 374,
`charge_or_melee` 25 -> 28, `range_real` 204 -> 207, charge-gate keys 161 -> 163, the A4
bootstrap iterations 1394 -> 1414 (two per entry). Plus one content line: harness 93's mirror of
the allowed tooltip wordings gained the `enemy_melee` sentence (without it D2/D3 correctly
reported a trigger with no allowed wording). Running harness 121 on the new source failed on
exactly these pins and that wording, and on nothing else.

## 4. Build and install

Builder `build_and_install123.py` (from `tools\make_builder123.py`): count pins moved (11 entry
asserts 697 -> 707, 4 `melee_unwavering` 370 -> 374, 1 `charge_or_melee` 25 -> 28, 2
`range_real` 204 -> 207) and one new gate: the `enemy_melee` evaluator is present and wired, has
exactly 3 entries, and Daemonic Possession is absent.

- `ARMY-BAR GATE OK: 759 ABILITIES keys, none of them in the 286-key army_spec junction`
- `ROUND 123 GATE OK: enemy_melee evaluator wired, 3 entries, no Daemonic Possession`
- `MATCHES SOURCE: True` for all five shipped files.
- Installed pack md5 **`88890ada80776c18ba5e142eeb3d9ced`**, 1,116,453 bytes, `IDENTICAL True`;
  the live source is embedded byte-for-byte in it.

Archived: `archive\packs\zz_test_deadly_onslaught_20261027_round123.pack`,
`archive\mod_source\round123\` (source md5 `4f9e0d31500553e960a2a90f259a9067`, annotated md5
`e6dac1058d65c5a92322ceb2dd1adf0c`). The replaced round-122 pack was already archived
byte-identical. Pre-round snapshots: `docs\backups\round123\`.

## 5. Not done (deferred to the v21 sign-off, now covering rounds 122 and 123)

- Master spreadsheet v21, the tracker and the database: 21 implemented rows (10 from round 122,
  11 keys from round 123) still read NOT IMPLEMENTED, and Daemonic Possession still needs its
  "rejected (user decision)" status. The new `enemy_melee` family needs its Definitions entry.
- `tools\audit_wheel_status.py` and `tools\verify_ability_database.py` not re-run.
- Not field-tested.
- Open idea from the user, not built: a trigger for Flash Bomb that uses its speed reduction.
