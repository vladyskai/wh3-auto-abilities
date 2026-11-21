# Round 198: the overnight review's fixes (2026-11-22)

## 1. The rulings

User, 2026-11-22, replying row by row to the overnight review (`docs\WH3_overnight_review_2026-11-22.md`):

| Review row | Reply | This round |
|---|---|---|
| 1 the "one ability at a time" window | "fix" | BUILT |
| 2 the air-drop fast timer | "fix" | BUILT |
| 3 Get Tha Gitz! | "fix" | BUILT |
| 4 Heaven's Flash | "I tested it and it fired correctly. Not sure what's wrong with it." | WITHDRAWN (the finding was wrong, section 5) |
| 5 Doom & Darkness (gunnery school) | "I don't see this ability on the Amethyst Land Ship. Only 'Full Power!'" | not touched, answered in chat |
| 6 the Necromancer on a Nightmare | "fix" | BUILT |
| 7 the slow aura and the guard aura | "fix" | BUILT |
| 8 Favour of the Fay, Shielding Swarm x2 | "fix", and "the game will refuse the cast, but still need fixing" | BUILT |
| 9 the "cast on self for now" abilities | "need more details" | details given in chat, waiting |
| 10 the bombardments' infantry test | "need more details" | details given in chat, waiting |
| 11 Bugman's XXXXXX | "fix" | BUILT |
| 12 one click changes the whole unit type | "I'm unsure on how to fix it and preserve the functionality of the A/M state between battles." | options given in chat, waiting |

## 2. The change (`tools\round198_patch.py`, both copies)

1. **The serial window.** After a cast, no OTHER ability of that unit may be ordered until the window closes (wind-up +
   2 s). The window was only set when the ability differed from the last one that set it, and that memory was never
   cleared. So a second cast of the SAME ability set no window, and another ability could replace it mid wind-up. Now a
   window that has closed forgets who armed it, so the repeat arms it again. NO STARVING: found by the round's own test.
   An ability that repeats exactly when its window closes would lock the unit's other abilities out for good, so the
   ability that armed the last window yields one poll when another ability waited through it
   (`cast_gate.unit_waiting`).
2. **The entry reset.** The poll cleared about 40 "chosen target" slots before each ability. The air-drop fast timer
   (every 0.2 s) cleared only its own 6 and inherited whatever the last ability of the last poll had chosen. The block is
   now ONE function, `FOURTH.entry_reset(ability, unit)`, called by the poll and by the fast pass.
3. **Get Tha Gitz!** (3 uses): its charge-hold row (120 s). It was the one multi-use entry without one.
4. **The Necromancer (Undeath) on a Nightmare.** The Lord/Hero list had the main_units key
   (`..._undeath_barded_nightmare`). The land_units key (`..._undeath_nightmare`) is added. The old row stays: which of
   the two `type()` answers for this unit is not proven, and a spare row costs nothing.
5. **slow_aura and guard_aura** (The Rock of Inevitability, The Wissenland Runefang, Seismic Snare x2, Shield of Aeons,
   The Armour of Morkar): their "fast enemy" arm had its own copy of the pre-192 read (any fast-type enemy that is
   moving). It now calls `FOURTH.fast_enemy_near` (RUNNING and CLOSING on our units, round 192), then tests the aura.
6. **No self arm** for Favour of the Fay and Shielding Swarm x2 (the game's `target_self` is false): entry field
   `no_self = true`, read through `FOURTH.ab_no_self`. Their card (`FOURTH.CARD_TIP_NOSELF`) says "Fires on the nearest
   ally in melee" and "Fires on an ally under fire, else on an ally in melee". Terrorgheist Skull and Shield of Thorns
   (target_self true) keep the self arm.
7. **Bugman's XXXXXX**: `FOURTH.BUGMAN_CLEAR_M` 38 -> 55. It is a keep-out distance (the game refuses the cast with an
   enemy inside its 55 m range), so the 70% cut pointed the wrong way.

## 3. What changes in battle

- A hero who casts a wind-up ability twice in a row no longer has it replaced by his next ability.
- A Gyrocopter, Sky-junk or other bomb carrier no longer skips a drop (or aims it at another unit's target) because
  another unit's ability had picked a target a moment earlier.
- Get Tha Gitz! goes out once per 120 s, not three times in 15 s.
- The slow and guard auras wait for an enemy that is really running at us. Cavalry walking past no longer spends them.
- Favour of the Fay and Shielding Swarm go to an ally, never to the caster.
- Bugman's XXXXXX waits until no visible enemy is within 55 m.

## 4. Proof

- Harness 197: **8,161 checks / 0 failures**, twice, byte-identical (8,104 old + 57 new). New section 0zz44 (tokens),
  SW1 (the window), FP1 (the fast pass), GG1 (Get Tha Gitz!), SL1-SL3 (The Rock), GA1-GA2 (Shield of Aeons), NS1-NS5
  (no self arm and the cards), BG3 (Bugman's at 45 m).
- RED (`h197_red.txt`, the section on the pre-198 snapshot, every RED expectation met): the Eye is issued 1 poll after
  the Roar's second cast, the fast pass holds the bomb, Get Tha Gitz! casts 4 times in 20 s, the auras fire on a walking
  or passing enemy, Favour and the Swarm cast on the caster, Bugman's casts at 45 m.
- FOUR pins rebased in harness 197 (old harnesses untouched):

  | Pin | Old | New | Why |
  |---|---|---|---|
  | 0zz (harness 103) | 347 charge-gate rows | 348 | Get Tha Gitz!'s row |
  | 0zz12 (harness 164) | the `ab_atarget` line with 5 tabs | 1 tab | the block moved into `FOURTH.entry_reset` |
  | 0zz28 (harness 179) | `FOURTH.BUGMAN_CLEAR_M = 38` | `= 55` | the ruling |
  | 0zz37 (harness 188) | the `eg_caster` / `eg_los` lines with 5 tabs | 1 tab | the block moved |

  Before the rebase the old harness 196 failed exactly these 8 checks (4 pins x 2 files) on the new source and no world.
- Build `build_and_install198.py`. ROUND 198 GATE: one entry reset called by both timers, the re-armed window, every
  multi-use entry holds a row (checked against the game table), `no_self` equals the game's `target_self` on the two
  families (checked against the game table), the two auras on the round-192 read, Bugman's 55 m. NEW: the script must
  compile on Lua 5.1, the game's Lua (lupa's default is 5.5). Rebased: the round-180 Bugman gate and the round-189 gate's
  two 5-tab lines.
- Installed pack md5 **`b5f1ce36cfc8a12a50f7f6ff5fab5ba7`**, 1,622,076 bytes, 5 x `MATCHES SOURCE: True`, archived.
- Workbook **v77** (`verify_xlsx_v77.py` OK): 10 trigger texts and 3 cards restated. No roster change.

Not seen in game yet. Next battle from log byte 978,682,624.

## 5. The withdrawn finding (Heaven's Flash)

The review said a ground-only key (`target_ground` true, `target_enemies` false) cast in unit form would land nowhere.
The user's test battle (log bytes 957,838,791 to 978,682,624) shows 4 casts of `wh3_main_unit_abilities_stun_bomb` at
Skeleton Warriors in melee, each fired. ENGINE FACT: a ground-only key ordered at an enemy UNIT is placed on that unit.
The round-184 note ("a ground-only key MUST join enemy_ground_keys") overstated it.
