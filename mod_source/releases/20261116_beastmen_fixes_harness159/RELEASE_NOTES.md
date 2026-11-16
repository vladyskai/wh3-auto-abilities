# Round 160: the Beastmen-battle fixes (tuning round)

Date: 2026-11-16. Harness: `harness159.lua`. Release folder: `mod_source\releases\20261116_beastmen_fixes_harness159\`.
Source: the user's Beastmen battle of 2026-11-16 (log bytes 689,926,854 to 704,611,726, archived as
`archive\logs\battle_20261116_r159.txt`).

## 1. What the battle showed

- **Clean overall:** no Lua errors. 19 of the 20 armed abilities fired. Bloodbeast (round 159, `melee_clear`) fired twice,
  113 s apart, with our nearest other unit at 25.1 m and 25.9 m (the ring is 25 m). The WINDS row reads (pool 12 at the
  start, reserve 68, refill 0.752/s).
- **Bug 1, Jagged Dagger:** the game "accepted" it 6 times in 11 s (t=140 to 151) while the Bray-Shaman fled:
  - his card went from "wavering" to "inactive";
  - he moved about 18 m away;
  - the first cast after he stopped was refused "on cooldown".
  The `when_ready` family (the 21 Winds of Magic abilities, round 150) was the only family that ignored the poll's routing
  read.
- **Gap 2, Potion of Speed:** the Wargor's Deadly Onslaught took the charge at t=76. The per-unit window then held Potion
  of Speed for 2.5 s, past the charge. Both abilities are instant (no wind-up).

## 2. The ruling (user, 2026-11-16)

"Yes, fix it and also the abilities that activate instantly (no casting time) do not need to trigger the 2.5 wait to cast
another ability. Do you have information about which are which? If not, then just disable the trigger for Deadly
Onslaught."

**The information exists.** The mod's wind-up table (`cast_gate.wind_up_s`) lists exactly the game's 258 keys with
`wind_up_time > 0`: none missing, none wrong, checked against `unit_spec_abil`. The other 659 keys are instant, Deadly
Onslaught and Potion of Speed among them. So Deadly Onslaught keeps its trigger.

## 3. The change (what you will see in battle)

1. **`when_ready` skips a routing unit.** The 21 Winds of Magic abilities wait while their unit flees and fire once it
   rallies.
2. **An instant ability holds its unit for one poll (0.25 s), not 2.5 s** (`FOURTH.SERIAL_INSTANT_HOLD_SECONDS =
   POLL_MS / 1000`).
   - **Why one poll stays:** two orders are never sent in the same tick (the engine replaces a same-tick order).
   - **Wind-up abilities are unchanged:** wind-up + 2 s, never less than 2.5 s (the round-107 Moondial evidence).
   - **In practice:** a unit with two instant abilities on the same trigger (Onslaught and Potion of Speed on the
     charge, two melee buffs) now fires both a quarter second apart.

**Honest risk:**
- The 2.5 s minimum came from a wind-up ability being replaced. There is no field evidence either way for instant ones.
- **How to tell next battle:** if an instant cast took effect, its own retry 2 s later is refused "on cooldown", as
  today. If a retry is ACCEPTED instead, the first one was replaced.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 6,779 | 0 | `h159_run1.txt` |
| FULL, run 2 | 6,779 | 0, byte-identical | `h159_run2.txt` |
| RED, pre-160 snapshot | 6,769 | 0; RED 4/4 | `h159_red.txt` |

**Section 159** (4 worlds, both files):

| World | Situation | Result |
|---|---|---|
| JR1 | Jagged Dagger on a routing caster | none (RED: one cast) |
| JR2 | Jagged Dagger on a steady caster | one cast |
| IN1 | Apocalyptic Vision + Burp of Grom, both instant, in melee | both within 1 s (RED: only the first) |
| IN2 | Death Frenzy (3 s wind-up) + Whirl of Weeping Blades (instant) | only Death Frenzy within 1 s (the wind-up still holds) |

**Fixes to my own test during the round:**
- The first IN1 used Blood Lust, whose badge has the old name `zz_auto_badge_bl`. My click missed it. Swapped for Burp of
  Grom.
- The section first printed two names in an unstable order, so run 1 and run 2 differed by those bytes. Sorted.

## 5. Pins rebased

| Pin | Old | New | Why |
|---|---|---|---|
| B3b2 (harness 81 / round 107): Onslaught and Foe-Seeker on one unit | second fire at least 10 polls after the first | at least 1 poll | both are instant; B3b ("never on the same poll") is unchanged |
| harness 140 S2: Staff of Tomorrow after Strike of Tombs | counted over 16 polls | 9 polls | the instant helper no longer holds the caster 2.5 s, so the tested ability fires at poll 2, and the mock accepts its repeat at poll 10 |
| harness 140 P2: Scroll of Power after two helpers | counted over 23 polls | 10 polls | the same: it now fires at poll 3, the mock repeat at 11 |

## 6. Build and install

- **`build_and_install160.py`:** ROUND 123 to 160 gates OK.
  - The new gate checks the routing skip and both hold constants.
  - It also rebuilds the wind-up set from the game data and refuses a mismatch: 258 of 917 keys have a wind-up.
  - `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`fa8c6d9f0c38ba1f6ed9bfd6e8b644df`**, 1,639,315 bytes, `IDENTICAL True`. The new constant is
  found in the installed pack.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261116_round160.pack`;
  - `archive\mod_source\round160\` (source md5 `0fb0420df8740c578d7f6f6ffa40e7ac`, annotated md5
    `5a2443d0d45088f16c96b9e24cf22bd6`).

## 7. Documents

- **No roster change**, so no new workbook version (v45 stays current).
- **Database:** the `when_ready` text names the routing skip; `DATABASE VERIFY OK`.
- **Trigger audit:** R1 to R8 all 0.
- **Progress page:** 917 automated, 370 seen in battle, 0 open.
- **Tracker:** section 10.38.

## 8. Not done

- **Still untested in a battle:** rounds 156 to 158, and all of round 159 except Bloodbeast.
- **Not yet seen in a battle:** this round's two changes.
- The next battle starts at log byte 704,611,726.
