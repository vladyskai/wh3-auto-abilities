# Round 117 — air drop: edge detection → centre detection (light iteration)

**2026-10-18** · one measurement change · air-drop family only

## The change

The user's ruling, verbatim:

> "Let's keep our current calculation but just replace the detection on edge with detection on the
> distance to center. Let's say 6 meters for now. I'll test."

`UNDER` is now the **ground-plane centre-to-centre** gap between the caster's `position()` and the
enemy's `position()` — **x/z only** (`get_y` is HEIGHT), `distance_xz` with a `sqrt(dx²+dz²)`
fallback, **nil on any unreadable read** — against `FOURTH.AIR_DROP_CENTER_M = 6.0`.

`FOURTH.AIR_DROP_EDGE_M` (0.1 m) and every `unit_distance()` read in this evaluator are **gone**
(nothing else in the file used the constant). Everything else is untouched: candidate filter,
velocity-aware delay measured once per contact (0/1/2 s), short-crossing fallback (0.3 s), 0.2 s fast
pass, 250 ms poll, `air_only` / `no_melee`, self-cast, gates, read-verification lines.

Log text renamed `edge=` → `centre=` everywhere (2 decimals).

## Files

| file | note |
|---|---|
| `mod_source/script/battle/mod/zz_test_deadly_onslaught.lua` | the change (md5 `c75d492d4e7599469d4b6e7b28aae3f0`) |
| `docs/WH3_auto_ability_annotated.lua` | the reading copy, same change (md5 `b00fda45a7f92d1750f5653ef6a98970`) |
| `round117_centre_edit.py` | the edit, applied to both copies with exact-anchor assertions |
| `h117_section.lua` | the new harness section (pins + worlds A1/A2/B1-B3/C1/C2/D/E) |
| `splice117.py` → `harness117.lua` | harness 117 + the `H117_LIGHT` hook |
| `make_builder117b.py` → `build_and_install117.py` | the builder + the round-117 content gates |
| `h117_light_final.txt` | the light run (1828 checks, 0 failures) |
| `h117_light_red.txt` | the red control (85 failures — the old edge rule)

## Verification

* **Light run (air-drop sections only):** 1828 checks, **0 failures**. 17 cumulative whole-suite
  total checks were not evaluated (they compare against the full suite) and are reported as skipped.
* **25 existing assertions retouched** (12 static pins + 13 world/log assertions), mechanically
  diffed; 3 suite-boundary pins made LIGHT-aware. The h115/h116 mock worlds were migrated from the
  old edge table to a ground position with the same bearing and heading, so every cosine is unchanged.
* **Red control:** the same sections against the pre-117 snapshots → 85 failures (every h117 pin,
  A2 fires at 6.1 m, C1/C2, D and E fail), i.e. the new worlds really do discriminate.
* **Build + install:** 5 ship files byte-identical (sha256 per file), the main script read back
  byte-identical out of the pack, gates 114/115/116/117 OK.
  Built pack md5 **`516b16aaa33d26abede8738c4447ffbe`** = installed md5, `IDENTICAL True`.
  The installed pack carries the whole script verbatim, `AIR_DROP_EDGE_M` = 0, `" edge="` = 0.

## Deliberately NOT run this round

* **The full suite** — only the air-drop sections ran (the approved light cycle).
* **The spreadsheet / master workbook** — not regenerated, not touched; the ability tracker unchanged.

Remaining unverified: the 6 m value itself (a field decision), the other families against this
source, the engine's live `distance_xz` return, and the full-suite totals (the h117 boundary pin is a
floor until the next full run). Retest plan: `docs/WH3_round117_airdrop_centredist.md` §7.
