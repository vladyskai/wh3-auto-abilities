# Round 121 — all army-bar abilities excluded, 4 keys out of the mod

**Date:** 2026-10-20
**Ruling (verbatim):** *"The triggers will not work if the ability is not in the ability wheel on the
lower left corner of the battle screen, meaning 'you'd lose working triggers' makes no sense.
Therefore, ALL ARMY ABILITIES PLEASE EXCLUDE."*

An army-bar ability is a key in the `army_spec` junction. It has no button on the battle ability wheel,
so `perform_special_ability` can never be called for it — the entry can never fire, and it cannot be
IN-WHEEL. Round 120 flagged 17 such rows and moved none; this round moves all 17 and removes the
implemented ones from the mod.

## What moved

| Where | Before | After |
|---|---|---|
| Workbook status | 1,140 IN-WHEEL / 660 EXCLUDED | **1,123 / 677** (1,800 rows) |
| Workbook implemented | 742 rows / 742 keys | **738 / 738** |
| Not implemented among the included | 398 | **385** (738 + 385 = 1,123) |
| Mod ABILITIES table | 689 entries / 742 keys | **687 / 738** |
| Trigger families | 46 | **45** (ally_infinite_buff left with Merciw's) |

## What left the mod — 3 entries / 4 keys

Found by intersecting the mod's key set with the `army_spec` set (286 keys), not from the round-120
report: 3 entries carried an army-bar key, holding 4 army-bar keys between them.

| Shape | Entry | Keys removed | Entry survives? |
|---|---|---|---|
| WHOLE ENTRY | `merciws_monstrous_regiment` | 2 (both army-bar) | no |
| WHOLE ENTRY | `wardens_cage` | 1 | no |
| KEY ONLY | `greater_gate_of_khorne` | 1 (the cataclysm twin) | **yes** — keeps `wh3_main_character_abilities_greater_gate_of_khorne` |

The 4 dead per-key data rows (charge pool, three `wind_up_s` rows) and the cataclysm key's
`enemy_ground_keys` flag went too: **0 army_spec keys remain anywhere in either file**.

## Gates (permanent)

1. `tools/audit_wheel_status.py` — **G3 fails on any IN-WHEEL row carrying an army_spec key.** The old
   17-row `BASELINE` and every exceptions list are deleted.
2. `tools/build_and_install.py` / `tools/build_and_install121.py` — **refuses the build** if any
   ABILITIES key is in the army_spec set, before any pack is deleted or any command sent.
3. `tools/verify_ability_database.py` — assertion **A0**, the same test on the regenerated database.

Both directions proven: v19 → 17 rows, exit 1; v20 → 0, exit 0. Pre-121 source → BUILD REFUSED with the
4 keys; shipped source → 738 keys / 0 hits.

## Harness 120

| run | checks | failures |
|---|---|---|
| FULL, run 1 | 4,767 | **0** |
| FULL, run 2 | 4,767 | 0 — byte-identical |
| FULL, final re-run | 4,767 | 0 — byte-identical |
| LIGHT (`H118_LIGHT=1`) | 1,586 | 0 |

Pins rebased: 689→687 entries, 742→738 keys, `enemy_engaged_or_shot` 86→85, `range_real` 205→204,
charge-gate keys 162→161, wind-up keys 173→170, `ally_infinite_buff` 1→0, the eleven suite boundaries
−10 (the two removed `merciws` worlds' checks no longer run). Worlds MC1/MC2 and `K.merc` removed.

## Artifacts

| file | what |
|---|---|
| `harness120.lua` | the full/light harness (built by `tools/make_harness120.py`) |
| `h120_run1.txt` / `h120_run2.txt` / `h120_final.txt` | the full runs (2 and final byte-identical) |
| `h120_light.txt` | light mode |
| `tools/build_and_install121.py` | the build that shipped this round (gate inside) |
| `tools/build_out_h121.txt` | build/install log |

**Installed pack md5 `eec8e1e09d7c3106686b478e01e2f771`** — built == installed, five shipped files
`MATCHES SOURCE: True`.

Workbook: `docs/WH3_abilities_master_v20_2026-10-20.xlsx` (+ `.ods`). Database:
`docs/WH3_ability_database_master.md` (regenerated, `verify_ability_database.py` OK). Tracker: §10.9.
