# Round 100 - removal of the two out-of-rule army abilities (2026-10-17)

## Job

The user's single in-wheel rule (*"Do not implement any ability that is not in the ability
wheel…"*) leaves exactly two implemented keys outside: **Meat Feast** (`wh3_main_prisoners_butcher`)
and **Massacre** (`wh3_main_prisoners_massacre`), both `source_type = army`. Per the user's
instruction of 2026-10-17 both are removed from the mod.

## Source change

Exactly two entries deleted from the `ABILITIES` table (same deletion in
`docs/WH3_auto_ability_annotated.lua`):

| marker | name | trigger | badge | key |
|---|---|---|---|---|
| `butcher` | Meat Feast | `ushoran_health` | `zz_auto_badge_butcher` | `wh3_main_prisoners_butcher` |
| `massacre` | Massacre | `melee_unwavering` | `zz_auto_badge_massacre` | `wh3_main_prisoners_massacre` |

Nothing else was touched: no evaluator/trigger/helper/constant/state was removed.
`ushoran_health` keeps its other member (Gulyas); `melee_unwavering` remains the shared
in-melee trigger. **Grut's Sickle** (a different, in-wheel item ability with the max-HP
`winds` pick rule) is untouched. A full table diff confirms: removed markers = exactly
`butcher`, `massacre`; added = none; changed entries = none; removed keys = exactly the two.

## Counts

| | before | after |
|---|---:|---:|
| entries | 579 | **577** |
| keys | 605 | **603** |
| `melee_unwavering` | 363 | **362** |
| `ushoran_health` | 34 | **33** |

Live script: 546,408 bytes, sha256 `c8573d52a54195aaa3b13a3dbdcc290aa2ed23d7c79bfb76fb957aa835b872ab`.
Annotated: 438,570 bytes, sha256 `58db04cb3737bbcdcb38393c553141416b130925081b0559ff41de06ac2946b0`.

## Harness 100

`harness100.lua` = `harness99.lua` + re-based count pins + a new section 0x. New checks:
both keys/markers/badge ids absent from the `ABILITIES` table and the whole file, entry count
577, key count 603, one `keys` list per entry, neighbours intact, Gulyas + `ushoran_health` 33,
`melee_unwavering` 362, and Grut's Sickle untouched (marker, key, badge, evaluator, `winds`
family, `HealthValue` read). RED mode asserts the opposite state on the pre-edit snapshot.

- GREEN: **3388 checks / 0 failures** - `h100_green.txt`
- RED (pre100 snapshot): **3355 checks / 74 designed failures** - `h100_red.txt`
  - 66 re-based count-pin checks: `579 -> 577` (32 comparisons), `605 -> 603` (8),
    `363 -> 362` (13), `34 -> 33` (7), plus the `A4a` two-pass pin `1158 -> 1154`
  - 8 inherited red-control branches from earlier rounds (harness 82/88/89/90/93/96/97/98)
    whose own pre-edit snapshots are older than this round's pre100 snapshot
  - both the harness-99 red branch (now N/A: the pre100 snapshot is post-99) and the new
    harness-100 red control pass

## Builder

`build_and_install100.py` (from `build_and_install99.py`): entry pins `579 -> 577`, melee pins
`363 -> 362`, `ushoran_health` `34 -> 33`, the block-7-9 list `69/73 -> 67/71`, the Meat Feast
presence assert replaced by absence asserts for both keys plus a Grut's Sickle untouched pin.

## Build / install

- 5 ship files: all `MATCHES SOURCE: True` (script 546,408; tooltip 331,235; badge template 2,864; blank.png 69; auto_badge.png 252)
- `main mod untouched (byte-identical): True`
- installed pack md5 **`f7c5e525ded0d1a07242b22d9053d66d`**, dist == installed
- `zz_probe_dist.pack` left installed and untouched (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`, 20,063 bytes)
- RPFM server on 45127 used and stopped afterwards

## Docs

- tracker: both §3a rows -> `excluded (not in wheel: army ability - removed from mod per user decision 2026-10-17)`;
  §2 entries carry a Removed line; legend updated; §10.2 records the decision with the user's wording.
- spreadsheet: `docs/WH3_abilities_master_v2_2026-10-17.xlsx` (+ `.ods`) - **v2 supersedes v1, v1 unchanged**;
  both rows `REMOVED (outside rule)`; new status row in Definitions; trigger-glossary and Numbers totals updated;
  v2 changelog row added.
