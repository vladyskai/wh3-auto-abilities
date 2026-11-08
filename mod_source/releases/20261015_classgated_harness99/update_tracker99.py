# -*- coding: utf-8 -*-
"""Update WH3_ability_tracker.md for round 99 (the target-class-gated Class-B
entries + the Rampage pair + Merciw's + the two mid-flight entries)."""
import io, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "C:/Users/vlady/Desktop"
TRK = ROOT + "/WH3_ability_tracker.md"
NL = chr(10)

# marker -> (keys, trigger, real, bound, class note)
INFO = {
 "overseer_of_the_unseen": (["wh3_dlc29_hero_active_overseer_of_the_unseen"], "ally_overseer", 100, 70,
   "non-commander / non-large target - DERIVED (land_units.class != \"com\" AND the battle entity size is not large/very_large; 918 keys)"),
 "whiplash": (["wh2_dlc14_lord_abilities_whiplash"], "ally_beast", 100, 70,
   "beast target - DERIVED (main_units.caste == \"war_beast\"; 55 keys)"),
 "iron_hand_captain": (["wh3_dlc27_character_abilities_iron_hand_captain"], "ally_broken", 200, 140,
   "morale-BROKEN target (MoraleState == \"broken\")"),
 "inspired_marksmanship_i": (["wh3_main_lord_abilities_inspired_marksmanship_i"], "ally_missile", 100, 70,
   "missile-capable target - DERIVED (land_units.primary_missile_weapon non-empty; 493 keys)"),
 "inspired_marksmanship_ii": (["wh3_main_lord_abilities_inspired_marksmanship_ii"], "ally_missile", 100, 70,
   "missile-capable target - DERIVED (land_units.primary_missile_weapon non-empty; 493 keys)"),
 "inspired_marksmanship_iii": (["wh3_main_lord_abilities_inspired_marksmanship_iii"], "ally_missile", 100, 70,
   "missile-capable target - DERIVED (land_units.primary_missile_weapon non-empty; 493 keys)"),
 "makaissons_persuader": (["wh3_dlc25_weapon_abilities_makaissons_persuader"], "ally_warmachine_heal", 100, 70,
   "WAR MACHINE target - DERIVED (main_units.caste == \"warmachine\"; 68 keys)"),
 "reforge": (["wh3_dlc23_character_abilities_reforge"], "ally_hellforged_heal", 100, 70,
   "HELL-FORGED target - DERIVED (unit_attributes attribute \"hellforged\"; 13 keys)"),
 "remouldered": (["wh2_dlc16_lord_abilities_remouldered"], "ally_monster_heal", 100, 70,
   "MONSTER target - DERIVED (main_units.caste == \"monster\"; 235 keys)"),
 "restore": (["wh2_dlc09_character_abilities_restore"], "ally_construct_heal", 100, 70,
   "CONSTRUCT target - DERIVED (unit_attributes attribute \"construct\"; 29 keys)"),
 "fury_of_khaine": (["wh2_main_unit_abilities_fury_of_khaine"], "ally_melee_buff", 100, 70,
   "plain ally buff (owner in melee) - the RAMPAGE entry, implemented (the M/A badge is the opt-in)"),
 "verminous_fury": (["wh3_dlc29_lord_abilities_verminous_fury"], "ally_melee_buff", 200, 140,
   "plain ally buff (owner in melee) - the RAMPAGE entry, implemented (the M/A badge is the opt-in)"),
 "merciws_monstrous_regiment": (["wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment"], "ally_infinite_buff", None, None,
   "NO distance bound - INFINITE RANGE per the wiki (target_intercept_range = -1.0); the real distance is still logged"),
 "slezuzus_voice": (["wh3_dlc27_character_abilities_slezuzus_voice"], "ally_melee_buff", 200, 140,
   "plain ally buff (owner in melee) - ruled + requested MID-FLIGHT this round"),
 "gruts_sickle": (["wh3_main_item_abilities_gruts_sickle"], "ally_winds", 100, 70,
   "the ally with the HIGHEST ABSOLUTE HIT POINTS REMAINING (max HealthValue) - ruled + requested MID-FLIGHT this round"),
}
# Merciw's second bound key shares the same phase and gets the same row update
MERCIW_EXTRA = "wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment"

shutil.copy2(TRK, TRK + ".bak_pre_classgated99")
lines = io.open(TRK, encoding="utf-8", newline="").read().split(NL)
start = next(i for i, l in enumerate(lines) if l.startswith("| Ability | Status | Group |"))
end = next(i for i, l in enumerate(lines) if l.startswith("### 3b."))

def patch_row(key, status, group, note_tag, label, prop=None):
    hits = 0
    for i in range(start, end):
        l = lines[i]
        if not l.startswith("| ") or ("`" + key + "`") not in l:
            continue
        parts = l.split(" | ")
        if len(parts) < 5:
            continue
        if status is not None:
            parts[1] = status
        if group is not None:
            parts[2] = group
        if prop is not None:
            parts[3] = prop
        last = parts[-1]
        trail = "|" if last.rstrip().endswith("|") else ""
        body = last.rstrip()
        if trail:
            body = body[:-1].rstrip()
        if note_tag not in body:
            body = body + " · " + note_tag
        parts[-1] = body + " " + ("|" if trail else "")
        lines[i] = " | ".join(parts)
        hits += 1
    assert hits == 1, "%s: %d rows matched for %s" % (label, hits, key)
    print("  patched %-46s %s" % (key[:46], label))

print("== the 15 implemented entries ==")
for m, (keys, trig, real, bound, cls) in INFO.items():
    if real is None:
        tag = ("**round 99 (target-class-gated):** casts ON THE CHOSEN ALLY with **NO distance bound** -"
               " INFINITE RANGE per the wiki (" + cls + "); offer test skipped entirely, the real distance"
               " is still logged for diagnosis; fresh caster+ally handles; was a self-cast.")
        boundtxt = "no bound (infinite range per the wiki)"
    else:
        tag = ("**round 99 (target-class-gated):** casts ON THE CHOSEN ALLY of the required class (" + cls + ")"
               " - the offer test is `unit:unit_distance(ally)` <= its own 70% bound = floor(" + str(real)
               + " * 0.70) = " + str(bound) + " m (`FOURTH.ALLY_CAST_R" + str(real) + "`) ONLY, never the engine's"
               " `unit_in_range`; fresh caster+ally handles. Was a self-cast.")
        boundtxt = str(bound) + " m = 70% of the real " + str(real) + " m"
    st = "`implemented (ally-targeted: %s)`" % ("winds_maxhp" if trig == "ally_winds" else trig)
    prop = ("Cast on the chosen ALLY (trigger `" + trig + "`; class gate: " + cls + "); trigger range = "
            + boundtxt + ".")
    for k in keys:
        patch_row(k, st, "ally_unit", tag, "implemented " + m, prop=prop)
# the second Merciw's bound key
patch_row(MERCIW_EXTRA, "`implemented (ally-targeted: ally_infinite_buff)`", "ally_unit",
          "**round 99 (target-class-gated):** shares the bound key's phase - casts ON THE CHOSEN ALLY with"
          " **NO distance bound** (infinite range per the wiki); was a self-cast.",
          "merciw extra key",
          prop="Cast on the chosen ALLY (trigger `ally_infinite_buff`); no bound (infinite range per the wiki).")

# ---------------------------------------------------------------- top note
anchor = None
for i, l in enumerate(lines[:130]):
    if l.startswith("**Update 2026-10-"):
        anchor = i
assert anchor is not None, "no update-note anchor found"
note = ("**Update 2026-10-15 (TARGET-CLASS-GATED CLASS-B ROUND - harness99):** the **15** entries the Class-B"
        " round left tagged NEEDS A RULING were ruled and are now **ALL IMPLEMENTED as ally-targeted casts** on"
        " the mod's own ally picker. **10** are **TARGET-CLASS-GATED** - each must cast on an ALLY of a required"
        " class, whose key list is **DERIVED FROM THE GAME'S OWN DATA** (exact whole-key equality, the Glorious-"
        " Death method): `overseer_of_the_unseen` -> non-commander / non-large (**918** keys: `land_units.class`"
        " != \"com\" AND `battle_entities.size` not large/very_large), `whiplash` -> beast (**55**: `main_units."
        "caste` == \"war_beast\"), `iron_hand_captain` -> morale BROKEN (`MoraleState` == \"broken\"),"
        " `inspired_marksmanship_i/ii/iii` -> missile-capable (**493**: `land_units.primary_missile_weapon`"
        " non-empty), `makaissons_persuader` -> war machine (**68**: `main_units.caste` == \"warmachine\"),"
        " `reforge` -> Hell-Forged (**13**: the `hellforged` unit attribute), `remouldered` -> monster (**235**:"
        " `main_units.caste` == \"monster\"), `restore` -> construct (**29**: the `construct` unit attribute)."
        " **2** are the **RAMPAGE** pair (`fury_of_khaine`, `verminous_fury`) - implemented on the plain in-melee"
        " ally buff family (the M/A badge is the opt-in). **1** - **Merciw's Monstrous Regiment** - is an ally-"
        "targeted cast with **NO distance bound** (INFINITE RANGE per the wiki; `target_intercept_range` = -1.0)."
        " **2** were ruled **mid-flight** this round and are included: **Daemonic Whispers** (plain ally buff,"
        " real 200 m) and **Grut's Sickle** (real 100 m, but its PICK RULE is the ally with the **HIGHEST ABSOLUTE"
        " HIT POINTS REMAINING**, max `HealthValue` - the recipient pays a health cost for the winds recharge)."
        " The offer test is the per-ability 70% constant ONLY - **never** the engine's `unit_in_range`; the cast"
        " goes through the **fresh-handle** route; the chosen ally is ALWAYS the cast target (never the owner)."
        " `melee_unwavering` 373 -> 363, `charge_or_melee` 26 -> 25, `ushoran_health` 38 -> 34; `ally_melee_buff`"
        " 11 -> 14; 10 new ally triggers; `ally_range_real` 18 -> 32; a new `FOURTH.ALLY_CAST_R200` = 140."
        " Entries/keys unchanged (579 / 605). Harness99: **3365 checks, 0 failures**; red control vs the pre-edit"
        " snapshot: 3332 checks, the round's RED CONTROL passes 26/56 world results by design.")
lines.insert(anchor, note)
lines.insert(anchor + 1, "")

io.open(TRK, "w", encoding="utf-8", newline="").write(NL.join(lines))
print("wrote", TRK, len(NL.join(lines)), "bytes")
