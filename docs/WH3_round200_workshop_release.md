# Round 200: the Steam Workshop release pack (2026-11-22)

## 1. The request and the rulings

User, 2026-11-22: "After, please prepare the pack for me to upload to steam workshop". The decisions were already taken
(`docs\WH3_open_points.md` item 18): the name "Smart Ability Autocast" ("good"), pack type Mod ("of course, agreed"),
logs removed completely before publishing, the debug tools out ("agreed"), single-player only for now.

## 2. What was built

`tools\build_release.py` GENERATES the release from the development script. Nothing in the release is edited by hand,
so every later round is released by running the tool again.

| | Development build | Release build |
|---|---|---|
| Pack | `zz_test_deadly_onslaught.pack`, type Movie (always on) | `smart_ability_autocast.pack`, type Mod (listed in the launcher) |
| Script | `script\battle\mod\zz_test_deadly_onslaught.lua` | `script\battle\mod\smart_ability_autocast.lua` |
| Log | writes `zz_test_deadly_onslaught_log.txt` | no log at all: no file, no ModLog, no game log |
| Periodic dumps | dial dump, inventory sweep, map probe, heartbeat, tick line | not called |
| Console functions (`zz_badge_*`, `zz_all_*`) | global | removed after load |
| Test switches (`ZZ_AUTO_TEST_*`) | read from the global table | read as nil |
| Multiplayer battle | runs | does nothing (`bm:is_multiplayer()`) |

The other four files are the same in both packs (the badge layout, two images, the optional MCT page). The remembered
choices file keeps its name, `smart_ability_autocast_settings.txt`.

**Both packs on one PC.** The development pack is a Movie pack and always loads. When both scripts are loaded the release
stands down (it sees the development build's console function, at load or on every timer tick) and the development
build runs alone. To try the release build itself, move `zz_test_deadly_onslaught.pack` out of the game's `data` folder
first.

## 3. Proof

- The release script compiles on Lua 5.1. It reads only the engine's globals (`bm`, `core`, `common`, `UIComponent`) and
  Lua's own. `io.open` appears twice, both for the remembered choices file.
- **The casts are the same.** The whole harness 198 suite was run twice with every cast order recorded (unit form and
  ground form, with the caster, the poll tick and the target): once on the development script, once on the release
  transform with the test switches kept (the harness needs them). 2,067 worlds, 1,652 casts, the two traces are
  byte-identical. The shipped release differs from that variant in 6 code lines, the six test switches replaced by nil.
  On the release run 373 of 8,210 checks fail, as they must: they read log lines the release no longer writes.
- `bm:is_multiplayer()` is the read the game's own battle scripts use (12 uses in `data_script.pack`, for example
  `script\battle\scripted_tours\battle_tours.lua`).
- Pack: type Mod (header byte 03), 5 files, each byte-identical to its source, no probe path and no user path inside.
  md5 `4999bdbbd824b0cf390badcaf6d8c440`, 1,626,761 bytes. Built from the round-199 development script.

Not seen in a battle. The multiplayer guard has not been tried in a multiplayer battle.

## 4. Where the files are

- `C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER III\data\smart_ability_autocast.pack`
- `...\data\smart_ability_autocast.png` (the approved image, 256 x 256, 71 KB)
- The Workshop text: `mod_source\workshop\description.txt` (Steam markup, to paste into the Workshop page).
- A copy of the pack: `archive\packs\smart_ability_autocast_20261122_round199.pack`.

## 5. Upload steps (from open point 18)

1. In Steam, press Play on Total War: WARHAMMER III and choose "TW Launcher (Legacy)". CA's new Mod Manager cannot
   upload.
2. In the mod list find `smart_ability_autocast`. Click the folder icon on it.
3. Choose the tag Battle (the default is Graphical), press UPLOAD, accept SEGA's agreement.
4. Open the new Workshop page in Steam, set the title "Smart Ability Autocast", paste the text, set the visibility.
5. An update later: rebuild with `tools\build_release.py --pack`, then the launcher's UPDATE button on the same mod. The
   pack name must never change after the first upload.

## 6. Known limits of the release (from the overnight review, open point 23)

- Lords, Heroes and large units added by other mods are not in the generated lists.
- Only the player's own army and army 1 of the enemy alliance are read. CONFIRMED from the game's
  `lib_battle_manager.lua` (`get_scriptunits_for_main_enemy_army_to_local_player` = army 1 of the non-player alliance).
- No replay guard: no replay read was found in the game's battle scripts.
- The log calls still build their text (the function is empty). The five periodic dumps are gone. The UI timer's
  per-tick component walk is unchanged.
- Three hover cards contain a semicolon and clauses are joined with "; ".
