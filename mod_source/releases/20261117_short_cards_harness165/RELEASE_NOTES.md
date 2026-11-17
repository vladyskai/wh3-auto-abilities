# Round 166: the short cards (2026-11-17)

- The M/A badge card is one short sentence ("Fires when charging or in melee."), with no distances and no name. The
  game's rules follow as short clauses. Longest card: 115 characters.
- The static note at the bottom of the ability card is gone: the pack no longer ships
  ui/common ui/special_ability_tooltip.twui.xml (four files now).
- ALL tooltip: "Arm or disarm every automatic ability of the selected unit(s)."
- A wanderer's caster no longer blocks its own cast (enemy_wander kinds 2 and 3, 39 keys).
- Friendly fire: a new build gate refuses a fixed friendly-fire check on any blast the game says cannot hit our units
  (tools/ff_gate.py, 95 keys). The four ally-safe vortices already had none.
- Harness 165: 7,025 checks / 0 failures (run twice, identical); RED 12/12.
- Installed pack md5 5fdc60d3685f343e1efd2dc5869fd39e (1,400,952 bytes).
