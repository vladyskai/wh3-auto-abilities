# Round 126 field test: the firing flag, read from the battle log

Battle log excerpt: `archive\logs\2026-11-03_round126_firing_battle.txt` (13,211 lines, md5
`fdfc4b1b2693c9b5b6434c291feab2c9`). Army: 40 Empire units, nearly every ranged type: hunters and
engineers, archers, crossbows, handgunners, Long Rifles, Ironsides, Outriders and Pistoliers, War
Wagons, every artillery piece, both Luminarks, Land Ships and Steam Tanks. 38 units fired. The battle
lasted about 151 s.

## 1. The reload table and the cast point

- Every unit that fired was found in the table: none was "not in the table".
- **Infantry and artillery:** one long firing episode each, and the cast point (first shot + half
  reload) fell well inside it, with the unit still shooting afterwards. Examples: Handgunners, cast
  +6.5 s, then 67 more drops; Crossbowmen, cast +6.5 s, then 20 drops; Mortar, cast +9.5 s, episode
  98 s long.
- **Some units fire SLOWER than their table reload,** against the expectation that in-battle reload
  is never slower than the base:

| Unit | Table reload | Real gap between shots |
|---|---:|---|
| Marienburg Land Ship | 10 s | 13.0 to 13.5 s (one gap of 25.75 s) |
| Land Ship (RoR) | 8.2 s | 13 s (one gap of 20 s) |
| Steam Tank | 10 s | 19.75 s |
| Witch Hunter | 4 s | 16 s, 8.25 s |
| Hertwig van Hal | 4 s | 19.75 s, 5.75 s |

  For these units, half the table reload is still before the next shot, so the cast point stays
  correct. But the OFF window (1.25 x table reload) is shorter than their real gap, so each shot
  becomes its own episode: 5 episodes for each Land Ship.

## 2. The OFF window, replayed on this battle's real shot times

Ideal: 38 episodes (one per unit that fired).

| OFF window | Total episodes | Units still split |
|---|---:|---|
| 1.25 x reload (round 126) | 64 | Land Ships 5 each, artillery, Steam Tanks, Long Rifles, Kalara |
| 2 x reload | 48 | Land Ships, Volley Gun tank, Huntsmen RoR, Ironsides, Ulrika, Hertwig, Witch Hunter |
| 2.5 x reload | 45 | 6 units |
| max(1.25 x reload, 20 s) | 45 | 6 units |
| **max(2 x reload, 20 s)** | **43** | Land Ship, Volley Gun tank, Huntsmen RoR (3), Ulrika |
| fixed 20 s / fixed 25 s | 46 / 45 | 7 / 6 units |

The splits that remain under max(2 x reload, 20 s) come from real pauses of 20 s or more.

## 3. Predicting the first shot from "target in range"

- **Necessary:** 37 of 38 first shots came after the target was already in range. The warning ran
  from 0.5 s to 34 s:
  - regular units: median 5.0 s, and 26 of 32 had at least 2 s;
  - characters: median 3.6 s.
- **Not sufficient:**
  - regular units: 28 of 69 in-range periods (41%) produced no shot;
  - characters: 52 of 62 (84%).

  Casting on "in range" alone would waste the ability that often.

## 4. A bug found in the log

When a unit's target disappears (dies, or no target is set), the OUT OF RANGE line formats a
distance and a range that are nil. The logging call raises inside the probe's pcall. As a result:

- the OUT line is never written;
- the probe skips the remaining units for that one poll (250 ms);
- `in_range` has already been set to false, so the next IN RANGE prints without an OUT before it.

Kalara shows 14 IN and 0 OUT. The harness only tested a target walking out of range, never one
disappearing. Fix: log "target lost" without numbers.
