# Round 195: the MCT page fixed (2026-11-21)

## 1. The report (user, 2026-11-21, with a screenshot of the MCT page)

"the '?' is in the middle. Also, there is no feedback to the player when I press it." The page also showed MCT's own
"Default Category" heading. And: "casting before the first shot: let's park this idea for now. I might return later to
it" (open point 8 PARKED).

## 2. Why (MCT's own source, commit a06610c, objects/options/obj.lua)

- The "?" is MCT's tooltip marker. MCT docks its icon row to the BOTTOM-LEFT of the label box. The round-194 label
  ("Forget the remembered M/A choices") wrapped onto three lines, so the marker sat on the third line.
- MCT names a mod's first section "Default Category" unless the mod adds its own (add_new_section).
- MCT's button type runs the callback and changes nothing on screen.

## 3. The change (`mod_source\script\mct\settings\smart_ability_autocast.lua`)

- A section "Remembered M/A choices", the label "All unit types" (one line) and the button "Reset".
- No tooltip at all, so no "?" marker. The explanation moved into the mod's description.
- After a press: the button reads "Done" and greys out, the label reads "Forgotten" (until the panel is reopened).
- The older-MCT checkbox fallback: the label "Reset all" (one line), no tooltip.

The battle script did not change.

## 4. Proof

- Harness 194: **8,082 checks / 0 failures**, twice, byte-identical. New: MC4a (section, one-line label, no tooltip,
  button Reset), MC4b (a press empties the file, calls the battle hook, Done + inactive, Forgotten), MC5 (the checkbox
  label is one line, no tooltip). RED (`h194_red.txt`, H194_MCT on `docs\backups\round195\pre195_mct.lua`): the round-194
  page had a tooltip, a long label and no feedback.
- Build `build_and_install195.py` (ROUND 195 GATE: no tooltip, the named section, the feedback). Installed pack md5
  **`c308f766e509d0ca839f795c296a8b9f`**, 1,615,263 bytes, 5 x `MATCHES SOURCE: True`, archived.
- Not seen in game yet.
