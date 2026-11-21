# Round 199: the overnight review's second replies (2026-11-22)

## 1. The rulings

User, 2026-11-22, replying to the round-198 report:

| Review row | Reply | This round |
|---|---|---|
| 5 Doom & Darkness (gunnery school), the capital B | "okay, then fix" | BUILT |
| 9 the ten ally-targeted abilities cast on the caster | "please implement, but also include the caster as I tested and it could cast on the caster". On Cash Cascade: "tested and it did fire" | BUILT (option A plus the caster) |
| 10 the bombardments' infantry test | "agreed, please fix" | BUILT (option A) |
| 12 the remembered M/A choice | "agreed, implement" (option A) | BUILT |

Also: "Swordsmen ... this unit has no active abilities. bad example". Correct. The test of row 12 uses two units of one
type that own Primeval Roar.

## 2. The change (`tools\round199_patch.py`, both copies)

1. **A key with a capital letter.** The badge code lowercases the button's key and compares it with the listed key. The
   game spells one key with a capital B (`wh3_dlc25_spell_Bound_doom_and_darkness_gunnery_school`), so it never matched.
   `FOURTH.KEY_LOWER` (built at load, one row today) gives the listed key in lower case and the compare accepts it.
2. **The ally arm** (`FOURTH.ally_arm_wrap`, entry field `ally_value_arm`). The entry keeps its own trigger for the
   caster. It also looks for the most valuable ally in melee inside the game's range (the round-179 pick). The more
   valuable of the two wins, the caster on a tie. Entries and ranges (`ally_range_real`, the range rule applies):

   | Ability | Game range | Bound | Caster's own trigger |
   |---|---|---|---|
   | Hellish Vigour Upgraded | 75 m | 55 m | in melee unless wavering |
   | Cash Cascade | 200 m | 180 m | charging or in melee |
   | Master of Alchemy (4 variants) | 100 m | 80 m | in melee, or allies shooting in its aura |
   | Master Rune of Oath & Steel | 100 m | 80 m | in melee unless wavering |
   | Spite of Da Bad Moon | 150 m | 130 m | in melee unless wavering |
   | Wild Abandon | 100 m | 80 m | ALLY ONLY |
   | The Hand of Dust | 200 m | 180 m | ALLY ONLY |

   **Ally only** (`ally_value_arm = "only"`): Wild Abandon and The Hand of Dust are single-target abilities. The game
   gives them neither the caster (`target_self` false) nor a ground form, which is the Favour of the Fay case the user
   ruled on ("the game will refuse the cast"). The user's test that a cast on the caster works was Cash Cascade, an area
   ability with a ground form. The build checks this split against the game table.
3. **The infantry test** of the 30 bombardment entries (31 keys) refuses a unit of the generated large set and a unit
   flying right now, before it asks the engine. The engine calls Fell Bats, the Varghulf and the Zombie Dragon infantry.
4. **The remembered choice.** `ability.remembered[type]` is now the START of the battle and a click no longer changes
   it. The click goes to `ability.remember_next[type]`, the table the file is written from (the last click wins). The
   reset clears both.

## 3. What changes in battle

- On the Amethyst Land Ship, when Doom & Darkness is on its wheel, the icon gets its M/A badge.
- The ten abilities above can now go to an ally in melee. The hover card of the eight says "..., or on a more valuable
  ally in melee", the card of the two says "Fires on the most valuable ally in melee".
- Comet-type bombardments no longer drop on a Varghulf, a Zombie Dragon or a flying unit.
- Clicking one unit's badge changes that unit only. The other units of the same type keep their state for this battle.
  The next battle starts every unit of that type on the last choice you clicked.

## 4. Proof

- Harness 198: **8,210 checks / 0 failures**, twice, byte-identical (8,161 old + 49 new). New section 0zz46 (tokens), KB1
  (the capital key), AA1-AA6 (the ally arm and the cards), IN1-IN3 (the infantry test), RS1-RS2 (the remembered choice).
- RED (`h198_red.txt`, the pre-199 snapshot, every RED expectation met): no badge for the capital key, Spite and Wild
  Abandon cast on the caster, no cast for an ally when the caster is idle, the bombardment drops on the Varghulf and on
  the flier, the click flips the untouched unit of the same type.
- THREE count pins rebased in harness 198 (old harnesses untouched): the number of `ally_range_real` fields, 71 -> 81,
  in sections 98, 99 and 104. Before the rebase harness 197 failed exactly these 6 checks (3 pins x 2 files) on the new
  source and no world.
- Build `build_and_install199.py`. ROUND 199 GATE: the compare line, the wiring, exactly 10 ally-arm entries whose game
  rows target friends and carry the game's range, ally-only exactly where the game gives neither caster nor ground, the
  infantry lines, a click writes `remember_next` only. Rebased: the builder's own 71-field pin.
- Installed pack md5 **`8c61a82ae7f86bb2820b5156ad65fc5d`**, 1,626,713 bytes, 5 x `MATCHES SOURCE: True`, archived.
- Workbook **v78** (`verify_xlsx_v78.py` OK): 41 trigger texts extended (8 ally arm, 2 ally only, 31 bombardments), 10
  cards restated. No roster change.

Not seen in game yet. Next battle from log byte 978,682,624 (re-measure before reading).

## 5. Not verified

- Whether the game accepts an AREA ability ordered at an ALLY unit (the user tested the caster). The ally casts go out in
  unit form on the ally, like every other ally-targeted ability of the mod.
- Whether Wild Abandon and The Hand of Dust would in fact accept the caster. If a test shows they do, the two entries
  change from `"only"` to `true`.
