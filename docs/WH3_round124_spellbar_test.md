# Round 124: the spell-bar badge test, game data out of Temp, Skjalandir's Fall research

Date: 2026-11-01. Harness: `harness123.lua`. Release folder:
`mod_source\releases\20261101_spellbar_test_harness123\`.

## 1. The requests

The user, 2026-11-01 (points 1, 2 and 3 only; point 4, the ammo test, and the next-batch
candidates are deferred):

1. "Let's work in a way so things like 'Windows Temp cleanup' does not affect us."
2. On the Hammer of Karak Drazh 'M' and 'A' overlap: with no runes the letters switch correctly;
   with runes it misbehaves. The runes are on the right-hand bar (spells). "What I want to test
   is it possible to add this letter on the right side or not?", isolated from the other things.
3. Skjalandir's Fall also carries Imbuement: Blinded!. Check online whether it applies only to
   ranged attacks or also to melee.

## 2. Point 1: game data no longer lives in Windows Temp

- New folder `gamedata\`:
  - `gamedata\wh3\` is the live extract set every tool reads (TSV tables and `uieff\`).
  - `gamedata\temp_snapshot_2026-11-01\` is the Temp copy as found today, frozen and never edited.
  - `gamedata\DRIFT_2026-11-01.md` is the drift report (below).
- `tools\gamedata_paths.py` is the one place that names the folder. The live tools import it:
  `build_ability_database.py`, `verify_ability_database.py`, `audit_wheel_status.py`,
  `make_xlsx_v21.py`, `verify_xlsx_v21.py`, `extract_uieff.py`
  (`tools\repoint_gamedata_2026_11_01.py` did the edit). The v21 workbook check list moved to
  `docs\backups\signoff_v21\pre_v21_workbook_md5.txt`.
- `tools\extract_gamedata.py` regenerates the whole set from the installed game: each TSV names its
  own source table on its second line, so 36 files rebuild themselves from `data\db.pack` and
  `data\local_en.pack`. All 36 came back with the same header and source line as the original
  export (the format is reproduced exactly, including the editor's colour-column folding). Seven
  older custom dumps with no source line (`db_*.tsv`, `game_auto_deactivate.tsv`) are kept frozen;
  only historical tools use them.
- This round's harness and builder read `army_spec.tsv` from `gamedata\wh3`.
- What was already lost to Temp: `wh3_layouts\` (the vanilla UI layouts) was empty, folders only.
  It can be re-extracted from `data\ui3.pack` when a layout patch is next needed.
- Not changed: historical one-shot scripts and earlier rounds' builders and harnesses still name
  Temp. They are history and are not re-run; re-running an old builder would need Temp restored.

**Drift found (the old Temp extracts against today's game):** 11 tables differ. Four mod
abilities are touched, none in a way that moves a mod constant:

| Ability | What changed |
|---|---|
| More Power! | recharge 90 s -> 120 s (unlimited uses, so no charge hold to update) |
| Storm Hammer | duration 25 s -> 30 s |
| Daemonic Whispers | phase effect type negative -> positive |
| Invocation of Nehek | an invalid-target flag row changed |

No range changed, so every 70% bound stands. The database was regenerated from the fresh
extract; its text changed only for rows whose game data changed.

## 3. Point 2: the spell-bar badge test

**Root cause (from the 2026-10-28 battle log).** The Rune Smith's runes are claimed on
`button_spell`, `button_spell2` ... `button_spell6`. Each of those buttons is the only ability
button under its own parent, so the bar-position count answered 1 for every rune, and the mod
put all five rune badges on wheel slot 1, `(96,845)`: the Hammer's slot. After the click the
Hammer's badge said 'A', and Rune of Slowness's 'M' was drawn on exactly the same spot.

**The test (isolated to spell-bar buttons).**

- `FOURTH.SPELLBAR_BADGES = true` is the test switch; set it to `false` and the old behaviour returns.
- When a claimed button's id starts with `button_spell`, the ability gets no wheel slot. Its badge
  offset comes from that button's own on-screen position, with the same formula the wheel uses:
  `BADGE_X + (x - 96), BADGE_Y + (y - 845)`. The six wheel slots are themselves the visible wheel
  buttons' positions, so if the game reports the spell button's drawn position, the badge lands on it.
- The badge follows the button: the offset is re-read every UI tick and re-applied only when it moves.
- If the position cannot be read, the badge gets its fallback offset and the log says so.
- A read-only `SPELLBAR` line, once a second per spell-bar ability, logs the button's id, visibility,
  position, relative position, its parent's id and position, and the offset applied. If the badge
  lands in the wrong place, those numbers are what the next round calibrates from.
- Wheel buttons are untouched: same code path, same offsets, same log lines.

**What the user should see:** with runes added, the Hammer's badge alone on the Hammer, with no
second letter under it. Each rune gets its own M/A badge drawn over (or near) its button on the
right-hand bar. If a rune badge appears somewhere wrong, send the battle log: the `SPELLBAR` lines
carry the numbers to correct it.

**Proof.**

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness 122 on the round-124 source (before harness 123 existed) | 5,359 | 0 | (no pin moves) |
| FULL, run 1 | 5,398 | 0 | `h123_run1.txt` |
| FULL, run 2 | 5,398 | 0, byte-identical to run 1 | `h123_run2.txt` |
| LIGHT (`H118_LIGHT=1`) | 2,217 | 0 | `h123_light.txt` |
| RED control, pre-124 snapshot (light) | 2,193 | 7, all section-123 tokens | `h123_red.txt` |

Section 123 (39 checks, live and annotated):

- **S1, the field case:** the Hammer badge stays on wheel slot 1 `(-865,-209)`; the rune badge on
  `button_spell4` at `(1300,1000)` gets `(339,-54)`; the two no longer share a spot.
- **S2:** the button moves to `(1400,1000)` and the badge follows to `(439,-54)`.
- **S3:** an unreadable position gives the logged fallback.
- **S4:** the SPELLBAR line reports button, position and parent.
- **S5:** a wheel-only Rune Smith behaves exactly as before, with no spell-bar line.

**The RED control reproduces the field bug** in both files: on the pre-round source the rune badge
is placed on the Hammer's own offset, `hammer (-865,-209), rune (-865,-209)`.

The harness mock gives the spell bar the in-game shape (each button alone under its own parent),
and defines `Position()` only on those new components, so no earlier world changed.

Harness corrections during the round (harness-side only, no mod change): the first SPELLBAR check
polled without the UI tick the sweep runs on.

**Build:** `build_and_install124.py` (from `tools\make_builder124.py`), with army_spec read from
`gamedata\wh3` and a new gate that the test is in the source. Results:

- `ARMY-BAR GATE OK: 759 ABILITIES keys, none of them in the 286-key army_spec junction`
- `ROUND 124 GATE OK`, and `MATCHES SOURCE: True` for all five files.
- Installed pack md5 **`14775f8bb2323381bf850b578e210e21`**, 1,120,795 bytes, `IDENTICAL True`.

Archived: `archive\packs\zz_test_deadly_onslaught_20261101_round124.pack` and
`archive\mod_source\round124\` (source md5 `9ef2c8bc90f08d33b3491f48bf421f70`, annotated md5
`a20d0b6bfbfe5a808ec65df9fea7d525`).

**Known limit:** an ability whose fallback offset is the default `(0,0)` lands on wheel slot 1 when
its spell-bar position cannot be read. The log names that case ("using fallback offset").

**Not verified:** whether `Position()` on a spell-bar button reports where the button is drawn.
That is exactly what the field test answers.

## 4. Point 3: Skjalandir's Fall and Blinded!

- **Game data** (`phases.tsv`): the ability's phase imbues contact effect
  `wh3_dlc23_unit_contact_blinded` and adds Accuracy +90, for 39 s, with a 120 s cooldown. Carrier:
  Ulrika Magdova, who has a bow (30 arrows).
- **Online** (Total War: WARHAMMER Wiki, "Skjalandir's Fall" page, Strategy section): "it is also
  powerful in melee, as the contact effect is imbued to melee attacks as well." The same wiki's
  search summary describes this Blinded! variant as Melee Attack -24, Melee Defence -24, Missile
  Block Chance -26, Speed -50% for 26 seconds on the enemy hit.
- **Consequence:** the ability pays off in melee (the Blinded! debuff on what she hits) and at range
  (Accuracy +90 and Blinded! on arrow hits). The current trigger, `melee_unwavering`, covers the
  melee half correctly. The ranged half (fire while she is shooting at an enemy in melee) still
  waits on the ammo test (point 4, deferred). No change was made in this round.

## 5. Not done

- No workbook version: no roster change.
- Point 4 (the ammo test) and the next-batch candidates: deferred by the user.
- The spell-bar badges are not field-tested.
