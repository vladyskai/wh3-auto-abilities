# Round 201: the Master Runes leave, Endless Whirlwind of Death joins (2026-11-22)

## 1. What the user saw

A Dwarf battle on the release build (no log):

1. "Endless Whirlwind has no automatization"
2. "Master Rune of Slowness, ability on the right side, fired by itself."

## 2. The rulings (user, 2026-11-22)

- "do it" on: remove the five Master Runes the game marks as runes.
- "do it" on: the same trigger as Whirlwind of Death (for Endless Whirlwind of Death).

Earlier decisions quoted (rule 11):

- Runes, 2026-11-21: "They should not be in the mod. Just mark them as closed because they are on the right ability
  wheel." Round 192 removed the five plain runes and left the five Master Runes in, with a question that was never
  answered.
- Endless Whirlwind of Death, the questionnaire (section 2, number 56): "rejected (friendly fire)". The game data does not
  support that reason. Both keys launch the vortexes of Whirlwind of Death, and `battle_vortexs.affects_allies` is false.

## 3. The cause

The mod gives no M/A letter to a button on the right-hand bar (rule 12). The Master Runes were still entries in the
ability list. Their trigger families start armed, and a cast does not need a letter. So a Master Rune fired with nothing
on screen to show it or switch it off.

## 4. The change

| | Before | After |
|---|---|---|
| Master Rune of Breaking, Negation, Oath & Steel | on melee_unwavering | removed |
| Master Rune of Speed | on charge_or_melee | removed |
| Master Rune of Slowness | on enemy_fast_near_ally | removed |
| Endless Whirlwind of Death | not automated | fires in melee unless wavering |
| Endless Whirlwind of Death Upgraded | not automated | fires in melee unless wavering |

- Master Rune of Flight and Master Rune of Immolation are normal abilities in the game data (source_type active), not
  runes. They stay. The user was asked where he sees them.
- Roster: 982 entries / 1,035 keys / 141 trigger families (was 985 / 1,038).
- The ally arm of round 199 now rides 9 entries (Master Rune of Oath & Steel was one of the ten).
- A new permanent build gate: none of the game's 12 rune-type keys may appear in the script. The build also checks that
  the two Endless Whirlwind vortexes do not hit allies.

Tools: `tools\round201_patch.py` (both copies, backups in `docs\backups\round201\`), then
`tools\round171_regen_tables.py` (the animation and recharge tables moved).

## 5. Proof

- RED control on the pre-round source (`h199_red.txt`): with the default states and no click, Master Rune of Breaking,
  Negation, Oath & Steel and Speed each fire once by themselves. Endless Whirlwind never fires.
- GREEN: harness 199, full suite, **8,245 checks / 0 failures**, run twice (`h199_run1.txt`, `h199_run2.txt`).
- Installed test pack: md5 `d5535679368f82138f341b6138667818`, 1,625,301 bytes. The new key is in the pack, the rune key
  is not.
- Workbook v79 verified (17 checks): 1,802 rows, 687 excluded, 1,115 included, 1,035 implemented, 80 decided by the user,
  0 open.
- Database, wheel audit, trigger audit and progress page regenerated.

### Pins rebased in harness 199 (old value, new value, why)

| Pin | Old | New | Why |
|---|---|---|---|
| entries | 985 | 982 | 5 runes out, 2 Endless Whirlwind in |
| keys | 1,038 | 1,035 | the same |
| badge-path walk | 1,970 | 1,964 | 2 x 982 |
| melee_unwavering | 279 | 278 | 3 runes out, 2 in |
| charge_or_melee | 35 | 34 | Master Rune of Speed |
| enemy_fast_near_ally | 19 | 18 | Master Rune of Slowness |
| range_real fields | 429 | 428 | Master Rune of Slowness (100 m) |
| ally_range_real fields | 81 | 80 | Master Rune of Oath & Steel |
| ally arm entries (harness 198) | 8 | 7 | Master Rune of Oath & Steel |
| wind-up keys | 348 | 343 | the five runes had a wind-up |

Old worlds that used a removed rune moved to a sibling on the same trigger: harness 123 and 124 (the right-hand-bar rule)
use Hunter's Trap, harness 133 G3 uses Slippery.

## 6. The Workshop release

Rebuilt with `tools\build_release.py --pack`: `smart_ability_autocast.pack`, md5 `007f09d50b0d298a979ae477dfa2c4ed`,
1,625,349 bytes, in the game's data folder. The cast trace of the whole suite is identical on the test build and the
release build (2,083 worlds, 1,656 casts).

The Workshop item still carries the round-199 pack. The user uploads the new one with the UPDATE button of TW Launcher
(Legacy). The item is Hidden.

## 7. Not verified

- Nothing of this round has been seen in a battle.
- Whether Master Rune of Flight and of Immolation sit on the wheel or on the right-hand bar.

## 8. Donation link (researched, not added)

- SEGA's agreement for the game (Schedule 2, modding terms): no compensation for making mods, and no selling or other
  commercial use of mods.
- Creative Assembly's content page: "It is not permitted to charge or ask for money for your Total War: WARHAMMER mods."
- No source found that allows tips or names donations. Steam's own rules do not mention donation links.
- Practice: large WARHAMMER III mods carry such links (Radious: Patreon and PayPal, read on its page).
- Conclusion: a tolerated grey area, not a permission. The safe wording is an optional thank-you with nothing given in
  return. A written question to CA support would settle it.
- Service (PayPal excluded by the user): Ko-fi with Stripe is recommended. No platform fee on one-off tips, no account
  needed for the donor, a display name instead of the real name. Not confirmed: what name the donor sees on the card
  statement.
