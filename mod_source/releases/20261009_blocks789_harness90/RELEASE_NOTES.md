# HARNESS 90 / blocks 7-9 build - release notes

## What shipped
THE BLOCKS 7-9 IMPLEMENTATION BUILD. The approved-but-unimplemented backlog was
derived PROGRAMMATICALLY from `WH3_ability_tracker.md` section 3a: every row
whose status cell starts with `approved (` and whose key is not already in the
mod, plus the two backlog `redesigned` abilities (#36 Commanding Presence, #46
Dazh's Song of Winter Sunlight = 2 keys) and the one `pending review` (#32
Chanson of Caging). The four shipped Enchanted Metallurgy rows were skipped
idempotently.

  * 69 new entry-groups / 73 new keys  -> the abilities table grows
    193 -> 262 entries (199 -> 272 keys).
  * FIVE NEW trigger types, each its own FOURTH evaluator:
      charge_only           Ferocious Battle Howl (charge window, NO melee arm)
      wavering_self         Ferocious Fury of Ulric / Helm of Yvresse / Vial of Troll Blood
      wavering_self_or_ally Fury of Ulric + the redesigned #36 Commanding Presence
      charge_or_wavering    Bangers & Smash
      wavering_ally_range   "Stay Here, I'll Get Help!" (Verminking shape, NO ally-melee gate)
  * The redesigned #46 Dazh's Song rides the EXISTING `tired` trigger.
  * The four Master of Alchemy abilities ride the EXISTING `metallurgy_melee`
    (melee self-or-ally half; the shooting half stays proven-unbuildable).
  * New named constant: FOURTH.WAVERING_RANGE_M = 25 (game-data 35 m aura,
    unit_spec_abil.tsv effect_range 35.0000 - the conservative 25 m pattern).
  * Every new trigger casts ON SELF, with the pre-cast gap re-check / drift skip.
  * No new chunk-level locals (the chunk sits at Lua's 200-local ceiling): all
    state/constants ride the FOURTH helper bag.

## Files
  script/battle/mod/zz_test_deadly_onslaught.lua   (live)  sha256 f2dbe00c8a1cdb7bf073b51d91022249b156b239acf4e3dbdf1afd8f4504338f
  WH3_auto_ability_annotated.lua                   (reading copy, log-free) sha256 138c5013a51feca150d5af70c8af5c05e30d858611392607bb99d91066074628

## Harness 90
  GREEN : 2500 checks, 0 failures   (baseline was harness89 2369/0; +131 new checks)
  RED   : 2469 checks, 95 failures   (baseline snapshot = pre-edit live+ann:
                                     pre90_live.lua / pre90_ann.lua = 193 entries / 199 keys)
  No red-branch self-failures. Every red failure is a DESIGNED grown-table pin or
  the new HARNESS-90 section failing because the new abilities are absent on the
  snapshot. Categories:

