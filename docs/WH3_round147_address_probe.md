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
