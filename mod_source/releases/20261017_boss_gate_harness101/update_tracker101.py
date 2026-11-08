# -*- coding: utf-8 -*-
"""Round-101 tracker updates: boss-only exclusion + Gate of Khorne."""
import io, re, sys

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
s = io.open(P, "rb").read().decode("utf-8")

BOSS = [
    ("Greater Faith Bastion", "wh_dlc06_quest_abilities_grand_faiths_bastion",
     "wh_dlc06_emp_cha_arch_lector_0_boss", "melee_self"),
    ("Bitter Sting", "wh3_dlc27_qb_unit_abilities_bitter_sting",
     "wh3_dlc27_chs_feral_manticore_boss", "enemy_unit"),
    ("Frenzied Challenge", "wh3_dlc27_qb_unit_abilities_frenzied_challenge",
     "wh3_dlc27_bst_mon_ghorgon_boss", "enemy_unit"),
    ("Visions of Madness", "wh3_dlc27_qb_unit_abilities_visions_of_madness",
     "wh3_dlc27_bst_mon_jabberslythe_boss", "enemy_unit"),
    ("Guttural Roar", "wh3_dlc27_qb_unit_abilities_guttural_roar",
     "wh3_dlc27_cth_mon_celestial_lion_boss", "target"),
]
NEVER = [
    ("Breath of the Hydra", "wh2_dlc10_quest_abilities_fiery_head", "wh2_dlc10_def_mon_war_hydra_boss"),
    ("Eye of Rejuvenation", "wh2_dlc10_quest_abilities_regenerating_head", "wh2_dlc10_def_mon_war_hydra_boss"),
    ("Howling Winter", "wh_dlc08_quest_abilities_howling_winter", "wh_dlc08_nor_mon_frost_wyrm_boss"),
    ("Master of Souls", "wh_dlc08_quest_abilities_master_of_souls", "wh_dlc08_vmp_mon_terrorgheist_boss"),
    ("Servants of Nagash", "wh_dlc04_quest_abilities_servant_of_nagash", "wh_dlc04_vmp_cha_strigoi_ghoul_king_0_boss"),
    ("Dissolving Bone", "wh3_dlc27_qb_unit_abilities_dissolving_bone", "wh3_dlc27_tmb_mon_carrion_boss"),
    ("Terrible Malice", "wh3_dlc27_qb_unit_abilities_terrible_malice", "wh3_dlc27_sla_mon_preyton_boss"),
    ("Copious Phlegm", "wh3_dlc27_qb_unit_abilities_copious_phlegm", "wh3_dlc27_nur_mon_toad_dragon_boss"),
    ("Fiery Convocation", "wh2_dlc10_quest_abilities_magic_fiery_convocation", "wh2_dlc10_nor_mon_phoenix_flamespyre_boss"),
    ("Flame Storm", "wh2_dlc10_quest_abilities_flame_storm", "wh2_dlc10_nor_mon_phoenix_flamespyre_boss"),
]

def once(old, new, label):
    global s
    n = s.count(old)
    assert n == 1, "%s: %d matches" % (label, n)
    s = s.replace(old, new, 1)
    print("ok", label)

# ------------------------------------------------------------------ legend
army_line = ("- `excluded (not in wheel: army ability - removed from mod per user decision 2026-10-17)` "
             "— the ability WAS implemented but sits outside the single in-wheel rule (army-bar); it has been "
             "**REMOVED from the mod's `ABILITIES` table** per the user's decision of 2026-10-17 (**Meat Feast**, "
             "**Massacre**; see §10.2).\n")
once(army_line, army_line +
     "- `excluded (not in wheel: boss-only unit)` — the ability's **ONLY grant path is a `_boss` unit** (a "
     "quest-battle boss variant: no player can recruit it, equip it, learn it from a skill tree or spend a rite "
     "on it), so it can never appear on a player unit's wheel. The five that were implemented were **REMOVED from "
     "the mod's `ABILITIES` table**; the other ten never shipped (see **§10.3**).\n",
     "legend")

# ------------------------------------------------------------------ header update
anchor = ("**Update 2026-10-10 (annotated copy):** `WH3_auto_ability_annotated.lua` carries the same change "
          "(the per-ability bound, the shared picker, the enemy-ground evaluator/helper/key-set) — log-free / "
          "find-free, as always.\n")
HEAD = (
 "**Update 2026-10-17 (harness 101 — BOSS-ONLY EXCLUSION + GATE OF KHORNE).** **A. Boss-only exclusion.** "
 "Every ACTIVE ability whose only grant path is a `_boss` unit is excluded: **15** in-wheel keys were verified "
 "from the grant junctions (`land_abil.tsv`, `uset_ability.tsv`, the `sag_to_abilities`+`sag_to_units` pair and "
 "`army_ab_faction.tsv` - none of them has any other grant). **5 were implemented and are REMOVED from the mod**: "
 "Greater Faith Bastion, Bitter Sting, Frenzied Challenge, Visions of Madness, Guttural Roar; the other **10** "
 "never shipped and stay absent. The table is now **573 entries / 599 keys** (was 577 / 603); `melee_unwavering` "
 "**360**, `enemy_engaged_or_shot` **86**. **B. Gate of Khorne** (`wh3_main_character_abilities_gate_of_khorne`) "
 "is **IMPLEMENTED** on the user's trigger, verbatim: *\"The trigger will place it on the closest enemy that is in "
 "range of the ability and fighting.\"* — a new `enemy_ground_melee` trigger: among enemies within the ability's "
 "own 70% bound (**35 m** of the 50 m cast range) keep those **FIGHTING (in melee)**, pick the **CLOSEST**, and "
 "place the summon on **THAT ENEMY'S ground** via `perform_special_ability_ground(key, enemy_pos, 0, 0)` with a "
 "fresh caster controller and a fresh enemy, a hold, a pre-cast re-check, and its own reason string naming the "
 "enemy type and the real distance — never the caster's position, and no `unit_in_range`. Full record: **§10.3**. "
 "Spreadsheet: `docs/WH3_abilities_master_v3_2026-10-17.xlsx` (v3 supersedes v2; v1 and v2 are unchanged).\n\n")
once(anchor, HEAD + anchor, "header update")

# ------------------------------------------------------------------ §2 blocks: Removed line
def add_removed_after_key(key, unit, verb):
    global s
    idxs = [m.start() for m in re.finditer(re.escape("- Keys: `%s`" % key), s)]
    if not idxs:
        print("removed-line", key, "NO §2 BLOCK")
        return
    added = 0
    for i in reversed(idxs):
        j = s.find("\n\n", i)
        assert j > i
        block = s[i:j]
        if "Removed: **2026-10-17**" in block:
            continue
        line = ("\n- Removed: **2026-10-17** — `excluded (not in wheel: boss-only unit)`; its only grant path is "
                "`%s` (land_abil.tsv), a quest-battle boss variant. %s See §10.3." % (unit, verb))
        s = s[:j] + line + s[j:]
        added += 1
    print("removed-line", key, added)

for name, key, unit, _fam in BOSS:
    add_removed_after_key(key, unit, "It was implemented and is REMOVED from the mod's `ABILITIES` table.")
for name, key, unit in NEVER:
    add_removed_after_key(key, unit, "It never shipped in the mod (no code change was needed).")

# ------------------------------------------------------------------ §3a rows
for name, key, unit, fam in BOSS:
    old = None
    for ln in s.split("\n"):
        if ln.startswith("| %s `%s`" % (name, key)):
            old = ln
            break
    assert old is not None, name
    cd = old.split("|")[4].strip()
    new = ("| %s `%s` | `excluded (not in wheel: boss-only unit)` | %s | — | %s · "
           "**round 101 (2026-10-17):** EXCLUDED - its ONLY grant path is `%s` (land_abil.tsv), a quest-battle "
           "boss variant; %s |" % (
               name, key, fam, cd, unit,
               "REMOVED from the mod (it was implemented before this round)" if name != "x" else ""))
    # the REMOVED wording only for the five (all of them are implemented)
    new = new.replace("; ;", ";")
    s = s.replace(old, new, 1)
    print("row", name)

# ------------------------------------------------------------------ Gate of Khorne §3a row
old_gate = ("| Gate of Khorne `wh3_main_character_abilities_gate_of_khorne` | `skipped (unsuitable: spawned/ranged)` "
            "| melee_enemy | When in melee: cast on self (self-cast allowed; nearest-ally picker later). | "
            "cd 120s · 10s · friend/self · ×1 uses · wind-up 5s · questionnaire §2 #327 |")
new_gate = ("| Gate of Khorne `wh3_main_character_abilities_gate_of_khorne` | "
            "`implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | "
            "The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is "
            "FIGHTING (in melee): the summon is placed on THAT ENEMY'S ground (perform_special_ability_ground, "
            "fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · ground/friend · ×1 uses · "
            "wind-up 5s · questionnaire §2 #327 · **round 101 (2026-10-17):** implemented per the user's trigger "
            "\"place it on the closest enemy that is in range of the ability and fighting\" (harness 101) |")
once(old_gate, new_gate, "gate row")

# ------------------------------------------------------------------ Gate §2 blocks
gate_old_decision = ("- Decision: **skipped (unsuitable: spawned/ranged)** — collection-time: unsuitable "
                     "(spawned/ranged); no automatic logic.")
gate_new_decision = ("- Decision: **implemented (enemy_ground_melee)** — **round 101 (2026-10-17):** the user "
                     "chose the trigger, verbatim: *\"The trigger will place it on the closest enemy that is in "
                     "range of the ability and fighting.\"* Among enemies within the ability's own 70% bound "
                     "(35 m of 50 m, `FOURTH.ENEMY_CAST_R50`) keep those FIGHTING (in melee), pick the CLOSEST, "
                     "and place the summon on THAT ENEMY'S ground with the ground form, a fresh caster controller "
                     "and a fresh enemy, a hold and a pre-cast re-check. Its own reason names the enemy type and "
                     "the real distance; the cast target is never the caster.")
blocks = [m.start() for m in re.finditer(re.escape("**327. Gate of Khorne**"), s)]
assert len(blocks) >= 1, "gate block"
for i in reversed(blocks):
    j = s.find("\n\n", i)
    block = s[i:j]
    assert gate_old_decision in block, "gate decision shape"
    s = s[:i] + block.replace(gate_old_decision, gate_new_decision, 1) + s[j:]
print("gate blocks", len(blocks))

# ------------------------------------------------------------------ §10.3
old_102_tail = ("**Build/install:** pack rebuilt and installed; all **5 ship files byte-identical** to source; "
                "installed pack md5 **`f7c5e525ded0d1a07242b22d9053d66d`** (live mod sha256 "
                "`c8573d52a54195aaa3b13a3dbdcc290aa2ed23d7c79bfb76fb957aa835b872ab`, 546,408 bytes). The passive "
                "observer probe `zz_probe_dist.pack` was **left installed and untouched** (md5 "
                "`d4e67cfb8bc562c7d6f0ff742909c13d`, 20,063 bytes).")
assert s.count(old_102_tail) == 1
rows = "\n".join("| %s | `%s` | `%s` |" % (n, k, u) for n, k, u in
                 [(b[0], b[1], b[2]) for b in BOSS] + NEVER)
SEC = old_102_tail + """

### 10.3 The boss-only exclusion + Gate of Khorne (2026-10-17)

**The user's instruction (verbatim):** "exclude the active abilities that are granted to boss units. Mark in the
excel the reason for exclusion." and, for the second build: "The trigger will place it on the closest enemy that
is in range of the ability and fighting."

**A. What "boss-only" means, and how the list was verified.** A key is boss-only when **every** grant path found
in the extracted junction tables terminates on a `_boss` unit: `land_abil.tsv`
(land_units_to_unit_abilites), `uset_ability.tsv` (unit_set -> ability), `sag_to_abilities.tsv` +
`sag_to_units.tsv` (special-ability group -> ability -> unit) and `army_ab_faction.tsv`. `ui_coll_junc.tsv` is
display-only and grants nothing; skill-tree and rite junctions are **not part of this extraction**, so the
negative is closed only for the tables above (the same documented limit as `WH3_summon_analysis.md` §5.3).
**15 in-wheel keys qualify.** A naive `_boss` name test finds 18 - the extra three (`Empowering Shrooms`,
`They Needs Stabbin'`, `Squig Thinkin'`) are granted to `*_big_boss*` units, which are **ordinary recruitable Big
Boss heroes**, not quest variants (on-screen name is the generic rank name; `multiplayer_qb_cap = 2` in
`db_main_units.tsv`; they reuse an existing warboss attribute group instead of a bespoke one). Those three stay.

| Ability | Key | Only granting unit |
|---|---|---|
""" + rows + """

**The five that were IMPLEMENTED and are now REMOVED** (entry, marker, badge and key all gone from the live
script and the annotated copy):

| marker | name | trigger before | badge | key |
|---|---|---|---|---|
| `grand_faiths_bastion` | Greater Faith Bastion | `melee_unwavering` | `zz_auto_badge_grand_faiths_bastion` | `wh_dlc06_quest_abilities_grand_faiths_bastion` |
| `bitter_sting` | Bitter Sting | `enemy_engaged_or_shot` | `zz_auto_badge_bitter_sting` | `wh3_dlc27_qb_unit_abilities_bitter_sting` |
| `frenzied_challenge` | Frenzied Challenge | `enemy_engaged_or_shot` | `zz_auto_badge_frenzied_challenge` | `wh3_dlc27_qb_unit_abilities_frenzied_challenge` |
| `visions_of_madness` | Visions of Madness | `enemy_engaged_or_shot` | `zz_auto_badge_visions_of_madness` | `wh3_dlc27_qb_unit_abilities_visions_of_madness` |
| `guttural_roar` | Guttural Roar | `melee_unwavering` | `zz_auto_badge_guttural_roar` | `wh3_dlc27_qb_unit_abilities_guttural_roar` |

**What was NOT touched:** no evaluator, trigger, helper, constant or state was removed. `melee_unwavering` loses
its two boss members only (362 -> 360) and stays the shared in-melee trigger; `enemy_engaged_or_shot` loses three
(89 -> 86); `enemy_ground_area` stays 9; `ushoran_health` stays 33; every other entry is unchanged.

**B. Gate of Khorne.** Key `wh3_main_character_abilities_gate_of_khorne` (there is NO `dlc26` variant - confirmed
against `unit_spec_abil.tsv` / `unit_abilities.tsv`). Data: 1 use, 120 s recharge / 60 s initial, 10 s active,
5 s wind-up, `target_intercept_range` 50 m, `target_ground` + `target_friends` (not `target_self`), restriction
`climbing_manning_eq_on_platform`, `ai_usage = hex_melee`, summons `wh3_main_kho_inf_bloodletters_summoned_0`
(100 Bloodletters). New trigger `enemy_ground_melee`, evaluated per poll:
1. enumerate the enemy army; keep enemies alive, valid, **in melee** and within **35 m** (70% of 50 m, the
   standing rule; `unit:unit_distance` ONLY - never `unit_in_range`);
2. pick the **CLOSEST** of them (the melee-only arm means the shared picker's melee preference collapses to a
   pure distance comparison);
3. re-fetch the caster controller and the chosen enemy the SAME tick; re-read the enemy (alive, still in melee,
   still within 35 m) immediately before the cast and SKIP if it lapsed, logging the real distance;
4. cast `perform_special_ability_ground(key, enemy:position(), 0, 0)` - the position is the ENEMY'S, never the
   caster's;
5. its own reason string: `closest fighting (in-melee) enemy within bound (targeting <type>, distance=<x>m)`.

**Counts (exact, before -> after):** ABILITIES **577 -> 573 entries** (-5 +1); **603 -> 599 keys** (-5 +1);
`melee_unwavering` **362 -> 360**; `enemy_engaged_or_shot` **89 -> 86**; `enemy_ground_melee` **1**;
`range_real` fields **98 -> 96**; `ushoran_health` 33 and `enemy_ground_area` 9 unchanged.

**Harness 101:** GREEN **3442 checks / 0 failures** (live + annotated). RED (pre101 snapshot) **3396 checks /
78 designed failures**: 65 re-based count pins (573/599, 360, 86, 96, 1146, wording 573) + 3 tooltip-coverage
pins + 8 inherited red-control branches from earlier rounds + 2 aggregate world tallies; harness 101's own 0aa
section and all seven Gate worlds pass on both sides by design (the snapshot has no Gate of Khorne, so every
gate world fires nothing).

**Build/install:** all **5 ship files byte-identical** to source (script 548,092 bytes); installed pack md5
**`deaf707dcda5087d689116860f7b0f27`**, dist == installed. `zz_probe_dist.pack` left installed and untouched
(md5 `d4e67cfb8bc562c7d6f0ff742909c13d`).

**Spreadsheet:** `docs/WH3_abilities_master_v3_2026-10-17.xlsx` (+ `.ods`) - **v3 supersedes v2; v1 and v2 are
unchanged**. The five rows carry Status `EXCLUDED` and reason `boss-only unit (granted only to _boss units)`;
the five removed implementations read `REMOVED (boss-only)`; Gate of Khorne reads `IMPLEMENTED` on
`enemy_ground_melee`; the Changelog has a v3 row."""

once(old_102_tail, SEC, "section 10.3")

io.open(P, "wb").write(s.encode("utf-8"))
print("wrote", P, len(s))
