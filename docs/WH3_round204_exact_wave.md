# Round 204: an exact wave needs no safety distance (2026-11-22)

## 1. What the user saw

The Master Engineer with two Miners units against three Skeleton Warriors units. Both Miners units in melee, "plenty of
targets here, still not firing". The log has no `FREE AIM` line: round 203 never found a path.

## 2. The cause (Claude's flaw in round 203)

Round 203 tested 24 headings, but every path ran through the centre of the enemy unit. An enemy in melee with ours has its
centre 6 to 10 m from our unit, and the rule asked for 16 m. Replay of the map snapshots (`tools\replay_free_aim.py`):

| Path placement | Margin | Skeleton battle | Zombie battle |
|---|---|---|---|
| through the centre (round 203) | 10 m | 0 of 21 clear | 0 of 25 clear |
| moved sideways up to 20 m | 10 m | 21 of 21 | 25 of 25 |
| moved sideways | 0 m | 21 of 21, median 268 soldiers | 25 of 25, median 388 soldiers |

Claude had said round 203 would fire in the Zombie battle. It would not have. The harness world put the friend 30 m in
front of the enemy instead of in melee with it.

## 3. The ruling (user, 2026-11-22)

"I think the safety makes no sense for this ability. Look, the safety was meant for abilities. That have a deviation from
their path. But this ability's path is deterministic. You know exactly where it's going to land. So why do we need a
safety check? We only need to know that in the path of the ability, there is very little of our units. Or should I say
very little of our soldiers. And in this case, we should ignore single entities because the damage to our single entities
would be not relevant. Also, please implement for tight call and wind blast. The slow effect is irrelevant in this case."

## 4. The change

**Exact waves.** A wave whose generated table row has no sideways drift is exact: 27 of the 32 keys on the wave trigger.

| | Round 203 | Round 204 |
|---|---|---|
| Friendly test | none of ours within radius + 10 m of the path | at most 5 of our SOLDIERS under the wave |
| Our single entities (Lords, Heroes, monsters) | block the path | not counted |
| The caster | never blocks | never counted |
| Value of a path | the whole value of every unit it touches | the enemy value under the wave |
| Paths per enemy | 24 headings through the centre | 24 headings x 7 sideways positions (0, 6, 12, 18 m either side) |
| The order | unit form on the caster's line, ground form otherwise | always the aimed ground form |
| How often | every poll (0.25 s) | once per second per caster and ability |

"Under the wave" means inside the wave's own radius along the path. The count spreads a unit's soldiers over its
rectangle (frontage from the game, depth estimated from men and spacing).

**The 5 drifting waves** (Wrath of Manann, Wind of Death, The Burning Head x2, Arnzipal's Black Horror) keep the
round-162 safety distance and round 203's aim. The user's reason for dropping the distance does not apply to them.

**Tidecall and Wind Blast** leave the charge trigger (round 164: "Charge, clear path") and ride the wave trigger: a
standing enemy in range, the path with the most enemy value. Both are exact waves. The charge-wave family is empty now
(its code stays).

**Claude's own choice, flagged:** the limit of 5 soldiers is a reading of "very little". It is one named constant
(`FOURTH.WAVE_OWN_MAX`).

**Not built:** a minimum of enemy soldiers under the wave. Claude proposed 60, the user did not rule on it. A wave can
therefore fire at a single Lord or at the corner of a unit when that is the best path there is.

Code: `FOURTH.ww_exact`, `FOURTH.wave_cover`, `FOURTH.ww_line_value` (the exact branch), `FOURTH.ww_aim_value` (the
shift), `FOURTH.FREE_AIM_SHIFTS`, `FOURTH.WAVE_OWN_MAX`, `FOURTH.FREE_AIM_EVERY`, `FOURTH.aim_next`.

## 5. Proof

- RED control on the round-203 source (`h202_red.txt`): no order in the melee world, no order with one of our Heroes
  inside the enemy, no Tidecall on a standing enemy.
- GREEN, harness 202, full suite: **8,305 checks / 0 failures** (`h202_run1.txt`).
  - EX1 the user's battle (Miners and Skeletons overlapping): ONE aimed order, 0 of our soldiers and 75 Skeletons under
    the wave, start 66 m from the caster.
  - EX2 one of our Heroes inside the Zombies: ONE order.
  - EX3 Tidecall on a standing enemy: ONE order.
  - EX4 Wind of Death (drifting) in the same melee: no order.
  - EX5 nothing in the way: ONE aimed order under 136 of 160 Zombies.
  - EX6 no vector constructor: no order. EX7 a walking enemy: no order.
- Rebased pins (harness 202): the wave family 30 -> 32, the charge family 2 -> 0, harness 163's two Wind Blast worlds
  swapped (a moving enemy: no cast, a standing one: one cast). `run_h201` stays in the file and is no longer called: its
  worlds pinned the through-the-centre paths this round replaces.
- A standing pin caught a joined text key (`.. "|" ..`) in the first version of the throttle. It is a nested table now.
- Installed test pack: md5 `11a01a69e4c513e1c4d444dab5f7606a`, 1,639,185 bytes. Release pack: md5
  `3a39d70d276b71d094850452be15457f`. Cast trace of the whole suite: the release differs from the test build in exactly
  the 3 probe casts it removes (2,109 worlds, 1,670 casts).
- Workbook v81 verified (13 checks). Database, audits and progress page regenerated.

## 6. Skipped, stated plainly

- The full suite ran once on the final source, not twice.

## 7. Not verified

- Nothing of this round has been seen in a battle.
- The wave's real width against the table radius. With no margin, a wave wider than its table radius burns our front rank.
- Units move during the 1 s cast and the 3 s travel. The count is taken at the moment of the order.
- The depth of a unit is an estimate, so "under the wave" is too.
- The 31 other keys in an aimed ground order (only the Fiery Ring of Thori was probed).
- The cost of 168 paths per enemy once per second in a large battle.
