# Round 149: the memory-reading project closed, probes reverted (2026-11-14)

## Ruling

User, 2026-11-14: "In that case, we close this project and reverse everything. I wanted melee attack and defense,
but if the game is so obfuscated that it is impossible to find..." and, after the comment search, "Yes, revert".

## Why it closed

The goal was live melee attack and defence. Rounds 147-148 showed (docs/WH3_round147_address_probe.md,
docs/WH3_round148_memreader_probe.md) that the game does not hide them: it never STORES them. It computes them when
asked (the card, the AI, the combat roll) from the base value plus modifiers. Searches: every block up to three
pointers from a unit (first 0x1000 bytes each), the whole engine unit object up to 0x8000 bytes plus one pointer, and
all of memory on the card's scale for leadership. No one online reads them either: 109 comments on memreader Plus,
178 on the original memreader, and a web search found nobody; the public Cheat Engine tables change damage and
defence through multipliers inside the combat code, not a stored value.

What WAS readable (kept here as knowledge, not in the mod): current hit points `[[u+8]+0x280]+0x5CC`, men
`[u+8]+0xA4`, current leadership `[u+8]+0x3B78` (signed int), ammunition left (total across men) `[u+8]+0x3D90`,
base stats block `[u+8]+0x3730..` (melee attack +0x37F0, melee defence +0x3820, charge +0x379C), where u is the
address CA's tostring prints for a battle.unit (memreader Plus `ud_topointer`).

## The change

`mod_source/script/battle/mod/zz_test_deadly_onslaught.lua` and `docs/WH3_auto_ability_annotated.lua` restored from
`docs/backups/round147/pre147_*` (identical to commit b78c8b7, round 146; md5 e439dafc... and a42ebe00...). Gone: the
round-147 `addr=` field and the round-148 memreader probe (mr_lead / mr_hp / mr_men, MEMREADER rows). Kept as history:
the round docs, `tools/memprobe/`, `tools/check_memreader_log.py`, the release folders, the archived packs.

## Proof

- Harness 148 (`mod_source/releases/20261114_revert_probes_harness148/harness148.lua`), FULL suite: 6,347 checks,
  0 failures (`h148_run1.txt`) = round 146's 6,339 + 8 new. The new section: both files byte-identical to round 146;
  no address / memreader code; a battle with a memreader mock present logs MAP rows ending at `routing=` again, no
  addr / mr_ / MEMREADER, and never touches the mock.
- RETIRED (pins kept in the file): `run_h146` (address field) and `run_h147` (memreader probe); they test code this
  ruling removed, like `run_h123` in round 125.
- RED on the pre-149 snapshot (`docs/backups/round149/`): 3/3 (`h148_red.txt`).
- Build `build_and_install149.py` (the round-146 builder + ROUND 149 GATE refusing any probe code): all gates OK,
  five files MATCHES SOURCE, installed md5 `57c01589023a04b1b0c8ffb4008e885a`, 1,488,123 bytes (the round-146 size).
  Against the archived round-146 pack only 3 header bytes differ (offsets 25-27, the build stamp). Archived as
  `archive/packs/zz_test_deadly_onslaught_round149_57c01589.pack`.

## The user's side

Unsubscribe memreader Plus in the launcher (Claude does not touch the mod list), delete
`twwh3-memreader_plus.dll` next to `Warhammer3.exe` if wanted (memreader Plus wrote it), and uninstall Cheat Engine if
wanted.
