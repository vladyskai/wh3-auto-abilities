# Round 190: the animation decides in every shot trigger (2026-11-21)

## 1. The field report and the ruling

After round 189 the user fought two battles (log bytes 860,397,883-881,292,588, archived as
`archive\logs\battle_20261121_r189_lineoffire.txt`):

> "Amber Bow canceled his movement, not good. It seems the our check is working, so good work!"

Then: "Fix the 8 and also audit all the triggers."

## 2. What the log showed

- **The line of fire works.** No `LINE OF FIRE:` failure line: the ground read answered and passed its check. 22 targets
  were blocked: Amber Bow 15 times (14 by our Spearmen standing 3-13 m from Markus, 1 by a second Foot Squires unit),
  Focused Shot 7 times (our Spearmen). Each then fired once a line was clear (42.6 m and 44.3 m). Markus did not walk.
- **Amber Bow stopped Markus.** Markus moved about 8 m every 2 s (`moving=1`), the mod cast Amber Bow at t=118 on the Foot
  Squires (accepted), and from t=120 he stood at the same spot (-99.2, 104.1).
- **Why.** Amber Bow plays a cast animation (`wind_up_stance = cast_forward_medium`, 4.5 s wind-up). The 2026-11-17
  ruling ("Option A, animation decides all") says such a cast waits until the caster stands still. Its trigger
  (`enemy_large_shot`) called the shared shot check with "no stand-still needed", and round 168 never changed that.

## 3. The change (`tools\round190_still.py`, both copies)

`FOURTH.blob_still(unit)` already answers "yes" for a cast without an animation, and for an animated cast asks whether
the caster reads exactly not moving. The change makes every shot trigger ask it:

1. `FOURTH.shot_caster_ok`: the stand-still question is always asked (it used to be asked only when the trigger passed
   `still = true`).
2. `FOURTH.shot_still_ok` (the last check before the cast): asks it for every shot kind.
3. The five shot triggers with no caster check at all (`enemy_spellcaster`, `enemy_commander_wavering`,
   `enemy_summon_blob`, `enemy_execute`, `enemy_commander_value`) ask it first.

What changes in battle: these 8 abilities, which play a cast animation, now wait until the caster stops:
Amber Bow, Gaze of Nagash, Damned Pistol, Schalkain's Teeth, Goggly Glare, Vindictive Glare, Shem's Burning Gaze,
The Black Tongue. Every other ability on those triggers has no animation and fires on the move as before.

## 4. Proof

Harness 189 (`mod_source\releases\20261121_shotstill_harness189\harness189.lua`, section `run_h189`):

| Test | World | Expected | RED (pre-190) |
|---|---|---|---|
| 0zz38 | the 7 ROUND 190 lines, the old 'still and' line gone | present | absent |
| AB1 | **Amber Bow, Markus walking** (the field case) | **0 casts** | **1 cast** |
| AB2 | Amber Bow, Markus standing | 1 | 1 |
| AB3 | Hunting Spear (same trigger, no animation), caster walking | 1 | 1 |
| BT1 | The Black Tongue, caster walking | 0 | 1 |
| BT2 | The Black Tongue, caster standing | 1 | 1 |

- GREEN: full suite **7,944 checks / 0 failures**, twice, byte-identical (`h189_run1.txt`, `h189_run2.txt`). No pin
  needed a rebase.
- RED (`H189_LIVE` / `H189_ANN` on `docs\backups\round190\pre190_*.lua`, `h189_red.txt`): the old code casts Amber Bow and
  The Black Tongue while the caster walks.
- Build `build_and_install190.py` (ROUND 190 GATE: the 7 lines, the old line gone, the animated keys still in the ANIM
  table). Installed pack md5 **`1b749a4d7c6815722a94db93f420eff0`**, 1,599,680 bytes, `IDENTICAL True`, 4 x `MATCHES
  SOURCE: True`. Archived as `archive\packs\zz_test_deadly_onslaught_20261121_round190.pack`.
- Workbook v72: the 8 trigger texts gain the STANDING sentence; `verify_xlsx_v72.py` VERIFY OK.

## 5. The audit (not built)

`docs\WH3_stand_still_audit_2026-11-21.md` (tool `tools\audit_stand_still.py`): 33 more triggers carry 103 animated
abilities that never check, in six groups. They wait for the user's rulings.

Not seen in game yet. Next battle from log byte 881,292,588.
