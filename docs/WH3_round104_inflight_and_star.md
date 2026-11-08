# Round 104 — Nurgling Tide's activation window, and Star of Avelorn's ally arm

Date: 2026-10-17 · Harness 104 · Installed pack md5 `1d7c199208d3892881fb6dea2adfbfac`

Two items, both from the user's field reports.

---

# 1. Nurgling Tide — "it takes ~4 s to activate and the guard is only 2 s"

## 1.1 What the ability's own data declares

`unit_spec_abil.tsv`, key `wh3_main_lord_abilities_nurgling_tide`:

```
wind_up_time          3.0000
active_time          10.0000
recharge_time        90.0000
num_uses              3
activation_effect    (empty)
spawn_type           (empty)
spawned_unit         wh3_main_nur_inf_nurglings_summoned_0
```

There is **no other activation field**: the row has 74 columns, none named `cast_time`, and the
key has **no row in `phase_junc.tsv`/`phases.tsv`** (0 of 2,731 phase-junction rows name it — the
ability spawns, it has no effect phases; other abilities do have rows there, so the absence is
meaningful). The order-to-effect window the engine declares is therefore **3.0 s**, and the user's
"around four seconds" is that 3 s plus order delivery and the visible cast. Both numbers are
**longer than the 2 s guard**, which is the part that matters.

## 1.2 Why a re-issue inside that window replaces the cast

`battle_unitcontroller` (API dump):

> `perform_special_ability(ability_key, target_unit)` — "Issues an **order** to the units associated
> with this unitcontroller to perform the supplied special ability."
>
> `perform_special_ability_q(...)` — "Issues a **queued order** ... **Queued orders start when the
> current order completes.**"

The queued twin exists precisely because the plain call does **not** queue: it issues an order that
replaces the unit's current one. A second order arriving 2 s into a 3 s wind-up therefore replaces
the first before its effect lands. This is the mechanism the user described, and it is the
engine's documented contract, not an inference from a single log line.

## 1.3 Is the user's cancel theory compatible with the three 90 s recharges?

**Yes — and the recharge timing does not prove what the previous round said it proved.**

* The counter went **3 → 2 → 1 within four seconds** (the user's own report) while each activation
  takes 3–4 s. A use can only be deducted **when the activation starts**; if it were deducted when
  the effect landed, the third activation (ordered at 71 s) could not have been counted before 74 s.
* So spent-at 67/69/71 and returned-at 157/159/161 proves **three activations began**, one per use,
  each with its own 90 s clock. It does **not** show that any of the three effects landed.
* The log cannot show a cancel directly (there is no engine line for it), and it cannot confirm a
  summon either: the watched army list never grew in the Nurgling battle, but it never grew in any
  other session of that log either, so it is not a usable summon detector.
* A pure "cancel every cast" reading and a "three casts completed" reading are both compatible with
  the recharge times. The **order semantics** above and the **sub-second charge deduction** are what
  favour the cancel reading; with a 2 s cadence and a 3–4 s activation, every cast except the last
  would be replaced before landing.

## 1.4 The fix: an in-flight gate, on top of the charge gate

* New table `cast_gate.wind_up_s`: **every key in this mod whose own row declares a wind-up (136
  keys, 0.5–6.0 s)**, generated from `unit_spec_abil.tsv`. Nurgling Tide → `["…nurgling_tide"] = 3`.
* At load each `ABILITIES` entry gets `ability.wind_up_s` (max over its keys; `nil` for the 518 keys
  with no wind-up — those keep the plain 2 s guard, because they have no activation to protect).
* After a successful cast the pair is held for **`wind_up_s + 2 s`** (`IN_FLIGHT_SETTLE_SECONDS`),
  never less than `GUARD_SECONDS`:
  Nurgling Tide **5 s**, a 5 s wind-up **7 s**, a 1 s wind-up **3 s**.
  Silent while it holds; the gate writes ONE line per (unit, marker) per battle.
  The single knob for more margin is `IN_FLIGHT_SETTLE_SECONDS` (3 gives 6 s / 8 s).
* The **charge gate stays** (round 103) and is the longer hold for Nurgling Tide: 90 s.
* The deadline is purged with the unit in the one drop routine.

**Why a timeout and not an observation:** there is still no script read of a cast's progress — no
per-unit charges / cooldown / active-effect read exists (established over earlier rounds), so "the
effect landed" cannot be measured on the caster. The data-declared wind-up plus slack is the honest
window.

## 1.5 Proof (harness 104, world I1)

`death_frenzy` (`wh2_dlc16_spell_bound_death_frenzy`): `wind_up_time = 3.0`, `num_uses = 1`, so the
charge gate cannot mask the result and the ONLY brake is the guard.

| build | fires in 19 polls (4.75 s) | at poll 20 | at poll 21 | gap |
|-------|---------------------------|-----------|-----------|-----|
| pre-104 | **3** (ticks 1/9/17) | 3 | 3 | **8 ticks = 2 s** |
| this build | **1** | 1 | **2** | **20 ticks = 5 s** |

---

# 2. Star of Avelorn — it only ever checked the caster

## 2.1 What was wrong

Star of Avelorn is a **ground-targeted group heal**: `target_ground = true`,
`target_ground_under_allies = true`, `effect_range 15 m`, `num_effected_friendly_units 3`,
`affect_self = true`, and its effect text is "Heals: 0.008 per tick every 1 s **(to self and allies
in range)**". It rode the health-only evaluator, which reads **the owner's** health and casts on the
owner — so it fired only when the caster herself was below 75 %, at her own feet.

## 2.2 The rule now

The health family is **ally-aware**: fire when **this unit OR a friendly unit inside the ability's
own reach** is at or below 75 % health, and choose the **LOWEST-health** qualifying unit.

The reach is data-derived, never guessed:

* an **area** heal uses `floor(effect_range × 0.70)` — Star of Avelorn **10 m**, Gulyas **24 m**,
  Salyak's Lullaby **24 m**, Locus of Fecundity **38 m**;
* a **friend-targeted** heal uses `floor(target_intercept_range × 0.70)` through the existing
  `ally_range_real` map — 60 → **42 m**, 100 → **70 m**, 200 → **140 m**.

The cast target follows the ability's own targeting data:

* `target_ground_under_allies` → the **ground form under the chosen ally**;
* `target_friends` → the **unit form on the chosen ally**;
* a **self-centred aura** → the **caster**, always (the hurt ally only arms the trigger).

The owner keeps its old arm unchanged (≤ 75 %, no distance test), so a hurt caster behaves exactly
as before. The chosen ally is re-checked immediately before the call (alive, still ≤ 75 %, still in
reach) and the cast is skipped with a logged reason if it lapsed. The ally arm logs the chosen
unit's **type**, its **health percentage** and the **real distance**, e.g.:

```
star_of_avelorn ally: 'wh2_main_hef_inf_swordsmen' is the chosen unit (health 60%,
distance 7.0m of 10m aura) - cast on the ground under that ally
```

## 2.3 Every health-family entry, and what happened to it

**Changed — ally-aware (13 entries):**

| entry | trigger | reach used | cast |
|-------|---------|-----------|------|
| Star of Avelorn | `health_aura_ground` | 15 → 10 m aura | ground under the ally |
| Gulyas | `health_aura_ground` | 35 → 24 m aura | ground under the ally |
| Salyak's Lullaby | `health_aura_self` | 35 → 24 m aura | caster |
| Locus of Fecundity | `health_aura_self` | 55 → 38 m aura | caster |
| Berry Wine | `health_aura_ally` | 60 → 42 m | the ally |
| Dreaming Ring I / II / III | `health_aura_ally` | 200 → 140 m | the ally |
| Earth Blood | `health_aura_ally` | 200 → 140 m | the ally |
| Fleshy Abundance | `health_aura_ally` | 200 → 140 m | the ally |
| Regrowth | `health_aura_ally` | 200 → 140 m | the ally |
| Radiant Gem of Hoeth | `health_aura_ally` | 200 → 140 m | the ally |
| Trollguts | `health_aura_ally` | 200 → 140 m | the ally |

**Deliberately left on the owner-only check (20 entries):**

| entries | reason |
|---------|--------|
| Ghoul King of Ushoran, Blood Chalice, Bugman's XXXXXX, Hieratic Jar, Immortal Will, Invocation of Nehek, Necroparasites, Potion of Charoi, Potion of Healing, Regenerating Flesh, Skalm, Skar's Kraken-Killer | the game's effect text says **(to self)** — a self-only heal. Nothing to be ally-aware about. |
| Mantra of Invigoration (`protection_prayer`) | reaches allies, but the game restricts the target: `invalid_target = unit_is_not_tiger_warrior`. The mod has no Tiger Warrior key list, so an ally arm would offer ineligible units and the engine would refuse (wasting the attempt and arming the cooldown hold). |
| Blood Chalice of Bathori | reaches allies, but `invalid_target = unit_is_not_commander_class`. A commander list IS derivable — left for a later round rather than bolting a one-entry class gate into this one. |
| Breath of Darkness and its Upgraded twin | reach allies, but `invalid_target = living_unit` — the recipient must be undead, and the mod has no undead key list. |
| Necrotic Phylactery, Pestilent Regeneration, Saint Annushka's Finger Bone | reach allies ("to self and allies in range" / spreading area) but the data carries **no measurable radius**: `effect_range = 0`, no target flags, and no range column. A distance test would be a guess and would break the standing 70 % rule. |
| Scroll of Power | reaches allies ("own ability recharge -60 s to self and allies in range") but it is a **recharge buff, not a heal** — an ally's health is not the right trigger for it. |

Entry arithmetic: 642 entries unchanged; `ushoran_health` 33 → **20**; the three new triggers hold
**2 + 9 + 2 = 13**; keys **682** unchanged; `ally_range_real` fields 32 → **41**; new `aura_real`
fields **4**. Trigger sum = 642.

---

# 3. Harness 104

New `%LOCALAPPDATA%\Temp\harness104.lua` = harness 103 + one section (older harnesses never edited).

**GREEN:** `checks: 3650, failures: 0` → `HARNESS OK - all checks passed`.

Worlds: I1 (the in-flight gate, above), I2 (Nurgling Tide is in both tables — the 90 s charge
dominates), S1 (Star fires for a 60 % ally at 7 m, ground cast at `pos:<ally>`), S2 (nothing hurt →
silent), S3 (60 % ally at 12 m, outside the 10 m aura → silent), S4 (caster at 60 %, allies fine →
still fires, at the caster's feet), S5 (owner 40 % beats ally 60 % → cast at the caster), S6 (Gulyas
fires at a 55 % ally at 20 m inside its 24 m aura), S7 (Gulyas silent at 30 m), S8 (Salyak's Lullaby
arms on a 50 % ally at 10 m but casts on the CASTER), S9 (Berry Wine casts ON the ally), S10
(a routing ally is never offered), S11 (a chosen ally that drifts from 7 m to 15 m is re-checked and
the cast is skipped, with the real numbers logged).

**RED** (`H104_LIVE`/`H104_ANN` → `docs\backups\round103\*.pre103.lua`):
`checks: 3563, failures: 74` = 60 baseline (older rounds' red aggregates against this snapshot;
harness 103 on the same snapshot has 44, and the extra 16 are exactly this round's updated count
pins) + **14 discriminators**: I1's three RED rows (3 casts / 2 s gap), S1a-d, S4a-b, S5, S6, S8a-c,
S9a-b, S11b.

---

# 4. Build + install

`mod_source\releases\20261017_nurgling_star_harness104\build_and_install104.py` (cloned from 103,
round note + 22 new content gates; two count gates updated to this round's truth):

```
script/battle/mod/zz_test_deadly_onslaught.lua   701943 bytes  MATCHES SOURCE: True
ui/templates/zz_auto_badge.twui.xml                2864 bytes  MATCHES SOURCE: True
ui/zz_auto/blank.png                                 69 bytes  MATCHES SOURCE: True
ui/zz_auto/auto_badge.png                           252 bytes  MATCHES SOURCE: True
ui/common ui/special_ability_tooltip.twui.xml    331235 bytes  MATCHES SOURCE: True
built pack   md5 1d7c199208d3892881fb6dea2adfbfac
installed    md5 1d7c199208d3892881fb6dea2adfbfac
IDENTICAL    True
```

Installed artifact re-checked in the game folder: `data\zz_test_deadly_onslaught.pack` md5
`1d7c199208d3892881fb6dea2adfbfac`, 1,037,019 bytes, and the new tokens are present inside it
(`local cast_gate = {`, `in-flight gate `, `function FOURTH.evaluate_health_aura_ground`,
`ally-ground cast`, `FOURTH.ah_chosen`). `zz_probe_dist.pack` is still installed.

---

# 5. What to retest

**Nurgling Tide** (Nurgle lord in melee, ability armed):
1. One cast, then the counter sits at **2**.
2. In the log: one `charge gate nurgling_tide: one use spent - the next attempt waits 90s`, and one
   `in-flight gate nurgling_tide: the cast needs 3s wind-up - the next attempt on this unit waits 5s`.
3. No second `ATTEMPT nurgling_tide` for 90 s, and the ability should now visibly complete its
   wind-up (nurglings appear). If nurglings still never appear after this build, the cast itself is
   inert for another reason and that is a new finding.

**Any wind-up ability with a short trigger** (e.g. Gate of Khorne summons, 5 s wind-up): its second
cast can no longer arrive before the first resolves — the pair waits 7 s.

**Star of Avelorn** (any unit carrying it, an ally hurt nearby):
1. Order a friendly unit to take damage while the caster is at full health. The mod should fire with
   `star_of_avelorn ally: '<type>' is the chosen unit (health NN%, distance D.Dm of 10m aura)` and
   `ally-ground cast : perform_special_ability_ground('<key>', <the chosen ALLY's own position
   vector>)`.
2. The heal should land on the ALLY's area (up to 3 friendly units within 15 m of that point),
   not at the caster's feet.
3. No hurt ally within 10 m → no cast. Caster hurt, allies fine → still fires, at her own feet.

**Gulyas / Salyak's Lullaby / Locus of Fecundity** now also fire for a hurt ally inside their aura
(24 / 24 / 38 m) — Gulyas places the ground under the ally, the two self-centred auras cast on the
caster.

---

# 6. Follow-ups not done here

* The tracker (`docs\WH3_ability_tracker.md`) and the master spreadsheet were **not** updated; a
  `v5` with a changelog row for the in-flight gate and the 13 moved entries is the next
  bookkeeping step.
* Three ally-reaching entries remain owner-only for want of a target-class list (Tiger Warrior,
  undead) — see §2.3. Adding those lists would let them join the ally arm.
* The commander-class gate for Blood Chalice of Bathori is derivable today (`FOURTH.commander_keys`)
  if wanted.
