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
