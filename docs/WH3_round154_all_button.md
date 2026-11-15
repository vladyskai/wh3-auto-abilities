# Round 154: the ALL control becomes the game's own round button; Lua Console hooks to place it

Date: 2026-11-15. Harness: `harness153.lua`. Release folder: `mod_source\releases\20261115_all_button_harness153\`.
A UI-only round: no ability, trigger or count changed, so no workbook version (v41 stays current).

## 1. The field feedback (round 153 build, user screenshot 2026-11-15)

- The tooltip works.
- The spot is still not perfect. The user will place it by hand in battle and asked how.
- The look: "it feels like it's there, but it shouldn't be there". It was white ALL letters floating on the ribbon.

## 2. The ruling (user, 2026-11-15)

Three looks were offered:

| Option | What it is |
|---|---|
| **Game round button (Rec.), chosen** | The game's own bronze round button, the family of the camera and help buttons beside the portrait |
| Gold lettering | The same ALL letters, recoloured gold |
| Drawn plaque | A plate drawn by us behind the letters |

## 3. What the game ships (read from the installed packs, `tools\extract_ui_layouts.py`)

- **The button templates (`ui3.pack`):**
  - `ui/templates/round_small_button_toggle` is 38 x 38. Image 0 is its icon. Its states are active, hover, down, selected,
    selected_hover, selected_down and the inactive pair.
  - The camera button beside the portrait is `round_medium_button_toggle`, 56 x 56. The small one was chosen to fit
    the ribbon.
- **The icon (`ui2.pack`):** `ui/skins/default/icon_abilities.png` (37 x 37), the game's gold fist "abilities" icon. The
  auto-resolve icons (a screen with arrows) were rejected as the wrong meaning.
- The extracts sit in `gamedata\wh3_layouts\` (gitignored: Creative Assembly data).

## 4. The change (what you will see in battle)

- **The look:** the ALL control is now the game's bronze round toggle button with the gold fist icon, and no letters. The
  tooltip is unchanged, plus one sentence: "The button stays pressed while all of them are on A."
- **The pressed look follows the arming:**
  - pressed while EVERY ability of ours owned by the selected unit(s) is on A;
  - released while any of them is on M.
  - This holds however the abilities were armed: through ALL, through each ability's own badge, or by default.
  - Only a wrong family of states is corrected, so the game's own hover glow and press look stay. Nothing blinks.
- **The spot:** (-855, -21). It keeps the old text badge's centre: the button is 14 px taller, so 7 lower. This is an
  ESTIMATE, to be tuned by hand.
- **The tuning hooks, for the Lua Console** (the Modding Development Tools: Lua Console mod, workshop 2791799449; Shift+F3
  per `docs\WH3_auto_ability_mod_feasibility.md`). Each call moves the button at once and writes `ALL POS x,y` to the
  mod log:
  - `zz_all_nudge(dx, dy)`: move by dx to the right and dy down (negative = left / up);
  - `zz_all_set(x, y)`: put it at x,y;
  - `zz_all_where()`: report where it is.

  The spot does not persist on its own. Claude reads the last `ALL POS` line from the log and bakes it in the next build.

## 5. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 6,505 | 0 | `h153_run1.txt` |
| FULL, run 2 | 6,505 | 0, byte-identical | `h153_run2.txt` |
| RED, pre-154 snapshot (full) | 6,486 | 0; RED 6/6 | `h153_red.txt` |

**Before the rebase,** harness 152 on the new source failed 10 checks. All 10 were the ALL-spot pins reading -21 instead
of -28: no regression.

Section 153 (Book of Hoeth plus Runefang on one unit):

| World | What it checks | Result |
|---|---|---|
| BT1 | how the control is built | the round toggle template, the icon in image 0, no letters, no resize, (-855, -21) docked bottom-centre, shown, the tooltip |
| BT2 | the pressed look | not pressed with nothing armed; pressed after the ALL click; the engine's selected_hover and hover looks are left alone; released after the second click; one ability armed by its own badge = not pressed; both = pressed |
| BT3 | the hooks | `zz_all_nudge(5, -3)` gives -850,-24; `zz_all_set(-900, 10)`; `zz_all_where()`; the live log carries the line |

**RED:** the pre-154 control is built from the text-badge template, never looks pressed, and has no hooks.

**Limit:** the mock cannot show what the button looks like on screen. Unverified until the battle:
- whether the template takes the icon in image 0 at runtime;
- whether the engine flips a toggle's look on its own when clicked (the mod corrects it on the next UI tick either way).

## 6. Pins rebased

| Pin | Old | New | Why |
|---|---|---|---|
| sections 151 and 152: the ALL spot (0zx, AP1a, 0zy, AP2a) | (-855, -28) | (-855, -21) | the 38 x 38 button keeps the centre |
| builder round-152 gate | (-855, -28) | (-855, -21) | same |
| mock component | `CurrentState` always "default" | it records image paths per index and `SetState`; `CurrentState` returns the last state set, else "default" | the pressed look |

## 7. Build and install

- **`build_and_install154.py`:** ROUND 123 to 154 gates OK. The new gate also proves that the template and the icon exist
  in the installed game's `ui3.pack` and `ui2.pack` (read-only memory map). `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`4d95eaa03f3d773c9f9bcf166bd96db9`**, 1,588,799 bytes, `IDENTICAL True`.
  `function zz_all_nudge(dx, dy)` appears in the installed pack.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261115_round154.pack`;
  - `archive\mod_source\round154\` (source md5 `35bfa71cfa97ccbbc081a378294ca85c`, annotated md5
    `f9aaddfa3c65bd4803d1075330702fac`).

## 8. Not done

- **Not seen in the game.**
- **Workbook and database:** skipped, since there is no roster change.
- **Trigger audit and progress page:** re-run (R1 to R8 empty; 68 open).
- **The round-153 UI test** (the screenshot battle, log from byte 668,831,712, 6.3 MB) confirmed the ALL click in the
  field: "ALL click: 16 ability switch(es) on 7 unit(s)" turned ON, OFF, then ON again. No breath was cast in it, so
  the trash rule is still untested in the field.
- **The next battle** starts at log byte **675,107,621**.
