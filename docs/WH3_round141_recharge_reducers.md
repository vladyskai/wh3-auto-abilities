# Round 141: the nine recharge reducers, one by one (sign-off round)

Date: 2026-11-13. Harness: `harness140.lua`. Release folder: `mod_source\releases\20261113_recharge_reducers_harness140\`.

## 1. Why

QA battle 5 showed Staff of Nagash (-30 s) firing in melee, whether or not anything was recharging. Scroll of Power
fired on "health 75% or less". The user: *"We should go one by one, maybe the other effects of those active abilities
are more important."*

## 2. The rulings (user, 2026-11-13, one by one)

| Ability | Effect (game data) | Ruling | Family |
|---|---|---|---|
| Scroll of Power | recharge -60 s (the campaign shows -90), 57 s, 1 use | 2+ abilities recharging | `self_recharging_2` (NEW) |
| Staff of Nagash | winds recharge +60%, recharge -30 s | 1 ability recharging | `self_recharging` (NEW) |
| Staff of Tomorrow | recharge -120 s | 1 ability recharging | `self_recharging` |
| Armour of Caledor | heal, vigour, cannot move, recharge -120 s | in melee + health <= 75% | `melee_health75` |
| Terrorgheist Skull | on one friendly unit: blinding attacks, recharge -60 s | self or ally in melee | `melee_self_or_ally` (NEW) |
| Spell-Wrought Sceptre | recharge -30 s on the caster and its target | recharging unit in reach | `recharging_in_reach` (NEW) |
| The Liber Noctus | winds +140% / +0.3 per second, recharge -30 s, 33 self-damage | 1 ability recharging | `self_recharging` |
| Channelling Staff | recharge -15 s | 1 ability recharging | `self_recharging` |
| Aken-seth | Spell Mastery +60%, recharge -15 s | 1 ability recharging | `self_recharging` |

**What the game data cannot settle.** The stat is the phase column `ability_recharge_change` (e.g. -60) on an effect
that lasts 20 to 57 s. The data does not say whether it cuts recharges already running or shortens recharges that
start during the effect. The triggers assume the first.

## 3. The change

- **The mod remembers every cast the game accepted** (`FOURTH.note_cast`, called where an accepted cast returns, in
  both files). It also remembers when that ability's lock ends.
- **The lock:** effect + recharge from the GENERATED `FOURTH.RECHARGE_S` (`tools\gen_recharge_keys.py`, 618 keys).
  - The game starts a recharge when the effect ENDS (QA battle 5: Restore, 24 + 60 s).
  - Single-use and no-recharge rows are left out.
  - The table is embedded as one text that the mod reads into the lookup at load, inside a function, so no ability key
    appears in quotes a second time and the main chunk's 200-local ceiling is untouched.
- **`FOURTH.recharging_count(unit)`:** how many of that unit's mod-cast abilities are still locked, the current entry's
  own keys excluded.
- **The four new families** cast on the caster, or on the chosen ally through the shared ally picker (new picker
  families "melee" and "recharging", each re-checked before the cast).
- **What it cannot know:**
  - spells and abilities the player clicks;
  - campaign recharge bonuses (the table may say "recharging" a little too long).

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness139 on the new source (before the rebase) | 6,049 | 50: count pins, the tooltip mirror, the harness-131 A1 world | (not kept) |
| FULL, run 1 | 6,088 | 0 | `h140_run1.txt` |
| FULL, run 2 | 6,088 | 0, byte-identical | `h140_run2.txt` |
| LIGHT | 2,907 | 0 | `h140_light.txt` |
| RED, pre-141 snapshot (light) | 2,881 | 0; RED 6/6 | `h140_red.txt` |

Section 140 (18 worlds):
- **Staff of Tomorrow:**
  - S1: in melee with nothing recharging: no cast.
  - S2: the mod casts Strike of Tombs first, then Staff of Tomorrow fires.
- **Scroll of Power:**
  - P1: one ability recharging: no cast.
  - P2: two recharging: one cast.
- **Armour of Caledor:**
  - C1: in melee at 60% health: one cast.
  - C2: at full health: no cast.
- **Terrorgheist Skull:**
  - T1: an ally 50 m away in melee: one cast on the ally.
  - T2: the ally 80 m away: no cast.
- **Spell-Wrought Sceptre:** W1: an ally whose Strike of Tombs the mod cast: one cast on the ally.

**RED** (the round-140 build): S1 and C2 cast (the old melee trigger); T1 casts nothing on the ally.

**Harness corrections during the round** (all in the test worlds or my own code; the mod logic was right):
- **The first table format broke 72 checks.** It listed every key in quotes, so each key appeared twice. Both files
  were restored from the backup (md5 checked against the round-140 archive) and the table was re-embedded as one text.
- **The mock accepts every repeat cast,** so helper abilities kept taking the caster's cast slot. Each world now marks
  a helper not ready after its first cast, as the game's cooldown would.
- **P2 polls 23 instead of 30,** so it stops inside the 2 s guard after Scroll of Power's single cast.
- **Two pin rules** were first lost to a heredoc escape and were then added with the editor.

## 5. Pins and worlds rebased

| Pin | Old | New |
|---|---:|---:|
| `melee_unwavering` (harness; builder 4 gates) | 314 | 306 |
| `ushoran_health` (incl. `ush = 20` in an expectation table) | 20 | 19 |
| `melee_health75` | 1 | 2 |
| `ally_range_real` fields | 51 | 53 |
| tooltip mirror | - | + 4 wordings |

The harness-131 A1 world (Aken-seth's 120 s charge hold) gives the caster Strike of Tombs as well. The mod casts it
first, Aken-seth then fires, and the hold is armed (14 polls instead of 4, for the per-unit cast gate).

## 6. Build and install

- **`build_and_install141.py`:**
  - ROUND 123 to 141 gates OK;
  - the lock table matches the game data;
  - `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`2eafed987e269c47af570cf4670865cb`**, 1,390,568 bytes, `IDENTICAL True`.

Archived:
- `archive\packs\zz_test_deadly_onslaught_20261113_round141.pack`;
- `archive\mod_source\round141\` (source md5 `98b42493095794f796d7f8514846ce2d`, annotated md5
  `27cc38fcfa2229100c679d70228ac458`).

## 7. Roster documents

- **Tracker:** 9 rows updated, plus section 10.23.
- **Database:** 4 family texts; `DATABASE VERIFY OK`.
- **Workbook:** `docs\WH3_abilities_master_v33_2026-11-13.xlsx` plus `.ods`.
  - Checked by `XLSX v33 VERIFY OK`.
  - 64 families; the bombardment block is now at row 110.
  - v1 to v32 are byte-unchanged (60 files).
- **Wheel audit:** OK.
- **Progress page:** rebuilt.
- **Trigger audit:** re-run; still empty.

## 8. Not done

- **Not tested in the game.** A good check is a battle with Arkhan: he owns Staff of Nagash, Liber Mortis and Tomb Blade.
  Staff of Nagash should now fire only after one of his other abilities was cast.
