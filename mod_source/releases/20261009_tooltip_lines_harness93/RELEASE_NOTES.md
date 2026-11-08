# HARNESS 93 / the PER-ABILITY TOOLTIP LINE — release notes

## What changed
The mod appends ONE line to each implemented special ability's tooltip. It was a
single generic sentence for **every** ability:

> "Automatic: this ability fires by itself while the unit charges - click the M/A
> badge to switch automatic use on or off"

That described a **charge** behaviour most abilities do not have — the bulk-added
entries ride a handful of evaluators, none of them a charge — so the line was
wrong for most tooltips (the user's report).

**Fix:** the line is now **composed per entry from the trigger the entry actually
rides**: a new `FOURTH.TRIGGER_TIP` wording map plus the one-line wiring
`ability.tip = FOURTH.TRIGGER_TIP[ability.trigger]` in the existing evaluator-wiring
loop (never a hand-written line per ability). The old generic sentence is **removed**
from the shipped `ui/common ui/special_ability_tooltip.twui.xml`, which now carries
only the short badge hint: *"Automatic: click the M/A badge to switch automatic use
on or off"*.

## Where the text is composed
* `script/battle/mod/zz_test_deadly_onslaught.lua` and the annotated reading copy —
  `FOURTH.TRIGGER_TIP = { ... }` (the wording table) + the wiring loop
  `for _, ability in ipairs(ABILITIES) do ability.evaluate = ...; ability.tip =
  FOURTH.TRIGGER_TIP[ability.trigger] end`.
* `ui/common ui/special_ability_tooltip.twui.xml` — the old generic sentence removed;
  the shared static label now carries only the short badge hint.

## The wording table (implemented)
| Trigger (evaluator ridden) | Line |
|---|---|
| `melee_unwavering` | When armed, fires when this unit is in melee |
| `charge_or_melee` | When armed, fires when this unit charges or is in melee |
| `charge_only` | When armed, fires when this unit charges |
| `ushoran_health` | When armed, fires when this unit is at or below 75% health |
| `melee_health75` | When armed, fires when this unit is in melee and at or below 75% health |
| `wavering_self` | When armed, fires when this unit is wavering |
| `wavering_self_or_ally` | When armed, fires when this unit or an ally in range is wavering |
| `wavering_ally_range`, `verminking_wavering` | When armed, fires when an ally in range is wavering |
| `tired` | When armed, fires when this unit is tired or worse |
| `barrier_broken` | When armed, fires when this unit's barrier breaks |
| `glorious_death` | When armed, fires when a Slayer ally in range is in melee |
| `metallurgy_melee` | When armed, fires when this unit or an ally in range is in melee |
| `blood_sacrifice` | When armed, fires on the lowest-health ally in range when it is at or below 75% health |
| `eat_da_runts` | When armed, fires when this unit is at or below 75% health, otherwise on the lowest-health ally in range |
| `charge` (Deadly Onslaught legacy charge+melee) | When armed, fires when this unit charges or is in melee |
| `melee` | When armed, fires when this unit is in melee |
| `melee_low_morale` | When armed, fires when this unit is in melee and wavering |
| `charge_or_wavering` | When armed, fires when this unit charges or is wavering |

## Unmatched entries
**None.** All **579/579** implemented entries carry a non-empty line that equals the
allowed wording for their actual trigger; 0 unmatched, 0 entries whose trigger lacks a
wording.

## Files
    script/battle/mod/zz_test_deadly_onslaught.lua   (live)   sha256 489964dc80557003c4feb678fc2fb38aad38a2f9fd393587c98a7397362f2319
    WH3_auto_ability_annotated.lua                   (reading copy) sha256 120bef06e3e1df2cf0bf49a3b4bbc124f36b93c275eb97168e7042ec37084da5
    ui/common ui/special_ability_tooltip.twui.xml    (shipped) sha256 3b39112c1f3675b96a3803023ed3a82dbb04dd92e98674f851d566345662b692

## Build + install (RPFM WebSocket ws://127.0.0.1:45127, server started then stopped)
    All 5 ship files MATCHES SOURCE: True (per-file sha256 gate).
    Main mod byte-identical (untouched by the packer): True.
    installed md5 d83c5f93539d770fd6003cf91ce73e2d   (dist == installed, IDENTICAL True)

## Harness 93
    GREEN : 2678 checks, 0 failures
    RED   : 2645 checks, 11 failures  (baseline snapshot = pre-edit live+ann+twui,
                                        pre93_live.lua / pre93_ann.lua / pre93_twui.xml
                                        = the shipped harness-92 build, 579 entries,
                                        NO FOURTH.TRIGGER_TIP, the old twui.xml sentence)
    Every red failure is DESIGNED: the section-0q map/wiring tokens (live+ann),
    the D1b non-empty-line check, the D2 per-entry match (0/579 on the snapshot),
    the D3a unmatched report, and the D4a/D4b twui checks (the snapshot twui
    carries the old sentence). The earlier rounds' red-branch aggregates
    (harnesses 82 / 88 / 89 / 90 / 92) were RE-BASED to the N/A form - the
    harness-93 snapshot already carries everything through round 92, so every
    one of their worlds passes. No unexpected red-branch self-failures.
