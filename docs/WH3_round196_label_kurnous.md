# Round 196: the MCT label back, why Arrow of Kurnous held (2026-11-21)

## 1. The user's report

- MCT page (screenshot): "Now it is not clear what the button does. I liked the previous text, just not the misaligned
  '?'." And: "I tested the functionality of the button and it worked, well done" (FIELD-CONFIRMED: the reset works).
- "I did a short battle test with wood elves, and I say the arrow of kurnois ability did not fire. I think it is because
  there was only trash melee. However, when no better target exists on the enemy side (visible or invisible), it should
  fire as it wouldn't be wasteful. Am I right?"

## 2. The label (BUILT)

The action's label is "Forget the remembered M/A choices" again. The page still sets no tooltip, so MCT draws no "?"
marker for the wrapped label to collide with. Harness 195: 8,083 checks / 0 failures, twice identical (MC6 new, MC4a
rebased from "one line of at most 15 characters" to the user's text). RED on the round-195 page. Build
`build_and_install196.py`, installed pack md5 **`9d1c2c8fc15aeb4a4a7181d4d88119ee`**, 1,615,586 bytes, 5 files, archived.
(A first builder made through a bash heredoc lost a line continuation and refused to build. The installed pack was
untouched. An archive copy of the unchanged pack under the round-196 name was removed. The maker is now written with the
Write tool.)

## 3. Why Arrow of Kurnous held (log bytes 933,407,000-946,588,829, `archive\logs\battle_20261121_r195_woodelves.txt`)

- The battle: Wood Elves (a Waystalker with Arrow of Kurnous, Sisters of Thorn, Waywatchers, Hawk Riders, Deepwood
  Scouts) against Vampire Counts: a Wight King and 7 units of Skeleton Warriors.
- Arrow of Kurnous rides enemy_blob (the area attacks that pick the enemy block where the blast destroys the most value).
  Its data: one arrow, 150 armour-piercing damage, a 4 m blast. The blob family keeps three "save it for a better target"
  rules:
  1. an armour-piercing-heavy attack never targets armour below 50 (`FOURTH.BLOB_AP_ARMOUR_MIN`, user ruling 2026-11-14),
  2. trash infantry (live value below 2 per soldier) only when the blast covers 3 packed blocks (round 153),
  3. only infantry blocks of 10 or more soldiers, or a large non-flying unit (round 151).
- Skeleton Warriors have armour 20 (the GENERATED UNIT_DEF table): rule 1 excluded all seven units for the whole battle.
  The Wight King is a single model: rule 3 excluded him. So Arrow of Kurnous had no legal target at any moment.
- Trash (rule 2) was NOT the first reason: at full strength the Skeletons were worth 325 for 160 soldiers (2.03 a
  soldier, just above the line). They fell below it only after losses. From t=68 s to t=128 s all seven were visible, out
  of melee and at full strength.

## 4. The user's idea (PROPOSED, waiting for a ruling)

The user is right in principle: the save-it rules only make sense while a better target exists or may still appear. If
no living enemy unit, visible or hidden, could ever pass them, holding the ability only wastes it.

- **A (the user's idea, recommended):** for each blob ability, the mod checks the whole living enemy army, visible and
  hidden. When no unit there passes this ability's save-it rules (rule 1 for the armour-piercing ones, rule 2), the
  ability takes the best visible target without them. Everything else stays: none of our units in the blast + 10 m, the
  caster standing when its cast is animated, the target visible and in range, the coverage minimum.
  Hidden enemies are only counted to decide "is something better out there", never targeted. That is a deliberate
  exception to the round-169 rule that every decision ignores an enemy we cannot see.
- **B:** as A, but only visible enemies count. It fires sooner, but it can spend the arrow on Skeletons just before a
  hidden armoured unit shows up.
- **C:** keep the rules as they are.

A side question: Arrow of Kurnous is one heavy arrow. Under A it would hit a Skeleton block, not the Wight King (rule 3
never takes a single model). Moving it to a single-target family (like Focused Shot's "most valuable single") would aim
it at lords and heroes instead. That is a trigger change for the user to decide.
