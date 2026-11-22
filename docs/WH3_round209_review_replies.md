# Round 209: the replies to the afternoon code review (2026-11-22)

## 1. The rulings

The user answered the review's findings one by one.

| Finding | The user's reply | What happened |
|---|---|---|
| Spinning Loons, The Loons of Eight Peaks (no friendly test) | "I checked them in battle now. They are really prone for friendly fire. We need a friendly fire check, yes." | BUILT |
| The mod can cancel a cast the player just ordered | "Fixable?" | BUILT |
| Slow units can never be seen charging | "need more details" | Explained in the chat, a ruling is still needed |
| The five caster-front breaths and Lamprey's Bite | "fix please" | Lamprey's Bite BUILT. The five breaths NOT built: a hand test is needed first |
| The area blasts count walking enemies | "leave for now, we might improve on that later" | Left |
| Three machinery bugs | "fixable?" | One BUILT (one bad unit). Two explained, each has a cost |
| The button that arms everything also arms the risky abilities | "that's okay" | Closed |
| "At most 5 of our soldiers" is coarser than it reads | "I don't understand" | Explained in the chat |
| Chain Lightning's explosion | "leave it for now" | Left |

## 2. What changed in battle

1. **The Loons.** Before: they fired at the nearest enemy in melee within 17 m, whatever stood around. Now the same,
   and also none of our other units within 98 m of the Night Goblins. The 98 m is the fanatics' own numbers from the
   game's table: they are 4 m wide, travel 84 m in 12 s and turn at random, plus the usual 10 m. Da Boss' Loons has had
   the same rule since round 164. Our expendable and cheap units do not block it. In a normal battle line this is rarely
   true, so on A the Loons will mostly wait. The letter's hover text says so: "Fires at the nearest enemy in melee when
   none of our other units is near".
2. **Lamprey's Bite.** Before: the mod thought it was a 25 m disc and wanted 415 enemy soldiers inside it, so it almost
   never fired, and when it did the order pointed north. In the game's table it is a short wave: 0.1 m wide at its
   start, growing while it rolls 24 m, 14.1 m wide at the end. Now it is aimed like the Fiery Ring of Thori: the mod
   tries 24 directions and 7 sideways shifts per standing enemy and orders the path with the most enemy soldiers under
   it, with at most 5 of ours.
3. **Your own cast.** The game tells the mod about every ability order, with the ability's key. The mod now remembers
   the orders it gave itself. An order it did not give is yours. Every unit you have selected then stops receiving
   automatic abilities until your cast is out: its wind-up plus 2 s when the mod knows the ability, 5 s when it does not
   (a spell), nothing when it is one of the mod's instant abilities.
4. **One broken unit.** Before: if reading one unit raised an error, every unit after it in the list was skipped for
   that quarter second. Now each unit is read inside its own guard.

## 3. Proof

- RED control (the pre-round snapshot, `docs\backups\round209\`): LN1 and LN3 fire with one of our units 50 m away.
  LB1 never fires on 160 standing Zombies. PC1 and PC5 fire at once after the player's own cast. UE1: no cast after the
  first unit's error.
- GREEN: harness 207, full suite, 8,412 checks, 0 failures (`mod_source\releases\20261122_replies_harness207\h207_run1.txt`).
- The cast trace of the whole suite: 2,155 worlds, 1,702 casts, the test build and the release build differ only in the
  3 casts of the console probe (expected).
- Test pack md5 `c7835b1a8ef6c3e61dc750f588673aed` (1,649,264 bytes), release pack md5 `3457ac1b985901ba088c56eade838a8e`. Workbook v83.

## 4. Rebased pins (old value, new value, why)

| Where | Old | New | Why |
|---|---|---|---|
| harness 114, "the per-ability walk still BREAKS on 'gone'" | the word `break` within 80 characters of the answer | `return "gone"` there, and the caller's `break` after the guard | each ability step runs in a guard, the break moved one line out |
| harness 160 (0zz9) | 32 waves, 42 wanderers | 33, 41 | Lamprey's Bite moved |
| harness 161 (0zz10) | 42 wanderers | 41 | the same |
| harness 162 (0zz11) | 32 waves, 42 wanderers | 33, 41 | the same |
| harness 202 (0zz50) | 32 waves | 33 | the same |
| builder, round 162 gate | 32 / 42 | 33 / 41 | the same |
| builder, round 203 gate | every enemy_wave key target_near_edge, 32 entries | also target_centre for a ground-only key, 33 entries | Lamprey's Bite launches from the target centre and has only the ground form |
| builder, round 204 gate | 27 exact waves | 28 | Lamprey's Bite |
| builder, round 205 gate | 19 growing waves | 20 | Lamprey's Bite |
| builder, round 198 gate | 5 uses of the waiting slot | 6 | the player's-cast window clears it too |

## 5. What is not verified

- Nothing of this round has been seen in a battle.
- Lamprey's Bite: that a ground order starts the wave at the point and sends it along the bearing is seen in game for
  the Fiery Ring of Thori only.
- The player's own cast: the three archived battles show the game's report arriving for the mod's own orders, a moment
  after each. That it also arrives for a hand cast and for a spell is the game's own documentation, not yet a log line
  of ours. The next battle's log shows it: the line "the player's own cast of".
- The 5 s for an unknown key is Claude's number. 37 abilities in the game wind up longer than 5 s.
- When several units are selected and one casts, all of them wait.

## 6. Still waiting

- The five caster-front breaths (Shatter, Pestilent Breath x2, Fishy Breath, Skabscrath): a hand test of where the
  breath starts.
- Slow units and the charge test: a ruling.
- Phantom casts after the last use, and the transformed unit: the user's go-ahead, each has a cost (see the chat).
