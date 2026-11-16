# Round 161: the ally melee buffs start armed, and the honest open count (tuning round)

Date: 2026-11-16. Harness: `harness160.lua`. Release folder: `mod_source\releases\20261116_ally_buffs_armed_harness160\`.
Source: the user's Bretonnia battle of 2026-11-16 (log bytes 704,611,726 to 735,692,926, archived as
`archive\logs\battle_20261116_r160_bretonnia.txt`).

## 1. What the battle showed

- **Clean overall:** no Lua errors; about 165 cast attempts by 20 abilities.
- **Round 160's one-poll rule is field-confirmed.** Ten times a unit cast two instant abilities back to back, for
  example Deadly Onslaught then Sword of Anti-Heroes on unit 1006. Every time, the first ability's own retry 2 s later
  was refused "on cooldown", so the first cast landed and was not replaced.
- **Uncovered wheel abilities:**
  - Wrath of Manann is the only uncovered non-spell wheel ability.
  - The 12 spells sit on the right-hand bar (rule 12).
  - The Lance formation is a formation.
- **Lion's Shield** (armed, `under_fire`) never fired: its trigger is "under missile fire", and nothing in the log shows
  that happening.

## 2. The rulings (user, 2026-11-16)

| Question | Ruling |
|---|---|
| Favour of the Fay "could have been armed from the beginning" | "Whole family": the 14 ally melee buffs start armed |
| Which of the rule-shut groups to propose first | "Wandering winds" (34, Wrath of Manann among them) |

**The 14 abilities:** Da Boss 'as a Plan!, Favour of the Fay, Fury of Khaine, Helping Hand, Inspired Assault I to III,
Inspired Defence I to III, Orcs are da Best!, Daemonic Whispers, Hellish Vigour, Verminous Fury. Every phase in the game
data is a pure buff for an ally (melee attack or defence, damage, charge, morale, resistance, reflection). Daemonic
Whispers carries a `max_damaged_entities = -1` field with no damage amount.

## 3. The change (what you will see in battle)

- **The 14 ally melee buffs start on A.** `ally_melee_buff` joins `FOURTH.DEFAULT_ON_TRIGGERS`; a badge click still
  switches any of them off.
- **The four round-159 friendly-fire and suicide families still start on M.** The new build gate checks this.
- **The progress page no longer counts rule-shut abilities as decided.** An ability shut by a 2026-10-09 family
  decision, an `auto:` exclusion or a collection-time "unsuitable" skip is shown as open, in its own group, because the
  user never ruled on it.
  - **The new count:** 917 automated, 61 decided by the user, 145 open.
  - **The correction:** round 159's "0 open" was wrong in that sense.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 6,794 | 0 | `h160_run1.txt` |
| FULL, run 2 | 6,794 | 0, byte-identical | `h160_run2.txt` |
| RED, pre-161 snapshot | 6,788 | 0; RED 4/4 | `h160_red.txt` |

| World | Situation | Result |
|---|---|---|
| FF1 | Favour of the Fay, no badge click, in melee with an ally | one cast (RED: none) |
| FF2 | Favour of the Fay, one badge click (switched off) | none |
| HH1 | Helping Hand, no badge click | one cast (RED: none) |

**My slip during the round:** I cloned the harness generator through a shell heredoc. It mangled the `run_h` lines,
which I then fixed by hand with the editor. This is the pitfall CLAUDE.md already warns about.

## 5. Pins rebased

| Pin | Old | New | Why |
|---|---|---|---|
| builder round-151 gate: the exact default-armed family set | 28 families | 29, `ally_melee_buff` added | the user's 2026-11-16 ruling; the first build was refused by this gate and left the installed pack untouched |

No harness pin moved.

## 6. Build and install

- **`build_and_install161.py`:** ROUND 123 to 161 gates OK; `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`45cc23e8c2edac364057b461f390fad0`**, 1,639,421 bytes, `IDENTICAL True`. The new line is
  found in the installed pack.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261116_round161.pack`;
  - `archive\mod_source\round161\` (source md5 `f893b5562f6be6824112622e0239aeb4`, annotated md5
    `92f23da78df42e177bb6d22d0d21b116`).

## 7. Documents

- **No roster change**, so no new workbook version (v45 stays current).
- **Tracker:** section 10.39.
- **Progress page:** regenerated with the rule-shut group.
- **Trigger audit:** R1 to R8 all 0.

## 8. Next

The wandering-winds proposal (34 abilities). The next battle starts at log byte 735,692,926.
