# Round 125 field test: the ammo probe, read from the battle log

Battle log excerpt: `archive\logs\2026-11-03_round125_ammo_probe_battle.txt` (10,788 lines, the
last battle in the live log, from line 1,192,150). Army: Arch Lector, Warrior Priest, 2
Crossbowmen, 2 Handgunners, Mortar, Helstorm Rocket Battery, against Vampire Counts.

## 1. `ammo_left()` works

It drops shot by shot during the battle: 501 AMMO lines, every shooting unit reported, no
resupply in this battle.

| Unit | Starting ammo | Drops logged | Ammo spent | Ammo per drop (most common) |
|---|---:|---:|---:|---|
| Crossbowmen 1003 | 1,980 | 119 | 524 | 1, 2, 3 |
| Crossbowmen 1004 | 1,980 | 79 | 347 | 2, 1, 3 |
| Handgunners 1005 | 1,980 | 118 | 468 | 1, 2, 3 |
| Handgunners 1006 | 1,980 | 93 | 441 | 6, 5, 1 |
| Mortar 1007 | 88 | 13 | 22 | 1, 2, 4 |
| Helstorm 1008 | 264 | 79 | 142 | 1, 2, 3 |

Infantry ammo is counted per model (1,980 = models x shots each), so a volley shows up as a
trickle of small drops over several polls as the models fire one after another.

## 2. The window rule fails on real units

The round-125 rule (window = 1.25 x the most recent gap of 1 s or more, 10 s default) flickers:

- **Infantry:** the models' staggered shots give gaps of 1.0 to 1.5 s, so the window shrank to
  1.25 to 1.9 s and the flag fell OFF mid-fight. Crossbowmen 1003: 7 OFFs, most followed by ON
  again within 0.25 to 3.5 s.
- **Mortar:** reload about 10.5 s, just longer than the 10 s default, so no gap was ever measured
  and the flag went OFF before every shot: 10 ON/OFF cycles.
- **Helstorm:** fires in bursts, about 1.25 s between rockets and about 11 s between bursts. It
  measured the in-burst gap, so the window shrank to 1.56 s: 23 ON/OFF cycles.

## 3. The same drops replayed against candidate rules

Each cell is the number of separate firing episodes, and how long after the last shot the flag
fell OFF.

| Rule | Helstorm | Mortar | Crossb. 1003 | Crossb. 1004 | Handg. 1005 | Handg. 1006 |
|---|---|---|---|---|---|---|
| round 125 (1.25 x last gap, 10 s default) | 23, +2.0 s | 10, +1.5 s | 8, +2.0 s | 5, +2.2 s | 5, +2.0 s | 3, +2.0 s |
| fixed 10 s | 10, +10.2 s | 8, +10.2 s | 1 | 3 | 1 | 1 |
| fixed 12 s | 3, +12.2 s | 4, +12.2 s | 1 | 3 | 1 | 1 |
| fixed 15 s | 2, +15.2 s | 4, +15.2 s | 1 | 2 | 1 | 1 |
| 1.25 x longest gap up to 20 s, 12 s minimum | 2, +22.2 s | 4, +20.8 s | 1, +12.2 s | 2, +20.5 s | 1, +12.2 s | 1, +12.2 s |

The mortar's remaining episodes come from real pauses of 16 to 21 s in its fire. Crossbowmen
1004 had pauses of 12.5 and 16.25 s.

## 4. Other findings

- `target_in_melee=true` appeared on 11 drops (Crossbowmen 1003: 5, Handgunners 1005: 5,
  Handgunners 1006: 1), so "shooting at an enemy in melee" is visible in the data.
- The spell-bar rule was not exercised: no unit in this battle had anything on the right-hand bar.
