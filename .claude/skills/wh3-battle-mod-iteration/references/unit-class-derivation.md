# Deriving unit-CLASS key lists from the game's own db tables

For a target-class-gated ability (`cast on an ALLY of class X`), derive the
`land_units` key set for X from the game's own tables - never hand-type it - and
embed it as `FOURTH.class_keys.<name> = { ["<key>"] = true, ... }`, matched by
EXACT WHOLE-KEY equality against `battle_unit:type()` (which returns the
`land_units` key). An unreadable `type()` read fails CLOSED (unit not offered).

## Extract the tables (RPFM WebSocket, db.pack)

`rpfm_server.exe` exits when the last session leaves, so start it, `sleep 4`, then
connect. `DecodePackedFile` on `db/<table>/data__` returns
`resp["DBRFileInfo"][0]["table"]` whose shape is:

- `table.definition.fields[]` -> column names (`f["name"]`)
- `table.table_data[]` -> rows; each row is a LIST of single-key dicts
  (`{"StringU8": value}` / `{"I32": value}`) in field order, so
  `[list(cell.values())[0] for cell in row]` flattens it.

Tables that matter here (all in `data/db.pack`): `db/land_units_tables/data__`,
`db/main_units_tables/data__`, `db/unit_attributes_tables/data__`,
`db/unit_attributes_to_groups_junctions_tables/data__`, `db/battle_entities_tables/data__`.

## Which column gives which class

| class | source | rule |
|---|---|---|
| beast | `main_units_tables.caste` | `== "war_beast"` (take each row's `land_unit` key) |
| monster | `main_units_tables.caste` | `== "monster"` |
| war machine | `main_units_tables.caste` | `== "warmachine"` |
| construct | `unit_attributes` | attribute `construct` |
| Hell-Forged | `unit_attributes` | attribute `hellforged` |
| missile-capable | `land_units_tables.primary_missile_weapon` | non-empty |
| non-commander / non-large | `land_units_tables.class` + `battle_entities_tables.size` | `class != "com"` AND size not `large`/`very_large` |

`unit_attributes` join: `attr_by_group[land_units.attribute_group]` from
`unit_attributes_to_groups_junctions_tables` (`attribute`, `attribute_group`).
Unit attributes link through `land_units.attribute_group`; the entity size links
through `land_units.man_entity` -> `battle_entities.size`
(`small`/`medium`/`large`/`very_large`).

NOTE: `land_units.category` / `unit_category_tables` do NOT distinguish monsters
from beasts (both are `war_beast`) - `main_units.caste` does. `land_units.class`
has no "monster"; it has `com` (commander), `inf_mel`, `cav_mis`, `art_fld`, ...

Sanity counts for Warhammer III (db.pack, v54 land_units): beast 55, monster 235,
warmachine 68, construct 29, hellforged 13, missile 493,
non-commander+non-large 918, commander 1403, large 522.

## Verifying a key is in a class

Pick fixture keys for harness worlds by looking them up in the derived set, e.g.
beast `wh2_dlc09_tmb_mon_dire_wolves`, monster `wh2_dlc09_tmb_mon_heirotitan_0`,
warmachine `wh2_dlc11_cst_art_carronade`, construct
`wh2_dlc09_tmb_cav_necropolis_knights_0`, hellforged
`wh3_dlc23_chd_mon_kdaai_destroyer`, missile
`wh2_dlc09_tmb_cav_skeleton_horsemen_archers_0`, a plain non-commander non-large
`wh2_dlc09_tmb_inf_skeleton_warriors_0`, a commander `wh2_dlc09_tmb_cha_arkhan_0`,
a large non-commander `wh2_dlc09_tmb_mon_ushabti_0`.

## Harness-side engine reads the gates need

`FOURTH.context_value(unit, field)` = `common.get_context_value("CcoBattleUnit", id, field)`,
so the mock answers ANY field via `def.ctx[field]` (checked first) - e.g.
`ctx = { MoraleState = "broken" }` for a broken-morale gate, or
`ctx = { HealthValue = 2000 }` for a max-hit-points pick rule. No mock change is
needed for a new field when the world sets `def.ctx`.

## Tooling pitfall

Shell heredocs (and tool-call JSON) MANGLED backslash escapes: build search
strings with `chr(92)`, or write the helper script with the file-writer tool and
run it - do not inline `\\"` sequences in a heredoc. Also: a Python
find/replace helper that RETURNS the new text must be assigned back
(`live = sub(live, ...)`) or the edit silently does nothing.
