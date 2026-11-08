# WH3 Auto Abilities

A Total War: WARHAMMER III battle-script mod that fires special abilities by themselves, each on its
own trigger. Every ability gets a small badge on its icon: **M** = manual, **A** = automatic. Click
the badge on a selected unit to switch it.

The mod watches the battle every 250 ms and casts an armed ability when its trigger is met. Examples:

- **melee buffs** fire when the unit is in melee;
- **heals** fire when a unit is at 75% health or less;
- **shooting buffs** fire once a unit has started shooting, detected from its ammunition count;
- **Restock!** fires on a shooting ally that has 70% or less of its ammunition left;
- **Potion of Farsight** fires when an enemy is just beyond the unit's range.

Trigger ranges are always 70% of the ability's real range from the game's own tables.

## Layout

| Path | What it is |
|---|---|
| `mod_source/script/battle/mod/zz_test_deadly_onslaught.lua` | the mod (one Lua file) |
| `mod_source/ui/` | the badge template and images |
| `mod_source/releases/` | one folder per round: test harness, build script, release notes |
| `tools/` | builders, verifiers and the test runner (Python) |
| `docs/` | the ability tracker, the master database and workbooks, one document per round |

## Testing and building

The tests are Lua harnesses run under [lupa](https://github.com/scoder/lupa):

```
uv run --with lupa python tools/run_harness.py mod_source/releases/<round>/harness<N>.lua
```

Packing uses [RPFM](https://github.com/Frodo45127/rpfm), which is not included here. Each round's
`build_and_install<N>.py` drives it, checks every gate, and installs the pack.

Not included: battle logs, built packs, and the game data extracted from the installed game (it
belongs to Creative Assembly). The tools regenerate the game data locally.
