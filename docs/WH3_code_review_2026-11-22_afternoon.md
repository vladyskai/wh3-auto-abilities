# Code review, afternoon of 2026-11-22

Request (user): "do another check of the code, maybe there are more bugs like the one we found. And check if anything
else can be improved", then "check in general, not only the wave abilities".

## 0. How it was done

Six read-only reviewers read the mod in parallel, each with one question, and none edited anything:

1. every ground-form order that still sends direction 0
2. every effect whose real shape differs from the one number the mod uses
3. every trigger that counts or targets units which will have moved when the effect lands
4. the wave code written today (rounds 203 to 206)
5. the core machinery (poll, cast gates, holds, selection, remembered choices)
6. the shared target pickers of the other trigger families

VERIFIED below means Claude re-checked the finding against the source or the game's tables. The rest is a reviewer's
reading that still needs that check. ASSUMPTION marks anything about how the game behaves that is not a table value.

Measured separately: the free-aim search costs 11 to 13 ms per search in the test harness (a 20 against 20 mock battle,
few enemies inside the cast range), once per second per armed wave caster. The game's Lua is slower than the harness's,
by a factor that is not known.

## 1. Fixed today (round 207, inside rulings that already exist)

| # | Defect | Fix |
|---|---|---|
| F1 | The 5 drifting waves (Wrath of Manann, Wind of Death, The Burning Head x2, Arnzipal's Black Horror) still counted WALKING enemies when choosing a path. Round 206 had fixed only the exact waves. They take 3 to 5 s to cast and then roll slowly. | A wave's path value counts standing enemies only. |
| F2 | Blue Fire of Chaos (ground-only) could fall back to the old order, the enemy's centre with direction 0 (north), when the caster's position was unreadable or the enemy stood on the caster. | It holds. |

Proof: harness 205, 8,350 checks, 0 failures (once). The old build reproduces F1. Test pack md5
`346e1448d5de45e57c805a81dde8436f`, release pack rebuilt.

## 2. Findings that need a ruling, ranked

### A. Can hurt our own units

| # | Ability | What is wrong | Evidence |
|---|---|---|---|
| A1 | **Spinning Loons, The Loons of Eight Peaks** (Night Goblin Fanatics) | They fire at the closest enemy in melee within 17 m with NO friendly test at all, and the order is a ground order with direction 0. The game releases 4 fanatics that travel 84 m, turn at random and hit allies. Da Boss' Loons, the same vortex, holds unless our units are 98 m clear (round 164). | VERIFIED in the tables: launch_source activator_front, 4 vortexes, 7 m/s for 12 s, change_max_angle 30, affects_allies true. Which way they leave under direction 0 is an ASSUMPTION (north, by the Blue Fire probe). |
| A2 | **Chain Lightning** (the two dlc27 keys) | Treated as a direct effect with no friendly distance. Its projectile explodes with a 12 m radius that the game marks as hitting allies. Cast on a block fighting ours, it touches ours. | VERIFIED: explosion radius 12, affects_allies true, can_damage_allies true. The explosion damage is small (5). |
| A3 | **Splode da Big 'Un!, Glacial Blast, Thundermace, Groundbreaker, Land Mine** (self-centred blasts) | The "none of ours near" test is made at the order. The blast comes 3 to 7 s later (Splode: 6.8 s delay, 30 m). The caster is in melee, where our units converge. | Table delays. Not seen in a battle. |
| A4 | **Ancient Chaos Frost Dragon Scale** | Modelled as a 7 m disc that stays put, friends clear to 17 m. It wanders at 1 m/s for 24 s. The mod's own drift simulator gives 17 m, so its reach is about 24 m. | Table values plus the mod's simulator. |

### B. Fires at the wrong place or holds for the wrong reason

| # | Ability | What is wrong | Evidence |
|---|---|---|---|
| B1 | **The 5 caster-front breaths** (Shatter, Pestilent Breath x2, Fishy Breath, Skabscrath) | The same mistake as Sunfang. They start 0.1 m wide at the caster and grow. The mod treats them as their full width (12, 16 or 6 m) from the caster on, and as 72 to 108 m long. At the 21 m cast bound a 12 m breath is about 5 m wide. So it fires at enemies the fire does not reach, and holds for friends 50 to 100 m ahead that it cannot reach. | Table values. Where the breath starts relative to the caster (the 24 m offset) is an ASSUMPTION under every reading, and all three readings disagree with the mod. |
| B2 | **Lamprey's Bite** | Modelled as a 25 m disc on the target. In the tables it is a short straight wave like Blue Fire (0.1 m growing 14 m/s for 1 s while moving 24 m), it never reaches 25 m, and it is ordered with direction 0. The 25 m figure makes it need 415 soldiers in the disc, so it almost never fires. | VERIFIED: start 0.1, goal 25, expansion 14, duration 1, speed 24, ground-only. |
| B3 | **enemy_wander** (42 abilities: Pit of Shades, Blight Boil, The Dwellers Below, Magma Storm, the Banishments) | The target must stand, but the blast's value counts every block around it, walking or not. These take 5 to 11 s to land (Blight Boil 5 + 6 s). | VERIFIED in the code: blob_score and blob_value have no standing test. Delays are table values. |
| B4 | **enemy_blob** (68 abilities: breaths, bombs, Fireball) | No standing test at all, on the target or its neighbours. Wind-up plus flight is 1.3 to 10 s (median 3.4 s). | VERIFIED in the code. ASSUMPTION: a unit-form projectile is aimed where the unit is at launch. If the game leads the target, this matters less. |
| B5 | **Hell Hammer** | Modelled as a 14.1 m band along 60 m. The travelling wave is 5 m wide. The 14 m is one explosion. Enemy value and our soldiers are both over-counted. | Table values. ASSUMPTION: the explosion lands at one point. |
| B6 | **An exact wave counts fliers** | The value counts every standing enemy under the wave, flying ones too, even for abilities the game forbids on flying targets (Seafang). | Reviewer's reading of the code. |
| B7 | **Flesh-eating Scarabs, Irresistible Plague!** | Scarabs: the clear ring around the caster is 46 m, the real reach about 33 m, so it rarely fires. Plague: counted at 14 m, which it reaches only after 11 of 20 s. | Table values. |

### C. Core machinery

| # | What | Situation | Evidence |
|---|---|---|---|
| C1 | **The mod can cancel a cast YOU just ordered.** The "one cast at a time per unit" window is armed only by the mod's own casts. | You order a 3 s spell on a Lord in melee. A quarter second later one of his armed abilities becomes true and the mod orders it. By the known engine fact, the second order replaces the first. | VERIFIED in the code: the game's "Special Ability" command callback exists but only writes a log line. Not seen in a battle. |
| C2 | **A transformed unit's new abilities never fire.** The re-scan of a unit's abilities runs only for units that own none of ours, a condition from when the mod had 3 abilities. | A unit changes form mid-battle. The new buttons get letters and can be armed, and nothing fires. | VERIFIED: the condition is still `ability_key == nil`. Whether a transformed unit keeps its id is not known. |
| C3 | **Phantom casts after the last use.** The mod spaces multi-use casts but never counts them, and the game accepts a cast on an empty pool. | After the last real use the mod sends one empty order per recharge period for the rest of the battle. Each blocks the unit's other abilities for a moment. | VERIFIED: no use counter exists. Three archived battles show none, so it rests on the code and one documented case. |
| C4 | **One bad read stops the rest of the army for that poll.** Known from the overnight review, still present. | A unit handle that raises an error. Every unit after it in the list is skipped. | VERIFIED: the poll is one guarded body, not one guard per unit. |
| C5 | **The search runs while the ability recharges.** | A wave caster on A runs the path search once per second for the whole battle, also during its 60 to 120 s recharge and with no uses left. | Reviewer's reading, consistent with the 11 to 13 ms measurement. |
| C6 | **The ALL button arms the risky abilities and remembers them.** | One ALL click, and a rampage or self-damage ability starts on A in every later battle. | Reviewer's reading. |
| C7 | **Ghost selection while paused.** The veto that removes units the game forgot to deselect counts battle time, which stops during a pause. | Pause, box-select seven units, click one, click a letter: it can flip all seven. | Reviewer's reading. |
| C8 | Small: the retry after a cooldown refusal can run every quarter second. The air-drop fast pass walks every unit five times a second even when nobody owns an air drop. | Wasted work, no wrong cast. | Reviewer's reading. |

### D. Precision of today's wave rule

- **"At most 5 of our soldiers" is coarser than it reads.** The count uses a grid of points over each unit. In a 120-man
  unit one point stands for 6 soldiers, so a single point under the wave already blocks the path. In a 60-man unit one
  point passes. The thin start of a cone can also slip between two columns of points and count nothing.
- **All armed wave casters search on the same poll.** Four casters cost four searches in one frame. Spreading them over
  the four polls of a second costs nothing.

## 3. What the reviewers checked and found sound

- The sideways shift, the bearing, the 24 headings and the cone formula of the wave code have the right signs.
- No stale state leaks between abilities in the wave code. The per-entry reset covers every cast slot.
- No table grows without limit over a long battle.
- The release build still removes every test switch and console command, and free aim stays on in it.
- The 19 growing waves, the instant blasts, the pits, the Banishments, the self-centred blast radii and all 68 projectile
  explosion radii match the game's tables.
- No shrinking vortex exists among the mod's abilities.
- The remembered M/A choice behaves as ruled in round 199.

## 4. Open questions that only a battle answers

- Does a ground order start the Loons and the caster-front breaths at the given point, as it does for the placed waves?
- Does the game lead a moving target with a projectile or a bombardment?
- Does `is_moving()` read false for a unit shuffling inside a melee?
- Does a transformed unit keep its id?
- What does the game answer when an aimed point lies outside the map?

## 5. Claude's recommendation on the order of work

1. A1, the Loons. It is the only finding where the mod orders friendly fire with no check at all. The simplest fix is the
   rule Da Boss' Loons already has.
2. C1, the player's own cast. It is the finding most likely to be felt as "the mod ruined my spell". It needs one probe
   first: whether the game's command callback also fires for the mod's own orders.
3. B1 and B2, the breaths and Lamprey's Bite: the Sunfang fix applied to the remaining cones. It needs a probe of where a
   caster-front breath starts.
4. B3 and B4, standing enemies only for the area blasts. One small change, but it will make them fire later and less
   often, so it is a trigger decision.
5. C2, C3, C4: three contained fixes in the machinery.
6. C5 and the two points in D: speed and precision.
