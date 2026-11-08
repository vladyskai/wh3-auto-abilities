# HARNESS 99 / THE TARGET-CLASS-GATED CLASS-B ENTRIES — release notes

## What shipped
The **15** entries the audit left tagged **NEEDS A RULING** were ruled and are **all implemented**
as **ally-targeted casts** on the mod's own ally picker. The Class-B mechanism is unchanged:
the offer test is the per-ability **70 % constant ONLY** (never the engine's `unit_in_range`), the
cast goes through the **fresh-handle** route (caster controller **and** chosen ally re-enumerated the
same tick), the **hold + pre-cast lapse re-check** is kept, and the **cast target is ALWAYS the
qualifying ally — never the owner**.

| # | entry | trigger | real → bound | target-class gate |
|---|---|---|---|---|
| 1 | Overseer of the Unseen | `ally_overseer` | 100 → 70 | non-commander / non-large (**918** keys) |
| 2 | Whiplash! | `ally_beast` | 100 → 70 | beast (**55**) |
| 3 | Iron-Handed Captain | `ally_broken` | 200 → 140 | morale broken (`MoraleState == "broken"`) |
| 4-6 | Inspired Marksmanship I/II/III | `ally_missile` | 100 → 70 | missile-capable (**493**) |
| 7 | Makaisson's Persuader | `ally_warmachine_heal` | 100 → 70 | war machine (**68**) |
| 8 | Reforge | `ally_hellforged_heal` | 100 → 70 | Hell-Forged (**13**) |
| 9 | Remouldered | `ally_monster_heal` | 100 → 70 | monster (**235**) |
| 10 | Restore | `ally_construct_heal` | 100 → 70 | construct (**29**) |
| 11 | Fury of Khaine (Rampage) | `ally_melee_buff` | 100 → 70 | plain ally buff (owner in melee) |
| 12 | Verminous Fury (Rampage) | `ally_melee_buff` | 200 → 140 | plain ally buff (owner in melee) |
| 13 | Merciw's Monstrous Regiment | `ally_infinite_buff` | **NONE** | **infinite range per the wiki** |
| 14 | Daemonic Whispers (mid-flight) | `ally_melee_buff` | 200 → 140 | plain ally buff |
| 15 | Grut's Sickle (mid-flight) | `ally_winds` | 100 → 70 | pick the **HIGHEST hit points** (max `HealthValue`) |

**Entries: 15. Keys: 15** (Merciw's carries two bound keys that share one phase — both rows updated).
Counts as stated in the brief (9 / 12) do not reconcile with its own numbered list; the 15 NEEDS-RULING
audit rows are what was implemented.

## The derived class lists (the Glorious-Death method)
Every list is **derived programmatically** from the game's own db tables (extracted from `db.pack`
via RPFM into `%LOCALAPPDATA%\Temp\wh3\db_*.tsv`) and copied in verbatim as `FOURTH.class_keys`.
Membership is **exact whole-key equality** (one table read; no substring finder). An unreadable
`type()` read fails **closed** (the unit is not offered).

| list | source table / column | rule | size |
|---|---|---|---:|
| `beast` | `main_units_tables.caste` | `== "war_beast"` (each row's `land_unit` key) | **55** |
| `monster` | `main_units_tables.caste` | `== "monster"` | **235** |
| `warmachine` | `main_units_tables.caste` | `== "warmachine"` | **68** |
| `construct` | `unit_attributes` via `land_units.attribute_group` | attribute `construct` | **29** |
| `hellforged` | `unit_attributes` via `land_units.attribute_group` | attribute `hellforged` | **13** |
| `missile` | `land_units_tables.primary_missile_weapon` | non-empty | **493** |
| `overseer` | `land_units_tables.class` + `battle_entities_tables.size` | `class != "com"` AND size not `large`/`very_large` | **918** |

**Nothing was left unimplemented for lack of derivability — 0 classes were non-derivable.** The
morale-broken gate is a live read (`MoraleState == "broken"`), not a list.

## Constants used
`FOURTH.ALLY_CAST_R100 = 70` (shared by 11 entries), `FOURTH.ALLY_CAST_R200 = 140` (**new** this
round, shared by 3), `FOURTH.ALLY_CAST_R150 = 105` / `R75 = 52` / `R60 = 42` / `R50 = 35` (unchanged).
`FOURTH.RANGE_FRACTION = 0.70`.

## Counts moved
`melee_unwavering` 373 → **363**, `charge_or_melee` 26 → **25**, `ushoran_health` 38 → **34**;
`ally_melee_buff` 11 → **14**; **10 new** ally triggers (overseer 1 / beast 1 / broken 1 / missile 3 /
warmachine_heal 1 / hellforged_heal 1 / monster_heal 1 / construct_heal 1 / infinite_buff 1 / winds 1);
`ally_range_real` 18 → **32**. **Entries 579 / keys 605 (unchanged).**

## Harness
`harness99.lua` (built from `harness98.lua`; the moved pins are re-based and documented).
* **Green: 3365 checks, 0 failures** (up from 3186). All **56** target-class worlds pass.
* **Red control** vs the pre-edit snapshot (`pre99_live.lua` / `pre99_ann.lua`): 3332 checks,
  the round's RED CONTROL passes **26/56** world results by design (every FIRE world fails on the
  snapshot, the SILENT worlds pass).

Worlds: for **every** class a qualifying ally fires **on that ally** (self-cast guard holds); a
non-qualifying ally in range stays silent; a qualifying ally **beyond the 70 % bound stays silent
though the engine helper says in-range**; Merciw's fires on an ally **5 km away**; the Rampage pair
fires on its family trigger; Grut's Sickle picks the **higher-HP** ally; self-cast guard throughout.

## Build & install
5 ship files built into `zz_test_deadly_onslaught.pack` (Movie), verified **byte-identical** to source.
`installed md5 = a7313d327f6ee57ebb73b30e048506a0`, size 881827. The observer probe
**`zz_probe_dist.pack` is still installed** (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`, size 20063).

## Files
* `script/battle/mod/zz_test_deadly_onslaught.lua` (LIVE) — 546751 bytes
* `C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua` (ANN) — 438907 bytes, log-free
* `C:/Users/vlady/Desktop/WH3_mod/docs/WH3_ability_tracker.md` — the 15 rows updated (backup
  `WH3_ability_tracker.md.bak_pre_classgated99`)

## Mid-flight additions
**Daemonic Whispers** and **Grut's Sickle** were ruled mid-flight and **are included** (the round had
not passed implementation when the ruling arrived).
