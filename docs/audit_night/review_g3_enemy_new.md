# Review G3: the newest enemy-targeted families (rounds 156-164)

Scope: 25 families, 184 entries (43 enemy_wander, 35 enemy_melee, 30 enemy_wave, and 22 smaller families). Source read: `FOURTH.evaluate_*` for each family (lines about 11952, 13636, 17021, 17527, 18296, 19296-19560, 19700-20060), `FOURTH.TRIGGER_TIP` (line 20229 onward), `FOURTH.WW_TEXT`, the entries' `target_class`, and the game facts (`tools/fact_sheet_open.py`). Nothing was run in a battle; all verdicts are from the code and the data.

WW table kinds (from the code): 1 straight wave, 2 wanderer or static area, 3 Ruination (three spokes), 4 strike (Siegebreaker), 5 cone from the caster, 6 Da Boss' Loons (released at the caster), 7 sweep. Columns of a row: radius, path, offset, reach/buffer, hits allies, ground-only.

## 0. Cross-family findings (read these first)

| # | Finding | Severity | Fix |
|---|---|---|---|
| G1 | The 7 ground-only WW keys (Siegebreaker, Blue Fire of Chaos x2, Heaven's Gate, Lamprey's Bite, Flesh-eating Scarabs, Magma Storm; WW column `ground` = 1) are cast with `perform_special_ability(key, enemy_unit)`. `ww_take` sets `FOURTH.eg_ground = true`, but nothing in the file reads `eg_ground` (grep: 6 writes, 0 reads); the cast branch at line 8171 tests only `FOURTH.enemy_ground_keys[key]`, and none of the 73 WW keys is in that table. The round 163/164 documents and the proposal say "cast on the ground under it", the harness counts `fires + ground_fires` together so it cannot tell the two forms apart. Siegebreaker's game flag `not_climbing_manning_eq_on_platform` makes a unit target invalid, and the other five have `enemies = no`. | High: 7 keys may never cast (the engine may accept and ignore, as with Isha's Rain) | Add the 7 keys to `enemy_ground_keys`, or make the cast branch read `FOURTH.eg_ground`; add a harness check that a ground-only key lands in `W.ground_fires` and not in `W.fires`. |
| G2 | Transfix (enemy_melee): the game only accepts a target whose morale is at or below half of base (`morale_is_higher_than_half_of_base_morale` is an invalid-target flag). The mod fires on any Lord/Hero in melee. | Medium: casts refused or wasted | New class `commander_wavering` (commander AND `FOURTH.wavering(enemy) == true`); same for the pre-cast re-check. |
| G3 | Dweomer Leach Orb and Slann Gold: the game needs a target with a casting ability (`hasnt_casting_ability`); the mod uses "Lord or Hero" as a proxy, so a non-caster Lord is picked and the engine refuses it. | Medium | A GENERATED set of unit keys that own a spell ability (same pattern as `gen_undead_keys.py`) replacing the proxy; keep the Lord/Hero fall-back only if the set cannot be built. |
| G4 | Older pickers read the raw enemy list with no visibility test: `eg_pick_enemy` (enemy_melee and the melee arms), `evaluate_enemy_fast_near_ally`, `evaluate_enemy_wavering`, `evaluate_enemy_missile_shooting`, `enc_pick_enemy`. Only the map families (`blob_map`, `m.all`) use `is_visible_to_alliance`. A fast mover or a wavering unit inside forest/fog within 40 to 140 m can be targeted although the player cannot see it. | Low to medium (also a fairness issue) | `is_visible_to_alliance(bm:get_player_alliance())` must read true in these pickers (it is proven on both sides, CLAUDE.md section 5). |
| G5 | The wave, strike and cone pickers have no minimum target value. `ww_wave_value` returns the path value even when it is tiny, so a wave can be spent on three remaining Skavenslaves (the wander family has the round 153 trash rule, `blob_trash_ok`; waves do not). | Medium for limited-use waves (1 to 4 uses) | A floor on `bv` (user to name it; for example the live value of one ordinary infantry unit) in `evaluate_enemy_wave`, `_wave_charge`, `_cone`, `_strike`. |
| G6 | Trophy Heads is one entry with two keys but one `target_class = "commander"`; the Daemon Wings key has no Lord/Hero flag, so it is over-restricted. | Low | Split the entry. |
| G7 | Wander safety counts the caster as a unit of ours (unlike waves, where "caster doesn't count"). Together with the buffers this makes several keys nearly unfireable: Sandstorm (clear 68 m, bound 70 m), Lamprey's Bite (59 m / 70 m), Ruination of Cities (77 m + half extent / 105 m), Da Boss' Loons (98 m around the caster). Not a bug against the ruling, but the user should know these will almost never fire. | Info | Optional: apply "caster doesn't count" to wander too (Sandstorm and Lamprey then keep a workable window). |
| G8 | Hammer of Smednir (enemy_wander) has a slow (speed and charge x0.4) as its only extracted effect, but rides the standing-blob rule. Rule 10 says slows fire in melee or on the charge. | Medium (needs a confirmation of the full effect) | See the B table. |

Audit flags checked against the code (restriction audit, my families): `enemy_low_health_noncommander` `unit_is_commander_class` and `health_above_20%` are both HONOURED (`enc_pick_enemy`: `enemy_is_commander` excluded, strictly below `HEALTH_LINE_PCT` = 20); `enemy_area_drain` Staff of Masks `morale_is_broken_or_lower` is covered by the routing gate; `enemy_melee` Transfix and `enemy_wavering` Ghostly Howl `morale_is_higher_than_half_of_base_morale`: Transfix NOT honoured (G2), Ghostly Howl honoured if wavering is below half (C1).

## A. Families

Conventions: "caster standing" = `is_moving() == false` (exact). "Visible" = `is_visible_to_alliance` (map families only). "Ours" = tracked units minus the expendable set and units under 2 value per soldier (`ff_ignored`).

### enemy_wander (43)
- Current: "When armed and standing still, fires at a standing enemy blob worth the most, with none of our units within the blast's wandering reach"
- Code: caster standing (`blob_still`); target from `m.enemies` = visible, infantry (class begins inf, not in the large set), not flying, at least 10 men; target standing (`is_moving` exact false); entry `target_class` (not_flying for the 8 whose game flag is flying_currently); inside the 70% bound; the blast circle covers the density line (`blob_need(radius)`) and passes the trash rule (3 packed blocks under 2 value per soldier); safety: no unit of ours (the caster counts) within radius + simulated 95% reach + 10 m of the target (+ the target's half extent for Ruination; no test when the game says allies are safe: Heaven's Gate, Abyssal Swarm, Crackleblaze); Loons (kind 6): the ring is around the caster; most blob value wins; pre-cast re-check on a fresh map.
- Verdict: INCOMPLETE ("blob" is undefined to a player; "wandering reach" is vague; the +10 m margin, infantry only, and the caster counting are not said).
- Proposed: "When armed and standing still, fires at the standing enemy infantry unit whose blast covers the most value, with none of your units within the blast radius plus its wander reach plus 10 m of it"
- Append per entry: Heaven's Gate, Abyssal Swarm, Crackleblaze: "; no safety test (cannot hit your units)". Da Boss' Loons: "; the ring is measured around this unit". The 8 flying-flag keys: "; not flying". Ground-only keys (Heaven's Gate, Lamprey's Bite, Magma Storm): "; cast on the ground under it" (once G1 is fixed).

### enemy_wave (30)
- Current: "When armed and standing still, fires its wave at a standing enemy whose path holds the most enemy value and none of our units"
- Code: caster standing; Blue Fire x2 also out of melee (generated `WW_NOMELEE`); target from `m.all` (every visible enemy, flying too), standing, entry class (not_flying for 13 keys), within bound; the path starts offset + the target's half extent before the target and runs the table length; none of ours except the caster within radius + 10 m at the start, widening to radius + 95% drift + 10 m at the end (taken at each unit's farthest point along the path); the value of every visible enemy touched by the path is summed, the highest wins; no minimum value (G5).
- Verdict: INCOMPLETE ("none of our units" omits the radius, the +10 m, the drift, and "other than the caster"; "standing" for the target is there).
- Proposed: "When armed and standing still, fires its wave at a standing enemy whose path holds the most enemy value, with none of your other units within the wave's width plus 10 m (plus its drift at the far end)"
- Append: Blue Fire x2: "; not while this unit is in melee". The 13 flying-flag keys: "; not at flying enemies".

### enemy_melee (35)
- Current: "When armed, fires on the closest enemy unit in range that is fighting in melee"
- Code: any visible-or-not (G4) alive valid enemy with `is_in_melee() == true` inside the 70% bound and the entry class; the closest by edge gap; unit-target cast; pre-cast re-check that it is still in melee.
- Verdict: EXACT for the 28 unrestricted entries; INCOMPLETE for entries with a class.
- Proposed: keep, with "valid" implied: "When armed, fires on the closest enemy unit in range that is fighting in melee"
- Append: Assassin's Trophy, El Syf, You're Next!, Trophy Heads, Transfix: "; Lords and Heroes only". Tendrils of the Sea: "; large enemies only". Transfix also: "; only if its morale is at or below half" (after G2).

### enemy_single_drain (10)
- Current: "When armed and standing still, fires on the most valuable single-entity enemy in range (lord, hero or monster)"
- Code: caster standing (melee allowed); visible enemy from `m.all` in the generated single-entity set, inside the bound; highest live `strategic_value`; no friendly margin (a direct effect cannot hit ours).
- Verdict: EXACT (add "visible").
- Proposed: "When armed and standing still, fires on the most valuable visible single-entity enemy in range (lord, hero or monster)"

### enemy_fast_near_ally (9)
- Current: "When armed, fires on a fast enemy unit moving close to your units"
- Code: enemy alive, valid, entry class, inside the bound, `is_moving() == true`, `fast_speed() >= 5` m/s (FAST_ENEMY_MPS), and the gap to one of our living units (caster counting) at most 40 m (FAST_ENEMY_NEAR_M); the one closest to ours wins. No heading, no routing, no visibility test.
- Verdict: INCOMPLETE ("fast" and "close" have numbers; the pick rule is missing).
- Proposed: "When armed, fires on the moving enemy in range with a run speed of 5 m/s or more that is within 40 m of one of your units; the one closest to yours is chosen"
- Append: Spearfisher's Net: "; not flying".

### enemy_area_drain (8)
- Current: "When armed and standing still, fires on the enemy infantry in range worth the most per soldier, with enough soldiers for every strike"
- Code: caster standing; target from `m.enemies` (visible infantry, 10+ men, not flying); `men >= area_min` (25, or 15 for Staff of Masks); highest live value per soldier; no safety margin.
- Verdict: INCOMPLETE ("strike" is jargon; the 25/15 number and "visible" are missing).
- Proposed: "When armed and standing still, fires on the visible enemy infantry unit in range worth the most per soldier that still has at least as many soldiers as the ability hits (25, or 15)"

### enemy_large_shot (5)
- Current: "When armed, fires on the most valuable large enemy in range with none of yours near it, otherwise on the most armoured enemy infantry"
- Code: caster out of melee (exact false; not required to stand still); target from `m.all` in the generated large set (cavalry and chariots included by user ruling), past the min range, none of ours within 10 m of it; highest live value; else the enemy infantry with the highest armour (`UNIT_DEF`) and then value per soldier.
- Verdict: INCOMPLETE ("near" = 10 m; caster out of melee missing).
- Proposed: "When armed and out of melee, fires on the most valuable visible large enemy in range with none of your units within 10 m of it, otherwise on the most armoured enemy infantry"

### enemy_cone (5)
- Current: "When armed and standing still, breathes at a standing enemy when the cone holds the most enemy value and none of our other units"
- Code: caster standing; standing visible target in range (not_flying for Shatter and Skabscrath); the zone runs from the caster through the target for offset + path (60 to 108 m), width radius + 10 m (+ reach), none of our OTHER units in it; highest enemy value in the zone.
- Verdict: INCOMPLETE (the zone size is missing).
- Proposed: "When armed and standing still, breathes through a standing enemy when the cone holds the most enemy value and none of your other units within its width plus 10 m"
- Append: Shatter, Skabscrath: "; not at flying enemies".

### melee_clear (5)
- Current: "When armed, fires when this unit is in melee and none of our other units are inside its blast"
- Code: `is_in_melee()` and not wavering (an unreadable morale still passes); none of our other units' rectangles within blast radius + 10 m of the caster's centre (blast from the generated vortex table: 10 to 25 m).
- Verdict: INCOMPLETE (the 10 m margin and "not wavering" are missing).
- Proposed: "When armed, fires when this unit is in melee and not wavering and none of your other units is within its blast radius plus 10 m"

### enemy_melee_or_fast (4)
- Current: "When armed, fires on the closest enemy in range that is fighting in melee, otherwise on a fast enemy closing on your units"
- Code: caster out of melee when the game says so (Crippling Throw); melee arm as enemy_melee, then min range; else the fast arm as enemy_fast_near_ally (5 m/s, within 40 m of ours), then min range (Blowpipe 5 m); Storm of the Night class flying.
- Verdict: INCOMPLETE ("closing on" is not what is read: any moving fast enemy within 40 m).
- Proposed: "When armed, fires on the closest enemy in range fighting in melee, otherwise on a moving enemy with a run speed of 5 m/s or more within 40 m of your units"
- Append: Crippling Throw: "; not while this unit is in melee". Storm of the Night: "; flying enemies only". Golden Blowpipe: "; not closer than 5 m".

### enemy_commander_value (3)
- Current: "When armed, fires on the most valuable enemy lord or hero in range"
- Code: visible enemy with class commander (commander_ground for the Sigil: also exactly not flying), inside the bound; highest live value; for the Sigil also none of ours within blast (15 m) + 10 m of the target; no caster gate.
- Verdict: INCOMPLETE for the Sigil; the Orb and Slann Gold are a proxy for "caster" (G3).
- Proposed: "When armed, fires on the most valuable visible enemy lord or hero in range"
- Append: Deathmaster's Sigil: "; not flying, with none of your units within 25 m of it". Dweomer Leach Orb, Slann Gold: "; stands in for 'a spellcaster'".

### fly_dive (2)
- Current: "When armed, fires when this unit is flying over an enemy and none of our other units are inside its blast"
- Code: `is_currently_flying() == true`; a visible enemy rectangle within 70% of the blast radius (7 m) of the caster's centre; none of our other units within blast (10 m) + 10 m.
- Verdict: INCOMPLETE ("over" is a distance test; the +10 m margin is missing).
- Proposed: "When armed, fires when this unit is flying with an enemy within 7 m of its centre (70% of the blast) and none of your other units within the blast radius plus 10 m"

### enemy_wavering (2)
- Current: "When armed, fires on the closest wavering enemy in range"
- Code: alive, valid, `is_wavering() == true` (exact), entry class, inside the bound; closest.
- Verdict: EXACT.
- Proposed: unchanged.

### enemy_wave_charge (2)
- Current: "When armed and standing still, fires its wave at a charging enemy whose path holds none of our units"
- Code: caster standing; target from `m.all` that is moving with run speed 5 m/s or more and within 40 m of one of ours (the fast_enemy_near test, not a true charge); path clear of our other units (width + 10 m, widening by drift); the most value on the path.
- Verdict: INCOMPLETE ("charging" is a speed read, the pick rule is missing).
- Proposed: "When armed and standing still, fires its wave at a moving enemy (5 m/s or more, within 40 m of your units) with the most enemy value on the path and none of your other units near it"

### enemy_sweep (2)
- Current: "When armed, sweeps the closest enemy in melee when none of our other units are within its reach"
- Code: caster in melee and not wavering; none of our other units within the sweep reach + 10 m (22 m, 46.5 m); target = the closest visible enemy that is itself in melee, inside the bound (4 m, 2 m).
- Verdict: INCOMPLETE (the caster's own melee and the +10 m are missing).
- Proposed: "When armed, sweeps the closest enemy in melee while this unit is in melee and not wavering, and none of your other units is within the sweep's reach plus 10 m"

### enemy_single_shot (2)
- Current: "When armed and standing still, fires on the most valuable single-entity enemy in range (lord, hero or monster) with none of yours near it"
- Code: caster standing and out of melee; single-entity set; none of ours within 10 m; Focused Shot takes a large single first (SHOT prefer_large).
- Verdict: INCOMPLETE (10 m, out of melee).
- Proposed: "When armed, standing still and out of melee, fires on the most valuable visible single-entity enemy in range with none of your units within 10 m of it"
- Append: Focused Shot: "; a large one first".

### enemy_execute (2)
- Current: "When armed, fires on the most valuable enemy in range whose health is at or below the execute line"
- Code: visible enemy, health at or below 20% (33% for the upgrade), Lord/Hero for the base key (class commander), single entity for the upgrade; highest live value; no caster gate and no safety margin.
- Verdict: INCOMPLETE ("execute line" is hidden).
- Proposed: "When armed, fires on the most valuable visible enemy in range at or below 20% health (33% for the upgrade); the base ability takes Lords and Heroes only"

### enemy_strike (1)
- Current: "When armed and standing still, strikes the ground under the most valuable standing single enemy, with none of our units near"
- Code: caster standing; standing visible single-entity enemy in range; none of ours within 11.1 m (radius 1.1 + 10); highest value; intended ground cast (G1).
- Verdict: INCOMPLETE ("near" = 11 m).
- Proposed: "When armed and standing still, strikes the ground under the most valuable standing single-entity enemy in range, with none of your units within 11 m of it"

### enemy_missile_shooting (1)
- Current: "When armed, fires on the closest enemy missile unit in range that is shooting"
- Code: alive, valid, class missile (Missile Mirror), shooting by the ammo-drop flag, NOT in melee, inside the bound; closest.
- Verdict: INCOMPLETE ("not in melee").
- Proposed: "When armed, fires on the closest enemy missile unit in range that is shooting and not in melee"

### enemy_melee_or_shooting (1)
- Current: "When armed, fires on the closest enemy in range that is fighting in melee, otherwise on the closest enemy missile unit that is shooting"
- Code: as written, plus the shooting arm requires the target not in melee (it never overlaps).
- Verdict: EXACT.
- Proposed: unchanged.

### enemy_melee_noncommander (1)
- Current: "When armed, fires on the closest enemy in range that is fighting in melee and is not a Lord or Hero"
- Code: exactly that; ground cast on the enemy (explosion plus summon).
- Verdict: EXACT.
- Proposed: unchanged.

### enemy_low_health_noncommander (1)
- Current: "When armed, fires on the lowest-health enemy in range that is below 20% health and is not a Lord or Hero"
- Code: exactly that (strictly below 20, commander set excluded, valid, inside the bound); lowest health, ties by distance.
- Verdict: EXACT.
- Proposed: unchanged.

### enemy_infantry_shot (1)
- Current: "When armed and standing still, fires on the enemy infantry in range worth the most per soldier, with none of yours near it"
- Code: caster standing and out of melee; target from `m.enemies` (visible infantry, 10+ men); none of ours within 10 m; highest value per soldier.
- Verdict: INCOMPLETE.
- Proposed: "When armed, standing still and out of melee, fires on the visible enemy infantry unit in range worth the most per soldier, with none of your units within 10 m of it"

### enemy_blob_vortex (1)
- Current: "When armed and standing still, fires at the enemy infantry where the blast destroys the most value, when it hits enough soldiers and none of ours are near"
- Code: `evaluate_enemy_blob` with the vortex radius (7 m): caster standing, usage rules, infantry targets (10+ men, not flying) whose blast covers the density line, trash rule, none of ours within blast + 10 m, most value destroyed.
- Verdict: INCOMPLETE ("enough" and "near" are numbers).
- Proposed: "When armed and standing still, fires at the enemy infantry unit where its 7 m blast destroys the most value, covering the density line, with none of your units within 17 m of the target"

### last_stand_clear (1)
- Current: "When armed, fires when this unit is at 10% health or less in melee and none of our other units are inside its blast"
- Code: not routing, health at or below 10, `ah_in_melee == true`, none of our other units within blast (15 m) + 10 m.
- Verdict: INCOMPLETE (+10 m).
- Proposed: "When armed, fires when this unit is at 10% health or less and in melee, with none of your other units within 25 m (its blast plus 10 m)"

## B. Abilities

Scores follow the brief (5 = fires at the payoff moment). Most limits below come from the families being ruled by the user; those rows carry "ruling" in the Why column.

### enemy_wander (43)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| banishment | Banishment | white ball 12 m, reach 16 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| banishment_dlc04 | Banishment | white ball 12 m, reach 16 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| banishment_innate | Banishment | white ball 12 m, reach 16 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| lesser_banishment | Lesser Banishment | 12 m ball, reach 11, bound 105 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| lesser_chain_lightning | Lesser Chain Lightning | chain lightning 10 m, reach 12 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| flame_storm_dlc20 | Flame Storm | flame column 10 m, reach 20 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| flame_storm | Flame Storm | flame column 10 m, reach 20 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| gem_of_sunfire | The Gem of Sunfire | flame column 10 m, reach 19 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| gehennas_golden_hounds | Gehenna's Golden Hounds | hound pack 7 m, reach 13 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | Honoured (not_flying) |
| gilded_horn | Gilded Horn of Galon Konook | hound pack 7 m, reach 33 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | Honoured (not_flying) |
| hounds_of_orion | Hounds of Orion | wolf pack 7 m, reach 20 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | Honoured (not_flying) |
| sandstorm | Sandstorm | sand vortex 12 m, reach 46: clear 68 m vs bound 70 m | 3 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach'); the window between 'ours 68 m clear' and the 70 m bound is a few metres | None cheaper; the user could accept a smaller buffer than 95% for this key | - |
| soul_slaying_hunger | Soul-slaying Hunger | soul drain 7 m, reach 30 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| sword_of_khaine | Sword of Khaine | 12 m, reach 38 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| purple_sun_of_xereus | The Purple Sun of Xereus | purple sun 12 m, reach 12 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| ruination_of_cities | The Ruination of Cities | three 60 m spokes, clear 77 m + half extent | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | Honoured (not_flying) |
| dwellers_below | The Dwellers Below | static 20 m hands | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| dwellers_below_dlc08 | The Dwellers Below | static 20 m hands | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| heavens_gate | Heaven's Gate | caster vanishes and reappears at the target: 5 m strike; not hitting allies | 3 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach'); the caster teleports into the blob, and the code does not test its own safety | Require the caster to be a Lord/Hero able to survive, or ask the user (C) | Ground-only key: cast form, see G1 |
| abyssal_swarm | The Abyssal Swarm | 12 m swarm, reach 47, not hitting allies; 30 s | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| acorns_of_the_oak | Acorns of the Oak of Ages | instant blast 15 m | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | Honoured (not_flying) |
| blight_boil | Blight Boil | instant blast 20 m | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| frost_fang | Frost Fang | static ice spikes 15 m | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | Honoured (not_flying) |
| hammer_of_smednir | The Hammer of Smednir | slow x0.4 speed and charge in a wandering 15 m area, strong vs groups | 2 | Its only listed effect is a slow (rule 10: slows fire in melee or on the charge), yet it rides the standing-blob rule | Charge arm (fast enemy infantry/cavalry closing, safe ring), as Tidecall/Wind Blast | Honoured (not_flying) |
| viletide | Viletide | static swarm 15 m, 4 uses | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | Honoured (not_flying) |
| crackleblaze | Crackleblaze | fire ball 15 m, not hitting allies | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| lampreys_bite | Lamprey's Bite | shockwave 25 m, reach 24; 5 uses; ground only | 3 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach'); clear distance 59 m against a 70 m bound: fires rarely | - | Ground-only key: cast form, see G1 |
| boiling_cauldron | Boiling Cauldron | static 15 m, 1 use | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| simmering_pot | Simmering Pot | static 15 m, 1 use | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| brass_orb | Brass Orb | vortex 12 m, 5 dmg x25 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| brass_orb_doom_flayer | Brass Orb | vortex 12 m | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| brass_orb_upgrade | Brass Orb Upgraded | vortex 12 m, 5 dmg x25, aura 12 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| infernal_gateway | Infernal Gateway | portal 15 m, 17 s, 1 use | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| pit_of_shades_dlc27 | Pit of Shades | static pit 15 m | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| pit_of_shades_main | Pit of Shades | static pit 15 m | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| pit_of_shades | Pit of Shades | static pit 15 m | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| rubric_of_dark_dimensions | Rubric of Dark Dimensions | vortex into the Pit 15 m | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| irresistible_plague | Irresistible Plague! | plague 14 m static, petrifies | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| plaguemaster | Plaguemaster | plague 14 m static, petrifies | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| warp_junction | Warp Junction | ruin burst 15 m, 14 s | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| magma_storm | Magma Storm | 20 m vortex + 60 m bombardment (spread 45 m); ground only | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | Ground-only key: cast form, see G1 |
| chain_lightning_ror | Chain Lightning | chain lightning 10 m, reach 17 | 4 | Wanderer/static area on a standing infantry blob; value rule, trash rule, safety ring (ruling 'worst-case reach') | - | - |
| da_boss_loons | Da Boss' Loons | fanatics released at the caster: ring 98 m clear around the caster; bound 10 m | 3 | Ring is around the caster: 98 m free of any other unit of ours; almost never true in a real line | Ask whether the released fanatics hit allies; if 'worst-case' is too strict a smaller ring | - |

### enemy_wave (30)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| wrath_of_manann | Wrath of Manann | wave 6 m wide, 70 m, drift 17 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | Honoured (not_flying) |
| wind_of_death | Wind of Death | wave 6 m wide, 100 m, drift 25 m; 1 use | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | - |
| seafang | Seafang | longship strafe 4 m wide, 95 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | Honoured (not_flying) |
| the_burning_head | The Burning Head | flaming head 7 m, 180 m, drift 109 m | 3 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling); end-of-path buffer 84 to 126 m against a 70 to 105 m bound: fires only when the army is far from the far end | None more feasible; consider the user re-checking the 95% drift | Honoured (not_flying) |
| burning_head_skull | The Burning Head | flaming head 7 m, 180 m, drift 109 m | 3 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling); end-of-path buffer 84 to 126 m against a 70 to 105 m bound: fires only when the army is far from the far end | None more feasible; consider the user re-checking the 95% drift | Honoured (not_flying) |
| khaines_ring_of_fury | Bound Fiery Convocation | phoenix 7 m, 132 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | - |
| fiery_convocation | Fiery Convocation | phoenix 7 m, 132 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | - |
| burning_alignment | Burning Alignment | ray 8 m, 120 m, 5 s wind-up | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | - |
| hell_hammer | Hell Hammer | hammer 14 m, 60 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | - |
| nightmaw | Nightmaw | beast 4.5 m, 33 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | - |
| penumbral_pendulum | The Penumbral Pendulum | pendulum 4 m, 80 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | Honoured (not_flying) |
| arnizipals_black_horror | Arnzipal's Black Horror | horror 10 m, 140 m, drift 64 m | 3 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling); end-of-path buffer 84 to 126 m against a 70 to 105 m bound: fires only when the army is far from the far end | None more feasible; consider the user re-checking the 95% drift | Honoured (not_flying) |
| bangstick | Bangstick | line of explosions 12 m, 48 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | - |
| black_dragon_egg | Black Dragon Egg | fire breath 6 m, 72 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | - |
| blue_fire | Blue Fire of Chaos | warpflame 12 m, 48 m; ground; not in melee | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | engaged_in_melee honoured (WW_NOMELEE). Ground cast: see G1 |
| blue_fire_upgraded | Blue Fire of Chaos Upgraded | warpflame 12 m, 48 m; ground; not in melee | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | engaged_in_melee honoured (WW_NOMELEE). Ground cast: see G1 |
| fiery_ring_of_thori | Fiery Ring of Thori | fireball 6 m, 72 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | Honoured (not_flying) |
| gaze_of_malice | Gaze of Malice | gaze 14 m, 24 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | - |
| jade_lions_breath | Jade Lion's Breath | breath 9 m, 37.5 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | - |
| kovsh_breath | Kovsh Breath | frost breath 12 m, 48 m; may slow (C) | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | Honoured (not_flying) |
| lash_of_slaanesh_dlc27 | Lash of Slaanesh | lash 12 m, 40 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | - |
| lash_of_slaanesh | Lash of Slaanesh | lash 12 m, 40 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | - |
| lash_of_slaanesh_keeper | Lash of Slaanesh | lash 12 m, 40 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | - |
| pink_fire_dlc20 | Pink Fire of Tzeentch | pink fire 12 m, 48 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | Honoured (not_flying) |
| pink_fire | Pink Fire of Tzeentch | pink fire 12 m, 48 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | Honoured (not_flying) |
| scorch | Scorch | fissures 6 m, 72 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | - |
| stream_of_corruption_dlc20 | Stream of Corruption | poison stream 6 m, 72 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | Honoured (not_flying) |
| stream_of_corruption | Stream of Corruption | poison stream 6 m, 72 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | Honoured (not_flying) |
| sunfang | Sunfang | sunfire 12 m, 48 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | - |
| spear_slaupnir | The Spear Slaupnir | spear thrust 4 m, 80 m | 4 | Straight wave: standing target, clear corridor (radius + 10 m, widening to drift), most value on the path (ruling) | - | Honoured (not_flying) |

### enemy_melee (35)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| acquiescence | Acquiescence | speed -25%, melee def -24; 2 uses | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | - |
| assassins_trophy | Assassin's Trophy | melee atk -24, melee def -24, Lord/Hero only | 5 | Melee stat hex on an enemy in melee: pays off at once | - | Honoured (target_class commander) |
| blight_swarm | Blight Swarm | melee def -20, spreads; 4 uses | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | - |
| el_syf | El Syf | speed -45%, melee def -40, phys res -20, Lord/Hero only | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | Honoured (commander) |
| preyton_horns | Preyton Horns | leadership -8 enemy, +8 allies | 4 | User ruling (audit R6): enemy_melee | - | - |
| fermented_fungi | Fermented Fungi | melee def -24, rampage; 3 uses | 4 | Melee def -24 in melee fine; rampage effect unclear (C) | - | - |
| frost_shard_glaive | Frost Shard Glaive | speed -45%, melee def -40 | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | - |
| hidden_huntress | Hidden Huntress | speed -25%, melee def -24 | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | - |
| hidden_huntress_upgraded | Hidden Huntress Upgraded | speed -25%, armour -30, melee def -40 | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | - |
| hornswaggle | Hornswaggle | speed -25%, armour -30, melee def -24 | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | - |
| lord_of_dragons | Lord of Dragons | melee atk -40, melee def -24 | 5 | Melee stat hex on an enemy in melee: pays off at once | - | - |
| marked_for_eatin | Marked for Eatin' | speed -25%, armour -30, melee def -40 | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | - |
| beguile | Master of Beguilement | melee atk -40 | 5 | Melee stat hex on an enemy in melee: pays off at once | - | - |
| oath_of_vengeance | Oath of Vengeance | melee def -24 | 5 | Melee stat hex on an enemy in melee: pays off at once | - | - |
| ottos_scythe | Otto's Scythe | melee atk -40, leadership -24, charge defence down | 5 | Melee stat hex on an enemy in melee: pays off at once | - | - |
| pestilent_potions | Pestilent Potions | melee atk -24, damage -25%; 3 uses | 5 | Melee stat hex on an enemy in melee: pays off at once; limited uses: the closest enemy may be a chaff unit | - | - |
| dispatch_the_swarm_attack | Ravaging Swarm | melee def -24, spreading swarm | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | - |
| dispatch_the_swarm_attack_upgraded | Ravaging Swarm Upgraded | melee def -40, 4 dmg x10, spreading swarm | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | - |
| taunt | Taunt | speed -25%, armour -30, melee def -24 | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | - |
| tendrils_of_the_sea | Tendrils of the Sea | speed/charge -60%, mass -20%, melee atk -40, large only | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | Honoured (target_class large = unit_is_not_large) |
| averland_runefang | The Averland Runefang | melee atk -40, base damage -60% | 5 | Melee stat hex on an enemy in melee: pays off at once | - | - |
| the_dark_master | The Dark Master | melee atk -40 | 5 | Melee stat hex on an enemy in melee: pays off at once | - | - |
| enfeebling_foe | The Enfeebling Foe | melee atk -24, melee def -24; 1-3 uses, 4 keys | 4 | Melee stat hex on an enemy in melee: pays off at once; limited uses: the closest enemy may be a chaff unit | - | - |
| the_hammer_of_karak_drazh | The Hammer of Karak Drazh | melee atk -40, base damage -30% | 5 | Melee stat hex on an enemy in melee: pays off at once | - | - |
| titan_headsman | Titan Headsman | speed -45%, melee def -24 | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | - |
| torment_blade | Torment Blade | melee atk -24, damage -25% | 5 | Melee stat hex on an enemy in melee: pays off at once | - | - |
| trophy_heads | Trophy Heads | lord key: melee atk -24, def -40, Lord/Hero only; daemon key: -30/-30, any target | 3 | One entry, two keys, one target_class | Split the entry: the daemon_wings key has no commander flag, so it is over-restricted to Lords/Heroes | Daemon-wings key over-restricted (shared commander class) |
| virulent_contagion | Virulent Contagion | melee def -40, spreading; 2 uses | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest; limited uses: the closest enemy may be a chaff unit | - | - |
| virulent_contagion_upgraded | Virulent Contagion Upgraded | melee def -50, spreading; 3 uses | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest; limited uses: the closest enemy may be a chaff unit | - | - |
| whip_of_agony | Whip of Agony | melee def -24, fear and terror | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | - |
| willing_prey | Willing Prey | melee atk -24, melee def -40 | 5 | Melee stat hex on an enemy in melee: pays off at once | - | - |
| youre_next | You're Next! | speed -45%, melee atk -24, def -40, Lord/Hero only | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | Honoured (commander) |
| no_escape | No Escape | melee def -40, cannot move; 3 uses | 4 | Root plus melee def: right while in melee | - | - |
| transfix_hex | Transfix | melee def -40, silence, cannot move, Lord/Hero with morale at or below half; 3 uses | 2 | Fires on any Lord/Hero in melee; the game accepts it only when target morale is at or below half of base | Add FOURTH.wavering(enemy) == true to the commander class for this entry (enemy Lord/Hero in melee AND wavering) | NOT HONOURED: target flag morale_is_higher_than_half_of_base_morale |
| flash_bomb | Flash Bomb | speed/charge -60%, melee def -24, aura 35 m | 4 | Debuff on an enemy in melee; payoff immediate, target is only the closest | - | - |

### enemy_single_drain (10)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| spirit_leech_death_bound | Spirit Leech | 67-180 dmg to ONE entity | 4 | Single-target damage on the highest-value single entity, standing still (user ruling 2026-11-15) | - | - |
| spirit_leech_dlc25 | Spirit Leech | 67-180 dmg to ONE entity | 4 | Single-target damage on the highest-value single entity, standing still (user ruling 2026-11-15) | - | - |
| spirit_leech_gunnery_school | Spirit Leech | 67-180 dmg to ONE entity | 4 | Single-target damage on the highest-value single entity, standing still (user ruling 2026-11-15) | - | - |
| spirit_leech | Spirit Leech | 67-180 dmg to ONE entity | 4 | Single-target damage on the highest-value single entity, standing still (user ruling 2026-11-15) | - | - |
| spirit_leech_guo_ror | Spirit Leech | 67-180 dmg to ONE entity | 4 | Single-target damage on the highest-value single entity, standing still (user ruling 2026-11-15) | - | - |
| liber_bubonicus | The Liber Bubonicus | 67-180 dmg to ONE entity | 4 | Single-target damage on the highest-value single entity, standing still (user ruling 2026-11-15) | - | - |
| deaths_timekeeper | Death's Timekeeper | 67-180 dmg to ONE entity | 4 | Single-target damage on the highest-value single entity, standing still (user ruling 2026-11-15) | - | - |
| rancid_visitations | Rancid Visitations | 133 dmg, strong vs characters | 4 | Single-target damage on the highest-value single entity, standing still (user ruling 2026-11-15) | - | - |
| effagee_of_da_git | 'Effagee' of da Git | 67 dmg, cannot move, strong vs characters | 4 | Single-target damage on the highest-value single entity, standing still (user ruling 2026-11-15) | - | - |
| punch_dagger | Punch-Dagger | 180 dmg, strong vs characters; reach 15 m so bound 10 m | 4 | Single-target damage on the highest-value single entity, standing still (user ruling 2026-11-15) | - | - |

### enemy_fast_near_ally (9)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| petrifying_gaze | Petrifying Gaze | speed -25/-50/-75% then cannot move; 2 uses | 4 | Rooting/slowing a fast mover near our units: right moment, but no heading test (a unit passing by qualifies) | - | - |
| befuddlement_of_mischiefs | Befuddlement of Mischiefs | cannot move, aura 35 m on the ground; 3 uses | 4 | Rooting/slowing a fast mover near our units: right moment, but no heading test (a unit passing by qualifies) | - | - |
| gaze_of_fate | Gaze of Fate | melee atk -40, cannot move; 3 uses | 4 | Rooting/slowing a fast mover near our units: right moment, but no heading test (a unit passing by qualifies); melee atk -40 is wasted if it never engages | - | - |
| master_rune_of_slowness | Master Rune of Slowness | speed/charge -60%, charge bonus -40%, 45 s | 4 | Rooting/slowing a fast mover near our units: right moment, but no heading test (a unit passing by qualifies) | - | - |
| mither | Mither | speed/charge -60%; 3 uses | 4 | Rooting/slowing a fast mover near our units: right moment, but no heading test (a unit passing by qualifies) | - | - |
| rune_of_slowness | Rune of Slowness | speed/charge -45%, charge bonus -40% | 4 | Rooting/slowing a fast mover near our units: right moment, but no heading test (a unit passing by qualifies) | - | - |
| sadistic_snare | Sadistic Snare | cannot move, melee def -24; 14 m bound | 4 | Rooting/slowing a fast mover near our units: right moment, but no heading test (a unit passing by qualifies) | - | - |
| spearfishers_net | Spearfisher's Net | cannot move, melee def -24; not flying | 4 | Rooting/slowing a fast mover near our units: right moment, but no heading test (a unit passing by qualifies) | - | Honoured (not_flying class) |
| whispering_mist | Whispering Mist | speed/charge -45%, fatigue | 4 | Rooting/slowing a fast mover near our units: right moment, but no heading test (a unit passing by qualifies) | - | - |

### enemy_area_drain (8)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| blood_statuette_of_spite | Blood Statuette of Spite | 5 dmg x25 entities | 4 | Damages up to 25 (or 15) soldiers per tick: right to want a unit with enough soldiers; most value per soldier | - | - |
| darkened_mist | Darkened Mist | 7 dmg x25, spreading; bound 21 m | 4 | Damages up to 25 (or 15) soldiers per tick: right to want a unit with enough soldiers; most value per soldier | - | - |
| fate_of_bjuna_dlc25 | The Fate of Bjuna | 10 dmg x25 | 4 | Damages up to 25 (or 15) soldiers per tick: right to want a unit with enough soldiers; most value per soldier | - | - |
| fate_of_bjuna | The Fate of Bjuna | 10 dmg x25 | 4 | Damages up to 25 (or 15) soldiers per tick: right to want a unit with enough soldiers; most value per soldier | - | - |
| maelstrom_of_change | Maelstrom of Change | 10 dmg x25, spreading | 4 | Damages up to 25 (or 15) soldiers per tick: right to want a unit with enough soldiers; most value per soldier | - | - |
| otherworldly_pestilence | Otherworldly Pestilence | 5 dmg x25, spreading; 1 use | 4 | Damages up to 25 (or 15) soldiers per tick: right to want a unit with enough soldiers; most value per soldier | - | - |
| staff_of_masks | Staff of Masks | 5 dmg x15, fatigue; caster must not be broken | 4 | Damages up to 25 (or 15) soldiers per tick: right to want a unit with enough soldiers; most value per soldier | - | Caster morale_is_broken_or_lower: covered by the routing gate |
| winged_staff | Winged Staff | 5 dmg x25, ground aura 35 m | 4 | Damages up to 25 (or 15) soldiers per tick: right to want a unit with enough soldiers; most value per soldier | - | - |

### enemy_large_shot (5)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| blast | Blast | 150+350 AP, 1 use | 4 | Armour-piercing shot: large first, then armour (user ruling); caster out of melee; 10 m clear | - | - |
| damned_pistol | Damned Pistol | 495+855 AP, 2 uses | 4 | Armour-piercing shot: large first, then armour (user ruling); caster out of melee; 10 m clear | - | - |
| hunting_spear | Hunting Spear | 540 AP, unlimited | 4 | Armour-piercing shot: large first, then armour (user ruling); caster out of melee; 10 m clear | - | - |
| master_rune_of_flight | Master Rune of Flight | 150+350 AP, min range 5 m | 4 | Armour-piercing shot: large first, then armour (user ruling); caster out of melee; 10 m clear | - | Min range honoured (shot_min_ok) |
| schalkains_teeth | Schalkain's Teeth | 2 shots 250+250, 2 uses | 4 | Armour-piercing shot: large first, then armour (user ruling); caster out of melee; 10 m clear | - | - |

### enemy_cone (5)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| fishy_breath | Fishy Breath | breath cone from the caster, 3 uses | 4 | Clear cone, most value (ruling) | - | - |
| pestilent_breath_mount | Pestilent Breath | poison cone, unlimited | 4 | Clear cone, most value | - | - |
| pestilent_breath | Pestilent Breath | poison cone, 4 uses | 4 | Clear cone, most value | - | - |
| shatter | Shatter | ground-pound cone; not flying | 4 | Clear cone, most value | - | Honoured (not_flying) |
| skabscrath | Skabscrath | cone, not flying | 4 | Clear cone, most value | - | Honoured (not_flying) |

### melee_clear (5)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| groundbreaker | Groundbreaker | shockwave, blast 10 m; 3 uses | 4 | Self-centred blast: in melee, not wavering, none of ours within blast + 10 m (user ruling) | - | - |
| burning_rage | Burning Rage | fire explosion, blast 15 m; 3 uses | 4 | Self-centred blast: in melee, not wavering, none of ours within blast + 10 m (user ruling) | - | - |
| bloodbeast | Bloodbeast | fiery convulsions, blast 15 m, unlimited | 4 | Self-centred blast: in melee, not wavering, none of ours within blast + 10 m (user ruling) | - | - |
| emergency_vent | Emergency Vent | scalding steam, blast 15 m, 12 s | 4 | Self-centred blast: in melee, not wavering, none of ours within blast + 10 m (user ruling) | - | - |
| land_mine | Land Mine | steam bomb, blast 25 m; 3 uses, 10 s recharge | 3 | Self-centred blast: in melee, not wavering, none of ours within blast + 10 m (user ruling); all 3 charges can go in 30 s of one melee | Count enemies inside the blast, or one use per engagement | - |

### enemy_melee_or_fast (4)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| crippling_throw | Crippling Throw | speed x0.75, melee def -24, 30 s; 3 uses; not in melee | 4 | Melee arm fits melee def; fast arm only slows x0.75 (ruling 'split by effect') | - | Honoured (caster out of melee) |
| golden_blowpipe | The Golden Blowpipe of P'Toohee | poison: speed and damage x0.85; min range 5 m | 4 | Same split | - | Min range checked only after the pick (a second melee enemy is not tried) |
| ethracs_brazier | Ethrac's Brazier | speed -25%, 4 dmg x25, spreading; 1 use | 4 | Same split; 1 use | - | - |
| storm_of_the_night | Storm of the Night | speed -60%, 67 dmg, strong vs flying; flying targets only | 4 | Same split | - | Honoured (class flying) |

### enemy_commander_value (3)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| dweomer_leach_orb | Dweomer Leach Orb | enemy winds recharge -160%, caster gains winds; target must have a casting ability | 3 | Lord/Hero is only a proxy for 'caster'; fires whenever one is visible, no own-pool test | Generated set of caster unit keys (units owning a spell) in place of 'commander'; skip when own winds pool is full | NOT HONOURED: hasnt_casting_ability (proxy only) |
| slann_gold | Slann Gold | enemy winds recharge -180%, 55 s; caster target | 3 | Same proxy problem | Same generated caster set | NOT HONOURED: hasnt_casting_ability (proxy only) |
| deathmasters_sigil | Deathmaster's Sigil | cannot move 7 s, good vs armour; not flying, Lord/Hero | 3 | User ruling (round 159); a 7 s root on the top-value Lord at any moment, not tied to a payoff | Enemy Lord/Hero in melee with ours, or fast near ours | Honoured (commander_ground) |

### fly_dive (2)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| emberstorm | Emberstorm | flaming vortex 10 m under the phoenix; 3 uses | 4 | Flying over an enemy with ours clear | - | grounded honoured; flying_over_invalid_location not readable |
| moon_flare | Moon Flare | flame 10 m, self cannot move 11.5 s; 3 uses | 4 | Same trigger; the self-root on a flier is accepted by the ruling | - | grounded honoured; flying_over_invalid_location not readable |

### enemy_wavering (2)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| ghostly_howl | Ghostly Howl | 16 dmg x25 entities, morale -16 (target morale at or below half) | 4 | Finishes a wavering enemy; closest is fine | - | Honoured only if 'wavering' implies morale at or below half (C1) |
| the_amber_trance | The Amber Trance | morale -16 enemy, +16 caster; 1 use | 4 | Tips a wavering enemy into rout; 1 use so the closest may be a poor pick | - | - |

### enemy_wave_charge (2)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| tidecall | Tidecall | wave: speed x0.75 10 s | 4 | Slow wave at a fast enemy with a clear path (rule 10) | - | - |
| wind_blast | Wind Blast | wave: speed and charge speed x0.6 12 s | 4 | Slow wave at a fast enemy with a clear path (rule 10) | - | - |

### enemy_sweep (2)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| disembowelling_sweep | Disembowelling Sweep | sweep, reach 12 m, morale -6 | 4 | Sweep needs melee and a clear 22 m | - | - |
| flesh_eating_scarabs | Flesh-eating Scarabs | scarab sweep, reach 36.5 m, morale -16; 3 uses | 4 | Sweep needs melee and a clear 46.5 m (rarely true) | - | - |

### enemy_single_shot (2)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| dead_eye | Dead Eye | 420+630, single entities only, 5 s wind-up | 4 | Sniper on the most valuable single, standing still (ruling) | - | Honoured (class single) |
| focused_shot | Focused Shot | 100+230, +120 vs large, single entities only, 2 uses | 4 | Sniper; takes a large single first | - | Honoured (class single) |

### enemy_execute (2)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| emperors_executioner | The Emperor's Executioner | 732 dmg, executes below 20%; Lord/Hero only; 1 use | 5 | Fires exactly at the execute line | - | Honoured (commander class) |
| emperors_executioner_upgrade | The Emperor's Executioner | 732 dmg, executes below 33%; 1 use | 5 | Fires exactly at the execute line | - | - |

### enemy_strike (1)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| siegebreaker | Siegebreaker | wall breaker, 3 uses, 5 s wind-up; unit target invalid unless climbing | 3 | Effect on units unconfirmed; fires on the top-value standing single entity | Confirm it harms units (C); otherwise limit to sieges | Ground form: see issue G1 (cast form not wired) |

### enemy_missile_shooting (1)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| unit_bound_missile_mirror | Missile Mirror | redirects projectiles back at the shooter; missile units only | 4 | Shooter must be shooting and not in melee | - | Honoured (class missile) |

### enemy_melee_or_shooting (1)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| spear_of_kurnous | Spear of Kurnous | blind: accuracy -30, melee atk/def -24 | 5 | Melee arm for the melee stats, shooting arm for accuracy: matches both halves | - | - |

### enemy_melee_noncommander (1)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| the_dreaded_thirteenth | The Dreaded Thirteenth | explosion plus Skaven summon on the enemy; 1 use, 4 keys | 4 | Closest non-Lord/Hero enemy in melee, ground cast on it (ruling) | - | Honoured (commander excluded) |

### enemy_low_health_noncommander (1)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| eye_of_khorne | Eye of Khorne | 2660 dmg x100 entities, summons Chaos Spawn; below 20% health, not Lord/Hero; 1 use | 3 | Finisher: lowest-health pick can be a 3-man remnant, wasting the single use | Among valid targets take the highest live value (or require a minimum soldier count) | Honoured (not commander, strictly below 20%); audit flags are false positives |

### enemy_infantry_shot (1)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| bolt_storm | Bolt Storm | 12 bolts 9+24 AP, +33 vs infantry, not in melee | 4 | Most valuable infantry per soldier, standing still (ruling) | - | Honoured (caster out of melee) |

### enemy_blob_vortex (1)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| frost_dragon_scale | Ancient Chaos Frost Dragon Scale | 7 m cold vortex 24 s (burns who touch it) | 4 | Blob rule with the vortex radius | - | - |

### last_stand_clear (1)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---:|---|---|---|
| necrotic_explosion | Necrotic Explosion | 26600 dmg to self and area, kills the unit; 1 use | 5 | At 10% health in melee the unit dies anyway (user ruling 'Necrotic last') | - | - |

## C. Game-mechanics questions

1. Is a "wavering" unit always at or below half of base morale (so Ghostly Howl's `morale_is_higher_than_half_of_base_morale` flag is always satisfied by `is_wavering()`)? Does `is_wavering()` stay true for a routing (broken) unit? (If yes, enemy_wavering would aim at routed units.)
2. Does a ground-only ability (Heaven's Gate, Lamprey's Bite, Flesh-eating Scarabs, Blue Fire, Magma Storm, Siegebreaker) refuse `perform_special_ability(key, unit)`, or does the engine use the unit's position? One QA battle log line settles it (G1).
3. Heaven's Gate: does the wearer really teleport to the target point and strike there? If so, is it acceptable that the mod sends a character into an enemy blob with no test of its own safety?
4. Hammer of Smednir: the extracted phase is only speed and charge speed x0.4. Does the vortex also deal damage ("strong vs multiple combatants")? If not, rule 10 argues for a charge arm.
5. Siegebreaker: does it damage units at all (a wall breaker), or only gates and walls? Its unit-target flag suggests a siege-only unit effect.
6. Fermented Fungi lists "Rampage (positive)": is rampage beneficial or harmful to the enemy unit it is cast on?
7. Kovsh Breath ("hinders and hampers the enemy's progress") and Tidecall/Wind Blast: any other slow-only abilities inside enemy_wave? A slow-only breath belongs on the charge arm (rule 10).
8. Frost Dragon Scale: does the 7 m vortex exist on the ground at the target (blob attack, as the user ruled), or is it a buff around the caster?
9. `fast_speed()`: the stat or the current speed? A walking cavalry unit passes the "fast" test either way; does a routing enemy cavalry unit read `is_moving` true and pass it?
10. Dweomer Leach Orb and Slann Gold: is the enemy army winds pool readable (`army winds_of_magic_current`) so they could wait until the enemy pool is worth draining?
11. Does the vortex of the wanderers hit the caster's own army when the game table says `affects_allies` = 0 (Heaven's Gate, Abyssal Swarm, Crackleblaze)? The mod skips the safety test for them.
12. Da Boss' Loons: do the released fanatics hit our units at the caster's feet (the mod keeps 98 m clear)? A player test would show whether a smaller ring is enough.
13. Eye of Khorne: is the summon of Chaos Spawn worth the single use on a nearly dead remnant? If the user wants the summon regardless, the current pick is fine.

## Summary (5 lines)

1. G1, the biggest finding: the 7 ground-only WW keys (Siegebreaker, Blue Fire x2, Heaven's Gate, Lamprey's Bite, Scarabs, Magma Storm) are cast in the unit form; `eg_ground` is written but never read, and the harness cannot tell the two forms apart.
2. Transfix fires on any Lord/Hero in melee, but the game needs target morale at or below half; Dweomer Leach Orb and Slann Gold use "Lord/Hero" as a stand-in for "has a casting ability" and will be refused on non-casters (fixes in G2, G3).
3. Waves, cones and strikes have no minimum target value (G5), and the older enemy pickers (melee, fast, wavering, missile, non-commander) ignore fog of war (G4).
4. Most tooltip sentences are INCOMPLETE rather than wrong: they hide the 10 m margin, the caster-out-of-melee gate, the "standing" target rule and the entry classes; 19 of 25 have a corrected sentence above; 6 are EXACT (enemy_melee and enemy_single_drain apart from class clauses, enemy_wavering, enemy_melee_or_shooting, enemy_melee_noncommander, enemy_low_health_noncommander).
5. Triggers themselves are sound (mostly 4 or 5 for the ruled families); the lowest scores are Transfix (2), Hammer of Smednir (2), Dweomer Leach Orb, Slann Gold, Deathmaster's Sigil, Eye of Khorne, Siegebreaker, Land Mine, Heaven's Gate, Lamprey's Bite, Sandstorm, Da Boss' Loons and the two Burning Heads / Arnizipal (3).
