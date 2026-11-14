# Round 148: the memreader probe (optional, read-only), 2026-11-14

## Ruling

User, 2026-11-14: "Approved, build round 148" (the plan: an optional, read-only probe that reads three engine
fields through memreader Plus on the existing map rows; no trigger uses them; the user enables memreader Plus
himself).

## The change

The map probe's row gains ` mr_lead=<n> mr_hp=<n> mr_men=<n>` after `sv=` (the `routing= ... addr=` end of the row
is unchanged). With memreader Plus (`_G.memreader_plus`) present, per unit:

| Field | Read | Found in |
|---|---|---|
| `mr_lead` | `read_int32(read_pointer(ud_topointer(u), 0x8), 0x3B78)`: current leadership, signed | round 147 (public CE table, checked 4 x) |
| `mr_hp` | `read_int32(read_pointer(<unit>, 0x280), 0x5CC)`: current hit points | round 147 (exact on 4 card readings) |
| `mr_men` | `read_int32(<unit>, 0xA4)`: men alive | round 147 |

`ud_topointer(u)` is the address CA's `tostring` prints (the `addr=` field); memreader Plus's README confirms "a
script interface userdata holds 8 bytes: the address of the *_SCRIPT_INTERFACE object", and round 147's outside reader
used exactly that address + 0x8.

- Without memreader Plus: one `MEMREADER absent ...` row per battle, fields `-`, nothing else changes.
- With it: one `MEMREADER present version=...` row.
- A failed read: `?`, one `MEMREADER read failed: <error>` row; after 3 failed units in a row,
  `MEMREADER off for this battle ...` and the fields read `-`.
- It only reads: no write, hook, call, patch or alloc (a build gate refuses them), no cast, no trigger reads it.

## Proof

- Harness 147 (`mod_source/releases/20261114_memreader_probe_harness147/harness147.lua`), FULL suite: 6,369 checks,
  0 failures (`h147_run1.txt`). New section (19 checks): a mock memreader absent / present / throwing, plus a trap
  that counts any write / hook / hook_site / call / patch / code_cave / unhook (0 in every world).
- RED on the pre-148 snapshot (`docs/backups/round148/`): no mr_ field, no MEMREADER row, 2/2 (`h147_red.txt`).
- The round-146 suite also passed unchanged on the new source (6,350). Pins: none rebased. No roster change.
- Build `build_and_install148.py` (round-147 builder + ROUND 148 GATE): all gates OK, five files MATCHES SOURCE,
  installed md5 `31d0ebcdd242188da2fb9f470ada7306`, 1,492,562 bytes; the installed pack contains
  `function FOURTH.mr_unit(u)`. Archived as `archive/packs/zz_test_deadly_onslaught_round148_31d0ebcd.pack`.

## The test battle

The user subscribes to memreader Plus and enables it in the launcher (rule 6: Claude adds no mods), restarts the
game, and fights a battle with a real melee. Log offset before it: 555,628,705. Pass criteria: one `present` row;
`mr_men` = `men=`; `mr_hp` / max = `hp=`; `mr_lead` = the card when read; no POLL ERROR, no `failed` row.

## Field result, battle 1 (2026-11-14, log from byte 555,628,705)

A large Empire mirror battle: 40 units of ours, 42 of the enemy's (characters, infantry, cavalry, war wagons, land
ships, steam tanks), 110 snapshots, 8,800 MAP rows. Checked with `tools/check_memreader_log.py`.

- `MEMREADER present version=1.2000000476837` once (memreader Plus reports memreader 1.2 compatibility). No
  `read failed`, no `off`, no POLL ERROR. Every row was read (0 rows with ? or -).
- **Men: 8,800 / 8,800 exact** (`mr_men` = the engine's `men=`), both sides.
- **Hit points: 8,480 / 8,800 within 0.005** of the engine's `hp=` (mr_hp divided by the unit's mr_hp while hp=1.00).
  The 320 others are almost all memory HIGHER than `hp=` (319 of 320), mostly scattered single snapshots
  (up to 0.08), so the two reads most likely sample a unit at slightly different moments of damage. Two units
  are off more often: the War Wagon RoR (79/110) and Ulrika's warhorse (50/110), both by a small positive amount,
  which suggests their `hp=` uses a different total (unexplained). Round 147 showed the memory value equals the
  unit CARD exactly.
- **Leadership: plausible on every unit.** Units that never break hold flat values (Flagellants 110, Gotrek 100,
  steam tanks and the land ship 110, its RoR copies 100); every other unit moves (up to 91 changes) and units that
  broke go NEGATIVE (lowest -40, a War Wagon RoR; many infantry between -1 and -36), as the Cheat Engine table
  said ("signed current leadership"). No card was compared in this battle; round 147 matched the card 4 times.

Verdict: the memreader probe works in a real battle, on both sides, for every unit type in it, with no errors.

## All card stats: wide search (battle 2, 2026-11-14, outside reader)

`tools/memprobe/wide.py` reads the engine unit object `[handle+8]` up to 0x8000 bytes plus every block it points to
(up to 0x8000 each), saves every offset holding each card value of the selected unit (Huntsman General), and keeps
the ones that follow the card; `score.py` checks candidates on all 80 units against land_units.

Card readings (General): start: HP 3908, armour 45, leadership 79, speed 36, MA 43, MD 40, WS 360, charge 30, ammo 45,
range 180, missile strength 500. In melee: HP 3695, leadership 51, speed 34, MA 41, ammo 42 (rest unchanged). Later:
HP 3490, leadership 33 (rest unchanged).

| Stat | Result |
|---|---|
| Hit points | LIVE `[[u+8]+0x280]+0x5CC` (card 3908 / 3695 / 3490) |
| Men | LIVE `[u+8]+0xA4` |
| Leadership | LIVE `[u+8]+0x3B78` int (also `+0x3B7C`) (79 / 51 / 33) |
| Ammunition | LIVE `[u+8]+0x3D90` int = TOTAL shots left across all men (Long Rifles 768 = 32 x 24; General 42 = card); 0 for melee units |
| Melee attack | BASE only: `[u+8]+0x37F0` float (43 while the card read 41). No live copy anywhere in the object or one pointer away (2,060 candidates -> 0): computed when asked |
| Speed | not found: the one candidate that followed 36 -> 34 is another unit's melee attack field (coincidence) |
| Melee defence, charge, missile strength, ammo at start | BASE: `+0x3820`, `+0x379C`, `+0x38F8`, `+0x373C` floats; 80/80 units equal their land_units value |
| Armour, weapon strength, range | undetermined: the card never changed during the test |

The base block (`[u+8]+0x3730..0x3A90`) holds one record per stat (a -100 floor, the value, then 1.0 / 0.1 multipliers);
the same layout as round 147's `[[u+8]+0x280]+0x850` block.
