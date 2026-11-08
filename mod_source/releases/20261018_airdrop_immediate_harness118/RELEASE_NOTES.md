# Round 118 — air drop: the delay is GONE (the 6 m centre stays)

**Date:** 2026-10-18
**Trigger:** `air_drop_on_infantry` (12 entries)
**User ruling, verbatim:** "I tried it. Let's keep the distance to center and remove the delay we had
completely."

## What changed

The trigger casts on the **evaluation that first measures the nearest valid enemy's centre inside
6 m**. Nothing is stamped, nothing is timed, nothing is re-measured inside a contact:

```
candidate = ALIVE, number_of_men_alive() > AIR_DROP_MIN_MEN (10), centre gap READABLE
chosen    = the NEAREST valid candidate by FOURTH.ad_centre_gap
FIRE      = chosen's centre gap < FOURTH.AIR_DROP_CENTER_M (6.0 m)
```

subject only to the armed state, `air_only` / `no_melee`, the gates in `FOURTH.try_pair`, and the
pre-cast re-check re-measuring the centre on **fresh handles**.

## Deleted (whole-file grep first; caller audit in the round doc)

* `AIR_DROP_DWELL_MID_S`, `AIR_DROP_DWELL_SWING_S`, `AIR_DROP_MIN_CONTACT_S`;
* `FOURTH.ad_pair` + `ad_pair_key`, `ad_pair_stamp`, `ad_pair_need`, `ad_pair_drop`, `ad_under`,
  `ad_purge_unit`, `ad_contact_clear`;
* the purge hook `zz_ad_dwell_purge` **and its only call site** in `drop_unit_by_ui_id` — the one
  dependency that lived outside the evaluator;
* `ad_enemy_velocity` + the raw-read body (`ad_vread`, `ad_vread_px`, `ad_vread_pz`),
  `ad_proj_text`, `ad_dynamic_delay`, `ad_event`;
* the short-crossing fallback and every dwell / hold / separation / cosine log line, **including the
  raw movement + heading read-verification block** (it existed only to check the cosine).

Nothing else in the file referenced any of it.

## Kept

The centre detection (`ad_centre_gap`, x/z, `distance_xz` with the sqrt fallback, fail-closed), the
candidate filter (alive, > 10 men, no infantry test), the 0.2 s fast pass with its 30 m near gate
(now naturally the centre distance), the 250 ms poll, `air_only` / `no_melee`, the self-centred cast,
every fail-closed read, the gates and the pre-cast re-check.

## Verification (LIGHT — air-drop sections only)

| run | checks | failures |
|---|---|---|
| `H118_LIGHT=1`, new source | **1586** | **0** |
| red control (pre-118 snapshots) | 1586 | **80** |

* **185 assertions retouched** (184 in the three delay sections: 183 rewritten/removed + 1 kept; plus
  `h114`'s `ad_tag` site pin), **24 new** in the six worlds:
  (a) 5.9 m casts on the first evaluation, (b) 6.1 m silent, (c) static pin — 21 deleted symbols ×
  2 files = **0 hits**, (d) no double-cast after a cast (gate proof), (e) unreadable positions fail
  closed, (f) 5.9 → 6.1 drift between picker and re-check skips the cast.
* 17 cumulative whole-suite pins are not evaluated in a light run (reported as skipped).

**The full suite was NOT run and NO spreadsheet/workbook was touched** — the approved light cycle,
same as rounds 116 and 117.

## Artifacts

| file | md5 |
|---|---|
| `mod_source/script/battle/mod/zz_test_deadly_onslaught.lua` | `99a3d107986ea06efc956c0e5ea5fb76` |
| `docs/WH3_auto_ability_annotated.lua` | `7a71e0d220fea0b4451ab5bf61ba752a` |
| installed `data/zz_test_deadly_onslaught.pack` | `2f215bc4c35845452103327fb62ba554` |

5 ship files, all **MATCHES SOURCE: True**; built md5 == installed md5 (IDENTICAL True); content
gates round 114 + 118 OK; installed-pack grep: `AIR_DROP_DWELL` 0, `ad_pair` 0,
`ad_dynamic_delay` 0, `dwell started` 0, `casts immediately on that evaluation - no delay at all` 1.

## Files in this release dir

| file | what |
|---|---|
| `harness118.lua` | the light/full harness (LIGHT switch `H118_LIGHT=1`) |
| `splice118.py` | assembles harness118 from harness117: the three retouched sections + the six worlds |
| `round118_nodelay_edit.py` | the source edit (live + annotated, with 0-occurrence assertions) |
| `make_builder118.py` | generates the builder from round 117's (round-115/116/117 gates → round-118) |
| `build_and_install118.py` | pack build + verify + install (RPFM ws://127.0.0.1:45127) |
| `h118_light_final.txt` | the green light run (1586 / 0) |
| `h118_red.txt` | the red control (80 failures) |
| `build_out.txt` | the build/install log |
| `rpfm_server_out.txt` | the RPFM server log |

Round doc: `docs/WH3_round118_airdrop_nodelay.md`.
