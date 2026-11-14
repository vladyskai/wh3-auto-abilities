# Round 147: the address probe (read-only), 2026-11-14

## Why

The user asked whether reading the game's memory (the way Skyrim's script extender works) could give
stats the battle script API hides. Feasibility so far:

- `tools/memprobe/memprobe.py` (new, READ-ONLY: PROCESS_VM_READ only, no injection, no writes) attaches
  to `Warhammer3.exe` without admin rights and scans its 7.4 to 7.9 GB of writable memory in about 9 s.
- Unit hit points are a plain 4-byte integer equal to the number on the unit card (8280 -> 7273 -> 6752 ->
  5510 in battle 1). Writing it does not stick (it is recalculated, most likely from the soldiers).
- Cheat Engine's pointer paths (34 transcribed in `tools/memprobe/chains_battle1.txt`): 10 survived a
  second battle in the same session (the unit sat at the very same address), and ALL died after a game
  restart (`chains_survivors.txt`). The game program loads at the same base (0x140000000) every time.
- User ruling (2026-11-14): "Lua address probe" over writing a deeper pointer scanner.

## The change

Every MAP row of the round-145 map probe gets one more field, LAST: `addr=<tostring(unit handle)>`, with
spaces turned into `_` (`FOURTH.map_addr`). If CA's Lua prints the handle's memory address
(`userdata: 0x...`), the outside reader can look behind it for the engine's own unit object, where hit
points and other stats live, without any fragile pointer chain, and already matched to the mod's units.
It casts nothing, reads nothing from the engine, and sets nothing a trigger reads.

## Proof

- Harness 146 (`mod_source/releases/20261114_addr_probe_harness146/harness146.lua`), FULL suite:
  6,350 checks, 0 failures (`h146_run1.txt`). New section 0zs/A1/A2: every MAP row ends with a one-word
  addr field; a raising `__tostring` logs `addr=?` with no poll error; an engine-like
  `userdata: 000001A2B3C4D5E6` keeps its address.
- RED control on the pre-147 snapshot (`docs/backups/round147/`): MAP rows without addr, 2/2
  (`h146_red.txt`).
- Pins: none rebased. No roster change (799 entries / 854 keys), so no workbook version.
- Build `build_and_install147.py` (round-146 builder + ROUND 147 GATE): every gate OK, five files
  MATCHES SOURCE, installed md5 `a45b916dd168ed2543786931448cdfc6`, 1,488,943 bytes; the installed pack
  contains `function FOURTH.map_addr(u)`. Archived as `archive/packs/zz_test_deadly_onslaught_round147_a45b916d.pack`.

## Next

The game must be restarted to load the new pack. Battle log offset before the next battle: 536,901,626.
Then: read the `addr=` values; if they are addresses, point memprobe at one and look for the unit's hit
points (the card number) inside the object or one pointer away. Unknown and decisive: whether
`tostring` on CA's handle shows an address at all, and whether the handle holds a pointer to the
engine's unit.

## Field result, battle 1 (2026-11-14, log from byte 536,901,626)

Custom battle: 2 Slaanesh Marauder units (ours) against 4 Skaven infantry units.

- `addr=` reads `battle.unit_(000000015CC7C590)`: a real address, the same on every row of a unit. Offset 0 of
  that object points into Warhammer3.exe (a C++ vtable), so it is the engine's own unit object.
- One pointer behind it, `[obj+8]`, the same layout for all 6 units, ours and the enemy's:

| Field | Meaning | Proof |
|---|---|---|
| `[[obj+8]+280]+5CC` (int) | CURRENT hit points | 6/6 units within about 1% of the mod's `hp=` x max (4781/9360 = 0.511 vs 0.52, ...); the same final offset 5CC as Cheat Engine's battle-1 chain |
| `[obj+8]+80`, `+84` (int) | MAXIMUM hit points | = men x (entity hit_points + bonus_hit_points) from the game tables, exact for 3 unit types; never moved in the fight |
| `[obj+8]+A4`, `+184` (int) | men alive | fell live in the fight (Marauders 120 -> 81, Skavenslaves 180 -> 110), equal to the log's `men=` |
| `[obj+8]+A0` (int) | 128 / 256, unknown (slot capacity?) | not checked |
| `[obj+8]+208`, `+210` (float) | position x / z | equal to the log |
| `[obj+8]+228` (float) | ordered width | equal to the log |

Tools (all READ-ONLY): `tools/memprobe/peek.py` (look at an object), `fields.py` / `near.py` / `near2.py`
(find a known value in an object up to two pointers deep), `watch.py` (record the fields every second from the
log's addresses).

Not yet known: whether the offsets survive a game restart (they should: they are offsets inside the engine's
own objects, not addresses), whether they survive a game PATCH (likely not; re-find with the tools), other stats
(leadership, fatigue, ability cooldowns), and how the mod would READ these values back (an outside file read by
Lua `io`, untested).

## Field result, live stats (same battle, 2026-11-14)

Three readings of the sword Marauders' card (paused each time, the unit in melee in between):

| Card | Reading 1 | Reading 2 | Reading 3 | Memory |
|---|---|---|---|---|
| Hit points | 4691 | 3969 | 3136 | `[[obj+8]+280]+5CC` read 4691, 3969, 3136: EXACT, live |
| Men | 81 | 70 | 56 | `[obj+8]+A4`: exact, live |
| Melee attack | 26 (34 base +1 rank -9 very tired) | 26 | 23 or 25 | base 34 at `[[obj+8]+280]+850`; no live field found |
| Melee defence | 29 | 29 | 26 | base 28 at `+880`; no live field found |
| Leadership | 26 | 33 | 14 | base 60 at `+8B0`; no live field found |
| Armour / charge | 14 / 14 | 14 / 14 | 11 / 13 | not searched |

Method: every float path up to two pointers deep from the unit handle that held the card value was kept, then
re-checked after the card changed (`tools/memprobe/pattern.py`, `track.py`). Melee attack 33 -> 7 -> 0 tracking
candidates, melee defence 7 -> 6 -> 0, leadership 25 -> 0 and 6 -> 0.

Reading: the LIVE melee attack, melee defence and leadership are not stored as a plain float within two pointers
of the unit. Most likely the engine computes them when asked, from the base value plus a list of active modifiers
(the card's tooltip lists them: "Unit rank: 1", "Very tired: -9"). `[[obj+170]+2A8]+2BC` holds -9.0 on all three
readings and may be the fatigue modifier (unproven). Reaching the live values would need either a deeper search
(three or more pointers) or reading the modifier list and repeating the game's own sum.

## Deeper search (three pointers), same battle, 2026-11-14

`tools/memprobe/bfs.py` searched every block up to three pointers from the sword Marauders' handle (36,290
blocks, 6 s) for the card values, then re-checked after two more 20 s stretches of fighting (card: leadership
14 -> 4 -> 4; melee attack 23 or 25, melee defence 26, armour 11, charge 13 unchanged).

- Leadership: 757 -> 13 -> 10 paths followed 14 -> 4. NONE of them resolves from any of the other five units
  (`tools/memprobe/cross.py`): they lead to data kept for the SELECTED unit only (most likely the card's own UI),
  not to a field of the unit.
- Melee attack / defence / armour / charge: hundreds of paths keep the value because the card did not change.
  Followed from all six units, no melee-defence path gives a sensible value on every unit; the few attack / armour
  / charge paths that resolve everywhere give table constants (equal for the two Skaven unit types), not live stats.
- The -9.0 at `[[obj+170]+2A8]+2BC` resolves on the selected unit only: also selected-unit data.

Conclusion: the engine does not keep the live melee attack, melee defence or leadership of a unit as a stored
number within three pointers of it; it computes them when the card (or the AI) asks. Live hit points and men are
stored and exact. The remaining route to live melee stats is the active-modifier list plus the game's own sum.

## Whole-memory leadership scan (battle 2, 2026-11-14)

Empire Spearmen (Shields), ours, selected, fighting the enemy's Spearmen RoR. `tools/memprobe/rscan.py` scans ALL
writable memory for floats in a RANGE (card value +-0.5, so a rounded stored value is not missed).

| Card leadership | Candidates |
|---|---|
| 75 (first scan 74.5..75.5) | 59,393 |
| 75 (after 15 s) | 59,052 |
| 64 | 16 |
| 64, 64 | 16 |
| 69 | 16: all 16 read exactly 69.0 |

All 16 are whole numbers and every one sits in the same pattern, `value, 120, -55` (a stat bar: value, bar top,
bar bottom), surrounded by UI text (`CcoComponentunit_card`, `button_flame`, sprite and texture names;
`tools/memprobe/around.py`). They are the interface's copies of the displayed number, not the engine's leadership.

Conclusion: no float within +-0.5 of the card's leadership exists anywhere in memory except the UI's copies. If the
engine stores a unit's morale, it stores it on another scale (or as an integer, not scanned) and computes the
card's number from it. Next possible step: an unknown-value "changed / unchanged" scan of the memory blocks around
the unit objects, which is not limited to the card's scale.

## Unknown-scale leadership scan (battle 2, 2026-11-14)

`tools/memprobe/uscan.py` snapshotted EVERY 4-byte slot in the 26,476 blocks reachable within three pointers of
the selected Spearmen's handle (25.5 million slots, about 1 s), dropped 1.6 million that move while paused, kept
the 2.5 million that changed when the card first changed, and recorded their values over 8 steps while the card
read 69, 69, 66, 66, 66, 62, 60, 67 (read exactly from one of the UI copies). `ufit.py` ranks every slot by how
well its history is a straight-line function of the card's (any scale, either sign; small integers read as floats
are tiny numbers that also stay linear, so integer storage is covered too).

- 28 perfect fits (r = 1.0000) on four scales: the card value itself; value / 120 (the bar fill); (value + 55) / 175
  (the bar fill from its -55 bottom); (value - 18) / 3 (unexplained).
- Followed from the ENEMY unit's handle, none of the 28 resolves at all (`ucross.py`): all are data kept for the
  selected unit only (the card and its bars). Looser fits (r > 0.9, 9,031 slots over 8 samples) are noise; the 234
  that resolve on the enemy give 0 or denormal values.

Conclusion: within three pointers of the unit there is no per-unit value, on any linear scale, that follows the
leadership the card shows. Together with the whole-memory scan (only UI copies on the card's scale), the live
leadership is either computed when asked or kept in a structure the unit does not point to within three steps
(for example a separate morale system).
