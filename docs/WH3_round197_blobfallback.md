# Round 197: the blob family's whole-army fallback (2026-11-21)

## 1. The ruling

User, 2026-11-21, after Arrow of Kurnous held a whole Wood Elves battle against Vampire Counts: "when no better target
exists on the enemy side (visible or invisible), it should fire as it wouldn't be wasteful". The options were in
`docs\WH3_round196_label_kurnous.md` section 4. Ruling: **"A: whole army"**.

## 2. The change (`tools\round197_patch.py`, both copies)

- `FOURTH.blob_better_exists(key, central)`: walks the WHOLE living enemy army (the engine's list, hidden units
  included). A unit counts as better when its class could be a target (an infantry block of 10 or more, or a large unit
  for the prefer-central attacks, flying or not, since a flier can land), the armour rule lets this attack aim at it, and
  it is not trash. Read once per poll per ability. An unreadable army keeps the rules (fail-closed).
- `evaluate_enemy_blob` (enemy_blob and enemy_blob_vortex) sets `FOURTH.blob_relax` when nothing better exists. While it
  is set, the two save-it rules (the armour rule for armour-piercing attacks, the trash rule) are dropped in the pick and
  in the pre-cast re-check (`FOURTH.blob_ap_rule`, `FOURTH.blob_trash_rule`). The wanderers keep the plain trash rule.
- Everything else stays: the class (infantry blocks or large non-flying), none of ours in the blast + 10 m, the caster
  standing when its cast is animated, the target visible and in range, the coverage line.
- Hidden enemies are only COUNTED, never targeted: the deliberate exception to round 169 the user ruled.
- The live log says it once per ability (`BLOB FALLBACK <key>: ...`), and the cast's reason names the fallback.

## 3. What changes in battle

Against an army with nothing worth saving the attack for (Skeleton Warriors only, Zombies only, Tithe only), the blob
abilities now fire at the best visible block. In the Wood Elves battle Arrow of Kurnous would have fired at a Skeleton
block. As soon as the enemy army holds one unit that passes the rules (even one still hidden), the attack keeps saving
itself, as before.

## 4. Proof

- Harness 196: **8,104 checks / 0 failures**, twice, byte-identical. New section: 0zz43 (tokens, the 8 rule places), FB1
  (Volley of High Arrows, only Tithe: ONE cast), FB2 (Tithe in sight, a HIDDEN Grave Guard block: no cast), FB3
  (Fireball, only Tithe: ONE cast), FB4 (Fireball, a hidden 7-a-soldier block: no cast), FB5 (one BLOB FALLBACK line, the
  reason names it). Older worlds run with the TEST-ONLY `ZZ_AUTO_TEST_NO_BLOB_FALLBACK` (they list only what they show).
- RED (`h196_red.txt`, the pre-197 snapshot): FB1 and FB3 cast nothing.
- Build `build_and_install197.py` (ROUND 197 GATE: the flag set once by the blob evaluation, the wrappers at their
  places, the wanderers' plain rule, the whole army counted and fail-closed). The round-153 gate's count rebased: the pick
  and the re-check now reach the trash rule through the wrapper (2 direct uses + 3 wrapper uses). Installed pack md5
  **`febf51077902ccef857d0ac42cc872d7`**, 1,619,340 bytes, 5 x `MATCHES SOURCE: True`, archived.
- Workbook **v76**: the 70 blob-family rows gain the FALLBACK sentence (`verify_xlsx_v76.py` OK).

Not seen in game yet. Next battle from log byte 946,588,829.
