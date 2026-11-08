# Round 127 field test: the battle log read

Battle log excerpt: `archive\logs\2026-11-03_round127_battle.txt` (44,381 lines, md5
`0f0045abad6abd519f99713ca5b5cd0c`), about 580 s of battle, the same 40-unit Empire army as round 126.

## 1. Isha's Rain (Kalara of Wydrioth) - the user's report: "for a very long time not firing,
especially the third charge"

Game data: 3 uses, 120 s recharge, 3 s wind-up. The mod casts it on the `enemy_ground_melee_infantry`
trigger, and after each cast its charge gate holds the next attempt for the ability's own 120 s
recharge.

Timeline (probe clock, seconds; button states are logged only while Kalara is selected):

| t | Event |
|---|---|
| 55 | the user arms Isha's Rain on Kalara |
| 154.5 | cast 1: accepted, and took effect (button in cooldown, `inactive`, at 210) |
| 274.25 | cast 2: accepted |
| about 394.5 | cast 3: accepted, but **did not take effect** |
| 426 to 496 | Kalara selected: the button reads `active` (ready), 32 to 100 s after cast 3 |
| 514.5 | cast 4: accepted, took effect (button `selected_inactive`, then `inactive`) |

Two facts show that cast 3 was dropped by the game. A cast that worked locks the button for 120 s,
but this one showed ready 32 s later. And the mod "cast" 4 times an ability that has only 3 uses.
The order was accepted (`perform_special_ability ... ACCEPTED`) and never executed. The mod had no
way to see it: `can_perform_special_ability` stays true the whole time for a multi-use ability (a
known engine quirk; 1,674 readiness reads, all true). So the mod kept its 120 s hold, and a ready
Isha's Rain sat unused for about 90 s. The log does not show why the game dropped the order (Kalara
was in melee with the target; the same shape worked for cast 4).

The battle API has no cooldown or charges read. The only signal is the ability button's own state,
and it exists only for the SELECTED unit.

## 2. The firing flag

- 85 FIRING ON, 85 CAST POINT, 77 FIRING OFF (34 on 2 x reload, 43 on the 20 s minimum).
- The units still showing several episodes had real pauses between shots: Steam Tank 26 to 71 s,
  Mortar 16 to 65 s, Ironsides of Morr 23 to 145 s, Crossbowmen 33 and 154 s.
- Borderline: the Helblaster Volley Gun (table 10 s) had gaps of 19.5 to 25.5 s, just past its 20 s
  window, so it split into 4 episodes. Its real cycle looks slower than its table reload, like the
  Land Ships and Steam Tanks.

## 3. The target-lost fix

86 "target lost" lines, and no unit has more IN RANGE than OUT OF RANGE lines: the fix works.

## 4. Errors

None: no step error, no raised ui tick, no load error in the whole battle.
