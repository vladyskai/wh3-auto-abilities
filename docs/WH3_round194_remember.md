# Round 194: remembered M/A states, the reset on an optional MCT page (2026-11-21)

## 1. The rulings (user, 2026-11-21)

- Remembering arming: option A, per unit type and ability ("implement"), with "an easy way for the user of the mod to
  restore the default M/A status".
- The reset: "Do it the MCT route. MCT should not be a requirement for the mod to work, only needed for this button."

## 2. The pre-shot test battle (round 193's probe), read first

Battle from log byte 905,235,993 (`archive\logs\battle_20261121_r193_preshot.txt`): Empire (Markus Wulfhart, Free Company
Militia, Crossbowmen, Handgunners, Huntsmen, a Great Cannon) against Vampire Counts. `tools\analyze_preshot.py`:

| Unit | WOULD CAST at | What followed |
|---|---|---|
| Great Cannon | t=90.25 s (421 m) | target read lost at 96.75 s, first shot at 97.50 s (7.25 s after) |
| Markus Wulfhart | t=157.50 s (177 m) | first shot at 164.75 s (7.25 s) |
| Handgunners | t=172.75 s (124 m) | target lost at 176.00 s, next first shot 87 s later |
| Free Company Militia | t=201.00 s (15 m) | first shot at 203.25 s (2.25 s) |
| Huntsmen | t=205.25 s (34 m) | first shot at 206.75 s (1.50 s) |
| Handgunners | t=257.50 s (80 m) | first shot at 259.75 s (2.25 s) |
| Markus Wulfhart, twice | t=294.25 s, 294.75 s (0 m) | ended after 0.25 s each (in melee) |

- 8 moments. Leaving out Markus's two 0.25 s flickers (an enemy touching him), **5 of 6 were followed by a shot within
  7.25 s**, with 1.5 to 7.25 s of warning. One (the first Handgunners) was not.
- 2 first shots came with no warning: the Great Cannon and the Militia fired while `current_target()` read nothing.
- Fire at will read `true` on every line: the read works, but no unit was caught with it off.
- One battle, six units, no Pistoliers: a small sample. The ruling is the user's (open point 8).

## 3. The change (`tools\round194_patch.py`, `round194_reset.py`, both copies)

1. **Remembered states.** Every badge or ALL click that changes a switch also records it for the unit's TYPE in
   `smart_ability_autocast_settings.txt` next to the game: one line per switch, `<unit type> <ability> A|M`. Only a
   switch that differs from the default is stored, so a click back to the default removes the line. At the next battle
   a unit with no switch of its own takes its type's remembered state before the family default. The states live on
   each ability entry (`ability.remembered`), because `is_armed` sits above the `FOURTH` table in the file (the first
   attempt put them in `FOURTH` and crashed every older test world: caught by the full suite).
2. **The in-battle reset hook** `smart_ability_autocast_reset_remembered()` (a global, so the MCT page can call it):
   forgets the remembered table and keeps the file empty. The switches already clicked in that battle stay.
3. **The MCT page**, a FIFTH pack file: `script/mct/settings/smart_ability_autocast.lua`. Only MCT loads that folder, so
   without MCT it never runs. With MCT it adds one control, "Forget the remembered M/A choices": MCT's button type
   ("Reset") when the installed MCT has it, else a checkbox (tick it and close the panel). It empties the file and calls
   the battle hook. All of it runs inside a pcall. Research (MCT's own source, commit a06610c): the button type exists
   since 2023 but no published mod uses it yet, hence the checkbox fallback.

TEST-ONLY: `ZZ_AUTO_TEST_NO_REMEMBER` (every older world) and `ZZ_AUTO_TEST_REMEMBER_FILE`.

## 4. What changes in battle

- Click a badge to A (or M) once: every unit of that type starts the next battle that way.
- MCT installed (main menu, campaign or battle): Mod Configuration Tool > Smart Ability Autocast > Reset. Every ability
  goes back to its default in the next battle.
- MCT not installed: everything works, there is just no reset button.

## 5. Proof

- Harness 193: **8,079 checks / 0 failures**, twice, byte-identical. New section: 0zz42 (tokens), RM1 (a click writes
  the line), RM2 (the next battle, another Warrior Priest casts with no click), RM5 (another type is not affected), RM3
  (a click back to the default empties the file), RM4 (after the reset, no cast), RM6 (the hook empties the file and a
  later click writes nothing back), MC1 (no MCT: the page returns quietly), MC2 (MCT's button: "Reset" empties the file
  and calls the hook), MC3 (no button type: the checkbox's finalize listener empties the file and unticks itself).
- RED (`h193_red.txt`, the pre-194 snapshot): nothing written, the next battle forgets, the click-back arms instead.
- No pin rebased (no roster change). Workbook not touched (no ability changed).
- Build `build_and_install194.py` (5 files; ROUND 194 GATE: one write, two reads, the hook; the MCT page compiles,
  starts with the no-MCT guard, issues no order). Installed pack md5 **`3d9c6617f3ae4cd5ae1e924a91547417`**, 1,614,383
  bytes, 5 x `MATCHES SOURCE: True`, archived as `archive\packs\zz_test_deadly_onslaught_20261121_round194.pack`.
- MCT is subscribed on this PC (Workshop 2927955021, groovy_mct.pack). Not seen in game yet.

Next battle from log byte 933,407,000.
