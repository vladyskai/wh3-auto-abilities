# Round 151: large first + hold, breaths at 90 degrees, default armed, the ALL badge (sign-off round)

Date: 2026-11-14. Harness: `harness150.lua`. Release folder: `mod_source\releases\20261114_large_defaults_harness150\`.

## 1. The field battle (round 150, High Elves vs Vampire Counts)

Log from byte 604,674,328, archived as `archive\logs\battle_20261114_blob_he2.txt`.

- **Round 150 worked.** 19 of 25 blob casts went at Grave Guard (estimated value destroyed 72-160). The Tithe was hit
  only when no Grave Guard was a safe option (14-19).
- **The winds reads work.** `WINDS t=4.0 current=12.0 reserve=68.0 recharge_rate=0.752`, exactly the user's
  screenshot; by 236 s, current 74, reserve 31.9.
- **A Zombie Dragon was on the field**, and no blob attack could target it: the trigger only looked at infantry.

## 2. The rulings (user, 2026-11-14)

| Topic | Ruling |
|---|---|
| Soporific Breath and large enemies | "Large first, but also include a hold when there is a valuable large unit in the battlefield (not only in range). Also, all abilities with tags prefer_central_targets should consider using this rule." |
| Valuable | "Worth more than infantry" |
| Start armed | "The 21 when ready, but also ... all of the ones that trigger in melee or in charge, as they are a no brainer", plus protection & last stand, morale saves, heals, ammo refills |
| Arm / disarm all | "ALL badge per unit" |
| Breaths at 90 degrees | "Prefer 90 now, no need to log. I know this is better from experience." |

**What the data said about Soporific Breath:** it has no bonus vs large. The tooltip's "Good against large combatants /
Strong vs a single unit" reflects 15 projectiles of 90 damage that `prefer_central_targets`, so on a single big target
most of the volley lands. The game also forbids it while the caster is grounded or in melee; the mod did not check
that before.

## 3. The change (what you will see in battle)

- **Large first (53 prefer-central blob attacks):**
  - When a safe, visible LARGE enemy (the generated large set; flying ones included) is in range, the attack goes at
    the one losing the most value: all its shots hit it, projectile and blast damage after armour (bonus vs large
    included) against its current hit points, times its live value.
  - Example: one Soporific Breath on a full-health Zombie Dragon (armour 90, 8,236 HP) is about 1,143 damage, about
    14% of its health, about 330 value. The best infantry target last battle was about 83.
- **The hold:** with no large enemy in range, the attack is held while a visible large enemy ANYWHERE would lose more
  value than the best infantry target now. The log says `HOLD: ...` at most once every 10 s per ability.
  - **A consequence to watch:** a valuable large enemy that stays in melee with your units is never safe to hit, so it
    keeps the hold on. Those attacks then wait until it dies, leaves melee or its value drops.
- **The game's usage rules (all 77 blob attacks):** 12 need a flying caster (grounded rule), 26 a caster out of melee.
- **Breaths (20):** among the infantry targets within 20% of the best value, the one whose side faces the breath (the
  line of fire closest to 90 degrees off its facing).
- **Default armed:**
  - 27 trigger families, 432 entries (451 keys) start every battle on **A**.
  - A click on the badge still switches each one off, and the explicit choice always wins.
  - The rest start on **M** as before. That includes the blob attacks, the curses, the summons and the bombardments,
    which can hit your own men or spend limited uses.
- **The ALL badge:**
  - One extra badge reading "ALL", left of the wheel's left slot, shown whenever ability badges are shown.
  - A click arms every ability of ours on the selected unit(s), or disarms them all when every one is already armed.
  - Built on the UI tick with the badges' own template and steps.
  - **Its exact position is a first guess** (48 px left of the left wheel slot) and needs a look in the game.
- **New generated tables** (the build refuses a pack that differs from the game data):
  - `FOURTH.BLOB_SHOT_TEXT` (77): shots, projectile damage, bonus vs large, central, breath, usage rules;
  - `FOURTH.LARGE_DEF_TEXT` (980): armour and hit points per model, rider + mount + bonus.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness149 on the new source | - | 711: the older worlds arm by clicking, which now disarms a default-armed ability | (not kept) |
| FULL, run 1 | 6,423 | 0 | `h150_run1.txt` |
| FULL, run 2 | 6,423 | 0, byte-identical | `h150_run2.txt` |
| LIGHT | 3,242 | 0 | `h150_light.txt` |
| RED, pre-151 snapshot (light) | 3,222 | 0; RED 14/14 | `h150_red.txt` |

**The test switch:**
- `ZZ_AUTO_TEST_NO_DEFAULTS` is a global the harness sets before loading the mod, for every older world. The game never
  defines it, so the defaults always apply there. The build gate checks the switch is the only exception.
- The mock counts the ALL badge separately (`W.all_badge_created`), so the older "one badge per ability" counts keep
  their meaning.

Section 150 (13 worlds per file):

| World | Situation | Result |
|---|---|---|
| LG1 | Soporific: a Zombie Dragon and Grave Guard both in range | the dragon |
| LG2 | the dragon at 200 m, Grave Guard in range | no cast (the hold) |
| LG3 | only Grave Guard | one cast at it |
| UG1 | the caster grounded | no cast |
| BR1 | Sun Dragon's Breath, a facing block (listed first) and an equal side-on block | the side-on block |
| DF1 | Book of Hoeth, no click | one cast |
| DF2 | Runefang in melee, no click | one cast |
| DF3 | Runefang in melee, one click | none (switched off) |
| DF4 | Fireball, not a default family | none |
| AB1 | the ALL badge | created once; click 1 arms both (A / A), click 2 disarms (M / M), click 3 re-arms and both fire |

**RED:** on the round-150 source, LG1 hits the Grave Guard, LG2 and UG1 cast, BR1 hits the facing block, DF1 / DF2 stay
silent, and there is no ALL badge.

## 5. Pins rebased

| Pin | Old | New | Why |
|---|---|---|---|
| active-list walks (harness 104) | 5 | 6 | the ALL badge's "any badge shown?" walk |
| the armed read token | `return per ~= nil and per[marker] == true` | `if per ~= nil and per[marker] ~= nil then return per[marker] == true end` | still nil-guarded; the family default follows |
| older worlds | defaults on | off (test switch) | they arm by clicking |
| component counts | everything | ability badges only | the ALL badge is counted on its own |

## 6. Build and install

- **`build_and_install151.py`:** ROUND 123 to 151 gates OK; `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`929621699dcf172b415c2e27d20c4a78`**, 1,584,781 bytes, `IDENTICAL True`.
- Archived: `archive\packs\zz_test_deadly_onslaught_20261114_round151.pack`; `archive\mod_source\round151\` (source md5
  `684b5db44ee509f9e3578e45dd34ded5`, annotated md5 `81a0403ffb722dac4a85dffb2d063d27`).

## 7. Roster documents

- **Workbook:** `docs\WH3_abilities_master_v39_2026-11-14.xlsx` plus `.ods`; `XLSX v39 VERIFY OK` (all v38 checks,
  plus 53 / 53 large-first, 20 / 20 breath and 451 / 451 default-armed texts); counts unchanged; v1 to v38
  byte-unchanged (72 files).
- **Tracker:** section 10.29. **Database:** the enemy_blob text; `DATABASE VERIFY OK`.
- **Audits:** the wheel audit is OK; R1 to R8 are empty. **Progress:** 68 open.

## 8. Not done

- **Not tested in the game.** The next battle starts at log byte **618,416,228**.
- **Check in the game:** where the ALL badge sits, that the default-armed abilities show **A** at the start, and a
  large enemy for Soporific (the Zombie Dragon again).
- **Not modelled:** ward saves, physical and magic resistance, and the climbing / manning-equipment usage rules.
