# Sign-off pass — the FULL suite (heavy mode) + workbook v18

**Date:** 2026-10-18 (executed 2026-10-20)
**Trigger:** the user said *"Update the spreadsheet"* — the agreed sign-off point after the light
cycle. Rounds 117 and 118 shipped in LIGHT mode (air-drop sections only, no workbook), so v17 still
described round 116's measured delay, machinery that no longer exists.

**No source change. No rebuild.** The installed pack was already the round-118 build.

## Why a new harness number

`harness118.lua` was released as the round-118 light/full harness. Its FULL run failed 5 checks, all
ONE stale pin, and the light-mode cycle had also left four air-drop boundary pins as floors. Rather
than edit a released harness, this pass adds `harness119.lua` — **byte-identical to harness118 apart
from five edits**:

| # | Edit | Why |
|---|---|---|
| 1 | `run_h93`'s hand-kept `TIP.air_drop_on_infantry` → the round-118 wording | the mirror still quoted round 116's velocity-delay text, which is byte-equal to the PRE-118 snapshot (`docs/backups/round118/pre118_*.lua`). h93 is skipped by `H118_LIGHT`, so rounds 117/118 never exercised it |
| 2 | h114 boundary `pre115 >= 200` → `== 4614` (FULL branch) | light-cycle floor → exact |
| 3 | h115 boundary `pre116 >= 200` → `LIGHT and >= 200 or == 4686` | as above, light mode preserved |
| 4 | h116 boundary `pre117 >= 250` → `LIGHT and >= 250 or == 4702` | as above |
| 5 | h117 boundary `pre118 >= 250` → `LIGHT and >= 250 or == 4718` | as above |

## Results

| run | checks | failures |
|---|---|---|
| `harness118`, **FULL**, shipped source | 4,777 | **5** (all the h93 tooltip pin: `0q live`, `0q ann`, `D2` 677/689, `D3a` 12 unmatched, h93 HEADLINE) |
| `harness119`, **FULL** (run 1) | **4,777** | **0** |
| `harness119`, **FULL** (run 2) | 4,777 | 0 — byte-identical to run 1 |
| `harness119`, LIGHT (`H118_LIGHT=1`) | 1,586 | 0 |

**Disposition of the 5:** one stale pin inside the air-drop family, caused by rounds 117/118 changing
`FOURTH.TRIGGER_TIP` while h93 was skipped. The pin was fixed to follow the source; nothing outside
the air-drop family failed and there is no regression from rounds 117/118.

## Artifacts

| file | what |
|---|---|
| `harness119.lua` | the full/light harness (md5 `fc2ae6ffb793e5056f50b562552c90f2`) |
| `h118_full_run1.txt` | the FULL run of harness118 — the 5 failures, kept as the evidence |
| `h119_full_run1.txt` / `h119_full_run2.txt` | the green FULL runs (byte-identical) |
| `h119_light.txt` | light mode still green |

Workbook: `docs/WH3_abilities_master_v18_2026-10-18.xlsx` (+ `.ods`).
Sign-off record: `docs/WH3_signoff_full_suite_v18.md`.
