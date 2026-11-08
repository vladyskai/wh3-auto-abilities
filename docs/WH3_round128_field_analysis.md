# Round 128 field test: the battle log read

Battle log excerpt: `archive\logs\2026-11-03_round128_battles.txt` (59,297 lines, md5
`2efdd011a2a5e9f5adc97e7cdd999a4e`). It holds three battles on the round-128 build: battle 1 (about
305 s), battle 2 (about 100 s) and battle 3 (about 305 s, the one the user reported). Every line was
read by two scripts, `tools\field_isha_timeline_128.py` and `tools\field_recharge_128.py`.

## 1. Isha's Rain in battle 3 (the user's report: "the second use was not firing for a very long time")

Probe clock, seconds. Button states are seen only while Kalara's card is shown.

| t | Event |
|---|---|
| 55.75 | cast 1, took effect (button busy until 138) |
| 139 | the button reads READY: the real recharge is about 83 s, not the table's 120 s |
| 139 to 175 | Kalara selected, button READY, but fix A did **not** release the hold (cause 2 below) |
| 175.75 | cast 2, when the 120 s hold ran out. The game **dropped it**: the button went back to READY 2.25 s later |
| 178 to 295 | the button reads READY for about 117 s, Kalara selected most of the time, still no release |
| 295.75 | cast 3, when the next 120 s hold ran out. Took effect |

About 155 s of a ready Isha's Rain went unused in this battle.

## 2. The three causes

1. **The real recharge is shorter than the table.** The table says 120 s for Isha's Rain and Pigeon
   Bomb. In battle both buttons were READY after about 83 to 85 s (Isha's Rain 82.25 to 83.25 s,
   twice; Pigeon Bomb 81.25 to 85.25 s). Something in the campaign (a skill, an item or a
   technology) shortens recharges by about 30%. The battle API cannot read it, so the mod's hold
   is about 37 s too long on every cast.
2. **Fix A was blocked by two ghost selections.** At 55 s the user box-selected seven characters
   (1001 to 1007), then clicked Kalara alone. The engine's selection callback never sent the
   "deselected" events for the other six. Four of them dropped out later, when each was clicked
   and deselected on its own. The Witch Hunter (1006) and Ulrika (1007) were never clicked again,
   so the mod's live selection list read "1003, 1006, 1007" for the rest of the battle. Fix A
   requires exactly one selected unit, so it refused. The unit cards told the truth the whole
   time: 1006 and 1007 read `active` (not selected), and only Kalara's card read `selected`.
   The same ghost list also means a badge click would have flipped the ability on 1006 and 1007
   as well, had they owned it.
3. **The game drops some casts.** Cast 2 was accepted and issued, and was cancelled within 2 s.
   This is the second drop seen (round 127 had one). The log does not show why. The round-127 drop
   happened with no click at all, so a click is not the cause.

## 3. Fix A where it could work: battle 1

Battle 1 had no ghost selections. Fix A released the hold twice, and both releases were right: the
button read READY 82.75 s and 103.75 s after the previous cast, and both recasts took effect.

## 4. The NOT FIRING snapshot

1,202 lines across the three battles:

| Count | What the snapshot showed |
|---:|---|
| 542 | the unit or its target in melee |
| 301 | every readable reason clear (target in range, nobody in melee, fire at will on): line of sight, or the normal gap between shots |
| 207 | no target |
| 144 | wavering or routing |
| 8 | target out of range |

## 5. Errors

None: no step error, no raised ui tick, no load error in the three battles.
