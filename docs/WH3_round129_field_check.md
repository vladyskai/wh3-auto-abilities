# Round 129 field test: the battle log read

Log excerpt: `archive\logs\2026-11-01_round129_battle.txt` (31,627 lines, md5
`23bbc7e67af4df4aa987e53e7d949356`): one battle on the round-129 build (installed pack md5
`104f86410200b6d82923a2d67d2a8e23`, re-measured). Live log lines 1,319,828 to the end.

## 1. The selection fix works

- Six ghost selections were dropped (cards 1001, 1002, 1004, 1005, 1006, 1007 read `active`), the
  same box-select-then-click situation as round-128 battle 3.
- Fix A then released the hold three times: Isha's Rain twice (82.75 s after the cast both times,
  matching the real recharge of about 83 s) and Pigeon Bomb once (116.75 s). Each release was
  followed by an ACCEPTED cast.
- No errors: the 1,164 lines matching "error" are all the word "terror" inside the scan and
  heartbeat lists. No raised ui tick.

## 2. The firing flag in this battle

57 FIRING ON, 39 FIRING OFF, 55 CAST POINT lines. Lowest ammunition per unit (the `AMMO` lines):

- Characters barely shoot: Kalara 2 shots, Ulrika 1, the Witch Hunter 1, Jorek Grimm none.
- No unit ran dry. The lowest were the Sunmaker (37.5%), the Archers of the Order (54%), the
  Mortar (60%), the Archers (63%) and the Helstorm (67%). Most others ended above 85%.

## 3. Ammo-related abilities in this army

The regular ranged units own no active ranged ability (passives only, plus Full Power! on the
Land Ships, which is already automated). The candidates are all on characters:

| Ability | Owners here | Effect | Status |
|---|---|---|---|
| Restock! | Jorek Grimm, Engineer, Master Engineer | refills 30% of an ally's ammo; 4 uses, 60 s cooldown, reach 100 m (bound 70 m) | not implemented (auto: no ammo-low read) |
| Ballistics Calibration | Jorek Grimm | Reload Skill +20 for allies within 55 m of a ground point, 22 s, 90 s cooldown (bound 38 m) | not implemented (auto: ground-target-only) |
| Skjalandir's Fall | Ulrika | Accuracy +90 and Blinded! on hits, 39 s | implemented (melee); the ranged half was deferred to this data |
| Entrenchment | Jorek Grimm | AP missile damage +40%, Physical Resistance +20, cannot move | implemented (melee) |

Restock! and Ballistics Calibration were on the user's deferred next-batch list (2026-11-01).
Neither is in `army_spec` (count 0).
