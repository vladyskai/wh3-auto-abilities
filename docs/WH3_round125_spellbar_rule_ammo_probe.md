# Round 125: the spell-bar rule and the read-only ammo probe

Date: 2026-11-03. Harness: `harness124.lua`. Release folder:
`mod_source\releases\20261103_spellbar_rule_ammo_probe_harness124\`.

## 1. The rulings

The user, 2026-11-03:

1. On the round-124 spell-bar badges: they worked ("the bug has disappeared"), but activating one
   rune makes the others unavailable, so automating runes makes little sense. "For now, I would
   like to remove the letters from anything that is on the right side. I would just leave the ones
   on the left side ... everything that is an active ability on the left side is our job. And
   whatever is on the right side, which are spells, and now ... these runes, we don't implement the
   triggers and the letters." The caveat: "there might be some runes that appear on the left side
   because they are given by an object or they are an active ability ... Those ones we can implement."
2. "Let's start with implementing the ammo."

## 2. The spell-bar rule

- The round-124 placement test is removed, not switched off. This round starts from the
  pre-round-124 source (`docs\backups\round124\pre124_*.lua`, the round-123 build), so none of its
  code remains (the build refuses it).
- **The rule:** a button whose `Id()` reads `button_spell...` (the right-hand bar) is never claimed.
  - No badge is built, so the ability can never be armed, so it never fires.
  - The same key on a left-hand wheel button is claimed exactly as before. That covers the caveat:
    a rune granted by an item or ability, and shown on the wheel, keeps its letter and trigger.
  - The live file logs the skip once per ability per battle: `scan: <ability> is on the
    right-hand SPELL bar ('button_spellN') - not claimed: no badge, no trigger (user rule
    2026-11-03)`.
  - Only a plain-text `Id()` can mark a button as spell-bar. If the engine ever answers `Id()` with
    anything else, the button is judged by its key alone, as before.
- **What changes in battle:** on a Rune Smith, the runes on the right-hand bar show no letter, and
  the Hammer keeps its own. Mod abilities the 2026-11-01 field log ever saw on the spell bar: five
  runes (Rune of Breaking, Slowness, Speed, Negation, Oath and Steel). Every other key on that bar
  was a real spell the mod never had.
- **Roster:** the five rune entries stay in the ABILITIES table, because the same key on a wheel
  button is still the mod's job. Whether to mark them in the workbook (implemented, but in
  practice spell-bar) is a question for the next sign-off.

## 3. The ammo probe (read-only: nothing is cast from it)

Each poll (250 ms), for every player unit that started the battle with ammunition:

| Event | What the probe does |
|---|---|
| `ammo_left()` lower than the poll before | `FIRING ON` (first drop), an `AMMO` line per drop |
| a second volley while firing, at least 1.0 s after the last drop | the gap is measured; the window becomes 1.25 x that gap (the unit's own reload, read live) |
| drops less than 1.0 s apart | one volley (models fire a fraction of a second apart); they never set the gap |
| no drop for longer than the window (10 s default until a gap is measured) | `FIRING OFF` |
| `ammo_left()` higher than before | `RESUPPLIED (not a shot)` |
| a unit with `starting_ammo()` 0 or unreadable | read once, never again |

Every AMMO / FIRING line carries the unit's ui id, its type, its current target, and whether that
target is in melee: the facts a "shooting at an enemy in melee" trigger (Skjalandir's Fall) would
need. Named test values, the user's to change: `FOURTH.AMMO_WINDOW_DEFAULT_S = 10`,
`FOURTH.AMMO_WINDOW_FACTOR = 1.25`, `FOURTH.AMMO_SAME_VOLLEY_S = 1.0`.

**What the field test answers:** does `ammo_left()` actually drop shot by shot during a battle, by
how much per volley, and how far apart the drops are. Look for `AMMO` and `FIRING` lines in the
battle log for any shooting unit.

**Known limit (accepted 2026-11-01):** the first volley can never be anticipated; the flag rises on
the poll after the ammunition is spent.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness 123 on the round-125 source | 5,398 | 19, all in section 123 (the removed placement) | (discrimination run) |
| FULL, run 1 | 5,411 | 0 | `h124_run1.txt` |
| FULL, run 2 | 5,411 | 0, byte-identical | `h124_run2.txt` |
| LIGHT | 2,230 | 0 | `h124_light.txt` |
| RED, pre-125 snapshot (light) | 2,194 | 8, all section-124 tokens | `h124_red.txt` |

**Retired section:** `run_h123` (39 checks) is no longer called. It tested the spell-bar badge
placement that the user's ruling removed, and on the new source it failed exactly its own 19
placement checks and nothing else. The function stays in the file as history, and the reason is
written beside the runner. 5,398 - 39 + 52 = 5,411.

Section 124 (52 checks, live and annotated):

- **0u:** the tokens; the round-124 code is gone; the probe never casts; the annotated copy stays log-free.
- **P1, the field case:** the Hammer badge is on wheel slot 1, the spell-bar rune gets no badge,
  and the skip is logged exactly once over many scans.
- **P2, the caveat:** the same rune key on a wheel button is claimed and badged.
- **A1:** a drop gives one FIRING ON (target `orc_boyz` in melee). The second volley 2.00 s later
  sets a 2.50 s window. After 2.75 s quiet, one FIRING OFF. The rise logs RESUPPLIED. Nothing is cast.
- **A2:** two drops 0.25 s apart are one volley, so the 10 s default window holds.
- **A3:** a unit with no ammunition: `ammo_left()` is never read.

**RED** (round-124 build): in both files the rune on the spell bar does get a badge, which is the
letter the user asked to remove.

**Harness mock:** ammunition and a shooting target are opt-in per unit (`ammo_start`, `ammo_seq`,
`ammo_target`); units without them are unchanged, which is why no earlier pin moved.

## 5. Build and install

`build_and_install125.py` (from `tools\make_builder125.py`):

- The round-124 gate is replaced. The build now refuses the removed test code, and requires both
  the spell-bar rule and exactly one call of the probe.
- `ARMY-BAR GATE OK: 759 ABILITIES keys, none of them in the 286-key army_spec junction`;
  `ROUND 125 GATE OK`; `MATCHES SOURCE: True` for all five files.
- Installed pack md5 **`4d76da08a484d91b2c97a0ea6a7788c6`**, 1,123,082 bytes, `IDENTICAL True`.

Archived: `archive\packs\zz_test_deadly_onslaught_20261103_round125.pack` and
`archive\mod_source\round125\` (source md5 `371c380d8d39cb1b4edcb29fcef0bc1f`, annotated md5
`5f96343a9f078d19fbadae38c9bff046`).

## 6. Not done

- No workbook version (no roster change). The five spell-bar rune rows are a question for the next sign-off.
- Not field-tested: neither the spell-bar rule nor the ammo probe.
- No trigger uses the firing flag yet. That comes after the field data (Skjalandir's Fall's ranged half first).
